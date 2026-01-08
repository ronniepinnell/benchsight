# Role: ETL Engineer

**Version:** 16.08  
**Updated:** January 8, 2026


## Scope
Build new tables, add columns, fix data transformations, extend ETL pipeline.

## First Steps
1. Read `LLM_REQUIREMENTS.md` completely
2. Read `MASTER_GUIDE.md` for architecture overview
3. Check `config/TABLE_METADATA.json` for existing table definitions
4. Check `config/GROUND_TRUTH.json` for current table counts

## Critical Rules

### NEVER
- Delete existing working code without testing first
- Use `Shot_Goal` to count goals (use `event_type='Goal' AND event_detail='Goal_Scored'`)
- Create placeholder data
- Skip running tests after changes
- Output without running `python scripts/pre_delivery.py`

### ALWAYS
- Run ETL from scratch before claiming success: `rm -rf data/output/*.csv && python -m src.etl_orchestrator full`
- Verify goal counts: must be 17 total (18969=7, 18977=6, 18981=3, 18987=1)
- Update `config/TABLE_METADATA.json` when adding tables/columns
- Add tests for new functionality
- Increment version number

## Adding a New Table

1. Check if columns already exist in source data (tracking Excel files)
2. Add table definition to `config/TABLE_METADATA.json` with:
   - description, purpose, source_module, logic, grain
   - columns with description, context, calculation, type
3. Add processing code to `src/core/base_etl.py` or create new module
4. Register table in `src/etl_orchestrator.py`
5. Run ETL and verify table created
6. Add Tier 1 or Tier 2 tests as appropriate
7. Run `python scripts/pre_delivery.py` to verify everything

## Adding Missing Tables

Many tables have keys present in existing tables but no ETL code. To add:

```python
# Check what keys exist
import pandas as pd
events = pd.read_csv('data/output/fact_events.csv')
print(events.columns)  # Look for IDs that could be fact tables
```

Common patterns:
- `fact_*` tables derived from filtered `fact_events`
- `dim_*` tables from unique values in fact tables
- Bridge tables from unpivoting player columns

## Key Files

| File | Purpose |
|------|---------|
| `src/core/base_etl.py` | Main ETL logic (3174 lines) |
| `src/etl_orchestrator.py` | Pipeline coordination |
| `config/TABLE_METADATA.json` | Table/column metadata |
| `tests/test_tier1_blocking.py` | Must-pass tests |

## Testing Changes

```bash
# Quick test
rm -rf data/output/*.csv
python -m src.etl_orchestrator full
python -m pytest tests/test_tier1_blocking.py -v

# Full verification
python scripts/pre_delivery.py
```

## Verification Checklist

- [ ] ETL runs without errors
- [ ] 59+ tables created (check ground truth)
- [ ] 17 goals counted correctly
- [ ] All Tier 1 tests pass
- [ ] TABLE_METADATA.json updated
- [ ] Version bumped
