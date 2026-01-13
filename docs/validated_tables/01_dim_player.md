# dim_player - Validation Documentation

**Status:** ✅ VALIDATED  
**Date:** 2026-01-10  
**Reviewers:** Ronnie + Claude

---

## Table Overview

| Property | Value |
|----------|-------|
| **Table Name** | `dim_player` |
| **Type** | Dimension (Master Reference) |
| **Description** | All players who have ever been in the NORAD league |
| **Purpose** | Central lookup for player info; FK target for all player references |
| **Source** | BLB_Tables.xlsx → dim_player sheet |
| **Source Module** | `src/models/master_dims.py` |
| **Logic** | One row per unique player from registration data |
| **Grain** | One row = One player |
| **Row Count** | 337 |
| **Column Count** | 27 → **20 after cleanup** |

---

## Column Documentation

| # | Column | Data Type | Type | Description | Source/Calculation | Non-Null | Status |
|---|--------|-----------|------|-------------|-------------------|----------|--------|
| 1 | player_id | TEXT | 🟡 PK | Primary key | Generated: 'P' + 6-digit sequence | 337 (100%) | ✅ Keep |
| 2 | player_first_name | TEXT | 🟢 Explicit | Player's first name | BLB_Tables → dim_player | 337 (100%) | ✅ Keep |
| 3 | player_last_name | TEXT | 🟢 Explicit | Player's last name | BLB_Tables → dim_player | 337 (100%) | ✅ Keep |
| 4 | player_full_name | TEXT | 🔵 Calculated | Full display name | `first_name + ' ' + last_name` | 337 (100%) | ✅ Keep |
| 5 | player_primary_position | TEXT | 🟢 Explicit | Position: Forward, Defense, Goalie | BLB_Tables → dim_player | 337 (100%) | ✅ Keep |
| 6 | current_skill_rating | INT | 🟢 Explicit | Skill level 2-6 | BLB_Tables → dim_player | 337 (100%) | ✅ Keep |
| 7 | player_hand | TEXT | 🟢 Explicit | Handedness (L/R) | BLB_Tables → dim_player | 0 (0%) | ❌ Remove |
| 8 | birth_year | INT | 🟢 Explicit | Year of birth | BLB_Tables → dim_player | 190 (56%) | ✅ Keep |
| 9 | player_gender | TEXT | 🟢 Explicit | Gender (M/F) | BLB_Tables → dim_player | 337 (100%) | ✅ Keep |
| 10 | highest_beer_league | TEXT | 🟢 Explicit | Highest league played | BLB_Tables → dim_player | 172 (51%) | ✅ Keep |
| 11 | player_rating_ly | INT | 🟢 Explicit | Last year's rating | BLB_Tables → dim_player | 337 (100%) | ✅ Keep |
| 12 | player_notes | TEXT | 🟢 Explicit | Admin notes | BLB_Tables → dim_player | 0 (0%) | ❌ Remove |
| 13 | player_leadership | TEXT | 🟢 Explicit | Leadership role (C/A) | BLB_Tables → dim_player | 28 (8%) | ✅ Keep |
| 14 | player_norad | TEXT | 🟢 Explicit | NORAD league flag (always Y) | BLB_Tables → dim_player | 337 (100%) | ✅ Keep |
| 15 | player_csaha | TEXT | 🟢 Explicit | CSAHA league flag | BLB_Tables → dim_player | 0 (0%) | ❌ Remove |
| 16 | player_norad_primary_number | INT | 🟢 Explicit | NORAD jersey number | BLB_Tables → dim_player | 0 (0%) | ❌ Remove |
| 17 | player_csah_primary_number | INT | 🟢 Explicit | CSAHA jersey number | BLB_Tables → dim_player | 0 (0%) | ❌ Remove |
| 18 | player_norad_current_team | TEXT | 🟣 FK | Current NORAD team name | Lookup from dim_team | 337 (100%) | ✅ Keep |
| 19 | player_csah_current_team | TEXT | 🟣 FK | Current CSAHA team name | Lookup from dim_team | 0 (0%) | ❌ Remove |
| 20 | player_norad_current_team_id | TEXT | 🟣 FK | FK to dim_team | dim_team.team_id | 337 (100%) | ✅ Keep |
| 21 | player_csah_current_team_id | TEXT | 🟣 FK | FK to dim_team | dim_team.team_id | 0 (0%) | ❌ Remove |
| 22 | other_url | TEXT | 🟢 Explicit | External profile URL (EliteProspects, etc.) | BLB_Tables → dim_player | 13 (4%) | ✅ Keep |
| 23 | player_url | TEXT | 🟢 Explicit | NORAD profile URL | BLB_Tables → dim_player | 320 (95%) | ✅ Keep |
| 24 | player_image | TEXT | 🟢 Explicit | Profile image URL | BLB_Tables → dim_player | 337 (100%) | ✅ Keep |
| 25 | random_player_first_name | TEXT | 🔵 Calculated | Anonymized first name | Random name generator | 337 (100%) | ✅ Keep |
| 26 | random_player_last_name | TEXT | 🔵 Calculated | Anonymized last name | Random name generator | 337 (100%) | ✅ Keep |
| 27 | random_player_full_name | TEXT | 🔵 Calculated | Anonymized full name | Random name generator | 337 (100%) | ✅ Keep |

### Type Legend

| Badge | Type | Meaning |
|-------|------|---------|
| 🟢 | Explicit | Directly from source data (BLB) |
| 🔵 | Calculated | Computed from other columns |
| 🟡 | PK/Derived | Primary key or generated value |
| 🟣 | FK | Foreign key reference |

---

## Validation Results

### Data Quality ✅

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| Primary key unique | 337 | 337 | ✅ Pass |
| No null names | 0 nulls | 0 nulls | ✅ Pass |
| Position values valid | 3 values | 3 values | ✅ Pass |
| Skill rating range | 2-6 | 2-6 | ✅ Pass |

### Value Distributions

**Position:**
| Position | Count | % |
|----------|-------|---|
| Forward | 224 | 66% |
| Defense | 86 | 26% |
| Goalie | 27 | 8% |

**Skill Rating:**
| Rating | Count |
|--------|-------|
| 2 | 52 |
| 3 | 78 |
| 4 | 97 |
| 5 | 89 |
| 6 | 21 |

**Current Team:**
| Team | Count |
|------|-------|
| Free Agent | 165 |
| Nelson | 21 |
| Triple J | 19 |
| HollowBrook | 18 |
| Outlaws | 18 |
| Ace | 17 |
| Velodrome | 16 |
| Platinum | 16 |
| Orphans | 16 |
| OS Offices | 16 |
| AMOS | 14 |
| Amos | 1 |

---

## Issues Found

| # | Issue | Severity | Description | Action |
|---|-------|----------|-------------|--------|
| 1 | CSAH columns 100% null | Low | 7 columns for unused CSAHA league | **Remove columns** |
| 2 | AMOS vs Amos | Low | Team name casing inconsistency (14 vs 1) | **Fix in source BLB** |
| 3 | player_hand 100% null | Low | Handedness not tracked | **Remove column** |
| 4 | player_notes 100% null | Low | Notes not used | **Remove column** |

---

## Action Items

### Source Data Fix (BLB_Tables.xlsx)
- [ ] Standardize "Amos" → "AMOS" in dim_player sheet

### ETL Column Removal
Remove these 9 columns from dim_player output:
- [ ] player_hand
- [ ] player_notes
- [ ] player_csaha
- [ ] player_norad_primary_number
- [ ] player_csah_primary_number
- [ ] player_csah_current_team
- [ ] player_csah_current_team_id

### Final Column Count
- Before: 27 columns
- After: **20 columns**

---

## Sign-Off

| Reviewer | Date | Verdict |
|----------|------|---------|
| Ronnie | 2026-01-10 | ✅ Validated |
| Claude | 2026-01-10 | ✅ Validated |

**Notes:** Essential table. Logic is correct. Remove CSAH-related and unused columns.

---

**Next Table:** dim_team
