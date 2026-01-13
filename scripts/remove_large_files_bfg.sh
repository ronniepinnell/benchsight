#!/bin/bash
#
# Remove large files from git history using BFG Repo-Cleaner
# BFG is faster and easier than git filter-branch
#

set -e

echo "=========================================="
echo "Remove Large Files with BFG Repo-Cleaner"
echo "=========================================="
echo ""
echo "BFG is faster and safer than git filter-branch"
echo ""

# Check if BFG is installed
if ! command -v bfg &> /dev/null; then
    echo "❌ BFG is not installed"
    echo ""
    echo "Install with:"
    echo "  brew install bfg"
    echo ""
    echo "Or download from: https://rtyley.github.io/bfg-repo-cleaner/"
    exit 1
fi

echo "✓ BFG is installed"
echo ""
echo "⚠️  WARNING: This will rewrite git history!"
echo "⚠️  Make sure you have a backup"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "Step 1: Creating backup branch..."
git branch backup-before-bfg-$(date +%Y%m%d-%H%M%S)
echo "  ✓ Backup branch created"

echo ""
echo "Step 2: Removing files larger than 5MB..."
bfg --strip-blobs-bigger-than 5M

echo ""
echo "Step 3: Cleaning up..."
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo ""
echo "=========================================="
echo "Done! Next steps:"
echo "=========================================="
echo ""
echo "1. Check repository size:"
echo "   du -sh .git"
echo ""
echo "2. Force push (WARNING: Rewrites remote history):"
echo "   git push origin --force --all"
echo "   git push origin --force --tags"
echo ""
