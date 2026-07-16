import csv
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT / "data/outputs/test_set.csv"
OUTPUT_CSV = ROOT / "data/outputs/translation_with_llm.csv"

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL", "https://openwebui-test.hrz.uni-bonn.de/api")
MODEL = os.getenv("MODEL_NAME", "local.openai/gpt-oss-120b")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "60"))
NUM_WORKERS = 5


def translate_text(german_text):
    # Send one German text to the LLM and return the English translation.
    prompt = f"""Translate this German text into English.
Return only the English translation. Do not use Markdown or explanations.

German:
{german_text}

English:"""

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
    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"].strip()


def read_test_set():
    # Read German text and ground truth English text from the test set.
    rows = []

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
    # Save German text, ground truth, and LLM translation.
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["de_text", "en_grtr", "en_tr_llm"])
        writer.writeheader()
        writer.writerows(rows)


def translate_row(row):
    # Translate one CSV row.
    english_translation = translate_text(row["de_text"])

    return {
        "de_text": row["de_text"],
        "en_grtr": row["en_grtr"],
        "en_tr_llm": english_translation,
    }


def main():
    if not API_KEY:
        raise SystemExit("Set API_KEY first.")

    rows = read_test_set()

    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        translated_rows = []

        for index, translated_row in enumerate(
            executor.map(translate_row, rows), start=1
        ):
            translated_rows.append(translated_row)
            print(f"Translated {index}/{len(rows)}")

    save_translations(translated_rows)
    print(f"Saved output: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
