#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${API_KEY:-}" ]]; then
  echo "Set API_KEY before running, for example:"
  echo "  export API_KEY='...'"
  exit 1
fi

python tests/test_token.py
