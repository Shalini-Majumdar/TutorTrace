import pandas as pd
DATA_PATH = "data/raw/skill_builder_data.csv"

df = pd.read_csv(
    DATA_PATH,
    encoding="ISO-8859-15",
    low_memory=False
)

print("\n========== SHAPE ==========")
print(df.shape)

print("\n========== COLUMNS ==========")
print(df.columns.tolist())

print("\n========== FIRST 5 ROWS ==========")
print(df.head())

print("\n========== IMPORTANT COLUMNS ==========")

important_columns = [
    "user_id",
    "problem_id",
    "correct",
    "skill_id",
    "skill_name",
    "opportunity"
]

for col in important_columns:
    if col in df.columns:
        print(f"{col}: FOUND")
    else:
        print(f"{col}: MISSING")

print("\n========== NULL COUNTS ==========")
for col in important_columns:
    if col in df.columns:
        print(col, df[col].isna().sum())

print("\n========== CORRECT VALUES ==========")
if "correct" in df.columns:
    print(df["correct"].value_counts(dropna=False))

print("\n========== NUMBER OF STUDENTS ==========")
if "user_id" in df.columns:
    print(df["user_id"].nunique())

print("\n========== NUMBER OF SKILLS ==========")
if "skill_name" in df.columns:
    print(df["skill_name"].nunique())

print("\n========== TOP 30 SKILLS ==========")
if "skill_name" in df.columns:
    print(df["skill_name"].value_counts().head(30))

skill_stats = (
    df.dropna(subset=["skill_name"])
      .groupby("skill_name")
      .agg(
          interactions=("correct", "count"),
          students=("user_id", "nunique"),
          accuracy=("correct", "mean")
      )
      .sort_values("interactions", ascending=False)
)

print(skill_stats.head(30))