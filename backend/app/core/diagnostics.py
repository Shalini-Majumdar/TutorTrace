from typing import Any


def find_option(
    question: dict,
    selected_option_id: str
) -> dict:
    """
    Find the selected answer option inside a question.

    Raises
    ------
    ValueError
        If the option does not exist.
    """

    options = question.get(
        "options",
        []
    )

    for option in options:
        if option.get("id") == selected_option_id:
            return option

    raise ValueError(
        f"Option '{selected_option_id}' "
        f"does not exist for question "
        f"'{question.get('id')}'."
    )


def analyze_selected_option(
    question: dict,
    selected_option_id: str
) -> dict[str, Any]:
    """
    Analyze a selected multiple-choice option.

    Returns:
    - whether the answer was correct
    - misconception tag if present
    - skill/question information

    Misconceptions are diagnostic metadata.
    They do NOT directly alter BKT parameters.
    """

    selected_option = find_option(
        question=question,
        selected_option_id=selected_option_id
    )

    correct = bool(
        selected_option.get(
            "correct",
            False
        )
    )

    misconception = None

    if not correct:
        misconception = selected_option.get(
            "misconception"
        )

    return {
        "question_id": question.get("id"),
        "skill_id": question.get("skill_id"),
        "selected_option_id": selected_option_id,
        "correct": correct,
        "misconception": misconception,
        "misconception_detected": misconception is not None
    }


def increment_misconception(
    misconception_counts: dict[str, int],
    misconception: str | None
) -> dict[str, int]:
    """
    Increment the count for a misconception.

    The dictionary is mutated and returned.

    If misconception is None, nothing changes.
    """

    if misconception is None:
        return misconception_counts

    current_count = misconception_counts.get(
        misconception,
        0
    )

    misconception_counts[
        misconception
    ] = current_count + 1

    return misconception_counts


def get_dominant_misconception(
    misconception_counts: dict[str, int],
    minimum_count: int = 2
) -> str | None:
    """
    Return the most frequently observed misconception,
    provided it has appeared at least `minimum_count`
    times.

    This will later help the adaptive selector decide
    when repeated evidence is strong enough to target
    a misconception.
    """

    if not misconception_counts:
        return None

    misconception, count = max(
        misconception_counts.items(),
        key=lambda item: item[1]
    )

    if count < minimum_count:
        return None

    return misconception


def process_option_diagnostic(
    question: dict,
    selected_option_id: str,
    misconception_counts: dict[str, int]
) -> dict:
    """
    Analyze a selected option and update the
    student's misconception fingerprint if needed.
    """

    diagnostic = analyze_selected_option(
        question=question,
        selected_option_id=selected_option_id
    )

    misconception = diagnostic[
        "misconception"
    ]

    if misconception is not None:
        increment_misconception(
            misconception_counts,
            misconception
        )

    diagnostic[
        "misconception_counts"
    ] = misconception_counts.copy()

    diagnostic[
        "dominant_misconception"
    ] = get_dominant_misconception(
        misconception_counts
    )

    return diagnostic


def increment_skill_misconception(
    misconceptions_by_skill: dict,
    skill_id: str,
    misconception: str | None
) -> dict:
    """
    Track misconception frequencies within
    individual skills.
    """

    if misconception is None:
        return misconceptions_by_skill

    if skill_id not in misconceptions_by_skill:
        misconceptions_by_skill[
            skill_id
        ] = {}

    skill_counts = misconceptions_by_skill[
        skill_id
    ]

    skill_counts[
        misconception
    ] = (
        skill_counts.get(
            misconception,
            0
        )
        + 1
    )

    return misconceptions_by_skill


def get_weakest_prerequisite(
    skill_id: str,
    mastery_by_skill: dict[str, float],
    prerequisites: dict[str, list[str]]
) -> dict | None:
    """
    Return the weakest direct prerequisite for a skill.

    Returns None if the skill has no prerequisites.

    Example return:
    {
        "skill_id": "one_step_equations",
        "mastery": 0.18
    }
    """

    skill_prerequisites = prerequisites.get(
        skill_id,
        []
    )

    if not skill_prerequisites:
        return None

    available_prerequisites = []

    for prerequisite_skill in skill_prerequisites:

        if prerequisite_skill in mastery_by_skill:

            available_prerequisites.append(
                {
                    "skill_id": prerequisite_skill,
                    "mastery": mastery_by_skill[
                        prerequisite_skill
                    ]
                }
            )

    if not available_prerequisites:
        return None

    return min(
        available_prerequisites,
        key=lambda item: item["mastery"]
    )


def should_pivot_to_prerequisite(
    target_skill_id: str,
    mastery_by_skill: dict[str, float],
    attempts_by_skill: dict[str, int],
    prerequisites: dict[str, list[str]],
    mastery_threshold: float = 0.25,
    minimum_attempts: int = 2
) -> dict:
    """
    Decide whether TutorTrace should pivot from a
    struggling target skill to its weakest prerequisite.

    Safeguards:
    - target mastery must be below threshold
    - target must have at least minimum_attempts
    - target must have at least one prerequisite
    - prerequisite must be weaker than target skill
    """

    if target_skill_id not in mastery_by_skill:
        raise ValueError(
            f"Mastery missing for skill "
            f"'{target_skill_id}'."
        )

    target_mastery = mastery_by_skill[
        target_skill_id
    ]

    target_attempts = attempts_by_skill.get(
        target_skill_id,
        0
    )

    # --------------------------------------------------
    # SAFEGUARD 1
    # Target is not weak enough.
    # --------------------------------------------------

    if target_mastery >= mastery_threshold:

        return {
            "should_pivot": False,
            "reason": "target_mastery_above_threshold",
            "target_skill_id": target_skill_id,
            "target_mastery": target_mastery,
            "target_attempts": target_attempts,
            "pivot_skill_id": None
        }

    # --------------------------------------------------
    # SAFEGUARD 2
    # Not enough evidence yet.
    # --------------------------------------------------

    if target_attempts < minimum_attempts:

        return {
            "should_pivot": False,
            "reason": "insufficient_target_attempts",
            "target_skill_id": target_skill_id,
            "target_mastery": target_mastery,
            "target_attempts": target_attempts,
            "pivot_skill_id": None
        }

    # --------------------------------------------------
    # FIND WEAKEST PREREQUISITE
    # --------------------------------------------------

    weakest = get_weakest_prerequisite(
        skill_id=target_skill_id,
        mastery_by_skill=mastery_by_skill,
        prerequisites=prerequisites
    )

    # --------------------------------------------------
    # SAFEGUARD 3
    # No prerequisite available.
    # --------------------------------------------------

    if weakest is None:

        return {
            "should_pivot": False,
            "reason": "no_prerequisite_available",
            "target_skill_id": target_skill_id,
            "target_mastery": target_mastery,
            "target_attempts": target_attempts,
            "pivot_skill_id": None
        }

    # --------------------------------------------------
    # SAFEGUARD 4
    # Do not pivot if prerequisite is not weaker
    # than the target skill.
    # --------------------------------------------------

    if weakest["mastery"] >= target_mastery:

        return {
            "should_pivot": False,
            "reason": "prerequisites_not_weaker",
            "target_skill_id": target_skill_id,
            "target_mastery": target_mastery,
            "target_attempts": target_attempts,
            "pivot_skill_id": None
        }

    # --------------------------------------------------
    # PIVOT
    # --------------------------------------------------

    return {
        "should_pivot": True,
        "reason": "weak_target_with_prerequisite_gap",
        "target_skill_id": target_skill_id,
        "target_mastery": target_mastery,
        "target_attempts": target_attempts,
        "pivot_skill_id": weakest["skill_id"],
        "pivot_mastery": weakest["mastery"]
    }