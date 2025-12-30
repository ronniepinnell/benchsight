# ETL Pipeline Guide

**Version:** 2.0  
**Date:** December 30, 2025

---

## Overview

The ETL (Extract, Transform, Load) pipeline processes raw game tracking data from Excel files into the normalized star schema in Supabase.

```
Raw Excel Files → ETL (Python) → CSV Files → Loader → Supabase
```

---

## Pipeline Architecture

### Data Flow

```
data/raw/
├── BLB_Tables.xlsx              # Dimension tables
└── [game_id]/
    ├── events_tracking.xlsx     # Event data
    └── shifts_tracking.xlsx     # Shift data
          │
          ▼
      etl.py (orchestrator)
          │
          ▼
      src/etl/*.py (transformations)
          │
          ▼
data/output/
├── dim_*.csv (44 files)         # Dimension tables
├── fact_*.csv (51 files)        # Fact tables
└── qa_*.csv (1 file)            # Quality checks
          │
          ▼
scripts/load_all_tables.py
          │
          ▼
Supabase PostgreSQL (96 tables)
```

---

## Running ETL

### Basic Usage

```bash
# Process all games in data/raw/
python etl.py

# Process specific games
python etl.py --games 18969,18977,18981,18987

# Dry run (no output)
python etl.py --dry-run

# With validation
python etl.py --validate

# Verbose output
python etl.py --verbose
```

### Configuration

ETL settings in `config/config.ini`:

```ini
[etl]
games = 18969,18977,18981,18987
process_tracking = true
enhance_stats = true
validate = true
```

---

## Adding a New Game

### Step 1: Prepare Raw Data

```bash
# Create game folder
mkdir data/raw/19001

# Add tracking files
# - events_tracking.xlsx (event data)
# - shifts_tracking.xlsx (shift data)
```

### Step 2: Run ETL

```bash
python etl.py --games 19001
```

### Step 3: Validate

```bash
# Run tests
python -m pytest tests/test_data_quality.py -v
```

### Step 4: Load to Supabase

```bash
python scripts/load_all_tables.py --upsert
```

---

## ETL Modules

### Core Modules

| Module | Purpose |
|--------|---------|
| `etl.py` | Orchestrator |
| `src/etl/extract.py` | Read raw files |
| `src/etl/transform.py` | Transform data |
| `src/etl/load.py` | Write CSVs |
| `src/etl/validate.py` | Data validation |

### Transformation Modules

| Module | Purpose |
|--------|---------|
| `src/etl/events.py` | Event processing |
| `src/etl/shifts.py` | Shift processing |
| `src/etl/players.py` | Player stats |
| `src/etl/teams.py` | Team stats |
| `src/etl/enhanced.py` | Advanced stats |

---

## Schema Changes

### Adding a New Column

1. **Update CSV generation** in relevant ETL module:

```python
# In src/etl/events.py
def transform_events(df):
    # Add new column
    df['new_column'] = calculate_new_value(df)
    return df
```

2. **Update schema SQL**:

```sql
-- Add to sql/05_FINAL_COMPLETE_SCHEMA.sql
ALTER TABLE fact_events ADD COLUMN new_column TEXT;
```

3. **Or regenerate schema** from CSV:

```bash
# Update SQL generator to include new column
python scripts/generate_schema.py
```

4. **Run in Supabase**:
```sql
-- Or drop and recreate table
DROP TABLE fact_events CASCADE;
-- Then run CREATE TABLE from schema
```

5. **Reload data**:
```bash
python scripts/load_all_tables.py --table fact_events --upsert
```

### Adding a New Table

1. **Create CSV output** in ETL:

```python
# In relevant module
def generate_new_table(data):
    df = pd.DataFrame(data)
    df.to_csv('data/output/new_table.csv', index=False)
```

2. **Schema is auto-generated** from CSV by loader

3. **Add to schema SQL** if manual control needed

### Renaming/Removing Columns

1. **Update ETL** to output new column names
2. **Run migration SQL**:
```sql
ALTER TABLE fact_events RENAME COLUMN old_name TO new_name;
-- or
ALTER TABLE fact_events DROP COLUMN old_column;
```
3. **Reload data**

---

## Data Quality Validation

### Built-in Validations

| Check | Description |
|-------|-------------|
| Primary key uniqueness | No duplicate PKs |
| Foreign key integrity | All FKs exist in parent |
| Required fields | No nulls where required |
| Data types | Values match expected types |
| Business rules | Goals match official |

### Running Validations

```bash
# All validation tests
python -m pytest tests/test_data_validation.py -v

# Specific checks
python -m pytest tests/test_referential_integrity.py -v
python -m pytest tests/test_business_logic.py -v
```

### Adding Custom Validations

```python
# In tests/test_data_validation.py
def test_new_validation():
    df = pd.read_csv('data/output/fact_events.csv')
    
    # Your validation logic
    assert df['new_column'].notna().all(), "new_column should not be null"
```

---

## Handling Data Issues

### Duplicate Keys

```python
# In ETL, ensure unique keys
df = df.drop_duplicates(subset=['event_key'], keep='first')
```

### Missing Data

```python
# Fill with defaults
df['column'] = df['column'].fillna('default_value')

# Or filter out
df = df[df['column'].notna()]
```

### Invalid Data

```python
# Validate and flag
df['is_valid'] = df.apply(validate_row, axis=1)
invalid = df[~df['is_valid']]
if len(invalid) > 0:
    invalid.to_csv('data/output/qa_invalid_rows.csv')
```

---

## Performance Optimization

### For Large Datasets

```python
# Process in chunks
chunk_size = 10000
for chunk in pd.read_csv(file, chunksize=chunk_size):
    process_chunk(chunk)

# Use efficient types
df['int_col'] = df['int_col'].astype('Int64')  # Nullable int
df['str_col'] = df['str_col'].astype('string')  # String dtype
```

### Memory Management

```python
# Release memory
del large_df
import gc
gc.collect()
```

---

## Future Enhancements

### ML/CV Integration

To add machine learning predictions (xG, etc.):

```python
# 1. Add prediction module
# src/etl/ml_predictions.py

import joblib

def add_xg_predictions(events_df):
    model = joblib.load('models/xg_model.pkl')
    
    features = events_df[['shot_type', 'distance', 'angle', 'is_rebound']]
    events_df['xg'] = model.predict_proba(features)[:, 1]
    
    return events_df

# 2. Call from main ETL
events_df = add_xg_predictions(events_df)
```

### Tracking Data (CV)

For computer vision tracking data:

```python
# New tables for position data
# fact_player_xy_long - player positions over time
# fact_puck_xy_long - puck positions over time

def process_tracking_data(video_id):
    # Load CV output
    positions = load_tracking_csv(f'data/tracking/{video_id}_positions.csv')
    
    # Transform to schema
    player_xy = transform_player_positions(positions)
    puck_xy = transform_puck_positions(positions)
    
    # Output
    player_xy.to_csv('data/output/fact_player_xy_long.csv')
    puck_xy.to_csv('data/output/fact_puck_xy_long.csv')
```

### NHL Data Integration

To incorporate NHL data for comparison:

```python
# 1. Add NHL API client
# src/etl/nhl_api.py

import requests

def fetch_nhl_game(nhl_game_id):
    url = f"https://statsapi.web.nhl.com/api/v1/game/{nhl_game_id}/feed/live"
    response = requests.get(url)
    return response.json()

# 2. Map NHL players to internal IDs
def map_nhl_to_internal(nhl_player_id):
    # Use mapping table
    mapping = pd.read_csv('data/raw/nhl_player_mapping.csv')
    return mapping[mapping['nhl_id'] == nhl_player_id]['player_id'].iloc[0]

# 3. Create comparison tables
# fact_nhl_comparison - side-by-side with NHL averages
```

---

## Monitoring & Alerting

### Log Monitoring

```python
# Check for errors in logs
import glob

def check_recent_errors():
    log_files = glob.glob('logs/**/*.log', recursive=True)
    for log_file in log_files:
        with open(log_file) as f:
            for line in f:
                if 'ERROR' in line:
                    print(f"{log_file}: {line}")
```

### Automated Validation

```python
# Run after every ETL
def post_etl_validation():
    import subprocess
    result = subprocess.run(
        ['python', '-m', 'pytest', 'tests/', '-v', '--tb=short'],
        capture_output=True
    )
    if result.returncode != 0:
        send_alert("ETL validation failed!")
    return result.returncode == 0
```

---

## Troubleshooting

### "File not found"

```bash
# Check file exists
ls data/raw/18969/

# Check file format
file data/raw/18969/events_tracking.xlsx
```

### "Column not found"

```bash
# Check column names in source
python -c "import pandas as pd; print(pd.read_excel('data/raw/18969/events_tracking.xlsx').columns.tolist())"
```

### "Data type error"

```python
# Debug data types
df = pd.read_csv('data/output/fact_events.csv')
print(df.dtypes)
print(df['problematic_column'].unique())
```

### "Memory error"

```bash
# Increase memory limit or process in chunks
python etl.py --chunk-size 5000
```

---

## Maintenance Checklist

### Daily
- [ ] Check log files for errors
- [ ] Verify new games processed correctly

### Weekly
- [ ] Run full validation suite
- [ ] Check data quality metrics
- [ ] Review any flagged issues

### Monthly
- [ ] Backup database
- [ ] Clean old log files
- [ ] Review and update documentation
- [ ] Check for dependency updates

### Quarterly
- [ ] Performance review
- [ ] Schema optimization
- [ ] Review and archive old data
- [ ] Plan enhancements

---

## Resources

- ETL Code: `etl.py` and `src/etl/`
- Tests: `tests/`
- Logs: `logs/`
- Config: `config/`
- Raw Data: `data/raw/`
- Output: `data/output/`
