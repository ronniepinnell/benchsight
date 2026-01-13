#!/bin/bash
#
# Unstage files that should be ignored
# Run this before committing
#

set -e

echo "=========================================="
echo "Unstaging Files That Should Be Ignored"
echo "=========================================="
echo ""

# Check .gitignore exists
if [ ! -f .gitignore ]; then
    echo "❌ .gitignore not found! Creating it..."
    # .gitignore should already exist, but just in case
    exit 1
fi

echo "Step 1: Removing data/output files from staging..."
git reset HEAD data/output/*.csv 2>/dev/null || echo "  (No CSV files to unstage)"
git reset HEAD data/output/*.json 2>/dev/null || echo "  (No JSON files to unstage)"

echo ""
echo "Step 2: Removing data/raw Excel files from staging..."
git reset HEAD "data/raw/games/**/*.xlsx" 2>/dev/null || echo "  (No Excel files to unstage)"
git reset HEAD "data/raw/*.xlsx" 2>/dev/null || echo "  (No Excel files to unstage)"

echo ""
echo "Step 3: Removing node_modules from staging..."
git reset HEAD ui/**/node_modules/ 2>/dev/null || echo "  (No node_modules to unstage)"

echo ""
echo "Step 4: Removing .next build files from staging..."
git reset HEAD ui/**/.next/ 2>/dev/null || echo "  (No .next files to unstage)"

echo ""
echo "Step 5: Removing from git tracking (but keeping local files)..."
git rm --cached -r data/output/*.csv 2>/dev/null || echo "  (No CSV files to remove)"
git rm --cached -r data/output/*.json 2>/dev/null || echo "  (No JSON files to remove)"
git rm --cached -r "data/raw/games/**/*.xlsx" 2>/dev/null || echo "  (No Excel files to remove)"
git rm --cached -r ui/**/node_modules/ 2>/dev/null || echo "  (No node_modules to remove)"
git rm --cached -r ui/**/.next/ 2>/dev/null || echo "  (No .next files to remove)"

echo ""
echo "Step 6: Checking what's left to commit..."
REMAINING=$(git status --short | wc -l | tr -d ' ')
echo "  Files remaining: $REMAINING"

if [ "$REMAINING" -lt 100 ]; then
    echo ""
    echo "✅ Good! Only $REMAINING files left to commit"
    echo ""
    echo "Files to commit:"
    git status --short | head -20
else
    echo ""
    echo "⚠️  Still $REMAINING files. Showing first 20:"
    git status --short | head -20
    echo ""
    echo "You may need to review what should be committed."
fi

echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo ""
echo "1. Review what's left to commit:"
echo "   git status"
echo ""
echo "2. If looks good, commit:"
echo "   git add .gitignore .gitattributes"
echo "   git commit -m 'Add .gitignore and remove large files from tracking'"
echo ""
echo "3. Then push (from command line is more reliable):"
echo "   git push origin --force --all"
echo ""
