DEFAULT_PROBE_SKILLS = [
    "integer_operations",
    "one_step_equations",
    "two_step_equations"
]


def initialize_student_skills(
    bkt_params: dict
) -> dict:
    """
    Initialize every skill using its fitted BKT prior P(L0).

    No mastery values are invented manually.
    """

    skills = {}

    for skill_id, params in bkt_params.items():

        skills[skill_id] = {
            "mastery": params["p_l0"],
            "attempts": 0,
            "correct_attempts": 0,
            "last_practiced_at": None,
            "uncertainty_count": 0
        }

    return skills


def create_initial_student_state(
    student_id: str,
    bkt_params: dict
) -> dict:
    """
    Build the canonical initial TutorTrace student state.
    """

    return {
        "student_id": student_id,

        "skills": initialize_student_skills(
            bkt_params
        ),

        "misconceptions": {},

        "misconceptions_by_skill": {},

        "asked_question_ids": [],

        "active_diagnosis": None,

        "pending_question_id": None,

        "pending_selection_reason": None,

        "cold_start": {
            "completed": False,

            "probe_skills":
                DEFAULT_PROBE_SKILLS.copy(),

            "completed_probe_skills": []
        }
    }


def get_next_cold_start_skill(
    student_state: dict
) -> str | None:
    """
    Return the next diagnostic probe skill.

    Returns None once all cold-start probes
    have been completed.
    """

    cold_start = student_state.get(
        "cold_start",
        {}
    )

    probe_skills = cold_start.get(
        "probe_skills",
        DEFAULT_PROBE_SKILLS
    )

    completed = set(
        cold_start.get(
            "completed_probe_skills",
            []
        )
    )

    for skill_id in probe_skills:

        if skill_id not in completed:
            return skill_id

    return None


def mark_cold_start_probe_completed(
    student_state: dict,
    skill_id: str
) -> None:
    """
    Mark one diagnostic probe as completed.

    Mutates student state.
    """

    cold_start = student_state[
        "cold_start"
    ]

    completed = cold_start[
        "completed_probe_skills"
    ]

    if skill_id not in completed:
        completed.append(skill_id)

    if get_next_cold_start_skill(
        student_state
    ) is None:

        cold_start[
            "completed"
        ] = True