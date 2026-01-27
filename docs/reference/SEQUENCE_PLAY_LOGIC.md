# Sequence and Play Logic Reference

> **Status:** Reference Document
> **Last Updated:** 2026-01-26
> **Related Issues:** TBD (code update pending)

This document defines the parameters and logic for generating `sequence_key` and `play_key` in the BenchSight ETL pipeline.

---

## Conceptual Overview

### Hierarchy

```
Game
  └─ Period
       └─ Sequence (Faceoff → Whistle)
            └─ Play (Possession Unit)
                 └─ Events (Passes, Shots, etc.)
```

### Definitions

| Concept | Definition | Duration |
|---------|------------|----------|
| **Sequence** | Continuous period of play from one stoppage to the next | Faceoff to whistle (typically 20-60 seconds) |
| **Play** | Distinct possession stretch within a sequence | Zone possession until turnover/transition (typically 5-20 seconds) |

### Relationship

- **Plays are nested within sequences** (dependent, not independent)
- One sequence contains 1+ plays
- One play belongs to exactly one sequence
- Plays **never** span sequences
- Play numbering **resets** when a new sequence starts

---

## Sequence Parameters

### Sequence Start Events

A new sequence begins when:

| Event | Description | Priority |
|-------|-------------|----------|
| `Faceoff` | Any faceoff (game start, after goal, after stoppage) | Primary |
| `PeriodStart` | Start of period (fallback if faceoff missing) | Fallback |

**Key Principle:** Every sequence starts with a faceoff. If tracker data is missing the faceoff, use PeriodStart as fallback.

### Sequence End Events

A sequence ends when any whistle-causing event occurs:

| Event | Description | Example |
|-------|-------------|---------|
| `Stoppage` | General whistle/stoppage | Puck out of play, goalie freeze |
| `Goal` | Puck enters net | Any goal scored |
| `Penalty` | Infraction called | Tripping, hooking, etc. |
| `Icing` | Icing call | Puck dumped past goal line |
| `Offside` | Offside call | Player enters zone before puck |
| `Timeout` | Team or TV timeout | Called timeout |
| `PeriodEnd` | End of period | Buzzer sounds |
| `GameEnd` | End of game | Final buzzer |
| `GoalieChange` | Goalie pulled/replaced (delayed whistle) | Rare edge case |

**Key Principle:** If the whistle blows, the sequence ends. Period.

### Sequence Logic Pseudocode

```python
SEQUENCE_START_EVENTS = ['Faceoff', 'PeriodStart']

SEQUENCE_END_EVENTS = [
    'Stoppage',
    'Goal',
    'Penalty',
    'Icing',
    'Offside',
    'Timeout',
    'PeriodEnd',
    'GameEnd',
    'GoalieChange'
]

# Logic:
# 1. New sequence starts on Faceoff (or PeriodStart fallback)
# 2. Sequence ends on any SEQUENCE_END_EVENT
# 3. The ending event IS part of the sequence (then sequence closes)
# 4. Next event after sequence end requires new faceoff to start new sequence
```

---

## Play Parameters

### Play Start Events

A new play begins when:

| Event | Description | Context |
|-------|-------------|---------|
| `Faceoff` | Faceoff win | Possession established |
| `Turnover_Takeaway` | Steal/interception | Possession gained |
| `Zone_Entry` | Successful zone entry | New offensive opportunity |
| `Zone_Exit` | Successful zone exit | Breakout/transition |
| `Possession_PuckRecovery` | Loose puck recovered | Possession established |
| `Possession_PuckRetrieval` | Puck retrieved | Possession established |

### Play End Events

A play ends when:

| Event | Description | Outcome |
|-------|-------------|---------|
| **Possession Changes** | | |
| `Turnover_Giveaway` | Lost puck to opponent | Opponent starts new play |
| `Turnover_Takeaway` | Opponent steals puck | This team's play ends |
| `ShotBlocked` | Shot blocked by opponent | Possession change |
| `SaveFreeze` | Goalie covers puck | Stoppage imminent |
| **Zone Transitions** | | |
| `Zone_Entry` | Entered offensive zone | Old play ends, new play starts |
| `Zone_Exit` | Exited defensive zone | Old play ends, new play starts |
| `Zone_Entry_Failed` | Failed zone entry | Turnover at blueline |
| `Zone_Exit_Failed` | Failed zone exit | Turnover at blueline |
| **Sequence-Ending Events** | | |
| `Goal` | Goal scored | Sequence + play both end |
| `Stoppage` | Whistle blown | Sequence + play both end |
| `Penalty` | Penalty called | Sequence + play both end |
| `Icing` | Icing called | Sequence + play both end |
| `Offside` | Offside called | Sequence + play both end |

### Play Logic Pseudocode

```python
PLAY_START_EVENTS = [
    'Faceoff',
    'Turnover_Takeaway',
    'Zone_Entry',
    'Zone_Exit',
    'Possession_PuckRecovery',
    'Possession_PuckRetrieval'
]

PLAY_END_EVENTS = [
    # Possession changes
    'Turnover_Giveaway',
    'Turnover_Takeaway',
    'ShotBlocked',
    'SaveFreeze',

    # Zone transitions (end old play, start new play)
    'Zone_Entry',
    'Zone_Exit',
    'Zone_Entry_Failed',
    'Zone_Exit_Failed',

    # Sequence-ending events (play ends when sequence ends)
    'Goal',
    'Stoppage',
    'Penalty',
    'Icing',
    'Offside'
]

# Logic:
# 1. Play starts on PLAY_START_EVENT or first event in sequence
# 2. Play ends on PLAY_END_EVENT
# 3. Zone transitions both END old play AND START new play
# 4. Failed zone transitions END play (turnover)
# 5. When sequence ends, current play also ends
```

---

## Key Formats

### sequence_key

```
Format: SQ{game_id}{sequence_number:05d}
Example: SQ1896900001 (Game 18969, Sequence 1)
```

### play_key

```
Format: PL{game_id}{sequence_number:02d}{play_number:02d}
Example: PL1896900101 (Game 18969, Sequence 1, Play 1)
         PL1896900203 (Game 18969, Sequence 2, Play 3)
```

**Note:** Current implementation uses `sequence * 100 + play` which limits to 99 plays per sequence. This is acceptable (typical sequence has 5-15 plays).

---

## Example Walkthrough

### Game 18969, Sequence 1

```
Event  Type              Detail              Sequence    Play     Notes
─────  ────              ──────              ────────    ────     ─────
1000   Faceoff           Faceoff_GameStart   SQ...0001   PL...01  Seq 1 starts, Play 1 starts
1001   Pass              Pass_Completed      SQ...0001   PL...01
1002   Possession        Possession_Regroup  SQ...0001   PL...01
1003   Pass              Pass_Completed      SQ...0001   PL...01
1004   Zone_Entry_Exit   Zone_Entry          SQ...0001   PL...01  Play 1 ENDS (zone transition)
1005   Turnover          Turnover_Giveaway   SQ...0001   PL...02  Play 2 starts, then ENDS
1006   Possession        PuckRetrieval       SQ...0001   PL...03  Play 3 starts (recovery)
1007   Pass              Pass_Completed      SQ...0001   PL...03
1008   Zone_Entry_Exit   Zone_Exit           SQ...0001   PL...03  Play 3 ENDS (zone transition)
...
1039   Stoppage          Stoppage_Play       SQ...0001   PL...11  Seq 1 ENDS, Play 11 ENDS
1040   DeadIce           —                   —           —        Between sequences
1041   Faceoff           Faceoff_Neutral     SQ...0002   PL...01  Seq 2 starts, Play 1 starts
```

---

## Edge Cases

### 1. Goal Scored

```
Event: Goal
Behavior:
  - Current play ENDS
  - Current sequence ENDS
  - Next faceoff starts new sequence
```

### 2. Failed Zone Entry

```
Event: Zone_Entry_Failed
Behavior:
  - Current play ENDS (turnover at blueline)
  - Sequence CONTINUES (no whistle)
  - Opponent's new play starts
```

### 3. Shot → Save → Rebound → Recovery

```
Events: Shot_OnNet → Save_Rebound → Rebound_TeamRecovered
Behavior:
  - SAME play continues (possession maintained by shooting team)
  - If opponent recovers rebound: play ENDS, new opponent play starts
```

### 4. Icing

```
Event: Icing
Behavior:
  - Current play ENDS
  - Current sequence ENDS
  - Faceoff in defensive zone starts new sequence
```

### 5. Delayed Penalty

```
Scenario: Penalty called but play continues until offending team touches puck
Behavior:
  - Sequence continues until stoppage
  - Track as normal until whistle
  - Penalty event ends sequence when called
```

### 6. Empty Net / Goalie Pulled

```
Event: GoalieChange (pull)
Behavior:
  - Does NOT end sequence (no whistle)
  - Play continues
  - Only ends sequence if delayed whistle situation
```

---

## Analytics Applications

### Sequence-Level Metrics

| Metric | Formula | Use Case |
|--------|---------|----------|
| Sequence Duration | `time_end - time_start` | Possession time analysis |
| Shots per Sequence | `COUNT(shots) / COUNT(sequences)` | Offensive efficiency |
| Sequence Outcome | `Goal / Stoppage / Penalty / etc.` | Play result analysis |
| Entry Rate | `sequences_with_entry / total_sequences` | Zone entry success |

### Play-Level Metrics

| Metric | Formula | Use Case |
|--------|---------|----------|
| Play Duration | `time_end - time_start` | Possession stretch analysis |
| Passes per Play | `COUNT(passes) / COUNT(plays)` | Puck movement |
| Play Outcome | `Shot / Turnover / Zone_Exit` | Play result |
| Controlled Plays | `plays_with_controlled_entry` | Quality entries |

---

## Industry Alignment

| Platform | Sequence Equivalent | Play Equivalent |
|----------|---------------------|-----------------|
| **NHL Edge IQ** | Shift segments | Possessions |
| **Sportlogiq** | Sequences | Possession units |
| **Natural Stat Trick** | Shift events | Zone time segments |
| **BenchSight** | `sequence_key` | `play_key` |

---

## Implementation Status

### Current Code Location

```
src/core/key_utils.py
  - SEQUENCE_END_EVENTS (line ~480)
  - PLAY_END_DETAILS (line ~483)
  - generate_sequence_play_keys() function (line ~490+)
```

### Required Updates

| Parameter | Current | Should Be | Action |
|-----------|---------|-----------|--------|
| SEQUENCE_END_EVENTS | Missing Icing, Offside, GoalieChange | Add these | Update |
| SEQUENCE_END_EVENTS | Has DeadIce, Clockstop | Remove (redundant) | Update |
| SEQUENCE_END_EVENTS | Has Intermission | Rename to PeriodEnd | Update |
| PLAY_END_EVENTS | Missing ShotBlocked, SaveFreeze | Add these | Update |
| PLAY_END_EVENTS | Missing sequence-enders | Add Goal, Stoppage, etc. | Update |

---

## References

- NHL Edge IQ Documentation
- Sportlogiq Methodology Papers
- BenchSight CLAUDE.md (project rules)
- `src/core/key_utils.py` (implementation)
