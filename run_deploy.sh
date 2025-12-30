#!/bin/bash
# Deploy data to Supabase
# Usage: ./run_deploy.sh                         # Deploy all tables
#        ./run_deploy.sh --scope table --table dim_player --operation replace
#        ./run_deploy.sh --counts                # Check row counts
#        ./run_deploy.sh --dry-run               # Preview what would happen

cd "$(dirname "$0")"

if [ $# -eq 0 ]; then
    # Default: deploy all with replace
    python scripts/flexible_loader.py --scope full --operation replace
else
    python scripts/flexible_loader.py "$@"
fi
