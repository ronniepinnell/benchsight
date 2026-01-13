# Supabase Update Instructions for v28.1

## Overview

v28.1 expands `fact_goalie_game_stats` from 39 to 128 columns. This requires schema changes in Supabase.

---

## Option 1: Drop and Recreate (Recommended for Development)

```sql
-- 1. Drop the existing table
DROP TABLE IF EXISTS fact_goalie_game_stats CASCADE;

-- 2. The table will be auto-created on next upload
-- Run upload.py to recreate with new schema
```

Then run:
```bash
python upload.py --table fact_goalie_game_stats
```

---

## Option 2: ALTER TABLE (Preserve Existing Data)

### Step 1: Generate ALTER statements
Run this Python script to generate SQL for new columns:

```python
import pandas as pd

# Load the new CSV
df = pd.read_csv('data/output/fact_goalie_game_stats.csv')

# Get column types
type_map = {
    'int64': 'INTEGER',
    'float64': 'DOUBLE PRECISION',
    'object': 'TEXT',
    'bool': 'BOOLEAN'
}

# Generate ALTER statements for new columns
new_columns = [
    'freeze_pct', 'rebound_rate', 'rebounds_team_recovered', 'rebounds_opp_recovered',
    'rebounds_shot_generated', 'rebounds_flurry_generated', 'rebound_control_rate',
    'rebound_danger_rate', 'second_chance_shots_against', 'second_chance_goals_against',
    'second_chance_sv_pct', 'dangerous_rebound_pct', 'p1_saves', 'p1_goals_against',
    'p1_shots_against', 'p1_sv_pct', 'p2_saves', 'p2_goals_against', 'p2_shots_against',
    'p2_sv_pct', 'p3_saves', 'p3_goals_against', 'p3_shots_against', 'p3_sv_pct',
    'best_period', 'worst_period', 'period_consistency', 'early_period_saves',
    'mid_period_saves', 'late_period_saves', 'final_minute_saves', 'early_period_ga',
    'mid_period_ga', 'late_period_ga', 'final_minute_ga', 'early_period_sv_pct',
    'mid_period_sv_pct', 'late_period_sv_pct', 'final_minute_sv_pct', 'rush_saves',
    'quick_attack_saves', 'set_play_saves', 'avg_time_from_entry', 'rush_goals_against',
    'quick_attack_ga', 'set_play_ga', 'rush_sv_pct', 'quick_attack_sv_pct',
    'set_play_sv_pct', 'rush_pct_of_shots', 'transition_defense_rating',
    'single_shot_saves', 'multi_shot_saves', 'sustained_pressure_saves',
    'max_sequence_faced', 'avg_sequence_length', 'multi_shot_sv_pct',
    'sustained_pressure_sv_pct', 'sequence_survival_rate', 'pressure_handling_index',
    'glove_side_saves', 'blocker_side_saves', 'five_hole_saves', 'glove_side_ga',
    'blocker_side_ga', 'five_hole_ga', 'glove_side_sv_pct', 'blocker_side_sv_pct',
    'five_hole_sv_pct', 'side_preference_ratio', 'shots_per_period', 'saves_per_period',
    'max_shots_in_period', 'shot_volume_variance', 'time_between_shots_avg',
    'time_between_shots_min', 'rapid_fire_saves', 'consecutive_saves_max',
    'workload_index', 'fatigue_adjusted_gsaa', 'goalie_game_score', 'goalie_gax',
    'goalie_gsax', 'clutch_rating', 'consistency_rating', 'pressure_rating',
    'rebound_rating', 'positioning_rating', 'overall_game_rating', 'win_probability_added'
]

for col in new_columns:
    dtype = str(df[col].dtype)
    sql_type = type_map.get(dtype, 'TEXT')
    print(f"ALTER TABLE fact_goalie_game_stats ADD COLUMN IF NOT EXISTS {col} {sql_type};")
```

### Step 2: Run the ALTER statements in Supabase SQL Editor

### Step 3: Truncate and reload data
```sql
TRUNCATE TABLE fact_goalie_game_stats;
```

Then run:
```bash
python upload.py --table fact_goalie_game_stats
```

---

## Option 3: Full Database Refresh

If you want to refresh all tables:

```bash
# 1. Run fresh ETL (already done)
python run_etl.py

# 2. Upload all tables
python upload.py

# OR upload specific tables
python upload.py --table fact_goalie_game_stats
python upload.py --table fact_player_game_stats
# etc.
```

---

## Upload Commands

```bash
# Single table
python upload.py --table fact_goalie_game_stats

# Multiple tables
python upload.py --table fact_goalie_game_stats --table fact_player_game_stats

# All tables (caution: slow)
python upload.py

# Dry run (see what would be uploaded)
python upload.py --table fact_goalie_game_stats --dry-run
```

---

## Verify Upload

After uploading, verify in Supabase:

```sql
-- Check column count
SELECT COUNT(*) 
FROM information_schema.columns 
WHERE table_name = 'fact_goalie_game_stats';
-- Should return 128

-- Check row count
SELECT COUNT(*) FROM fact_goalie_game_stats;
-- Should return 8

-- Sample data
SELECT player_name, saves, goals_against, save_pct, rush_sv_pct, clutch_rating, overall_game_rating
FROM fact_goalie_game_stats
ORDER BY overall_game_rating DESC;
```
