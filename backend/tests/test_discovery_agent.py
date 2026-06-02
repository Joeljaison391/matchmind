import pytest
from agents.discovery_agent import vector_search_faqs, hybrid_search_businesses, build_faq_answer

FAKE_EMBEDDING = [0.01] * 768

SAMPLE_FAQ_RESULT = {
    "question": "Which group is Brazil in?",
    "answer": "Brazil are in Group C.",
    "tags": ["team", "Brazil"],
    "score": 0.92
}

SAMPLE_BUSINESS = {
    "name": "Al Madina Halal Grill",
    "category": "restaurant",
    "cuisine": "Middle Eastern",
    "halal_flag": True,
    "vegan_flag": False,
    "rating": 4.5,
    "price_range": "$$",
    "distance_to_venue_m": 350,
    "address": "123 Main St, East Rutherford"
}


# --- vector_search_faqs ---

def test_vector_search_faqs_returns_list(mock_db):
    mock_db.faq_embeddings.aggregate.return_value = [SAMPLE_FAQ_RESULT]
    result = vector_search_faqs(mock_db, FAKE_EMBEDDING)
    assert isinstance(result, list)


def test_vector_search_faqs_uses_pipeline(mock_db):
    mock_db.faq_embeddings.aggregate.return_value = []
    vector_search_faqs(mock_db, FAKE_EMBEDDING)
    pipeline = mock_db.faq_embeddings.aggregate.call_args[0][0]
    assert pipeline[0].get("$vectorSearch") is not None


def test_vector_search_faqs_correct_index(mock_db):
    mock_db.faq_embeddings.aggregate.return_value = []
    vector_search_faqs(mock_db, FAKE_EMBEDDING)
    pipeline = mock_db.faq_embeddings.aggregate.call_args[0][0]
    assert pipeline[0]["$vectorSearch"]["index"] == "faq_embeddings"


def test_vector_search_faqs_correct_path(mock_db):
    mock_db.faq_embeddings.aggregate.return_value = []
    vector_search_faqs(mock_db, FAKE_EMBEDDING)
    pipeline = mock_db.faq_embeddings.aggregate.call_args[0][0]
    assert pipeline[0]["$vectorSearch"]["path"] == "embedding"


def test_vector_search_faqs_passes_embedding(mock_db):
    mock_db.faq_embeddings.aggregate.return_value = []
    vector_search_faqs(mock_db, FAKE_EMBEDDING)
    pipeline = mock_db.faq_embeddings.aggregate.call_args[0][0]
    assert pipeline[0]["$vectorSearch"]["queryVector"] == FAKE_EMBEDDING


def test_vector_search_faqs_default_limit(mock_db):
    mock_db.faq_embeddings.aggregate.return_value = []
    vector_search_faqs(mock_db, FAKE_EMBEDDING)
    pipeline = mock_db.faq_embeddings.aggregate.call_args[0][0]
    assert pipeline[0]["$vectorSearch"]["limit"] == 5


# --- hybrid_search_businesses ---

def test_hybrid_search_returns_list(mock_db):
    mock_db.local_businesses.aggregate.return_value = [SAMPLE_BUSINESS]
    result = hybrid_search_businesses(mock_db, FAKE_EMBEDDING, "metlife_stadium")
    assert isinstance(result, list)


def test_hybrid_search_uses_vector_search(mock_db):
    mock_db.local_businesses.aggregate.return_value = []
    hybrid_search_businesses(mock_db, FAKE_EMBEDDING, "metlife_stadium")
    pipeline = mock_db.local_businesses.aggregate.call_args[0][0]
    stages = [list(s.keys())[0] for s in pipeline]
    assert "$vectorSearch" in stages


def test_hybrid_search_filters_by_venue(mock_db):
    mock_db.local_businesses.aggregate.return_value = []
    hybrid_search_businesses(mock_db, FAKE_EMBEDDING, "metlife_stadium")
    pipeline = mock_db.local_businesses.aggregate.call_args[0][0]
    vs = pipeline[0]["$vectorSearch"]
    assert vs.get("filter", {}).get("venue_id") == "metlife_stadium"


def test_hybrid_search_halal_filter(mock_db):
    mock_db.local_businesses.aggregate.return_value = []
    hybrid_search_businesses(mock_db, FAKE_EMBEDDING, "metlife_stadium", dietary_flags=["halal"])
    pipeline = mock_db.local_businesses.aggregate.call_args[0][0]
    vs = pipeline[0]["$vectorSearch"]
    assert vs["filter"].get("halal_flag") is True


# --- build_faq_answer ---

def test_build_faq_answer_structure():
    answer = build_faq_answer([SAMPLE_FAQ_RESULT])
    assert "question" in answer
    assert "answer" in answer
    assert "score" in answer


def test_build_faq_answer_picks_top_result():
    results = [SAMPLE_FAQ_RESULT, {**SAMPLE_FAQ_RESULT, "score": 0.5}]
    answer = build_faq_answer(results)
    assert answer["score"] == 0.92


def test_build_faq_answer_empty_returns_none():
    assert build_faq_answer([]) is None
