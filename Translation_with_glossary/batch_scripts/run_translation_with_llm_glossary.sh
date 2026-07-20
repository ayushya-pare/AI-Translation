#!/bin/bash
#SBATCH --job-name=translation_with_llm_glossary
#SBATCH --partition=intelsr_devel
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=5
#SBATCH --time=00:30:00
#SBATCH --output=logs/translation_with_llm_glossary_%j.out
#SBATCH --error=logs/translation_with_llm_glossary_%j.err

set -euo pipefail

python python_scripts/translation_with_llm_glossary.py
