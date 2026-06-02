def find_matches(db, team=None, venue_id=None, round_type=None, limit=10):
    query = {}
    if team:
        query["$or"] = [{"home_team": team}, {"away_team": team}]
    if venue_id:
        query["venue_id"] = venue_id
    if round_type:
        query["round_type"] = round_type

    return list(db.matches.find(query, {"_id": 0}))[:limit]


def get_venue(db, venue_id):
    return db.venues.find_one(
        {"venue_id": venue_id},
        {"_id": 0, "description_embedding": 0}
    )


def get_team(db, team_name):
    return db.teams.find_one(
        {"$or": [{"name": team_name}, {"fifa_code": team_name}]},
        {"_id": 0}
    )


def build_match_card(match, venue):
    return {
        "match_id": match.get("match_id"),
        "home_team": match.get("home_team"),
        "away_team": match.get("away_team"),
        "kickoff_utc": match.get("kickoff_utc"),
        "kickoff_local": match.get("kickoff_local"),
        "venue_name": venue["stadium_name"] if venue else None,
        "city": match.get("city"),
        "group": match.get("group"),
        "round_type": match.get("round_type"),
        "broadcast": match.get("broadcast", []),
        "transport_options": venue.get("transport_options", []) if venue else [],
    }
