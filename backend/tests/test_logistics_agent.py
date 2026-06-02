import pytest
from agents.logistics_agent import get_transport_options, plan_itinerary, build_itinerary_step

SAMPLE_VENUE = {
    "venue_id": "att_stadium",
    "stadium_name": "AT&T Stadium",
    "city": "Arlington",
    "transport_options": [
        {"mode": "shuttle", "description": "Official shuttle from Dallas Union Station", "cost_usd": 10},
        {"mode": "rideshare", "description": "Uber/Lyft drop-off zone on Collins St", "cost_usd": None},
    ]
}

SAMPLE_MATCH = {
    "match_id": "WC2026_M020",
    "home_team": "Argentina",
    "away_team": "Austria",
    "kickoff_utc": "2026-06-22T19:00:00+00:00",
    "kickoff_local": "2026-06-22T14:00:00",
    "venue_id": "att_stadium",
    "city": "Arlington",
}


# --- get_transport_options ---

def test_get_transport_options_returns_list(mock_db):
    mock_db.venues.find_one.return_value = SAMPLE_VENUE
    result = get_transport_options(mock_db, "att_stadium")
    assert isinstance(result, list)


def test_get_transport_options_queries_by_venue_id(mock_db):
    mock_db.venues.find_one.return_value = SAMPLE_VENUE
    get_transport_options(mock_db, "att_stadium")
    call_filter = mock_db.venues.find_one.call_args[0][0]
    assert call_filter == {"venue_id": "att_stadium"}


def test_get_transport_options_returns_transport_array(mock_db):
    mock_db.venues.find_one.return_value = SAMPLE_VENUE
    result = get_transport_options(mock_db, "att_stadium")
    assert len(result) == 2
    assert result[0]["mode"] == "shuttle"


def test_get_transport_options_missing_venue_returns_empty(mock_db):
    mock_db.venues.find_one.return_value = None
    result = get_transport_options(mock_db, "unknown_venue")
    assert result == []


# --- build_itinerary_step ---

def test_build_itinerary_step_structure():
    step = build_itinerary_step(
        time="14:00",
        activity="Arrive at AT&T Stadium",
        location="Arlington, TX",
        transport_mode="shuttle",
        notes="Take shuttle from Union Station"
    )
    assert step["time"] == "14:00"
    assert step["activity"] == "Arrive at AT&T Stadium"
    assert step["location"] == "Arlington, TX"
    assert step["transport_mode"] == "shuttle"
    assert step["notes"] == "Take shuttle from Union Station"


def test_build_itinerary_step_notes_optional():
    step = build_itinerary_step("10:00", "Breakfast", "Dallas", "walk")
    assert "notes" in step
    assert step["notes"] is None


# --- plan_itinerary ---

def test_plan_itinerary_returns_dict(mocker, mock_db):
    mock_db.venues.find_one.return_value = SAMPLE_VENUE
    mock_result = mocker.MagicMock()
    mock_result.text = '{"steps": [{"time": "12:00", "activity": "Depart hotel", "location": "Dallas", "transport_mode": "shuttle", "notes": null}]}'
    mocker.patch("agents.logistics_agent.gemini.models.generate_content", return_value=mock_result)
    result = plan_itinerary(mock_db, SAMPLE_MATCH, "downtown Dallas")
    assert isinstance(result, dict)


def test_plan_itinerary_has_steps(mocker, mock_db):
    mock_db.venues.find_one.return_value = SAMPLE_VENUE
    mock_result = mocker.MagicMock()
    mock_result.text = '{"steps": [{"time": "12:00", "activity": "Depart hotel", "location": "Dallas", "transport_mode": "shuttle", "notes": null}]}'
    mocker.patch("agents.logistics_agent.gemini.models.generate_content", return_value=mock_result)
    result = plan_itinerary(mock_db, SAMPLE_MATCH, "downtown Dallas")
    assert "steps" in result
    assert len(result["steps"]) >= 1


def test_plan_itinerary_calls_gemini(mocker, mock_db):
    mock_db.venues.find_one.return_value = SAMPLE_VENUE
    mock_result = mocker.MagicMock()
    mock_result.text = '{"steps": []}'
    mock = mocker.patch("agents.logistics_agent.gemini.models.generate_content", return_value=mock_result)
    plan_itinerary(mock_db, SAMPLE_MATCH, "downtown Dallas")
    mock.assert_called_once()
