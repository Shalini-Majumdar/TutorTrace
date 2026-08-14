import pytest

from backend.app.core.diagnostics import (
    get_weakest_prerequisite,
    should_pivot_to_prerequisite
)


PREREQUISITES = {
    "integer_operations": [],

    "one_step_equations": [
        "integer_operations"
    ],

    "order_of_operations": [
        "integer_operations"
    ],

    "two_step_equations": [
        "one_step_equations",
        "order_of_operations"
    ]
}


def test_find_weakest_prerequisite():

    mastery = {
        "two_step_equations": 0.20,
        "one_step_equations": 0.18,
        "order_of_operations": 0.40
    }

    result = get_weakest_prerequisite(
        skill_id="two_step_equations",
        mastery_by_skill=mastery,
        prerequisites=PREREQUISITES
    )

    assert (
        result["skill_id"]
        == "one_step_equations"
    )

    assert (
        result["mastery"]
        == pytest.approx(0.18)
    )


def test_skill_with_no_prerequisite_returns_none():

    mastery = {
        "integer_operations": 0.30
    }

    result = get_weakest_prerequisite(
        skill_id="integer_operations",
        mastery_by_skill=mastery,
        prerequisites=PREREQUISITES
    )

    assert result is None


def test_does_not_pivot_after_only_one_attempt():

    mastery = {
        "two_step_equations": 0.18,
        "one_step_equations": 0.10,
        "order_of_operations": 0.30
    }

    attempts = {
        "two_step_equations": 1
    }

    result = should_pivot_to_prerequisite(
        target_skill_id="two_step_equations",
        mastery_by_skill=mastery,
        attempts_by_skill=attempts,
        prerequisites=PREREQUISITES
    )

    assert (
        result["should_pivot"]
        is False
    )

    assert (
        result["reason"]
        == "insufficient_target_attempts"
    )


def test_does_not_pivot_when_mastery_is_high_enough():

    mastery = {
        "two_step_equations": 0.40,
        "one_step_equations": 0.10,
        "order_of_operations": 0.20
    }

    attempts = {
        "two_step_equations": 4
    }

    result = should_pivot_to_prerequisite(
        target_skill_id="two_step_equations",
        mastery_by_skill=mastery,
        attempts_by_skill=attempts,
        prerequisites=PREREQUISITES
    )

    assert (
        result["should_pivot"]
        is False
    )

    assert (
        result["reason"]
        == "target_mastery_above_threshold"
    )


def test_pivots_to_weakest_prerequisite():

    mastery = {
        "two_step_equations": 0.20,
        "one_step_equations": 0.12,
        "order_of_operations": 0.18
    }

    attempts = {
        "two_step_equations": 3
    }

    result = should_pivot_to_prerequisite(
        target_skill_id="two_step_equations",
        mastery_by_skill=mastery,
        attempts_by_skill=attempts,
        prerequisites=PREREQUISITES
    )

    assert (
        result["should_pivot"]
        is True
    )

    assert (
        result["pivot_skill_id"]
        == "one_step_equations"
    )

    assert (
        result["reason"]
        == "weak_target_with_prerequisite_gap"
    )


def test_does_not_pivot_when_prerequisites_are_stronger():

    mastery = {
        "two_step_equations": 0.20,
        "one_step_equations": 0.75,
        "order_of_operations": 0.60
    }

    attempts = {
        "two_step_equations": 3
    }

    result = should_pivot_to_prerequisite(
        target_skill_id="two_step_equations",
        mastery_by_skill=mastery,
        attempts_by_skill=attempts,
        prerequisites=PREREQUISITES
    )

    assert (
        result["should_pivot"]
        is False
    )

    assert (
        result["reason"]
        == "prerequisites_not_weaker"
    )