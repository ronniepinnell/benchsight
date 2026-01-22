# ETL Data Flow

**Detailed data flow documentation for the BenchSight ETL pipeline.**

Last Updated: 2026-01-22

---

## Overview

This document describes how data flows through the ETL pipeline, from raw input files to final output tables.

---

## Input Data Sources

### 1. BLB Tables (Excel)

**Location:** `data/raw/BLB_Tables.xlsx`

**Sheets:**
- `dim_player` - Player master data
- `dim_team` - Team master data
- `dim_league` - League master data
- `dim_season` - Season master data
- `dim_schedule` - Game schedule

**Used In:** Phase 1

### 2. Game Tracking Data (Excel/JSON)

**Location:** `data/raw/games/{game_id}/`

**Files:**
- `{game_id}_tracking.xlsx` - Event and shift tracking data
- `{game_id}_events.json` - Event data (alternative format)
- `{game_id}_shifts.json` - Shift data (alternative format)

**Used In:** Phase 1

---

## Data Flow by Phase

### Phase 1: Data Loading

```
BLB_Tables.xlsx
    ↓
[Load BLB Tables]
    ↓
dim_player (staging)
dim_team (staging)
dim_league (staging)
dim_season (staging)
dim_schedule (staging)
    ↓
[Build Player Lookup]
    ↓
player_lookup (in-memory)
    ↓
{game_id}_tracking.xlsx
    ↓
[Load Tracking Data]
    ↓
raw_events (DataFrame)
raw_shifts (DataFrame)
    ↓
[Build Fact Tables]
    ↓
fact_events.csv
fact_event_players.csv
fact_shifts.csv
fact_shift_players.csv
```

### Phase 3B: Dimension Tables

```
fact_events (from Phase 1)
    ↓
[Extract Unique Values]
    ↓
dim_player.csv (final)
dim_team.csv (final)
dim_schedule.csv (final)
    ↓
[Create Static Dimensions]
    ↓
dim_zone.csv
dim_period.csv
dim_venue.csv
... (50+ dimension tables)
```

### Phase 4: Core Stats

```
fact_events.csv
fact_event_players.csv
fact_shifts.csv
    ↓
[Group by player_id, game_id]
    ↓
[Calculate Stats]
    ↓
fact_player_game_stats.csv
    ↓
[Group by team_id, game_id]
    ↓
fact_team_game_stats.csv
```

### Phase 5: Foreign Keys

```
All tables from Phases 1-4
    ↓
[Add Foreign Key Columns]
    ↓
[Update Tables]
    ↓
All tables (with FK columns added)
```

---

## Key Data Transformations

### Event Data Transformation

```
Raw Event (Excel/JSON)
    ↓
Normalize columns
    ↓
Add derived columns (time, zone, etc.)
    ↓
Generate event_id key
    ↓
fact_events row
```

### Player Stats Aggregation

```
fact_events (filtered by player_id)
    ↓
Group by game_id
    ↓
Aggregate:
  - goals (count where event_type='Goal' AND event_detail='Goal_Scored')
  - assists (count where play_details contains 'Assist')
  - shots (count where event_type='Shot')
  - ...
    ↓
fact_player_game_stats row
```

### Foreign Key Resolution

```
fact_events.player_id
    ↓
Lookup in dim_player
    ↓
Add dim_player.player_key
    ↓
fact_events (with FK column)
```

---

## Data Quality Checks

### Phase 1 Checks
- All required columns present
- No duplicate event_ids
- Valid game_ids
- Valid player_ids

### Phase 3B Checks
- No duplicate dimension keys
- All required dimension values present

### Phase 4 Checks
- Stats match source event counts
- No negative values
- Valid aggregations

### Phase 5 Checks
- All foreign keys resolve
- No orphaned records

---

## Output Data Structure

### Dimension Tables
- **Format:** CSV
- **Location:** `data/output/dim_*.csv`
- **Key Column:** `{table_name}_id` or `{table_name}_key`
- **Purpose:** Reference data for foreign keys

### Fact Tables
- **Format:** CSV
- **Location:** `data/output/fact_*.csv`
- **Key Column:** `{table_name}_key` (composite keys)
- **Purpose:** Transactional/analytical data

### QA Tables
- **Format:** CSV
- **Location:** `data/output/qa_*.csv`
- **Purpose:** Quality assurance and validation

---

## Data Volume

**Typical Game:**
- Events: ~500-800 per game
- Shifts: ~200-300 per game
- Event Players: ~1500-2500 per game
- Shift Players: ~1000-1500 per game

**4 Games:**
- Total Events: ~2000-3200
- Total Shifts: ~800-1200
- Output Tables: 139
- Total Rows: ~500,000+

---

## Related Documentation

- [ETL Phase Flow](ETL_PHASE_FLOW.md) - Phase-by-phase flow
- [Core Modules](CORE_MODULES.md) - Implementation details
- [Code Walkthrough](CODE_WALKTHROUGH.md) - Step-by-step guide
