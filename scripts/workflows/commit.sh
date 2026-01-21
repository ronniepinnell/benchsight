#!/bin/bash
# =============================================================================
# Smart Commit Workflow
# =============================================================================
# Interactive commit with checklist and validation
# =============================================================================

set -euo pipefail

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check git status
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "Not a git repository"
    exit 1
fi

# Check for staged changes
if [ -z "$(git diff --cached --name-only)" ]; then
    print_warning "No staged changes"
    read -p "Stage all changes? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add .
    else
        print_info "Stage changes first: git add <files>"
        exit 0
    fi
fi

print_header "Smart Commit Checklist"

# Show staged changes
echo ""
echo "Staged changes:"
git diff --cached --name-only | sed 's/^/  - /'
echo ""

# Pre-commit checks
print_warning "Pre-commit checks:"

# Check for .iterrows()
if git diff --cached --name-only | grep -q "\.py$"; then
    if git diff --cached | grep -q "\.iterrows()"; then
        print_warning "  Found .iterrows() - consider vectorized operations"
    else
        print_success "  No .iterrows() usage"
    fi
fi

# Check for goal counting pattern
if git diff --cached --name-only | grep -q "\.py$"; then
    if git diff --cached | grep -q "event_type.*Goal" && ! git diff --cached | grep -q "Goal_Scored"; then
        print_warning "  Check goal counting - should use GOAL_FILTER pattern"
    fi
fi

# Check commit message format
echo ""
read -p "Commit type [FEAT/FIX/DOCS/REFACTOR/TEST]: " TYPE
TYPE=$(echo "$TYPE" | tr '[:lower:]' '[:upper:]')

if [[ ! "$TYPE" =~ ^(FEAT|FIX|DOCS|REFACTOR|TEST|DEPLOY)$ ]]; then
    print_warning "Invalid type, using FEAT"
    TYPE="FEAT"
fi

read -p "Commit message: " MESSAGE

if [ -z "$MESSAGE" ]; then
    print_error "Commit message required"
    exit 1
fi

COMMIT_MSG="[${TYPE}] ${MESSAGE}"

# Confirm
echo ""
echo "Commit message: ${COMMIT_MSG}"
read -p "Commit? (y/N) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    git commit -m "$COMMIT_MSG"
    print_success "Committed: ${COMMIT_MSG}"
else
    print_info "Cancelled"
    exit 0
fi
