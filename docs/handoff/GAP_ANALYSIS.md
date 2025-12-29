# BenchSight v6.1 - Gap Analysis

## Executive Summary

**Current State**: 58 tables (39 dims, 19 facts), sequence/play logic built but not integrated
**Gap**: 5 missing tables, 11 missing columns, 9 missing stats, logic not yet in ETL

---

## Table Status

### ✅ Tables We Have (19 Fact Tables)

| Table | Rows | Status |
|-------|------|--------|
| fact_events | 7,834 | Complete |
| fact_events_player | 24,089 | Missing sequence/play columns |
| fact_shifts | 770 | Complete |
| fact_shifts_player | 5,539 | Has logical shift columns |
| fact_sequences | 946 | Generated but not from current logic |
| fact_plays | 3,390 | Generated but not from current logic |
| fact_player_boxscore_all | 14,473 | Complete for basic stats |
| fact_player_game_stats | 129 | Missing 9 stats |
| fact_goalie_game_stats | 11 | Needs verification |
| fact_team_game_stats | 15 | Complete |
| fact_team_standings_snapshot | 1,124 | Complete |
| fact_league_leaders_snapshot | 14,473 | Complete |
| fact_gameroster | - | Complete |
| fact_draft | - | Complete |
| fact_registration | - | Complete |
| fact_playergames | - | Complete |
| fact_head_to_head | - | Basic version |
| fact_leadership | - | Complete |
| fact_player_pair_stats | - | Basic version |

### ❌ Missing Tables (5)

| Table | Purpose | How to Build | Priority |
|-------|---------|--------------|----------|
| fact_event_chains | Entry→Shot→Goal timing | Trace zone entries to shots/goals, calculate time between | High |
| fact_team_zone_time | Zone time per team | Sum event durations by zone per game | Medium |
| fact_h2h | Player X vs Player Y | Match events where both players on ice | Medium |
| fact_wowy | With/without analysis | Compare stats when linemate present vs absent | Medium |
| fact_line_vs_line | Line matchups | Match shifts by line combination | Low |

---

## Column Gaps

### fact_events_player - Missing 11 Columns

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| sequence_id | FK | ETL | FK to fact_sequences |
| play_id | FK | ETL | FK to fact_plays |
| sequence_index_auto | INT | ETL | Auto-generated sequence number |
| play_index_auto | INT | ETL | Auto-generated play number |
| is_rush | BOOL | ETL | Zone entry → shot within 5 events |
| rush_type | VARCHAR | ETL | breakaway, odd_man_2v1, even_3v3 |
| is_cycle | BOOL | ETL | 3+ consecutive o-zone passes |
| chain_id | VARCHAR | ETL | Event chain identifier |
| turnover_quality_id | FK | Lookup | FK to dim_turnover_quality |
| caused_by_turnover | BOOL | ETL | Possession started from turnover |
| sequence_result | VARCHAR | ETL | goal, shot, turnover, stoppage |

### fact_player_game_stats - Missing 9 Stats

| Stat | Formula | Source |
|------|---------|--------|
| shifts | COUNT(shifts) | fact_shifts_player |
| shots_on_goal | COUNT(Shot where detail contains 'OnNet' or 'Goal') | fact_events_player |
| faceoffs_won | COUNT(Faceoff where player_role = event_player_1) | fact_events_player |
| faceoffs_lost | COUNT(Faceoff where player_role = opp_player_1) | fact_events_player |
| corsi_for | COUNT(Shot/Goal for team while on ice) | fact_events + fact_shifts |
| corsi_against | COUNT(Shot/Goal against while on ice) | fact_events + fact_shifts |
| plus_es | Goals for at even strength | fact_shifts (home_team_plus) |
| plus_all | All goals for while on ice | fact_shifts (shift_stop_type) |
| goals_per_60 | goals * 60 / toi_seconds | Derived |

---

## Logic Gaps

### 1. Rush Detection
```
Definition: Zone entry followed by shot (same team) within 5 events
Types: breakaway, odd_man_2v1, odd_man_3v2, even_2v2, even_3v3
Status: Logic defined, not implemented
```

### 2. Cycle Detection
```
Definition: 3+ consecutive passes in o-zone without zone exit
Status: Logic defined, not implemented
```

### 3. Event Chain Timing
```
Definition: Time/events between zone_entry → shot → goal
Purpose: xG model input
Status: Not implemented
```

### 4. Skill Differential
```
Definition: Player rating vs opponent rating context
Purpose: "Goal vs 4.5 line different than goal vs 5.5 line"
Status: Not implemented
```

---

## Integration Gaps

### Sequence/Play Generator
- **File**: `src/sequence_play_generator.py`
- **Status**: Built and tested, NOT integrated into ETL
- **Output**: sequence_index_auto, play_index_auto columns
- **Action**: Call from main ETL, add columns to fact_events

### Validated Rules (from txt file)
- 115 stats validated in previous session
- Rules documented in VALIDATION_LOG.tsv
- **Action**: Ensure all rules applied in stat calculation

---

## Data Quality Gaps

### Columns to Remove
- All columns ending in `_` (underscore) - these are manual flags from tracking
- 29 underscore columns in events sheet
- 0 underscore columns in shifts sheet (already clean)

### Terminology Mapping
- dim_terminology_mapping has 84 rows
- Maps old terms to current dim table values
- **Action**: Apply during ETL load

---

## Priority Matrix

| Priority | Item | Effort | Impact |
|----------|------|--------|--------|
| P0 | Integrate sequence_play_generator | Medium | High |
| P0 | Add missing 9 stats | Medium | High |
| P1 | Rush/cycle detection | Medium | Medium |
| P1 | fact_event_chains | Medium | High (xG) |
| P2 | fact_team_zone_time | Low | Medium |
| P2 | fact_h2h, fact_wowy | High | Medium |
| P3 | Skill differential | Medium | Medium |
| P3 | fact_line_vs_line | High | Low |

---

## Validation Checklist

Before any delivery:
1. [ ] Run scripts/verify_delivery.py
2. [ ] Check goal counts match NORAD website
3. [ ] Verify TOI > 0 for players with events
4. [ ] Confirm sequence counts reasonable (~270/game)
5. [ ] Validate play counts (~740/game)
6. [ ] Check no underscore columns in output
