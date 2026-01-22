#!/bin/bash
# Deploy to Production Environment
# Usage: ./scripts/deploy_to_production.sh
# ⚠️  WARNING: This deploys to PRODUCTION. Be careful!

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Track status for summary
ETL_STATUS="⏭️  Skipped"
UPLOAD_STATUS="⏭️  Skipped"
VERCEL_STATUS="⏭️  Skipped"

echo "=========================================="
echo "🚀 Deploying to PRODUCTION Environment"
echo "=========================================="
echo ""
echo "⚠️  WARNING: You are about to deploy to PRODUCTION"
echo "   This will affect live users!"
echo ""

# Confirmation
read -p "Are you sure you want to deploy to PRODUCTION? (yes/no): " -r
echo
if [[ ! $REPLY == "yes" ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

# Pre-flight checks
echo ""
echo "📋 Pre-flight checks..."

# Check current branch
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
if [ "$CURRENT_BRANCH" = "unknown" ]; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
    echo "⚠️  Warning: You have uncommitted changes"
    read -p "   Continue anyway? (yes/no): " -r
    echo
    if [[ ! $REPLY == "yes" ]]; then
        echo "❌ Deployment cancelled"
        exit 1
    fi
fi

# Verify develop branch is up to date
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "⚠️  Warning: You're not on main branch (current: $CURRENT_BRANCH)"
    echo "   Production deployments should be from main branch"
    read -p "   Continue anyway? (yes/no): " -r
    echo
    if [[ ! $REPLY == "yes" ]]; then
        exit 1
    fi
fi

# Step 1: Switch to production environment
echo ""
echo "📋 Step 1: Switching to production environment..."
if [ -f "$PROJECT_ROOT/scripts/switch_env.sh" ]; then
    if ./scripts/switch_env.sh production; then
        echo "   ✅ Switched to production environment"
    else
        echo "   ⚠️  Environment switch had issues, continuing..."
    fi
else
    echo "⚠️  switch_env.sh not found, continuing with current config"
fi

# Step 2: Verify production config
echo ""
echo "📋 Step 2: Verifying production configuration..."
if [ -f "$PROJECT_ROOT/config/config_local.ini" ]; then
    SUPABASE_URL=$(grep "^url = " "$PROJECT_ROOT/config/config_local.ini" | cut -d'=' -f2 | xargs || echo "")
    if [ -n "$SUPABASE_URL" ]; then
        echo "   Supabase URL: ${SUPABASE_URL:0:50}..."
        echo ""
        read -p "Is this your PRODUCTION Supabase URL? (yes/no): " -r
        echo
        if [[ ! $REPLY == "yes" ]]; then
            echo ""
            echo "❌ Please update config/config_local.ini with your production Supabase URL"
            echo "   Then run this script again"
            exit 1
        fi
    else
        echo "⚠️  Could not read Supabase URL from config"
        read -p "   Continue anyway? (yes/no): " -r
        echo
        if [[ ! $REPLY == "yes" ]]; then
            exit 1
        fi
    fi
else
    echo "❌ config/config_local.ini not found"
    echo "   Please create it with your production Supabase credentials"
    exit 1
fi

# Step 3: Run ETL
echo ""
echo "📋 Step 3: Running ETL..."
read -p "Run ETL to generate tables? (Y/n): " -n 1 -r
ETL_REPLY=$REPLY
echo
if [[ ! $ETL_REPLY =~ ^[Nn]$ ]]; then
    echo "   Running ETL..."
    if python3 run_etl.py; then
        echo "   ✅ ETL completed"
        ETL_STATUS="✅ Completed"
    else
        echo "   ❌ ETL failed"
        ETL_STATUS="❌ Failed"
        read -p "   Continue with deployment? (yes/no): " -r
        echo
        if [[ ! $REPLY == "yes" ]]; then
            exit 1
        fi
    fi
else
    echo "   ⏭️  Skipping ETL"
fi

# Step 4: Upload to production Supabase
echo ""
echo "📋 Step 4: Uploading to PRODUCTION Supabase..."
echo "   ⚠️  WARNING: This will update production database!"
echo ""
read -p "Upload tables to PRODUCTION Supabase? (yes/no): " -r
UPLOAD_REPLY=$REPLY
echo
if [[ $UPLOAD_REPLY == "yes" ]]; then
    echo "   Uploading to production..."
    if python3 upload.py; then
        echo "   ✅ Upload completed"
        UPLOAD_STATUS="✅ Completed"
    else
        echo "   ❌ Upload failed"
        UPLOAD_STATUS="❌ Failed"
        read -p "   Continue with deployment? (yes/no): " -r
        echo
        if [[ ! $REPLY == "yes" ]]; then
            exit 1
        fi
    fi
else
    echo "   ⏭️  Skipping upload"
fi

# Step 5: Deploy to Vercel production
echo ""
echo "📋 Step 5: Deploying to Vercel PRODUCTION..."
echo "   ⚠️  WARNING: This will deploy to live production site!"
echo ""
read -p "Push to GitHub main branch to trigger Vercel production deploy? (yes/no): " -r
VERCEL_REPLY=$REPLY
echo
if [[ $VERCEL_REPLY == "yes" ]]; then
    # Check current branch
    CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
    echo ""
    echo "   Current branch: $CURRENT_BRANCH"
    
    if [ "$CURRENT_BRANCH" != "main" ]; then
        echo "   ⚠️  You're not on main branch"
        read -p "   Switch to main and merge develop? (yes/no): " -r
        echo
        if [[ $REPLY == "yes" ]]; then
            if git checkout main && git merge develop; then
                if git add .; then
                    if [ -n "$(git status --porcelain)" ]; then
                        git commit -m "chore: production deployment" || true
                    fi
                    if git push origin main; then
                        echo "   ✅ Pushed to main branch"
                        echo "   Vercel will auto-deploy to production environment"
                        VERCEL_STATUS="✅ Deployed"
                    else
                        echo "   ❌ Failed to push to main"
                        VERCEL_STATUS="❌ Failed"
                    fi
                else
                    echo "   ❌ Failed to stage files"
                    VERCEL_STATUS="❌ Failed"
                fi
            else
                echo "   ❌ Failed to checkout main or merge develop"
                VERCEL_STATUS="❌ Failed"
            fi
        else
            echo "   ⏭️  Skipping Vercel deploy"
        fi
    else
        if git add .; then
            if [ -n "$(git status --porcelain)" ]; then
                git commit -m "chore: production deployment" || true
            fi
            if git push origin main; then
                echo "   ✅ Pushed to main branch"
                echo "   Vercel will auto-deploy to production environment"
                VERCEL_STATUS="✅ Deployed"
            else
                echo "   ❌ Failed to push to main"
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
echo "✅ Production Deployment Complete!"
echo "=========================================="
echo ""
echo "📊 Summary:"
echo "   - ETL: $ETL_STATUS"
echo "   - Upload: $UPLOAD_STATUS"
echo "   - Vercel: $VERCEL_STATUS"
echo ""
echo "🔗 Check your production environment:"
echo "   - Vercel: https://benchsight.vercel.app"
echo "   - Supabase: Check your production project dashboard"
echo ""
echo "⚠️  Remember: You're now connected to PRODUCTION!"
echo "   Switch back to dev: ./scripts/switch_env.sh dev"
echo ""
