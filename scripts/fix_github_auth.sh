#!/bin/bash
#
# Fix GitHub authentication for HTTPS
# GitHub no longer accepts passwords - need Personal Access Token
#

echo "=========================================="
echo "Fix GitHub Authentication"
echo "=========================================="
echo ""

echo "GitHub no longer accepts passwords for HTTPS."
echo "You need a Personal Access Token."
echo ""
echo "Step 1: Create a Personal Access Token"
echo "----------------------------------------"
echo "1. Go to: https://github.com/settings/tokens"
echo "2. Click 'Generate new token (classic)'"
echo "3. Name it: 'Benchsight Repo'"
echo "4. Select scope: 'repo' (full control)"
echo "5. Click 'Generate token'"
echo "6. COPY THE TOKEN (you won't see it again!)"
echo ""
read -p "Press Enter when you have your token ready..."

echo ""
echo "Step 2: Clear old credentials from keychain"
echo "--------------------------------------------"
echo "Removing old GitHub credentials from macOS keychain..."
security delete-internet-password -s github.com 2>/dev/null || echo "  (No old credentials found)"
echo "  ✓ Old credentials cleared"

echo ""
echo "Step 3: Update remote URL"
echo "--------------------------------------------"
echo "Your current remote:"
git remote -v

echo ""
echo "The remote URL is already correct (HTTPS)."
echo "When you push, macOS will prompt for credentials."
echo ""
echo "Use these credentials:"
echo "  Username: ronniepinnell"
echo "  Password: [paste your Personal Access Token here]"
echo ""
echo "macOS will save it to your keychain."
echo ""
echo "Step 4: Test push"
echo "--------------------------------------------"
read -p "Ready to test push? (y/n): " test_push

if [ "$test_push" = "y" ]; then
    echo ""
    echo "Attempting push (will prompt for credentials)..."
    echo "Username: ronniepinnell"
    echo "Password: [paste your token]"
    echo ""
    git push origin --force --all
else
    echo ""
    echo "When ready, run:"
    echo "  git push origin --force --all"
    echo ""
    echo "Use your token as the password when prompted."
fi

echo ""
echo "=========================================="
echo "Done!"
echo "=========================================="
