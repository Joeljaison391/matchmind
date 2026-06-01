import pytest
from unittest.mock import patch, MagicMock, call
from scripts.embed_data import get_embedding, embed_venues, embed_faqs, build_faq_doc

FAKE_EMBEDDING = [0.01] * 768


# --- get_embedding ---

def test_get_embedding_returns_list(mocker):
    mocker.patch("scripts.embed_data.genai.embed_content", return_value={"embedding": FAKE_EMBEDDING})
    result = get_embedding("some text")
    assert isinstance(result, list)


def test_get_embedding_returns_768_dims(mocker):
    mocker.patch("scripts.embed_data.genai.embed_content", return_value={"embedding": FAKE_EMBEDDING})
    result = get_embedding("some text")
    assert len(result) == 768


def test_get_embedding_calls_correct_model(mocker):
    mock = mocker.patch("scripts.embed_data.genai.embed_content", return_value={"embedding": FAKE_EMBEDDING})
    get_embedding("hello")
    args, kwargs = mock.call_args
    assert kwargs.get("model") == "models/text-embedding-004"


def test_get_embedding_passes_text(mocker):
    mock = mocker.patch("scripts.embed_data.genai.embed_content", return_value={"embedding": FAKE_EMBEDDING})
    get_embedding("test content")
    args, kwargs = mock.call_args
    assert kwargs.get("content") == "test content"


# --- embed_venues ---

def test_embed_venues_calls_update_for_each(mocker, mock_db):
    venues = [
        {"venue_id": "metlife_stadium", "stadium_name": "MetLife Stadium", "city": "East Rutherford", "country": "USA", "description": "Big stadium."},
        {"venue_id": "att_stadium", "stadium_name": "AT&T Stadium", "city": "Arlington", "country": "USA", "description": "Dallas stadium."},
    ]
    mock_db.venues.find.return_value = venues
    mocker.patch("scripts.embed_data.get_embedding", return_value=FAKE_EMBEDDING)

    embed_venues(mock_db)

    assert mock_db.venues.update_one.call_count == 2


def test_embed_venues_sets_description_embedding(mocker, mock_db):
    venues = [{"venue_id": "metlife_stadium", "stadium_name": "MetLife Stadium", "city": "East Rutherford", "country": "USA", "description": "Big."}]
    mock_db.venues.find.return_value = venues
    mocker.patch("scripts.embed_data.get_embedding", return_value=FAKE_EMBEDDING)

    embed_venues(mock_db)

    call_args = mock_db.venues.update_one.call_args
    update_doc = call_args[0][1]
    assert "description_embedding" in update_doc["$set"]
    assert len(update_doc["$set"]["description_embedding"]) == 768


def test_embed_venues_filters_by_venue_id(mocker, mock_db):
    venues = [{"venue_id": "bc_place", "stadium_name": "BC Place", "city": "Vancouver", "country": "Canada", "description": "Vancouver stadium."}]
    mock_db.venues.find.return_value = venues
    mocker.patch("scripts.embed_data.get_embedding", return_value=FAKE_EMBEDDING)

    embed_venues(mock_db)

    filter_doc = mock_db.venues.update_one.call_args[0][0]
    assert filter_doc == {"venue_id": "bc_place"}


# --- build_faq_doc ---

def test_build_faq_doc_structure():
    faq = {"question": "Q?", "answer": "A.", "tags": ["tag1"]}
    doc = build_faq_doc(faq, FAKE_EMBEDDING)
    assert doc["question"] == "Q?"
    assert doc["answer"] == "A."
    assert doc["tags"] == ["tag1"]
    assert doc["embedding"] == FAKE_EMBEDDING


def test_build_faq_doc_embedding_length():
    faq = {"question": "Q?", "answer": "A.", "tags": []}
    doc = build_faq_doc(faq, FAKE_EMBEDDING)
    assert len(doc["embedding"]) == 768


# --- embed_faqs ---

def test_embed_faqs_inserts_correct_count(mocker, mock_db, tmp_path):
    faqs = [
        {"question": f"Q{i}?", "answer": f"Answer number {i}.", "tags": ["test"]}
        for i in range(5)
    ]
    faq_file = tmp_path / "faqs.json"
    import json
    faq_file.write_text(json.dumps(faqs))

    mocker.patch("scripts.embed_data.get_embedding", return_value=FAKE_EMBEDDING)
    mocker.patch("scripts.embed_data.SEED_DIR", tmp_path)

    embed_faqs(mock_db)

    inserted = mock_db.faq_embeddings.insert_many.call_args[0][0]
    assert len(inserted) == 5


def test_embed_faqs_drops_collection_first(mocker, mock_db, tmp_path):
    import json
    faq_file = tmp_path / "faqs.json"
    faq_file.write_text(json.dumps([{"question": "Q?", "answer": "An answer here.", "tags": []}]))

    mocker.patch("scripts.embed_data.get_embedding", return_value=FAKE_EMBEDDING)
    mocker.patch("scripts.embed_data.SEED_DIR", tmp_path)

    embed_faqs(mock_db)

    mock_db.faq_embeddings.drop.assert_called_once()


def test_embed_faqs_combines_question_and_answer_for_embedding(mocker, mock_db, tmp_path):
    import json
    faq_file = tmp_path / "faqs.json"
    faq_file.write_text(json.dumps([{"question": "When does France play?", "answer": "France plays in Group I.", "tags": []}]))

    mock_embed = mocker.patch("scripts.embed_data.get_embedding", return_value=FAKE_EMBEDDING)
    mocker.patch("scripts.embed_data.SEED_DIR", tmp_path)

    embed_faqs(mock_db)

    text_used = mock_embed.call_args[0][0]
    assert "When does France play?" in text_used
    assert "France plays in Group I." in text_used


# --- integration (skipped unless -m integration) ---

@pytest.mark.integration
def test_real_embedding_from_gemini():
    from scripts.embed_data import get_embedding
    result = get_embedding("Which group is Brazil in for the 2026 World Cup?")
    assert len(result) == 768
    assert all(isinstance(v, float) for v in result)
