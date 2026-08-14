from typing import Literal

from pydantic import BaseModel, Field


# ==========================================================
# SKILL STATE
# ==========================================================

class SkillState(BaseModel):
    """
    Runtime state for one TutorTrace skill.
    """

    mastery: float = Field(
        ge=0.0,
        le=1.0
    )

    attempts: int = Field(
        default=0,
        ge=0
    )

    correct_attempts: int = Field(
        default=0,
        ge=0
    )

    last_practiced_at: float | None = None

    uncertainty_count: int = Field(
        default=0,
        ge=0
    )


# ==========================================================
# ACTIVE PREREQUISITE DIAGNOSIS
# ==========================================================

class ActiveDiagnosis(BaseModel):
    """
    Represents an active prerequisite diagnostic pivot.

    Example:

    target_skill:
        two_step_equations

    diagnostic_skill:
        one_step_equations
    """

    target_skill: str

    diagnostic_skill: str


# ==========================================================
# COLD START STATE
# ==========================================================

class ColdStartState(BaseModel):
    """
    Tracks completion of the three TutorTrace
    cold-start diagnostic probes.
    """

    completed: bool = False

    probe_skills: list[str] = Field(
        default_factory=lambda: [
            "integer_operations",
            "one_step_equations",
            "two_step_equations"
        ]
    )

    completed_probe_skills: list[str] = Field(
        default_factory=list
    )


# ==========================================================
# COMPLETE STUDENT STATE
# ==========================================================

class StudentState(BaseModel):
    """
    Canonical in-memory TutorTrace student state.
    """

    student_id: str

    skills: dict[
        str,
        SkillState
    ]

    misconceptions: dict[
        str,
        int
    ] = Field(
        default_factory=dict
    )

    misconceptions_by_skill: dict[
        str,
        dict[str, int]
    ] = Field(
        default_factory=dict
    )

    asked_question_ids: list[
        str
    ] = Field(
        default_factory=list
    )

    active_diagnosis: (
        ActiveDiagnosis | None
    ) = None

    cold_start: ColdStartState = Field(
        default_factory=ColdStartState
    )

    # Question currently shown to the student
    # but not yet answered.
    pending_question_id: str | None = None

    # Preserve the reason why that pending
    # question was originally selected.
    pending_selection_reason: dict | None = None


# ==========================================================
# STUDENT ANSWER REQUEST
# ==========================================================

class SubmitAnswerRequest(BaseModel):
    """
    Request body used when a student submits
    an answer to a TutorTrace question.
    """

    question_id: str

    answer_type: Literal[
        "selected_option",
        "dont_know"
    ]

    selected_option_id: str | None = None

    time_taken_seconds: float = Field(
        ge=0.0
    )

    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0
    )


# ==========================================================
# SELECTION REASON
# ==========================================================

class SelectionReason(BaseModel):
    """
    Explanation for why TutorTrace selected
    a particular question.
    """

    type: str

    skill_id: str | None = None

    target_skill: str | None = None

    diagnostic_skill: str | None = None

    misconception: str | None = None

    observed_count: int | None = None

    mastery: float | None = None

    target_mastery: float | None = None

    diagnostic_mastery: float | None = None

    epsilon: float | None = None

    required_attempts: int | None = None

    # Used during the three-question
    # cold-start diagnostic sequence.
    probe_number: int | None = None

    total_probes: int | None = None


# ==========================================================
# QUESTION SELECTION
# ==========================================================

class QuestionSelection(BaseModel):
    """
    Adaptive selector output.
    """

    question: dict

    selection_reason: SelectionReason


# ==========================================================
# ANSWER PROCESSING RESPONSE
# ==========================================================

class AttemptResult(BaseModel):
    """
    Result returned after processing one student attempt.
    """

    question_id: str

    skill_id: str

    correct: bool | None = None

    answer_type: Literal[
        "selected_option",
        "dont_know"
    ]

    mastery_before: float

    mastery_after: float

    response_signal: str

    misconception: str | None = None

    misconception_detected: bool = False

    uncertainty_detected: bool = False

    selection_reason: (
        SelectionReason | None
    ) = None

    diagnostic_pivot_triggered: bool = False

    diagnostic_pivot: dict | None = None