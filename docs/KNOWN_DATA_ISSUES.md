# BenchSight Known Data Issues

This document tracks known data quality issues that are **source data problems**, not ETL bugs.

## ✅ Resolved Issues

### ISSUE-001: Game 18977 Missing Goal Scorer (RESOLVED)

**Status:** ✅ RESOLVED  
**Resolved:** 2025-12-29  

**Original Issue:** Galen Wood (P100161) was incorrectly assigned as `event_team_player_2` (assister) instead of `event_team_player_1` (scorer) for event 1368.

**Resolution:** Source file `18977_tracking.xlsx` was corrected - Galen Wood now properly credited as scorer.

**Verification:** Game 18977 now shows 6/6 goals ✅

---

## Warnings (Non-Critical)

### ISSUE-002: Incomplete Tracking Files

**Status:** EXPECTED - Awaiting Tracking  
**Severity:** INFO  

**Description:**
Several game folders contain tracking template files but no actual tracked data. These games cannot be loaded until they are tracked.

**Games with Incomplete Tracking:**
| Game ID | Matchup | Score | Status |
|---------|---------|-------|--------|
| 18965 | Velodrome vs OS Offices | 2-4 | Template only (0.1% filled) |
| 18991 | Triple J vs Velodrome | 1-5 | Template only (0.1% filled) |
| 19032 | Outlaws vs Velodrome | 3-6 | Template only (0.1% filled) |

**Indicators of Incomplete Tracking:**
- `Type` column: <5% filled
- `player_id` column: 0% filled
- Goal events: 0

**Resolution:**
These games need to be tracked using the game tracker before they can be loaded into the ETL.

---

### ISSUE-003: Assists Not Tracked in All Games

**Status:** EXPECTED BEHAVIOR  
**Severity:** LOW  

**Description:**
Assists are only tracked in games where the tracker recorded them in `play_detail` column with "Assist" pattern. Currently only 2/4 loaded games have assist data.

**Games with Assists:**
- 18969: 6 assists ✓
- 18987: 2 assists ✓

**Games without Assists:**
- 18977: 0 assists (not tracked)
- 18981: 0 assists (not tracked)

**Impact:**
- Assist totals incomplete
- Points totals incomplete

**Resolution:**
Future tracking should include assist notation in `play_detail` field using pattern: `AssistPrimary` or `OffensivePlay_Pass-AssistPrimary`.

---

### ISSUE-003: 48 Zero Columns Due to Missing Source Data

**Status:** EXPECTED - Source Data Limitation  
**Severity:** INFO  

**Description:**
48 stat columns are all zeros because the required source data is not captured:

**XY-Dependent (12 columns):**
- No XY coordinates in event tracking
- Affects: shot_danger_*, zone heatmaps

**Score State (6 columns):**
- No running score tracked
- Affects: goals_leading, goals_trailing, goals_tied

**Special Teams (3 columns):**
- EN/SH situations not consistently tagged
- Affects: empty_net_goals_for, shorthanded_goals

**Micro-Stats (27 columns):**
- Not in current event vocabulary
- Affects: hits, puck_retrievals, etc.

**Resolution:**
Update game tracker to capture this data. Infrastructure is ready in dim_rinkcoordzones (84 zones with danger levels).

---

### ISSUE-004: Incorrect Player Positions in dim_player

**Status:** OPEN - Master Data Issue  
**Severity:** LOW  

**Description:**
Some players have incorrect positions in dim_player, causing false positives in outlier detection.

**Known Incorrect Positions:**
| Player ID | Name | Listed Position | Actual Position |
|-----------|------|-----------------|-----------------|
| P100096 | Jared Wolf | Forward | Goalie |

**Impact:**
- Outlier detection flags goalies with high TOI as skaters
- Position-based analytics may be affected

**Resolution:**
Update player positions in the master BLB_Tables.xlsx dim_player sheet.

---

## Issue Resolution Log

| Issue | Date Discovered | Date Resolved | Resolution |
|-------|-----------------|---------------|------------|
| ISSUE-001 | 2025-12-29 | OPEN | Awaiting source fix |
| ISSUE-002 | 2025-12-29 | N/A | Expected behavior |
| ISSUE-003 | 2025-12-29 | N/A | Source limitation |

---

## How to Report New Issues

1. Run QA suite: `python scripts/qa_comprehensive.py`
2. If CRITICAL failure, investigate root cause
3. Determine if ETL bug or source data issue
4. Document here with:
   - Issue ID (ISSUE-NNN)
   - Status
   - Description
   - Evidence
   - Resolution path
