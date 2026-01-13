# fact_team_season_stats_basic - Validation Report

**Validated:** 2026-01-13  
**Version:** v28.7  
**Status:** ✅ VALIDATED

---

## Table Overview

| Property | Value |
|----------|-------|
| **Table Name** | `fact_team_season_stats_basic` |
| **Description** | Team performance aggregates by season and game type |
| **Purpose** | Standings, team comparisons, season summaries |
| **Source** | dim_schedule (record/goals), fact_gameroster (roster stats) |
| **Source Module** | `src/tables/macro_stats.py:create_fact_team_season_stats_basic()` |
| **Logic** | Aggregate schedule by team+season+game_type; join roster for player counts |
| **Grain** | One row per team + season + game_type |
| **Row Count** | 123 |
| **Column Count** | 21 |

---

## Column Documentation

| Column | Type | Description | Source | Calculation | Type | Validated |
|--------|------|-------------|--------|-------------|------|-----------|
| team_season_basic_key | TEXT | Primary key | Generated | `{team_id}_{season_id}_{game_type}` | Derived | ✅ |
| team_id | TEXT | Team identifier | dim_team | FK lookup | FK | ✅ |
| team_name | TEXT | Team display name | fact_gameroster | Denormalized | Explicit | ✅ |
| season_id | TEXT | Season identifier | dim_schedule | FK lookup | FK | ✅ |
| season | TEXT | Season year code | fact_gameroster | e.g., "20232024" | Explicit | ✅ |
| game_type | TEXT | Regular/Playoffs/All | dim_schedule | Filter criteria | Derived | ✅ |
| games_played | INT | Total games | dim_schedule | COUNT(home) + COUNT(away) | Calculated | ✅ |
| wins | INT | Games won | dim_schedule | home_goals > away_goals OR vice versa | Calculated | ✅ |
| losses | INT | Games lost | dim_schedule | games_played - wins - ties | Calculated | ✅ |
| ties | INT | Games tied | dim_schedule | SUM(home_team_t) + SUM(away_team_t) | Calculated | ✅ |
| win_pct | FLOAT | Win percentage | Calculated | wins / games_played * 100 | Calculated | ✅ |
| points | INT | Standing points | Calculated | wins*2 + ties*1 | Calculated | ✅ |
| goals_for | INT | Goals scored | dim_schedule | SUM(home_total_goals when home) + SUM(away_total_goals when away) | Calculated | ✅ |
| goals_against | INT | Goals allowed | dim_schedule | SUM(away_total_goals when home) + SUM(home_total_goals when away) | Calculated | ✅ |
| goal_diff | INT | Goal differential | Calculated | goals_for - goals_against | Calculated | ✅ |
| goals_for_per_game | FLOAT | GF rate | Calculated | goals_for / games_played | Calculated | ✅ |
| goals_against_per_game | FLOAT | GA rate | Calculated | goals_against / games_played | Calculated | ✅ |
| team_goals | INT | Sum of player goals | fact_gameroster | SUM(goals) for skaters, NULL if game_type != 'All' | Calculated | ✅ |
| team_assists | INT | Sum of player assists | fact_gameroster | SUM(assist) for skaters, NULL if game_type != 'All' | Calculated | ✅ |
| team_pim | INT | Sum of PIM | fact_gameroster | SUM(pim) for skaters, NULL if game_type != 'All' | Calculated | ✅ |
| unique_players | INT | Distinct players | fact_gameroster | COUNT(DISTINCT player_id), NULL if game_type != 'All' | Calculated | ✅ |

---

## Validation Checks

### Data Quality
| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| Row count | ~120 | 123 | ✅ |
| No duplicate keys | 0 | 0 | ✅ |
| wins + losses + ties = games_played | All rows | All rows | ✅ |
| Tie count matches schedule | 110 (55 games × 2 teams) | 110 | ✅ |

### Calculation Verification
| Calculation | Formula | Sample Check | Status |
|-------------|---------|--------------|--------|
| goal_diff | goals_for - goals_against | All rows match | ✅ |
| goals_for_per_game | goals_for / games_played | All rows match | ✅ |
| points | wins*2 + ties*1 | All rows match | ✅ |

### Cross-Table Consistency
| Check | Source | Target | Match |
|-------|--------|--------|-------|
| Tie count | dim_schedule (55 tie games) | fact_team_season_stats_basic (110 tie records) | ✅ |
| Season IDs | dim_season | fact_team_season_stats_basic | ✅ |

---

## Sample Data

### By Game Type (AMOS N20232024F)
| game_type | GP | W | L | T | Pts | GF | GA |
|-----------|----|----|---|---|-----|-----|-----|
| Regular | 29 | 15 | 11 | 3 | 33 | 139 | 115 |
| Playoffs | 6 | 4 | 2 | 0 | 8 | 24 | 14 |
| All | 35 | 19 | 13 | 3 | 41 | 163 | 129 |

### Teams with Most Ties
| Team | Season | Ties |
|------|--------|------|
| Triple J | N20232024F | 5 |
| Nelson | N20242025F | 5 |
| HollowBrook | N20242025F | 5 |

---

## Issues Found & Fixed

| Issue | Severity | Description | Fix |
|-------|----------|-------------|-----|
| ~~nan season_id~~ | HIGH | Scrimmage teams had null season_id | Use dim_schedule as primary source |
| ~~Wrong games_played~~ | CRITICAL | Counted ALL seasons, not per-season | Added season_id filter |
| ~~Missing game_type~~ | HIGH | No Regular vs Playoffs split | Added game_type to grain |
| ~~Missing ties~~ | MEDIUM | Ties not tracked | Added ties column from schedule |
| ~~Wrong points~~ | MEDIUM | points = wins*2 (ignored ties) | Fixed: wins*2 + ties*1 |

---

## Sign-Off

| Reviewer | Date | Verdict |
|----------|------|---------|
| Ronnie + Claude | 2026-01-13 | ✅ VALIDATED |

---

## Notes

- Roster stats (team_goals, team_assists, team_pim, unique_players) are only available for game_type='All' because BLB roster data is season-level, not split by game type
- Points system: Win=2, Tie=1, Loss=0 (no OT loss point in this league)
- 55 games ended in ties (Regulation with equal score)
