# dim_schedule - Validation Documentation

**Status:** ✅ VALIDATED  
**Date:** 2026-01-10  
**Reviewers:** Ronnie + Claude

---

## Table Overview

| Property | Value |
|----------|-------|
| **Table Name** | `dim_schedule` |
| **Type** | Dimension (Reference) |
| **Description** | All scheduled games across all NORAD seasons |
| **Purpose** | Game master data; FK target for all game references; official score source |
| **Source** | BLB_Tables.xlsx → dim_schedule sheet (scraped from noradhockey.com) |
| **Source Module** | `src/models/master_dims.py` |
| **Logic** | One row per game from league schedule |
| **Grain** | One row = One game |
| **Row Count** | 567 |
| **Column Count** | 44 → **37 after cleanup** |

---

## Column Documentation

| # | Column | Data Type | Type | Description | Source/Calculation | Non-Null | Status |
|---|--------|-----------|------|-------------|-------------------|----------|--------|
| 1 | game_id | INT | 🟡 PK | Primary key - unique game identifier | noradhockey.com game ID | 567 (100%) | ✅ Keep |
| 2 | season | INT | 🟢 Explicit | Season in YYYYYYYY format | noradhockey.com | 567 (100%) | ✅ Keep |
| 3 | season_id | TEXT | 🟣 FK | FK to dim_season | Derived from season | 567 (100%) | ✅ Keep |
| 4 | game_url | TEXT | 🟢 Explicit | URL to game page | noradhockey.com | 567 (100%) | ✅ Keep |
| 5 | home_team_game_id | INT | 🟢 Explicit | Home team's game sequence # | noradhockey.com | 567 (100%) | ❌ Remove |
| 6 | away_team_game_id | INT | 🟢 Explicit | Away team's game sequence # | noradhockey.com | 567 (100%) | ❌ Remove |
| 7 | date | DATETIME | 🟢 Explicit | Game date | noradhockey.com | 567 (100%) | ✅ Keep |
| 8 | game_time | TEXT | 🟢 Explicit | Game start time | noradhockey.com | 86 (15%) | ✅ Keep |
| 9 | home_team_name | TEXT | 🟣 FK | Home team name | Lookup from dim_team | 567 (100%) | ✅ Keep |
| 10 | away_team_name | TEXT | 🟣 FK | Away team name | Lookup from dim_team | 567 (100%) | ✅ Keep |
| 11 | home_team_id | TEXT | 🟣 FK | FK to dim_team | dim_team.team_id | 567 (100%) | ✅ Keep |
| 12 | away_team_id | TEXT | 🟣 FK | FK to dim_team | dim_team.team_id | 567 (100%) | ✅ Keep |
| 13 | head_to_head_id | TEXT | 🔵 Calculated | Matchup identifier | Sorted team_id combination | 567 (100%) | ✅ Keep |
| 14 | game_type | TEXT | 🟢 Explicit | Regular or Playoffs | noradhockey.com | 567 (100%) | ✅ Keep |
| 15 | playoff_round | TEXT | 🟢 Explicit | Playoff round (if applicable) | noradhockey.com | 54 (10%) | ✅ Keep |
| 16 | last_period_type | TEXT | 🟢 Explicit | How game ended (REG/OT/SO) | noradhockey.com | 567 (100%) | ✅ Keep |
| 17 | period_length | INT | 🟢 Explicit | Minutes per period | noradhockey.com | 567 (100%) | ✅ Keep |
| 18 | ot_period_length | INT | 🟢 Explicit | OT period length | noradhockey.com | 566 (100%) | ✅ Keep |
| 19 | shootout_rounds | INT | 🟢 Explicit | # of shootout rounds | noradhockey.com | 121 (21%) | ✅ Keep |
| 20 | home_total_goals | INT | 🟢 Explicit | **OFFICIAL** home team goals | noradhockey.com | 567 (100%) | ✅ Keep |
| 21 | away_total_goals | INT | 🟢 Explicit | **OFFICIAL** away team goals | noradhockey.com | 567 (100%) | ✅ Keep |
| 22 | home_team_period1_goals | INT | 🟢 Explicit | Home P1 goals | noradhockey.com | 363 (64%) | ✅ Keep |
| 23 | home_team_period2_goals | INT | 🟢 Explicit | Home P2 goals | noradhockey.com | 366 (65%) | ✅ Keep |
| 24 | home_team_period3_goals | INT | 🟢 Explicit | Home P3 goals | noradhockey.com | 362 (64%) | ✅ Keep |
| 25 | home_team_periodOT_goals | INT | 🟢 Explicit | Home OT goals | noradhockey.com | 128 (23%) | ✅ Keep |
| 26 | away_team_period1_goals | INT | 🟢 Explicit | Away P1 goals | noradhockey.com | 366 (65%) | ✅ Keep |
| 27 | away_team_period2_goals | INT | 🟢 Explicit | Away P2 goals | noradhockey.com | 351 (62%) | ✅ Keep |
| 28 | away_team_period3_goals | INT | 🟢 Explicit | Away P3 goals | noradhockey.com | 359 (63%) | ✅ Keep |
| 29 | away_team_periodOT_goals | INT | 🟢 Explicit | Away OT goals | noradhockey.com | 127 (22%) | ✅ Keep |
| 30 | home_team_seeding | INT | 🟢 Explicit | Playoff seeding | noradhockey.com | 40 (7%) | ✅ Keep |
| 31 | away_team_seeding | INT | 🟢 Explicit | Playoff seeding | noradhockey.com | 40 (7%) | ✅ Keep |
| 32 | home_team_w | INT | 🟢 Explicit | Home team wins (at game time) | noradhockey.com | 567 (100%) | ✅ Keep |
| 33 | home_team_l | INT | 🟢 Explicit | Home team losses | noradhockey.com | 567 (100%) | ✅ Keep |
| 34 | home_team_t | INT | 🟢 Explicit | Home team ties/OTL | noradhockey.com | 567 (100%) | ✅ Keep |
| 35 | home_team_pts | INT | 🟢 Explicit | Home team points | noradhockey.com | 567 (100%) | ✅ Keep |
| 36 | away_team_w | INT | 🟢 Explicit | Away team wins | noradhockey.com | 567 (100%) | ✅ Keep |
| 37 | away_team_l | INT | 🟢 Explicit | Away team losses | noradhockey.com | 567 (100%) | ✅ Keep |
| 38 | away_team_t | INT | 🟢 Explicit | Away team ties/OTL | noradhockey.com | 567 (100%) | ✅ Keep |
| 39 | away_team_pts | INT | 🟢 Explicit | Away team points | noradhockey.com | 567 (100%) | ✅ Keep |
| 40 | video_id | TEXT | 🟢 Explicit | YouTube video ID | Manual entry | 0 (0%) | ❌ Remove |
| 41 | video_start_time | TEXT | 🟢 Explicit | Video start timestamp | Manual entry | 0 (0%) | ❌ Remove |
| 42 | video_end_time | TEXT | 🟢 Explicit | Video end timestamp | Manual entry | 0 (0%) | ❌ Remove |
| 43 | video_title | TEXT | 🟢 Explicit | Video title | Manual entry | 0 (0%) | ❌ Remove |
| 44 | video_url | TEXT | 🟢 Explicit | Video URL | Manual entry | 0 (0%) | ❌ Remove |

### Type Legend

| Badge | Type | Meaning |
|-------|------|---------|
| 🟢 | Explicit | Directly from source (noradhockey.com) |
| 🔵 | Calculated | Computed from other columns |
| 🟡 | PK | Primary key |
| 🟣 | FK | Foreign key reference |

---

## Validation Results

### Data Quality ✅

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| Primary key unique | 567 | 567 | ✅ Pass |
| home ≠ away team | 0 violations | 0 violations | ✅ Pass |
| Goals ≥ 0 | Yes | Yes | ✅ Pass |

### Goal Validation - Tracked Games ✅

| Game | dim_schedule | noradhockey.com | Match |
|------|--------------|-----------------|-------|
| 18969 | Platinum 4-3 Velodrome | Platinum 4-3 Velodrome | ✅ |
| 18977 | Velodrome 4-2 HollowBrook | Velodrome 4-2 HollowBrook | ✅ |
| 18981 | Nelson 2-1 Velodrome | Nelson 2-1 Velodrome | ✅ |
| 18987 | Outlaws 0-1 Velodrome | Outlaws 0-1 Velodrome | ✅ |

### Season Distribution (Fixed ✅)

| Season | Games |
|--------|-------|
| 20212022 | 98 |
| 20222023 | 133 |
| 20232024 | 130 |
| 20242025 | 120 |
| 20252026 | 85 |
| 2025 | 1 |

### Game Type Distribution

| Type | Games |
|------|-------|
| Regular | 512 |
| Playoffs | 55 |

---

## Critical Business Rule

**`home_total_goals` and `away_total_goals` are the OFFICIAL source of truth for game scores.**

All calculated goal counts from fact_events MUST match these values.

---

## Issues Found

| # | Issue | Severity | Description | Action |
|---|-------|----------|-------------|--------|
| 1 | Weird season values | Fixed | ✅ Fixed in updated BLB | None |
| 2 | Video columns 100% null | Low | Video data in separate table | **Remove 5 columns** |
| 3 | home/away_team_game_id | Low | Not needed | **Remove 2 columns** |

---

## Action Items

### ETL Column Removal
Remove these 7 columns:
- [ ] home_team_game_id
- [ ] away_team_game_id
- [ ] video_id
- [ ] video_start_time
- [ ] video_end_time
- [ ] video_title
- [ ] video_url

### Source Data ✅
- [x] Season values fixed in updated BLB_Tables.xlsx

### Final Counts
- Columns: 44 → **37**

---

## Sign-Off

| Reviewer | Date | Verdict |
|----------|------|---------|
| Ronnie | 2026-01-10 | ✅ Validated |
| Claude | 2026-01-10 | ✅ Validated |

**Notes:** Essential table. Official source of truth for game scores. Remove video columns (separate table) and team_game_id columns.

---

**Next Table:** dim_event_type
