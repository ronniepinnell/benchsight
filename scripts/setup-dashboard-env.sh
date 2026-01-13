#!/bin/bash
# Script to create .env.local for dashboard from config/config_local.ini

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_FILE="$PROJECT_ROOT/config/config_local.ini"
ENV_FILE="$PROJECT_ROOT/ui/dashboard/.env.local"

echo "🔧 Setting up dashboard environment variables..."
echo ""

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Error: $CONFIG_FILE not found"
    exit 1
fi

# Extract Supabase URL from config
SUPABASE_URL=$(grep -E "^url\s*=" "$CONFIG_FILE" | sed 's/.*=\s*//' | tr -d ' ')

if [ -z "$SUPABASE_URL" ]; then
    echo "❌ Error: Could not find Supabase URL in config file"
    exit 1
fi

echo "✅ Found Supabase URL: $SUPABASE_URL"
echo ""

# Check if .env.local already exists
if [ -f "$ENV_FILE" ]; then
    echo "⚠️  .env.local already exists"
    read -p "   Overwrite? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "   Keeping existing file"
        exit 0
    fi
fi

# Create .env.local
cat > "$ENV_FILE" << EOF
# Auto-generated from config/config_local.ini
# Next.js Dashboard Environment Variables

NEXT_PUBLIC_SUPABASE_URL=$SUPABASE_URL
NEXT_PUBLIC_SUPABASE_ANON_KEY=REPLACE_WITH_YOUR_ANON_KEY
EOF

echo "✅ Created $ENV_FILE"
echo ""
echo "⚠️  IMPORTANT: You need to add your Supabase ANON KEY"
echo ""
echo "   1. Go to: https://supabase.com/dashboard/project/$(echo $SUPABASE_URL | sed 's|https://||' | sed 's|\.supabase\.co||')/settings/api"
echo "   2. Find 'anon public' key (NOT service_role key)"
echo "   3. Replace 'REPLACE_WITH_YOUR_ANON_KEY' in $ENV_FILE"
echo ""
echo "   Or edit the file manually:"
echo "   nano $ENV_FILE"
echo ""
