import pytest

from backend.app.core.diagnostics import (
    find_option,
    analyze_selected_option,
    increment_misconception,
    get_dominant_misconception
)


SAMPLE_QUESTION = {
    "id": "eq_two_001",

    "skill_id": "two_step_equations",

    "prompt": "Solve: 2x + 5 = 11",

    "options": [
        {
            "id": "A",
            "text": "x = 3",
            "correct": True
        },

        {
            "id": "B",
            "text": "x = 8",
            "correct": False,
            "misconception":
                "inverse_operation_error"
        },

        {
            "id": "C",
            "text": "x = -3",
            "correct": False,
            "misconception":
                "sign_error"
        }
    ]
}


def test_find_valid_option():

    option = find_option(
        question=SAMPLE_QUESTION,
        selected_option_id="B"
    )

    assert option["id"] == "B"


def test_invalid_option_raises_error():

    with pytest.raises(ValueError):

        find_option(
            question=SAMPLE_QUESTION,
            selected_option_id="Z"
        )


def test_correct_option_has_no_misconception():

    result = analyze_selected_option(
        question=SAMPLE_QUESTION,
        selected_option_id="A"
    )

    assert result["correct"] is True

    assert (
        result["misconception"]
        is None
    )

    assert (
        result["misconception_detected"]
        is False
    )


def test_wrong_option_returns_misconception():

    result = analyze_selected_option(
        question=SAMPLE_QUESTION,
        selected_option_id="B"
    )

    assert result["correct"] is False

    assert (
        result["misconception"]
        == "inverse_operation_error"
    )

    assert (
        result["misconception_detected"]
        is True
    )


def test_increment_misconception():

    counts = {}

    increment_misconception(
        counts,
        "sign_error"
    )

    assert counts == {
        "sign_error": 1
    }


def test_increment_existing_misconception():

    counts = {
        "sign_error": 2
    }

    increment_misconception(
        counts,
        "sign_error"
    )

    assert counts[
        "sign_error"
    ] == 3


def test_none_misconception_does_not_change_counts():

    counts = {
        "sign_error": 2
    }

    result = increment_misconception(
        counts,
        None
    )

    assert result == {
        "sign_error": 2
    }


def test_dominant_misconception():

    counts = {
        "sign_error": 3,
        "inverse_operation_error": 1
    }

    result = (
        get_dominant_misconception(
            counts
        )
    )

    assert result == "sign_error"


def test_dominant_requires_minimum_evidence():

    counts = {
        "sign_error": 1
    }

    result = (
        get_dominant_misconception(
            counts,
            minimum_count=2
        )
    )

    assert result is None
from backend.app.core.diagnostics import (
    process_option_diagnostic
)


def test_process_option_updates_fingerprint():

    counts = {}

    result = process_option_diagnostic(
        question=SAMPLE_QUESTION,
        selected_option_id="B",
        misconception_counts=counts
    )

    assert result[
        "misconception"
    ] == "inverse_operation_error"

    assert result[
        "misconception_counts"
    ] == {
        "inverse_operation_error": 1
    }


def test_repeated_misconception_becomes_dominant():

    counts = {}

    process_option_diagnostic(
        question=SAMPLE_QUESTION,
        selected_option_id="B",
        misconception_counts=counts
    )

    result = process_option_diagnostic(
        question=SAMPLE_QUESTION,
        selected_option_id="B",
        misconception_counts=counts
    )

    assert (
        result[
            "dominant_misconception"
        ]
        == "inverse_operation_error"
    )