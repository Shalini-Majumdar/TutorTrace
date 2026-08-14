import json
from pathlib import Path
from statistics import mean

FORCE_GLOBAL_MEAN = {
    "two_step_equations",
    "exponents"
}

# ============================================================
# PATH CONFIGURATION
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
DATA_DIR = BACKEND_DIR / "data"

FITTED_PARAMS_PATH = (
    DATA_DIR / "fitted_bkt_params.json"
)

TAXONOMY_PATH = (
    DATA_DIR / "skill_taxonomy.json"
)

OUTPUT_PARAMS_PATH = (
    DATA_DIR / "bkt_params.json"
)

PROVENANCE_PATH = (
    DATA_DIR / "bkt_param_provenance.json"
)


# ============================================================
# PARAMETER NAMES
# ============================================================

PARAM_NAMES = [
    "p_l0",
    "p_t",
    "p_g",
    "p_s"
]


# ============================================================
# SOURCE-SKILL PREFERENCES
#
# These are NOT claiming exact equivalence.
#
# They specify which fitted ASSISTments skills are most
# reasonable as INITIAL PARAMETER SOURCES for each TutorTrace
# concept.
#
# The script uses every preferred source that actually exists.
# Missing preferred sources are simply ignored.
# ============================================================

SOURCE_PREFERENCES = {

    "integer_operations": [
        "Addition and Subtraction Integers",
        "Multiplication and Division Integers"
    ],

    "fraction_operations": [
        "Addition and Subtraction Fractions",
        "Conversion of Fraction Decimals Percents"
    ],

    "order_of_operations": [
        "Order of Operations",
        "Multiplication and Division Integers",
        "Addition and Subtraction Integers"
    ],

    "distributive_property": [
        "Distributive Property",
        "Equation Solving Two or Fewer Steps",
        "Multiplication and Division Integers"
    ],

    "one_step_equations": [
        "Equation Solving Two or Fewer Steps"
    ],

    "two_step_equations": [
        "Equation Solving More Than Two Steps",
    ],

    "inequalities": [
        "Solving Inequalities",
        "Equation Solving Two or Fewer Steps",
        "Addition and Subtraction Integers"
    ],

    "exponents": [
        "Exponents",
        "Multiplication and Division Integers",
        "Pattern Finding"
    ]
}


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def load_json(path):
    """
    Load and return JSON content.
    """

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def save_json(path, data):
    """
    Save dictionary as nicely formatted JSON.
    """

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )


def validate_probability(value, name):
    """
    Ensure a BKT parameter is a valid probability.
    """

    if not isinstance(value, (int, float)):
        raise ValueError(
            f"{name} must be numeric. "
            f"Received: {value}"
        )

    if not 0 <= value <= 1:
        raise ValueError(
            f"{name} must lie between 0 and 1. "
            f"Received: {value}"
        )


def validate_fitted_params(fitted):
    """
    Validate the structure produced by Phase 0.
    """

    if not fitted:
        raise ValueError(
            "fitted_bkt_params.json is empty."
        )

    for source_skill, params in fitted.items():

        for param_name in PARAM_NAMES:

            if param_name not in params:
                raise ValueError(
                    f"Source skill '{source_skill}' "
                    f"is missing '{param_name}'."
                )

            validate_probability(
                params[param_name],
                f"{source_skill}/{param_name}"
            )


def mean_parameter_set(
    fitted,
    source_skills
):
    """
    Calculate the mean BKT parameter set across
    multiple fitted source skills.
    """

    result = {}

    for param_name in PARAM_NAMES:

        values = [
            fitted[skill][param_name]
            for skill in source_skills
        ]

        result[param_name] = round(
            mean(values),
            6
        )

    return result


def global_parameter_mean(fitted):
    """
    Calculate a fallback parameter set using
    all fitted skills.

    This is used ONLY if none of the preferred
    source skills exist for a TutorTrace concept.
    """

    source_skills = list(
        fitted.keys()
    )

    return mean_parameter_set(
        fitted,
        source_skills
    )


# ============================================================
# MAIN BUILD PROCESS
# ============================================================

def main():

    print(
        "========== PHASE 1: BUILD BKT PARAMS =========="
    )

    # --------------------------------------------------------
    # 1. LOAD INPUT FILES
    # --------------------------------------------------------

    print(
        "\nLoading fitted ASSISTments parameters..."
    )

    fitted = load_json(
        FITTED_PARAMS_PATH
    )

    taxonomy = load_json(
        TAXONOMY_PATH
    )


    # --------------------------------------------------------
    # 2. VALIDATE FITTED PARAMETERS
    # --------------------------------------------------------

    validate_fitted_params(
        fitted
    )


    print(
        f"Fitted ASSISTments skills available: "
        f"{len(fitted)}"
    )

    print(
        "\nAvailable fitted skills:"
    )

    for skill in fitted:

        print(
            f"  - {skill}"
        )


    # --------------------------------------------------------
    # 3. VALIDATE TAXONOMY
    # --------------------------------------------------------

    taxonomy_skills = list(
        taxonomy.keys()
    )

    if len(taxonomy_skills) != 8:

        raise ValueError(
            "TutorTrace taxonomy must contain "
            "exactly 8 demo skills."
        )


    # --------------------------------------------------------
    # 4. CALCULATE GLOBAL FALLBACK
    # --------------------------------------------------------

    global_mean = (
        global_parameter_mean(
            fitted
        )
    )


    # --------------------------------------------------------
    # 5. BUILD FINAL PARAMETER SET
    # --------------------------------------------------------

    final_params = {}

    provenance = {}


    for target_skill in taxonomy_skills:

        print(
            f"\nMapping: {target_skill}"
        )

        preferred_sources = (
            SOURCE_PREFERENCES.get(
                target_skill,
                []
            )
        )


        # Only keep source skills that actually
        # exist in our fitted parameter file.
        available_sources = [
            source
            for source in preferred_sources
            if source in fitted
        ]


        # ----------------------------------------------------
        # CASE A:
        # One or more meaningful source skills exist.
        # ----------------------------------------------------
        if target_skill in FORCE_GLOBAL_MEAN:

            mapped_params = global_mean.copy()

            mapping_method = (
                "global_fitted_mean_fallback"
            )

            available_sources = []

            print(
                "  Using global fitted mean "
                "for stability."
            )
        elif available_sources:

            mapped_params = (
                mean_parameter_set(
                    fitted,
                    available_sources
                )
            )

            mapping_method = (
                "related_fitted_skill_mean"
                if len(available_sources) > 1
                else "direct_related_fitted_skill"
            )


            print(
                "  Source skill(s):"
            )

            for source in available_sources:

                print(
                    f"    - {source}"
                )


        # ----------------------------------------------------
        # CASE B:
        # None of the preferred source skills were fitted.
        #
        # Use the average of ALL fitted ASSISTments skills.
        # ----------------------------------------------------

        else:

            mapped_params = (
                global_mean.copy()
            )

            mapping_method = (
                "global_fitted_mean_fallback"
            )

            print(
                "  No preferred fitted source found."
            )

            print(
                "  Using global fitted parameter mean."
            )


        # ----------------------------------------------------
        # 6. SAVE PARAMETERS
        # ----------------------------------------------------

        final_params[target_skill] = (
            mapped_params
        )


        # ----------------------------------------------------
        # 7. SAVE PARAMETER PROVENANCE
        # ----------------------------------------------------

        provenance[target_skill] = {

            "display_name":
                taxonomy[
                    target_skill
                ]["display_name"],

            "mapping_method":
                mapping_method,

            "source_skills":
                available_sources,

            "parameters":
                mapped_params,

            "note":
                (
                    "Parameters are initialization "
                    "priors derived from fitted "
                    "ASSISTments BKT models. "
                    "They are not claimed to be "
                    "directly fitted on the "
                    "TutorTrace demo concept."
                )
        }


    # --------------------------------------------------------
    # 8. FINAL VALIDATION
    # --------------------------------------------------------

    if set(final_params.keys()) != set(
        taxonomy.keys()
    ):

        raise ValueError(
            "Parameter skill IDs do not match "
            "the TutorTrace taxonomy."
        )


    for skill, params in final_params.items():

        for name in PARAM_NAMES:

            validate_probability(
                params[name],
                f"{skill}/{name}"
            )


    # --------------------------------------------------------
    # 9. SAVE FILES
    # --------------------------------------------------------

    save_json(
        OUTPUT_PARAMS_PATH,
        final_params
    )

    save_json(
        PROVENANCE_PATH,
        provenance
    )


    # --------------------------------------------------------
    # 10. PRINT FINAL SUMMARY
    # --------------------------------------------------------

    print(
        "\n\n========== FINAL TUTORTRACE PARAMETERS =========="
    )


    for skill, params in final_params.items():

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
        "\nFiles created:"
    )

    print(
        f"  {OUTPUT_PARAMS_PATH}"
    )

    print(
        f"  {PROVENANCE_PATH}"
    )

    print(
        "\nPHASE 1 COMPLETE."
    )


if __name__ == "__main__":
    main()