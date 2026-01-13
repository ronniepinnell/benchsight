#!/bin/bash
#
# Unstage and untrack files that should be ignored
# This will reduce the 32k files to just the code changes
#

set -e

echo "=========================================="
echo "Fixing Staging - Removing Large Files"
echo "=========================================="
echo ""

echo "Current files staged:"
git status --short | wc -l | xargs echo "  Total:"

echo ""
echo "Step 1: Unstaging data/output CSV files..."
git reset HEAD data/output/*.csv 2>/dev/null || true
echo "  ✓ Unstaged CSV files"

echo ""
echo "Step 2: Unstaging data/output JSON files..."
git reset HEAD data/output/*.json 2>/dev/null || true
echo "  ✓ Unstaged JSON files"

echo ""
echo "Step 3: Removing data/output files from git tracking..."
git rm --cached data/output/*.csv 2>/dev/null || true
git rm --cached data/output/*.json 2>/dev/null || true
echo "  ✓ Removed from tracking"

echo ""
echo "Step 4: Removing data/raw Excel files..."
git rm --cached "data/raw/games/"*/*.xlsx 2>/dev/null || true
git rm --cached "data/raw/"*.xlsx 2>/dev/null || true
echo "  ✓ Removed Excel files"

echo ""
echo "Step 5: Removing node_modules if tracked..."
find . -name "node_modules" -type d -exec git rm -r --cached {} + 2>/dev/null || true
echo "  ✓ Removed node_modules"

echo ""
echo "Step 6: Removing .next build files..."
find . -name ".next" -type d -exec git rm -r --cached {} + 2>/dev/null || true
echo "  ✓ Removed .next files"

echo ""
echo "Step 7: Checking remaining files..."
REMAINING=$(git status --short | wc -l | tr -d ' ')
echo "  Files remaining: $REMAINING"

echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="
echo ""
echo "Files that should be committed:"
git status --short | head -30

if [ "$REMAINING" -gt 1000 ]; then
    echo ""
    echo "⚠️  Still many files. Checking what's left..."
    git status --short | grep -v "data/output" | grep -v "data/raw" | grep -v "node_modules" | grep -v ".next" | head -20
fi

echo ""
echo "=========================================="
echo "Next Steps"
echo "=========================================="
echo ""
echo "1. Review what's left:"
echo "   git status"
echo ""
echo "2. Add .gitignore and .gitattributes:"
echo "   git add .gitignore .gitattributes"
echo ""
echo "3. Commit only the code changes:"
echo "   git commit -m 'Add .gitignore and remove large files from tracking'"
echo ""
echo "4. Push (use command line - more reliable):"
echo "   git push origin --force --all"
echo ""
