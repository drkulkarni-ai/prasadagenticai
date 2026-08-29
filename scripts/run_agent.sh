#!/usr/bin/env bash
# Example run script
set -euo pipefail

SCIMAGO_CSV="scimago_mapping_example.csv"
python -m prasad_agenticai.cli fetch-articles --quartile Q1 --scimago-file "$SCIMAGO_CSV" --query "neuroscience" --limit 50 --out results.json --fmt json

echo "Done. results.json created."
