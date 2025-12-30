# BenchSight Database Schema

**Version:** 2.0  
**Date:** December 30, 2025  
**Tables:** 96  
**Total Columns:** ~1,900

---

## Schema Design: Star Schema

```
                    ┌─────────────────┐
                    │   DIMENSIONS    │
                    │   (44 tables)   │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│  dim_player   │  │   dim_team    │  │ dim_schedule  │
│  (337 rows)   │  │   (26 rows)   │  │  (562 rows)   │
└───────────────┘  └───────────────┘  └───────────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                    ┌────────┴────────┐
                    │     FACTS       │
                    │   (51 tables)   │
                    └─────────────────┘
```

---

## Table Categories

### Dimension Tables (44)
Reference/lookup data that rarely changes.

| Table | Rows | Description |
|-------|------|-------------|
| dim_player | 337 | Player information |
| dim_team | 26 | Team information |
| dim_schedule | 562 | Game schedule |
| dim_season | 9 | Season definitions |
| dim_event_type | ~15 | Event type lookups |
| dim_event_detail | ~30 | Event detail lookups |
| dim_play_detail | ~10 | Play context |
| dim_zone | 3 | Zone definitions |
| dim_period | 5 | Period definitions |
| dim_situation | ~6 | Game situations |
| dim_strength | ~10 | Strength states |
| ... | ... | 33 more dimension tables |

### Fact Tables (51)
Metrics, events, and analytical data.

| Table | Rows | Description |
|-------|------|-------------|
| fact_events | 5,833 | All game events |
| fact_events_player | 11,635 | Player involvement in events |
| fact_shifts | 672 | All shifts |
| fact_shifts_player | 4,626 | Players on shifts |
| fact_player_game_stats | 107 | Per-game player stats |
| fact_team_game_stats | 8 | Per-game team stats |
| fact_goalie_game_stats | 8 | Goalie stats |
| fact_h2h | 684 | Head-to-head matchups |
| fact_wowy | 641 | With/Without analysis |
| fact_line_combos | 332 | Line combinations |
| fact_sequences | 1,088 | Possession sequences |
| fact_plays | 2,714 | Plays within sequences |
| fact_player_boxscore_all | 14,473 | Complete boxscores |
| ... | ... | 38 more fact tables |

### Logging Tables (5)
ETL and system logs.

| Table | Description |
|-------|-------------|
| log_etl_runs | ETL run tracking |
| log_etl_tables | Per-table load details |
| log_errors | Error tracking |
| log_data_changes | Audit trail |
| log_test_results | Test results |

---

## Key Relationships

### Primary Keys

| Table | Primary Key | Format |
|-------|-------------|--------|
| dim_player | player_id | P001, P002... |
| dim_team | team_id | T001, T002... |
| dim_schedule | game_id | 18969, 18977... |
| fact_events | event_key | EV1896900001 |
| fact_shifts | shift_key | 18969_1 |
| fact_events_player | event_player_key | EV1896900001_1 |
| fact_shifts_player | shift_player_key | 18969_1_P001 |
| fact_player_game_stats | player_game_key | 18969_P001 |

### Foreign Key Relationships

```
dim_player (player_id)
    ├── fact_events_player.player_id
    ├── fact_shifts_player.player_id
    ├── fact_player_game_stats.player_id
    ├── fact_h2h.player_id
    └── fact_wowy.player_id

dim_team (team_id)
    ├── dim_schedule.home_team_id
    ├── dim_schedule.away_team_id
    ├── fact_events.home_team_id
    └── fact_team_game_stats.team_id

dim_schedule (game_id)
    ├── fact_events.game_id
    ├── fact_shifts.game_id
    └── fact_player_game_stats.game_id

fact_shifts (shift_key)
    └── fact_events.shift_key

fact_events (event_key)
    └── fact_events_player.event_key
```

---

## Core Table Schemas

### dim_player (28 columns)
```sql
player_id TEXT PRIMARY KEY,
player_first_name TEXT,
player_last_name TEXT,
player_full_name TEXT,
player_primary_position TEXT,
current_skill_rating INTEGER,
player_hand TEXT,
birth_year INTEGER,
player_gender TEXT,
-- ... more columns
```

### dim_team (15 columns)
```sql
team_id TEXT PRIMARY KEY,
team_name TEXT,
long_team_name TEXT,
team_cd TEXT,
team_color1 TEXT,
team_color2 TEXT,
team_logo TEXT,
team_url TEXT,
-- ... more columns
```

### dim_schedule (44 columns)
```sql
game_id TEXT PRIMARY KEY,
season INTEGER,
date DATE,
game_time TEXT,
home_team_name TEXT,
away_team_name TEXT,
home_team_id TEXT,
away_team_id TEXT,
home_total_goals INTEGER,
away_total_goals INTEGER,
video_url TEXT,
video_start_time DECIMAL,
-- ... more columns
```

### fact_events (54 columns)
```sql
event_key TEXT PRIMARY KEY,
game_id TEXT,
shift_key TEXT,
"period" DECIMAL,
event_index DECIMAL,
event_type TEXT,
event_detail TEXT,
event_successful TEXT,
"Type" TEXT,
running_video_time DECIMAL,
time_start_total_seconds DECIMAL,
-- ... more columns
```

### fact_shifts (63 columns)
```sql
shift_key TEXT PRIMARY KEY,
game_id TEXT,
shift_index INTEGER,
"Period" DECIMAL,
shift_duration DECIMAL,
strength TEXT,
situation TEXT,
home_forward_1 DECIMAL,
home_forward_2 DECIMAL,
-- ... more columns (player numbers, stats)
```

### fact_player_game_stats (317 columns)
```sql
player_game_key TEXT PRIMARY KEY,
game_id TEXT,
player_id TEXT,
goals INTEGER,
assists INTEGER,
points INTEGER,
shots INTEGER,
toi_minutes DECIMAL,
-- ... 309 more stat columns
```

---

## Naming Conventions

### Tables
- `dim_*` - Dimension tables
- `fact_*` - Fact tables
- `log_*` - Logging tables
- `v_*` - Views
- `staging_*` - Staging tables

### Columns
- `*_id` - Foreign key or identifier
- `*_key` - Primary key (composite)
- `*_name` - Display name
- `*_at` - Timestamp
- `*_url` - URL/link
- `is_*` - Boolean flag

### IDs
- Player IDs: P001, P002...
- Team IDs: T001, T002...
- Event Type IDs: EVT001, EVT002...
- Period IDs: P1, P2, P3, OT, SO

---

## SQL Files

| File | Purpose |
|------|---------|
| 05_FINAL_COMPLETE_SCHEMA.sql | Create all 96 tables |
| 02_CREATE_LOGGING_TABLES.sql | Create logging tables |
| 06_TRUNCATE_ALL_DATA.sql | Clear all data |

---

## Views

| View | Purpose |
|------|---------|
| v_recent_runs | Last 50 ETL runs |
| v_daily_run_stats | Daily statistics |
| v_table_load_stats | Per-table metrics |
| v_unresolved_errors | Open errors |
| v_test_pass_rate | Test results |
| v_recent_changes | Recent data changes |

---

## Functions

| Function | Purpose |
|----------|---------|
| get_all_table_counts() | Row counts for all tables |
| get_run_summary(run_id) | Full run summary |
| cleanup_old_logs(days) | Delete old logs |
| resolve_error(id, user, notes) | Mark error resolved |
| truncate_all_facts() | Clear fact tables |

