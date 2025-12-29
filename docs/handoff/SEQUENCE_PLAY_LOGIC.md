# Sequence and Play Logic Documentation

## Overview

BenchSight uses two levels of event grouping:
1. **SEQUENCE**: Possession chain from turnover to turnover
2. **PLAY**: Single zone + single team possession

---

## SEQUENCE Definition

A **sequence** tracks what happens after a possession change until the next possession change.

### Use Case
"How often does player X turn it over and the opponent scores?"

### Sequence Boundaries

| Event | Effect |
|-------|--------|
| **Turnover** (Giveaway/Takeaway) | STARTS new sequence for recovering team |
| **Faceoff** | STARTS new sequence for winning team |
| **Stoppage** | STARTS new sequence |
| **Period Change** | STARTS new sequence |
| **Goal** | ENDS sequence (goal is last event of sequence) |

### Example: Turnover → Goal (18 events)
```
Event 1173: Turnover_Giveaway (Away d-zone)     ← SEQUENCE STARTS
Event 1174: Possession - Home retrieves (o-zone)
Event 1175: Pass_Completed (o-zone)
Event 1176: Shot_OnNetSaved (o-zone)
Event 1177: Save_Rebound
Event 1178: Rebound_OppTeamRecovered
Event 1179: Possession_Recovery (o-zone)
Event 1180-1188: Passes and possessions (o-zone)
Event 1189: Shot_Goal (o-zone)
Event 1190: Goal_Scored (o-zone, Home)           ← SEQUENCE ENDS
```

This sequence shows: Away giveaway → Home recovers → Home cycles → Home scores

### Sequence Metrics
| Metric | Description |
|--------|-------------|
| sequence_id | Unique identifier (SQ{game_id:05d}{seq:05d}) |
| event_count | Number of events in sequence |
| start_team | Team at sequence start (Home/Away) |
| end_team | Team at sequence end |
| start_zone | Zone at start (o/n/d) |
| end_zone | Zone at end |
| has_goal | Boolean: sequence ended in goal |
| duration_seconds | Time from first to last event |
| trigger_type | What started: Turnover, Faceoff, Stoppage |

---

## PLAY Definition

A **play** is a continuous possession by one team in one zone.

### Use Case
"Analyze entry-to-shot patterns within the offensive zone"

### Play Boundaries

| Event | Effect |
|-------|--------|
| **Zone Entry** | STARTS new play |
| **Zone Exit** | STARTS new play |
| **Possession Change** | STARTS new play (different team) |
| **New Sequence** | STARTS new play (inherits from sequence) |

### Example: O-Zone Play (6 events)
```
Event 1011: Zone_Entry (Away o-zone)            ← PLAY STARTS
Event 1012: Shot_Blocked (o-zone)
Event 1013: Possession_Recovery (o-zone)
Event 1014: Possession (o-zone)
Event 1015: Pass_Completed (o-zone)
Event 1016: Turnover_Giveaway (o-zone)          ← PLAY ENDS
```

### Play Metrics
| Metric | Description |
|--------|-------------|
| play_id | Unique identifier (PL{game_id:05d}{play:05d}) |
| sequence_id | Parent sequence FK |
| event_count | Number of events in play |
| team | Team with possession (Home/Away) |
| zone | Zone of play (o/n/d) |
| has_shot | Boolean: play included shot |
| has_goal | Boolean: play ended in goal |
| duration_seconds | Time from first to last event |

---

## Relationship

```
GAME
└── SEQUENCE 1 (Faceoff → Turnover)
    ├── PLAY 1 (n-zone, Home)
    ├── PLAY 2 (o-zone, Home)
    └── PLAY 3 (d-zone, Away)
└── SEQUENCE 2 (Turnover → Stoppage)
    ├── PLAY 4 (o-zone, Away)
    └── PLAY 5 (n-zone, Away)
└── SEQUENCE 3 (Faceoff → Goal)
    ├── PLAY 6 (d-zone, Home)
    ├── PLAY 7 (n-zone, Home)
    └── PLAY 8 (o-zone, Home) ← Has goal
```

---

## Implementation

### Generator File
`src/sequence_play_generator.py`

### Key Functions
```python
# Add sequence/play indexes to events
df = generate_sequence_play_indexes(events_df, game_id)

# Build sequence summary table
fact_sequences = analyze_sequences(events_df, game_id)

# Build play summary table  
fact_plays = analyze_plays(events_df, game_id)
```

### Trigger Sets
```python
SEQUENCE_START_EVENTS = {
    'Faceoff',
    'Turnover',
    'GameStart',
    'Stoppage',
    'Intermission',
}

SEQUENCE_START_DETAILS = {
    'Turnover_Giveaway',
    'Turnover_Takeaway',
    'Faceoff_AfterGoal',
    'Faceoff_AfterStoppage',
    ...
}
```

---

## Expected Counts

| Game | Events | Sequences | Plays | Avg Events/Seq |
|------|--------|-----------|-------|----------------|
| 18969 | 1,595 | ~268 | ~741 | 5.4 |
| 18977 | 1,362 | ~271 | ~538 | 5.0 |
| 18981 | 1,297 | ~260 | ~771 | 5.0 |
| 18987 | 1,579 | ~277 | ~682 | 5.7 |
| **Total** | 5,833 | ~1,076 | ~2,732 | 5.4 |

---

## Linked Events

Separate from sequences/plays, **linked_event_index** tracks manually-linked events from the tracker:

| Chain Type | Description |
|------------|-------------|
| Shot → Save | Shot linked to save |
| Save → Rebound | Save linked to rebound |
| Pass → Reception | Passer linked to receiver |

These are tracked via `linked_event_index` column in the tracking data.
