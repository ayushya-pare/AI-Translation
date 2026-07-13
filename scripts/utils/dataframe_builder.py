"""
Utilities to build a DataFrame from any source (PDF, XML, TML).
"""
import pandas as pd
from typing import List, Dict

def build_parallel_dataframe(pairs: List, extract_func, num_workers: int | None = None) -> pd.DataFrame:
    import concurrent.futures
    def process_pair(pair):
        de_path, en_path = pair
        doc_id = de_path.split("/")[-1].split(".")[0]
        de_segments = extract_func(de_path)
        en_segments = extract_func(en_path)
        max_len = max(len(de_segments), len(en_segments))
        de_segments += ["" for _ in range(max_len - len(de_segments))]
        en_segments += ["" for _ in range(max_len - len(en_segments))]
        return [
            {
                "doc_id": doc_id,
                "seg_id": seg_id,
                "de_text": de,
                "en_ref": en,
            }
            for seg_id, (de, en) in enumerate(zip(de_segments, en_segments), start=1)
        ]
    rows = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        for result in executor.map(process_pair, pairs):
            rows.extend(result)
    return pd.DataFrame(rows)
