import pandas as pd

train = pd.read_csv(
    "data/processed/assistments_train.csv"
)

test = pd.read_csv(
    "data/processed/assistments_test.csv"
)

print("\n========== TRAIN ==========")
print(train.shape)
print("Students:", train["user_id"].nunique())
print("Skills:", train["skill_name"].nunique())

print("\n========== TEST ==========")
print(test.shape)
print("Students:", test["user_id"].nunique())
print("Skills:", test["skill_name"].nunique())

print("\n========== TRAIN SKILL COUNTS ==========")
print(
    train["skill_name"]
    .value_counts()
)

print("\n========== TEST SKILL COUNTS ==========")
print(
    test["skill_name"]
    .value_counts()
)

print("\n========== OVERLAP ==========")

overlap = (
    set(train["user_id"])
    & set(test["user_id"])
)

print("Student overlap:", len(overlap))


print("\n========== CORRECT DISTRIBUTION ==========")

print("Train:")
print(
    train["correct"]
    .value_counts(normalize=True)
)

print("\nTest:")
print(
    test["correct"]
    .value_counts(normalize=True)
)