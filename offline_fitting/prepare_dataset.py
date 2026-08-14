import pandas as pd
from sklearn.model_selection import train_test_split

RAW_PATH = "data/raw/skill_builder_data.csv"

CLEAN_PATH = "data/processed/assistments_clean.csv"
TRAIN_PATH = "data/processed/assistments_train.csv"
TEST_PATH = "data/processed/assistments_test.csv"

RANDOM_STATE = 42

# ---------------------------------------------------
# 1. LOAD DATA
# ---------------------------------------------------

df = pd.read_csv(
    RAW_PATH,
    encoding="ISO-8859-15",
    low_memory=False
)

print("\n========== ORIGINAL DATA ==========")
print("Rows:", len(df))
print("Students:", df["user_id"].nunique())
print("Skills:", df["skill_name"].nunique())


# ---------------------------------------------------
# 2. KEEP ONLY COLUMNS WE ACTUALLY NEED
# ---------------------------------------------------

df = df[
    [
        "order_id",
        "user_id",
        "problem_id",
        "skill_id",
        "skill_name",
        "correct",
        "opportunity"
    ]
].copy()


# ---------------------------------------------------
# 3. DROP ROWS THAT CANNOT BE USED FOR BKT
# ---------------------------------------------------

before = len(df)

df = df.dropna(
    subset=[
        "order_id",
        "user_id",
        "skill_name",
        "correct"
    ]
)

print("\nDropped rows with missing required fields:",
      before - len(df))


# ---------------------------------------------------
# 4. ENSURE CORRECT IS BINARY
# ---------------------------------------------------

df = df[df["correct"].isin([0, 1])].copy()

df["correct"] = df["correct"].astype(int)


# ---------------------------------------------------
# 5. REMOVE DUPLICATE INTERACTIONS IF ANY
# ---------------------------------------------------

before = len(df)

df = df.drop_duplicates(
    subset=[
        "order_id",
        "user_id",
        "problem_id",
        "skill_name"
    ]
)

print("Dropped duplicate interactions:",
      before - len(df))


# ---------------------------------------------------
# 6. SKILL STATISTICS
# ---------------------------------------------------

skill_stats = (
    df.groupby("skill_name")
      .agg(
          interactions=("correct", "count"),
          students=("user_id", "nunique"),
          accuracy=("correct", "mean")
      )
      .sort_values(
          "interactions",
          ascending=False
      )
)

print("\n========== TOP SKILLS BEFORE FILTER ==========")
print(skill_stats.head(30))


# ---------------------------------------------------
# 7. SELECT SKILLS
#
# Require:
# - at least 500 interactions
# - at least 50 students
# - not almost always correct
# - not almost always wrong
# ---------------------------------------------------

eligible = skill_stats[
    (skill_stats["interactions"] >= 500)
    & (skill_stats["students"] >= 50)
    & (skill_stats["accuracy"] >= 0.20)
    & (skill_stats["accuracy"] <= 0.95)
]

# Keep top 15 skills
selected_skills = eligible.head(8).index.tolist()


print("\n========== SELECTED SKILLS ==========")

for i, skill in enumerate(selected_skills, start=1):

    row = skill_stats.loc[skill]

    print(
        f"{i:02d}. {skill} | "
        f"interactions={int(row['interactions'])} | "
        f"students={int(row['students'])} | "
        f"accuracy={row['accuracy']:.3f}"
    )


# ---------------------------------------------------
# 8. FILTER DATASET TO SELECTED SKILLS
# ---------------------------------------------------

df = df[
    df["skill_name"].isin(selected_skills)
].copy()


# ---------------------------------------------------
# 9. SORT CHRONOLOGICALLY
# ---------------------------------------------------

df = df.sort_values(
    by=[
        "user_id",
        "order_id"
    ]
).reset_index(drop=True)


# ---------------------------------------------------
# 10. SAVE CLEAN FULL SUBSET
# ---------------------------------------------------

df.to_csv(
    CLEAN_PATH,
    index=False
)


# ---------------------------------------------------
# 11. SPLIT BY STUDENT
# ---------------------------------------------------

students = df["user_id"].unique()

train_students, test_students = train_test_split(
    students,
    test_size=0.20,
    random_state=RANDOM_STATE
)


train_df = df[
    df["user_id"].isin(train_students)
].copy()

test_df = df[
    df["user_id"].isin(test_students)
].copy()


# ---------------------------------------------------
# 12. SORT AGAIN AFTER SPLIT
# ---------------------------------------------------

train_df = train_df.sort_values(
    ["user_id", "order_id"]
).reset_index(drop=True)

test_df = test_df.sort_values(
    ["user_id", "order_id"]
).reset_index(drop=True)


# ---------------------------------------------------
# 13. VERIFY NO STUDENT LEAKAGE
# ---------------------------------------------------

train_set = set(train_df["user_id"])
test_set = set(test_df["user_id"])

overlap = train_set.intersection(test_set)

assert len(overlap) == 0


# ---------------------------------------------------
# 14. SAVE TRAIN / TEST
# ---------------------------------------------------

train_df.to_csv(
    TRAIN_PATH,
    index=False
)

test_df.to_csv(
    TEST_PATH,
    index=False
)


# ---------------------------------------------------
# 15. FINAL SUMMARY
# ---------------------------------------------------

print("\n========== FINAL DATASET ==========")

print("Clean rows:", len(df))
print("Train rows:", len(train_df))
print("Test rows:", len(test_df))

print()

print("Train students:",
      train_df["user_id"].nunique())

print("Test students:",
      test_df["user_id"].nunique())

print("Student overlap:",
      len(overlap))

print("Skills:",
      df["skill_name"].nunique())

print("\nSaved:")
print(CLEAN_PATH)
print(TRAIN_PATH)
print(TEST_PATH)