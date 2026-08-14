from fastapi.testclient import TestClient

from backend.app.main import app

import backend.app.services.student_service as student_service

from backend.app.services.student_service import (
    STUDENTS,
    QUESTION_BANK
)


client = TestClient(app)


# ==========================================================
# HELPERS
# ==========================================================

def get_correct_option(
    question: dict
) -> dict:

    return next(
        option
        for option in question["options"]
        if option["correct"]
    )


def get_wrong_option_with_misconception(
    question: dict
) -> dict:

    return next(
        option
        for option in question["options"]
        if (
            not option["correct"]
            and option.get(
                "misconception"
            )
        )
    )


def submit_selected_option(
    student_id: str,
    question: dict,
    option: dict,
    time_taken_seconds: float = 10.0,
    confidence: float = 0.8
):

    return client.post(
        f"/students/{student_id}/submit-answer",
        json={
            "question_id":
                question["id"],

            "selected_option_id":
                option["id"],

            "time_taken_seconds":
                time_taken_seconds,

            "confidence":
                confidence,

            "answer_type":
                "selected_option"
        }
    )


# ==========================================================
# FULL ADAPTIVE JOURNEY
# ==========================================================

def test_complete_tutortrace_adaptive_journey(monkeypatch):
    """
    Full TutorTrace adaptive learner journey.

    Exploration is disabled only for this test so that
    the sequence is deterministic.
    """

    monkeypatch.setattr(
        student_service,
        "ADAPTIVE_EPSILON",
        0.0
    )

    student_id = (
        "e2e_adaptive_student"
    )
    # ======================================================
    # 1. START STUDENT
    # ======================================================

    response = client.post(
        f"/students/{student_id}/start"
    )

    assert response.status_code == 200

    student = STUDENTS[
        student_id
    ]

    assert len(
        student["skills"]
    ) == 8

    assert (
        student[
            "cold_start"
        ][
            "completed"
        ]
        is False
    )

    # ======================================================
    # 2. FIRST COLD-START DIAGNOSTIC
    # ======================================================

    response = client.get(
        f"/students/{student_id}/next-question"
    )

    assert response.status_code == 200

    data = response.json()

    first_question = data[
        "question"
    ]

    assert (
        first_question[
            "skill_id"
        ]
        == "integer_operations"
    )

    assert (
        data[
            "selection_reason"
        ][
            "type"
        ]
        == "cold_start_coverage"
    )

    mastery_before = student[
        "skills"
    ][
        "integer_operations"
    ][
        "mastery"
    ]

    correct_option = get_correct_option(
        first_question
    )

    # Use a normal response time here.
    response = submit_selected_option(
        student_id=student_id,
        question=first_question,
        option=correct_option,
        time_taken_seconds=10,
        confidence=0.9
    )

    assert response.status_code == 200

    result = response.json()

    assert result["correct"] is True

    assert (
        result["mastery_after"]
        > mastery_before
    )

    assert (
        student[
            "pending_question_id"
        ]
        is None
    )

    # ======================================================
    # 3. SECOND COLD-START PROBE
    # ======================================================

    response = client.get(
        f"/students/{student_id}/next-question"
    )

    second_question = response.json()[
        "question"
    ]

    assert (
        second_question[
            "skill_id"
        ]
        == "one_step_equations"
    )

    correct_option = get_correct_option(
        second_question
    )

    response = submit_selected_option(
        student_id=student_id,
        question=second_question,
        option=correct_option
    )

    assert response.status_code == 200

    # ======================================================
    # 4. THIRD COLD-START PROBE
    # ======================================================

    response = client.get(
        f"/students/{student_id}/next-question"
    )

    third_question = response.json()[
        "question"
    ]

    assert (
        third_question[
            "skill_id"
        ]
        == "two_step_equations"
    )

    # We deliberately answer the target skill wrong.
    wrong_option = (
        get_wrong_option_with_misconception(
            third_question
        )
    )

    response = submit_selected_option(
        student_id=student_id,
        question=third_question,
        option=wrong_option
    )

    assert response.status_code == 200

    first_failure = response.json()

    assert (
        first_failure["correct"]
        is False
    )

    assert (
        first_failure[
            "misconception"
        ]
        is not None
    )

    first_misconception = (
        first_failure[
            "misconception"
        ]
    )

    assert (
        student[
            "misconceptions"
        ][
            first_misconception
        ]
        >= 1
    )

    assert (
        student[
            "cold_start"
        ][
            "completed"
        ]
        is True
    )

    # ======================================================
    # 5. FORCE TARGET TO REMAIN THE WEAKEST SKILL
    #
    # This creates a deterministic test condition so the
    # selector gives another two-step-equation question.
    # ======================================================

    target_mastery = student[
        "skills"
    ][
        "two_step_equations"
    ][
        "mastery"
    ]

    for skill_id in student[
        "skills"
    ]:

        if (
            skill_id
            != "two_step_equations"
        ):

            student[
                "skills"
            ][
                skill_id
            ][
                "mastery"
            ] = max(
                target_mastery + 0.30,
                0.70
            )

    # Keep values inside probability range.
    for skill_state in student[
        "skills"
    ].values():

        skill_state[
            "mastery"
        ] = min(
            skill_state[
                "mastery"
            ],
            0.95
        )

    # ======================================================
    # 6. SECOND FAILURE ON TARGET
    # ======================================================

    response = client.get(
        f"/students/{student_id}/next-question"
    )

    assert response.status_code == 200

    target_question_2 = response.json()[
        "question"
    ]

    assert (
        target_question_2[
            "skill_id"
        ]
        == "two_step_equations"
    )

    wrong_option = (
        get_wrong_option_with_misconception(
            target_question_2
        )
    )

    response = submit_selected_option(
        student_id=student_id,
        question=target_question_2,
        option=wrong_option
    )

    assert response.status_code == 200

    second_failure = response.json()

    assert (
        second_failure["correct"]
        is False
    )

    assert (
        student[
            "skills"
        ][
            "two_step_equations"
        ][
            "attempts"
        ]
        >= 2
    )

    # ======================================================
    # 7. SIMULATE A WEAK PREREQUISITE
    #
    # The prerequisite engine requires:
    #
    # target mastery < 0.25
    # target attempts >= 2
    # prerequisite weaker than target
    #
    # We set up that deterministic state here.
    # ======================================================

    student[
    "skills"
    ][
        "two_step_equations"
    ][
        "mastery"
    ] = 0.20

    # Deliberately weak prerequisite.
    student[
        "skills"
    ][
        "one_step_equations"
    ][
        "mastery"
    ] = 0.10

    # This prerequisite is healthy enough that once
    # one_step_equations is repaired, TutorTrace can
    # return to the original target.
    student[
        "skills"
    ][
        "order_of_operations"
    ][
        "mastery"
    ] = 0.40
    # ======================================================
    # 8. PREREQUISITE PIVOT
    # ======================================================

    response = client.get(
        f"/students/{student_id}/next-question"
    )

    assert response.status_code == 200

    pivot_data = response.json()

    assert (
        pivot_data[
            "selection_reason"
        ][
            "type"
        ]
        == "prerequisite_diagnosis"
    )

    assert (
        pivot_data[
            "selection_reason"
        ][
            "target_skill"
        ]
        == "two_step_equations"
    )

    assert (
        pivot_data[
            "selection_reason"
        ][
            "diagnostic_skill"
        ]
        == "one_step_equations"
    )

    prerequisite_question = (
        pivot_data[
            "question"
        ]
    )

    assert (
        prerequisite_question[
            "skill_id"
        ]
        == "one_step_equations"
    )

    assert (
    student[
        "active_diagnosis"
    ]
    == {
        "target_skill":
            "two_step_equations",

        "diagnostic_skill":
            "one_step_equations"
    }
    )

    # ======================================================
    # 9. ANSWER PREREQUISITE CORRECTLY
    # ======================================================

    correct_option = get_correct_option(
        prerequisite_question
    )

    response = submit_selected_option(
        student_id=student_id,
        question=prerequisite_question,
        option=correct_option
    )

    assert response.status_code == 200

    prerequisite_result = (
        response.json()
    )

    assert (
        prerequisite_result[
            "correct"
        ]
        is True
    )

    # Prerequisite should improve.
    assert (
        student[
            "skills"
        ][
            "one_step_equations"
        ][
            "mastery"
        ]
        > 0.10
    )

    # ======================================================
    # 10. SYSTEM RETURNS TO TARGET
    # ======================================================

    # Ensure the successful prerequisite correction
    # resolved the active diagnosis.
    assert (
        student[
            "active_diagnosis"
        ]
        is None
    )

    response = client.get(
        f"/students/{student_id}/next-question"
    )

    assert response.status_code == 200

    return_question = response.json()[
        "question"
    ]

    assert (
        return_question[
            "skill_id"
        ]
        == "two_step_equations"
    )


# ==========================================================
# RESPONSE-AWARE BKT
# ==========================================================

def test_slow_correct_response_signal():

    student_id = (
        "e2e_slow_correct_student"
    )

    client.post(
        f"/students/{student_id}/start"
    )

    response = client.get(
        f"/students/{student_id}/next-question"
    )

    question = response.json()[
        "question"
    ]

    correct_option = get_correct_option(
        question
    )

    response = submit_selected_option(
        student_id=student_id,
        question=question,
        option=correct_option,

        # Current Phase 4 slow threshold
        # is > 30 seconds.
        time_taken_seconds=35
    )

    assert response.status_code == 200

    result = response.json()

    assert (
        result[
            "response_signal"
        ]
        == "slow_correct"
    )

    assert (
        result[
            "mastery_after"
        ]
        > result[
            "mastery_before"
        ]
    )


# ==========================================================
# DON'T KNOW / UNCERTAINTY
# ==========================================================

def test_dont_know_updates_uncertainty():

    student_id = (
        "e2e_dont_know_student"
    )

    client.post(
        f"/students/{student_id}/start"
    )

    response = client.get(
        f"/students/{student_id}/next-question"
    )

    question = response.json()[
        "question"
    ]

    response = client.post(
        f"/students/{student_id}/submit-answer",

        json={
            "question_id":
                question["id"],

            "time_taken_seconds":
                12.0,

            "answer_type":
                "dont_know"
        }
    )

    assert response.status_code == 200

    result = response.json()

    assert (
        result[
            "uncertainty_detected"
        ]
        is True
    )

    assert (
        result[
            "response_signal"
        ]
        == "explicit_uncertainty"
    )

    student = STUDENTS[
        student_id
    ]

    skill_id = question[
        "skill_id"
    ]

    assert (
        student[
            "skills"
        ][
            skill_id
        ][
            "uncertainty_count"
        ]
        == 1
    )


# ==========================================================
# PENDING QUESTION SAFETY
# ==========================================================

def test_pending_question_is_stable_and_protected():

    student_id = (
        "e2e_pending_student"
    )

    client.post(
        f"/students/{student_id}/start"
    )

    first = client.get(
        f"/students/{student_id}/next-question"
    )

    second = client.get(
        f"/students/{student_id}/next-question"
    )

    first_question = first.json()[
        "question"
    ]

    second_question = second.json()[
        "question"
    ]

    # Repeated reads return the same reservation.
    assert (
        first_question["id"]
        == second_question["id"]
    )

    wrong_question = next(
        question
        for question in QUESTION_BANK
        if question["id"]
        != first_question["id"]
    )

    response = client.post(
        f"/students/{student_id}/submit-answer",

        json={
            "question_id":
                wrong_question["id"],

            "selected_option_id":
                wrong_question[
                    "options"
                ][0]["id"],

            "time_taken_seconds":
                10,

            "answer_type":
                "selected_option"
        }
    )

    assert response.status_code == 400

    # Rejected submission must NOT destroy the
    # original pending question.
    assert (
        STUDENTS[
            student_id
        ][
            "pending_question_id"
        ]
        == first_question["id"]
    )


# ==========================================================
# MEMORY DECAY / DASHBOARD
# ==========================================================

def test_mastery_dashboard_shows_decay():

    student_id = (
        "e2e_decay_student"
    )

    client.post(
        f"/students/{student_id}/start"
    )

    student = STUDENTS[
        student_id
    ]

    skill = student[
        "skills"
    ][
        "integer_operations"
    ]

    # Give the learner a known stored mastery.
    skill[
        "mastery"
    ] = 0.80

    # Pretend this skill was last practiced
    # seven days ago.
    import time

    seven_days_seconds = (
        7
        * 24
        * 60
        * 60
    )

    skill[
        "last_practiced_at"
    ] = (
        time.time()
        - seven_days_seconds
    )

    response = client.get(
        f"/students/{student_id}/mastery"
    )

    assert response.status_code == 200

    mastery_data = (
        response.json()[
            "skills"
        ][
            "integer_operations"
        ]
    )

    assert (
        mastery_data[
            "stored_mastery"
        ]
        == 0.80
    )

    assert (
        mastery_data[
            "effective_mastery"
        ]
        < mastery_data[
            "stored_mastery"
        ]
    )

    # Decay must be non-destructive.
    assert (
        student[
            "skills"
        ][
            "integer_operations"
        ][
            "mastery"
        ]
        == 0.80
    )