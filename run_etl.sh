#!/bin/bash
# Run the BenchSight ETL pipeline
# Usage: ./run_etl.sh --game 18969
#        ./run_etl.sh --games 18969,18977,18981
#        ./run_etl.sh --export

cd "$(dirname "$0")"
PYTHONPATH="$(pwd)" python src/main.py "$@"
