import json
import pytest
from agents.router import classify


MATCH_RESPONSE = json.dumps({
    "language": "en",
    "intent": "MATCH_LOOKUP",
    "entities": {"teams": ["Brazil"], "city": None, "date": None, "dietary_flags": []}
})

FAQ_RESPONSE = json.dumps({
    "language": "en",
    "intent": "GENERAL_FAQ",
    "entities": {"teams": [], "city": None, "date": None, "dietary_flags": []}
})

DISCOVER_RESPONSE = json.dumps({
    "language": "en",
    "intent": "LOCAL_DISCOVER",
    "entities": {"teams": [], "city": "Dallas", "date": None, "dietary_flags": ["halal"]}
})

SPANISH_RESPONSE = json.dumps({
    "language": "es",
    "intent": "MATCH_LOOKUP",
    "entities": {"teams": ["Argentina"], "city": None, "date": None, "dietary_flags": []}
})


def _mock_gemini(mocker, response_text):
    mock_result = mocker.MagicMock()
    mock_result.text = response_text
    return mocker.patch("agents.router.gemini.models.generate_content", return_value=mock_result)


def test_classify_returns_dict(mocker):
    _mock_gemini(mocker, MATCH_RESPONSE)
    result = classify("When does Brazil play?")
    assert isinstance(result, dict)


def test_classify_has_required_keys(mocker):
    _mock_gemini(mocker, MATCH_RESPONSE)
    result = classify("When does Brazil play?")
    assert "intent" in result
    assert "language" in result
    assert "entities" in result


def test_classify_match_intent(mocker):
    _mock_gemini(mocker, MATCH_RESPONSE)
    result = classify("When does Brazil play?")
    assert result["intent"] == "MATCH_LOOKUP"


def test_classify_extracts_team(mocker):
    _mock_gemini(mocker, MATCH_RESPONSE)
    result = classify("When does Brazil play?")
    assert "Brazil" in result["entities"]["teams"]


def test_classify_faq_intent(mocker):
    _mock_gemini(mocker, FAQ_RESPONSE)
    result = classify("How many teams are in the World Cup?")
    assert result["intent"] == "GENERAL_FAQ"


def test_classify_local_discover_with_dietary(mocker):
    _mock_gemini(mocker, DISCOVER_RESPONSE)
    result = classify("Find halal food near AT&T Stadium in Dallas")
    assert result["intent"] == "LOCAL_DISCOVER"
    assert "halal" in result["entities"]["dietary_flags"]
    assert result["entities"]["city"] == "Dallas"


def test_classify_detects_spanish(mocker):
    _mock_gemini(mocker, SPANISH_RESPONSE)
    result = classify("¿Cuándo juega Argentina?")
    assert result["language"] == "es"


def test_classify_calls_gemini(mocker):
    mock = _mock_gemini(mocker, MATCH_RESPONSE)
    classify("When does Brazil play?")
    mock.assert_called_once()


def test_classify_valid_intent_values(mocker):
    _mock_gemini(mocker, MATCH_RESPONSE)
    result = classify("test")
    valid = {"MATCH_LOOKUP", "ITINERARY", "LOCAL_DISCOVER", "TEAM_INFO", "GENERAL_FAQ", "MEMORY_READ"}
    assert result["intent"] in valid
