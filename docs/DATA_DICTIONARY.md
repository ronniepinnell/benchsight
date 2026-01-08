# BenchSight Data Dictionary v16.08

**Version:** 16.08  
**Updated:** January 8, 2026


**Auto-generated:** 2026-01-07 21:13  
**Metadata source:** `config/TABLE_METADATA.json`

---

## Overview

| Metric | Count |
|--------|-------|
| Total Tables | 59 |
| Dimension Tables | 33 |
| Fact Tables | 24 |
| QA Tables | 2 |
| Games Tracked | 4 |
| Total Goals | 17 |

---

## ⚠️ Critical Rules

### Goal Counting

**Rule:** `event_type='Goal' AND event_detail='Goal_Scored'`

⚠️ **Warning:** Shot_Goal is the SHOT that resulted in a goal, NOT the goal itself!

```python
df[(df['event_type']=='Goal') & (df['event_detail']=='Goal_Scored')]
```

### Player Roles

| Role | Meaning |
|------|--------|
| `event_player_1` | PRIMARY player - scorer for goals, shooter for shots, passer for passes |
| `event_player_2` | SECONDARY player - primary assist, pass receiver |
| `event_player_3` | TERTIARY player - secondary assist |
| `event_player_4-6` | Additional on-ice players at time of event |

### Time Formats

| Field | Format |
|-------|--------|
| `game_clock` | Time REMAINING in period (MM:SS format, counts down) |
| `elapsed_time` | Time ELAPSED in period (seconds, counts up) |
| `shift_duration` | Duration in seconds |

---

## Stat Calculation Formulas

| Stat | Formula |
|------|--------|
| `goals` | `COUNT(fact_event_players) WHERE event_type='Goal' AND event_detail='Goal_Scored' AND player_role='event_player_1'` |
| `assists` | `COUNT(fact_event_players) WHERE event_type='Goal' AND event_detail='Goal_Scored' AND player_role IN ('event_player_2','event_player_3')` |
| `primary_assists` | `COUNT(fact_event_players) WHERE event_type='Goal' AND event_detail='Goal_Scored' AND player_role='event_player_2'` |
| `secondary_assists` | `COUNT(fact_event_players) WHERE event_type='Goal' AND event_detail='Goal_Scored' AND player_role='event_player_3'` |
| `points` | `goals + assists` |
| `shots` | `COUNT(fact_event_players) WHERE event_type='Shot' AND player_role='event_player_1'` |
| `shots_on_goal` | `COUNT(fact_event_players) WHERE event_type='Shot' AND event_detail LIKE 'Shot_OnNet%' AND player_role='event_player_1'` |
| `shooting_pct` | `(goals / shots) * 100` |
| `faceoff_wins` | `COUNT(fact_event_players) WHERE event_type='Faceoff' AND player_role='event_player_1'` |
| `faceoff_losses` | `COUNT(fact_event_players) WHERE event_type='Faceoff' AND player_role='event_player_2'` |
| `faceoff_pct` | `(faceoff_wins / (faceoff_wins + faceoff_losses)) * 100` |
| `toi_total` | `SUM(fact_shift_players.shift_duration) WHERE player_id = X` |
| `toi_avg` | `toi_total / games_played` |
| `shifts_per_game` | `COUNT(fact_shift_players) / games_played` |
| `avg_shift_length` | `toi_total / shift_count` |

---

## Table of Contents

### Dimension Tables (33)
- [dim_assist_type](#dim_assist_type)
- [dim_danger_level](#dim_danger_level)
- [dim_event_detail](#dim_event_detail)
- [dim_event_detail_2](#dim_event_detail_2)
- [dim_event_type](#dim_event_type)
- [dim_game_state](#dim_game_state)
- [dim_giveaway_type](#dim_giveaway_type)
- [dim_league](#dim_league)
- [dim_pass_type](#dim_pass_type)
- [dim_period](#dim_period)
- [dim_play_detail](#dim_play_detail)
- [dim_play_detail_2](#dim_play_detail_2)
- [dim_player](#dim_player)
- [dim_player_role](#dim_player_role)
- [dim_playerurlref](#dim_playerurlref)
- [dim_position](#dim_position)
- [dim_randomnames](#dim_randomnames)
- [dim_schedule](#dim_schedule)
- [dim_season](#dim_season)
- [dim_shift_quality_tier](#dim_shift_quality_tier)
- [dim_shift_start_type](#dim_shift_start_type)
- [dim_shift_stop_type](#dim_shift_stop_type)
- [dim_shot_type](#dim_shot_type)
- [dim_situation](#dim_situation)
- [dim_stoppage_type](#dim_stoppage_type)
- [dim_success](#dim_success)
- [dim_takeaway_type](#dim_takeaway_type)
- [dim_team](#dim_team)
- [dim_time_bucket](#dim_time_bucket)
- [dim_venue](#dim_venue)
- [dim_zone](#dim_zone)
- [dim_zone_entry_type](#dim_zone_entry_type)
- [dim_zone_exit_type](#dim_zone_exit_type)

### Fact Tables (24)
- [fact_breakouts](#fact_breakouts)
- [fact_cycle_events](#fact_cycle_events)
- [fact_draft](#fact_draft)
- [fact_event_players](#fact_event_players)
- [fact_events](#fact_events)
- [fact_faceoffs](#fact_faceoffs)
- [fact_gameroster](#fact_gameroster)
- [fact_high_danger_chances](#fact_high_danger_chances)
- [fact_leadership](#fact_leadership)
- [fact_penalties](#fact_penalties)
- [fact_player_game_position](#fact_player_game_position)
- [fact_plays](#fact_plays)
- [fact_registration](#fact_registration)
- [fact_rushes](#fact_rushes)
- [fact_saves](#fact_saves)
- [fact_scoring_chances_detailed](#fact_scoring_chances_detailed)
- [fact_season_summary](#fact_season_summary)
- [fact_sequences](#fact_sequences)
- [fact_shift_players](#fact_shift_players)
- [fact_shifts](#fact_shifts)
- [fact_tracking](#fact_tracking)
- [fact_turnovers_detailed](#fact_turnovers_detailed)
- [fact_zone_entries](#fact_zone_entries)
- [fact_zone_exits](#fact_zone_exits)

### QA Tables (2)
- [qa_data_completeness](#qa_data_completeness)
- [qa_goal_accuracy](#qa_goal_accuracy)

---

## Dimension Tables

### dim_assist_type

**Rows:** 5 | **Columns:** 5

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `assist_type_id` | object | Foreign key reference | AT001 |
| `assist_type_code` | object | - | primary |
| `assist_type_name` | object | - | Primary Assist |
| `points_value` | int64 | Total points (goals + assists) | 1 |
| `description` | object | - | Last pass before goal |

---

### dim_danger_level

**Rows:** 3 | **Columns:** 4

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `danger_level_id` | object | Foreign key reference | DL01 |
| `danger_level_code` | object | - | high |
| `danger_level_name` | object | - | High Danger |
| `xg_multiplier` | float64 | - | 1.5 |

---

### dim_event_detail

**Lookup table for event subtypes**

| Property | Value |
|----------|-------|
| Grain | One row per event detail |
| Rows | 31 |
| Columns | 10 |

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `event_detail_id` | object | Detailed event subtype | ED0001 |
| `event_detail_code` | object | Detailed event subtype | Shot_OnNetSaved |
| `event_detail_name` | object | Detailed event subtype | Shot OnNetSaved |
| `event_type` | object | Type of event (Goal, Shot, Pass, etc.) | Shot |
| `category` | object | - | shot_on_goal |
| `is_shot_on_goal` | bool | Boolean flag | True |
| `is_goal` | bool | Boolean flag | False |
| `is_miss` | bool | Boolean flag | False |
| `is_block` | bool | Boolean flag | False |
| `danger_potential` | object | - | medium |

---

### dim_event_detail_2

**Rows:** 97 | **Columns:** 4

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `event_detail_2_id` | object | Detailed event subtype | ED201 |
| `event_detail_2_code` | object | Detailed event subtype | Deke |
| `event_detail_2_name` | object | Detailed event subtype | Deke |
| `category` | object | - | other |

---

### dim_event_type

**Lookup table for event types**

| Property | Value |
|----------|-------|
| Grain | One row per event type |
| Rows | 12 |
| Columns | 7 |

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `event_type_id` | object | Type of event (Goal, Shot, Pass, etc.) | ET0001 |
| `event_type_code` | object | Type of event (Goal, Shot, Pass, etc.) | Shot |
| `event_type_name` | object | Type of event (Goal, Shot, Pass, etc.) | Shot |
| `event_category` | object | - | offensive |
| `description` | object | - | Shot attempt on goal |
| `is_corsi` | bool | Boolean flag | True |
| `is_fenwick` | bool | Boolean flag | True |

---

### dim_game_state

**Rows:** 6 | **Columns:** 6

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `game_state_id` | object | Foreign key reference | GS01 |
| `game_state_code` | object | - | leading |
| `game_state_name` | object | - | Leading |
| `goal_diff_min` | int64 | - | 1 |
| `goal_diff_max` | int64 | - | 99 |
| `description` | object | - | Team is ahead |

---

### dim_giveaway_type

**Rows:** 15 | **Columns:** 3

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `giveaway_type_id` | object | Foreign key reference | GA0001 |
| `giveaway_type_code` | object | - | Giveaway_AttemptedZoneCle... |
| `giveaway_type_name` | object | - | Giveaway AttemptedZoneCle... |

---

### dim_league

**Rows:** 2 | **Columns:** 2

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `league_id` | object | Foreign key reference | N |
| `league` | object | - | NORAD |

---

### dim_pass_type

**Rows:** 8 | **Columns:** 4

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `pass_type_id` | object | Foreign key reference | PT0001 |
| `pass_type_code` | object | - | Forehand |
| `pass_type_name` | object | - | Forehand |
| `description` | object | - | Standard forehand pass |

---

### dim_period

**Rows:** 5 | **Columns:** 5

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `period_id` | object | Game period (1, 2, 3, OT) | P01 |
| `period_number` | int64 | Game period (1, 2, 3, OT) | 1 |
| `period_name` | object | Game period (1, 2, 3, OT) | 1st Period |
| `period_type` | object | Game period (1, 2, 3, OT) | regulation |
| `period_minutes` | int64 | Game period (1, 2, 3, OT) | 18 |

---

### dim_play_detail

**Rows:** 126 | **Columns:** 6

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `play_detail_id` | object | Foreign key reference | PD0001 |
| `play_detail_code` | object | - | AssistPrimary |
| `play_detail_name` | object | - | AssistPrimary |
| `play_category` | object | - | scoring |
| `skill_level` | object | - | Standard |
| `description` | object | - | Primary assist on goal |

---

### dim_play_detail_2

**Rows:** 62 | **Columns:** 6

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `play_detail_2_id` | object | Foreign key reference | PD201 |
| `play_detail_2_code` | object | - | AttemptedBreakOutPass |
| `play_detail_2_name` | object | - | AttemptedBreakOutPass |
| `play_category` | object | - | offensive |
| `skill_level` | object | - | Standard |
| `description` | object | - | Secondary play detail fro... |

---

### dim_player

**Player master data - names, positions, profile info**

| Property | Value |
|----------|-------|
| Grain | One row per player (all-time) |
| Rows | 337 |
| Columns | 27 |

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `player_first_name` | object | - | Sam |
| `player_last_name` | object | - | Downs |
| `player_full_name` | object | - | Sam Downs |
| `player_id` | object | Unique player identifier | P100001 |
| `player_primary_position` | object | Player position (C, LW, RW, D, G) | Forward |
| `current_skill_rating` | int64 | - | 6 |
| `player_hand` | float64 | - |  |
| `birth_year` | float64 | - | 1986.0 |
| `player_gender` | object | - | M |
| `highest_beer_league` | object | - | B - Platinum Group |
| `player_rating_ly` | int64 | - | 6 |
| `player_notes` | float64 | - |  |
| `player_leadership` | object | - | A |
| `player_norad` | object | - | Y |
| `player_csaha` | float64 | - |  |
| `player_norad_primary_number` | float64 | - |  |
| `player_csah_primary_number` | float64 | - |  |
| `player_norad_current_team` | object | - | Velodrome |
| `player_csah_current_team` | float64 | - |  |
| `player_norad_current_team_id` | object | Unique team identifier | N10010 |
| `player_csah_current_team_id` | float64 | Unique team identifier |  |
| `other_url` | object | - | https://www.eliteprospect... |
| `player_url` | object | - | https://www.noradhockey.c... |
| `player_image` | object | - | https://i0.wp.com/www.nor... |
| `random_player_first_name` | object | - | Joshua Walton |
| `random_player_last_name` | object | - | Joshua |
| `random_player_full_name` | object | - | Walton |

---

### dim_player_role

**Rows:** 14 | **Columns:** 5

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `role_id` | object | Foreign key reference | PR01 |
| `role_code` | object | - | event_player_1 |
| `role_name` | object | - | Event Player 1 |
| `role_type` | object | - | event_team |
| `sort_order` | int64 | - | 1 |

---

### dim_playerurlref

**Rows:** 548 | **Columns:** 3

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `n_player_url` | object | - | Zach Schirm - SUB - 6 |
| `player_full_name` | object | - | SUB - Zach Schirm - SUB |
| `n_player_id_2` | object | Unique player identifier | Zach Schirm - SUB - 6 |

---

### dim_position

**Rows:** 6 | **Columns:** 4

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `position_id` | object | Player position (C, LW, RW, D, G) | POS01 |
| `position_code` | object | Player position (C, LW, RW, D, G) | C |
| `position_name` | object | Player position (C, LW, RW, D, G) | Center |
| `position_type` | object | Player position (C, LW, RW, D, G) | forward |

---

### dim_randomnames

**Rows:** 486 | **Columns:** 5

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `random_full_name` | object | - | Zachary Perry |
| `random_first_name` | object | - | Zachary |
| `random_last_name` | object | - | Perry |
| `gender` | object | - | M |
| `name_used` | object | - | Y |

---

### dim_schedule

**Rows:** 562 | **Columns:** 44

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `game_id` | int64 | Unique game identifier from NORAD league | 18619 |
| `season` | int64 | - | 2025 |
| `season_id` | object | Foreign key reference | N2025S |
| `game_url` | object | - | https://www.noradhockey.c... |
| `home_team_game_id` | object | Unique game identifier | 18619N10022 |
| `away_team_game_id` | object | Unique game identifier | 18619N10023 |
| `date` | object | - | 2025-07-13 00:00:00 |
| `game_time` | object | - | 18:45:00 |
| `home_team_name` | object | - | Red |
| `away_team_name` | object | - | Green |
| `home_team_id` | object | Unique team identifier | N10022 |
| `away_team_id` | object | Unique team identifier | N10023 |
| `head_to_head_id` | object | Foreign key reference | N10022_N10023 |
| `game_type` | object | - | Regular |
| `playoff_round` | object | - | Championship |
| `last_period_type` | object | Game period (1, 2, 3, OT) | Regulation |
| `period_length` | object | Game period (1, 2, 3, OT) | 00:18:00 |
| `ot_period_length` | object | Game period (1, 2, 3, OT) | 00:00:00 |
| `shootout_rounds` | float64 | - | 0.0 |
| `home_total_goals` | int64 | Goals scored | 4 |
| `away_total_goals` | int64 | Goals scored | 5 |
| `home_team_period1_goals` | float64 | Game period (1, 2, 3, OT) | 1.0 |
| `home_team_period2_goals` | float64 | Game period (1, 2, 3, OT) | 0.0 |
| `home_team_period3_goals` | float64 | Game period (1, 2, 3, OT) | 0.0 |
| `home_team_periodOT_goals` | float64 | Game period (1, 2, 3, OT) | 0.0 |
| `away_team_period1_goals` | float64 | Game period (1, 2, 3, OT) | 0.0 |
| `away_team_period2_goals` | float64 | Game period (1, 2, 3, OT) | 0.0 |
| `away_team_period3_goals` | float64 | Game period (1, 2, 3, OT) | 1.0 |
| `away_team_periodOT_goals` | float64 | Game period (1, 2, 3, OT) | 1.0 |
| `home_team_seeding` | float64 | - | 1.0 |
| `away_team_seeding` | float64 | - | 3.0 |
| `home_team_w` | int64 | - | 0 |
| `home_team_l` | int64 | - | 1 |
| `home_team_t` | int64 | - | 0 |
| `home_team_pts` | int64 | - | 0 |
| `away_team_w` | int64 | - | 1 |
| `away_team_l` | int64 | - | 0 |
| `away_team_t` | int64 | - | 0 |
| `away_team_pts` | int64 | - | 2 |
| `video_id` | float64 | Foreign key reference |  |
| `video_start_time` | float64 | Shift start time |  |
| `video_end_time` | float64 | Shift end time |  |
| `video_title` | float64 | - |  |
| `video_url` | float64 | - |  |

---

### dim_season

**Rows:** 9 | **Columns:** 8

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `season_id` | object | Foreign key reference | N20212022F |
| `season` | int64 | - | 20212022 |
| `session` | object | - | F |
| `norad` | object | - | Y |
| `csah` | object | - | N |
| `league_id` | object | Foreign key reference | N |
| `league` | object | - | NORAD |
| `start_date` | object | - | 2021-08-01 00:00:00 |

---

### dim_shift_quality_tier

**Rows:** 5 | **Columns:** 6

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `tier_id` | object | Foreign key reference | SQ01 |
| `tier_code` | object | - | elite |
| `tier_name` | object | - | Elite Shift |
| `score_min` | int64 | - | 80 |
| `score_max` | int64 | - | 100 |
| `description` | object | - | Outstanding performance |

---

### dim_shift_start_type

**Rows:** 9 | **Columns:** 2

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `shift_start_type_id` | object | Foreign key reference | SST0001 |
| `shift_start_type_name` | object | - | GameStart |

---

### dim_shift_stop_type

**Rows:** 18 | **Columns:** 2

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `shift_stop_type_id` | object | Foreign key reference | SPT0001 |
| `shift_stop_type_name` | object | - | Away Icing |

---

### dim_shot_type

**Rows:** 6 | **Columns:** 4

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `shot_type_id` | object | Foreign key reference | ST0001 |
| `shot_type_code` | object | - | Wrist |
| `shot_type_name` | object | - | Wrist Shot |
| `description` | object | - | Quick release from wrist |

---

### dim_situation

**Rows:** 5 | **Columns:** 2

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `situation_id` | object | Foreign key reference | SIT0001 |
| `situation_name` | object | - | Full Strength |

---

### dim_stoppage_type

**Rows:** 4 | **Columns:** 3

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `stoppage_type_id` | object | Foreign key reference | SP0001 |
| `stoppage_type_code` | object | - | Stoppage_Freeze |
| `stoppage_type_name` | object | - | Stoppage Freeze |

---

### dim_success

**Rows:** 3 | **Columns:** 4

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `success_id` | object | Foreign key reference | SC01 |
| `success_code` | object | - | s |
| `success_name` | object | - | Successful |
| `is_successful` | object | Boolean flag | True |

---

### dim_takeaway_type

**Rows:** 2 | **Columns:** 3

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `takeaway_type_id` | object | Foreign key reference | TA0001 |
| `takeaway_type_code` | object | - | PuckRecovery |
| `takeaway_type_name` | object | - | PuckRecovery |

---

### dim_team

**Team master data**

| Property | Value |
|----------|-------|
| Grain | One row per team |
| Rows | 26 |
| Columns | 14 |

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `team_name` | object | - | Amos |
| `team_id` | object | Unique team identifier | N10001 |
| `norad_team` | object | - | Y |
| `csah_team` | object | - | N |
| `league_id` | object | Foreign key reference | N |
| `league` | object | - | NORAD |
| `long_team_name` | object | - | AMOS |
| `team_cd` | object | - | ACE |
| `team_color1` | object | - | #641C28 |
| `team_color2` | object | - | #458BC5 |
| `team_color3` | object | - | #FFFFFF |
| `team_color4` | object | - | #030629 |
| `team_logo` | object | - | https://i0.wp.com/www.nor... |
| `team_url` | object | - | https://www.noradhockey.c... |

---

### dim_time_bucket

**Rows:** 6 | **Columns:** 6

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `time_bucket_id` | object | Foreign key reference | TB01 |
| `time_bucket_code` | object | - | early |
| `time_bucket_name` | object | - | Early Period (0-5) |
| `minute_start` | int64 | - | 0 |
| `minute_end` | int64 | - | 5 |
| `description` | object | - | First 5 minutes |

---

### dim_venue

**Rows:** 2 | **Columns:** 4

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `venue_id` | object | Foreign key reference | VN01 |
| `venue_code` | object | - | home |
| `venue_name` | object | - | Home |
| `venue_abbrev` | object | - | H |

---

### dim_zone

**Rows:** 3 | **Columns:** 4

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `zone_id` | object | Ice zone (Off, Def, Neu) | ZN01 |
| `zone_code` | object | Ice zone (Off, Def, Neu) | O |
| `zone_name` | object | Ice zone (Off, Def, Neu) | Offensive Zone |
| `zone_abbrev` | object | Ice zone (Off, Def, Neu) | OZ |

---

### dim_zone_entry_type

**Rows:** 11 | **Columns:** 3

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `zone_entry_type_id` | object | Ice zone (Off, Def, Neu) | ZE0001 |
| `zone_entry_type_code` | object | Ice zone (Off, Def, Neu) | ZoneEntry_CausedTurnover |
| `zone_entry_type_name` | object | Ice zone (Off, Def, Neu) | CausedTurnover |

---

### dim_zone_exit_type

**Rows:** 10 | **Columns:** 3

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `zone_exit_type_id` | object | Ice zone (Off, Def, Neu) | ZX0001 |
| `zone_exit_type_code` | object | Ice zone (Off, Def, Neu) | ZoneExit_CausedTurnover |
| `zone_exit_type_name` | object | Ice zone (Off, Def, Neu) | CausedTurnover |

---

## Fact Tables

### fact_breakouts

**Rows:** 475 | **Columns:** 80

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `event_id` | object | Unique event identifier | EV1896901009 |
| `game_id` | int64 | Unique game identifier from NORAD league | 18969 |
| `period` | int64 | Game period | 1 |
| `period_id` | object | Game period (1, 2, 3, OT) | P01 |
| `event_type` | object | Type of event (Goal, Shot, Pass, etc.) | Zone_Entry_Exit |
| `event_type_id` | object | Type of event (Goal, Shot, Pass, etc.) | ET0006 |
| `event_detail` | object | Detailed event subtype | Zone_Exit |
| `event_detail_id` | float64 | Detailed event subtype |  |
| `event_detail_2` | object | Detailed event subtype | ZoneExit_Pass |
| `event_detail_2_id` | object | Detailed event subtype | ED292 |
| `event_successful` | object | - | s |
| `success_id` | object | Foreign key reference | SC01 |
| `event_team_zone` | object | Ice zone (Off, Def, Neu) | d |
| `event_zone_id` | object | Ice zone (Off, Def, Neu) | ZN02 |
| `sequence_key` | object | - | SQ1896900062 |
| `play_key` | object | - | PL1896906203 |
| `event_chain_key` | object | - | EC18969001009 |
| `tracking_event_key` | object | - | TV1896909002 |
| `shift_key` | object | - | SH1896900001 |
| `linked_event_key` | object | - | LV1896909002 |
| `home_team` | object | - | Platinum |
| `home_team_id` | object | Unique team identifier | N10008 |
| `away_team` | object | - | Velodrome |
| `away_team_id` | object | Unique team identifier | N10010 |
| `duration` | float64 | - | 0.0 |
| `event_player_ids` | object | Unique player identifier | P100070,P100161 |
| `opp_player_ids` | object | Unique player identifier | P100210 |
| `player_name` | object | Player full name | Hayden Perea |
| `season_id` | object | Foreign key reference | N20252026F |
| `position_id` | float64 | Player position (C, LW, RW, D, G) | 5.0 |
| `shot_type_id` | float64 | Foreign key reference |  |
| `zone_entry_type_id` | object | Ice zone (Off, Def, Neu) | ZE0010 |
| `zone_exit_type_id` | object | Ice zone (Off, Def, Neu) | ZX0007 |
| `stoppage_type_id` | float64 | Foreign key reference |  |
| `giveaway_type_id` | object | Foreign key reference | GT0005 |
| `takeaway_type_id` | float64 | Foreign key reference |  |
| `turnover_type_id` | object | Foreign key reference | TO0007 |
| `pass_type_id` | float64 | Foreign key reference |  |
| `time_bucket_id` | object | Foreign key reference | TB01 |
| `strength_id` | object | Foreign key reference | STR0001 |
| `cycle_key` | float64 | - |  |
| `is_cycle` | int64 | Boolean flag | 0 |
| `event_start_min` | float64 | - | 17.0 |
| `event_start_sec` | float64 | - | 41.0 |
| `event_end_min` | float64 | - | 12.0 |
| `event_end_sec` | float64 | - | 40.0 |
| `running_video_time` | float64 | - | 19.0 |
| `event_running_start` | float64 | - | 14.0 |
| `event_running_end` | float64 | - | 19.0 |
| `play_detail1` | object | - | Breakout |
| `is_rush` | int64 | Boolean flag | 0 |
| `is_rebound` | int64 | Boolean flag | 0 |
| `is_breakout` | int64 | Boolean flag | 1 |
| `is_zone_entry` | int64 | Ice zone (Off, Def, Neu) | 0 |
| `is_zone_exit` | int64 | Ice zone (Off, Def, Neu) | 1 |
| `is_shot` | int64 | Boolean flag | 0 |
| `is_goal` | int64 | Boolean flag | 0 |
| `is_save` | int64 | Boolean flag | 0 |
| `is_turnover` | int64 | Boolean flag | 0 |
| `is_giveaway` | int64 | Boolean flag | 0 |
| `is_takeaway` | int64 | Boolean flag | 0 |
| `is_faceoff` | int64 | Boolean flag | 0 |
| `is_penalty` | int64 | Boolean flag | 0 |
| `is_blocked_shot` | int64 | Boolean flag | 0 |
| `is_missed_shot` | int64 | Boolean flag | 0 |
| `is_deflected` | int64 | Boolean flag | 0 |
| `is_sog` | int64 | Boolean flag | 0 |
| `shot_outcome_id` | float64 | Foreign key reference |  |
| `pass_outcome_id` | float64 | Foreign key reference |  |
| `save_outcome_id` | float64 | Foreign key reference |  |
| `zone_outcome_id` | object | Ice zone (Off, Def, Neu) | ZO03 |
| `is_scoring_chance` | int64 | Boolean flag | 0 |
| `is_high_danger` | int64 | Boolean flag | 0 |
| `pressured_pressurer` | float64 | - | 1.0 |
| `is_pressured` | int64 | Boolean flag | 0 |
| `danger_level` | float64 | - |  |
| `danger_level_id` | float64 | Foreign key reference |  |
| `scoring_chance_key` | float64 | - |  |
| `breakout_key` | object | - | BO189690009 |
| `breakout_successful` | object | - | True |

---

### fact_cycle_events

**Rows:** 32 | **Columns:** 22

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `cycle_key` | object | - | CY189690001 |
| `game_id` | int64 | Unique game identifier from NORAD league | 18969 |
| `season_id` | object | Foreign key reference | N20252026F |
| `team_id` | object | Unique team identifier | N10008 |
| `team_name` | object | - | Platinum |
| `home_team_id` | object | Unique team identifier | N10008 |
| `away_team_id` | object | Unique team identifier | N10010 |
| `pass_count` | int64 | Count/total | 3 |
| `event_count` | int64 | Count/total | 7 |
| `player_count` | int64 | Count/total | 2 |
| `start_event_id` | object | Unique event identifier | EV1896901046 |
| `end_event_id` | object | Unique event identifier | EV1896901052 |
| `start_time` | float64 | Shift start time | 105.0 |
| `end_time` | float64 | Shift end time | 120.0 |
| `duration_seconds` | float64 | - | 15.0 |
| `ended_with` | object | - | zone_change |
| `ended_with_shot` | int64 | - | 0 |
| `ended_with_goal` | int64 | - | 0 |
| `event_ids` | object | Unique event identifier | EV1896901046,EV1896901047... |
| `player_ids` | object | Unique player identifier | P100117,P100022 |
| `period` | int64 | Game period | 1 |
| `period_id` | object | Game period (1, 2, 3, OT) | P01 |

---

### fact_draft

**Rows:** 160 | **Columns:** 14

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `team_id` | object | Unique team identifier | N10010 |
| `skill_rating` | int64 | - | 6 |
| `round` | int64 | - | 1 |
| `player_full_name` | object | - | Sam Downs |
| `player_id` | object | Unique player identifier | P100001 |
| `team_name` | object | - | Velodrome |
| `restricted` | bool | - | False |
| `overall_draft_round` | int64 | - | 1 |
| `overall_draft_position` | int64 | Player position (C, LW, RW, D, G) | 1 |
| `unrestricted_draft_position` | int64 | Player position (C, LW, RW, D, G) | 1 |
| `season` | int64 | - | 20252026 |
| `season_id` | object | Foreign key reference | N20252026F |
| `league` | object | - | NORAD |
| `player_draft_id` | object | Foreign key reference | DRAFT_N20252026FP100001 |

---

### fact_event_players

**Bridge table linking events to players with their roles**

| Property | Value |
|----------|-------|
| Grain | One row per player per event |
| Rows | 11,181 |
| Columns | 61 |

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `event_id` | object | Unique event identifier | EV1896901000 |
| `game_id` | int64 | Unique game identifier from NORAD league | 18969 |
| `player_id` | object | Unique player identifier | P100192 |
| `player_game_number` | float64 | - | 53.0 |
| `sequence_key` | object | - | SQ1896900001 |
| `play_key` | object | - | PL1896900101 |
| `shift_key` | object | - | SH1896900001 |
| `linked_event_key` | object | - | LV1896909001 |
| `event_chain_key` | object | - | EC18969001000 |
| `tracking_event_key` | object | - | TV1896901000 |
| `zone_change_key` | object | Ice zone (Off, Def, Neu) | ZC1896900001 |
| `period_id` | object | Game period (1, 2, 3, OT) | P01 |
| `home_team_id` | object | Unique team identifier | N10008 |
| `away_team_id` | object | Unique team identifier | N10010 |
| `player_team_id` | object | Unique team identifier | N10008 |
| `period` | int64 | Game period | 1 |
| `event_start_min` | float64 | - | 18.0 |
| `event_start_sec` | float64 | - | 0.0 |
| `event_end_min` | float64 | - | 17.0 |
| `event_end_sec` | float64 | - | 52.0 |
| `event_team_zone` | object | Ice zone (Off, Def, Neu) | n |
| `home_team_zone` | object | Ice zone (Off, Def, Neu) | n |
| `away_team_zone` | object | Ice zone (Off, Def, Neu) | n |
| `team_venue` | object | - | Home |
| `side_of_puck` | object | - | Offensive |
| `play_detail1` | object | - | Delay |
| `play_detail_2` | object | - | ForceWide |
| `play_detail_successful` | object | - | s |
| `pressured_pressurer` | float64 | - | 1.0 |
| `home_team` | object | - | Platinum |
| `away_team` | object | - | Velodrome |
| `event_type` | object | Type of event (Goal, Shot, Pass, etc.) | GameStart |
| `event_detail` | object | Detailed event subtype | Faceoff_GameStart |
| `event_detail_2` | object | Detailed event subtype | Pass_Forehand |
| `event_successful` | object | - | s |
| `duration` | float64 | - | 0.0 |
| `time_start_total_seconds` | float64 | - | 1080.0 |
| `time_end_total_seconds` | float64 | - | 1080.0 |
| `running_intermission_duration` | float64 | - | 0.0 |
| `period_start_total_running_seconds` | float64 | Game period (1, 2, 3, OT) | 0.0 |
| `running_video_time` | float64 | - | 0.0 |
| `event_running_start` | float64 | - | 0.0 |
| `event_running_end` | float64 | - | 5.0 |
| `player_role` | object | Role in event (event_player_1, etc.) | event_player_1 |
| `player_team` | object | - | Platinum |
| `is_goal` | int64 | Boolean flag | 0 |
| `player_name` | object | Player full name | Chris Premo |
| `season_id` | object | Foreign key reference | N20252026F |
| `position_id` | float64 | Player position (C, LW, RW, D, G) | 4.0 |
| `shot_type_id` | float64 | Foreign key reference |  |
| `zone_entry_type_id` | object | Ice zone (Off, Def, Neu) | ZE0010 |
| `zone_exit_type_id` | object | Ice zone (Off, Def, Neu) | ZX0010 |
| `stoppage_type_id` | object | Foreign key reference | SP0008 |
| `giveaway_type_id` | object | Foreign key reference | GT0001 |
| `takeaway_type_id` | object | Foreign key reference | TA0010 |
| `turnover_type_id` | object | Foreign key reference | TO0007 |
| `pass_type_id` | float64 | Foreign key reference |  |
| `time_bucket_id` | object | Foreign key reference | TB01 |
| `strength_id` | object | Foreign key reference | STR0001 |
| `cycle_key` | object | - | CY189690001 |
| `is_cycle` | int64 | Boolean flag | 0 |

---

### fact_events

**Core event table - every tracked event from game video**

| Property | Value |
|----------|-------|
| Grain | One row per event per game |
| Rows | 5,831 |
| Columns | 78 |

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `event_id` | object | Unique event identifier | EV1896901000 |
| `game_id` | int64 | Unique game identifier from NORAD league | 18969 |
| `period` | int64 | Game period | 1 |
| `period_id` | object | Game period (1, 2, 3, OT) | P01 |
| `event_type` | object | Type of event (Goal, Shot, Pass, etc.) | GameStart |
| `event_type_id` | object | Type of event (Goal, Shot, Pass, etc.) | ET0004 |
| `event_detail` | object | Detailed event subtype | Faceoff_GameStart |
| `event_detail_id` | object | Detailed event subtype | ED0020 |
| `event_detail_2` | object | Detailed event subtype | Pass_Forehand |
| `event_detail_2_id` | object | Detailed event subtype | ED226 |
| `event_successful` | object | - | s |
| `success_id` | object | Foreign key reference | SC01 |
| `event_team_zone` | object | Ice zone (Off, Def, Neu) | n |
| `event_zone_id` | object | Ice zone (Off, Def, Neu) | ZN03 |
| `sequence_key` | object | - | SQ1896900001 |
| `play_key` | object | - | PL1896900101 |
| `event_chain_key` | object | - | EC18969001000 |
| `tracking_event_key` | object | - | TV1896901000 |
| `shift_key` | object | - | SH1896900001 |
| `linked_event_key` | object | - | LV1896909001 |
| `home_team` | object | - | Platinum |
| `home_team_id` | object | Unique team identifier | N10008 |
| `away_team` | object | - | Velodrome |
| `away_team_id` | object | Unique team identifier | N10010 |
| `duration` | float64 | - | 0.0 |
| `event_player_ids` | object | Unique player identifier | P100025,P100192 |
| `opp_player_ids` | object | Unique player identifier | P100001 |
| `player_name` | object | Player full name | Chris Premo |
| `season_id` | object | Foreign key reference | N20252026F |
| `position_id` | float64 | Player position (C, LW, RW, D, G) | 4.0 |
| `shot_type_id` | float64 | Foreign key reference |  |
| `zone_entry_type_id` | object | Ice zone (Off, Def, Neu) | ZE0003 |
| `zone_exit_type_id` | object | Ice zone (Off, Def, Neu) | ZX0007 |
| `stoppage_type_id` | object | Foreign key reference | SP0010 |
| `giveaway_type_id` | object | Foreign key reference | GT0005 |
| `takeaway_type_id` | object | Foreign key reference | TA0010 |
| `turnover_type_id` | object | Foreign key reference | TO0007 |
| `pass_type_id` | float64 | Foreign key reference |  |
| `time_bucket_id` | object | Foreign key reference | TB01 |
| `strength_id` | object | Foreign key reference | STR0001 |
| `cycle_key` | object | - | CY189690001 |
| `is_cycle` | int64 | Boolean flag | 0 |
| `event_start_min` | float64 | - | 18.0 |
| `event_start_sec` | float64 | - | 0.0 |
| `event_end_min` | float64 | - | 17.0 |
| `event_end_sec` | float64 | - | 52.0 |
| `running_video_time` | float64 | - | 0.0 |
| `event_running_start` | float64 | - | 0.0 |
| `event_running_end` | float64 | - | 5.0 |
| `play_detail1` | object | - | Delay |
| `is_rush` | int64 | Boolean flag | 0 |
| `is_rebound` | int64 | Boolean flag | 0 |
| `is_breakout` | int64 | Boolean flag | 0 |
| `is_zone_entry` | int64 | Ice zone (Off, Def, Neu) | 0 |
| `is_zone_exit` | int64 | Ice zone (Off, Def, Neu) | 0 |
| `is_shot` | int64 | Boolean flag | 0 |
| `is_goal` | int64 | Boolean flag | 0 |
| `is_save` | int64 | Boolean flag | 0 |
| `is_turnover` | int64 | Boolean flag | 0 |
| `is_giveaway` | int64 | Boolean flag | 0 |
| `is_takeaway` | int64 | Boolean flag | 0 |
| `is_faceoff` | int64 | Boolean flag | 0 |
| `is_penalty` | int64 | Boolean flag | 0 |
| `is_blocked_shot` | int64 | Boolean flag | 0 |
| `is_missed_shot` | int64 | Boolean flag | 0 |
| `is_deflected` | int64 | Boolean flag | 0 |
| `is_sog` | int64 | Boolean flag | 0 |
| `shot_outcome_id` | object | Foreign key reference | SO03 |
| `pass_outcome_id` | object | Foreign key reference | PO01 |
| `save_outcome_id` | object | Foreign key reference | SV01 |
| `zone_outcome_id` | object | Ice zone (Off, Def, Neu) | ZO01 |
| `is_scoring_chance` | int64 | Boolean flag | 0 |
| `is_high_danger` | int64 | Boolean flag | 0 |
| `pressured_pressurer` | float64 | - | 1.0 |
| `is_pressured` | int64 | Boolean flag | 0 |
| `danger_level` | object | - | medium |
| `danger_level_id` | object | Foreign key reference | DL02 |
| `scoring_chance_key` | object | - | SC189690000 |

---

### fact_faceoffs

**Rows:** 171 | **Columns:** 80

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `event_id` | object | Unique event identifier | EV1896901001 |
| `game_id` | int64 | Unique game identifier from NORAD league | 18969 |
| `period` | int64 | Game period | 1 |
| `period_id` | object | Game period (1, 2, 3, OT) | P01 |
| `event_type` | object | Type of event (Goal, Shot, Pass, etc.) | Faceoff |
| `event_type_id` | object | Type of event (Goal, Shot, Pass, etc.) | ET0004 |
| `event_detail` | object | Detailed event subtype | Faceoff_GameStart |
| `event_detail_id` | float64 | Detailed event subtype |  |
| `event_detail_2` | object | Detailed event subtype | Pass_Forehand |
| `event_detail_2_id` | object | Detailed event subtype | ED226 |
| `event_successful` | float64 | - |  |
| `success_id` | float64 | Foreign key reference |  |
| `event_team_zone` | object | Ice zone (Off, Def, Neu) | n |
| `event_zone_id` | object | Ice zone (Off, Def, Neu) | ZN03 |
| `sequence_key` | object | - | SQ1896900001 |
| `play_key` | object | - | PL1896900101 |
| `event_chain_key` | object | - | EC18969001001 |
| `tracking_event_key` | object | - | TV1896901001 |
| `shift_key` | object | - | SH1896900001 |
| `linked_event_key` | object | - | LV1896909163 |
| `home_team` | object | - | Platinum |
| `home_team_id` | object | Unique team identifier | N10008 |
| `away_team` | object | - | Velodrome |
| `away_team_id` | object | Unique team identifier | N10010 |
| `duration` | float64 | - | 0.0 |
| `event_player_ids` | object | Unique player identifier | P100025,P100192 |
| `opp_player_ids` | object | Unique player identifier | P100001 |
| `player_name` | object | Player full name | Chris Premo |
| `season_id` | object | Foreign key reference | N20252026F |
| `position_id` | float64 | Player position (C, LW, RW, D, G) | 4.0 |
| `shot_type_id` | float64 | Foreign key reference |  |
| `zone_entry_type_id` | float64 | Ice zone (Off, Def, Neu) |  |
| `zone_exit_type_id` | object | Ice zone (Off, Def, Neu) | ZX0007 |
| `stoppage_type_id` | float64 | Foreign key reference |  |
| `giveaway_type_id` | float64 | Foreign key reference |  |
| `takeaway_type_id` | float64 | Foreign key reference |  |
| `turnover_type_id` | float64 | Foreign key reference |  |
| `pass_type_id` | float64 | Foreign key reference |  |
| `time_bucket_id` | object | Foreign key reference | TB01 |
| `strength_id` | object | Foreign key reference | STR0001 |
| `cycle_key` | float64 | - |  |
| `is_cycle` | int64 | Boolean flag | 0 |
| `event_start_min` | float64 | - | 18.0 |
| `event_start_sec` | float64 | - | 0.0 |
| `event_end_min` | float64 | - | 17.0 |
| `event_end_sec` | float64 | - | 1.0 |
| `running_video_time` | float64 | - | 0.0 |
| `event_running_start` | float64 | - | 0.0 |
| `event_running_end` | float64 | - | 5.0 |
| `play_detail1` | float64 | - |  |
| `is_rush` | int64 | Boolean flag | 0 |
| `is_rebound` | int64 | Boolean flag | 0 |
| `is_breakout` | int64 | Boolean flag | 0 |
| `is_zone_entry` | int64 | Ice zone (Off, Def, Neu) | 0 |
| `is_zone_exit` | int64 | Ice zone (Off, Def, Neu) | 0 |
| `is_shot` | int64 | Boolean flag | 0 |
| `is_goal` | int64 | Boolean flag | 0 |
| `is_save` | int64 | Boolean flag | 0 |
| `is_turnover` | int64 | Boolean flag | 0 |
| `is_giveaway` | int64 | Boolean flag | 0 |
| `is_takeaway` | int64 | Boolean flag | 0 |
| `is_faceoff` | int64 | Boolean flag | 1 |
| `is_penalty` | int64 | Boolean flag | 0 |
| `is_blocked_shot` | int64 | Boolean flag | 0 |
| `is_missed_shot` | int64 | Boolean flag | 0 |
| `is_deflected` | int64 | Boolean flag | 0 |
| `is_sog` | int64 | Boolean flag | 0 |
| `shot_outcome_id` | float64 | Foreign key reference |  |
| `pass_outcome_id` | float64 | Foreign key reference |  |
| `save_outcome_id` | float64 | Foreign key reference |  |
| `zone_outcome_id` | float64 | Ice zone (Off, Def, Neu) |  |
| `is_scoring_chance` | int64 | Boolean flag | 0 |
| `is_high_danger` | int64 | Boolean flag | 0 |
| `pressured_pressurer` | float64 | - |  |
| `is_pressured` | int64 | Boolean flag | 0 |
| `danger_level` | float64 | - |  |
| `danger_level_id` | float64 | Foreign key reference |  |
| `scoring_chance_key` | float64 | - |  |
| `faceoff_key` | object | - | FO189690001 |
| `faceoff_type` | object | - | other |

---

### fact_gameroster

**Rows:** 14,471 | **Columns:** 24

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `game_id` | int64 | Unique game identifier from NORAD league | 10001 |
| `player_id` | object | Unique player identifier | P100250 |
| `team_id` | object | Unique team identifier | N10002 |
| `opp_team_id` | object | Unique team identifier | N10004 |
| `season_id` | object | Foreign key reference | N20232024F |
| `venue_id` | object | Foreign key reference | VN02 |
| `position_id` | object | Player position (C, LW, RW, D, G) | PS0005 |
| `team_name` | object | - | Ace |
| `opp_team_name` | object | - | Nelson |
| `team_venue` | object | - | away |
| `date` | object | - | 2023-10-08 00:00:00 |
| `season` | int64 | - | 20232024 |
| `player_full_name` | object | - | Geoff Nolan |
| `player_game_number` | object | - | 2 |
| `player_position` | object | Player position (C, LW, RW, D, G) | Defense |
| `goals` | float64 | Goals scored | 0.0 |
| `assist` | float64 | - | 2.0 |
| `points` | float64 | Total points (goals + assists) | 2.0 |
| `goals_against` | float64 | Goals scored | 0.0 |
| `pim` | float64 | - | 0.0 |
| `shutouts` | float64 | - | 0.0 |
| `games_played` | float64 | - | 1.0 |
| `sub` | object | - | True |
| `current_team` | object | - | Free Agent |

---

### fact_high_danger_chances

**Rows:** 26 | **Columns:** 79

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `event_id` | object | Unique event identifier | EV1896901032 |
| `game_id` | int64 | Unique game identifier from NORAD league | 18969 |
| `period` | int64 | Game period | 1 |
| `period_id` | object | Game period (1, 2, 3, OT) | P01 |
| `event_type` | object | Type of event (Goal, Shot, Pass, etc.) | Shot |
| `event_type_id` | object | Type of event (Goal, Shot, Pass, etc.) | ET0001 |
| `event_detail` | object | Detailed event subtype | Shot_OnNetSaved |
| `event_detail_id` | object | Detailed event subtype | ED0001 |
| `event_detail_2` | object | Detailed event subtype | Shot_OneTime |
| `event_detail_2_id` | object | Detailed event subtype | ED256 |
| `event_successful` | object | - | s |
| `success_id` | object | Foreign key reference | SC01 |
| `event_team_zone` | object | Ice zone (Off, Def, Neu) | o |
| `event_zone_id` | object | Ice zone (Off, Def, Neu) | ZN01 |
| `sequence_key` | object | - | SQ1896900062 |
| `play_key` | object | - | PL1896906205 |
| `event_chain_key` | object | - | EC18969001032 |
| `tracking_event_key` | object | - | TV1896909004 |
| `shift_key` | object | - | SH1896900001 |
| `linked_event_key` | object | - | LV1896909004 |
| `home_team` | object | - | Platinum |
| `home_team_id` | object | Unique team identifier | N10008 |
| `away_team` | object | - | Velodrome |
| `away_team_id` | object | Unique team identifier | N10010 |
| `duration` | float64 | - | 0.0 |
| `event_player_ids` | object | Unique player identifier | P100024 |
| `opp_player_ids` | object | Unique player identifier | P100016,P100108 |
| `player_name` | object | Player full name | John Thien |
| `season_id` | object | Foreign key reference | N20252026F |
| `position_id` | float64 | Player position (C, LW, RW, D, G) | 4.0 |
| `shot_type_id` | float64 | Foreign key reference |  |
| `zone_entry_type_id` | float64 | Ice zone (Off, Def, Neu) |  |
| `zone_exit_type_id` | float64 | Ice zone (Off, Def, Neu) |  |
| `stoppage_type_id` | float64 | Foreign key reference |  |
| `giveaway_type_id` | float64 | Foreign key reference |  |
| `takeaway_type_id` | float64 | Foreign key reference |  |
| `turnover_type_id` | float64 | Foreign key reference |  |
| `pass_type_id` | float64 | Foreign key reference |  |
| `time_bucket_id` | object | Foreign key reference | TB01 |
| `strength_id` | object | Foreign key reference | STR0001 |
| `cycle_key` | object | - | CY189690003 |
| `is_cycle` | int64 | Boolean flag | 0 |
| `event_start_min` | float64 | - | 16.0 |
| `event_start_sec` | float64 | - | 48.0 |
| `event_end_min` | float64 | - |  |
| `event_end_sec` | float64 | - |  |
| `running_video_time` | float64 | - | 72.0 |
| `event_running_start` | float64 | - | 67.0 |
| `event_running_end` | float64 | - | 72.0 |
| `play_detail1` | object | - | SecondTouch |
| `is_rush` | int64 | Boolean flag | 0 |
| `is_rebound` | int64 | Boolean flag | 0 |
| `is_breakout` | int64 | Boolean flag | 0 |
| `is_zone_entry` | int64 | Ice zone (Off, Def, Neu) | 0 |
| `is_zone_exit` | int64 | Ice zone (Off, Def, Neu) | 0 |
| `is_shot` | int64 | Boolean flag | 1 |
| `is_goal` | int64 | Boolean flag | 0 |
| `is_save` | int64 | Boolean flag | 0 |
| `is_turnover` | int64 | Boolean flag | 0 |
| `is_giveaway` | int64 | Boolean flag | 0 |
| `is_takeaway` | int64 | Boolean flag | 0 |
| `is_faceoff` | int64 | Boolean flag | 0 |
| `is_penalty` | int64 | Boolean flag | 0 |
| `is_blocked_shot` | int64 | Boolean flag | 0 |
| `is_missed_shot` | int64 | Boolean flag | 0 |
| `is_deflected` | int64 | Boolean flag | 0 |
| `is_sog` | int64 | Boolean flag | 1 |
| `shot_outcome_id` | object | Foreign key reference | SO02 |
| `pass_outcome_id` | float64 | Foreign key reference |  |
| `save_outcome_id` | float64 | Foreign key reference |  |
| `zone_outcome_id` | float64 | Ice zone (Off, Def, Neu) |  |
| `is_scoring_chance` | int64 | Boolean flag | 1 |
| `is_high_danger` | int64 | Boolean flag | 1 |
| `pressured_pressurer` | float64 | - | 1.0 |
| `is_pressured` | int64 | Boolean flag | 0 |
| `danger_level` | object | - | high |
| `danger_level_id` | object | Foreign key reference | DL01 |
| `scoring_chance_key` | object | - | SC189690003 |
| `high_danger_key` | object | - | HD189690032 |

---

### fact_leadership

**Rows:** 28 | **Columns:** 9

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `player_full_name` | object | - | Peter Husak |
| `player_id` | object | Unique player identifier | P100048 |
| `leadership` | object | - | S |
| `skill_rating` | int64 | - | 2 |
| `n_player_url` | object | - | Peter Husak (S) – 2 |
| `team_name` | object | - | OS Offices |
| `team_id` | object | Unique team identifier | N10005 |
| `season` | int64 | - | 20252026 |
| `season_id` | object | Foreign key reference | N20252026F |

---

### fact_penalties

**Rows:** 20 | **Columns:** 79

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `event_id` | object | Unique event identifier | EV1896902018 |
| `game_id` | int64 | Unique game identifier from NORAD league | 18969 |
| `period` | int64 | Game period | 2 |
| `period_id` | object | Game period (1, 2, 3, OT) | P02 |
| `event_type` | object | Type of event (Goal, Shot, Pass, etc.) | Penalty |
| `event_type_id` | object | Type of event (Goal, Shot, Pass, etc.) | ET0008 |
| `event_detail` | object | Detailed event subtype | Penalty_Minor |
| `event_detail_id` | float64 | Detailed event subtype |  |
| `event_detail_2` | object | Detailed event subtype | Penalty_Hooking |
| `event_detail_2_id` | object | Detailed event subtype | ED234 |
| `event_successful` | float64 | - |  |
| `success_id` | float64 | Foreign key reference |  |
| `event_team_zone` | object | Ice zone (Off, Def, Neu) | d |
| `event_zone_id` | object | Ice zone (Off, Def, Neu) | ZN02 |
| `sequence_key` | object | - | SQ1896900032 |
| `play_key` | object | - | PL1896903204 |
| `event_chain_key` | object | - | EC18969002018 |
| `tracking_event_key` | object | - | TV1896902018 |
| `shift_key` | object | - | SH1896900062 |
| `linked_event_key` | object | - | LV1898709075 |
| `home_team` | object | - | Platinum |
| `home_team_id` | object | Unique team identifier | N10008 |
| `away_team` | object | - | Velodrome |
| `away_team_id` | object | Unique team identifier | N10010 |
| `duration` | float64 | - | 0.0 |
| `event_player_ids` | object | Unique player identifier | P100030 |
| `opp_player_ids` | object | Unique player identifier | P100117 |
| `player_name` | object | Player full name | Jesse Chambless |
| `season_id` | object | Foreign key reference | N20252026F |
| `position_id` | float64 | Player position (C, LW, RW, D, G) | 5.0 |
| `shot_type_id` | float64 | Foreign key reference |  |
| `zone_entry_type_id` | float64 | Ice zone (Off, Def, Neu) |  |
| `zone_exit_type_id` | float64 | Ice zone (Off, Def, Neu) |  |
| `stoppage_type_id` | float64 | Foreign key reference |  |
| `giveaway_type_id` | float64 | Foreign key reference |  |
| `takeaway_type_id` | float64 | Foreign key reference |  |
| `turnover_type_id` | float64 | Foreign key reference |  |
| `pass_type_id` | float64 | Foreign key reference |  |
| `time_bucket_id` | object | Foreign key reference | TB05 |
| `strength_id` | object | Foreign key reference | STR0001 |
| `cycle_key` | float64 | - |  |
| `is_cycle` | int64 | Boolean flag | 0 |
| `event_start_min` | float64 | - | 1.0 |
| `event_start_sec` | float64 | - | 35.0 |
| `event_end_min` | float64 | - |  |
| `event_end_sec` | float64 | - |  |
| `running_video_time` | float64 | - | 2137.0 |
| `event_running_start` | float64 | - | 2132.0 |
| `event_running_end` | float64 | - | 2137.0 |
| `play_detail1` | object | - | Defensive_PlayZone_PuckRe... |
| `is_rush` | int64 | Boolean flag | 0 |
| `is_rebound` | int64 | Boolean flag | 0 |
| `is_breakout` | int64 | Boolean flag | 0 |
| `is_zone_entry` | int64 | Ice zone (Off, Def, Neu) | 0 |
| `is_zone_exit` | int64 | Ice zone (Off, Def, Neu) | 0 |
| `is_shot` | int64 | Boolean flag | 0 |
| `is_goal` | int64 | Boolean flag | 0 |
| `is_save` | int64 | Boolean flag | 0 |
| `is_turnover` | int64 | Boolean flag | 0 |
| `is_giveaway` | int64 | Boolean flag | 0 |
| `is_takeaway` | int64 | Boolean flag | 0 |
| `is_faceoff` | int64 | Boolean flag | 0 |
| `is_penalty` | int64 | Boolean flag | 1 |
| `is_blocked_shot` | int64 | Boolean flag | 0 |
| `is_missed_shot` | int64 | Boolean flag | 0 |
| `is_deflected` | int64 | Boolean flag | 0 |
| `is_sog` | int64 | Boolean flag | 0 |
| `shot_outcome_id` | float64 | Foreign key reference |  |
| `pass_outcome_id` | float64 | Foreign key reference |  |
| `save_outcome_id` | float64 | Foreign key reference |  |
| `zone_outcome_id` | float64 | Ice zone (Off, Def, Neu) |  |
| `is_scoring_chance` | int64 | Boolean flag | 0 |
| `is_high_danger` | int64 | Boolean flag | 0 |
| `pressured_pressurer` | float64 | - | 1.0 |
| `is_pressured` | int64 | Boolean flag | 0 |
| `danger_level` | float64 | - |  |
| `danger_level_id` | float64 | Foreign key reference |  |
| `scoring_chance_key` | float64 | - |  |
| `penalty_key` | object | - | PN189691018 |

---

### fact_player_game_position

**Rows:** 105 | **Columns:** 8

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `game_id` | int64 | Unique game identifier from NORAD league | 18969 |
| `player_id` | object | Unique player identifier | P100001 |
| `total_shifts` | int64 | - | 49 |
| `dominant_position` | object | Player position (C, LW, RW, D, G) | Forward |
| `dominant_position_pct` | float64 | Player position (C, LW, RW, D, G) | 100.0 |
| `forward_shifts` | int64 | - | 49 |
| `defense_shifts` | int64 | - | 0 |
| `goalie_shifts` | int64 | - | 0 |

---

### fact_plays

**Rows:** 1,956 | **Columns:** 39

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `play_key` | object | - | PL1896900101 |
| `play_id` | object | Foreign key reference | PL1896900101 |
| `game_id` | int64 | Unique game identifier from NORAD league | 18969 |
| `season_id` | object | Foreign key reference | N20252026F |
| `period` | int64 | Game period | 1 |
| `period_id` | object | Game period (1, 2, 3, OT) | P01 |
| `sequence_key` | object | - | SQ1896900001 |
| `first_event_key` | object | - | EV1896901001 |
| `last_event_key` | object | - | EV1896901011 |
| `event_count` | int64 | Count/total | 7 |
| `start_min` | float64 | - | 18.0 |
| `start_sec` | float64 | - | 0.0 |
| `duration_seconds` | float64 | - | 16.0 |
| `video_time_start` | float64 | - | 0.0 |
| `video_time_end` | float64 | - | 27.0 |
| `time_bucket_id` | object | Foreign key reference | TB01 |
| `strength_id` | object | Foreign key reference | STR0001 |
| `home_team` | object | - | Platinum |
| `home_team_id` | object | Unique team identifier | N10008 |
| `away_team` | object | - | Velodrome |
| `away_team_id` | object | Unique team identifier | N10010 |
| `start_zone` | object | Ice zone (Off, Def, Neu) | n |
| `end_zone` | object | Ice zone (Off, Def, Neu) | o |
| `start_zone_id` | object | Ice zone (Off, Def, Neu) | ZN03 |
| `end_zone_id` | object | Ice zone (Off, Def, Neu) | ZN01 |
| `event_types` | object | Type of event (Goal, Shot, Pass, etc.) | Faceoff,Pass,Possession,P... |
| `has_goal` | bool | Boolean flag | False |
| `goal_count` | int64 | Count/total | 0 |
| `has_shot` | bool | Boolean flag | False |
| `shot_count` | int64 | Count/total | 0 |
| `zone_entry_count` | int64 | Ice zone (Off, Def, Neu) | 1 |
| `zone_exit_count` | int64 | Ice zone (Off, Def, Neu) | 0 |
| `pass_count` | int64 | Count/total | 2 |
| `pass_success_count` | int64 | Count/total | 2 |
| `turnover_count` | int64 | Count/total | 0 |
| `giveaway_count` | int64 | Count/total | 0 |
| `takeaway_count` | int64 | Count/total | 0 |
| `unique_player_count` | int64 | Count/total | 6 |
| `player_ids` | object | Unique player identifier | P100024,P100025,P100030,P... |

---

### fact_registration

**Rows:** 190 | **Columns:** 18

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `player_full_name` | object | - | Ty Smith |
| `player_id` | object | Unique player identifier | P100084 |
| `season_id` | object | Foreign key reference | N20252026F |
| `season` | int64 | - | 20252026 |
| `restricted` | object | - | Y |
| `email` | object | - | ty0214@gmail.com |
| `position` | object | Player position (C, LW, RW, D, G) | Forward |
| `norad_experience` | object | - | 6 |
| `CAF` | object | - | No |
| `highest_beer_league_played` | object | - | Big Bear, C4, Birds of Wa... |
| `skill_rating` | int64 | - | 6 |
| `age` | int64 | - | 30 |
| `referred_by` | object | - | - |
| `notes` | object | - | Wants to play with wife K... |
| `sub_yn` | object | - | N |
| `drafted_team_name` | object | - | HollowBrook |
| `drafted_team_id` | object | Unique team identifier | N10003 |
| `player_season_registration_id` | object | Foreign key reference | R_N20252026FP100084 |

---

### fact_rushes

**Rows:** 314 | **Columns:** 80

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `event_id` | object | Unique event identifier | EV1896901011 |
| `game_id` | int64 | Unique game identifier from NORAD league | 18969 |
| `period` | int64 | Game period | 1 |
| `period_id` | object | Game period (1, 2, 3, OT) | P01 |
| `event_type` | object | Type of event (Goal, Shot, Pass, etc.) | Zone_Entry_Exit |
| `event_type_id` | object | Type of event (Goal, Shot, Pass, etc.) | ET0006 |
| `event_detail` | object | Detailed event subtype | Zone_Entry |
| `event_detail_id` | float64 | Detailed event subtype |  |
| `event_detail_2` | object | Detailed event subtype | ZoneEntry_Rush |
| `event_detail_2_id` | object | Detailed event subtype | ED284 |
| `event_successful` | object | - | s |
| `success_id` | object | Foreign key reference | SC01 |
| `event_team_zone` | object | Ice zone (Off, Def, Neu) | o |
| `event_zone_id` | object | Ice zone (Off, Def, Neu) | ZN01 |
| `sequence_key` | object | - | SQ1896900001 |
| `play_key` | object | - | PL1896900101 |
| `event_chain_key` | object | - | EC18969001011 |
| `tracking_event_key` | object | - | TV1896901011 |
| `shift_key` | object | - | SH1896900001 |
| `linked_event_key` | object | - | LV1896909018 |
| `home_team` | object | - | Platinum |
| `home_team_id` | object | Unique team identifier | N10008 |
| `away_team` | object | - | Velodrome |
| `away_team_id` | object | Unique team identifier | N10010 |
| `duration` | float64 | - | 4.0 |
| `event_player_ids` | object | Unique player identifier | P100161 |
| `opp_player_ids` | object | Unique player identifier | P100030 |
| `player_name` | object | Player full name | Galen Wood |
| `season_id` | object | Foreign key reference | N20252026F |
| `position_id` | float64 | Player position (C, LW, RW, D, G) | 4.0 |
| `shot_type_id` | float64 | Foreign key reference |  |
| `zone_entry_type_id` | object | Ice zone (Off, Def, Neu) | ZE0010 |
| `zone_exit_type_id` | object | Ice zone (Off, Def, Neu) | ZX0010 |
| `stoppage_type_id` | float64 | Foreign key reference |  |
| `giveaway_type_id` | float64 | Foreign key reference |  |
| `takeaway_type_id` | float64 | Foreign key reference |  |
| `turnover_type_id` | float64 | Foreign key reference |  |
| `pass_type_id` | float64 | Foreign key reference |  |
| `time_bucket_id` | object | Foreign key reference | TB01 |
| `strength_id` | object | Foreign key reference | STR0001 |
| `cycle_key` | object | - | CY189770013 |
| `is_cycle` | int64 | Boolean flag | 0 |
| `event_start_min` | float64 | - | 17.0 |
| `event_start_sec` | float64 | - | 37.0 |
| `event_end_min` | float64 | - | 17.0 |
| `event_end_sec` | float64 | - | 33.0 |
| `running_video_time` | float64 | - | 23.0 |
| `event_running_start` | float64 | - | 18.0 |
| `event_running_end` | float64 | - | 27.0 |
| `play_detail1` | object | - | Delay |
| `is_rush` | int64 | Boolean flag | 1 |
| `is_rebound` | int64 | Boolean flag | 0 |
| `is_breakout` | int64 | Boolean flag | 0 |
| `is_zone_entry` | int64 | Ice zone (Off, Def, Neu) | 1 |
| `is_zone_exit` | int64 | Ice zone (Off, Def, Neu) | 0 |
| `is_shot` | int64 | Boolean flag | 0 |
| `is_goal` | int64 | Boolean flag | 0 |
| `is_save` | int64 | Boolean flag | 0 |
| `is_turnover` | int64 | Boolean flag | 0 |
| `is_giveaway` | int64 | Boolean flag | 0 |
| `is_takeaway` | int64 | Boolean flag | 0 |
| `is_faceoff` | int64 | Boolean flag | 0 |
| `is_penalty` | int64 | Boolean flag | 0 |
| `is_blocked_shot` | int64 | Boolean flag | 0 |
| `is_missed_shot` | int64 | Boolean flag | 0 |
| `is_deflected` | int64 | Boolean flag | 0 |
| `is_sog` | int64 | Boolean flag | 0 |
| `shot_outcome_id` | float64 | Foreign key reference |  |
| `pass_outcome_id` | float64 | Foreign key reference |  |
| `save_outcome_id` | float64 | Foreign key reference |  |
| `zone_outcome_id` | object | Ice zone (Off, Def, Neu) | ZO01 |
| `is_scoring_chance` | int64 | Boolean flag | 0 |
| `is_high_danger` | int64 | Boolean flag | 0 |
| `pressured_pressurer` | float64 | - | 1.0 |
| `is_pressured` | int64 | Boolean flag | 1 |
| `danger_level` | float64 | - |  |
| `danger_level_id` | float64 | Foreign key reference |  |
| `scoring_chance_key` | float64 | - |  |
| `rush_key` | object | - | RU189690011 |
| `rush_outcome` | object | - | zone_entry |

---

### fact_saves

**Rows:** 212 | **Columns:** 79

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `event_id` | object | Unique event identifier | EV1896901033 |
| `game_id` | int64 | Unique game identifier from NORAD league | 18969 |
| `period` | int64 | Game period | 1 |
| `period_id` | object | Game period (1, 2, 3, OT) | P01 |
| `event_type` | object | Type of event (Goal, Shot, Pass, etc.) | Save |
| `event_type_id` | object | Type of event (Goal, Shot, Pass, etc.) | ET0002 |
| `event_detail` | object | Detailed event subtype | Save_Rebound |
| `event_detail_id` | object | Detailed event subtype | ED0055 |
| `event_detail_2` | object | Detailed event subtype | Save_LeftPad |
| `event_detail_2_id` | object | Detailed event subtype | ED248 |
| `event_successful` | float64 | - |  |
| `success_id` | float64 | Foreign key reference |  |
| `event_team_zone` | object | Ice zone (Off, Def, Neu) | d |
| `event_zone_id` | object | Ice zone (Off, Def, Neu) | ZN02 |
| `sequence_key` | object | - | SQ1896900062 |
| `play_key` | object | - | PL1896906205 |
| `event_chain_key` | object | - | EC18969001033 |
| `tracking_event_key` | object | - | TV1896909004 |
| `shift_key` | object | - | SH1896900001 |
| `linked_event_key` | object | - | LV1896909004 |
| `home_team` | object | - | Platinum |
| `home_team_id` | object | Unique team identifier | N10008 |
| `away_team` | object | - | Velodrome |
| `away_team_id` | object | Unique team identifier | N10010 |
| `duration` | float64 | - | 0.0 |
| `event_player_ids` | object | Unique player identifier | P100016,P100108 |
| `opp_player_ids` | object | Unique player identifier | P100024 |
| `player_name` | object | Player full name | Wyatt Crandall |
| `season_id` | object | Foreign key reference | N20252026F |
| `position_id` | float64 | Player position (C, LW, RW, D, G) | 6.0 |
| `shot_type_id` | float64 | Foreign key reference |  |
| `zone_entry_type_id` | float64 | Ice zone (Off, Def, Neu) |  |
| `zone_exit_type_id` | float64 | Ice zone (Off, Def, Neu) |  |
| `stoppage_type_id` | float64 | Foreign key reference |  |
| `giveaway_type_id` | float64 | Foreign key reference |  |
| `takeaway_type_id` | float64 | Foreign key reference |  |
| `turnover_type_id` | float64 | Foreign key reference |  |
| `pass_type_id` | float64 | Foreign key reference |  |
| `time_bucket_id` | object | Foreign key reference | TB01 |
| `strength_id` | object | Foreign key reference | STR0001 |
| `cycle_key` | float64 | - |  |
| `is_cycle` | int64 | Boolean flag | 0 |
| `event_start_min` | float64 | - | 16.0 |
| `event_start_sec` | float64 | - | 48.0 |
| `event_end_min` | float64 | - | 13.0 |
| `event_end_sec` | float64 | - | 14.0 |
| `running_video_time` | float64 | - | 72.0 |
| `event_running_start` | float64 | - | 67.0 |
| `event_running_end` | float64 | - | 72.0 |
| `play_detail1` | float64 | - |  |
| `is_rush` | int64 | Boolean flag | 0 |
| `is_rebound` | int64 | Boolean flag | 1 |
| `is_breakout` | int64 | Boolean flag | 0 |
| `is_zone_entry` | int64 | Ice zone (Off, Def, Neu) | 0 |
| `is_zone_exit` | int64 | Ice zone (Off, Def, Neu) | 0 |
| `is_shot` | int64 | Boolean flag | 0 |
| `is_goal` | int64 | Boolean flag | 0 |
| `is_save` | int64 | Boolean flag | 1 |
| `is_turnover` | int64 | Boolean flag | 0 |
| `is_giveaway` | int64 | Boolean flag | 0 |
| `is_takeaway` | int64 | Boolean flag | 0 |
| `is_faceoff` | int64 | Boolean flag | 0 |
| `is_penalty` | int64 | Boolean flag | 0 |
| `is_blocked_shot` | int64 | Boolean flag | 0 |
| `is_missed_shot` | int64 | Boolean flag | 0 |
| `is_deflected` | int64 | Boolean flag | 0 |
| `is_sog` | int64 | Boolean flag | 0 |
| `shot_outcome_id` | float64 | Foreign key reference |  |
| `pass_outcome_id` | float64 | Foreign key reference |  |
| `save_outcome_id` | object | Foreign key reference | SV01 |
| `zone_outcome_id` | float64 | Ice zone (Off, Def, Neu) |  |
| `is_scoring_chance` | int64 | Boolean flag | 0 |
| `is_high_danger` | int64 | Boolean flag | 0 |
| `pressured_pressurer` | float64 | - |  |
| `is_pressured` | int64 | Boolean flag | 0 |
| `danger_level` | float64 | - |  |
| `danger_level_id` | float64 | Foreign key reference |  |
| `scoring_chance_key` | float64 | - |  |
| `save_key` | object | - | SV189690033 |

---

### fact_scoring_chances_detailed

**Rows:** 455 | **Columns:** 78

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `event_id` | object | Unique event identifier | EV1896901012 |
| `game_id` | int64 | Unique game identifier from NORAD league | 18969 |
| `period` | int64 | Game period | 1 |
| `period_id` | object | Game period (1, 2, 3, OT) | P01 |
| `event_type` | object | Type of event (Goal, Shot, Pass, etc.) | Shot |
| `event_type_id` | object | Type of event (Goal, Shot, Pass, etc.) | ET0001 |
| `event_detail` | object | Detailed event subtype | Shot_Blocked |
| `event_detail_id` | object | Detailed event subtype | ED0008 |
| `event_detail_2` | object | Detailed event subtype | Shot_Wrist |
| `event_detail_2_id` | object | Detailed event subtype | ED263 |
| `event_successful` | object | - | u |
| `success_id` | object | Foreign key reference | SC02 |
| `event_team_zone` | object | Ice zone (Off, Def, Neu) | o |
| `event_zone_id` | object | Ice zone (Off, Def, Neu) | ZN01 |
| `sequence_key` | object | - | SQ1896900001 |
| `play_key` | object | - | PL1896900102 |
| `event_chain_key` | object | - | EC18969001012 |
| `tracking_event_key` | object | - | TV1896901012 |
| `shift_key` | object | - | SH1896900001 |
| `linked_event_key` | object | - | LV1896909004 |
| `home_team` | object | - | Platinum |
| `home_team_id` | object | Unique team identifier | N10008 |
| `away_team` | object | - | Velodrome |
| `away_team_id` | object | Unique team identifier | N10010 |
| `duration` | float64 | - | 0.0 |
| `event_player_ids` | object | Unique player identifier | P100161 |
| `opp_player_ids` | object | Unique player identifier | P100024 |
| `player_name` | object | Player full name | Galen Wood |
| `season_id` | object | Foreign key reference | N20252026F |
| `position_id` | float64 | Player position (C, LW, RW, D, G) | 4.0 |
| `shot_type_id` | float64 | Foreign key reference |  |
| `zone_entry_type_id` | float64 | Ice zone (Off, Def, Neu) |  |
| `zone_exit_type_id` | float64 | Ice zone (Off, Def, Neu) |  |
| `stoppage_type_id` | object | Foreign key reference | SP0010 |
| `giveaway_type_id` | object | Foreign key reference | GT0005 |
| `takeaway_type_id` | float64 | Foreign key reference |  |
| `turnover_type_id` | object | Foreign key reference | TO0007 |
| `pass_type_id` | float64 | Foreign key reference |  |
| `time_bucket_id` | object | Foreign key reference | TB01 |
| `strength_id` | object | Foreign key reference | STR0001 |
| `cycle_key` | object | - | CY189690002 |
| `is_cycle` | int64 | Boolean flag | 0 |
| `event_start_min` | float64 | - | 17.0 |
| `event_start_sec` | float64 | - | 33.0 |
| `event_end_min` | float64 | - | 13.0 |
| `event_end_sec` | float64 | - | 14.0 |
| `running_video_time` | float64 | - | 27.0 |
| `event_running_start` | float64 | - | 22.0 |
| `event_running_end` | float64 | - | 27.0 |
| `play_detail1` | object | - | SecondTouch |
| `is_rush` | int64 | Boolean flag | 0 |
| `is_rebound` | int64 | Boolean flag | 0 |
| `is_breakout` | int64 | Boolean flag | 0 |
| `is_zone_entry` | int64 | Ice zone (Off, Def, Neu) | 0 |
| `is_zone_exit` | int64 | Ice zone (Off, Def, Neu) | 0 |
| `is_shot` | int64 | Boolean flag | 1 |
| `is_goal` | int64 | Boolean flag | 0 |
| `is_save` | int64 | Boolean flag | 0 |
| `is_turnover` | int64 | Boolean flag | 0 |
| `is_giveaway` | int64 | Boolean flag | 0 |
| `is_takeaway` | int64 | Boolean flag | 0 |
| `is_faceoff` | int64 | Boolean flag | 0 |
| `is_penalty` | int64 | Boolean flag | 0 |
| `is_blocked_shot` | int64 | Boolean flag | 1 |
| `is_missed_shot` | int64 | Boolean flag | 0 |
| `is_deflected` | int64 | Boolean flag | 0 |
| `is_sog` | int64 | Boolean flag | 0 |
| `shot_outcome_id` | object | Foreign key reference | SO03 |
| `pass_outcome_id` | float64 | Foreign key reference |  |
| `save_outcome_id` | float64 | Foreign key reference |  |
| `zone_outcome_id` | float64 | Ice zone (Off, Def, Neu) |  |
| `is_scoring_chance` | int64 | Boolean flag | 1 |
| `is_high_danger` | int64 | Boolean flag | 0 |
| `pressured_pressurer` | float64 | - | 1.0 |
| `is_pressured` | int64 | Boolean flag | 1 |
| `danger_level` | object | - | medium |
| `danger_level_id` | object | Foreign key reference | DL02 |
| `scoring_chance_key` | object | - | SC189690000 |

---

### fact_season_summary

**Rows:** 1 | **Columns:** 7

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `season_summary_key` | object | - | SS2024001 |
| `season_id` | object | Foreign key reference | S2024 |
| `games_tracked` | int64 | - | 4 |
| `total_goals` | int64 | Goals scored | 0 |
| `total_players` | int64 | - | 0 |
| `avg_goals_per_game` | float64 | Goals scored | 0.0 |
| `created_at` | object | Record creation timestamp | 2026-01-07T21:13:25.57319... |

---

### fact_sequences

**Rows:** 397 | **Columns:** 38

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `sequence_key` | object | - | SQ1896900001 |
| `sequence_id` | object | Foreign key reference | SQ1896900001 |
| `game_id` | int64 | Unique game identifier from NORAD league | 18969 |
| `season_id` | object | Foreign key reference | N20252026F |
| `period` | int64 | Game period | 1 |
| `period_id` | object | Game period (1, 2, 3, OT) | P01 |
| `first_event_key` | object | - | EV1896901001 |
| `last_event_key` | object | - | EV1896901038 |
| `event_count` | int64 | Count/total | 27 |
| `start_min` | float64 | - | 18.0 |
| `start_sec` | float64 | - | 0.0 |
| `duration_seconds` | float64 | - | 44.0 |
| `video_time_start` | float64 | - | 0.0 |
| `video_time_end` | float64 | - | 80.0 |
| `time_bucket_id` | object | Foreign key reference | TB01 |
| `strength_id` | object | Foreign key reference | STR0001 |
| `home_team` | object | - | Platinum |
| `home_team_id` | object | Unique team identifier | N10008 |
| `away_team` | object | - | Velodrome |
| `away_team_id` | object | Unique team identifier | N10010 |
| `start_zone` | object | Ice zone (Off, Def, Neu) | n |
| `end_zone` | object | Ice zone (Off, Def, Neu) | n |
| `start_zone_id` | object | Ice zone (Off, Def, Neu) | ZN03 |
| `end_zone_id` | object | Ice zone (Off, Def, Neu) | ZN03 |
| `event_types` | object | Type of event (Goal, Shot, Pass, etc.) | Faceoff,Pass,Possession,P... |
| `has_goal` | bool | Boolean flag | False |
| `goal_count` | int64 | Count/total | 0 |
| `shot_count` | int64 | Count/total | 3 |
| `zone_entry_count` | int64 | Ice zone (Off, Def, Neu) | 2 |
| `zone_exit_count` | int64 | Ice zone (Off, Def, Neu) | 0 |
| `pass_count` | int64 | Count/total | 4 |
| `pass_success_count` | int64 | Count/total | 4 |
| `pass_success_rate` | float64 | Rate value | 1.0 |
| `turnover_count` | int64 | Count/total | 3 |
| `giveaway_count` | int64 | Count/total | 2 |
| `takeaway_count` | int64 | Count/total | 1 |
| `unique_player_count` | int64 | Count/total | 9 |
| `player_ids` | object | Unique player identifier | P100001,P100023,P100024,P... |

---

### fact_shift_players

**Bridge table linking shifts to players**

| Property | Value |
|----------|-------|
| Grain | One row per player per shift |
| Rows | 4,613 |
| Columns | 9 |

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `shift_player_id` | object | Unique player identifier | SH1896900001_home_F1 |
| `shift_id` | object | Foreign key reference | SH1896900001 |
| `game_id` | int64 | Unique game identifier from NORAD league | 18969 |
| `shift_index` | int64 | Sequential shift number within a game | 1 |
| `player_game_number` | int64 | - | 53 |
| `player_id` | object | Unique player identifier | P100192 |
| `venue` | object | - | home |
| `position` | object | Player position (C, LW, RW, D, G) | F1 |
| `period` | int64 | Game period | 1 |

---

### fact_shifts

**Player shift data - when players are on the ice**

| Property | Value |
|----------|-------|
| Grain | One row per shift per game |
| Rows | 398 |
| Columns | 129 |

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `shift_id` | object | Foreign key reference | SH1896900001 |
| `game_id` | int64 | Unique game identifier from NORAD league | 18969 |
| `shift_index` | int64 | Sequential shift number within a game | 1 |
| `period` | float64 | Game period | 1.0 |
| `shift_start_type` | object | - | GameStart |
| `shift_stop_type` | object | - | Away Icing |
| `shift_start_min` | float64 | - | 18.0 |
| `shift_start_sec` | float64 | - | 0.0 |
| `shift_end_min` | float64 | - | 16.0 |
| `shift_end_sec` | float64 | - | 38.0 |
| `home_team` | object | - | Platinum |
| `away_team` | object | - | Velodrome |
| `home_forward_1` | float64 | - | 53.0 |
| `home_forward_2` | float64 | - | 20.0 |
| `home_forward_3` | float64 | - | 12.0 |
| `home_defense_1` | float64 | - | 8.0 |
| `home_defense_2` | float64 | - | 21.0 |
| `home_xtra` | float64 | - | 68.5 |
| `home_goalie` | float64 | - | 99.0 |
| `away_forward_1` | float64 | - | 70.0 |
| `away_forward_2` | float64 | - | 75.0 |
| `away_forward_3` | float64 | - | 49.0 |
| `away_defense_1` | float64 | - | 52.0 |
| `away_defense_2` | float64 | - | 22.0 |
| `away_xtra` | float64 | - | 91.0 |
| `away_goalie` | float64 | - | 39.0 |
| `shift_start_total_seconds` | float64 | - | 1080.0 |
| `shift_end_total_seconds` | float64 | - | 998.0 |
| `shift_duration` | float64 | Length of shift in seconds | 82.0 |
| `home_team_strength` | float64 | - | 5.0 |
| `away_team_strength` | float64 | - | 5.0 |
| `home_team_en` | float64 | - | 0.0 |
| `away_team_en` | float64 | - | 0.0 |
| `home_team_pk` | float64 | - | 0.0 |
| `home_team_pp` | float64 | - | 0.0 |
| `away_team_pp` | float64 | - | 0.0 |
| `away_team_pk` | float64 | - | 0.0 |
| `situation` | object | - | Full Strength |
| `strength` | object | - | 5v5 |
| `home_goals` | float64 | Goals scored | 0.0 |
| `away_goals` | float64 | Goals scored | 0.0 |
| `stoppage_time` | float64 | - | 0.0 |
| `home_ozone_start` | float64 | Ice zone (Off, Def, Neu) | 0.0 |
| `home_ozone_end` | float64 | Ice zone (Off, Def, Neu) | 1.0 |
| `home_dzone_start` | float64 | Ice zone (Off, Def, Neu) | 1.0 |
| `home_dzone_end` | float64 | Ice zone (Off, Def, Neu) | 1.0 |
| `home_nzone_start` | float64 | Ice zone (Off, Def, Neu) | 1.0 |
| `home_nzone_end` | float64 | Ice zone (Off, Def, Neu) | 1.0 |
| `period_id` | object | Game period (1, 2, 3, OT) | P01 |
| `home_team_id` | object | Unique team identifier | N10008 |
| `away_team_id` | object | Unique team identifier | N10010 |
| `season_id` | object | Foreign key reference | N20252026F |
| `time_bucket_id` | object | Foreign key reference | TB01 |
| `strength_id` | object | Foreign key reference | STR0001 |
| `shift_start_type_derived` | object | - | GameStart |
| `shift_stop_type_derived` | object | - | Away Icing |
| `start_zone` | object | Ice zone (Off, Def, Neu) | n |
| `end_zone` | object | Ice zone (Off, Def, Neu) | n |
| `start_zone_id` | float64 | Ice zone (Off, Def, Neu) | 3.0 |
| `end_zone_id` | float64 | Ice zone (Off, Def, Neu) | 3.0 |
| `home_forward_1_id` | object | Foreign key reference | P100192 |
| `home_forward_2_id` | object | Foreign key reference | P100024 |
| `home_forward_3_id` | object | Foreign key reference | P100027 |
| `home_defense_1_id` | object | Foreign key reference | P100030 |
| `home_defense_2_id` | object | Foreign key reference | P100025 |
| `home_xtra_id` | object | Foreign key reference | P100066 |
| `home_goalie_id` | object | Foreign key reference | P100202 |
| `away_forward_1_id` | object | Foreign key reference | P100001 |
| `away_forward_2_id` | object | Foreign key reference | P100039 |
| `away_forward_3_id` | object | Foreign key reference | P100161 |
| `away_defense_1_id` | object | Foreign key reference | P100070 |
| `away_defense_2_id` | object | Foreign key reference | P100108 |
| `away_xtra_id` | object | Foreign key reference | P100002 |
| `away_goalie_id` | object | Foreign key reference | P100016 |
| `home_gf_all` | int64 | - | 0 |
| `home_ga_all` | int64 | - | 0 |
| `away_gf_all` | int64 | - | 0 |
| `away_ga_all` | int64 | - | 0 |
| `home_gf_ev` | int64 | - | 0 |
| `home_ga_ev` | int64 | - | 0 |
| `away_gf_ev` | int64 | - | 0 |
| `away_ga_ev` | int64 | - | 0 |
| `home_gf_nen` | int64 | - | 0 |
| `home_ga_nen` | int64 | - | 0 |
| `away_gf_nen` | int64 | - | 0 |
| `away_ga_nen` | int64 | - | 0 |
| `home_gf_pp` | int64 | - | 0 |
| `home_ga_pp` | int64 | - | 0 |
| `away_gf_pp` | int64 | - | 0 |
| `away_ga_pp` | int64 | - | 0 |
| `home_gf_pk` | int64 | - | 0 |
| `home_ga_pk` | int64 | - | 0 |
| `away_gf_pk` | int64 | - | 0 |
| `away_ga_pk` | int64 | - | 0 |
| `home_pm_all` | int64 | - | 0 |
| `away_pm_all` | int64 | - | 0 |
| `home_pm_ev` | int64 | - | 0 |
| `away_pm_ev` | int64 | - | 0 |
| `home_pm_nen` | int64 | - | 0 |
| `away_pm_nen` | int64 | - | 0 |
| `home_pm_pp` | int64 | - | 0 |
| `away_pm_pp` | int64 | - | 0 |
| `home_pm_pk` | int64 | - | 0 |
| `away_pm_pk` | int64 | - | 0 |
| `sf` | int64 | - | 1 |
| `sa` | int64 | - | 0 |
| `shot_diff` | int64 | - | 1 |
| `cf` | int64 | - | 3 |
| `ca` | int64 | - | 1 |
| `cf_pct` | float64 | Percentage value | 75.0 |
| `ff` | int64 | - | 3 |
| `fa` | int64 | - | 1 |
| `ff_pct` | float64 | Percentage value | 75.0 |
| `scf` | int64 | - | 3 |
| `sca` | int64 | - | 1 |
| `hdf` | int64 | - | 1 |
| `hda` | int64 | - | 0 |
| `zone_entries` | int64 | Ice zone (Off, Def, Neu) | 3 |
| `zone_exits` | int64 | Ice zone (Off, Def, Neu) | 3 |
| `giveaways` | int64 | - | 3 |
| `takeaways` | int64 | - | 1 |
| `fo_won` | int64 | - | 0 |
| `fo_lost` | int64 | - | 0 |
| `fo_pct` | float64 | Percentage value | 0.0 |
| `event_count` | int64 | Count/total | 39 |
| `shift_start_type_id` | object | Foreign key reference | SST0001 |
| `shift_stop_type_id` | object | Foreign key reference | SPT0001 |
| `situation_id` | object | Foreign key reference | SIT0001 |
| `shift_key` | object | - | SH1896900001 |

---

### fact_tracking

**Rows:** 5,117 | **Columns:** 22

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `tracking_event_key` | object | - | TV1896901000 |
| `game_id` | int64 | Unique game identifier from NORAD league | 18969 |
| `period` | int64 | Game period | 1 |
| `period_id` | object | Game period (1, 2, 3, OT) | P01 |
| `event_start_min` | float64 | - | 18.0 |
| `event_start_sec` | float64 | - | 0.0 |
| `event_end_min` | float64 | - | 17.0 |
| `event_end_sec` | float64 | - | 52.0 |
| `time_start_total_seconds` | float64 | - | 1080.0 |
| `time_end_total_seconds` | float64 | - | 1080.0 |
| `running_video_time` | float64 | - | 0.0 |
| `event_running_start` | float64 | - | 0.0 |
| `event_running_end` | float64 | - | 5.0 |
| `event_team_zone` | object | Ice zone (Off, Def, Neu) | n |
| `home_team_zone` | object | Ice zone (Off, Def, Neu) | n |
| `away_team_zone` | object | Ice zone (Off, Def, Neu) | n |
| `x_coord` | float64 | - |  |
| `y_coord` | float64 | - |  |
| `rink_zone` | float64 | Ice zone (Off, Def, Neu) |  |
| `season_id` | object | Foreign key reference | N20252026F |
| `time_bucket_id` | object | Foreign key reference | TB01 |
| `strength_id` | object | Foreign key reference | STR0001 |

---

### fact_turnovers_detailed

**Rows:** 741 | **Columns:** 79

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `event_id` | object | Unique event identifier | EV1896901006 |
| `game_id` | int64 | Unique game identifier from NORAD league | 18969 |
| `period` | int64 | Game period | 1 |
| `period_id` | object | Game period (1, 2, 3, OT) | P01 |
| `event_type` | object | Type of event (Goal, Shot, Pass, etc.) | Turnover |
| `event_type_id` | object | Type of event (Goal, Shot, Pass, etc.) | ET0005 |
| `event_detail` | object | Detailed event subtype | Turnover_Giveaway |
| `event_detail_id` | object | Detailed event subtype | ED0030 |
| `event_detail_2` | object | Detailed event subtype | Giveaway_ZoneClear_Dump |
| `event_detail_2_id` | object | Detailed event subtype | ED214 |
| `event_successful` | object | - | u |
| `success_id` | object | Foreign key reference | SC02 |
| `event_team_zone` | object | Ice zone (Off, Def, Neu) | n |
| `event_zone_id` | object | Ice zone (Off, Def, Neu) | ZN03 |
| `sequence_key` | object | - | SQ1896900062 |
| `play_key` | object | - | PL1896906202 |
| `event_chain_key` | object | - | EC18969001006 |
| `tracking_event_key` | object | - | TV1896909001 |
| `shift_key` | object | - | SH1896900001 |
| `linked_event_key` | object | - | LV1896909001 |
| `home_team` | object | - | Platinum |
| `home_team_id` | object | Unique team identifier | N10008 |
| `away_team` | object | - | Velodrome |
| `away_team_id` | object | Unique team identifier | N10010 |
| `duration` | float64 | - | 0.0 |
| `event_player_ids` | object | Unique player identifier | P100024 |
| `opp_player_ids` | object | Unique player identifier | P100030 |
| `player_name` | object | Player full name | John Thien |
| `season_id` | object | Foreign key reference | N20252026F |
| `position_id` | float64 | Player position (C, LW, RW, D, G) | 4.0 |
| `shot_type_id` | float64 | Foreign key reference |  |
| `zone_entry_type_id` | object | Ice zone (Off, Def, Neu) | ZE0010 |
| `zone_exit_type_id` | float64 | Ice zone (Off, Def, Neu) |  |
| `stoppage_type_id` | object | Foreign key reference | SP0008 |
| `giveaway_type_id` | object | Foreign key reference | GT0005 |
| `takeaway_type_id` | object | Foreign key reference | TA0010 |
| `turnover_type_id` | object | Foreign key reference | TO0007 |
| `pass_type_id` | float64 | Foreign key reference |  |
| `time_bucket_id` | object | Foreign key reference | TB01 |
| `strength_id` | object | Foreign key reference | STR0001 |
| `cycle_key` | float64 | - |  |
| `is_cycle` | int64 | Boolean flag | 0 |
| `event_start_min` | float64 | - | 17.0 |
| `event_start_sec` | float64 | - | 49.0 |
| `event_end_min` | float64 | - | 14.0 |
| `event_end_sec` | float64 | - | 31.0 |
| `running_video_time` | float64 | - | 11.0 |
| `event_running_start` | float64 | - | 6.0 |
| `event_running_end` | float64 | - | 11.0 |
| `play_detail1` | object | - | Chip |
| `is_rush` | int64 | Boolean flag | 0 |
| `is_rebound` | int64 | Boolean flag | 0 |
| `is_breakout` | int64 | Boolean flag | 0 |
| `is_zone_entry` | int64 | Ice zone (Off, Def, Neu) | 0 |
| `is_zone_exit` | int64 | Ice zone (Off, Def, Neu) | 0 |
| `is_shot` | int64 | Boolean flag | 0 |
| `is_goal` | int64 | Boolean flag | 0 |
| `is_save` | int64 | Boolean flag | 0 |
| `is_turnover` | int64 | Boolean flag | 1 |
| `is_giveaway` | int64 | Boolean flag | 1 |
| `is_takeaway` | int64 | Boolean flag | 0 |
| `is_faceoff` | int64 | Boolean flag | 0 |
| `is_penalty` | int64 | Boolean flag | 0 |
| `is_blocked_shot` | int64 | Boolean flag | 0 |
| `is_missed_shot` | int64 | Boolean flag | 0 |
| `is_deflected` | int64 | Boolean flag | 0 |
| `is_sog` | int64 | Boolean flag | 0 |
| `shot_outcome_id` | float64 | Foreign key reference |  |
| `pass_outcome_id` | float64 | Foreign key reference |  |
| `save_outcome_id` | float64 | Foreign key reference |  |
| `zone_outcome_id` | float64 | Ice zone (Off, Def, Neu) |  |
| `is_scoring_chance` | int64 | Boolean flag | 0 |
| `is_high_danger` | int64 | Boolean flag | 0 |
| `pressured_pressurer` | float64 | - | 1.0 |
| `is_pressured` | int64 | Boolean flag | 0 |
| `danger_level` | float64 | - |  |
| `danger_level_id` | float64 | Foreign key reference |  |
| `scoring_chance_key` | float64 | - |  |
| `turnover_key_new` | object | - | TO189690006 |

---

### fact_zone_entries

**Rows:** 508 | **Columns:** 80

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `event_id` | object | Unique event identifier | EV1896901005 |
| `game_id` | int64 | Unique game identifier from NORAD league | 18969 |
| `period` | int64 | Game period | 1 |
| `period_id` | object | Game period (1, 2, 3, OT) | P01 |
| `event_type` | object | Type of event (Goal, Shot, Pass, etc.) | Zone_Entry_Exit |
| `event_type_id` | object | Type of event (Goal, Shot, Pass, etc.) | ET0006 |
| `event_detail` | object | Detailed event subtype | Zone_Entry |
| `event_detail_id` | object | Detailed event subtype | ED0030 |
| `event_detail_2` | object | Detailed event subtype | ZoneEntry_DumpIn |
| `event_detail_2_id` | object | Detailed event subtype | ED277 |
| `event_successful` | object | - | u |
| `success_id` | object | Foreign key reference | SC02 |
| `event_team_zone` | object | Ice zone (Off, Def, Neu) | n |
| `event_zone_id` | object | Ice zone (Off, Def, Neu) | ZN03 |
| `sequence_key` | object | - | SQ1896900062 |
| `play_key` | object | - | PL1896906202 |
| `event_chain_key` | object | - | EC18969001005 |
| `tracking_event_key` | object | - | TV1896909001 |
| `shift_key` | object | - | SH1896900001 |
| `linked_event_key` | object | - | LV1896909001 |
| `home_team` | object | - | Platinum |
| `home_team_id` | object | Unique team identifier | N10008 |
| `away_team` | object | - | Velodrome |
| `away_team_id` | object | Unique team identifier | N10010 |
| `duration` | float64 | - | 0.0 |
| `event_player_ids` | object | Unique player identifier | P100024 |
| `opp_player_ids` | object | Unique player identifier | P100030 |
| `player_name` | object | Player full name | John Thien |
| `season_id` | object | Foreign key reference | N20252026F |
| `position_id` | float64 | Player position (C, LW, RW, D, G) | 4.0 |
| `shot_type_id` | float64 | Foreign key reference |  |
| `zone_entry_type_id` | object | Ice zone (Off, Def, Neu) | ZE0003 |
| `zone_exit_type_id` | object | Ice zone (Off, Def, Neu) | ZX0007 |
| `stoppage_type_id` | float64 | Foreign key reference |  |
| `giveaway_type_id` | object | Foreign key reference | GT0005 |
| `takeaway_type_id` | float64 | Foreign key reference |  |
| `turnover_type_id` | object | Foreign key reference | TO0007 |
| `pass_type_id` | float64 | Foreign key reference |  |
| `time_bucket_id` | object | Foreign key reference | TB01 |
| `strength_id` | object | Foreign key reference | STR0001 |
| `cycle_key` | object | - | CY189770013 |
| `is_cycle` | int64 | Boolean flag | 0 |
| `event_start_min` | float64 | - | 17.0 |
| `event_start_sec` | float64 | - | 49.0 |
| `event_end_min` | float64 | - | 17.0 |
| `event_end_sec` | float64 | - | 33.0 |
| `running_video_time` | float64 | - | 11.0 |
| `event_running_start` | float64 | - | 6.0 |
| `event_running_end` | float64 | - | 11.0 |
| `play_detail1` | object | - | Chip |
| `is_rush` | int64 | Boolean flag | 0 |
| `is_rebound` | int64 | Boolean flag | 0 |
| `is_breakout` | int64 | Boolean flag | 0 |
| `is_zone_entry` | int64 | Ice zone (Off, Def, Neu) | 1 |
| `is_zone_exit` | int64 | Ice zone (Off, Def, Neu) | 0 |
| `is_shot` | int64 | Boolean flag | 0 |
| `is_goal` | int64 | Boolean flag | 0 |
| `is_save` | int64 | Boolean flag | 0 |
| `is_turnover` | int64 | Boolean flag | 0 |
| `is_giveaway` | int64 | Boolean flag | 0 |
| `is_takeaway` | int64 | Boolean flag | 0 |
| `is_faceoff` | int64 | Boolean flag | 0 |
| `is_penalty` | int64 | Boolean flag | 0 |
| `is_blocked_shot` | int64 | Boolean flag | 0 |
| `is_missed_shot` | int64 | Boolean flag | 0 |
| `is_deflected` | int64 | Boolean flag | 0 |
| `is_sog` | int64 | Boolean flag | 0 |
| `shot_outcome_id` | float64 | Foreign key reference |  |
| `pass_outcome_id` | float64 | Foreign key reference |  |
| `save_outcome_id` | float64 | Foreign key reference |  |
| `zone_outcome_id` | object | Ice zone (Off, Def, Neu) | ZO01 |
| `is_scoring_chance` | int64 | Boolean flag | 0 |
| `is_high_danger` | int64 | Boolean flag | 0 |
| `pressured_pressurer` | float64 | - | 1.0 |
| `is_pressured` | int64 | Boolean flag | 0 |
| `danger_level` | float64 | - |  |
| `danger_level_id` | float64 | Foreign key reference |  |
| `scoring_chance_key` | float64 | - |  |
| `zone_entry_key` | object | Ice zone (Off, Def, Neu) | ZN189690005 |
| `entry_method` | object | - | dump_in |

---

### fact_zone_exits

**Rows:** 487 | **Columns:** 80

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `event_id` | object | Unique event identifier | EV1896901009 |
| `game_id` | int64 | Unique game identifier from NORAD league | 18969 |
| `period` | int64 | Game period | 1 |
| `period_id` | object | Game period (1, 2, 3, OT) | P01 |
| `event_type` | object | Type of event (Goal, Shot, Pass, etc.) | Zone_Entry_Exit |
| `event_type_id` | object | Type of event (Goal, Shot, Pass, etc.) | ET0006 |
| `event_detail` | object | Detailed event subtype | Zone_Exit |
| `event_detail_id` | float64 | Detailed event subtype |  |
| `event_detail_2` | object | Detailed event subtype | ZoneExit_Pass |
| `event_detail_2_id` | object | Detailed event subtype | ED292 |
| `event_successful` | object | - | s |
| `success_id` | object | Foreign key reference | SC01 |
| `event_team_zone` | object | Ice zone (Off, Def, Neu) | d |
| `event_zone_id` | object | Ice zone (Off, Def, Neu) | ZN02 |
| `sequence_key` | object | - | SQ1896900062 |
| `play_key` | object | - | PL1896906203 |
| `event_chain_key` | object | - | EC18969001009 |
| `tracking_event_key` | object | - | TV1896909002 |
| `shift_key` | object | - | SH1896900001 |
| `linked_event_key` | object | - | LV1896909002 |
| `home_team` | object | - | Platinum |
| `home_team_id` | object | Unique team identifier | N10008 |
| `away_team` | object | - | Velodrome |
| `away_team_id` | object | Unique team identifier | N10010 |
| `duration` | float64 | - | 0.0 |
| `event_player_ids` | object | Unique player identifier | P100070,P100161 |
| `opp_player_ids` | object | Unique player identifier | P100210 |
| `player_name` | object | Player full name | Hayden Perea |
| `season_id` | object | Foreign key reference | N20252026F |
| `position_id` | float64 | Player position (C, LW, RW, D, G) | 5.0 |
| `shot_type_id` | float64 | Foreign key reference |  |
| `zone_entry_type_id` | object | Ice zone (Off, Def, Neu) | ZE0010 |
| `zone_exit_type_id` | object | Ice zone (Off, Def, Neu) | ZX0007 |
| `stoppage_type_id` | float64 | Foreign key reference |  |
| `giveaway_type_id` | object | Foreign key reference | GT0005 |
| `takeaway_type_id` | float64 | Foreign key reference |  |
| `turnover_type_id` | object | Foreign key reference | TO0007 |
| `pass_type_id` | float64 | Foreign key reference |  |
| `time_bucket_id` | object | Foreign key reference | TB01 |
| `strength_id` | object | Foreign key reference | STR0001 |
| `cycle_key` | float64 | - |  |
| `is_cycle` | int64 | Boolean flag | 0 |
| `event_start_min` | float64 | - | 17.0 |
| `event_start_sec` | float64 | - | 41.0 |
| `event_end_min` | float64 | - | 12.0 |
| `event_end_sec` | float64 | - | 40.0 |
| `running_video_time` | float64 | - | 19.0 |
| `event_running_start` | float64 | - | 14.0 |
| `event_running_end` | float64 | - | 19.0 |
| `play_detail1` | object | - | Breakout |
| `is_rush` | int64 | Boolean flag | 0 |
| `is_rebound` | int64 | Boolean flag | 0 |
| `is_breakout` | int64 | Boolean flag | 1 |
| `is_zone_entry` | int64 | Ice zone (Off, Def, Neu) | 0 |
| `is_zone_exit` | int64 | Ice zone (Off, Def, Neu) | 1 |
| `is_shot` | int64 | Boolean flag | 0 |
| `is_goal` | int64 | Boolean flag | 0 |
| `is_save` | int64 | Boolean flag | 0 |
| `is_turnover` | int64 | Boolean flag | 0 |
| `is_giveaway` | int64 | Boolean flag | 0 |
| `is_takeaway` | int64 | Boolean flag | 0 |
| `is_faceoff` | int64 | Boolean flag | 0 |
| `is_penalty` | int64 | Boolean flag | 0 |
| `is_blocked_shot` | int64 | Boolean flag | 0 |
| `is_missed_shot` | int64 | Boolean flag | 0 |
| `is_deflected` | int64 | Boolean flag | 0 |
| `is_sog` | int64 | Boolean flag | 0 |
| `shot_outcome_id` | float64 | Foreign key reference |  |
| `pass_outcome_id` | float64 | Foreign key reference |  |
| `save_outcome_id` | float64 | Foreign key reference |  |
| `zone_outcome_id` | object | Ice zone (Off, Def, Neu) | ZO03 |
| `is_scoring_chance` | int64 | Boolean flag | 0 |
| `is_high_danger` | int64 | Boolean flag | 0 |
| `pressured_pressurer` | float64 | - | 1.0 |
| `is_pressured` | int64 | Boolean flag | 0 |
| `danger_level` | float64 | - |  |
| `danger_level_id` | float64 | Foreign key reference |  |
| `scoring_chance_key` | float64 | - |  |
| `zone_exit_key` | object | Ice zone (Off, Def, Neu) | ZX189690009 |
| `exit_method` | object | - | other |

---

## QA Tables

### qa_data_completeness

**Rows:** 4 | **Columns:** 7

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `qa_key` | object | - | QA_COMPLETE_18969 |
| `game_id` | int64 | Unique game identifier from NORAD league | 18969 |
| `has_events` | bool | Boolean flag | True |
| `has_shifts` | bool | Boolean flag | True |
| `has_rosters` | bool | Boolean flag | True |
| `is_complete` | bool | Boolean flag | True |
| `check_date` | object | - | 2026-01-07T21:13:25.62067... |

---

### qa_goal_accuracy

**Quality assurance - verifies goal counts match official records**

| Property | Value |
|----------|-------|
| Grain | One row per game |
| Rows | 4 |
| Columns | 10 |

#### Columns

| Column | Type | Description | Sample |
|--------|------|-------------|--------|
| `qa_key` | object | - | QA_GOAL_18969 |
| `game_id` | int64 | Unique game identifier from NORAD league | 18969 |
| `game_date` | object | - | 2025-09-07 00:00:00 |
| `home_team` | object | - | Platinum |
| `away_team` | object | - | Velodrome |
| `expected_goals` | int64 | Goals scored | 7 |
| `actual_goals` | int64 | Goals scored | 7 |
| `match` | bool | - | True |
| `difference` | int64 | - | 0 |
| `check_date` | object | - | 2026-01-07T21:13:25.61398... |

---

