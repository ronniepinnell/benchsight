#!/bin/bash
# Setup Vercel Development Environment
# This script helps set up Vercel for dashboard development

set -e

echo "=========================================="
echo "BenchSight Vercel Dev Environment Setup"
echo "=========================================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found"
    echo "Please install Node.js 18+ and try again"
    exit 1
fi

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "Installing Vercel CLI..."
    npm install -g vercel
fi

# Navigate to dashboard directory
cd ui/dashboard

# Install dependencies
echo "Installing dependencies..."
npm install

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "Creating .env.local from example..."
    if [ -f ".env.local.example" ]; then
        cp .env.local.example .env.local
        echo "⚠️  Please update .env.local with your Supabase credentials"
    else
        echo "Creating .env.local..."
        cat > .env.local << EOF
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
        echo "⚠️  Please update .env.local with your Supabase credentials"
    fi
fi

# Link to Vercel project (if not already linked)
if [ ! -d ".vercel" ]; then
    echo "Linking to Vercel project..."
    vercel link
fi

echo ""
echo "✅ Vercel setup complete!"
echo ""
echo "To start development server:"
echo "  cd ui/dashboard"
echo "  npm run dev"
echo ""
echo "Or use Vercel dev:"
echo "  cd ui/dashboard"
echo "  vercel dev"
