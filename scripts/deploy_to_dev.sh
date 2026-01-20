#!/bin/bash
# Deploy to Development Environment
# Usage: ./scripts/deploy_to_dev.sh

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Track status for summary
ETL_STATUS="⏭️  Skipped"
UPLOAD_STATUS="⏭️  Skipped"
VERCEL_STATUS="⏭️  Skipped"

echo "=========================================="
echo "🚀 Deploying to DEVELOPMENT Environment"
echo "=========================================="
echo ""

# Pre-flight checks
echo "📋 Pre-flight checks..."
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
if [ "$CURRENT_BRANCH" = "unknown" ]; then
    echo "⚠️  Warning: Not in a git repository"
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
    echo "⚠️  Warning: You have uncommitted changes"
    read -p "   Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Deployment cancelled"
        exit 1
    fi
fi

# Step 1: Switch to dev environment
echo ""
echo "📋 Step 1: Switching to dev environment..."
if [ -f "$PROJECT_ROOT/scripts/switch_env.sh" ]; then
    if ./scripts/switch_env.sh dev; then
        echo "   ✅ Switched to dev environment"
    else
        echo "   ⚠️  Environment switch had issues, continuing..."
    fi
else
    echo "⚠️  switch_env.sh not found, continuing with current config"
fi

# Step 2: Verify dev config
echo ""
echo "📋 Step 2: Verifying dev configuration..."
if [ -f "$PROJECT_ROOT/config/config_local.ini" ]; then
    SUPABASE_URL=$(grep "^url = " "$PROJECT_ROOT/config/config_local.ini" | cut -d'=' -f2 | xargs || echo "")
    if [ -n "$SUPABASE_URL" ]; then
        echo "   Supabase URL: ${SUPABASE_URL:0:50}..."
        echo ""
        read -p "Is this your DEV Supabase URL? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo ""
            echo "❌ Please update config/config_local.ini with your dev Supabase URL"
            echo "   Then run this script again"
            exit 1
        fi
    else
        echo "⚠️  Could not read Supabase URL from config"
        read -p "   Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo "❌ config/config_local.ini not found"
    echo "   Please create it with your dev Supabase credentials"
    exit 1
fi

# Step 3: Run ETL
echo ""
echo "📋 Step 3: Running ETL..."
read -p "Run ETL to generate tables? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo "   Running ETL..."
    if python3 run_etl.py; then
        echo "   ✅ ETL completed"
        ETL_STATUS="✅ Completed"
    else
        echo "   ❌ ETL failed"
        ETL_STATUS="❌ Failed"
        read -p "   Continue with deployment? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo "   ⏭️  Skipping ETL"
fi

# Step 4: Upload to dev Supabase
echo ""
echo "📋 Step 4: Uploading to dev Supabase..."
read -p "Upload tables to dev Supabase? (Y/n): " -n 1 -r
UPLOAD_REPLY=$REPLY
echo
if [[ ! $UPLOAD_REPLY =~ ^[Nn]$ ]]; then
    echo "   Uploading..."
    if python3 upload.py; then
        echo "   ✅ Upload completed"
        UPLOAD_STATUS="✅ Completed"
    else
        echo "   ❌ Upload failed"
        UPLOAD_STATUS="❌ Failed"
        read -p "   Continue with deployment? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo "   ⏭️  Skipping upload"
fi

# Step 5: Deploy to Vercel dev
echo ""
echo "📋 Step 5: Deploying to Vercel dev..."
echo "   (This will deploy the develop branch to Vercel dev project)"
echo ""
read -p "Push to GitHub develop branch to trigger Vercel deploy? (Y/n): " -n 1 -r
VERCEL_REPLY=$REPLY
echo
if [[ ! $VERCEL_REPLY =~ ^[Nn]$ ]]; then
    # Check current branch
    CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
    echo ""
    echo "   Current branch: $CURRENT_BRANCH"
    
    if [ "$CURRENT_BRANCH" != "develop" ]; then
        echo "   ⚠️  You're not on develop branch"
        read -p "   Switch to develop and push? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if git checkout develop && git add .; then
                if [ -n "$(git status --porcelain)" ]; then
                    git commit -m "chore: update for dev deployment" || true
                fi
                if git push origin develop; then
                    echo "   ✅ Pushed to develop branch"
                    echo "   Vercel will auto-deploy to dev environment"
                    VERCEL_STATUS="✅ Deployed"
                else
                    echo "   ❌ Failed to push to develop"
                    VERCEL_STATUS="❌ Failed"
                fi
            else
                echo "   ❌ Failed to checkout develop or stage files"
                VERCEL_STATUS="❌ Failed"
            fi
        else
            echo "   ⏭️  Skipping Vercel deploy"
        fi
    else
        if git add .; then
            if [ -n "$(git status --porcelain)" ]; then
                git commit -m "chore: update for dev deployment" || true
            fi
            if git push origin develop; then
                echo "   ✅ Pushed to develop branch"
                echo "   Vercel will auto-deploy to dev environment"
                VERCEL_STATUS="✅ Deployed"
            else
                echo "   ❌ Failed to push to develop"
                VERCEL_STATUS="❌ Failed"
            fi
        else
            echo "   ❌ Failed to stage files"
            VERCEL_STATUS="❌ Failed"
        fi
    fi
else
    echo "   ⏭️  Skipping Vercel deploy"
fi

echo ""
echo "=========================================="
echo "✅ Development Deployment Complete!"
echo "=========================================="
echo ""
echo "📊 Summary:"
echo "   - ETL: $ETL_STATUS"
echo "   - Upload: $UPLOAD_STATUS"
echo "   - Vercel: $VERCEL_STATUS"
echo ""
echo "🔗 Check your dev environment:"
echo "   - Vercel: https://benchsight-dev.vercel.app"
echo "   - Supabase: Check your dev project dashboard"
echo ""
