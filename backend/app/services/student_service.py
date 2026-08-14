import json
import time
from pathlib import Path

from backend.app.core.adaptive_selector import (
    find_prerequisite_pivot,
    select_next_question
)

from backend.app.core.bkt_engine import (
    process_attempt
)

from backend.app.core.cold_start import (
    create_initial_student_state,
    mark_cold_start_probe_completed
)

from backend.app.core.decay import (
    get_effective_mastery
)

from backend.app.core.diagnostics import (
    analyze_selected_option,
    increment_misconception,
    increment_skill_misconception
)

from backend.app.core.paths import (
    BKT_PARAMS_PATH,
    QUESTIONS_PATH,
    PREREQUISITES_PATH
)


# ==========================================================
# LOAD STATIC BACKEND DATA
# ==========================================================

def _load_json(path: Path):
    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


BKT_PARAMS = _load_json(
    BKT_PARAMS_PATH
)

QUESTION_BANK = _load_json(
    QUESTIONS_PATH
)

PREREQUISITES = _load_json(
    PREREQUISITES_PATH
)


# ==========================================================
# IN-MEMORY STUDENT STORE
# ==========================================================

STUDENTS: dict[str, dict] = {}

# ==========================================================
# ADAPTIVE SELECTION CONFIGURATION
# ==========================================================

ADAPTIVE_EPSILON = 0.10
# ==========================================================
# BASIC LOOKUPS
# ==========================================================

def get_student(
    student_id: str
) -> dict:
    """
    Return one student state.

    Raises ValueError if the student
    has not been started.
    """

    if student_id not in STUDENTS:
        raise ValueError(
            f"Student '{student_id}' not found. "
            f"Call /start first."
        )

    return STUDENTS[
        student_id
    ]


def get_question_by_id(
    question_id: str
) -> dict:
    """
    Find one question in the question bank.
    """

    for question in QUESTION_BANK:

        if question.get(
            "id"
        ) == question_id:

            return question

    raise ValueError(
        f"Question '{question_id}' not found."
    )


# ==========================================================
# START STUDENT
# ==========================================================

def start_student(
    student_id: str
) -> dict:
    """
    Initialize all skills using their fitted P(L0).

    Calling start again resets the student's
    in-memory state.
    """

    state = create_initial_student_state(
        student_id=student_id,
        bkt_params=BKT_PARAMS
    )

    STUDENTS[
        student_id
    ] = state

    return state


# ==========================================================
# SELECT NEXT QUESTION
# ==========================================================

def get_next_question(
    student_id: str
) -> dict:
    """
    Return the student's current unanswered question.

    The adaptive selector is called only when there is
    no pending question.

    Repeated calls therefore return the same question
    until the student submits an answer.
    """

    student = get_student(
        student_id
    )

    pending_question_id = student.get(
        "pending_question_id"
    )

    # ======================================================
    # RETURN CURRENT PENDING QUESTION
    # ======================================================

    if pending_question_id is not None:

        question = get_question_by_id(
            pending_question_id
        )

        return {
            "question": question,

            "selection_reason":
                student.get(
                    "pending_selection_reason"
                )
        }

    # ======================================================
    # SELECT NEW QUESTION
    # ======================================================
    result = select_next_question(
        student_state=student,
        question_bank=QUESTION_BANK,
        prerequisites=PREREQUISITES,
        epsilon=ADAPTIVE_EPSILON
    )

    selection_reason = result[
        "selection_reason"
    ]

    # ======================================================
    # ACTIVATE NEW PREREQUISITE DIAGNOSIS
    #
    # adaptive_selector only DECIDES.
    # student_service owns state mutation.
    # ======================================================

    if (
        selection_reason.get(
            "type"
        )
        == "prerequisite_diagnosis"
    ):

        student[
            "active_diagnosis"
        ] = {
            "target_skill":
                selection_reason[
                    "target_skill"
                ],

            "diagnostic_skill":
                selection_reason[
                    "diagnostic_skill"
                ]
        }

    # ======================================================
    # STORE PENDING QUESTION
    # ======================================================

    student[
        "pending_question_id"
    ] = result[
        "question"
    ][
        "id"
    ]

    student[
        "pending_selection_reason"
    ] = result[
        "selection_reason"
    ]

    return result


# ==========================================================
# EFFECTIVE MASTERY
# ==========================================================

def get_student_mastery(
    student_id: str
) -> dict:
    """
    Return both stored and time-adjusted mastery.
    """

    student = get_student(
        student_id
    )

    now = time.time()

    mastery = {}

    for skill_id, skill_state in (
        student["skills"].items()
    ):

        stored_mastery = skill_state[
            "mastery"
        ]

        effective_mastery = (
            get_effective_mastery(
                stored_mastery=stored_mastery,

                last_practiced_at=
                    skill_state.get(
                        "last_practiced_at"
                    ),

                current_time=now
            )
        )

        mastery[
            skill_id
        ] = {
            "stored_mastery":
                stored_mastery,

            "effective_mastery":
                effective_mastery,

            "attempts":
                skill_state[
                    "attempts"
                ],

            "correct_attempts":
                skill_state[
                    "correct_attempts"
                ],

            "uncertainty_count":
                skill_state[
                    "uncertainty_count"
                ],

            "last_practiced_at":
                skill_state.get(
                    "last_practiced_at"
                )
        }

    return {
        "student_id": student_id,
        "skills": mastery
    }


# ==========================================================
# DIAGNOSTICS
# ==========================================================

def get_student_diagnostics(
    student_id: str
) -> dict:
    """
    Return student diagnostic information.
    """

    student = get_student(
        student_id
    )

    pivot = find_prerequisite_pivot(
        student_state=student,
        prerequisites=PREREQUISITES
    )

    return {
        "student_id":
            student_id,

        "misconceptions":
            student.get(
                "misconceptions",
                {}
            ),

        "misconceptions_by_skill":
            student.get(
                "misconceptions_by_skill",
                {}
            ),

        "active_diagnosis":
            student.get(
                "active_diagnosis"
            ),

        "possible_prerequisite_pivot":
            pivot,

        "cold_start":
            student.get(
                "cold_start"
            )
    }


# ==========================================================
# SUBMIT ANSWER
# ==========================================================

def submit_answer(
    student_id: str,
    payload: dict
) -> dict:
    """
    Process one complete TutorTrace student attempt.

    Flow:
        validate student
        ↓
        validate pending question
        ↓
        determine correctness / misconception
        ↓
        calculate effective mastery
        ↓
        run appropriate mastery pathway
        ↓
        update student state
        ↓
        update diagnostics
        ↓
        update cold-start state
        ↓
        resolve active prerequisite diagnosis if possible
        ↓
        inspect whether a new prerequisite pivot is needed
        ↓
        clear pending question
    """

    student = get_student(
        student_id
    )

    # ======================================================
    # VALIDATE PENDING QUESTION
    # ======================================================

    pending_question_id = student.get(
        "pending_question_id"
    )

    if pending_question_id is None:

        raise ValueError(
            "No question is currently pending. "
            "Call /next-question first."
        )

    question_id = payload[
        "question_id"
    ]

    if question_id != pending_question_id:

        raise ValueError(
            f"Question '{question_id}' is not the "
            f"student's pending question. "
            f"Expected '{pending_question_id}'."
        )

    # ======================================================
    # READ REQUEST VALUES
    # ======================================================

    answer_type = payload[
        "answer_type"
    ]

    time_taken_seconds = payload[
        "time_taken_seconds"
    ]

    selected_option_id = payload.get(
        "selected_option_id"
    )

    confidence = payload.get(
        "confidence"
    )

    question = get_question_by_id(
        question_id
    )

    skill_id = question[
        "skill_id"
    ]

    if skill_id not in student[
        "skills"
    ]:

        raise ValueError(
            f"Skill '{skill_id}' is missing "
            f"from student state."
        )

    skill_state = student[
        "skills"
    ][
        skill_id
    ]

    params = BKT_PARAMS[
        skill_id
    ]

    now = time.time()

    # ======================================================
    # USE EFFECTIVE MASTERY AS PRE-ATTEMPT STATE
    # ======================================================

    mastery_before = (
        get_effective_mastery(
            stored_mastery=
                skill_state[
                    "mastery"
                ],

            last_practiced_at=
                skill_state.get(
                    "last_practiced_at"
                ),

            current_time=now
        )
    )

    misconception = None
    misconception_detected = False
    correct = None

    # ======================================================
    # SELECTED OPTION
    # ======================================================

    if answer_type == "selected_option":

        if selected_option_id is None:

            raise ValueError(
                "selected_option_id is required "
                "when answer_type='selected_option'."
            )

        diagnostic = (
            analyze_selected_option(
                question=question,

                selected_option_id=
                    selected_option_id
            )
        )

        correct = diagnostic[
            "correct"
        ]

        misconception = diagnostic[
            "misconception"
        ]

        misconception_detected = (
            diagnostic[
                "misconception_detected"
            ]
        )

    # ======================================================
    # DON'T KNOW
    # ======================================================

    elif answer_type == "dont_know":

        correct = None

    else:

        raise ValueError(
            f"Unsupported answer_type "
            f"'{answer_type}'."
        )

    # ======================================================
    # BKT / UNCERTAINTY UPDATE
    # ======================================================

    attempt_result = process_attempt(
        current_mastery=
            mastery_before,

        answer_type=
            answer_type,

        correct=
            correct,

        time_taken_seconds=
            time_taken_seconds,

        p_t=
            params["p_t"],

        p_g=
            params["p_g"],

        p_s=
            params["p_s"],

        confidence=
            confidence
    )

    mastery_after = attempt_result[
        "mastery_after"
    ]

    # ======================================================
    # UPDATE SKILL STATE
    # ======================================================

    skill_state[
        "mastery"
    ] = mastery_after

    skill_state[
        "attempts"
    ] += 1

    if correct is True:

        skill_state[
            "correct_attempts"
        ] += 1

    if attempt_result.get(
        "uncertainty_detected",
        False
    ):

        skill_state[
            "uncertainty_count"
        ] += 1

    skill_state[
        "last_practiced_at"
    ] = now

    # ======================================================
    # UPDATE MISCONCEPTION STATE
    # ======================================================

    if misconception is not None:

        increment_misconception(
            student[
                "misconceptions"
            ],
            misconception
        )

        increment_skill_misconception(
            student[
                "misconceptions_by_skill"
            ],
            skill_id,
            misconception
        )

    # ======================================================
    # RECORD QUESTION AS USED
    # ======================================================

    if question_id not in student[
        "asked_question_ids"
    ]:

        student[
            "asked_question_ids"
        ].append(
            question_id
        )

    # ======================================================
    # COLD START
    # ======================================================

    cold_start = student.get(
        "cold_start"
    )

    if (
        cold_start is not None
        and not cold_start.get(
            "completed",
            False
        )
    ):

        probe_skills = cold_start.get(
            "probe_skills",
            []
        )

        if skill_id in probe_skills:

            mark_cold_start_probe_completed(
                student_state=student,
                skill_id=skill_id
            )

    # ======================================================
    # RESOLVE ACTIVE PREREQUISITE DIAGNOSIS
    # ======================================================

    active_diagnosis = student.get(
        "active_diagnosis"
    )

    if (
        active_diagnosis is not None
        and correct is True
        and skill_id
        == active_diagnosis.get(
            "diagnostic_skill"
        )
    ):

        target_skill = (
            active_diagnosis.get(
                "target_skill"
            )
        )

        diagnostic_skill = (
            active_diagnosis.get(
                "diagnostic_skill"
            )
        )

        target_mastery = student[
            "skills"
        ][
            target_skill
        ][
            "mastery"
        ]

        diagnostic_mastery = student[
            "skills"
        ][
            diagnostic_skill
        ][
            "mastery"
        ]

        # Once the prerequisite is no longer weaker
        # than the target, the diagnostic gap has
        # been sufficiently resolved.
        if (
            diagnostic_mastery
            >= target_mastery
        ):

            student[
                "active_diagnosis"
            ] = None

    # ======================================================
    # PREREQUISITE PIVOT CHECK
    # ======================================================

    pivot = find_prerequisite_pivot(
        student_state=student,
        prerequisites=PREREQUISITES
    )

    diagnostic_pivot_triggered = (
        pivot is not None
    )

    # Only install a new diagnosis when one is needed.
    if pivot is not None:

        student[
            "active_diagnosis"
        ] = {
            "target_skill":
                pivot[
                    "target_skill_id"
                ],

            "diagnostic_skill":
                pivot[
                    "pivot_skill_id"
                ]
        }

    # ======================================================
    # CLEAR PENDING QUESTION
    #
    # Only done after successful processing.
    # ======================================================

    student[
        "pending_question_id"
    ] = None

    student[
        "pending_selection_reason"
    ] = None

    # ======================================================
    # BUILD RESPONSE
    # ======================================================

    response_signal = attempt_result[
        "response_signal"
    ]

    # Make ordinary correct/incorrect cases easier
    # to understand from the API response.
    if (
        answer_type
        == "selected_option"
        and correct is False
        and response_signal == "normal"
    ):

        response_signal = (
            "normal_error"
        )

    elif (
        answer_type
        == "selected_option"
        and correct is True
        and response_signal == "normal"
    ):

        response_signal = (
            "normal_correct"
        )

    return {
        "question_id":
            question_id,

        "answer_type":
            answer_type,

        "correct":
            correct,

        "skill_id":
            skill_id,

        "mastery_before":
            mastery_before,

        "mastery_after":
            mastery_after,

        "misconception":
            misconception,

        "misconception_detected":
            misconception_detected,

        "response_signal":
            response_signal,

        "uncertainty_detected":
            attempt_result.get(
                "uncertainty_detected",
                False
            ),

        "diagnostic_pivot_triggered":
            diagnostic_pivot_triggered,

        "diagnostic_pivot":
            pivot
    }