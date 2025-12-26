# Power BI Strategies and Best Practices

## Overview

This document provides advanced strategies for building effective hockey analytics dashboards in Power BI using the datamart tables.

---

## 1. Data Model Architecture

### Star Schema Design

The datamart uses a **star schema** optimized for Power BI:

```
                    ┌─────────────┐
                    │  dim_dates  │
                    └──────┬──────┘
                           │
┌─────────────┐    ┌───────┴───────┐    ┌─────────────┐
│  dim_player │────│ fact_box_score│────│   dim_team  │
└─────────────┘    └───────┬───────┘    └─────────────┘
                           │
                    ┌──────┴──────┐
                    │ dim_schedule│
                    └─────────────┘
```

### Relationship Strategy

**One-to-Many Relationships (Primary):**
- `dim_player[player_id]` → `fact_box_score[player_id]`
- `dim_team[team_id]` → `dim_schedule[home_team_id]`
- `dim_team[team_id]` → `dim_schedule[away_team_id]`
- `dim_schedule[game_id]` → `fact_box_score[game_id]`
- `dim_dates[date_key]` → `dim_schedule[game_date]` (needs date key conversion)
- `dim_seconds[time_key]` → `fact_events[time_key]` (for event timing)

**Inactive Relationships (Use USERELATIONSHIP in DAX):**
- `dim_team[team_id]` → `fact_box_score[player_team]` (for filtering by player's team)
- `dim_player[player_id]` → `fact_events[player_id]` (for event analysis)

### Role-Playing Dimensions

**dim_team as Role-Playing Dimension:**
```
Home Team:  dim_schedule[home_team_id] → dim_team[team_id]
Away Team:  dim_schedule[away_team_id] → dim_team[team_id]  (inactive)
```

**How to use in DAX:**
```dax
// Get away team name
Away Team Name = 
CALCULATE(
    SELECTEDVALUE(dim_team[team_name]),
    USERELATIONSHIP(dim_schedule[away_team_id], dim_team[team_id])
)
```

---

## 2. Advanced Filtering Strategies

### Slicer Hierarchy

Recommended slicer organization:
1. **Season** (top level)
2. **Date Range** (year, month, week)
3. **Team** (home, away, or both)
4. **Player** (position, skill tier, specific player)
5. **Game Type** (regular, playoff)
6. **Strength** (5v5, power play, etc.)

### Cross-Filtering for Head-to-Head

To enable head-to-head team comparisons:

**Step 1: Create a disconnected Team Selector table**
```dax
Team Selector = DISTINCT(dim_team[team_name])
```

**Step 2: Create measures that respect the selector**
```dax
Selected Team Goals = 
VAR SelectedTeam = SELECTEDVALUE('Team Selector'[team_name])
RETURN
CALCULATE(
    SUM(fact_box_score[goals]),
    fact_box_score[player_team] = SelectedTeam
)
```

### Period-Based Filtering with dim_seconds

Connect events to dim_seconds for time-based analysis:

```dax
// Events in last 2 minutes of period
Last 2 Min Events = 
CALCULATE(
    COUNTROWS(fact_events),
    FILTER(
        dim_seconds,
        dim_seconds[time_remaining_period_seconds] <= 120
    )
)
```

---

## 3. Performance Optimization

### Aggregation Tables

Create pre-aggregated tables for large datasets:

**Player Season Summary:**
```sql
CREATE TABLE agg_player_season AS
SELECT 
    player_id,
    season_id,
    COUNT(DISTINCT game_id) as games_played,
    SUM(goals) as total_goals,
    SUM(assists) as total_assists,
    SUM(points) as total_points,
    AVG(toi_seconds) as avg_toi
FROM fact_box_score
GROUP BY player_id, season_id;
```

### Query Reduction Techniques

1. **Use variables in DAX** to avoid repeated calculations
2. **Set up incremental refresh** for large fact tables
3. **Create calculated columns** for frequently filtered values
4. **Use SUMMARIZE** instead of GROUP BY when possible

### Data Type Optimization

- Use **Integer** for IDs and counts
- Use **Decimal** only for rates/percentages
- Store dates as **Date** type, not text
- Use **Text** sparingly (high cardinality = slow)

---

## 4. Line Combination Analysis

### Understanding Line Combos

A "line" in hockey is a group of players on ice together during a shift. Analyzing line combinations requires:
1. Shift data showing which players were on ice
2. Aggregating stats for those player groupings

### Data Model for Line Combos

**Create a Line Combination Bridge Table:**

```sql
-- In datamart, create line combinations from shifts
CREATE TABLE fact_line_combos AS
SELECT 
    game_id,
    shift_index,
    -- Create line key from forward numbers
    home_forward_1 || '-' || home_forward_2 || '-' || home_forward_3 AS home_forward_line,
    home_defense_1 || '-' || home_defense_2 AS home_defense_pair,
    away_forward_1 || '-' || away_forward_2 || '-' || away_forward_3 AS away_forward_line,
    away_defense_1 || '-' || away_defense_2 AS away_defense_pair,
    shift_duration,
    home_goals - away_goals AS goal_diff_home
FROM fact_shifts;
```

### DAX for Line Analysis

```dax
// Time on Ice for specific line combo
Line TOI = 
CALCULATE(
    SUM(fact_shifts[shift_duration]),
    FILTER(
        fact_shifts,
        fact_shifts[home_forward_line] = SELECTEDVALUE('Line Selector'[line_key])
    )
)

// Goals For when line is on ice
Line Goals For = 
CALCULATE(
    SUM(fact_shifts[home_goals]),
    FILTER(
        fact_shifts,
        fact_shifts[home_forward_line] = SELECTEDVALUE('Line Selector'[line_key])
    )
)

// Goals per 60 for line
Line Goals Per 60 = 
DIVIDE(
    [Line Goals For] * 3600,
    [Line TOI],
    0
)
```

---

## 5. Head-to-Head Analysis

### Schema for H2H Filtering

**Challenge:** Compare two teams directly requires careful filtering.

**Solution 1: Game-Level H2H**

Use dim_schedule to find matchups:
```dax
H2H Games = 
CALCULATETABLE(
    dim_schedule,
    dim_schedule[home_team] = "Team A" && dim_schedule[away_team] = "Team B"
    || dim_schedule[home_team] = "Team B" && dim_schedule[away_team] = "Team A"
)
```

**Solution 2: Disconnected Slicers**

Create two team selector tables:

```dax
Team A Selector = DISTINCT(dim_team[team_name])
Team B Selector = DISTINCT(dim_team[team_name])
```

Then use in measures:
```dax
Team A Wins = 
VAR TeamA = SELECTEDVALUE('Team A Selector'[team_name])
VAR TeamB = SELECTEDVALUE('Team B Selector'[team_name])
RETURN
CALCULATE(
    COUNTROWS(dim_schedule),
    dim_schedule[winner] = TeamA,
    dim_schedule[home_team] = TeamA && dim_schedule[away_team] = TeamB
    || dim_schedule[home_team] = TeamB && dim_schedule[away_team] = TeamA
)
```

### H2H Visualization Layout

```
┌─────────────────────────────────────────────────────────────┐
│  [Team A Dropdown]     VS      [Team B Dropdown]            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Team A Logo    Record: 3-2-0    Team B Logo              │
│                                                             │
├────────────────────────┬────────────────────────────────────┤
│   Goals Scored         │         Goals Against              │
│   ████████████  12     │     8   ████████                   │
├────────────────────────┼────────────────────────────────────┤
│   Shots For            │         Shots Against              │
│   ████████████████ 156 │    134  ██████████████             │
├────────────────────────┴────────────────────────────────────┤
│                   Game-by-Game Results                       │
│   Date      | Score     | Winner   | Location               │
│   2024-01-15| 3-2       | Team A   | Home                   │
│   2024-02-10| 1-4       | Team B   | Away                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Calculated Column Strategies

### Pre-Calculate Common Filters

Add to fact_box_score:
```dax
Is Top Scorer = IF([points] >= PERCENTILE.INC(fact_box_score[points], 0.9), 1, 0)
Skill Tier = 
    SWITCH(TRUE(),
        [skill_rating] >= 5.5, "Elite",
        [skill_rating] >= 4.5, "Advanced",
        [skill_rating] >= 3.5, "Intermediate",
        [skill_rating] >= 2.5, "Developing",
        "Beginner"
    )
```

Add to dim_schedule:
```dax
Is High Scoring Game = IF([home_score] + [away_score] >= 8, 1, 0)
Game Result Type = 
    SWITCH(TRUE(),
        [home_score] > [away_score], "Home Win",
        [away_score] > [home_score], "Away Win",
        "Tie"
    )
```

---

## 7. Bookmarks and Drill-Through

### Bookmark Strategy

Create bookmarks for common views:
1. **Overview** - League-wide summary
2. **Team Focus** - Single team deep dive
3. **Player Focus** - Individual player analysis
4. **Game Analysis** - Single game breakdown
5. **H2H** - Head-to-head comparison

### Drill-Through Pages

**Player Drill-Through:**
- Source: Any player name in any visual
- Target: Player detail page
- Filter: player_id

**Game Drill-Through:**
- Source: Any game in schedule
- Target: Game detail page
- Filter: game_id

**Configure:** Right-click visual → Drill through → Set up destination

---

## 8. Row-Level Security (RLS)

### Team-Based Security

```dax
// In Power BI Desktop: Modeling → Manage Roles

Team RLS = 
[team_id] = USERPRINCIPALNAME() 
|| USERPRINCIPALNAME() = "admin@domain.com"
```

### Player-Based Security (for player portals)

```dax
Player RLS = 
[player_id] = LOOKUPVALUE(
    dim_player[player_id],
    dim_player[email],
    USERPRINCIPALNAME()
)
```

---

## 9. Refresh Strategy

### Incremental Refresh Setup

1. Create `RangeStart` and `RangeEnd` parameters (DateTime type)
2. Filter fact tables: `game_date >= RangeStart && game_date < RangeEnd`
3. Configure in Power BI Service:
   - Archive: 2 years
   - Incremental: 30 days
   - Refresh: Daily

### Refresh Dependencies

```
Order of refresh:
1. dim_* tables (dimensions change rarely)
2. fact_gameroster (base stats)
3. fact_box_score (tracking stats)
4. fact_events (detailed events)
```

---

## 10. Mobile Optimization

### Mobile Layout Best Practices

1. **Stack vertically** - single column layout
2. **KPIs at top** - most important numbers first
3. **Large touch targets** - buttons/slicers easy to tap
4. **Limit visuals** - 4-6 per mobile page
5. **Use cards** - clear, large numbers

### Responsive Breakpoints

- Phone: < 500px width
- Tablet: 500-900px
- Desktop: > 900px

---

## 11. Error Handling

### Handle Missing Data

```dax
Safe Division = 
IF(
    ISBLANK([Denominator]) || [Denominator] = 0,
    BLANK(),
    [Numerator] / [Denominator]
)

// With default value
Goals Per Game = 
DIVIDE(
    SUM(fact_box_score[goals]),
    DISTINCTCOUNT(fact_box_score[game_id]),
    0  // Default if no games
)
```

### Handle Missing Relationships

```dax
Player Name Safe = 
VAR PlayerName = RELATED(dim_player[display_name])
RETURN
IF(ISBLANK(PlayerName), "Unknown Player", PlayerName)
```

---

## 12. Documentation in Power BI

### Measure Descriptions

Add descriptions to every measure:
1. Right-click measure → Properties
2. Add description explaining:
   - What it calculates
   - How it's calculated
   - When to use it

### Naming Conventions

```
Measures:      [Total Goals], [Avg TOI], [Goals Per 60]
Columns:       player_id, game_date, goals
Calculated:    _Skill Tier, _Is Weekend
Parameters:    pRangeStart, pSelectedTeam
```
