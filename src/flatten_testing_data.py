import pandas as pd
from pathlib import Path


# ============================================================
# FLATTEN SWAHILI VERB DATASET
# ============================================================
# This script converts a wide dataset such as:
#
# stem | form_1 | form_2 | form_3 | ...
# buka | anabuka | amebuka | atabuka | ...
#
# into:
#
# word      | stem
# anabuka   | buka
# amebuka   | buka
# atabuka   | buka
#
# IMPORTANT:
# ALL word-form cells are retained.
# Repeated words/forms are NOT removed.
#
# Every occurrence is treated as a separate word-stem pair.
# This is intentional because the evaluation dataset should
# contain every form present in the original dataset.
# ============================================================


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

INPUT_FILE = DATA_DIR / "Full_Data.csv"

OUTPUT_FILE = DATA_DIR / "Testing_A_Flattenned.csv"


# ============================================================
# SETTINGS
# ============================================================

POSSIBLE_STEM_COLUMNS = [
    "stem",
    "stems",
    "lemma",
    "root",
    "verb",
    "base",
]


# ============================================================
# LOAD DATASET
# ============================================================

print("Loading original dataset...")

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Dataset not found:\n{INPUT_FILE}\n\n"
        "Make sure Full_Data.csv is inside the data folder."
    )

df = pd.read_csv(INPUT_FILE, dtype=str)

print(f"Original rows: {len(df):,}")
print(f"Original columns: {len(df.columns):,}")


# ============================================================
# CLEAN COLUMN NAMES
# ============================================================

df.columns = (
    df.columns
    .astype(str)
    .str.strip()
    .str.lower()
)

print("\nColumns found:")

for i, column in enumerate(df.columns):
    print(f"  {i}: {column}")


# ============================================================
# FIND STEM COLUMN
# ============================================================

stem_column = None

for column in POSSIBLE_STEM_COLUMNS:

    if column in df.columns:
        stem_column = column
        break


# If no standard stem column is found,
# use the first column.

if stem_column is None:

    stem_column = df.columns[0]

    print(
        "\nNo standard stem column name was found."
        f"\nUsing the first column as the stem column: "
        f"'{stem_column}'"
    )

else:

    print(
        f"\nStem column detected: '{stem_column}'"
    )


# ============================================================
# IDENTIFY WORD-FORM COLUMNS
# ============================================================

word_columns = [
    column
    for column in df.columns
    if column != stem_column
]

if not word_columns:

    raise ValueError(
        "No word-form columns were found. "
        "The dataset must contain the stem column plus "
        "one or more columns containing inflected/derived forms."
    )


print(
    f"Word-form columns: {len(word_columns):,}"
)


# ============================================================
# EXPECTED NUMBER OF CELLS
# ============================================================

expected_pairs = len(df) * len(word_columns)

print(
    f"\nExpected word-form cells: "
    f"{expected_pairs:,}"
)


# ============================================================
# FLATTEN DATA
# ============================================================

print("\nFlattening dataset...")

flattened_parts = []

for column in word_columns:

    # Select the stem and current word-form column
    part = df[[stem_column, column]].copy()

    # Rename to standard format
    part.columns = ["stem", "word"]


    # --------------------------------------------------------
    # CLEAN STEM
    # --------------------------------------------------------

    part["stem"] = (
        part["stem"]
        .astype(str)
        .str.lower()
        .str.strip()
    )


    # --------------------------------------------------------
    # CLEAN WORD
    # --------------------------------------------------------

    part["word"] = (
        part["word"]
        .astype(str)
        .str.lower()
        .str.strip()
    )


    # --------------------------------------------------------
    # REMOVE ONLY EMPTY / MISSING CELLS
    # --------------------------------------------------------
    #
    # IMPORTANT:
    # We DO NOT remove duplicate words.
    #
    # If the same word occurs twice, both occurrences
    # remain in the flattened dataset.
    #
    # --------------------------------------------------------

    part = part[
        (part["stem"] != "")
        & (part["word"] != "")
        & (part["stem"] != "nan")
        & (part["word"] != "nan")
    ].copy()


    # Add this column's pairs
    flattened_parts.append(part)


# ============================================================
# CHECK THAT DATA WAS GENERATED
# ============================================================

if not flattened_parts:

    raise ValueError(
        "No usable word-stem pairs were found."
    )


# ============================================================
# COMBINE ALL WORD-FORM COLUMNS
# ============================================================

flattened = pd.concat(
    flattened_parts,
    ignore_index=True
)


# ============================================================
# IMPORTANT:
# DO NOT REMOVE DUPLICATES
# ============================================================
#
# Every occurrence from the original dataset is retained.
#
# For example, if:
#
# column A = ziliozoeleka
# column B = ziliozoeleka
#
# both are kept:
#
# ziliozoeleka | zoelek
# ziliozoeleka | zoelek
#
# ============================================================

print(
    "\nDuplicate removal: DISABLED"
)

print(
    "All valid word-stem occurrences are retained."
)


# ============================================================
# FINAL COLUMN ORDER
# ============================================================

flattened = flattened[
    ["word", "stem"]
]


# ============================================================
# SAVE FLATTENED DATASET
# ============================================================

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

flattened.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# SUMMARY
# ============================================================

print(
    "\n========== FLATTENING COMPLETE =========="
)

print(
    f"Original rows:              {len(df):,}"
)

print(
    f"Original columns:           {len(df.columns):,}"
)

print(
    f"Stem column used:            {stem_column}"
)

print(
    f"Word-form columns used:      {len(word_columns):,}"
)

print(
    f"Expected word-form cells:    {expected_pairs:,}"
)

print(
    f"Word-stem pairs generated:   {len(flattened):,}"
)

print(
    f"Occurrences removed:         0"
)

print(
    f"Unique words:                "
    f"{flattened['word'].nunique():,}"
)

print(
    f"Unique stems:                "
    f"{flattened['stem'].nunique():,}"
)


# ============================================================
# VERIFY THAT NO VALID OCCURRENCES WERE LOST
# ============================================================

print(
    "\n========== VERIFICATION =========="
)

if len(flattened) == expected_pairs:

    print(
        "SUCCESS: Every word-form cell was flattened."
    )

    print(
        "No occurrences were removed because of repetition."
    )

else:

    difference = expected_pairs - len(flattened)

    print(
        "WARNING: The flattened count is different "
        "from the expected count."
    )

    print(
        f"Expected: {expected_pairs:,}"
    )

    print(
        f"Generated: {len(flattened):,}"
    )

    print(
        f"Difference: {difference:,}"
    )

    print(
        "\nThe difference is caused by empty/missing cells "
        "or another issue in the source data, NOT by "
        "duplicate removal."
    )


# ============================================================
# SHOW FIRST 20 PAIRS
# ============================================================

print(
    "\n========== FIRST 20 FLATTENED PAIRS =========="
)

print(
    flattened.head(20).to_string(index=False)
)


# ============================================================
# OUTPUT LOCATION
# ============================================================

print(
    "\nFlattened dataset saved successfully:"
)

print(
    OUTPUT_FILE
)