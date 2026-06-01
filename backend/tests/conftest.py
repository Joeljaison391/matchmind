import sys
from pathlib import Path

# make backend/ importable from tests/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

FAKE_EMBEDDING = [0.01] * 768


@pytest.fixture
def fake_embedding():
    return FAKE_EMBEDDING


@pytest.fixture
def sample_venue():
    return {
        "venue_id": "metlife_stadium",
        "stadium_name": "MetLife Stadium",
        "city": "East Rutherford",
        "country": "USA",
        "description": "Largest stadium in the 2026 World Cup.",
        "description_embedding": [],
    }


@pytest.fixture
def sample_faq():
    return {
        "question": "When does Brazil play in the group stage?",
        "answer": "Brazil are in Group C and play three group stage matches.",
        "tags": ["team", "Brazil", "schedule"],
    }


@pytest.fixture
def mock_db(mocker):
    db = mocker.MagicMock()
    db.venues.find.return_value = []
    db.faq_embeddings.drop.return_value = None
    db.faq_embeddings.insert_many.return_value = mocker.MagicMock(inserted_ids=[])
    return db
