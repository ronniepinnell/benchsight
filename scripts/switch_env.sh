#!/bin/bash

# Switch between development and production environments
# Usage: ./scripts/switch_env.sh [dev|production|prod]
# Note: 'sandbox' and 'develop' are aliases for 'dev' for backward compatibility

set -euo pipefail

ENV=${1:-dev}
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Normalize aliases to standard names
if [ "$ENV" == "sandbox" ] || [ "$ENV" == "develop" ]; then
    ENV="dev"
fi
if [ "$ENV" == "prod" ]; then
    ENV="production"
fi

if [ "$ENV" == "dev" ]; then
    echo "🔄 Switching to DEVELOPMENT environment..."
    
    # Check if dev config exists (prefer config_local.dev.ini, fallback to old names)
    if [ -f "$PROJECT_ROOT/config/config_local.dev.ini" ]; then
        DEV_CONFIG="$PROJECT_ROOT/config/config_local.dev.ini"
    elif [ -f "$PROJECT_ROOT/config/config_local.develop.ini" ]; then
        DEV_CONFIG="$PROJECT_ROOT/config/config_local.develop.ini"
        echo "⚠️  Using old config name: config_local.develop.ini"
        echo "   Consider renaming to config_local.dev.ini for consistency"
    elif [ -f "$PROJECT_ROOT/config/config_local_sandbox.ini" ]; then
        DEV_CONFIG="$PROJECT_ROOT/config/config_local_sandbox.ini"
        echo "⚠️  Using old config name: config_local_sandbox.ini"
        echo "   Consider renaming to config_local.dev.ini for consistency"
    else
        echo "⚠️  Warning: Dev config not found"
        echo "   Looking for: config_local.dev.ini (preferred)"
        echo "   Or: config_local.develop.ini, config_local_sandbox.ini (legacy)"
        echo "   Create it by copying config_local.ini and updating with dev credentials"
        echo "   Or run: ./scripts/setup_environments.sh"
        read -p "   Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Switch config file
    if [ -n "${DEV_CONFIG:-}" ] && [ -f "$DEV_CONFIG" ]; then
        cp "$DEV_CONFIG" "$PROJECT_ROOT/config/config_local.ini"
        echo "✓ Updated config/config_local.ini with dev settings"
    fi
    
    # Switch dashboard env (prefer .env.local.dev, fallback to old names)
    if [ -f "$PROJECT_ROOT/ui/dashboard/.env.local.dev" ]; then
        cp "$PROJECT_ROOT/ui/dashboard/.env.local.dev" "$PROJECT_ROOT/ui/dashboard/.env.local"
        echo "✓ Updated ui/dashboard/.env.local with dev settings"
    elif [ -f "$PROJECT_ROOT/ui/dashboard/.env.local.sandbox" ]; then
        cp "$PROJECT_ROOT/ui/dashboard/.env.local.sandbox" "$PROJECT_ROOT/ui/dashboard/.env.local"
        echo "✓ Updated ui/dashboard/.env.local with dev settings"
        echo "⚠️  Using old env file name: .env.local.sandbox"
        echo "   Consider renaming to .env.local.dev for consistency"
    else
        echo "⚠️  Warning: .env.local.dev not found"
        echo "   Create it by copying .env.local and updating with dev credentials"
    fi
    
    echo ""
    echo "✅ Switched to DEVELOPMENT environment"
    echo "   Remember to restart your dev server if it's running"
    
elif [ "$ENV" == "production" ]; then
    echo "🔄 Switching to PRODUCTION environment..."
    
    # Warn user about production
    echo "⚠️  You are about to switch to PRODUCTION configuration"
    echo "   Make sure you have production credentials configured"
    read -p "   Continue? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    
    # Production uses config_local.ini directly (no switching needed)
    # Just verify it exists and warn user
    if [ ! -f "$PROJECT_ROOT/config/config_local.ini" ]; then
        echo "❌ config/config_local.ini not found"
        echo "   This should contain your production Supabase credentials"
        exit 1
    fi
    
    echo "ℹ️  Production uses config/config_local.ini directly"
    echo "   No switching needed - this is already the production config"
    
    if [ -f "$PROJECT_ROOT/ui/dashboard/.env.local.production" ]; then
        cp "$PROJECT_ROOT/ui/dashboard/.env.local.production" "$PROJECT_ROOT/ui/dashboard/.env.local"
        echo "✓ Updated ui/dashboard/.env.local with production settings"
    else
        echo "⚠️  Warning: .env.local.production not found"
        echo "   Backup your production .env.local first:"
        echo "   cp ui/dashboard/.env.local ui/dashboard/.env.local.production"
    fi
    
    echo ""
    echo "✅ Switched to PRODUCTION environment"
    echo "   ⚠️  Be careful - you're now connected to production!"
    
else
    echo "❌ Unknown environment: $ENV"
    echo ""
    echo "Usage: ./scripts/switch_env.sh [dev|production|prod]"
    echo ""
    echo "Standard names:"
    echo "  dev         # Development environment (preferred)"
    echo "  production  # Production environment"
    echo ""
    echo "Aliases (for backward compatibility):"
    echo "  sandbox     # Alias for dev"
    echo "  develop     # Alias for dev"
    echo "  prod        # Alias for production"
    echo ""
    echo "Examples:"
    echo "  ./scripts/switch_env.sh dev         # Switch to dev"
    echo "  ./scripts/switch_env.sh production  # Switch to production"
    exit 1
fi
