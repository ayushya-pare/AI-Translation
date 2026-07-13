#!/usr/bin/env bash
set -euo pipefail

# Find the llm_glossary folder, no matter where this script is started from.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Set paths used by the pipeline.
PY="${ROOT}/python_scripts"
GLOSSARY_CSV="${GLOSSARY_CSV:-${ROOT}/data/glossary.csv}"
LOG_FILE="${LOG_FILE:-${ROOT}/logs/translation_comparison.log}"
SAMPLE_INDEX="${SAMPLE_INDEX:-0}"

# Make sure the log folder exists. 
if [ ! -d "$(dirname "${LOG_FILE}")" ]; then
  mkdir -p "$(dirname "${LOG_FILE}")"
fi

# Pick one German or English sample sentence from the glossary CSV.
sample() {
  FIELD="$1" SAMPLE_INDEX="${SAMPLE_INDEX}" GLOSSARY_CSV="${GLOSSARY_CSV}" python -c '
import csv, os
rows = [r for r in csv.DictReader(open(os.environ["GLOSSARY_CSV"], encoding="utf-8"))
        if "http" not in r["de"].lower() and "www." not in r["de"].lower()
        and len(r["de"].split()) >= 8 and len(r["en"].split()) >= 8]
print(rows[int(os.environ["SAMPLE_INDEX"])][os.environ["FIELD"]])
'
}

# Use given text if it exists. Otherwise, take one sample from the CSV.
GERMAN_TEXT="${GERMAN_TEXT:-$(sample de)}"
GROUND_TRUTH="${GROUND_TRUTH:-$(sample en)}"

# Print the last log lines when something fails.
fail() {
  echo "Translation pipeline failed. Last log lines:"
  tail -n 40 "${LOG_FILE}"
  exit 1
}

# Start a fresh log file.
echo "Running translation comparison" > "${LOG_FILE}"
echo >> "${LOG_FILE}"

# Translate the German text without glossary help.
WITHOUT="$(python "${PY}/translate_without_glossary.py" "${GERMAN_TEXT}" 2>> "${LOG_FILE}")" || fail

# Translate the same German text with glossary help.
WITH="$(GLOSSARY_CSV="${GLOSSARY_CSV}" python "${PY}/translate_with_glossary.py" "${GERMAN_TEXT}" 2>> "${LOG_FILE}")" || fail

# Compare both translations with the ground truth.
python "${PY}/compare_translations.py" \
  --german-text "${GERMAN_TEXT}" \
  --without-glossary "${WITHOUT}" \
  --with-glossary "${WITH}" \
  --ground-truth "${GROUND_TRUTH}" >> "${LOG_FILE}" 2>&1 || fail

echo "Saved log to ${LOG_FILE}"
