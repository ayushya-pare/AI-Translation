"""
Output utilities for saving data in various formats.
"""
import pandas as pd
import os

def save_as_csv(df: pd.DataFrame, path: str):
    df.to_csv(path, index=False)

def save_as_json(df: pd.DataFrame, path: str):
    df.to_json(path, orient="records", lines=True)

def save_as_excel(df: pd.DataFrame, path: str):
    df.to_excel(path, index=False)

def save_output(df: pd.DataFrame, path: str):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        save_as_csv(df, path)
    elif ext == ".json":
        save_as_json(df, path)
    elif ext in (".xls", ".xlsx"):
        save_as_excel(df, path)
    else:
        raise ValueError(f"Unsupported output format: {ext}")
