#!/bin/bash
#SBATCH --job-name=translation_evaluator
#SBATCH --partition=mlgpu_devel
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=5
#SBATCH --time=00:30:00
#SBATCH --output=logs/translation_evaluator_%j.out
#SBATCH --error=logs/translation_evaluator_%j.err

set -euo pipefail

python python_scripts/translation_evaluator.py
