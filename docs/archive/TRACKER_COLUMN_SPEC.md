# BenchSight Tracker Column Specification
## Exact Format Required for ETL Pipeline

**Version:** 1.0  
**Date:** December 2025

---

## File Structure

The tracker Excel file must contain these sheets:
1. `events` - All game events
2. `shifts` - All shift changes
3. `game_rosters` - Player roster (optional, can come from BLB)

---

## EVENTS SHEET - Required Columns

| Column Name | Data Type | Required | Description | Valid Values |
|-------------|-----------|----------|-------------|--------------|
| `event_index` | INT | ✅ | Unique event ID (auto-increment) | 1, 2, 3, ... |
| `period` | INT | ✅ | Period number | 1, 2, 3, 4 (OT) |
| `event_start_min` | INT | ✅ | Start minute within period | 0-20 |
| `event_start_sec` | INT | ✅ | Start seconds | 0-59 |
| `event_end_min` | INT | ✅ | End minute | 0-20 |
| `event_end_sec` | INT | ✅ | End seconds | 0-59 |
| `player_game_number` | INT | ✅ | Jersey # of PRIMARY player | 1-99 |
| `event_type` | STRING | ✅ | Event type | See Event Types |
| `event_detail` | STRING | ✅ | Event outcome | See Event Details |
| `event_detail_2` | STRING | | Additional detail | See Event Detail 2 |
| `event_successful` | STRING | | Success indicator | s, u |
| `play_detail1` | STRING | **✅ for assists** | Play-specific detail | AssistPrimary, AssistSecondary |
| `play_detail_2` | STRING | | Secondary play detail | |
| `play_detail_successful` | STRING | | Play detail success | s, u |
| `event_team_zone` | STRING | | Zone of event | OZ, NZ, DZ |
| `team_venue` | STRING | ✅ | Team executing event | home, away |
| `shift_index` | INT | ✅ | Current shift number | Links to shifts sheet |
| `linked_event_index` | INT | | Links related events | For assists → goals |

### Event Types (event_type column)

```
Goal              - Puck enters net (scorer in player_game_number)
Shot              - Shot attempt
Save              - Goalie save
Pass              - Pass attempt
Faceoff           - Faceoff (s=win, u=loss)
Turnover          - Puck lost/gained
Zone_Entry_Exit   - Zone transition
Possession        - Puck possession
Stoppage          - Play stoppage
Penalty           - Penalty called
Rebound           - Rebound created
Play              - General play
DeadIce           - Puck out of play
Intermission      - Period break
GameStart         - Game start
GameEnd           - Game end
```

### Event Details (event_detail column)

```
# Goals
Goal_Scored           - Confirmed goal

# Shots
Shot_OnNetSaved       - Shot saved by goalie
Shot_Goal             - Shot that scored
Shot_Blocked          - Shot blocked by skater
Shot_Missed           - Shot missed net
Shot_OnNetTippedGoal  - Tipped shot that scored

# Passes
Pass_Completed        - Successful pass
Pass_Missed           - Failed pass

# Zone
Zone_Entry            - Entered offensive zone
Zone_Exit             - Exited defensive zone
Zone_Keepin           - Kept puck in zone
Zone_Entryfailed      - Failed zone entry
Zone_ExitFailed       - Failed zone exit

# Turnovers
Turnover_Giveaway     - Lost possession
Turnover_Takeaway     - Gained possession

# Faceoffs
Faceoff_AfterStoppage - Normal faceoff
Faceoff_AfterGoal     - Faceoff after goal

# Saves
Save_Rebound          - Save with rebound
Save_Freeze           - Save frozen puck

# Puck
PuckRecovery          - Recovered loose puck
PuckRetrieval         - Retrieved puck
```

### Event Detail 2 (event_detail_2 column)

```
# Zone Entries
ZoneEntry-Rush              - Controlled entry via skating
ZoneEntry-Pass              - Entry via pass
ZoneEntry-DumpIn            - Dump and chase
ZoneEntry-Chip              - Chip entry
ZoneEntry-FromExitClear     - Entry from defensive clear
ZoneEntry-RushBreakaway     - Breakaway entry

# Zone Exits
ZoneExit-Rush               - Exit via skating
ZoneExit-Pass               - Exit via pass
ZoneExit-Clear              - Clear the zone
ZoneExit-Chip               - Chip out
ZoneExit-Lob                - Lob out

# Shots
Shot-Wrist                  - Wrist shot
Shot-Slap                   - Slap shot
Shot-Snap                   - Snap shot
Shot-Backhand               - Backhand shot
Shot-Tip                    - Tip/deflection

# Passes
Pass-Forehand               - Forehand pass
Pass-Backhand               - Backhand pass
Pass-Saucer                 - Saucer pass
Pass-Rim/Wrap               - Rim/wrap pass

# Turnovers
Giveaway-PassMissed         - Giveaway via bad pass
Giveaway-ZoneClear/Dump     - Giveaway via dump
Takeaway-PokeCheck          - Takeaway via poke check
Takeaway-StickCheck         - Takeaway via stick check

# Zone
Zone-KeepIn                 - Puck kept in zone
Zone-Pinch                  - Defensive pinch
```

### Play Details (play_detail1, play_detail_2 columns)

```
# ASSISTS - CRITICAL FOR PROPER TRACKING
AssistPrimary                      - Primary assist (last pass before goal)
AssistSecondary                    - Secondary assist (2nd to last pass)
OffensivePlay_Pass-AssistPrimary   - Primary assist via pass play
OffensivePlay_Pass-AssistSecondary - Secondary assist via pass play

# Defensive Plays
Backcheck                          - Backcheck play
PokeCheck                          - Poke check
StickCheck                         - Stick check
BlockedShot                        - Blocked a shot
InShotPassLane                     - In shooting/passing lane
Contain                            - Contained player
Pressure                           - Applied pressure

# Offensive Plays
Deke                               - Deke attempt
Screen                             - Screened goalie
CrashNet                           - Crashed the net
DriveMiddle                        - Drive to middle
DriveWide                          - Drive wide
Cycle                              - Cycle play
Forecheck                          - Forecheck play

# Zone Plays
Breakout                           - Breakout play
ZoneEntryDenial                    - Denied zone entry
ZoneKeepin                         - Kept puck in zone
DumpChase                          - Dump and chase

# Puck Battles
LoosePuckBattleWon                 - Won loose puck battle
LoosePuckBattleLost                - Lost loose puck battle
PuckRecovery                       - Recovered puck
```

---

## SHIFTS SHEET - Required Columns

| Column Name | Data Type | Required | Description | Valid Values |
|-------------|-----------|----------|-------------|--------------|
| `shift_index` | INT | ✅ | Unique shift ID | 1, 2, 3, ... |
| `Period` | INT | ✅ | Period number | 1, 2, 3, 4 |
| `shift_start_min` | INT | ✅ | Start minute | 0-20 |
| `shift_start_sec` | INT | ✅ | Start seconds | 0-59 |
| `shift_end_min` | INT | ✅ | End minute | 0-20 |
| `shift_end_sec` | INT | ✅ | End seconds | 0-59 |
| `shift_start_type` | STRING | | How shift started | Faceoff, OnTheFly, AfterGoal |
| `shift_stop_type` | STRING | | How shift ended | Change, Whistle, Goal, Period |
| `home_forward_1` | INT | ✅ | Home F1 jersey # | 1-99 or blank |
| `home_forward_2` | INT | | Home F2 jersey # | |
| `home_forward_3` | INT | | Home F3 jersey # | |
| `home_defense_1` | INT | ✅ | Home D1 jersey # | |
| `home_defense_2` | INT | | Home D2 jersey # | |
| `home_xtra` | INT | | Home extra attacker | For empty net |
| `home_goalie` | INT | ✅ | Home goalie jersey # | Blank = pulled |
| `away_forward_1` | INT | ✅ | Away F1 jersey # | |
| `away_forward_2` | INT | | Away F2 jersey # | |
| `away_forward_3` | INT | | Away F3 jersey # | |
| `away_defense_1` | INT | ✅ | Away D1 jersey # | |
| `away_defense_2` | INT | | Away D2 jersey # | |
| `away_xtra` | INT | | Away extra attacker | For empty net |
| `away_goalie` | INT | ✅ | Away goalie jersey # | Blank = pulled |

---

## GOAL TRACKING REQUIREMENTS

### For Each Goal, You MUST Track:

1. **Goal Event**
   - `event_type` = 'Goal'
   - `event_detail` = 'Goal_Scored'
   - `player_game_number` = scorer's jersey #
   - `team_venue` = 'home' or 'away'

2. **Preceding Shot Event** (same event_index or linked)
   - `event_type` = 'Shot'
   - `event_detail` = 'Shot_Goal'
   - Same `player_game_number` as goal

3. **Primary Assist** (if any)
   - Separate event OR same row
   - `play_detail1` = 'AssistPrimary'
   - `player_game_number` = assist player's jersey #
   - `linked_event_index` = goal's event_index

4. **Secondary Assist** (if any)
   - Separate event
   - `play_detail1` = 'AssistSecondary'
   - `player_game_number` = assist player's jersey #
   - `linked_event_index` = goal's event_index

### Example: Goal with Two Assists

```
event_index | event_type | player_game_number | event_detail | play_detail1     | linked_event_index
------------|------------|-------------------|--------------|------------------|-------------------
101         | Pass       | 12                | Pass_Completed| AssistPrimary    | 103
102         | Pass       | 8                 | Pass_Completed| AssistSecondary  | 103
103         | Goal       | 21                | Goal_Scored  |                  |
```

---

## VALIDATION AFTER TRACKING

### Must-Check Items

1. **Goal Count**
   ```
   COUNT(event_type = 'Goal') should equal noradhockey.com final score
   ```

2. **Assist Count**
   ```
   COUNT(play_detail1 CONTAINS 'Assist') should roughly match BLB
   ```

3. **All Jersey Numbers Valid**
   ```
   Every player_game_number should exist in game roster
   ```

4. **Shift Coverage**
   ```
   No time gaps in shifts
   Goalie always present (unless pulled)
   ```

5. **Event-Shift Linkage**
   ```
   Every event has valid shift_index
   ```

---

## COMMON ERRORS TO AVOID

| Error | Consequence | Prevention |
|-------|-------------|------------|
| Missing assists | Under-counted assists | Always add assist events for goals |
| Wrong jersey # | Stats credited to wrong player | Verify against roster |
| Missing Goal event | Under-counted goals | Check vs official score |
| No shift_index | Events can't link to shifts | Always fill shift_index |
| Wrong team_venue | Stats credited to wrong team | Verify home/away |
| Duplicate events | Over-counted stats | Check for duplicates |
| Goalie not tracked | Missing goalie stats | Always include goalie in shifts |
