
import pandas as pd
from pathlib import Path

# ============================================================
# FILE PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"

INPUT_FILE = DATA_DIR / "Testing_A_Flattenned.csv"
CLEANED_FILE = DATA_DIR / "Testing_A_Cleaned.csv"

SUMMARY_FILE = RESULTS_DIR / "dataset_analysis_summary.csv"
DUPLICATE_PAIRS_FILE = RESULTS_DIR / "duplicate_word_stem_pairs.csv"
REPEATED_WORDS_FILE = RESULTS_DIR / "repeated_words.csv"
CONFLICTS_FILE = RESULTS_DIR / "conflicting_word_stems.csv"

DATA_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD FLATTENED DATASET
# ============================================================

print("\nLoading flattened conjugation dataset...")

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Dataset not found:\n{INPUT_FILE}"
    )

df = pd.read_csv(
    INPUT_FILE,
    dtype=str,
    keep_default_na=False
)

df.columns = df.columns.str.strip().str.lower()

required_columns = ["word", "stem"]

if not all(col in df.columns for col in required_columns):
    raise ValueError(
        "The dataset must contain 'word' and 'stem' columns."
    )

df = df[required_columns].copy()

# Preserve original CSV line numbers for tracing.
# Line 1 contains the header.
df["source_csv_line"] = df.index + 2

total_original_rows = len(df)


# ============================================================
# NORMALIZE WORDS AND STEMS
# ============================================================

print("Normalizing words and stems...")

for column in ["word", "stem"]:
    df[column] = (
        df[column]
        .astype(str)
        .str.strip()
        .str.lower()
    )

# Remove only rows with missing word or stem.
missing_mask = (
    (df["word"] == "")
    | (df["stem"] == "")
)

missing_rows = int(missing_mask.sum())

df = df.loc[~missing_mask].copy()

valid_rows = len(df)


# ============================================================
# BASIC DATASET STATISTICS
# ============================================================

print("Calculating dataset statistics...")

unique_words = df["word"].nunique()
unique_stems = df["stem"].nunique()

unique_pairs = df[["word", "stem"]].drop_duplicates()

total_unique_pairs = len(unique_pairs)

duplicate_occurrences = valid_rows - total_unique_pairs


# ============================================================
# IDENTIFY EXACT DUPLICATE WORD-STEM PAIRS
# ============================================================

print("Identifying exact duplicate word-stem pairs...")

pair_counts = (
    df.groupby(["word", "stem"], sort=False)
    .agg(
        occurrences=("word", "size"),
        first_csv_line=("source_csv_line", "min")
    )
    .reset_index()
)

duplicate_pairs = pair_counts[
    pair_counts["occurrences"] > 1
].copy()

duplicate_pairs["extra_occurrences"] = (
    duplicate_pairs["occurrences"] - 1
)

# Include every CSV line where the pair occurs.
duplicate_line_locations = (
    df.groupby(["word", "stem"], sort=False)[
        "source_csv_line"
    ]
    .agg(lambda values: ", ".join(map(str, values)))
    .reset_index(name="all_csv_lines")
)

duplicate_pairs = duplicate_pairs.merge(
    duplicate_line_locations,
    on=["word", "stem"],
    how="left"
)

duplicate_pairs = duplicate_pairs.sort_values(
    ["occurrences", "word"],
    ascending=[False, True]
)

duplicate_pairs.to_csv(
    DUPLICATE_PAIRS_FILE,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# IDENTIFY REPEATED WORDS
# ============================================================

print("Identifying repeated conjugations...")

word_counts = (
    df.groupby("word", sort=False)
    .agg(
        occurrences=("word", "size"),
        distinct_stems=("stem", "nunique")
    )
    .reset_index()
)

repeated_words = word_counts[
    word_counts["occurrences"] > 1
].copy()

repeated_words = repeated_words.sort_values(
    ["occurrences", "word"],
    ascending=[False, True]
)

repeated_words.to_csv(
    REPEATED_WORDS_FILE,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# IDENTIFY CONFLICTING STEM ANNOTATIONS
# ============================================================

print("Identifying conflicting word-stem annotations...")

conflicting_word_counts = word_counts[
    word_counts["distinct_stems"] > 1
].copy()

conflicting_words = set(
    conflicting_word_counts["word"]
)

conflicts = df[
    df["word"].isin(conflicting_words)
].copy()

conflicts = conflicts[
    ["word", "stem", "source_csv_line"]
].sort_values(
    ["word", "stem", "source_csv_line"]
)

conflicts.to_csv(
    CONFLICTS_FILE,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# CREATE CLEANED DATASET
# ============================================================

print("Creating cleaned dataset...")

# Remove only identical (word, stem) pairs.
#
# IMPORTANT:
# Different words sharing one stem remain.
#
# A word assigned different stems is retained with
# each distinct stem, pending manual review.

cleaned = df.drop_duplicates(
    subset=["word", "stem"],
    keep="first"
).copy()

cleaned = cleaned[["word", "stem"]]

cleaned.to_csv(
    CLEANED_FILE,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# VERIFY CLEANED DATASET
# ============================================================

remaining_duplicate_pairs = int(
    cleaned.duplicated(
        subset=["word", "stem"]
    ).sum()
)

cleaned_rows = len(cleaned)

if cleaned_rows != total_unique_pairs:
    raise RuntimeError(
        "Cleaned dataset row count does not match "
        "the number of unique word-stem pairs."
    )

if remaining_duplicate_pairs != 0:
    raise RuntimeError(
        "Exact duplicate pairs remain in cleaned dataset."
    )


# ============================================================
# SAVE ANALYSIS SUMMARY
# ============================================================

summary = [
    ("Original flattened rows", total_original_rows),
    ("Rows with missing word or stem", missing_rows),
    ("Valid word-stem occurrences", valid_rows),
    ("Unique words", unique_words),
    ("Unique stems", unique_stems),
    ("Unique word-stem pairs", total_unique_pairs),
    ("Distinct repeated word-stem pairs", len(duplicate_pairs)),
    ("Extra duplicate pair occurrences", duplicate_occurrences),
    ("Distinct repeated words", len(repeated_words)),
    ("Words with conflicting stems", len(conflicting_words)),
    ("Cleaned dataset rows", cleaned_rows),
    ("Remaining exact duplicate pairs", remaining_duplicate_pairs),
]

summary_df = pd.DataFrame(
    summary,
    columns=["metric", "value"]
)

summary_df.to_csv(
    SUMMARY_FILE,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# PRINT SUMMARY
# ============================================================

print("\n========== DATASET ANALYSIS SUMMARY ==========")

for metric, value in summary:
    print(f"{metric:<42}: {value:,}")

print("\n========== CLEANING VERIFICATION ==========")

print("Exact duplicate word-stem pairs removed.")
print("Different conjugations sharing a stem retained.")
print("Conflicting word-stem annotations retained for review.")

print("\n========== OUTPUT FILES ==========")

print("\nCleaned dataset:")
print(CLEANED_FILE)

print("\nAnalysis reports:")
print(SUMMARY_FILE)
print(DUPLICATE_PAIRS_FILE)
print(REPEATED_WORDS_FILE)
print(CONFLICTS_FILE)

print("\nAnalysis completed successfully.")
