FROM python:3.9-slim

WORKDIR /app

ENV MODEL_URL="https://github.com/Profession-AI/progetti-devops/raw/refs/heads/main/Deploy%20e%20monitoraggio%20di%20un%20modello%20di%20sentiment%20analysis%20per%20recensioni/sentimentanalysismodel.pkl" \
    MODEL_PATH="/app/sentimentanalysismodel.pkl"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Pre-scarica il modello per evitare dipendenze esterne in runtime
RUN python -c "import os, urllib.request; url=os.environ.get('MODEL_URL'); dest=os.environ.get('MODEL_PATH');\nprint(f'Downloading model from {url}...'); urllib.request.urlretrieve(url, dest); print('Model ready at', dest)"

# Expose port 5000
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
