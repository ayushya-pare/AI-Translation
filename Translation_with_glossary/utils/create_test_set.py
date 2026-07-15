import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT / "data/outputs/tmx_text_pairs.csv"
OUTPUT_CSV = ROOT / "data/outputs/test_set.csv"
TEST_SET_SIZE = 500


def word_count(text):
    # Count words in a simple way.
    return len(text.split())


def looks_like_full_sentence(text):
    # Keep only texts that look like full sentences.
    text = text.strip()
    if word_count(text) < 6:
        return False
    return text.endswith((".", "!", "?"))


def make_test_set():
    # Read German-English pairs and keep 500 full sentence pairs.
    test_rows = []

    with open(INPUT_CSV, encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            german_text = row["german_text"].strip()
            english_text = row["english_text"].strip()

            if not looks_like_full_sentence(german_text):
                continue
            if not looks_like_full_sentence(english_text):
                continue

            test_rows.append(
                {
                    "de_text": german_text,
                    "en_grtr": english_text,
                }
            )

            if len(test_rows) == TEST_SET_SIZE:
                break

    return test_rows


def save_test_set(test_rows):
    # Save the test set as a CSV file.
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["de_text", "en_grtr"])
        writer.writeheader()
        writer.writerows(test_rows)


def main():
    test_rows = make_test_set()
    save_test_set(test_rows)

    print(f"Input: {INPUT_CSV}")
    print(f"Output: {OUTPUT_CSV}")
    print(f"Rows: {len(test_rows)}")


if __name__ == "__main__":
    main()
