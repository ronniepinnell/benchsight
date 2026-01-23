#!/bin/bash
# =============================================================================
# BenchSight Unified CLI
# =============================================================================
# Unified command interface for all BenchSight operations
# Usage: ./benchsight.sh [command] [subcommand] [options]
# =============================================================================

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Helper functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# ETL Commands
cmd_etl_run() {
    print_header "Running ETL Pipeline"
    
    if [ "$#" -gt 0 ] && [ "$1" == "--games" ]; then
        shift
        GAMES="$*"
        print_info "Running ETL for games: $GAMES"
        python run_etl.py --games $GAMES
    elif [ "$#" -gt 0 ] && [ "$1" == "--wipe" ]; then
        print_warning "Wiping output directory and running full ETL"
        python run_etl.py --wipe
    else
        print_info "Running full ETL pipeline"
        python run_etl.py
    fi
    
    print_success "ETL complete"
}

cmd_etl_validate() {
    print_header "Validating ETL Output"

    if [ "$#" -gt 0 ]; then
        case "$1" in
            --manifest|--comprehensive)
                print_info "Running comprehensive table verification"
                python validate.py --manifest
                ;;
            --full)
                print_info "Running full validation suite"
                python validate.py --full
                ;;
            --quick)
                print_info "Running quick validation"
                python validate.py --quick
                ;;
            --goals)
                print_info "Validating goal counts"
                python validate.py --goals
                ;;
            *)
                python validate.py "$@"
                ;;
        esac
    else
        python validate.py
    fi

    print_success "Validation complete"
}

cmd_etl_verify() {
    print_header "Running Comprehensive Table Verification"
    python -m src.validation.table_verifier
}

cmd_etl_status() {
    print_header "ETL Status"
    python run_etl.py --status
}

cmd_etl_wipe() {
    print_warning "This will delete all output files and rebuild"
    read -p "Continue? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python run_etl.py --wipe
        print_success "ETL wiped and rebuilt"
    else
        print_info "Cancelled"
    fi
}

cmd_etl_test() {
    print_header "Running ETL Tests"

    if [ "$#" -gt 0 ] && [ "$1" == "--fresh" ]; then
        shift
        print_info "Running ETL with --wipe first, then tests"
        pytest --run-etl tests/ "$@"
    else
        print_info "Running tests with existing output"
        print_info "Use --fresh to wipe and rebuild ETL first"
        pytest tests/ "$@"
    fi
}

# Dashboard Commands
cmd_dashboard_dev() {
    print_header "Starting Dashboard Dev Server"
    
    if [ ! -d "ui/dashboard" ]; then
        print_error "Dashboard directory not found"
        exit 1
    fi
    
    cd ui/dashboard
    
    if [ ! -d "node_modules" ]; then
        print_info "Installing dependencies..."
        npm install
    fi
    
    print_success "Starting dev server on http://localhost:3000"
    npm run dev
}

cmd_dashboard_build() {
    print_header "Building Dashboard for Production"
    
    if [ ! -d "ui/dashboard" ]; then
        print_error "Dashboard directory not found"
        exit 1
    fi
    
    cd ui/dashboard
    
    if [ ! -d "node_modules" ]; then
        print_info "Installing dependencies..."
        npm install
    fi
    
    npm run build
    print_success "Build complete"
}

cmd_dashboard_deploy() {
    print_header "Deploying Dashboard"
    print_info "Deploying to Vercel..."
    
    if [ ! -d "ui/dashboard" ]; then
        print_error "Dashboard directory not found"
        exit 1
    fi
    
    cd ui/dashboard
    
    if command -v vercel &> /dev/null; then
        vercel --prod
        print_success "Deployment complete"
    else
        print_error "Vercel CLI not found. Install with: npm i -g vercel"
        exit 1
    fi
}

# API Commands
cmd_api_dev() {
    print_header "Starting API Dev Server"
    
    if [ ! -d "api" ]; then
        print_error "API directory not found"
        exit 1
    fi
    
    cd api
    
    if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
        print_warning "Virtual environment not found. Creating..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    else
        if [ -d "venv" ]; then
            source venv/bin/activate
        else
            source .venv/bin/activate
        fi
    fi
    
    print_success "Starting API server on http://localhost:8000"
    print_info "API docs available at http://localhost:8000/docs"
    uvicorn main:app --reload
}

cmd_api_test() {
    print_header "Running API Tests"
    
    if [ ! -d "api" ]; then
        print_error "API directory not found"
        exit 1
    fi
    
    cd api
    
    if [ -d "venv" ]; then
        source venv/bin/activate
    elif [ -d ".venv" ]; then
        source .venv/bin/activate
    fi
    
    if [ -d "tests" ]; then
        pytest tests/
        print_success "Tests complete"
    else
        print_warning "No tests directory found"
    fi
}

cmd_api_deploy() {
    print_header "Deploying API"
    print_info "Deploying to Railway/Render..."
    
    if [ ! -d "api" ]; then
        print_error "API directory not found"
        exit 1
    fi
    
    print_warning "API deployment should be configured via Railway/Render dashboard"
    print_info "See api/DEPLOYMENT.md for deployment instructions"
}

# Database Commands
cmd_db_upload() {
    print_header "Uploading Tables to Supabase"
    
    if [ "$#" -gt 0 ] && [ "$1" == "--tables" ]; then
        shift
        TABLES="$*"
        print_info "Uploading tables: $TABLES"
        python upload.py --tables $TABLES
    elif [ "$#" -gt 0 ] && [ "$1" == "--pattern" ]; then
        shift
        PATTERN="$1"
        print_info "Uploading tables matching pattern: $PATTERN"
        python upload.py --pattern "$PATTERN"
    else
        print_info "Uploading all tables"
        python upload.py
    fi
    
    print_success "Upload complete"
}

cmd_db_schema() {
    print_header "Generating Supabase Schema"
    python upload.py --schema
    print_success "Schema generated"
    print_info "Run the generated SQL in Supabase SQL Editor"
}

cmd_db_reset() {
    print_warning "This will reset the Supabase database"
    print_warning "Make sure you have a backup!"
    read -p "Continue? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Resetting Supabase database..."
        if [ -f "sql/reset_supabase.sql" ]; then
            print_info "Run sql/reset_supabase.sql in Supabase SQL Editor"
        else
            print_error "sql/reset_supabase.sql not found"
        fi
    else
        print_info "Cancelled"
    fi
}

# Environment Commands
cmd_env_switch() {
    if [ "$#" -eq 0 ]; then
        print_error "Please specify environment: dev or production"
        exit 1
    fi
    
    ENV="$1"
    print_header "Switching to $ENV environment"
    
    if [ -f "scripts/switch_env.sh" ]; then
        ./scripts/switch_env.sh "$ENV"
        print_success "Switched to $ENV environment"
    else
        print_error "scripts/switch_env.sh not found"
        exit 1
    fi
}

cmd_env_status() {
    print_header "Environment Status"

    # Show BENCHSIGHT_ENV setting
    if [ -n "${BENCHSIGHT_ENV:-}" ]; then
        if [ "$BENCHSIGHT_ENV" = "dev" ] || [ "$BENCHSIGHT_ENV" = "development" ]; then
            print_success "BENCHSIGHT_ENV: $BENCHSIGHT_ENV (Development)"
            if [ -f "config/config.dev.ini" ]; then
                print_info "Using: config/config.dev.ini"
            else
                print_warning "config/config.dev.ini not found!"
            fi
        elif [ "$BENCHSIGHT_ENV" = "prod" ] || [ "$BENCHSIGHT_ENV" = "production" ]; then
            print_warning "BENCHSIGHT_ENV: $BENCHSIGHT_ENV (Production)"
            if [ -f "config/config.prod.ini" ]; then
                print_info "Using: config/config.prod.ini"
            else
                print_warning "config/config.prod.ini not found!"
            fi
        else
            print_info "BENCHSIGHT_ENV: $BENCHSIGHT_ENV (Unknown)"
        fi
    else
        print_info "BENCHSIGHT_ENV: (not set - using legacy config_local.ini)"
        if [ -f "config/config_local.ini" ]; then
            # Check which Supabase URL is in the config
            if grep -q "amuisqvhhiigxetsfame" config/config_local.ini 2>/dev/null; then
                print_success "config_local.ini points to: Development"
            elif grep -q "uuaowslhpgyiudmbvqze" config/config_local.ini 2>/dev/null; then
                print_warning "config_local.ini points to: Production"
            else
                print_info "config_local.ini: Unknown target"
            fi
        else
            print_warning "config/config_local.ini not found"
        fi
    fi

    echo ""
    print_info "Dashboard environment (Next.js auto-selects):"
    if [ -f "ui/dashboard/.env.development" ]; then
        print_success "  .env.development exists (used by npm run dev)"
    fi
    if [ -f "ui/dashboard/.env.production" ]; then
        print_info "  .env.production exists (used by builds)"
    fi
    if [ -f "ui/dashboard/.env.local" ]; then
        print_info "  .env.local exists (overrides above)"
    fi

    echo ""
    print_info "To switch environments:"
    print_info "  export BENCHSIGHT_ENV=dev   # Use dev Supabase"
    print_info "  export BENCHSIGHT_ENV=prod  # Use prod Supabase"
}

# Workflow Commands
cmd_commit() {
    print_header "Smart Commit"
    
    if [ -f "scripts/workflows/commit.sh" ]; then
        ./scripts/workflows/commit.sh "$@"
    else
        print_warning "Commit workflow script not found, using standard git commit"
        git add .
        read -p "Commit message: " MESSAGE
        git commit -m "$MESSAGE"
    fi
}

cmd_review_pr() {
    print_header "Review PR"
    
    CURRENT_BRANCH=$(git branch --show-current)
    if [ "$CURRENT_BRANCH" == "main" ] || [ "$CURRENT_BRANCH" == "develop" ]; then
        print_error "Cannot create PR from $CURRENT_BRANCH branch"
        exit 1
    fi
    
    print_info "Current branch: $CURRENT_BRANCH"
    print_info "Opening PR creation page..."
    
    if command -v gh &> /dev/null; then
        gh pr create --web
    else
        REMOTE=$(git remote get-url origin)
        if [[ $REMOTE == *"github.com"* ]]; then
            REPO=$(echo $REMOTE | sed 's/.*github.com[:/]\(.*\)\.git/\1/')
            print_info "Create PR at: https://github.com/$REPO/compare/$CURRENT_BRANCH"
            if command -v open &> /dev/null; then
                open "https://github.com/$REPO/compare/$CURRENT_BRANCH"
            elif command -v xdg-open &> /dev/null; then
                xdg-open "https://github.com/$REPO/compare/$CURRENT_BRANCH"
            fi
        else
            print_info "Push your branch and create PR manually"
        fi
    fi
}

cmd_generate_tests() {
    print_header "Generate Test Templates"
    
    if [ -f "scripts/workflows/test-generation.sh" ]; then
        ./scripts/workflows/test-generation.sh "$@"
    else
        print_warning "Test generation script not found"
        print_info "Create test file manually in tests/ directory"
    fi
}

cmd_refactor() {
    print_header "Refactoring Helper"
    
    if [ "$#" -eq 0 ]; then
        print_info "Refactoring helpers available:"
        echo "  - Check for .iterrows() usage"
        echo "  - Find duplicated code"
        echo "  - Check function length"
        echo ""
        print_info "Usage: ./benchsight.sh refactor [check|help]"
    else
        case "$1" in
            check)
                print_info "Checking for refactoring opportunities..."
                if grep -r "\.iterrows()" src/ --include="*.py" 2>/dev/null; then
                    print_warning "Found .iterrows() usage - consider vectorized operations"
                else
                    print_success "No .iterrows() usage found"
                fi
                ;;
            help)
                print_info "Refactoring helpers:"
                echo "  check - Check for common refactoring opportunities"
                ;;
            *)
                print_error "Unknown refactor command: $1"
                ;;
        esac
    fi
}

cmd_fix_types() {
    print_header "TypeScript Type Fixes"
    
    if [ ! -d "ui/dashboard" ]; then
        print_error "Dashboard directory not found"
        exit 1
    fi
    
    cd ui/dashboard
    
    if [ ! -d "node_modules" ]; then
        print_info "Installing dependencies..."
        npm install
    fi
    
    print_info "Running TypeScript type check..."
    npm run type-check || print_warning "Type check found issues - review output above"
}

# PRD Commands
cmd_prd_create() {
    print_header "Create PRD"
    
    if [ "$#" -eq 0 ]; then
        print_error "PRD name required"
        print_info "Usage: ./benchsight.sh prd create [feature|refactor|bug] <name>"
        exit 1
    fi
    
    TYPE="$1"
    shift
    
    if [ "$#" -eq 0 ]; then
        print_error "PRD name required"
        exit 1
    fi
    
    NAME="$1"
    
    case "$TYPE" in
        feature)
            DIR="docs/prds/features"
            ;;
        refactor)
            DIR="docs/prds/refactors"
            ;;
        bug)
            DIR="docs/prds/bugs"
            DATE=$(date +%Y-%m-%d)
            NAME="${DATE}-${NAME}"
            ;;
        *)
            print_error "Invalid PRD type: $TYPE (use: feature, refactor, bug)"
            exit 1
            ;;
    esac
    
    mkdir -p "$DIR"
    PRD_FILE="$DIR/$NAME.md"
    
    if [ -f "$PRD_FILE" ]; then
        print_warning "PRD already exists: $PRD_FILE"
        read -p "Overwrite? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Cancelled"
            exit 0
        fi
    fi
    
    if [ -f "docs/prds/template.md" ]; then
        cp docs/prds/template.md "$PRD_FILE"
        print_success "Created PRD: $PRD_FILE"
        print_info "Edit the PRD and fill in the details"
        
        if command -v code &> /dev/null; then
            code "$PRD_FILE"
        elif command -v vim &> /dev/null; then
            vim "$PRD_FILE"
        fi
    else
        print_error "PRD template not found: docs/prds/template.md"
        exit 1
    fi
}

cmd_prd_list() {
    print_header "PRD List"
    
    echo ""
    echo "Features:"
    if [ -d "docs/prds/features" ]; then
        ls -1 docs/prds/features/*.md 2>/dev/null | sed 's|docs/prds/features/||' | sed 's|\.md||' || echo "  (none)"
    else
        echo "  (none)"
    fi
    
    echo ""
    echo "Refactors:"
    if [ -d "docs/prds/refactors" ]; then
        ls -1 docs/prds/refactors/*.md 2>/dev/null | sed 's|docs/prds/refactors/||' | sed 's|\.md||' || echo "  (none)"
    else
        echo "  (none)"
    fi
    
    echo ""
    echo "Bugs:"
    if [ -d "docs/prds/bugs" ]; then
        ls -1 docs/prds/bugs/*.md 2>/dev/null | sed 's|docs/prds/bugs/||' | sed 's|\.md||' || echo "  (none)"
    else
        echo "  (none)"
    fi
}

# Documentation Commands
cmd_docs_sync() {
    print_header "Sync Documentation"
    
    print_info "Checking documentation consistency..."
    
    if [ -f "scripts/docs-check.sh" ]; then
        ./scripts/docs-check.sh
    else
        print_warning "Documentation check script not found"
        print_info "See docs/DOCUMENTATION_MAINTENANCE.md for guidelines"
    fi
}

cmd_docs_check() {
    print_header "Check Documentation"
    
    if [ -f "scripts/docs-check.sh" ]; then
        ./scripts/docs-check.sh "$@"
    else
        print_warning "Documentation check script not found"
        print_info "Manual checks:"
        echo "  - Check for broken links"
        echo "  - Verify cross-references"
        echo "  - Check for outdated docs"
    fi
}

# Debug Commands (Local PostgreSQL)
cmd_debug_start() {
    print_header "Starting Debug PostgreSQL"

    if ! command -v docker &> /dev/null; then
        print_error "Docker not found. Install Docker Desktop first."
        exit 1
    fi

    if [ ! -f "docker/docker-compose.yml" ]; then
        print_error "docker/docker-compose.yml not found"
        exit 1
    fi

    docker-compose -f docker/docker-compose.yml up -d

    # Wait for PostgreSQL to be ready
    print_info "Waiting for PostgreSQL to start..."
    sleep 3

    if docker exec benchsight-pg pg_isready -U benchsight -d benchsight &> /dev/null; then
        print_success "PostgreSQL started on localhost:5432"
        print_info "Schemas: raw, stage, intermediate, datamart"
    else
        print_warning "PostgreSQL may still be starting. Try: ./benchsight.sh debug status"
    fi
}

cmd_debug_stop() {
    print_header "Stopping Debug PostgreSQL"

    if [ ! -f "docker/docker-compose.yml" ]; then
        print_error "docker/docker-compose.yml not found"
        exit 1
    fi

    docker-compose -f docker/docker-compose.yml stop
    print_success "PostgreSQL stopped (data preserved)"
}

cmd_debug_reset() {
    print_warning "This will DELETE ALL data in the debug database"
    read -p "Continue? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Resetting debug database..."
        docker-compose -f docker/docker-compose.yml down -v
        docker-compose -f docker/docker-compose.yml up -d
        sleep 3
        print_success "Database reset complete"
    else
        print_info "Cancelled"
    fi
}

cmd_debug_status() {
    print_header "Debug PostgreSQL Status"

    if docker ps | grep -q benchsight-pg; then
        print_success "Container: Running"

        if docker exec benchsight-pg pg_isready -U benchsight -d benchsight &> /dev/null; then
            print_success "Database: Ready"

            # Show schema summary
            echo ""
            print_info "Schema Summary:"
            docker exec benchsight-pg psql -U benchsight -d benchsight -c "SELECT * FROM schema_summary();" 2>/dev/null || print_warning "Helper functions not loaded"
        else
            print_warning "Database: Not ready"
        fi
    else
        print_warning "Container: Not running"
        print_info "Start with: ./benchsight.sh debug start"
    fi
}

cmd_debug_shell() {
    print_header "Opening PostgreSQL Shell"

    if ! docker ps | grep -q benchsight-pg; then
        print_error "Debug PostgreSQL is not running"
        print_info "Start with: ./benchsight.sh debug start"
        exit 1
    fi

    docker exec -it benchsight-pg psql -U benchsight -d benchsight
}

cmd_debug_tables() {
    SCHEMA="${1:-datamart}"
    print_header "Tables in $SCHEMA Schema"

    if ! docker ps | grep -q benchsight-pg; then
        print_error "Debug PostgreSQL is not running"
        exit 1
    fi

    docker exec benchsight-pg psql -U benchsight -d benchsight -c "\dt $SCHEMA.*"
}

cmd_debug_counts() {
    print_header "Table Row Counts"

    if ! docker ps | grep -q benchsight-pg; then
        print_error "Debug PostgreSQL is not running"
        exit 1
    fi

    echo ""
    print_info "Raw Schema:"
    docker exec benchsight-pg psql -U benchsight -d benchsight -c "SELECT * FROM get_table_counts('raw');" 2>/dev/null || echo "  (no tables)"

    echo ""
    print_info "Stage Schema:"
    docker exec benchsight-pg psql -U benchsight -d benchsight -c "SELECT * FROM get_table_counts('stage');" 2>/dev/null || echo "  (no tables)"

    echo ""
    print_info "Intermediate Schema:"
    docker exec benchsight-pg psql -U benchsight -d benchsight -c "SELECT * FROM get_table_counts('intermediate');" 2>/dev/null || echo "  (no tables)"

    echo ""
    print_info "Datamart Schema:"
    docker exec benchsight-pg psql -U benchsight -d benchsight -c "SELECT * FROM get_table_counts('datamart');" 2>/dev/null || echo "  (no tables)"
}

cmd_debug_query() {
    if [ "$#" -eq 0 ]; then
        print_error "SQL query required"
        print_info "Usage: ./benchsight.sh debug query \"SELECT * FROM datamart.dim_player LIMIT 5\""
        exit 1
    fi

    QUERY="$1"

    if ! docker ps | grep -q benchsight-pg; then
        print_error "Debug PostgreSQL is not running"
        exit 1
    fi

    docker exec benchsight-pg psql -U benchsight -d benchsight -c "$QUERY"
}

cmd_debug_run() {
    print_header "Running ETL in Debug Mode"

    if ! docker ps | grep -q benchsight-pg; then
        print_error "Debug PostgreSQL is not running"
        print_info "Start with: ./benchsight.sh debug start"
        exit 1
    fi

    # Pass all arguments to run_etl.py with --debug flag
    python run_etl.py --debug "$@"
}

cmd_debug_compare() {
    print_header "Comparing Local vs Supabase"

    if ! docker ps | grep -q benchsight-pg; then
        print_error "Debug PostgreSQL is not running"
        exit 1
    fi

    print_warning "Comparison feature requires issues #18-#21 to be implemented"
    print_info "See: gh issue view 21"
}

cmd_debug_help() {
    cat << EOF
${BLUE}Debug PostgreSQL Commands${NC}

${GREEN}Database Management:${NC}
  debug start          Start local PostgreSQL container
  debug stop           Stop container (preserves data)
  debug reset          Reset database (deletes all data)
  debug status         Show container and database status

${GREEN}Inspection:${NC}
  debug shell          Open psql shell
  debug tables [schema] List tables (default: datamart)
  debug counts         Show row counts per schema
  debug query "SQL"    Run ad-hoc SQL query

${GREEN}ETL Execution:${NC}
  debug run            Run ETL in debug mode
  debug run --to-phase 4B   Run up to specific phase
  debug run --step     Step through phases interactively

${GREEN}Comparison:${NC}
  debug compare        Compare local vs Supabase (not yet implemented)

${GREEN}Examples:${NC}
  ./benchsight.sh debug start
  ./benchsight.sh debug shell
  ./benchsight.sh debug query "SELECT COUNT(*) FROM datamart.fact_events"
  ./benchsight.sh debug tables raw
  ./benchsight.sh debug run --to-phase 4B

EOF
}

# Project Commands
cmd_status() {
    print_header "Project Status"
    
    echo ""
    echo "Component Status:"
    echo ""
    
    # ETL Status
    if [ -f "run_etl.py" ]; then
        print_success "ETL Pipeline: Available"
    else
        print_error "ETL Pipeline: Not found"
    fi
    
    # Dashboard Status
    if [ -d "ui/dashboard" ]; then
        print_success "Dashboard: Available"
        if [ -d "ui/dashboard/node_modules" ]; then
            print_info "  Dependencies: Installed"
        else
            print_warning "  Dependencies: Not installed"
        fi
    else
        print_error "Dashboard: Not found"
    fi
    
    # API Status
    if [ -d "api" ]; then
        print_success "API: Available"
    else
        print_error "API: Not found"
    fi
    
    # Tracker Status
    if [ -d "ui/tracker" ]; then
        print_success "Tracker: Available"
    else
        print_warning "Tracker: Not found"
    fi
    
    # Portal Status
    if [ -d "ui/portal" ]; then
        print_success "Portal: Available"
    else
        print_warning "Portal: Not found"
    fi
    
    echo ""
    print_info "See docs/PROJECT_STATUS.md for detailed status"
}

cmd_docs() {
    print_header "Opening Documentation"
    
    if [ -f "docs/MASTER_INDEX.md" ]; then
        print_info "Master Index: docs/MASTER_INDEX.md"
        if command -v open &> /dev/null; then
            open docs/MASTER_INDEX.md
        elif command -v xdg-open &> /dev/null; then
            xdg-open docs/MASTER_INDEX.md
        else
            print_info "Open docs/MASTER_INDEX.md in your editor"
        fi
    else
        print_error "Documentation not found"
    fi
}

cmd_help() {
    cat << EOF
${BLUE}BenchSight Unified CLI${NC}

${GREEN}Usage:${NC}
  ./benchsight.sh [command] [subcommand] [options]

${GREEN}ETL Commands:${NC}
  etl run [--games GAME_ID ...]    Run ETL pipeline
  etl run --wipe                   Wipe and rebuild
  etl validate                     Validate ETL output (legacy)
  etl validate --manifest          Comprehensive table verification
  etl validate --full              All validation checks
  etl verify                       Comprehensive table verification
  etl test                         Run ETL tests (uses existing output)
  etl test --fresh                 Wipe + run ETL, then tests
  etl status                       Check ETL status
  etl wipe                         Wipe output directory

${GREEN}Dashboard Commands:${NC}
  dashboard dev                    Start dev server
  dashboard build                  Build for production
  dashboard deploy                 Deploy to Vercel

${GREEN}API Commands:${NC}
  api dev                          Start dev server
  api test                         Run tests
  api deploy                       Deploy (see docs)

${GREEN}Database Commands:${NC}
  db upload [--tables TABLE ...]  Upload tables to Supabase
  db upload --pattern PATTERN      Upload matching tables
  db schema                        Generate Supabase schema
  db reset                         Reset database (careful!)

${GREEN}Environment Commands:${NC}
  env switch dev                   Switch to dev environment
  env switch production            Switch to production
  env status                       Show current environment

${GREEN}Workflow Commands:${NC}
  commit                           Smart commit with checklist
  review-pr                        Open PR for review
  generate-tests [FILE]           Generate test templates
  refactor [check]                 Refactoring helpers
  fix-types                        Fix TypeScript types

${GREEN}PRD Commands:${NC}
  prd create [type] <name>         Create new PRD (feature/refactor/bug)
  prd list                         List all PRDs

${GREEN}Documentation Commands:${NC}
  docs sync                        Sync documentation
  docs check                       Check doc consistency

${GREEN}Project Commands:${NC}
  status                           Show project status
  docs                             Open documentation
  help                             Show this help

${GREEN}Examples:${NC}
  ./benchsight.sh etl run
  ./benchsight.sh etl run --games 18969 18977
  ./benchsight.sh dashboard dev
  ./benchsight.sh db upload
  ./benchsight.sh env switch dev
  ./benchsight.sh commit
  ./benchsight.sh prd create feature portal-api
  ./benchsight.sh review-pr

${GREEN}Documentation:${NC}
  See docs/COMMANDS.md for complete command reference
  See docs/MASTER_INDEX.md for all documentation

EOF
}

# Main command router
main() {
    if [ "$#" -eq 0 ]; then
        cmd_help
        exit 0
    fi
    
    COMMAND="$1"
    shift
    
    case "$COMMAND" in
        etl)
            if [ "$#" -eq 0 ]; then
                print_error "ETL subcommand required"
                cmd_help
                exit 1
            fi
            SUBCOMMAND="$1"
            shift
            case "$SUBCOMMAND" in
                run) cmd_etl_run "$@" ;;
                validate) cmd_etl_validate "$@" ;;
                verify) cmd_etl_verify "$@" ;;
                test) cmd_etl_test "$@" ;;
                status) cmd_etl_status "$@" ;;
                wipe) cmd_etl_wipe "$@" ;;
                *) print_error "Unknown ETL subcommand: $SUBCOMMAND"; cmd_help; exit 1 ;;
            esac
            ;;
        dashboard)
            if [ "$#" -eq 0 ]; then
                print_error "Dashboard subcommand required"
                cmd_help
                exit 1
            fi
            SUBCOMMAND="$1"
            shift
            case "$SUBCOMMAND" in
                dev) cmd_dashboard_dev "$@" ;;
                build) cmd_dashboard_build "$@" ;;
                deploy) cmd_dashboard_deploy "$@" ;;
                *) print_error "Unknown dashboard subcommand: $SUBCOMMAND"; cmd_help; exit 1 ;;
            esac
            ;;
        api)
            if [ "$#" -eq 0 ]; then
                print_error "API subcommand required"
                cmd_help
                exit 1
            fi
            SUBCOMMAND="$1"
            shift
            case "$SUBCOMMAND" in
                dev) cmd_api_dev "$@" ;;
                test) cmd_api_test "$@" ;;
                deploy) cmd_api_deploy "$@" ;;
                *) print_error "Unknown API subcommand: $SUBCOMMAND"; cmd_help; exit 1 ;;
            esac
            ;;
        db)
            if [ "$#" -eq 0 ]; then
                print_error "Database subcommand required"
                cmd_help
                exit 1
            fi
            SUBCOMMAND="$1"
            shift
            case "$SUBCOMMAND" in
                upload) cmd_db_upload "$@" ;;
                schema) cmd_db_schema "$@" ;;
                reset) cmd_db_reset "$@" ;;
                *) print_error "Unknown database subcommand: $SUBCOMMAND"; cmd_help; exit 1 ;;
            esac
            ;;
        env)
            if [ "$#" -eq 0 ]; then
                print_error "Environment subcommand required"
                cmd_help
                exit 1
            fi
            SUBCOMMAND="$1"
            shift
            case "$SUBCOMMAND" in
                switch) cmd_env_switch "$@" ;;
                status) cmd_env_status "$@" ;;
                *) print_error "Unknown environment subcommand: $SUBCOMMAND"; cmd_help; exit 1 ;;
            esac
            ;;
        commit)
            cmd_commit "$@"
            ;;
        review-pr)
            cmd_review_pr "$@"
            ;;
        generate-tests)
            cmd_generate_tests "$@"
            ;;
        refactor)
            cmd_refactor "$@"
            ;;
        fix-types)
            cmd_fix_types "$@"
            ;;
        prd)
            if [ "$#" -eq 0 ]; then
                print_error "PRD subcommand required"
                cmd_help
                exit 1
            fi
            SUBCOMMAND="$1"
            shift
            case "$SUBCOMMAND" in
                create) cmd_prd_create "$@" ;;
                list) cmd_prd_list "$@" ;;
                *) print_error "Unknown PRD subcommand: $SUBCOMMAND"; cmd_help; exit 1 ;;
            esac
            ;;
        status)
            cmd_status "$@"
            ;;
        debug)
            if [ "$#" -eq 0 ]; then
                cmd_debug_help
                exit 0
            fi
            SUBCOMMAND="$1"
            shift
            case "$SUBCOMMAND" in
                start) cmd_debug_start "$@" ;;
                stop) cmd_debug_stop "$@" ;;
                reset) cmd_debug_reset "$@" ;;
                status) cmd_debug_status "$@" ;;
                shell) cmd_debug_shell "$@" ;;
                tables) cmd_debug_tables "$@" ;;
                counts) cmd_debug_counts "$@" ;;
                query) cmd_debug_query "$@" ;;
                run) cmd_debug_run "$@" ;;
                compare) cmd_debug_compare "$@" ;;
                help|--help|-h) cmd_debug_help ;;
                *) print_error "Unknown debug subcommand: $SUBCOMMAND"; cmd_debug_help; exit 1 ;;
            esac
            ;;
        docs)
            if [ "$#" -gt 0 ]; then
                SUBCOMMAND="$1"
                shift
                case "$SUBCOMMAND" in
                    sync) cmd_docs_sync "$@" ;;
                    check) cmd_docs_check "$@" ;;
                    *) cmd_docs "$@" ;;
                esac
            else
                cmd_docs "$@"
            fi
            ;;
        help|--help|-h)
            cmd_help
            ;;
        *)
            print_error "Unknown command: $COMMAND"
            echo ""
            cmd_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
