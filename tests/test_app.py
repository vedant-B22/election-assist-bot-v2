import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'ElectionBot' in response.data

def test_health_route(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}

def test_chat_missing_message(client):
    response = client.post('/chat', json={})
    assert response.status_code == 400
    assert b'Message is required' in response.data
