# BenchSight Data Dictionary

Last Updated: 2026-01-12
Version: 28.3

## Overview

This document defines every table and column in the BenchSight data warehouse. The warehouse follows a dimensional model (star schema) with:
- **50 Dimension Tables** (`dim_*`) - Reference/lookup data
- **81 Fact Tables** (`fact_*`) - Transactional/metric data
- **8 QA/Lookup Tables** - Quality assurance and helper tables
- **30 Supabase Views** (`v_*`) - Pre-aggregated for dashboard consumption

**Total: 139 ETL tables + 30 views = 169 database objects**

---

## Supabase Views (Dashboard Layer)

Views are computed on-the-fly from ETL tables. They provide pre-aggregated data for fast dashboard rendering.

| Category | Views | Purpose |
|----------|-------|---------|
| `v_leaderboard_*` | 8 | Points, goals, assists, PPG, career, goalie leaders |
| `v_standings_*` | 4 | Current standings, history, H2H |
| `v_rankings_*` | 7 | Full rankings with rank numbers |
| `v_summary_*` | 6 | League, team, player, goalie summaries |
| `v_recent_*` | 6 | Recent games, hot players |
| `v_compare_*` | 7 | Player, goalie, team comparisons |
| `v_detail_*` | 9 | Game logs, period splits |
| `v_tracking_*` | 8 | Micro-stats from tracking data |

**See `sql/views/VIEW_CATALOG.md` for complete view documentation.**

---

## Table Naming Conventions

| Prefix | Type | Description |
|--------|------|-------------|
| `dim_` | Dimension | Reference/lookup data (slowly changing) |
| `fact_` | Fact | Transactional data, metrics, events |
| `bridge_` | Bridge | Many-to-many relationship tables |

---

## Key Concepts

### Primary Keys
- **Surrogate Keys**: System-generated IDs (e.g., `player_id = 'P100001'`)
- **Natural Keys**: Business-meaningful IDs (e.g., `season = 20232024`)
- **Composite Keys**: Multiple columns form the key (e.g., `game_id + player_id`)

### Foreign Key Patterns
- `*_id` columns reference dimension table primary keys
- Example: `fact_events.player_id` → `dim_player.player_id`

### Goal Counting Rule (CRITICAL)
**Goals are ONLY counted via:**
```sql
event_type = 'Goal' AND event_detail = 'Goal_Scored'
```
- `Shot_Goal` in event_detail indicates the shot that resulted in a goal, NOT the goal itself
- `event_player_1` is always the primary player (goal scorer, shooter, etc.)

### play_detail_successful Values (CRITICAL)
**Tracks outcome of micro plays (dekes, drives, etc.):**
| Value | Meaning |
|-------|---------|
| `s` | Successful - play achieved its purpose |
| `u` | Unsuccessful - play failed |
| blank/NaN | Not tracked - DO NOT count as either |

**Example:** A deke with `s` means the player beat the defender. `u` means got stopped.

---

## Core Dimension Tables

### dim_player
**Description:** Master player reference data  
**Source:** Registration data + game tracking  
**Primary Key:** `player_id`  
**Row Count:** ~200 players

| Column | Type | Description | Calculation/Source |
|--------|------|-------------|-------------------|
| player_id | TEXT | Unique player identifier | Generated: 'P' + 6-digit number |
| player_full_name | TEXT | Display name | Registration form |
| first_name | TEXT | First name | Parsed from full name |
| last_name | TEXT | Last name | Parsed from full name |
| birth_year | BIGINT | Year of birth | Registration form |
| position | TEXT | Primary position (F/D/G) | Registration form |
| email | TEXT | Contact email | Registration form |
| current_team_id | TEXT | Current team FK | Most recent season roster |
| current_team_name | TEXT | Denormalized team name | Lookup from dim_team |

### dim_team
**Description:** Team master data  
**Source:** League administration  
**Primary Key:** `team_id`

| Column | Type | Description | Calculation/Source |
|--------|------|-------------|-------------------|
| team_id | TEXT | Unique team identifier | Generated: 'N' + 5-digit number |
| team_name | TEXT | Official team name | League registration |
| short_name | TEXT | Abbreviated name | Derived (first 3 chars or custom) |
| primary_color | TEXT | Team color | League registration |

### dim_season
**Description:** Season definitions  
**Source:** League schedule  
**Primary Key:** `season_id`

| Column | Type | Description | Calculation/Source |
|--------|------|-------------|-------------------|
| season_id | TEXT | Season identifier | Format: 'N' + YYYYYYYYF (e.g., N20232024F) |
| season | BIGINT | Season as number | YYYYYYYY format (e.g., 20232024) |
| season_name | TEXT | Display name | "2023-2024 Fall" |
| start_date | DATE | First game date | Min(game_date) for season |
| end_date | DATE | Last game date | Max(game_date) for season |
| is_current | BOOLEAN | Current season flag | Most recent season |

### dim_game
**Description:** Game master data  
**Source:** Schedule + game tracking  
**Primary Key:** `game_id`

| Column | Type | Description | Calculation/Source |
|--------|------|-------------|-------------------|
| game_id | BIGINT | Unique game identifier | Generated from schedule |
| season_id | TEXT | Season FK | Schedule data |
| home_team_id | TEXT | Home team FK | Schedule data |
| away_team_id | TEXT | Away team FK | Schedule data |
| game_date | TIMESTAMPTZ | Game date/time | Schedule data |
| venue_id | TEXT | Venue FK | Schedule data |
| home_score | BIGINT | Final home goals | Count from fact_events |
| away_score | BIGINT | Final away goals | Count from fact_events |
| game_status | TEXT | Game status | 'Completed', 'Scheduled', 'Cancelled' |

---

## Core Fact Tables

### fact_events
**Description:** Raw event-level game tracking data (SOURCE OF TRUTH)  
**Source:** Game tracking application  
**Primary Key:** Composite (`game_id`, `event_id`)  
**Grain:** One row per tracked event

| Column | Type | Description | Calculation/Source |
|--------|------|-------------|-------------------|
| game_id | BIGINT | Game FK | From tracking session |
| event_id | BIGINT | Event sequence number | Auto-increment per game |
| period | BIGINT | Period number (1/2/3/OT) | Tracker input |
| time_remaining | TEXT | Clock time (MM:SS) | Tracker input |
| event_type | TEXT | Event category | Lookup: Shot, Goal, Pass, etc. |
| event_detail | TEXT | Event subcategory | Lookup: Wrist, Slap, Goal_Scored, etc. |
| event_player_1 | TEXT | Primary player ID | ALWAYS the main actor |
| event_player_2 | TEXT | Secondary player ID | Assist, defender, etc. |
| event_player_3 | TEXT | Tertiary player ID | Second assist |
| team_id | TEXT | Team executing event | From player roster |
| zone_id | TEXT | Ice zone FK | Tracker input |
| x_coord | DOUBLE PRECISION | X position (0-200) | Tracker input |
| y_coord | DOUBLE PRECISION | Y position (0-85) | Tracker input |
| shot_outcome | TEXT | Shot result | 'Goal', 'Save', 'Miss', 'Block' |

**Flag Columns (is_*) - 29 total:**

| Flag | Count | Definition | Notes |
|------|-------|------------|-------|
| is_sog | 231 | Shot on goal | `event_type='Shot' AND event_detail IN ('Shot_Goal','Shot_OnNetSaved','Shot_OnNet')` |
| is_corsi | 430 | Corsi shot attempt | `is_sog OR is_blocked_shot OR is_missed_shot` |
| is_fenwick | 319 | Fenwick shot attempt | `is_sog OR is_missed_shot` |
| is_blocked_shot | 111 | Blocked shot | `event_detail CONTAINS 'Blocked'` |
| is_missed_shot | 88 | Missed shot | `event_detail IN ('Shot_Missed','Shot_MissedPost')` |
| is_goal | 16 | Goal scored | `event_type='Goal' AND event_detail='Goal_Scored'` |
| is_save | 213 | Save by goalie | `event_detail STARTS WITH 'Save'` |
| is_zone_entry | 495 | Successful zone entry | `event_detail='Zone_Entry'` |
| is_zone_exit | 476 | Successful zone exit | `event_detail='Zone_Exit'` |
| is_faceoff | 169 | Faceoff event | `event_type='Faceoff'` |
| is_giveaway | 602 | Giveaway event | `giveaway_type_id IS NOT NULL` |
| is_bad_giveaway | 251 | Bad giveaway (misplay) | `is_giveaway AND event_detail_2 IN (bad types)` |
| is_takeaway | 133 | Takeaway event | `takeaway_type_id IS NOT NULL` |
| is_turnover | 744 | Turnover event | `event_type='Turnover'` |
| is_penalty | 11 | Penalty event | `event_type='Penalty'` |
| is_rush | 421 | Rush play (tracker) | `event_detail_2 CONTAINS 'Rush'` |
| is_rush_calculated | 107 | Rush to shot | Zone entry → SOG ≤5 sec & ≤5 events |
| is_rebound | 137 | Rebound event | `event_type='Rebound'` |
| is_cycle | 244 | Cycle play | Based on cycle_key (3+ passes in o-zone) |
| is_pressured | 964 | Under pressure | `pressured_pressurer=1` for event_player_1 |
| is_deflected | 5 | Deflected shot | `event_detail='Shot_Deflected'` |
| is_tipped | 20 | Tipped shot | `event_detail_2 IN ('Shot_Tip','Shot_Tipped','Goal_Tip')` |
| is_pre_shot_event | 192 | Pre-shot event | Within 3 events of SOG in same sequence |
| is_shot_assist | 82 | Shot assist | Immediately before SOG in same sequence |
| is_sequence_first | 521 | Sequence start | First event in sequence |
| is_sequence_last | 521 | Sequence end | Last event in sequence |
| is_scoring_chance | 247 | Scoring chance | TODO: verify logic |
| is_high_danger | 23 | High danger | TODO: verify logic |
| is_highlight | 1 | Highlight play | TODO: verify logic |

**Context Columns (43 columns):**

| Column | Non-null | Description |
|--------|----------|-------------|
| prev_event_id | 5819 | Previous event ID in game |
| prev_event_type | 5819 | Previous event type |
| prev_event_detail | 4709 | Previous event detail |
| prev_event_team | 5819 | Previous event team |
| prev_event_same_team | 5823 | Was prev by same team? (1/0) |
| next_event_id | 5819 | Next event ID in game |
| next_event_type | 5819 | Next event type |
| next_event_detail | 4710 | Next event detail |
| next_event_team | 5819 | Next event team |
| next_event_same_team | 5823 | Is next by same team? (1/0) |
| time_since_prev | 5814 | Seconds since prev event |
| time_to_next | 5814 | Seconds to next event |
| time_to_next_sog | 5692 | Seconds to next shot on goal |
| time_since_last_sog | 5555 | Seconds since last SOG |
| events_to_next_sog | 5692 | Event count to next SOG |
| events_since_last_sog | 5555 | Event count since last SOG |
| next_sog_result | 5692 | Result of next SOG (goal/save) |
| led_to_sog | 5823 | In sequence that produced SOG (1/0) |
| is_pre_shot_event | 5823 | Within 3 events of SOG (1/0) |
| is_shot_assist | 5823 | Immediately before SOG (1/0) |
| time_to_next_goal | 4748 | Seconds to next goal |
| time_since_last_goal | 4151 | Seconds since last goal |
| events_to_next_goal | 4748 | Event count to next goal |
| events_since_last_goal | 4151 | Event count since last goal |
| led_to_goal | 5823 | In sequence that produced goal (1/0) |
| time_since_zone_entry | 5792 | Seconds since last zone entry |
| events_since_zone_entry | 5792 | Events since last zone entry |
| time_since_zone_exit | 5726 | Seconds since last zone exit |
| sequence_event_num | 5821 | Position in sequence (1, 2, 3...) |
| sequence_total_events | 5821 | Total events in sequence |
| sequence_duration | 5821 | Sequence length in seconds |
| is_sequence_first | 5823 | First event in sequence (1/0) |
| is_sequence_last | 5823 | Last event in sequence (1/0) |
| sequence_has_sog | 5823 | Sequence contains SOG (1/0) |
| sequence_has_goal | 5823 | Sequence contains goal (1/0) |
| sequence_shot_count | 5821 | Total shots in sequence |
| consecutive_team_events | 5823 | Streak of events by same team |
| time_since_possession_change | 5808 | Seconds since turnover/faceoff |
| events_since_possession_change | 5808 | Events since possession change |
| time_since_faceoff | 5808 | Seconds since last faceoff |
| events_since_faceoff | 5808 | Events since last faceoff |
| is_rush_calculated | 5823 | Zone entry → SOG ≤5 sec & ≤5 events (1/0) |
| time_from_entry_to_shot | 107 | If rush, time from entry to shot |

### fact_event_players
**Description:** Player-level event tracking data (one row per player per event)  
**Source:** Expanded from fact_events  
**Primary Key:** `event_player_key` (format: `EP{game_id:05d}{event_index:05d}{player_id}`)  
**Grain:** One row per player per event (players can have multiple roles)

| Column | Type | Description | Calculation/Source |
|--------|------|-------------|-------------------|
| event_player_key | TEXT | Primary key | `EP{game_id}{event_index}{player_id}` |
| game_id | BIGINT | Game FK | From tracking session |
| event_id | TEXT | Event FK | `EV{game_id}{event_index}` |
| player_id | TEXT | Player FK | From roster lookup |
| player_role | TEXT | Role in event | `event_player_1`, `opp_player_1`, etc. |
| player_team | TEXT | Player's team name | Derived from team_venue + home/away_team |
| player_team_id | TEXT | Player's team FK | Lookup from dim_team |
| team_venue | TEXT | Player's venue | `h` (home) or `a` (away) |
| player_toi | FLOAT | Shift TOI at event (seconds) | `shift_start - event_time` |
| team_on_ice_toi_avg | FLOAT | Avg shift TOI of teammates on ice | Mean of teammate shift TOIs (excl goalies) |
| team_on_ice_toi_min | FLOAT | Min shift TOI of teammates on ice | Min of teammate shift TOIs (excl goalies) |
| team_on_ice_toi_max | FLOAT | Max shift TOI of teammates on ice | Max of teammate shift TOIs (excl goalies) |
| opp_on_ice_toi_avg | FLOAT | Avg shift TOI of opponents on ice | Mean of opponent shift TOIs (excl goalies) |
| opp_on_ice_toi_min | FLOAT | Min shift TOI of opponents on ice | Min of opponent shift TOIs (excl goalies) |
| opp_on_ice_toi_max | FLOAT | Max shift TOI of opponents on ice | Max of opponent shift TOIs (excl goalies) |

**Note:** TOI columns show time on ice THIS SHIFT only (not cumulative game TOI).

### fact_player_season_stats
**Description:** Aggregated player statistics per season  
**Source:** Calculated from fact_events  
**Primary Key:** Composite (`player_id`, `season_id`)  
**Grain:** One row per player per season

| Column | Type | Description | Calculation/Source |
|--------|------|-------------|-------------------|
| player_id | TEXT | Player FK | From fact_events |
| season_id | TEXT | Season FK | From dim_game |
| games_played | BIGINT | Games appeared | COUNT(DISTINCT game_id) |
| goals | BIGINT | Goals scored | COUNT where event_type='Goal' AND event_detail='Goal_Scored' |
| assists | BIGINT | Primary + secondary assists | COUNT where event_type='Goal' AND player is event_player_2 or event_player_3 |
| points | BIGINT | Total points | goals + assists |
| shots | BIGINT | Shots on goal | COUNT where event_type='Shot' |
| shooting_pct | DOUBLE PRECISION | Shooting percentage | goals / shots * 100 |
| plus_minus | BIGINT | Plus/minus rating | Goals for - Goals against while on ice |
| pim | BIGINT | Penalty minutes | SUM(penalty_minutes) |
| toi | TEXT | Time on ice | SUM(shift_duration) |

### fact_gameroster
**Description:** Player statistics per game  
**Source:** Calculated from fact_events + roster  
**Primary Key:** Composite (`game_id`, `player_id`)  
**Grain:** One row per player per game

| Column | Type | Description | Calculation/Source |
|--------|------|-------------|-------------------|
| game_id | BIGINT | Game FK | From game |
| player_id | TEXT | Player FK | From roster |
| team_id | TEXT | Player's team FK | From roster |
| opp_team_id | TEXT | Opponent team FK | Derived |
| goals | BIGINT | Goals in game | COUNT from fact_events |
| assist | BIGINT | Assists in game | COUNT from fact_events |
| points | BIGINT | Points in game | goals + assists |
| goals_against | BIGINT | Goals against (goalies) | COUNT opponent goals |
| player_game_number | BIGINT | Jersey number | From roster |
| sub | BIGINT | Substitute flag | 1 if sub, NULL otherwise |

### fact_registration
**Description:** Player season registration data  
**Source:** Registration forms  
**Primary Key:** `player_season_registration_id`  
**Grain:** One row per player per season registration

| Column | Type | Description | Calculation/Source |
|--------|------|-------------|-------------------|
| player_season_registration_id | TEXT | Unique registration ID | Generated |
| player_id | TEXT | Player FK | Matched or generated |
| season_id | TEXT | Season FK | From form |
| restricted | TEXT | Restricted player flag | Y/N from form |
| norad_experience | TEXT | Years in NORAD | Free text from form |
| skill_rating | BIGINT | Self-rated skill (1-10) | From form |
| age | BIGINT | Age at registration | Calculated from birth_year |
| position | TEXT | Preferred position | From form |
| drafted_team_id | TEXT | Team drafted to | From draft results |

### fact_shifts
**Description:** Shift-level game data with all players on ice and team-level stats  
**Source:** Tracking spreadsheets + calculated stats  
**Primary Key:** `shift_id`  
**Grain:** One row per shift (time interval between whistles)

**Key Columns:**
| Column | Type | Description |
|--------|------|-------------|
| shift_id | TEXT | Primary key (SH{game_id}{shift_index:05d}) |
| game_id | BIGINT | Game FK |
| period | BIGINT | Period number |
| shift_duration | FLOAT | Total shift duration in seconds |
| stoppage_time | FLOAT | Time in stoppages during shift |

**Shot/Corsi Columns (Home perspective):**
| Column | Description |
|--------|-------------|
| sf / sa | Shots for/against (home team) |
| cf / ca | Corsi for/against (all shot attempts) |
| cf_pct | Corsi % (cf / (cf + ca) * 100) |
| ff / fa | Fenwick for/against (unblocked shots) |
| ff_pct | Fenwick % |
| scf / sca | Scoring chances for/against |
| hdf / hda | High danger for/against |

**Event Columns (Team-specific):**
| Column | Description |
|--------|-------------|
| home_zone_entries / away_zone_entries | Zone entries by team |
| home_zone_exits / away_zone_exits | Zone exits by team |
| home_giveaways / away_giveaways | Giveaways by team |
| home_bad_giveaways / away_bad_giveaways | Bad giveaways by team |
| home_takeaways / away_takeaways | Takeaways by team |
| fo_won / fo_lost | Faceoffs won/lost by home team |

**Rating Columns:**
| Column | Description |
|--------|-------------|
| home_avg_rating / away_avg_rating | Average player rating on ice |
| home_min_rating / home_max_rating | Min/max rating on ice |
| rating_differential | home_avg - away_avg |
| home_rating_advantage | Boolean (differential > 0) |

### fact_shift_players
**Description:** Player-level shift data with venue-mapped stats  
**Source:** Expanded from fact_shifts  
**Primary Key:** `shift_player_id`  
**Grain:** One row per player per shift

**Key Columns:**
| Column | Type | Description |
|--------|------|-------------|
| shift_player_id | TEXT | Primary key (SP{shift_id}{player_id}) |
| player_id | TEXT | Player FK |
| venue | TEXT | 'home' or 'away' |

**Venue-Mapped Stats (player's team perspective):**
| Column | Description |
|--------|-------------|
| cf / ca | Corsi for/against (player's team) |
| ff / fa | Fenwick for/against (player's team) |
| sf / sa | Shots for/against (player's team) |
| zone_entries / zone_exits | Player's team zone entries/exits |
| giveaways / bad_giveaways | Player's team giveaways |
| takeaways | Player's team takeaways |
| fo_won / fo_lost | Player's team faceoff wins/losses |
| gf / ga / pm | Goals for/against/plus-minus |

**Rating Columns:**
| Column | Description |
|--------|-------------|
| player_rating | Individual player rating |
| team_avg_rating | Player's teammates avg rating |
| opp_avg_rating | Opponents avg rating |
| qoc_rating | Quality of competition (= opp_avg) |
| qot_rating | Quality of teammates (= team_avg) |
| competition_tier_id | FK to dim_competition_tier (TI01-TI04) |

---

## Event Dimension Tables

### dim_event_type
**Description:** Event type categories  
**Primary Key:** `event_type_id`

| Value | Description |
|-------|-------------|
| Shot | Shot attempt |
| Goal | Goal scored |
| Pass | Pass attempt |
| Faceoff | Faceoff event |
| Hit | Body check |
| Block | Shot blocked |
| Turnover | Puck loss |
| Recovery | Puck recovery |
| Penalty | Penalty called |

### dim_event_detail
**Description:** Event detail subcategories  
**Primary Key:** `event_detail_id`

| Value | Parent Type | Description |
|-------|-------------|-------------|
| Goal_Scored | Goal | Actual goal (count this!) |
| Shot_Goal | Shot | Shot that became a goal |
| Wrist | Shot | Wrist shot |
| Slap | Shot | Slap shot |
| Snap | Shot | Snap shot |
| Backhand | Shot | Backhand shot |
| Save | Shot | Shot saved |
| Miss | Shot | Shot missed net |

---

## Zone and Location Tables

### dim_zone
**Description:** Ice zones for event tracking  
**Primary Key:** `zone_id`

| Zone | Description |
|------|-------------|
| OZ | Offensive Zone |
| NZ | Neutral Zone |
| DZ | Defensive Zone |

### dim_danger_zone
**Description:** Shot danger areas  
**Primary Key:** `danger_zone_id`

| Zone | Description | xG Multiplier |
|------|-------------|---------------|
| Slot | High slot area | 1.5x |
| Crease | In front of net | 2.0x |
| Point | Blue line | 0.5x |
| Perimeter | Outside areas | 0.3x |

### dim_zone_entry_type
**Description:** Zone entry types with controlled/uncontrolled classification  
**Source:** dim_event_detail_2 (entries starting with 'ZoneEntry')  
**Primary Key:** `zone_entry_type_id`

| Column | Type | Description |
|--------|------|-------------|
| zone_entry_type_id | TEXT | Primary key (ZE0001, etc.) |
| zone_entry_type_code | TEXT | Full code (ZoneEntry_Rush, etc.) |
| zone_entry_type_name | TEXT | Display name (Rush, Pass, etc.) |
| is_controlled | BOOLEAN | True = maintain possession (Pass, Rush, RushBreakaway) |

**Controlled entries (3):** Pass, Rush, RushBreakaway  
**Uncontrolled entries (10):** CausedTurnover, Chip, DumpIn, FromExitClear, Lob, OppTeam, Other, PassMiss/Misplay, PenaltyKillClear, Shot

### dim_zone_exit_type
**Description:** Zone exit types with controlled/uncontrolled classification  
**Source:** dim_event_detail_2 (entries starting with 'ZoneExit')  
**Primary Key:** `zone_exit_type_id`

| Column | Type | Description |
|--------|------|-------------|
| zone_exit_type_id | TEXT | Primary key (ZX0001, etc.) |
| zone_exit_type_code | TEXT | Full code (ZoneExit_Rush, etc.) |
| zone_exit_type_name | TEXT | Display name (Rush, Pass, etc.) |
| is_controlled | BOOLEAN | True = maintain possession (Pass, Rush) |

**Controlled exits (2):** Pass, Rush  
**Uncontrolled exits (10):** CausedTurnover, Chip, Clear, Lob, OppTeam, Other, PassMiss/Misplay, PassMiss_Misplay, PenaltyKillClear, Shot

---

## Aggregate/Summary Tables

### fact_team_season_stats
**Description:** Team-level season statistics  
**Source:** Aggregated from fact_events  
**Grain:** One row per team per season

### fact_player_vs_team
**Description:** Player performance against each opponent  
**Source:** Aggregated from fact_events  
**Grain:** One row per player per opponent team per season

### fact_period_stats
**Description:** Statistics by period  
**Source:** Aggregated from fact_events  
**Grain:** One row per game per period

---

## ETL Calculation Rules

### Goal Attribution
```python
# Goals are counted from fact_events where:
goals = events[(events.event_type == 'Goal') & 
               (events.event_detail == 'Goal_Scored')]

# The scorer is ALWAYS event_player_1
scorer = goal_event.event_player_1

# Assists are event_player_2 (primary) and event_player_3 (secondary)
primary_assist = goal_event.event_player_2
secondary_assist = goal_event.event_player_3
```

### Shot Counting
```python
# All shots (including goals)
shots = events[events.event_type == 'Shot']

# Shots on goal (saved or scored)
shots_on_goal = shots[shots.shot_outcome.isin(['Save', 'Goal'])]
```

### Plus/Minus
```python
# +1 for each even-strength goal FOR while on ice
# -1 for each even-strength goal AGAINST while on ice
# Power play goals don't count
```

---

## Table Index

### Dimension Tables (55)
| Table | Description | Key Columns |
|-------|-------------|-------------|
| dim_assist_type | Assist type codes | assist_type_id |
| dim_comparison_type | Comparison categories | comparison_type_id |
| dim_competition_tier | Skill tier definitions | competition_tier_id |
| dim_composite_rating | Rating calculations | composite_rating_id |
| dim_danger_level | Shot danger levels | danger_level_id |
| dim_danger_zone | Shot location danger | danger_zone_id |
| dim_event_detail | Event detail codes | event_detail_id |
| dim_event_detail_2 | Secondary event details | event_detail_2_id |
| dim_event_type | Event type codes | event_type_id |
| dim_game | Game master data | game_id |
| dim_game_state | Game state codes | game_state_id |
| dim_giveaway_type | Turnover types | giveaway_type_id |
| dim_league | League definitions | league_id |
| dim_micro_stat | Micro statistic types | micro_stat_id |
| dim_net_location | Net target locations | net_location_id |
| dim_pass_outcome | Pass result codes | pass_outcome_id |
| dim_pass_type | Pass type codes | pass_type_id |
| dim_period | Period definitions | period_id |
| dim_play_detail | Play detail codes | play_detail_id |
| dim_player | Player master | player_id |
| dim_position | Position codes | position_id |
| dim_schedule | Game schedule | schedule_id |
| dim_season | Season definitions | season_id |
| dim_shot_outcome | Shot result codes | shot_outcome_id |
| dim_team | Team master | team_id |
| dim_venue | Venue/rink data | venue_id |
| dim_zone | Ice zone codes | zone_id |
| ... | (28 more dimension tables) | ... |

### Fact Tables (71)
| Table | Description | Grain |
|-------|-------------|-------|
| fact_events | Raw event data | Event |
| fact_gameroster | Player game stats | Player-Game |
| fact_player_season_stats | Player season stats | Player-Season |
| fact_team_season_stats | Team season stats | Team-Season |
| fact_registration | Player registrations | Registration |
| fact_shots | Shot-level data | Shot |
| fact_goals | Goal-level data | Goal |
| fact_passes | Pass-level data | Pass |
| fact_faceoffs | Faceoff-level data | Faceoff |
| fact_penalties | Penalty-level data | Penalty |
| ... | (61 more fact tables) | ... |

---

## Change Log

| Date | Version | Change |
|------|---------|--------|
| 2026-01-10 | 21.1 | Initial data dictionary created |

---

## Future Documentation Needed

- [ ] Complete column definitions for all 131 tables
- [ ] Add sample queries for common analytics
- [ ] Document data lineage (source → transformation → target)
- [ ] Add business rules for each calculated metric
- [ ] Include data quality rules per column

---

## v25.1 New Columns - fact_player_game_stats

### Period Splits
| Column | Type | Description | Calculation |
|--------|------|-------------|-------------|
| p1_goals | INT | Period 1 goals | COUNT goals where period=1 |
| p1_assists | INT | Period 1 assists | COUNT assists where period=1 |
| p1_shots | INT | Period 1 shots | COUNT shots where period=1 |
| p1_points | INT | Period 1 points | p1_goals + p1_assists |
| p1_toi_seconds | INT | Period 1 TOI | SUM(shift_duration) where period=1 |
| p2_goals | INT | Period 2 goals | As above for period=2 |
| p2_assists | INT | Period 2 assists | As above for period=2 |
| p2_shots | INT | Period 2 shots | As above for period=2 |
| p2_points | INT | Period 2 points | As above for period=2 |
| p2_toi_seconds | INT | Period 2 TOI | As above for period=2 |
| p3_goals | INT | Period 3 goals | As above for period=3 |
| p3_assists | INT | Period 3 assists | As above for period=3 |
| p3_shots | INT | Period 3 shots | As above for period=3 |
| p3_points | INT | Period 3 points | As above for period=3 |
| p3_toi_seconds | INT | Period 3 TOI | As above for period=3 |
| p3_clutch_diff | FLOAT | P3 performance differential | P3 points/min - P1P2 points/min |

### Danger Zone Stats
| Column | Type | Description | Calculation |
|--------|------|-------------|-------------|
| shots_high_danger | INT | High danger shots | COUNT where danger_level='high' |
| shots_medium_danger | INT | Medium danger shots | Total - high - low |
| shots_low_danger | INT | Low danger shots | COUNT where danger_level='low' |
| goals_high_danger | INT | High danger goals | Goals where danger_level='high' |
| goals_medium_danger | INT | Medium danger goals | Total - high - low |
| goals_low_danger | INT | Low danger goals | Goals where danger_level='low' |
| scoring_chance_shots | INT | Scoring chance shots | COUNT where is_scoring_chance=1 |
| scoring_chance_goals | INT | Scoring chance goals | Goals where is_scoring_chance=1 |
| scoring_chance_pct | FLOAT | SC conversion rate | sc_goals / sc_shots * 100 |
| avg_shot_danger | FLOAT | Average shot quality | Weighted danger (HD=3, MD=2, LD=1) |
| high_danger_shot_pct | FLOAT | HD shooting % | HD goals / HD shots * 100 |
| low_danger_shot_pct | FLOAT | LD shooting % | LD goals / LD shots * 100 |

### Rush Stats
| Column | Type | Description | Calculation |
|--------|------|-------------|-------------|
| rush_shots | INT | Rush shots | Shots where is_rush=1 |
| rush_goals | INT | Rush goals | Goals where is_rush=1 |
| rush_assists | INT | Rush assists | Assists where is_rush=1 |
| rush_points | INT | Rush points | rush_goals + rush_assists |
| rush_shot_pct | FLOAT | Rush shooting % | rush_goals / rush_shots * 100 |
| rush_involvement | INT | Rush event count | Total rush events involved in |
| rush_involvement_pct | FLOAT | Rush participation | involvement / total_rush * 100 |

### Micro Stats (from play_detail1/play_detail_2)
| Column | Type | Description |
|--------|------|-------------|
| dekes | INT | Deke attempts |
| drives_middle | INT | Drives to middle |
| drives_wide | INT | Drives wide |
| drives_corner | INT | Drives to corner |
| drives_total | INT | Total drives |
| cutbacks | INT | Cutback plays |
| delays | INT | Delay plays |
| chips | INT | Chip plays |
| crash_net | INT | Net crash attempts |
| screens | INT | Screen plays |
| give_and_go | INT | Give-and-go plays |
| second_touch | INT | Second touch passes |
| cycles | INT | Cycle plays |
| poke_checks | INT | Poke check attempts |
| stick_checks | INT | Stick check attempts |
| zone_entry_denials | INT | Zone entry denials |
| backchecks | INT | Backcheck events |
| forechecks | INT | Forecheck events |
| breakouts | INT | Breakout plays |
| dump_ins | INT | Dump-in plays |
| loose_puck_wins | INT | Loose puck battles won |
| puck_recoveries | INT | Puck recovery events |
| puck_battles_total | INT | Total puck battles |
| plays_successful | INT | Successful plays (s) |
| plays_unsuccessful | INT | Unsuccessful plays (u) |
| play_success_rate | FLOAT | Success % |

### Expected Goals (xG)
| Column | Type | Description | Calculation |
|--------|------|-------------|-------------|
| xg_for | FLOAT | Expected goals | SUM(shot_xg) based on danger + modifiers |
| goals_actual | INT | Actual goals | Count of goals scored |
| goals_above_expected | FLOAT | Goals - xG | Finishing skill indicator |
| xg_per_shot | FLOAT | Average xG | xg_for / shots |
| shots_for_xg | INT | Shots in xG calc | Total shots + goals |
| finishing_skill | FLOAT | Goals / xG | >1.0 = good finisher |

**xG Model:**
- Base rates: High=0.25, Medium=0.08, Low=0.03, Default=0.06
- Modifiers: Rush=1.3x, Rebound=1.5x, Screen=1.2x
- XY support: Distance/angle calculation when coordinates available

### WAR/GAR
| Column | Type | Description | Calculation |
|--------|------|-------------|-------------|
| gar_offense | FLOAT | Offensive GAR | G*1.0 + A1*0.7 + A2*0.4 + SOG*0.015 + xG*0.8 |
| gar_defense | FLOAT | Defensive GAR | TK*0.05 + BLK*0.02 + ZE*0.03 |
| gar_possession | FLOAT | Possession GAR | CF%Rel * TOI factor |
| gar_transition | FLOAT | Transition GAR | Controlled entries * 0.04 |
| gar_total | FLOAT | Total GAR | Sum of components |
| war | FLOAT | Wins Above Replacement | GAR / 4.5 |
| war_pace | FLOAT | Season WAR projection | WAR * 20 (games per season) |

### BenchSight Game Score
| Column | Type | Description | Calculation |
|--------|------|-------------|-------------|
| game_score | FLOAT | Total game score | 2.0 baseline + components |
| game_score_raw | FLOAT | Raw score | Sum of components |
| game_score_per_60 | FLOAT | Normalized score | game_score * (3600/TOI) |
| gs_scoring | FLOAT | Scoring component | G*1.0 + A1*0.8 + A2*0.5 |
| gs_shots | FLOAT | Shot component | SOG*0.1 + HD*0.15 |
| gs_playmaking | FLOAT | Playmaking | Entries*0.08 + 2ndTouch*0.02 |
| gs_defense | FLOAT | Defense | TK*0.15 + BLK*0.08 + PC*0.05 |
| gs_hustle | FLOAT | Hustle | BC*0.1 + FC*0.08 + PB*0.03 |
| offensive_game_score | FLOAT | Offensive GS (v27.2) | gs_scoring + gs_shots + gs_playmaking |
| defensive_game_score | FLOAT | Defensive GS (v27.2) | gs_defense + gs_hustle - giveaway_penalty |

### Performance vs Rating
| Column | Type | Description | Calculation |
|--------|------|-------------|-------------|
| skill_rating | FLOAT | Player skill rating | From fact_registration |
| expected_points | FLOAT | Expected points | 0.1 * 1.4^(rating-1) |
| expected_game_score | FLOAT | Expected GS | 1.5 + rating * 0.8 |
| points_vs_expected | FLOAT | Points diff | actual - expected |
| game_score_vs_expected | FLOAT | GS diff | actual - expected |
| performance_index | FLOAT | Performance % | actual_gs / expected_gs * 100 |
| performance_tier | TEXT | Category | Elite/Above/As/Below/Struggling |
| rating_vs_competition | FLOAT | Rating vs QoC | rating - qoc_rating |
| adjusted_performance_index | FLOAT | QoC-adjusted | Index * (1 + (qoc-rating)*0.1) |
| calculated_rating | FLOAT | Calculated rating (v27.2) | Game score mapped to 2-6 scale |
| rating_differential | FLOAT | Rating diff (v27.2) | calculated_rating - skill_rating |

### Game State Stats (v27.2)
| Column | Type | Description | Calculation |
|--------|------|-------------|-------------|
| leading_toi | INT | TOI while leading | Sum of shift_duration where team is ahead |
| trailing_toi | INT | TOI while trailing | Sum of shift_duration where team is behind |
| tied_toi | INT | TOI while tied | Sum of shift_duration where score tied |
| close_game_toi | INT | TOI in close games | Sum where |score_diff| <= 1 |
| leading_cf_pct | FLOAT | CF% while leading | Corsi % when team ahead |
| trailing_cf_pct | FLOAT | CF% while trailing | Corsi % when team behind |
| tied_cf_pct | FLOAT | CF% while tied | Corsi % when score tied |
| leading_goals | INT | Goals while leading | GF when team ahead |
| trailing_goals | INT | Goals while trailing | GF when team behind |
| tied_goals | INT | Goals while tied | GF when score tied |

### Defensive Clutch Stats (v27.3)
| Column | Type | Description | Calculation |
|--------|------|-------------|-------------|
| p3_leading_toi | INT | P3 TOI when leading | Shift duration in P3 when team ahead |
| p3_leading_cf | INT | P3 Corsi For when leading | CF in P3 when team ahead |
| p3_leading_ca | INT | P3 Corsi Against when leading | CA in P3 when team ahead |
| p3_leading_cf_pct | FLOAT | P3 CF% when leading | CF/(CF+CA) in P3 when ahead |
| p3_leading_gf | INT | P3 Goals For when leading | Goals scored in P3 when ahead |
| p3_leading_ga | INT | P3 Goals Against when leading | Goals allowed in P3 when ahead |
| defensive_clutch_cf_pct | FLOAT | Defensive clutch rating | Same as p3_leading_cf_pct |
| defensive_clutch_diff | FLOAT | Clutch vs neutral | p3_leading_cf_pct - 50.0 |

### Per-60 Rates
| Column | Type | Description |
|--------|------|-------------|
| goals_per_60 | FLOAT | Goals per 60 min |
| assists_per_60 | FLOAT | Assists per 60 min |
| points_per_60 | FLOAT | Points per 60 min |
| sog_per_60 | FLOAT | SOG per 60 min |
| fenwick_for_per_60 | FLOAT | FF per 60 min |
| corsi_for_per_60 | FLOAT | CF per 60 min |
| xg_per_60 | FLOAT | xG per 60 min |

### Relative Stats
| Column | Type | Description | Calculation |
|--------|------|-------------|-------------|
| cf_pct_rel | FLOAT | Corsi % relative | cf_pct - 50.0 |
| ff_pct_rel | FLOAT | Fenwick % relative | ff_pct - 50.0 |
| gf_pct | FLOAT | Goals For % | GF / (GF + GA) * 100 |
| gf_pct_rel | FLOAT | GF% relative | gf_pct - 50.0 |

---

## v25.1 New Columns - fact_goalie_game_stats

| Column | Type | Description | Calculation |
|--------|------|-------------|-------------|
| is_quality_start | INT | Quality start flag | 1 if SV%>=91.7 or GA<=2 |
| is_bad_start | INT | Bad start flag | 1 if SV%<85.0 |
| expected_goals_against | FLOAT | Expected GA | SA * (1 - 0.88) |
| goals_saved_above_avg | FLOAT | GSAx | xGA - GA |


---

## v25.2 New Columns - fact_player_game_stats

### KEY CHANGE: Goalies Excluded
fact_player_game_stats now contains SKATERS ONLY. Goalies are in fact_goalie_game_stats.

### Adjusted Rating (NEW)
| Column | Type | Description | Calculation |
|--------|------|-------------|-------------|
| adjusted_rating | FLOAT | What rating did they play like | Game score mapped to rating scale |
| rating_delta | FLOAT | Performance vs actual rating | adjusted_rating - skill_rating |

**Rating to Game Score Map:**
- Rating 1 → GS 1.0, Rating 2 → GS 2.3, Rating 3 → GS 3.5
- Rating 4 → GS 4.7, Rating 5 → GS 5.9, Rating 6 → GS 7.1
- Rating 7 → GS 8.3, Rating 8 → GS 9.5, Rating 9 → GS 10.7, Rating 10 → GS 12.0

### Strength/Situation Splits
| Column | Type | Description |
|--------|------|-------------|
| ev_goals | INT | Even strength goals |
| ev_assists | INT | Even strength assists |
| ev_points | INT | Even strength points |
| ev_shots | INT | Even strength shots |
| ev_toi_seconds | INT | Even strength TOI |
| ev_cf | INT | Even strength Corsi For |
| ev_ca | INT | Even strength Corsi Against |
| ev_cf_pct | FLOAT | Even strength Corsi % |
| ev_gf | INT | Even strength Goals For |
| ev_ga | INT | Even strength Goals Against |
| pp_goals | INT | Power play goals |
| pp_assists | INT | Power play assists |
| pp_points | INT | Power play points |
| pp_shots | INT | Power play shots |
| pp_toi_seconds | INT | Power play TOI |
| pp_cf | INT | Power play Corsi For |
| pp_ca | INT | Power play Corsi Against |
| pp_cf_pct | FLOAT | Power play Corsi % |
| pp_gf | INT | Power play Goals For |
| pp_ga | INT | Power play Goals Against |
| pk_toi_seconds | INT | Penalty kill TOI |
| pk_cf | INT | Penalty kill Corsi For |
| pk_ca | INT | Penalty kill Corsi Against |
| pk_cf_pct | FLOAT | Penalty kill Corsi % |
| pk_gf | INT | Penalty kill Goals For |
| pk_ga | INT | Penalty kill Goals Against |
| en_toi_seconds | INT | Empty net TOI |
| pp_toi_pct | FLOAT | % of TOI on power play |
| pk_toi_pct | FLOAT | % of TOI on penalty kill |

### Shot Type Analysis
| Column | Type | Description |
|--------|------|-------------|
| shots_wrist | INT | Wrist shots |
| shots_slap | INT | Slap shots |
| shots_snap | INT | Snap shots |
| shots_backhand | INT | Backhand shots |
| shots_one_timer | INT | One-timer shots |
| shots_tip | INT | Tip/redirect shots |
| shots_deflection | INT | Deflection shots |
| shots_wraparound | INT | Wraparound attempts |
| shots_poke | INT | Poke shots |
| shots_bat | INT | Bat shots |
| goals_wrist | INT | Wrist shot goals |
| goals_one_timer | INT | One-timer goals |
| goals_tip | INT | Tip goals |
| goals_backhand | INT | Backhand goals |
| wrist_shot_pct | FLOAT | Wrist shot conversion % |
| one_timer_pct | FLOAT | One-timer conversion % |
| primary_shot_type | TEXT | Most common shot type |
| shot_type_variety | INT | Different shot types used |

### Pass Type Analysis
| Column | Type | Description |
|--------|------|-------------|
| passes_forehand | INT | Forehand passes |
| passes_backhand | INT | Backhand passes |
| passes_stretch | INT | Stretch passes |
| passes_bank | INT | Bank passes |
| passes_rim | INT | Rim/wrap passes |
| passes_drop | INT | Drop passes |
| passes_lob | INT | Lob passes |
| passes_one_touch | INT | One-touch passes |
| creative_passes | INT | High-skill passes (stretch+bank+lob) |
| passes_completed | INT | Completed passes |
| passes_attempted | INT | Total pass attempts |
| pass_completion_pct | FLOAT | Pass completion % |
| stretch_pass_pct | FLOAT | Stretch pass success % |
| pass_type_diversity | INT | Different pass types used |

### Shot Assists / Playmaking
| Column | Type | Description |
|--------|------|-------------|
| shot_assists | INT | Passes leading to shots |
| goal_creating_actions | INT | Passes leading to goals |
| pre_shot_touches | INT | Touches before shots |
| sequences_involved | INT | Play sequences involved in |
| sequence_involvement_pct | FLOAT | % of team sequences |
| sog_sequences | INT | Sequences ending in SOG |
| goal_sequences | INT | Sequences ending in goal |
| playmaking_index | FLOAT | Composite playmaking score |

### Pressure Stats
| Column | Type | Description |
|--------|------|-------------|
| plays_under_pressure | INT | Events while pressured |
| plays_not_pressured | INT | Events without pressure |
| pressure_rate | FLOAT | % of plays under pressure |
| pressure_success_count | INT | Successful pressured plays |
| pressure_success_pct | FLOAT | Success % under pressure |
| unpressured_success_pct | FLOAT | Success % without pressure |
| pressure_differential | FLOAT | Success drop under pressure |
| pressure_giveaways | INT | Turnovers when pressured |
| poise_index | FLOAT | Composure score |

### Competition Tier Stats
| Column | Type | Description |
|--------|------|-------------|
| vs_elite_toi | INT | TOI vs elite competition |
| vs_elite_cf_pct | FLOAT | CF% vs elite |
| vs_elite_gf | INT | Goals for vs elite |
| vs_elite_ga | INT | Goals against vs elite |
| vs_good_toi | INT | TOI vs good competition |
| vs_good_cf_pct | FLOAT | CF% vs good |
| vs_good_gf | INT | Goals for vs good |
| vs_good_ga | INT | Goals against vs good |
| vs_avg_toi | INT | TOI vs average competition |
| vs_avg_cf_pct | FLOAT | CF% vs average |
| vs_avg_gf | INT | Goals for vs average |
| vs_avg_ga | INT | Goals against vs average |
| vs_weak_toi | INT | TOI vs weak competition |
| vs_weak_cf_pct | FLOAT | CF% vs weak |
| vs_weak_gf | INT | Goals for vs weak |
| vs_weak_ga | INT | Goals against vs weak |
| cf_pct_adjusted | FLOAT | Competition-adjusted CF% |
| cf_pct_vs_expected | FLOAT | CF% vs expected |

### Game State Stats
| Column | Type | Description |
|--------|------|-------------|
| leading_toi | INT | TOI while leading |
| trailing_toi | INT | TOI while trailing |
| tied_toi | INT | TOI while tied |
| close_game_toi | INT | TOI in 1-goal games |
| leading_cf_pct | FLOAT | CF% while leading |
| trailing_cf_pct | FLOAT | CF% while trailing |
| tied_cf_pct | FLOAT | CF% while tied |
| close_game_cf_pct | FLOAT | CF% in close games |
| leading_goals | INT | Goals while leading |
| trailing_goals | INT | Goals while trailing |
| tied_goals | INT | Goals while tied |

### Enhanced WAR
| Column | Type | Description |
|--------|------|-------------|
| gar_poise | FLOAT | Poise under pressure component |

### Per-60 Rates
| Column | Type | Description |
|--------|------|-------------|
| shot_assists_per_60 | FLOAT | Shot assists per 60 min |

---

## v25.2 New Columns - fact_goalie_game_stats

### Save Type Breakdown
| Column | Type | Description |
|--------|------|-------------|
| saves_butterfly | INT | Butterfly saves |
| saves_pad | INT | Pad saves |
| saves_glove | INT | Glove saves |
| saves_blocker | INT | Blocker saves |
| saves_chest | INT | Chest/shoulder saves |
| saves_stick | INT | Stick saves |
| saves_scramble | INT | Scramble saves |

### High Danger Saves
| Column | Type | Description |
|--------|------|-------------|
| hd_shots_against | INT | High danger shots faced |
| hd_goals_against | INT | High danger goals allowed |
| hd_saves | INT | High danger saves |
| hd_save_pct | FLOAT | High danger save % |

### Rebound Control
| Column | Type | Description |
|--------|------|-------------|
| saves_freeze | INT | Saves with freeze (estimate) |
| saves_rebound | INT | Saves with rebound |
| rebound_rate | FLOAT | % of saves with rebound |

### Goalie WAR
| Column | Type | Description | Calculation |
|--------|------|-------------|-------------|
| goalie_gar_gsaa | FLOAT | GSAx component | goals_saved_above_avg |
| goalie_gar_hd_bonus | FLOAT | HD save bonus | hd_saves * 0.15 |
| goalie_gar_qs_bonus | FLOAT | Quality start bonus | 0.5 if QS |
| goalie_gar_rebound | FLOAT | Rebound control bonus | saves_freeze * 0.05 |
| goalie_gar_total | FLOAT | Total Goalie GAR | Sum of components |
| goalie_war | FLOAT | Goalie WAR | goalie_gar_total / 4.5 |
| goalie_war_pace | FLOAT | Season projection | goalie_war * 20 |


---

## v28.1 fact_goalie_game_stats - ADVANCED EXPANSION (128 columns)

**Table**: fact_goalie_game_stats
**Rows**: 8 (2 goalies per game × 4 games)
**Columns**: 128 (was 39)
**Grain**: One row per goalie per game
**Source**: src/tables/core_facts.py:create_fact_goalie_game_stats()

### Category 1: Core & Identifiers (1-12)

| # | Column | Type | Description |
|---|--------|------|-------------|
| 1 | goalie_game_key | TEXT | PK: GK{game_id}{player_id} |
| 2 | game_id | INT | FK to dim_schedule |
| 3 | player_id | TEXT | FK to dim_player |
| 4 | _export_timestamp | TIMESTAMP | ETL timestamp |
| 5 | player_name | TEXT | Denormalized |
| 6 | team_name | TEXT | Denormalized |
| 7 | team_id | TEXT | FK to dim_team |
| 8 | is_home | BOOLEAN | Home/away flag |
| 9 | saves | INT | Total saves |
| 10 | goals_against | INT | Goals allowed |
| 11 | shots_against | INT | saves + goals_against |
| 12 | save_pct | FLOAT | Save percentage |

### Category 2: Save Type Breakdown (13-19)

| # | Column | Type | Filter on event_detail_2 |
|---|--------|------|--------------------------|
| 13 | saves_butterfly | INT | Contains 'butterfly' |
| 14 | saves_pad | INT | Contains 'pad' |
| 15 | saves_glove | INT | Contains 'glove' |
| 16 | saves_blocker | INT | Contains 'blocker' |
| 17 | saves_chest | INT | Contains 'chest\|shoulder' |
| 18 | saves_stick | INT | Contains 'stick' |
| 19 | saves_scramble | INT | Contains 'scramble' |

### Category 3: High Danger Stats (20-23)

| # | Column | Type | Description |
|---|--------|------|-------------|
| 20 | hd_shots_against | INT | HD shots faced |
| 21 | hd_goals_against | INT | HD goals allowed |
| 22 | hd_saves | INT | HD saves made |
| 23 | hd_save_pct | FLOAT | HD save percentage |

### Category 4: Rebound Control Advanced (24-37)

| # | Column | Type | Description |
|---|--------|------|-------------|
| 24 | saves_freeze | INT | Saves with puck frozen (from event_detail) |
| 25 | saves_rebound | INT | Saves with rebound given |
| 26 | freeze_pct | FLOAT | saves_freeze / saves * 100 |
| 27 | rebound_rate | FLOAT | saves_rebound / saves * 100 |
| 28 | rebounds_team_recovered | INT | ⚠️ GAME-LEVEL: Team recovered rebounds |
| 29 | rebounds_opp_recovered | INT | ⚠️ GAME-LEVEL: Opponent recovered |
| 30 | rebounds_shot_generated | INT | ⚠️ GAME-LEVEL: Rebounds → shots |
| 31 | rebounds_flurry_generated | INT | ⚠️ GAME-LEVEL: Rebounds → flurries |
| 32 | rebound_control_rate | FLOAT | team_recovered / total * 100 |
| 33 | rebound_danger_rate | FLOAT | (shot+flurry) / total * 100 |
| 34 | second_chance_shots_against | INT | Shots after rebounds |
| 35 | second_chance_goals_against | INT | Set to 0 (data limitation) |
| 36 | second_chance_sv_pct | FLOAT | 2nd chance save % |
| 37 | dangerous_rebound_pct | FLOAT | Same as rebound_danger_rate |

⚠️ **Note**: Columns 28-31 are GAME-LEVEL, not goalie-specific. Both goalies in same game show same values.

### Category 5: Period Splits (38-52)

| # | Column | Type | Description |
|---|--------|------|-------------|
| 38 | p1_saves | INT | Period 1 saves |
| 39 | p1_goals_against | INT | Period 1 GA |
| 40 | p1_shots_against | INT | Period 1 SA |
| 41 | p1_sv_pct | FLOAT | Period 1 SV% |
| 42 | p2_saves | INT | Period 2 saves |
| 43 | p2_goals_against | INT | Period 2 GA |
| 44 | p2_shots_against | INT | Period 2 SA |
| 45 | p2_sv_pct | FLOAT | Period 2 SV% |
| 46 | p3_saves | INT | Period 3 saves |
| 47 | p3_goals_against | INT | Period 3 GA |
| 48 | p3_shots_against | INT | Period 3 SA |
| 49 | p3_sv_pct | FLOAT | Period 3 SV% |
| 50 | best_period | INT | Period with highest SV% |
| 51 | worst_period | INT | Period with lowest SV% |
| 52 | period_consistency | FLOAT | StdDev of period SV%s |

### Category 6: Time Bucket / Clutch (53-64)

| # | Column | Type | Description |
|---|--------|------|-------------|
| 53 | early_period_saves | INT | 0-5 min of each period |
| 54 | mid_period_saves | INT | 5-15 min |
| 55 | late_period_saves | INT | 15-18 min |
| 56 | final_minute_saves | INT | 18-20 min (clutch) |
| 57 | early_period_ga | INT | GA in early period |
| 58 | mid_period_ga | INT | GA in mid period |
| 59 | late_period_ga | INT | GA in late period |
| 60 | final_minute_ga | INT | GA in final minute |
| 61 | early_period_sv_pct | FLOAT | Early SV% |
| 62 | mid_period_sv_pct | FLOAT | Mid SV% |
| 63 | late_period_sv_pct | FLOAT | Late SV% |
| 64 | final_minute_sv_pct | FLOAT | Final minute SV% (CLUTCH) |

### Category 7: Shot Context (65-76)

| # | Column | Type | Description |
|---|--------|------|-------------|
| 65 | rush_saves | INT | Saves <5s after zone entry |
| 66 | quick_attack_saves | INT | Saves 5-10s after entry |
| 67 | set_play_saves | INT | Saves >10s after entry |
| 68 | avg_time_from_entry | FLOAT | Avg seconds from zone entry |
| 69 | rush_goals_against | INT | Set to 0 (data limitation) |
| 70 | quick_attack_ga | INT | Set to 0 |
| 71 | set_play_ga | INT | Set to 0 |
| 72 | rush_sv_pct | FLOAT | Rush save % |
| 73 | quick_attack_sv_pct | FLOAT | Quick attack save % |
| 74 | set_play_sv_pct | FLOAT | Set play save % |
| 75 | rush_pct_of_shots | FLOAT | % of shots that are rush |
| 76 | transition_defense_rating | FLOAT | rush_sv_pct - set_play_sv_pct |

### Category 8: Pressure / Sequence (77-85)

| # | Column | Type | Description |
|---|--------|------|-------------|
| 77 | single_shot_saves | INT | Saves on 1st shot of sequence |
| 78 | multi_shot_saves | INT | Saves on 2+ shot sequences |
| 79 | sustained_pressure_saves | INT | Saves on 4+ shot sequences |
| 80 | max_sequence_faced | INT | Longest shot sequence |
| 81 | avg_sequence_length | FLOAT | Avg shots per sequence |
| 82 | multi_shot_sv_pct | FLOAT | SV% on multi-shot (100.0 est.) |
| 83 | sustained_pressure_sv_pct | FLOAT | SV% on sustained (100.0 est.) |
| 84 | sequence_survival_rate | FLOAT | % sequences with 0 GA |
| 85 | pressure_handling_index | FLOAT | Avg of multi/sustained SV% |

### Category 9: Body Location (86-95)

| # | Column | Type | Description |
|---|--------|------|-------------|
| 86 | glove_side_saves | INT | Glove + LeftPad saves |
| 87 | blocker_side_saves | INT | Blocker + RightPad saves |
| 88 | five_hole_saves | INT | Butterfly + Scramble saves |
| 89 | glove_side_ga | INT | Set to 0 (data limitation) |
| 90 | blocker_side_ga | INT | Set to 0 |
| 91 | five_hole_ga | INT | Set to 0 |
| 92 | glove_side_sv_pct | FLOAT | Glove side SV% |
| 93 | blocker_side_sv_pct | FLOAT | Blocker side SV% |
| 94 | five_hole_sv_pct | FLOAT | Five hole SV% |
| 95 | side_preference_ratio | FLOAT | Glove / Blocker ratio |

### Category 10: Workload Metrics (96-105)

| # | Column | Type | Description |
|---|--------|------|-------------|
| 96 | shots_per_period | FLOAT | SA / 3 |
| 97 | saves_per_period | FLOAT | Saves / 3 |
| 98 | max_shots_in_period | INT | Peak period workload |
| 99 | shot_volume_variance | FLOAT | StdDev of period SA |
| 100 | time_between_shots_avg | FLOAT | Avg gap (seconds) |
| 101 | time_between_shots_min | FLOAT | Min gap (seconds) |
| 102 | rapid_fire_saves | INT | Saves with <3s gap |
| 103 | consecutive_saves_max | INT | Longest save streak (est.) |
| 104 | workload_index | FLOAT | SA * (1 + variance/10) |
| 105 | fatigue_adjusted_gsaa | FLOAT | GSAA * fatigue_factor |

### Category 11: Quality Indicators (106-109)

| # | Column | Type | Description |
|---|--------|------|-------------|
| 106 | is_quality_start | INT | 1 if SV% >= 91.7 or GA <= 2 |
| 107 | is_bad_start | INT | 1 if SV% < 85.0 |
| 108 | expected_goals_against | FLOAT | SA * (1 - 0.88) |
| 109 | goals_saved_above_avg | FLOAT | xGA - GA |

### Category 12: Advanced Composites (110-119)

| # | Column | Type | Calculation |
|---|--------|------|-------------|
| 110 | goalie_game_score | FLOAT | saves*0.1 - GA*0.75 + shutout + HD*0.2 |
| 111 | goalie_gax | FLOAT | Simple xG model |
| 112 | goalie_gsax | FLOAT | gax - goals_against |
| 113 | clutch_rating | FLOAT | P3*0.4 + late*0.3 + final*0.3 |
| 114 | consistency_rating | FLOAT | 100 - period_consistency*2 |
| 115 | pressure_rating | FLOAT | Same as pressure_handling_index |
| 116 | rebound_rating | FLOAT | freeze*0.4 + control*0.4 + danger*0.2 |
| 117 | positioning_rating | FLOAT | Controlled saves / total * 100 |
| 118 | overall_game_rating | FLOAT | 1-10 composite scale |
| 119 | win_probability_added | FLOAT | GSAA * 0.05 |

### Category 13: Goalie WAR (120-126)

| # | Column | Type | Calculation |
|---|--------|------|-------------|
| 120 | goalie_gar_gsaa | FLOAT | = goals_saved_above_avg |
| 121 | goalie_gar_hd_bonus | FLOAT | hd_saves * 0.15 |
| 122 | goalie_gar_qs_bonus | FLOAT | 0.5 if quality_start |
| 123 | goalie_gar_rebound | FLOAT | saves_freeze * 0.05 |
| 124 | goalie_gar_total | FLOAT | Sum of GAR components |
| 125 | goalie_war | FLOAT | goalie_gar_total / 4.5 |
| 126 | goalie_war_pace | FLOAT | goalie_war * 20 |

### Category 14: Venue (127-128)

| # | Column | Type | Description |
|---|--------|------|-------------|
| 127 | venue | TEXT | 'home' or 'away' |
| 128 | venue_id | TEXT | FK to dim_venue |

---

## v28.0 fact_goalie_game_stats - Complete Documentation

**Table**: fact_goalie_game_stats
**Rows**: 8 (2 goalies per game × 4 games)
**Columns**: 39
**Grain**: One row per goalie per game
**Source**: src/tables/core_facts.py:create_fact_goalie_game_stats()
**Validated**: v28.0 (2026-01-12)

### Identifiers (Columns 1-8)

| # | Column | Type | Description | Source/Calculation |
|---|--------|------|-------------|-------------------|
| 1 | goalie_game_key | TEXT | PK | `GK{game_id}{player_id}` |
| 2 | game_id | INT | FK to dim_schedule | From fact_gameroster |
| 3 | player_id | TEXT | FK to dim_player | From fact_gameroster |
| 4 | _export_timestamp | TIMESTAMP | ETL metadata | datetime.now() |
| 5 | player_name | TEXT | Denormalized | From dim_player |
| 6 | team_name | TEXT | Denormalized | From fact_gameroster |
| 7 | team_id | TEXT | FK to dim_team | From fact_gameroster |
| 8 | is_home | BOOLEAN | Home/away flag | team_id == home_team_id |

### Core Stats (Columns 9-10)

| # | Column | Type | Description | Calculation |
|---|--------|------|-------------|-------------|
| 9 | saves | INT | Total saves | Count Save events where team_venue = goalie's venue |
| 10 | goals_against | INT | Goals allowed | Count Goal_Scored events where team_venue = opponent's venue |

### Save Type Breakdown (Columns 11-17)

| # | Column | Type | Description | Filter |
|---|--------|------|-------------|--------|
| 11 | saves_butterfly | INT | Butterfly saves | event_detail_2 contains 'butterfly' |
| 12 | saves_pad | INT | Pad saves | event_detail_2 contains 'pad' |
| 13 | saves_glove | INT | Glove saves | event_detail_2 contains 'glove' |
| 14 | saves_blocker | INT | Blocker saves | event_detail_2 contains 'blocker' |
| 15 | saves_chest | INT | Chest/shoulder saves | event_detail_2 contains 'chest\|shoulder' |
| 16 | saves_stick | INT | Stick saves | event_detail_2 contains 'stick' |
| 17 | saves_scramble | INT | Scramble saves | event_detail_2 contains 'scramble' |

**Note**: 3 saves uncategorized (Save_Other: 2, Save_Skate: 1) - sum may be 1-3 less than total saves.

### High Danger Stats (Columns 18-21)

| # | Column | Type | Description | Calculation |
|---|--------|------|-------------|-------------|
| 18 | hd_shots_against | INT | HD shots faced | Count shots where danger_level='high' by opponent |
| 19 | hd_goals_against | INT | HD goals allowed | Count goals where danger_level='high' by opponent |
| 20 | hd_saves | INT | HD saves | hd_shots_against - hd_goals_against |
| 21 | hd_save_pct | FLOAT | HD save % | hd_saves / hd_shots_against * 100 |

### Derived Stats (Columns 22-30)

| # | Column | Type | Description | Calculation |
|---|--------|------|-------------|-------------|
| 22 | shots_against | INT | Total shots faced | saves + goals_against |
| 23 | save_pct | FLOAT | Save percentage | saves / shots_against * 100 |
| 24 | is_quality_start | INT | Quality start flag | 1 if save_pct >= 91.7 OR goals_against <= 2 |
| 25 | is_bad_start | INT | Bad start flag | 1 if save_pct < 85.0 |
| 26 | expected_goals_against | FLOAT | xGA | shots_against * (1 - 0.88) |
| 27 | goals_saved_above_avg | FLOAT | GSAA | expected_goals_against - goals_against |
| 28 | saves_freeze | INT | Freeze saves (est) | saves_glove + saves_chest |
| 29 | saves_rebound | INT | Rebound saves | saves - saves_freeze |
| 30 | rebound_rate | FLOAT | Rebound % | saves_rebound / saves * 100 |

### Goalie WAR (Columns 31-37)

| # | Column | Type | Description | Calculation |
|---|--------|------|-------------|-------------|
| 31 | goalie_gar_gsaa | FLOAT | GSAA component | = goals_saved_above_avg |
| 32 | goalie_gar_hd_bonus | FLOAT | HD save bonus | hd_saves * 0.15 |
| 33 | goalie_gar_qs_bonus | FLOAT | QS bonus | 0.5 if is_quality_start else 0 |
| 34 | goalie_gar_rebound | FLOAT | Rebound bonus | saves_freeze * 0.05 |
| 35 | goalie_gar_total | FLOAT | Total GAR | gsaa + hd_bonus + qs_bonus + rebound |
| 36 | goalie_war | FLOAT | Goalie WAR | goalie_gar_total / 4.5 |
| 37 | goalie_war_pace | FLOAT | 20-game projection | goalie_war * 20 |

### Venue (Columns 38-39)

| # | Column | Type | Description | Calculation |
|---|--------|------|-------------|-------------|
| 38 | venue | TEXT | Home/away | 'home' if is_home else 'away' |
| 39 | venue_id | TEXT | FK to dim_venue | VN01 (home) or VN02 (away) |

### Constants Used

```python
LEAGUE_AVG_SV_PCT = 88.0
GOALS_PER_WIN = 4.5
GAMES_PER_SEASON = 20
GOALIE_GAR_WEIGHTS = {
    'high_danger_saves': 0.15,
    'goals_prevented': 1.0,
    'rebound_control': 0.05,
    'quality_start_bonus': 0.5,
}
```

### v28.0 Bug Fixes

1. **Saves bug** - Was filtering by opponent's venue instead of goalie's venue
2. **Venue bug** - Always showed 'home' regardless of is_home
3. **Key format** - Changed from `GK{player_id}_{game_id}` to `GK{game_id}{player_id}`

---

## Phase 3 Columns (v26.1)

### fact_player_game_stats - Linemate Analysis

| Column | Type | Description | Calculation |
|--------|------|-------------|-------------|
| unique_linemates | INT | Count of different linemates | Count distinct player_ids on shared shifts |
| top_linemate_player_id | TEXT | FK to dim_player | Player with most TOI together |
| top_linemate_toi_together | INT | Seconds on ice together | Sum of shift_duration on shared shifts |
| top_line_cf_pct | FLOAT | Corsi For % with top line | CF / (CF + CA) * 100 |
| chemistry_score | FLOAT | Performance with linemates | top_line_cf_pct - 50.0 |
| d_partner_player_id | TEXT | FK to dim_player (D only) | Defensemen's primary partner |
| d_partner_toi_together | INT | Seconds with D partner | Sum of shift_duration with D partner |
| line_consistency_pct | FLOAT | Same line percentage | Shifts with top 2 / total shifts * 100 |

### fact_player_game_stats - Time Bucket Analysis

| Column | Type | Description | Calculation |
|--------|------|-------------|-------------|
| early_period_goals | INT | Goals in TB01-TB02 | Count goals where time_bucket_id in early buckets |
| early_period_assists | INT | Assists in TB01-TB02 | Count assists where time_bucket_id in early buckets |
| early_period_points | INT | Points in TB01-TB02 | early_period_goals + early_period_assists |
| early_period_shots | INT | Shots in TB01-TB02 | Count shots/goals where time_bucket_id in early buckets |
| late_period_goals | INT | Goals in TB04-TB05 | Count goals where time_bucket_id in late buckets |
| late_period_assists | INT | Assists in TB04-TB05 | Count assists where time_bucket_id in late buckets |
| late_period_points | INT | Points in TB04-TB05 | late_period_goals + late_period_assists |
| late_period_shots | INT | Shots in TB04-TB05 | Count shots/goals where time_bucket_id in late buckets |
| early_period_cf_pct | FLOAT | Early possession % | Placeholder (50.0) |
| late_period_cf_pct | FLOAT | Late possession % | Placeholder (50.0) |
| first_goal_involvement | INT | Involved in 1st goal | 1 if player in first goal event, else 0 |

### fact_player_game_stats - Rebound/Second Chance

| Column | Type | Description | Calculation |
|--------|------|-------------|-------------|
| rebound_recoveries | INT | Rebounds recovered | Count where is_rebound=1 |
| rebound_shots | INT | Quick shots | Shots within 3 sec of previous event |
| rebound_goals | INT | Quick goals | Goals from rebound_shots |
| rebound_shot_pct | FLOAT | Rebound shooting % | rebound_goals / rebound_shots * 100 |
| crash_net_attempts | INT | Net crash attempts | Count from play_detail 'crashnet' |
| crash_net_success | INT | Successful crashes | Placeholder (0) |
| garbage_goals | INT | Scramble/deflection goals | Goals with scramble/deflection/tip in detail |

---

## v26.2 Corrections and New Columns

### CRITICAL CALCULATION CORRECTIONS

The following calculation rules were corrected in v26.2:

#### Player Attribution Rule
**ONLY `event_player_1` gets credit for events.** This applies to:
- Goals (scorer)
- Shots (shooter)
- Passes (passer)
- Faceoffs (winner)
- Turnovers (giveaway/takeaway)
- All play_detail actions

#### Assist Tracking (CORRECTED)
Assists are tracked via `play_detail1` column, NOT via player_role on goal events:
- `play_detail1='AssistPrimary'` → Primary assist (A1)
- `play_detail1='AssistSecondary'` → Secondary assist (A2)
- The assister is `event_player_1` on their pass/shot event

#### Faceoff Win/Loss (CORRECTED)
- **FO Win**: Player is `event_player_1` on faceoff event
- **FO Loss**: Player is `opp_player_1` on faceoff event

#### play_detail Counting (CORRECTED)
For `play_detail1` and `play_detail2` counts, use **DISTINCT by `linked_event_index_flag`** to avoid double-counting on linked events (e.g., pass > turnover sequences).

### New Columns - fact_player_game_stats

| Column | Type | Description | Calculation |
|--------|------|-------------|-------------|
| bad_giveaways | INT | High-cost turnovers | Giveaways where is_bad_giveaway=1 in fact_events |
| bad_turnover_diff | INT | Takeaways minus bad giveaways | takeaways - bad_giveaways |

### Corrected Column Calculations

| Column | Old Calculation | New Calculation |
|--------|-----------------|-----------------|
| primary_assists | player_role contains 'event_player_2' on goals | play_detail1='AssistPrimary' where player_role='event_player_1' |
| secondary_assists | player_role contains 'event_player_3' on goals | play_detail1='AssistSecondary' where player_role='event_player_1' |
| fo_wins | event_detail contains 'won' | event_type='Faceoff' AND player_role='event_player_1' |
| fo_losses | fo_total - fo_wins | event_type='Faceoff' AND player_role='opp_player_1' |
| shots | All shot events for player | Only where player_role='event_player_1' |
| pass_attempts | All pass events for player | Only where player_role='event_player_1' |
| blocks | play_detail1 contains 'block' | play_detail1='BlockedShot', DISTINCT by linked_event |

### Shift Count Correction (v26.2)

| Column | Old Calculation | New Calculation |
|--------|-----------------|-----------------|
| shift_count | COUNT of raw shift_player rows | COUNT DISTINCT logical_shift_number |
| avg_shift | toi_seconds / raw_count | toi_seconds / logical_shift_count |

**Logical Shift Rule:** Consecutive shift segments (no gap in shift_index) are grouped into one logical shift. This represents a single continuous period on ice.

Example: Player with 49 raw shift rows but 13 logical shifts = 13 times they went over the boards.

### Rating Diff Correction (v26.2)

| Column | Old Calculation | New Calculation |
|--------|-----------------|-----------------|
| rating_diff | player_rating - opp_avg_rating | opp_avg_rating - player_rating |

**Interpretation:**
- Positive rating_diff = facing tougher competition (opp rated higher than you)
- Negative rating_diff = facing weaker competition (opp rated lower than you)

Example: Player rated 4.0 vs opponents avg 3.0 → rating_diff = **-1.0** (facing weaker)

### New Rating Columns (v26.2) - 8 columns added

| Column | Type | Description | Calculation |
|--------|------|-------------|-------------|
| team_avg_rating | FLOAT | Avg rating of teammates on ice | Mean of team_avg_rating from shifts (excludes goalies) |
| team_rating_diff | FLOAT | Team vs Opp strength | opp_avg_rating - team_avg_rating |
| team_min_rating_avg | FLOAT | Avg of weakest player on team per shift | Mean of team's min_rating across shifts |
| team_max_rating_avg | FLOAT | Avg of strongest player on team per shift | Mean of team's max_rating across shifts |
| opp_min_rating_avg | FLOAT | Avg of weakest opponent per shift | Mean of opp's min_rating across shifts |
| opp_max_rating_avg | FLOAT | Avg of strongest opponent per shift | Mean of opp's max_rating across shifts |
| min_rating_diff | FLOAT | Opp min vs team min | opp_min_rating_avg - team_min_rating_avg |
| max_rating_diff | FLOAT | Opp max vs team max | opp_max_rating_avg - team_max_rating_avg |

**Interpretation (positive = tougher opposition):**
- `team_rating_diff > 0` = Opponents are stronger team overall
- `rating_diff > 0` = Opponents rated higher than this player
- `max_rating_diff > 0` = Opponents have better top player on average

**Example - Sam Downs (6.0 rated):**
- team_avg_rating: 4.11 (his teammates)
- opp_avg_rating: 3.99 (opponents)
- team_rating_diff: -0.12 (his team slightly stronger)
- rating_diff: -2.01 (he's much better than opponents - facing weaker competition)
- team_max_rating_avg: 6.0 (he's usually the max on his team)
- opp_max_rating_avg: 5.59 (opponents' best is usually ~5.6)

**Note:** All ratings exclude goalies.

### New Zone Entry/Exit Success Columns (v26.2) - 12 columns added

| Column | Type | Description |
|--------|------|-------------|
| zone_ent_successful | INT | Zone entries with event_successful=True |
| zone_ent_success_pct | FLOAT | Success rate for all zone entries |
| zone_ent_controlled_successful | INT | Controlled entries that were successful |
| zone_ent_controlled_success_pct | FLOAT | Success rate for controlled entries |
| zone_ent_uncontrolled_successful | INT | Uncontrolled entries that were successful |
| zone_ent_uncontrolled_success_pct | FLOAT | Success rate for uncontrolled entries |
| zone_ext_successful | INT | Zone exits with event_successful=True |
| zone_ext_success_pct | FLOAT | Success rate for all zone exits |
| zone_ext_controlled_successful | INT | Controlled exits that were successful |
| zone_ext_controlled_success_pct | FLOAT | Success rate for controlled exits |
| zone_ext_uncontrolled_successful | INT | Uncontrolled exits that were successful |
| zone_ext_uncontrolled_success_pct | FLOAT | Success rate for uncontrolled exits |

**Column naming:**
- `zone_ent_*` = Zone Entry columns
- `zone_ext_*` = Zone Exit columns

**Note:** All zone entry/exit columns count only event_player_1 (the player who performed the action).

### XY Data Dependency Note (v26.2)

The following columns currently use zone-based or event_detail-based danger classification. Once XY coordinate data is populated, these should be recalculated using distance/angle-based formulas for improved accuracy:

**Danger Zone Columns (need XY for accurate calculation):**
- `shots_high_danger`, `goals_high_danger`
- `shots_medium_danger`, `goals_medium_danger`
- `shots_low_danger`, `goals_low_danger`
- `scoring_chance_shots`, `scoring_chance_goals`, `scoring_chance_pct`
- `avg_shot_danger`
- `high_danger_for`, `high_danger_against`, `hd_pct`
- `xg_for`, `xg_against`, `xg_diff` (xG model)

**Current logic:** Uses zone classification from tracking (OZ/NZ/DZ + event_detail)
**Future logic:** Distance from goal + angle calculation from XY coordinates

### New Rush & Defensive Role Columns (v26.2) - 12 columns added

**Rush Role Breakdown:**
| Column | Type | Description |
|--------|------|-------------|
| rush_primary | INT | Times as event_player_1 on rush events (primary rusher) |
| rush_support | INT | Times as event_player_2-6 on rush events (supporting rusher) |
| rush_involvement | INT | rush_primary + rush_support (total offensive rush involvement) |
| rush_primary_def | INT | Times as opp_player_1 on rush events (primary defender) |
| rush_def_support | INT | Times as opp_player_2-6 on rush events (supporting defender) |
| rush_def_involvement | INT | rush_primary_def + rush_def_support (total defensive rush involvement) |

**General Defensive Role Metrics:**
| Column | Type | Description |
|--------|------|-------------|
| primary_def_events | INT | Times as opp_player_1 on any event (primary defender) |
| support_def_events | INT | Times as opp_player_2-6 on any event (supporting defender) |
| def_involvement | INT | primary_def_events + support_def_events |
| primary_def_shots | INT | Times as opp_player_1 when opponent shot |
| primary_def_goals_against | INT | Times as opp_player_1 when opponent scored |
| primary_def_passes | INT | Times as opp_player_1 when opponent passed |

**Rush Detection:** Uses `is_rush` flag in fact_events table.

---

## v26.2 Additions - Rush & Zone Success Metrics

### Rush Success Metrics - Offensive

| Column | Type | Formula/Description |
|--------|------|---------------------|
| rush_off_success | INT | Count where (event_successful=True OR time_to_next_sog<=10) |
| rush_off_success_pct | FLOAT | rush_off_success / rush_involvement * 100 |
| rush_off_shot_generated | INT | Count where time_to_next_sog <= 10 seconds |
| rush_off_shot_generated_pct | FLOAT | rush_off_shot_generated / rush_involvement * 100 |
| rush_off_goal_generated | INT | Count where time_to_next_goal <= 15 seconds |
| rush_off_goal_generated_pct | FLOAT | rush_off_goal_generated / rush_involvement * 100 |
| rush_off_immediate_shot | INT | Count where time_from_entry_to_shot is populated (<=5s) |

### Rush Success by Role - Primary Rusher (event_player_1)

| Column | Type | Formula/Description |
|--------|------|---------------------|
| rush_primary_success | INT | Successful rushes as primary rusher |
| rush_primary_success_pct | FLOAT | Success rate as primary rusher |
| rush_primary_shot | INT | Rushes that generated shot within 10s (as primary) |
| rush_primary_shot_pct | FLOAT | Shot generation rate as primary |
| rush_primary_goal | INT | Rushes that generated goal within 15s (as primary) |
| rush_primary_goal_pct | FLOAT | Goal generation rate as primary |

### Rush Success by Role - Support Rusher (event_player_2-6)

| Column | Type | Formula/Description |
|--------|------|---------------------|
| rush_support_success | INT | Successful rushes as supporting rusher |
| rush_support_success_pct | FLOAT | Success rate as support |
| rush_support_shot | INT | Rushes that generated shot within 10s (as support) |
| rush_support_shot_pct | FLOAT | Shot generation rate as support |
| rush_support_goal | INT | Rushes that generated goal within 15s (as support) |
| rush_support_goal_pct | FLOAT | Goal generation rate as support |

### Rush Success Metrics - Defensive

| Column | Type | Formula/Description |
|--------|------|---------------------|
| rush_def_success | INT | Rushes where NO shot within 15 seconds |
| rush_def_success_pct | FLOAT | rush_def_success / rush_def_involvement * 100 |
| rush_def_stop | INT | Rushes where event_successful=False (failed entry) |
| rush_def_stop_pct | FLOAT | rush_def_stop / rush_def_involvement * 100 |
| rush_def_ga | INT | Goals allowed within 15s while defending rush |

### Defensive Rush by Role - Primary Defender (opp_player_1)

| Column | Type | Formula/Description |
|--------|------|---------------------|
| rush_primary_def_success | INT | Rushes stopped as primary defender (no shot in 15s) |
| rush_primary_def_success_pct | FLOAT | Success rate as primary defender |
| rush_primary_def_stop | INT | Entry denials as primary defender |
| rush_primary_def_stop_pct | FLOAT | Stop rate as primary defender |
| rush_primary_def_ga | INT | Goals allowed as primary defender |

### Defensive Rush by Role - Support Defender (opp_player_2-6)

| Column | Type | Formula/Description |
|--------|------|---------------------|
| rush_support_def_success | INT | Rushes stopped as supporting defender |
| rush_support_def_success_pct | FLOAT | Success rate as support defender |
| rush_support_def_stop | INT | Entry denials as support defender |
| rush_support_def_stop_pct | FLOAT | Stop rate as support defender |
| rush_support_def_ga | INT | Goals allowed as support defender |

### Zone Entry Shot/Goal Generation by Control Type

| Column | Type | Formula/Description |
|--------|------|---------------------|
| zone_ent_shot_generated | INT | Entries that led to shot within 10s |
| zone_ent_shot_generated_pct | FLOAT | Shot generation rate for all entries |
| zone_ent_controlled_shot | INT | Controlled entries that led to shot within 10s |
| zone_ent_controlled_shot_pct | FLOAT | Shot generation rate for controlled entries |
| zone_ent_uncontrolled_shot | INT | Dump-ins that led to shot within 10s |
| zone_ent_uncontrolled_shot_pct | FLOAT | Shot generation rate for dump-ins |
| zone_ent_goal_generated | INT | Entries that led to goal within 15s |
| zone_ent_goal_generated_pct | FLOAT | Goal generation rate for all entries |
| zone_ent_controlled_goal | INT | Controlled entries that led to goal within 15s |
| zone_ent_controlled_goal_pct | FLOAT | Goal generation rate for controlled entries |
| zone_ent_uncontrolled_goal | INT | Dump-ins that led to goal within 15s |
| zone_ent_uncontrolled_goal_pct | FLOAT | Goal generation rate for dump-ins |

(Same pattern applies to zone_ext_* columns)

---

## Success Metric Thresholds

| Metric | Threshold | Description |
|--------|-----------|-------------|
| Quick Shot | ≤10 seconds | time_to_next_sog <= 10 |
| Quick Goal | ≤15 seconds | time_to_next_goal <= 15 |
| Immediate Shot | ≤5 seconds | time_from_entry_to_shot populated |
| Defensive Stop | >15 seconds | time_to_next_sog > 15 OR null |

---

## is_rush Flag Logic

```python
# Populated in base_etl.py
events['is_rush'] = (
    events['event_detail_2'].str.contains('Rush', na=False) | 
    events['event_detail'].str.contains('Rush', na=False)
).astype(int)
```

**Related Tables:**
- `fact_rushes.csv` - All rush events (is_rush=1)
- `fact_rush_events.csv` - Links entry events to resulting shots

---

---

## Calculated Rush Metrics (Systematic Definition)

These columns use `is_rush_calculated` which is populated systematically:
- Zone entry that leads to shot within ≤5 seconds AND ≤5 events

This is stricter than the manual `is_rush` flag which relies on tracker judgment.

| Column | Type | Description |
|--------|------|-------------|
| rush_calc_off | INT | Offensive involvement on calculated rushes |
| rush_calc_def | INT | Defensive involvement on calculated rushes |
| rush_calc_off_goal | INT | Goals generated on calculated rushes (goal within 15s) |
| rush_calc_def_ga | INT | Goals allowed on calculated rushes |

### Comparison: Manual vs Calculated Rush

| Metric | Manual (is_rush) | Calculated (is_rush_calculated) |
|--------|------------------|----------------------------------|
| Events marked | 421 | 107 |
| Definition | Tracker marks event_detail_2 as 'Rush' | Zone entry → shot ≤5s, ≤5 events |
| Includes | Zone entries AND exits | Zone entries only |
| Overlap | 82 events have both flags | Stricter subset |

---

---

## v26.3 Rush Flag Definitions (Root Level in fact_events)

### Three Rush Definitions

| Flag | Count | Definition | Use Case |
|------|-------|------------|----------|
| `is_rush` | 421 | Tracker marks event_detail_2 as 'Rush' | Original tracker judgment |
| `is_rush_calculated` | 114 | Zone entry → shot ≤10s AND ≤5 events | Any quick attack |
| **`is_true_rush`** | 142 | **Controlled entry + shot ≤7 seconds** | **NHL-standard rush definition** |

### Supporting Flags

| Flag | Count | Definition |
|------|-------|-------------|
| `is_controlled_entry` | 338 | Zone entry with puck control (not dump-in) |
| `is_zone_entry` | 495 | Successful zone entries only |

### True Rush (NHL Definition)

Based on hockey analytics research, a true rush requires:
1. **Controlled zone entry** - carrying or passing the puck in (not dump-in)
2. **Shot within 7 seconds** - before defense can set up

This aligns with JFresh's definition: "a controlled zone entry where a shot/goal occurs within 5-7 seconds without losing possession"

### Player-Level Rush Metrics

**Tracker-based (is_rush):**
- `rush_involvement`, `rush_off_goal_generated`, etc.

**Calculated (is_rush_calculated):**
- `rush_calc_off`, `rush_calc_def`, `rush_calc_off_goal`, `rush_calc_def_ga`

**True Rush (is_true_rush - NHL definition):**
- `true_rush_off` - Offensive involvement on true rushes
- `true_rush_def` - Defensive involvement on true rushes
- `true_rush_off_goal` - Goals generated on true rushes
- `true_rush_def_ga` - Goals allowed on true rushes

---
