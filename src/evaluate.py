import pandas as pd
from stemmer import stem

# ============================================================
# LOAD DATASET
# ============================================================

df = pd.read_csv("../data/swahili_subset.csv")

# ============================================================
# APPLY STEMMER
# ============================================================

df["predicted"] = df["word"].apply(stem)

# ============================================================
# COMPARE PREDICTIONS
# ============================================================

df["correct"] = df["predicted"] == df["stem"]

# ============================================================
# CALCULATE ACCURACY
# ============================================================

accuracy = df["correct"].mean() * 100

# ============================================================
# SHOW RESULTS
# ============================================================

print("\n========== STEMMER EVALUATION ==========")
print(f"Total words tested: {len(df)}")
print(f"Accuracy: {accuracy:.2f}%")

# ============================================================
# SHOW WRONG PREDICTIONS
# ============================================================

errors = df[df["correct"] == False]

print("\n========== SAMPLE ERRORS ==========")
print(errors[["word", "stem", "predicted"]].head(20))

# ============================================================
# SAVE RESULTS
# ============================================================

df.to_csv("evaluation_results.csv", index=False)

errors.to_csv("errors_only.csv", index=False)

print("\nResults saved successfully:")
print("1. evaluation_results.csv")
print("2. errors_only.csv")