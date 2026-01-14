#!/bin/bash
# Setup script to copy portal files to public directory

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DASHBOARD_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$(dirname "$DASHBOARD_DIR")")"
PORTAL_SRC="$PROJECT_ROOT/ui/portal"
PORTAL_DEST="$DASHBOARD_DIR/public/portal"

echo "Setting up portal files..."
echo "Source: $PORTAL_SRC"
echo "Destination: $PORTAL_DEST"

if [ ! -d "$PORTAL_SRC" ]; then
    echo "Error: Portal source directory not found at $PORTAL_SRC"
    echo "Please ensure ui/portal exists in the project root"
    exit 1
fi

# Create destination directory
mkdir -p "$PORTAL_DEST/js"

# Copy files
echo "Copying portal files..."
cp "$PORTAL_SRC/index.html" "$PORTAL_DEST/" 2>/dev/null || echo "Warning: index.html not found"
cp "$PORTAL_SRC/js/"*.js "$PORTAL_DEST/js/" 2>/dev/null || echo "Warning: JS files not found"

echo "Portal files copied successfully!"
echo "Portal is now available at /portal/index.html"
