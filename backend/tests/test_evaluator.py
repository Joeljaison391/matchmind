import json
import pytest
from api.evaluator import score_response, passes_threshold


def make_eval_result(mocker, scores):
    result = mocker.MagicMock()
    result.text = json.dumps(scores)
    return result


SCORES_GOOD = {"relevance": 0.8, "completeness": 0.9, "accuracy": 0.85}
SCORES_BAD = {"relevance": 0.5, "completeness": 0.4, "accuracy": 0.6}


# --- score_response ---

def test_score_response_returns_dict(mocker):
    mocker.patch("api.evaluator.gemini.models.generate_content",
                 return_value=make_eval_result(mocker, SCORES_GOOD))
    result = score_response("When does Brazil play?", "Brazil plays at 3pm.")
    assert isinstance(result, dict)


def test_score_response_has_avg(mocker):
    mocker.patch("api.evaluator.gemini.models.generate_content",
                 return_value=make_eval_result(mocker, SCORES_GOOD))
    result = score_response("q", "a")
    assert "avg" in result


def test_score_response_has_all_dimensions(mocker):
    mocker.patch("api.evaluator.gemini.models.generate_content",
                 return_value=make_eval_result(mocker, SCORES_GOOD))
    result = score_response("q", "a")
    assert "relevance" in result
    assert "completeness" in result
    assert "accuracy" in result


def test_score_response_avg_is_mean(mocker):
    mocker.patch("api.evaluator.gemini.models.generate_content",
                 return_value=make_eval_result(mocker, {"relevance": 1.0, "completeness": 1.0, "accuracy": 1.0}))
    result = score_response("q", "a")
    assert result["avg"] == 1.0


def test_score_response_avg_calculation(mocker):
    mocker.patch("api.evaluator.gemini.models.generate_content",
                 return_value=make_eval_result(mocker, SCORES_GOOD))
    result = score_response("q", "a")
    expected = round((0.8 + 0.9 + 0.85) / 3, 4)
    assert result["avg"] == expected


def test_score_response_calls_gemini(mocker):
    mock = mocker.patch("api.evaluator.gemini.models.generate_content",
                        return_value=make_eval_result(mocker, SCORES_GOOD))
    score_response("q", "a")
    mock.assert_called_once()


def test_score_response_with_context(mocker):
    mock = mocker.patch("api.evaluator.gemini.models.generate_content",
                        return_value=make_eval_result(mocker, SCORES_GOOD))
    score_response("q", "a", context="Brazil is in Group C")
    _, kwargs = mock.call_args
    assert "Brazil is in Group C" in kwargs.get("contents", "")


# --- passes_threshold ---

def test_passes_threshold_above():
    assert passes_threshold({"avg": 0.85}) is True


def test_passes_threshold_below():
    assert passes_threshold({"avg": 0.50}) is False


def test_passes_threshold_exact():
    # exactly 0.75 should pass
    assert passes_threshold({"avg": 0.75}) is True


def test_passes_threshold_custom_value():
    assert passes_threshold({"avg": 0.60}, threshold=0.50) is True


def test_passes_threshold_custom_value_fail():
    assert passes_threshold({"avg": 0.60}, threshold=0.70) is False
