# BenchSight Future Column Ideas

Last Updated: 2026-01-12
Version: 26.1

This document catalogs potential new statistics and columns that could be added to BenchSight based on available data in the tracking system.

---

## ✅ IMPLEMENTED - Phase 3 (v26.1)

### Linemate Analysis (8 columns) ✅
Implemented in `calculate_linemate_stats()`. See DATA_DICTIONARY.md for details.

### Time Bucket Analysis (11 columns) ✅
Implemented in `calculate_time_bucket_stats()`. See DATA_DICTIONARY.md for details.
Note: early/late_period_cf_pct are placeholders (need shift-level time buckets).

### Rebound/Second Chance (7 columns) ✅
Implemented in `calculate_rebound_stats()`. See DATA_DICTIONARY.md for details.
Note: crash_net_success is placeholder (needs sequence analysis).

---

## 🎯 Priority 2: Medium Value, Some Work Required

### Defensive Detail (~12 columns)
Granular defensive contributions.

| Column | Description | Source |
|--------|-------------|--------|
| `shots_blocked_hd` | High danger shots blocked | danger_level + block |
| `shots_blocked_slot` | Slot shots blocked | zone + block |
| `lane_denials` | Passing lanes cut | play_detail |
| `gap_control_events` | Gap control plays | play_detail |
| `man_coverage_events` | Man-on-man coverage | play_detail |
| `force_wide_events` | Forced attacks wide | play_detail |
| `defensive_stick_lifts` | Stick lifts on D | play_detail |
| `body_positioning` | Body position plays | play_detail |
| `recovery_speed` | Defensive recoveries | sequence timing |
| `penalty_drawn` | Penalties drawn | event_type = Penalty |
| `penalties_taken` | Penalties committed | event_type = Penalty |
| `net_penalty` | Drawn - Taken | Calculated |

**Implementation Notes:**
- Many play_detail values exist for these
- Need to map specific codes to categories

### Cycle/Possession (~8 columns)
Track sustained offensive pressure.

| Column | Description | Source |
|--------|-------------|--------|
| `cycle_events` | Events in cycle plays | is_cycle |
| `cycle_shots` | Shots from cycles | is_cycle + shot |
| `cycle_goals` | Goals from cycles | is_cycle + goal |
| `cycle_duration` | Time in cycle possession | cycle_key |
| `cycle_started` | Cycles initiated | is_sequence_first + cycle |
| `cycle_finished` | Cycles completed with shot | is_sequence_last + cycle |
| `cycle_efficiency` | Shots per cycle | Calculated |
| `possession_chains` | Consecutive team events | consecutive_team_events |

**Implementation Notes:**
- is_cycle and cycle_key exist in fact_events
- Track individual involvement in cycles

### Entry/Exit Detail (~10 columns)
More granular zone transition data.

| Column | Description | Source |
|--------|-------------|--------|
| `entries_with_speed` | Rush entries | zone_entry_type |
| `entries_with_pass` | Pass entries | zone_entry_type |
| `entries_dump_chase` | Dump and chase | zone_entry_type |
| `entries_failed` | Failed entry attempts | event_detail |
| `exits_stretch_pass` | Stretch pass exits | zone_exit_type |
| `exits_skate` | Carry exits | zone_exit_type |
| `exits_clear` | Clear exits | zone_exit_type |
| `exits_failed` | Failed exit attempts | event_detail |
| `neutral_zone_time` | Time in NZ | zone tracking |
| `transition_speed` | Entry-to-shot time | time_from_entry_to_shot |

**Implementation Notes:**
- zone_entry_type_id and zone_exit_type_id exist
- time_from_entry_to_shot already calculated

---

## 🎯 Priority 3: Advanced Analytics

### Expected Assists (xA) Model (~4 columns)
Value of passing that leads to shots.

| Column | Description | Calculation |
|--------|-------------|-------------|
| `xa_generated` | Expected assists | Pass xG value |
| `assists_above_expected` | Actual - xA | Finishing luck |
| `pass_danger_added` | xG boost from pass | Pre/post pass xG diff |
| `primary_xa` | xA on primary assists | Higher weight |

**Implementation Notes:**
- Use shot xG and attribute portion to passer
- Weight by pass type and location

### Defensive xG Against (xGA) (~4 columns)
Quality of chances allowed while on ice.

| Column | Description | Calculation |
|--------|-------------|-------------|
| `xg_against` | xG of shots against | Sum opponent shot xG |
| `xg_against_per_60` | Rate stat | Normalized |
| `goals_prevented` | xGA - GA | Defensive impact |
| `defensive_impact` | xGA vs team avg | Relative |

**Implementation Notes:**
- Apply xG model to opponent shots
- Track by player on-ice

### RAPM-Style Regression (~6 columns)
Regularized adjusted plus-minus.

| Column | Description | Calculation |
|--------|-------------|-------------|
| `rapm_offense` | Offensive impact | Ridge regression |
| `rapm_defense` | Defensive impact | Ridge regression |
| `rapm_total` | Total impact | Combined |
| `rapm_rank` | League rank | Percentile |
| `rapm_vs_replacement` | vs replacement level | Baseline adjusted |
| `rapm_uncertainty` | Confidence interval | Standard error |

**Implementation Notes:**
- Requires multiple seasons of data
- Need sufficient sample size
- Ridge regression implementation

---

## 🎯 Priority 4: Future / Complex

### Video-Derived Metrics
Require video analysis or XY coordinates.

| Column | Description | Requirement |
|--------|-------------|-------------|
| `skating_speed_avg` | Average skating speed | XY tracking |
| `top_speed` | Maximum speed | XY tracking |
| `distance_skated` | Total distance | XY tracking |
| `shot_release_time` | Quick release | Video timing |
| `shot_velocity` | Shot speed | Radar/video |
| `pass_velocity` | Pass speed | Video timing |
| `reaction_time` | Defensive reaction | Video analysis |

### Team Context (~6 columns)
Performance relative to team.

| Column | Description | Source |
|--------|-------------|--------|
| `team_cf_pct_on` | Team CF% with player | Shift analysis |
| `team_cf_pct_off` | Team CF% without player | Shift analysis |
| `on_off_cf_diff` | Impact on team | Calculated |
| `usage_rate` | % of team TOI | toi / team_toi |
| `leverage_index` | High leverage minutes | Close games |
| `deployment_score` | How player is used | Zone starts + QoC |

---

## 📊 Column Count Summary

| Category | Potential Columns |
|----------|-------------------|
| Linemate Analysis | 10 |
| Time Bucket Analysis | 8 |
| Rebound/Second Chance | 6 |
| Defensive Detail | 12 |
| Cycle/Possession | 8 |
| Entry/Exit Detail | 10 |
| Expected Assists | 4 |
| Defensive xGA | 4 |
| RAPM | 6 |
| Video-Derived | 8 |
| Team Context | 6 |
| **TOTAL POTENTIAL** | **82** |

**Current v25.2:** 303 skater columns, 37 goalie columns
**With all future:** 385+ skater columns

---

## 🔧 Implementation Notes

### Data Already Available
These columns can be added immediately from existing data:
- Linemate analysis (from fact_shifts)
- Time bucket analysis (from time_bucket_id)
- Rebound stats (from is_rebound)
- Cycle stats (from is_cycle, cycle_key)
- Entry/exit detail (from type IDs)

### Requires Model Development
- xA (expected assists) - need to build pass value model
- Defensive xGA - need opponent shot attribution
- RAPM - need regression framework

### Requires Additional Data
- Video-derived metrics need XY coordinates or video analysis
- Some team context needs broader data aggregation

---

## 📝 Notes for Implementation

1. **Batch additions**: Add related columns together (e.g., all linemate stats at once)
2. **Backward compatible**: New columns should have sensible defaults (0 or null)
3. **Document immediately**: Add to DATA_DICTIONARY with each batch
4. **Validate**: Add tests for new calculations
5. **Performance**: Consider query impact of 300+ column tables

---

*This document should be updated as columns are implemented or new ideas emerge.*
