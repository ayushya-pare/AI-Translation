"""Extract text from TMX files.

This script will be used to read German and English text pairs from TMX files.
"""

import csv
import json
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = ROOT / "data/raw"
OUTPUT_DIR = ROOT / "data/outputs"
OUTPUT_CSV = OUTPUT_DIR / "tmx_text_pairs.csv"
OUTPUT_JSON = OUTPUT_DIR / "tmx_text_pairs.json"


def get_segment_text(tuv):
    # Find the segment text inside one translation unit variant.
    segment = tuv.find("seg")
    if segment is None:
        return ""
    return "".join(segment.itertext()).strip()


def extract_german_english_pairs(tmx_path):
    # Read one TMX file and extract German-English text pairs.
    pairs = []
    root = ET.parse(tmx_path).getroot()

    for translation_unit in root.findall(".//tu"):
        german_text = ""
        english_text = ""

        for tuv in translation_unit.findall("tuv"):
            language = tuv.attrib.get("{http://www.w3.org/XML/1998/namespace}lang", "")

            if language.startswith("de"):
                german_text = get_segment_text(tuv)

            if language.startswith("en"):
                english_text = get_segment_text(tuv)

        if german_text and english_text:
            pairs.append((german_text, english_text))

    return pairs


def save_pairs_as_csv(pairs, output_path):
    # Save German-English text pairs in CSV format.
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["german_text", "english_text"])

        for german_text, english_text in pairs:
            writer.writerow([german_text, english_text])


def save_pairs_as_json(pairs, output_path):
    # Save German-English text pairs in JSON format.
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for german_text, english_text in pairs:
        rows.append(
            {
                "german_text": german_text,
                "english_text": english_text,
            }
        )

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(rows, file, ensure_ascii=False, indent=2)


def main():
    # Read all TMX files from the raw data folder.
    all_pairs = []

    for tmx_path in RAW_DATA_DIR.rglob("*.tmx"):
        pairs = extract_german_english_pairs(tmx_path)
        all_pairs.extend(pairs)
        print(f"Read {len(pairs)} pairs from {tmx_path}")

    # Save the extracted German-English pairs.
    save_pairs_as_csv(all_pairs, OUTPUT_CSV)
    save_pairs_as_json(all_pairs, OUTPUT_JSON)

    print(f"Saved CSV: {OUTPUT_CSV}")
    print(f"Saved JSON: {OUTPUT_JSON}")
    print(f"Total pairs: {len(all_pairs)}")


if __name__ == "__main__":
    main()
