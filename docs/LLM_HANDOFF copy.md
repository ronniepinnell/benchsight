# BENCHSIGHT LLM HANDOFF DOCUMENT

**Version:** 2.0.0  
**Date:** December 27, 2025  
**Status:** Supabase Integration Ready

---

## QUICK START FOR NEW LLM SESSION

1. Read this document first
2. Check `/docs/DATA_DICTIONARY_COMPLETE.md` for table schemas
3. Check `/docs/SCHEMA_DIAGRAMS.md` for visual diagrams
4. Supabase schema is in `/sql/supabase_schema_complete.sql`

---

## PROJECT OVERVIEW

**BenchSight** is a beer league hockey analytics platform with:
- ETL pipeline (Python) to process game data
- Supabase PostgreSQL database (36 tables)
- Tracker UI (HTML) for live game tracking
- Dashboards (HTML) for visualization
- Power BI integration planned

---

## ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                              │
├─────────────────────────────────────────────────────────────────┤
│  BLB_Tables.xlsx    │  *_tracking.xlsx  │  *_video_times.xlsx   │
│  (master data)      │  (game events)    │  (video links)        │
└─────────┬───────────┴────────┬──────────┴──────────┬────────────┘
          │                    │                     │
          ▼                    ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                     PYTHON ETL PIPELINE                          │
├─────────────────────────────────────────────────────────────────┤
│  src/combine_tracking.py  - Combines all game tracking files     │
│  src/export_all_data.py   - Exports CSVs from Excel              │
│  src/roster_loader.py     - Loads rosters per game               │
│  src/supabase_upload.py   - Uploads CSVs to Supabase             │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SUPABASE POSTGRESQL                           │
├─────────────────────────────────────────────────────────────────┤
│  36 Tables (see DATA_DICTIONARY_COMPLETE.md)                     │
│  - 8 Core Dimensions                                             │
│  - 16 Lookup Dimensions                                          │
│  - 12 Fact Tables                                                │
│                                                                  │
│  URL: https://uuaowslhpgyiudmbvqze.supabase.co                  │
└────────────┬─────────────────────────────┬──────────────────────┘
             │                             │
             ▼                             ▼
┌────────────────────────┐    ┌───────────────────────────────────┐
│     TRACKER UI         │    │         DASHBOARDS                │
├────────────────────────┤    ├───────────────────────────────────┤
│  tracker.html          │    │  dashboard_static.html            │
│  - Read/write to DB    │    │  games_browser.html               │
│  - XY coordinate input │    │  - Read from DB                   │
│  - Auto-save/backup    │    │  - Visualize stats                │
└────────────────────────┘    └───────────────────────────────────┘
             │                             │
             ▼                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      POWER BI (PLANNED)                          │
├─────────────────────────────────────────────────────────────────┤
│  Direct PostgreSQL connection to Supabase                        │
│  DAX date table generation                                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## DATABASE SCHEMA (36 TABLES)

### Core Dimensions (8)
| Table | Rows | Primary Key | Description |
|-------|------|-------------|-------------|
| dim_player | 335 | player_id | Player master |
| dim_team | 26 | team_id | Team master |
| dim_schedule | 552 | game_id | All games |
| dim_season | 9 | season_id | Seasons |
| dim_league | 2 | league_id | Leagues |
| dim_rinkboxcoord | 50 | box_id | Rink boxes |
| dim_rinkcoordzones | 297 | id | Rink zones |
| dim_video | 10 | id | Video links |

### Lookup Dimensions (16)
| Table | Rows | Description |
|-------|------|-------------|
| dim_event_type | 7 | Shot, Pass, etc. |
| dim_event_detail | 59 | Event subtypes |
| dim_play_detail | 81 | Play details |
| dim_strength | 9 | 5v5, 5v4, etc. |
| dim_situation | 5 | PP/PK/EN |
| dim_position | 9 | C, LW, RW, F, D, LD, RD, G, X |
| dim_zone | 3 | OZ, NZ, DZ |
| dim_period | 5 | 1, 2, 3, OT, SO |
| dim_venue | 2 | Home, Away |
| dim_shot_type | 6 | Wrist, Slap, etc. |
| dim_pass_type | 8 | Pass types |
| dim_shift_type | 6 | Start/stop types |
| dim_skill_tier | 5 | Skill tiers |
| dim_player_role | 7 | Player roles |
| dim_danger_zone | 3 | High/Med/Low danger |
| dim_time_bucket | 4 | Time periods |

### Fact Tables (12)
| Table | Rows | Format | Description |
|-------|------|--------|-------------|
| fact_gameroster | 14,239 | - | Players per game |
| fact_events_tracking | 24,089 | Wide | Events (1 row per event) |
| fact_events_long | 24,090 | Long | Events (1 row per player-event) |
| fact_event_players_tracking | 3,133 | Junction | Player-event links |
| fact_shifts_tracking | 770 | Wide | Shifts (1 row per shift) |
| fact_shift_players_tracking | 1,137 | Long | Player-shift links |
| fact_playergames | 3,010 | - | Player game stats |
| fact_box_score_tracking | 27 | - | Detailed box scores |
| fact_linked_events_tracking | 230 | - | Event chains |
| fact_sequences_tracking | 5 | - | Sequences |
| fact_plays_tracking | 5 | - | Plays |
| fact_event_coordinates | 0 | - | XY tracking (from tracker) |

---

## FILE STRUCTURE

```
benchsight/
├── data/
│   ├── BLB_Tables.xlsx           # Master data (3.8MB)
│   ├── raw/
│   │   └── games/                # Raw tracking files
│   │       ├── 18965/
│   │       ├── 18969/
│   │       └── ...
│   └── output/                   # 36 CSV files
│       ├── dim_player.csv
│       ├── dim_team.csv
│       ├── fact_events_tracking.csv
│       └── ...
├── docs/
│   ├── DATA_DICTIONARY_COMPLETE.md
│   ├── SCHEMA_DIAGRAMS.md
│   ├── LLM_HANDOFF.md (this file)
│   └── CHANGELOG.md
├── html/
│   ├── tracker.html
│   ├── dashboard_static.html
│   └── games_browser.html
├── sql/
│   └── supabase_schema_complete.sql
├── src/
│   ├── combine_tracking.py
│   ├── export_all_data.py
│   ├── roster_loader.py
│   └── supabase_upload.py
├── QUICKSTART.md
├── PROJECT_STATUS.md
└── README.md
```

---

## SUPABASE CONNECTION

```python
SUPABASE_URL = "https://uuaowslhpgyiudmbvqze.supabase.co"
SUPABASE_KEY = "sb_publishable_t1lIOebbbCjAu_YBKc8tLg_B_zH_l73"
```

```javascript
// JavaScript
const supabase = createClient(
  'https://uuaowslhpgyiudmbvqze.supabase.co',
  'sb_publishable_t1lIOebbbCjAu_YBKc8tLg_B_zH_l73'
);
```

---

## TRACKER UI REQUIREMENTS

The tracker must:
1. **Read** roster from `fact_gameroster` for selected game
2. **Read** existing events from `fact_events_tracking` to continue tracking
3. **Read** existing shifts from `fact_shifts_tracking` to continue tracking
4. **Write** new events to `fact_events_tracking`
5. **Write** new shifts to `fact_shifts_tracking`
6. **Write** XY coordinates to `fact_event_coordinates`
7. **Auto-save** to localStorage every 30 seconds
8. **Export** Excel matching fact table schemas exactly
9. **Backup** JSON files for recovery

### Tracker Output Schema

Events must match `fact_events_tracking` columns exactly:
- game_id, event_index, shift_index, period, type, event_detail, event_detail_2
- event_successful, event_team_zone, team_venue, player_game_number
- time_start_total_seconds, time_end_total_seconds

Shifts must match `fact_shifts_tracking` columns exactly:
- game_id, shift_index, period, shift_start_total_seconds, shift_end_total_seconds
- strength, situation, home_forward_1..3, home_defense_1..2, home_goalie, home_xtra
- away_forward_1..3, away_defense_1..2, away_goalie, away_xtra

Coordinates use `fact_event_coordinates`:
- event_id, game_id, entity_type (event_player/opp_player/puck)
- entity_slot (1-6), sequence (variable), x (0-200), y (0-85)

---

## ETL COMMANDS

```bash
# Combine all tracking files
python src/combine_tracking.py

# Upload to Supabase
python src/supabase_upload.py

# Full pipeline
python src/orchestrator.py
```

---

## GAMES WITH TRACKING DATA

| Game ID | Events | Shifts | Video |
|---------|--------|--------|-------|
| 18965 | 3,999 | 98 | Yes |
| 18969 | 3,596 | 98 | Yes |
| 18977 | 2,527 | 88 | Yes |
| 18981 | 2,428 | 106 | Yes |
| 18987 | 3,084 | 106 | Yes |
| 18991 | 4,000 | 78 | Yes |
| 18993 | 456 | 98 | No |
| 19032 | 3,999 | 98 | Yes |

---

## KNOWN ISSUES / TODO

1. **Tracker** - Needs rebuild to connect to Supabase instead of embedded data
2. **Power BI** - Connection not yet configured
3. **CV Tracking** - XY coordinate table ready, CV integration pending

---

## CHANGE LOG

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-27 | 2.0.0 | Supabase schema (36 tables), complete data dictionary |
| 2025-12-27 | 1.4.0 | Tracker v18/v19 with embedded data |
| 2025-12-20 | 1.0.0 | Initial ETL pipeline |

---

*Last updated: December 27, 2025*
