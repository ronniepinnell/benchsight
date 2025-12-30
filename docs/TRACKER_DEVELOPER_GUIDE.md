# BenchSight Tracker UI Developer Guide
## Complete Specification for Event and Shift Tracking

**Version:** 1.0  
**Last Updated:** December 2025  
**Author:** BenchSight ETL Team

---

## Table of Contents
1. [Overview](#overview)
2. [Events Sheet Specification](#events-sheet-specification)
3. [Shifts Sheet Specification](#shifts-sheet-specification)
4. [Goal Detection Logic](#goal-detection-logic)
5. [Assist Detection Logic](#assist-detection-logic)
6. [Validation Rules](#validation-rules)
7. [Data Quality Checks](#data-quality-checks)

---

## Overview

The BenchSight ETL pipeline expects tracking data in two primary sheets:
- **events** - All game events (passes, shots, goals, turnovers, zone entries, etc.)
- **shifts** - All shift changes with player positions

### Critical Requirements
1. **Goals MUST be tracked correctly** - Verified against noradhockey.com official scores
2. **Assists MUST be tracked correctly** - Primary and Secondary assists in play_detail1
3. **Player numbers MUST match roster** - Cross-reference with BLB gameroster
4. **Each event needs a primary actor** - event_team_player_1 gets credit for the stat

---

## Events Sheet Specification

### Required Columns (MUST HAVE)

| Column | Type | Description | Example Values |
|--------|------|-------------|----------------|
| `event_index` | INT | Unique event ID within game (auto-increment) | 1, 2, 3, ... |
| `period` | INT | Period number | 1, 2, 3, OT |
| `event_start_min` | INT | Event start minute within period | 0-20 |
| `event_start_sec` | INT | Event start seconds | 0-59 |
| `event_end_min` | INT | Event end minute | 0-20 |
| `event_end_sec` | INT | Event end seconds | 0-59 |
| `player_game_number` | INT | Jersey number of PRIMARY player | 1-99 |
| `event_type` | STRING | Type of event (see Event Types) | Goal, Shot, Pass |
| `event_detail` | STRING | Detailed event outcome (see Event Details) | Goal_Scored, Shot_OnNetSaved |
| `event_detail_2` | STRING | Additional detail | ZoneEntry-Rush, Pass-Forehand |
| `event_successful` | STRING | Success indicator | s, u |
| `play_detail1` | STRING | Play-specific detail | AssistPrimary, Backcheck |
| `play_detail_2` | STRING | Secondary play detail | AssistSecondary |
| `play_detail_successful` | STRING | Play detail success | s, u |
| `event_team_zone` | STRING | Zone where event occurred | OZ, NZ, DZ |
| `team_venue` | STRING | Team executing event | home, away |
| `shift_index` | INT | Links to current shift | 1-100 |

### Event Types (event_type column)

| Event Type | Description | Requires |
|------------|-------------|----------|
| `Goal` | Puck enters net | player_game_number = scorer |
| `Shot` | Shot attempt | event_detail shows outcome |
| `Save` | Goalie save | Links to Shot event |
| `Pass` | Pass attempt | event_successful = s/u |
| `Faceoff` | Faceoff | event_successful = s (win) / u (loss) |
| `Turnover` | Puck lost | Giveaway or takeaway |
| `Zone_Entry_Exit` | Zone transition | event_detail_2 shows type |
| `Possession` | Puck possession | |
| `Stoppage` | Play stoppage | |
| `Penalty` | Penalty called | |
| `Rebound` | Rebound created | |

### Event Details (event_detail column)

| Category | event_detail Value | Description |
|----------|-------------------|-------------|
| **Goals** | `Goal_Scored` | Goal was scored |
| **Shots** | `Shot_OnNetSaved` | Shot saved by goalie |
| | `Shot_Goal` | Shot that scored (use with Goal event) |
| | `Shot_Blocked` | Shot blocked by skater |
| | `Shot_Missed` | Shot missed net |
| **Passes** | `Pass_Completed` | Successful pass |
| | `Pass_Missed` | Failed pass |
| **Zone** | `Zone_Entry` | Entered offensive zone |
| | `Zone_Exit` | Exited defensive zone |
| | `Zone_Keepin` | Kept puck in zone |
| **Turnovers** | `Turnover_Giveaway` | Lost possession |
| | `Turnover_Takeaway` | Gained possession |
| **Faceoffs** | `Faceoff_AfterStoppage` | Normal faceoff |
| | `Faceoff_AfterGoal` | Faceoff after goal |

### Event Detail 2 (event_detail_2 column)

| Category | Value | Description |
|----------|-------|-------------|
| **Zone Entries** | `ZoneEntry-Rush` | Controlled entry via rush |
| | `ZoneEntry-Pass` | Entry via pass |
| | `ZoneEntry-DumpIn` | Dump and chase |
| | `ZoneEntry-Chip` | Chip in |
| **Zone Exits** | `ZoneExit-Rush` | Exit via skating |
| | `ZoneExit-Pass` | Exit via pass |
| | `ZoneExit-Clear` | Clear the zone |
| **Shots** | `Shot-Wrist` | Wrist shot |
| | `Shot-Slap` | Slap shot |
| | `Shot-Snap` | Snap shot |
| | `Shot-Backhand` | Backhand shot |
| **Passes** | `Pass-Forehand` | Forehand pass |
| | `Pass-Backhand` | Backhand pass |
| | `Pass-Saucer` | Saucer pass |

---

## Shifts Sheet Specification

### Required Columns

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `shift_index` | INT | Unique shift ID (auto-increment) | 1, 2, 3, ... |
| `Period` | INT | Period number | 1, 2, 3 |
| `shift_start_min` | INT | Shift start minute | 0-20 |
| `shift_start_sec` | INT | Shift start seconds | 0-59 |
| `shift_end_min` | INT | Shift end minute | 0-20 |
| `shift_end_sec` | INT | Shift end seconds | 0-59 |
| `shift_start_type` | STRING | How shift started | Faceoff, OnTheFly, AfterGoal |
| `shift_stop_type` | STRING | How shift ended | Change, Whistle, Goal, Period |
| `home_forward_1` | INT | Home team forward 1 jersey # | 1-99 or blank |
| `home_forward_2` | INT | Home team forward 2 jersey # | |
| `home_forward_3` | INT | Home team forward 3 jersey # | |
| `home_defense_1` | INT | Home team defense 1 jersey # | |
| `home_defense_2` | INT | Home team defense 2 jersey # | |
| `home_xtra` | INT | Home extra attacker (empty net) | |
| `home_goalie` | INT | Home goalie jersey # | |
| `away_forward_1` | INT | Away team forward 1 jersey # | |
| `away_forward_2` | INT | Away team forward 2 jersey # | |
| `away_forward_3` | INT | Away team forward 3 jersey # | |
| `away_defense_1` | INT | Away team defense 1 jersey # | |
| `away_defense_2` | INT | Away team defense 2 jersey # | |
| `away_xtra` | INT | Away extra attacker | |
| `away_goalie` | INT | Away goalie jersey # | |

### Logical Shift Definition

A **logical shift** is a continuous on-ice presence for a player, NOT individual row changes:
- Player comes ON → Player goes OFF = 1 logical shift
- Multiple consecutive rows with same player = 1 logical shift
- Typical game: 10-15 logical shifts per skater, 1-3 for goalie

### Empty Net Tracking

When a team pulls their goalie:
- Set `home_goalie` or `away_goalie` to blank/0
- Set `home_xtra` or `away_xtra` to the extra skater's number
- **IMPORTANT**: Goals against during empty net should be flagged

---

## Goal Detection Logic

### How ETL Identifies Goals

```python
# Primary method: event_type = 'Goal'
goals = events[events['event_type'] == 'Goal']

# Verification: event_detail contains 'Goal'
# - 'Goal_Scored' = definite goal
# - 'Shot_Goal' = shot that resulted in goal

# The SCORER is the player_game_number on the Goal event
# with player_role = 'event_team_player_1'
```

### UI Tracker Requirements for Goals

1. **Create a Goal event** with:
   - `event_type` = 'Goal'
   - `event_detail` = 'Goal_Scored'
   - `player_game_number` = jersey # of SCORER
   - `team_venue` = 'home' or 'away' (scoring team)

2. **Verify with preceding Shot event**:
   - Shot event should have `event_detail` = 'Shot_Goal'
   - Same `player_game_number` as Goal event

3. **CRITICAL VALIDATION**:
   - After tracking, compare total goals to noradhockey.com
   - Game 18969: Platinum 4 - Velodrome 3 = 7 goals
   - If mismatch, review video and fix

---

## Assist Detection Logic

### How ETL Identifies Assists

```python
# Assists are in play_detail1 column on the Goal event row
# OR on separate event rows linked to the goal

# Primary Assist:
#   play_detail1 = 'AssistPrimary'
#   OR play_detail1 = 'OffensivePlay_Pass-AssistPrimary'

# Secondary Assist:
#   play_detail1 = 'AssistSecondary'  
#   OR play_detail1 = 'OffensivePlay_Pass-AssistSecondary'
#   OR play_detail_2 = 'AssistSecondary'
```

### UI Tracker Requirements for Assists

**CRITICAL: Assists are currently under-tracked!**

BLB shows 17 assists across 4 games, but tracking data only has 8.

For each goal, you MUST record assists:

1. **Option A: Same row as Goal event**
   - Add primary assist player # in a dedicated column
   - Add secondary assist player # in another column

2. **Option B: Separate event rows (PREFERRED)**
   - Create event with `event_type` = 'Pass' (the pass that led to goal)
   - Set `play_detail1` = 'AssistPrimary'
   - Set `player_game_number` = jersey # of PRIMARY ASSIST
   - Create another event for secondary assist with `play_detail1` = 'AssistSecondary'

3. **Linking to Goal**:
   - Use `linked_event_index` to link assist events to the Goal event
   - Assists should have same `shift_index` as the goal

### Example: Goal with Two Assists

```
event_index | event_type | player_game_number | play_detail1      | linked_event_index
------------|------------|-------------------|-------------------|-------------------
45          | Pass       | 12                | AssistPrimary     | 47
46          | Pass       | 8                 | AssistSecondary   | 47  
47          | Goal       | 21                |                   |
```

---

## Validation Rules

### Pre-Submission Checklist

Before submitting tracking data, verify:

- [ ] **Goal count matches noradhockey.com**
  - Check home_total_goals and away_total_goals
  - Each goal has a scorer identified
  
- [ ] **Assist count matches noradhockey.com (or BLB)**
  - Each goal should have 0-2 assists
  - Primary assist = last pass before goal
  - Secondary assist = second-to-last pass
  
- [ ] **All player numbers exist in roster**
  - Cross-reference with BLB gameroster
  - No invalid jersey numbers
  
- [ ] **Shifts are complete**
  - Every period has shift entries
  - All players accounted for
  - Goalie always present (unless pulled)

- [ ] **Events have valid types**
  - No blank event_type
  - event_detail matches event_type

### Post-ETL Validation

After running ETL, the system validates:

1. **Total Goals** = noradhockey.com official score ✅
2. **Player Goals** = BLB gameroster goals (95%+ match)
3. **Player Assists** = BLB gameroster assists (90%+ match)
4. **Goalie Stats** = 2 goalies per game
5. **Internal Consistency** = Points = Goals + Assists

---

## Data Quality Checks

### Automatic Error Detection

The ETL will flag these errors:

| Error Type | Description | Severity |
|------------|-------------|----------|
| `GOAL_COUNT_MISMATCH` | Goals ≠ official score | CRITICAL |
| `MISSING_ASSISTS` | Goal without assists when BLB shows assists | WARNING |
| `INVALID_PLAYER_NUMBER` | Jersey # not in roster | ERROR |
| `EMPTY_NET_GOAL` | Goal when goalie pulled (don't penalize goalie) | INFO |
| `DUPLICATE_EVENT` | Same event recorded twice | WARNING |
| `ORPHAN_ASSIST` | Assist not linked to goal | ERROR |
| `SHIFT_GAP` | Missing shift coverage | WARNING |

### Real-Time Validation in UI

The tracker UI should validate IN REAL-TIME:

```javascript
// When user enters a Goal event:
function validateGoal(goalEvent) {
  // Check scorer is valid player
  if (!isValidPlayerNumber(goalEvent.player_game_number)) {
    showError("Invalid scorer jersey number");
  }
  
  // Prompt for assists
  showPrompt("Enter primary assist (or leave blank for unassisted)");
  
  // Update running goal count
  updateGoalCount(goalEvent.team_venue);
  
  // Compare to expected (if known)
  if (runningGoalCount > expectedGoals) {
    showWarning("Goal count exceeds expected. Please verify.");
  }
}
```

---

## Summary for Developers

### Must-Have Features

1. **Goal Entry Form**
   - Scorer jersey number (required)
   - Primary assist jersey number (optional)
   - Secondary assist jersey number (optional)
   - Shot type
   - Auto-creates linked Goal + Assist events

2. **Running Score Display**
   - Show current home/away goals
   - Compare to expected final score (if pre-loaded)

3. **Roster Validation**
   - Load roster from BLB before game
   - Validate all jersey numbers against roster
   - Flag unknown numbers immediately

4. **Shift Tracking**
   - Track logical shifts (on-ice periods)
   - Flag empty net situations
   - Auto-calculate shift lengths

5. **Export Format**
   - Excel file with 'events' and 'shifts' sheets
   - Column names exactly as specified above
   - UTF-8 encoding

### Error Prevention

1. **No goal without verification**: Prompt "Is this goal confirmed?" 
2. **Assist reminders**: After goal, prompt "Any assists?"
3. **Period validation**: Warn if events outside period time
4. **Running totals**: Show stats in sidebar for sanity check
