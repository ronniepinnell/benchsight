#!/bin/bash
# BenchSight Daily Startup Script
# Run this at the start of each development session

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "========================================"
echo "  BenchSight Development Session Start"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Git status
echo -e "${BLUE}[1/5] Git Status${NC}"
echo "Current branch: $(git branch --show-current)"
echo ""

# 2. Pull latest
echo -e "${BLUE}[2/5] Pulling latest from develop...${NC}"
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" = "develop" ]; then
    git pull origin develop
else
    echo -e "${YELLOW}Not on develop branch. Skipping pull.${NC}"
    echo "Run: git checkout develop && git pull"
fi
echo ""

# 3. Switch to dev environment
echo -e "${BLUE}[3/5] Environment${NC}"
if [ -f "./benchsight.sh" ]; then
    ./benchsight.sh env switch dev 2>/dev/null || echo "Environment switch command not available"
    ./benchsight.sh env status 2>/dev/null || echo "Environment status command not available"
else
    echo -e "${YELLOW}benchsight.sh not found. Skipping environment check.${NC}"
fi
echo ""

# 4. Check for uncommitted changes
echo -e "${BLUE}[4/5] Uncommitted Changes${NC}"
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}Warning: You have uncommitted changes:${NC}"
    git status --short
else
    echo -e "${GREEN}Working directory clean.${NC}"
fi
echo ""

# 5. Quick project status
echo -e "${BLUE}[5/5] Quick Status${NC}"
echo "Dashboard: ui/dashboard/"
echo "ETL: src/"
echo "API: api/"
echo "Tests: pytest"
echo ""

echo "========================================"
echo "  Ready to develop!"
echo "========================================"
echo ""
echo "Quick commands:"
echo "  ./benchsight.sh dashboard dev   # Start dashboard"
echo "  ./benchsight.sh api dev         # Start API"
echo "  ./benchsight.sh etl run         # Run ETL"
echo "  pytest                          # Run tests"
echo ""
echo "Start a feature:"
echo "  git checkout -b feature/my-feature"
echo ""
echo "Docs:"
echo "  docs/workflows/QUICKSTART_WORKFLOW.md"
echo ""
