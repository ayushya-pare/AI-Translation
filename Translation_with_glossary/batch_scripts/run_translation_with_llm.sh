#!/bin/bash
#SBATCH --job-name=translation_with_llm
#SBATCH --partition=intelsr_short
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=5
#SBATCH --time=03:00:00
#SBATCH --output=logs/translation_with_llm_%j.out
#SBATCH --error=logs/translation_with_llm_%j.err

set -euo pipefail

# Slurm executes a spooled copy of this script, so BASH_SOURCE points under
# /var/spool/slurmd rather than to this repository.
ROOT="/lustre/scratch/data/apare_hpc-HPCA/hpca/AI-Translation/Translation_with_glossary"
cd "${ROOT}"

python "${ROOT}/python_scripts/translation_with_llm.py"
