import csv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

SOURCE_FILE = BASE_DIR / "data" / "Full_Data.csv"
CONFLICTS_FILE = BASE_DIR / "results" / "conflicting_word_stems.csv"
TRACE_FILE = BASE_DIR / "results" / "conflicting_stems_source_trace.csv"


def normalize(value):
    return value.strip().lower()


def main():
    with CONFLICTS_FILE.open(encoding="utf-8-sig", newline="") as file:
        reported_pairs = {
            (normalize(row["word"]), normalize(row["stem"]))
            for row in csv.DictReader(file)
        }

    conflicting_words = {word for word, stem in reported_pairs}
    found_pairs = set()
    matches = []

    with SOURCE_FILE.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file)
        header = next(reader)
        normalized_header = [normalize(column) for column in header]

        stem_index = normalized_header.index("mzizi_wa_neno")
        headword_index = normalized_header.index("kidahizo")

        while True:
            source_line = reader.line_num + 1
            row = next(reader, None)
            if row is None:
                break

            if len(row) <= max(stem_index, headword_index):
                continue

            original_stem = row[stem_index]
            stem = normalize(original_stem)

            for index, value in enumerate(row[:len(header)]):
                if index == stem_index:
                    continue

                word = normalize(value)
                if word not in conflicting_words:
                    continue

                pair = (word, stem)
                found_pairs.add(pair)
                matches.append(
                    (
                        word,
                        stem,
                        row[headword_index],
                        original_stem,
                        source_line,
                        index + 1,
                        header[index],
                        value,
                        pair in reported_pairs,
                    )
                )

    matches.sort(key=lambda row: (row[0], row[1], row[4], row[5]))

    with TRACE_FILE.open("x", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "word",
                "stem",
                "Kidahizo",
                "Mzizi_wa_neno",
                "original_csv_line",
                "original_column_number",
                "column_name",
                "original_cell_value",
                "pair_in_conflict_report",
            ]
        )
        writer.writerows(matches)

    print(f"Conflicting words in report: {len(conflicting_words):,}")
    print(f"Source occurrences found: {len(matches):,}")
    print(f"Reported pairs missing from source: {len(reported_pairs - found_pairs):,}")
    print(f"Saved: {TRACE_FILE}")


if __name__ == "__main__":
    main()