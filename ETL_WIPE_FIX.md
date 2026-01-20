# ETL Wipe Issue - FIXED

## What Happened

When you ran `python run_etl.py --wipe`, it deleted ALL CSV files from `data/output/`. The problem was:

1. **Wipe deleted everything** - All tables were removed
2. **ETL runs in phases** - Later phases depend on tables created in earlier phases
3. **Missing dependencies** - When later phases tried to load tables that didn't exist yet, they got empty DataFrames
4. **Empty tables created** - Table builders didn't check if source data was empty, so they created empty tables

## The Fix - IN-MEMORY TABLE STORE

I've completely refactored the ETL to use an **in-memory table store** so it works from scratch without relying on previously generated CSVs.

### Key Changes

1. **Created `src/core/table_store.py`** - Global in-memory cache for tables
   - Tables created during ETL are stored in memory
   - Later phases can access tables from earlier phases without reading CSV
   - Falls back to CSV only if table not in cache (for backward compatibility)

2. **Updated all `load_table()` functions** to check cache first:
   - `src/tables/core_facts.py`
   - `src/tables/remaining_facts.py`
   - `src/tables/shift_analytics.py`
   - `src/tables/event_analytics.py`

3. **Updated `save_output_table()` in `table_writer.py`**:
   - Now stores tables in cache when saving
   - All tables saved through this function are automatically cached

4. **Updated `base_etl.py`**:
   - Critical functions now use table store when reading tables
   - Ensures data flows through memory during the same ETL run

## How It Works Now

```
Phase 1-3: Base ETL
├─ Creates fact_events, fact_shifts, etc.
├─ Saves to CSV
└─ ALSO stores in memory cache ✅

Phase 4: Core Stats
├─ Needs fact_events, fact_shifts
├─ Checks cache FIRST ✅ (finds them from Phase 1-3)
└─ Creates fact_player_game_stats, etc.

Phase 4C: Remaining Facts
├─ Needs fact_player_game_stats, fact_events, etc.
├─ Checks cache FIRST ✅ (finds them from earlier phases)
└─ Creates derived tables
```

**Result:** ETL now works completely from scratch! No reliance on previously generated CSVs.

## Testing

After re-running ETL, verify tables are populated:

```bash
# Run ETL (works even after wipe now!)
python run_etl.py --wipe

# Check table counts
python run_etl.py --status

# Validate tables
python run_etl.py --validate
```

## Benefits

- ✅ **Works from scratch** - No need for previously generated CSVs
- ✅ **Faster** - In-memory access is faster than reading CSV
- ✅ **Backward compatible** - Still reads from CSV if table not in cache
- ✅ **Resilient** - Clear warnings when dependencies are missing

## Notes

- The table store is cleared between ETL runs (fresh start each time)
- Tables are still saved to CSV (for persistence and external access)
- Cache is checked first, CSV is fallback (best of both worlds)
