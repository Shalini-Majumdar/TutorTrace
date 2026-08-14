import pytest
import json
from pathlib import Path

import pytest
from backend.app.core.cold_start import (
    initialize_student_skills,
    create_initial_student_state,
    get_next_cold_start_skill,
    mark_cold_start_probe_completed
)


BKT_PARAMS = {
    "integer_operations": {
        "p_l0": 0.72,
        "p_t": 0.01,
        "p_g": 0.37,
        "p_s": 0.21
    },

    "one_step_equations": {
        "p_l0": 0.62,
        "p_t": 0.02,
        "p_g": 0.36,
        "p_s": 0.23
    },

    "two_step_equations": {
        "p_l0": 0.61,
        "p_t": 0.15,
        "p_g": 0.33,
        "p_s": 0.20
    }
}


def test_initial_mastery_comes_from_p_l0():

    skills = initialize_student_skills(
        BKT_PARAMS
    )

    assert (
        skills["integer_operations"]["mastery"]
        == pytest.approx(0.72)
    )

    assert (
        skills["one_step_equations"]["mastery"]
        == pytest.approx(0.62)
    )


def test_initial_attempt_counts_are_zero():

    skills = initialize_student_skills(
        BKT_PARAMS
    )

    for skill in skills.values():

        assert skill["attempts"] == 0
        assert skill["correct_attempts"] == 0
        assert skill["uncertainty_count"] == 0


def test_initial_last_practiced_is_none():

    skills = initialize_student_skills(
        BKT_PARAMS
    )

    for skill in skills.values():

        assert (
            skill["last_practiced_at"]
            is None
        )


def test_initial_student_state():

    state = create_initial_student_state(
        student_id="student_001",
        bkt_params=BKT_PARAMS
    )

    assert (
        state["student_id"]
        == "student_001"
    )

    assert (
        state["cold_start"]["completed"]
        is False
    )

    assert (
        state["cold_start"]["completed_probe_skills"]
        == []
    )


def test_first_probe_is_integer_operations():

    state = create_initial_student_state(
        student_id="student_001",
        bkt_params=BKT_PARAMS
    )

    result = get_next_cold_start_skill(
        state
    )

    assert result == "integer_operations"


def test_second_probe_after_first_completed():

    state = create_initial_student_state(
        student_id="student_001",
        bkt_params=BKT_PARAMS
    )

    mark_cold_start_probe_completed(
        state,
        "integer_operations"
    )

    result = get_next_cold_start_skill(
        state
    )

    assert result == "one_step_equations"


def test_cold_start_completes_after_three_probes():

    state = create_initial_student_state(
        student_id="student_001",
        bkt_params=BKT_PARAMS
    )

    mark_cold_start_probe_completed(
        state,
        "integer_operations"
    )

    mark_cold_start_probe_completed(
        state,
        "one_step_equations"
    )

    mark_cold_start_probe_completed(
        state,
        "two_step_equations"
    )

    assert (
        state["cold_start"]["completed"]
        is True
    )

    assert (
        get_next_cold_start_skill(
            state
        )
        is None
    )


def test_unprobed_skill_keeps_original_prior():

    state = create_initial_student_state(
        student_id="student_001",
        bkt_params=BKT_PARAMS
    )

    original = state[
        "skills"
    ][
        "two_step_equations"
    ][
        "mastery"
    ]

    mark_cold_start_probe_completed(
        state,
        "integer_operations"
    )

    assert (
        state[
            "skills"
        ][
            "two_step_equations"
        ][
            "mastery"
        ]
        == original
    )
def test_real_tutortrace_initialization_uses_fitted_priors():

    params_path = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "bkt_params.json"
    )

    with open(
        params_path,
        "r",
        encoding="utf-8"
    ) as file:

        params = json.load(file)

    state = create_initial_student_state(
        student_id="student_real_test",
        bkt_params=params
    )

    assert (
        len(state["skills"])
        == 8
    )

    for skill_id, skill_params in params.items():

        assert (
            state["skills"][skill_id]["mastery"]
            == pytest.approx(
                skill_params["p_l0"]
            )
        )