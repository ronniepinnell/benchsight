# Event Success/Unsuccessful (s/u) Logic

## Overview

This document defines when and how to apply success/unsuccessful flags at two levels:
1. **Event-level s/u** - Applies to ALL players involved in the event
2. **Play-level s/u** - Applies to SPECIFIC player performing the micro-action (play_detail1/2)

**Format:** Single character flag: `'s'` (successful) or `'u'` (unsuccessful)
**Not a ratio** - Binary flag only

---

## CONFIGURATION CONSTANTS (Easy to Adjust)

All thresholds in one place for easy modification:

```python
# ============================================================
# S/U LOGIC CONFIGURATION CONSTANTS
# Adjust these values to tune derivation thresholds
# ============================================================

# Time Windows (seconds)
CONTEXT_WINDOW_SECONDS = 3          # Look-ahead for turnover check
QUICK_UP_MAX_SECONDS = 3            # Zone exit → entry for QuickUp
GIVE_AND_GO_MAX_SECONDS = 4         # Pass → return pass for GiveAndGo
DELAY_MIN_SECONDS = 5               # Min time between events for Delay
ONE_TIMER_MAX_SECONDS = 0.5         # Pass → shot for ShotOneTimer
TAKEAWAY_MAINTAIN_SECONDS = 3       # Maintain possession for takeaway 's'

# Distance Thresholds (feet)
CEDED_ENTRY_DISTANCE_FT = 20        # Defender distance for ceded zone entry
CEDED_EXIT_DISTANCE_FT = 18         # Defender distance for ceded zone exit
FORCED_TURNOVER_DISTANCE_FT = 2     # Pressure distance for ForcedTurnover
PASS_CROSS_MIN_Y_CHANGE_FT = 20     # Y change for PassCross
PASS_STRETCH_MIN_DISTANCE_FT = 60   # Distance for PassStretch (outlet)
CHIP_MAX_DISTANCE_FT = 15           # Max distance for Chip pass

# Percentage Thresholds
PASS_LANE_TOLERANCE_PCT = 0.05      # 5% tolerance for BlockPassingLane

# Event Look-Ahead Counts
ZONE_ENTRY_LOOK_AHEAD_EVENTS = 5    # Max events to check for entry success
ZONE_EXIT_LOOK_AHEAD_EVENTS = 3     # Max events to check for exit success
PASS_LOOK_AHEAD_EVENTS = 2          # Max events to check for pass success
```

**Implementation Note:** These should be loaded from `config/etl_thresholds.json` or similar config file so they can be adjusted without code changes.

---

### VALUE STANDARDIZATION (CRITICAL)

**Current problem:** Field has multiple value types: `TRUE`, `1`, `'s'`, `'u'`, `'S'`, `'U'`

**Rule:** ALL values must be lowercase `'s'` or `'u'` only.

```python
# ETL standardization logic
def standardize_success_flag(value):
    if pd.isna(value) or value == '':
        return None
    val_str = str(value).lower().strip()
    if val_str in ['s', 'true', '1', 'success', 'successful']:
        return 's'
    elif val_str in ['u', 'false', '0', 'unsuccessful', 'fail', 'failed']:
        return 'u'
    else:
        return None  # Invalid value - log warning
```

**Apply to:** `event_successful`, `play_detail1_s`, `play_detail2_s`

---

## MASTER LIST: Human Required vs Automated Play Details

### KEY RULES

1. **Human input is SUPREME** - Tracker entries always take priority over derived values
2. **Only 2 slots** - Maximum 2 play_details per player (play_detail1, play_detail2)
3. **Priority order** - When deriving, select the 2 most important from priority table
4. **Never overwrite** - If tracker has a value, keep it; only derive into empty slots

### DERIVATION PRIORITY (When Filling Empty Slots)

| Priority | Category | Examples | Why Important |
|----------|----------|----------|---------------|
| 1 | Forced outcomes | ForcedTurnover, ForcedMissedPass | Defensive impact |
| 2 | Beat/Stopped pairs | BeatDeke, StoppedDeke | 1v1 outcomes |
| 3 | Battle outcomes | LoosePuckBattleWon/Lost | Possession battles |
| 4 | Ceded zone | CededZoneEntry, CededZoneExit | Defensive accountability |
| 5 | Pass lane blocks | BlockPassingLane, InShotPassLane | Defensive positioning |
| 6 | Failure attribution | LostPuck, SeparateFromPuck | Who lost possession |
| 7 | Pass outcomes | ReceiverCompleted | Confirmation only |
| 8 | Descriptive | Drive*, Screen, Position | Lowest priority |

### ❌ HUMAN REQUIRED (Must Come From Tracker)

These play_details **cannot be calculated** - they require human observation during tracking:

| Category | play_details | Why Human Required |
|----------|--------------|-------------------|
| **Offensive Moves** | Deke, FakeShot, OpenIceDeke | Subjective move assessment |
| **Beat Moves** | BeatWide, BeatMiddle, BeatSpeed, BeatFake, BeatDeke | Did player actually beat defender? |
| **Stopped Moves** | StoppedDeke | Defender stopped the move |
| **Defensive Techniques** | StickCheck, PokeCheck, StickLift, TieUp, PinToBoards | Specific technique used |
| **Defensive Positioning** | Pressure, Contain, GapControl, Angling | Intent-based assessment |
| **Effort/Hustle** | Forecheck, Backcheck | Player effort observation |
| **Attribution** | ReceiverMissed, ReceiverBobbled, ForcedMissedShot | Cause determination (receiver/shot specific) |
| **Shot Types** | ShotWrist, ShotSlap, ShotSnap, ShotBackhand | Can't determine from XY |
| **Goalie Saves** | SaveGlove, SaveBlocker, SavePad, SaveStick, SaveBody, SaveDesperation | Requires video |
| **Pass Types** | PassSaucer | Airborne pass - can't detect |

**Total: ~35 play_details require human observation**

### ✅ AUTOMATED (ETL Can Derive)

These play_details **can be calculated** from XY data, event data, or event sequences:

| Category | play_details | Data Source |
|----------|--------------|-------------|
| **From XY Trajectory** | DriveMiddle, DriveWide, DriveCorner, DriveNetMiddle, DriveNetWide | Player XY movement |
| **From Player Position** | FrontofNet, CrashNet, Screen, BoxOut | Player XY relative to net |
| **From Puck XY** | Breakout, Zone, Regroup, Cycle, EndToEndRush | Puck trajectory/pattern |
| **From Event Detail** | BlockedShot, PassIntercepted, PassDeflected, ZoneEntryDenial, ZoneExitDenial | event_detail value |
| **From Event Sequence** | QuickUp, GiveAndGo, SecondTouch, Delay, ShotOneTimer, ShotTip | Time between events |
| **From Event Chain** | DeflectedShot, AttemptedTip/Deflection, PassForTip | linked_event analysis |
| **From Defender Distance** | CededZoneEntry (≥20ft), CededZoneExit (≥18ft) | opp_player_1 XY distance |
| **From Zone + Event** | PenaltyKillClear, AttemptedBreakOut*, AttemptedEntry*, ClearingAttempt | Zone + event_type |
| **From Pass XY** | PassCross (Y>20ft), PassBackdoor, PassRoyal, PassStretch (>60ft), Chip (<15ft) | Puck start/end XY |
| **From Rebound Pattern** | ReboundControlled, ReboundGiven, ReboundNone | Save → next event |
| **From Zone Location** | NeutralZoneTurnover, NeutralZoneWin, StretchPass | Puck XY in zone |
| **From Puck Battle** | LoosePuckBattleWon, LoosePuckBattleLost (derive opposite) | Already tracked, derive pair |
| **From Pressure Distance** | ForcedTurnover, ForcedMissedPass, ForcedLostPossession | opp_player within 2 ft of puck carrier at turnover |
| **From Pass Path** | BlockPassingLane, InShotPassLane | Player within 5% of puck travel path |

**Total: ~50 play_details can be automated**

### ⚠️ MAYBE AUTOMATED (Needs Validation)

| play_detail | Potential Logic | Concern |
|-------------|-----------------|---------|
| ShotBackhand | Player orientation + XY | May not be reliable |
| SealOff | Player XY blocking path to net | Needs validation |

---

## Guiding Principle

**Not all events/plays need a flag.** Some are:
- **Implied** - Goal is obviously successful, no flag needed
- **Neutral** - Rebound is not inherently good or bad
- **Irrelevant** - Stoppage has no success concept

Only apply flags where success/failure is **ambiguous but determinable** from context.

---

## Event-Level Success (Applies to All Players in Event)

### FINAL EVENT S/U DECISIONS (User Confirmed)

| Event Type | event_detail | Flag | Logic |
|------------|--------------|------|-------|
| **Pass** | Pass_Completed | context | 's' unless Turnover within 3 sec → 'u' |
| **Pass** | Pass_Missed | u | Always 'u' |
| **Pass** | Pass_Intercepted | u | Always 'u' |
| **Pass** | Pass_Deflected | context | Check if team retained → 's', if Turnover → 'u' |
| **Zone Entry** | Zone_Entry | context | 's' if retained 2-3 events, 'u' if immediate Turnover |
| **Zone Entry** | Zone_Entry_Failed | u | Always 'u' |
| **Zone Exit** | Zone_Exit | context | 's' if possession through N-zone, 'u' if Turnover |
| **Zone Exit** | Zone_Exit_Failed | u | Always 'u' |
| **Zone Keepin** | Zone_Keepin | context | 's' if retained 3+ sec or shot, 'u' if puck exits |
| **Zone Keepin** | Zone_Keepin_Failed | u | Always 'u' |
| **Turnover** | Turnover_Giveaway | u | Always 'u' for losing team |
| **Turnover** | Turnover_Takeaway | context | 's' only if maintained possession 3+ sec |

### Events That DO NOT Need s/u Flag (Leave Blank)

| Event Type | Reason |
|------------|--------|
| **Goal** | Obviously successful - implied |
| **Shot** | Ambiguous - leave blank |
| **Faceoff** | Win/loss already tracked separately |
| **Save** | Goalie event - tracked separately |
| **Rebound** | Neutral - recovery is separate event |
| **Stoppage** | Neutral game event |
| **Penalty** | Not success/failure context |
| **Possession** | Skip for now - too context-dependent |
| **Puck Recovery** | Skip for now - too context-dependent |
| **Loose Puck** | Neutral - battle outcome tracked separately |
| **DeadIce/Intermission/GameStart/End** | Time events - not applicable |

### Context Logic Summary

**Time window:** 3 seconds (industry standard per Sportslogiq)
**Look-ahead:** Next 2-3 events OR 3 seconds, whichever comes first
**Turnover test:** If next event by same team is Turnover → previous event = 'u'

### Shot Clarification

**DECISION: Leave blank.**

Shots are ambiguous:
- On net but saved - is that success or failure?
- Missed the net - bad, but attempt was made
- Blocked - opponent made a play

**No event-level s/u flag for shots.** Other metrics (shot quality, xG, on-net %) handle shot evaluation.

---

## Play-Level Success (Applies to SPECIFIC Player)

Play-level s/u is derived from `play_detail1` and `play_detail_2` columns.

### INHERITANCE RULE (Key Simplification)

**event_player_1's play_details inherit the event's s/u flag automatically.**

Only flag play_details explicitly when they **differ** from the event outcome:
- Defender's successful action in an offensive team's failed event
- Receiver's failure when event might be ambiguous

```
Example 1: Pass_Missed event = 'u'
  - event_player_1 (passer) → inherits 'u' from event
  - event_player_2 (receiver) with ReceiverMissed → explicit 'u'

Example 2: Turnover_Giveaway event = 'u' for offense
  - event_player_1 (offensive) → inherits 'u' from event
  - opp_player_1 (defender) with StickCheck → explicit 's' (caused turnover)

Example 3: Zone_Entry event = 's'
  - event_player_1 → inherits 's' from event
  - No explicit flags needed for play_details
```

### Play_Details That OVERRIDE Event Flag

These get explicit flags because they represent a **different perspective**:

| play_detail | Flag | Applies To | Logic |
|-------------|------|------------|-------|
| **StickCheck** | s | Defender | 's' if caused turnover (blank otherwise) |
| **PokeCheck** | s | Defender | 's' if caused turnover (blank otherwise) |
| **Pressure** | s | Defender | 's' if caused turnover (blank otherwise) |
| **ForcedTurnover** | s | Defender | Always 's' |
| **ForcedMissedPass** | s | Defender | Always 's' |
| **ForcedMissedShot** | s | Defender | Always 's' |
| **Beat*** | u | Defender who was beat | BeatWide/Middle/Speed = 'u' for defender |
| **ReceiverMissed** | u | Receiver | Explicit 'u' for receiver |
| **ReceiverBobbled** | u | Receiver | Explicit 'u' for receiver |
| **LostPuck** | u | Player | Explicit 'u' |
| **LoosePuckBattleWon** | s | Player | Explicit 's' |
| **LoosePuckBattleLost** | u | Player | Explicit 'u' |

### Play_Details That Inherit Event Flag (No Explicit Flag Needed)

| Category | play_details |
|----------|--------------|
| **Scoring** | AssistPrimary, AssistSecondary, Screen, FrontofNet |
| **Transition** | Breakout, Regroup, AttemptedEntry*, AttemptedBreakOut* |
| **Playmaking** | GiveAndGo, QuickUp, PassForTip, Reverse |
| **Offensive** | Drive*, Cycle, CrashNet |
| **Descriptive** | SecondTouch, Chip, Delay, Speed, Wheel, Surf |
| **Positioning** | ManOnMan, BoxOut, Contain, GapControl |

---

## Auto-Derivation Pairs (Concrete List)

When one player's action is flagged, auto-derive the opposing player's corresponding action.
**Reuse existing play_details** - player_role determines perspective.

### Offensive → Defensive Derivations

| If event_player has... | With flag | → Auto-add to opp_player | With flag |
|------------------------|-----------|--------------------------|-----------|
| Deke | s | BeatDeke | u |
| Deke | u | StoppedDeke | s |
| BeatWide | s | BeatWide | u |
| BeatMiddle | s | BeatMiddle | u |
| BeatSpeed | s | BeatSpeed | u |
| BeatFake | s | BeatFake | u |
| OpenIceDeke | s | BeatDeke | u |
| OpenIceDeke | u | StoppedDeke | s |

### Defensive → Offensive Derivations

| If opp_player has... | With flag | → Auto-add to event_player | With flag |
|----------------------|-----------|----------------------------|-----------|
| StickCheck | s (caused TO) | LostPuck | u |
| PokeCheck | s (caused TO) | SeparateFromPuck | u |
| StickLift | s (caused TO) | LostPuck | u |
| ForcedTurnover | s | LostPuck | u |
| BlockedShot | s | (no add - shot already tracked) | - |

### Pass → Receiver Derivations

| If event_player_1 (passer) has... | Event s/u | → For event_player_2 (receiver) |
|-----------------------------------|-----------|----------------------------------|
| AttemptedPass | s | ReceiverCompleted (if not already set) |
| AttemptedPass | u | Check if ReceiverMissed already set |
| Pass_Completed (event_detail) | s | Receiver inherits 's' |
| Pass_Missed (event_detail) | u | Receiver inherits 'u' (unless ReceiverMissed explicit) |

### Puck Battle Derivations

| If one player has... | With flag | → Other player in battle gets |
|----------------------|-----------|-------------------------------|
| LoosePuckBattleWon | s | LoosePuckBattleLost = u |
| LoosePuckBattleLost | u | LoosePuckBattleWon = s |

### Implementation Logic

```python
def derive_opposing_play_detail(player_role, play_detail, flag):
    """
    Given a player's play_detail and flag, derive the opposing player's action.

    Returns: (target_role, derived_play_detail, derived_flag) or None
    """
    OFFENSIVE_TO_DEFENSIVE = {
        ('Deke', 's'): ('opp_player_1', 'BeatDeke', 'u'),
        ('Deke', 'u'): ('opp_player_1', 'StoppedDeke', 's'),
        ('BeatWide', 's'): ('opp_player_1', 'BeatWide', 'u'),
        ('BeatMiddle', 's'): ('opp_player_1', 'BeatMiddle', 'u'),
        ('BeatSpeed', 's'): ('opp_player_1', 'BeatSpeed', 'u'),
        ('BeatFake', 's'): ('opp_player_1', 'BeatFake', 'u'),
        ('OpenIceDeke', 's'): ('opp_player_1', 'BeatDeke', 'u'),
        ('OpenIceDeke', 'u'): ('opp_player_1', 'StoppedDeke', 's'),
    }

    DEFENSIVE_TO_OFFENSIVE = {
        ('StickCheck', 's'): ('event_player_1', 'LostPuck', 'u'),
        ('PokeCheck', 's'): ('event_player_1', 'SeparateFromPuck', 'u'),
        ('StickLift', 's'): ('event_player_1', 'LostPuck', 'u'),
        ('ForcedTurnover', 's'): ('event_player_1', 'LostPuck', 'u'),
    }

    BATTLE_PAIRS = {
        ('LoosePuckBattleWon', 's'): ('opponent', 'LoosePuckBattleLost', 'u'),
        ('LoosePuckBattleLost', 'u'): ('opponent', 'LoosePuckBattleWon', 's'),
    }

    if player_role.startswith('event_player'):
        return OFFENSIVE_TO_DEFENSIVE.get((play_detail, flag))
    elif player_role.startswith('opp_player'):
        return DEFENSIVE_TO_OFFENSIVE.get((play_detail, flag))

    return None
```

### Derivation Rules

1. **Only derive if opp_player exists** in the event
2. **Don't overwrite** existing play_details on the opposing player
3. **Use opp_player_1** as default target (closest defender)
4. **Puck battles** - if both players involved, derive the opposite

---

## Play_Detail Slot Management

### Constraint: Only 2 Slots (play_detail1, play_detail2)

Manual tracker entries are **supreme** - never overwrite.

### Processing Order

```python
def assign_play_details(player_row, derived_list):
    """
    Assign play_details respecting manual entries and 2-slot limit.

    Args:
        player_row: Row with play_detail1, play_detail2 from tracker
        derived_list: List of (play_detail, flag) tuples to potentially add

    Returns:
        Updated play_detail1, play_detail2, play_detail1_s, play_detail2_s
    """
    # Get manual entries (from tracker)
    pd1 = player_row.get('play_detail1')
    pd2 = player_row.get('play_detail2')

    # Track source during ETL (not stored in final table)
    pd1_source = 'manual' if pd1 else None
    pd2_source = 'manual' if pd2 else None

    # Find empty slots
    empty_slots = []
    if not pd1:
        empty_slots.append(1)
    if not pd2:
        empty_slots.append(2)

    # Fill empty slots from prioritized derivation list
    for play_detail, flag in derived_list:
        if not empty_slots:
            break  # No more slots

        slot = empty_slots.pop(0)
        if slot == 1:
            pd1 = play_detail
            pd1_source = 'derived'
        else:
            pd2 = play_detail
            pd2_source = 'derived'

    return pd1, pd2
```

### Derivation Priority Order

When multiple play_details could be derived, prioritize:

| Priority | Category | Examples |
|----------|----------|----------|
| 1 | Defensive success | StickCheck→s, PokeCheck→s (if caused TO) |
| 2 | Beat/Stopped pairs | BeatDeke, StoppedDeke |
| 3 | Battle outcomes | LoosePuckBattleWon, LoosePuckBattleLost |
| 4 | Failure attribution | LostPuck, SeparateFromPuck, ReceiverMissed |
| 5 | Pass outcomes | ReceiverCompleted |
| 6 | All others | Descriptive play_details |

### Example Scenarios

**Scenario 1: Manual + Derived**
```
Tracker input:
  play_detail1 = "Breakout"
  play_detail2 = empty

Event: Turnover_Giveaway
opp_player has: StickCheck (caused turnover)

Result for event_player:
  play_detail1 = "Breakout" (manual - kept)
  play_detail2 = "LostPuck" (derived)
```

**Scenario 2: Both Slots Filled Manually**
```
Tracker input:
  play_detail1 = "Breakout"
  play_detail2 = "AttemptedPass"

Derivation would add: LostPuck

Result:
  play_detail1 = "Breakout" (manual - kept)
  play_detail2 = "AttemptedPass" (manual - kept)
  LostPuck = NOT ADDED (no empty slots)
```

**Scenario 3: Multiple Derivations Possible**
```
Tracker input:
  play_detail1 = empty
  play_detail2 = empty

Derivations available:
  - StickCheck (priority 1)
  - LostPuck (priority 4)

Result:
  play_detail1 = "StickCheck" (higher priority)
  play_detail2 = "LostPuck" (next priority)
```

### Source Tracking (ETL Only)

During ETL processing, track source for validation:
- `_pd1_source`: 'manual' | 'derived' | null
- `_pd2_source`: 'manual' | 'derived' | null

These internal columns are used for:
1. Debugging derivation logic
2. Validating manual entry quality
3. Analytics on tracker input patterns

**Not stored in final output tables** - source is inferred from presence in original tracker file.

### Micro-Stats That DO NOT Need s/u Flag

| Micro-Stat | Reason |
|------------|--------|
| **SecondTouch** | Descriptive - not success/failure |
| **Breakout** | Describes play type, not outcome |
| **Dump_RimInZone** | Describes action, not outcome |
| **DumpChase** | Describes play type |
| **Reverse** | Describes pass direction |
| **AssistPrimary** | Tracked separately |
| **AssistSecondary** | Tracked separately |
| **Contested** | Neutral - outcome determines success |
| **ManOnMan** | Describes defensive coverage |

---

## Context-Based Evaluation (Linked Events)

For events in a linked chain (`linked_event_key != ''`):

### Rule: Terminal Event Determines Chain Success

```
Chain: Pass_Completed → Zone_Exit → Turnover_Giveaway
       ↓              ↓           ↓
       ?              ?           u (always)

Result: Pass = u, Zone Exit = u (because terminal = Turnover for this team)
```

```
Chain: Pass_Completed → Zone_Entry → Shot
       ↓              ↓           ↓
       s              s           (no flag - shot ambiguous)

Result: Pass = s, Zone Entry = s (possession maintained, shot generated)
```

### Look-Ahead Rules by Event Type

| Event Type | Look Ahead | Success If | Failure If |
|------------|------------|------------|------------|
| Pass | 1-2 events | Same team next event, not Turnover | Turnover or opponent next |
| Zone Entry | 2-5 events | Shot generated OR 3+ O-zone events | Immediate turnover |
| Zone Exit | 2-3 events | Possession maintained through N-zone | Turnover in D/N zone |
| Zone Keepin | 1-2 events | Team retains possession | Puck leaves zone |
| Puck Recovery | 2-3 events | Maintained possession 2+ events | Immediate loss |

---

## Attribution Examples

### Example 1: Pass_Missed with ReceiverMissed

```
Event: Pass_Missed (event_index: 1002)
- event_player_1: #91 (passer)     play_detail1: AttemptedPass
- event_player_2: #77 (receiver)   play_detail1: ReceiverMissed

Event-level s/u: 'u' (applies to both #91 and #77)
Play-level s/u:
  - #77 gets 'u' for ReceiverMissed (receiver failed)
  - #91 gets no play-level flag (pass was thrown, unclear if bad throw or bad receive)
```

### Example 2: Zone Entry → Turnover

```
Event 1: Zone_Entry (event_index: 1007)
- event_player_1: #19

Event 2: Turnover_Giveaway (event_index: 1008)
- event_player_1: #19

Event-level s/u for Zone_Entry: 'u' (because next event is Turnover by same team)
```

### Example 3: Faceoff

```
Event: Faceoff (event_index: 1001)
- event_player_1: #91 (winner)
- opp_player_1: #44 (loser)

Event-level s/u: 's' for event_player_1 rows, 'u' for opp_player_1 rows
```

### Example 4: Defensive Success

```
Event: Turnover_Giveaway (event_index: 1003)
- event_player_1: #19 (lost puck)     play_detail1: LostPuck
- opp_player_1: #77 (gained puck)     play_detail1: StickCheck

Event-level s/u: 'u' (for event team - the team that lost the puck)
Play-level s/u:
  - #19 gets 'u' for LostPuck (he lost it)
  - #77 gets 's' for StickCheck (he made the defensive play)

NOTE: Play-level 's' for #77 is independent of event-level 'u'.
The defender's individual action was successful, even though the
event as a whole is marked unsuccessful for the offensive team.
```

**DECISION: Defensive players get play-level 's' for successful defensive actions.**
The defender who made the poke check/stick check gets 's' for their micro-action.
This is tracked at play-level, not event-level.

---

## Implementation Priority

1. **Faceoffs** - Direct derivation (event_player_1 = winner)
2. **Turnovers** - Always 'u' for Giveaway (event team), 's' for Takeaway (defending team)
3. **Zone Entry/Exit** - Context-based (check next 2-3 events)
4. **Passes** - Context-based + micro-stat override (ReceiverMissed)
5. **Puck Recovery** - Context-based (maintained 2+ events)
6. **Linked chains** - Terminal event evaluation

**Skip for now:**
- Shots (ambiguous without linked chain)
- Rebounds (neutral)
- Stoppages (not applicable)

---

---

## Play Detail Automation Analysis

**Goal:** Reduce subjectivity, increase automation. Only require tracker input for observations that CANNOT be calculated from XY/event data.

### Play Details That CAN Be Calculated (from XY data)

| play_detail | How to Calculate | Data Required |
|-------------|------------------|---------------|
| DriveMiddle | Player X moves toward center (Y toward 0) | player XY over time |
| DriveWide | Player X moves toward boards (Y toward ±42.5) | player XY over time |
| DriveCorner | Player moves to corner zone (X>75, Y>±30) | player XY |
| DriveNetMiddle | Player moves toward net center | player XY relative to net |
| DriveNetWide | Player moves toward net from wide angle | player XY trajectory |
| FrontofNet | Player positioned in slot/crease area | player XY in danger zone |
| CrashNet | Player velocity toward net increases | player XY velocity vector |
| Screen | Player between shooter and goalie | shooter XY, player XY, goalie XY |
| Breakout | Zone exit with possession (D-zone → N-zone) | puck XY trajectory |
| Zone | Current zone from puck XY | puck X coordinate |
| EndToEndRush | Puck travels from D-zone to O-zone rapidly | puck XY trajectory + time |
| Cycle | Puck movement pattern in O-zone (circular) | puck XY pattern recognition |
| Regroup | Team resets in neutral zone | puck XY + team possession |

### Play Details That CAN Be Derived (from event data)

| play_detail | Derivation Source |
|-------------|-------------------|
| AssistPrimary/Secondary | Goal events - already tracked |
| BlockedShot | event_detail = Shot_Blocked |
| PassIntercepted | event_detail = Pass_Intercepted |
| PassDeflected | event_detail = Pass_Deflected |
| PuckRecoveryRetrieval* | event_type = Possession + event_detail |
| AttemptedShot | event_type = Shot |
| AttemptedPass | event_type = Pass |
| ZoneEntryDenial | event_detail = Zone_Entry_Failed |
| ZoneExitDenial | event_detail = Zone_Exit_Failed |
| ZoneKeepin | event_detail = Zone_Keepin |

### Play Details That CAN Be Derived (from event sequence/time)

| play_detail | Derivation Logic | Data Required |
|-------------|------------------|---------------|
| QuickUp | Zone exit → Zone entry < 3 seconds | event time sequence |
| GiveAndGo | Pass by A → Pass back to A < 4 seconds | player_id sequence in linked events |
| SecondTouch | Same player in 2 consecutive events | player_id in linked_event chain |
| Delay | >5 seconds between events, same team | event timestamps |
| ClearingAttempt | D-zone event with no target (Pass_Missed from D-zone) | zone + event_detail |
| PenaltyKillClear | Clear during penalty (strength != 5v5) | strength_state + zone exit |
| Chip | Short pass - puck travels < 15 feet | puck XY start/end distance |
| AttemptedBreakOutClear | Zone exit attempt from D-zone | zone + event_type |
| AttemptedBreakOutPass | Pass from D-zone toward N-zone | zone + pass direction |
| AttemptedBreakOutRush | Carry from D-zone toward N-zone | zone + possession |
| AttemptedEntryDumpIn | Zone entry via dump (no possession) | entry type from event pattern |
| AttemptedEntryPass | Zone entry via pass | pass → entry in linked event |
| AttemptedEntryRush | Zone entry via carry (with possession) | entry with same player carrying |

### Play Details That CAN Be Derived (from linked event chains)

| play_detail | Derivation Logic | Data Required |
|-------------|------------------|---------------|
| DeflectedShot | Shot in linked chain after Pass_Deflected | linked_event_key sequence |
| AttemptedTip/Deflection | Shot event after pass to slot area | linked_event + XY |
| PassForTip | Pass to slot followed by shot | linked events + XY |
| InShotPassLane | Player between passer and target | player XY during pass event |
| ForcedMissedPass | Pass_Missed with defensive player nearby | pass event + opp_player proximity |
| ForcedMissedShot | Shot_Missed with block attempt nearby | shot event + opp_player XY |
| ForcedLostPossession | Turnover with defensive pressure | turnover + opp_player proximity |

### Play Details That CAN Be Derived (from player/position data)

| play_detail | Derivation Logic | Data Required |
|-------------|------------------|---------------|
| Backcheck | Forward in D-zone during defensive event | player position (F) + zone |
| Forecheck | Forward in O-zone during opponent possession | player position (F) + zone + opp poss |
| BoxOut | Player between opponent and net during save/rebound | player positions near net |

### Play Details That CAN Be Derived (from game state)

| play_detail | Derivation Logic | Data Required |
|-------------|------------------|---------------|
| PenaltyKillClear | Clear during PK | strength_state |
| DelayedOffside | Stoppage_Play after zone entry attempt | event_detail sequence |
| CededZoneEntry | Entry where opp_player_1 ≥ 20 ft from puck (defensive metric, always 'u') | entry + defender XY |
| CededZoneExit | Exit where opp_player_1 ≥ 18 ft from puck (defensive metric, always 'u') | exit + defender XY |

### Play Details That REQUIRE Human Observation (Tracker Input)

| play_detail | Why Human Required |
|-------------|-------------------|
| Deke | Subjective move assessment |
| BeatFake, BeatSpeed, BeatWide, BeatMiddle | Did player actually beat defender? |
| FakeShot | Can't tell from XY if it was a fake |
| StickCheck, PokeCheck, StickLift, TieUp | Specific defensive technique |
| ReceiverMissed | Why did pass fail? Receiver's fault? |
| Pressure, Contain, GapControl, Angling | Defensive positioning intent |
| Forecheck, Backcheck | Player effort/hustle assessment |
| ForcedTurnover, ForcedMissedPass | Cause attribution |
| **Shot Types** (ShotWrist, ShotSlap, ShotSnap, ShotBackhand) | Can't determine from XY |
| **Goalie Save Types** (SaveGlove, SaveBlocker, SavePad) | Requires video observation |

---

## MISSING Play Details (Hockey SME Recommendations)

### Tier 1: CRITICAL GAPS (Must Add)

**Shot Types** (for xG modeling):
| play_detail | Can Automate? | Notes |
|-------------|---------------|-------|
| ShotWrist | ❌ Human | Most common shot type |
| ShotSlap | ❌ Human | Wind-up visible on video |
| ShotSnap | ❌ Human | Quick release |
| ShotBackhand | ⚠️ Maybe | Could infer from player orientation + XY |
| ShotOneTimer | ✅ Yes | Pass → immediate shot < 0.5 sec |
| ShotTip | ✅ Yes | Deflection in shot chain |

**Goalie Save Types** (for goalie evaluation):
| play_detail | Can Automate? | Notes |
|-------------|---------------|-------|
| SaveGlove | ❌ Human | Requires video |
| SaveBlocker | ❌ Human | Requires video |
| SavePad | ❌ Human | Requires video |
| SaveStick | ❌ Human | Requires video |
| SaveBody | ❌ Human | Requires video |
| SaveDesperation | ❌ Human | Requires video |

**Rebound Control** (key goalie metric):
| play_detail | Can Automate? | Notes |
|-------------|---------------|-------|
| ReboundControlled | ✅ Yes | Save → Freeze or Save → Clear to corner |
| ReboundGiven | ✅ Yes | Save → Rebound → slot area (high danger XY) |
| ReboundNone | ✅ Yes | Save with no rebound event |

**Pass Types** (for assist quality):
| play_detail | Can Automate? | Notes |
|-------------|---------------|-------|
| PassCross | ✅ Yes | Large Y change (>20 ft) in pass |
| PassBackdoor | ✅ Yes | Pass to back post area (XY) |
| PassRoyal | ✅ Yes | Pass across crease (XY pattern) |
| PassSaucer | ❌ Human | Airborne pass - can't detect from XY |
| PassStretch | ✅ Yes | Long outlet pass (>60 ft) |

### Tier 2: HIGH VALUE ADDS

**Defensive Positioning**:
| play_detail | Can Automate? | Notes |
|-------------|---------------|-------|
| BlockPassingLane | ⚠️ Maybe | Player XY between passer and target |
| Angling | ❌ Human | Body positioning intent |
| StickLift | ❌ Human | Specific technique |
| TieUp | ❌ Human | Stick-on-stick contact |
| SealOff | ⚠️ Maybe | Player XY blocking path to net |
| PinToBoards | ❌ Human | Physical contact |

**Neutral Zone**:
| play_detail | Can Automate? | Notes |
|-------------|---------------|-------|
| NeutralZoneTurnover | ✅ Yes | Turnover where puck XY in N-zone |
| NeutralZoneWin | ✅ Yes | Possession gain in N-zone |
| StretchPass | ✅ Yes | Long pass from D-zone to O-zone |

### Consolidation Recommendations

**REMOVE (Redundant):**
- `BeatDeke` → Redundant with `Deke`
- `OpenIceDeke` → Use location field instead

**CONSOLIDATE:**
- Drive variants (5 → 3): `DriveWide`, `DriveMiddle`, `DriveNet`
- Or use single `Drive` + XY location

**REVIEW:**
- PuckRecoveryRetrieval* variants (currently 12+) → Consider using event context instead

### Recommendation: Tracker Input Simplification

**KEEP in tracker (human observation required):**
1. Deke/beat moves (BeatDeke, BeatWide, etc.)
2. Defensive techniques (StickCheck, PokeCheck)
3. Attribution (ReceiverMissed, ForcedTurnover)
4. Effort-based (Forecheck, Backcheck, Pressure)

**REMOVE from tracker (calculate in ETL):**
1. All Drive* patterns (from XY trajectory)
2. Zone transitions (from puck XY)
3. Screen, FrontofNet, CrashNet (from player position)
4. Cycle, Regroup (from pattern recognition)
5. All PuckRecoveryRetrieval* (from event_detail)

**Estimated reduction:** ~40% of play_detail options could be automated

---

## Industry Standards (from Web Research)

**Sources:**
- [NHL Edge Advanced Stats](https://www.nhl.com/news/nhl-edge-site-new-look-has-advanced-statistics-for-everybody)
- [The Hockey Analytics - Zone Entry Research](https://www.thehockeyanalytics.com/posts/zone-entry-efficiency-research/)
- [NHL EDGE Zone Time Analysis](https://puckovertheglass.substack.com/p/nhl-edge-quantifying-even-strength)

**Key Findings:**
1. **3-second window** is industry standard for possession chain events (Sportslogiq)
2. **Controlled entries yield 34% higher goal probability** than dump-ins
3. **NHL Edge uses XY tracking** to derive zone time and possession
4. **Zone entry denial rate** is tracked as defensive metric
5. **Microstats** are increasingly automated via AI/ML on tracking data

---

## Ceded Zone Entry/Exit Auto-Derivation (Hockey SME Guidance)

**Purpose:** Auto-derive CededZoneEntry/CededZoneExit as a **defensive metric** based on defender distance.

**Key Point:** This is ONLY added to opp_player_1 (the defender). The offensive player (event_player_1) does NOT get any auto-added play_detail for ceded situations.

### Distance Thresholds (Conservative)

| Zone Event | Ceded Threshold | Rationale |
|------------|-----------------|-----------|
| **Zone Entry** | ≥ 20 feet | ~3 stick lengths - defender clearly backed off |
| **Zone Exit** | ≥ 18 feet | Slightly tighter for exits |

**Why conservative:** Only flag obvious cases where the defender clearly didn't contest. Smaller distances might be tactical (gap control, waiting for help).

### Auto-Derivation Rules

| Condition | Auto-Add to opp_player_1 | Flag |
|-----------|--------------------------|------|
| Zone Entry + opp_player_1 distance ≥ 20 ft | CededZoneEntry | **'u'** |
| Zone Exit + opp_player_1 distance ≥ 18 ft | CededZoneExit | **'u'** |

**Always 'u'** - If defender was this far away, they didn't make a play. That's a defensive failure regardless of whether it was "tactical."

### Implementation Logic

```python
def derive_ceded_zone_play_detail(row, event_detail):
    """
    Check if defender ceded zone entry/exit.
    ONLY applies to opp_player_1 (defensive metric).

    Args:
        row: Event row with opp_player_1 XY and puck XY
        event_detail: 'Zone_Entry' or 'Zone_Exit'

    Returns:
        (play_detail, flag) or None
    """
    # Calculate distance from defender to puck
    distance = calculate_distance(
        row['puck_x'], row['puck_y'],
        row['opp_player_1_x'], row['opp_player_1_y']
    )

    if pd.isna(distance):
        return None  # No XY data - can't determine

    # Conservative thresholds
    if event_detail == 'Zone_Entry' and distance >= 20:
        return ('CededZoneEntry', 'u')
    elif event_detail == 'Zone_Exit' and distance >= 18:
        return ('CededZoneExit', 'u')

    return None  # Below threshold - don't auto-derive
```

### Implementation Notes

1. **Defensive metric only** - Only added to opp_player_1, never to event_player_1
2. **Always 'u'** - Ceding = defensive failure (didn't contest)
3. **Conservative thresholds** - 20/18 feet ensures we only flag obvious cases
4. **No XY data** - Don't derive anything; leave blank
5. **opp_player_1** - The closest/primary defender assigned during tracking

### What This Tracks

- **Defender accountability** - Who let the opponent in/out without a fight?
- **Defensive lapses** - Identifies when defenders are out of position
- **NOT tactical gap control** - Conservative thresholds avoid flagging intentional backing off

**Future Use:** Can aggregate to player-level "ceded rate" for defensive evaluation.
