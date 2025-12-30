# BenchSight Game Tracker - Complete Developer Guide

## Overview

This guide provides everything needed to develop the BenchSight game tracker interface. It includes event logic, validation lists, linking patterns for predictive suggestions, XY coordinate requirements, and ETL integration instructions.

---

## Table of Contents

1. [Event Types & Validation Lists](#1-event-types--validation-lists)
2. [Event Detail Hierarchies](#2-event-detail-hierarchies)
3. [Event Linking Patterns (For Predictions)](#3-event-linking-patterns-for-predictions)
4. [Shift Data Structure](#4-shift-data-structure)
5. [XY Coordinate Requirements](#5-xy-coordinate-requirements)
6. [Player Role Logic](#6-player-role-logic)
7. [Adding Games to ETL](#7-adding-games-to-etl)
8. [Folder Structure](#8-folder-structure)
9. [Data Validation Rules](#9-data-validation-rules)

---

## 1. Event Types & Validation Lists

### Primary Event Types (event_type_ column)
```
Faceoff              - Puck drop to start/resume play
Shot                 - Any shot attempt (on goal, blocked, missed)
Pass                 - Puck transfer between teammates
Goal                 - Puck crosses goal line (also tracked as Shot with detail)
Turnover             - Loss of puck possession (Giveaway/Takeaway)
Zone_Entry_Exit      - Puck crosses blue line
Penalty              - Infraction called
PenaltyShot_Shootout - Penalty shot or shootout attempt
Stoppage             - Play stoppage (whistle)
Hit                  - Body check
Possession           - Player gains control of puck
LoosePuck            - Contested puck (no clear possession)
Save                 - Goalie stop
TeamPossessionChange - Possession switches teams
Rebound              - Puck loose after save
DeadIce              - No play (between whistle and faceoff)
Play                 - Offensive/Defensive play classification
Timeout              - Team timeout
Intermission         - Period break
Clockstop            - Clock stoppage
GameStart            - Game begins
GameEnd              - Game ends
Penalty_Delayed      - Delayed penalty call
Zone_Change          - Zone transition marker
```

### Success Indicator (event_successful_ column)
```
s = Successful (pass completed, shot on goal, zone entry maintained)
u = Unsuccessful (pass incomplete, shot missed/blocked, entry failed)
```

---

## 2. Event Detail Hierarchies

### Shot Details (event_detail_)
```
SHOT OUTCOMES:
Shot_OnNetSaved        - Shot on goal, saved by goalie
Shot_Missed            - Shot missed the net entirely
Shot_Blocked           - Shot blocked by defending player
Shot_BlockedSameTeam   - Shot blocked by teammate
Shot_Deflected         - Shot deflected (not on net)
Shot_DeflectedOnNet    - Shot deflected, went on net
Shot_Tipped            - Shot tipped (not on net)
Shot_TippedOnNetSaved  - Tipped shot saved
Shot_OnNetGoal         - Shot on net = GOAL
Shot_OnNetTippedGoal   - Tipped shot = GOAL
Shot_OnNetDeflectedGoal- Deflected shot = GOAL
Shot_Goal              - Direct goal
Shot_MissedPost        - Hit post/crossbar

SHOT TYPES (event_detail_2_):
Shot-Wrist, Shot-Slap, Shot-Backhand, Shot-Snap, Shot-WrapAround
Shot-Bat, Shot-Cradle, Shot-Poke, Shot-BetweenLegs, Shot-Tip, Shot-Other
Shot-Deflection, Shot-Dumpin, Shot-OneTime
```

### Save Details (event_detail_2_)
```
SAVE LOCATION:
Save-Glove, Save-Blocker, Save-LeftPad, Save-RightPad
Save-Stick, Save-Scramble, Save-Butterfly, Save-Chest
Save-Shoulder, Save-Skate, Save-Other

SAVE RESULT (event_detail_):
Save_Rebound   - Save resulted in rebound
Save_Freeze    - Goalie covered/froze puck
Save_Played    - Save played to corner/boards
```

### Pass Details (event_detail_)
```
PASS OUTCOMES:
Pass_Completed    - Successful pass
Pass_Missed       - Pass missed target
Pass_Deflected    - Pass deflected
Pass_Intercepted  - Pass intercepted by opponent

PASS TYPES (event_detail_2_):
Pass-Stretch, Pass-Rim/Wrap, Pass-Backhand, Pass-Forehand
Pass-Bank, Pass-Dump, Pass-Tipped, Pass-Lob, Pass-Drop
Pass-Deflected/TippedShot, Pass-ReceiverMissed, Pass-OneTouch
Pass-SecondTouch, Pass-QuickUp, Pass-GiveAndGo, Pass-Reverse, Pass-Other
```

### Turnover Details (event_detail_)
```
GIVEAWAYS (team loses puck):
Giveaway-Misplayed, Giveaway-BattleLost, Giveaway-PassIntercepted
Giveaway-PassMissed, Giveaway-PassBlocked, Giveaway-PassReceiverMissed
Giveaway-ShotBlocked, Giveaway-ShotMissed, Giveaway-ZoneClear/Dump
Giveaway-AttemptedZoneClear/Dump, Giveaway-ZoneEntry/ExitMisplay
Giveaway-DumpInZone, Giveaway-Other

TAKEAWAYS (team gains puck):
Takeaway-BattleWon, Takeaway-PokeCheck, Takeaway-PassIntercepted
Takeaway-PassBlocked, Takeaway-ShotBlocked, Takeaway-ZoneClear/Dump
Takeaway-AttemptedZoneClear/Dump, Takeaway-Other
```

### Zone Entry/Exit Details (event_detail_2_)
```
ZONE ENTRY TYPES:
ZoneEntry-Rush          - Controlled carry into zone
ZoneEntry-Pass          - Pass into zone
ZoneEntry-DumpIn        - Dump and chase
ZoneEntry-Chip          - Chip puck in
ZoneEntry-FromExitClear - Entry from opponent's clearing attempt
ZoneEntry-PassMiss/Misplay
ZoneEntry-OppTeam       - Opponent caused entry
ZoneEntry-Lob, ZoneEntry-RushBreakaway
ZoneEntry-CausedTurnover, ZoneEntry-PenaltyKillClear, ZoneEntry-Other

ZONE EXIT TYPES:
ZoneExit-Rush, ZoneExit-Pass, ZoneExit-Clear, ZoneExit-Chip
ZoneExit-PassMiss/Misplay, ZoneExit-OppTeam, ZoneExit-Lob
ZoneExit-CausedTurnover, ZoneExit-PenaltyKillClear, ZoneExit-Other

ZONE KEEPIN:
Zone-KeepIn, Zone-Pinch, Zone-KeepinFailed, Zone-Other
```

### Faceoff Details (event_detail_)
```
Faceoff_GameStart, Faceoff_AfterGoal, Faceoff_PeriodStart
Faceoff_AfterPenalty, Faceoff_AfterStoppage
```

### Stoppage Details (event_detail_)
```
STOPPAGE TYPES:
Stoppage_Period, Stoppage_Play, Stoppage_Other, Stoppage_GameEnd

STOPPAGE REASONS (shift_stop_type column):
Period Start, Period End, Puck Out of Play, Injury
Home Penalty, Away Penalty, Home Goalie Stoppage, Away Goalie Stoppage
Home Offside, Away Offside, Home Icing, Away Icing
Clock Problem, Puck Frozen, Puck in Crowd, Puck in Netting, Puck in Benches
Goalie Stopped (after SOG), Referee or Linesperson, High Stick
Objects on Ice, Hand Pass, Premature Substitution, Skater Puck Frozen
Net Dislodged Offensive Skater, TV timeout, Home Timeout, Visitor Timeout
Player Injury, Official Injury, Rink Repair, Ice problem, Player Equipment
Video Review, Home Goal, Away Goal, DeadIce/Stoppage, Offset Penalty, GameEnd
```

### Play Details (play_detail1_ column)
```
OFFENSIVE PLAYS:
AssistPrimary, AssistSecondary, AssistTertiary (for goal attribution)
AttemptedBlockedShot, AttemptedBreakOutClear, AttemptedBreakOutPass
AttemptedBreakOutRush, AttemptedEntryDumpIn, AttemptedEntryPass
AttemptedEntryRush, AttemptedKeepin, AttemptedPass, AttemptedShot
AttemptedTip/Deflection, Backcheck, BeatDeke, BeatFake, BeatMiddle
BeatSpeed, BeatWide, BlockedShot, BoxOut, Breakout, CededZoneEntry
CededZoneExit, Chip, ClearingAttempt, Contain, CrashNet, CutBack
Cycle, DeflectedShot, Deke, Delay, DelayedOffside, DriveCorner
DriveMiddle, DriveNetMiddle, DriveNetWide, DriveWide, Dump/RimInZone
DumpChase, DumpInAttempt, EndToEndRush, FakeShot, ForcedDumpin/Clear
ForcedLostPossession, ForcedMissedPass, ForcedMissedShot, ForcedTurnover
ForceWide, Forecheck, ForecedOutside, FrontofNet, GapControl, GiveAndGo
InShotPassLane, LoosePuckBattleLost, LoosePuckBattleWon, LostPuck
ManOnMan, MisplayedPuck, OpenIceDeke, Other, PassDeflected, PassForTip
PassIntercepted, PenaltyKillClear, PokeCheck, Pressure, QuickUp
ReceiverMissed, Regroup, RegroupClear, RegroupDumpin, Reverse
SeperateFromPuck, Speed, StickCheck, StoppedDeke, Surf, Tracker
Wheel, Zone, ZoneEntryDenial, ZoneExitDenial, ZoneKeepin
```

---

## 3. Event Linking Patterns (For Predictions)

### High-Confidence Predictions (ALWAYS suggest)

| Current Event | Next Event | Confidence | Notes |
|--------------|------------|------------|-------|
| Stoppage → | DeadIce | 100% | Always follows stoppage |
| DeadIce → | Faceoff | 100% | Always follows dead ice |
| Goal → | Stoppage | 100% | Play stops after goal |
| Penalty → | Stoppage | 95% | Usually stops play |
| Save_Freeze → | Stoppage | 95% | Goalie freezes = whistle |

### Medium-Confidence Predictions (SUGGEST as primary option)

| Current Event | Next Event | Confidence | Notes |
|--------------|------------|------------|-------|
| Shot → | Save | 70% | Most shots are saved |
| Save_Rebound → | Rebound | 90% | Rebound event follows |
| Rebound → | Possession | 60% | Someone gets the puck |
| Rebound → | Shot | 30% | Quick second shot |
| Faceoff → | Possession | 50% | Winner gains possession |
| Faceoff → | Pass | 25% | Clean win to pass |
| Zone_Entry (success) → | Possession | 60% | Entry = possession |
| Zone_Entry (success) → | Pass | 30% | Entry leads to pass |
| Zone_Entry (fail) → | Turnover | 80% | Failed entry = turnover |
| Turnover → | Possession | 60% | Opponent gains control |
| Turnover → | Zone_Entry_Exit | 25% | Leads to zone change |

### Event Transition Matrix (from actual data analysis)

```
TOP 30 MOST COMMON TRANSITIONS:
225x  Possession → Pass           (Possession usually leads to pass)
135x  Turnover → Possession       (After turnover, new team has puck)
109x  Zone_Entry_Exit → Possession (After entry, control the puck)
108x  Pass → Possession           (After pass, receiver has puck)
106x  Possession → Zone_Entry_Exit (With puck, advance zones)
 82x  Pass → Zone_Entry_Exit      (Pass into new zone)
 60x  Possession → Shot           (Control leads to shot)
 58x  Shot → Save                 (Most shots saved)
 55x  Zone_Entry_Exit → Turnover  (Entry contested, puck lost)
 54x  Pass → Turnover             (Pass intercepted/missed)
 44x  Possession → Turnover       (Lost the puck)
 44x  Stoppage → DeadIce          (Whistle = dead ice)
 42x  DeadIce → Faceoff           (Dead ice = faceoff)
 39x  Save → Rebound              (Save creates rebound)
 37x  Rebound → Possession        (Rebound recovered)
 36x  Zone_Entry_Exit → Pass      (Enter zone, make pass)
 34x  Turnover → Zone_Entry_Exit  (Turnover leads to zone change)
 26x  Zone_Entry_Exit → Shot      (Entry leads to shot)
 23x  Pass → Pass                 (Quick passing)
 22x  Shot → Possession           (Shot recovered)
 22x  Pass → Shot                 (Pass for shot)
 21x  Faceoff → Possession        (Faceoff won = possession)
 19x  Zone_Entry_Exit → Zone_Entry_Exit (Quick zone changes)
 19x  Save → Stoppage             (Freeze/whistle)
 18x  Play → Possession           (Play leads to possession)
```

### Linked Event Index Usage

The `linked_event_index` column connects related events:

```
ASSIST LINKING:
- When recording AssistPrimary/AssistSecondary in play_detail1_
- linked_event_index points to the Goal event

SHOT-SAVE CHAINS:
- Save event's linked_event_index points to the Shot event
- Allows tracking shot → save → rebound → shot sequences

TURNOVER CHAINS:
- Giveaway linked to subsequent Takeaway
- Tracks possession changes
```

### Prediction Algorithm Pseudocode

```javascript
function suggestNextEvent(currentEvent) {
  const suggestions = [];
  
  // Always-true rules
  if (currentEvent.type === 'Stoppage') {
    return [{ type: 'DeadIce', confidence: 1.0 }];
  }
  if (currentEvent.type === 'DeadIce') {
    return [{ type: 'Faceoff', confidence: 1.0 }];
  }
  if (currentEvent.type === 'Goal') {
    return [{ type: 'Stoppage', confidence: 1.0, detail: 'Stoppage-Goal' }];
  }
  
  // Shot outcomes
  if (currentEvent.type === 'Shot') {
    suggestions.push({ type: 'Save', confidence: 0.7 });
    suggestions.push({ type: 'Possession', confidence: 0.15 }); // blocked/missed
    suggestions.push({ type: 'Goal', confidence: 0.10 });
    suggestions.push({ type: 'Turnover', confidence: 0.05 });
  }
  
  // Save outcomes
  if (currentEvent.type === 'Save') {
    if (currentEvent.detail === 'Save_Freeze') {
      return [{ type: 'Stoppage', confidence: 0.95 }];
    }
    suggestions.push({ type: 'Rebound', confidence: 0.65 });
    suggestions.push({ type: 'Stoppage', confidence: 0.30 });
    suggestions.push({ type: 'Possession', confidence: 0.05 });
  }
  
  // Rebound outcomes
  if (currentEvent.type === 'Rebound') {
    suggestions.push({ type: 'Possession', confidence: 0.50 });
    suggestions.push({ type: 'Shot', confidence: 0.35 });
    suggestions.push({ type: 'Turnover', confidence: 0.15 });
  }
  
  // Possession outcomes
  if (currentEvent.type === 'Possession') {
    suggestions.push({ type: 'Pass', confidence: 0.50 });
    suggestions.push({ type: 'Zone_Entry_Exit', confidence: 0.25 });
    suggestions.push({ type: 'Shot', confidence: 0.15 });
    suggestions.push({ type: 'Turnover', confidence: 0.10 });
  }
  
  // Pass outcomes
  if (currentEvent.type === 'Pass') {
    if (currentEvent.successful === 's') {
      suggestions.push({ type: 'Possession', confidence: 0.40 });
      suggestions.push({ type: 'Zone_Entry_Exit', confidence: 0.30 });
      suggestions.push({ type: 'Shot', confidence: 0.20 });
      suggestions.push({ type: 'Pass', confidence: 0.10 });
    } else {
      suggestions.push({ type: 'Turnover', confidence: 0.70 });
      suggestions.push({ type: 'Possession', confidence: 0.30 });
    }
  }
  
  // Zone entry outcomes
  if (currentEvent.type === 'Zone_Entry_Exit') {
    if (currentEvent.successful === 's') {
      suggestions.push({ type: 'Possession', confidence: 0.45 });
      suggestions.push({ type: 'Pass', confidence: 0.30 });
      suggestions.push({ type: 'Shot', confidence: 0.15 });
      suggestions.push({ type: 'Play', confidence: 0.10 });
    } else {
      suggestions.push({ type: 'Turnover', confidence: 0.80 });
      suggestions.push({ type: 'Zone_Entry_Exit', confidence: 0.20 });
    }
  }
  
  // Turnover outcomes
  if (currentEvent.type === 'Turnover') {
    suggestions.push({ type: 'Possession', confidence: 0.55 });
    suggestions.push({ type: 'Zone_Entry_Exit', confidence: 0.25 });
    suggestions.push({ type: 'Pass', confidence: 0.15 });
    suggestions.push({ type: 'LoosePuck', confidence: 0.05 });
  }
  
  // Faceoff outcomes
  if (currentEvent.type === 'Faceoff') {
    suggestions.push({ type: 'Possession', confidence: 0.50 });
    suggestions.push({ type: 'Pass', confidence: 0.25 });
    suggestions.push({ type: 'Zone_Entry_Exit', confidence: 0.15 });
    suggestions.push({ type: 'Turnover', confidence: 0.10 });
  }
  
  return suggestions.sort((a, b) => b.confidence - a.confidence);
}
```

---

## 4. Shift Data Structure

### Shift Columns

```
IDENTIFIERS:
shift_index       - Unique shift number within game (1, 2, 3...)
Period            - Period number (1, 2, 3, OT)
game_id           - Game identifier

TIMING:
shift_start_min, shift_start_sec  - Start time (countdown clock)
shift_end_min, shift_end_sec      - End time (countdown clock)
shift_start_total_seconds         - Start in total game seconds
shift_end_total_seconds           - End in total game seconds
shift_duration                    - Length in seconds

SHIFT BOUNDARIES:
shift_start_type  - What started the shift (GameStart, OtherFaceoff, etc.)
shift_stop_type   - What ended the shift (reason for whistle)
stoppage_time     - Duration of stoppage (seconds)

HOME PLAYERS ON ICE:
home_forward_1, home_forward_2, home_forward_3  - Forward jersey numbers
home_defense_1, home_defense_2                   - Defense jersey numbers
home_xtra                                        - Extra attacker (if any)
home_goalie                                      - Goalie jersey number

AWAY PLAYERS ON ICE:
away_forward_1, away_forward_2, away_forward_3
away_defense_1, away_defense_2
away_xtra
away_goalie

GAME STATE:
home_team_strength, away_team_strength  - Number of skaters (5, 4, 3)
home_team_en, away_team_en              - Empty net flags (1 = pulled goalie)
home_team_pk, home_team_pp              - Penalty kill/power play flags
away_team_pk, away_team_pp
situation                                - Full Strength, Power Play, etc.
strength                                 - 5v5, 5v4, 4v5, 4v4, etc.

SCORE:
home_goals, away_goals                  - Running score

ZONE TIME:
home_ozone_start, home_ozone_end        - Offensive zone time
home_dzone_start, home_dzone_end        - Defensive zone time
home_nzone_start, home_nzone_end        - Neutral zone time
```

---

## 5. XY Coordinate Requirements

### Coordinate System

```
RINK DIMENSIONS (standard NHL):
- Length: 200 feet (0 to 200)
- Width: 85 feet (0 to 85)

COORDINATE ORIGIN:
- (0, 0) = Bottom-left corner of rink
- X increases left to right (along length)
- Y increases bottom to top (along width)

KEY LOCATIONS:
- Center ice: (100, 42.5)
- Home goal line: x = 11 (or x = 189 depending on period)
- Away goal line: x = 189 (or x = 11 depending on period)
- Blue lines: x = 75 and x = 125
- Goal crease center: (11, 42.5) and (189, 42.5)
```

### Required XY Data Points

#### Per Event:
```javascript
{
  event_index: 1001,
  puck_x: 145.5,        // Puck X coordinate
  puck_y: 38.2,         // Puck Y coordinate
  puck_zone: 'ozone',   // Derived: ozone, dzone, nzone
  puck_slot: true,      // Is puck in slot area?
  shot_distance: 22.5,  // For shots: distance to goal
  shot_angle: 15.3,     // For shots: angle to goal center
}
```

#### Per Player (on-ice at event time):
```javascript
{
  player_id: 'P100192',
  player_x: 140.0,
  player_y: 35.0,
  player_zone: 'ozone',
  distance_to_puck: 8.5,
  distance_to_net: 30.2,
}
```

### XY Data File Format

Create `{game_id}_xy.csv` or include in events sheet:

```csv
event_index,puck_x,puck_y,player_id,player_x,player_y
1001,145.5,38.2,P100192,140.0,35.0
1001,145.5,38.2,P100025,138.5,45.0
1001,145.5,38.2,P100001,175.0,42.5
...
```

### Zone Definitions

```javascript
function getZone(x, teamVenue, period) {
  // Adjust for period (teams switch sides)
  const homeAttacksRight = (period % 2 === 1);
  
  if (x < 75) {
    return homeAttacksRight 
      ? (teamVenue === 'Home' ? 'dzone' : 'ozone')
      : (teamVenue === 'Home' ? 'ozone' : 'dzone');
  } else if (x > 125) {
    return homeAttacksRight
      ? (teamVenue === 'Home' ? 'ozone' : 'dzone')
      : (teamVenue === 'Home' ? 'dzone' : 'ozone');
  }
  return 'nzone';
}
```

### Shot Quality Zones

```javascript
const SHOT_ZONES = {
  // High danger (slot)
  HIGH_DANGER: { xMin: 0, xMax: 30, yMin: 22, yMax: 63 },
  
  // Medium danger (circles)
  MEDIUM_DANGER_LEFT: { xMin: 20, xMax: 50, yMin: 0, yMax: 25 },
  MEDIUM_DANGER_RIGHT: { xMin: 20, xMax: 50, yMin: 60, yMax: 85 },
  
  // Low danger (point/perimeter)
  LOW_DANGER: { xMin: 50, xMax: 75 }
};

function getShotDanger(x, y) {
  const distFromGoal = Math.sqrt(x*x + (y-42.5)**2);
  if (distFromGoal < 25 && Math.abs(y - 42.5) < 20) return 'high';
  if (distFromGoal < 45) return 'medium';
  return 'low';
}
```

---

## 6. Player Role Logic

### CRITICAL: Player Role Determines Stat Credit

```
event_team_player_1 = PRIMARY ACTOR
  - Gets credit for: shots, goals, faceoff wins, passes, zone entries
  - This is the player who performed the action

opp_team_player_1 = OPPONENT ACTOR  
  - Gets credit for: faceoff losses, defensive plays
  - This is the opposing player involved

event_team_player_2 through event_team_player_6 = SUPPORTING PLAYERS
  - On ice but not primary actor
  - Used for H2H/WOWY calculations

opp_team_player_2 through opp_team_player_6 = OPPONENT SUPPORTING
  - Opposing players on ice
```

### Role Assignment Example

```javascript
// Faceoff
{
  event_type: 'Faceoff',
  event_team_player_1: 53,  // WINNER (gets fo_wins stat)
  opp_team_player_1: 70,    // LOSER (gets fo_losses stat)
}

// Shot
{
  event_type: 'Shot',
  event_team_player_1: 21,  // SHOOTER (gets shots stat)
  // Other players are just on-ice
}

// Goal with Assist
{
  event_type: 'Goal',
  event_team_player_1: 21,  // SCORER (gets goals stat)
  play_detail1: null,
}
// Separate assist event:
{
  event_type: 'Pass',  // or similar
  event_team_player_1: 12,  // ASSISTER
  play_detail1: 'AssistPrimary',
  linked_event_index: [goal_event_index]
}
```

---

## 7. Adding Games to ETL

### Step 1: Create Game Folder

```
data/raw/games/{game_id}/
├── {game_id}_tracking.xlsx    # REQUIRED: Main tracking file
├── {game_id}_video_times.xlsx # OPTIONAL: Video sync data
├── roster.json                # OPTIONAL: Pre-loaded roster
├── xy/                        # OPTIONAL: XY coordinate files
│   └── {game_id}_xy.csv
├── events/                    # OPTIONAL: Pre-processed events
├── shots/                     # OPTIONAL: Shot charts
└── !info.rtf                  # OPTIONAL: Game notes
```

### Step 2: Tracking File Structure

The `{game_id}_tracking.xlsx` must contain these sheets:

```
REQUIRED SHEETS:
- events        # All game events
- shifts        # All shift data
- game_rosters  # Player roster for the game

OPTIONAL SHEETS:
- Rules         # Event type rules
- Lists         # Validation dropdown lists
- examples      # Example data
```

### Step 3: Run ETL Pipeline

```bash
# Full ETL run
python etl.py

# Or step by step:
python etl.py                    # Transform raw to output
python scripts/fix_data_integrity.py  # Fix keys/FKs
python scripts/fix_final_data.py      # Final cleanup
python scripts/etl_validation.py      # Validate
pytest tests/                          # Run tests
```

### Step 4: Updating Existing Games

To update a game that's already been processed:

```bash
# 1. Update the tracking file in data/raw/games/{game_id}/

# 2. Re-run ETL (it will overwrite existing output)
python etl.py

# 3. Re-run data integrity fixes
python scripts/fix_data_integrity.py

# 4. Re-validate
python scripts/etl_validation.py
```

### Step 5: Upload to Supabase

```bash
python upload.py  # Uploads all CSV files to Supabase
```

---

## 8. Folder Structure

```
benchsight/
├── etl.py                    # Main ETL pipeline
├── upload.py                 # Supabase uploader
├── requirements.txt          # Python dependencies
│
├── data/
│   ├── raw/
│   │   └── games/
│   │       ├── 18969/        # One folder per game
│   │       │   ├── 18969_tracking.xlsx
│   │       │   ├── roster.json
│   │       │   └── xy/
│   │       ├── 18977/
│   │       └── ...
│   │
│   └── output/               # ETL output (CSV files)
│       ├── dim_player.csv
│       ├── dim_team.csv
│       ├── dim_schedule.csv
│       ├── fact_events.csv
│       ├── fact_events_player.csv
│       ├── fact_shifts.csv
│       ├── fact_shifts_player.csv
│       ├── fact_player_game_stats.csv
│       ├── fact_team_game_stats.csv
│       ├── fact_goalie_game_stats.csv
│       ├── fact_h2h.csv
│       ├── fact_wowy.csv
│       └── data_dictionary/
│
├── src/                      # ETL source modules
│   ├── loaders.py
│   ├── transforms.py
│   └── validators.py
│
├── scripts/                  # Utility scripts
│   ├── fix_data_integrity.py
│   ├── fix_final_data.py
│   ├── etl_validation.py
│   └── generate_data_dictionary.py
│
├── tracker/                  # Game tracker HTML files
│   └── tracker_v19.html
│
├── config/                   # Configuration files
│   └── supabase_config.json
│
└── tests/                    # Test files
    └── test_etl.py
```

---

## 9. Data Validation Rules

### Required Fields by Event Type

```javascript
const REQUIRED_FIELDS = {
  'Faceoff': ['event_team_player_1', 'opp_team_player_1', 'event_detail'],
  'Shot': ['event_team_player_1', 'event_detail', 'event_detail_2'],
  'Pass': ['event_team_player_1', 'event_successful'],
  'Goal': ['event_team_player_1'],
  'Save': ['event_detail', 'event_detail_2'],  // result + location
  'Zone_Entry_Exit': ['event_team_player_1', 'event_detail', 'event_successful'],
  'Turnover': ['event_team_player_1', 'event_detail'],
  'Penalty': ['event_team_player_1', 'event_detail'],
};
```

### Value Ranges

```javascript
const VALUE_RANGES = {
  period: [1, 2, 3, 4],  // 4 = OT
  player_game_number: [1, 99],
  event_start_min: [0, 20],  // 20 for overtime
  event_start_sec: [0, 59],
  shift_duration: [1, 300],  // Max 5 minutes
};
```

### Cross-Validation Rules

```javascript
const CROSS_VALIDATION = [
  // Faceoff winner/loser must be different teams
  { rule: 'faceoff_teams_differ', 
    check: (e) => e.event_team_player_1_team !== e.opp_team_player_1_team },
  
  // Goals must have corresponding save (except empty net)
  { rule: 'goal_has_preceding_shot',
    check: (events, goalEvent) => {
      const prevEvent = events.find(e => e.event_index === goalEvent.event_index - 1);
      return prevEvent?.event_type === 'Shot' || goalEvent.empty_net;
    }},
  
  // Assists must link to goal
  { rule: 'assist_links_to_goal',
    check: (e) => !e.play_detail1?.includes('Assist') || e.linked_event_index },
];
```

---

## Quick Reference Card

### Most Common Event Sequences

```
GOAL SEQUENCE:
Possession → Pass(s) → Pass(AssistPrimary) → Shot(Goal) → Stoppage → DeadIce → Faceoff

SAVE SEQUENCE:
Possession → Shot(OnNet) → Save(Rebound) → Rebound → [Possession|Shot|Stoppage]

TURNOVER SEQUENCE:
Possession → Pass(u) → Turnover(Giveaway) → Possession(other team)

ZONE ENTRY SEQUENCE:
Zone_Entry_Exit(Entry,s) → Possession → [Pass|Shot|Turnover]
Zone_Entry_Exit(Entry,u) → Turnover → Possession(other team)

PERIOD START:
GameStart/Intermission → DeadIce → Faceoff(PeriodStart) → Possession
```

### Keyboard Shortcuts (Suggested)

```
F = Faceoff         S = Shot          P = Pass
G = Goal            V = Save          T = Turnover
Z = Zone Entry      D = DeadIce       X = Stoppage
R = Rebound         H = Hit           O = Possession
1-6 = Player 1-6    Tab = Next field  Enter = Save event
```

---

*Document Version: 1.0 | Last Updated: December 2024*
