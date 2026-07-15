import csv
import os
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT / "data/outputs/tmx_text_pairs.csv"
OUTPUT_CSV = ROOT / "data/glossary/glossary_from_tmx_text_pairs.csv"

MAX_WORDS = int(os.getenv("MAX_WORDS", "12"))
MAX_CHARS = int(os.getenv("MAX_CHARS", "140"))


def clean_text(text):
    # Remove extra spaces from text.
    
    # remove special characters like *, #, : and
    # replace them with a space
    text = remove_special_characters(text)
    
    return " ".join(text.strip().split())

# function to remove special characters like *, # and replace
# them with a space
def remove_special_characters(text):
    return text.replace("*", " ").replace("#", " ").replace(":", " ")

def has_url(text):
    # Skip website links because they are not useful glossary terms.
    lower_text = text.lower()
    return "http://" in lower_text or "https://" in lower_text or "www." in lower_text


def is_good_glossary_pair(german_text, english_text):
    # Keep only useful German-English pairs.
    if not german_text or not english_text:
        return False
    if german_text.lower() == english_text.lower():
        return False
    if has_url(german_text) or has_url(english_text):
        return False
    if len(german_text) > MAX_CHARS or len(english_text) > MAX_CHARS:
        return False
    if len(german_text.split()) > MAX_WORDS or len(english_text.split()) > MAX_WORDS:
        return False

    return True


def read_pairs_from_csv():
    # Read German-English text pairs from the CSV file.
    pairs = []

    with open(INPUT_CSV, encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            german_text = clean_text(row["german_text"])
            
            english_text = clean_text(row["english_text"])

            if is_good_glossary_pair(german_text, english_text):
                pairs.append((german_text, english_text))

    return pairs


def write_glossary(pairs):
    # Count repeated pairs and save them as glossary entries.
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["de", "en", "frequency"])

        for (german_text, english_text), frequency in Counter(pairs).most_common():
            writer.writerow([german_text, english_text, frequency])


def main():
    pairs = read_pairs_from_csv()
    write_glossary(pairs)

    print(f"Input: {INPUT_CSV}")
    print(f"Output: {OUTPUT_CSV}")
    print(f"Glossary rows: {len(Counter(pairs))}")


if __name__ == "__main__":
    main()
