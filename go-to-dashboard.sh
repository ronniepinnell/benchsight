#!/bin/bash
# Helper script to navigate to dashboard directory

cd "$(dirname "$0")/ui/dashboard" || {
    echo "Error: Could not find ui/dashboard directory"
    echo "Make sure you're running this from the project root"
    exit 1
}

echo "✅ Navigated to dashboard directory"
echo "Current directory: $(pwd)"
echo ""
echo "Now run:"
echo "  npm install"
echo "  npm run dev"
