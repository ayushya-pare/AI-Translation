"""
Data input utilities for various formats: PDF, XML, TML.
"""
import pdfplumber
import os
from glob import glob
from typing import List, Tuple

# PDF input

def find_pdf_pairs(data_dir: str) -> List[Tuple[str, str]]:
    german = sorted(glob(os.path.join(data_dir, "Rundschreiben*.pdf")))
    english = sorted(glob(os.path.join(data_dir, "Circular*.pdf")))
    if not german or not english:
        raise FileNotFoundError("No matching Rundschreiben*/Circular* PDFs found in data folder.")
    pair_count = min(len(german), len(english))
    return list(zip(german[:pair_count], english[:pair_count]))

def extract_text_segments_pdf(pdf_path: str) -> List[str]:
    segments: List[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            parts = [seg.strip() for seg in text.split("\n\n") if seg.strip()]
            segments.extend(parts)
    return segments

# XML input (stub)
def extract_text_segments_xml(xml_path: str) -> List[str]:
    # TODO: Implement XML parsing and segmentation
    return []

# TML input (stub)
def extract_text_segments_tml(tml_path: str) -> List[str]:
    # TODO: Implement TML parsing and segmentation
    return []
