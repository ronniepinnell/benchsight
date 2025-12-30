# Guide: Adding Rows to Dimension Tables

## Overview

Dimension tables in BenchSight are sourced from:
1. **BLB_Tables.xlsx** - Master dimensional data (players, teams, positions, etc.)
2. **Auto-generated** - Derived from fact data (like new strength values)
3. **Manual addition** - For new reference values

## Method 1: Update BLB_Tables.xlsx (Recommended)

Most dimension data comes from `data/BLB_Tables.xlsx`. To add new rows:

1. **Open BLB_Tables.xlsx**
2. **Find the relevant sheet** (e.g., `dim_player`, `dim_team`)
3. **Add new row(s)** with required columns
4. **Run ETL** to regenerate dim tables:
   ```bash
   python -m src.etl_orchestrator --tables dims
   ```

### Required Columns by Table

| Table | Required Columns |
|-------|-----------------|
| dim_player | player_id, player_full_name, player_first_name, player_last_name |
| dim_team | team_id, team_name, league_id |
| dim_strength | strength_id, strength_code, strength_name |
| dim_event_type | event_type_id, event_type_code, event_type_name |

## Method 2: Auto-Generation from Facts

Some dim values are auto-generated when new values appear in fact data:

```python
# Example: dim_strength auto-updates with new strength values
# In src/comprehensive_fixes.py

def update_dim_strength():
    shifts = pd.read_csv('data/output/fact_shifts_player.csv')
    strength = pd.read_csv('data/output/dim_strength.csv')
    
    # Find new values not in dim
    new_values = set(shifts['strength']) - set(strength['strength_code'])
    
    # Add new rows
    for val in new_values:
        strength = strength.append({
            'strength_id': f'STR{len(strength)+1:04d}',
            'strength_code': val,
            'strength_name': val,
        }, ignore_index=True)
    
    strength.to_csv('data/output/dim_strength.csv', index=False)
```

## Method 3: Direct CSV Edit

For quick additions, directly edit the CSV:

```python
import pandas as pd

# Load dim table
dim = pd.read_csv('data/output/dim_player.csv')

# Add new row
new_player = {
    'player_id': 'P999999',
    'player_full_name': 'New Player',
    'player_first_name': 'New',
    'player_last_name': 'Player',
}
dim = dim.append(new_player, ignore_index=True)

# Save
dim.to_csv('data/output/dim_player.csv', index=False)
```

## Key Generation

All dim tables use standard key formats:

| Table | Key Format | Example |
|-------|------------|---------|
| dim_player | P{6 digits} | P100117 |
| dim_team | T{4 digits} | T1001 |
| dim_strength | STR{4 digits} | STR0001 |
| dim_event_type | EVT{4 digits} | EVT0001 |

## Validation After Adding

After adding dim rows, validate FK integrity:

```python
# Check all facts reference valid dims
facts = pd.read_csv('data/output/fact_events_player.csv')
dims = pd.read_csv('data/output/dim_player.csv')

orphans = facts[~facts['player_id'].isin(dims['player_id'])]
if len(orphans) > 0:
    print(f"Warning: {len(orphans)} events have invalid player_id")
```

## Upload to Supabase

After adding dim rows locally, upload to Supabase:

```python
# Using etl_upload.py
python -m src.etl_upload --table dim_player --mode upsert
```
