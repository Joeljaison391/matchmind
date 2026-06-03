import pytest
from fastapi.testclient import TestClient


MOCK_CHAT_RESPONSE = {
    "response": {"type": "faq_answer", "data": {}, "text": "Brazil plays at 3pm local time."},
    "trace": {
        "agents_fired": ["memory_agent", "router", "discovery_agent"],
        "total_ms": 140,
        "steps": [],
        "eval": {"relevance": 0.9, "completeness": 0.8, "accuracy": 0.85, "avg": 0.85},
        "retry_marker": "PASS",
    },
    "session_id": "test-session-123",
}

MOCK_PROFILE = {
    "fan_id": "abc123",
    "team_preference": ["Brazil"],
    "dietary_flags": ["halal"],
    "preferred_language": "en",
    "visited_venues": [],
}


@pytest.fixture
def client(mocker):
    mock_db = mocker.MagicMock()
    from api.main import app
    from api.db import get_db
    app.dependency_overrides[get_db] = lambda: mock_db
    yield TestClient(app)
    app.dependency_overrides.clear()


# --- /api/health ---

def test_health_returns_200(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200


def test_health_returns_ok_status(client):
    resp = client.get("/api/health")
    assert resp.json()["status"] == "ok"


def test_health_has_atlas_field(client):
    resp = client.get("/api/health")
    assert "atlas_connected" in resp.json()


def test_health_has_gemini_field(client):
    resp = client.get("/api/health")
    assert "gemini_reachable" in resp.json()


# --- /api/chat ---

def test_chat_missing_message_returns_422(client):
    resp = client.post("/api/chat", json={"session_id": "abc"})
    assert resp.status_code == 422


def test_chat_missing_session_id_returns_422(client):
    resp = client.post("/api/chat", json={"message": "hello"})
    assert resp.status_code == 422


def test_chat_valid_request_returns_200(mocker, client):
    mocker.patch("api.routes.chat.handle", return_value=MOCK_CHAT_RESPONSE)
    resp = client.post("/api/chat", json={"message": "When does Brazil play?", "session_id": "test-session-123"})
    assert resp.status_code == 200


def test_chat_returns_session_id(mocker, client):
    mocker.patch("api.routes.chat.handle", return_value=MOCK_CHAT_RESPONSE)
    resp = client.post("/api/chat", json={"message": "When does Brazil play?", "session_id": "test-session-123"})
    assert resp.json()["session_id"] == "test-session-123"


def test_chat_response_has_trace(mocker, client):
    mocker.patch("api.routes.chat.handle", return_value=MOCK_CHAT_RESPONSE)
    resp = client.post("/api/chat", json={"message": "When does Brazil play?", "session_id": "test-session-123"})
    assert "trace" in resp.json()


def test_chat_response_has_response_field(mocker, client):
    mocker.patch("api.routes.chat.handle", return_value=MOCK_CHAT_RESPONSE)
    resp = client.post("/api/chat", json={"message": "When does Brazil play?", "session_id": "test-session-123"})
    assert "response" in resp.json()


def test_chat_accepts_language_hint(mocker, client):
    mocker.patch("api.routes.chat.handle", return_value=MOCK_CHAT_RESPONSE)
    resp = client.post("/api/chat", json={
        "message": "¿Cuándo juega Brasil?",
        "session_id": "test-session-123",
        "language_hint": "es"
    })
    assert resp.status_code == 200


# --- /api/memory/{session_id} ---

def test_memory_returns_200(mocker, client):
    mocker.patch("api.routes.memory.get_fan_profile", return_value=MOCK_PROFILE)
    resp = client.get("/api/memory/test-session-123")
    assert resp.status_code == 200


def test_memory_returns_profile(mocker, client):
    mocker.patch("api.routes.memory.get_fan_profile", return_value=MOCK_PROFILE)
    resp = client.get("/api/memory/test-session-123")
    assert resp.json()["fan_id"] == "abc123"


def test_memory_missing_session_returns_empty(mocker, client):
    mocker.patch("api.routes.memory.get_fan_profile", return_value=None)
    resp = client.get("/api/memory/unknown-session")
    assert resp.status_code == 200
    assert resp.json() == {}
