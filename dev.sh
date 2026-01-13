#!/bin/bash
# =============================================================================
# BenchSight - Parallel Development Script
# =============================================================================
# Run multiple development processes in parallel:
#   - Next.js Dashboard (port 3000)
#   - Python ETL (data processing)
# =============================================================================

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}BenchSight - Parallel Development${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down processes...${NC}"
    kill $(jobs -p) 2>/dev/null || true
    wait
    echo -e "${GREEN}All processes stopped.${NC}"
}

trap cleanup EXIT INT TERM

# Check if dashboard directory exists
if [ -d "ui/dashboard" ]; then
    echo -e "${GREEN}✓${NC} Starting Next.js Dashboard (port 3000)..."
    (
        cd ui/dashboard
        if [ ! -d "node_modules" ]; then
            echo -e "${YELLOW}  Installing dashboard dependencies...${NC}"
            npm install
        fi
        npm run dev
    ) &
    DASHBOARD_PID=$!
    echo -e "${GREEN}  Dashboard PID: $DASHBOARD_PID${NC}"
    echo -e "${BLUE}  → http://localhost:3000${NC}"
    echo ""
else
    echo -e "${YELLOW}⚠ Dashboard directory not found (ui/dashboard)${NC}"
    echo ""
fi

# Check if Python ETL is available
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓${NC} Python ETL available (run manually: python run_etl.py)"
    echo ""
else
    echo -e "${YELLOW}⚠ Python3 not found${NC}"
    echo ""
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Development servers running!${NC}"
echo ""
echo "Available commands:"
echo "  • Dashboard: http://localhost:3000"
echo "  • ETL: Run 'python run_etl.py' in another terminal"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all processes${NC}"
echo ""

# Wait for all background processes
wait
