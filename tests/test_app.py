import pytest
import json
from unittest.mock import patch, MagicMock
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
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "ElectionBot-v2"


def test_topics_route(client):
    response = client.get('/api/topics')
    assert response.status_code == 200
    data = response.get_json()
    assert "topics" in data
    assert len(data["topics"]) > 0


def test_chat_missing_message(client):
    response = client.post('/chat',
                           data=json.dumps({}),
                           content_type='application/json')
    assert response.status_code == 400


def test_chat_empty_message(client):
    response = client.post('/chat',
                           data=json.dumps({"message": "   "}),
                           content_type='application/json')
    assert response.status_code == 400


def test_chat_message_too_long(client):
    response = client.post('/chat',
                           data=json.dumps({"message": "x" * 501}),
                           content_type='application/json')
    assert response.status_code == 400


def test_chat_no_json(client):
    response = client.post('/chat',
                           data="not json",
                           content_type='text/plain')
    assert response.status_code == 400


def test_chat_success(client):
    mock_vertex_response = {
        "candidates": [{
            "content": {"parts": [{"text": "Elections in India are conducted by the ECI."}]}
        }]
    }
    with patch('app.get_access_token', return_value="fake-token"), \
         patch('requests.post') as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_vertex_response
        mock_post.return_value = mock_resp

        response = client.post('/chat',
                               data=json.dumps({"message": "How do elections work?"}),
                               content_type='application/json')
        assert response.status_code == 200
        data = response.get_json()
        assert "reply" in data


def test_chat_no_token(client):
    with patch('app.get_access_token', return_value=None):
        response = client.post('/chat',
                               data=json.dumps({"message": "hello"}),
                               content_type='application/json')
        assert response.status_code == 500


def test_chat_model_fallback(client):
    mock_vertex_response = {
        "candidates": [{
            "content": {"parts": [{"text": "Fallback answer about elections."}]}
        }]
    }
    with patch('app.get_access_token', return_value="fake-token"), \
         patch('requests.post') as mock_post:
        mock_fail = MagicMock()
        mock_fail.status_code = 404

        mock_ok = MagicMock()
        mock_ok.status_code = 200
        mock_ok.json.return_value = mock_vertex_response

        mock_post.side_effect = [mock_fail, mock_ok]

        response = client.post('/chat',
                               data=json.dumps({"message": "What is VVPAT?"}),
                               content_type='application/json')
        assert response.status_code == 200


def test_chat_exactly_500_chars(client):
    mock_vertex_response = {
        "candidates": [{"content": {"parts": [{"text": "Valid response"}]}}]
    }
    with patch('app.get_access_token', return_value="tok"), \
         patch('requests.post') as mock_post:
        mock_resp = MagicMock()
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


def test_get_access_token_success():
    from app import get_access_token, _token_cache
    _token_cache["token"] = None
    _token_cache["expires_at"] = 0

    mock_resp = MagicMock()
    mock_resp.json.return_value = {"access_token": "test-token", "expires_in": 3600}
    mock_resp.raise_for_status = MagicMock()

    with patch('requests.get', return_value=mock_resp):
        token = get_access_token()
        assert token == "test-token"


def test_get_access_token_failure():
    from app import get_access_token, _token_cache
    _token_cache["token"] = None
    _token_cache["expires_at"] = 0

    with patch('requests.get', side_effect=Exception("network error")):
        token = get_access_token()
        assert token is None


def test_get_access_token_cached():
    from app import get_access_token, _token_cache
    import time
    _token_cache["token"] = "cached-token"
    _token_cache["expires_at"] = time.time() + 3600

    token = get_access_token()
    assert token == "cached-token"