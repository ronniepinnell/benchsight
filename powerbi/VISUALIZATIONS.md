# Power BI Visualizations - Complete How-To Guide

## Overview

This document provides step-by-step instructions for creating hockey analytics visualizations in Power BI.

---

## Required Tables for Power BI

### Dimension Tables (Load All)
| Table | Purpose | Key Field |
|-------|---------|-----------|
| dim_player | Player master data | player_id |
| dim_team | Team reference | team_id |
| dim_schedule | Game schedule | game_id |
| dim_dates | Calendar dates | date_key |
| dim_seconds | Time dimension | time_key |
| dim_period | Period reference | period_id |
| dim_event_type | Event categories | event_type |
| dim_strength | Strength situations | strength |
| dim_position | Position reference | position_code |
| dim_skill_tier | Skill level tiers | tier_id |
| dim_venue | Home/Away | venue_code |
| dim_zone | Rink zones | zone_code |

### Fact Tables (Load All)
| Table | Purpose | Key Fields |
|-------|---------|------------|
| fact_box_score | Player game stats | player_game_key, game_id, player_id |
| fact_events | Event details | event_key, game_id |
| fact_gameroster | Basic roster stats | game_id, player_id |

---

## 1. Player Leaderboard

### Purpose
Show top players ranked by selected statistic.

### Step-by-Step Setup

**Step 1: Create the Table Visual**
1. Click on "Table" in Visualizations pane
2. Drag to canvas and resize

**Step 2: Add Fields**
- Rows: `dim_player[display_name]`
- Values: 
  - `SUM(fact_box_score[goals])`
  - `SUM(fact_box_score[assists])`
  - `SUM(fact_box_score[points])`
  - `AVERAGE(fact_box_score[toi_seconds]) / 60` (rename to "Avg TOI")

**Step 3: Add Conditional Formatting**
1. Click column header → Format → Background color
2. Select "Gradient" 
3. Choose color scale (green = high, white = low)

**Step 4: Add Sorting**
1. Click column header → Sort by [points] descending

**Step 5: Add Data Bars (Optional)**
1. Click Goals column → Format → Data bars → On
2. Choose bar color

### Required DAX Measures
```dax
Games Played = DISTINCTCOUNT(fact_box_score[game_id])

Points Per Game = 
DIVIDE(
    SUM(fact_box_score[points]),
    [Games Played],
    0
)

Goals Per 60 = 
DIVIDE(
    SUM(fact_box_score[goals]) * 3600,
    SUM(fact_box_score[toi_seconds]),
    0
)
```

---

## 2. Team Comparison Bar Chart

### Purpose
Side-by-side team statistics comparison.

### Step-by-Step Setup

**Step 1: Create Grouped Bar Chart**
1. Click "Clustered Bar Chart" in Visualizations
2. Drag to canvas

**Step 2: Add Fields**
- Y-axis: `dim_team[team_name]`
- X-axis: `SUM(fact_box_score[goals])`
- Legend: None (or add for multi-stat)

**Step 3: Add Team Filter/Slicer**
1. Add Slicer visual nearby
2. Add `dim_team[team_name]` to slicer
3. Set to multi-select

**Step 4: Format**
1. Data labels → On
2. Colors → Match team colors
3. Sort by value descending

### For Multi-Stat Comparison

**Step 1: Create Parameter Table**
```dax
Stat Selector = 
DATATABLE(
    "Stat", STRING,
    {
        {"Goals"},
        {"Assists"},
        {"Points"},
        {"Shots"},
        {"TOI"}
    }
)
```

**Step 2: Create Dynamic Measure**
```dax
Selected Stat Value = 
SWITCH(
    SELECTEDVALUE('Stat Selector'[Stat]),
    "Goals", SUM(fact_box_score[goals]),
    "Assists", SUM(fact_box_score[assists]),
    "Points", SUM(fact_box_score[points]),
    "Shots", SUM(fact_box_score[shots]),
    "TOI", SUM(fact_box_score[toi_seconds]) / 60,
    BLANK()
)
```

**Step 3: Add Slicer for Stat**
- Add Stat Selector to slicer
- Use buttons or dropdown

---

## 3. Head-to-Head Comparison

### Purpose
Compare two specific teams across multiple metrics.

### Schema Setup

**Step 1: Create Two Team Selector Tables**

In Power BI Desktop → Modeling → New Table:
```dax
Team A = DISTINCT(dim_team[team_name])
Team B = DISTINCT(dim_team[team_name])
```

**Step 2: Create H2H Measures**
```dax
// Games where Team A and Team B played each other
H2H Games = 
VAR TeamA = SELECTEDVALUE('Team A'[team_name])
VAR TeamB = SELECTEDVALUE('Team B'[team_name])
RETURN
CALCULATE(
    COUNTROWS(dim_schedule),
    (dim_schedule[home_team] = TeamA && dim_schedule[away_team] = TeamB)
    || (dim_schedule[home_team] = TeamB && dim_schedule[away_team] = TeamA)
)

// Team A Wins in H2H
Team A Wins = 
VAR TeamA = SELECTEDVALUE('Team A'[team_name])
VAR TeamB = SELECTEDVALUE('Team B'[team_name])
RETURN
CALCULATE(
    COUNTROWS(dim_schedule),
    dim_schedule[winner] = TeamA,
    (dim_schedule[home_team] = TeamA && dim_schedule[away_team] = TeamB)
    || (dim_schedule[home_team] = TeamB && dim_schedule[away_team] = TeamA)
)

// Team A Goals in H2H
Team A Goals H2H = 
VAR TeamA = SELECTEDVALUE('Team A'[team_name])
VAR TeamB = SELECTEDVALUE('Team B'[team_name])
VAR HomeGoals = 
    CALCULATE(
        SUM(dim_schedule[home_score]),
        dim_schedule[home_team] = TeamA,
        dim_schedule[away_team] = TeamB
    )
VAR AwayGoals = 
    CALCULATE(
        SUM(dim_schedule[away_score]),
        dim_schedule[away_team] = TeamA,
        dim_schedule[home_team] = TeamB
    )
RETURN
HomeGoals + AwayGoals
```

### Visual Layout Setup

**Step 1: Create Header Row**
1. Add two Dropdown slicers side by side
2. Left: Team A selector
3. Right: Team B selector
4. Add "VS" text box between them

**Step 2: Create Record Display**
1. Add Card visual for Team A Wins
2. Add Card visual for Team B Wins
3. Add Card visual for Ties

**Step 3: Create Comparison Bars**
1. Add 100% Stacked Bar Chart
2. Y-axis: Metric name (use a measure table)
3. X-axis: Values for each team
4. Create measures for each comparison metric

**Step 4: Add Game History Table**
```
Fields:
- dim_schedule[game_date]
- dim_schedule[home_team]
- dim_schedule[home_score]
- dim_schedule[away_score]
- dim_schedule[away_team]
- dim_schedule[winner]
```

Filter: Use H2H Games measure to filter visible games

---

## 4. Line Combination Analysis

### Purpose
Analyze performance of forward lines and defense pairs.

### Data Model Setup

**Step 1: Create Line Combo Table (in SQL or Power Query)**
```sql
-- Add to datamart
SELECT DISTINCT
    game_id,
    shift_index,
    CAST(home_forward_1 AS TEXT) || '-' || 
    CAST(home_forward_2 AS TEXT) || '-' || 
    CAST(home_forward_3 AS TEXT) AS forward_line,
    'home' AS venue,
    shift_duration,
    home_goals AS goals_for,
    away_goals AS goals_against
FROM fact_shifts
WHERE home_forward_1 IS NOT NULL
UNION ALL
SELECT DISTINCT
    game_id,
    shift_index,
    CAST(away_forward_1 AS TEXT) || '-' || 
    CAST(away_forward_2 AS TEXT) || '-' || 
    CAST(away_forward_3 AS TEXT) AS forward_line,
    'away' AS venue,
    shift_duration,
    away_goals AS goals_for,
    home_goals AS goals_against
FROM fact_shifts
WHERE away_forward_1 IS NOT NULL
```

**Step 2: Create Line Selector**
```dax
Line Selector = DISTINCT(fact_line_combos[forward_line])
```

**Step 3: Create Line Measures**
```dax
Line TOI = 
SUM(fact_line_combos[shift_duration])

Line Goals For = 
SUM(fact_line_combos[goals_for])

Line Goals Against = 
SUM(fact_line_combos[goals_against])

Line Goal Diff = 
[Line Goals For] - [Line Goals Against]

Line GF/60 = 
DIVIDE([Line Goals For] * 3600, [Line TOI], 0)

Line GA/60 = 
DIVIDE([Line Goals Against] * 3600, [Line TOI], 0)
```

### Visual Setup

**Step 1: Line Selector Dropdown**
- Add Slicer with Line Selector[forward_line]
- Enable search

**Step 2: Line Stats Cards**
- Card 1: Line TOI (formatted as MM:SS)
- Card 2: Line Goals For
- Card 3: Line Goals Against  
- Card 4: Line Goal Diff

**Step 3: Line Comparison Table**
- Rows: forward_line
- Values: All line measures
- Sort by TOI descending

**Step 4: Player Names Display**
Create calculated column to show names:
```dax
Line Display Name = 
VAR Numbers = SUBSTITUTE(fact_line_combos[forward_line], "-", "|")
VAR P1 = LOOKUPVALUE(dim_player[display_name], dim_player[player_game_number], VALUE(LEFT(Numbers, FIND("|", Numbers)-1)))
// ... continue for P2, P3
RETURN P1 & " - " & P2 & " - " & P3
```

---

## 5. Shot Chart / Heat Map

### Purpose
Visualize shot locations on the rink.

### Prerequisites
- fact_events with x_coord, y_coord columns
- Rink image as background

### Step-by-Step Setup

**Step 1: Prepare Background Image**
1. Get hockey rink image (PNG, white background)
2. Note image dimensions (e.g., 600 x 255 pixels)

**Step 2: Create Scatter Chart**
1. Add Scatter Chart visual
2. X-axis: fact_events[x_coord]
3. Y-axis: fact_events[y_coord]
4. Size: Count of events (or use 1 for equal dots)
5. Color: dim_event_type[event_type]

**Step 3: Set Axis Ranges**
1. X-axis: Min = 0, Max = 200 (rink length)
2. Y-axis: Min = 0, Max = 85 (rink width)
3. Turn off axis titles

**Step 4: Add Background**
1. Format pane → Plot area → Image
2. Upload rink image
3. Set transparency to ~80%
4. Fit image to plot area

**Step 5: Add Filters**
- Slicer: Event type (Shot only)
- Slicer: Period
- Slicer: Team
- Slicer: Strength

### Heat Map Alternative (Using R/Python Visual)

```python
# Python visual for heat map
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# dataset contains x_coord, y_coord from Power BI
x = dataset['x_coord']
y = dataset['y_coord']

# Create 2D histogram
heatmap, xedges, yedges = np.histogram2d(x, y, bins=20)

# Plot
plt.figure(figsize=(10, 4.25))
plt.imshow(heatmap.T, origin='lower', cmap='hot', aspect='auto')
plt.colorbar(label='Shot Frequency')
plt.xlabel('Rink Length')
plt.ylabel('Rink Width')
plt.show()
```

---

## 6. Time Series / Game Flow

### Purpose
Show events over the course of a game.

### Step-by-Step Setup

**Step 1: Create Line Chart**
1. Add Line Chart visual
2. X-axis: dim_seconds[time_elapsed_game_seconds]
3. Y-axis: Running total measure

**Step 2: Create Running Total**
```dax
Running Goals = 
VAR CurrentTime = MAX(fact_events[time_total_seconds])
RETURN
CALCULATE(
    COUNTROWS(fact_events),
    fact_events[event_detail] = "Goal_Scored",
    fact_events[time_total_seconds] <= CurrentTime
)
```

**Step 3: Add Period Markers**
1. Add Reference Lines at period breaks (900, 1800, 2700 seconds)
2. Format as dashed vertical lines
3. Add labels "P1", "P2", "P3"

**Step 4: Add Game Selector**
1. Add slicer for dim_schedule[game_id]
2. Format as dropdown

### Momentum Chart

```dax
Home Momentum = 
VAR CurrentTime = MAX(fact_events[time_total_seconds])
VAR HomeShots = 
    CALCULATE(
        COUNTROWS(fact_events),
        fact_events[event_type] = "Shot",
        fact_events[player_venue] = "home",
        fact_events[time_total_seconds] <= CurrentTime
    )
VAR AwayShots = 
    CALCULATE(
        COUNTROWS(fact_events),
        fact_events[event_type] = "Shot",
        fact_events[player_venue] = "away",
        fact_events[time_total_seconds] <= CurrentTime
    )
RETURN
HomeShots - AwayShots
```

---

## 7. Player Comparison Radar Chart

### Purpose
Compare players across multiple dimensions.

### Step-by-Step Setup

**Step 1: Install Custom Visual**
1. Click "..." in Visualizations pane
2. "Get more visuals"
3. Search "Radar Chart"
4. Install and add to report

**Step 2: Create Normalized Metrics**
```dax
// Normalize each stat 0-100 for radar chart
Goals Normalized = 
VAR MaxGoals = MAXX(ALL(fact_box_score), [Total Goals])
RETURN
DIVIDE(SUM(fact_box_score[goals]), MaxGoals, 0) * 100

Assists Normalized = 
VAR MaxAssists = MAXX(ALL(fact_box_score), [Total Assists])
RETURN
DIVIDE(SUM(fact_box_score[assists]), MaxAssists, 0) * 100

// Repeat for: Shots, TOI, FaceoffWins, etc.
```

**Step 3: Create Metrics Table**
```dax
Radar Metrics = 
DATATABLE(
    "Metric", STRING,
    "Sort", INTEGER,
    {
        {"Goals", 1},
        {"Assists", 2},
        {"Shots", 3},
        {"TOI", 4},
        {"Faceoffs", 5},
        {"Takeaways", 6}
    }
)
```

**Step 4: Configure Radar Chart**
- Category: Radar Metrics[Metric]
- Y-axis: Normalized metric measure
- Legend: dim_player[display_name] (for comparison)

---

## 8. KPI Cards Dashboard

### Purpose
Display key metrics at a glance.

### Step-by-Step Setup

**Step 1: Create KPI Measures**
```dax
Total Goals = SUM(fact_box_score[goals])

Goals Trend = 
VAR CurrentPeriod = SUM(fact_box_score[goals])
VAR PriorPeriod = 
    CALCULATE(
        SUM(fact_box_score[goals]),
        DATEADD(dim_dates[full_date], -30, DAY)
    )
RETURN
DIVIDE(CurrentPeriod - PriorPeriod, PriorPeriod, 0)

Games This Month = 
CALCULATE(
    DISTINCTCOUNT(dim_schedule[game_id]),
    MONTH(dim_dates[full_date]) = MONTH(TODAY())
)
```

**Step 2: Add Card Visuals**
1. Add Card visual for each KPI
2. Value: KPI measure
3. Add trend indicator (up/down arrow)

**Step 3: Format Cards**
1. Data label → Size: 40pt
2. Category label → Show
3. Background → Team color or neutral

**Step 4: Arrange in Grid**
- Top row: Season totals
- Second row: Monthly totals
- Third row: Per-game averages

---

## 9. Drill-Through Player Card

### Purpose
Detailed player profile accessed by clicking player name.

### Step-by-Step Setup

**Step 1: Create Drill-Through Page**
1. Add new page named "Player Detail"
2. Page format → Type → Drill Through

**Step 2: Set Drill-Through Filter**
1. In Visualizations → Drill through section
2. Add dim_player[player_id]

**Step 3: Design Player Card**
Layout:
```
┌─────────────────────────────────────────────┐
│  [Photo]  Player Name          Team Logo    │
│           Position | Skill Rating           │
├─────────────────────────────────────────────┤
│  G    A    P    +/-   PIM   TOI             │
│  12   23   35   +8    14    18:32           │
├─────────────────────────────────────────────┤
│         Scoring by Game (Line Chart)        │
├─────────────────────────────────────────────┤
│  Game Log Table                              │
│  Date | Opponent | G | A | P | TOI          │
└─────────────────────────────────────────────┘
```

**Step 4: Enable Drill-Through**
On source page:
1. Right-click any player name
2. Drill through → Player Detail

---

## 10. Calendar Heat Map

### Purpose
Show activity/performance by day of week and time.

### Step-by-Step Setup

**Step 1: Create Matrix Visual**
1. Add Matrix visual
2. Rows: dim_dates[day_name]
3. Columns: dim_dates[week_of_year]
4. Values: Count of games or average metric

**Step 2: Apply Conditional Formatting**
1. Select values → Format → Background color
2. Choose "Gradient"
3. Min color: Light
4. Max color: Dark (team color)

**Step 3: Sort Days Correctly**
```dax
Day Sort = 
SWITCH(
    dim_dates[day_name],
    "Monday", 1,
    "Tuesday", 2,
    "Wednesday", 3,
    "Thursday", 4,
    "Friday", 5,
    "Saturday", 6,
    "Sunday", 7
)
```
Sort by Day Sort column.

---

## Summary: Complete Table List for Power BI

### Must Have
- dim_player
- dim_team
- dim_schedule
- dim_dates
- dim_seconds
- fact_box_score
- fact_events

### Recommended
- dim_period
- dim_event_type
- dim_strength
- dim_position
- dim_skill_tier
- dim_venue
- dim_zone
- fact_gameroster

### Optional (if using)
- fact_shifts (for line combo analysis)
- dim_rinkboxcoord (for shot location zones)
- dim_rinkcoordzones (for zone analysis)
