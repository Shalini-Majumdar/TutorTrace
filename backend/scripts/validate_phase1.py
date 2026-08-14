import json
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"


TAXONOMY_PATH = (
    DATA_DIR / "skill_taxonomy.json"
)

PARAMS_PATH = (
    DATA_DIR / "bkt_params.json"
)


PARAM_NAMES = {
    "p_l0",
    "p_t",
    "p_g",
    "p_s"
}


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def main():

    taxonomy = load_json(
        TAXONOMY_PATH
    )

    params = load_json(
        PARAMS_PATH
    )


    print(
        "========== PHASE 1 VALIDATION =========="
    )


    # --------------------------------------------
    # SKILL COUNT
    # --------------------------------------------

    assert len(taxonomy) == 8

    assert len(params) == 8


    # --------------------------------------------
    # SAME SKILL IDs
    # --------------------------------------------

    assert set(
        taxonomy.keys()
    ) == set(
        params.keys()
    )


    # --------------------------------------------
    # PARAMETER VALIDATION
    # --------------------------------------------

    for skill, values in params.items():

        assert set(
            values.keys()
        ) == PARAM_NAMES


        for param_name, value in values.items():

            assert isinstance(
                value,
                (int, float)
            )

            assert 0 <= value <= 1


    # --------------------------------------------
    # PREREQUISITE VALIDATION
    # --------------------------------------------

    valid_skills = set(
        taxonomy.keys()
    )


    for skill, metadata in taxonomy.items():

        prereqs = metadata.get(
            "prerequisites",
            []
        )


        for prerequisite in prereqs:

            assert (
                prerequisite
                in valid_skills
            ), (
                f"{skill} refers to unknown "
                f"prerequisite {prerequisite}"
            )


            assert (
                prerequisite != skill
            ), (
                f"{skill} cannot be its "
                f"own prerequisite."
            )


    print(
        "Skills: 8/8"
    )

    print(
        "Taxonomy IDs match parameters: PASS"
    )

    print(
        "Parameter probabilities valid: PASS"
    )

    print(
        "Prerequisites valid: PASS"
    )

    print(
        "\nPHASE 1 VALIDATION PASSED."
    )


if __name__ == "__main__":
    main()