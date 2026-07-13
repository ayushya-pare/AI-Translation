"""
Text cleaning utilities (header/footer removal, etc).
"""
import re
import pandas as pd

HEADER_PATTERN = re.compile(
    r"(Sehr geehrte[rn]?|Dear|Mitteilung|Einführung|Neuwahl|Ende der|Einführung der|Wichtige Fristen|Schließzeiten|"
    r"To prevent danger|Expanding|Election|Support|Introduction|Closure times|Key Deadlines)",
    re.IGNORECASE,
)
FOOTER_PATTERN = re.compile(
    r"(Mit freundlichen Grüßen|Sincerely,|signed|gez\\.|Yours sincerely|Thank you|Best regards|Kind regards)",
    re.IGNORECASE,
)

def clean_circular_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    start = HEADER_PATTERN.search(text)
    if start:
        text = text[start.start():]
    end = FOOTER_PATTERN.search(text[::-1])
    if end:
        text = text[: len(text) - end.start()]
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()

def add_clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["de_text_clean"] = df["de_text"].apply(clean_circular_text)
    df["en_ref_clean"] = df["en_ref"].apply(clean_circular_text)
    return df
