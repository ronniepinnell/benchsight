# Comprehensive Advanced Stats Views - Summary

**File:** `sql/views/10_comprehensive_advanced_stats_views.sql`  
**Created:** 2026-01-15  
**Purpose:** Efficient, flexible, in-depth dashboard stats for all situations

---

## Overview

This SQL file contains **30+ views and 4 materialized views** covering:
- ✅ All 317 columns from `fact_player_game_stats`
- ✅ All 128 columns from `fact_goalie_game_stats`
- ✅ All situational splits (5v5, PP, PK, periods, game state, competition tier)
- ✅ All micro stats with success rates
- ✅ All advanced metrics (WAR, GAR, xG)
- ✅ Dashboard performance improvements

---

## View Categories

### 1. Comprehensive Season Stats (Section 1)
**`v_player_season_comprehensive`**
- Aggregates all game-level stats to season level
- Handles column name variations (cf/corsi_for, zone_ent/zone_entries, etc.)
- Calculates all percentages and rates
- **Use for:** Player season pages, leaderboards

### 2. Situational Splits (Sections 2-5)

#### Strength Splits (5v5, PP, PK)
**`v_player_stats_by_strength`**
- Separate stats for Even Strength, Power Play, Penalty Kill
- **Use for:** "5v5 Only" filters, PP/PK analysis

#### Period Splits
**`v_player_stats_by_period`**
- Stats broken down by Period 1, 2, 3
- **Use for:** Period performance analysis, clutch stats

#### Game State Splits (Leading, Trailing, Tied)
**`v_player_stats_by_game_state`**
- Stats while leading, trailing, or tied
- **Use for:** Clutch performance, situational analysis

#### Competition Tier Splits (Elite, Good, Average, Weak)
**`v_player_stats_by_competition_tier`**
- Stats vs different quality opponents
- **Use for:** Quality of competition analysis

### 3. Micro Stats with Success Rates (Section 6)
**`v_player_micro_stats_comprehensive`**
- All micro stats (dekes, drives, zone entries/exits, etc.)
- Calculated success rates for each micro stat
- **Use for:** Micro stats explorer page, player compass visualization

### 4. Advanced Metrics (Section 7)
**`v_player_advanced_metrics`**
- WAR/GAR component breakdowns
- xG metrics and goals above expected
- Game Score components
- Rating metrics
- Rankings (percentiles)
- **Use for:** Advanced stats tabs, WAR/GAR pages

### 5. Goalie Comprehensive Stats (Section 8)
**`v_goalie_season_comprehensive`**
- All 128 goalie stat columns aggregated to season
- Save types, danger levels, rebounds, periods, pressure
- Goalie WAR/GAR
- **Use for:** Goalie season pages, goalie leaders

### 6. Goalie Situational Splits (Section 16)
**`v_goalie_stats_by_period`**
- Goalie stats by period
- **Use for:** Goalie period analysis

### 7. Materialized Views - Expensive Operations (Section 9)

#### Career Totals
**`mv_player_career_totals`**
- Career aggregations across all seasons
- Percentiles, peaks, best seasons
- **Refresh:** After each ETL
- **Use for:** Career tabs, all-time leaders

#### Player vs Opponent
**`mv_player_vs_opponent`**
- Stats vs each specific opponent
- Very expensive - uses materialized view
- **Refresh:** Weekly or after ETL
- **Use for:** Matchup analysis, "vs Team X" pages

#### Rolling Averages
**`mv_player_rolling_stats`**
- Last 5, 10, 20 games rolling averages
- **Refresh:** After each ETL (or daily)
- **Use for:** Recent form, trends

#### Career by Situation
**`mv_player_career_by_situation`** (Section 23)
- Career totals broken down by situation (5v5, PP, PK, periods)
- **Refresh:** After each ETL
- **Use for:** Career situational analysis

### 8. League Percentiles (Section 10)
**`v_player_league_percentiles`**
- Percentile rankings for all key stats
- Calculated using `PERCENT_RANK()` window function
- **Use for:** Player comparisons, percentile displays

### 9. Team Advanced Stats (Section 24)
**`v_team_advanced_stats`**
- Team metrics aggregated from players
- Team CF%, FF%, GAR, xG
- Team micro stats
- **Use for:** Team advanced stats tabs

### 10. Rush Analysis (Section 19)
**`v_player_rush_comprehensive`**
- Offensive and defensive rush stats
- Rush success rates, shot/goal generation
- **Use for:** Rush analysis page

### 11. Zone Play Analysis (Section 20)
**`v_player_zone_play_comprehensive`**
- Zone entry/exit stats with success rates
- Entry → shot/goal conversion rates
- **Use for:** Zone play analysis page

### 12. Playmaking Analysis (Section 21)
**`v_player_playmaking_comprehensive`**
- Shot assists, goal creating actions
- Pass types (royal road, cross-ice, etc.)
- Sequence involvement
- **Use for:** Playmaking analysis

### 13. Pressure & Poise (Section 22)
**`v_player_pressure_comprehensive`**
- Pressure handling stats
- Success rates under pressure vs not pressured
- Poise index
- **Use for:** Pressure analysis, poise metrics

### 14. Dashboard Performance Improvements (Section 25)

These views **directly replace JavaScript aggregation** currently done in the dashboard:

#### Possession Stats
**`v_player_possession_aggregated`**
- Replaces: JavaScript `.reduce()` in `players/[playerId]/page.tsx` (lines 143-175)
- **Use:** Instead of fetching all game stats and aggregating in JS

#### Zone Stats
**`v_player_zone_aggregated`**
- Replaces: JavaScript `.reduce()` in `players/[playerId]/page.tsx` (lines 219-241)
- **Use:** Direct query instead of aggregation

#### WAR/GAR Stats
**`v_player_war_gar_aggregated`**
- Replaces: JavaScript `.reduce()` in `players/[playerId]/page.tsx` (lines 264-285)
- **Use:** Pre-aggregated WAR/GAR

#### Physical Stats
**`v_player_physical_aggregated`**
- Replaces: JavaScript aggregation for hits/blocks/takeaways
- **Use:** Direct query

#### Shooting Stats
**`v_player_shooting_aggregated`**
- Replaces: JavaScript aggregation for shots/shooting %
- **Use:** Pre-calculated shooting stats

#### Per-60 Stats
**`v_player_per60_aggregated`**
- Replaces: JavaScript calculation of per-60 rates
- **Use:** Pre-calculated rates

#### Faceoff Stats
**`v_player_faceoff_aggregated`**
- Replaces: JavaScript aggregation
- **Use:** Pre-aggregated faceoff stats

#### Passing Stats
**`v_player_passing_aggregated`**
- Replaces: JavaScript aggregation
- **Use:** Pre-aggregated passing stats

#### Situational Stats
**`v_player_situational_aggregated`**
- Replaces: JavaScript aggregation for 5v5/PP/PK stats
- **Use:** Pre-aggregated situational stats

### 15. Enhanced Current Views (Section 15)

#### Enhanced Standings
**`v_standings_enhanced`**
- Adds team CF%, GAR to existing standings
- **Use:** Improved standings page

#### Enhanced Rankings
**`v_rankings_players_enhanced`**
- Adds percentiles to player rankings
- **Use:** Rankings with percentile bars

#### Game Roster Comprehensive
**`v_game_roster_comprehensive`**
- Adds all player stats to game roster
- **Use:** Boxscores with complete stats

---

## Usage Examples

### Replace JavaScript Aggregation

**Before (JavaScript - Slow):**
```typescript
// Fetch all game stats
const { data: gameStats } = await supabase
  .from('fact_player_game_stats')
  .select('*')
  .eq('player_id', playerId)

// Aggregate in JavaScript
const totals = gameStats.reduce((acc, stat) => {
  return {
    cf: acc.cf + stat.corsi_for,
    ca: acc.ca + stat.corsi_against,
    // ... many calculations
  }
}, { cf: 0, ca: 0, ... })
```

**After (View - Fast):**
```typescript
// Query pre-aggregated view
const { data: possessionStats } = await supabase
  .from('v_player_possession_aggregated')
  .select('*')
  .eq('player_id', playerId)
  .eq('season_id', seasonId)
  .single()

// Data is already aggregated! No JavaScript calculation needed
```

### Situational Splits

**Query 5v5 stats:**
```typescript
const { data } = await supabase
  .from('v_player_stats_by_strength')
  .select('*')
  .eq('player_id', playerId)
  .eq('strength', '5v5')
  .eq('season_id', seasonId)
```

**Query period splits:**
```typescript
const { data } = await supabase
  .from('v_player_stats_by_period')
  .select('*')
  .eq('player_id', playerId)
  .eq('season_id', seasonId)
```

### Micro Stats

**Query micro stats with success rates:**
```typescript
const { data } = await supabase
  .from('v_player_micro_stats_comprehensive')
  .select('*')
  .eq('player_id', playerId)
  .eq('season_id', seasonId)
  .single()

// All success rates are pre-calculated!
// data.deke_success_rate, data.drive_success_rate, etc.
```

### Advanced Metrics

**Query WAR/GAR with components:**
```typescript
const { data } = await supabase
  .from('v_player_advanced_metrics')
  .select('*')
  .eq('player_id', playerId)
  .eq('season_id', seasonId)
  .single()

// All components pre-calculated:
// data.gar_offense, data.gar_defense, data.gar_possession, etc.
```

### Percentiles

**Query percentiles:**
```typescript
const { data } = await supabase
  .from('v_player_league_percentiles')
  .select('*')
  .eq('player_id', playerId)
  .eq('season_id', seasonId)
  .single()

// Percentiles pre-calculated:
// data.points_percentile, data.war_percentile, etc.
```

---

## Materialized View Refresh

After each ETL run, refresh materialized views:

```sql
REFRESH MATERIALIZED VIEW mv_player_career_totals;
REFRESH MATERIALIZED VIEW mv_player_vs_opponent;
REFRESH MATERIALIZED VIEW mv_player_rolling_stats;
REFRESH MATERIALIZED VIEW mv_player_career_by_situation;
```

**Or add to your ETL post-processing script:**
```python
# After ETL completes
supabase.rpc('refresh_all_materialized_views')
```

---

## Performance Benefits

### Before (JavaScript Aggregation)
- ❌ Fetch 50-100 game rows per player
- ❌ Transfer all data to browser
- ❌ Calculate aggregations in JavaScript
- ❌ Slow on mobile devices
- ❌ Doesn't scale with more games

### After (Views)
- ✅ Fetch 1 aggregated row per player
- ✅ Minimal data transfer
- ✅ Pre-calculated in database (fast!)
- ✅ Works great on mobile
- ✅ Scales infinitely

**Expected performance improvement: 10-100x faster**

---

## View Index

### Player Views
1. `v_player_season_comprehensive` - All stats aggregated
2. `v_player_stats_by_strength` - 5v5/PP/PK splits
3. `v_player_stats_by_period` - P1/P2/P3 splits
4. `v_player_stats_by_game_state` - Leading/Trailing/Tied
5. `v_player_stats_by_competition_tier` - Elite/Good/Avg/Weak
6. `v_player_micro_stats_comprehensive` - Micro stats + success rates
7. `v_player_advanced_metrics` - WAR/GAR/xG breakdowns
8. `v_player_passing_comprehensive` - Passing analysis
9. `v_player_shot_types_comprehensive` - Shot type breakdown
10. `v_player_rush_comprehensive` - Rush analysis
11. `v_player_zone_play_comprehensive` - Zone entry/exit analysis
12. `v_player_playmaking_comprehensive` - Playmaking stats
13. `v_player_pressure_comprehensive` - Pressure handling
14. `v_player_league_percentiles` - Percentile rankings
15. `v_player_rolling_averages` - Last 5/10/20 games
16. `v_player_all_seasons` - Multi-season comparison

### Performance Views (Replace JS Aggregation)
17. `v_player_possession_aggregated` - CF%/FF%/xG
18. `v_player_zone_aggregated` - Zone entries/exits
19. `v_player_war_gar_aggregated` - WAR/GAR totals
20. `v_player_physical_aggregated` - Hits/blocks/takeaways
21. `v_player_shooting_aggregated` - Shots/shooting %
22. `v_player_per60_aggregated` - Per-60 rates
23. `v_player_faceoff_aggregated` - Faceoff stats
24. `v_player_passing_aggregated` - Passing stats
25. `v_player_situational_aggregated` - 5v5/PP/PK TOI/goals

### Goalie Views
26. `v_goalie_season_comprehensive` - All goalie stats
27. `v_goalie_stats_by_period` - Period splits
28. `v_goalie_stats_by_strength` - Strength splits

### Team Views
29. `v_team_season_comprehensive` - Team advanced stats
30. `v_team_stats_by_strength` - Team 5v5/PP/PK
31. `v_team_advanced_stats` - Team from player aggregation

### Materialized Views
32. `mv_player_career_totals` - Career aggregations
33. `mv_player_vs_opponent` - Player vs opponent
34. `mv_player_rolling_stats` - Rolling averages
35. `mv_player_career_by_situation` - Career by situation

### Enhanced Current Views
36. `v_standings_enhanced` - Standings with advanced metrics
37. `v_rankings_players_enhanced` - Rankings with percentiles
38. `v_game_roster_comprehensive` - Game roster with stats

### Specialized Views
39. `v_player_linemates` - Who plays with whom
40. `v_game_comprehensive_stats` - Game-level aggregates

---

## Recommended Migration Plan

### Phase 1: Replace JavaScript Aggregation (This Week)
1. Replace possession stats aggregation → `v_player_possession_aggregated`
2. Replace zone stats aggregation → `v_player_zone_aggregated`
3. Replace WAR/GAR aggregation → `v_player_war_gar_aggregated`
4. Replace physical stats aggregation → `v_player_physical_aggregated`

### Phase 2: Add Situational Splits (Next Week)
1. Add 5v5/PP/PK filters → `v_player_stats_by_strength`
2. Add period breakdowns → `v_player_stats_by_period`
3. Add competition tier filters → `v_player_stats_by_competition_tier`

### Phase 3: Add Advanced Pages (Following Weeks)
1. Micro Stats Explorer → `v_player_micro_stats_comprehensive`
2. Rush Analysis → `v_player_rush_comprehensive`
3. Zone Play Analysis → `v_player_zone_play_comprehensive`
4. WAR/GAR Leaders → `v_player_advanced_metrics`

---

## Installation

Run the SQL file in Supabase SQL Editor:

```sql
-- Copy contents of sql/views/10_comprehensive_advanced_stats_views.sql
-- Paste into Supabase SQL Editor
-- Execute
```

Then refresh materialized views:

```sql
REFRESH MATERIALIZED VIEW mv_player_career_totals;
REFRESH MATERIALIZED VIEW mv_player_vs_opponent;
REFRESH MATERIALIZED VIEW mv_player_rolling_stats;
REFRESH MATERIALIZED VIEW mv_player_career_by_situation;
```

---

## Maintenance

### After Each ETL:
```sql
REFRESH MATERIALIZED VIEW mv_player_career_totals;
REFRESH MATERIALIZED VIEW mv_player_rolling_stats;
REFRESH MATERIALIZED VIEW mv_player_career_by_situation;
```

### Weekly (Optional):
```sql
REFRESH MATERIALIZED VIEW mv_player_vs_opponent;
```

**Note:** Regular views don't need refreshing - they're computed on query.

---

## Troubleshooting

### Views are slow?
- Check if you're filtering by indexed columns (player_id, season_id, team_id)
- Use materialized views for expensive operations (career, vs opponent)

### Missing columns?
- Views handle column name variations (cf/corsi_for, zone_ent/zone_entries)
- If a column doesn't exist, it will be NULL or 0

### Data looks wrong?
- Views aggregate from `fact_player_game_stats` where `game_type = 'All'`
- Check if your ETL is populating the base tables correctly

---

**Total Views Created:** 40+  
**Materialized Views:** 4  
**Total SQL Lines:** ~1,350  
**Coverage:** All 317 player columns × All situations
