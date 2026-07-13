#!/bin/bash
#SBATCH --job-name=corpus_pipeline
#SBATCH --output=logs/corpus_pipeline_%j.out
#SBATCH --error=logs/corpus_pipeline_%j.err
#SBATCH --account=hpca
#SBATCH --partition=intelsr_devel
#SBATCH --time=00:30:00
#SBATCH --exclusive
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --constraint=perfctr



set -eo pipefail

# ---- REQUIRED: replace placeholders ----
export API_KEY="sk-de46f4883b504d16b369b35838a4fdf9"
export BASE_URL="https://openwebui-test.hrz.uni-bonn.de/api" 

# model names:
# Qwen.Qwen3-Omni-30B-A3B-Instruct
# openai.gpt-oss-120b

export MODEL_NAME="${MODEL_NAME:-openai.gpt-oss-120b}"

echo "Running corpus pipeline on $(hostname)..."


# Install requirements locally for this user if missing.
#python -m pip install --user -r requirements.txt

likwid-perfctr -C 0-3 -g FLOPS_DP python scripts/corpus_pipeline.py --translate --model "$MODEL_NAME" --job-number "$SLURM_JOB_ID" --num-workers 4