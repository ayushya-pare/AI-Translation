"""
Deprecated shim.
Use scripts/corpus_pipeline.py for the full pipeline.
This file simply forwards to the new script so old commands still work.
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(__file__)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from corpus_pipeline import main


if __name__ == "__main__":
    main()
