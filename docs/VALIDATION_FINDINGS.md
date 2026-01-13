# BenchSight Validation Findings

**Version:** v23.0  
**Date:** 2026-01-11

---

## Executive Summary

Field-level validation in progress. **v23.0 applied ETL fixes** for column cleanup and goalie stats bug. Currently validating fact_event_players (11,155 rows, 156 columns).

| Table | Rows | Cols | Status | Notes |
|-------|------|------|--------|-------|
| dim_player | 337 | 20 | ✅ VALID | Cleaned (removed 7 CSAH cols) |
| dim_team | 17 | 13 | ✅ VALID | Filtered to NORAD only |
| dim_schedule | 567 | 37 | ✅ VALID | Cleaned (removed 7 video cols) |
| dim_event_type | 23 | 7 | ✅ VALID | No changes needed |
| fact_events | 5,823 | 130 | ⚠️ PENDING | Game 18977 missing 1 goal (tracking) |
| fact_event_players | 11,155 | 156 | 🔄 IN PROGRESS | Validating now |
| fact_goalie_game_stats | 8 | 19 | ✅ FIXED | Per-goalie attribution corrected |

---

## v23.0 Fixes Applied

### Column Cleanup (Root-Cause)
| Table | Before | After | Removed |
|-------|--------|-------|---------|
| dim_player | 27 cols | 20 cols | 7 CSAH columns (all 100% null) |
| dim_team | 26 rows, 14 cols | 17 rows, 13 cols | CSAHA teams + csah_team col |
| dim_schedule | 44 cols | 37 cols | 7 video/team_game_id columns |

### Key Format Standardization (Root-Cause)
| Key | Old Format | New Format |
|-----|------------|------------|
| event_player_key | `EP18969_EV1896901000_1` | `EP189690100001` |
| shift_player_id | `SH1896900001_away_F1` | `SP1896900001AF1` |

### Goalie Stats Bug Fix (Root-Cause)
- **Issue:** Both goalies had identical stats (total saves/goals divided by 2)
- **Fix:** Use `team_venue` column to attribute per-goalie
  - Home goalie: events where `team_venue='a'` (opponent shots)
  - Away goalie: events where `team_venue='h'` (opponent shots)
- **Verification:**
  | Game | Goalie | Team | Home | GA | Saves | SV% |
  |------|--------|------|------|-----|-------|-----|
  | 18969 | Francis Forte | Platinum | ✓ | 3 | 37 | 92.5% |
  | 18969 | Wyatt Crandall | Velodrome | ✗ | 4 | 21 | 84.0% |

---

## fact_event_players Validation (In Progress)

**Table:** 11,155 rows, 156 columns, 4 games

### Column Group 1: Keys & Identifiers (Validated)

| # | Column | Null% | Status | Notes |
|---|--------|-------|--------|-------|
| 1 | event_player_key | 0% | ✅ | PK (new format: `EP189690100001`) |
| 2 | game_id | 0% | ✅ | FK to dim_schedule |
| 3 | event_id | 0% | ✅ | FK to fact_events |
| 4 | event_index | 0% | ✅ | Used in key generation |
| 5 | player_id | 1.6% | ⚠️ | 177 nulls - tracking errors (see below) |
| 6 | player_role | 0.2% | ⚠️ | 22 nulls - system events |
| 7 | player_game_number | 0.2% | ✅ | Jersey number |
| 8 | sequence_key | 0% | ✅ | Groups related events |
| 9 | play_key | 0% | ✅ | Groups play sequences |
| 10 | event_chain_key | 0% | ✅ | Chains events |
| 11 | tracking_event_key | 0% | ✅ | Original tracker key |

### Null player_id Analysis (177 rows)

**Root Cause:** Tracking errors - jersey numbers not in roster

| Jersey | Game | Team(s) | Count | Issue |
|--------|------|---------|-------|-------|
| #84 | 18977 | Both | 111 | Not in roster |
| #33 | 18977 | Both | 41 | Not in roster |
| #41 | 18969 | Platinum | 1 | Not in roster |
| #48 | 18969 | Velodrome | 1 | Not in roster |
| N/A | Various | - | ~23 | System events (expected) |

**Action:** Add to tracking error log. Not an ETL bug.

### Duplicate Row Found (Tracker Bug)

Event `EV1897701368` (Game 18977):
- Galen Wood (P100161) appears as `event_player_1` **twice** - identical rows
- **Action:** Fix in tracking file or add dedup logic

---

## Known Tracking Errors

| Game | Issue | Status |
|------|-------|--------|
| 18977 | Missing 1 home goal | TO FIX |
| 18977 | Jersey #84 not in roster (111 events) | LOG ONLY |
| 18977 | Jersey #33 not in roster (41 events) | LOG ONLY |
| 18977 | Galen Wood duplicate row | TO FIX |
| 18969 | Jersey #41 not in roster (1 event) | LOG ONLY |
| 18969 | Jersey #48 not in roster (1 event) | LOG ONLY |

---

## Deferred Items

| Item | Reason |
|------|--------|
| Jared Wolf (P100096) as goalie | Special case - per user request |
| Taxonomy sync (117 values) | Cosmetic - doesn't break analytics |

---

## Next Columns to Validate

**All key fact tables validated ✅**

Remaining tables for future validation:
- fact_shift_players
- fact_tracking
- fact_sequences, fact_plays, fact_event_chains
- Other derived analytics tables

---

## Completed Column Groups

### fact_gameroster, fact_player_game_stats, fact_team_game_stats (v23.3)

All validated with 0 empty columns, no fixes needed.

---

### fact_shifts Validation (v23.3)

**Summary:** 399 rows, 132 columns, 0 empty columns

**FK Fix:**
| Column | Before | After | Fix |
|--------|--------|-------|-----|
| start_zone_id | 0% | 97.7% | Map zone names→ZN01/02/03 |
| end_zone_id | 0% | 97.7% | Map zone names→ZN01/02/03 |

**Expected Low Fill (6v5 only):**
- home_xtra, away_xtra, *_xtra_id: 0.5-1.3%

---

### fact_events Validation (v23.2)

**Summary:** 5,823 rows, 131 → 125 columns

**FK Fixes:**
| Column | Before | After | Fix |
|--------|--------|-------|-----|
| success_id | 0% | 26.9% | Map True→SC01, False→SC02 |
| event_zone_id | 0% | 100% | Map Offensive/Defensive/Neutral→ZN01/02/03 |
| strength_id | 0% | 100% | Direct map from strength column |
| shot_type_id | 0% | 6.9% | Strip Shot_/Goal_ prefix |
| pass_type_id | 0% | 14.8% | Strip Pass_ prefix |

**Rating Fixes:**
| Column | Before | After |
|--------|--------|-------|
| event_team_avg_rating | 0% | 99.6% |
| opp_team_avg_rating | 0% | 99.6% |
| rating_vs_opp | 0% | 98.8% |

**Removed Columns (2):**
- team_venue_abv (unused), player_toi (player-level)

---

### fact_event_players Validation (v23.1)

**Summary:** 11,155 rows, 156 → 140 columns
All key columns validated. player_team derived, key formats standardized.

### Group 2: FK Columns ✅
All FK values that are populated resolve to valid dimension records (100% integrity).

### Group 3: Event Details ✅
| Column | Status | Notes |
|--------|--------|-------|
| event_type | ✅ | Core field |
| team | ❌ REMOVED | Duplicate of team_venue |
| Type | ❌ REMOVED | Duplicate of event_type |
| period, home_team, away_team | ✅ | Core fields |
| strength, event_team_zone | ✅ | Core fields |
| event_start/end_min/sec | ✅ | Time fields |
| event_detail, event_detail_2 | ✅ | Detail fields |
| event_successful, is_highlight | ✅ | Flag fields |
| linked_event_index_flag | ⚠️ KEPT | Values don't map to valid event indices. Raw tracking provides flag but not linked_event_index. Note for future tracker update. |

### Group 4: XY Coordinates ✅
- 42 columns for spatial tracking (puck_x/y, player_x/y, net_x/y)
- Currently ~0.04% populated (5 rows)
- Kept as placeholder for future spatial tracking feature

### Group 5: Time Columns ✅
| Column | Status | Notes |
|--------|--------|-------|
| period, period_id | ✅ | Core |
| event_start/end_min/sec | ✅ | Clock time |
| time_start/end_total_seconds | ✅ | Countdown clock (start > end is expected) |
| duration | ✅ | 0-124 sec |
| running_video_time | ✅ | 2 negative (Intermission - expected) |
| time_bucket_id | ✅ | TB01-TB05 |
| time_to/from_* columns | ✅ | Use -1 as sentinel for N/A |

**TOI Columns - FIXED:**
| Column | Before | After | Notes |
|--------|--------|-------|-------|
| player_toi | 1.6% | 90.1% | Shift TOI (time on ice this shift) |
| team_on_ice_toi_avg | 32.8% | 99.8% | Teammates avg shift TOI (excl goalies) |
| team_on_ice_toi_min | 32.8% | 99.8% | Teammates min shift TOI |
| team_on_ice_toi_max | 32.8% | 99.8% | Teammates max shift TOI |
| opp_on_ice_toi_avg | 68.7% | 99.8% | Opponents avg shift TOI (excl goalies) |
| opp_on_ice_toi_min | 68.7% | 99.8% | Opponents min shift TOI |
| opp_on_ice_toi_max | 68.7% | 99.8% | Opponents max shift TOI |
| event_player_1-6_toi | - | ❌ REMOVED | Unused in player-level table |
| opp_player_1-6_toi | - | ❌ REMOVED | Unused in player-level table |

### Group 6: Derived Columns ✅
**Core Fields (100%):** event_index, event_type, home_team, away_team, strength, event_team_zone, is_highlight, team_venue, player_team, home_team_zone, away_team_zone, is_goal, is_cycle

**Player Fields (~99%):** player_role, player_game_number, role_abrev_binary, side_of_puck, player_name, player_rating

**Event Details (partial):** event_detail, event_detail_2, event_successful, play_detail1, pressured_pressurer

**Rating Columns - FIXED:**
| Column | Before | After | Notes |
|--------|--------|-------|-------|
| event_team_avg_rating | 0% | 99.8% | Teammates avg rating (excl goalies) |
| opp_team_avg_rating | 0% | 99.8% | Opponents avg rating (excl goalies) |
| rating_vs_opp | 0% | 98.4% | player_rating - opp_team_avg_rating |

**Turnover Columns - FIXED:**
| Column | Before | After | Notes |
|--------|--------|-------|-------|
| turnover_weight | 0% | 97.8% (of turnovers) | Giveaway=0.8, Takeaway=1.2 |
| turnover_zone_multiplier | 0% | 97.8% (of turnovers) | Zone danger factor |
| turnover_category | 0% | 97.8% (of turnovers) | 'giveaway' or 'takeaway' |

**Removed:**
- play_detail2 (duplicate of play_detail_2)

---

*Validation session: 2026-01-11*
