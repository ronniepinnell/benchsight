# BenchSight Collaborative Validation Plan

**Goal:** Walk through each table together, validate logic, calculations, and data quality.

---

## Session Structure

For each table, we will:

1. **Purpose** - What is this table for? What business question does it answer?
2. **Source** - Where does the data come from? (BLB, tracking files, calculated)
3. **Key Fields** - Walk through important columns and their logic
4. **Sample Data** - Look at actual rows together
5. **Calculations** - Verify formulas are correct
6. **Cross-Checks** - Compare to source data / other tables
7. **Issues Found** - Document anything wrong
8. **Sign-Off** - Mark as validated or needs fix

---

## Validation Order

### Phase 1: Master Dimensions (Source of Truth)
These are the foundation - if these are wrong, everything is wrong.

| # | Table | Source | Priority |
|---|-------|--------|----------|
| 1 | dim_player | BLB_Tables.xlsx | Critical |
| 2 | dim_team | BLB_Tables.xlsx | Critical |
| 3 | dim_schedule | BLB + noradhockey.com | Critical |

### Phase 2: Event Taxonomy Dimensions
The classification system for all events.

| # | Table | Source | Priority |
|---|-------|--------|----------|
| 4 | dim_event_type | Hardcoded + BLB | High |
| 5 | dim_event_detail | BLB_Tables.xlsx | High |
| 6 | dim_event_detail_2 | BLB_Tables.xlsx | High |
| 7 | dim_play_detail | BLB_Tables.xlsx | High |
| 8 | dim_play_detail_2 | BLB_Tables.xlsx | High |

### Phase 3: Core Fact Tables
The raw data from tracking files.

| # | Table | Source | Priority |
|---|-------|--------|----------|
| 9 | fact_events | Tracking Excel files | Critical |
| 10 | fact_shifts | Tracking Excel files | Critical |
| 11 | fact_gameroster | BLB + Tracking | Critical |

### Phase 4: Derived Statistics
Aggregated/calculated from core facts.

| # | Table | Source | Priority |
|---|-------|--------|----------|
| 12 | fact_player_game_stats | Calculated from fact_events | Critical |
| 13 | fact_team_game_stats | Aggregated from player stats | High |
| 14 | fact_goalie_game_stats | Calculated from fact_events | High |

### Phase 5: Season Aggregates
Roll-ups of game-level stats.

| # | Table | Source | Priority |
|---|-------|--------|----------|
| 15 | fact_player_season_stats | Sum of game stats | Medium |
| 16 | fact_team_season_stats | Sum of game stats | Medium |

---

## Questions to Answer for Each Table

### Data Quality
- Are there unexpected nulls?
- Are there duplicate keys?
- Do all FK references resolve?

### Logic
- Does the calculation make sense?
- Is the formula implemented correctly?
- Are edge cases handled?

### Completeness
- Are all expected rows present?
- Are all expected columns present?
- Is the data coverage adequate?

### Accuracy
- Do totals match source data?
- Do aggregates match detail rows?
- Does it match external sources (noradhockey.com)?

---

## Ready to Start?

Let's begin with **dim_player** - the player master dimension.

When ready, I'll show you:
1. The table structure
2. Sample data
3. Source comparison
4. Any issues found

Then we discuss and decide: ✅ Valid or ❌ Needs Fix
