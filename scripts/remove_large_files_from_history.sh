#!/bin/bash
#
# Remove large files from git history
# WARNING: This rewrites git history - coordinate with team if working together
#

set -e

echo "=========================================="
echo "Removing Large Files from Git History"
echo "=========================================="
echo ""
echo "⚠️  WARNING: This will rewrite git history!"
echo "⚠️  Make sure you have a backup and coordinate with your team"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "Step 1: Creating backup branch..."
git branch backup-before-cleanup-$(date +%Y%m%d-%H%M%S)
echo "  ✓ Backup branch created"

echo ""
echo "Step 2: Removing large files from history..."
echo "  This may take several minutes..."

# Remove large CSV files from data/output
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch 'data/output/*.csv' 'data/output/*.json'" \
  --prune-empty --tag-name-filter cat -- --all

# Remove large Excel files from data/raw
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch 'data/raw/**/*.xlsx' 'data/raw/*.xlsx'" \
  --prune-empty --tag-name-filter cat -- --all

# Remove old backup directories
git filter-branch --force --index-filter \
  "git rm -r --cached --ignore-unmatch 'data/output_backup*' 'app/data' 'archive' 2>/dev/null || true" \
  --prune-empty --tag-name-filter cat -- --all

echo ""
echo "Step 3: Cleaning up..."
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo ""
echo "=========================================="
echo "Done! Next steps:"
echo "=========================================="
echo ""
echo "1. Check the repository size:"
echo "   du -sh .git"
echo ""
echo "2. Verify large files are gone:"
echo "   git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | awk '/^blob/ {print substr(\$0,6)}' | sort -k2 -n -r | head -10"
echo ""
echo "3. Force push to remote (WARNING: This rewrites remote history):"
echo "   git push origin --force --all"
echo "   git push origin --force --tags"
echo ""
echo "⚠️  IMPORTANT:"
echo "   - Make sure all team members are aware"
echo "   - They will need to re-clone or reset their local repos"
echo "   - Backup branch created: backup-before-cleanup-*"
echo ""
