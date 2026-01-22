---
name: validate
description: Run ETL validation suite and verify output integrity. Use after ETL runs, when checking goal counting, or verifying data quality.
allowed-tools: Bash, Read, Grep, Write, Edit, Task
---

# ETL Validation Suite

Comprehensive validation of ETL pipeline output with automatic documentation updates.

## Invocation

```
/validate               # Full validation (recommended)
/validate quick         # Quick checks only
/validate phase [N]     # Validate specific phase output
/validate goals         # Goal counting verification
/validate tables        # Table completeness check
/validate docs          # Update table docs only
```

---

## Full Validation Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. PRE-FLIGHT CHECKS                                        │
│    - ETL output exists                                      │
│    - Required files present                                 │
│    - No obvious errors in logs                              │
└────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. TABLE COMPLETENESS                                       │
│    - Count tables vs manifest (139 expected)                │
│    - Identify missing/extra tables                          │
│    - Flag empty tables                                      │
└────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. GOAL COUNTING VERIFICATION                               │
│    - Check filter: event_type='Goal' & event_detail='Goal_Scored' │
│    - Compare to official scores                             │
│    - ZERO TOLERANCE for discrepancies                       │
└────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. STAT ATTRIBUTION                                         │
│    - Only event_player_1 counted for stats                  │
│    - No duplicate micro-stats in linked events              │
│    - Assist rules (primary, secondary only)                 │
└────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. KEY INTEGRITY                                            │
│    - Format: {XX}{ID}{5D}                                   │
│    - Foreign keys valid                                     │
│    - Primary keys unique                                    │
└────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. HOCKEY SME REVIEW (if calculations changed)              │
│    - Corsi/Fenwick logic                                    │
│    - xG inputs reasonable                                   │
│    - WAR/GAR methodology                                    │
└────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. UPDATE DOCUMENTATION                                     │
│    - Table logic docs (docs/etl/TABLE_LOGIC.md)             │
│    - Data dictionary (docs/reference/DATA_DICTIONARY.md)    │
│    - Table manifest (config/table_manifest.json)            │
└────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 8. QA REPORT                                                │
│    - Generate validation report                             │
│    - Flag issues by severity                                │
│    - Create GitHub issues for failures                      │
└────────────────────────────────────────────────────────────┘
```

---

## Execution Commands

### Step 1: Pre-flight

```bash
# Check ETL output exists
ls data/output/*.csv | wc -l

# Check for error logs
grep -i "error\|critical" logs/etl.log | tail -20
```

### Step 2: Table Completeness

```bash
# Count tables
ACTUAL=$(ls data/output/*.csv | wc -l)
EXPECTED=139
echo "Tables: $ACTUAL / $EXPECTED"

# Find missing
diff <(ls data/output/*.csv | xargs -n1 basename | sed 's/.csv//' | sort) \
     <(cat config/table_manifest.json | python -c "import json,sys; [print(t) for t in sorted(json.load(sys.stdin)['tables'].keys())]")

# Check for empty tables
for f in data/output/*.csv; do
  if [ $(wc -l < "$f") -le 1 ]; then
    echo "EMPTY: $f"
  fi
done
```

### Step 3: Goal Counting

```bash
# Verify goal filter is correct
grep -r "event_type.*Goal" src/calculations/goals.py

# Count goals in output
python -c "
import pandas as pd
goals = pd.read_csv('data/output/fact_goals.csv')
print(f'Total goals: {len(goals)}')
print(goals.groupby('game_id').size())
"
```

Compare to official scores in `data/validation/official_scores.json`.

### Step 4: Stat Attribution

```bash
# Check for event_player_1 filter
grep -r "event_player_1" src/calculations/

# Verify no duplicate counting
python -c "
import pandas as pd
ep = pd.read_csv('data/output/event_players.csv')
# Check for duplicates in linked events
dupes = ep[ep['linked_event_key'] != ''].groupby(['linked_event_key', 'player_id']).size()
print(f'Potential duplicate stats: {len(dupes[dupes > 1])}')
"
```

### Step 5: Key Integrity

```bash
# Check key format
python -c "
import pandas as pd
import re

# Sample key check
games = pd.read_csv('data/output/dim_game.csv')
pattern = r'^[A-Z]{2}\d+$'
invalid = games[~games['game_key'].str.match(pattern, na=False)]
print(f'Invalid game keys: {len(invalid)}')
"

# FK validation
./benchsight.sh etl validate --fk-only
```

### Step 6: Hockey SME Review

For calculation changes, invoke hockey-stats specialist:

```
Use Task tool with hockey-analytics-sme agent:
"Review the following calculation changes for correctness:
- [list changed files]
- Verify Corsi/Fenwick methodology
- Check xG feature inputs
- Validate WAR components"
```

### Step 7: Update Documentation

After validation passes, update docs:

#### Table Logic (docs/etl/TABLE_LOGIC.md)

```python
# Generate table logic doc
tables = {}
for csv in glob.glob('data/output/*.csv'):
    df = pd.read_csv(csv)
    name = os.path.basename(csv).replace('.csv', '')
    tables[name] = {
        'columns': list(df.columns),
        'row_count': len(df),
        'primary_key': detect_pk(df),
        'foreign_keys': detect_fks(df)
    }

# Write to docs/etl/TABLE_LOGIC.md
```

#### Data Dictionary (docs/reference/DATA_DICTIONARY.md)

Update with:
- New columns discovered
- Data types
- Value ranges
- Business rules

#### Table Manifest (config/table_manifest.json)

Sync with actual output:
- Add new tables
- Remove deprecated tables
- Update schemas

---

## Quick Mode (`/validate quick`)

Minimum checks only:

```bash
./benchsight.sh etl validate
```

Checks:
- Table count
- Goal totals
- No empty critical tables

Skips:
- Full FK validation
- Hockey SME review
- Doc updates

---

## Phase-Specific Validation (`/validate phase N`)

| Phase | Validates |
|-------|-----------|
| 1 | Raw data loaded, BLB parsed |
| 3B | Dimension tables complete |
| 4 | Event tables linked correctly |
| 5-7 | Calculations reasonable |
| 8-10 | Aggregations correct |
| 11 | QA tables populated |

---

## Goal-Only Validation (`/validate goals`)

CRITICAL check for goal counting:

```python
# ONLY valid goal filter
GOAL_FILTER = (df['event_type'] == 'Goal') & (df['event_detail'] == 'Goal_Scored')

# NEVER count these as goals:
# - event_type='Shot' with event_detail='Goal'
# - event_detail='Goal' without event_type='Goal'
```

Compare output to `data/validation/official_scores.json`.

---

## Docs-Only Update (`/validate docs`)

Just update documentation without full validation:

1. Read current table output
2. Update TABLE_LOGIC.md
3. Update DATA_DICTIONARY.md
4. Update table_manifest.json
5. Commit doc changes

---

## Validation Report

```
═══════════════════════════════════════════════════
              ETL VALIDATION REPORT
═══════════════════════════════════════════════════
Run: 2026-01-22 10:30:15
Duration: 82.3 seconds

TABLE COMPLETENESS
  Tables generated: 132 / 139
  ❌ MISSING: 7 tables (see #31)
  ⚠️  EMPTY: qa_orphaned_events (expected)

GOAL COUNTING
  ✅ Goal filter correct
  ✅ Totals match official: 45 goals across 4 games

STAT ATTRIBUTION
  ✅ event_player_1 filter in place
  ✅ No duplicate micro-stats found

KEY INTEGRITY
  ✅ All keys valid format
  ✅ 0 FK violations
  ✅ 0 duplicate PKs

HOCKEY SME
  ⏭️  Skipped (no calculation changes)

DOCUMENTATION
  📝 Updated: TABLE_LOGIC.md
  📝 Updated: DATA_DICTIONARY.md
  ⚠️  table_manifest.json needs sync (7 missing)

═══════════════════════════════════════════════════
STATUS: ⚠️  PASS WITH WARNINGS
═══════════════════════════════════════════════════

Actions Required:
  1. Investigate 7 missing tables (#31)
  2. Sync table_manifest.json
```

---

## Severity Levels

| Level | Meaning | Action |
|-------|---------|--------|
| CRITICAL | Data integrity broken | STOP - fix immediately |
| ERROR | Incorrect output | Fix before commit |
| WARNING | Potential issue | Investigate, may be OK |
| INFO | Informational | No action needed |

### Critical Issues (auto-create GitHub issue)

- Goal count mismatch
- Missing critical tables (dim_player, dim_game, etc.)
- Duplicate primary keys
- Broken foreign keys in core tables

---

## Integration

After `/validate` passes:
- Run `/post-code` for full workflow
- Or proceed to commit if only ETL changes

Creates GitHub issues automatically for:
- Missing tables
- Goal discrepancies
- Critical validation failures
