#!/bin/bash
#
# Push to GitHub using Personal Access Token
# Usage: ./scripts/push_with_token.sh YOUR_TOKEN
#

if [ -z "$1" ]; then
    echo "Usage: ./scripts/push_with_token.sh YOUR_GITHUB_TOKEN"
    echo ""
    echo "Get a token from: https://github.com/settings/tokens"
    exit 1
fi

TOKEN="$1"
REPO_URL="https://${TOKEN}@github.com/ronniepinnell/benchsight.git"

echo "Pushing to GitHub..."
echo ""

# Push using token in URL
git push "${REPO_URL}" --force --all

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Push successful!"
    echo ""
    echo "To avoid entering token each time, you can:"
    echo "1. Use SSH (recommended):"
    echo "   git remote set-url origin git@github.com:ronniepinnell/benchsight.git"
    echo ""
    echo "2. Or use credential helper (will save token):"
    echo "   git config credential.helper osxkeychain"
    echo "   git push origin --force --all"
    echo "   (Enter token when prompted, macOS will save it)"
else
    echo ""
    echo "❌ Push failed. Check:"
    echo "  - Token is correct"
    echo "  - Token has 'repo' scope"
    echo "  - You have push access to the repository"
fi
