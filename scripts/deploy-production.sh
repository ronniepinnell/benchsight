#!/bin/bash
# Production Deployment Script
# Helps deploy BenchSight to production

set -e

echo "🚀 BenchSight Production Deployment"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Node.js found: $(node --version)${NC}"

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ npm found: $(npm --version)${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python found: $(python3 --version)${NC}"

# Check Vercel CLI
if ! command -v vercel &> /dev/null; then
    echo -e "${YELLOW}⚠️  Vercel CLI not found. Install with: npm i -g vercel${NC}"
    echo "   You can also deploy via Vercel Dashboard"
else
    echo -e "${GREEN}✅ Vercel CLI found${NC}"
fi

# Check Railway CLI
if ! command -v railway &> /dev/null; then
    echo -e "${YELLOW}⚠️  Railway CLI not found. Install with: npm i -g @railway/cli${NC}"
    echo "   You can also deploy via Railway Dashboard"
else
    echo -e "${GREEN}✅ Railway CLI found${NC}"
fi

echo ""
echo "📦 Preparing for deployment..."
echo ""

# Setup portal files
echo "1. Setting up portal files..."
cd ui/dashboard
if [ -f "./scripts/setup-portal.sh" ]; then
    chmod +x ./scripts/setup-portal.sh
    ./scripts/setup-portal.sh
    echo -e "${GREEN}✅ Portal files ready${NC}"
else
    echo -e "${YELLOW}⚠️  Portal setup script not found${NC}"
fi

# Test dashboard build
echo ""
echo "2. Testing dashboard build..."
if npm run build > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Dashboard build successful${NC}"
else
    echo -e "${RED}❌ Dashboard build failed. Fix errors before deploying.${NC}"
    exit 1
fi

cd ../..

# Test API (optional)
echo ""
echo "3. Checking API..."
if [ -f "api/main.py" ]; then
    echo -e "${GREEN}✅ API code found${NC}"
    if [ -f "api/requirements.txt" ]; then
        echo -e "${GREEN}✅ API requirements found${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  API code not found${NC}"
fi

echo ""
echo "===================================="
echo -e "${GREEN}✅ Prerequisites check complete!${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. Deploy Dashboard to Vercel:"
echo "   cd ui/dashboard"
echo "   vercel --prod"
echo "   (Or use Vercel Dashboard)"
echo ""
echo "2. Deploy API to Railway:"
echo "   cd api"
echo "   railway login"
echo "   railway init"
echo "   railway up"
echo "   (Or use Railway Dashboard)"
echo ""
echo "3. Configure environment variables:"
echo "   - See docs/PRODUCTION_SETUP.md for details"
echo ""
echo "4. Set up Supabase Auth:"
echo "   - See docs/AUTHENTICATION_SETUP.md"
echo ""
echo "📚 Full guide: docs/PRODUCTION_SETUP.md"
echo "📋 Checklist: PRODUCTION_CHECKLIST.md"
echo ""
