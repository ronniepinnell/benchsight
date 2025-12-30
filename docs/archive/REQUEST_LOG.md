# BenchSight Request Log

## Session: 2024-12-28

### Request 1: Complete ETL Rebuild (v6.0)
**Summary of User Request:**
1. Rerun ETL on new BLB_Tables.xlsx
2. Fix blank goalie stats
3. Advanced stats/microstats only for tracked games; basic boxscore for all games from NORAD
4. Consolidate confusing duplicate tables (events_long vs events_tracking, etc.)
5. Add possession time, zone time calculations
6. Add team-level boxscores (basic, advanced, micro)
7. Add over-time fact tables (standings snapshots, league leaders by date)
8. Calculate sequences (faceoff/stoppage/turnover boundaries) and plays (zone/possession boundaries)
9. Use player roles properly (event_player_1 = primary, event_player_2 = target, opp_player_1 = defender)
10. Identify cycles, rushes, rush types (odd-man, even)
11. Create event chains to track time between events (entry→shot→goal)
12. Research xG models

**Status:** Partially complete - validation shows inaccuracies

### Request 2: Accuracy Investigation
**Summary:** User reports data still looks "wildly inaccurate"
**Action:** Audit raw tracking data against output stats to find root cause

---

## Known Issues to Investigate
- [ ] Goals by game may not match NORAD
- [ ] Team stats showing NaN team names
- [ ] SOG = Goals (non-goal shots not counted)
- [ ] Pass % = 0 for all teams
- [ ] Some games show 0 goals despite having tracking data

### Finding: Goal Double-Counting Root Cause
**Date:** 2024-12-28
**Issue:** Goals counted at 2x (14 vs 7 for game 18969)
**Root Cause:** 
- Each goal creates TWO consecutive events with DIFFERENT event_index values
- Shot_Goal at index N, Goal_Scored at index N+1
- Deduplicating by event_index doesn't work
**Solution:** Count only Goal_Scored events + Shot_OnNetTippedGoal NOT followed by Goal_Scored

---

### Finding: Multiple Bugs in Stat Calculations
**Date:** 2024-12-28

**Bug 1: role_number comparison**
- Data stores role_number as '1.0' (string with decimal)
- Code compared to '1' (no decimal)
- Result: All role_number filtered stats = 0

**Bug 2: Assists not in tracking data**
- Goal events don't have event_team_player_2/3 for assists
- Assists must come from fact_gameroster (NORAD source)

**Bug 3: Goal double-counting (previously found)**
- Shot_Goal and Goal_Scored are separate events
- Solution: Use event_type='Goal' only

---

### Request: Logical Shift Tracking
**Date:** 2024-12-28
**Summary:** Add logical shift columns to fact_shifts_player to track actual shift duration vs segments caused by stoppages

**New columns added:**
- `logical_shift_number` - Increments when player comes OFF then back ON ice, OR period changes
- `shift_segment` - Segment number within a logical shift (1, 2, 3...)
- `cumulative_shift_duration` - Running total of duration within a logical shift

**Logic:**
- Consecutive shift_indices + same period = same logical shift
- Gap in shift_index = new logical shift
- Period change = new logical shift

**Use case:** Identify extended shifts when team is pinned in zone

**Status:** Complete ✓

### Rule: Success Rate Calculation
**Date:** 2024-12-28
**Rule:** When calculating success rates from event_successful column:
- Only count rows where event_successful is NOT blank
- Ignore blank/null values in denominator
- Example: 3 successful, 3 unsuccessful, 4 blank = 50% (not 30%)

---

### Rule: Save Event Roles
**Date:** 2024-12-28
- event_team_player_1 = Goalie making save (ALWAYS)
- event_team_player_2+ = Defenders making plays (stick check on shooter, etc.)
- Goalies identified via shifts where slot='goalie'

---

### Rule: Linked Event Deduplication
**Date:** 2024-12-28
**Rule:** When counting play_details for a player:
- If events are linked (linked_event_index), a player may appear in multiple linked events with same play_detail
- Count play_detail only ONCE per linked event chain
- Example: If StickCheck appears in event 1001 and linked event 1002 for same player, count as 1 StickCheck not 2

---

### Known Issue: Tipped Goal Scoring
**Date:** 2024-12-28
**Issue:** On some tipped goals, the scorer appears as event_team_player_2 on the Goal event instead of player_1
**Example:** Game 18977, Galen Wood - Shot_OnNetTippedGoal (player_1) + Goal_Scored (player_2) at same event_index
**Impact:** May undercount goals by 1-2 per game
**Potential Fix:** If player has Shot_OnNetTippedGoal at same event_index as Goal, count as goal even if player_2
**Status:** Noted - needs resolution

---

### Rule: Plus/Minus Calculation
**Date:** 2024-12-28
**Source:** Shift data, not events
**Logic:**
- Even Strength: Use home_team_plus/home_team_minus columns (excludes PP goals)
- All Goals: Count any shift ending in Home Goal or Away Goal
- Goalies do NOT get plus/minus
- Player must be on ice (check player columns, not goalie column)

**Columns needed:**
- plus_es, minus_es, plus_minus_es (even strength)
- plus_all, minus_all, plus_minus_all (all situations)

**Tracker requirement:** shift_stop_type needs to clarify which team scored and strength

---

### Rule: Goalie GAA Calculation
**Date:** 2024-12-28
**Rule:** 
- Team GAA = total goals against (matches NORAD box score)
- Goalie GAA = excludes goals scored into empty net (when goalie was pulled)
- GAA per 60 = (goals_against_goalie / toi_min) * 60

---

### Session Wrap-Up
**Date:** 2024-12-28
**Completed:**
- Validated 115+ stats across 3 players (Keegan, Wyatt, Hayden)
- Established all counting rules
- Documented plus/minus calculation (ES, All, EN)
- Documented Corsi/Fenwick calculation
- Created comprehensive handoff docs

**Next Session:**
- Rebuild fact_player_game_stats with validated rules
- Build verbiage normalization
- Automated validation for new games
