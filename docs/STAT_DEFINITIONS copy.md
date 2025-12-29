# BenchSight Stat Definitions

## Player Role Attribution

| Role | Description | Used For |
|------|-------------|----------|
| event_player_1 | Primary player | Shots, passes, goals, turnovers |
| event_player_2 | Secondary player | Assists, pass targets |
| event_player_3+ | Supporting players | On-ice tracking |
| opp_player_1 | Primary defender | Defender stats |
| opp_player_2+ | Supporting defenders | On-ice tracking |

---

## Success Flags

| Flag | Meaning |
|------|---------|
| `s` | Successful |
| `u` | Unsuccessful |
| blank | Ignore/N/A |

---

## Basic Counting Stats

### Goals (G)
```
Source: fact_events_player
Filter: Type = 'Goal' AND player_role = 'event_player_1'
Note: event_detail can be 'Goal_Scored' or event_detail_2 can be 'Shot_Goal'
```

### Assists (A, A1, A2)
```
Source: fact_events_player
Filter: play_detail CONTAINS 'Assist'
A1 (Primary): play_detail = 'Assist-Primary' OR role closest to goal
A2 (Secondary): play_detail = 'Assist-Secondary'
```

### Points (PTS)
```
Formula: G + A
```

### Shots on Goal (SOG)
```
Source: fact_events_player
Filter: Type = 'Shot' AND player_role = 'event_player_1'
        AND (event_detail CONTAINS 'OnNet' OR event_detail CONTAINS 'Goal')
```

### Shots Total
```
Source: fact_events_player
Filter: Type = 'Shot' AND player_role = 'event_player_1'
Includes: On net, blocked, missed
```

### Shooting Percentage (SH%)
```
Formula: G / SOG * 100
```

---

## Time Stats

### Time on Ice (TOI)
```
Source: fact_shifts_player
Formula: SUM(shift_duration) for player in game
```

### Playing Time (TOI_PLAYING)
```
Source: fact_shifts_player
Formula: SUM(playing_duration) = SUM(shift_duration - stoppage_time)
```

### Shifts
```
Source: fact_shifts_player
Formula: COUNT(DISTINCT shift_index) for player in game
Note: Use logical_shift_number for "actual" shifts
```

### Avg Shift Length
```
Formula: TOI / Shifts
```

---

## Pass Stats

### Pass Attempts
```
Source: fact_events_player
Filter: Type = 'Pass' AND player_role = 'event_player_1'
```

### Pass Completed
```
Source: fact_events_player
Filter: Type = 'Pass' AND player_role = 'event_player_1' 
        AND event_successful = 's'
```

### Pass Percentage
```
Formula: Pass_Completed / Pass_Attempts * 100
```

### Pass Targets (received)
```
Source: fact_events_player
Filter: Type = 'Pass' AND player_role = 'event_player_2'
Note: This is how often a player was targeted for a pass
```

---

## Faceoff Stats

### Faceoff Wins (FOW)
```
Source: fact_events_player
Filter: Type = 'Faceoff' AND player_role = 'event_player_1'
Note: event_player_1 on faceoff = winner
```

### Faceoff Losses (FOL)
```
Source: fact_events_player
Filter: Type = 'Faceoff' AND player_role = 'opp_player_1'
Note: opp_player_1 on faceoff = loser (opposing center)
```

### Faceoff Percentage (FO%)
```
Formula: FOW / (FOW + FOL) * 100
```

---

## Zone Stats

### Zone Entries (ZE)
```
Source: fact_events_player
Filter: event_detail CONTAINS 'Zone_Entry' AND player_role = 'event_player_1'
```

### Controlled Entries (ZE_C)
```
Source: fact_events_player
Filter: event_detail_2 IN ('ZoneEntry-Carry', 'ZoneEntry-Pass')
        AND player_role = 'event_player_1'
```

### Zone Entry Percentage
```
Formula: ZE_C / ZE * 100
```

### Zone Exits (ZX)
```
Source: fact_events_player
Filter: event_detail CONTAINS 'Zone_Exit' AND player_role = 'event_player_1'
```

### Controlled Exits (ZX_C)
```
Source: fact_events_player
Filter: event_detail_2 IN ('ZoneExit-Carry', 'ZoneExit-Pass')
        AND player_role = 'event_player_1'
```

---

## Turnover Stats

### Giveaways (GIVE)
```
Source: fact_events_player
Filter: Type = 'Turnover' AND event_detail = 'Turnover_Giveaway'
        AND player_role = 'event_player_1'
```

### Bad Giveaways (GIVE_BAD)
```
Source: fact_events_player
Filter: Type = 'Turnover' AND event_detail = 'Turnover_Giveaway'
        AND turnover_quality_id = 'BAD'
        AND player_role = 'event_player_1'
```

### Takeaways (TAKE)
```
Source: fact_events_player
Filter: Type = 'Turnover' AND event_detail = 'Turnover_Takeaway'
        AND player_role = 'event_player_1'
```

### Turnover Differential
```
Formula: TAKE - GIVE_BAD
```

---

## Plus/Minus Stats

### Plus Even Strength (plus_es)
```
Source: fact_shifts
Formula: SUM(home_team_plus) for home player shifts
         SUM(away_team_plus) for away player shifts
Note: home_team_plus/minus columns exclude PP goals
```

### Minus Even Strength (minus_es)
```
Source: fact_shifts
Formula: SUM(ABS(home_team_minus)) for home player shifts
```

### Plus All Situations (plus_all)
```
Source: fact_shifts
Formula: COUNT(shifts WHERE shift_stop_type = 'Home Goal') for home player
         COUNT(shifts WHERE shift_stop_type = 'Away Goal') for away player
```

### Minus All Situations (minus_all)
```
Source: fact_shifts
Formula: COUNT(shifts WHERE shift_stop_type = 'Away Goal') for home player
         COUNT(shifts WHERE shift_stop_type = 'Home Goal') for away player
```

### Plus/Minus Empty Net
```
Source: fact_shifts
Filter: Include home_team_en or away_team_en = 1
```

---

## On-Ice Stats (Corsi/Fenwick)

### Corsi For (CF)
```
Source: Match fact_events to fact_shifts via shift_index
Formula: COUNT(Shot/Goal events where player on ice AND same team)
Includes: All shot attempts (on net, blocked, missed)
```

### Corsi Against (CA)
```
Source: Match fact_events to fact_shifts via shift_index
Formula: COUNT(Shot/Goal events where player on ice AND opponent team)
```

### Corsi Percentage (CF%)
```
Formula: CF / (CF + CA) * 100
```

### Fenwick For (FF)
```
Same as Corsi but excludes blocked shots
```

### Fenwick Against (FA)
```
Same as Corsi Against but excludes blocked shots
```

---

## Per-60 Stats

### Goals Per 60 (G/60)
```
Formula: G * 3600 / TOI_seconds
```

### Assists Per 60 (A/60)
```
Formula: A * 3600 / TOI_seconds
```

### Points Per 60 (P/60)
```
Formula: PTS * 3600 / TOI_seconds
```

### Shots Per 60 (SOG/60)
```
Formula: SOG * 3600 / TOI_seconds
```

---

## Goalie Stats

### Shots Against (SA)
```
Source: fact_events_player
Filter: Type = 'Save' AND player_role = 'event_player_1'
```

### Goals Against (GA)
```
Source: fact_events_player
Filter: Type = 'Goal' AND player_role IN ('opp_player_1', 'away_goalie', 'home_goalie')
```

### Saves (SV)
```
Formula: SA - GA
```

### Save Percentage (SV%)
```
Formula: SV / SA * 100
```

### Goals Against Average (GAA)
```
Formula: GA * 3600 / TOI_seconds
```

---

## Defender Stats (from opp_player_1)

### Defender Targets
```
Source: fact_events_player
Filter: player_role = 'opp_player_1'
Note: How often this player was the primary defender on an event
```

### Entries Allowed
```
Source: fact_events_player
Filter: event_detail CONTAINS 'Zone_Entry' AND player_role = 'opp_player_1'
```

### Shots Against (as defender)
```
Source: fact_events_player
Filter: Type = 'Shot' AND player_role = 'opp_player_1'
```

---

## Turnover Quality

| Quality | Description | Counts Against |
|---------|-------------|----------------|
| BAD | Player error (misplay, bad pass) | Yes |
| NEUTRAL | Normal play (shot blocked, battle lost) | No |
| GOOD | Intentional (dump, clear) | No |

Used in: GIVE_BAD calculation, turnover differential
