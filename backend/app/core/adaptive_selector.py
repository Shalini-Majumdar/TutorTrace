import random

from backend.app.core.diagnostics import (
    should_pivot_to_prerequisite,
    get_dominant_misconception
)

from backend.app.core.cold_start import (
    get_next_cold_start_skill
)


DEFAULT_EPSILON = 0.10


def get_unused_questions(
    question_bank: list[dict],
    asked_question_ids: list[str]
) -> list[dict]:
    """
    Return questions the student has not already seen.
    """

    asked = set(asked_question_ids)

    return [
        question
        for question in question_bank
        if question.get("id") not in asked
    ]


def get_questions_for_skill(
    questions: list[dict],
    skill_id: str
) -> list[dict]:
    """
    Return questions belonging to a specific skill.
    """

    return [
        question
        for question in questions
        if question.get("skill_id") == skill_id
    ]


def get_questions_for_misconception(
    questions: list[dict],
    misconception: str
) -> list[dict]:
    """
    Return questions explicitly designed to investigate
    or remediate a misconception.
    """

    matches = []

    for question in questions:

        targets = question.get(
            "targets_misconceptions",
            []
        )

        if misconception in targets:
            matches.append(question)

    return matches


def choose_question(
    questions: list[dict],
    rng: random.Random
) -> dict | None:
    """
    Choose one question from a list.

    Returns None when no questions are available.
    """

    if not questions:
        return None

    return rng.choice(questions)


def get_mastery_by_skill(
    student_state: dict
) -> dict[str, float]:
    """
    Extract:
        skill_id -> mastery
    """

    skills = student_state.get(
        "skills",
        {}
    )

    return {
        skill_id: data.get("mastery", 0.0)
        for skill_id, data in skills.items()
    }


def get_attempts_by_skill(
    student_state: dict
) -> dict[str, int]:
    """
    Extract:
        skill_id -> attempt count
    """

    skills = student_state.get(
        "skills",
        {}
    )

    return {
        skill_id: data.get("attempts", 0)
        for skill_id, data in skills.items()
    }


def find_weakest_skill(
    student_state: dict
) -> str | None:
    """
    Return the skill with the lowest current mastery.
    """

    skills = student_state.get(
        "skills",
        {}
    )

    if not skills:
        return None

    return min(
        skills,
        key=lambda skill_id:
            skills[
                skill_id
            ].get(
                "mastery",
                0.0
            )
    )


def find_prerequisite_pivot(
    student_state: dict,
    prerequisites: dict[str, list[str]]
) -> dict | None:
    """
    Search all struggling skills for a valid
    prerequisite diagnosis.

    We do not inspect only the globally weakest skill,
    because a prerequisite diagnosis requires a target
    skill whose prerequisite is even weaker.

    Returns the strongest valid prerequisite-pivot
    candidate, or None if no pivot is appropriate.
    """

    mastery_by_skill = get_mastery_by_skill(
        student_state
    )

    attempts_by_skill = get_attempts_by_skill(
        student_state
    )

    pivot_candidates = []

    for skill_id in mastery_by_skill:

        pivot = should_pivot_to_prerequisite(
            target_skill_id=skill_id,
            mastery_by_skill=mastery_by_skill,
            attempts_by_skill=attempts_by_skill,
            prerequisites=prerequisites
        )

        if pivot["should_pivot"]:
            pivot_candidates.append(
                pivot
            )

    if not pivot_candidates:
        return None

    return min(
        pivot_candidates,
        key=lambda item: item[
            "target_mastery"
        ]
    )


def select_next_question(
    student_state: dict,
    question_bank: list[dict],
    prerequisites: dict[str, list[str]],
    epsilon: float = DEFAULT_EPSILON,
    rng: random.Random | None = None
) -> dict:
    """
    Select the next TutorTrace question.

    Priority:
    1. Three-question cold-start diagnostic
    2. Active prerequisite diagnosis
    3. New prerequisite diagnosis
    4. Repeated misconception investigation
    5. Weakest mastery / epsilon-greedy exploration
    6. Fallback unused question
    """

    if rng is None:
        rng = random.Random()

    if not 0 <= epsilon <= 1:
        raise ValueError(
            "epsilon must be between 0 and 1."
        )

    asked_question_ids = student_state.get(
        "asked_question_ids",
        []
    )

    unused_questions = get_unused_questions(
        question_bank=question_bank,
        asked_question_ids=asked_question_ids
    )

    if not unused_questions:
        raise ValueError(
            "No unused questions remain."
        )

    mastery_by_skill = get_mastery_by_skill(
        student_state
    )

    # ==================================================
    # PRIORITY 1
    # COLD-START DIAGNOSTIC PROBES
    # ==================================================

    cold_start = student_state.get(
        "cold_start",
        {}
    )

    cold_start_completed = cold_start.get(
        "completed",
        False
    )

    if not cold_start_completed:

        cold_start_skill = get_next_cold_start_skill(
            student_state
        )

        if cold_start_skill is not None:

            candidates = get_questions_for_skill(
                questions=unused_questions,
                skill_id=cold_start_skill
            )

            question = choose_question(
                candidates,
                rng
            )

            if question is not None:

                completed_probes = cold_start.get(
                    "completed_probe_skills",
                    []
                )

                probe_skills = cold_start.get(
                    "probe_skills",
                    []
                )

                return {
                    "question": question,

                    "selection_reason": {
                        "type":
                            "cold_start_coverage",

                        "skill_id":
                            cold_start_skill,

                        "probe_number":
                            len(completed_probes) + 1,

                        "total_probes":
                            len(probe_skills)
                    }
                }

    # ==================================================
    # PRIORITY 2
    # ACTIVE PREREQUISITE DIAGNOSIS
    # ==================================================

    active_diagnosis = student_state.get(
        "active_diagnosis"
    )

    if active_diagnosis is not None:

        diagnostic_skill = (
            active_diagnosis.get(
                "diagnostic_skill"
            )
        )

        target_skill = (
            active_diagnosis.get(
                "target_skill"
            )
        )

        if diagnostic_skill is not None:

            candidates = get_questions_for_skill(
                questions=unused_questions,
                skill_id=diagnostic_skill
            )

            question = choose_question(
                candidates,
                rng
            )

            if question is not None:

                return {
                    "question": question,

                    "selection_reason": {
                        "type":
                            "active_prerequisite_diagnosis",

                        "target_skill":
                            target_skill,

                        "diagnostic_skill":
                            diagnostic_skill
                    }
                }

    # ==================================================
    # PRIORITY 3
    # NEW PREREQUISITE DIAGNOSIS
    # ==================================================

    pivot = find_prerequisite_pivot(
        student_state=student_state,
        prerequisites=prerequisites
    )

    if pivot is not None:

        target_skill = pivot[
            "target_skill_id"
        ]

        diagnostic_skill = pivot[
            "pivot_skill_id"
        ]

        candidates = get_questions_for_skill(
            questions=unused_questions,
            skill_id=diagnostic_skill
        )

        question = choose_question(
            candidates,
            rng
        )

        if question is not None:

            return {
                "question": question,

                "selection_reason": {
                    "type":
                        "prerequisite_diagnosis",

                    "target_skill":
                        target_skill,

                    "diagnostic_skill":
                        diagnostic_skill,

                    "target_mastery":
                        pivot[
                            "target_mastery"
                        ],

                    "diagnostic_mastery":
                        pivot[
                            "pivot_mastery"
                        ]
                }
            }

    # ==================================================
    # PRIORITY 4
    # REPEATED MISCONCEPTION INVESTIGATION
    # ==================================================

    misconception_counts = student_state.get(
        "misconceptions",
        {}
    )

    dominant_misconception = (
        get_dominant_misconception(
            misconception_counts,
            minimum_count=2
        )
    )

    if dominant_misconception is not None:

        candidates = get_questions_for_misconception(
            questions=unused_questions,
            misconception=dominant_misconception
        )

        question = choose_question(
            candidates,
            rng
        )

        if question is not None:

            return {
                "question": question,

                "selection_reason": {
                    "type":
                        "misconception_investigation",

                    "misconception":
                        dominant_misconception,

                    "observed_count":
                        misconception_counts[
                            dominant_misconception
                        ]
                }
            }

    # ==================================================
    # PRIORITY 5
    # EPSILON-GREEDY
    # ==================================================

    explore = (
        rng.random() < epsilon
    )

    if not explore:

        weakest_skill = find_weakest_skill(
            student_state
        )

        if weakest_skill is not None:

            candidates = get_questions_for_skill(
                questions=unused_questions,
                skill_id=weakest_skill
            )

            question = choose_question(
                candidates,
                rng
            )

            if question is not None:

                return {
                    "question": question,

                    "selection_reason": {
                        "type":
                            "weakest_mastery",

                        "skill_id":
                            weakest_skill,

                        "mastery":
                            mastery_by_skill[
                                weakest_skill
                            ]
                    }
                }

    # ==================================================
    # EPSILON EXPLORATION
    # ==================================================

    if explore:

        question = choose_question(
            unused_questions,
            rng
        )

        if question is not None:

            return {
                "question": question,

                "selection_reason": {
                    "type":
                        "epsilon_exploration",

                    "epsilon":
                        epsilon,

                    "skill_id":
                        question.get(
                            "skill_id"
                        )
                }
            }

    # ==================================================
    # PRIORITY 6
    # FALLBACK UNUSED QUESTION
    # ==================================================

    question = choose_question(
        unused_questions,
        rng
    )

    if question is None:
        raise ValueError(
            "Unable to select a question."
        )

    return {
        "question": question,

        "selection_reason": {
            "type":
                "fallback_unused_question",

            "skill_id":
                question.get(
                    "skill_id"
                )
        }
    }