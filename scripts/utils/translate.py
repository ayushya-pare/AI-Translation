"""
Translation utilities for DataFrame rows.
"""
import requests
import pandas as pd

def call_translation_api(text: str, base_url: str, api_key: str, model: str) -> str:
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": f"Translate this German text into English. Only return the translation.\n\n{text}",
            }
        ],
        "temperature": 0.2,
        "stream": False,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    url = base_url.rstrip("/") + "/chat/completions"
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()

def translate_dataframe(df: pd.DataFrame, base_url: str, api_key: str, model: str, max_rows: int | None) -> pd.DataFrame:
    df = df.copy()
    translated = []
    total = len(df) if max_rows is None else min(max_rows, len(df))
    for idx, text in enumerate(df["de_text_clean" if "de_text_clean" in df else "de_text"].tolist()[:total], start=1):
        if not text:
            translated.append("")
            continue
        try:
            english = call_translation_api(text, base_url, api_key, model)
        except Exception as exc:
            english = f"<error: {exc}>"
        translated.append(english)
        if idx % 10 == 0:
            print(f"Translated {idx}/{total} segments...")
    df.loc[: total - 1, f"en_mit_{model}"] = translated
    return df
