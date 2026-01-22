# PRD: ETL-013 - Comprehensive Table Verification Framework

**Product Requirements Document**

Created: 2026-01-22
Status: Approved
Owner: Developer
Related Issues: #35, #6, #7, #8, #31

---

## Problem Statement

**What problem are we solving?**

The ETL pipeline generates 139 tables, but we lack systematic verification that:
1. All expected tables are generated (currently seeing 132 vs 139)
2. Tables have correct schemas
3. Tables have expected row counts
4. Foreign key relationships are valid
5. No duplicate keys exist

**Why is this important?**

- Missing tables cause dashboard failures
- Schema drift causes silent bugs
- Invalid foreign keys cause join failures
- Duplicates cause incorrect aggregations
- We need confidence that ETL output is complete and correct

**Who is affected?**

- Dashboard developers relying on table contracts
- Data consumers expecting consistent schemas
- Users seeing incorrect or missing data

---

## Solution Approach

**How will we solve this problem?**

Create a comprehensive verification framework that runs after each ETL execution and validates:
1. Table existence (all 139 tables)
2. Schema correctness (columns, types)
3. Row count thresholds (minimum expected rows)
4. Foreign key integrity
5. Primary key uniqueness

**What are the key design decisions?**

1. **Table manifest as source of truth** - JSON file defining expected tables
2. **Schema contracts** - Each table has defined schema
3. **Fail fast** - Stop on first critical error
4. **CI integration** - Run on every PR

---

## Technical Design

### Architecture

**Verification Flow:**

```
ETL Completes
      ↓
[Table Verification Framework]
      ↓
  ┌──────────────────────────────────┐
  │ 1. Check all tables exist        │
  │ 2. Validate schemas              │
  │ 3. Check row count thresholds    │
  │ 4. Verify foreign keys           │
  │ 5. Check for duplicate keys      │
  └──────────────────────────────────┘
      ↓
PASS (all checks pass) or FAIL (detailed report)
```

### Implementation Details

**New files/modules needed:**

| File | Purpose |
|------|---------|
| `config/table_manifest.json` | Defines all 139 tables with schemas |
| `src/validation/table_verifier.py` | Core verification logic |
| `tests/test_table_verification.py` | Verification tests |

**Table Manifest Structure:**

```json
{
  "version": "1.0",
  "total_tables": 139,
  "tables": {
    "dim_players": {
      "type": "dimension",
      "required_columns": ["player_id", "player_name", "team_id"],
      "primary_key": "player_id",
      "foreign_keys": {
        "team_id": "dim_teams.team_id"
      },
      "min_rows": 1,
      "description": "Player dimension table"
    },
    "fact_goals": {
      "type": "fact",
      "required_columns": ["goal_id", "game_id", "player_id", "period", "time"],
      "primary_key": "goal_id",
      "foreign_keys": {
        "game_id": "dim_games.game_id",
        "player_id": "dim_players.player_id"
      },
      "min_rows": 1,
      "description": "Goal events fact table"
    }
  }
}
```

**Verification API:**

```python
class TableVerifier:
    def __init__(self, output_dir: Path, manifest_path: Path):
        self.output_dir = output_dir
        self.manifest = self._load_manifest(manifest_path)

    def verify_all(self) -> VerificationResult:
        """Run all verification checks."""
        results = []
        results.append(self.check_table_existence())
        results.append(self.check_schemas())
        results.append(self.check_row_counts())
        results.append(self.check_foreign_keys())
        results.append(self.check_primary_keys())
        return VerificationResult(results)

    def check_table_existence(self) -> CheckResult:
        """Verify all expected tables exist as CSV files."""
        missing = []
        for table_name in self.manifest['tables']:
            csv_path = self.output_dir / f"{table_name}.csv"
            if not csv_path.exists():
                missing.append(table_name)
        return CheckResult('existence', passed=len(missing) == 0, missing=missing)

    def check_schemas(self) -> CheckResult:
        """Verify each table has required columns."""
        ...

    def check_foreign_keys(self) -> CheckResult:
        """Verify all foreign key values exist in parent tables."""
        ...
```

---

## Implementation Phases

### Phase 1: Create Table Manifest

**Description:** Document all 139 expected tables with schemas.

**Tasks:**
- [ ] Audit current ETL output to list all generated tables
- [ ] Identify the 7 missing tables (132 vs 139)
- [ ] Create `config/table_manifest.json` with all tables
- [ ] Define required columns for each table
- [ ] Define primary/foreign key relationships

**Success Criteria:**
- Complete manifest with 139 tables
- All schemas documented
- Missing tables identified and logged as issues

### Phase 2: Build Verification Framework

**Description:** Create the core verification logic.

**Tasks:**
- [ ] Create `src/validation/table_verifier.py`
- [ ] Implement existence check
- [ ] Implement schema check
- [ ] Implement row count check
- [ ] Implement foreign key check
- [ ] Implement primary key uniqueness check

**Success Criteria:**
- All checks implemented
- Clear error messages for failures
- Summary report output

### Phase 3: Integrate with ETL and CI

**Description:** Make verification part of standard workflow.

**Tasks:**
- [ ] Add `--verify` flag to ETL run
- [ ] Add to `./benchsight.sh etl validate`
- [ ] Add to CI pipeline
- [ ] Create GitHub Action for verification

**Success Criteria:**
- Verification runs automatically after ETL
- CI fails on verification failures
- Clear reporting in PR checks

---

## Success Criteria

**How do we know this is complete and successful?**

- [ ] Table manifest documents all 139 tables
- [ ] Verification framework catches missing tables
- [ ] Framework catches schema mismatches
- [ ] Framework catches FK violations
- [ ] Framework catches duplicate PKs
- [ ] Integrated into CI pipeline

**Acceptance Tests:**
- Remove a table → verification fails
- Add wrong column → verification fails
- Create duplicate PK → verification fails
- Create orphan FK → verification fails

---

## Dependencies

**What needs to exist or be completed first?**

- [ ] ETL must complete successfully
- [ ] Understanding of 7 missing tables (#31)

**Blocking Issues:**
- #31 - Investigate missing tables (should be resolved as part of Phase 1)

---

## Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Manifest gets out of sync | Medium | Medium | Update manifest when adding tables |
| FK checks too slow | Low | Medium | Sample-based checking for large tables |
| False positives | Medium | Low | Careful threshold tuning |

---

## Testing Strategy

**How will we test this?**

- [ ] Unit tests for each check type
- [ ] Integration test with full ETL output
- [ ] Test with intentionally broken data

**Test scenarios:**
- All tables present and correct
- Missing table
- Wrong schema
- Duplicate primary key
- Orphan foreign key
- Empty table (below threshold)

---

## Documentation

**What documentation needs to be updated?**

- [ ] ETL documentation
- [ ] Validation workflow docs
- [ ] Table manifest is self-documenting

---

## Related Documents

- [ETL Architecture](../etl/ETL_ARCHITECTURE.md)
- [Table Definitions](../../src/tables/)

---

## Notes

**Table Categories (139 total):**

| Category | Count | Pattern |
|----------|-------|---------|
| Dimension | 50 | `dim_*` |
| Fact | 81 | `fact_*` |
| QA | 8 | `qa_*` |
| **Total** | **139** | |

**Verification Levels:**

1. **Critical** - Table existence, PK uniqueness (fail build)
2. **Error** - Schema mismatch, FK violations (fail build)
3. **Warning** - Low row counts, unused columns (log only)

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-01-22 | Initial PRD | Claude |

---

*Status: Approved*
