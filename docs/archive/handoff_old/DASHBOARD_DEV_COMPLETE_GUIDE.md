# BenchSight Dashboard Developer Guide

## Complete Dashboard Hierarchy: Macro to Micro Analytics

This guide provides comprehensive dashboard specifications from league-wide macro views down to granular micro-level analytics, including XY coordinate visualizations.

---

## Table of Contents

1. [Dashboard Hierarchy Overview](#1-dashboard-hierarchy-overview)
2. [Level 1: League Overview (Macro)](#2-level-1-league-overview-macro)
3. [Level 2: Team Analytics](#3-level-2-team-analytics)
4. [Level 3: Player Analytics](#4-level-3-player-analytics)
5. [Level 4: Game Analytics](#5-level-4-game-analytics)
6. [Level 5: Goalie Analytics](#6-level-5-goalie-analytics)
7. [Level 6: Advanced/Micro Analytics](#7-level-6-advancedmicro-analytics)
8. [Level 7: XY Coordinate Visualizations](#8-level-7-xy-coordinate-visualizations)
9. [Real-Time Game Tracker Dashboard](#9-real-time-game-tracker-dashboard)
10. [Data Sources & Aggregations](#10-data-sources--aggregations)

---

## 1. Dashboard Hierarchy Overview

```
MACRO (League-Wide)
├── Standings & League Leaders
├── Team Rankings & Comparisons
│
├── TEAM LEVEL
│   ├── Team Overview Dashboard
│   ├── Team Offensive Analytics
│   ├── Team Defensive Analytics
│   ├── Team Special Teams
│   └── Team Line Combinations
│
├── PLAYER LEVEL
│   ├── Player Overview Dashboard
│   ├── Player Detailed Stats
│   ├── Player Comparisons
│   ├── Player Usage/Deployment
│   └── Player Trends
│
├── GAME LEVEL
│   ├── Game Summary
│   ├── Game Flow Analysis
│   ├── Shift-by-Shift Breakdown
│   └── Event Timeline
│
├── GOALIE LEVEL
│   ├── Goalie Overview
│   ├── Goalie Micro-Stats
│   └── Goalie Shot Maps
│
├── ADVANCED/MICRO
│   ├── H2H Matchups
│   ├── WOWY Analysis
│   ├── Zone Entry/Exit Analysis
│   ├── Possession Chains
│   └── Expected Goals (xG)
│
└── XY ANALYTICS (MICRO)
    ├── Shot Maps / Heat Maps
    ├── Zone Time Visualizations
    ├── Player Positioning
    └── Pass Networks
```

---

## 2. Level 1: League Overview (Macro)

### 2.1 League Standings Dashboard

**Primary View: Standings Table**
```
| Rank | Team      | GP | W  | L | OTL | PTS | GF | GA | DIFF | Streak | L10  |
|------|-----------|----|----|---|-----|-----|----|----|------|--------|------|
| 1    | Platinum  | 12 | 9  | 2 | 1   | 19  | 45 | 28 | +17  | W3     | 7-2-1|
| 2    | Velodrome | 12 | 8  | 3 | 1   | 17  | 42 | 31 | +11  | W1     | 6-3-1|
```

**Supporting Visualizations:**
- Points trend line chart (all teams over time)
- Goal differential bar chart
- Win% pie charts by team

**KPIs (Card Display):**
- Total games played (league)
- Total goals scored
- Average goals per game
- Most wins / Least losses

### 2.2 League Leaders Dashboard

**Scoring Leaders:**
```
| Rank | Player        | Team     | GP | G  | A  | PTS | +/- | PIM |
|------|---------------|----------|----|----|----|----|------|-----|
| 1    | John Smith    | Platinum | 12 | 15 | 18 | 33 | +12  | 4   |
| 2    | Mike Johnson  | Velodrome| 12 | 12 | 19 | 31 | +8   | 6   |
```

**Leader Categories:**
- Goals, Assists, Points
- Plus/Minus
- Shots, Shooting %
- Faceoff %
- TOI per game
- Zone Entries
- Hits, Blocks
- Giveaways, Takeaways

**Goalie Leaders:**
- Save %, GAA
- Wins, Shutouts
- Shots Against per game

### 2.3 League Trends Dashboard

**Trend Charts:**
- Goals per game (weekly trend)
- Penalties per game trend
- Power play % trend
- Average TOI trend

---

## 3. Level 2: Team Analytics

### 3.1 Team Overview Dashboard

**Team Selector:** Dropdown to select team

**Primary KPIs (Cards):**
```
┌─────────────┬──────────────┬─────────────┬────────────────┐
│   RECORD    │  GOALS FOR   │GOALS AGAINST│   GOAL DIFF    │
│   9-2-1     │     45       │     28      │     +17        │
├─────────────┼──────────────┼─────────────┼────────────────┤
│   PP%       │    PK%       │   SHOTS/G   │   SHOTS AG/G   │
│   22.5%     │   85.3%      │    32.4     │     28.1       │
└─────────────┴──────────────┴─────────────┴────────────────┘
```

**Visualizations:**
1. **Goals For/Against by Period** (Stacked bar)
2. **Shot Differential Trend** (Line chart over games)
3. **Team Corsi/Fenwick Trend** (CF%, FF% per game)
4. **Home vs Away Performance** (Split bar charts)

### 3.2 Team Offensive Analytics

**Shot Analytics:**
```
| Metric              | Value | League Rank |
|---------------------|-------|-------------|
| Shots/Game          | 65.2  | 2nd         |
| SOG/Game            | 32.4  | 1st         |
| Shooting %          | 11.5% | 3rd         |
| High Danger Shots   | 18.2  | 2nd         |
| xG/Game             | 3.45  | 1st         |
```

**Zone Entry Analytics:**
```
| Entry Type    | Count | Success% | Shots Generated |
|---------------|-------|----------|-----------------|
| Controlled    | 145   | 72%      | 1.8 per entry   |
| Dump & Chase  | 89    | 45%      | 0.9 per entry   |
| Pass          | 56    | 68%      | 1.5 per entry   |
```

**Visualizations:**
- Shot location heat map
- Zone entry success funnel
- Scoring chances by period
- Power play shot chart

### 3.3 Team Defensive Analytics

**Defensive Metrics:**
```
| Metric              | Value | League Rank |
|---------------------|-------|-------------|
| Shots Against/Game  | 56.1  | 4th (good)  |
| SOG Against/Game    | 28.1  | 3rd         |
| Save %              | 91.2% | 2nd         |
| Blocked Shots/Game  | 12.5  | 1st         |
| Takeaways/Game      | 8.3   | 2nd         |
```

**Zone Exit Analytics:**
```
| Exit Type     | Count | Success% | Time Saved |
|---------------|-------|----------|------------|
| Rush          | 98    | 78%      | n/a        |
| Pass          | 76    | 65%      | n/a        |
| Clear         | 134   | 55%      | n/a        |
```

### 3.4 Team Special Teams

**Power Play:**
```
PP%: 22.5% (League: 18.2%)
PP Goals: 12 | PP Opportunities: 53
PP Shots/2min: 4.8
PP Faceoff%: 58%
```

**Penalty Kill:**
```
PK%: 85.3% (League: 82.1%)
PK Goals Against: 8 | Times Shorthanded: 54
PK Shots Against/2min: 3.2
PK Clears: 45
```

### 3.5 Line Combinations

**Forward Lines Performance:**
```
| Line           | TOI/G | GF | GA | CF% | xGF% |
|----------------|-------|----|----|-----|------|
| 12-53-20       | 8:45  | 15 | 5  | 58% | 62%  |
| 45-82-34       | 7:30  | 8  | 6  | 52% | 51%  |
| 47-21-88       | 6:15  | 6  | 7  | 48% | 45%  |
```

**Defense Pairs:**
```
| Pair    | TOI/G | GF | GA | CF% | Blocked |
|---------|-------|----|----|-----|---------|
| 3-78    | 12:30 | 12 | 8  | 55% | 34      |
| 8-21    | 10:45 | 9  | 7  | 52% | 28      |
```

---

## 4. Level 3: Player Analytics

### 4.1 Player Overview Dashboard

**Player Selector:** Search/dropdown

**Player Card:**
```
┌──────────────────────────────────────────────┐
│  #53 JOHN SMITH | C | Platinum               │
│  Height: 6'1" | Weight: 195 | Shoots: L      │
├───────────┬───────────┬───────────┬──────────┤
│  12 GP    │  15 G     │  18 A     │  33 PTS  │
│           │  1.25/G   │  1.50/G   │  2.75/G  │
├───────────┼───────────┼───────────┼──────────┤
│  +12      │  52 SOG   │  28.8%    │  4 PIM   │
│  +/-      │  Shots    │  SH%      │          │
└───────────┴───────────┴───────────┴──────────┘
```

**Visualizations:**
- Points timeline (game by game)
- Shot chart (player's shots on rink)
- Radar chart (multi-stat comparison to league avg)

### 4.2 Player Detailed Stats

**Offensive Stats Table:**
```
| Stat              | Value | Per Game | Per 60 | League Rank |
|-------------------|-------|----------|--------|-------------|
| Goals             | 15    | 1.25     | 2.14   | 1st         |
| Assists           | 18    | 1.50     | 2.57   | 2nd         |
| Points            | 33    | 2.75     | 4.71   | 1st         |
| Shots             | 52    | 4.33     | 7.43   | 3rd         |
| SOG               | 38    | 3.17     | 5.43   | 2nd         |
| Shooting%         | 28.8% | -        | -      | 1st         |
| IPP               | 78%   | -        | -      | 4th         |
```

**Possession Stats:**
```
| Stat              | Value | Per Game | League Rank |
|-------------------|-------|----------|-------------|
| Zone Entries      | 45    | 3.75     | 2nd         |
| Controlled Entries| 32    | 2.67     | 1st         |
| Entry Control%    | 71%   | -        | 3rd         |
| Passes Attempted  | 312   | 26.0     | 5th         |
| Pass%             | 78%   | -        | 4th         |
| Giveaways         | 18    | 1.50     | 12th        |
| Takeaways         | 22    | 1.83     | 3rd         |
```

**Shift/Time Stats:**
```
| Stat              | Value  | League Rank |
|-------------------|--------|-------------|
| TOI/Game          | 14:35  | 5th         |
| Shifts/Game       | 12.3   | 8th         |
| Avg Shift Length  | 1:11   | 15th        |
| EV TOI            | 11:20  | 6th         |
| PP TOI            | 2:45   | 3rd         |
| PK TOI            | 0:30   | 28th        |
```

### 4.3 Player Usage & Deployment

**Zone Starts:**
```
Offensive Zone Starts: 62% (League Avg: 50%)
Defensive Zone Starts: 28%
Neutral Zone Starts: 10%
```

**Quality of Competition:**
```
Avg Opponent CF%: 52.3% (faces tougher competition)
Avg Opponent TOI: 12:45/game
```

**Quality of Teammates:**
```
Most Common Linemates:
- #20 Mike Johnson (85% together)
- #12 Steve Brown (82% together)
```

**Usage Chart (Bubble):**
```
X-axis: Offensive Zone Start %
Y-axis: Quality of Competition
Bubble size: TOI/Game
Color: CF% (green = good, red = bad)
```

### 4.4 Player Trends

**Rolling Averages (Line Charts):**
- 5-game rolling points average
- 5-game rolling shots average
- 5-game rolling CF%

**Game Log:**
```
| Date  | Opp       | G | A | PTS | +/- | SOG | TOI   | FO% |
|-------|-----------|---|---|-----|-----|-----|-------|-----|
| 12/28 | Velodrome | 2 | 1 | 3   | +2  | 5   | 15:30 | 55% |
| 12/21 | Warriors  | 0 | 2 | 2   | +1  | 3   | 14:45 | 48% |
```

---

## 5. Level 4: Game Analytics

### 5.1 Game Summary Dashboard

**Game Header:**
```
┌─────────────────────────────────────────────┐
│  PLATINUM 5 - 3 VELODROME                   │
│  December 28, 2024 | Final                  │
├─────────────┬─────────────┬─────────────────┤
│   Period 1  │   Period 2  │    Period 3     │
│    2 - 1    │    2 - 1    │     1 - 1       │
└─────────────┴─────────────┴─────────────────┘
```

**Game Stats Comparison:**
```
            PLATINUM  |  VELODROME
Shots          68     |     52
SOG            35     |     28
Faceoffs      23-19   |   19-23
PP             2/5    |    1/4
Hits           18     |     22
Blocked        14     |     11
Giveaways      12     |     15
Takeaways      10     |      8
```

**Three Stars:**
```
⭐⭐⭐ #53 J. Smith (PLA) - 2G, 1A
⭐⭐ #99 T. Goalie (PLA) - 25 saves, .893 SV%
⭐ #70 M. Forward (VEL) - 1G, 1A
```

### 5.2 Game Flow Analysis

**Cumulative Shot Chart:**
```
         Platinum  Velodrome
   ^
20 |           ____/
   |      ____/
15 |  ___/
   | /
10 |____/
   |   \____
 5 |        \____
   +-----|-----|-----|----> Time
        P1    P2    P3
```

**Momentum Chart (5-min rolling Corsi):**
Shows which team is dominating possession over time

**Score-Adjusted Corsi:**
- Accounts for game state (leading/trailing)

### 5.3 Shift-by-Shift Breakdown

**Shift Timeline:**
```
Shift | Time        | Players          | Events            | CF
------|-------------|------------------|-------------------|----
1     | 0:00-1:22   | 53,20,12,8,21    | FO(W), 2 shots    | +3
2     | 1:22-2:45   | 45,82,34,3,78    | Zone entry, shot  | +1
3     | 2:45-3:58   | 53,20,12,8,21    | PP, GOAL          | +4
```

**Line Chart: Each line's performance by shift**

### 5.4 Event Timeline

**Filterable Event Log:**
```
| Time  | Period | Event      | Team     | Player(s)    | Detail          |
|-------|--------|------------|----------|--------------|-----------------|
| 18:00 | 1      | Faceoff    | Platinum | #53 (W)      | Center ice      |
| 17:58 | 1      | Pass       | Platinum | #53 → #20    | Completed       |
| 17:45 | 1      | Zone Entry | Platinum | #20          | Controlled      |
| 17:30 | 1      | Shot       | Platinum | #12          | On net, saved   |
| 17:28 | 1      | Rebound    | -        | -            | Goalie freeze   |
```

**Filters:** Event type, Team, Period, Player

---

## 6. Level 5: Goalie Analytics

### 6.1 Goalie Overview Dashboard

**Goalie Card:**
```
┌──────────────────────────────────────────────┐
│  #99 TOM GOALIE | G | Platinum               │
├───────────┬───────────┬───────────┬──────────┤
│  10 GP    │  8-1-1    │  2.45 GAA │  .912 SV%│
├───────────┼───────────┼───────────┼──────────┤
│  25.5 SA  │  23.2 SV  │  285 MIN  │  1 SO    │
│  per game │  per game │  played   │ shutouts │
└───────────┴───────────┴───────────┴──────────┘
```

### 6.2 Goalie Micro-Stats

**Save Breakdown by Location:**
```
| Location    | Saves | Shots | SV%   |
|-------------|-------|-------|-------|
| Glove       | 45    | 48    | 93.8% |
| Blocker     | 32    | 35    | 91.4% |
| Left Pad    | 38    | 42    | 90.5% |
| Right Pad   | 41    | 45    | 91.1% |
| Five Hole   | 12    | 18    | 66.7% |
| Other       | 15    | 17    | 88.2% |
```

**Rebound Control:**
```
| Metric            | Value | League Rank |
|-------------------|-------|-------------|
| Saves Freeze      | 85    | 2nd         |
| Saves Rebound     | 98    | -           |
| Rebound Control%  | 46.4% | 3rd         |
| Rebounds→Shots    | 12    | 5th (good)  |
| Rebounds→Goals    | 2     | 4th (good)  |
```

**By Shot Type:**
```
| Shot Type   | Saves | Goals | SV%   |
|-------------|-------|-------|-------|
| Wrist       | 95    | 10    | 90.5% |
| Slap        | 42    | 6     | 87.5% |
| Snap        | 35    | 4     | 89.7% |
| Backhand    | 18    | 3     | 85.7% |
| Tip/Deflect | 22    | 5     | 81.5% |
```

**By Situation:**
```
| Situation      | SA  | GA | SV%   |
|----------------|-----|----|-------|
| Even Strength  | 185 | 18 | 90.3% |
| Power Play     | 35  | 5  | 85.7% |
| Penalty Kill   | 12  | 1  | 91.7% |
| Empty Net Opp  | 8   | 0  | 100%  |
```

### 6.3 Goalie Shot Maps

**Heat Map of Goals Against:**
Visual rink diagram showing where goals were scored from

**Save Location Chart:**
Visual goal diagram showing save distribution

---

## 7. Level 6: Advanced/Micro Analytics

### 7.1 H2H (Head-to-Head) Matchups

**H2H Dashboard:**
```
Player A: #53 John Smith (Platinum)
Player B: #70 Mark Forward (Velodrome)

| When Together On Ice |
| Time Together: 45:30 across 5 games |
| Shifts Together: 38 |

| Player A Stats |          | Player B Stats |
|----------------|----------|----------------|
| 2 Goals For    |    GF    | 1 Goals For    |
| 1 Goals Against|    GA    | 2 Goals Against|
| +1 Goal Diff   |   DIFF   | -1 Goal Diff   |
| 8 CF           |    CF    | 5 CF           |
| 5 CA           |    CA    | 8 CA           |
| 61.5% CF%      |   CF%    | 38.5% CF%      |
```

### 7.2 WOWY (With Or Without You)

**WOWY Dashboard:**
```
Player: #53 John Smith

| Linemate        | With    | Without | Impact  |
|-----------------|---------|---------|---------|
| #20 M. Johnson  | 62% CF% | 48% CF% | +14%    |
| #12 S. Brown    | 58% CF% | 52% CF% | +6%     |
| #8 D. Defenseman| 55% CF% | 53% CF% | +2%     |

Best Partner: #20 M. Johnson (+14% CF% when together)
```

**WOWY Visualization:**
Scatter plot with player pairs showing CF% with vs without

### 7.3 Zone Entry/Exit Analysis

**Zone Entry Dashboard:**
```
| Player       | Entries | Controlled | Dump | Success% | Shots/Entry |
|--------------|---------|------------|------|----------|-------------|
| #53 J. Smith | 45      | 32 (71%)   | 13   | 78%      | 1.8         |
| #20 M. Johns | 38      | 28 (74%)   | 10   | 82%      | 1.6         |
```

**Entry Type Effectiveness:**
```
| Type       | Entries | Shots | Goals | Shots/Entry | Goal% |
|------------|---------|-------|-------|-------------|-------|
| Controlled | 145     | 261   | 28    | 1.80        | 19%   |
| Dump       | 89      | 80    | 5     | 0.90        | 6%    |
| Pass       | 56      | 84    | 9     | 1.50        | 16%   |
```

### 7.4 Possession Chains

**Chain Analysis:**
```
GOAL SEQUENCE #1:
Faceoff Win (OZ) → Pass → Pass → Shot (Goal)
Chain Length: 4 events | Time: 8 seconds | xG: 0.45

GOAL SEQUENCE #2:
Zone Entry (Controlled) → Possession → Pass (Assist) → Shot (Goal)
Chain Length: 4 events | Time: 12 seconds | xG: 0.38
```

**Chain Statistics:**
```
| Metric                    | Value |
|---------------------------|-------|
| Avg Chain Length to Shot  | 3.2   |
| Avg Chain Length to Goal  | 4.1   |
| Shots from Zone Entry     | 68%   |
| Shots from Faceoff Win    | 15%   |
| Shots from Turnover       | 17%   |
```

### 7.5 Expected Goals (xG)

**xG Model Inputs:**
- Shot distance
- Shot angle
- Shot type
- Rebound (yes/no)
- Rush (yes/no)
- Shot location zone

**Player xG Table:**
```
| Player       | Goals | xG    | G-xG   | Shooting Luck |
|--------------|-------|-------|--------|---------------|
| #53 J. Smith | 15    | 12.3  | +2.7   | Lucky (+22%)  |
| #20 M. Johns | 12    | 13.1  | -1.1   | Unlucky (-8%) |
```

**Team xG:**
```
| Team      | GF | xGF   | GA | xGA   | xG Diff |
|-----------|----|----- -|----|-------|---------|
| Platinum  | 45 | 41.2  | 28 | 31.5  | +9.7    |
| Velodrome | 42 | 38.8  | 31 | 33.2  | +5.6    |
```

---

## 8. Level 7: XY Coordinate Visualizations

### 8.1 Shot Maps

**Team Shot Heat Map:**
- Rink diagram with color intensity showing shot concentration
- Filter by: All shots, SOG only, Goals only
- Filter by: Period, Situation (5v5, PP, PK)

**Individual Shot Chart:**
- Player's shots plotted on rink
- Color coded: Goal (green), SOG (blue), Missed/Blocked (gray)
- Symbol size: xG value

### 8.2 Zone Time Visualization

**Time in Zone Heat Map:**
- Shows where puck spends most time
- Offensive/Defensive/Neutral zone breakdown
- Per period or full game

### 8.3 Player Positioning

**Average Position Chart:**
- Shows each player's average XY position during shifts
- Compare lines/players

**Player Movement Trails:**
- Animated paths showing player movement
- Good for reviewing specific plays

### 8.4 Pass Networks

**Pass Network Diagram:**
- Nodes = Players
- Edges = Pass connections (thickness = frequency)
- Shows team's passing patterns

**Pass Heat Map:**
- Origin of successful passes
- Destination of successful passes

### 8.5 Goalie Save Charts

**Save Location Chart:**
- Goal diagram (front view)
- Shows where saves were made
- Color by: Save type (glove, blocker, pad)

**Shot Against Heat Map:**
- Rink view showing where shots came from
- Red = Goals, Blue = Saves

---

## 9. Real-Time Game Tracker Dashboard

### 9.1 Live Game View

**Game Clock & Score:**
```
┌─────────────────────────────────────────────┐
│  PLATINUM    3 - 2    VELODROME             │
│         Period 2 | 12:45 remaining          │
│  Shots: 24-18 | Faceoffs: 12-10             │
└─────────────────────────────────────────────┘
```

**Live Event Feed:**
```
12:50 | Shot | Platinum #53 | Saved
12:45 | Rebound | - | Goalie freeze
12:45 | Stoppage | - | Goalie stoppage
12:40 | Faceoff | Platinum #53 (W) | Offensive zone
```

**On-Ice Players (Live):**
```
PLATINUM                    VELODROME
F: 53-20-12                 F: 70-75-49
D: 8-21                     D: 52-22
G: 99                       G: 39
```

### 9.2 Live Analytics

**Rolling Stats (Last 5 minutes):**
```
| Metric      | Platinum | Velodrome |
|-------------|----------|-----------|
| Shots       | 8        | 3         |
| Corsi       | 12       | 5         |
| Zone Time   | 3:45     | 1:15      |
```

**Momentum Meter:**
Visual indicator showing which team is dominating

---

## 10. Data Sources & Aggregations

### 10.1 Data Tables Used

| Dashboard Section | Primary Tables |
|-------------------|----------------|
| League Standings  | dim_schedule, dim_team |
| League Leaders    | fact_player_game_stats (SUM/AVG) |
| Team Analytics    | fact_team_game_stats, fact_events |
| Player Analytics  | fact_player_game_stats, fact_shifts_player |
| Game Analytics    | fact_events, fact_shifts |
| Goalie Analytics  | fact_goalie_game_stats |
| H2H / WOWY        | fact_h2h, fact_wowy |
| XY Analytics      | fact_events (with XY), fact_shots |

### 10.2 Key Aggregations

**Season Totals:**
```sql
SELECT player_id, 
       SUM(goals) as total_goals,
       SUM(assists) as total_assists,
       SUM(points) as total_points,
       AVG(shooting_pct) as avg_shooting_pct
FROM fact_player_game_stats
GROUP BY player_id
```

**Per-60 Stats:**
```sql
SELECT player_id,
       SUM(goals) * 60.0 * 60.0 / SUM(toi_seconds) as goals_per_60,
       SUM(assists) * 60.0 * 60.0 / SUM(toi_seconds) as assists_per_60
FROM fact_player_game_stats
GROUP BY player_id
```

**Rolling Averages:**
```sql
SELECT game_id, player_id,
       AVG(points) OVER (
         PARTITION BY player_id 
         ORDER BY game_date 
         ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
       ) as rolling_5_game_points
FROM fact_player_game_stats
```

### 10.3 Performance Considerations

- **Materialized Views:** Pre-aggregate common calculations
- **Indexes:** Create indexes on game_id, player_id, team_id
- **Caching:** Cache league leaders (update hourly)
- **Pagination:** Limit game logs to 20 per page

---

## Quick Reference: Key Metrics by Dashboard

| Dashboard | Key Metrics |
|-----------|-------------|
| **Macro** | W-L, PTS, GF, GA, PP%, PK% |
| **Team** | CF%, xGF%, Zone Entry%, Special Teams |
| **Player** | G, A, PTS, +/-, SOG, TOI, FO% |
| **Game** | Shots, CF, Score, Faceoffs, Hits |
| **Goalie** | SV%, GAA, GSAA, Rebound Control% |
| **Advanced** | H2H CF%, WOWY, Entry Success%, xG |
| **XY** | Shot density, Zone time, Positioning |

---

*Document Version: 1.0 | Last Updated: December 2024*
