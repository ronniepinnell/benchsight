# BenchSight Supabase Deployment Guide

## Quick Summary

You have 96 CSV files in `data/output/`. These need to be:
1. Tables created in Supabase (via SQL)
2. Data loaded (via `flexible_loader.py`)

---

## Step 1: Prerequisites

```bash
# Install Python dependencies
pip install supabase pandas

# Verify you have the files
ls data/output/*.csv | wc -l  # Should show 96
```

---

## Step 2: Configure Supabase Credentials

```bash
# Copy the example config
cp config/config_local.ini.example config/config_local.ini
```

Edit `config/config_local.ini`:
```ini
[supabase]
url = https://YOUR_PROJECT_ID.supabase.co
service_key = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...YOUR_SERVICE_ROLE_KEY

[etl]
batch_size = 500
data_dir = data/output
```

**IMPORTANT:** Use the `service_role` key, NOT the `anon` key!
- Find it in Supabase Dashboard → Settings → API → Service Role Key

---

## Step 3: Create Tables in Supabase

Go to Supabase Dashboard → SQL Editor → New Query

**Run in order:**

### 3a. Create all 98 tables
Copy and run: `sql/01_CREATE_ALL_TABLES.sql`

### 3b. Fix column types (important!)
Copy and run: `sql/02_TYPE_FIXES.sql`

This fixes columns like:
- `period_number`: INTEGER → TEXT (has "OT", "SO")
- `player_game_number`: INTEGER → TEXT (has "FA")
- `norad_experience`: INTEGER → TEXT (has "10+")

---

## Step 4: Load Data

### Load ALL 98 tables (recommended first time)
```bash
python scripts/flexible_loader.py --scope full --operation replace
```

### Or load by category
```bash
# Dimensions first
python scripts/flexible_loader.py --scope category --category dims --operation replace

# Then facts
python scripts/flexible_loader.py --scope category --category all_facts --operation replace

# Then QA
python scripts/flexible_loader.py --scope category --category qa --operation replace
```

### Or load a single table
```bash
python scripts/flexible_loader.py --scope table --table dim_player --operation replace
python scripts/flexible_loader.py --scope table --table fact_player_game_stats --operation replace
```

---

## Step 5: Verify Deployment

### Check row counts
```bash
python scripts/flexible_loader.py --counts
```

### Expected counts (sample)
| Table | Rows |
|-------|------|
| dim_player | 337 |
| dim_team | 26 |
| dim_schedule | 562 |
| fact_events | 5,833 |
| fact_shifts | 672 |
| fact_player_game_stats | 107 |

---

## Troubleshooting

### "403 Forbidden"
- You're using `anon` key instead of `service_role` key
- Fix: Use service_role key in config_local.ini

### "Column does not exist"
- Table schema doesn't match CSV
- Fix: Run `sql/02_TYPE_FIXES.sql`
- Or check if table was created with wrong columns

### "Duplicate key value violates unique constraint"
- Data already exists
- Fix: Use `--operation replace` (truncates first)

### "Table doesn't exist"
- Table not created yet
- Fix: Run `sql/01_CREATE_ALL_TABLES.sql` in Supabase SQL Editor

### Missing tables in Supabase
```bash
# List all tables that should exist
python scripts/flexible_loader.py --dry-run --scope full

# Load specific missing table
python scripts/flexible_loader.py --scope table --table YOUR_TABLE --operation replace
```

---

## Categories Reference

| Category | Tables | Description |
|----------|--------|-------------|
| `dims` | 44 | Dimension/lookup tables |
| `core_facts` | 11 | Core event/shift tables |
| `stats_facts` | 11 | Player/team statistics |
| `analytics_facts` | 9 | H2H, WOWY, line combos |
| `zone_facts` | 7 | Zone/danger analysis |
| `tracking_facts` | 5 | XY coordinate data |
| `other_facts` | 8 | Video, draft, registration |
| `qa` | 1 | Quality assurance |
| `all_facts` | 51 | All fact tables |
| `all` | 96 | Everything |

---

## Operation Modes

| Mode | Behavior |
|------|----------|
| `replace` | TRUNCATE table, then INSERT (clean slate) |
| `append` | INSERT only (add to existing) |
| `upsert` | INSERT or UPDATE on conflict |

**Recommended:** Use `replace` for initial load and full refreshes.

---

## Full Reload Procedure

```bash
# 1. Truncate all data (optional - replace does this)
# Run sql/03_TRUNCATE_DATA.sql in Supabase

# 2. Load everything fresh
python scripts/flexible_loader.py --scope full --operation replace

# 3. Verify
python scripts/flexible_loader.py --counts
```

---

## Convenience Scripts

### `run_deploy.sh` - Deploy to Supabase
```bash
# Deploy all tables
./run_deploy.sh

# With custom options
./run_deploy.sh --scope table --table dim_player --operation replace

# Check counts
./run_deploy.sh --counts
```

### `run_etl.sh` - Run ETL Pipeline
```bash
# Process single game
./run_etl.sh --game 18969

# Process multiple games
./run_etl.sh --games 18969,18977,18981

# Export to CSV
./run_etl.sh --export

# Show status
./run_etl.sh --status

# List available games
./run_etl.sh --list-games
```

---

## Common Workflows

### Initial Setup
```bash
# 1. Configure credentials
cp config/config_local.ini.example config/config_local.ini
# Edit with your Supabase URL and service_role key

# 2. Create tables in Supabase SQL Editor
# Run: sql/01_CREATE_ALL_TABLES.sql
# Run: sql/02_TYPE_FIXES.sql

# 3. Deploy all data
./run_deploy.sh

# 4. Verify
./run_deploy.sh --counts
```

### Add New Game
```bash
# 1. Place tracking file in data/raw/games/{game_id}/
# 2. Run ETL
./run_etl.sh --game {game_id}

# 3. Re-deploy affected tables
./run_deploy.sh --scope category --category all_facts --operation replace
```

### Full Refresh
```bash
# Regenerate all CSVs
./run_etl.sh --process-all --export

# Reload all data to Supabase
./run_deploy.sh
```

---

## Complete Table List (96 Tables)

### Load Missing Tables

If you have missing tables in Supabase:

```bash
# First create the table in Supabase SQL Editor using sql/01_CREATE_ALL_TABLES.sql
# Find the CREATE TABLE statement for your missing table and run it

# Then load the data:
python scripts/flexible_loader.py --scope table --table TABLE_NAME --operation replace
```

### All 44 Dimension Tables
```
dim_comparison_type, dim_composite_rating, dim_danger_zone, dim_event_detail,
dim_event_detail_2, dim_event_type, dim_giveaway_type, dim_league,
dim_micro_stat, dim_net_location, dim_pass_type, dim_period,
dim_play_detail, dim_play_detail_2, dim_player, dim_player_role,
dim_playerurlref, dim_position, dim_randomnames, dim_rink_coord,
dim_rinkboxcoord, dim_rinkcoordzones, dim_schedule, dim_season,
dim_shift_slot, dim_shift_start_type, dim_shift_stop_type, dim_shot_type,
dim_situation, dim_stat, dim_stat_category, dim_stat_type,
dim_stoppage_type, dim_strength, dim_success, dim_takeaway_type,
dim_team, dim_terminology_mapping, dim_turnover_quality, dim_turnover_type,
dim_venue, dim_zone, dim_zone_entry_type, dim_zone_exit_type
```

### All 51 Fact Tables
```
fact_cycle_events, fact_draft, fact_event_chains, fact_events,
fact_events_long, fact_events_player, fact_events_tracking, fact_game_status,
fact_gameroster, fact_goalie_game_stats, fact_h2h, fact_head_to_head,
fact_leadership, fact_league_leaders_snapshot, fact_line_combos, fact_linked_events,
fact_matchup_summary, fact_player_boxscore_all, fact_player_event_chains,
fact_player_game_position, fact_player_game_stats, fact_player_micro_stats,
fact_player_pair_stats, fact_player_period_stats, fact_player_stats_long,
fact_player_xy_long, fact_player_xy_wide, fact_playergames, fact_plays,
fact_possession_time, fact_puck_xy_long, fact_puck_xy_wide, fact_registration,
fact_rush_events, fact_scoring_chances, fact_sequences, fact_shift_players,
fact_shift_quality, fact_shift_quality_logical, fact_shifts, fact_shifts_long,
fact_shifts_player, fact_shifts_tracking, fact_shot_danger, fact_shot_xy,
fact_suspicious_stats, fact_team_game_stats, fact_team_standings_snapshot,
fact_team_zone_time, fact_video, fact_wowy
```

### 1 QA Table
```
qa_suspicious_stats
```
