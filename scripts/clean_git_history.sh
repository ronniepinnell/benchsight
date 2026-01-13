#!/bin/bash
#
# Remove large files from git history using git filter-branch
# Run this from the project root directory
#

set -e

echo "=========================================="
echo "Removing Large Files from Git History"
echo "=========================================="
echo ""
echo "⚠️  WARNING: This will rewrite git history!"
echo "⚠️  Make sure you have a backup"
echo ""
read -p "Continue? (type 'yes' to continue): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "Step 1: Creating backup branch..."
BACKUP_BRANCH="backup-before-cleanup-$(date +%Y%m%d-%H%M%S)"
git branch "$BACKUP_BRANCH"
echo "  ✓ Backup branch created: $BACKUP_BRANCH"

echo ""
echo "Step 2: Removing large CSV files from history..."
echo "  This may take 5-10 minutes..."

git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch data/output/*.csv data/output/*.json' \
  --prune-empty --tag-name-filter cat -- --all

echo ""
echo "Step 3: Removing large Excel files from history..."

git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch "data/raw/games/**/*.xlsx" "data/raw/*.xlsx" "data/BLB_Tables.xlsx" "data/BLB_TABLES.xlsx"' \
  --prune-empty --tag-name-filter cat -- --all

echo ""
echo "Step 4: Removing old backup directories..."

git filter-branch --force --index-filter \
  'git rm -r --cached --ignore-unmatch data/output_backup* app/data archive 2>/dev/null || true' \
  --prune-empty --tag-name-filter cat -- --all

echo ""
echo "Step 5: Cleaning up git objects..."
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin || true
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo ""
echo "=========================================="
echo "✅ Done!"
echo "=========================================="
echo ""
echo "Repository size:"
du -sh .git
echo ""
echo "Next steps:"
echo "1. Verify cleanup worked:"
echo "   du -sh .git"
echo ""
echo "2. Force push to remote (WARNING: Rewrites remote history):"
echo "   git push origin --force --all"
echo "   git push origin --force --tags"
echo ""
echo "3. Backup branch: $BACKUP_BRANCH"
echo ""
