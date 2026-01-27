# BenchSight Data Dictionary

**Comprehensive reference for all tables, columns, calculations, and business rules**

Last Updated: 2026-01-21
Version: 2.00

---

## Overview

This data dictionary provides complete metadata for all tables in the BenchSight database, including:

- **Table-level metadata:** Source, derivation path, ETL phase, primary/foreign keys, row counts
- **Column-level metadata:** Data types, sources (explicit/calculated/derived), calculation formulas, filter contexts, business rules
- **Calculation reference:** Formulas for all derived metrics (xG, WAR/GAR, Corsi, Fenwick, etc.)
- **Business rules:** Critical logic for goal counting, player identification, time calculations, etc.

**Total Tables:** 132-139 tables  
**Total Columns:** 3000+ columns across all tables

---

## Table of Contents

1. [Table Source Types](#table-source-types)
2. [BLB Tables (Direct Loads)](#blb-tables-direct-loads)
3. [Tracking Tables](#tracking-tables)
4. [Static Reference Tables](#static-reference-tables)
5. [Calculated/Derived Tables](#calculatedderived-tables)
6. [QA Tables](#qa-tables)
7. [Calculation Reference](#calculation-reference)
8. [Business Rules](#business-rules)

---

## Table Source Types

| Code | Type | Description | Example |
|------|------|-------------|---------|
| [BLB] BLB | Direct Load | Loaded directly from BLB_Tables.xlsx | dim_player, dim_team |
| 🎮 TRK | Tracking | Derived from tracking Excel files | fact_events, fact_shifts |
| [CALC] CALC | Calculated | Calculated from other tables | fact_player_game_stats |
| [STATIC] STATIC | Static | Hardcoded constants | dim_period, dim_zone |
| [QA] QA | Quality Assurance | Validation tables | qa_goal_verification |

### Column Source Types

| Type | Description | Example |
|------|-------------|---------|
| **Explicit** | Directly from source data | player_id, game_id, event_type |
| **Calculated** | Formula-based calculation | shooting_pct = goals / sog * 100 |
| **Derived** | Filtered/aggregated from source | goals = COUNT WHERE event_type='Goal' AND event_detail='Goal_Scored' |

---

## Table Population Reference

This section documents **HOW** each table is populated - the source code location, input dependencies, transformation logic, and ETL phase. Use this to understand what creates each table and trace data lineage.

### ETL Phase Overview

The ETL pipeline runs in 11+ phases. Each phase builds on outputs from previous phases.

```
Phase 1: Load BLB Tables (dim_player, dim_team, dim_schedule, etc.)
    ↓
Phase 2: Build Player Lookup (game_id + jersey → player_id mapping)
    ↓
Phase 3: Load Tracking Data (raw events/shifts from game Excel files)
    ↓
Phase 4: Create Derived Tables (fact_events, fact_shifts from tracking)
    ↓
Phase 5: Create Reference Tables (23 static dimension tables)
    ↓
Phase 5.5-5.12: Enhance Tables (add FKs, flags, derived columns)
    ↓
Phase 6: Player/Team/Goalie Game Stats (fact_player_game_stats, etc.)
    ↓
Phase 7: Macro Stats (season/career aggregations)
    ↓
Phase 8-10: Analytics Tables (scoring chances, shift quality, etc.)
    ↓
Phase 11: QA Tables (validation checks)
```

### Phase 1: BLB Table Loading

**File:** `src/core/base_etl.py` → `load_blb_tables()` (line 956)
**Source:** `data/raw/BLB_Tables.xlsx`
**Purpose:** Load master data tables from the league database export

| Table | Source Sheet | Key | Transformation | Rows |
|-------|--------------|-----|----------------|------|
| **dim_player** | dim_player | player_id | Removes 7 CSAH-specific columns (all null for NORAD) | ~337 |
| **dim_team** | dim_team | team_id | Filters to NORAD teams; removes csah_team column | ~26 |
| **dim_league** | dim_league | league_id | Direct load | ~3 |
| **dim_season** | dim_season | season_id | Direct load | ~10 |
| **dim_schedule** | dim_schedule | game_id | Removes video/team_game_id columns | ~567 |
| **dim_playerurlref** | dim_playerurlref | - | Direct load (player URL references) | ~300 |
| **dim_randomnames** | dim_randomnames | - | Direct load (anonymization names) | ~500 |
| **dim_event_type** | dim_event_type | event_type_id | Direct load (NOT auto-generated) | ~15 |
| **dim_event_detail** | dim_event_detail | event_detail_id | Direct load (NOT auto-generated) | ~50 |
| **dim_event_detail_2** | dim_play_detail_2 | event_detail_2_id | Column rename: play_detail_* → event_detail_2_* | ~30 |
| **dim_play_detail** | dim_play_detail | play_detail_id | Direct load or dynamic creation in Phase 5 | ~40 |
| **dim_play_detail_2** | dim_play_detail_2 | play_detail_2_id | Column rename: play_detail_* → play_detail_2_* | ~30 |
| **fact_gameroster** | fact_gameroster | (game_id, player_id) | Enhanced with season/schedule data; official league stats | ~2000 |
| **fact_leadership** | fact_leadership | composite | Direct load (team captains/alternates) | ~100 |
| **fact_registration** | fact_registration | player_season_registration_id | Direct load | ~400 |
| **fact_draft** | fact_draft | player_draft_id | Direct load | ~200 |

**Code Pattern:**
```python
# In load_blb_tables() - line 956
xlsx = pd.ExcelFile('data/raw/BLB_Tables.xlsx')
dim_player = pd.read_excel(xlsx, sheet_name='dim_player')
# Drop CSAH-specific columns (all null for NORAD)
csah_cols = [c for c in dim_player.columns if 'csah' in c.lower()]
dim_player = dim_player.drop(columns=csah_cols)
```

---

### Phase 2: Build Player Lookup

**File:** `src/core/base_etl.py` → `build_player_lookup()` (line 1095)
**Input:** fact_gameroster
**Output:** In-memory dictionary (not a table)
**Purpose:** Map tracking data (game_id, team_name, jersey_number) → player_id

**Why This Exists:**
Tracking files identify players by jersey number, not player_id. This lookup resolves:
- `(game_id=19001, team='Blue', jersey=12)` → `player_id='P001'`

**Logic:**
```python
# Primary lookup: (game_id, team_name, jersey_number) → player_id
player_lookup = {}
for _, row in fact_gameroster.iterrows():
    key = (row['game_id'], row['team_name'], row['jersey_number'])
    player_lookup[key] = row['player_id']
```

**Edge Cases Handled:**
- Players who change jerseys mid-season
- Players who play for multiple teams
- Missing jersey numbers (uses fallback lookups)

---

### Phase 3: Load Tracking Data

**File:** `src/core/base_etl.py` (inline, line 1155)
**Source:** `data/raw/games/{game_id}/` tracking Excel files
**Purpose:** Load raw event and shift data from game tracking files

**Input Files per Game:**
- `{game_id}_tracking.xlsx` → Events sheet, Shifts sheet
- Or legacy format: `events.xlsx`, `shifts.xlsx`

**Intermediate Tables Created:**
| Table | Source | Purpose |
|-------|--------|---------|
| **fact_event_players** | Events sheet | One row per player per event (expanded from event_player_1/2/3) |
| **fact_shifts (raw)** | Shifts sheet | Raw shift data before deduplication |

**Key Transformations:**
1. **Player Resolution:** Jersey numbers → player_ids via Phase 2 lookup
2. **Time Calculation:** Convert min:sec to total_seconds
3. **Key Generation:** Create event_id, shift_id, sequence_key

**Excluded Games:** 18965, 18993, 19032 (incomplete tracking data)

---

### Phase 4: Create Derived Tables

**File:** `src/core/base_etl.py` → `create_derived_tables()` (line 1455)
**Purpose:** Build core fact tables from tracking data

| Table | Builder | Input | Logic | Rows |
|-------|---------|-------|-------|------|
| **fact_events** | `src/builders/events.py` → `build_fact_events()` | fact_event_players | One row per event; prioritizes Goal > Shot > Pass when deduping | ~5,800/4 games |
| **fact_shifts** | `src/builders/shifts.py` → `build_fact_shifts()` | raw tracking shifts | Deduplicate; assign shift_id; calculate duration | ~400/4 games |
| **fact_shift_players** | inline | fact_shifts | One row per player per shift (from shift rosters) | ~2,000/4 games |
| **fact_tracking** | inline | fact_event_players | Unique tracking points with XY coordinates | ~8,000/4 games |

**fact_events Builder Logic (`src/builders/events.py`):**
```python
def build_fact_events(fact_event_players: pd.DataFrame) -> pd.DataFrame:
    """
    Collapse fact_event_players to one row per event.
    Priority: Goal > Shot > Pass > other (when same event has multiple types)
    """
    # Group by event_id, take first row after sorting by priority
    priority_order = {'Goal': 0, 'Shot': 1, 'Pass': 2}
    df['priority'] = df['event_type'].map(priority_order).fillna(99)
    fact_events = df.sort_values('priority').groupby('event_id').first()
    return fact_events
```

---

### Phase 5: Create Reference Tables (Static Dimensions)

**File:** `src/tables/dimension_tables.py` → `create_all_dimension_tables()` (called from line 1579)
**Purpose:** Create 23 hardcoded dimension tables

| Table | Rows | Purpose | Key Columns |
|-------|------|---------|-------------|
| **dim_comparison_type** | 6 | H2H, WOWY, vs_team analysis types | comparison_type_code |
| **dim_competition_tier** | 4 | Elite/Above Avg/Avg/Below Avg rating tiers | tier_name, min_rating, max_rating |
| **dim_composite_rating** | 8 | Offensive/Defensive/Two-way ratings | rating_code, scale_min, scale_max |
| **dim_danger_zone** | 4 | High/Medium/Low/Perimeter shot danger | danger_zone_name |
| **dim_highlight_category** | 10 | Highlight event classifications | category_name |
| **dim_micro_stat** | 22 | Screen, Tip, One-timer, Board Battle, etc. | micro_stat_code |
| **dim_net_location** | 10 | Glove High/Low, Blocker, Five Hole, etc. | net_location_name |
| **dim_pass_outcome** | 4 | Completed/Missed/Intercepted/Blocked | outcome_name |
| **dim_period** | 5 | Periods 1-3, OT, SO | period_number, period_name |
| **dim_position** | 4 | F/D/G/XTRA positions | position_code |
| **dim_rating** | 5 | 2-6 rating scale | rating_value, rating_name |
| **dim_rating_matchup** | 5 | Big Advantage to Big Disadvantage | matchup_name |
| **dim_rink_zone** | 267 | 200ft x 85ft grid coordinates | x, y, zone_name |
| **dim_save_outcome** | 3 | Saved/Blocked/Scored | outcome_name |
| **dim_shift_slot** | 7 | F1-F3, D1-D2, G, XTRA slots | slot_code |
| **dim_shot_outcome** | 5 | Scored/Saved/Blocked/Missed/Crossbar | outcome_name |
| **dim_situation** | 6 | EV/PP/PK/EN/4v4/3v3 | situation_code |
| **dim_stat** | 83 | All stat definitions | stat_code, stat_name, category |
| **dim_stat_category** | 13 | Stat groupings | category_name |
| **dim_stat_type** | 57 | Specific measurements | type_code |
| **dim_strength** | 18 | PP/PK/EV/EN with goal variations | strength_code |
| **dim_terminology_mapping** | 84 | Cross-reference mappings | source_term, target_term |
| **dim_turnover_quality** | 3 | High/Medium/Low quality | quality_name |
| **dim_turnover_type** | 21 | Giveaway/Takeaway subtypes | turnover_type_name |
| **dim_video_type** | 9 | Video classifications | video_type_name |
| **dim_zone** | 3 | O/N/D zones | zone_code, zone_name |
| **dim_zone_outcome** | 6 | Zone entry/exit outcomes | outcome_name |

**Dynamic Dimension Tables (from tracking data):**

| Table | Source | Logic |
|-------|--------|-------|
| **dim_zone_entry_type** | fact_events | Extract unique zone_entry_type values |
| **dim_zone_exit_type** | fact_events | Extract unique zone_exit_type values |
| **dim_stoppage_type** | fact_events | Extract unique stoppage_type values |
| **dim_giveaway_type** | fact_events | Extract unique giveaway_type values |
| **dim_takeaway_type** | fact_events | Extract unique takeaway_type values |

---

### Phases 5.5-5.12: Table Enhancement

These phases add foreign keys, calculated columns, and flags to existing tables.

| Phase | Function | Line | Tables Modified | Enhancements |
|-------|----------|------|-----------------|--------------|
| **5.5** | `enhance_event_tables()` | 2337 | fact_events, fact_event_players | Add shift_id FK, period_id, zone_id, event_type_id, event_detail_id |
| **5.6** | `enhance_derived_event_tables()` | 2995 | fact_tracking | Add FKs to tracking table |
| **5.7** | `create_fact_sequences()` | 3063 | Creates fact_sequences | Group continuous events; assign is_goal, is_sog flags |
| **5.8** | `create_fact_plays()` | 3195 | Creates fact_plays | Group sequences into possession units |
| **5.9** | `enhance_events_with_flags()` | 3310 | fact_events | Add is_goal, is_shot_on_goal, is_corsi_event, is_fenwick_event flags |
| **5.10** | `create_derived_event_tables()` | 3973 | Creates analytics tables | fact_scoring_chances, fact_shot_danger, fact_linked_events |
| **5.11** | `enhance_shift_tables()` | 4493 | fact_shifts | Add period_id, team_ids, strength, situation |
| **5.11B** | `enhance_shift_players()` | 5105 | fact_shift_players | Add player_name, player_position, player_rating |
| **5.12** | (inline) | 5535 | fact_gameroster | Update positions from actual shift data |

---

### Phase 6: Player/Team/Goalie Stats

**Files:** `src/tables/core_facts.py`, `src/builders/player_stats.py`, `src/builders/goalie_stats.py`, `src/builders/team_stats.py`

| Table | Builder | Input Tables | Key Logic | Columns |
|-------|---------|--------------|-----------|---------|
| **fact_player_game_stats** | `PlayerStatsBuilder` | fact_event_players, fact_events, fact_shifts, fact_shift_players, fact_gameroster | Aggregate per (game_id, player_id); skaters only | 317 |
| **fact_goalie_game_stats** | `GoalieStatsBuilder` | fact_events, fact_shifts, fact_gameroster | Aggregate per (game_id, goalie_id); goalies only | ~50 |
| **fact_team_game_stats** | `TeamStatsBuilder` | fact_player_game_stats (aggregated) | Sum player stats per team | ~100 |

**fact_player_game_stats Calculation Categories:**
1. **Event Stats:** Goals, assists, shots, passes (from fact_event_players WHERE player_role='event_player_1')
2. **Shift Stats:** TOI, shift count, avg shift (from fact_shifts)
3. **Advanced:** xG, xA, Corsi, Fenwick (calculated from events + on-ice analysis)
4. **Micro Stats:** Blocks, takeaways, screens (from event_detail filtering)
5. **Zone Stats:** Entry/exit analysis (from zone_entry_type/zone_exit_type)
6. **Strength Splits:** EV/PP/PK breakdowns (from shift strength)
7. **Game Score:** Composite performance metric
8. **WAR/GAR:** Wins/Goals Above Replacement

---

### Phase 7: Macro Stats (Season/Career Aggregations)

**File:** `src/tables/macro_stats.py`

| Table | Input | Grain | Logic |
|-------|-------|-------|-------|
| **fact_player_season_stats_basic** | fact_gameroster | (player_id, season_id, game_type) | Official league stats (G, A, PIM); skaters only |
| **fact_player_career_stats_basic** | fact_gameroster | (player_id, game_type) | Sum across all seasons |
| **fact_goalie_season_stats_basic** | fact_gameroster | (player_id, season_id, game_type) | GP, W, L, GAA, SV%; goalies only |
| **fact_goalie_career_stats_basic** | fact_gameroster | (player_id, game_type) | Career totals |
| **fact_team_season_stats_basic** | fact_gameroster | (team_id, season_id, game_type) | Team totals |
| **fact_player_season_stats** | fact_player_game_stats | (player_id, season_id) | Advanced tracking stats aggregated |
| **fact_player_career_stats** | fact_player_season_stats | (player_id) | Career advanced stats + linemate data |
| **fact_goalie_season_stats** | fact_goalie_game_stats | (player_id, season_id) | Goalie tracking metrics |
| **fact_goalie_career_stats** | fact_goalie_season_stats | (player_id) | Goalie career tracking |
| **fact_team_season_stats** | fact_team_game_stats | (team_id, season_id) | Team advanced metrics |

---

### Phases 8-10: Analytics Tables

**File:** `src/tables/event_analytics.py`, `src/tables/shift_analytics.py`, `src/tables/remaining_facts.py`

#### Event Analytics (Phase 8)

| Table | Input | Grain | Logic |
|-------|-------|-------|-------|
| **fact_scoring_chances** | fact_events | event_id | High-danger events (xG > threshold) |
| **fact_shot_danger** | fact_events (shots) | event_id | Danger zone + xG calculation |
| **fact_linked_events** | fact_events | (event_id_1, event_id_2) | Causal links (shot→rebound, pass→shot) |
| **fact_rush_events** | fact_events | event_id | Rush identification + speed |
| **fact_possession_time** | fact_shifts + fact_events | (game_id, team_id) | Possession by zone |

#### Shift Analytics (Phase 9)

| Table | Input | Grain | Logic |
|-------|-------|-------|-------|
| **fact_h2h** | fact_shift_players | (player_1_id, player_2_id, game_id) | Head-to-head matchup (together vs apart) |
| **fact_wowy** | fact_shift_players | (player_id, season_id) | With/Without You season analysis |
| **fact_line_combos** | fact_shift_players | (season_id, F1, F2, F3) | Forward line combinations |
| **fact_shift_quality** | fact_shifts + players | shift_id | Shift quality scoring (EV only) |
| **fact_shift_quality_logical** | fact_shift_quality | shift_id | Quality tiers (Elite/Good/Avg/Below) |

#### Remaining Facts (Phase 10)

**File:** `src/tables/remaining_facts.py` → `build_remaining_tables()`

| Table | Input | Grain | Purpose |
|-------|-------|-------|---------|
| **fact_player_period_stats** | fact_player_game_stats | (game_id, player_id, period) | Period breakdown |
| **fact_period_momentum** | fact_events | (game_id, period) | Momentum analysis |
| **fact_player_micro_stats** | fact_events | (game_id, player_id, micro_stat_id) | Micro-stat tracking |
| **fact_player_qoc_summary** | fact_shift_players | (game_id, player_id) | Quality of competition |
| **fact_player_position_splits** | fact_gameroster | (season_id, player_id, position) | Position splits |
| **fact_player_trends** | fact_player_season_stats | (season_id, player_id) | Trend analysis |
| **fact_player_stats_long** | fact_player_game_stats | (game_id, player_id, stat_id) | Unpivoted stats |
| **fact_player_stats_by_competition_tier** | fact_player_game_stats | (player_id, tier, season) | Stats vs rating tier |
| **fact_player_pair_stats** | fact_h2h | (player_1_id, player_2_id, season) | Linemate chemistry |
| **fact_player_boxscore_all** | fact_player_game_stats | (game_id, player_id) | Complete boxscore |
| **fact_playergames** | fact_gameroster | (game_id, player_id) | Legacy format |
| **fact_zone_entry_summary** | fact_events | (game_id, team_id, entry_type) | Entry aggregation |
| **fact_zone_exit_summary** | fact_events | (game_id, team_id, exit_type) | Exit aggregation |
| **fact_team_zone_time** | fact_shifts | (game_id, team_id, zone) | Zone possession |
| **fact_special_teams_summary** | fact_events | (game_id, team_id) | PP/PK stats |
| **fact_player_xy_long** | fact_events | (game_id, player_id, event_id) | Player location |
| **fact_player_xy_wide** | fact_events | (game_id, player_id) | Location summary |
| **fact_puck_xy_long** | fact_events | (game_id, event_id) | Puck location |
| **fact_puck_xy_wide** | fact_events | (game_id) | Puck summary |
| **fact_shot_xy** | fact_events (shots) | (game_id, event_id) | Shot locations |
| **fact_highlights** | fact_events | (game_id, event_id) | Highlight events |
| **fact_video** | fact_events | (game_id, event_id) | Video references |
| **fact_team_standings_snapshot** | dim_schedule | (season_id) | Standings |
| **fact_league_leaders_snapshot** | fact_player_season_stats | (season_id) | Leaders |
| **lookup_player_game_rating** | dim_player | (game_id, player_id) | Rating lookup |

---

### Phase 11: QA Tables

**File:** `src/qa/build_qa_facts.py`, `src/tables/remaining_facts.py`

| Table | Input | Purpose | Key Checks |
|-------|-------|---------|------------|
| **qa_goal_accuracy** | fact_events vs dim_schedule | Validate goal counts | calculated vs official must match |
| **qa_data_completeness** | fact_event_players | Check coverage | Missing player_ids, missing events |
| **qa_scorer_comparison** | fact_player_game_stats | Cross-verify scorers | Multiple calculation paths agree |
| **qa_suspicious_stats** | fact_player_game_stats | Flag anomalies | Statistical outliers |
| **fact_suspicious_stats** | qa_suspicious_stats | Flagged records | Unusual patterns |

---

### Table Dependency Graph

```
BLB_Tables.xlsx
├── dim_player ─────────────────────────────────┐
├── dim_team ───────────────────────────────────┤
├── dim_schedule ───────────────────────────────┤
├── fact_gameroster ────────────────────────────┤
│       ↓                                       │
│   Player Lookup (Phase 2)                     │
│       ↓                                       │
Tracking Files (games/{id}/)                    │
├── fact_event_players ─────────────────────────┤
│       ↓                                       │
├── fact_events ←───────────────────────────────┤
│   ├── fact_sequences                          │
│   │   └── fact_plays                          │
│   ├── fact_scoring_chances                    │
│   ├── fact_shot_danger                        │
│   └── fact_linked_events                      │
│                                               │
├── fact_shifts ←───────────────────────────────┤
│   └── fact_shift_players                      │
│       ├── fact_h2h                            │
│       ├── fact_wowy                           │
│       └── fact_line_combos                    │
│                                               │
└───────────────────────────────────────────────┘
        ↓
fact_player_game_stats ← (events + shifts + roster + dims)
        ↓
├── fact_player_season_stats
│   └── fact_player_career_stats
├── fact_team_game_stats
│   └── fact_team_season_stats
└── fact_goalie_game_stats
    └── fact_goalie_season_stats
            ↓
        QA Tables (validation)
```

---

### Key Code Locations Summary

| Component | File | Line | Purpose |
|-----------|------|------|---------|
| ETL Orchestrator | `src/core/base_etl.py` | 1-5600 | All phases |
| BLB Loading | `src/core/base_etl.py` | 956 | Phase 1 |
| Player Lookup | `src/core/base_etl.py` | 1095 | Phase 2 |
| Event Builder | `src/builders/events.py` | all | fact_events |
| Shift Builder | `src/builders/shifts.py` | all | fact_shifts |
| Static Dims | `src/tables/dimension_tables.py` | all | 23 dim tables |
| Player Stats | `src/builders/player_stats.py` | all | fact_player_game_stats |
| Goalie Stats | `src/builders/goalie_stats.py` | all | fact_goalie_game_stats |
| Team Stats | `src/builders/team_stats.py` | all | fact_team_game_stats |
| Macro Stats | `src/tables/macro_stats.py` | all | *_season/career_stats |
| Event Analytics | `src/tables/event_analytics.py` | all | Scoring chances, etc. |
| Shift Analytics | `src/tables/shift_analytics.py` | all | H2H, WOWY, combos |
| Remaining | `src/tables/remaining_facts.py` | all | 30+ other tables |
| QA | `src/qa/build_qa_facts.py` | all | Validation tables |
| Key Utils | `src/core/key_utils.py` | all | Key generation |
| Goals Calc | `src/calculations/goals.py` | all | Goal counting logic |

---

## BLB Tables (Direct Loads)

### dim_player

**Source:** [BLB] BLB - Direct load from `BLB_Tables.xlsx` → `dim_player` sheet  
**ETL Phase:** Phase 1 (`load_blb_tables()`)  
**Code Location:** `src/core/base_etl.py` lines 864-936  
**Primary Key:** `player_id`  
**Row Count:** ~337 rows  
**Purpose:** Master player list with biographical and registration data

#### Key Columns

| Column | Type | Source | Description | Example |
|--------|------|--------|-------------|---------|
| player_id | VARCHAR(20) | Explicit | Unique player identifier | "P001" |
| player_full_name | VARCHAR(200) | Explicit | Player's full name | "John Smith" |
| team_id | VARCHAR(20) | Explicit | Current team ID | "T001" |
| position | VARCHAR(10) | Explicit | Primary position (F/D/G) | "F" |
| jersey_number | INTEGER | Explicit | Jersey number | 12 |
| skill_rating | DECIMAL(3,1) | Explicit | Player skill rating (1-10) | 7.5 |
| age | INTEGER | Explicit | Player age | 25 |

#### Foreign Keys

- `team_id` → `dim_team.team_id`

---

### dim_team

**Source:** [BLB] BLB - Direct load from `BLB_Tables.xlsx` → `dim_team` sheet  
**ETL Phase:** Phase 1  
**Primary Key:** `team_id`  
**Row Count:** ~26 rows  
**Purpose:** Team definitions and metadata

#### Key Columns

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| team_id | VARCHAR(20) | Explicit | Unique team identifier |
| team_name | VARCHAR(100) | Explicit | Team name |
| league_id | VARCHAR(20) | Explicit | League identifier |
| division | VARCHAR(50) | Explicit | Division name |

---

### dim_schedule

**Source:** [BLB] BLB - Direct load from `BLB_Tables.xlsx` → `dim_schedule` sheet  
**ETL Phase:** Phase 1  
**Primary Key:** `game_id`  
**Row Count:** ~567 rows  
**Purpose:** All scheduled games with metadata

#### Key Columns

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| game_id | INTEGER | Explicit | Unique game identifier |
| game_date | DATE | Explicit | Game date |
| home_team_id | VARCHAR(20) | Explicit | Home team ID |
| away_team_id | VARCHAR(20) | Explicit | Away team ID |
| season_id | VARCHAR(20) | Explicit | Season identifier |
| game_type | VARCHAR(20) | Explicit | Regular/Playoff |

---

## Tracking Tables

### fact_events

**Source:** 🎮 TRK - Derived from `{game_id}_tracking.xlsx` → `events` sheet  
**ETL Phase:** Phase 3 (`process_tracking_files()`)  
**Code Location:** `src/core/base_etl.py` lines 1000-1200  
**Primary Key:** `event_id`  
**Row Count:** ~5,800 rows (per 4 games)  
**Purpose:** All game events (shots, goals, passes, faceoffs, etc.)

#### Key Columns

| Column | Type | Source | Description | Filter Context |
|--------|------|--------|-------------|----------------|
| event_id | VARCHAR(50) | Explicit | Unique event identifier | - |
| game_id | INTEGER | Explicit | Game identifier | - |
| event_type | VARCHAR(50) | Explicit | Event type (Shot, Goal, Pass, etc.) | - |
| event_detail | VARCHAR(100) | Explicit | Event detail (Shot_OnNet, Goal_Scored, etc.) | - |
| event_player_1 | VARCHAR(20) | Explicit | Primary player (gets credit) | Used for player stats |
| event_player_2 | VARCHAR(20) | Explicit | Secondary player (assist, etc.) | - |
| event_player_3 | VARCHAR(20) | Explicit | Tertiary player | - |
| time_start_total_seconds | INTEGER | Calculated | Time remaining in period (seconds) | Calculated from event_start_min * 60 + event_start_sec |
| event_running_start | INTEGER | Calculated | Cumulative seconds from game start | (period-1)*1200 + (1200 - time_start_total_seconds) |
| period | INTEGER | Explicit | Period number (1-5) | - |
| zone | VARCHAR(10) | Explicit | Zone (O/N/D) | - |
| danger_level | VARCHAR(20) | Derived | Shot danger level (high/medium/low) | Calculated from XY coordinates |

#### Critical Business Rules

- **Goal Identification:** `event_type='Goal' AND event_detail='Goal_Scored'`
- **Shot vs Goal:** `Shot_Goal` is the SHOT that scored, not the goal event
- **Player Credit:** Only `event_player_1` gets credit for shots, passes, etc.
- **Assists:** Tracked via `play_detail1='AssistPrimary'/'AssistSecondary'` on PASS/SHOT events

#### Derived Columns

| Column | Calculation | Notes |
|--------|-------------|-------|
| time_start_total_seconds | `event_start_min * 60 + event_start_sec` | Time remaining in period |
| event_running_start | `(period-1)*1200 + (1200 - time_start_total_seconds)` | Cumulative from game start |
| duration | `time_start_total_seconds - time_end_total_seconds` | Event duration (clipped >= 0) |
| danger_level | Calculated from XY coordinates | High/Medium/Low based on shot location |

---

### fact_shifts

**Source:** 🎮 TRK - Derived from `{game_id}_tracking.xlsx` → `shifts` sheet  
**ETL Phase:** Phase 3  
**Primary Key:** `shift_id`  
**Row Count:** ~400 rows (per 4 games)  
**Purpose:** Player shift data (ice time)

#### Key Columns

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| shift_id | VARCHAR(50) | Explicit | Unique shift identifier |
| game_id | INTEGER | Explicit | Game identifier |
| player_id | VARCHAR(20) | Explicit | Player identifier |
| shift_start | INTEGER | Explicit | Shift start time (seconds) |
| shift_end | INTEGER | Explicit | Shift end time (seconds) |
| shift_duration | INTEGER | Calculated | Shift duration (seconds) |
| strength | VARCHAR(20) | Explicit | Game strength (5v5, PP, PK, etc.) |

#### Derived Columns

| Column | Calculation |
|--------|-------------|
| shift_duration | `shift_end - shift_start` |

---

### fact_event_players

**Source:** 🎮 TRK - Derived from `fact_events` (expanded)  
**ETL Phase:** Phase 3  
**Primary Key:** `event_player_id`  
**Row Count:** ~11,000 rows (per 4 games)  
**Purpose:** One row per event-player combination (event_player_1, event_player_2, etc.)

#### Key Columns

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| event_player_id | VARCHAR(50) | Explicit | Unique event-player identifier |
| event_id | VARCHAR(50) | Explicit | Event identifier (FK) |
| player_id | VARCHAR(20) | Explicit | Player identifier |
| player_role | VARCHAR(20) | Explicit | Role (event_player_1, event_player_2, opp_player_1, etc.) |

#### Filter Context

- **Primary Player Stats:** Filter `player_role='event_player_1'` for shots, passes, goals
- **Assist Tracking:** Filter `play_detail1='AssistPrimary'/'AssistSecondary'` where `player_role='event_player_1'`

---

## Calculated/Derived Tables

### fact_player_game_stats

**Source:** [CALC] CALC - Calculated from `fact_events` + `fact_shifts`  
**ETL Phase:** Phase 4 (Core Facts)  
**Code Location:** `src/tables/core_facts.py`  
**Primary Key:** `player_game_key` (format: `PG{game_id}{player_id}`)  
**Row Count:** ~1,400 rows (per 4 games, ~350 players)  
**Column Count:** 317 columns  
**Purpose:** Per-game player statistics (comprehensive)

#### Table Metadata

- **Derivation:** Aggregated per player per game from `fact_events` and `fact_shifts`
- **Dependencies:** `fact_events`, `fact_event_players`, `fact_shifts`, `fact_shift_players`, `dim_player`, `dim_team`, `dim_schedule`
- **Excludes:** Goalies (separate table: `fact_goalie_game_stats`)

#### Core Stat Columns

| Column | Type | Source | Calculation | Filter Context |
|--------|------|--------|-------------|----------------|
| goals | INTEGER | Derived | `COUNT WHERE event_type='Goal' AND event_detail='Goal_Scored'` | `event_player_1` |
| primary_assists | INTEGER | Derived | `COUNT WHERE play_detail1='AssistPrimary'` | `event_player_1` |
| secondary_assists | INTEGER | Derived | `COUNT WHERE play_detail1='AssistSecondary'` | `event_player_1` |
| assists | INTEGER | Calculated | `primary_assists + secondary_assists` | - |
| points | INTEGER | Calculated | `goals + assists` | - |
| shots | INTEGER | Derived | `COUNT WHERE event_type='Shot'` | `event_player_1` |
| sog | INTEGER | Derived | `COUNT WHERE event_type='Shot' AND event_detail LIKE '%OnNet%' OR event_detail LIKE '%Saved%'` + `goals` | `event_player_1` |
| shooting_pct | DECIMAL(10,4) | Calculated | `goals / sog * 100` | WHERE `sog > 0` |
| pass_attempts | INTEGER | Derived | `COUNT WHERE event_type='Pass'` | `event_player_1` |
| pass_completed | INTEGER | Derived | `COUNT WHERE event_type='Pass' AND event_detail LIKE '%Completed%'` | `event_player_1` |
| pass_pct | DECIMAL(10,4) | Calculated | `pass_completed / pass_attempts * 100` | WHERE `pass_attempts > 0` |

#### Time on Ice Columns

| Column | Type | Source | Calculation |
|--------|------|--------|-------------|
| toi_seconds | INTEGER | Derived | `SUM(shift_duration)` from `fact_shifts` |
| toi_minutes | DECIMAL(10,2) | Calculated | `toi_seconds / 60` |
| shift_count | INTEGER | Derived | `COUNT(DISTINCT logical_shift_number)` from `fact_shifts` |
| avg_shift | DECIMAL(10,2) | Calculated | `toi_seconds / shift_count` |

#### Faceoff Columns

| Column | Type | Source | Calculation | Filter Context |
|--------|------|--------|-------------|----------------|
| fo_wins | INTEGER | Derived | `COUNT WHERE event_type='Faceoff'` | `event_player_1` (winner) |
| fo_losses | INTEGER | Derived | `COUNT WHERE event_type='Faceoff'` | `opp_player_1` (loser) |
| fo_total | INTEGER | Calculated | `fo_wins + fo_losses` | - |
| fo_pct | DECIMAL(10,4) | Calculated | `fo_wins / fo_total * 100` | WHERE `fo_total > 0` |

#### Turnover Columns

| Column | Type | Source | Calculation | Filter Context |
|--------|------|--------|-------------|----------------|
| giveaways | INTEGER | Derived | `COUNT WHERE event_type='Turnover' AND event_detail LIKE '%Giveaway%'` | `event_player_1` |
| takeaways | INTEGER | Derived | `COUNT WHERE event_type='Turnover' AND event_detail LIKE '%Takeaway%'` | `event_player_1` |
| turnover_diff | INTEGER | Calculated | `takeaways - giveaways` | - |
| bad_giveaways | INTEGER | Derived | `COUNT WHERE event_type='Turnover' AND is_bad_giveaway=1` | `event_player_1` |

#### Corsi/Fenwick Columns

| Column | Type | Source | Calculation | Filter Context |
|--------|------|--------|-------------|----------------|
| corsi_for | INTEGER | Derived | `COUNT WHERE is_corsi_event(event_type, event_detail)=True` | `event_player_1`, player's team |
| corsi_against | INTEGER | Derived | `COUNT WHERE is_corsi_event(event_type, event_detail)=True` | Opponent team, player on ice |
| cf_pct | DECIMAL(10,4) | Calculated | `corsi_for / (corsi_for + corsi_against) * 100` | WHERE `corsi_for + corsi_against > 0` |
| fenwick_for | INTEGER | Derived | `COUNT WHERE is_fenwick_event(event_type, event_detail)=True` | `event_player_1`, player's team |
| fenwick_against | INTEGER | Derived | `COUNT WHERE is_fenwick_event(event_type, event_detail)=True` | Opponent team, player on ice |
| ff_pct | DECIMAL(10,4) | Calculated | `fenwick_for / (fenwick_for + fenwick_against) * 100` | WHERE `fenwick_for + fenwick_against > 0` |

**Corsi Event Definition:**
- SOG (Shot_OnNetSaved, Shot_OnNet, Shot_Goal) OR
- Blocked Shot OR
- Missed Shot (Shot_Missed, Shot_MissedPost)

**Fenwick Event Definition:**
- SOG OR
- Missed Shot
- (Excludes blocked shots)

#### xG (Expected Goals) Columns

| Column | Type | Source | Calculation | Filter Context |
|--------|------|--------|-------------|----------------|
| xg_for | DECIMAL(10,4) | Calculated | `SUM(shot_xg)` | `event_player_1`, `event_type='Shot'` |
| xg_against | DECIMAL(10,4) | Calculated | `SUM(shot_xg)` | Opponent team, player on ice |
| goals_above_xg | DECIMAL(10,4) | Calculated | `goals - xg_for` | - |
| xg_per_shot | DECIMAL(10,4) | Calculated | `xg_for / shots` | WHERE `shots > 0` |

**xG Calculation Formula:**
```
shot_xg = base_rate × rush_modifier × shot_type_modifier × flurry_adjustment

Base Rates:
- High Danger: 0.25
- Medium Danger: 0.08
- Low Danger: 0.03
- Default: 0.06

Modifiers:
- Rush: 1.3x
- Rebound: 1.5x
- One-timer: 1.4x
- Breakaway: 2.5x
- Screened: 1.2x
- Deflection: 1.3x

Shot Type Modifiers:
- Wrist: 1.0x
- Slap: 0.95x
- Snap: 1.05x
- Backhand: 0.9x
- Tip: 1.15x
- Deflection: 1.1x

Final: xg = min(base_rate × modifiers, 0.95)  # Capped at 0.95
```

#### WAR/GAR Columns

| Column | Type | Source | Calculation |
|--------|------|--------|-------------|
| gar_offense | DECIMAL(10,4) | Calculated | `goals×1.0 + primary_assists×0.7 + secondary_assists×0.4 + sog×0.015 + xg_for×0.8 + shot_assists×0.3` |
| gar_defense | DECIMAL(10,4) | Calculated | `takeaways×0.05 + blocks×0.02 + zone_exit_controlled×0.03` |
| gar_possession | DECIMAL(10,4) | Calculated | `(cf_pct - 50) / 100 × 0.02 × toi_hours × 60` |
| gar_transition | DECIMAL(10,4) | Calculated | `zone_entry_controlled×0.04` |
| gar_poise | DECIMAL(10,4) | Calculated | `pressure_success_count×0.02` |
| gar_total | DECIMAL(10,4) | Calculated | `gar_offense + gar_defense + gar_possession + gar_transition + gar_poise` |
| war | DECIMAL(10,4) | Calculated | `gar_total / 4.5` |

**GAR Weights:**
- Goals: 1.0
- Primary Assists: 0.7
- Secondary Assists: 0.4
- Shots Generated (SOG): 0.015
- xG Generated: 0.8
- Takeaways: 0.05
- Blocked Shots: 0.02
- Defensive Zone Exits: 0.03
- CF% Above Average: 0.02 per hour
- Zone Entry Value: 0.04
- Shot Assists: 0.3
- Pressure Success: 0.02

**WAR Conversion:**
- `WAR = GAR / 4.5` (4.5 goals per win in rec hockey)

#### Game Score Columns

| Column | Type | Source | Calculation |
|--------|------|--------|-------------|
| game_score | DECIMAL(10,4) | Calculated | `gs_scoring + gs_shots + gs_playmaking + gs_defense + gs_hustle` |
| gs_scoring | DECIMAL(10,4) | Calculated | `goals×1.0 + primary_assists×0.8 + secondary_assists×0.5` |
| gs_shots | DECIMAL(10,4) | Calculated | `sog×0.1 + high_danger_shots×0.15` |
| gs_playmaking | DECIMAL(10,4) | Calculated | `controlled_entries×0.08 + second_touch×0.02` |
| gs_defense | DECIMAL(10,4) | Calculated | `takeaways×0.15 + blocks×0.08 + poke_checks×0.05` |
| gs_hustle | DECIMAL(10,4) | Calculated | `(fo_wins - fo_losses)×0.03` |

#### Rate Stats Columns

| Column | Type | Source | Calculation |
|--------|------|--------|-------------|
| goals_per_60 | DECIMAL(10,4) | Calculated | `goals / toi_hours × 60` |
| assists_per_60 | DECIMAL(10,4) | Calculated | `assists / toi_hours × 60` |
| points_per_60 | DECIMAL(10,4) | Calculated | `points / toi_hours × 60` |
| shots_per_60 | DECIMAL(10,4) | Calculated | `shots / toi_hours × 60` |
| corsi_per_60 | DECIMAL(10,4) | Calculated | `corsi_for / toi_hours × 60` |

**Note:** `toi_hours = toi_seconds / 3600`

#### Situation Splits Columns

| Column | Type | Source | Calculation | Filter Context |
|--------|------|--------|-------------|----------------|
| toi_5v5 | INTEGER | Derived | `SUM(shift_duration)` | `strength='5v5'` |
| goals_5v5 | INTEGER | Derived | `COUNT WHERE event_type='Goal' AND event_detail='Goal_Scored'` | `strength='5v5'`, `event_player_1` |
| toi_pp | INTEGER | Derived | `SUM(shift_duration)` | `strength LIKE '%PP%'` |
| goals_pp | INTEGER | Derived | `COUNT WHERE event_type='Goal' AND event_detail='Goal_Scored'` | `strength LIKE '%PP%'`, `event_player_1` |
| toi_pk | INTEGER | Derived | `SUM(shift_duration)` | `strength LIKE '%PK%'` |
| goals_pk | INTEGER | Derived | `COUNT WHERE event_type='Goal' AND event_detail='Goal_Scored'` | `strength LIKE '%PK%'`, `event_player_1` |

#### Additional Columns

The table includes 300+ additional columns covering:
- Shot type breakdowns (wrist, slap, snap, etc.)
- Pass type analysis (stretch, bank, rim, etc.)
- Zone entry/exit statistics
- Pressure statistics
- Competition tier performance
- Game state analysis (leading/trailing/close)
- Period splits
- Micro statistics
- Linemate analysis
- Time bucket analysis
- Rebound/second chance statistics

**Full column list:** See `src/tables/core_facts.py` for complete implementation.

---

## Calculation Reference

### Goal Counting

**CRITICAL RULE:**
```sql
Goals = COUNT(*) 
WHERE event_type = 'Goal' 
  AND event_detail = 'Goal_Scored'
  AND event_player_1 = player_id
```

**Important Notes:**
- `Shot_Goal` is the SHOT that scored, not the goal event
- `event_player_1` = goal scorer
- `event_player_2` = primary assist (if applicable)
- `event_player_3` = secondary assist (if applicable)
- Must match official goal count from `fact_gameroster`

### Corsi Calculation

**Corsi For (CF):**
```python
CF = COUNT(*) 
WHERE is_corsi_event(event_type, event_detail) = True
  AND event_player_1 = player_id
  AND team_id = player_team_id
```

**Corsi Against (CA):**
```python
CA = COUNT(*) 
WHERE is_corsi_event(event_type, event_detail) = True
  AND team_id = opponent_team_id
  AND player_id ON ICE (from fact_shifts)
```

**Corsi Event Definition:**
- SOG: `event_type='Shot' AND event_detail IN ('Shot_OnNetSaved', 'Shot_OnNet', 'Shot_Goal')`
- Blocked: `event_detail LIKE '%Blocked%'`
- Missed: `event_detail IN ('Shot_Missed', 'Shot_MissedPost')`

**Corsi For Percentage:**
```python
CF% = (CF / (CF + CA)) * 100
```

### Fenwick Calculation

**Fenwick For (FF):**
```python
FF = COUNT(*) 
WHERE is_fenwick_event(event_type, event_detail) = True
  AND event_player_1 = player_id
  AND team_id = player_team_id
```

**Fenwick Against (FA):**
```python
FA = COUNT(*) 
WHERE is_fenwick_event(event_type, event_detail) = True
  AND team_id = opponent_team_id
  AND player_id ON ICE (from fact_shifts)
```

**Fenwick Event Definition:**
- SOG: Same as Corsi
- Missed: Same as Corsi
- **EXCLUDES:** Blocked shots

**Fenwick For Percentage:**
```python
FF% = (FF / (FF + FA)) * 100
```

### xG (Expected Goals) Calculation

**Base Formula:**
```python
shot_xg = base_rate × rush_modifier × shot_type_modifier × flurry_adjustment
shot_xg = min(shot_xg, 0.95)  # Cap at 0.95
```

**Base Rates (by danger level):**
- High Danger: 0.25
- Medium Danger: 0.08
- Low Danger: 0.03
- Default: 0.06

**Rush Modifiers:**
- Rush: 1.3x
- Rebound: 1.5x
- One-timer: 1.4x
- Breakaway: 2.5x
- Screened: 1.2x
- Deflection: 1.3x

**Shot Type Modifiers:**
- Wrist: 1.0x
- Slap: 0.95x
- Snap: 1.05x
- Backhand: 0.9x
- Tip: 1.15x
- Deflection: 1.1x

**Flurry Adjustment:**
- Applied when multiple shots occur within 3 seconds
- Reduces xG for subsequent shots in flurry

**Total xG:**
```python
xg_for = SUM(shot_xg) 
WHERE event_type = 'Shot' 
  AND event_player_1 = player_id
```

**Flurry Adjustment:**
- Applied when multiple shots occur within 3 seconds
- Groups shots into sequences (shots within 3 seconds of each other)
- Formula: `P(AtLeastOneGoal) = 1 - ∏(1 - xG_i)` for each sequence
- Single shot sequences: No adjustment (use raw xG)
- Multi-shot sequences: Calculate probability of at least one goal
- Prevents over-counting rapid-fire shots (e.g., shot + rebound + rebound)
- Capped at 0.99 per sequence

**Flurry Adjustment Algorithm:**
```python
# Group shots into sequences (within 3 seconds)
for shot in sorted_shots:
    if time_diff <= 3.0:
        add_to_current_sequence(shot)
    else:
        start_new_sequence(shot)

# Calculate adjusted xG per sequence
for sequence in sequences:
    if len(sequence) == 1:
        xg_adjusted += sequence[0].xg_value  # No adjustment
    else:
        # Multi-shot: P(AtLeastOneGoal) = 1 - ∏(1 - xG_i)
        prob_no_goal = 1.0
        for xg in sequence.xg_values:
            prob_no_goal *= (1.0 - xg)
        xg_flurry = 1.0 - prob_no_goal
        xg_adjusted += min(xg_flurry, 0.99)  # Cap at 0.99
```

**xG Output Columns:**
- `xg_raw`: Sum before flurry adjustment
- `xg_for`: Final xG after flurry adjustment (used in stats)
- `xg_flurry_adjustment`: Total reduction from flurry logic
- `goals_above_expected`: `goals - xg_for`
- `xg_per_shot`: `xg_for / shots` (average xG per shot)
- `finishing_skill`: `goals / xg_for` (conversion rate)

### WAR/GAR Calculation

**GAR (Goals Above Replacement) Components:**

**Offense GAR:**
```python
GAR_offense = goals × 1.0
            + primary_assists × 0.7
            + secondary_assists × 0.4
            + sog × 0.015
            + xg_for × 0.8
            + shot_assists × 0.3
```

**Defense GAR:**
```python
GAR_defense = takeaways × 0.05
            + blocks × 0.02
            + zone_exit_controlled × 0.03
```

**Possession GAR:**
```python
GAR_possession = (cf_pct - 50) / 100 × 0.02 × toi_hours × 60
```

**Transition GAR:**
```python
GAR_transition = zone_entry_controlled × 0.04
```

**Poise GAR:**
```python
GAR_poise = pressure_success_count × 0.02
```

**Total GAR:**
```python
GAR_total = GAR_offense + GAR_defense + GAR_possession + GAR_transition + GAR_poise
```

**WAR (Wins Above Replacement):**
```python
WAR = GAR_total / 4.5
WAR_pace = WAR * GAMES_PER_SEASON  # Projected WAR for full season
```

**Note:** 4.5 goals per win in rec hockey (20 games per season)

**WAR Output Columns:**
- `gar_offense`: Offensive contribution
- `gar_defense`: Defensive contribution
- `gar_possession`: Possession impact
- `gar_transition`: Transition game value
- `gar_poise`: Performance under pressure
- `gar_total`: Sum of all components
- `war`: `gar_total / 4.5`
- `war_pace`: `war * 20` (season projection)

### Game Score Calculation

**Game Score Components:**

**Scoring:**
```python
gs_scoring = goals × 1.0
           + primary_assists × 0.8
           + secondary_assists × 0.5
```

**Shots:**
```python
gs_shots = sog × 0.1
         + high_danger_shots × 0.15
```

**Playmaking:**
```python
gs_playmaking = controlled_entries × 0.08
              + second_touch × 0.02
```

**Defense:**
```python
gs_defense = takeaways × 0.15
           + blocks × 0.08
           + poke_checks × 0.05
```

**Hustle:**
```python
gs_hustle = (fo_wins - fo_losses) × 0.03
```

**Total Game Score:**
```python
game_score_raw = gs_scoring + gs_shots + gs_playmaking + gs_defense + gs_hustle + gs_faceoffs + gs_poise + gs_penalties
game_score = 2.0 + game_score_raw  # Baseline shift for 2-10 scale
game_score_per_60 = game_score * 3600 / toi_seconds
```

**Game Score Components (Detailed):**

**Offensive Game Score:**
```python
offensive_game_score = gs_scoring + gs_shots + gs_playmaking
```

**Defensive Game Score:**
```python
defensive_game_score = gs_defense + gs_hustle - (giveaways * 0.08)
```

**Calculated Rating (from Game Score):**
```python
if game_score < 2.5:
    calculated_rating = 2.0
elif game_score < 3.5:
    calculated_rating = 2.0 + (game_score - 2.5) / 1.0  # Linear interpolation 2-3
elif game_score < 5.0:
    calculated_rating = 3.0 + (game_score - 3.5) / 1.5  # Linear interpolation 3-4
elif game_score < 7.0:
    calculated_rating = 4.0 + (game_score - 5.0) / 2.0  # Linear interpolation 4-5
else:
    calculated_rating = 5.0 + min((game_score - 7.0) / 3.0, 1.0)  # Linear interpolation 5-6

calculated_rating = max(2.0, min(6.0, calculated_rating))  # Cap at 2-6
```

**Performance vs Rating:**
```python
expected_game_score = RATING_GAME_SCORE_MAP[player_rating]
# RATING_GAME_SCORE_MAP: {1: 1.0, 2: 2.3, 3: 3.5, 4: 4.7, 5: 5.9, 6: 7.1, 7: 8.3, 8: 9.5, 9: 10.7, 10: 12.0}

performance_index = (actual_game_score / expected_game_score) * 100
rating_delta = adjusted_rating - player_rating  # Positive = played above rating
rating_differential = calculated_rating - player_rating  # Positive = outperformed
```

**Performance Tiers:**
- Elite: `performance_index >= 130`
- Above Expected: `110 <= performance_index < 130`
- As Expected: `90 <= performance_index < 110`
- Below Expected: `70 <= performance_index < 90`
- Struggling: `performance_index < 70`

---

## Business Rules

### Goal Counting Rule

**CRITICAL:** Always use this filter for goals:
```sql
event_type = 'Goal' 
AND event_detail = 'Goal_Scored'
AND event_player_1 = player_id
```

**DO NOT:**
- Count `Shot_Goal` as a goal (it's a shot that scored)
- Count goals where `event_detail != 'Goal_Scored'`
- Count goals for players other than `event_player_1`

### Player Identification

**Lookup Key:**
```python
key = (game_id, team_name, jersey_number)
# Returns: player_id
```

**Player Credit Rules:**
- Only `event_player_1` gets credit for shots, passes, goals
- Assists tracked via `play_detail1='AssistPrimary'/'AssistSecondary'` on PASS/SHOT events
- The assister is `event_player_1` on their assist event

### Time on Ice (TOI)

**Calculation:**
- From `fact_shifts`: `SUM(shift_duration)`
- Units: seconds (convert to MM:SS for display)
- Propagated to event tables via shift joins

**Logical Shifts:**
- Count `DISTINCT logical_shift_number`, not raw shift rows
- Handles overlapping/duplicate shifts

### Foreign Key Relationships

**Key Relationships:**
- `fact_events.game_id` → `dim_schedule.game_id`
- `fact_events.event_player_1` → `dim_player.player_id`
- `fact_shifts.player_id` → `dim_player.player_id`
- `fact_shifts.game_id` → `dim_schedule.game_id`
- `fact_events.shift_id` → `fact_shifts.shift_id` (when available)

### Derived Column Calculations

**Time Columns:**
- `time_start_total_seconds = event_start_min * 60 + event_start_sec`
- `event_running_start = (period-1)*1200 + (1200 - time_start_total_seconds)`
- `duration = time_start_total_seconds - time_end_total_seconds` (clipped >= 0)

**Zone Columns:**
- `home_team_zone` / `away_team_zone` calculated from `zone` and `team_venue`

**Team Columns:**
- `team_venue` = 'home' or 'away' (from team name comparison)
- `team_venue_abv` = 'H' or 'A'

### fact_team_game_stats

**Source:** [CALC] CALC - Calculated from `fact_player_game_stats`  
**ETL Phase:** Phase 4  
**Primary Key:** `team_game_key`  
**Purpose:** Team totals per game

#### Key Columns

| Column | Type | Source | Calculation |
|--------|------|--------|-------------|
| team_game_key | VARCHAR(50) | Explicit | Format: `TG{game_id}{team_id}` |
| game_id | INTEGER | Explicit | Game identifier |
| team_id | VARCHAR(20) | Explicit | Team identifier |
| goals | INTEGER | Calculated | `SUM(goals)` from `fact_player_game_stats` |
| shots | INTEGER | Calculated | `SUM(shots)` from `fact_player_game_stats` |
| sog | INTEGER | Calculated | `SUM(sog)` from `fact_player_game_stats` |
| corsi_for | INTEGER | Calculated | `SUM(corsi_for)` from `fact_player_game_stats` |
| corsi_against | INTEGER | Calculated | `SUM(corsi_against)` from `fact_player_game_stats` |
| cf_pct | DECIMAL(10,4) | Calculated | `corsi_for / (corsi_for + corsi_against) * 100` |

---

### fact_goalie_game_stats

**Source:** [CALC] CALC - Calculated from `fact_events` + `fact_saves`  
**ETL Phase:** Phase 4  
**Primary Key:** `goalie_game_key`  
**Purpose:** Per-game goalie statistics

#### Key Columns

| Column | Type | Source | Calculation | Filter Context |
|--------|------|--------|-------------|----------------|
| goals_against | INTEGER | Derived | `COUNT WHERE event_type='Goal' AND event_detail='Goal_Scored'` | Opponent team, goalie on ice |
| saves | INTEGER | Derived | `COUNT WHERE event_type='Shot' AND event_detail LIKE '%Saved%'` | Goalie's team |
| shots_against | INTEGER | Derived | `COUNT WHERE event_type='Shot'` | Opponent team, goalie on ice |
| save_pct | DECIMAL(10,4) | Calculated | `saves / shots_against * 100` | WHERE `shots_against > 0` |
| goals_saved_above_avg | DECIMAL(10,4) | Calculated | `(save_pct - league_avg_sv_pct) / 100 * shots_against` | - |

**Goalie WAR Calculation:**
```python
GAR_goalie = saves_above_avg × 0.1
           + high_danger_saves × 0.15
           + goals_prevented × 1.0
           + rebound_control × 0.05
           + quality_start_bonus × 0.5

WAR_goalie = GAR_goalie / 4.5
```

---

## QA Tables

### qa_goal_verification

**Source:** [QA] QA - Validation check  
**ETL Phase:** Phase 9  
**Purpose:** Verify goal counts match official counts

#### Key Columns

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| game_id | INTEGER | Explicit | Game identifier |
| official_goals_home | INTEGER | Explicit | Official goal count (home team) |
| official_goals_away | INTEGER | Explicit | Official goal count (away team) |
| calculated_goals_home | INTEGER | Calculated | Calculated goal count (home team) |
| calculated_goals_away | INTEGER | Calculated | Calculated goal count (away team) |
| goal_diff_home | INTEGER | Calculated | `calculated_goals_home - official_goals_home` |
| goal_diff_away | INTEGER | Calculated | `calculated_goals_away - official_goals_away` |
| verification_status | VARCHAR(20) | Calculated | 'PASS' if diff = 0, 'FAIL' otherwise |

---

## Related Documentation

- [DATA.md](DATA.md) - Data lineage and table manifest
- [ETL.md](../etl/ETL.md) - ETL process documentation
- [CALCULATION_FLOWS.md](CALCULATION_FLOWS.md) - Calculation flow diagrams

---

*Last Updated: 2026-01-15*
