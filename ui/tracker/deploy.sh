#!/bin/bash
# Deploy Tracker to Vercel

echo "🚀 Deploying BenchSight Tracker to Vercel..."
echo ""

# Check if vercel is installed
if ! command -v npx &> /dev/null; then
    echo "❌ npx not found. Please install Node.js"
    exit 1
fi

# Deploy using npx (no global install needed)
echo "📦 Using npx to deploy..."
npx vercel

echo ""
echo "✅ Deployment initiated!"
echo ""
echo "📝 Next steps:"
echo "1. If tracker uses Supabase, add environment variables:"
echo "   - NEXT_PUBLIC_SUPABASE_URL"
echo "   - NEXT_PUBLIC_SUPABASE_ANON_KEY"
echo "2. Redeploy with: npx vercel --prod"
echo ""
