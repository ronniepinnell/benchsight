# dim_team - Validation Documentation

**Status:** ✅ VALIDATED  
**Date:** 2026-01-10  
**Reviewers:** Ronnie + Claude

---

## Table Overview

| Property | Value |
|----------|-------|
| **Table Name** | `dim_team` |
| **Type** | Dimension (Master Reference) |
| **Description** | All teams in the NORAD league |
| **Purpose** | Central lookup for team info; FK target for all team references |
| **Source** | BLB_Tables.xlsx → dim_team sheet |
| **Source Module** | `src/models/master_dims.py` |
| **Logic** | One row per team, filtered to NORAD only |
| **Grain** | One row = One team |
| **Row Count** | 26 → **17 after CSAHA removal** |
| **Column Count** | 14 → **12 after cleanup** |

---

## Column Documentation

| # | Column | Data Type | Type | Description | Source/Calculation | Non-Null | Status |
|---|--------|-----------|------|-------------|-------------------|----------|--------|
| 1 | team_id | TEXT | 🟡 PK | Primary key (N##### for NORAD) | BLB_Tables → dim_team | 26 (100%) | ✅ Keep |
| 2 | team_name | TEXT | 🟢 Explicit | Team short name | BLB_Tables → dim_team | 26 (100%) | ✅ Keep |
| 3 | norad_team | TEXT | 🟢 Explicit | NORAD league flag (Y/N) | BLB_Tables → dim_team | 26 (100%) | ✅ Keep |
| 4 | csah_team | TEXT | 🟢 Explicit | CSAHA league flag (Y/N) | BLB_Tables → dim_team | 26 (100%) | ❌ Remove |
| 5 | league_id | TEXT | 🟣 FK | FK to league dimension | BLB_Tables → dim_team | 26 (100%) | ✅ Keep |
| 6 | league | TEXT | 🟢 Explicit | League name | BLB_Tables → dim_team | 26 (100%) | ✅ Keep |
| 7 | long_team_name | TEXT | 🟢 Explicit | Full team name with sponsor | BLB_Tables → dim_team | 26 (100%) | ✅ Keep |
| 8 | team_cd | TEXT | 🟢 Explicit | Team code/abbreviation | BLB_Tables → dim_team | 26 (100%) | ✅ Keep |
| 9 | team_color1 | TEXT | 🟢 Explicit | Primary team color | BLB_Tables → dim_team | 26 (100%) | ✅ Keep |
| 10 | team_color2 | TEXT | 🟢 Explicit | Secondary team color | BLB_Tables → dim_team | 26 (100%) | ✅ Keep |
| 11 | team_color3 | TEXT | 🟢 Explicit | Tertiary team color | BLB_Tables → dim_team | 23 (88%) | ✅ Keep |
| 12 | team_color4 | TEXT | 🟢 Explicit | Quaternary team color | BLB_Tables → dim_team | 2 (8%) | ✅ Keep |
| 13 | team_logo | TEXT | 🟢 Explicit | Logo image URL | BLB_Tables → dim_team | 26 (100%) | ✅ Keep |
| 14 | team_url | TEXT | 🟢 Explicit | Team page URL | BLB_Tables → dim_team | 26 (100%) | ✅ Keep |

### Type Legend

| Badge | Type | Meaning |
|-------|------|---------|
| 🟢 | Explicit | Directly from source data (BLB) |
| 🟡 | PK | Primary key |
| 🟣 | FK | Foreign key reference |

---

## Teams After Cleanup (17 NORAD Teams)

| team_id | team_name | Type |
|---------|-----------|------|
| N10001 | AMOS | Regular |
| N10002 | Ace | Regular |
| N10003 | HollowBrook | Regular |
| N10004 | Nelson | Regular |
| N10005 | OS Offices | Regular |
| N10006 | Orphans | Regular |
| N10007 | Outlaws | Regular |
| N10008 | Platinum | Regular |
| N10009 | Triple J | Regular |
| N10010 | Velodrome | Regular |
| N10011 | Norad | League/All-Star |
| N10012 | Canada | Special |
| N10022 | Red | Draft/All-Star |
| N10023 | Green | Draft/All-Star |
| N10024 | Blue | Draft/All-Star |
| N10025 | Yellow | Draft/All-Star |
| N10026 | Free Agent | Placeholder |

## Teams Removed (9 CSAHA Teams)

| team_id | team_name |
|---------|-----------|
| C120012 | Patriots |
| C130013 | Angry Dolphins |
| C140014 | Cereal Killers |
| C150015 | Chiefs |
| C160016 | Teal Team 6 |
| C170017 | Banana Havoc |
| C180018 | Sasquatch |
| C190019 | Holligans |
| C200020 | Puck Masters |

---

## Validation Results

### Data Quality ✅

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| Primary key unique | 26 | 26 | ✅ Pass |
| team_name unique | 26 | 26 | ✅ Pass |
| All have URLs | 26 | 26 | ✅ Pass |

---

## Issues Found

| # | Issue | Severity | Description | Action |
|---|-------|----------|-------------|--------|
| 1 | CSAHA teams present | Medium | 9 CSAHA teams not needed | **Filter out in ETL** |
| 2 | csah_team column | Low | Not needed | **Remove column** |
| 3 | AMOS spelling | Fixed | Was "Amos" in some places | **✅ Fixed in new BLB** |

---

## Action Items

### ETL Changes
- [ ] Filter dim_team to `norad_team = 'Y'` only (removes 9 CSAHA teams)
- [ ] Remove `csah_team` column from output

### Source Data ✅
- [x] AMOS spelling standardized in new BLB_Tables.xlsx

### Final Counts
- Teams: 26 → **17**
- Columns: 14 → **13**

---

## Sign-Off

| Reviewer | Date | Verdict |
|----------|------|---------|
| Ronnie | 2026-01-10 | ✅ Validated |
| Claude | 2026-01-10 | ✅ Validated |

**Notes:** Keep special teams (Red, Green, Blue, Yellow, Canada, Norad, Free Agent). Remove CSAHA teams and csah_team column.

---

**Next Table:** dim_schedule
