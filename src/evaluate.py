import pandas as pd
from stemmer import stem

# ============================================================
# LOAD FIXED TEST DATASET
# SAME 28,753 WORDS USED TO TEST ByT5
# ============================================================

df = pd.read_csv("../data/Testing_Data.csv")

print("Test dataset shape:", df.shape)

# ============================================================
# CLEAN TEXT
# ============================================================

df = df.dropna(subset=["word", "stem"]).copy()

df["word"] = (
    df["word"]
    .astype(str)
    .str.lower()
    .str.strip()
)

df["stem"] = (
    df["stem"]
    .astype(str)
    .str.lower()
    .str.strip()
)

print("Total words for evaluation:", len(df))
print("Unique stems:", df["stem"].nunique())

# ============================================================
# APPLY RULE-BASED STEMMER
# ============================================================

print("\nRunning rule-based stemmer...")

df["predicted"] = df["word"].apply(stem)

# ============================================================
# COMPARE PREDICTIONS
# ============================================================

df["correct"] = (
    df["predicted"] == df["stem"]
)

# ============================================================
# CALCULATE ACCURACY
# ============================================================

total = len(df)
correct_predictions = int(df["correct"].sum())
incorrect_predictions = total - correct_predictions
accuracy = df["correct"].mean() * 100

# ============================================================
# SHOW RESULTS
# ============================================================

print("\n========== RULE-BASED STEMMER EVALUATION ==========")

print(f"Total words tested: {total:,}")
print(f"Correct predictions: {correct_predictions:,}")
print(f"Incorrect predictions: {incorrect_predictions:,}")
print(f"Accuracy: {accuracy:.2f}%")

# ============================================================
# WRONG PREDICTIONS
# ============================================================

errors = df[
    df["correct"] == False
].copy()

print("\n========== SAMPLE ERRORS ==========")

print(
    errors[
        ["word", "stem", "predicted"]
    ].head(30)
)

# ============================================================
# SAVE ALL RESULTS
# ============================================================

df.to_csv(
    "rule_based_test_results.csv",
    index=False
)

# ============================================================
# SAVE ERRORS ONLY
# ============================================================

errors.to_csv(
    "rule_based_test_errors.csv",
    index=False
)

# ============================================================
# SUMMARY
# ============================================================

print("\nResults saved successfully:")
print("1. rule_based_test_results.csv")
print("2. rule_based_test_errors.csv")