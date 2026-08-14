import json
import pandas as pd
import numpy as np
from pyBKT.models import Model

np.seterr(
    divide="ignore",
    invalid="ignore"
)
TRAIN_PATH = "data/processed/assistments_train.csv"
TEST_PATH = "data/processed/assistments_test.csv"

PARAMS_PATH = "outputs/fitted_bkt_parameters.csv"
METRICS_PATH = "outputs/bkt_metrics.json"


def main():

    # ---------------------------------------------------
    # 1. LOAD DATA
    # ---------------------------------------------------

    print("Loading datasets...")

    train_df = pd.read_csv(TRAIN_PATH)
    test_df = pd.read_csv(TEST_PATH)

    skills = sorted(
        train_df["skill_name"]
        .dropna()
        .unique()
        .tolist()
    )

    print(f"Train rows: {len(train_df)}")
    print(f"Test rows : {len(test_df)}")
    print(f"Skills    : {len(skills)}")


    # ---------------------------------------------------
    # 2. INITIALIZE MODEL
    # ---------------------------------------------------

    print("\nCreating BKT model...")

    model = Model(
        seed=42,
        num_fits=1,
        parallel=False
    )


    # ---------------------------------------------------
    # 3. FIT
    # ---------------------------------------------------

    print("\nFitting BKT model...")
    print("This may take several minutes.")

    model.fit(
        data=train_df,
        skills=skills
    )

    print("\nModel fitting complete.")


    # ---------------------------------------------------
    # 4. EVALUATE TEST SET
    # ---------------------------------------------------

    print("\nEvaluating model...")

    test_auc = model.evaluate(
        data=test_df,
        metric="auc"
    )

    test_rmse = model.evaluate(
        data=test_df,
        metric="rmse"
    )


    print("\n========== RESULTS ==========")

    print(f"Test AUC  : {test_auc:.4f}")
    print(f"Test RMSE : {test_rmse:.4f}")


    # ---------------------------------------------------
    # 5. EXTRACT PARAMETERS
    # ---------------------------------------------------

    params = model.params()

    print("\nParameter extraction complete.")

    params.to_csv(
        PARAMS_PATH
    )


    # ---------------------------------------------------
    # 6. SAVE METRICS
    # ---------------------------------------------------

    metrics = {
        "test_auc": float(test_auc),
        "test_rmse": float(test_rmse),

        "num_skills": len(skills),

        "num_train_rows": len(train_df),
        "num_test_rows": len(test_df),

        "num_train_students":
            int(train_df["user_id"].nunique()),

        "num_test_students":
            int(test_df["user_id"].nunique()),

        "skills": skills
    }


    with open(
        METRICS_PATH,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            metrics,
            f,
            indent=4
        )


    print("\nFiles saved:")

    print(PARAMS_PATH)
    print(METRICS_PATH)

    print("\nSTEP 1 COMPLETE.")


if __name__ == "__main__":
    main()