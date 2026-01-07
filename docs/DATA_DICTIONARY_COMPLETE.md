# BenchSight Complete Data Dictionary

**Purpose:** Definitive reference for all tables, columns, sources, and calculations.

---

## Column Source Legend

| Code | Meaning | Description |
|------|---------|-------------|
| **RAW** | Raw from tracking | Direct from `{game_id}_tracking.xlsx` |
| **BLB** | From BLB_Tables | Direct from `BLB_Tables.xlsx` master data |
| **CALC** | Calculated | ETL computes from raw data |
| **DERIVED** | Derived | Aggregated from other tables |
| **KEY** | Generated key | ETL generates unique identifier |

---

## Dimension Tables

### dim_player
**Source:** BLB_Tables.xlsx → dim_player sheet  
**Purpose:** Master player data for all players in the league

| Column | Source | Description |
|--------|--------|-------------|
| player_id | BLB | Unique player identifier (e.g., "P12345") |
| player_first_name | BLB | First name |
| player_last_name | BLB | Last name |
| player_full_name | BLB | Full name (First Last) |
| current_team_id | BLB | Current team FK |
| current_team_name | BLB | Current team name |
| position | BLB | Position (F, D, G) |
| current_skill_rating | BLB | Skill rating 1.0-5.0 |
| player_email | BLB | Contact email |
| jersey_number | BLB | Preferred jersey number |

---

### dim_team  
**Source:** BLB_Tables.xlsx → dim_team sheet  
**Purpose:** Master team data

| Column | Source | Description |
|--------|--------|-------------|
| team_id | BLB | Unique team identifier |
| team_name | BLB | Full team name (e.g., "Velodrome") |
| team_short_name | BLB | Abbreviated name (e.g., "VEL") |
| division | BLB | Division name |
| league | BLB | League (NORAD, CSAHA) |
| home_rink | BLB | Home rink name |
| team_color_primary | BLB | Primary jersey color |
| team_color_secondary | BLB | Secondary jersey color |

---

### dim_schedule
**Source:** BLB_Tables.xlsx → dim_schedule sheet  
**Purpose:** All scheduled games

| Column | Source | Description |
|--------|--------|-------------|
| game_id | BLB | Unique game identifier |
| season_id | BLB | Season FK |
| game_date | BLB | Date of game |
| game_time | BLB | Scheduled start time |
| home_team_id | BLB | Home team FK |
| home_team_name | BLB | Home team name |
| away_team_id | BLB | Away team FK |
| away_team_name | BLB | Away team name |
| home_score | BLB | Final home score (NULL if not played) |
| away_score | BLB | Final away score (NULL if not played) |
| game_status | BLB | Status (Scheduled, Final, Cancelled) |
| rink_name | BLB | Rink/venue name |

---

### dim_season
**Source:** BLB_Tables.xlsx → dim_season sheet  
**Purpose:** Season definitions

| Column | Source | Description |
|--------|--------|-------------|
| season_id | BLB | Unique season identifier |
| season_name | BLB | Season name (e.g., "Fall 2025") |
| start_date | BLB | First game date |
| end_date | BLB | Last game date |
| league | BLB | League name |
| is_current | BLB | Is this the current season? |

---

## Event Type Reference Tables

### dim_event_type (Reference)
**Source:** Implicit from tracking data  
**Purpose:** Valid event types for tracker

| event_type | Description | Primary Player | Has Result |
|------------|-------------|----------------|------------|
| Shot | Shot attempt | Shooter | Yes (OnNet/Blocked/Missed/Goal) |
| Goal | Goal scored | Scorer | No |
| Pass | Pass attempt | Passer | Yes (Completed/Incomplete) |
| Faceoff | Faceoff taken | Winner | No (implied from role) |
| Hit | Body check | Hitter | No |
| Block | Shot block | Blocker | No |
| Turnover | Puck turnover | Player losing puck | No |
| Recovery | Puck recovery | Player gaining puck | No |
| ZoneEntry | Entry to offensive zone | Carrier | Yes (Carry/Pass/Dump) |
| ZoneExit | Exit from defensive zone | Carrier | Yes (Carry/Pass/Clear) |
| Penalty | Penalty called | Penalized player | No |
| Stoppage | Play stoppage | N/A | No |

---

### dim_event_detail (Reference)
**Source:** Implicit from tracking data  
**Purpose:** Valid event_detail values

| event_detail | event_type | Description |
|--------------|------------|-------------|
| Shot_OnNet | Shot | Shot on goal |
| Shot_Blocked | Shot | Blocked by opponent |
| Shot_Blocked_SameTeam | Shot | Blocked by teammate |
| Shot_Missed | Shot | Missed net |
| Shot_Goal | Shot | Resulted in goal |
| Pass_Completed | Pass | Successful pass |
| Pass_Incomplete | Pass | Failed pass |
| Pass_Intercepted | Pass | Intercepted by opponent |
| Entry_Carry | ZoneEntry | Carried puck in |
| Entry_Pass | ZoneEntry | Passed puck in |
| Entry_Dump | ZoneEntry | Dumped puck in |
| Exit_Carry | ZoneExit | Carried puck out |
| Exit_Pass | ZoneExit | Passed puck out |
| Exit_Clear | ZoneExit | Cleared puck |
| Giveaway | Turnover | Lost possession |
| Takeaway | Recovery | Gained possession |
| Faceoff_Won | Faceoff | Won faceoff |
| Faceoff_Lost | Faceoff | Lost faceoff |

---

### dim_play_detail (Reference)
**Source:** Implicit from tracking data  
**Purpose:** Play detail modifiers

| play_detail | Applies To | Description |
|-------------|------------|-------------|
| Assist_Primary | Goal | Primary assist |
| Assist_Secondary | Goal | Secondary assist |
| OneTimer | Shot | One-timer shot |
| Wrist | Shot | Wrist shot |
| Slap | Shot | Slap shot |
| Backhand | Shot | Backhand shot |
| Deflection | Shot | Deflected shot |
| Tip | Shot | Tipped shot |
| Rebound | Shot | Rebound shot |
| Saucer | Pass | Saucer pass |
| CrossIce | Pass | Cross-ice pass |
| Tape2Tape | Pass | Tape-to-tape pass |
| Breakout | Pass | Breakout pass |
| HighSlot | Location | High slot area |
| LowSlot | Location | Low slot area |
| Point | Location | Point/blue line |
| Circle | Location | Faceoff circle area |
| Behind_Net | Location | Behind the net |
| Crease | Location | Crease area |

---

### dim_player_role (Reference)
**Source:** Implicit from tracking data  
**Purpose:** Player role in events

| player_role | role_number | Description |
|-------------|-------------|-------------|
| event_team_player_1 | 1 | Primary player (performed action) |
| event_team_player_2 | 2 | Secondary player (assist, screen) |
| event_team_player_3 | 3 | Tertiary player |
| opp_team_player_1 | 1 | Opponent primary (defender) |
| opp_team_player_2 | 2 | Opponent secondary |
| opp_team_goalie | 1 | Opposing goalie |
| event_team_goalie | 1 | Own goalie |

---

## Fact Tables - Events

### fact_events
**Source:** Tracking file → events sheet (deduplicated)  
**Purpose:** One row per unique event (wide format)

| Column | Source | Formula/Notes |
|--------|--------|---------------|
| event_key | KEY | `E{game_id:05d}{event_index:06d}` |
| game_id | RAW | From tracking file name |
| period | RAW | Period number (1, 2, 3, OT) |
| event_index | RAW | Sequential event number |
| linked_event_index | RAW | Links related events (shot→save→rebound) |
| sequence_index | RAW | Sequence within play |
| play_index | RAW | Play number |
| event_type | RAW | Type column from tracking |
| event_detail | RAW | Result/detail of event |
| event_detail_2 | RAW | Secondary detail |
| event_successful | RAW | 's' = success, 'u' = unsuccessful |
| event_team_zone | RAW | Zone where event occurred (OZ/NZ/DZ) |
| home_team_zone | RAW | Zone relative to home team |
| away_team_zone | RAW | Zone relative to away team |
| shift_index | RAW | Which shift this occurred in |
| time_start_total_seconds | RAW | Game time in seconds |
| time_end_total_seconds | RAW | Event end time |
| duration | CALC | `time_end - time_start` |
| running_video_time | RAW | Video timestamp if available |

---

### fact_events_player
**Source:** Tracking file → events sheet (all rows)  
**Purpose:** One row per player per event (long format)

| Column | Source | Formula/Notes |
|--------|--------|---------------|
| event_player_key | KEY | `P{game_id:05d}{event_index:05d}{role_number:01d}` |
| event_key | KEY | Links to fact_events |
| game_id | RAW | Game identifier |
| player_id | RAW | Player FK |
| player_name | DERIVED | Lookup from fact_gameroster |
| player_team | RAW | Team name |
| player_game_number | RAW | Jersey number for this game |
| event_index | RAW | Event FK |
| player_role | RAW | Role in event (event_team_player_1, etc.) |
| role_number | RAW | Role sequence (1=primary) |
| period | RAW | Period number |
| event_type | RAW | Event type |
| event_detail | RAW | Event detail |
| play_detail | RAW | play_detail1 from tracking |
| play_detail_2 | RAW | play_detail2 from tracking |

**CRITICAL RULE:** `event_team_player_1` (role_number=1) is the PRIMARY player who performed the action.

---

## Fact Tables - Shifts

### fact_shifts_player
**Source:** Tracking file → shifts sheet (unpivoted)  
**Purpose:** One row per player per shift

| Column | Source | Formula/Notes |
|--------|--------|---------------|
| shift_player_key | KEY | `SP{game_id:05d}{shift_index:05d}{player_hash:04d}` |
| shift_key | KEY | `S{game_id:05d}{shift_index:05d}` |
| game_id | RAW | Game identifier |
| shift_index | RAW | Shift number |
| period | RAW | Period column from shifts |
| venue | CALC | 'home' or 'away' (from which column player was in) |
| slot | CALC | Position slot (forward_1, defense_2, goalie, etc.) |
| player_number | RAW | Jersey number from column value |
| player_id | DERIVED | Lookup from fact_gameroster by (venue, player_number) |
| player_name | DERIVED | Lookup from fact_gameroster |
| team_id | DERIVED | From roster |
| team_name | DERIVED | From roster |
| shift_duration | RAW | shift_duration column |
| shift_start_total_seconds | RAW | Start time in seconds |
| shift_end_total_seconds | RAW | End time in seconds |
| shift_start_type | RAW | How shift started (Faceoff, Line Change) |
| shift_stop_type | RAW | How shift ended (Whistle, Home Goal, etc.) |
| stoppage_time | RAW | Stoppage duration within shift |
| strength | RAW | Game strength (5v5, 5v4, etc.) |
| situation | RAW | Game situation |
| plus | RAW | +/- for this shift |
| minus | RAW | -/+ for this shift |
| home_goal_this_shift | CALC | 1 if shift_stop_type = 'Home Goal' else 0 |
| away_goal_this_shift | CALC | 1 if shift_stop_type = 'Away Goal' else 0 |
| goals_for_this_shift | CALC | home_goal if venue='home' else away_goal |
| goals_against_this_shift | CALC | away_goal if venue='home' else home_goal |
| logical_shift_number | CALC | Groups consecutive shifts into logical shifts |
| shift_segment | CALC | Segment within logical shift |
| cumulative_shift_duration | CALC | Running total within logical shift |
| running_toi | CALC | Cumulative TOI for player in game |
| playing_duration | CALC | `shift_duration - stoppage_time` |
| running_playing_toi | CALC | Cumulative playing TOI |

**Logical Shift Algorithm:**
```python
# New logical shift if:
# 1. Gap in shift_index > 1, OR
# 2. Period changed
if curr_shift_index - prev_shift_index > 1 or curr_period != prev_period:
    logical_shift_number += 1
```

---

## Fact Tables - Statistics

### fact_player_game_stats
**Source:** Aggregated from fact_events_player and fact_shifts_player  
**Purpose:** One row per player per game with all statistics

| Column | Source | Formula/Calculation |
|--------|--------|---------------------|
| player_game_key | KEY | `PG{game_id:05d}{player_hash:05d}` |
| game_id | DERIVED | From events |
| player_id | DERIVED | From events |
| player_name | DERIVED | From events |
| team_name | DERIVED | From roster |
| team_id | DERIVED | From roster |
| team_venue | DERIVED | From roster |
| is_sub | DERIVED | From roster (not on official team roster) |
| player_game_number | DERIVED | From roster |
| skill_rating | DERIVED | From dim_player |

**Scoring Stats:**

| Column | Source | Formula |
|--------|--------|---------|
| goals | CALC | `COUNT(events WHERE event_type='Goal' AND player_role='event_team_player_1')` |
| assists | CALC | `COUNT(events WHERE play_detail CONTAINS 'Assist')` |
| points | CALC | `goals + assists` |

**Shooting Stats:**

| Column | Source | Formula |
|--------|--------|---------|
| shots | CALC | `COUNT(events WHERE event_type='Shot' AND player_role='event_team_player_1')` |
| sog | CALC | `COUNT(shots WHERE event_detail CONTAINS 'OnNet' OR 'Goal')` |
| shots_blocked | CALC | `COUNT(shots WHERE event_detail CONTAINS 'Blocked' AND NOT 'SameTeam')` |
| shots_missed | CALC | `COUNT(shots WHERE event_detail CONTAINS 'Missed')` |
| shooting_pct | CALC | `ROUND(goals / shots * 100, 1)` if shots > 0 else 0 |

**Passing Stats:**

| Column | Source | Formula |
|--------|--------|---------|
| pass_attempts | CALC | `COUNT(events WHERE event_type='Pass' AND player_role='event_team_player_1')` |
| pass_completed | CALC | `COUNT(passes WHERE event_detail='Pass_Completed')` |
| pass_pct | CALC | `ROUND(pass_completed / pass_attempts * 100, 1)` |

**Faceoff Stats:**

| Column | Source | Formula |
|--------|--------|---------|
| fo_wins | CALC | `COUNT(events WHERE event_type='Faceoff' AND player_role='event_team_player_1')` |
| fo_losses | CALC | `COUNT(events WHERE event_type='Faceoff' AND player_role='opp_team_player_1')` |
| fo_total | CALC | `fo_wins + fo_losses` |
| fo_pct | CALC | `ROUND(fo_wins / fo_total * 100, 1)` |

**Zone Stats:**

| Column | Source | Formula |
|--------|--------|---------|
| zone_entries | CALC | `COUNT(events WHERE event_detail CONTAINS 'Entry' AND player_role='event_team_player_1')` |
| zone_exits | CALC | `COUNT(events WHERE event_detail CONTAINS 'Exit' AND player_role='event_team_player_1')` |

**Turnover Stats:**

| Column | Source | Formula |
|--------|--------|---------|
| giveaways | CALC | `COUNT(events WHERE event_detail CONTAINS 'Giveaway' AND player_role='event_team_player_1')` |
| takeaways | CALC | `COUNT(events WHERE event_detail CONTAINS 'Takeaway' AND player_role='event_team_player_1')` |

**Time on Ice Stats:**

| Column | Source | Formula |
|--------|--------|---------|
| toi_seconds | CALC | `SUM(shifts.shift_duration)` |
| toi_minutes | CALC | `ROUND(toi_seconds / 60, 1)` |
| playing_toi_seconds | CALC | `SUM(shifts.playing_duration)` |
| playing_toi_minutes | CALC | `ROUND(playing_toi_seconds / 60, 1)` |
| stoppage_seconds | CALC | `toi_seconds - playing_toi_seconds` |
| shift_count | CALC | `COUNT(shifts)` |
| logical_shifts | CALC | `MAX(shifts.logical_shift_number)` |
| avg_shift | CALC | `ROUND(toi_seconds / logical_shifts, 1)` |
| avg_playing_shift | CALC | `ROUND(playing_toi_seconds / logical_shifts, 1)` |

---

### fact_h2h
**Source:** Calculated from fact_shifts_player  
**Purpose:** Head-to-head matchup time between opposing players

| Column | Source | Formula |
|--------|--------|---------|
| h2h_key | KEY | `H2H{game_id:05d}{p1_hash:04d}{p2_hash:04d}` |
| game_id | DERIVED | From shifts |
| player_1_id | DERIVED | Home player |
| player_1_venue | CALC | Always 'home' |
| player_2_id | DERIVED | Away player |
| player_2_venue | CALC | Always 'away' |
| toi_together | CALC | `SUM(shift_duration WHERE both on ice)` |
| shifts_together | CALC | `COUNT(shifts WHERE both on ice)` |

**Algorithm:**
```python
for each shift_index:
    home_players = players WHERE venue='home'
    away_players = players WHERE venue='away'
    for home_p in home_players:
        for away_p in away_players:
            record (home_p, away_p, shift_duration)
aggregate by (player_1_id, player_2_id)
```

---

### fact_wowy
**Source:** Calculated from fact_shifts_player  
**Purpose:** With Or Without You - performance with/without teammates

| Column | Source | Formula |
|--------|--------|---------|
| wowy_key | KEY | `WY{game_id:05d}{player_hash:04d}{teammate_hash:04d}` |
| game_id | DERIVED | From shifts |
| player_id | DERIVED | Subject player |
| teammate_id | DERIVED | Teammate being analyzed |
| toi_with | CALC | `SUM(shift_duration WHERE both on ice)` |
| toi_without | CALC | `player_total_toi - toi_with` |
| toi_total | CALC | Player's total TOI in game |
| pct_with | CALC | `ROUND(toi_with / toi_total * 100, 1)` |

---

### fact_line_combos
**Source:** Calculated from fact_shifts_player  
**Purpose:** Line combination usage and performance

| Column | Source | Formula |
|--------|--------|---------|
| combo_key | KEY | `LC{game_id:05d}{players_hash:08d}` |
| game_id | DERIVED | From shifts |
| venue | DERIVED | 'home' or 'away' |
| player_ids | CALC | Comma-separated sorted player IDs |
| player_count | CALC | Number of players in combo |
| toi_seconds | CALC | `SUM(shift_duration)` for this exact combo |
| toi_minutes | CALC | `ROUND(toi_seconds / 60, 1)` |
| shift_count | CALC | Number of shifts with this exact combo |

---

### fact_gameroster
**Source:** BLB_Tables.xlsx → fact_gameroster sheet + is_sub calculation  
**Purpose:** Who played in each game with sub detection

| Column | Source | Formula |
|--------|--------|---------|
| roster_key | KEY | `R{game_id:05d}{player_hash:05d}` |
| game_id | BLB | Game identifier |
| player_id | BLB | Player FK |
| player_full_name | BLB | Player name |
| player_game_number | BLB | Jersey number for this game |
| team_id | BLB | Team FK |
| team_name | BLB | Team name |
| team_venue | BLB | 'home' or 'away' |
| season_id | BLB | Season FK |
| is_sub | CALC | `TRUE if (team_id, player_id) NOT IN fact_team_roster` |

---

## Validation Rules

### Goal Count Validation
**Ground Truth Source:** noradhockey.com official box scores

| game_id | Home Team | Home Goals | Away Team | Away Goals |
|---------|-----------|------------|-----------|------------|
| 18969 | Velodrome | 3 | Platinum | 4 |
| 18977 | HollowBrook | 2 | Velodrome | 4 |
| 18981 | Velodrome | 1 | Nelson | 2 |
| 18987 | Velodrome | 1 | Outlaws | 0 |

**ETL Validation:**
```python
calculated_goals = COUNT(fact_events_player 
    WHERE event_type='Goal' AND player_role='event_team_player_1')

assert calculated_goals == official_goals
```

### Column Preservation
The ETL preserves enhanced columns. When rebuilding:
- If existing file has 322 columns
- And new calculation produces 50 columns
- Merge on (game_id, player_id) to keep all 322
