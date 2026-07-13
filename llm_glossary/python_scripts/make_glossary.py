import csv
import glob
import os
import xml.etree.ElementTree as ET
from collections import Counter


TMX_DIR = "data/Translation-Memory- und Termbank-Exporte"
OUTPUT_CSV = "llm_glossary/data/glossary.csv"


def text_from_segment(tuv):
    seg = tuv.find("seg")
    return "".join(seg.itertext()).strip() if seg is not None else ""


pairs = []

for path in glob.glob(f"{TMX_DIR}/*.tmx"):
    root = ET.parse(path).getroot()

    for tu in root.findall(".//tu"):
        de_text = ""
        en_text = ""

        for tuv in tu.findall("tuv"):
            lang = tuv.attrib.get("{http://www.w3.org/XML/1998/namespace}lang", "")
            if lang.startswith("de"):
                de_text = text_from_segment(tuv)
            if lang.startswith("en"):
                en_text = text_from_segment(tuv)

        if de_text and en_text and de_text != en_text:
            pairs.append((de_text, en_text))


os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["de", "en", "frequency"])

    for (de_text, en_text), frequency in Counter(pairs).most_common():
        writer.writerow([de_text, en_text, frequency])


print(f"Wrote {OUTPUT_CSV}")
