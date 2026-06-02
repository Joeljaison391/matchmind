import pytest
from agents.memory_agent import get_fan_profile, upsert_fan_profile, build_personalisation_context

SAMPLE_PROFILE = {
    "fan_id": "abc123",
    "team_preference": ["Brazil"],
    "dietary_flags": ["halal"],
    "preferred_language": "en",
    "visited_venues": ["metlife_stadium"],
    "past_queries": ["When does Brazil play?"]
}


# --- get_fan_profile ---

def test_get_fan_profile_returns_profile(mock_db):
    mock_db.fan_graph.find_one.return_value = SAMPLE_PROFILE
    result = get_fan_profile(mock_db, "abc123")
    assert result["fan_id"] == "abc123"


def test_get_fan_profile_queries_by_fan_id(mock_db):
    mock_db.fan_graph.find_one.return_value = SAMPLE_PROFILE
    get_fan_profile(mock_db, "abc123")
    call_filter = mock_db.fan_graph.find_one.call_args[0][0]
    assert call_filter == {"fan_id": "abc123"}


def test_get_fan_profile_returns_none_if_missing(mock_db):
    mock_db.fan_graph.find_one.return_value = None
    result = get_fan_profile(mock_db, "unknown")
    assert result is None


# --- upsert_fan_profile ---

def test_upsert_fan_profile_calls_update_one(mock_db):
    upsert_fan_profile(mock_db, "abc123", {"team_preference": ["Brazil"]})
    mock_db.fan_graph.update_one.assert_called_once()


def test_upsert_fan_profile_uses_upsert_true(mock_db):
    upsert_fan_profile(mock_db, "abc123", {"team_preference": ["Brazil"]})
    kwargs = mock_db.fan_graph.update_one.call_args[1]
    assert kwargs.get("upsert") is True


def test_upsert_fan_profile_filters_by_fan_id(mock_db):
    upsert_fan_profile(mock_db, "abc123", {"team_preference": ["Brazil"]})
    call_filter = mock_db.fan_graph.update_one.call_args[0][0]
    assert call_filter == {"fan_id": "abc123"}


def test_upsert_fan_profile_sets_fields(mock_db):
    upsert_fan_profile(mock_db, "abc123", {"team_preference": ["Brazil"]})
    update_doc = mock_db.fan_graph.update_one.call_args[0][1]
    assert "team_preference" in update_doc["$set"]


# --- build_personalisation_context ---

def test_build_personalisation_context_with_profile():
    ctx = build_personalisation_context(SAMPLE_PROFILE)
    assert ctx["team_preference"] == ["Brazil"]
    assert ctx["dietary_flags"] == ["halal"]
    assert ctx["preferred_language"] == "en"


def test_build_personalisation_context_no_profile():
    ctx = build_personalisation_context(None)
    assert ctx["team_preference"] == []
    assert ctx["dietary_flags"] == []
    assert ctx["preferred_language"] == "en"


def test_build_personalisation_context_has_visited_venues():
    ctx = build_personalisation_context(SAMPLE_PROFILE)
    assert "metlife_stadium" in ctx["visited_venues"]
