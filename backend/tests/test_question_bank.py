import json
from collections import Counter
from pathlib import Path


QUESTIONS_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "questions.json"
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


def load_questions():

    with open(
        QUESTIONS_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def test_question_bank_has_48_questions():

    questions = load_questions()

    assert len(questions) == 48


def test_question_ids_are_unique():

    questions = load_questions()

    ids = [
        question["id"]
        for question in questions
    ]

    assert (
        len(ids)
        == len(set(ids))
    )


def test_all_eight_skills_exist():

    questions = load_questions()

    skills = {
        question["skill_id"]
        for question in questions
    }

    assert skills == EXPECTED_SKILLS


def test_six_questions_per_skill():

    questions = load_questions()

    counts = Counter(
        question["skill_id"]
        for question in questions
    )

    for skill in EXPECTED_SKILLS:

        assert counts[skill] == 6


def test_required_question_fields_exist():

    questions = load_questions()

    required_fields = {
        "id",
        "skill_id",
        "difficulty",
        "expected_time_seconds",
        "prompt",
        "options",
        "tags",
        "targets_misconceptions",
        "prerequisite_targets"
    }

    for question in questions:

        assert required_fields.issubset(
            question.keys()
        )


def test_difficulty_valid():

    questions = load_questions()

    for question in questions:

        assert question[
            "difficulty"
        ] in {
            1,
            2,
            3
        }


def test_expected_time_positive():

    questions = load_questions()

    for question in questions:

        assert (
            question[
                "expected_time_seconds"
            ]
            > 0
        )


def test_every_question_has_four_options():

    questions = load_questions()

    for question in questions:

        assert (
            len(
                question["options"]
            )
            == 4
        )


def test_option_ids_are_unique_within_question():

    questions = load_questions()

    for question in questions:

        ids = [
            option["id"]
            for option in question[
                "options"
            ]
        ]

        assert (
            len(ids)
            == len(set(ids))
        )


def test_exactly_one_correct_answer():

    questions = load_questions()

    for question in questions:

        correct_options = [
            option
            for option in question[
                "options"
            ]
            if option.get(
                "correct"
            ) is True
        ]

        assert (
            len(correct_options)
            == 1
        )


def test_incorrect_options_have_misconception():

    questions = load_questions()

    for question in questions:

        for option in question[
            "options"
        ]:

            if not option.get(
                "correct",
                False
            ):

                assert (
                    option.get(
                        "misconception"
                    )
                    is not None
                )


def test_correct_option_has_no_misconception():

    questions = load_questions()

    for question in questions:

        for option in question[
            "options"
        ]:

            if option.get(
                "correct"
            ):

                assert (
                    "misconception"
                    not in option
                )


def test_question_tags_are_lists():

    questions = load_questions()

    for question in questions:

        assert isinstance(
            question["tags"],
            list
        )

        assert isinstance(
            question[
                "targets_misconceptions"
            ],
            list
        )

        assert isinstance(
            question[
                "prerequisite_targets"
            ],
            list
        )
PREREQUISITES_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "prerequisites.json"
)


def test_prerequisite_targets_are_valid():

    questions = load_questions()

    with open(
        PREREQUISITES_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        prerequisites = json.load(file)

    valid_skills = set(
        prerequisites.keys()
    )

    for question in questions:

        for prerequisite in question[
            "prerequisite_targets"
        ]:

            assert prerequisite in valid_skills