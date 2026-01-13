#!/bin/bash
# =============================================================================
# Auto-archive Documentation Script
# =============================================================================
# Runs archive_docs.py in auto mode (no prompts)
# Can be used in git hooks, cron jobs, or manually
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# Run archive script in auto mode
python3 "$SCRIPT_DIR/archive_docs.py" --auto
