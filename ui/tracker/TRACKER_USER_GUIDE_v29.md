# BenchSight Tracker User Guide v29.1

## Table of Contents
1. [Quick Start](#1-quick-start)
2. [Event Entry](#2-event-entry)
3. [Command Bar](#3-command-bar)
4. [Auto-Events](#4-auto-events)
5. [Shortcuts](#5-shortcuts)
6. [Derived Fields](#6-derived-fields)
7. [Export](#7-export)

---

## 1. Quick Start

### Game Tracking Workflow

1. **Load Video** - Use + button or drag file
2. **Set Markers** - P1 start at puck drop
3. **Track Events** - Type → XY → Enter
4. **Export** - Download Excel

### Key Modes

| Mode | Description |
|------|-------------|
| **Shot Mode** | Click rink to quickly log shots |
| **Possession Mode** | Track continuous possession chains |
| **Sequence Mode** | Auto-link consecutive events |
| **Mirror Mode** | Auto-flip XY for period 2 |
| **Auto Zone** | Set zone from click position |
| **Auto Goalie** | Add opposing goalie on shots/saves |

### Speed Tips

- Use **Command Bar** for fastest entry: `h S 17 on wr`
- Press **Shift+Enter** for quick log (no confirmation)
- Use **Quick Chains**: Entry, Dump, Shot+, Break, PP buttons
- Press **K** to link to last event

---

## 2. Event Entry

### Event Types & Details (from DIM tables)

| Type | Detail1 Options | Detail2 Options |
|------|-----------------|-----------------|
| **Shot** | Shot_OnNetSaved, Shot_Missed, Shot_Blocked, Shot_Goal | Shot_Wrist, Shot_Slap, Shot_Backhand, Shot_Snap, Shot_OneTime, Shot_Tip |
| **Pass** | Pass_Completed, Pass_Missed, Pass_Intercepted, Pass_Deflected | Pass_Stretch, Pass_Rim, Pass_Backhand, Pass_Forehand, Pass_Drop, Pass_Dump |
| **Goal** | Goal_Scored, Goal_OwnGoal | Goal_Wrist, Goal_Slap, Goal_Backhand, Goal_Tip, Goal_OneTime |
| **Save** | Save_Played, Save_Freeze, Save_Rebound | Save_Glove, Save_Blocker, Save_Pad, Save_Stick, Save_Butterfly |
| **Faceoff** | Faceoff, Faceoff_AfterGoal, Faceoff_AfterPenalty, Faceoff_GameStart, Faceoff_PeriodStart | - |
| **Stoppage** | Stoppage_Freeze, Stoppage_GameEnd, Stoppage_Goal, Stoppage_OutOfPlay, Stoppage_Penalty, Stoppage_PeriodEnd, Stoppage_Play | - |
| **Penalty** | Penalty_Minor, Penalty_Major, Penalty_Misconduct | Penalty_Tripping, Penalty_Hooking, Penalty_Slashing, etc. |
| **Zone** | Zone_Entry, Zone_Entry_Failed, Zone_Exit, Zone_Exit_Failed, Zone_Keepin, Zone_Keepin_Failed | - |
| **Rebound** | Rebound_TeamRecovered, Rebound_OppTeamRecovered, Rebound_ShotGenerated, Rebound_FlurryGenerated | - |
| **DeadIce** | *(no detail1)* | - |

### Click Method

1. Select **Event Type** button (or press hotkey: S, P, G, etc.)
2. Select **Team** (H/A buttons or h/a key)
3. Choose **Detail1** from dropdown
4. Click **rink** to set puck XY
5. Add **players** from shift slots or roster
6. Press **Enter** to log

### Player Roles

| Role | Description |
|------|-------------|
| **event_player_1** | Primary actor (shooter, passer, faceoff winner) |
| **event_player_2-6** | Supporting players (assist, screen) |
| **opp_player_1** | Primary opponent (goalie, defender, faceoff loser) |
| **opp_player_2-6** | Other opponents involved |

---

## 3. Command Bar

### Syntax (v29.1 Enhanced)

```
[h/a] [EventCode] [Jersey#] [detail1] [detail2] [more jerseys] | [opp jerseys]
```

### Event Codes

| Code | Event Type |
|------|------------|
| `S` | Shot |
| `P` | Pass |
| `G` | Goal |
| `V` | Save |
| `F` | Faceoff |
| `T` | Turnover |
| `Z` | Zone |
| `N` | Penalty |
| `X` | Stoppage |
| `R` | Rebound |
| `D` | DeadIce |

### Detail1 Shortcuts

| Shortcut | Meaning |
|----------|---------|
| `on` | OnNetSaved |
| `m` | Missed |
| `bl` | Blocked |
| `c` | Completed |
| `int` | Intercepted |
| `w` | Won (Faceoff) |
| `l` | Lost (Faceoff) |
| `en` | Entry |
| `ex` | Exit |

### Detail2 Shortcuts

| Type | Shortcuts |
|------|-----------|
| Shot/Goal | `wr`=Wrist, `sl`=Slap, `bh`=Backhand, `sn`=Snap, `ot`=OneTime, `tp`=Tip |
| Pass | `st`=Stretch, `ri`=Rim, `bh`=Backhand, `fh`=Forehand, `dr`=Drop, `du`=Dump |
| Save | `gl`=Glove, `bl`=Blocker, `pd`=Pad, `sk`=Stick, `bf`=Butterfly |
| Penalty | `tr`=Tripping, `hk`=Hooking, `sl`=Slashing, `hi`=HighStick, `in`=Interference |

### Examples

| Command | Result |
|---------|--------|
| `h S 17 on wr` | Home Shot #17 OnNetSaved Wrist |
| `a P 9 c st 22` | Away Pass #9 Completed Stretch to #22 |
| `h G 17 \| 30` | Home Goal #17, goalie #30 |
| `F 5 w \| 11` | Faceoff #5 Won vs #11 |
| `a N 8 mi tr` | Away Penalty #8 Minor Tripping |

**Note:** Pipe `|` separates event players from opponent players

---

## 4. Auto-Events

### Auto-Event Chains (v29.1)

The tracker automatically creates or suggests follow-up events based on what you log.

| Chain | Trigger | Auto-Created | 1-Click Confirm |
|-------|---------|--------------|-----------------|
| **A1** | Shot_OnNetSaved | - | Save (with goalie from slots) |
| **A2** | Save | - | Next event options |
| **A3** | Zone_Entry | - | Possession event |
| **A4** | Faceoff_GameStart | GameStart event | - |
| **A5** | Period change | Stoppage_PeriodEnd | - |
| **A6** | Goal | Stoppage_Goal | Faceoff_AfterGoal (center ice) |
| **A7** | Penalty | Stoppage_Penalty | Faceoff_AfterPenalty (off zone) |
| **A8** | Save_Rebound | - | Rebound (look-ahead updates detail) |

### A6: Goal Chain

1. You log a **Goal**
2. Auto-creates **Stoppage_Goal** (silent)
3. Shows confirm bar for **Faceoff_AfterGoal** at center ice
4. Click ✓ to confirm, ✏️ to edit, ✗ to skip

### A7: Penalty Chain

1. You log a **Penalty**
2. Auto-creates **Stoppage_Penalty** (silent)
3. Shows confirm bar for **Faceoff_AfterPenalty** in non-penalized team's offensive zone

### A8: Rebound Chain (with Look-Ahead)

1. You log **Save_Rebound**
2. Shows confirm bar for **Rebound** (default: TeamRecovered)
3. After NEXT event is logged, Rebound detail auto-updates:
   - Next event by same team is Shot/Goal → **Rebound_ShotGenerated**
   - Next event by opposite team → **Rebound_OppTeamRecovered**

---

## 5. Shortcuts

### General Shortcuts

| Key | Action |
|-----|--------|
| `Enter` | Save event (shows confirmation) |
| `Shift+Enter` | Quick log (no confirmation) |
| `Ctrl+L` | Log & create next linked event |
| `Escape` | Cancel / Close modals |
| `?` | Open help |
| `Tab` | Toggle Puck/Player XY mode |
| `` ` `` | Switch to Puck XY mode |
| `Backspace` | Undo last XY point |
| `K` | Link to last event |

### Video Controls

| Key | Action |
|-----|--------|
| `Space` | Play/Pause |
| `←` / `→` | Seek ±1 second |
| `Shift+←/→` | Seek ±10 seconds |
| `↑` / `↓` | Speed up/down |
| `;` / `'` | Frame back/forward |
| `+` / `-` | Zoom in/out |
| `0` | Reset zoom |
| `Ctrl+1-9` | Switch video source |

### Team & Players

| Key | Action |
|-----|--------|
| `H` / `A` | Set team Home/Away |
| `Shift+S` | Swap Event/Opp Teams |
| `1-6` | Select Event Player 1-6 |
| `Alt+1-6` | Select Opp Player 1-6 |
| `[` / `]` | Cycle prev/next player |

### Event Type Hotkeys

| Key | Event |
|-----|-------|
| `F` | Faceoff |
| `S` | Shot |
| `P` | Pass |
| `G` | Goal |
| `T` | Turnover |
| `Z` | Zone |
| `N` | Penalty |
| `X` | Stoppage |
| `V` | Save |
| `R` | Rebound |
| `D` | DeadIce |

### Zone & Success

| Key | Action |
|-----|--------|
| `Q` | Offensive zone |
| `W` | Neutral zone |
| `E` | Defensive zone |
| `Y` | Successful |
| `U` | Unsuccessful |

### Shifts

| Key | Action |
|-----|--------|
| `L` | Log shift |
| `E` | End shift |
| `Q` | Quick line change |

---

## 6. Derived Fields

### ETL Auto-Derived vs Manual Entry

The ETL pipeline automatically derives certain fields from the event data you enter. You don't need to manually enter these.

### AUTO - Derived by ETL

| Field | Derived From |
|-------|--------------|
| **event_successful** | From event_detail code (Shot_OnNetSaved→s, Shot_Missed→u) |
| **shift_start_type** | From FIRST event of shift (Faceoff_AfterGoal→FaceoffAfterGoal) |
| **shift_stop_type** | From LAST event of shift (Goal→Goal, Penalty→Penalty) |
| **zone_change_index** | From puck XY movement |
| **strength** | From shift slot occupancy (5v5, 5v4, 4v5, ENH, ENA) |
| **assists** | From play_detail columns (AssistPrimary, AssistSecondary) |
| **faceoff_win/loss** | From player_role (event_player_1=winner) |
| **start_zone/end_zone** | From first/last event zones |

### MANUAL - Must Enter

| Field | Why Manual |
|-------|-----------|
| **event_type** | Core classification |
| **event_detail** | Usually required for stats |
| **event_detail_2** | Shot/pass type modifier |
| **play_detail** | Micro-stats for analysis |
| **puck_xy** | Rink position |
| **player_xy** | Player positions |
| **players** | Who did what |
| **time_start/end** | When it happened |
| **is_highlight** | User judgment |

### event_successful Derivation Rules

| event_detail | → | event_successful |
|--------------|---|------------------|
| Shot_OnNetSaved, Shot_Goal, Pass_Completed | → | **s** (successful) |
| Shot_Missed, Shot_Blocked, Pass_Missed, Pass_Intercepted | → | **u** (unsuccessful) |
| Zone_Entry, Zone_Exit, Zone_Keepin | → | **s** (successful) |
| Zone_Entry_Failed, Zone_Exit_Failed, Zone_Keepin_Failed | → | **u** (unsuccessful) |

### Play Details: Manual vs Derivable

**Manual play_details** (you enter these):
- BoardBattle, PuckProtection, Screening, StickCheck, BodyCheck, PokCheck, ShotAttemptCreated, etc.

**Derivable play_details** (ETL can derive from event context):
- AssistPrimary, AssistSecondary, BlockedShot, DeflectedShot, ForcedTurnover, PassIntercepted, etc.

---

## 7. Export

### Export Options

- **Download Excel**: Full game data with events, shifts, players
- **Export to BLB**: BenchSight League Box format for ETL
- **Copy JSON**: Raw event data for debugging

### Exported Columns (Events)

- idx, period, time_start, time_end
- event_type, event_detail, event_detail_2
- team, zone, event_successful
- event_player_1 through event_player_6
- opp_player_1 through opp_player_6
- puck_xy (JSON array)
- player_xy (JSON object)
- play_detail_1, play_detail_2
- linked_event_idx
- is_highlight, notes

### ETL Compatibility

- **DIM Table Codes**: All event_detail codes use underscores (e.g., Shot_OnNetSaved)
- **DeadIce**: No detail1 required (dim_event_detail has no DeadIce rows)
- **Faceoff winner**: Always event_player_1 (opp_player_1 = loser)
- **Goals**: Only counted when event_type='Goal' AND event_detail='Goal_Scored'
- **Stats**: Only event_player_1 gets stat credit (prevents double-counting)
- **Assists**: Only AssistPrimary and AssistSecondary count (not Tertiary)

### Common Issues

| Issue | Solution |
|-------|----------|
| Missing goals | Check event_detail is exactly 'Goal_Scored' |
| Double-counted stats | Ensure only event_player_1 has primary action |
| Incorrect strength | Verify shift slots have correct players |
| Bad zone inference | Ensure puck XY is placed correctly |

---

## Version History

- **v29.1** - Enhanced command bar syntax, auto-event chains A6/A7/A8, derived fields documentation, DIM table compliance
- **v29.0** - Auto-event chains A1-A5, command bar improvements
- **v28.0** - Home/away video type variants
