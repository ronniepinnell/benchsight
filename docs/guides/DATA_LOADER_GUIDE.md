# Data Loader Complete Guide

**Version:** 2.0  
**Date:** December 30, 2025

---

## Overview

BenchSight has two loader scripts:
1. **`load_all_tables.py`** - Simple loader for all 96 tables
2. **`flexible_loader_with_logging.py`** - Full-featured loader with logging

---

## Quick Reference

```bash
# Load everything
python scripts/load_all_tables.py --upsert

# Preview only (no changes)
python scripts/load_all_tables.py --dry-run

# Load single table
python scripts/load_all_tables.py --table dim_player --upsert

# Full logging version
python scripts/flexible_loader_with_logging.py --scope full --operation replace
```

---

## Script 1: load_all_tables.py

### Purpose
Loads all CSV files from `data/output/` to Supabase.

### Commands

| Command | Description |
|---------|-------------|
| `--upsert` | Insert new rows, update existing (handles duplicates) |
| `--dry-run` | Preview what would be loaded, no changes |
| `--table TABLE` | Load only specified table |
| `--skip-dims` | Skip dimension tables, load only facts |

### Examples

```bash
# Load all tables with upsert (recommended)
python scripts/load_all_tables.py --upsert

# Preview what will load
python scripts/load_all_tables.py --dry-run

# Load single table
python scripts/load_all_tables.py --table fact_events --upsert

# Load only fact tables
python scripts/load_all_tables.py --skip-dims --upsert
```

### Output

```
Connecting to Supabase...

============================================================
LOADING 96 TABLES (upsert)
============================================================

[ 1/96] dim_comparison_type... ✓ 5 rows
[ 2/96] dim_composite_rating... ✓ 6 rows
[ 3/96] dim_danger_zone... ✓ 5 rows
...
[96/96] qa_suspicious_stats... ✓ 22 rows

============================================================
COMPLETE
============================================================
Tables: 96/96
Total Rows: 120,534
Duration: 45.2s
```

---

## Script 2: flexible_loader_with_logging.py

### Purpose
Full-featured loader with comprehensive logging and more options.

### Commands

| Command | Description |
|---------|-------------|
| `--scope full` | Load all tables |
| `--scope table --table NAME` | Load single table |
| `--operation replace` | Delete existing, insert new |
| `--operation upsert` | Insert/update (handles duplicates) |
| `--operation append` | Add without deleting |
| `--dry-run` | Preview only |
| `--log-to-supabase` | Write logs to Supabase tables |
| `--show-config` | Display current configuration |
| `--test-connection` | Test Supabase connection |
| `--show-last-run` | Show last run results |

### Examples

```bash
# Show configuration
python scripts/flexible_loader_with_logging.py --show-config

# Test connection
python scripts/flexible_loader_with_logging.py --test-connection

# Full replace (delete + insert)
python scripts/flexible_loader_with_logging.py --scope full --operation replace

# Full upsert (safer)
python scripts/flexible_loader_with_logging.py --scope full --operation upsert

# Single table upsert
python scripts/flexible_loader_with_logging.py --scope table --table fact_events --operation upsert

# Dry run
python scripts/flexible_loader_with_logging.py --scope full --operation replace --dry-run

# With Supabase logging
python scripts/flexible_loader_with_logging.py --scope full --operation replace --log-to-supabase

# View last run
python scripts/flexible_loader_with_logging.py --show-last-run
```

### Log Output

Logs are written to `logs/YYYY-MM-DD/run_id/`:
- `run.log` - Human-readable log
- `run.jsonl` - JSON lines for parsing
- `summary.json` - Run summary
- `SUMMARY.md` - Markdown summary
- `errors/errors.log` - Error details
- `tables/*.json` - Per-table results

---

## Operations Explained

### REPLACE
```
1. Delete all existing rows from table
2. Insert all rows from CSV
```
**Use when:** Fresh load, schema changed, data corruption

### UPSERT
```
1. For each row:
   - If primary key exists: UPDATE
   - If primary key doesn't exist: INSERT
```
**Use when:** Incremental updates, handling duplicates

### APPEND
```
1. Insert all rows (may fail on duplicates)
```
**Use when:** Adding new data only, keys guaranteed unique

---

## Loading Specific Data

### Load One Game's Data

```bash
# After running ETL for a specific game, load all related tables
# Tables that contain game_id will have data for that game

# Upsert all tables (safest)
python scripts/load_all_tables.py --upsert

# Or load specific tables
python scripts/load_all_tables.py --table fact_events --upsert
python scripts/load_all_tables.py --table fact_shifts --upsert
python scripts/load_all_tables.py --table fact_events_player --upsert
```

### Load Only Dimension Tables

```bash
# Load dims first (they're referenced by facts)
for table in dim_player dim_team dim_schedule dim_event_type dim_period; do
    python scripts/load_all_tables.py --table $table --upsert
done
```

### Load Only Fact Tables

```bash
python scripts/load_all_tables.py --skip-dims --upsert
```

---

## Editing Dimension Tables

### Option 1: Edit CSV and Reload

```bash
# 1. Edit the CSV file
nano data/output/dim_event_type.csv

# 2. Reload the table
python scripts/load_all_tables.py --table dim_event_type --upsert
```

### Option 2: Edit in Supabase Directly

1. Go to https://supabase.com/dashboard/project/uuaowslhpgyiudmbvqze
2. Navigate to Table Editor
3. Find dimension table
4. Edit rows directly
5. Changes are immediate

### Option 3: SQL Update

```sql
-- In Supabase SQL Editor
UPDATE dim_event_type 
SET event_type = 'Wrist Shot'
WHERE event_type_id = 'EVT001';

-- Add new row
INSERT INTO dim_event_type (event_type_id, event_type)
VALUES ('EVT999', 'New Event Type');

-- Delete row
DELETE FROM dim_event_type 
WHERE event_type_id = 'EVT999';
```

---

## Troubleshooting

### "Could not find column X"

**Cause:** Schema in Supabase doesn't match CSV columns

**Fix:**
```bash
# 1. Regenerate schema from CSV
# 2. Run new schema SQL in Supabase
# 3. Reload data
```

### "Duplicate key violation"

**Cause:** Primary key already exists

**Fix:**
```bash
# Use upsert instead of replace/append
python scripts/load_all_tables.py --upsert
```

### "Foreign key violation"

**Cause:** Referenced row doesn't exist in parent table

**Fix:**
```bash
# Load dimension tables first
python scripts/load_all_tables.py --table dim_player --upsert
python scripts/load_all_tables.py --table dim_team --upsert
# Then load fact tables
python scripts/load_all_tables.py --skip-dims --upsert
```

### Connection Error

**Cause:** Invalid credentials or network issue

**Fix:**
```bash
# Check config
python scripts/flexible_loader_with_logging.py --show-config

# Test connection
python scripts/flexible_loader_with_logging.py --test-connection
```

---

## Configuration

### Config File Location
```
config/config_local.ini
```

### Config Contents
```ini
[supabase]
url = https://YOUR_PROJECT.supabase.co
service_key = YOUR_SERVICE_ROLE_KEY

[loader]
batch_size = 500
verbose = true
default_operation = upsert

[paths]
data_dir = data/output
log_dir = logs
```

### Environment Variable Alternative
```bash
export SUPABASE_URL="https://YOUR_PROJECT.supabase.co"
export SUPABASE_SERVICE_KEY="YOUR_KEY"
```

---

## Batch Size Tuning

Default batch size is 500 rows per API call. Adjust if needed:

```ini
# In config_local.ini
[loader]
batch_size = 1000  # Faster but may hit limits
batch_size = 100   # Slower but more reliable
```

---

## Full Reload Process

To completely reload all data:

```bash
# 1. Run truncate SQL in Supabase
# (Use sql/06_TRUNCATE_ALL_DATA.sql)

# 2. Load all tables
python scripts/load_all_tables.py --upsert

# 3. Verify
python scripts/flexible_loader_with_logging.py --show-last-run
```

---

## Automation

### Cron Job Example

```bash
# Run nightly at 2 AM
0 2 * * * cd /path/to/benchsight && python scripts/load_all_tables.py --upsert >> logs/cron.log 2>&1
```

### Python Script

```python
import subprocess
import datetime

def run_loader():
    result = subprocess.run(
        ["python", "scripts/load_all_tables.py", "--upsert"],
        capture_output=True,
        text=True
    )
    print(f"[{datetime.now()}] Loader completed")
    print(result.stdout)
    if result.returncode != 0:
        print(f"ERRORS: {result.stderr}")

if __name__ == "__main__":
    run_loader()
```

---

## Load Order

Tables are loaded in dependency order:

1. **Dimension Tables (44)** - No dependencies
   - dim_player, dim_team, dim_schedule, etc.

2. **Fact Tables (51)** - Depend on dimensions
   - fact_events, fact_shifts, etc.

3. **Other Tables (1)**
   - qa_suspicious_stats

The scripts handle this order automatically.

---

## Monitoring Loads

### Check Table Counts

```sql
-- In Supabase SQL Editor
SELECT * FROM get_all_table_counts();
```

### Check Recent Runs

```sql
SELECT * FROM v_recent_runs;
```

### Check Specific Table

```sql
SELECT COUNT(*) FROM fact_events;
SELECT * FROM fact_events LIMIT 10;
```

---

## CSV File Requirements

For the loader to work, CSV files must:

1. Be in `data/output/` directory
2. Have filename matching table name (e.g., `dim_player.csv` → `dim_player`)
3. Have header row with column names
4. Have column names matching Supabase schema
5. Use UTF-8 encoding

---

## Summary

| Task | Command |
|------|---------|
| Load all, handle duplicates | `python scripts/load_all_tables.py --upsert` |
| Preview only | `python scripts/load_all_tables.py --dry-run` |
| Load single table | `python scripts/load_all_tables.py --table NAME --upsert` |
| Full replace with logging | `python scripts/flexible_loader_with_logging.py --scope full --operation replace` |
| Check config | `python scripts/flexible_loader_with_logging.py --show-config` |
| Test connection | `python scripts/flexible_loader_with_logging.py --test-connection` |
