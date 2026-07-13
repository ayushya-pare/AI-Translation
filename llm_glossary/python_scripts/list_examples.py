import csv
import os


GLOSSARY_CSV = os.getenv("GLOSSARY_CSV", "llm_glossary/data/glossary.csv")


def is_sentence(de_text, en_text):
    if "http" in de_text.lower() or "www." in de_text.lower():
        return False
    return len(de_text.split()) >= 8 and len(en_text.split()) >= 8


count = 0
with open(GLOSSARY_CSV, encoding="utf-8") as file:
    for row in csv.DictReader(file):
        if not is_sentence(row["de"], row["en"]):
            continue

        print(f"{count}: {row['de']}")
        print(f"   {row['en']}")
        print()

        count += 1
        if count == 20:
            break
