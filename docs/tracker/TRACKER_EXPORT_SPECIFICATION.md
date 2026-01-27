# BenchSight Tracker Export Specification

**Version:** 1.0
**Last Updated:** 2026-01-23
**Purpose:** Complete specification of tracker export format for ETL pipeline consumption

---

## Table of Contents

1. [Overview](#overview)
2. [Export Format](#export-format)
3. [Events Sheet Specification](#events-sheet-specification)
4. [Shifts Sheet Specification](#shifts-sheet-specification)
5. [XY Coordinate Sheets](#xy-coordinate-sheets)
6. [Metadata Sheet](#metadata-sheet)
7. [Valid Values Reference](#valid-values-reference)
8. [Column Requirements Matrix](#column-requirements-matrix)
9. [Data Validation Rules](#data-validation-rules)

---

## Overview

The BenchSight tracker exports game data as an Excel file (`{game_id}_tracking.xlsx`) with 7 sheets:

| Sheet | Purpose | Format | ETL Usage |
|-------|---------|--------|-----------|
| **metadata** | Game configuration | Single row | Game setup validation |
| **events** | Event tracking data | One row per player per event (LONG format) | Core fact_event_players table |
| **shifts** | Shift tracking data | One row per shift | Shift analysis tables |
| **xy_puck** | Puck XY coordinates | One row per XY point per event | fact_puck_xy, heatmaps |
| **xy_player** | Player XY coordinates | One row per XY point per player per event | fact_player_xy, positioning |
| **video** | Video file metadata | One row per video | Video sync (future) |
| **video_timing** | Timing calibration | Single row | Video-to-game-time mapping |

**Critical Design Decision:**
- Events sheet uses **LONG format**: One row per player per event
- This means a 2v2 event (2 event players + 2 opp players) creates **4 rows** with the same event_index
- ETL collapses this to **fact_events** (one row per event) and **fact_event_players** (one row per player per event)

---

## Export Format

### File Structure

```
{game_id}_tracking.xlsx
├── metadata (1 row)
├── events (N rows, long format)
├── shifts (M rows)
├── xy_puck (optional, XY tracking)
├── xy_player (optional, XY tracking)
├── video (optional, video metadata)
└── video_timing (optional, calibration)
```

### Naming Convention

- **File name:** `{game_id}_tracking.xlsx` (e.g., `18969_tracking.xlsx`)
- **Location:** `data/raw/games/{game_id}/{game_id}_tracking.xlsx`

---

## Events Sheet Specification

### Format

**LONG format:** One row per player per event

Example: A goal with 1 scorer + 1 assist + 1 goalie against = **3 rows**

| event_index | player_role | player_game_number | play_detail1 |
|-------------|-------------|--------------------|--------------|
| 1000 | event_player_1 | 12 | AttemptedShot |
| 1000 | event_player_2 | 7 | AssistPrimary |
| 1000 | opp_player_1 | 35 | |

### Column List (91 columns)

#### Input Columns (underscore suffix, optional for ETL)

These columns have `_` suffix and are **optional** - ETL can derive them from non-underscore versions.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `event_index_flag_` | int | Event index (1-based) | 1, 2, 3... |
| `sequence_index_flag_` | int | Sequence grouping | 1, 2, 3... |
| `play_index_flag_` | int | Play grouping | 1, 2, 3... |
| `linked_event_index_flag_` | int | Linked event (1-based) | 5 (links to event 5) |
| `assist_to_goal_index_flag_` | int | Goal this pass assists (1-based) | 10 (assists event 10) |
| `assist_primary_event_index_flag_` | int | Primary assist event (1-based) | 8 |
| `assist_secondary_event_index_flag_` | int | Secondary assist event (1-based) | 7 |
| `event_start_min_` | int | Start time minutes | 18, 17, 16... |
| `event_start_sec_` | int | Start time seconds | 0-59 |
| `event_end_min_` | int | End time minutes | 18, 17, 16... |
| `event_end_sec_` | int | End time seconds | 0-59 |
| `event_team_zone_` | str | Zone abbreviation | o, d, n |
| `event_type_` | str | Event type name | Goal, Shot, Pass |
| `event_detail_` | str | Event detail name | Goal_Scored |
| `event_detail_2_` | str | Secondary detail | ZE_Carried |
| `event_successful_` | str | Success flag | Y, N, (blank) |
| `team_` | str | Team abbreviation | h, a |
| `player_game_number_` | int | Jersey number | 12, 7, 35 |
| `role_abrev_binary_` | str | Role prefix | e, o |
| `play_detail1_` | str | Play detail 1 | AssistPrimary |
| `play_detail2_` | str | Play detail 2 | Deke |
| `play_detail_successful_` | str | Play success | Y, N, (blank) |
| `pressured_pressurer_` | str | Pressure status | Pressured, Pressurer, (blank) |
| `side_of_puck_` | str | Player side | Left, Right, (blank) |

#### Core Columns (required)

| Column | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| `period` | int | YES | Period number | 1, 2, 3, OT |
| `event_index` | int | YES | Event index (1000-based) | 1000, 1001, 1002... |
| `tracking_event_index` | int | YES | Tracking event index | 1000, 1001, 1002... |
| `game_id` | str | YES | Game identifier | 18969 |
| `home_team` | str | YES | Home team name | Platinum |
| `away_team` | str | YES | Away team name | Velodrome |

#### Event Keys

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `linked_event_index` | int | Linked event (1000-based) | 1005 |
| `assist_to_goal_index` | int | Goal this pass assists | 1010 |
| `assist_primary_event_index` | int | Primary assist event | 1008 |
| `assist_secondary_event_index` | int | Secondary assist event | 1007 |

#### Event Type Information

| Column | Type | Required | Description | Valid Values |
|--------|------|----------|-------------|--------------|
| `event_type_code` | str | PREFERRED | Event type code | Shot, Goal, Pass, Faceoff, etc. |
| `event_type_id` | str | PREFERRED | Event type ID | ET0001, ET0002, ... |
| `event_detail_code` | str | OPTIONAL | Event detail code | GS, PM, FC, etc. |
| `event_detail_id` | str | OPTIONAL | Event detail ID | ED0001, ED0002, ... |
| `event_detail_2_code` | str | OPTIONAL | Event detail 2 code | ZE_C, ZX_D, etc. |
| `event_detail_2_id` | str | OPTIONAL | Event detail 2 ID | ED0050, ED0051, ... |
| `event_detail` | str | BACKWARD | Event detail name (use codes instead) | Goal_Scored |
| `event_detail_2` | str | BACKWARD | Event detail 2 name | ZE_Carried |
| `event_successful` | str | OPTIONAL | Success flag | Y, N, (blank) |

**Note:** ETL prefers `*_code` and `*_id` columns over name columns. Names are validated against dim tables.

#### Time Columns

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `event_start_min` | int | Start minutes | 18 |
| `event_start_sec` | int | Start seconds | 0 |
| `event_end_min` | int | End minutes | 17 |
| `event_end_sec` | int | End seconds | 45 |
| `time_start_total_seconds` | int | Elapsed seconds at start | 150 |
| `time_end_total_seconds` | int | Elapsed seconds at end | 165 |
| `duration` | int | Event duration (seconds) | 15 |
| `event_running_start` | int | Running time at start | 1230 |
| `event_running_end` | int | Running time at end | 1245 |
| `period_start_total_running_seconds` | int | Period offset | 1080 |
| `running_video_time` | int | Video time (with intermissions) | 2130 |
| `running_intermission_duration` | int | Cumulative intermission time | 900 |

**Time Calculation Logic:**
- Clock counts **down** from period length (e.g., 18:00 → 0:00)
- `time_start_total_seconds` = `period_length_sec - (start_min * 60 + start_sec)`
- `event_running_start` = sum of all previous period seconds + `time_start_total_seconds`

#### Zone and Context

| Column | Type | Description | Valid Values |
|--------|------|-------------|--------------|
| `event_team_zone` | str | Full zone name | Offensive, Defensive, Neutral |
| `strength` | str | Ice strength | 5v5, 5v4, 4v5, 4v4, 3v3, etc. |
| `zone_change_index` | int | Zone change counter | 1, 2, 3... |
| `shift_index` | int | Shift this event belongs to | 1, 2, 3... |

#### Highlight and Video

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `is_highlight` | int | Highlight flag | 0, 1 |
| `video_url` | str | Individual highlight URL | https://... |

#### Player Information

| Column | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| `player_game_number` | int | YES | Jersey number | 12 |
| `player_name` | str | OPTIONAL | Player name | John Doe |
| `player_role` | str | YES | Player role | event_player_1, opp_player_1 |
| `role_abrev` | str | DERIVED | Role abbreviation | e1, e2, o1, o2 |
| `play_detail1` | str | OPTIONAL | Play detail 1 | AssistPrimary |
| `play_detail_2` | str | OPTIONAL | Play detail 2 | Deke |
| `play_detail_successful` | str | OPTIONAL | Play success | Y, N, (blank) |
| `pressured_pressurer` | str | OPTIONAL | Pressure status | Pressured, Pressurer |
| `side_of_puck` | str | OPTIONAL | Side of puck | Left, Right |

**Player Role Values:**
- Event team: `event_player_1`, `event_player_2`, `event_player_3`, `event_player_4`, `event_player_5`
- Opposing team: `opp_player_1`, `opp_player_2`, `opp_player_3`, `opp_player_4`, `opp_player_5`

**Critical Rule:** `event_player_1` is the primary player (scorer, shooter, passer, etc.)

#### XY Coordinates

##### Puck XY

| Column | Type | Description | Range |
|--------|------|-------------|-------|
| `puck_x_start` | float | Puck X at event start | -100 to 100 |
| `puck_y_start` | float | Puck Y at event start | -42.5 to 42.5 |
| `puck_x_start_adjusted` | float | Adjusted X (offense = +) | -100 to 100 |
| `puck_y_start_adjusted` | float | Adjusted Y | -42.5 to 42.5 |
| `puck_x_stop` | float | Puck X at event end | -100 to 100 |
| `puck_y_stop` | float | Puck Y at event end | -42.5 to 42.5 |
| `puck_x_stop_adjusted` | float | Adjusted X at end | -100 to 100 |
| `puck_y_stop_adjusted` | float | Adjusted Y at end | -42.5 to 42.5 |
| `is_xy_adjusted` | int | Has adjusted XY | 0, 1 |
| `needs_xy_adjustment` | int | Even period flag | 0, 1 |

##### Player XY

| Column | Type | Description | Range |
|--------|------|-------------|-------|
| `player_x_start` | float | Player X at event start | -100 to 100 |
| `player_y_start` | float | Player Y at event start | -42.5 to 42.5 |
| `player_x_start_adjusted` | float | Adjusted X | -100 to 100 |
| `player_y_start_adjusted` | float | Adjusted Y | -42.5 to 42.5 |
| `player_x_stop` | float | Player X at event end | -100 to 100 |
| `player_y_stop` | float | Player Y at event end | -42.5 to 42.5 |
| `player_x_stop_adjusted` | float | Adjusted X at end | -100 to 100 |
| `player_y_stop_adjusted` | float | Adjusted Y at end | -42.5 to 42.5 |

##### Net XY

| Column | Type | Description | Range |
|--------|------|-------------|-------|
| `net_x` | float | Net X coordinate | -100 to 100 |
| `net_y` | float | Net Y coordinate | -42.5 to 42.5 |

**XY Coordinate System:**
- Origin (0, 0) = center ice
- X-axis: -100 (left boards) to +100 (right boards)
- Y-axis: -42.5 (bottom boards) to +42.5 (top boards)
- Adjusted XY: Offense = positive X, Defense = negative X (normalized across periods)

#### Legacy Columns

| Column | Type | Description | Note |
|--------|------|-------------|------|
| `Type` | str | Event type (legacy) | Use `event_type_code` instead |

---

## Shifts Sheet Specification

### Format

**One row per shift** (not per player - player numbers are in columns)

### Column List (66 columns)

#### Core Shift Information

| Column | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| `shift_index` | int | YES | Shift counter (1-based) | 1, 2, 3... |
| `Period` | int | YES | Period number | 1, 2, 3, OT |
| `game_id` | str | YES | Game identifier | 18969 |
| `home_team` | str | YES | Home team name | Platinum |
| `away_team` | str | YES | Away team name | Velodrome |

#### Shift Timing

| Column | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| `shift_start_min` | int | YES | Start minutes | 18 |
| `shift_start_sec` | int | YES | Start seconds | 0 |
| `shift_end_min` | int | YES | End minutes | 16 |
| `shift_end_sec` | int | YES | End seconds | 30 |
| `shift_duration` | int | DERIVED | Duration (seconds) | 90 |
| `stoppage_time` | int | DERIVED | Stoppage time (seconds) | 15 |
| `shift_start_total_seconds` | int | DERIVED | Elapsed at start | 0 |
| `shift_end_total_seconds` | int | DERIVED | Elapsed at end | 90 |
| `period_start_total_running_seconds` | int | DERIVED | Period offset | 1080 |
| `running_video_time` | int | OPTIONAL | Video time | 2130 |
| `shift_start_running_time` | int | DERIVED | Running start | 1080 |
| `shift_end_running_time` | int | DERIVED | Running end | 1170 |

#### Shift Types

| Column | Type | Required | Description | Valid Values |
|--------|------|----------|-------------|--------------|
| `shift_start_type` | str | YES | How shift started | Faceoff, OnTheFly, PeriodStart, DeadIce, Intermission |
| `shift_stop_type` | str | YES | How shift ended | Faceoff, OnTheFly, Stoppage, PeriodEnd |

**Special Shift Types:**
- **DeadIce:** Placeholder shift for time between whistles (all player columns blank)
- **Intermission:** Placeholder for intermission breaks (all player columns blank)

#### Player Roster (Home Team)

| Column | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| `home_forward_1` | int | YES (if regular shift) | Jersey number | 12 |
| `home_forward_2` | int | YES (if regular shift) | Jersey number | 7 |
| `home_forward_3` | int | YES (if regular shift) | Jersey number | 19 |
| `home_defense_1` | int | YES (if regular shift) | Jersey number | 5 |
| `home_defense_2` | int | YES (if regular shift) | Jersey number | 22 |
| `home_goalie` | int | YES (if regular shift) | Jersey number | 35 |
| `home_xtra` | str | OPTIONAL | Extra skaters (comma-separated) | 8,14 |

#### Player Roster (Away Team)

| Column | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| `away_forward_1` | int | YES (if regular shift) | Jersey number | 9 |
| `away_forward_2` | int | YES (if regular shift) | Jersey number | 11 |
| `away_forward_3` | int | YES (if regular shift) | Jersey number | 17 |
| `away_defense_1` | int | YES (if regular shift) | Jersey number | 2 |
| `away_defense_2` | int | YES (if regular shift) | Jersey number | 4 |
| `away_goalie` | int | YES (if regular shift) | Jersey number | 31 |
| `away_xtra` | str | OPTIONAL | Extra skaters (comma-separated) | 13,20 |

#### Strength and Situation

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `strength` | str | Ice strength | 5v5, 5v4, 4v5 |
| `home_team_strength` | int | Home skaters on ice | 5 |
| `away_team_strength` | int | Away skaters on ice | 5 |
| `home_team_en` | int | Home empty net flag | 0, 1 |
| `away_team_en` | int | Away empty net flag | 0, 1 |
| `home_team_pk` | int | Home penalty kill flag | 0, 1 |
| `home_team_pp` | int | Home power play flag | 0, 1 |
| `away_team_pp` | int | Away power play flag | 0, 1 |
| `away_team_pk` | int | Away penalty kill flag | 0, 1 |
| `situation` | str | Combined situation | EV, PP, SH, 4v4 |

#### Goals and Plus/Minus

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `home_goals` | int | Home goals at shift start | 0, 1, 2 |
| `away_goals` | int | Away goals at shift start | 0, 1, 2 |
| `home_team_plus` | int | Home goals during shift (EV/SH only) | 0, 1 |
| `home_team_minus` | int | Away goals during shift (EV/SH only) | 0, 1 |
| `away_team_plus` | int | Away goals during shift (EV/SH only) | 0, 1 |
| `away_team_minus` | int | Home goals during shift (EV/SH only) | 0, 1 |

**Plus/Minus Rules:**
- Only count goals that are **not** power play goals
- Home PP goal = no +/- change
- Away PP goal = no +/- change
- EV and SH goals count for +/-

#### Zone Start/End

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `home_ozone_start` | int | Home shift started in O-zone | 0, 1 |
| `home_ozone_end` | int | Home shift ended in O-zone | 0, 1 |
| `home_dzone_start` | int | Home shift started in D-zone | 0, 1 |
| `home_dzone_end` | int | Home shift ended in D-zone | 0, 1 |
| `home_nzone_start` | int | Home shift started in N-zone | 0, 1 |
| `home_nzone_end` | int | Home shift ended in N-zone | 0, 1 |
| `away_ozone_start` | int | Away shift started in O-zone | 0, 1 |
| `away_ozone_end` | int | Away shift ended in O-zone | 0, 1 |
| `away_dzone_start` | int | Away shift started in D-zone | 0, 1 |
| `away_dzone_end` | int | Away shift ended in D-zone | 0, 1 |
| `away_nzone_start` | int | Away shift started in N-zone | 0, 1 |
| `away_nzone_end` | int | Away shift ended in N-zone | 0, 1 |

**Zone Logic:**
- Zones are from **first** and **last** events in the shift
- O-zone = offensive zone, D-zone = defensive zone, N-zone = neutral zone
- Determined from event zone and team perspective

#### Puck Location

| Column | Type | Description | Range |
|--------|------|-------------|-------|
| `puck_start_x` | float | Puck X at shift start | -100 to 100 |
| `puck_start_y` | float | Puck Y at shift start | -42.5 to 42.5 |
| `puck_end_x` | float | Puck X at shift end | -100 to 100 |
| `puck_end_y` | float | Puck Y at shift end | -42.5 to 42.5 |
| `needs_xy_adjustment` | int | Even period flag | 0, 1 |

**Puck Location Logic:**
- Derived from closest event within 5 seconds of shift start/end
- Falls back to stored start_xy/end_xy if available

---

## XY Coordinate Sheets

### xy_puck Sheet

**Purpose:** All puck XY coordinates captured during events

**Format:** One row per XY point per event

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `event_index` | int | Event index (1000-based) | 1000 |
| `game_id` | str | Game identifier | 18969 |
| `period` | int | Period number | 1 |
| `event_type` | str | Event type | Pass |
| `event_detail` | str | Event detail | Pass_Completed |
| `xy_slot` | int | XY point sequence | 1, 2, 3... |
| `x` | float | Raw X coordinate | 45.35 |
| `y` | float | Raw Y coordinate | 28.44 |
| `x_adjusted` | float | Adjusted X | 45.35 |
| `y_adjusted` | float | Adjusted Y | 28.44 |
| `is_xy_adjusted` | int | Has adjusted XY | 0, 1 |
| `needs_xy_adjustment` | int | Even period flag | 0, 1 |
| `is_start` | int | First XY point flag | 0, 1 |
| `is_stop` | int | Last XY point flag | 0, 1 |

### xy_player Sheet

**Purpose:** All player XY coordinates captured during events

**Format:** One row per XY point per player per event

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `event_index` | int | Event index (1000-based) | 1000 |
| `game_id` | str | Game identifier | 18969 |
| `period` | int | Period number | 1 |
| `event_type` | str | Event type | Pass |
| `event_detail` | str | Event detail | Pass_Completed |
| `player_number` | int | Jersey number | 12 |
| `player_name` | str | Player name | John Doe |
| `player_role` | str | Player role | event_player_1 |
| `xy_slot` | int | XY point sequence | 1, 2, 3... |
| `x` | float | Raw X coordinate | 45.05 |
| `y` | float | Raw Y coordinate | 30.53 |
| `x_adjusted` | float | Adjusted X | 45.05 |
| `y_adjusted` | float | Adjusted Y | 30.53 |
| `is_xy_adjusted` | int | Has adjusted XY | 0, 1 |
| `needs_xy_adjustment` | int | Even period flag | 0, 1 |
| `is_start` | int | First XY point flag | 0, 1 |
| `is_stop` | int | Last XY point flag | 0, 1 |

**XY Tracking Notes:**
- XY sheets are **optional** - tracker can export events without XY data
- `xy_slot` is the sequence number for multiple XY points in a single event
- `is_start` = 1 for first XY point, `is_stop` = 1 for last XY point
- For single-point events, both `is_start` and `is_stop` = 1

---

## Metadata Sheet

**Purpose:** Game configuration and export metadata

**Format:** Single row with configuration values

| Column | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| `game_id` | str | YES | Game identifier | 18969 |
| `home_team` | str | YES | Home team name | Platinum |
| `away_team` | str | YES | Away team name | Velodrome |
| `period_length_minutes` | int | YES | Period length | 18 |
| `home_attacks_right_p1` | int | YES | Home offensive direction P1 | 0 (left), 1 (right) |
| `export_timestamp` | str | YES | Export time (ISO 8601) | 2026-01-18T00:00:24.892Z |
| `tracker_version` | str | YES | Tracker version | v28.0 |
| `total_videos` | int | OPTIONAL | Number of videos | 1 |

**Critical Metadata:**
- `home_attacks_right_p1`: Determines XY coordinate adjustment logic
  - 1 = Home attacks right in P1/P3 (odd periods)
  - 0 = Home attacks left in P1/P3
  - Teams switch ends in even periods (P2, OT2, etc.)
- `period_length_minutes`: Used for time calculations (usually 18 for NORAD)

---

## Valid Values Reference

### Event Types (23 types)

| Code | Name | Category | Corsi | Fenwick |
|------|------|----------|-------|---------|
| Shot | Shot | offensive | YES | YES |
| Save | Save | goaltending | NO | NO |
| Pass | Pass | playmaking | NO | NO |
| Faceoff | Faceoff | faceoff | NO | NO |
| Turnover | Turnover | turnover | NO | NO |
| Zone_Entry_Exit | Zone Entry Exit | transition | NO | NO |
| Possession | Possession | possession | NO | NO |
| Penalty | Penalty | penalty | NO | NO |
| Hit | Hit | physical | NO | NO |
| Block | Block | defensive | YES | NO |
| Stoppage | Stoppage | stoppage | NO | NO |
| Goal | Goal | scoring | YES | YES |
| PenaltyShot_Shootout | Penalty Shot or Shootout | offensive | NO | NO |
| LoosePuck | Loose Puck | transition | NO | NO |
| Rebound | Rebound from Shot | goaltending | NO | NO |
| DeadIce | Deadice | time | NO | NO |
| Play | Play | other | NO | NO |
| Timeout | Clockstop | time | NO | NO |
| Intermission | Intermission | time | NO | NO |
| Clockstop | Clockstop | time | NO | NO |
| GameStart | Game Start | time | NO | NO |
| GameEnd | Game End | time | NO | NO |
| Penalty_Delayed | Delayed Penalty | penalty | NO | NO |

### Event Details (55 details, showing key ones)

| Code | Name | Event Type | Is Goal | Is SOG |
|------|------|------------|---------|--------|
| Faceoff | Faceoff | Faceoff | NO | NO |
| Faceoff_AfterGoal | Faceoff AfterGoal | Faceoff | NO | NO |
| Goal_Scored | Goal Scored | Goal | **YES** | YES |
| Pass_Completed | Pass Completed | Pass | NO | NO |
| Pass_Intercepted | Pass Intercepted | Pass | NO | NO |
| Pass_Missed | Pass Missed | Pass | NO | NO |
| Penalty_Minor | Penalty Minor | Penalty | NO | NO |
| Penalty_Major | Penalty Major | Penalty | NO | NO |
| Shot_OnNet | Shot OnNet | Shot | NO | YES |
| Shot_Missed | Shot Missed | Shot | NO | NO |
| Shot_Blocked | Shot Blocked | Shot | NO | NO |
| ZE_Carried | Zone Entry Carried | Zone_Entry_Exit | NO | NO |
| ZE_Dumped | Zone Entry Dumped | Zone_Entry_Exit | NO | NO |
| ZE_Passed | Zone Entry Passed | Zone_Entry_Exit | NO | NO |
| ZX_Carried | Zone Exit Carried | Zone_Entry_Exit | NO | NO |
| ZX_Cleared | Zone Exit Cleared | Zone_Entry_Exit | NO | NO |

**Critical Goal Rule:**
- Goals are ONLY counted when `event_type = 'Goal'` AND `event_detail = 'Goal_Scored'`
- `event_type = 'Shot'` with `event_detail = 'Goal'` is a shot attempt, NOT a goal

### Play Details (111 details, showing key ones)

| Code | Name | Category | Skill Level |
|------|------|----------|-------------|
| AssistPrimary | AssistPrimary | scoring | Medium |
| AssistSecondary | AssistSecondary | scoring | Medium |
| AssistTertiary | AssistTertiary | scoring | Medium (not counted) |
| AttemptedShot | AttemptedShot | scoring | Medium |
| Deke | Deke | offensive | High |
| Backcheck | Backcheck | defensive | Medium |
| Forecheck | Forecheck | defensive | Medium |
| BeatWide | BeatWide | offensive | High |
| BeatMiddle | BeatMiddle | offensive | High |
| BeatSpeed | BeatSpeed | offensive | High |
| ReceiverMissed | ReceiverMissed | playmaking | Low |
| ReceiverCompleted | ReceiverCompleted | playmaking | Medium |
| Turnover | Turnover | turnover | Low |
| TurnoverForced | TurnoverForced | defensive | High |

**Micro-Stat Counting Rules:**
1. Only count for `player_role = 'event_player_1'` to avoid duplicates
2. For linked events, only count once per `linked_event_key`
3. Example: Pass > Zone Exit > Turnover linked event:
   - If event_player_2 has `ReceiverMissed` in all 3 events
   - Only count `ReceiverMissed` once for the entire linked chain

### Play Detail 2 (same 111 values as Play Detail)

Play Detail 2 uses the same dimension table as Play Detail. It allows tracking a secondary action (e.g., `play_detail1 = 'Deke'`, `play_detail_2 = 'AttemptedShot'`).

### Player Roles

**Event Team Players:**
- `event_player_1` - Primary player (scorer, shooter, passer)
- `event_player_2` - Secondary player (assist, receiver)
- `event_player_3` - Tertiary player
- `event_player_4`, `event_player_5` - Additional players

**Opposing Team Players:**
- `opp_player_1` - Primary opponent (goalie, defender)
- `opp_player_2` - Secondary opponent
- `opp_player_3`, `opp_player_4`, `opp_player_5` - Additional opponents

**Critical Rule:** `event_player_1` is the primary actor in every event.

---

## Column Requirements Matrix

### Events Sheet

| Column Category | Required | Optional | Derived |
|----------------|----------|----------|---------|
| **Keys** | `event_index`, `game_id`, `period` | `linked_event_index`, `assist_*` | `event_id` (ETL) |
| **Time** | `event_start_min`, `event_start_sec` | `event_end_*` | All `*_total_seconds` columns |
| **Event Type** | `event_type_code`, `event_type_id` | `event_detail_*`, `event_successful` | - |
| **Teams** | `home_team`, `away_team` | - | `team_venue`, `team_venue_id` |
| **Players** | `player_game_number`, `player_role` | `player_name`, `play_detail*` | `player_id` (via lookup) |
| **Zone** | - | `event_team_zone` | `event_zone_id` |
| **XY** | - | All `puck_*`, `player_*` | `*_adjusted` |

### Shifts Sheet

| Column Category | Required | Optional | Derived |
|----------------|----------|----------|---------|
| **Keys** | `shift_index`, `game_id`, `period` | - | `shift_id` (ETL) |
| **Time** | `shift_start_*`, `shift_end_*` | - | All `*_total_seconds` columns |
| **Players** | `home_forward_*`, `home_defense_*`, `home_goalie`, `away_*` | `home_xtra`, `away_xtra` | - |
| **Strength** | - | `strength`, `*_team_strength` | All `*_pp`, `*_pk` flags |
| **Goals** | - | - | All goal and +/- columns |
| **Zone** | - | - | All zone start/end flags |

---

## Data Validation Rules

### Event Validation

1. **Goal Counting:** `event_type = 'Goal'` AND `event_detail = 'Goal_Scored'` AND `player_role = 'event_player_1'`
2. **Event Index:** Must be unique per game (within events sheet)
3. **Time:** `event_start_*` must be valid game time (0:00 to period_length:00)
4. **Player Role:** Must be one of 10 valid roles (event_player_1-5, opp_player_1-5)
5. **Team:** `team_` must be 'h' or 'a'
6. **Zone:** `event_team_zone_` must be 'o', 'd', or 'n'
7. **Linked Events:** `linked_event_index` must reference a valid event in the same game
8. **Assists:** `assist_to_goal_index` must reference a Goal event

### Shift Validation

1. **Shift Index:** Must be unique per game
2. **Time:** `shift_start_*` < `shift_end_*` within the same period
3. **Player Count:** Home and away should have valid roster (typically 5 skaters + 1 goalie)
4. **Strength:** Derived from player counts (e.g., 5v5, 5v4)
5. **DeadIce/Intermission:** Special shifts can have blank player columns

### XY Validation

1. **Coordinate Range:** X: -100 to 100, Y: -42.5 to 42.5
2. **Event Reference:** `event_index` must exist in events sheet
3. **XY Slot:** Must be sequential (1, 2, 3...) per event
4. **Start/Stop:** First slot has `is_start=1`, last slot has `is_stop=1`

---

## ETL Processing Notes

### What ETL Expects

1. **Minimum Required Sheets:** `events`, `shifts`, `metadata`
2. **Optional Sheets:** `xy_puck`, `xy_player`, `video`, `video_timing`
3. **Underscore Columns:** ETL drops all `*_` columns after validation
4. **Player Lookup:** ETL uses `(game_id, team_venue, player_game_number)` → `player_id` lookup
5. **Key Generation:** ETL generates all `*_key` and `*_id` columns from base data

### What ETL Derives

1. **Keys:** `event_id`, `shift_id`, `sequence_key`, `play_key`, `shift_key`
2. **Foreign Keys:** All `*_id` columns (period_id, event_type_id, player_id, etc.)
3. **Flags:** `is_goal`, `is_shot`, `is_corsi`, `is_fenwick`
4. **Time Calculations:** All `*_total_seconds`, `*_running_*` columns (if missing)
5. **Player Resolution:** `player_id` from jersey numbers via `fact_gameroster` lookup

### Robust Design

- ETL can handle **minimal** exports (just required columns)
- ETL can handle **maximal** exports (all 91 columns)
- Missing columns are derived or filled with defaults
- Underscore columns are treated as "input hints" but not required

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-23 | Initial comprehensive specification |

---

## Related Documentation

- **Tracker Logic:** `docs/tracker/TRACKER_LOGIC_DOCUMENTATION.md`
- **Data Dictionary:** `docs/data/DATA_DICTIONARY.md`
- **ETL Phase 3:** `docs/walkthrough/etl/12-tracker.md`
- **Dimension Tables:** BLB_Tables.xlsx (dim_event_type, dim_event_detail, dim_play_detail)
