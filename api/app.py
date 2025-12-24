import os
import pickle
import time
import urllib.request
from flask import Flask, request, jsonify, Response, render_template
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

REQUEST_COUNT = Counter('request_count', 'App Request Count', ['method', 'endpoint', 'http_status'])
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency', ['endpoint'])
PREDICTION_ERRORS = Counter('prediction_errors_total', 'Total prediction errors')
AUTH_FAILURES = Counter('auth_failures_total', 'Requests rejected for missing/invalid auth token')

MODEL_PATH = os.getenv('MODEL_PATH', 'sentimentanalysismodel.pkl')
MODEL_URL = os.getenv(
    'MODEL_URL',
    'https://github.com/Profession-AI/progetti-devops/raw/refs/heads/main/Deploy%20e%20monitoraggio%20di%20un%20modello%20di%20sentiment%20analysis%20per%20recensioni/sentimentanalysismodel.pkl',  # noqa: E501
)
API_TOKEN = os.getenv('API_TOKEN')
model = None


def download_model_if_missing() -> None:
    """Scarica il modello dal repository se non è già presente."""
    if os.path.exists(MODEL_PATH):
        return
    try:
        print(f"Model not found locally, downloading from {MODEL_URL}...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("Model downloaded successfully.")
    except Exception as e:
        # Non blocchiamo l'avvio: la TextBlob fallback resta disponibile
        print(f"Failed to download model: {e}")


def load_model() -> None:
    """Carica il modello pickle se disponibile."""
    global model
    try:
        download_model_if_missing()
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, 'rb') as f:
                model = pickle.load(f)
            print("Model loaded successfully.")
        else:
            print(f"Warning: Model file not found at {MODEL_PATH}. Using fallback logic.")
    except Exception as e:
        print(f"Error loading model: {e}")


load_model()

def _is_authorized() -> bool:
    """Controlla l'header Authorization se il token è configurato."""
    if not API_TOKEN:
        return True
    auth_header = request.headers.get('Authorization', '')
    return auth_header == f"Bearer {API_TOKEN}"


@app.before_request
def before_request():
    request.start_time = time.time()
    if request.path not in {'/health', '/metrics', '/'} and not _is_authorized():
        AUTH_FAILURES.inc()
        return jsonify({'error': 'Unauthorized'}), 401

@app.after_request
def after_request(response):
    request_latency = time.time() - request.start_time
    # Record latency
    REQUEST_LATENCY.labels(endpoint=request.path).observe(request_latency)
    # Record request count
    REQUEST_COUNT.labels(method=request.method, endpoint=request.path, http_status=response.status_code).inc()
    return response

@app.route('/predict', methods=['POST'])
def predict():
    if not request.json or 'review' not in request.json:
        return jsonify({'error': 'No review provided'}), 400

    review = request.json['review']
    
    try:
        prediction = None
        confidence = 0.0
        
        if model:
            # Predict using the loaded model
            prediction_result = model.predict([review])
            prediction = prediction_result[0]
            
            if hasattr(model, 'predict_proba'):
                probas = model.predict_proba([review])
                confidence = max(probas[0])
            else:
                confidence = 1.0
        else:
            # Fallback to TextBlob if model is not available
            from textblob import TextBlob
            analysis = TextBlob(review)
            polarity = analysis.sentiment.polarity
            
            if polarity > 0:
                prediction = "positive"
                confidence = 0.5 + (polarity / 2)
            elif polarity < 0:
                prediction = "negative"
                confidence = 0.5 + (abs(polarity) / 2)
            else:
                # Check for common Italian positive keywords
                it_positive = {"fantastico", "ottimo", "bello", "piace", "adoro", "meraviglioso", "eccellente"}
                if any(w in review.lower() for w in it_positive):
                    prediction = "positive"
                    confidence = 0.9
                else:
                    prediction = "negative"
                    confidence = 0.6
            
        return jsonify({
            'sentiment': prediction,
            'confidence': float(confidence)
        })

    except Exception as e:
        PREDICTION_ERRORS.inc()
        return jsonify({'error': str(e)}), 500

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
