import json
import time
from collections import Counter
from pathlib import Path

from backend.app.core.decay import (
    get_effective_mastery
)

from backend.app.core.paths import (
    MOCK_STUDENTS_PATH,
    SKILL_TAXONOMY_PATH
)


# ==========================================================
# CONFIGURATION
# ==========================================================

LOW_MASTERY_THRESHOLD = 0.30

CLASS_ALERT_THRESHOLD = 0.40

HIGH_SEVERITY_THRESHOLD = 0.60


# ==========================================================
# STATIC DATA LOADING
# ==========================================================

def _load_json(
    path: Path
):
    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


MOCK_STUDENTS = _load_json(
    MOCK_STUDENTS_PATH
)

SKILL_TAXONOMY = _load_json(
    SKILL_TAXONOMY_PATH
)


# ==========================================================
# SKILL HELPERS
# ==========================================================

def get_skill_ids() -> list[str]:
    """
    Return canonical TutorTrace skill IDs.

    Supports taxonomy stored either as a list or dict.
    """

    if isinstance(
        SKILL_TAXONOMY,
        dict
    ):

        # If the taxonomy JSON itself directly maps
        # skill_id -> metadata.
        if all(
            isinstance(key, str)
            for key in SKILL_TAXONOMY.keys()
        ):
            return list(
                SKILL_TAXONOMY.keys()
            )

    raise ValueError(
        "skill_taxonomy.json must contain "
        "a dictionary keyed by skill_id."
    )


def get_skill_label(
    skill_id: str
) -> str:
    """
    Return a human-readable skill label.

    Uses taxonomy label/name when available,
    otherwise converts the ID.
    """

    data = SKILL_TAXONOMY.get(
        skill_id,
        {}
    )

    if isinstance(
        data,
        dict
    ):

        label = (
            data.get("label")
            or data.get("name")
        )

        if label:
            return label

    return skill_id.replace(
        "_",
        " "
    ).title()


# ==========================================================
# EFFECTIVE MASTERY
# ==========================================================

def calculate_effective_skill_mastery(
    skill_state: dict,
    current_time: float | None = None
) -> float:
    """
    Calculate time-decayed mastery without mutating
    stored mock-student state.
    """

    if current_time is None:
        current_time = time.time()

    return get_effective_mastery(
        stored_mastery=
            skill_state[
                "mastery"
            ],

        last_practiced_at=
            skill_state.get(
                "last_practiced_at"
            ),

        current_time=
            current_time
    )


# ==========================================================
# CLASSROOM MATRIX
# ==========================================================

def get_classroom() -> dict:
    """
    Build teacher classroom heatmap data.

    matrix[row][column] corresponds to:
        students[row]
        skills[column]

    Matrix values are EFFECTIVE mastery.
    """

    current_time = time.time()

    skill_ids = get_skill_ids()

    students = []

    matrix = []

    for student in MOCK_STUDENTS:

        student_summary = {
            "student_id":
                student[
                    "student_id"
                ],

            "name":
                student.get(
                    "name",
                    student[
                        "student_id"
                    ]
                ),

            "total_attempts":
                sum(
                    skill_state.get(
                        "attempts",
                        0
                    )
                    for skill_state
                    in student[
                        "skills"
                    ].values()
                ),

            "misconceptions":
                student.get(
                    "misconceptions",
                    {}
                )
        }

        students.append(
            student_summary
        )

        row = []

        for skill_id in skill_ids:

            skill_state = student[
                "skills"
            ][
                skill_id
            ]

            effective_mastery = (
                calculate_effective_skill_mastery(
                    skill_state=
                        skill_state,

                    current_time=
                        current_time
                )
            )

            row.append(
                round(
                    effective_mastery,
                    4
                )
            )

        matrix.append(
            row
        )

    skills = [
        {
            "skill_id":
                skill_id,

            "label":
                get_skill_label(
                    skill_id
                )
        }
        for skill_id in skill_ids
    ]

    return {
        "students":
            students,

        "skills":
            skills,

        "matrix":
            matrix
    }


# ==========================================================
# RECOMMENDATIONS
# ==========================================================

def get_alert_recommendation(
    skill_id: str
) -> str:
    """
    Return a simple teacher-facing intervention
    recommendation.
    """

    recommendations = {
        "integer_operations":
            (
                "Review signed-number operations "
                "and common sign errors."
            ),

        "fraction_operations":
            (
                "Revisit denominator alignment, "
                "fraction operations, and simplification."
            ),

        "order_of_operations":
            (
                "Reinforce order of operations "
                "with multi-step examples."
            ),

        "distributive_property":
            (
                "Re-teach distribution and "
                "combining like terms."
            ),

        "one_step_equations":
            (
                "Reinforce inverse operations "
                "and variable isolation."
            ),

        "two_step_equations":
            (
                "Re-teach prerequisite: "
                "one-step equations."
            ),

        "inequalities":
            (
                "Review inverse operations and "
                "inequality sign reversal."
            ),

        "exponents":
            (
                "Review exponent rules and "
                "common power-operation errors."
            )
    }

    return recommendations.get(
        skill_id,
        "Review this skill with targeted practice."
    )


# ==========================================================
# CLASSROOM ALERTS
# ==========================================================

def get_classroom_alerts() -> list[dict]:
    """
    Generate class-wide mastery alerts.

    Low mastery:
        effective mastery < 0.30

    Generate an alert when:
        >= 40% of the classroom is low

    Severity:
        40%-59% -> medium
        >=60%   -> high
    """

    current_time = time.time()

    skill_ids = get_skill_ids()

    total_students = len(
        MOCK_STUDENTS
    )

    if total_students == 0:
        return []

    alerts = []

    for skill_id in skill_ids:

        low_count = 0

        for student in MOCK_STUDENTS:

            skill_state = student[
                "skills"
            ][
                skill_id
            ]

            effective_mastery = (
                calculate_effective_skill_mastery(
                    skill_state=
                        skill_state,

                    current_time=
                        current_time
                )
            )

            if (
                effective_mastery
                < LOW_MASTERY_THRESHOLD
            ):
                low_count += 1

        low_fraction = (
            low_count
            / total_students
        )

        if (
            low_fraction
            < CLASS_ALERT_THRESHOLD
        ):
            continue

        if (
            low_fraction
            >= HIGH_SEVERITY_THRESHOLD
        ):
            severity = "high"

        else:
            severity = "medium"

        low_percentage = round(
            low_fraction * 100,
            1
        )

        alerts.append(
            {
                "skill_id":
                    skill_id,

                "skill_label":
                    get_skill_label(
                        skill_id
                    ),

                "low_mastery_count":
                    low_count,

                "class_size":
                    total_students,

                "low_mastery_percentage":
                    low_percentage,

                "severity":
                    severity,

                "recommendation":
                    get_alert_recommendation(
                        skill_id
                    )
            }
        )

    # Put the most serious class-wide weaknesses first.
    alerts.sort(
        key=lambda alert:
            alert[
                "low_mastery_percentage"
            ],
        reverse=True
    )

    return alerts