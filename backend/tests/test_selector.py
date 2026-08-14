import random

import pytest

from backend.app.core.adaptive_selector import (
    get_unused_questions,
    get_questions_for_skill,
    get_questions_for_misconception,
    find_weakest_skill,
    find_prerequisite_pivot,
    select_next_question
)


QUESTION_BANK = [
    {
        "id": "int_001",
        "skill_id": "integer_operations",
        "targets_misconceptions": []
    },

    {
        "id": "int_002",
        "skill_id": "integer_operations",
        "targets_misconceptions": [
            "sign_error"
        ]
    },

    {
        "id": "one_001",
        "skill_id": "one_step_equations",
        "targets_misconceptions": [
            "inverse_operation_error"
        ]
    },

    {
        "id": "one_002",
        "skill_id": "one_step_equations",
        "targets_misconceptions": []
    },

    {
        "id": "two_001",
        "skill_id": "two_step_equations",
        "targets_misconceptions": [
            "inverse_operation_error"
        ]
    },

    {
        "id": "order_001",
        "skill_id": "order_of_operations",
        "targets_misconceptions": []
    }
]


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


def make_student_state():
    """
    Default state represents a student who has already
    completed the three cold-start probes.

    This prevents cold-start logic from interfering with
    tests for the later selector priorities.
    """

    return {
        "student_id": "student_test",

        "skills": {
            "integer_operations": {
                "mastery": 0.60,
                "attempts": 2
            },

            "one_step_equations": {
                "mastery": 0.40,
                "attempts": 2
            },

            "order_of_operations": {
                "mastery": 0.50,
                "attempts": 2
            },

            "two_step_equations": {
                "mastery": 0.30,
                "attempts": 2
            }
        },

        "misconceptions": {},

        "asked_question_ids": [],

        "active_diagnosis": None,

        "cold_start": {
            "completed": True,

            "probe_skills": [
                "integer_operations",
                "one_step_equations",
                "two_step_equations"
            ],

            "completed_probe_skills": [
                "integer_operations",
                "one_step_equations",
                "two_step_equations"
            ]
        }
    }


def test_unused_questions_excludes_asked():

    result = get_unused_questions(
        question_bank=QUESTION_BANK,
        asked_question_ids=[
            "int_001"
        ]
    )

    ids = [
        question["id"]
        for question in result
    ]

    assert "int_001" not in ids


def test_questions_for_skill():

    result = get_questions_for_skill(
        questions=QUESTION_BANK,
        skill_id="one_step_equations"
    )

    assert len(result) == 2

    assert all(
        question["skill_id"]
        == "one_step_equations"
        for question in result
    )


def test_questions_for_misconception():

    result = get_questions_for_misconception(
        questions=QUESTION_BANK,
        misconception="inverse_operation_error"
    )

    ids = {
        question["id"]
        for question in result
    }

    assert ids == {
        "one_001",
        "two_001"
    }


def test_find_weakest_skill():

    state = make_student_state()

    result = find_weakest_skill(
        state
    )

    assert (
        result
        == "two_step_equations"
    )


# ==========================================================
# COLD START TESTS
# ==========================================================

def test_cold_start_first_probe_has_highest_priority():

    state = make_student_state()

    state["cold_start"] = {
        "completed": False,

        "probe_skills": [
            "integer_operations",
            "one_step_equations",
            "two_step_equations"
        ],

        "completed_probe_skills": []
    }

    result = select_next_question(
        student_state=state,
        question_bank=QUESTION_BANK,
        prerequisites=PREREQUISITES,
        epsilon=0,
        rng=random.Random(42)
    )

    assert (
        result[
            "selection_reason"
        ]["type"]
        == "cold_start_coverage"
    )

    assert (
        result["question"]["skill_id"]
        == "integer_operations"
    )

    assert (
        result[
            "selection_reason"
        ]["probe_number"]
        == 1
    )

    assert (
        result[
            "selection_reason"
        ]["total_probes"]
        == 3
    )


def test_cold_start_second_probe():

    state = make_student_state()

    state["cold_start"] = {
        "completed": False,

        "probe_skills": [
            "integer_operations",
            "one_step_equations",
            "two_step_equations"
        ],

        "completed_probe_skills": [
            "integer_operations"
        ]
    }

    state["asked_question_ids"] = [
        "int_001"
    ]

    result = select_next_question(
        student_state=state,
        question_bank=QUESTION_BANK,
        prerequisites=PREREQUISITES,
        epsilon=0,
        rng=random.Random(42)
    )

    assert (
        result[
            "selection_reason"
        ]["type"]
        == "cold_start_coverage"
    )

    assert (
        result["question"]["skill_id"]
        == "one_step_equations"
    )

    assert (
        result[
            "selection_reason"
        ]["probe_number"]
        == 2
    )


def test_cold_start_third_probe():

    state = make_student_state()

    state["cold_start"] = {
        "completed": False,

        "probe_skills": [
            "integer_operations",
            "one_step_equations",
            "two_step_equations"
        ],

        "completed_probe_skills": [
            "integer_operations",
            "one_step_equations"
        ]
    }

    state["asked_question_ids"] = [
        "int_001",
        "one_001"
    ]

    result = select_next_question(
        student_state=state,
        question_bank=QUESTION_BANK,
        prerequisites=PREREQUISITES,
        epsilon=0,
        rng=random.Random(42)
    )

    assert (
        result[
            "selection_reason"
        ]["type"]
        == "cold_start_coverage"
    )

    assert (
        result["question"]["skill_id"]
        == "two_step_equations"
    )

    assert (
        result[
            "selection_reason"
        ]["probe_number"]
        == 3
    )


# ==========================================================
# PREREQUISITE DIAGNOSIS
# ==========================================================

def test_active_diagnosis_priority():

    state = make_student_state()

    state["active_diagnosis"] = {
        "target_skill":
            "two_step_equations",

        "diagnostic_skill":
            "one_step_equations"
    }

    result = select_next_question(
        student_state=state,
        question_bank=QUESTION_BANK,
        prerequisites=PREREQUISITES,
        epsilon=0,
        rng=random.Random(42)
    )

    assert (
        result[
            "selection_reason"
        ]["type"]
        == "active_prerequisite_diagnosis"
    )

    assert (
        result["question"]["skill_id"]
        == "one_step_equations"
    )


def test_new_prerequisite_pivot():

    state = make_student_state()

    state["skills"][
        "two_step_equations"
    ]["mastery"] = 0.20

    state["skills"][
        "two_step_equations"
    ]["attempts"] = 3

    state["skills"][
        "one_step_equations"
    ]["mastery"] = 0.10

    state["skills"][
        "order_of_operations"
    ]["mastery"] = 0.18

    result = select_next_question(
        student_state=state,
        question_bank=QUESTION_BANK,
        prerequisites=PREREQUISITES,
        epsilon=0,
        rng=random.Random(42)
    )

    assert (
        result[
            "selection_reason"
        ]["type"]
        == "prerequisite_diagnosis"
    )

    assert (
        result[
            "selection_reason"
        ]["target_skill"]
        == "two_step_equations"
    )

    assert (
        result[
            "selection_reason"
        ]["diagnostic_skill"]
        == "one_step_equations"
    )

    assert (
        result["question"]["skill_id"]
        == "one_step_equations"
    )


def test_find_prerequisite_pivot():

    state = make_student_state()

    state["skills"][
        "two_step_equations"
    ]["mastery"] = 0.20

    state["skills"][
        "two_step_equations"
    ]["attempts"] = 3

    state["skills"][
        "one_step_equations"
    ]["mastery"] = 0.10

    state["skills"][
        "order_of_operations"
    ]["mastery"] = 0.18

    result = find_prerequisite_pivot(
        student_state=state,
        prerequisites=PREREQUISITES
    )

    assert result is not None

    assert (
        result["target_skill_id"]
        == "two_step_equations"
    )

    assert (
        result["pivot_skill_id"]
        == "one_step_equations"
    )


# ==========================================================
# MISCONCEPTION PRIORITY
# ==========================================================

def test_repeated_misconception_priority():

    state = make_student_state()

    state["misconceptions"] = {
        "inverse_operation_error": 3
    }

    result = select_next_question(
        student_state=state,
        question_bank=QUESTION_BANK,
        prerequisites=PREREQUISITES,
        epsilon=0,
        rng=random.Random(42)
    )

    assert (
        result[
            "selection_reason"
        ]["type"]
        == "misconception_investigation"
    )

    assert (
        "inverse_operation_error"
        in result[
            "question"
        ].get(
            "targets_misconceptions",
            []
        )
    )


# ==========================================================
# NORMAL ADAPTIVE SELECTION
# ==========================================================

def test_weakest_mastery_selected_when_no_other_signal():

    state = make_student_state()

    result = select_next_question(
        student_state=state,
        question_bank=QUESTION_BANK,
        prerequisites=PREREQUISITES,
        epsilon=0,
        rng=random.Random(42)
    )

    assert (
        result[
            "selection_reason"
        ]["type"]
        == "weakest_mastery"
    )

    assert (
        result["question"]["skill_id"]
        == "two_step_equations"
    )


def test_epsilon_one_forces_exploration():

    state = make_student_state()

    result = select_next_question(
        student_state=state,
        question_bank=QUESTION_BANK,
        prerequisites=PREREQUISITES,
        epsilon=1.0,
        rng=random.Random(42)
    )

    assert (
        result[
            "selection_reason"
        ]["type"]
        == "epsilon_exploration"
    )


# ==========================================================
# ERROR CASES
# ==========================================================

def test_invalid_epsilon():

    state = make_student_state()

    with pytest.raises(ValueError):

        select_next_question(
            student_state=state,
            question_bank=QUESTION_BANK,
            prerequisites=PREREQUISITES,
            epsilon=1.5
        )


def test_no_unused_questions_raises_error():

    state = make_student_state()

    state["asked_question_ids"] = [
        question["id"]
        for question in QUESTION_BANK
    ]

    with pytest.raises(ValueError):

        select_next_question(
            student_state=state,
            question_bank=QUESTION_BANK,
            prerequisites=PREREQUISITES
        )