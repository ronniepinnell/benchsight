#!/bin/bash
# Clear Next.js cache to fix compilation issues

cd "$(dirname "$0")"
echo "Clearing Next.js cache..."
rm -rf .next
echo "Cache cleared! Restart your dev server (npm run dev)"
