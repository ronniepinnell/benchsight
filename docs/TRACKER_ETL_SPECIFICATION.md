# BenchSight Tracker - ETL Input Specification

**Version:** 1.0  
**Date:** 2026-01-07  
**Purpose:** EXACT specification for tracker output that ETL expects

---

## CRITICAL: Export Format Requirements

The tracker MUST export Excel files with these EXACT sheet names and column structures.
The ETL will compute calculated fields - tracker only provides INPUT fields.

---

## Sheet 1: `events` (LONG FORMAT)

**Format:** One row PER PLAYER PER EVENT

If event has 3 players, it generates 3 rows with same event_index.

### Input Columns (Tracker Provides)

```
# Flag columns
event_index_flag_           # 1 for first player row (event_player_1), 0 for others
sequence_index_flag_        # Optional grouping
play_index_flag_            # Optional grouping
linked_event_index_flag_    # For linked events

# Time (from game clock - countdown format like 17:45)
event_start_min_            # Start minute (17 from "17:45")
event_start_sec_            # Start second (45 from "17:45")
event_end_min_              # End minute
event_end_sec_              # End second

# Player (changes per row)
player_game_number_         # Jersey number for THIS row's player
player_game_number          # Jersey number (duplicate)

# Zone
event_team_zone_            # 'o', 'n', or 'd' from event team perspective

# Event type & details (SAME for all rows of same event)
event_type_                 # Faceoff, Shot, Pass, Goal, etc.
event_detail_               # Shot_OnNetSaved, Pass_Completed, etc.
event_detail_2_             # Shot-Wrist, Pass-Forehand, etc.
event_successful_           # 's' or 'u'

# Play details (DIFFERENT per player row)
play_detail1_               # This player's offensive/defensive play
play_detail2_               # Play detail 2
play_detail_successful_     # 's' or 'u' for THIS player
pressured_pressurer_        # 'pressured' or 'pressurer' or blank

# Index tracking
event_index_                # Sequential event number (1, 2, 3...)
linked_event_index_         # Index of linked event (for Shot→Save chains)
sequence_index_             # Sequence grouping
play_index_                 # Play grouping

# Team (changes based on player role)
team_                       # 'h' or 'a' for THIS row's player's team
role_abrev_binary_          # 'e' or 'o' (event team or opposing)
role_abrev                  # 'e' or 'o'

# Venue
team_venue_                 # 'Home' or 'Away' for this player
team_venue_abv_             # 'h' or 'a'

# Zones from different perspectives
event_team_zone2_           # Copy of zone
home_team_zone_             # Zone from home team perspective
away_team_zone_             # Zone from away team perspective

# Game info
game_id                     # Game ID (18977)
home_team                   # Home team name
away_team                   # Away team name

# Event type copies
Type                        # Same as event_type_
event_detail                # Same as event_detail_
event_detail_2              # Same as event_detail_2_

# Shift link
shift_index                 # Which shift this event belongs to

# Player identification
player_role                 # event_team_player_1, event_team_player_2, opp_team_player_1, etc.
role_number                 # 1, 2, 3, 4 (player number within role type)
player_id                   # Player ID (P100084)
player_team                 # This player's team name
```

### Calculated by ETL (Don't include or leave blank)

```
event_index                 # Formatted as game_id * 10000 + event_index_
tracking_event_index        # Copy of event_index
period                      # (Actually INPUT - include this!)
event_start_min             # Copies of the underscore versions
event_start_sec
event_end_min
event_end_sec
event_team_zone             # Copy
home_team_zone              # Calculated
away_team_zone              # Calculated
team_venue                  # Copy
team_venue_abv              # Copy
side_of_puck                # Calculated from zone
sequence_index              # Copy
play_index                  # Copy
play_detail1                # Copy
play_detail_2               # Copy
play_detail_successful      # Copy
pressured_pressurer         # Copy
zone_change_index           # Calculated
duration                    # Calculated
time_start_total_seconds    # Calculated from period + time
time_end_total_seconds      # Calculated
running_intermission_duration  # Calculated
period_start_total_running_seconds  # Calculated
running_video_time          # Calculated
event_running_start         # Calculated
event_running_end           # Calculated
player_num_dup_             # Calculated
event_successful            # Copy (sometimes different logic)
linked_event_index          # Copy
```

---

## Sheet 2: `shifts` (WIDE FORMAT)

**Format:** One row PER SHIFT

### Input Columns (Tracker Provides)

```
# Core
shift_index                 # Sequential (1, 2, 3...)
Period                      # 1, 2, 3, OT

# Time (countdown format)
shift_start_min             # Start minute
shift_start_sec             # Start second
shift_end_min               # End minute
shift_end_sec               # End second

# Start/Stop types
shift_start_type            # GameStart, PeriodStart, OtherFaceoff, etc.
shift_stop_type             # Period End, Home Goal, Away Goalie Stopped, etc.

# Home lineup (jersey numbers)
home_forward_1
home_forward_2
home_forward_3
home_defense_1
home_defense_2
home_xtra                   # Extra attacker
home_goalie

# Away lineup (jersey numbers)
away_forward_1
away_forward_2
away_forward_3
away_defense_1
away_defense_2
away_xtra
away_goalie

# Stoppage
stoppage_time               # Duration of stoppage in seconds

# Zone tracking (1 if true, blank if false)
home_ozone_start            # Shift started in home offensive zone
home_ozone_end              # Shift ended in home offensive zone
home_dzone_start
home_dzone_end
home_nzone_start
home_nzone_end

# Game info
game_id
home_team
away_team
```

### Calculated by ETL

```
shift_start_total_seconds   # From period + time
shift_end_total_seconds
shift_duration              # End - start
home_team_strength          # Count of home skaters
away_team_strength          # Count of away skaters
home_team_en                # Empty net flag
away_team_en
home_team_pk                # Penalty kill flag
home_team_pp                # Power play flag
away_team_pp
away_team_pk
situation                   # "Full Strength", "Power Play", etc.
strength                    # "5v5", "5v4", etc.
home_goals                  # Current score
away_goals
home_team_plus              # Plus/minus
home_team_minus
away_team_plus
away_team_minus
period_start_total_running_seconds
running_video_time
shift_start_running_time
shift_end_running_time
```

---

## Sheet 3: `game_rosters` (Optional, for validation)

Links player numbers to player IDs.

---

## XY Data

XY data stored SEPARATELY in CSV files:

**Location:** `data/raw/games/{game_id}/xy/event_locations/{game_id}_{period}.csv`

### Columns

```
game_id
link_event_index            # Links to event_index
Player                      # Jersey number OR 'puck'
X                           # Position 1 X coordinate
Y                           # Position 1 Y coordinate
X2                          # Position 2 X coordinate (if multiple positions)
Y2
X3
Y3
... up to X10, Y10
Distance                    # Calculated distance traveled
```

---

## Shift Start Types (from dim table)

```
GameStart
PeriodStart
FaceoffAfterGoal
FaceoffAfterPenalty
OtherFaceoff
DeadIce/Stoppage
Intermission
DelayedPenalty
```

## Shift Stop Types (from dim table)

```
Period End
Period Start (for intermission)
Home Goal
Away Goal
Home Goalie Stopped (after Away SOG)
Away Goalie Stopped (after Home SOG)
Home Penalty
Away Penalty
Home Offside
Away Offside
Home Icing
Away Icing
Puck Out of Play
DeadIce/Stoppage
TV timeout
Home Timeout
Visitor Timeout
Player Injury
GameEnd
... (and many more - see Lists tab)
```

---

## Event Types

```
Faceoff
Shot
Pass
Goal
Turnover
Zone_Entry_Exit
Penalty
PenaltyShot_Shootout
Stoppage
Hit
Possession
LoosePuck
Save
TeamPossessionChange
Rebound
DeadIce
Play
Timeout
Intermission
Clockstop
GameStart
GameEnd
```

---

## Cascading Detail Dropdowns

### Shot → Detail 1 → Detail 2
```
Shot:
  Shot_OnNetSaved → Shot-Wrist, Shot-Slap, Shot-Backhand, Shot-Snap, Shot-Tip, etc.
  Shot_Missed → Same shot types
  Shot_Blocked → Same shot types
  Shot_Goal → Same shot types
```

### Pass → Detail 1 → Detail 2
```
Pass:
  Pass_Completed → Pass-Forehand, Pass-Backhand, Pass-Saucer, Pass-Stretch, etc.
  Pass_Missed → Same pass types
  Pass_Intercepted → Same pass types
```

### Turnover → Detail 1 → Detail 2
```
Turnover:
  Turnover_Giveaway → Giveaway-Misplayed, Giveaway-BattleLost, etc.
  Turnover_Takeaway → Takeaway-PokeCheck, Takeaway-BattleWon, etc.
```

---

## Player Roles

```
event_team_player_1         # Primary player for event team
event_team_player_2         # Second player for event team
event_team_player_3
event_team_player_4

opp_team_player_1           # Primary opposing player
opp_team_player_2
opp_team_player_3
opp_team_player_4
```

---

## Success/Unsuccessful Logic

`event_successful_` and `play_detail_successful_` use:
- `s` = successful
- `u` = unsuccessful

Applied logic:
- Shot_OnNetSaved: Usually 's' (shot was on target)
- Shot_Missed: 'u'
- Pass_Completed: 's'
- Pass_Intercepted: 'u'
- Turnover_Giveaway: 'u' (for team that gave it away)
- Turnover_Takeaway: 's' (for team that took it away)

Play details have their own s/u per player.

---

## Zone Calculation

Based on event_team_player_1's first XY position:

```
Rink coordinates: X from -100 to +100

For HOME team events:
  X > 25  → zone = 'o' (offensive - attacking right)
  X < -25 → zone = 'd' (defensive - defending left)
  else    → zone = 'n' (neutral)

For AWAY team events:
  X < -25 → zone = 'o' (offensive - attacking left)
  X > 25  → zone = 'd' (defensive - defending right)
  else    → zone = 'n' (neutral)
```

---

## Intermission Handling

Intermissions are special shifts where:
- `shift_start_type = 'Intermission'`
- All player slots are EMPTY
- `stoppage_time` contains duration in seconds
- Critical for video timestamp calculations

---

## Time Format

All times are in COUNTDOWN format (like NHL game clock):
- Period starts at 18:00 (or 20:00 for NHL)
- Counts down to 0:00
- Example: "15:42" means 15 minutes 42 seconds remaining

Total seconds calculation:
```
period_seconds = (period - 1) * 18 * 60  # For 18-min periods
time_from_period_start = (18 * 60) - (minutes * 60 + seconds)
total_seconds = period_seconds + time_from_period_start
```

---

## Video Time Calculation

```
running_video_time = time_from_game_start + total_intermission_duration

Where:
- time_from_game_start = total_seconds
- total_intermission_duration = sum of all intermission stoppage_time values up to this point
```
