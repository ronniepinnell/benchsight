# BENCHSIGHT DATA DICTIONARY & LINEAGE v34.00
## Complete Documentation of 138+ Tables, Every Column, and Data Sources

---

# PART 1: SYSTEM OVERVIEW

## 1.1 Architecture Summary

BenchSight is a hockey analytics ETL system that transforms raw game data into 138+ interconnected tables for analytics and visualization.

### Data Flow:
```
RAW DATA SOURCES                    ETL PHASES                          OUTPUT
─────────────────────────────────────────────────────────────────────────────────
BLB_TABLES.xlsx ──────────────┐
  ├── dim_player (roster)     │
  ├── dim_team                 │    PHASE 1: Load BLB Tables
  ├── dim_schedule            ├──► (src/core/base_etl.py)
  ├── dim_season              │         │
  ├── fact_gameroster         │         ▼
  └── fact_leadership         │
                              │    PHASE 2: Build Player Lookup
                              │    (game_id, team, number) → player_id
Tracking Excel Files ─────────┤         │
  {game_id}_tracking.xlsx     │         ▼
  ├── events sheet            │
  └── shifts sheet            ├──► PHASE 3: Load Tracking Data ──►   fact_event_players
                              │         │                              fact_shifts
                              │         ▼
                              │    PHASE 3B: Static Dimensions ──►    58 dim_* tables
                              │    (src/tables/dimension_tables.py)
                              │         │
                              │         ▼
                              │    PHASE 4: Core Player Stats ──►     fact_player_game_stats (325+ cols)
                              │    (src/tables/core_facts.py)          fact_team_game_stats
                              │                                        fact_goalie_game_stats
                              │         │
                              │         ▼
                              │    PHASE 4B: Shift Analytics ──►      fact_h2h
                              │    (src/tables/shift_analytics.py)    fact_wowy
                              │                                        fact_line_combos
                              │         │
                              │         ▼
                              │    PHASE 4C-D: Remaining Facts ──►    30+ analytics tables
                              │    (src/tables/remaining_facts.py)
                              │         │
                              │         ▼
                              │    PHASE 5-11: Advanced ──►           Extended analytics
                              │    QA, XY coords, Macro stats          ML features
                              │                                        Career aggregations
                              └─────────────────────────────────────────────────────────

```

## 1.2 Key Prefixes

| Prefix | Description | Example |
|--------|-------------|---------|
| EV | Event ID | EV1896901000 |
| SH | Shift ID | SH1896900001 |
| LV | Linked Event Key | LV1896909001 |
| SQ | Sequence Key | SQ1896905001 |
| PL | Play Key | PL1896906001 |
| ZC | Zone Change Key | ZC1896900001 |
| TV | Tracking Event Key | TV1896901000 |

**Key Format:** `{PREFIX}{game_id}{index:05d}`

---

# PART 2: DIMENSION TABLES (58 Tables)

## 2.1 Core Entity Dimensions (from BLB_TABLES.xlsx)

### dim_player
**Source:** BLB_TABLES.xlsx → dim_player sheet
**Primary Key:** player_id
**ETL Location:** `src/core/base_etl.py:load_blb_tables()` line 951

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| player_id | string | BLB | Unique player identifier (e.g., "PL00001") |
| player_full_name | string | BLB | Full name of player |
| player_name | string | BLB | Display name |
| player_first_name | string | BLB | First name |
| player_last_name | string | BLB | Last name |
| player_primary_position | string | BLB | Primary position (Forward/Defense/Goalie) |
| player_dob | date | BLB | Date of birth |
| player_image | string | BLB | URL to player photo |
| current_team | string | BLB | Current team name |
| current_team_id | string | BLB | Current team ID |
| current_skill_rating | int | BLB | 1-10 skill rating |
| norad_player | string | BLB | NORAD player flag (Y/N) |

### dim_team
**Source:** BLB_TABLES.xlsx → dim_team sheet (filtered to NORAD teams)
**Primary Key:** team_id
**ETL Location:** `src/core/base_etl.py:load_blb_tables()` line 1051-1058

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| team_id | string | BLB | Unique team identifier |
| team_name | string | BLB | Full team name |
| team_cd | string | BLB | Team code (3 letters) |
| team_logo | string | BLB | URL to team logo |
| team_color1 | string | BLB | Primary color hex |
| team_color2 | string | BLB | Secondary color hex |
| norad_team | string | BLB | NORAD team flag (Y/N) |

**Filter Applied:** `norad_team = 'Y'` (excludes non-NORAD teams)

### dim_schedule
**Source:** BLB_TABLES.xlsx → dim_schedule sheet
**Primary Key:** game_id
**ETL Location:** `src/core/base_etl.py:load_blb_tables()` line 1060-1070

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| game_id | int | BLB | Unique game identifier |
| season_id | string | BLB | Season identifier (e.g., "N2025S") |
| game_type | string | BLB | Regular/Playoffs |
| game_date | date | BLB | Date of game |
| game_time | time | BLB | Time of game |
| home_team_id | string | BLB | Home team ID |
| home_team_name | string | BLB | Home team name |
| away_team_id | string | BLB | Away team ID |
| away_team_name | string | BLB | Away team name |
| home_total_goals | int | BLB | Final home score |
| away_total_goals | int | BLB | Final away score |
| official_home_goals | int | BLB | Official home score |
| official_away_goals | int | BLB | Official away score |

### dim_season
**Source:** BLB_TABLES.xlsx → dim_season sheet
**Primary Key:** season_id

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| season_id | string | BLB | Season ID (e.g., "N2025S") |
| season | string | BLB | Season display name |
| season_type | string | BLB | Type (Regular/Summer) |
| start_date | date | BLB | Season start date |
| end_date | date | BLB | Season end date |

### dim_league
**Source:** BLB_TABLES.xlsx → dim_league sheet
**Primary Key:** league_id

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| league_id | string | BLB | League identifier |
| league_name | string | BLB | League name |
| league_url | string | BLB | League website URL |

---

## 2.2 Event Classification Dimensions (Code-Generated)

### dim_event_type
**Source:** BLB_TABLES.xlsx OR Code-generated in `src/tables/dimension_tables.py`
**Primary Key:** event_type_id
**ETL Location:** `src/tables/dimension_tables.py:create_dim_event_type()`

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| event_type_id | string | Generated | e.g., "ET01" |
| event_type_code | string | Generated | Event code |
| event_type_name | string | Generated | Display name |

**Values:** Shot, Goal, Pass, Faceoff, Hit, Block, Penalty, Stoppage, Zone_Entry, Zone_Exit, Turnover, etc.

### dim_event_detail
**Source:** BLB_TABLES.xlsx → dim_event_detail sheet
**Primary Key:** event_detail_id

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| event_detail_id | string | BLB | e.g., "ED01" |
| event_detail_code | string | BLB | Normalized code |
| event_detail_name | string | BLB | Display name |

**Values:** Shot_OnNetSaved, Shot_Goal, Shot_Blocked, Shot_Missed, Goal_Scored, Pass_Completed, Pass_Intercepted, etc.

### dim_play_detail
**Source:** BLB_TABLES.xlsx → dim_play_detail sheet
**Primary Key:** play_detail_id

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| play_detail_id | string | BLB | e.g., "PD01" |
| play_detail_code | string | BLB | Normalized code |
| play_detail_name | string | BLB | Display name |

**Values:** AssistPrimary, AssistSecondary, HitBig, HitNormal, BlockedShot, Takeaway, Giveaway, etc.

### dim_player_role
**Source:** Code-generated in `src/tables/dimension_tables.py:create_dim_player_role()`
**Primary Key:** player_role_id

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| player_role_id | string | Generated | e.g., "PR01" |
| player_role_code | string | Generated | Role code |
| player_role_name | string | Generated | Display name |
| side_of_puck | string | Generated | event_team/opp_team |

**Values:**
- PR01-PR06: event_player_1 through event_player_6 (event team skaters)
- PR07: event_goalie (event team goalie)
- PR08-PR13: opp_player_1 through opp_player_6 (opponent skaters)
- PR14: opp_goalie (opponent goalie)

---

## 2.3 Zone & Location Dimensions

### dim_zone
**Source:** Code-generated in `src/tables/dimension_tables.py:create_dim_zone()`
**Primary Key:** zone_id

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| zone_id | string | Generated | e.g., "ZN01" |
| zone_code | string | Generated | Zone code |
| zone_name | string | Generated | Display name |

**Values:** Offensive, Defensive, Neutral

### dim_rink_zone
**Source:** Code-generated with 12 zones in `src/tables/dimension_tables.py:create_dim_rink_zone()`
**Primary Key:** rink_zone_id

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| rink_zone_id | int | Generated | 1-12 |
| rink_zone_code | string | Generated | e.g., "LSH" |
| rink_zone_name | string | Generated | Full zone name |
| x_min | float | Generated | X coordinate minimum |
| x_max | float | Generated | X coordinate maximum |
| y_min | float | Generated | Y coordinate minimum |
| y_max | float | Generated | Y coordinate maximum |

**12 Rink Zones:**
1. LSH - Left Side High Slot
2. CSH - Center Slot High
3. RSH - Right Side High Slot
4. LSL - Left Side Low Slot
5. CSL - Center Slot Low
6. RSL - Right Side Low Slot
7. LC - Left Circle
8. RC - Right Circle
9. LP - Left Point
10. RP - Right Point
11. BN - Behind Net
12. NZ - Neutral Zone

### dim_danger_zone
**Source:** Code-generated in `src/tables/dimension_tables.py:create_dim_danger_zone()`
**Primary Key:** danger_zone_id

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| danger_zone_id | string | Generated | e.g., "DZ01" |
| danger_zone_code | string | Generated | Code |
| danger_zone_name | string | Generated | Display name |
| xg_base | float | Generated | Base xG for zone |

**Values:** high_danger (0.25), medium_danger (0.12), low_danger (0.06), perimeter (0.02)

---

## 2.4 Shot & Pass Dimensions

### dim_shot_type
**Source:** Code-generated in `src/tables/dimension_tables.py:create_dim_shot_type()`
**Primary Key:** shot_type_id

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| shot_type_id | string | Generated | e.g., "ST01" |
| shot_type_code | string | Generated | Code |
| shot_type_name | string | Generated | Display name |
| xg_modifier | float | Generated | xG multiplier |

**Values with xG Modifiers:**
- wrist: 1.0
- slap: 0.95
- snap: 1.05
- backhand: 0.9
- tip: 1.15
- deflection: 1.1
- one_timer: 1.4

### dim_shot_outcome
**Source:** Code-generated
**Primary Key:** shot_outcome_id

**Values:** goal, save, miss, block, post

### dim_pass_type
**Source:** Code-generated in `src/tables/dimension_tables.py:create_dim_pass_type()`
**Primary Key:** pass_type_id

**Values:** direct, stretch, bank, rim, saucer, chip, drop

### dim_pass_outcome
**Source:** Code-generated
**Primary Key:** pass_outcome_id

**Values:** completed, intercepted, incomplete, deflected

---

## 2.5 Strength & Situation Dimensions

### dim_strength
**Source:** Code-generated in `src/tables/dimension_tables.py:create_dim_strength()`
**Primary Key:** strength_id

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| strength_id | string | Generated | e.g., "5v5" |
| strength_code | string | Generated | Same as ID |
| strength_name | string | Generated | Display name |
| situation | string | Generated | EV/PP/PK/EN |

**Values:** 5v5, 5v4, 4v5, 5v3, 3v5, 4v4, 3v3, 6v5, 5v6, 6v4, 4v6

### dim_situation
**Source:** Code-generated
**Primary Key:** situation_id

**Values:** EV (Even Strength), PP (Power Play), PK (Penalty Kill), EN (Empty Net)

### dim_game_state
**Source:** Code-generated
**Primary Key:** game_state_id

**Values:** leading, trailing, tied, close_game (within 1)

---

## 2.6 Shift Analysis Dimensions

### dim_shift_start_type
**Source:** Code-generated
**Primary Key:** shift_start_type_id

**Values:** faceoff, on_the_fly, period_start, power_play_start, penalty_kill_start

### dim_shift_stop_type
**Source:** Code-generated
**Primary Key:** shift_stop_type_id

**Values:** line_change, period_end, goal_scored, goal_against, penalty_taken, stoppage

### dim_shift_slot
**Source:** Code-generated
**Primary Key:** shift_slot_id

**Values:** first_line, second_line, third_line, fourth_line, top_pair, second_pair, third_pair

### dim_shift_duration
**Source:** Code-generated
**Primary Key:** shift_duration_id

**Values:** short (<30s), normal (30-60s), long (60-90s), extended (>90s)

### dim_shift_quality_tier
**Source:** Code-generated
**Primary Key:** shift_quality_tier_id

**Values:** elite, strong, neutral, weak, poor

---

## 2.7 Rating & Comparison Dimensions

### dim_rating
**Source:** Code-generated
**Primary Key:** rating_id

**Values:** 1-10 (skill ratings)

### dim_composite_rating
**Source:** Code-generated
**Primary Key:** composite_rating_id

**Values:** Combinations like "8v5" (rating 8 player vs rating 5 player)

### dim_competition_tier
**Source:** Code-generated
**Primary Key:** competition_tier_id

**Values:** elite (8-10), strong (6-7), average (4-5), weak (1-3)

### dim_comparison_type
**Source:** Code-generated
**Primary Key:** comparison_type_id

**Values:** vs_higher_rated, vs_same_rated, vs_lower_rated

---

## 2.8 Time & Period Dimensions

### dim_period
**Source:** Code-generated
**Primary Key:** period_id

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| period_id | int | Generated | 1, 2, 3, 4 (OT) |
| period_name | string | Generated | "1st", "2nd", "3rd", "OT" |
| period_length_seconds | int | Generated | 1200 (20 min) |

### dim_time_bucket
**Source:** Code-generated
**Primary Key:** time_bucket_id

**Values:** early_period (0-5 min), mid_period (5-15 min), late_period (15-20 min), final_minute (19-20 min)

---

## 2.9 Other Classification Dimensions

### dim_stoppage_type
**Values:** offside, icing, puck_out, goalie_freeze, penalty, timeout, tv_timeout

### dim_giveaway_type
**Values:** bad_pass, puck_handling, cleared_into_opponent, errant_shot

### dim_takeaway_type
**Values:** stick_check, body_check, interception, loose_puck

### dim_turnover_type
**Values:** offensive_zone, defensive_zone, neutral_zone

### dim_turnover_quality
**Values:** forced, unforced, neutral

### dim_zone_entry_type
**Values:** carry (Carried), dump (Dump_In), pass, failed

### dim_zone_exit_type
**Values:** carry (Carried), dump (Dump_Out), pass, clear, failed

### dim_zone_outcome
**Values:** successful, failed, neutral

### dim_assist_type
**Values:** primary, secondary

### dim_net_location
**Values:** glove_side, blocker_side, five_hole, high_glove, high_blocker, short_side, far_side

### dim_save_outcome
**Values:** freeze, rebound_controlled, rebound_opponent, goal

---

# PART 3: CORE FACT TABLES

## 3.1 fact_event_players (Event-Player Grain)
**Source:** Tracking Excel files → events sheet
**Primary Key:** event_id + player_id (composite)
**Grain:** One row per player per event
**ETL Location:** `src/core/base_etl.py:load_tracking_data()` lines 1145-1384

### Key Columns:
| Column | Type | Source | Calculation/Derivation |
|--------|------|--------|------------------------|
| event_id | string | Derived | `format_key('EV', game_id, event_index)` |
| game_id | int | Tracking | Raw from Excel |
| player_id | string | Derived | Lookup from (game_id, team, player_number) |
| player_game_number | int | Tracking | Raw jersey number |
| player_role | string | Tracking | Normalized via `normalize_player_role()` |
| period | int | Tracking | Raw |
| event_type | string | Tracking | Normalized code |
| event_detail | string | Tracking | Normalized code |
| event_detail_2 | string | Tracking | Secondary detail |
| play_detail1 | string | Tracking | Play-level detail (e.g., "AssistPrimary") |
| play_detail_2 | string | Tracking | Secondary play detail |
| team_venue | string | Tracking | "home" or "away" |
| home_team | string | Tracking | Home team name |
| away_team | string | Tracking | Away team name |
| event_team_zone | string | Tracking | Offensive/Defensive/Neutral |
| strength | string | Tracking | e.g., "5v5" |
| time_start_total_seconds | int | Derived | `event_start_min * 60 + event_start_sec` |
| time_end_total_seconds | int | Derived | `event_end_min * 60 + event_end_sec` |
| duration | int | Derived | `time_start_total_seconds - time_end_total_seconds` |
| event_running_start | int | Derived | `(period-1)*1200 + (1200 - time_start_total_seconds)` |
| is_goal | int | Derived | 1 if event_type='Goal' AND event_detail='Goal_Scored' AND player_role='event_player_1' |
| sequence_key | string | Derived | `format_key('SQ', game_id, sequence_index)` |
| play_key | string | Derived | `format_key('PL', game_id, play_index)` |
| shift_key | string | Derived | `format_key('SH', game_id, shift_index)` |

### FK Columns (added via `add_fact_event_players_fkeys()`):
- period_id → dim_period
- event_type_id → dim_event_type
- event_detail_id → dim_event_detail
- event_detail_2_id → dim_event_detail_2
- play_detail_id → dim_play_detail
- play_detail_2_id → dim_play_detail_2
- player_role_id → dim_player_role
- event_zone_id → dim_zone
- home_zone_id → dim_zone
- away_zone_id → dim_zone
- home_team_id → dim_team
- away_team_id → dim_team
- player_team_id → dim_team
- team_venue_id → dim_venue

---

## 3.2 fact_events (Event Grain)
**Source:** Aggregated from fact_event_players
**Primary Key:** event_id
**Grain:** One row per event
**ETL Location:** `src/builders/events.py:build_fact_events()`

### Key Columns:
| Column | Type | Source | Calculation |
|--------|------|--------|-------------|
| event_id | string | fact_event_players | From event_player_1 row |
| game_id | int | fact_event_players | Direct |
| period | int | fact_event_players | Direct |
| event_type | string | fact_event_players | Direct |
| event_detail | string | fact_event_players | Direct |
| event_player_1_id | string | fact_event_players | Player with role='event_player_1' |
| event_player_1_name | string | dim_player lookup | Mapped from player_id |
| event_player_1_rating | int | fact_event_players | player_rating column |
| event_player_2_id | string | fact_event_players | Player with role='event_player_2' |
| opp_player_1_id | string | fact_event_players | Player with role='opp_player_1' |
| event_player_ids | string | Aggregated | Comma-separated event team player IDs |
| opp_player_ids | string | Aggregated | Comma-separated opponent player IDs |
| time_start_total_seconds | int | fact_event_players | Direct |
| is_goal | int | Derived | 1 if Goal_Scored event |
| strength | string | fact_event_players | Direct |

---

## 3.3 fact_shifts (Shift Grain)
**Source:** Tracking Excel files → shifts sheet
**Primary Key:** shift_id
**Grain:** One row per shift
**ETL Location:** `src/builders/shifts.py:build_fact_shifts()`

### Key Columns:
| Column | Type | Source | Calculation |
|--------|------|--------|-------------|
| shift_id | string | Derived | `format_key('SH', game_id, shift_index)` |
| game_id | int | Tracking | Raw |
| shift_index | int | Tracking | Sequential shift number |
| period | int | Tracking | Period number |
| player_count_home | int | Tracking | Home skaters on ice |
| player_count_away | int | Tracking | Away skaters on ice |
| strength | string | Derived | e.g., "5v5" from player counts |
| shift_start_seconds | int | Tracking | Start time in period |
| shift_end_seconds | int | Tracking | End time in period |
| shift_duration | int | Derived | `shift_start_seconds - shift_end_seconds` |
| home_players | string | Tracking | Comma-separated home player numbers |
| away_players | string | Tracking | Comma-separated away player numbers |
| events_during_shift | int | Derived | Count of events during shift |
| cf | int | Derived | Corsi For during shift |
| ca | int | Derived | Corsi Against during shift |
| gf | int | Derived | Goals For during shift |
| ga | int | Derived | Goals Against during shift |

---

## 3.4 fact_shift_players (Shift-Player Grain)
**Source:** fact_shifts exploded to player level
**Primary Key:** shift_id + player_id (composite)
**Grain:** One row per player per shift
**ETL Location:** `src/builders/shifts.py:build_fact_shift_players()`

### Key Columns:
| Column | Type | Source | Calculation |
|--------|------|--------|-------------|
| shift_id | string | fact_shifts | Direct |
| game_id | int | fact_shifts | Direct |
| player_id | string | Derived | Lookup from player number |
| player_game_number | int | fact_shifts | Parsed from home/away_players |
| team_venue | string | Derived | "home" or "away" |
| period | int | fact_shifts | Direct |
| shift_duration | int | fact_shifts | Direct |
| strength | string | fact_shifts | Direct |
| cf | int | fact_shifts | Direct (attributed to player) |
| ca | int | fact_shifts | Direct |
| gf | int | fact_shifts | Direct |
| ga | int | fact_shifts | Direct |
| opp_player_ids | string | Derived | Players on opposing team during shift |
| avg_opp_rating | float | Derived | Average rating of opponents |
| logical_shift_number | int | Derived | Groups physical shifts into logical units |

---

## 3.5 fact_player_game_stats (Player-Game Grain)
**Source:** Aggregated from fact_event_players + fact_shift_players
**Primary Key:** game_id + player_id (composite)
**Grain:** One row per player per game
**ETL Location:** `src/tables/core_facts.py:build_fact_player_game_stats()`
**Columns:** 325+ columns

### Core Identification:
| Column | Type | Source | Calculation |
|--------|------|--------|-------------|
| game_id | int | Input | Direct |
| player_id | string | Input | Direct |
| player_name | string | dim_player | Lookup |
| team_id | string | fact_gameroster | Lookup |
| team_name | string | fact_gameroster | Lookup |
| season_id | string | dim_schedule | Lookup |
| position | string | fact_shifts | Most common position in game |

### Counting Stats (from fact_event_players where player_role='event_player_1'):
| Column | Type | Calculation |
|--------|------|-------------|
| goals | int | COUNT where event_type='Goal' AND event_detail='Goal_Scored' |
| primary_assists | int | COUNT where play_detail1='AssistPrimary' |
| secondary_assists | int | COUNT where play_detail1='AssistSecondary' |
| assists | int | primary_assists + secondary_assists |
| points | int | goals + assists |
| shots | int | COUNT where event_type='Shot' |
| sog | int | COUNT where event_detail IN ('Shot_OnNetSaved', 'Shot_Goal') |
| shots_blocked | int | COUNT where event_detail='Shot_Blocked' |
| shots_missed | int | COUNT where event_detail IN ('Shot_Missed', 'Shot_MissedPost') |
| hits | int | COUNT where event_type='Hit' |
| blocks | int | COUNT where play_detail1='BlockedShot' |
| takeaways | int | COUNT where event_type='Turnover' AND event_detail='Takeaway' |
| giveaways | int | COUNT where event_type='Turnover' AND event_detail='Giveaway' |
| zone_entries | int | COUNT where event_type='Zone_Entry' |
| zone_exits | int | COUNT where event_type='Zone_Exit' |
| carried_entries | int | COUNT where event_detail_2 LIKE '%Carried%' |
| dump_ins | int | COUNT where event_detail_2 LIKE '%Dump%' |
| fo_wins | int | COUNT where event_type='Faceoff' AND event_detail='Won' |
| fo_losses | int | COUNT where event_type='Faceoff' AND event_detail='Lost' |
| penalties | int | COUNT where event_type='Penalty' |
| pim | int | SUM of penalty_minutes |
| pass_attempts | int | COUNT where event_type='Pass' |
| pass_completed | int | COUNT where event_detail='Pass_Completed' |

### Time Stats (from fact_shift_players):
| Column | Type | Calculation |
|--------|------|-------------|
| toi | int | SUM(shift_duration) in seconds |
| toi_minutes | float | toi / 60 |
| ev_toi | int | SUM where strength IN ('5v5', '4v4', '3v3') |
| pp_toi | int | SUM where strength IN ('5v4', '5v3', '4v3') |
| pk_toi | int | SUM where strength IN ('4v5', '3v5', '3v4') |
| shifts | int | COUNT DISTINCT logical_shift_number |
| avg_shift_length | float | toi / shifts |

### Corsi/Fenwick Stats (from fact_shift_players):
| Column | Type | Calculation |
|--------|------|-------------|
| cf | int | SUM(cf) from shifts (Corsi For) |
| ca | int | SUM(ca) from shifts (Corsi Against) |
| cf_pct | float | cf / (cf + ca) * 100 |
| ff | int | Fenwick For (CF - blocked shots against) |
| fa | int | Fenwick Against |
| ff_pct | float | ff / (ff + fa) * 100 |
| gf | int | SUM(gf) from shifts |
| ga | int | SUM(ga) from shifts |
| gf_pct | float | gf / (gf + ga) * 100 |

### xG Stats:
| Column | Type | Calculation |
|--------|------|-------------|
| xg | float | SUM(xg) for player's shots |
| xg_against | float | SUM(xg) for shots while on ice (against) |
| xg_diff | float | xg - xg_against |
| goals_above_xg | float | goals - xg |

### Strength/Situation Splits (prefixes: ev_, pp_, pk_, en_):
- {prefix}toi_seconds
- {prefix}cf, {prefix}ca, {prefix}cf_pct
- {prefix}gf, {prefix}ga
- {prefix}goals, {prefix}assists, {prefix}points, {prefix}shots
- {prefix}p1_, {prefix}p2_, {prefix}p3_ (period breakdowns for PP/PK)

### Shot Type Breakdown:
- shots_wrist, shots_slap, shots_snap, shots_backhand, shots_tip, shots_deflection
- goals_wrist, goals_slap, goals_snap, etc.
- shot_type_pct_{type}

### Pass Type Breakdown:
- passes_direct, passes_stretch, passes_bank, passes_rim, passes_saucer
- passes_completed_{type}, pass_type_pct_{type}

### Playmaking Stats:
| Column | Type | Calculation |
|--------|------|-------------|
| shot_assists | int | Passes that led directly to shots |
| shot_assist_rate | float | shot_assists / pass_attempts |
| primary_shot_assists | int | Passes directly before shot |
| secondary_shot_assists | int | Passes 2 events before shot |
| xg_from_passes | float | xG generated from passes |
| playmaking_value | float | Composite playmaking score |

### Pressure/Poise Stats:
- events_under_pressure, success_under_pressure, pressure_success_rate
- pressured_turnovers, pressured_passes_completed
- under_pressure_shots, under_pressure_goals

### Sequence Analytics:
- sequences_involved, sequences_started, sequences_finished
- sequences_to_shot, sequences_to_goal
- sequence_involvement_rate

### Competition Tier Performance:
- vs_elite_toi, vs_elite_cf_pct
- vs_strong_toi, vs_strong_cf_pct
- vs_average_toi, vs_average_cf_pct
- vs_weak_toi, vs_weak_cf_pct

### Game State Splits:
- leading_toi, leading_cf_pct, leading_gf
- trailing_toi, trailing_cf_pct, trailing_gf
- tied_toi, tied_cf_pct, tied_gf
- close_game_toi, close_game_cf_pct

### Linemate Analysis:
- unique_linemates, top_linemate_id, top_linemate_toi
- top_linemate_chemistry (CF% when together)

### Time Bucket Analysis:
- early_period_goals, early_period_shots
- mid_period_goals, mid_period_shots
- late_period_goals, late_period_shots
- final_minute_goals, final_minute_shots

### Rebound/Second Chance:
- rebounds_generated, rebounds_scored
- crash_net_attempts, garbage_goals
- second_chance_shots, second_chance_goals

### Rating/Impact Metrics:
| Column | Type | Calculation |
|--------|------|-------------|
| game_score | float | NHL-style game score formula |
| war | float | Wins Above Replacement |
| gar | float | Goals Above Replacement |
| offensive_rating | float | Offensive contribution score |
| defensive_rating | float | Defensive contribution score |
| adjusted_rating | float | What skill rating player "played like" |

### WAR/GAR Calculation (from `src/tables/core_facts.py`):
```python
GAR_WEIGHTS = {
    'goals': 1.0,
    'primary_assists': 0.7,
    'secondary_assists': 0.4,
    'shots_generated': 0.015,
    'xg_generated': 0.8,
    'takeaways': 0.05,
    'blocked_shots': 0.02,
    'defensive_zone_exits': 0.03,
    'cf_above_avg': 0.02,
    'zone_entry_value': 0.04,
    'shot_assists': 0.3,
    'pressure_success': 0.02,
}

GOALS_PER_WIN = 4.5
war = gar / GOALS_PER_WIN
```

---

## 3.6 fact_team_game_stats (Team-Game Grain)
**Source:** Aggregated from fact_player_game_stats
**Primary Key:** game_id + team_id (composite)
**Grain:** One row per team per game
**ETL Location:** `src/builders/team_stats.py:build_fact_team_game_stats()`

### Key Columns:
| Column | Type | Calculation |
|--------|------|-------------|
| game_id | int | Direct |
| team_id | string | Direct |
| team_name | string | Lookup |
| season_id | string | From schedule |
| venue | string | "home" or "away" |
| goals | int | SUM(goals) for team players |
| assists | int | SUM(assists) for team players |
| shots | int | SUM(shots) for team players |
| sog | int | SUM(sog) for team players |
| pim | int | SUM(pim) for team players |
| cf | int | Team Corsi For |
| ca | int | Team Corsi Against |
| cf_pct | float | Team CF% |
| xg | float | Team expected goals |
| xg_against | float | Expected goals against |
| pp_opportunities | int | Power play chances |
| pp_goals | int | Power play goals |
| pp_pct | float | pp_goals / pp_opportunities * 100 |
| pk_opportunities | int | Penalty kills |
| pk_goals_against | int | Goals allowed on PK |
| pk_pct | float | (1 - pk_goals_against/pk_opportunities) * 100 |
| fo_wins | int | Team faceoff wins |
| fo_losses | int | Team faceoff losses |
| fo_pct | float | Team faceoff % |
| zone_entries | int | Team zone entries |
| zone_exits | int | Team zone exits |
| hits | int | Team hits |
| blocks | int | Team blocked shots |
| win | int | 1 if team won, 0 if lost |

---

## 3.7 fact_goalie_game_stats (Goalie-Game Grain)
**Source:** fact_event_players + special goalie calculations
**Primary Key:** game_id + player_id (composite)
**Grain:** One row per goalie per game
**ETL Location:** `src/tables/core_facts.py:build_fact_goalie_game_stats()`

### Core Stats:
| Column | Type | Calculation |
|--------|------|-------------|
| game_id | int | Direct |
| player_id | string | Direct |
| player_name | string | Lookup |
| team_id | string | From roster |
| team_name | string | Lookup |
| shots_against | int | COUNT shots on goalie |
| goals_against | int | COUNT goals scored on goalie |
| saves | int | shots_against - goals_against |
| save_pct | float | saves / shots_against * 100 |

### Save Type Breakdown:
- saves_butterfly, saves_pad, saves_glove, saves_blocker
- saves_chest, saves_stick, saves_scramble
- saves_freeze (frozen puck), saves_rebound (gave rebound)

### High Danger Analysis:
| Column | Type | Calculation |
|--------|------|-------------|
| hd_shots_against | int | High danger shots against |
| hd_goals_against | int | High danger goals against |
| hd_saves | int | hd_shots_against - hd_goals_against |
| hd_save_pct | float | hd_saves / hd_shots_against * 100 |

### Rebound Control:
- rebounds_team_recovered, rebounds_opp_recovered
- rebounds_shot_generated (rebounds that became shots)
- rebounds_flurry_generated (rebounds that created scrambles)
- rebound_control_rate | float | rebounds_team_recovered / total_rebounds * 100

### Period Breakdown:
- p1_saves, p1_goals_against, p1_shots
- p2_saves, p2_goals_against, p2_shots
- p3_saves, p3_goals_against, p3_shots

### Time Bucket Analysis:
- early_period_saves/ga, mid_period_saves/ga
- late_period_saves/ga, final_minute_saves/ga

### Situation Analysis:
- rush_saves, rush_goals_against (quick attacks)
- quick_attack_saves, quick_attack_ga
- set_play_saves, set_play_ga (sustained pressure)
- single_shot_saves, multi_shot_saves, sustained_pressure_saves

### Location Analysis:
- glove_side_saves/goals, blocker_side_saves/goals
- five_hole_saves/goals

### Quality Metrics:
| Column | Type | Calculation |
|--------|------|-------------|
| is_quality_start | int | 1 if save_pct >= 90% |
| is_bad_start | int | 1 if save_pct < 85% |
| gsaa | float | Goals Saved Above Average |
| goalie_war | float | Goalie WAR |
| goalie_game_score | float | Goalie game score |
| overall_game_rating | float | 1-10 game rating |
| clutch_rating | float | Late-game/close-game performance |
| pressure_rating | float | Performance under sustained pressure |
| rebound_rating | float | Rebound control quality |

### GOALIE WAR Calculation:
```python
GOALIE_GAR_WEIGHTS = {
    'saves_above_avg': 0.1,      # Per save above expected
    'high_danger_saves': 0.15,   # HD saves worth more
    'goals_prevented': 1.0,      # GSAx directly
    'rebound_control': 0.05,     # Freeze vs rebound
    'quality_start_bonus': 0.5,  # Bonus for QS
}
```

---

# PART 4: ANALYTICS FACT TABLES

## 4.1 Shift Analytics Tables

### fact_h2h (Head-to-Head)
**Source:** fact_shift_players
**Grain:** player_1_id + player_2_id + game_id
**ETL:** `src/tables/shift_analytics.py:create_fact_h2h()`

| Column | Type | Calculation |
|--------|------|-------------|
| h2h_key | string | `{player_1_id}_{player_2_id}_{game_id}` |
| game_id | int | Direct |
| player_1_id | string | Direct |
| player_2_id | string | Direct |
| same_team | bool | True if teammates |
| toi_together | int | Seconds on ice together |
| cf_together | int | Corsi For when together |
| ca_together | int | Corsi Against when together |
| cf_pct_together | float | cf / (cf+ca) * 100 |
| gf_together | int | Goals For together |
| ga_together | int | Goals Against together |
| shifts_together | int | Count of shifts together |

### fact_wowy (With Or Without You)
**Source:** fact_shift_players
**Grain:** player_id + comparison_player_id + game_id
**ETL:** `src/tables/shift_analytics.py:create_fact_wowy()`

| Column | Type | Calculation |
|--------|------|-------------|
| wowy_key | string | `{player_id}_{comp_id}_{game_id}` |
| game_id | int | Direct |
| player_id | string | Subject player |
| comparison_player_id | string | Reference player |
| toi_with | int | TOI when playing together |
| toi_without | int | TOI when apart |
| cf_pct_with | float | CF% when together |
| cf_pct_without | float | CF% when apart |
| cf_pct_impact | float | cf_pct_with - cf_pct_without |
| gf_with | int | Goals For when together |
| ga_with | int | Goals Against when together |
| gf_without | int | Goals For when apart |
| ga_without | int | Goals Against when apart |

### fact_line_combos
**Source:** fact_shift_players
**Grain:** Line combination + game_id
**ETL:** `src/tables/shift_analytics.py:create_fact_line_combos()`

| Column | Type | Calculation |
|--------|------|-------------|
| line_combo_key | string | Sorted player IDs + game |
| game_id | int | Direct |
| player_1_id | string | First player (alphabetically) |
| player_2_id | string | Second player |
| player_3_id | string | Third player (if forward line) |
| line_type | string | "forward_line" or "defense_pair" |
| toi | int | TOI as a unit |
| cf | int | Corsi For |
| ca | int | Corsi Against |
| cf_pct | float | Line CF% |
| gf | int | Goals For |
| ga | int | Goals Against |
| xgf | float | Expected Goals For |
| xga | float | Expected Goals Against |
| chemistry_score | float | Performance vs expected |

### fact_shift_quality
**Source:** fact_shift_players
**Grain:** shift_id + player_id
**ETL:** `src/tables/shift_analytics.py:create_fact_shift_quality()`

| Column | Type | Calculation |
|--------|------|-------------|
| shift_quality_key | string | `{shift_id}_{player_id}` |
| shift_id | string | Direct |
| game_id | int | Direct |
| player_id | string | Direct |
| shift_duration | int | Shift length |
| duration_tier | string | "short"/"normal"/"long"/"extended" |
| events_in_shift | int | Events during shift |
| cf | int | Corsi For |
| ca | int | Corsi Against |
| net_cf | int | cf - ca |
| quality_tier | string | "elite"/"strong"/"neutral"/"weak"/"poor" |
| start_type | string | "faceoff"/"on_the_fly"/etc |
| stop_type | string | "line_change"/"goal"/etc |
| avg_opp_rating | float | Opponent quality faced |

### fact_shift_quality_logical
**Source:** fact_shift_players (grouped by logical_shift_number)
**Grain:** game_id + player_id + logical_shift_number
**Purpose:** Avoids double-counting by grouping physical shifts into logical units

---

## 4.2 Event Analytics Tables

### fact_scoring_chances
**Source:** fact_events
**Grain:** event_id (filtered to scoring chances)
**ETL:** `src/tables/event_analytics.py:create_fact_scoring_chances()`

| Column | Type | Calculation |
|--------|------|-------------|
| event_id | string | Direct |
| game_id | int | Direct |
| player_id | string | Shooter |
| team_id | string | Shooter's team |
| period | int | Direct |
| time_seconds | int | Time in period |
| danger_zone | string | "high"/"medium"/"low"/"perimeter" |
| xg | float | Expected goals |
| shot_type | string | Type of shot |
| is_goal | int | 1 if scored |
| is_rush | int | 1 if rush play |
| is_rebound | int | 1 if rebound |
| goalie_screened | int | 1 if screen |

### fact_shot_danger
**Source:** fact_events + fact_event_players
**Grain:** event_id (shots only)
**ETL:** `src/tables/event_analytics.py:create_fact_shot_danger()`

| Column | Type | Calculation |
|--------|------|-------------|
| shot_id | string | event_id |
| game_id | int | Direct |
| player_id | string | Shooter |
| shot_distance | float | Distance to net (XY calc or heuristic) |
| shot_angle | float | Angle to net |
| shot_x | float | X coordinate |
| shot_y | float | Y coordinate |
| rink_zone_id | int | Rink zone lookup |
| danger_zone | string | "high"/"medium"/"low"/"perimeter" |
| xg | float | Expected goals probability (0.0-0.95) |

**xG Calculation (from code):**
```python
# XY Method:
Base by distance: <15ft=0.35, 15-25ft=0.18, 25-35ft=0.10, >35ft=0.05
Angle adjustment: * cos(angle * 0.8), min 0.3
Shot type: wrist=1.0, slap=0.9, snap=1.05, backhand=0.7, deflect=1.2, tip=1.3
Rush: 1.15x
Rebound: 1.25x
Max cap: 0.95

# Heuristic Method (no XY):
High danger base: 0.25
Medium danger base: 0.12
Low danger base: 0.06
Perimeter base: 0.02
Plus modifiers as above
```

### fact_linked_events
**Source:** fact_event_players (grouped by linked_event_key)
**Grain:** linked_event_key
**ETL:** `src/tables/event_analytics.py:create_fact_linked_events()`

| Column | Type | Calculation |
|--------|------|-------------|
| linked_event_key | string | Chain identifier |
| game_id | int | Direct |
| event_count | int | Events in chain |
| event_1_type | string | First event type |
| event_1_player_id | string | First event player |
| event_2_type | string | Second event type |
| ... | ... | Up to event_5 |
| play_chain | string | "entry -> pass -> shot" |

### fact_rush_events
**Source:** fact_events
**Grain:** game_id + entry_event_id + shot_event_id
**ETL:** `src/tables/event_analytics.py:create_fact_rush_events()`

**Rush Definition:** Zone entry followed by shot within 5 events

| Column | Type | Calculation |
|--------|------|-------------|
| game_id | int | Direct |
| entry_event_id | string | Zone entry event |
| shot_event_id | string | Resulting shot |
| events_to_shot | int | Events from entry to shot |
| entry_type | string | "carry"/"dump"/"other" |
| rush_type | string | "controlled"/"dump_chase"/"other" |
| is_goal | bool | Goal on shot |

### fact_shot_chains
**Source:** fact_events + fact_event_players
**Grain:** shot_event_id
**ETL:** `src/chains/shot_chain_builder.py`

| Column | Type | Calculation |
|--------|------|-------------|
| shot_chain_key | string | Direct |
| shot_event_id | string | Shot event |
| game_id | int | Direct |
| chain_length | int | Events in sequence |
| entry_type | string | How possession started |
| passes_before_shot | int | Pass count |
| time_in_zone | int | Seconds in offensive zone |
| primary_passer_id | string | Last pass before shot |
| secondary_passer_id | string | 2nd-to-last pass |
| xg | float | Shot xG |
| is_goal | int | 1 if scored |

### fact_possession_time
**Source:** fact_event_players
**Grain:** game_id + player_id
**ETL:** `src/tables/event_analytics.py:create_fact_possession_time()`

| Column | Type | Calculation |
|--------|------|-------------|
| possession_key | string | `POSS_{game_id}_{player_id}` |
| game_id | int | Direct |
| player_id | string | Direct |
| zone_entries | int | COUNT entries (player_1 only) |
| zone_exits | int | COUNT exits |
| ozone_entries | int | Offensive zone entries |
| dzone_entries | int | Defensive zone entries |
| possession_events | int | COUNT pass/shot/deke events |
| estimated_possession_seconds | int | possession_events * 3 |

---

## 4.3 Zone Analysis Tables

### fact_zone_entries
**Source:** fact_events filtered to Zone_Entry
**Grain:** event_id
**ETL:** `src/tables/remaining_facts.py`

| Column | Type | Calculation |
|--------|------|-------------|
| event_id | string | Direct |
| game_id | int | Direct |
| player_id | string | Entry player |
| entry_type | string | "carry"/"dump"/"pass"/"failed" |
| outcome | string | "successful"/"failed" |
| possession_retained | int | 1 if team kept puck |
| shot_generated | int | 1 if resulted in shot |
| goal_generated | int | 1 if resulted in goal |

### fact_zone_entry_summary
**Source:** Aggregated fact_zone_entries
**Grain:** player_id + game_id

| Column | Type | Calculation |
|--------|------|-------------|
| player_id | string | Direct |
| game_id | int | Direct |
| zone_entries | int | Total entries |
| carry_ins | int | Carried entries |
| dump_ins | int | Dump entries |
| successful_entries | int | Entries with possession |
| entry_success_pct | float | successful / total * 100 |
| shots_per_entry | float | Shots generated / entries |

### fact_zone_exits / fact_zone_exit_summary
**Similar structure to entries**

### fact_team_zone_time
**Source:** fact_shift_players aggregated
**Grain:** team_id + game_id

| Column | Type | Calculation |
|--------|------|-------------|
| team_id | string | Direct |
| game_id | int | Direct |
| offensive_zone_time | int | Seconds in OZ |
| defensive_zone_time | int | Seconds in DZ |
| neutral_zone_time | int | Seconds in NZ |
| oz_pct | float | oz_time / total * 100 |
| dz_pct | float | dz_time / total * 100 |

---

## 4.4 Macro/Aggregation Tables

### fact_player_season_stats
**Source:** Aggregated fact_player_game_stats
**Grain:** player_id + season_id + game_type
**ETL:** `src/tables/macro_stats.py:create_fact_player_season_stats()`

**GAME_TYPE_SPLITS:** ['All', 'Regular', 'Playoffs'] (from game_type_aggregator.py)

| Column | Type | Calculation |
|--------|------|-------------|
| player_season_key | string | `{player_id}_{season_id}_{game_type}` |
| player_id | string | Direct |
| season_id | string | Direct |
| game_type | string | "All"/"Regular"/"Playoffs" |
| games_played | int | COUNT DISTINCT game_id |
| goals | int | SUM(goals) |
| assists | int | SUM(assists) |
| points | int | SUM(points) |
| ... | ... | All game stats summed/averaged |
| goals_per_game | float | goals / games_played |
| points_per_game | float | points / games_played |

### fact_player_career_stats
**Source:** Aggregated fact_player_season_stats
**Grain:** player_id + season_id + game_type

Same columns with career_ prefix, cumulative through that season.

### fact_player_season_stats_basic / fact_player_career_stats_basic
**Source:** fact_gameroster (official league data only)
**Purpose:** Basic stats from official rosters (not tracking)

### fact_goalie_season_stats / fact_goalie_career_stats
**Source:** Aggregated fact_goalie_game_stats
**Grain:** player_id + season_id + game_type

Similar to player stats but with goalie-specific columns.

### fact_team_season_stats / fact_team_season_stats_basic
**Source:** dim_schedule + fact_gameroster
**Grain:** team_id + season_id + game_type

| Column | Type | Calculation |
|--------|------|-------------|
| team_season_key | string | `{team_id}_{season_id}_{game_type}` |
| team_id | string | Direct |
| games_played | int | COUNT games |
| wins | int | get_team_record_from_schedule() |
| losses | int | get_team_record_from_schedule() |
| ties | int | get_team_record_from_schedule() |
| points | int | (wins * 2) + ties |
| win_pct | float | points / (games * 2) * 100 |
| goals_for | int | SUM(goals) |
| goals_against | int | SUM(goals_against) |
| goal_diff | int | goals_for - goals_against |

---

## 4.5 Other Analytics Tables

### fact_player_period_stats
**Grain:** player_id + game_id + period
**Purpose:** Period-by-period breakdown

### fact_period_momentum / fact_time_period_momentum
**Grain:** game_id + period + team_id
**Purpose:** Momentum tracking by time window

### fact_player_micro_stats
**Grain:** player_id + game_id + stat_category
**Purpose:** Detailed stat breakdowns (shot zones, event distributions)

### fact_player_qoc_summary
**Grain:** player_id + game_id
**Purpose:** Quality of Competition summary

| Column | Type | Calculation |
|--------|------|-------------|
| qoc_key | string | Direct |
| player_id | string | Direct |
| game_id | int | Direct |
| avg_opp_rating | float | AVG(opponent skill ratings) |
| avg_own_rating | float | AVG(teammate skill ratings) |
| rating_diff | float | avg_opp_rating - avg_own_rating |
| shifts_tracked | int | Shifts with rating data |

### fact_player_trends
**Grain:** player_id + game_id (sequential)
**Purpose:** Game-to-game performance trends

### fact_player_stats_long
**Grain:** player_id + game_id + stat_name
**Purpose:** Long format for pivoting

### fact_matchup_summary / fact_matchup_performance / fact_head_to_head
**Grain:** player_id + opp_player_id + game_id
**Purpose:** 1v1 matchup analysis

### fact_special_teams_summary
**Grain:** player_id + game_id
**Purpose:** PP/PK specific performance

### fact_highlights
**Grain:** event_id
**Purpose:** Notable plays for highlight reels

### fact_video
**Grain:** event_id
**Purpose:** Video metadata linkage

### fact_suspicious_stats
**Grain:** event_id or game_id
**Purpose:** Data quality flags

---

# PART 5: QA & LOOKUP TABLES

### qa_goal_accuracy
**Purpose:** Compare tracked goals vs official scores

### qa_scorer_comparison
**Purpose:** Compare tracked scorers vs official records

### qa_data_completeness
**Purpose:** Track data coverage by game

### qa_suspicious_stats
**Purpose:** Flag outliers and data issues

### lookup_player_game_rating
**Purpose:** Quick player rating lookup by game

---

# PART 6: FORMULAS REFERENCE

## 6.1 Formula Registry
**Location:** `src/formulas/player_stats_formulas.py`

### Percentage Formulas:
```python
'shooting_pct': goals / sog * 100
'fo_pct': fo_wins / (fo_wins + fo_losses) * 100
'pass_completion_pct': pass_completed / pass_attempts * 100
'zone_entry_success_pct': successful_entries / zone_entries * 100
```

### Per-60 Formulas:
```python
'goals_per_60': goals / toi_minutes * 60
'points_per_60': points / toi_minutes * 60
'cf_per_60': cf / toi_minutes * 60
'shots_per_60': shots / toi_minutes * 60
```

### Impact Metrics:
```python
'plus_minus': gf - ga
'cf_rel': player_cf_pct - team_cf_pct_without_player
'xg_diff': xg - xg_against
'goals_above_xg': goals - xg
```

### WAR Components:
```python
offensive_gar = (
    goals * 1.0 +
    primary_assists * 0.7 +
    secondary_assists * 0.4 +
    shots * 0.015 +
    xg * 0.8 +
    shot_assists * 0.3
)

defensive_gar = (
    takeaways * 0.05 +
    blocks * 0.02 +
    zone_exits * 0.03 +
    (cf_pct - 50) * 0.02
)

total_gar = offensive_gar + defensive_gar
war = total_gar / 4.5  # Goals per win
```

---

# PART 7: UI DASHBOARD DATA SOURCES

## 7.1 Pages → Tables Mapping

| Page | Primary Table | Supporting Tables |
|------|---------------|-------------------|
| /players | dim_player, v_rankings_players_current | fact_player_season_stats_basic |
| /teams | dim_team, v_standings_current | - |
| /standings | v_standings_current, dim_schedule | dim_team, fact_team_season_stats_basic |
| /leaders | v_leaderboard_points, v_leaderboard_goalie_* | dim_player |
| /goalies | v_leaderboard_goalie_* | v_rankings_goalies_current |
| /games | dim_schedule | fact_game_status, fact_team_game_stats |
| /players/[id] | dim_player, fact_player_game_stats | fact_shot_xy, dim_schedule |
| /goalies/[id] | dim_player, fact_goalie_game_stats | v_detail_goalie_games |
| /tracker | stage_dim_schedule | fact_events, fact_shifts |
| /team/[name] | dim_team, v_standings_current | v_rankings_players_current |

## 7.2 Views Used by UI

### Standings/Rankings:
- v_standings_current
- v_rankings_players_current
- v_rankings_goalies_current
- v_standings_all_seasons

### Leaderboards:
- v_leaderboard_points
- v_leaderboard_goals
- v_leaderboard_assists
- v_leaderboard_goalie_gaa
- v_leaderboard_goalie_wins

### Detail Views:
- v_recent_games
- v_detail_player_games
- v_detail_goalie_games
- v_compare_players
- v_summary_player_career
- v_summary_goalie_career
- v_summary_league

---

# PART 8: KEY UTILITIES & FUNCTIONS

## 8.1 Key Generation
**Location:** `src/core/key_utils.py`

```python
def format_key(prefix: str, game_id, index) -> str:
    """
    Create: {prefix}{gameid}{index:05d}
    Example: format_key('EV', 18969, 1000) -> 'EV1896901000'
    """
```

## 8.2 Goal Detection
**Location:** `src/calculations/goals.py`

```python
def get_goal_filter(events_df: pd.DataFrame) -> pd.Series:
    """
    SINGLE SOURCE OF TRUTH for goal identification.
    Goals ONLY via: event_type='Goal' AND event_detail='Goal_Scored'
    """
    return (
        (events_df['event_type'] == 'Goal') &
        (events_df['event_detail'] == 'Goal_Scored')
    )
```

## 8.3 Corsi/Fenwick Detection
**Location:** `src/calculations/corsi.py`

```python
def is_corsi_event(event_type: str, event_detail: str) -> bool:
    """Corsi = all shot attempts (SOG + blocked + missed)"""
    return is_sog_event(...) or is_blocked_shot(...) or is_missed_shot(...)

def is_fenwick_event(event_type: str, event_detail: str) -> bool:
    """Fenwick = unblocked shots (SOG + missed)"""
    return is_sog_event(...) or is_missed_shot(...)
```

## 8.4 Game Type Splits
**Location:** `src/utils/game_type_aggregator.py`

```python
GAME_TYPE_SPLITS = ['All', 'Regular', 'Playoffs']

def add_game_type_to_df(df, schedule):
    """Add game_type column from schedule"""

def get_team_record_from_schedule(schedule, team_id, season_id, game_type):
    """Calculate W-L-T record"""
```

---

# APPENDIX A: Complete Table List (138 Tables)

## Dimension Tables (58):
1. dim_player
2. dim_team
3. dim_schedule
4. dim_season
5. dim_league
6. dim_playerurlref
7. dim_randomnames
8. dim_event_type
9. dim_event_detail
10. dim_event_detail_2
11. dim_play_detail
12. dim_play_detail_2
13. dim_player_role
14. dim_position
15. dim_zone
16. dim_rink_zone
17. dim_period
18. dim_venue
19. dim_success
20. dim_shot_type
21. dim_shot_outcome
22. dim_pass_type
23. dim_pass_outcome
24. dim_save_outcome
25. dim_zone_entry_type
26. dim_zone_exit_type
27. dim_zone_outcome
28. dim_stoppage_type
29. dim_giveaway_type
30. dim_takeaway_type
31. dim_turnover_type
32. dim_turnover_quality
33. dim_shift_start_type
34. dim_shift_stop_type
35. dim_shift_slot
36. dim_shift_duration
37. dim_shift_quality_tier
38. dim_situation
39. dim_strength
40. dim_danger_level
41. dim_danger_zone
42. dim_net_location
43. dim_rating
44. dim_rating_matchup
45. dim_composite_rating
46. dim_competition_tier
47. dim_comparison_type
48. dim_stat
49. dim_stat_category
50. dim_stat_type
51. dim_micro_stat
52. dim_terminology_mapping
53. dim_assist_type
54. dim_game_state
55. dim_time_bucket
56. dim_video_type
57. dim_highlight_category
58. dim_terminology_mapping

## Core Fact Tables (10):
1. fact_event_players
2. fact_events
3. fact_shifts
4. fact_shift_players
5. fact_tracking
6. fact_gameroster
7. fact_player_game_stats
8. fact_team_game_stats
9. fact_goalie_game_stats
10. fact_playergames

## Shift Analytics (5):
1. fact_h2h
2. fact_head_to_head
3. fact_wowy
4. fact_line_combos
5. fact_shift_quality
6. fact_shift_quality_logical

## Event Analytics (10):
1. fact_scoring_chances
2. fact_scoring_chances_detailed
3. fact_shot_danger
4. fact_high_danger_chances
5. fact_linked_events
6. fact_rush_events
7. fact_cycle_events
8. fact_possession_time
9. fact_shot_chains
10. fact_event_chains

## Zone Analytics (6):
1. fact_zone_entries
2. fact_zone_exits
3. fact_zone_entry_summary
4. fact_zone_exit_summary
5. fact_team_zone_time
6. fact_breakouts
7. fact_rushes

## Player Analytics (15):
1. fact_player_period_stats
2. fact_player_season_stats
3. fact_player_season_stats_basic
4. fact_player_career_stats
5. fact_player_career_stats_basic
6. fact_player_micro_stats
7. fact_player_qoc_summary
8. fact_player_position_splits
9. fact_player_stats_long
10. fact_player_stats_by_competition_tier
11. fact_player_pair_stats
12. fact_player_boxscore_all
13. fact_player_event_chains
14. fact_player_trends
15. fact_player_game_position

## Goalie Tables (4):
1. fact_goalie_season_stats
2. fact_goalie_season_stats_basic
3. fact_goalie_career_stats
4. fact_goalie_career_stats_basic
5. fact_saves

## Team Tables (3):
1. fact_team_season_stats
2. fact_team_season_stats_basic
3. fact_special_teams_summary

## Matchup Tables (3):
1. fact_matchup_summary
2. fact_matchup_performance
3. fact_period_momentum

## Other Fact Tables (10):
1. fact_leadership
2. fact_registration
3. fact_draft
4. fact_faceoffs
5. fact_penalties
6. fact_turnovers_detailed
7. fact_sequences
8. fact_plays
9. fact_video
10. fact_highlights

## XY Coordinate Tables (4):
1. fact_player_xy_long
2. fact_player_xy_wide
3. fact_puck_xy_long
4. fact_puck_xy_wide
5. fact_shot_xy

## QA Tables (4):
1. qa_goal_accuracy
2. qa_scorer_comparison
3. qa_data_completeness
4. qa_suspicious_stats
5. fact_suspicious_stats
6. fact_suspicious_stats_player
7. fact_suspicious_stats_team

## Lookup Tables (1):
1. lookup_player_game_rating

## Assist/Goal Tables (4):
1. fact_assists
2. fact_goals
3. fact_shot_assists

---

*Document Generated: 2026-01-18*
*Version: 34.00*
*Total Tables: 138+*
*Total Documented Columns: 1000+*
