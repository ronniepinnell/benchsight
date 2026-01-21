#!/bin/bash
# Setup Supabase Development Environment
# This script helps set up Supabase for local development

set -e

echo "=========================================="
echo "BenchSight Supabase Dev Environment Setup"
echo "=========================================="
echo ""

# Check if Supabase CLI is installed
if ! command -v supabase &> /dev/null; then
    echo "❌ Supabase CLI not found"
    echo "Installing Supabase CLI..."
    npm install -g supabase
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running"
    echo "Please start Docker and try again"
    exit 1
fi

# Initialize Supabase if not already initialized
if [ ! -d "supabase" ]; then
    echo "Initializing Supabase..."
    supabase init
fi

# Start Supabase
echo "Starting Supabase..."
supabase start

echo ""
echo "✅ Supabase started successfully!"
echo ""
echo "Access Supabase Studio at: http://localhost:54323"
echo ""
echo "Credentials:"
supabase status
echo ""
echo "Update config/config_local.ini with the credentials above"
