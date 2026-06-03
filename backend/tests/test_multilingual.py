"""
Multilingual flow tests — verifies router correctly identifies language and
that the API accepts messages in all supported languages.
"""
import json
import pytest
from fastapi.testclient import TestClient
from agents.router import classify


LANGUAGES = [
    ("es", "¿Cuándo juega Argentina?", "MATCH_LOOKUP", ["Argentina"]),
    ("fr", "Quand joue la France?", "MATCH_LOOKUP", ["France"]),
    ("ar", "متى تلعب البرازيل؟", "MATCH_LOOKUP", ["Brazil"]),
    ("ml", "ബ്രസീൽ എപ്പോൾ കളിക്കും?", "MATCH_LOOKUP", ["Brazil"]),
]


def _make_router_response(language, intent, teams):
    return json.dumps({
        "language": language,
        "intent": intent,
        "entities": {"teams": teams, "city": None, "date": None, "dietary_flags": []},
    })


def _mock_gemini(mocker, response_text):
    mock_result = mocker.MagicMock()
    mock_result.text = response_text
    return mocker.patch("agents.router.gemini.models.generate_content", return_value=mock_result)


# --- Router language detection ---

def test_router_detects_spanish(mocker):
    _mock_gemini(mocker, _make_router_response("es", "MATCH_LOOKUP", ["Argentina"]))
    result = classify("¿Cuándo juega Argentina?")
    assert result["language"] == "es"


def test_router_detects_french(mocker):
    _mock_gemini(mocker, _make_router_response("fr", "MATCH_LOOKUP", ["France"]))
    result = classify("Quand joue la France?")
    assert result["language"] == "fr"


def test_router_detects_arabic(mocker):
    _mock_gemini(mocker, _make_router_response("ar", "MATCH_LOOKUP", ["Brazil"]))
    result = classify("متى تلعب البرازيل؟")
    assert result["language"] == "ar"


def test_router_detects_malayalam(mocker):
    _mock_gemini(mocker, _make_router_response("ml", "MATCH_LOOKUP", ["Brazil"]))
    result = classify("ബ്രസീൽ എപ്പോൾ കളിക്കും?")
    assert result["language"] == "ml"


def test_router_extracts_team_from_spanish(mocker):
    _mock_gemini(mocker, _make_router_response("es", "MATCH_LOOKUP", ["Argentina"]))
    result = classify("¿Cuándo juega Argentina?")
    assert "Argentina" in result["entities"]["teams"]


def test_router_extracts_team_from_french(mocker):
    _mock_gemini(mocker, _make_router_response("fr", "MATCH_LOOKUP", ["France"]))
    result = classify("Quand joue la France?")
    assert "France" in result["entities"]["teams"]


# --- API accepts messages in all languages ---

MOCK_RESPONSE = {
    "response": {"type": "match_card", "data": {"matches": []}, "text": "Found 0 matches."},
    "trace": {"agents_fired": ["router"], "total_ms": 80, "steps": [], "eval": None, "retry_marker": "PASS"},
    "session_id": "s1",
}


@pytest.fixture
def client(mocker):
    mock_db = mocker.MagicMock()
    from api.main import app
    from api.db import get_db
    app.dependency_overrides[get_db] = lambda: mock_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.mark.parametrize("language,message", [
    ("es", "¿Cuándo juega Argentina?"),
    ("fr", "Quand joue la France?"),
    ("ar", "متى تلعب البرازيل؟"),
    ("ml", "ബ്രസീൽ എപ്പോൾ കളിക്കും?"),
])
def test_api_accepts_multilingual_message(mocker, client, language, message):
    mocker.patch("api.routes.chat.handle", return_value=MOCK_RESPONSE)
    resp = client.post("/api/chat", json={"message": message, "session_id": "s1", "language_hint": language})
    assert resp.status_code == 200


@pytest.mark.parametrize("language,message", [
    ("es", "¿Cuándo juega Argentina?"),
    ("fr", "Quand joue la France?"),
    ("ar", "متى تلعب البرازيل؟"),
    ("ml", "ബ്രസീൽ എപ്പോൾ കളിക്കും?"),
])
def test_api_multilingual_response_has_session_id(mocker, client, language, message):
    mocker.patch("api.routes.chat.handle", return_value=MOCK_RESPONSE)
    resp = client.post("/api/chat", json={"message": message, "session_id": "s1", "language_hint": language})
    assert "session_id" in resp.json()
