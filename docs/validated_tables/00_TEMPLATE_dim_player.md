# dim_player - Validation Documentation

**Validated:** ⏳ PENDING  
**Date:** -  
**Reviewer:** Ronnie + Claude

---

## Table Overview

| Property | Value |
|----------|-------|
| **Table Name** | `dim_player` |
| **Type** | Dimension (Reference) |
| **Description** | Master dimension for all players in the NORAD league |
| **Purpose** | Central lookup for player info; FK target for all player references |
| **Source** | BLB_Tables.xlsx → dim_player sheet |
| **Source Module** | `src/models/master_dims.py` |
| **Logic** | One row per unique player from registration data |
| **Grain** | One row = One player |
| **Row Count** | 337 |
| **Column Count** | 27 |

---

## Column Documentation

| # | Column | Data Type | Type | Description | Source/Calculation | Non-Null | Null % |
|---|--------|-----------|------|-------------|-------------------|----------|--------|
| 1 | player_id | TEXT | 🟡 PK | Primary key | Generated: 'P' + 6-digit sequence | 337 | 0% |
| 2 | player_first_name | TEXT | 🟢 Explicit | Player's first name | BLB_Tables → dim_player | 337 | 0% |
| 3 | player_last_name | TEXT | 🟢 Explicit | Player's last name | BLB_Tables → dim_player | 337 | 0% |
| 4 | player_full_name | TEXT | 🔵 Calculated | Full display name | `first_name + ' ' + last_name` | 337 | 0% |
| 5 | player_primary_position | TEXT | 🟢 Explicit | Position (Forward/Defense/Goalie) | BLB_Tables → dim_player | 337 | 0% |
| 6 | current_skill_rating | INT | 🟢 Explicit | Skill level 1-10 | BLB_Tables → dim_player | 337 | 0% |
| 7 | player_hand | TEXT | 🟢 Explicit | Handedness (L/R) | BLB_Tables → dim_player | 0 | 100% |
| 8 | birth_year | INT | 🟢 Explicit | Year of birth | BLB_Tables → dim_player | 190 | 44% |
| 9 | player_gender | TEXT | 🟢 Explicit | Gender (M/F) | BLB_Tables → dim_player | 337 | 0% |
| 10 | highest_beer_league | TEXT | 🟢 Explicit | Highest league played | BLB_Tables → dim_player | 172 | 49% |
| 11 | player_rating_ly | INT | 🟢 Explicit | Last year's rating | BLB_Tables → dim_player | 337 | 0% |
| 12 | player_notes | TEXT | 🟢 Explicit | Admin notes | BLB_Tables → dim_player | 0 | 100% |
| 13 | player_leadership | TEXT | 🟢 Explicit | Leadership role (C/A) | BLB_Tables → dim_player | 28 | 92% |
| 14 | player_norad | TEXT | 🟢 Explicit | NORAD league flag | BLB_Tables → dim_player | 337 | 0% |
| 15 | player_csaha | TEXT | 🟢 Explicit | CSAHA league flag | BLB_Tables → dim_player | 0 | 100% |
| 16 | player_norad_primary_number | INT | 🟢 Explicit | NORAD jersey number | BLB_Tables → dim_player | 0 | 100% |
| 17 | player_csah_primary_number | INT | 🟢 Explicit | CSAHA jersey number | BLB_Tables → dim_player | 0 | 100% |
| 18 | player_norad_current_team | TEXT | 🟣 FK | Current NORAD team name | Lookup from dim_team | 337 | 0% |
| 19 | player_csah_current_team | TEXT | 🟣 FK | Current CSAHA team name | Lookup from dim_team | 0 | 100% |
| 20 | player_norad_current_team_id | TEXT | 🟣 FK | FK to dim_team | dim_team.team_id | 337 | 0% |
| 21 | player_csah_current_team_id | TEXT | 🟣 FK | FK to dim_team | dim_team.team_id | 0 | 100% |
| 22 | other_url | TEXT | 🟢 Explicit | External profile URL | BLB_Tables → dim_player | 13 | 96% |
| 23 | player_url | TEXT | 🟢 Explicit | NORAD profile URL | BLB_Tables → dim_player | 320 | 5% |
| 24 | player_image | TEXT | 🟢 Explicit | Profile image URL | BLB_Tables → dim_player | 337 | 0% |
| 25 | random_player_first_name | TEXT | 🔵 Calculated | Anonymized first name | Random name generator | 337 | 0% |
| 26 | random_player_last_name | TEXT | 🔵 Calculated | Anonymized last name | Random name generator | 337 | 0% |
| 27 | random_player_full_name | TEXT | 🔵 Calculated | Anonymized full name | Random name generator | 337 | 0% |

### Type Legend

| Badge | Type | Meaning |
|-------|------|---------|
| 🟢 | Explicit | Directly from source data (BLB, tracking) |
| 🔵 | Calculated | Computed from other columns |
| 🟡 | Derived | Generated key or transformation |
| 🟣 | FK | Foreign key reference |

---

## Validation Checks

### Data Quality

| Check | Expected | Actual | Status | Notes |
|-------|----------|--------|--------|-------|
| Primary key unique | 337 | 337 | ⏳ | |
| No duplicate names | ~337 | ? | ⏳ | |
| Position values valid | 3 | ? | ⏳ | Forward, Defense, Goalie |
| Rating range 1-10 | Yes | ? | ⏳ | |
| Team FK valid | All | ? | ⏳ | All team_ids exist in dim_team |

### Business Rules

| Rule | Expected | Actual | Status |
|------|----------|--------|--------|
| All NORAD players have Y flag | Yes | ? | ⏳ |
| Jersey numbers 1-99 | Yes | ? | ⏳ |
| Goalies have position=Goalie | Yes | ? | ⏳ |

### Cross-Table Consistency

| Check | This Table | Related Table | Match? |
|-------|------------|---------------|--------|
| Team IDs | player_norad_current_team_id | dim_team.team_id | ⏳ |
| Player in roster | player_id | fact_gameroster.player_id | ⏳ |

---

## Sample Data

| player_id | player_full_name | player_primary_position | current_skill_rating | player_norad_current_team |
|-----------|------------------|------------------------|----------------------|---------------------------|
| P100001 | Sam Downs | Forward | 6 | Velodrome |
| P100002 | Kevin White | Forward | 4 | Velodrome |
| P100003 | Scott Purdy | Goalie | 5 | Platinum |
| P100004 | Cesar Shinall | Forward | 4 | HollowBrook |
| P100005 | John-Michael Sebben | Forward | 2 | Outlaws |

---

## Issues Found

| # | Issue | Severity | Description | Recommended Action |
|---|-------|----------|-------------|-------------------|
| 1 | 100% null columns | Low | player_hand, player_notes, player_csaha, etc. | Remove or populate |
| 2 | ? | ? | ? | ? |

---

## Discussion Notes

*To be filled during validation session*

---

## Sign-Off

| Reviewer | Date | Verdict | Notes |
|----------|------|---------|-------|
| Ronnie | - | ⏳ Pending | |
| Claude | - | ⏳ Pending | |

---

**Next Table:** dim_team
