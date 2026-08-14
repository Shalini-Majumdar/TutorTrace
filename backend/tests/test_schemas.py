import pytest
from pydantic import ValidationError

from backend.app.models.schemas import (
    SkillState,
    StudentState,
    ActiveDiagnosis,
    SubmitAnswerRequest
)


def test_skill_state_valid():

    skill = SkillState(
        mastery=0.42,
        attempts=5,
        correct_attempts=3,
        last_practiced_at=1786680000,
        uncertainty_count=1
    )

    assert skill.mastery == 0.42
    assert skill.attempts == 5


def test_invalid_mastery_rejected():

    with pytest.raises(ValidationError):

        SkillState(
            mastery=1.5
        )


def test_negative_attempts_rejected():

    with pytest.raises(ValidationError):

        SkillState(
            mastery=0.5,
            attempts=-1
        )


def test_student_state_defaults():

    state = StudentState(
        student_id="student_001",

        skills={
            "two_step_equations": SkillState(
                mastery=0.42
            )
        }
    )

    assert state.misconceptions == {}

    assert (
        state.misconceptions_by_skill
        == {}
    )

    assert state.asked_question_ids == []

    assert (
        state.active_diagnosis
        is None
    )


def test_active_diagnosis():

    state = StudentState(
        student_id="student_001",

        skills={
            "two_step_equations": SkillState(
                mastery=0.20
            ),

            "one_step_equations": SkillState(
                mastery=0.10
            )
        },

        active_diagnosis=ActiveDiagnosis(
            target_skill=
                "two_step_equations",

            diagnostic_skill=
                "one_step_equations"
        )
    )

    assert (
        state.active_diagnosis
        .diagnostic_skill
        == "one_step_equations"
    )


def test_selected_option_request():

    request = SubmitAnswerRequest(
        question_id="eq_two_001",
        answer_type="selected_option",
        selected_option_id="B",
        time_taken_seconds=7.8,
        confidence=0.6
    )

    assert (
        request.answer_type
        == "selected_option"
    )

    assert (
        request.selected_option_id
        == "B"
    )


def test_dont_know_request():

    request = SubmitAnswerRequest(
        question_id="eq_two_001",
        answer_type="dont_know",
        time_taken_seconds=12.3
    )

    assert (
        request.answer_type
        == "dont_know"
    )

    assert (
        request.selected_option_id
        is None
    )


def test_invalid_confidence_rejected():

    with pytest.raises(ValidationError):

        SubmitAnswerRequest(
            question_id="q1",
            answer_type="selected_option",
            selected_option_id="A",
            time_taken_seconds=5,
            confidence=1.5
        )