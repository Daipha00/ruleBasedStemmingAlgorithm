import pandas as pd
from pathlib import Path

from stemmer import stem


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "data" / "Testing_A_Flattenned.csv"
RESULTS_DIR = BASE_DIR / "results"

RESULTS_FILE = RESULTS_DIR / "rule_based_test_results.csv"
ERRORS_FILE = RESULTS_DIR / "rule_based_test_errors.csv"




print("Loading dataset...")

if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"Dataset not found:\n{DATA_FILE}"
    )

df = pd.read_csv(DATA_FILE)


df.columns = (
    df.columns
    .astype(str)
    .str.strip()
    .str.lower()
)

required_columns = {"word", "stem"}

if not required_columns.issubset(df.columns):
    raise ValueError(
        "The dataset must contain the columns 'word' and 'stem'.\n"
        f"Available columns: {list(df.columns)}"
    )


df = df[["word", "stem"]].copy()

original_total = len(df)

print(f"Original number of pairs: {original_total:,}")


df = df.dropna(
    subset=["word", "stem"]
).copy()

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


df = df[
    (df["word"] != "")
    & (df["stem"] != "")
].copy()

df = df.reset_index(drop=True)

removed_rows = original_total - len(df)

print(f"Rows removed because of missing or empty values: {removed_rows:,}")
print(f"Total words for evaluation: {len(df):,}")
print(f"Unique words: {df['word'].nunique():,}")
print(f"Unique stems: {df['stem'].nunique():,}")




duplicate_pairs = int(
    df.duplicated(
        subset=["word", "stem"]
    ).sum()
)

stem_counts = (
    df.groupby("word")["stem"]
    .nunique()
)

conflicting_words = stem_counts[
    stem_counts > 1
]

print(f"Repeated word-stem pairs kept: {duplicate_pairs:,}")
print(f"Words linked to more than one stem kept: {len(conflicting_words):,}")



print("\nRunning rule-based stemmer...")

df["predicted"] = df["word"].apply(stem)

df["predicted"] = (
    df["predicted"]
    .astype(str)
    .str.lower()
    .str.strip()
)



df["correct"] = (
    df["predicted"] == df["stem"]
)

total = len(df)
correct_predictions = int(df["correct"].sum())
incorrect_predictions = total - correct_predictions

accuracy = (
    correct_predictions / total * 100
    if total > 0
    else 0.0
)



# CREATE ERROR DATASET

errors = df[
    df["correct"] == False
].copy()



# SAVE RESULTS

RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# Save every evaluated row
df[
    ["word", "stem", "predicted", "correct"]
].to_csv(
    RESULTS_FILE,
    index=False
)

# Save every incorrect row
errors[
    ["word", "stem", "predicted", "correct"]
].to_csv(
    ERRORS_FILE,
    index=False
)



print("\nRULE-BASED STEMMER EVALUATION")

print(f"Total words tested: {total:,}")
print(f"Correct predictions: {correct_predictions:,}")
print(f"Incorrect predictions: {incorrect_predictions:,}")
print(f"Accuracy: {accuracy:.2f}%")



# SAMPLE ERRORS

print("\nSAMPLE ERRORS")

if errors.empty:
    print("No errors found.")
else:
    print(
        errors[
            ["word", "stem", "predicted"]
        ].head(30).to_string(index=False)
    )



# VERIFY SAVED FILES

saved_results = pd.read_csv(RESULTS_FILE)
saved_errors = pd.read_csv(ERRORS_FILE)

print("\nSAVED FILE CHECK")

print(f"Rows saved in results file: {len(saved_results):,}")
print(f"Rows saved in errors file: {len(saved_errors):,}")

# FINAL FILE LOCATIONS

print("\nResults saved successfully:")

print(f"1. All evaluated words:\n   {RESULTS_FILE}")
print(f"2. All incorrect predictions:\n   {ERRORS_FILE}")
