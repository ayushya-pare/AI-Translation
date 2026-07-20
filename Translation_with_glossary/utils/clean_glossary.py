import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT / "data/glossary/glossary.csv"
OUTPUT_CSV = ROOT / "data/glossary/cleaned_glossary.csv"

# List common German words.
GERMAN_STOPWORDS = {
    "an", "auf", "das", "der", "die", "ein", "eine", "für", "im", "in",
    "ist", "mit", "oder", "sie", "und", "von", "zu",
}


def clean_text(text):
    # Remove extra text spaces.
    return " ".join(text.strip().split())


def read_and_clean_glossary():
    # Store cleaned glossary rows.
    cleaned_entries = []

    # Remember already used terms.
    seen_terms = set()

    # Open the original glossary.
    with open(INPUT_CSV, encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        # Read every glossary row.
        for row in reader:
            # Clean both language terms.
            german_term = clean_text(row["de"])
            english_term = clean_text(row["en"])
            frequency = row.get("frequency", "1")
            term_key = german_term.lower()

            # Skip incomplete glossary rows.
            if not german_term or not english_term:
                continue

            # Skip very short terms.
            if len(german_term) < 2:
                continue

            # Skip common German words.
            if term_key in GERMAN_STOPWORDS:
                continue

            # Skip repeated German terms.
            if term_key in seen_terms:
                continue

            # Save this useful entry.
            cleaned_entries.append((german_term, english_term, frequency))
            seen_terms.add(term_key)

    return cleaned_entries


def save_cleaned_glossary(entries):
    # Create the output folder.
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    # Write the cleaned glossary.
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["de", "en", "frequency"])
        writer.writerows(entries)


def main():
    # Clean all glossary entries.
    entries = read_and_clean_glossary()

    # Save all cleaned entries.
    save_cleaned_glossary(entries)

    # Print simple result information.
    print(f"Input: {INPUT_CSV}")
    print(f"Output: {OUTPUT_CSV}")
    print(f"Cleaned glossary rows: {len(entries)}")


if __name__ == "__main__":
    main()
