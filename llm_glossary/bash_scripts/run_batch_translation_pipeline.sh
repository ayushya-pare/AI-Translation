#!/bin/bash
#SBATCH --job-name=translation_pipeline
#SBATCH --partition=intelsr_short
#SBATCH --nodes=1
#SBATCH --ntasks=2
#SBATCH --time=03:00:00
#SBATCH --output=logs/%A.out
#SBATCH --error=logs/%A.err
## ========================

set -euo pipefail

# Find the llm_glossary folder, no matter where this script is started from.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Set paths used by the pipeline.
GLOSSARY_CSV="data/glossary.csv"
OUTPUT_XLSX="outputs/translation_results.xlsx"
LOG_FILE="logs/all_translation_results.log"
MAX_SAMPLES="${MAX_SAMPLES:-2000}"



# Print the last log lines when something fails.
fail() {
  echo "Translation pipeline failed. Last log lines:"
  tail -n 40 "${LOG_FILE}"
  exit 1
}

# Start a fresh log file.
echo "Running translation for all samples" > "${LOG_FILE}"

# Translate all samples and write the Excel file.
GLOSSARY_CSV="${GLOSSARY_CSV}" OUTPUT_XLSX="${OUTPUT_XLSX}" MAX_SAMPLES="${MAX_SAMPLES}" \
  python python_scripts/batch_translation.py >> "${LOG_FILE}" 2>&1 || fail

echo "Saved Excel file to ${OUTPUT_XLSX}"
echo "Saved log to ${LOG_FILE}"
