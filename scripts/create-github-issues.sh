#!/bin/bash
# BenchSight GitHub Issues Creator
# Creates all Phase 2 issues and labels from the backlog
#
# Prerequisites:
#   1. Install GitHub CLI: brew install gh
#   2. Authenticate: gh auth login
#
# Usage: ./scripts/create-github-issues.sh [--labels-only] [--phase2] [--all]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Check gh is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) is not installed${NC}"
    echo "Install with: brew install gh"
    exit 1
fi

# Check gh is authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI is not authenticated${NC}"
    echo "Run: gh auth login"
    exit 1
fi

echo -e "${BLUE}========================================"
echo "  BenchSight GitHub Issues Creator"
echo "========================================${NC}"
echo ""

# Parse arguments
CREATE_LABELS=false
CREATE_PHASE2=false
CREATE_ALL=false

for arg in "$@"; do
    case $arg in
        --labels-only) CREATE_LABELS=true ;;
        --phase2) CREATE_PHASE2=true ;;
        --all) CREATE_ALL=true ;;
        --help|-h)
            echo "Usage: ./scripts/create-github-issues.sh [options]"
            echo ""
            echo "Options:"
            echo "  --labels-only  Create only labels"
            echo "  --phase2       Create Phase 2 issues (ETL Optimization)"
            echo "  --all          Create all issues (all phases)"
            echo "  --help         Show this help"
            exit 0
            ;;
    esac
done

# Default to phase2 if no args
if [ "$CREATE_LABELS" = false ] && [ "$CREATE_PHASE2" = false ] && [ "$CREATE_ALL" = false ]; then
    CREATE_LABELS=true
    CREATE_PHASE2=true
fi

# Function to create label if it doesn't exist
create_label() {
    local name=$1
    local color=$2
    local description=$3

    if gh label list | grep -q "^$name"; then
        echo "  Label '$name' already exists"
    else
        gh label create "$name" --color "$color" --description "$description" 2>/dev/null || true
        echo -e "  ${GREEN}Created label: $name${NC}"
    fi
}

# Create labels
if [ "$CREATE_LABELS" = true ]; then
    echo -e "${BLUE}Creating labels...${NC}"

    # Type labels (blue shades)
    create_label "type:feature" "0052CC" "New functionality"
    create_label "type:enhancement" "1D76DB" "Improvement to existing feature"
    create_label "type:fix" "D73A4A" "Bug fix"
    create_label "type:refactor" "5319E7" "Code restructuring"
    create_label "type:docs" "0075CA" "Documentation only"
    create_label "type:test" "FBCA04" "Testing infrastructure"
    create_label "type:chore" "CCCCCC" "Maintenance tasks"
    create_label "type:design" "7057FF" "Architecture/design"
    create_label "type:research" "D4C5F9" "Investigation/spike"
    create_label "type:perf" "F9D0C4" "Performance optimization"

    # Area labels (green shades)
    create_label "area:etl" "0E8A16" "ETL pipeline"
    create_label "area:dashboard" "1D7648" "Next.js dashboard"
    create_label "area:tracker" "2E8B57" "Game tracker"
    create_label "area:portal" "3CB371" "Admin portal"
    create_label "area:api" "228B22" "FastAPI backend"
    create_label "area:data" "006400" "Database schema"
    create_label "area:infra" "556B2F" "Infrastructure"
    create_label "area:docs" "90EE90" "Documentation"
    create_label "area:commercial" "32CD32" "Business/monetization"
    create_label "area:workflow" "98FB98" "Development workflow"
    create_label "area:analytics" "00FA9A" "Advanced analytics/ML"

    # Priority labels (red/orange/yellow)
    create_label "priority:p0" "B60205" "Critical/blocking"
    create_label "priority:p1" "D93F0B" "High priority"
    create_label "priority:p2" "FBCA04" "Medium priority"
    create_label "priority:p3" "FEF2C0" "Low priority"

    # Phase labels (purple shades)
    create_label "phase:1" "E8D5E8" "Foundation & Documentation"
    create_label "phase:2" "D4A5D4" "ETL Optimization"
    create_label "phase:3" "C080C0" "Dashboard Enhancement"
    create_label "phase:4" "AC5CAC" "Portal Development"
    create_label "phase:5" "983898" "Tracker Conversion"
    create_label "phase:6" "841484" "ML/CV Integration"
    create_label "phase:7" "700070" "Multi-Tenancy"
    create_label "phase:8" "5C005C" "Commercial Launch"

    echo ""
fi

# Function to create issue
create_issue() {
    local title=$1
    local labels=$2
    local body=$3

    echo -e "Creating: ${YELLOW}$title${NC}"
    gh issue create --title "$title" --label "$labels" --body "$body"
}

# Create Phase 2 issues
if [ "$CREATE_PHASE2" = true ] || [ "$CREATE_ALL" = true ]; then
    echo -e "${BLUE}Creating Phase 2 (ETL Optimization) issues...${NC}"
    echo ""

    create_issue "[REFACTOR] ETL-001: Modularize base_etl.py" \
        "type:refactor,area:etl,priority:p0,phase:2" \
"## Description
Split \`src/core/base_etl.py\` (4,400 lines) into smaller modules (<500 lines each)

## Acceptance Criteria
- [ ] Create \`src/core/etl_phases/\` directory
- [ ] Extract Phase 1 logic → \`phase1_blb_loader.py\`
- [ ] Extract Phase 3 logic → \`phase3_tracking_processor.py\`
- [ ] Extract derived columns → \`derived_columns.py\`
- [ ] Extract validation → \`validation.py\`
- [ ] \`base_etl.py\` reduced to orchestration only
- [ ] All 139 tables still generated
- [ ] All tests pass

## Technical Notes
- Maintain backward compatibility
- Keep orchestration in base_etl.py
- Each module should be independently testable"

    create_issue "[CHORE] ETL-002: Profile ETL and identify bottlenecks" \
        "type:chore,area:etl,priority:p1,phase:2" \
"## Description
Profile ETL execution to identify slow operations

## Acceptance Criteria
- [ ] Add timing instrumentation to each phase
- [ ] Identify top 10 slowest operations
- [ ] Document bottlenecks in \`docs/etl/ETL_PERFORMANCE.md\`
- [ ] Find all \`.iterrows()\` usage

## Technical Notes
- Use Python's cProfile or line_profiler
- Create performance baseline for future comparison"

    create_issue "[PERF] ETL-003: Replace .iterrows() with vectorized operations" \
        "type:perf,area:etl,priority:p0,phase:2" \
"## Description
Remove all \`.iterrows()\` calls and replace with vectorized pandas operations

**Depends on:** #ETL-002

## Acceptance Criteria
- [ ] Zero \`.iterrows()\` usage in codebase
- [ ] Use \`.groupby()\` and \`.apply()\` instead
- [ ] Data integrity maintained
- [ ] Performance improved (target: <60s for 4 games)

## Technical Notes
- CRITICAL: This is a project rule - no .iterrows() allowed
- Test thoroughly to ensure data integrity"

    create_issue "[TEST] ETL-004: Create table verification script" \
        "type:test,area:etl,priority:p1,phase:2" \
"## Description
Create automated script to verify all tables have data

## Acceptance Criteria
- [ ] Script checks all 139 tables exist
- [ ] Script checks row counts > 0 for active tables
- [ ] Script validates column schemas
- [ ] Output report in markdown format

## Technical Notes
- Location: \`scripts/verify-tables.py\`
- Should be runnable standalone and in CI"

    create_issue "[TEST] ETL-005: Verify all 139 tables have data" \
        "type:test,area:etl,priority:p1,phase:2" \
"## Description
Run verification to confirm all tables populated correctly

**Depends on:** #ETL-004

## Acceptance Criteria
- [ ] All dimension tables populated
- [ ] All fact tables populated
- [ ] All QA tables populated
- [ ] Document any empty/unused tables"

    create_issue "[TEST] ETL-006: Validate foreign key relationships" \
        "type:test,area:etl,priority:p1,phase:2" \
"## Description
Verify referential integrity across all tables

**Depends on:** #ETL-004

## Acceptance Criteria
- [ ] All foreign keys resolve
- [ ] No orphaned records
- [ ] Document relationship graph"

    create_issue "[DOCS] ETL-007: Identify and document unused tables" \
        "type:docs,area:etl,priority:p2,phase:2" \
"## Description
Find tables that aren't used by dashboard or downstream processes

**Depends on:** #ETL-005

## Acceptance Criteria
- [ ] List all unused tables
- [ ] Recommendation: keep, archive, or delete
- [ ] Update DATA_DICTIONARY.md"

    create_issue "[TEST] ETL-008: Validate xG calculations" \
        "type:test,area:etl,priority:p1,phase:2" \
"## Description
Verify expected goals calculation accuracy

## Acceptance Criteria
- [ ] xG values within expected ranges (0-1)
- [ ] xG sums match reasonable goals-per-game
- [ ] Compare against known benchmarks
- [ ] Add regression tests"

    create_issue "[TEST] ETL-009: Validate WAR/GAR calculations" \
        "type:test,area:etl,priority:p1,phase:2" \
"## Description
Verify Wins Above Replacement calculation accuracy

## Acceptance Criteria
- [ ] WAR values within expected ranges
- [ ] Component breakdowns sum correctly
- [ ] Add regression tests"

    create_issue "[TEST] ETL-010: Validate Corsi/Fenwick calculations" \
        "type:test,area:etl,priority:p1,phase:2" \
"## Description
Verify shot attempt metrics accuracy

## Acceptance Criteria
- [ ] Corsi = shots + missed + blocked
- [ ] Fenwick = shots + missed
- [ ] CF% + CA% = 100%
- [ ] Add regression tests"

    create_issue "[TEST] ETL-011: Verify goal counting matches official counts" \
        "type:test,area:etl,priority:p0,phase:2" \
"## Description
CRITICAL test - ensure goals counted correctly

## Acceptance Criteria
- [ ] Goals ONLY counted when \`event_type == 'Goal' AND event_detail == 'Goal_Scored'\`
- [ ] Match official game scores for all test games
- [ ] Document goal counting rules
- [ ] Add regression tests

## Technical Notes
- This is the most critical rule in the project
- Reference: \`src/calculations/goals.py\`"

    create_issue "[CHORE] ETL-012: Add verification tests to CI" \
        "type:chore,area:etl,priority:p2,phase:2" \
"## Description
Integrate table verification into CI pipeline

**Depends on:** #ETL-004, #ETL-005, #ETL-006

## Acceptance Criteria
- [ ] GitHub Action runs verification on PR
- [ ] Fails on missing tables
- [ ] Fails on broken foreign keys
- [ ] Reports results in PR comment"

    echo ""
    echo -e "${GREEN}Phase 2 issues created!${NC}"
fi

echo ""
echo -e "${GREEN}Done!${NC}"
echo ""
echo "Next steps:"
echo "  1. View issues: gh issue list"
echo "  2. View in browser: gh browse"
echo "  3. Start working: ./scripts/create-feature.sh refactor etl-modularization"
