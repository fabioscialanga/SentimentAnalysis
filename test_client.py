import requests
import time

BASE_URL = "http://localhost:5000"

def test_health():
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health Check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health Check Failed: {e}")

def test_prediction(review):
    try:
        payload = {"review": review}
        response = requests.post(f"{BASE_URL}/predict", json=payload)
        print(f"Review: '{review}'")
        print(f"Prediction: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Prediction Failed: {e}")

if __name__ == "__main__":
    print(f"Testing API at {BASE_URL}...")
    
    # 1. Test Health
    test_health()
    print("-" * 20)
    
    # 2. Test Positive Review
    test_prediction("This product is amazing! I use it every day.")
    print("-" * 20)
    
    # 3. Test Negative Review
    test_prediction("Terrible experience. The item arrived broken.")
    print("-" * 20)
    
    print("\nGo to http://localhost:9090 to see Prometheus metrics.")
    print("Go to http://localhost:3000 to see Grafana.")
