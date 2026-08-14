from fastapi.testclient import TestClient

from backend.app.main import app

from backend.app.services.teacher_service import (
    MOCK_STUDENTS,
    LOW_MASTERY_THRESHOLD,
    CLASS_ALERT_THRESHOLD,
    get_classroom,
    get_classroom_alerts,
    calculate_effective_skill_mastery
)


client = TestClient(
    app
)


EXPECTED_SKILLS = {
    "integer_operations",
    "fraction_operations",
    "order_of_operations",
    "distributive_property",
    "one_step_equations",
    "two_step_equations",
    "inequalities",
    "exponents"
}


# ==========================================================
# MOCK DATA
# ==========================================================

def test_mock_classroom_has_ten_students():

    assert (
        len(MOCK_STUDENTS)
        == 10
    )


def test_every_mock_student_has_eight_skills():

    for student in MOCK_STUDENTS:

        assert (
            set(
                student[
                    "skills"
                ].keys()
            )
            == EXPECTED_SKILLS
        )


def test_mock_skills_have_required_fields():

    required_fields = {
        "mastery",
        "attempts",
        "correct_attempts",
        "last_practiced_at",
        "uncertainty_count"
    }

    for student in MOCK_STUDENTS:

        for skill_state in (
            student[
                "skills"
            ].values()
        ):

            assert (
                required_fields
                .issubset(
                    skill_state.keys()
                )
            )


# ==========================================================
# DECAY
# ==========================================================

def test_teacher_effective_mastery_is_non_destructive():

    skill_state = {
        "mastery": 0.80,
        "attempts": 5,
        "correct_attempts": 4,
        "last_practiced_at": None,
        "uncertainty_count": 0
    }

    before = skill_state[
        "mastery"
    ]

    effective = (
        calculate_effective_skill_mastery(
            skill_state
        )
    )

    assert effective == before

    assert (
        skill_state[
            "mastery"
        ]
        == before
    )


# ==========================================================
# CLASSROOM SERVICE
# ==========================================================

def test_classroom_structure():

    result = get_classroom()

    assert "students" in result
    assert "skills" in result
    assert "matrix" in result

    assert (
        len(
            result[
                "students"
            ]
        )
        == 10
    )

    assert (
        len(
            result[
                "skills"
            ]
        )
        == 8
    )

    assert (
        len(
            result[
                "matrix"
            ]
        )
        == 10
    )


def test_classroom_matrix_is_ten_by_eight():

    result = get_classroom()

    matrix = result[
        "matrix"
    ]

    assert len(matrix) == 10

    for row in matrix:

        assert (
            len(row)
            == 8
        )


def test_classroom_matrix_values_are_probabilities():

    result = get_classroom()

    for row in result[
        "matrix"
    ]:

        for mastery in row:

            assert (
                0.0
                <= mastery
                <= 1.0
            )


# ==========================================================
# ALERT SERVICE
# ==========================================================

def test_two_step_equations_generates_alert():

    alerts = (
        get_classroom_alerts()
    )

    two_step_alert = next(
        (
            alert
            for alert in alerts
            if alert[
                "skill_id"
            ]
            == "two_step_equations"
        ),
        None
    )

    assert (
        two_step_alert
        is not None
    )

    assert (
        two_step_alert[
            "low_mastery_percentage"
        ]
        >= 40
    )


def test_two_step_alert_is_high_severity():

    alerts = (
        get_classroom_alerts()
    )

    alert = next(
        alert
        for alert in alerts
        if alert[
            "skill_id"
        ]
        == "two_step_equations"
    )

    assert (
        alert[
            "severity"
        ]
        == "high"
    )


def test_all_alerts_meet_class_threshold():

    alerts = (
        get_classroom_alerts()
    )

    for alert in alerts:

        fraction = (
            alert[
                "low_mastery_percentage"
            ]
            / 100
        )

        assert (
            fraction
            >= CLASS_ALERT_THRESHOLD
        )


def test_alert_recommendation_exists():

    alerts = (
        get_classroom_alerts()
    )

    for alert in alerts:

        assert (
            isinstance(
                alert[
                    "recommendation"
                ],
                str
            )
        )

        assert (
            len(
                alert[
                    "recommendation"
                ]
            )
            > 0
        )


# ==========================================================
# API ENDPOINTS
# ==========================================================

def test_teacher_classroom_endpoint():

    response = client.get(
        "/teacher/classroom"
    )

    assert (
        response.status_code
        == 200
    )

    data = response.json()

    assert (
        len(
            data[
                "students"
            ]
        )
        == 10
    )

    assert (
        len(
            data[
                "skills"
            ]
        )
        == 8
    )


def test_teacher_alerts_endpoint():

    response = client.get(
        "/teacher/alerts"
    )

    assert (
        response.status_code
        == 200
    )

    alerts = response.json()

    assert isinstance(
        alerts,
        list
    )

    assert any(
        alert[
            "skill_id"
        ]
        == "two_step_equations"
        for alert in alerts
    )