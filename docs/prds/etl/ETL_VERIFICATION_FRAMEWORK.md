# PRD: ETL Verification Framework

**Status:** Draft
**Priority:** P0
**Phase:** 2 (ETL Optimization)
**Owner:** [Your Name]
**Created:** 2025-01-22
**GitHub Issues:** #35, #6, #7, #8

---

## Overview

### Problem Statement
The ETL pipeline produces 139 tables, but there's no systematic way to verify:
- All tables are generated
- Tables have correct schemas
- Data quality meets standards
- Foreign keys are valid
- Business rules are enforced

Currently showing 132 tables vs 139 expected (#31).

### Solution
Create a comprehensive verification framework that validates tables at multiple levels: existence, schema, data quality, relationships, and business rules.

---

## Goals

1. **Verify all 139 tables exist** with correct names and locations
2. **Validate schemas** match DATA_DICTIONARY.md
3. **Check data quality** (nulls, ranges, types)
4. **Verify relationships** (PK uniqueness, FK integrity)
5. **Enforce business rules** (goal counting, stat attribution)
6. **Generate reports** for human review
7. **Integrate with CI** for automated checks

### Success Criteria

- [ ] 100% of tables verified on each ETL run
- [ ] Schema mismatches detected and reported
- [ ] Data quality issues flagged with severity
- [ ] FK violations caught before Supabase upload
- [ ] Report generated in < 30 seconds
- [ ] CI integration blocks PRs with failures

---

## Non-Goals

- Real-time monitoring (batch verification only)
- Automatic data correction (report only)
- Performance optimization (separate effort)
- UI for viewing results (CLI/markdown only)

---

## Requirements

### Functional Requirements

#### FR-1: Table Existence Verification
- Check all 139 expected tables exist in `data/output/`
- Report missing tables with expected location
- Report unexpected tables (not in spec)

#### FR-2: Schema Validation
- Compare columns against DATA_DICTIONARY.md
- Check column data types
- Check nullability constraints
- Report: missing columns, extra columns, type mismatches

#### FR-3: Data Quality Checks
- Calculate null percentage per column
- Validate value ranges (e.g., xG in [0,1], percentages in [0,100])
- Check for duplicate rows
- Validate date formats

#### FR-4: Key Validation
- Verify primary key uniqueness
- Verify PK format matches `{XX}{ID}{5D}` pattern
- Verify all foreign keys resolve to valid PKs
- Report orphaned records

#### FR-5: Business Rule Validation
- **Goal Counting:** Verify goals only where `event_type='Goal' AND event_detail='Goal_Scored'`
- **Stat Attribution:** Verify stats counted only for `player_role='event_player_1'`
- **Corsi/Fenwick:** Verify CF% + CA% = 100%
- **Assists:** Verify only primary and secondary counted

#### FR-6: Report Generation
- Generate markdown report
- Include summary (pass/fail/warn counts)
- Include per-table details
- Include actionable error messages
- Save to `data/output/verification_report.md`

#### FR-7: CI Integration
- GitHub Action runs on PR
- Fails PR if critical issues found
- Posts summary as PR comment
- Uploads full report as artifact

### Non-Functional Requirements

- **Performance:** Complete verification in < 60 seconds for 139 tables
- **Maintainability:** Table specs in config file, not hardcoded
- **Extensibility:** Easy to add new validation rules

---

## Technical Design

### Architecture

```
scripts/
  verify_tables.py      # Main verification script

config/
  table_specs.json      # Expected tables, schemas, rules

src/core/
  verification/
    __init__.py
    table_checker.py    # Table existence
    schema_validator.py # Schema validation
    data_quality.py     # Data quality checks
    key_validator.py    # PK/FK validation
    business_rules.py   # Business rule checks
    report_generator.py # Report generation
```

### Table Specs Format

```json
{
  "tables": {
    "dim_player": {
      "type": "dimension",
      "primary_key": "player_key",
      "pk_pattern": "PL{player_id:05d}",
      "required_columns": ["player_key", "player_id", "player_name"],
      "column_types": {
        "player_key": "string",
        "player_id": "int",
        "player_name": "string"
      },
      "nullable": ["nickname", "birth_date"],
      "foreign_keys": {}
    },
    "fact_player_game_stats": {
      "type": "fact",
      "primary_key": "player_game_key",
      "required_columns": ["player_game_key", "player_key", "game_key"],
      "foreign_keys": {
        "player_key": "dim_player.player_key",
        "game_key": "dim_game.game_key"
      },
      "value_ranges": {
        "goals": {"min": 0, "max": 10},
        "xg": {"min": 0.0, "max": 1.0}
      }
    }
  }
}
```

### Report Format

```markdown
# ETL Verification Report
Generated: 2025-01-22 10:30:45
ETL Run: game_18969

## Summary
| Status | Count |
|--------|-------|
| ✅ Passed | 135 |
| ⚠️ Warnings | 3 |
| ❌ Failed | 1 |

## Critical Failures
### fact_player_game_stats
- ❌ FK violation: 5 player_keys not found in dim_player

## Warnings
### dim_player
- ⚠️ Column 'nickname' is 45% null (threshold: 30%)

## Passed Tables
[List of 135 passed tables]
```

---

## Implementation Plan

### Phase 1: Core Framework (2-3 days)
1. Create directory structure
2. Implement table existence checker
3. Create basic report generator
4. Add CLI interface

### Phase 2: Schema Validation (2 days)
1. Create table_specs.json for all 139 tables
2. Implement schema validator
3. Add to report

### Phase 3: Data Quality (2 days)
1. Implement null percentage checks
2. Implement value range validation
3. Implement duplicate detection

### Phase 4: Key Validation (2 days)
1. Implement PK uniqueness check
2. Implement FK resolution check
3. Add to report

### Phase 5: Business Rules (1-2 days)
1. Implement goal counting verification
2. Implement stat attribution check
3. Add Corsi/Fenwick verification

### Phase 6: CI Integration (1 day)
1. Create GitHub Action workflow
2. Add PR comment posting
3. Configure failure thresholds

---

## Testing Strategy

### Unit Tests
- Test each validator in isolation
- Use mock data with known issues
- Test edge cases (empty tables, all nulls, etc.)

### Integration Tests
- Run full verification on sample ETL output
- Verify report generation
- Test CI workflow locally

### Acceptance Tests
- Run on actual ETL output
- Verify all 139 tables checked
- Review report readability

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| table_specs.json out of sync | Medium | High | Generate from DATA_DICTIONARY.md |
| False positives blocking CI | Medium | Medium | Configurable severity thresholds |
| Performance too slow | Low | Medium | Parallel table processing |

---

## Open Questions

1. Should warnings block CI, or only failures?
2. What null percentage threshold triggers warning vs failure?
3. Should we version the table_specs.json?
4. How to handle intentionally empty tables?

---

## Appendix

### Related Documents
- [DATA_DICTIONARY.md](../../data/DATA_DICTIONARY.md)
- [CLAUDE.md](../../../CLAUDE.md) - Goal counting rules
- [ETL_ARCHITECTURE.md](../../etl/ETL_ARCHITECTURE.md)

### Related Issues
- #35: Comprehensive table verification framework
- #6: Create table verification script
- #7: Verify all 139 tables have data
- #8: Validate foreign key relationships
- #31: Investigate missing 7 tables
