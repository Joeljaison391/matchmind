import pytest
from agents.match_agent import find_matches, get_venue, get_team, build_match_card


SAMPLE_MATCH = {
    "match_id": "WC2026_M009",
    "home_team": "Brazil",
    "away_team": "Morocco",
    "kickoff_utc": "2026-06-13T22:00:00+00:00",
    "kickoff_local": "2026-06-13T18:00:00",
    "venue_id": "metlife_stadium",
    "city": "East Rutherford",
    "group": "C",
    "round_type": "group_stage",
    "broadcast": ["Fox", "Telemundo"]
}

SAMPLE_VENUE = {
    "venue_id": "metlife_stadium",
    "stadium_name": "MetLife Stadium",
    "city": "East Rutherford",
    "country": "USA",
    "capacity": 82500,
    "transport_options": ["NJ Transit", "Shuttle from Penn Station"]
}

SAMPLE_TEAM = {
    "team_id": "brazil",
    "name": "Brazil",
    "fifa_code": "BRA",
    "group": "C",
    "confed": "CONMEBOL"
}


# --- find_matches ---

def test_find_matches_by_team(mock_db):
    mock_db.matches.find.return_value = [SAMPLE_MATCH]
    results = find_matches(mock_db, team="Brazil")
    assert len(results) == 1
    assert results[0]["home_team"] == "Brazil"


def test_find_matches_queries_both_home_away(mock_db):
    mock_db.matches.find.return_value = []
    find_matches(mock_db, team="Brazil")
    call_filter = mock_db.matches.find.call_args[0][0]
    assert "$or" in call_filter


def test_find_matches_by_venue(mock_db):
    mock_db.matches.find.return_value = [SAMPLE_MATCH]
    results = find_matches(mock_db, venue_id="metlife_stadium")
    call_filter = mock_db.matches.find.call_args[0][0]
    assert call_filter.get("venue_id") == "metlife_stadium"


def test_find_matches_returns_list(mock_db):
    mock_db.matches.find.return_value = []
    result = find_matches(mock_db)
    assert isinstance(result, list)


def test_find_matches_no_filter_finds_all(mock_db):
    mock_db.matches.find.return_value = [SAMPLE_MATCH]
    find_matches(mock_db)
    call_filter = mock_db.matches.find.call_args[0][0]
    assert call_filter == {}


# --- get_venue ---

def test_get_venue_queries_by_venue_id(mock_db):
    mock_db.venues.find_one.return_value = SAMPLE_VENUE
    get_venue(mock_db, "metlife_stadium")
    call_filter = mock_db.venues.find_one.call_args[0][0]
    assert call_filter == {"venue_id": "metlife_stadium"}


def test_get_venue_returns_venue(mock_db):
    mock_db.venues.find_one.return_value = SAMPLE_VENUE
    result = get_venue(mock_db, "metlife_stadium")
    assert result["stadium_name"] == "MetLife Stadium"


def test_get_venue_excludes_embedding(mock_db):
    mock_db.venues.find_one.return_value = SAMPLE_VENUE
    get_venue(mock_db, "metlife_stadium")
    projection = mock_db.venues.find_one.call_args[0][1]
    assert projection.get("description_embedding") == 0


# --- get_team ---

def test_get_team_by_name(mock_db):
    mock_db.teams.find_one.return_value = SAMPLE_TEAM
    result = get_team(mock_db, "Brazil")
    assert result["name"] == "Brazil"


def test_get_team_searches_name_and_code(mock_db):
    mock_db.teams.find_one.return_value = SAMPLE_TEAM
    get_team(mock_db, "BRA")
    call_filter = mock_db.teams.find_one.call_args[0][0]
    assert "$or" in call_filter


# --- build_match_card ---

def test_build_match_card_structure():
    card = build_match_card(SAMPLE_MATCH, SAMPLE_VENUE)
    assert card["match_id"] == "WC2026_M009"
    assert card["home_team"] == "Brazil"
    assert card["away_team"] == "Morocco"
    assert card["venue_name"] == "MetLife Stadium"
    assert card["city"] == "East Rutherford"


def test_build_match_card_has_transport():
    card = build_match_card(SAMPLE_MATCH, SAMPLE_VENUE)
    assert "transport_options" in card
    assert len(card["transport_options"]) > 0


def test_build_match_card_handles_no_venue():
    card = build_match_card(SAMPLE_MATCH, None)
    assert card["venue_name"] is None
