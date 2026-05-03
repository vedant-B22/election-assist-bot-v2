import pytest
import json
from unittest.mock import patch, MagicMock
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# ── Route tests ────────────────────────────────────────────────

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'ElectionBot' in response.data


def test_health_route(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "ElectionBot-v2"


# ── Chat input validation tests ────────────────────────────────

def test_chat_missing_message(client):
    response = client.post('/chat',
                           data=json.dumps({}),
                           content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_chat_empty_message(client):
    response = client.post('/chat',
                           data=json.dumps({"message": "   "}),
                           content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_chat_message_too_long(client):
    response = client.post('/chat',
                           data=json.dumps({"message": "x" * 501}),
                           content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_chat_no_json_body(client):
    response = client.post('/chat',
                           data="not json",
                           content_type='text/plain')
    assert response.status_code == 400


# ── Chat success (mocked Vertex AI) ───────────────────────────

def test_chat_success(client):
    mock_token = "fake-token-123"
    mock_vertex_response = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": "In India, elections are conducted by the Election Commission of India."}]
                }
            }
        ]
    }

    with patch('app.get_access_token', return_value=mock_token), \
         patch('requests.post') as mock_post:

        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_vertex_response
        mock_post.return_value = mock_resp

        response = client.post('/chat',
                               data=json.dumps({"message": "How do elections work in India?"}),
                               content_type='application/json')

        assert response.status_code == 200
        data = response.get_json()
        assert "reply" in data
        assert len(data["reply"]) > 0


def test_chat_no_access_token(client):
    with patch('app.get_access_token', return_value=None):
        response = client.post('/chat',
                               data=json.dumps({"message": "Tell me about elections"}),
                               content_type='application/json')
        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data


def test_chat_vertex_fallback_on_404(client):
    mock_token = "fake-token"
    mock_vertex_response = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": "Fallback response about elections."}]
                }
            }
        ]
    }

    with patch('app.get_access_token', return_value=mock_token), \
         patch('requests.post') as mock_post:

        # First call returns 404, second call (fallback) succeeds
        mock_404 = MagicMock()
        mock_404.ok = False
        mock_404.status_code = 404

        mock_ok = MagicMock()
        mock_ok.ok = True
        mock_ok.status_code = 200
        mock_ok.json.return_value = mock_vertex_response

        mock_post.side_effect = [mock_404, mock_ok]

        response = client.post('/chat',
                               data=json.dumps({"message": "What is VVPAT?"}),
                               content_type='application/json')

        assert response.status_code == 200
        data = response.get_json()
        assert "reply" in data


# ── get_access_token unit tests ────────────────────────────────

def test_get_access_token_success():
    from app import get_access_token
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"access_token": "test-token-abc"}
    mock_resp.raise_for_status = MagicMock()

    with patch('requests.get', return_value=mock_resp):
        token = get_access_token()
        assert token == "test-token-abc"


def test_get_access_token_failure():
    from app import get_access_token
    with patch('requests.get', side_effect=Exception("metadata not available")):
        token = get_access_token()
        assert token is None


# ── Message boundary tests ─────────────────────────────────────

def test_chat_exactly_500_chars(client):
    mock_vertex_response = {
        "candidates": [{"content": {"parts": [{"text": "Valid response"}]}}]
    }
    with patch('app.get_access_token', return_value="tok"), \
         patch('requests.post') as mock_post:
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_vertex_response
        mock_post.return_value = mock_resp

        response = client.post('/chat',
                               data=json.dumps({"message": "a" * 500}),
                               content_type='application/json')
        assert response.status_code == 200


def test_chat_exactly_501_chars(client):
    response = client.post('/chat',
                           data=json.dumps({"message": "a" * 501}),
                           content_type='application/json')
    assert response.status_code == 400