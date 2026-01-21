#!/bin/bash
# Quick script to run ETL to dev Supabase

set -e

echo "=========================================="
echo "Running ETL to Dev Supabase"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "run_etl.py" ]; then
    echo "❌ Error: run_etl.py not found"
    echo "   Make sure you're in the project root directory"
    exit 1
fi

# Check current config
echo "📋 Current Supabase configuration:"
if [ -f "config/config_local.ini" ]; then
    echo "   URL: $(grep '^url = ' config/config_local.ini | cut -d'=' -f2 | xargs)"
    echo ""
    read -p "Is this the dev Supabase URL? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "⚠️  Please update config/config_local.ini with your dev Supabase URL"
        echo "   Then run this script again"
        exit 1
    fi
else
    echo "❌ config/config_local.ini not found"
    echo "   Please create it with your dev Supabase credentials"
    exit 1
fi

# Run ETL
echo ""
echo "🚀 Running ETL..."
echo ""

python3 run_etl.py

echo ""
echo "✅ ETL completed!"
echo ""
echo "📤 Next step: Upload to Supabase"
read -p "Upload to dev Supabase now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "📤 Uploading to dev Supabase..."
    python3 upload.py
    echo ""
    echo "✅ Upload completed!"
    echo ""
    echo "🎉 Done! Check your dev Supabase dashboard to verify data."
else
    echo ""
    echo "To upload later, run: python3 upload.py"
fi
