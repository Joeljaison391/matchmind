import json
from pathlib import Path

FAQS_PATH = Path(__file__).parent.parent / "data" / "seed" / "faqs.json"


def load_faqs():
    return json.loads(FAQS_PATH.read_text(encoding="utf-8"))


def test_faqs_file_exists():
    assert FAQS_PATH.exists(), "faqs.json not found"


def test_faqs_count():
    faqs = load_faqs()
    assert len(faqs) >= 200, f"need at least 200 FAQs, got {len(faqs)}"


def test_every_faq_has_required_fields():
    faqs = load_faqs()
    for i, faq in enumerate(faqs):
        assert "question" in faq, f"FAQ {i} missing question"
        assert "answer" in faq, f"FAQ {i} missing answer"
        assert "tags" in faq, f"FAQ {i} missing tags"


def test_no_empty_questions_or_answers():
    faqs = load_faqs()
    for i, faq in enumerate(faqs):
        assert faq["question"].strip(), f"FAQ {i} has empty question"
        assert faq["answer"].strip(), f"FAQ {i} has empty answer"


def test_tags_are_lists():
    faqs = load_faqs()
    for i, faq in enumerate(faqs):
        assert isinstance(faq["tags"], list), f"FAQ {i} tags must be a list"


def test_no_duplicate_questions():
    faqs = load_faqs()
    questions = [f["question"] for f in faqs]
    assert len(questions) == len(set(questions)), "duplicate questions found in faqs.json"


def test_answers_are_meaningful():
    faqs = load_faqs()
    for i, faq in enumerate(faqs):
        assert len(faq["answer"]) >= 20, f"FAQ {i} answer too short: '{faq['answer']}'"
