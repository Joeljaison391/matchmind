import pytest
from scripts.seed_businesses import load_and_insert


def test_seed_businesses_inserts_all(mocker, mock_db, tmp_path):
    import json
    biz = [
        {
            "name": f"Place {i}", "category": "restaurant", "cuisine": "American",
            "halal_flag": False, "vegan_flag": False,
            "coords": {"lat": 40.8, "lng": -74.0},
            "distance_to_venue_m": 500, "description": "A great place to eat near the stadium.",
            "description_embedding": [], "address": f"{i} Main St",
            "price_range": "$$", "rating": 4.0,
            "venue_id": "metlife_stadium", "city": "East Rutherford",
        }
        for i in range(10)
    ]
    biz_file = tmp_path / "businesses.json"
    biz_file.write_text(json.dumps(biz))
    mocker.patch("scripts.seed_businesses.SEED_DIR", tmp_path)

    load_and_insert(mock_db)

    mock_db.local_businesses.drop.assert_called_once()
    inserted = mock_db.local_businesses.insert_many.call_args[0][0]
    assert len(inserted) == 10


def test_seed_businesses_drops_first(mocker, mock_db, tmp_path):
    import json
    biz_file = tmp_path / "businesses.json"
    biz_file.write_text(json.dumps([
        {
            "name": "Test", "category": "restaurant", "cuisine": "American",
            "halal_flag": False, "vegan_flag": False,
            "coords": {"lat": 40.8, "lng": -74.0},
            "distance_to_venue_m": 300, "description": "Good food near the stadium area.",
            "description_embedding": [], "address": "1 Test St",
            "price_range": "$", "rating": 3.5,
            "venue_id": "metlife_stadium", "city": "East Rutherford",
        }
    ]))
    mocker.patch("scripts.seed_businesses.SEED_DIR", tmp_path)

    load_and_insert(mock_db)

    mock_db.local_businesses.drop.assert_called_once()


def test_seed_businesses_creates_index(mocker, mock_db, tmp_path):
    import json
    biz_file = tmp_path / "businesses.json"
    biz_file.write_text(json.dumps([
        {
            "name": "Test", "category": "bar", "cuisine": "American",
            "halal_flag": False, "vegan_flag": True,
            "coords": {"lat": 40.8, "lng": -74.0},
            "distance_to_venue_m": 400, "description": "Lively sports bar near the venue entrance.",
            "description_embedding": [], "address": "2 Test Ave",
            "price_range": "$$", "rating": 4.2,
            "venue_id": "metlife_stadium", "city": "East Rutherford",
        }
    ]))
    mocker.patch("scripts.seed_businesses.SEED_DIR", tmp_path)

    load_and_insert(mock_db)

    mock_db.local_businesses.create_index.assert_called()
