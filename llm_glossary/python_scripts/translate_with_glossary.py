import csv
import os
import re
import sys

import requests


API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL", "https://openwebui-test.hrz.uni-bonn.de/api")
MODEL = os.getenv("MODEL_NAME", "local.openai/gpt-oss-120b")
GLOSSARY_CSV = os.getenv("GLOSSARY_CSV", "llm_glossary/data/glossary.csv")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "60"))


def input_text():
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:]).strip()
    return sys.stdin.read().strip()


def find_glossary_terms(german_text):
    matches = []

    with open(GLOSSARY_CSV, encoding="utf-8") as file:
        for row in csv.DictReader(file):
            de = row["de"].strip()
            en = row["en"].strip()

            if de == german_text:
                continue

            pattern = r"\b" + re.escape(de.lower()) + r"\b"
            if re.search(pattern, german_text.lower()):
                matches.append(f"{de} = {en}")

            if len(matches) == 8:
                break

    return "\n".join(matches)


if not API_KEY:
    raise SystemExit("Set API_KEY first.")


german_text = input_text()
if not german_text:
    raise SystemExit("Pass German text as an argument or via stdin.")


glossary = find_glossary_terms(german_text)
prompt = f"""Translate this German text into English.
Use the glossary if relevant.
Return only the English translation. Do not use Markdown or explanations.

Glossary:
{glossary or "(none)"}

German:
{german_text}

English:"""

try:
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
except requests.RequestException as error:
    raise SystemExit(
        "Translation with glossary failed while calling "
        f"{BASE_URL}/chat/completions: {error}"
    ) from error

translation = response.json()["choices"][0]["message"]["content"].strip()

print(translation)
