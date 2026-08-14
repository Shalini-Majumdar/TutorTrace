from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(
    app
)


def test_health():

    response = client.get(
        "/health"
    )

    assert (
        response.status_code
        == 200
    )

    assert (
        response.json()[
            "status"
        ]
        == "healthy"
    )


def test_start_student():

    response = client.post(
        "/students/api_test_student/start"
    )

    assert (
        response.status_code
        == 200
    )

    data = response.json()

    assert (
        data["student_id"]
        == "api_test_student"
    )

    assert len(
        data["skills"]
    ) == 8


def test_next_question():

    client.post(
        "/students/api_next_student/start"
    )

    response = client.get(
        "/students/api_next_student/next-question"
    )

    assert (
        response.status_code
        == 200
    )

    data = response.json()

    assert "question" in data

    assert (
        "selection_reason"
        in data
    )


def test_submit_answer():

    student_id = (
        "api_submit_student"
    )

    client.post(
        f"/students/{student_id}/start"
    )

    next_response = client.get(
        f"/students/{student_id}/next-question"
    )

    question = (
        next_response.json()[
            "question"
        ]
    )

    correct_option = next(
        option
        for option in question[
            "options"
        ]
        if option["correct"]
    )

    response = client.post(
        f"/students/{student_id}/submit-answer",

        json={
            "question_id":
                question["id"],

            "selected_option_id":
                correct_option["id"],

            "time_taken_seconds":
                10,

            "confidence":
                0.8,

            "answer_type":
                "selected_option"
        }
    )

    assert (
        response.status_code
        == 200
    )

    result = response.json()

    assert (
        result["correct"]
        is True
    )

    assert (
        result["skill_id"]
        == question[
            "skill_id"
        ]
    )


def test_dont_know():

    student_id = (
        "api_dont_know_student"
    )

    client.post(
        f"/students/{student_id}/start"
    )

    next_response = client.get(
        f"/students/{student_id}/next-question"
    )

    question = (
        next_response.json()[
            "question"
        ]
    )

    response = client.post(
        f"/students/{student_id}/submit-answer",

        json={
            "question_id":
                question["id"],

            "time_taken_seconds":
                12.3,

            "answer_type":
                "dont_know"
        }
    )

    assert (
        response.status_code
        == 200
    )

    result = response.json()

    assert (
        result[
            "uncertainty_detected"
        ]
        is True
    )


def test_mastery_endpoint():

    student_id = (
        "api_mastery_student"
    )

    client.post(
        f"/students/{student_id}/start"
    )

    response = client.get(
        f"/students/{student_id}/mastery"
    )

    assert (
        response.status_code
        == 200
    )

    assert (
        len(
            response.json()[
                "skills"
            ]
        )
        == 8
    )


def test_diagnostics_endpoint():

    student_id = (
        "api_diagnostics_student"
    )

    client.post(
        f"/students/{student_id}/start"
    )

    response = client.get(
        f"/students/{student_id}/diagnostics"
    )

    assert (
        response.status_code
        == 200
    )

    result = response.json()

    assert (
        "misconceptions"
        in result
    )

    assert (
        "cold_start"
        in result
    )


def test_unknown_student():

    response = client.get(
        "/students/no_such_student/mastery"
    )

    assert (
        response.status_code
        == 404
    )