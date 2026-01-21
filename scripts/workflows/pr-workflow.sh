#!/bin/bash
# =============================================================================
# PR Workflow Helper
# =============================================================================
# Helper script for PR creation workflow
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

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check git status
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "Not a git repository"
    exit 1
fi

CURRENT_BRANCH=$(git branch --show-current)

if [ "$CURRENT_BRANCH" == "main" ] || [ "$CURRENT_BRANCH" == "develop" ]; then
    print_error "Cannot create PR from $CURRENT_BRANCH branch"
    exit 1
fi

print_header "PR Creation Checklist"

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    print_warning "You have uncommitted changes"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

# Check if branch is pushed
if ! git rev-parse --abbrev-ref --symbolic-full-name @{u} > /dev/null 2>&1; then
    print_warning "Branch not pushed to remote"
    read -p "Push branch now? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push -u origin "$CURRENT_BRANCH"
        print_success "Branch pushed"
    else
        print_info "Push branch manually: git push -u origin $CURRENT_BRANCH"
    fi
fi

# PR Checklist
echo ""
print_info "PR Checklist:"
echo "  [ ] Code follows standards"
echo "  [ ] Tests pass"
echo "  [ ] Documentation updated"
echo "  [ ] No breaking changes (or documented)"
echo "  [ ] CodeRabbit feedback addressed"
echo ""

# Open PR
print_info "Opening PR creation page..."

if command -v gh &> /dev/null; then
    gh pr create --web
else
    REMOTE=$(git remote get-url origin)
    if [[ $REMOTE == *"github.com"* ]]; then
        REPO=$(echo $REMOTE | sed 's/.*github.com[:/]\(.*\)\.git/\1/')
        PR_URL="https://github.com/$REPO/compare/$CURRENT_BRANCH"
        print_info "Create PR at: $PR_URL"
        if command -v open &> /dev/null; then
            open "$PR_URL"
        elif command -v xdg-open &> /dev/null; then
            xdg-open "$PR_URL"
        fi
    else
        print_info "Push your branch and create PR manually"
    fi
fi
