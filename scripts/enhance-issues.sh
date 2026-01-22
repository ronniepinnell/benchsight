#!/bin/bash
# enhance-issues.sh - Enhance GitHub issues with full detail
# Usage: ./scripts/enhance-issues.sh

set -e

echo "🔧 Enhancing Phase 2 P0 issues..."

# Issue #5 - Vectorization (P0)
echo "Updating issue #5..."
gh issue edit 5 --milestone "M1: MVP Foundation" --body "$(cat <<'EOF'
## Description
Replace all `.iterrows()` calls with pandas vectorized operations. This is a critical performance optimization that's explicitly required by CLAUDE.md rules.

## Priority: P0 (Critical)
## Execution Order: 7 (after tests and validation framework)
## Depends On: #36, #35

## Background
`.iterrows()` is 100-1000x slower than vectorized operations. Current ETL takes ~80 seconds for 4 games - this must improve as we scale.

## Acceptance Criteria
- [ ] `grep -r "iterrows" src/` returns zero results
- [ ] All 139 tables still generated correctly
- [ ] ETL validation passes
- [ ] Goal counts match official (verified by #13)
- [ ] Performance improvement ≥30%
- [ ] No regression in any calculations

## Implementation Steps
1. Profile ETL to identify all `.iterrows()` locations
2. Rank by runtime impact (highest first)
3. Replace each with vectorized equivalent:
   - `.groupby().apply()` for grouped operations
   - `.loc[]` with boolean indexing
   - `np.where()` for conditionals
   - `.merge()` instead of row-by-row lookups
4. Validate after each change
5. Benchmark performance

## Files to Modify
| File | Function | Priority |
|------|----------|----------|
| `src/core/base_etl.py` | `_build_event_players()` | High |
| `src/core/etl_phases/derived_columns.py` | `add_player_team_columns()` | High |
| `src/core/etl_phases/event_enhancers.py` | Various enhancers | Medium |
| `src/calculations/*.py` | Various | Medium |

## Test Strategy
- Before: Capture all CSV outputs
- After: Diff all outputs (must be identical)
- Run full validation suite
- Benchmark timing before/after

## Test Data
- 4-game dataset (current baseline)
- Known edge cases from test fixtures

## Related Issues
- #36 (unit tests - do first)
- #35 (verification framework - do first)
- #4 (profiling - can do in parallel)
- #25-29 (specific vectorization tasks)

## PRD
[PRD-ETL-003-vectorization.md](../docs/prds/PRD-ETL-003-vectorization.md)
EOF
)"

# Issue #13 - Goal Verification (P0)
echo "Updating issue #13..."
gh issue edit 13 --milestone "M1: MVP Foundation" --body "$(cat <<'EOF'
## Description
Create automated verification that ETL goal counts match official scoresheet totals. Goals are the foundation of all hockey analytics - this must be 100% accurate.

## Priority: P0 (Critical)
## Execution Order: 4 (after verification framework)
## Depends On: #35

## Background
CLAUDE.md Critical Rule:
```python
GOAL_FILTER = (df['event_type'] == 'Goal') & (df['event_detail'] == 'Goal_Scored')
```
**Never** count `event_type == 'Shot'` with `event_detail == 'Goal'`.

## Acceptance Criteria
- [ ] Official scores documented for all test games
- [ ] Automated test compares ETL output to official
- [ ] Test fails on ANY discrepancy (zero tolerance)
- [ ] Test runs as part of `pytest`
- [ ] Integrated into CI pipeline
- [ ] Clear error message showing expected vs actual

## Implementation Steps
1. Create `data/validation/official_scores.json` with verified scores
2. Create/enhance `tests/test_goal_verification.py`
3. Test loads official scores, compares to `fact_goals.csv`
4. Add to `./benchsight.sh etl validate`
5. Add to CI pipeline

## Test Strategy
- Manually verify scores against scoresheets
- Test with correct data (should pass)
- Test with intentional bug (should fail)
- Test edge cases (OT, empty net, etc.)

## Test Data
```json
{
  "games": [
    {"game_id": "18969", "home_goals": 5, "away_goals": 3, "source": "official_scoresheet"},
    {"game_id": "18970", "home_goals": 4, "away_goals": 2, "source": "official_scoresheet"}
  ]
}
```

## Edge Cases to Handle
- Own goals (count for opposing team)
- Disallowed goals (should NOT count)
- Empty net goals (count normally)
- Shootout (verify league rules)

## Related Issues
- #35 (verification framework - do first)
- #36 (unit tests)
- #10 (xG validation - related)

## PRD
[PRD-ETL-011-goal-verification.md](../docs/prds/PRD-ETL-011-goal-verification.md)
EOF
)"

# Issue #31 - Missing Tables (P0)
echo "Updating issue #31..."
gh issue edit 31 --milestone "M1: MVP Foundation" --add-label "priority:p0" --body "$(cat <<'EOF'
## Description
ETL produces 132 tables but 139 are expected. Identify which 7 tables are missing and why.

## Priority: P0 (Critical)
## Execution Order: 1 (do this FIRST)
## Depends On: None

## Background
The table manifest documents 139 expected tables (50 dim, 81 fact, 8 qa). Current ETL output shows 132. This gap must be understood before we can validate completeness.

## Acceptance Criteria
- [ ] Identify all 7 missing tables by name
- [ ] Determine why each is missing:
  - Not implemented yet?
  - Renamed?
  - Consolidated into another table?
  - Deprecated?
- [ ] Update table manifest to reflect reality
- [ ] Create issues for any tables that should exist but don't
- [ ] Document any intentional removals

## Investigation Steps
1. List all expected tables from manifest
2. List all generated tables in `data/output/`
3. Diff to find missing
4. Search codebase for each missing table
5. Document findings

## Commands
```bash
# List generated tables
ls data/output/*.csv | wc -l

# Compare to manifest
python -c "import json; print(len(json.load(open('config/table_manifest.json'))['tables']))"

# Find differences
diff <(ls data/output/*.csv | xargs -n1 basename | sed 's/.csv//' | sort) \
     <(python -c "import json; [print(t) for t in sorted(json.load(open('config/table_manifest.json'))['tables'].keys())]")
```

## Possible Outcomes
1. Tables should exist → Create implementation issues
2. Tables renamed → Update manifest
3. Tables consolidated → Update manifest + documentation
4. Tables deprecated → Remove from manifest, document why

## Related Issues
- #35 (verification framework - blocked by this)
- #7 (verify all tables have data)
- #6 (table verification script)

## Notes
This is the FIRST issue to tackle because it affects all subsequent verification work.
EOF
)"

# Issue #35 - Verification Framework (P0)
echo "Updating issue #35..."
gh issue edit 35 --milestone "M1: MVP Foundation" --body "$(cat <<'EOF'
## Description
Create comprehensive table verification framework that validates ETL output after each run.

## Priority: P0 (Critical)
## Execution Order: 2 (after missing tables investigation)
## Depends On: #31

## Background
We need systematic verification of:
- Table existence (all expected tables)
- Schema correctness (columns, types)
- Row count thresholds
- Foreign key integrity
- Primary key uniqueness

## Acceptance Criteria
- [ ] Table manifest defines all expected tables with schemas
- [ ] Verification framework catches missing tables
- [ ] Framework catches schema mismatches
- [ ] Framework catches FK violations
- [ ] Framework catches duplicate PKs
- [ ] Integrated into `./benchsight.sh etl validate`
- [ ] Integrated into CI pipeline
- [ ] Clear reporting of pass/fail with details

## Implementation Steps
1. Create `config/table_manifest.json` with all tables
2. Create `src/validation/table_verifier.py`
3. Implement checks:
   - `check_table_existence()`
   - `check_schemas()`
   - `check_row_counts()`
   - `check_foreign_keys()`
   - `check_primary_keys()`
4. Create test suite
5. Integrate into CLI and CI

## File Structure
```
config/
  table_manifest.json       # Source of truth for table definitions
src/
  validation/
    table_verifier.py       # Core verification logic
    __init__.py
tests/
  test_table_verification.py
```

## Validation Levels
| Level | Behavior | Examples |
|-------|----------|----------|
| CRITICAL | Stop ETL | Missing table, duplicate PK |
| ERROR | Log + continue | FK violation |
| WARNING | Log only | Low row count |

## Related Issues
- #31 (missing tables - do first)
- #6 (table verification script - superseded by this)
- #7 (verify all tables have data - part of this)
- #8 (validate FK relationships - part of this)

## PRD
[PRD-ETL-013-table-verification.md](../docs/prds/PRD-ETL-013-table-verification.md)
EOF
)"

# Issue #36 - Unit Tests (P0)
echo "Updating issue #36..."
gh issue edit 36 --milestone "M1: MVP Foundation" --body "$(cat <<'EOF'
## Description
Create unit tests for all critical calculation modules to enable safe refactoring.

## Priority: P0 (Critical)
## Execution Order: 3 (after verification framework)
## Depends On: #35

## Background
Complex calculations (goals, assists, Corsi, xG, WAR) have no test coverage. We cannot safely refactor (#5) without tests.

## Acceptance Criteria
- [ ] >80% coverage of `src/calculations/`
- [ ] All CLAUDE.md business rules have tests
- [ ] Tests run in <30 seconds
- [ ] Tests integrated into CI
- [ ] Tests catch intentional bugs

## Test Structure
```
tests/
  unit/
    calculations/
      test_goals.py         # Goal counting rules
      test_assists.py       # Assist attribution
      test_corsi.py         # Corsi/Fenwick
      test_time.py          # TOI calculations
      test_xg.py            # xG inputs
      test_war.py           # WAR/GAR
    conftest.py             # Shared fixtures
  fixtures/
    sample_events.csv
    sample_shifts.csv
```

## Critical Test Cases

### Goal Counting (test_goals.py)
- ✓ Goal counted when event_type='Goal' AND event_detail='Goal_Scored'
- ✓ Shot with event_detail='Goal' NOT counted as goal
- ✓ Goal counts match official scores

### Assist Attribution (test_assists.py)
- ✓ Primary assist counted (AssistPrimary)
- ✓ Secondary assist counted (AssistSecondary)
- ✓ Tertiary assist NOT counted (hockey rule)
- ✓ Max 2 assists per goal

### Stat Counting (test_stat_counting.py)
- ✓ Only event_player_1 counts for stats
- ✓ Linked event micro-stats counted once

## Test Data
- Small, focused fixtures from real games
- Edge case data (empty, nulls, etc.)
- Known correct outputs for comparison

## Related Issues
- #35 (verification framework - do first)
- #5 (vectorization - needs tests first)
- #40 (integration tests - after this)

## PRD
[PRD-ETL-035-unit-tests.md](../docs/prds/PRD-ETL-035-unit-tests.md)
EOF
)"

# Issue #37 - Error Handling (P0)
echo "Updating issue #37..."
gh issue edit 37 --milestone "M1: MVP Foundation" --body "$(cat <<'EOF'
## Description
Add comprehensive error handling throughout ETL pipeline with clear, actionable error messages.

## Priority: P0 (Critical)
## Execution Order: 5 (after unit tests)
## Depends On: #36

## Background
Current ETL has cryptic errors and no graceful degradation. Debugging is difficult.

## Acceptance Criteria
- [ ] Custom exception hierarchy for ETL errors
- [ ] All ETL phases wrapped with error handling
- [ ] Clear error messages with context
- [ ] Logging shows phase progress
- [ ] Critical errors stop immediately
- [ ] Non-critical errors log and continue

## Implementation Steps
1. Create `src/core/exceptions.py` with exception hierarchy
2. Create `src/core/decorators.py` with `@etl_phase` decorator
3. Apply decorator to all major ETL functions
4. Improve error messages in existing code
5. Add progress logging

## Exception Hierarchy
```python
ETLError (base)
├── ETLDataError        # Data quality issues
├── ETLConfigError      # Configuration problems
├── ETLValidationError  # Validation failures
└── ETLDependencyError  # Missing dependencies
```

## Error Message Format
```
ETLValidationError: Phase 'Build Events' failed

✗ [CRITICAL] event_players table empty
✗ [ERROR] 3 events missing game_id

Context:
  - Game files loaded: 4
  - Total raw events: 15,234
  - Phase runtime: 2.3s

Suggestion: Check that game files contain valid event data
```

## Related Issues
- #36 (unit tests - do first)
- #38 (phase validation)
- #35 (verification framework)

## PRD
[PRD-ETL-032-034-error-handling-validation.md](../docs/prds/PRD-ETL-032-034-error-handling-validation.md)
EOF
)"

# Issue #38 - Phase Validation (P0)
echo "Updating issue #38..."
gh issue edit 38 --milestone "M1: MVP Foundation" --body "$(cat <<'EOF'
## Description
Add validation gates between ETL phases to catch errors early instead of at the end.

## Priority: P0 (Critical)
## Execution Order: 6 (after error handling)
## Depends On: #37

## Background
Currently errors cascade through all phases before being discovered. Validation gates catch issues at the source.

## Acceptance Criteria
- [ ] Validation runs after each ETL phase
- [ ] Critical failures stop the pipeline
- [ ] Clear reporting of validation results
- [ ] Can skip validation with `--no-validate` flag
- [ ] Integrated into ETL run

## Implementation Steps
1. Create `src/validation/phase_validation.py`
2. Define validation checks for each phase:
   - Loading phase: raw data present, columns exist
   - Event building: event_players created, no duplicates
   - Calculations: reasonable values, no negatives
   - Table generation: all tables exist, FK valid
3. Integrate into `run_etl.py`
4. Add CLI flags

## Validation Gates
| After Phase | Key Checks |
|-------------|------------|
| Loading | Raw data loaded, required columns present |
| Event Building | event_players exists, no duplicate keys |
| Shift Building | shifts linked to events correctly |
| Calculations | Reasonable value ranges, no negatives |
| Table Generation | All tables exist, FK valid, PK unique |

## Related Issues
- #37 (error handling - do first)
- #35 (verification framework)
- #40 (integration tests)

## PRD
[PRD-ETL-032-034-error-handling-validation.md](../docs/prds/PRD-ETL-032-034-error-handling-validation.md)
EOF
)"

echo "✅ P0 issues enhanced with full detail"
echo ""
echo "Summary of execution order:"
echo "  1. #31 - Missing tables investigation"
echo "  2. #35 - Verification framework"
echo "  3. #36 - Unit tests"
echo "  4. #13 - Goal counting verification"
echo "  5. #37 - Error handling"
echo "  6. #38 - Phase validation"
echo "  7. #5  - Vectorization (safe to refactor)"
