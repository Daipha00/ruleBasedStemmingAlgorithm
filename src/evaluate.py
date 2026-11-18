import argparse
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "Testing_A_Cleaned.csv"
RESULTS_DIR = BASE_DIR / "results"
RESULTS_FILE = RESULTS_DIR / "rule_based_cleaned_test_results.csv"
ERRORS_FILE = RESULTS_DIR / "rule_based_cleaned_test_errors.csv"


def load_dataset():
    if not DATA_FILE.is_file():
        raise SystemExit(f"Dataset not found: {DATA_FILE}")

    pairs = pd.read_csv(DATA_FILE, dtype=str, keep_default_na=False)
    pairs.columns = pairs.columns.str.strip().str.lower()

    if not {"word", "stem"}.issubset(pairs.columns):
        raise SystemExit("The cleaned dataset must contain 'word' and 'stem' columns.")

    return pairs[["word", "stem"]].copy()


def evaluate(pairs):
    from stemmer import stem

    if pairs.empty:
        raise SystemExit("The cleaned dataset has no pairs to evaluate.")

    if pairs.apply(lambda column: column.str.strip().eq("")).any().any():
        raise SystemExit("The cleaned dataset contains an empty word or stem.")

    if pairs.duplicated(subset=["word", "stem"]).any():
        raise SystemExit("The cleaned dataset contains repeated word–stem pairs.")

    pairs["predicted"] = pairs["word"].map(stem)
    pairs["correct"] = pairs["predicted"].eq(pairs["stem"])
    errors = pairs.loc[~pairs["correct"]]

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    pairs.to_csv(RESULTS_FILE, index=False, encoding="utf-8-sig")
    errors.to_csv(ERRORS_FILE, index=False, encoding="utf-8-sig")

    correct = int(pairs["correct"].sum())
    print(f"Correct predictions: {correct:,}")
    print(f"Incorrect predictions: {len(errors):,}")
    print(f"Exact-match accuracy: {correct / len(pairs):.2%}")
    print(f"All predictions: {RESULTS_FILE}")
    print(f"Incorrect predictions: {ERRORS_FILE}")


def main():
    parser = argparse.ArgumentParser(
        description="Count the cleaned test pairs or run the rule-based experiment."
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Run the stemmer and save predictions. The default only prints the count.",
    )
    args = parser.parse_args()

    pairs = load_dataset()
    print(f"Word–stem pairs in Testing_A_Cleaned.csv: {len(pairs):,}")

    if args.run:
        evaluate(pairs)


if __name__ == "__main__":
    main()
