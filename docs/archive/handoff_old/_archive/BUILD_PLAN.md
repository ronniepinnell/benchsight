# BenchSight Build Plan

## Current State

- **58 tables** (39 dims, 19 facts) in data/output/
- **Sequence/play generator** built, tested, NOT integrated
- **Schema Excel** complete with 15 sheets
- **Gap analysis** complete - 5 missing tables, 11 missing columns, 9 missing stats

---

## Phase 1: Sequence/Play Integration (CRITICAL)

### Priority: P0
### Effort: 2-3 hours
### Impact: High

### Tasks

1. **Integrate sequence_play_generator.py into ETL**
   - Import and call from main ETL pipeline
   - Process all 4 tracked games
   - Generate sequence_index_auto, play_index_auto for each event

2. **Update fact_events**
   - Add columns: sequence_id, play_id, sequence_index_auto, play_index_auto
   - Regenerate from tracking data

3. **Update fact_events_player**
   - Add same columns (denormalized for convenience)
   - Regenerate from tracking data

4. **Regenerate fact_sequences**
   - Use corrected logic (turnover = new sequence)
   - Expected: ~1,076 sequences across 4 games

5. **Regenerate fact_plays**
   - Use corrected logic (zone change = new play)
   - Expected: ~2,732 plays across 4 games

### Validation
- [ ] Avg events per sequence ~5.4 (not 15+)
- [ ] Goal sequences have 10-20 events leading to goal
- [ ] Sequences start on turnovers, faceoffs, stoppages
- [ ] Plays change on zone entry/exit

---

## Phase 2: Stats Completion

### Priority: P0
### Effort: 3-4 hours
### Impact: High

### Tasks

1. **Add missing stats to fact_player_game_stats**
   - shifts: COUNT(DISTINCT shift_index)
   - shots_on_goal: Filter Shot where OnNet or Goal
   - faceoffs_won: Faceoff with event_player_1
   - faceoffs_lost: Faceoff with opp_player_1
   - corsi_for: Shot events while on ice, same team
   - corsi_against: Shot events while on ice, opp team
   - plus_es: SUM(home_team_plus/minus)
   - plus_all: COUNT(Goal shifts)
   - goals_per_60: G * 3600 / TOI

2. **Implement rush detection**
   - Find zone_entry followed by shot within 5 events
   - Add is_rush, rush_type columns to fact_events

3. **Implement cycle detection**
   - Find 3+ consecutive o-zone passes
   - Add is_cycle column to fact_events

4. **Validate against NORAD**
   - Compare goal counts to website
   - Verify player game totals

### Validation
- [ ] TOI > 0 for all players with events
- [ ] Goals match NORAD website
- [ ] Plus/minus balances across teams
- [ ] Corsi totals reasonable

---

## Phase 3: Advanced Tables

### Priority: P1
### Effort: 4-6 hours
### Impact: Medium

### Tasks

1. **fact_event_chains**
   - Track zone_entry → shot → goal chains
   - Calculate time between events
   - Purpose: xG model input

2. **fact_team_zone_time**
   - Sum event durations by zone per team per game
   - Columns: game_id, team_id, ozone_time, dzone_time, nzone_time

3. **fact_h2h (head-to-head)**
   - Match events where both players on ice
   - Calculate stats for Player X vs Player Y

4. **fact_wowy (with/without you)**
   - Compare stats when linemate present vs absent
   - Columns: player_id, teammate_id, stats_with, stats_without

5. **fact_line_vs_line**
   - Match shifts by line combination
   - Full 5v5 matchup analysis

### Validation
- [ ] Event chains trace correctly
- [ ] Zone times sum to ~game length
- [ ] H2H covers all player pairs on ice together

---

## Phase 4: Rating Context

### Priority: P2
### Effort: 2-3 hours
### Impact: Medium

### Tasks

1. **Add skill differential columns**
   - player_rating from dim_player
   - opp_avg_rating (average of opponents on ice)
   - skill_diff = player_rating - opp_avg_rating

2. **Line rating context**
   - line_avg_rating (average of 5 skaters)
   - opp_line_avg_rating
   - Purpose: "Goal vs 4.5 line different than goal vs 5.5 line"

3. **Context-adjusted stats**
   - Points vs higher-rated opponents
   - Upset factor

### Validation
- [ ] Ratings populated from dim_player
- [ ] Skill diff calculated correctly

---

## Phase 5: Tracker Integration

### Priority: P1 (parallel with Phase 2)
### Effort: Ongoing
### Impact: High

### Tasks

1. **Verify tracker output format**
   - JSON matches fact_events_tracking columns
   - Terminology uses current dim table values

2. **ETL handles both sources**
   - Excel tracking files (current)
   - Tracker JSON output (new games)

3. **Same output regardless of source**
   - Identical schema
   - Same stat calculations

---

## Dependency Graph

```
Phase 1 ─────┬───────> Phase 2 ──────> Phase 4
             │
             └───────> Phase 3 ──────> Phase 4
             
Phase 5 runs parallel to all phases
```

---

## Delivery Checklist

Before ANY delivery:

1. [ ] Run `python scripts/verify_delivery.py`
2. [ ] Check goal counts match NORAD website
3. [ ] Verify TOI > 0 for players with events
4. [ ] Confirm sequence counts ~270/game
5. [ ] Validate play counts ~740/game
6. [ ] Check no underscore columns in output
7. [ ] Include ALL files (src/, data/, config/, docs/)
8. [ ] Update HANDOFF.md with changes
9. [ ] Create changelog entry

---

## Success Criteria

### Phase 1 Complete When:
- Sequence/play IDs in all event tables
- fact_sequences has ~1,076 rows
- fact_plays has ~2,732 rows
- Goal sequences make sense (10-20 events)

### Phase 2 Complete When:
- All 9 missing stats populated
- Rush/cycle flags in fact_events
- Stats validated against NORAD

### Phase 3 Complete When:
- All 5 new tables created
- Event chain timing works
- H2H data available

### Phase 4 Complete When:
- Skill differential columns populated
- Rating context in analysis

---

## Timeline Estimate

| Phase | Effort | Dependencies |
|-------|--------|--------------|
| Phase 1 | 2-3 hrs | None |
| Phase 2 | 3-4 hrs | Phase 1 |
| Phase 3 | 4-6 hrs | Phase 1 |
| Phase 4 | 2-3 hrs | Phase 2, 3 |

**Total**: 11-16 hours of focused work
