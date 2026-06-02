def get_fan_profile(db, fan_id):
    return db.fan_graph.find_one({"fan_id": fan_id}, {"_id": 0})


def upsert_fan_profile(db, fan_id, updates):
    db.fan_graph.update_one(
        {"fan_id": fan_id},
        {"$set": updates},
        upsert=True
    )


def append_query(db, fan_id, query_text):
    db.fan_graph.update_one(
        {"fan_id": fan_id},
        {"$push": {"past_queries": {"$each": [query_text], "$slice": -20}}},
        upsert=True
    )


def add_visited_venue(db, fan_id, venue_id):
    db.fan_graph.update_one(
        {"fan_id": fan_id},
        {"$addToSet": {"visited_venues": venue_id}},
        upsert=True
    )


def build_personalisation_context(profile):
    if not profile:
        return {
            "team_preference": [],
            "dietary_flags": [],
            "preferred_language": "en",
            "visited_venues": [],
        }
    return {
        "team_preference": profile.get("team_preference", []),
        "dietary_flags": profile.get("dietary_flags", []),
        "preferred_language": profile.get("preferred_language", "en"),
        "visited_venues": profile.get("visited_venues", []),
    }
