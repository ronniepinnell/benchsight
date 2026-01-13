#!/bin/bash
#
# Fix Git "file too large" errors
# This script helps remove large files from git tracking and history
#

set -e

echo "=========================================="
echo "Fixing Git Large Files Issue"
echo "=========================================="
echo ""

# Step 1: Remove large files from git tracking (but keep local files)
echo "Step 1: Removing large files from git tracking..."
echo ""

# Remove data/output CSV files from tracking
git rm --cached data/output/*.csv 2>/dev/null || echo "  (No CSV files to remove)"
git rm --cached data/output/*.json 2>/dev/null || echo "  (No JSON files to remove)"

# Remove large Excel files from tracking
git rm --cached data/raw/games/**/*.xlsx 2>/dev/null || echo "  (No Excel files to remove)"
git rm --cached data/raw/*.xlsx 2>/dev/null || echo "  (No Excel files to remove)"

# Remove node_modules if tracked
git rm -r --cached ui/**/node_modules/ 2>/dev/null || echo "  (No node_modules to remove)"
git rm -r --cached ui/**/.next/ 2>/dev/null || echo "  (No .next to remove)"

echo ""
echo "Step 2: Checking for Git LFS..."
if command -v git-lfs &> /dev/null; then
    echo "  Git LFS is installed"
    git lfs install
    echo "  Git LFS initialized"
else
    echo "  Git LFS not installed. Install with: brew install git-lfs"
    echo "  Or download from: https://git-lfs.github.com/"
fi

echo ""
echo "Step 3: Summary of changes..."
echo ""
echo "Files removed from tracking (but kept locally):"
git status --short | head -20

echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo ""
echo "1. Review the changes:"
echo "   git status"
echo ""
echo "2. Commit the .gitignore and .gitattributes:"
echo "   git add .gitignore .gitattributes"
echo "   git commit -m 'Add .gitignore and Git LFS config for large files'"
echo ""
echo "3. If you need to remove large files from git history:"
echo "   git filter-branch --tree-filter 'rm -f data/output/*.csv' HEAD"
echo "   (Warning: This rewrites history - only do if necessary)"
echo ""
echo "4. Push your changes:"
echo "   git push"
echo ""
