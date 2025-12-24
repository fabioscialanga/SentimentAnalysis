import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    rv = client.get('/health')
    assert rv.status_code == 200
    assert rv.json == {'status': 'ok'}

def test_predict_no_data(client):
    rv = client.post('/predict', json={})
    assert rv.status_code == 400

def test_predict_mock(client):
    """
    Test prediction. If model is present, it tests the model.
    If not, it tests the mock logic in app.py.
    """
    rv = client.post('/predict', json={'review': 'This is a great movie!'})
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert 'sentiment' in json_data
    assert 'confidence' in json_data
