#!/bin/bash
#SBATCH --job-name=translation_with_llm
#SBATCH --partition=intelsr_short
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=5
#SBATCH --time=03:00:00
#SBATCH --output=data/outputs/translation_with_llm_%j.out
#SBATCH --error=data/outputs/translation_with_llm_%j.err

set -euo pipefail

# Find the project folder.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

python python_scripts/translation_with_llm.py
