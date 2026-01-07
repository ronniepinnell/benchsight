# BenchSight Tracker v3 - Complete Technical Specification

**Version:** 3.0  
**Date:** 2026-01-07  
**Status:** Specification for Implementation

---

## CRITICAL: ETL Format Requirements

### Events Tab Format (LONG - One Row Per Player Per Event)

The ETL expects events in **LONG FORMAT** - meaning each event generates MULTIPLE rows, one for each player involved.

```
Event #1002 with 3 players generates 3 rows:
Row 1: event_index=1002, player_role=event_team_player_1, player_game_number=42, ...
Row 2: event_index=1002, player_role=event_team_player_2, player_game_number=14, ...
Row 3: event_index=1002, player_role=opp_team_player_1, player_game_number=30, ...
```

### Required Events Tab Columns (73 columns)

```
# Index columns (tracking)
event_index_flag_           # 1 if this is event_player_1 row
sequence_index_flag_        # Sequence grouping
play_index_flag_            # Play grouping  
linked_event_index_flag_    # Linked event grouping

# Time columns
event_start_min_            # Start minute (countdown from 18/20)
event_start_sec_            # Start second
event_end_min_              # End minute
event_end_sec_              # End second

# Player columns (per row)
player_game_number_         # Jersey number
player_game_number          # Jersey number (duplicate)
player_num_dup_             # Duplicate check
role_abrev_binary_          # 'e' or 'o' (event/opp team)
role_abrev                  # 'e' or 'o'

# Zone columns
event_team_zone_            # o/n/d from event team perspective
event_team_zone2_           # Alternate zone
event_team_zone             # Final zone value
home_team_zone_             # Zone from home perspective
away_team_zone_             # Zone from away perspective
home_team_zone              # Final home zone
away_team_zone              # Final away zone

# Event columns
event_type_                 # Event type (Shot, Pass, etc.)
event_detail_               # Detail 1 (Shot_OnNetSaved, etc.)
event_detail_2_             # Detail 2 (Shot-Wrist, etc.)
event_successful_           # 's' or 'u' (successful/unsuccessful)
Type                        # Event type (copy)
event_detail                # Detail 1 (copy)
event_detail_2              # Detail 2 (copy)
event_successful            # s/u (copy)

# Play details (PER PLAYER - different for each row)
play_detail1_               # Offensive/defensive play type
play_detail2_               # Play detail 2
play_detail_successful_     # s/u for THIS PLAYER's play
play_detail1                # Copy
play_detail_2               # Copy
play_detail_successful      # Copy
pressured_pressurer_        # If player was pressured/pressurer
pressured_pressurer         # Copy

# Index columns (final)
event_index_                # Event index (internal)
linked_event_index_         # Linked event
sequence_index_             # Sequence index
play_index_                 # Play index
event_index                 # Event index (final) - FORMAT: {game_id}{4-digit-seq}
linked_event_index          # Linked event index
tracking_event_index        # Original tracking index
sequence_index              # Sequence index (final)
play_index                  # Play index (final)
zone_change_index           # Zone change tracking

# Team columns
team_                       # Team name
team_venue_                 # Home/Away
team_venue_abv_             # h/a
team_venue                  # Home/Away (final)
team_venue_abv              # h/a (final)
side_of_puck                # Offensive/Defensive/Neutral

# Game columns
game_id                     # Game ID
home_team                   # Home team name
away_team                   # Away team name
shift_index                 # Which shift this event belongs to

# Time calculations (ETL computes these)
duration                    # Event duration in seconds
time_start_total_seconds    # Total seconds from period start
time_end_total_seconds      # Total seconds from period start
running_intermission_duration  # Cumulative intermission time
period_start_total_running_seconds  # Video time at period start
running_video_time          # Running video timestamp
event_running_start         # Video time at event start
event_running_end           # Video time at event end

# Period
period                      # 1, 2, 3, OT

# Player identification
player_role                 # event_team_player_1, event_team_player_2, opp_team_player_1, etc.
role_number                 # 1, 2, 3, 4
player_id                   # Player ID (P######)
player_team                 # Player's team name
```

### Shifts Tab Format (WIDE - One Row Per Shift)

```
# Core columns
shift_index                 # Shift number
Period                      # 1, 2, 3, OT
shift_start_min             # Start minute
shift_start_sec             # Start second
shift_end_min               # End minute  
shift_end_sec               # End second
shift_start_type            # GameStart, PeriodStart, OtherFaceoff, etc.
shift_stop_type             # Period End, Stoppage, etc.

# Home players (jersey numbers)
home_forward_1
home_forward_2
home_forward_3
home_defense_1
home_defense_2
home_xtra
home_goalie

# Away players (jersey numbers)
away_forward_1
away_forward_2
away_forward_3
away_defense_1
away_defense_2
away_xtra
away_goalie

# Stoppage tracking
stoppage_time               # Time between shifts

# Zone tracking (per shift)
home_ozone_start            # 1 if shift started in home offensive zone
home_ozone_end              # 1 if shift ended in home offensive zone
home_dzone_start
home_dzone_end
home_nzone_start
home_nzone_end

# Game info
game_id
home_team
away_team

# Calculated fields (ETL computes)
shift_start_total_seconds
shift_end_total_seconds
shift_duration
home_team_strength          # 5, 4, 3
away_team_strength
home_team_en                # Empty net flag
away_team_en
home_team_pk                # Penalty kill flag
home_team_pp                # Power play flag
away_team_pp
away_team_pk
situation                   # "Full Strength", "Power Play", etc.
strength                    # "5v5", "5v4", etc.
home_goals                  # Score at shift start
away_goals

# Plus/minus per shift
home_team_plus
home_team_minus
away_team_plus
away_team_minus

# Video timing
period_start_total_running_seconds
running_video_time
shift_start_running_time
shift_end_running_time
```

---

## XY Data Format

XY data stored in separate CSV files:
- Location: `data/raw/games/{game_id}/xy/event_locations/{game_id}_{period}.csv`

Columns:
```
game_id                     # Game ID
link_event_index            # Event index to link to
Player                      # Jersey number
X, Y                        # Position 1
X2, Y2                      # Position 2
X3, Y3                      # Position 3
X4, Y4                      # Position 4 (up to 10)
...
X10, Y10                    # Position 10
Distance                    # Calculated distance
```

Puck positions stored separately or in same file with Player='puck':
```
game_id, link_event_index, Player='puck', X, Y, X2, Y2, ... X10, Y10
```

---

## Dropdown Options (From Lists Tab)

### Event Types
- Faceoff, Shot, Pass, Goal, Turnover, Zone_Entry_Exit, Penalty, PenaltyShot_Shootout
- Stoppage, Hit, Possession, LoosePuck, Save, TeamPossessionChange, Rebound
- DeadIce, Play, Timeout, Intermission, Clockstop

### Event Details (Cascading by Event Type)

**Shot:**
- Detail 1: Shot_OnNetSaved, Shot_Missed, Shot_Blocked, Shot_BlockedSameTeam, Shot_Deflected, Shot_DeflectedOnNetSaved, Shot_Tipped, Shot_TippedOnNetSaved, Shot_OnNetGoal, Shot_OnNetTippedGoal, Shot_OnNetDeflectedGoal, Shot_Goal, Shot_MissedPost
- Detail 2: Shot-Wrist, Shot-Slap, Shot-Backhand, Shot-Snap, Shot-WrapAround, Shot-Bat, Shot-Cradle, Shot-Poke, Shot-BetweenLegs, Shot-Dumpin, Shot-OneTime, Shot-Tip, Shot-Deflection, Shot-Other

**Pass:**
- Detail 1: Pass_Completed, Pass_Missed, Pass_Deflected, Pass_Intercepted
- Detail 2: Pass-Stretch, Pass-Rim/Wrap, Pass-Backhand, Pass-Forehand, Pass-Bank, Pass-Dump, Pass-Tipped, Pass-Lob, Pass-Drop, Pass-Deflected/TippedShot, Pass-ReceiverMissed, Pass-OneTouch, Pass-SecondTouch, Pass-QuickUp, Pass-GiveAndGo, Pass-Reverse, Pass-Other

**Goal:**
- Detail 1: Goal_Scored, Goal_Shootout, Goal_PenaltyShot
- Detail 2: Goal-Wrist, Goal-Slap, Goal-Backhand, Goal-Tip, Goal-Snap, Goal-WrapAround, Goal-Bat, Goal-Cradle, Goal-Poke, Goal-BetweenLegs, Goal-Dumpin, Goal-Deflection, Goal-OneTime, Goal-Other

**Turnover:**
- Detail 1: Turnover_Giveaway, Turnover_Takeaway
- Detail 2 (Giveaway): Giveaway-Misplayed, Giveaway-BattleLost, Giveaway-PassIntercepted, Giveaway-PassMissed, Giveaway-PassBlocked, Giveaway-PassReceiverMissed, Giveaway-ShotBlocked, Giveaway-ShotMissed, Giveaway-ZoneClear/Dump, Giveaway-AttemptedZoneClear/Dump, Giveaway-ZoneEntry/ExitMisplay, Giveaway-DumpInZone, Giveaway-Other
- Detail 2 (Takeaway): Takeaway-BattleWon, Takeaway-PokeCheck, Takeaway-PassIntercepted, Takeaway-PassBlocked, Takeaway-ShotBlocked, Takeaway-ZoneClear/Dump, Takeaway-AttemptedZoneClear/Dump, Takeaway-Other

**Zone_Entry_Exit:**
- Detail 1: Zone_Entry, Zone_Exit, Zone_Keepin, Zone_Entryfailed, Zone_ExitFailed, Zone_KeepinFailed
- Detail 2 (Entry): ZoneEntry-Rush, ZoneEntry-Pass, ZoneEntry-DumpIn, ZoneEntry-Chip, ZoneEntry-FromExitClear, ZoneEntry-PassMiss/Misplay, ZoneEntry-OppTeam, ZoneEntry-Lob, ZoneEntry-RushBreakaway, ZoneEntry-CausedTurnover, ZoneEntry-PenaltyKillClear, ZoneEntry-Shot, ZoneEntry-Other
- Detail 2 (Exit): ZoneExit-Rush, ZoneExit-Pass, ZoneExit-Clear, ZoneExit-Chip, ZoneExit-PassMiss/Misplay, ZoneExit-OppTeam, ZoneExit-Lob, ZoneExit-CausedTurnover, ZoneExit-PenaltyKillClear, ZoneExit-Shot, ZoneExit-Other
- Detail 2 (Keepin): Zone-KeepIn, Zone-Pinch, Zone-Other

**Faceoff:**
- Detail 1: Faceoff_AfterPenalty, Faceoff_AfterGoal, Faceoff_PeriodStart, Faceoff_AfterStoppage, Faceoff_GameStart

**Save:**
- Detail 1: Save_Rebound, Save_Freeze, Save_Played
- Detail 2: Save-Glove, Save-Blocker, Save-LeftPad, Save-RightPad, Save-Stick, Save-Scramble, Save-Butterfly, Save-Chest, Save-Shoulder, Save-Skate, Save-Other

**Stoppage:**
- Detail 1: Stoppage_Period, Stoppage_Play, Stoppage_Other, Stoppage_GameEnd
- Detail 2 (Play): Stoppage-Icing, Stoppage-Offsides, Stoppage-ClockProblem, Stoppage-HighStick, Stoppage-HandPass, Stoppage-NetDislodged, Stoppage-Injury, Stoppage-GoalieStoppage, Stoppage-PuckOutofPlay, Stoppage-Penalty, Stoppage-Goal
- Detail 2 (Period): Stoppage-StartofShootout, Stoppage-PeriodStart, Stoppage-PeriodEnd
- Detail 2 (Other): Stoppage-ObjectsonIce, Stoppage-HomeTimeout, Stoppage-VisitorTimeout, Stoppage-RinkRepair, Stoppage-PlayerEquipment, Stoppage-Challenge, Stoppage-Other

**Penalty:**
- Detail 1: Penalty_Minor, Penalty_Major, Penalty_Offsetting
- Detail 2: Penalty-Bench Penalty, Penalty-Boarding, Penalty-Charging, Penalty-CrossChecking, Penalty-DelayofGame, Penalty-Diving, Penalty-Elbowing, Penalty-GoalieInterference, Penalty-HighSticking, Penalty-Holding, Penalty-Interference, Penalty-Fighting, Penalty-Hooking, Penalty-Roughing, Penalty-Slashing, Penalty-Misconduct, Penalty-TooManyMenontheIce, Penalty-Tripping, Penalty-UnsportsmanlikeConduct, Penalty-Other

**Possession:**
- Detail 1: Breakaway, PuckRetrieval, PuckRecovery, Regroup

**Rebound:**
- Detail 1: Rebound_TeamRecovered, Rebound_OppTeamRecovered, Rebound_ShotGenerated, Rebound_FlurryGenerated

**LoosePuck:**
- Detail 1: LoosePuck_Forecheck, LoosePuck_Battle

**Play:**
- Detail 1: Play_Offensive, Play_Defensive
- Detail 2 (Offensive): Play-DriveMiddle, Play-DriveWide, Play-DriveCorner, Play-DriveNetMiddle, Play-DriveNetWide, Play-CrashNet, Play-Delay, Play-Deke, Play-Chip, Play-Other, Play-DumpChase, Play-Forecheck, Play-Speed, Play-Dump/RimInZone
- Detail 2 (Defensive): Play-PokeCheck, Play-PokeCheckFailed, Play-SeperateFromPuck, Play-Backcheck, Play-FroceWide, Play-Contain, Play-BeatMiddle, Play-BeatWide, Play-BeatDeke, Play-BeatSpeed, Play-BoxOut, Play-AttemptedClear, Play-Other

### Shift Start Types
- PeriodStart, FaceoffAfterGoal, GameStart, FaceoffAfterPenalty, OtherFaceoff, DeadIce/Stoppage, Intermission, DelayedPenalty

### Shift Stop Types  
- (Derived from events - linked to stoppage/goal/period end events)

---

## Play Details (PER PLAYER)

Each player in an event can have their own play details:

### Offensive Play Details (play_detail1 when offensive)
- Play-DriveMiddle, Play-DriveWide, Play-DriveCorner, Play-DriveNetMiddle, Play-DriveNetWide
- Play-CrashNet, Play-Delay, Play-Deke, Play-Chip, Play-DumpChase, Play-Forecheck, Play-Speed
- Play-Dump/RimInZone, Play-Other

### Defensive Play Details (play_detail1 when defensive)
- Play-PokeCheck, Play-PokeCheckFailed, Play-SeperateFromPuck, Play-Backcheck
- Play-FroceWide, Play-Contain, Play-BeatMiddle, Play-BeatWide, Play-BeatDeke
- Play-BeatSpeed, Play-BoxOut, Play-AttemptedClear, Play-Other

### Success/Unsuccessful
- `s` = successful
- `u` = unsuccessful

Applied to:
- `event_successful_` (overall event)
- `play_detail_successful_` (per player's play)

---

## Zone Calculation

Zone is determined by event_player_1's XY position:

```
Rink coordinates: x from -100 to +100, y from -42.5 to +42.5

For HOME team (defending left goal, attacking right):
  x < -25  → Zone = 'd' (defensive)
  x > +25  → Zone = 'o' (offensive)
  else     → Zone = 'n' (neutral)

For AWAY team (defending right goal, attacking left):
  x < -25  → Zone = 'o' (offensive)
  x > +25  → Zone = 'd' (defensive)
  else     → Zone = 'n' (neutral)
```

---

## Intermission Handling

Intermissions are special shift entries:
- `shift_start_type = 'Intermission'`
- All player slots empty
- Duration entered in seconds
- Affects `running_intermission_duration` calculation for video sync

---

## Data Flow

1. **User Input (Tracker)**
   - Events entered in UI-friendly format
   - Players added to event with roles
   - XY positions clicked on rink
   - Play details selected per player

2. **Internal Storage (JSON/localStorage)**
   - Events stored in intermediate format
   - One object per event with nested player array

3. **Export (Excel)**
   - Events expanded to LONG format (one row per player)
   - Shifts exported in WIDE format
   - XY data exported to separate CSV files

4. **ETL Processing**
   - Reads Excel files in expected format
   - Calculates derived fields
   - Loads to database tables

---

## Rink SVG Corrections

Current issues:
1. Goal lines should be at x = ±89 (not at edge)
2. Goal creases are semi-circles in front of goal
3. Goal nets are 6 feet wide (in rink scale: ~6 units)

Correct rink proportions (NHL standard, scaled to 200x85):
- Rink: 200 ft x 85 ft → viewBox: -100 to +100, -42.5 to +42.5
- Goal lines: x = ±89
- Blue lines: x = ±25
- Center line: x = 0
- Goal crease: 6 ft radius semicircle at goal line
- Faceoff circles: 15 ft radius at (±69, ±22)
- Center circle: 15 ft radius at (0, 0)

---

## UI Requirements Summary

1. **Time Auto-fill**: New shift/event start = previous end time
2. **Intermission**: Dropdown + duration input
3. **Play Details**: Per-player entry with s/u
4. **Zone Auto-fill**: Based on event_player_1 XY
5. **Full Editing**: All fields editable for events and shifts
6. **Cascading Dropdowns**: event_type → detail_1 → detail_2
7. **XY**: Up to 10 points per player, 10 puck points per event
8. **Long Format Export**: Events expand to one row per player
9. **Scrollable Logs**: Both events and shifts with quick navigation
10. **Dropdown Options**: All from dim tables (or Lists tab)
