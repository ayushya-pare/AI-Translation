import csv
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT / "data/outputs/test_set.csv"
OUTPUT_CSV = ROOT / "data/outputs/translation_with_llm_glossary.csv"
GLOSSARY_CSV = ROOT / "data/glossary/cleaned_glossary.csv"

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL", "https://openwebui-test.hrz.uni-bonn.de/api")
MODEL = os.getenv("MODEL_NAME", "local.openai/gpt-oss-120b")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "60"))
NUM_WORKERS = 5
MAX_GLOSSARY_TERMS = 15


def read_glossary():
    # Store all glossary entries.
    entries = []

    # Open the cleaned glossary.
    with open(GLOSSARY_CSV, encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        # Read every glossary row.
        for row in reader:
            german_term = row["de"].strip()
            english_term = row["en"].strip()

            # Keep complete glossary pairs.
            if german_term and english_term:
                entries.append((german_term, english_term))

    # Put longer terms first.
    entries.sort(key=lambda entry: len(entry[0]), reverse=True)
    return entries


def term_is_in_text(term, text):
    # Ignore uppercase and lowercase.
    term = term.lower()
    text = text.lower()

    # Start searching from here.
    start = 0

    while True:
        # Find the next occurrence.
        position = text.find(term, start)

        # Stop when nothing remains.
        if position == -1:
            return False

        # Find both term edges.
        left_edge = position
        right_edge = position + len(term)

        # Check the left character.
        left_is_clear = left_edge == 0 or not text[left_edge - 1].isalnum()

        # Check the right character.
        right_is_clear = right_edge == len(text) or not text[right_edge].isalnum()

        # Accept this complete term.
        if left_is_clear and right_is_clear:
            return True

        # Continue after this position.
        start = position + 1


def find_glossary_terms(german_text, glossary):
    # Store matching glossary terms.
    matches = []

    # Check every glossary entry.
    for german_term, english_term in glossary:
        # Skip terms not found.
        if not term_is_in_text(german_term, german_text):
            continue

        # Avoid shorter repeated matches.
        is_already_covered = any(
            german_term.lower() in chosen_term.lower()
            for chosen_term, _ in matches
        )

        if is_already_covered:
            continue

        # Save this glossary match.
        matches.append((german_term, english_term))

        # Limit the prompt size.
        if len(matches) == MAX_GLOSSARY_TERMS:
            break

    return matches


def make_prompt(german_text, glossary_terms):
    # Format the glossary matches.
    glossary_lines = "\n".join(
        f"- {german_term} = {english_term}"
        for german_term, english_term in glossary_terms
    )

    if glossary_lines:
        # Add found glossary terms.
        glossary_part = f"""Use these relevant glossary translations consistently:
{glossary_lines}

"""
    else:
        # Add no glossary section.
        glossary_part = ""

    return f"""Act as a professional German-to-English translator.
Write a natural English version of the German text while preserving its meaning.
{glossary_part}Use glossary terms when they fit the context, but adapt grammar if needed.
Output only the translated text.
Do not add Markdown, comments or explanations.

German:
{german_text}

English:"""


def translate_text(german_text, glossary_terms):
    # Create the translation prompt.
    prompt = make_prompt(german_text, glossary_terms)

    # Send prompt to model.
    response = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
        },
        timeout=REQUEST_TIMEOUT,
    )
    # Check for request errors.
    response.raise_for_status()

    # Return only translated text.
    return response.json()["choices"][0]["message"]["content"].strip()


def read_test_set():
    # Store all test rows.
    rows = []

    # Open the test set.
    with open(INPUT_CSV, encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            rows.append(
                {
                    "de_text": row["de_text"].strip(),
                    "en_grtr": row["en_grtr"].strip(),
                }
            )

    return rows


def save_translations(rows):
    # Create the output folder.
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    # Write all translation results.
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["de_text", "en_grtr", "en_tr_llm"])
        writer.writeheader()
        writer.writerows(rows)


def translate_row(row, glossary):
    # Find useful glossary terms.
    glossary_terms = find_glossary_terms(row["de_text"], glossary)

    # Translate this German text.
    english_translation = translate_text(row["de_text"], glossary_terms)

    return {
        "de_text": row["de_text"],
        "en_grtr": row["en_grtr"],
        "en_tr_llm": english_translation,
    }


def main():
    # Require an API key.
    if not API_KEY:
        raise SystemExit("Set API_KEY first.")

    # Load required input files.
    rows = read_test_set()
    glossary = read_glossary()
    print(f"Loaded {len(glossary)} glossary entries")

    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        # Store completed translation rows.
        translated_rows = []

        for index, translated_row in enumerate(
            executor.map(lambda row: translate_row(row, glossary), rows), start=1
        ):
            translated_rows.append(translated_row)
            print(f"Translated {index}/{len(rows)}")

    save_translations(translated_rows)
    print(f"Saved output: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
