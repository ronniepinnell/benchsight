#!/bin/bash
# sync-github-issues.sh - Sync GitHub issues status with GITHUB_ISSUES_BACKLOG.md
#
# Usage:
#   ./scripts/sync-github-issues.sh              # Update backlog with current status
#   ./scripts/sync-github-issues.sh --check      # Check only (no file changes)
#
# This script:
# 1. Queries GitHub for current issue counts
# 2. Updates the sync status section in GITHUB_ISSUES_BACKLOG.md
# 3. Can be run manually or via commit hook

set -e

# Configuration
BACKLOG_FILE="docs/GITHUB_ISSUES_BACKLOG.md"
CHECK_ONLY=false

# Parse arguments
if [[ "$1" == "--check" ]]; then
    CHECK_ONLY=true
fi

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "⚠️  GitHub CLI (gh) not installed. Skipping issue sync."
    exit 0
fi

# Check if authenticated
if ! gh auth status &> /dev/null 2>&1; then
    echo "⚠️  Not authenticated with GitHub. Skipping issue sync."
    exit 0
fi

# Get counts from GitHub
echo "📊 Querying GitHub issues..."

TOTAL_ISSUES=$(gh issue list --state all --limit 1000 --json number | jq length)
OPEN_ISSUES=$(gh issue list --state open --limit 1000 --json number | jq length)
CLOSED_ISSUES=$(gh issue list --state closed --limit 1000 --json number | jq length)

# Get phase 2 counts
PHASE2_OPEN=$(gh issue list --label "phase:2" --state open --limit 100 --json number | jq length)
PHASE2_CLOSED=$(gh issue list --label "phase:2" --state closed --limit 100 --json number | jq length)

# Get P0 counts
P0_OPEN=$(gh issue list --label "priority:p0" --state open --limit 100 --json number | jq length)
P0_CLOSED=$(gh issue list --label "priority:p0" --state closed --limit 100 --json number | jq length)

# Calculate documented vs gap (estimate ~211 documented)
DOCUMENTED=211
GAP=$((DOCUMENTED - TOTAL_ISSUES))

# Display results
echo ""
echo "GitHub Issues Status:"
echo "  Total in GitHub: $TOTAL_ISSUES"
echo "  Open: $OPEN_ISSUES"
echo "  Closed: $CLOSED_ISSUES"
echo "  Gap (not yet created): $GAP"
echo ""
echo "Phase 2 (Current):"
echo "  Open: $PHASE2_OPEN"
echo "  Closed: $PHASE2_CLOSED"
echo ""
echo "P0 Priority:"
echo "  Open: $P0_OPEN"
echo "  Closed: $P0_CLOSED"

if [[ "$CHECK_ONLY" == true ]]; then
    echo ""
    echo "✅ Check complete (no changes made)"
    exit 0
fi

# Update the backlog file
if [[ -f "$BACKLOG_FILE" ]]; then
    echo ""
    echo "📝 Updating $BACKLOG_FILE..."

    # Create temp file with updated counts
    # We'll update the sync status table using sed
    TODAY=$(date +%Y-%m-%d)

    # Update the counts in the table
    sed -i '' \
        -e "s/| \*\*In GitHub\*\* | [0-9]* |/| **In GitHub** | $TOTAL_ISSUES |/" \
        -e "s/| \*\*Open\*\* | [0-9]* |/| **Open** | $OPEN_ISSUES |/" \
        -e "s/| \*\*Closed\*\* | [0-9]* |/| **Closed** | $CLOSED_ISSUES |/" \
        -e "s/| \*\*Gap (not yet created)\*\* | ~[0-9]* |/| **Gap (not yet created)** | ~$GAP |/" \
        -e "s/Last Updated: [0-9-]*/Last Updated: $TODAY/" \
        "$BACKLOG_FILE"

    echo "✅ Backlog file updated"
else
    echo "⚠️  Backlog file not found: $BACKLOG_FILE"
    exit 1
fi

echo ""
echo "Done! Review changes with: git diff $BACKLOG_FILE"
