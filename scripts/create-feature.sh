#!/bin/bash
# BenchSight Feature Branch Creator
# Creates a properly named feature branch and optionally opens GitHub issue

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Help
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    echo "Usage: ./scripts/create-feature.sh <type> <name> [--issue]"
    echo ""
    echo "Types:"
    echo "  feature   - New feature"
    echo "  fix       - Bug fix"
    echo "  refactor  - Code restructuring"
    echo "  docs      - Documentation"
    echo "  perf      - Performance improvement"
    echo ""
    echo "Examples:"
    echo "  ./scripts/create-feature.sh feature dashboard-xg-analysis"
    echo "  ./scripts/create-feature.sh fix etl-goal-counting --issue"
    echo "  ./scripts/create-feature.sh refactor etl-modularization"
    echo ""
    exit 0
fi

# Validate arguments
if [ -z "$1" ] || [ -z "$2" ]; then
    echo -e "${RED}Error: Missing arguments${NC}"
    echo "Usage: ./scripts/create-feature.sh <type> <name>"
    echo "Run with --help for more info"
    exit 1
fi

TYPE=$1
NAME=$2
CREATE_ISSUE=false

if [ "$3" = "--issue" ]; then
    CREATE_ISSUE=true
fi

# Validate type
case $TYPE in
    feature|fix|refactor|docs|perf)
        ;;
    *)
        echo -e "${RED}Error: Invalid type '$TYPE'${NC}"
        echo "Valid types: feature, fix, refactor, docs, perf"
        exit 1
        ;;
esac

BRANCH_NAME="$TYPE/$NAME"

echo -e "${BLUE}Creating branch: $BRANCH_NAME${NC}"
echo ""

# Ensure we're on develop and up to date
echo "[1/3] Updating develop branch..."
git checkout develop
git pull origin develop
echo ""

# Create branch
echo "[2/3] Creating feature branch..."
git checkout -b "$BRANCH_NAME"
echo ""

# Summary
echo -e "${GREEN}========================================"
echo "  Branch created successfully!"
echo "========================================${NC}"
echo ""
echo "Branch: $BRANCH_NAME"
echo ""
echo "Next steps:"
echo "  1. Make your changes"
echo "  2. Commit: git commit -m \"[$TYPE] Description\""
echo "  3. Push: git push -u origin $BRANCH_NAME"
echo "  4. Create PR on GitHub"
echo ""

# Optionally open GitHub to create issue
if [ "$CREATE_ISSUE" = true ]; then
    echo "[3/3] Opening GitHub to create issue..."
    REPO_URL=$(git config --get remote.origin.url | sed 's/\.git$//' | sed 's/git@github.com:/https:\/\/github.com\//')
    open "$REPO_URL/issues/new/choose" 2>/dev/null || echo "Open: $REPO_URL/issues/new/choose"
fi

echo "Documentation: docs/workflows/QUICKSTART_WORKFLOW.md"
echo ""
