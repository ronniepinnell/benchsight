# ETL Changes Summary - January 2026

## Overview
This document summarizes all ETL changes made during this session, including fixes to data accuracy, added columns, and improved aggregations.

---

## 1. fact_rushes Enhancement

### Changes Made
- **Added supporting player lists:**
  - `event_supporting_player_ids`: Comma-separated list of `event_player_2` through `event_player_6` player IDs
  - `opp_supporting_player_ids`: Comma-separated list of `opp_player_2` through `opp_player_6` player IDs

- **Added opponent player 1 individual columns:**
  - `opp_player_1_id`: Player ID of the primary opponent player
  - `opp_player_1_name`: Name of the primary opponent player (lookup from `fact_event_players` or `dim_player`)
  - `opp_player_1_rating`: Rating of the primary opponent player (lookup from `fact_event_players` or `dim_player`)

### Files Modified
- `src/core/base_etl.py` - `create_derived_event_tables()` function

### Implementation Notes
- Player lists prioritize `event_player_1_id` and `opp_player_1_id` at the beginning
- Name/rating lookups try `fact_event_players` first, then fall back to `dim_player`
- All lists stored as comma-separated strings

---

## 2. fact_saves Enhancement

### Changes Made
- **Added goalie columns (from event_player_1):**
  - `goalie_player_id`: Player ID of the goalie who made the save
  - `goalie_name`: Name of the goalie
  - `goalie_rating`: Rating of the goalie

- **Added shooter columns (from opp_player_1):**
  - `shooter_player_id`: Player ID of the shooter
  - `shooter_name`: Name of the shooter
  - `shooter_rating`: Rating of the shooter

- **Added context columns:**
  - `is_cycle`, `cycle_key`: Whether save was part of a cycle play
  - `is_rush`, `is_rush_calculated`: Whether save was part of a rush play
  - `is_zone_entry`, `is_zone_exit`, `zone_entry_type_id`: Zone transition context
  - `is_rebound`: Whether this was a rebound save
  - `is_pre_shot_event`, `is_shot_assist`: Shot sequence context
  - `time_to_next_sog`, `time_since_last_sog`: Shot timing context
  - `events_to_next_sog`, `events_since_last_sog`: Event sequence context
  - `play_key`, `sequence_key`, `event_chain_key`: Play/sequence identifiers
  - `time_from_zone_entry`: **NEW** - Time (in seconds) from the most recent zone entry by the shooting team to this save

### Files Modified
- `src/core/base_etl.py` - `create_derived_event_tables()` function

### Implementation Notes
- Context columns are already present in `fact_events` (saves are filtered from events)
- `time_from_zone_entry` is calculated by looking backwards through events to find the most recent zone entry by the shooting team (opposite of goalie's team) before the save

---

## 3. fact_events Segment Numbers

### Changes Made
Added segment number columns to indicate position within different groupings:

- `play_segment_number`: Position within a play (1, 2, 3, ...) based on `play_key`
- `sequence_segment_number`: Position within a sequence (1, 2, 3, ...) based on `sequence_key`
- `event_chain_segment_number`: Position within an event chain (1, 2, 3, ...) based on `event_chain_key`
- `linked_event_segment_number`: Position within linked events (1, 2, 3, ...) based on `linked_event_key`

### Files Modified
- `src/core/base_etl.py` - `enhance_events_with_flags()` function

### Implementation Notes
- Events are sorted by `game_id`, `time_start_total_seconds`, and `event_id` before grouping
- Segment numbers start from 1 for the first event in each grouping
- Null for events not part of the corresponding grouping

---

## 4. Shot Events Player Columns

### Changes Made
Added labeled player columns for shot events:

- **Shooter columns (all shot events):**
  - `shooter_player_id`: From `event_player_1`
  - `shooter_name`: From `event_player_1`
  - `shooter_rating`: From `event_player_1`

- **Shot blocker columns (blocked shots only):**
  - `shot_blocker_player_id`: From `opp_player_1` when `is_blocked_shot == 1`
  - `shot_blocker_name`: From `opp_player_1`
  - `shot_blocker_rating`: From `opp_player_1`

- **Goalie columns (saved shots and goals):**
  - `goalie_player_id`: Goalie who saved the shot (from `opp_player_1` for saved shots) or allowed the goal (from `opp_player_1` for goals)
  - `goalie_name`: Goalie name
  - `goalie_rating`: Goalie rating

### Files Modified
- `src/core/base_etl.py` - `enhance_events_with_flags()` function

### Implementation Notes
- Shooter is always `event_player_1` for Shot/Goal events
- Shot blocker is `opp_player_1` for blocked shots
- Goalie is `opp_player_1` for saved shots (saves from shooting team's perspective) and for goals (goalie who allowed it)

---

## 5. fact_shift_quality - Logical Shifts

### Changes Made
- Updated to aggregate on logical shifts instead of `shift_index`
- Groups by `game_id`, `player_id`, and `logical_shift_number` to create one quality record per logical shift

### Files Modified
- `src/tables/shift_analytics.py` - `create_fact_shift_quality()` function

### Implementation Notes
- Uses `logical_shift_number` to identify actual shift changes where line composition changes
- Aggregates `shift_duration` and `pm_all` across multiple `shift_index` rows that belong to the same logical shift
- Falls back to `shift_index` if `logical_shift_number` is not available

---

## 6. fact_team_game_stats - Fixed Shots & Period Breakdowns

### Changes Made
- **Fixed shot counting:**
  - Changed from counting both 'shot' and 'goal' events (which double-counted goals)
  - Now counts only 'shot' events (including `Shot_Goal` which is a shot that scored)
  - Goals are tracked separately and deduplicated by `event_id`

- **Added period breakdowns:**
  - `p1_shots`, `p1_sog`, `p1_goals`, `p1_giveaways`, `p1_takeaways`, `p1_blocks`, `p1_hits`
  - `p2_shots`, `p2_sog`, `p2_goals`, `p2_giveaways`, `p2_takeaways`, `p2_blocks`, `p2_hits`
  - `p3_shots`, `p3_sog`, `p3_goals`, `p3_giveaways`, `p3_takeaways`, `p3_blocks`, `p3_hits`

### Files Modified
- `src/builders/team_stats.py` - `calculate_team_stats_from_events()` function

### Implementation Notes
- Shot counting now properly avoids double-counting goals
- Period breakdowns calculated by filtering events by `period` column
- Block counting uses deduplication by `event_id` to avoid double-counting linked events

---

## 7. Special Teams Corsi - Fixed Double-Counting & Period Breakdowns

### Changes Made
- **Fixed PP/PK corsi double-counting:**
  - Now groups by `logical_shift_number` before aggregating to avoid counting the same shift multiple times
  - Uses `first()` aggregation for shift-level stats (CF, CA, GF, GA) which are the same for all players on the same logical shift

- **Added period breakdowns for PP and PK:**
  - `pp_p1_cf`, `pp_p1_ca`, `pp_p1_cf_pct`, `pp_p1_toi_seconds`, `pp_p1_gf`, `pp_p1_ga`
  - `pp_p2_...`, `pp_p3_...` (same pattern)
  - `pk_p1_...`, `pk_p2_...`, `pk_p3_...` (same pattern)

### Files Modified
- `src/tables/core_facts.py` - `calculate_strength_splits()` function

### Implementation Notes
- Uses `logical_shift_number` grouping to ensure each logical shift is counted only once
- Falls back to `shift_index` if `logical_shift_number` is not available
- Period breakdowns only for PP and PK (not EV or EN)

---

## 8. Remove 100% Null Columns from Fact Tables

### Changes Made
- **Updated `drop_all_null_columns()` function:**
  - Now preserves coordinate, danger, and XY type columns even if 100% null
  - Preserved patterns include: `x`, `y`, `coord`, `danger`, `xy`, `target_x`, `target_y`, `shot_x`, `shot_y`, `net_target`, `location_id`, `zone_coord`, `rink_coord`

- **Integrated into all `save_table()` functions:**
  - `src/tables/core_facts.py`
  - `src/tables/event_analytics.py`
  - `src/tables/shift_analytics.py`
  - `src/tables/remaining_facts.py`
  - `src/core/table_writer.py` (for `fact_` tables)

### Files Modified
- `src/core/base_etl.py` - `drop_all_null_columns()` function
- All `save_table()` implementations across table modules

### Implementation Notes
- Automatically removes 100% null columns when saving fact tables
- Coordinate/danger/XY columns are preserved for potential future use even if currently empty
- Logs which columns were removed for each table

---

## 9. fact_wowy - Fixed Apart Stats & Added Shift Counts

### Changes Made
- **Fixed apart stats calculation:**
  - Changed from filtering to single player rows, then grouping
  - Now iterates through each logical shift where P1 is without P2 (and vice versa)
  - Properly aggregates shift-level stats (CF, CA, GF, GA) from logical shifts
  - Uses `logical_shift_duration` if available, otherwise sums first segments

- **Added total shift count columns:**
  - `p1_total_shifts`: Total logical shifts for player 1
  - `p2_total_shifts`: Total logical shifts for player 2

### Files Modified
- `src/tables/shift_analytics.py` - `create_fact_wowy()` function

### Implementation Notes
- Apart stats now use the same logical shift aggregation pattern as H2H (which works correctly)
- Iterates through logical shifts properly to aggregate stats instead of using `.first()` on grouped data
- Shift counts already used logical shifts, but now includes explicit total counts for reference

---

## Summary of Files Modified

1. `src/core/base_etl.py`
   - Updated `drop_all_null_columns()` to preserve coordinate/danger/xy columns
   - Enhanced `fact_rushes` with supporting players and opp_player_1 columns
   - Enhanced `fact_saves` with goalie/shooter columns and context info
   - Added segment numbers to `fact_events`
   - Added shooter/blocker/goalie columns for shot events

2. `src/builders/team_stats.py`
   - Fixed shot counting to avoid double-counting goals
   - Added period breakdowns for shots, SOG, goals, giveaways, takeaways, blocks, hits

3. `src/tables/core_facts.py`
   - Updated `calculate_strength_splits()` to use logical shifts and add period breakdowns
   - Updated `save_table()` to drop null columns

4. `src/tables/shift_analytics.py`
   - Updated `create_fact_shift_quality()` to use logical shifts
   - Fixed `create_fact_wowy()` apart stats calculation
   - Added total shift counts to WOWY
   - Updated `save_table()` to drop null columns

5. `src/tables/event_analytics.py`
   - Updated `save_table()` to drop null columns

6. `src/tables/remaining_facts.py`
   - Updated `save_table()` to drop null columns

7. `src/core/table_writer.py`
   - Added null column removal for `fact_` tables

---

## Questions for User

1. **fact_saves time_from_zone_entry calculation:**
   - Currently looks for zone entries by the shooting team (opposite of goalie's team) within 60 seconds before the save. Is this the correct logic, or should it be calculated differently?

2. **Shot events goalie attribution:**
   - For saved shots, goalie is set from `opp_player_1` (on defending team). Is this correct, or should we link to the corresponding Save event to get the actual goalie?

3. **fact_team_game_stats period breakdowns:**
   - Added period breakdowns for shots, SOG, goals, giveaways, takeaways, blocks, hits. Should other stats also have period breakdowns (e.g., CF, CA, zone time, etc.)?

4. **Special teams period breakdowns:**
   - Added period breakdowns for PP and PK. Should we also add period breakdowns for EV (even strength)?

5. **Null column removal:**
   - The coordinate/danger/XY column preservation uses regex patterns. Are there any other column naming patterns that should be preserved even if 100% null?

6. **WOWY apart stats:**
   - The apart stats now aggregate shift-level stats from logical shifts. Should apart stats represent team stats during those shifts (current implementation) or individual player stats when apart? The current implementation matches the "together" stats which are shift-level.

---

## Testing Recommendations

1. **Verify shot counts:**
   - Compare `fact_team_game_stats.shots` with sum of `fact_player_game_stats.shots` to ensure no double-counting
   - Verify goals are not included in shot counts

2. **Verify special teams corsi:**
   - Check that PP/PK corsi values are reasonable (not super high)
   - Compare period breakdowns sum to total PP/PK stats

3. **Verify WOWY stats:**
   - Check that apart stats are not all zeros
   - Verify `shifts_together + p1_shifts_without_p2 <= p1_total_shifts` (and similar for P2)

4. **Verify period breakdowns:**
   - Check that `p1_* + p2_* + p3_* = total_*` for team stats

5. **Verify null column removal:**
   - Confirm coordinate/danger/xy columns are preserved even if null
   - Check that other 100% null columns are removed

---

## Next Steps

After running the ETL:
1. Review the changes to ensure values are reasonable
2. Verify period breakdowns sum correctly
3. Check that special teams stats are no longer inflated
4. Confirm WOWY apart stats have non-zero values where expected
5. Verify shot counts are accurate and not double-counting goals
