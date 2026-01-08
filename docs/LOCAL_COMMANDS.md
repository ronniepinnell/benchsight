# BenchSight Local Commands Reference

**Version:** 16.08  
**Updated:** January 8, 2026


## Quick Reference

### ETL Commands

```bash
# Full ETL run (wipes and rebuilds everything)
rm -rf data/output/*
rm -f data/.etl_state.json
python -m src.etl_orchestrator full

# Quick ETL (incremental, uses cached state)
python -m src.etl_orchestrator full

# Verify ETL output
python -c "import pandas as pd; df=pd.read_csv('data/output/fact_events.csv'); print('Goals:', len(df[(df['event_type']=='Goal') & (df['event_detail']=='Goal_Scored')]))"
ls data/output/*.csv | wc -l
```

### Supabase Sync Commands

```bash
# Sync all tables (wipe first)
python supabase/sync_to_supabase.py --wipe

# Sync only dimension tables
python supabase/sync_to_supabase.py --dims --wipe

# Sync only fact tables
python supabase/sync_to_supabase.py --facts --wipe

# Sync specific games only (facts with game_id)
python supabase/sync_to_supabase.py --games 18977 18981 --wipe

# Sync a single table
python supabase/sync_to_supabase.py --table fact_events --wipe

# Dry run (preview without changes)
python supabase/sync_to_supabase.py --dry-run
```

### Testing Commands

```bash
# Run all tests
python -m pytest tests/ -v

# Run only critical (tier 1) tests
python -m pytest tests/test_tier1_blocking.py -v

# Run ETL tests
python -m pytest tests/test_etl.py -v

# Run goal verification
python -m pytest tests/test_goal_verification.py -v
```

### Validation Commands

```bash
# Pre-delivery validation (runs full pipeline)
python scripts/pre_delivery.py

# BS Detector (finds suspicious code/data)
python scripts/bs_detector.py

# Verify delivery package
python scripts/utilities/verify_delivery.py
```

### Schema Commands

```bash
# Regenerate Supabase schema from CSVs
python supabase/generate_schema.py

# Preview schema without saving
python supabase/generate_schema.py --preview
```

### Data Quality Commands

```bash
# Check for non-integer floats in a CSV
python -c "
import pandas as pd
df = pd.read_csv('data/output/fact_shifts.csv')
for col in df.columns:
    if df[col].dtype == 'float64':
        vals = df[col].dropna()
        bad = vals[vals % 1 != 0]
        if len(bad) > 0:
            print(f'{col}: {bad.head(5).tolist()}')
"

# Check source tracking file for bad data
python -c "
import pandas as pd
df = pd.read_excel('data/raw/games/18981/18981_tracking.xlsx', sheet_name='shifts')
print(df['home_xtra'].dropna().unique())
"
```

## Common Workflows

### Adding a New Game

1. Create game folder: `data/raw/games/{game_id}/`
2. Add tracking file: `{game_id}_tracking.xlsx`
3. Add roster: `roster.json`
4. Run ETL: `python -m src.etl_orchestrator full`
5. Sync to Supabase: `python supabase/sync_to_supabase.py --games {game_id} --wipe`

### Fixing Data Issues

1. Edit source file in `data/raw/games/{game_id}/`
2. Clear ETL state:
   ```bash
   rm -rf data/output/*
   rm -f data/.etl_state.json
   ```
3. Re-run ETL: `python -m src.etl_orchestrator full`
4. Verify: Check goal count, table count
5. Re-sync: `python supabase/sync_to_supabase.py --wipe`

### Updating Supabase Schema

1. Regenerate schema: `python supabase/generate_schema.py`
2. In Supabase SQL Editor:
   - Drop existing tables (or run reset script)
   - Paste and run new schema.sql
3. Re-sync data: `python supabase/sync_to_supabase.py --wipe`

## Environment Setup

### Required Packages

```bash
pip install pandas openpyxl requests numpy
```

### Config File

Edit `config/config_local.ini`:
```ini
[supabase]
url = https://your-project.supabase.co
service_key = your-service-role-key

[loader]
batch_size = 500
verbose = true
```

## Troubleshooting

### ETL Fails

```bash
# Check logs
cat logs/etl_v5.log | tail -50

# Clear state and retry
rm -rf data/output/*
rm -f data/.etl_state.json
python -m src.etl_orchestrator full
```

### Supabase Sync Fails

```bash
# Check for type mismatches (float vs int)
python -c "
import pandas as pd
df = pd.read_csv('data/output/TABLE_NAME.csv')
print(df.dtypes)
"

# Regenerate schema to match CSVs
python supabase/generate_schema.py
```

### Wrong Goal Count

```bash
# Should be 17 (18969:7, 18977:6, 18981:3, 18987:1)
python -c "
import pandas as pd
df = pd.read_csv('data/output/fact_events.csv')
goals = df[(df['event_type']=='Goal') & (df['event_detail']=='Goal_Scored')]
print('Total:', len(goals))
print(goals.groupby('game_id').size())
"
```
