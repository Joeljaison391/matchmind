import json
from pathlib import Path

BUSINESSES_PATH = Path(__file__).parent.parent / "data" / "seed" / "businesses.json"

REQUIRED_FIELDS = [
    "name", "category", "cuisine", "halal_flag", "vegan_flag",
    "coords", "distance_to_venue_m", "description",
    "description_embedding", "address", "price_range", "rating",
    "venue_id", "city",
]

VALID_CATEGORIES = {"restaurant", "bar", "sports_bar", "hotel", "cafe", "fast_food", "attraction"}
VALID_PRICE_RANGES = {"$", "$$", "$$$", "$$$$"}
EXPECTED_VENUE_IDS = {
    "metlife_stadium", "att_stadium", "sofi_stadium",
    "mercedes_benz_stadium", "hard_rock_stadium",
}


def load_businesses():
    return json.loads(BUSINESSES_PATH.read_text(encoding="utf-8"))


def test_businesses_file_exists():
    assert BUSINESSES_PATH.exists(), "businesses.json not found"


def test_businesses_total_count():
    biz = load_businesses()
    assert len(biz) >= 2500, f"need at least 2500 businesses, got {len(biz)}"


def test_every_business_has_required_fields():
    biz = load_businesses()
    for i, b in enumerate(biz):
        for field in REQUIRED_FIELDS:
            assert field in b, f"business {i} ({b.get('name', '?')}) missing field: {field}"


def test_no_empty_names_or_descriptions():
    biz = load_businesses()
    for i, b in enumerate(biz):
        assert b["name"].strip(), f"business {i} has empty name"
        assert b["description"].strip(), f"business {i} has empty description"


def test_descriptions_are_meaningful():
    biz = load_businesses()
    for i, b in enumerate(biz):
        assert len(b["description"]) >= 30, f"business {i} description too short: '{b['description']}'"


def test_flags_are_booleans():
    biz = load_businesses()
    for i, b in enumerate(biz):
        assert isinstance(b["halal_flag"], bool), f"business {i} halal_flag must be bool"
        assert isinstance(b["vegan_flag"], bool), f"business {i} vegan_flag must be bool"


def test_coords_have_lat_lng():
    biz = load_businesses()
    for i, b in enumerate(biz):
        assert "lat" in b["coords"], f"business {i} coords missing lat"
        assert "lng" in b["coords"], f"business {i} coords missing lng"
        assert isinstance(b["coords"]["lat"], float), f"business {i} lat must be float"
        assert isinstance(b["coords"]["lng"], float), f"business {i} lng must be float"


def test_distances_are_reasonable():
    biz = load_businesses()
    for i, b in enumerate(biz):
        d = b["distance_to_venue_m"]
        assert 50 <= d <= 5000, f"business {i} distance out of range: {d}m"


def test_ratings_in_range():
    biz = load_businesses()
    for i, b in enumerate(biz):
        assert 1.0 <= b["rating"] <= 5.0, f"business {i} rating out of range: {b['rating']}"


def test_valid_categories():
    biz = load_businesses()
    for i, b in enumerate(biz):
        assert b["category"] in VALID_CATEGORIES, f"business {i} invalid category: {b['category']}"


def test_valid_price_ranges():
    biz = load_businesses()
    for i, b in enumerate(biz):
        assert b["price_range"] in VALID_PRICE_RANGES, f"business {i} invalid price_range: {b['price_range']}"


def test_all_five_cities_represented():
    biz = load_businesses()
    venue_ids = {b["venue_id"] for b in biz}
    for vid in EXPECTED_VENUE_IDS:
        assert vid in venue_ids, f"no businesses found for venue: {vid}"


def test_each_city_has_500_businesses():
    biz = load_businesses()
    from collections import Counter
    counts = Counter(b["venue_id"] for b in biz)
    for vid in EXPECTED_VENUE_IDS:
        assert counts[vid] >= 500, f"{vid} only has {counts[vid]} businesses, need 500"


def test_each_city_has_halal_options():
    biz = load_businesses()
    from collections import defaultdict
    halal_by_city = defaultdict(int)
    total_by_city = defaultdict(int)
    for b in biz:
        total_by_city[b["venue_id"]] += 1
        if b["halal_flag"]:
            halal_by_city[b["venue_id"]] += 1
    for vid in EXPECTED_VENUE_IDS:
        pct = halal_by_city[vid] / total_by_city[vid]
        assert pct >= 0.08, f"{vid} only {pct:.0%} halal options, need at least 8%"


def test_each_city_has_vegan_options():
    biz = load_businesses()
    from collections import defaultdict
    vegan_by_city = defaultdict(int)
    total_by_city = defaultdict(int)
    for b in biz:
        total_by_city[b["venue_id"]] += 1
        if b["vegan_flag"]:
            vegan_by_city[b["venue_id"]] += 1
    for vid in EXPECTED_VENUE_IDS:
        pct = vegan_by_city[vid] / total_by_city[vid]
        assert pct >= 0.08, f"{vid} only {pct:.0%} vegan options, need at least 8%"


def test_description_embedding_is_empty_list():
    # embeddings are populated later by embed_businesses.py, seed has []
    biz = load_businesses()
    for i, b in enumerate(biz):
        assert isinstance(b["description_embedding"], list), f"business {i} embedding must be list"
