import json
from pathlib import Path

import pandas as pd


# ---------------------------------------------------
# PATHS
# ---------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent

INPUT_PATH = (
    SCRIPT_DIR
    / "outputs"
    / "fitted_bkt_parameters.csv"
)

METRICS_PATH = (
    SCRIPT_DIR
    / "outputs"
    / "bkt_metrics.json"
)

OUTPUT_DIR = (
    SCRIPT_DIR
    / ".."
    / "backend"
    / "data"
)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "fitted_bkt_params.json"
)


# ---------------------------------------------------
# EXPECTED BKT PARAMETERS
# ---------------------------------------------------

PARAMETER_MAP = {
    "prior": "p_l0",
    "learns": "p_t",
    "guesses": "p_g",
    "slips": "p_s"
}


def main():

    # ---------------------------------------------------
    # 1. LOAD FITTED PARAMETER CSV
    # ---------------------------------------------------

    print("Loading fitted BKT parameters...")

    df = pd.read_csv(INPUT_PATH)

    print("Columns:", df.columns.tolist())
    print("Rows:", len(df))


    # ---------------------------------------------------
    # 2. NORMALIZE COLUMN NAMES
    # ---------------------------------------------------

    df.columns = [
        str(col).strip().lower()
        for col in df.columns
    ]


    # ---------------------------------------------------
    # 3. CHECK EXPECTED STRUCTURE
    # ---------------------------------------------------

    required_columns = {
        "skill",
        "param",
        "value"
    }

    missing = (
        required_columns
        - set(df.columns)
    )

    if missing:

        print(
            "\nERROR: The parameter CSV does not "
            "have the expected pyBKT structure."
        )

        print(
            "Missing columns:",
            missing
        )

        print(
            "\nActual columns:",
            df.columns.tolist()
        )

        print(
            "\nFirst 20 rows:"
        )

        print(
            df.head(20)
            .to_string(index=False)
        )

        raise ValueError(
            "Unexpected fitted_bkt_parameters.csv format."
        )


    # ---------------------------------------------------
    # 4. KEEP ONLY STANDARD BKT PARAMETERS
    # ---------------------------------------------------

    df["param"] = (
        df["param"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    standard_df = df[
        df["param"].isin(
            PARAMETER_MAP.keys()
        )
    ].copy()


    if standard_df.empty:
        raise ValueError(
            "No standard BKT parameters found."
        )


    # ---------------------------------------------------
    # 5. CONVERT VALUES TO NUMERIC
    # ---------------------------------------------------

    standard_df["value"] = pd.to_numeric(
        standard_df["value"],
        errors="raise"
    )


    # ---------------------------------------------------
    # 6. BUILD PARAMETER DICTIONARY
    # ---------------------------------------------------

    exported = {}


    skills = sorted(
        standard_df["skill"]
        .dropna()
        .unique()
        .tolist()
    )


    for skill in skills:

        skill_rows = standard_df[
            standard_df["skill"] == skill
        ]

        skill_params = {}


        for (
            pybkt_name,
            tutortrace_name
        ) in PARAMETER_MAP.items():

            matches = skill_rows[
                skill_rows["param"]
                == pybkt_name
            ]


            if matches.empty:

                raise ValueError(
                    f"Skill '{skill}' is missing "
                    f"parameter '{pybkt_name}'."
                )


            # Standard BKT should have one value
            # for each of these parameters.
            value = float(
                matches.iloc[0]["value"]
            )


            # Probability validation
            if not 0 <= value <= 1:

                raise ValueError(
                    f"Invalid probability for "
                    f"{skill}/{pybkt_name}: "
                    f"{value}"
                )


            skill_params[
                tutortrace_name
            ] = round(value, 6)


        exported[str(skill)] = (
            skill_params
        )


    # ---------------------------------------------------
    # 7. VALIDATE SKILL COUNT
    # ---------------------------------------------------

    print(
        "\nSkills exported:",
        len(exported)
    )


    if len(exported) != 8:

        print(
            "\nWARNING:"
            f" Expected 8 fitted skills but found "
            f"{len(exported)}."
        )


    # ---------------------------------------------------
    # 8. CREATE BACKEND/DATA IF NEEDED
    # ---------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    # ---------------------------------------------------
    # 9. SAVE JSON
    # ---------------------------------------------------

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            exported,
            file,
            indent=4
        )


    # ---------------------------------------------------
    # 10. DISPLAY SUMMARY
    # ---------------------------------------------------

    print(
        "\n========== EXPORTED PARAMETERS =========="
    )


    for (
        skill,
        params
    ) in exported.items():

        print(
            f"\n{skill}"
        )

        print(
            f"  P(L0): {params['p_l0']}"
        )

        print(
            f"  P(T) : {params['p_t']}"
        )

        print(
            f"  P(G) : {params['p_g']}"
        )

        print(
            f"  P(S) : {params['p_s']}"
        )


    print(
        "\n========== OUTPUT =========="
    )

    print(
        OUTPUT_PATH.resolve()
    )

    print(
        "\nPHASE 0 COMPLETE."
    )


if __name__ == "__main__":
    main()