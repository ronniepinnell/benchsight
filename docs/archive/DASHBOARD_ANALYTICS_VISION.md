# BenchSight Dashboard & Analytics Vision
## Comprehensive Dashboard, Report, and ML Strategy

**Last Updated:** 2026-01-13  
**Version:** 1.0  
**Scope:** Complete utilization of all 139 tables + 30 views for dashboards, reports, and ML

---

## Executive Summary

This document outlines a comprehensive strategy to utilize **ALL** of BenchSight's rich data infrastructure (139 tables + 30 views) across:
- **Interactive Dashboards** (50+ pages)
- **Advanced Reports** (30+ report types)
- **Machine Learning Models** (20+ ML applications)
- **Real-time Analytics** (Live game tracking)
- **Visualization Components** (100+ charts/graphs)

**Inspiration Sources:**
- MoneyPuck (xG models, shot maps, player cards)
- Natural Stat Trick (on-ice stats, 5v5 analysis)
- Evolving Hockey (GAR, RAPM, WAR methodology)
- Hockey Reference (historical data, advanced stats)
- NHL EDGE (tracking data, speed, distance)
- PuckPedia (salary, contracts, stats glossary)

---

## Table Inventory Overview

### Core Data Assets

| Category | Count | Key Tables |
|----------|-------|------------|
| **Dimension Tables** | 50 | dim_player, dim_team, dim_season, dim_event_type, etc. |
| **Fact Tables** | 81 | fact_player_game_stats (317 cols), fact_events (140 cols), fact_shift_players (86 cols) |
| **Player Stats** | 15+ | fact_player_game_stats, fact_player_season_stats, fact_player_career_stats, fact_player_micro_stats |
| **Goalie Stats** | 6+ | fact_goalie_game_stats (128 cols), fact_goalie_season_stats, fact_goalie_career_stats |
| **Team Stats** | 8+ | fact_team_game_stats, fact_team_season_stats, fact_team_zone_time |
| **Event Data** | 20+ | fact_events, fact_event_players, fact_shifts, fact_rushes, fact_faceoffs |
| **Advanced Analytics** | 15+ | fact_wowy, fact_matchup_performance, fact_player_qoc_summary, fact_shot_chains |
| **Views (Pre-aggregated)** | 30 | v_leaderboard_*, v_standings_*, v_rankings_*, v_summary_*, etc. |

---

## Part 1: Interactive Dashboard Pages (50+ Pages)

### 1.1 Core Navigation Structure

```
Dashboard Home
├── Players
│   ├── Player Directory
│   ├── Player Profile (Individual)
│   ├── Player Comparison (2+ players)
│   ├── Player Search & Filters
│   └── Player Trends
├── Goalies
│   ├── Goalie Directory
│   ├── Goalie Profile (Individual)
│   ├── Goalie Comparison
│   ├── Goalie Advanced Metrics
│   └── Goalie Performance Trends
├── Teams
│   ├── Team Directory
│   ├── Team Profile
│   ├── Team Comparison
│   ├── Team Line Combinations
│   ├── Team Zone Time Analysis
│   └── Team Matchups (H2H)
├── Games
│   ├── Game Center (Live)
│   ├── Game Recap
│   ├── Game Boxscore
│   ├── Play-by-Play
│   ├── Shift Charts
│   ├── Shot Maps
│   └── Game Analytics
├── Analytics
│   ├── Advanced Metrics Hub
│   ├── xG Analysis
│   ├── WAR/GAR Leaders
│   ├── RAPM Analysis (future)
│   ├── Micro Stats Explorer
│   ├── Zone Entry/Exit Analysis
│   ├── Rush Analysis
│   └── Faceoff Analysis
├── Reports
│   ├── Custom Report Builder
│   ├── Pre-built Reports
│   └── Export Tools
└── Admin (if applicable)
```

---

### 1.2 Player Dashboards (15+ Pages)

#### 1.2.1 Player Profile Page (Individual Player)
**Data Sources:** `fact_player_game_stats`, `fact_player_season_stats`, `fact_player_career_stats`, `fact_player_micro_stats`, `fact_player_qoc_summary`, `fact_player_matchups_xy`

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ [Player Header: Name, Team, Position, Photo]           │
│ [Quick Stats Cards: GP, G, A, P, +/-]                  │
├─────────────────────────────────────────────────────────┤
│ Tab Navigation: Overview | Season | Career | Advanced  │
├─────────────────────────────────────────────────────────┤
│ OVERVIEW TAB:                                           │
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ Performance Trend│ │ Game Log         │             │
│ │ (Line Chart)     │ │ (Data Table)     │             │
│ └──────────────────┘ └──────────────────┘             │
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ Stat Breakdown   │ │ Recent Games     │             │
│ │ (Radar Chart)    │ │ (Timeline)       │             │
│ └──────────────────┘ └──────────────────┘             │
├─────────────────────────────────────────────────────────┤
│ SEASON TAB:                                             │
│ ┌────────────────────────────────────────────┐         │
│ │ Season Summary (Cards: G, A, P, TOI, etc.)│         │
│ └────────────────────────────────────────────┘         │
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ Goals/Game Trend │ │ Advanced Metrics │             │
│ │ (Line Chart)     │ │ (Cards)          │             │
│ └──────────────────┘ └──────────────────┘             │
│ ┌────────────────────────────────────────────┐         │
│ │ Game-by-Game Stats Table                   │         │
│ └────────────────────────────────────────────┘         │
├─────────────────────────────────────────────────────────┤
│ CAREER TAB:                                             │
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ Career Totals    │ │ Career Trends    │             │
│ │ (Cards)          │ │ (Multi-line)     │             │
│ └──────────────────┘ └──────────────────┘             │
│ ┌────────────────────────────────────────────┐         │
│ │ Season-by-Season Comparison Table          │         │
│ └────────────────────────────────────────────┘         │
├─────────────────────────────────────────────────────────┤
│ ADVANCED TAB:                                           │
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ xG Analysis      │ │ WAR/GAR          │             │
│ │ (Bar + Line)     │ │ (Cards)          │             │
│ └──────────────────┘ └──────────────────┘             │
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ Zone Analytics   │ │ Micro Stats      │             │
│ │ (Heat Maps)      │ │ (Cards)          │             │
│ └──────────────────┘ └──────────────────┘             │
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ Competition Tier │ │ Quality Metrics  │             │
│ │ (Stacked Bar)    │ │ (Cards)          │             │
│ └──────────────────┘ └──────────────────┘             │
└─────────────────────────────────────────────────────────┘
```

**Key Stats to Display (from fact_player_game_stats - 317 columns):**

**Basic Stats:**
- Goals, Assists, Points, Primary/Secondary Assists
- Shots, SOG, Shooting %, Shot Types
- Plus/Minus, TOI, Shifts
- Faceoff Wins/Losses/%
- Passes (Attempts/Completed/%)

**Advanced Stats:**
- Corsi For/Against/%
- Fenwick For/Against/%
- Expected Goals (xG), Goals Above Expected
- WAR, GAR, Game Score
- Zone Entry/Exit %, Controlled Entries
- Possession Time (by zone)
- Rush Stats (rush_goals, rush_xg, breakaway_goals, odd_man_rushes)
- Ratings-Adjusted Stats (goals_adj, points_adj, xg_adj)
- Competition Tier Stats (vs_elite_*, vs_good_*, etc.)
- Micro Stats (dekes, drives, stick checks, etc.)

**Splits:**
- Period Splits (P1, P2, P3, OT)
- Strength Splits (5v5, PP, PK, EN)
- Situation Splits (leading, trailing, tied)
- Competition Tier Splits
- Game State Splits

#### 1.2.2 Player Comparison Page (Side-by-Side)
**Data Sources:** `fact_player_game_stats`, `fact_player_season_stats`, `fact_player_career_stats`

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ [Player Selector: Search/Select 2-4 Players]           │
├─────────────────────────────────────────────────────────┤
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│ │ Player 1     │ │ Player 2     │ │ Player 3     │    │
│ │ [Photo]      │ │ [Photo]      │ │ [Photo]      │    │
│ │ Name, Team   │ │ Name, Team   │ │ Name, Team   │    │
│ └──────────────┘ └──────────────┘ └──────────────┘    │
├─────────────────────────────────────────────────────────┤
│ Tab: Overview | Advanced | Head-to-Head                │
├─────────────────────────────────────────────────────────┤
│ OVERVIEW:                                               │
│ ┌────────────────────────────────────────────┐         │
│ │ Stat Comparison Table (Sortable)           │         │
│ │ [G, A, P, TOI, CF%, xG, WAR, etc.]        │         │
│ └────────────────────────────────────────────┘         │
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ Radar Chart      │ │ Bar Chart        │             │
│ │ (Multi-player)   │ │ (Key Stats)      │             │
│ └──────────────────┘ └──────────────────┘             │
├─────────────────────────────────────────────────────────┤
│ ADVANCED:                                               │
│ ┌────────────────────────────────────────────┐         │
│ │ Advanced Metrics Comparison                │         │
│ │ [xG, WAR, GAR, Zone Stats, etc.]          │         │
│ └────────────────────────────────────────────┘         │
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ Trend Comparison │ │ Micro Stats      │             │
│ │ (Multi-line)     │ │ (Cards)          │             │
│ └──────────────────┘ └──────────────────┘             │
└─────────────────────────────────────────────────────────┘
```

#### 1.2.3 Player Directory / Leaderboard
**Data Sources:** `v_leaderboard_*`, `fact_player_season_stats`, `fact_player_career_stats`

**Features:**
- Sortable columns (Goals, Points, WAR, xG, CF%, etc.)
- Filters (Position, Team, Season, Min GP)
- Export to CSV
- Quick links to player profiles

**Leaderboards:**
- Points Leaders
- Goals Leaders
- Assists Leaders
- WAR Leaders
- xG Leaders
- CF% Leaders
- Ratings-Adjusted Stats Leaders
- Per-60 Rate Leaders
- Advanced Metrics Leaders

#### 1.2.4 Player Trends / Analytics
**Data Sources:** `fact_player_game_stats`, `fact_player_season_stats`, `fact_player_trends`

**Features:**
- Time series charts (Goals/Game, Points/Game, WAR trend)
- Rolling averages (5-game, 10-game)
- Performance vs. rating comparison
- Streak analysis (hot/cold streaks)
- Game state performance (leading/trailing)
- Period performance analysis

#### 1.2.5 Player Micro Stats Explorer
**Data Sources:** `fact_player_micro_stats`, `fact_player_game_stats`

**Features:**
- Interactive micro stats breakdown
- Deke success rate, drive success rate
- Stick checks, poke checks, backchecks
- Zone entry/exit success rates
- Rush involvement metrics
- Pressure performance metrics

---

### 1.3 Goalie Dashboards (10+ Pages)

#### 1.3.1 Goalie Profile Page (Individual Goalie)
**Data Sources:** `fact_goalie_game_stats` (128 columns), `fact_goalie_season_stats`, `fact_goalie_career_stats`, `fact_saves`

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ [Goalie Header: Name, Team, Photo]                     │
│ [Quick Stats: GP, W, L, SV%, GAA, SO]                  │
├─────────────────────────────────────────────────────────┤
│ Tab: Overview | Season | Career | Advanced | Saves     │
├─────────────────────────────────────────────────────────┤
│ OVERVIEW:                                               │
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ Save % Trend     │ │ Game Log         │             │
│ │ (Line Chart)     │ │ (Data Table)     │             │
│ └──────────────────┘ └──────────────────┘             │
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ Goals Against    │ │ Recent Games     │             │
│ │ (Bar Chart)      │ │ (Timeline)       │             │
│ └──────────────────┘ └──────────────────┘             │
├─────────────────────────────────────────────────────────┤
│ ADVANCED:                                               │
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ GSAx (Goals      │ │ High/Med/Low     │             │
│ │ Saved Above x)   │ │ Danger SV%       │             │
│ │ (Cards)          │ │ (Stacked Bar)    │             │
│ └──────────────────┘ └──────────────────┘             │
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ Save Type        │ │ Rebound Control  │             │
│ │ Breakdown        │ │ (Cards)          │             │
│ │ (Pie/Bar)        │ └──────────────────┘             │
│ └──────────────────┘                                   │
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ Period Splits    │ │ Workload Metrics │             │
│ │ (Stacked Bar)    │ │ (Cards)          │             │
│ └──────────────────┘ └──────────────────┘             │
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ Rush vs Set Play │ │ Pressure Metrics │             │
│ │ (Comparison)     │ │ (Cards)          │             │
│ └──────────────────┘ └──────────────────┘             │
├─────────────────────────────────────────────────────────┤
│ SAVES DETAIL:                                           │
│ ┌────────────────────────────────────────────┐         │
│ │ Save-by-Save Breakdown (from fact_saves)   │         │
│ │ [Save Type, Location, Danger, Result]      │         │
│ └────────────────────────────────────────────┘         │
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ Save Location    │ │ Save Type        │             │
│ │ Heat Map         │ │ Distribution     │             │
│ └──────────────────┘ └──────────────────┘             │
└─────────────────────────────────────────────────────────┘
```

**Key Stats from fact_goalie_game_stats (128 columns):**

**Core Stats:**
- Saves, Goals Against, Shots Against, Save %
- Wins, Losses, Shutouts
- TOI, Period Splits

**Advanced Stats (ALL GOALIE MICRO & ADVANCED STATS):**
- **GSAx (Goals Saved Above Expected)**
- **Save Type Breakdown:** Butterfly, Pad, Glove, Blocker, Chest, Stick, Scramble
- **Rebound Control:** Freeze Rate, Rebound Rate, Rebound Control Index
- **Danger Zone Stats:** High/Medium/Low Danger SV%, HD Saves, MD Saves, LD Saves
- **Period Performance:** P1/P2/P3/OT SV%, Goals Against by Period
- **Time Bucket Performance:** Early Period, Late Period, Overtime SV%
- **Shot Context:** Rush vs Set Play SV%, Odd-Man Rush SV%, Breakaway SV%
- **Pressure Metrics:** Pressure Save %, Sequence Handling
- **Body Location/Technique:** Save Location Heat Maps, Save Type Distribution
- **Workload Metrics:** Shots per Period, Save Volume Variance, Time Between Shots
- **Goalie WAR/GAR:** Goalie GAR Components, Goalie WAR, Quality Start Bonus
- **Advanced Composites:** Fatigue-Adjusted GSAx, Workload Index, Performance Index

#### 1.3.2 Goalie Comparison Page
**Data Sources:** `fact_goalie_game_stats`, `fact_goalie_season_stats`, `fact_goalie_career_stats`

**Features:**
- Side-by-side comparison (2-4 goalies)
- Save % comparison chart
- GSAx comparison
- Save type distribution comparison
- Danger zone SV% comparison
- Advanced metrics comparison

#### 1.3.3 Goalie Leaderboard
**Data Sources:** `v_leaderboard_goalie_*`, `fact_goalie_season_stats`

**Leaderboards:**
- Save % Leaders
- GSAx Leaders
- Wins Leaders
- Shutout Leaders
- High Danger SV% Leaders
- Goalie WAR Leaders
- Rebound Control Leaders

---

### 1.4 Team Dashboards (12+ Pages)

#### 1.4.1 Team Profile Page
**Data Sources:** `fact_team_game_stats`, `fact_team_season_stats`, `fact_team_zone_time`, `fact_line_combos`, `fact_wowy`

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ [Team Header: Logo, Name, Season Record]               │
│ [Quick Stats: W, L, PTS, GF, GA, Diff]                 │
├─────────────────────────────────────────────────────────┤
│ Tab: Overview | Roster | Lines | Analytics | Matchups  │
├─────────────────────────────────────────────────────────┤
│ OVERVIEW:                                               │
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ Standings        │ │ Goal Differential│             │
│ │ (Table)          │ │ (Bar Chart)      │             │
│ └──────────────────┘ └──────────────────┘             │
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ Team Stats       │ │ Game Results     │             │
│ │ (Cards)          │ │ (Timeline)       │             │
│ └──────────────────┘ └──────────────────┘             │
├─────────────────────────────────────────────────────────┤
│ ROSTER:                                                 │
│ ┌────────────────────────────────────────────┐         │
│ │ Player List (Sortable)                     │         │
│ │ [Name, Position, GP, G, A, P, TOI, etc.]  │         │
│ └────────────────────────────────────────────┘         │
├─────────────────────────────────────────────────────────┤
│ LINES:                                                  │
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ Line Combinations│ │ Line Performance │             │
│ │ (from fact_line_ │ │ (CF%, xGF%, etc.)│             │
│ │  combos)         │ └──────────────────┘             │
│ └──────────────────┘                                   │
├─────────────────────────────────────────────────────────┤
│ ANALYTICS:                                              │
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ Zone Time        │ │ xG For/Against   │             │
│ │ (from fact_team_ │ │ (Cards)          │             │
│ │  zone_time)      │ └──────────────────┘             │
│ └──────────────────┘                                   │
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ WOWY Analysis    │ │ Team Trends      │             │
│ │ (from fact_wowy) │ │ (Line Charts)    │             │
│ └──────────────────┘ └──────────────────┘             │
└─────────────────────────────────────────────────────────┘
```

#### 1.4.2 Team Comparison Page
**Data Sources:** `fact_team_season_stats`, `fact_team_game_stats`

**Features:**
- Side-by-side team comparison
- Stat comparison tables
- Trend comparisons
- Head-to-head record (if applicable)

#### 1.4.3 Team Zone Time Analysis
**Data Sources:** `fact_team_zone_time`, `fact_events`

**Features:**
- Zone time breakdown (O-zone, N-zone, D-zone)
- Zone time heat maps
- Zone time by period
- Zone time by game state

---

### 1.5 Game Dashboards (10+ Pages)

#### 1.5.1 Game Center (Live Game View)
**Data Sources:** `fact_events`, `fact_shifts`, `fact_game_status`, `fact_player_game_stats`

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ [Scoreboard: Teams, Score, Period, Time]               │
│ [Live Stats: Shots, Faceoffs, TOI]                     │
├─────────────────────────────────────────────────────────┤
│ Tab: Live | Boxscore | Shifts | Shot Map | Analytics   │
├─────────────────────────────────────────────────────────┤
│ LIVE TAB:                                               │
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ Play-by-Play     │ │ Game Flow        │             │
│ │ (Live Feed)      │ │ (xG Timeline)    │             │
│ └──────────────────┘ └──────────────────┘             │
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ Key Events       │ │ Period Summary   │             │
│ │ (Timeline)       │ │ (Cards)          │             │
│ └──────────────────┘ └──────────────────┘             │
├─────────────────────────────────────────────────────────┤
│ BOXSCORE TAB:                                           │
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ Home Team        │ │ Away Team        │             │
│ │ Player Stats     │ │ Player Stats     │             │
│ │ (Table)          │ │ (Table)          │             │
│ └──────────────────┘ └──────────────────┘             │
│ ┌────────────────────────────────────────────┐         │
│ │ Goalie Stats (Both Teams)                  │         │
│ └────────────────────────────────────────────┘         │
├─────────────────────────────────────────────────────────┤
│ SHOT MAP TAB:                                           │
│ ┌────────────────────────────────────────────┐         │
│ │ Shot Map (Interactive Rink Diagram)        │         │
│ │ [Shots, Goals, xG bubbles]                 │         │
│ └────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────┘
```

#### 1.5.2 Game Recap Page
**Data Sources:** `fact_events`, `fact_player_game_stats`, `fact_goalie_game_stats`

**Features:**
- Game summary
- Highlights timeline
- Key players
- Key moments
- Full boxscore
- Shot map

#### 1.5.3 Shift Charts
**Data Sources:** `fact_shifts`, `fact_shift_players`

**Features:**
- Shift timeline for each player
- Line combinations visualization
- TOI breakdown
- Shift quality analysis

---

### 1.6 Advanced Analytics Dashboards (15+ Pages)

#### 1.6.1 Advanced Metrics Hub
**Data Sources:** All advanced stat tables

**Features:**
- xG Analysis Dashboard
- WAR/GAR Leaders
- RAPM Analysis (future)
- Micro Stats Explorer
- Zone Analytics
- Rush Analysis
- Faceoff Analysis

#### 1.6.2 xG Analysis Dashboard
**Data Sources:** `fact_player_game_stats` (xg_for, xg_adj, goals_above_expected), `fact_events`, `fact_shot_event`

**Features:**
- xG Leaders
- Goals Above Expected
- xG Timeline (Game Flow)
- Shot Quality Analysis
- xG by Situation
- xG Trends

#### 1.6.3 WAR/GAR Leaders Dashboard
**Data Sources:** `fact_player_game_stats`, `fact_goalie_game_stats`

**Features:**
- WAR Leaders (Players & Goalies)
- GAR Component Breakdown
- WAR Trends
- WAR by Position
- WAR by Season

#### 1.6.4 Micro Stats Explorer
**Data Sources:** `fact_player_micro_stats`, `fact_player_game_stats`

**Features:**
- Interactive micro stats explorer
- Deke success rates
- Zone entry/exit success
- Rush involvement
- Pressure performance
- Detailed micro stat breakdowns

#### 1.6.5 Zone Analytics Dashboard
**Data Sources:** `fact_zone_entries`, `fact_zone_exits`, `fact_team_zone_time`, `fact_player_game_stats`

**Features:**
- Zone Entry Analysis
- Zone Exit Analysis
- Zone Time Analysis
- Zone Entry/Exit Success Rates
- Zone Time Heat Maps

#### 1.6.6 Rush Analysis Dashboard
**Data Sources:** `fact_rushes`, `fact_rush_events`, `fact_player_game_stats`

**Features:**
- Rush Leaders
- Rush Success Rates
- Breakaway Analysis
- Odd-Man Rush Analysis
- Rush xG Analysis

#### 1.6.7 Faceoff Analysis Dashboard
**Data Sources:** `fact_faceoffs`, `fact_player_game_stats`

**Features:**
- Faceoff Leaders
- Faceoff Win % by Zone
- WDBE Faceoff Analysis
- Faceoff Outcomes
- Faceoff Trends

---

## Part 2: Advanced Reports (30+ Report Types)

### 2.1 Player Reports

1. **Player Performance Report** (PDF/CSV)
   - Season summary
   - Game-by-game breakdown
   - Advanced metrics
   - Charts and graphs

2. **Player Comparison Report** (PDF)
   - Side-by-side comparison
   - Statistical analysis
   - Visualizations

3. **Player Trend Report** (PDF)
   - Performance trends over time
   - Rolling averages
   - Streak analysis

4. **Player Advanced Metrics Report** (PDF)
   - WAR/GAR breakdown
   - xG analysis
   - Micro stats breakdown
   - Zone analytics

5. **Player Scouting Report** (PDF)
   - Comprehensive player evaluation
   - Strengths and weaknesses
   - Recommendations

### 2.2 Goalie Reports

6. **Goalie Performance Report** (PDF/CSV)
   - Season summary
   - Save breakdown
   - Advanced metrics
   - GSAx analysis

7. **Goalie Comparison Report** (PDF)
   - Side-by-side comparison
   - Save type analysis
   - Advanced metrics

8. **Goalie Scouting Report** (PDF)
   - Comprehensive evaluation
   - Save technique analysis
   - Performance trends

### 2.3 Team Reports

9. **Team Performance Report** (PDF/CSV)
   - Season summary
   - Roster analysis
   - Line combinations
   - Zone time analysis

10. **Team Comparison Report** (PDF)
    - Side-by-side comparison
    - Statistical analysis

11. **Team Line Analysis Report** (PDF)
    - Line combination performance
    - WOWY analysis
    - Recommendations

12. **Team Zone Time Report** (PDF)
    - Zone time breakdown
    - Zone time by situation
    - Visualizations

### 2.4 Game Reports

13. **Game Recap Report** (PDF)
    - Game summary
    - Key moments
    - Player highlights
    - Shot map

14. **Game Analytics Report** (PDF)
    - Advanced game analysis
    - xG timeline
    - Shift analysis
    - Zone time analysis

15. **Play-by-Play Report** (PDF/CSV)
    - Complete event log
    - Timestamps
    - Player involvement

### 2.5 Advanced Analytics Reports

16. **xG Analysis Report** (PDF)
    - xG leaders
    - Goals above expected
    - Shot quality analysis

17. **WAR/GAR Report** (PDF)
    - WAR leaders
    - GAR component breakdown
    - Position analysis

18. **Micro Stats Report** (PDF)
    - Micro stats breakdown
    - Success rates
    - Trends

19. **Zone Analytics Report** (PDF)
    - Zone entry/exit analysis
    - Zone time analysis
    - Success rates

20. **Rush Analysis Report** (PDF)
    - Rush leaders
    - Success rates
    - Breakaway analysis

21. **Faceoff Analysis Report** (PDF)
    - Faceoff leaders
    - WDBE analysis
    - Zone analysis

### 2.6 Custom Reports

22. **Custom Report Builder**
    - Drag-and-drop interface
    - Select tables/columns
    - Apply filters
    - Choose visualization types
    - Export formats (PDF, CSV, Excel, JSON)

23. **Scheduled Reports**
    - Daily/weekly/monthly reports
    - Email delivery
    - Automated generation

24. **Comparative Reports**
    - Compare any entities (players, teams, seasons)
    - Statistical significance testing
    - Visualizations

---

## Part 3: Machine Learning Applications (20+ ML Models)

### 3.1 Predictive Models

1. **Game Outcome Prediction**
   - Input: Team stats, player stats, matchup history
   - Output: Win probability, predicted score
   - Model: XGBoost/Random Forest
   - Data: `fact_team_season_stats`, `fact_player_season_stats`, `fact_h2h`

2. **Player Performance Prediction**
   - Input: Historical stats, recent form, opponent quality
   - Output: Predicted goals, points, xG
   - Model: Time series (LSTM/GRU)
   - Data: `fact_player_game_stats`, `fact_player_season_stats`

3. **Goalie Performance Prediction**
   - Input: Historical saves, shot quality, workload
   - Output: Predicted save %, GSAx
   - Model: XGBoost
   - Data: `fact_goalie_game_stats`, `fact_saves`

4. **Injury Risk Prediction**
   - Input: TOI, shift patterns, workload, age
   - Output: Injury risk score
   - Model: Classification (Random Forest)
   - Data: `fact_player_game_stats`, `fact_shifts`

### 3.2 Player Valuation Models

5. **Player Value Model**
   - Input: WAR, GAR, stats, age, position
   - Output: Player value score
   - Model: Regression (XGBoost)
   - Data: `fact_player_career_stats`, `fact_player_season_stats`

6. **Contract Value Prediction**
   - Input: Performance, age, position, league averages
   - Output: Predicted contract value
   - Model: Regression
   - Data: `fact_player_career_stats`

7. **Draft Value Model**
   - Input: Player stats, age, position
   - Output: Draft value score
   - Model: Classification/Regression
   - Data: `fact_draft`, `fact_player_career_stats`

### 3.3 Advanced Analytics Models

8. **Expected Goals (xG) Model Enhancement**
   - Current: Lookup table
   - Target: Gradient Boosting Machine (GBM)
   - Features: Shot location (when XY available), shot type, context
   - Data: `fact_events`, `fact_shot_event`

9. **RAPM (Regularized Adjusted Plus-Minus)**
   - Input: Stint data (player combinations, outcomes)
   - Output: Isolated player impact
   - Model: Ridge Regression
   - Data: `fact_shift_players`, `fact_events` (requires stint structure)

10. **Expected Threat (xT) Model**
    - Input: Zone transitions, shot outcomes
    - Output: Zone value, transition value
    - Model: Markov Chain
    - Data: `fact_zone_entries`, `fact_zone_exits`, `fact_events`

11. **Player Similarity Model**
    - Input: Player stats, play style
    - Output: Similarity scores
    - Model: Clustering (K-Means), Embeddings
    - Data: `fact_player_career_stats`, `fact_player_micro_stats`

12. **Line Optimization Model**
    - Input: Player combinations, historical performance
    - Output: Optimal line combinations
    - Model: Optimization (Genetic Algorithm) + Regression
    - Data: `fact_line_combos`, `fact_wowy`

### 3.4 Anomaly Detection

13. **Performance Anomaly Detection**
    - Input: Player stats over time
    - Output: Anomaly flags (over/under performance)
    - Model: Isolation Forest, Autoencoders
    - Data: `fact_player_game_stats`, `fact_player_season_stats`

14. **Suspicious Stats Detection**
    - Input: Game stats, historical patterns
    - Output: Suspicious game flags
    - Model: Statistical tests, ML classification
    - Data: `fact_suspicious_stats`, `fact_player_game_stats`

### 3.5 Clustering & Segmentation

15. **Player Type Clustering**
    - Input: Player stats, micro stats
    - Output: Player archetypes (power forward, playmaker, etc.)
    - Model: K-Means, Hierarchical Clustering
    - Data: `fact_player_career_stats`, `fact_player_micro_stats`

16. **Team Style Clustering**
    - Input: Team stats, playing style
    - Output: Team archetypes
    - Model: Clustering
    - Data: `fact_team_season_stats`, `fact_team_zone_time`

### 3.6 Recommendation Systems

17. **Line Recommendation System**
    - Input: Available players, opponent, game state
    - Output: Recommended line combinations
    - Model: Collaborative Filtering, Optimization
    - Data: `fact_line_combos`, `fact_wowy`

18. **Player Recommendation System**
    - Input: Team needs, player availability
    - Output: Recommended players
    - Model: Content-Based Filtering
    - Data: `fact_player_career_stats`, `fact_player_season_stats`

### 3.7 Time Series Analysis

19. **Performance Trend Analysis**
    - Input: Time series of player stats
    - Output: Trend identification, forecasting
    - Model: ARIMA, Prophet, LSTM
    - Data: `fact_player_game_stats`, `fact_player_trends`

20. **Season Long Trends**
    - Input: Season stats over time
    - Output: Team/player trajectory
    - Model: Time series analysis
    - Data: `fact_player_season_stats`, `fact_team_season_stats`

### 3.8 Computer Vision (Future - with Video Data)

21. **Video Analysis Models**
    - Shot recognition
    - Player tracking
    - Event detection
    - Technique analysis

---

## Part 4: Visualization Components Library (100+ Components)

### 4.1 Basic Charts

1. **Line Charts**
   - Time series (Goals/Game, Points/Game)
   - Multi-line (Player comparison)
   - Rolling averages

2. **Bar Charts**
   - Horizontal/Vertical
   - Stacked (Situation splits)
   - Grouped (Comparison)

3. **Pie Charts**
   - Stat distribution
   - Category breakdown

4. **Scatter Plots**
   - xG vs Goals
   - Correlation analysis

5. **Area Charts**
   - Cumulative stats
   - Zone time accumulation

### 4.2 Advanced Visualizations

6. **Radar Charts**
   - Player comparison
   - Multi-dimensional stats

7. **Heat Maps**
   - Shot location
   - Zone time
   - Performance by zone

8. **Shot Maps**
   - Rink diagram with shots
   - xG visualization
   - Goal locations

9. **Shift Charts**
   - Shift timeline
   - Line combinations

10. **Timeline Charts**
    - Game events
    - xG timeline
    - Play-by-play

11. **Sankey Diagrams**
    - Zone transitions
    - Shot chains

12. **Network Graphs**
    - Player connections (assists)
    - Line combinations

13. **Violin Plots**
    - Distribution analysis
    - Comparison

14. **Box Plots**
    - Statistical distribution
    - Outlier detection

### 4.3 Interactive Components

15. **Interactive Tables**
    - Sortable columns
    - Filters
    - Pagination
    - Export

16. **Interactive Filters**
    - Date range
    - Player/Team selector
    - Stat selector
    - Situation filters

17. **Hover Tooltips**
    - Detailed stats on hover
    - Contextual information

18. **Zoom/Pan**
    - Charts with zoom
    - Detailed exploration

19. **Drill-Down**
    - Click to explore details
    - Navigation hierarchy

---

## Part 5: Data Utilization Matrix

### Complete Table → Feature Mapping

| Table | Dashboard Pages | Reports | ML Models | Visualizations |
|-------|----------------|---------|-----------|----------------|
| `fact_player_game_stats` (317 cols) | Player Profile, Player Comparison, Player Trends, Advanced Analytics | Player Reports, Performance Reports | Performance Prediction, Player Value, Anomaly Detection | Line Charts, Bar Charts, Radar Charts, Tables |
| `fact_goalie_game_stats` (128 cols) | Goalie Profile, Goalie Comparison, Goalie Analytics | Goalie Reports, Performance Reports | Goalie Performance Prediction, GSAx Model | Save Location Maps, Bar Charts, Line Charts |
| `fact_events` (140 cols) | Game Center, Play-by-Play, Shot Maps | Game Reports, Event Analysis | xG Model, Event Prediction | Timeline, Shot Maps, Heat Maps |
| `fact_shift_players` (86 cols) | Shift Charts, Line Analysis | Shift Reports | RAPM Model, Line Optimization | Shift Charts, Timeline |
| `fact_player_micro_stats` | Micro Stats Explorer, Player Profile | Micro Stats Reports | Player Similarity, Clustering | Bar Charts, Heat Maps |
| `fact_zone_entries` / `fact_zone_exits` | Zone Analytics, Team Analysis | Zone Reports | xT Model, Zone Optimization | Heat Maps, Flow Diagrams |
| `fact_rushes` / `fact_rush_events` | Rush Analysis, Player Profile | Rush Reports | Rush Success Prediction | Bar Charts, Timeline |
| `fact_faceoffs` | Faceoff Analysis, Player Profile | Faceoff Reports | Faceoff Success Prediction | Pie Charts, Bar Charts |
| `fact_wowy` | Team Analysis, Line Analysis | WOWY Reports | Line Optimization | Network Graphs, Bar Charts |
| `fact_matchup_performance` | Player Matchups, Team Analysis | Matchup Reports | Matchup Prediction | Heat Maps, Comparison Charts |
| `fact_player_qoc_summary` | Player Profile, Advanced Analytics | Quality Reports | Performance Adjustment | Bar Charts, Line Charts |
| `fact_line_combos` | Team Lines, Line Analysis | Line Reports | Line Optimization | Network Graphs, Bar Charts |
| `fact_team_zone_time` | Team Analysis, Zone Analytics | Zone Reports | Zone Optimization | Heat Maps, Bar Charts |
| `fact_saves` | Goalie Profile, Save Analysis | Save Reports | Save Prediction | Heat Maps, Bar Charts |
| `fact_xg_*` (future) | xG Analysis, Player Profile | xG Reports | xG Model | Shot Maps, Bar Charts |

---

## Part 6: Implementation Priority

### Phase 1: Core Dashboards (Weeks 1-4)
1. Player Profile Page (Basic)
2. Goalie Profile Page (Basic)
3. Team Profile Page
4. Game Center (Basic)
5. Leaderboards
6. Standings

### Phase 2: Advanced Dashboards (Weeks 5-8)
7. Player Comparison
8. Goalie Comparison
9. Advanced Analytics Hub
10. xG Analysis Dashboard
11. WAR/GAR Leaders
12. Micro Stats Explorer

### Phase 3: Reports & Export (Weeks 9-12)
13. Player Reports (PDF/CSV)
14. Goalie Reports (PDF/CSV)
15. Team Reports
16. Game Reports
17. Custom Report Builder

### Phase 4: ML Models (Weeks 13-16+)
18. xG Model Enhancement
19. Performance Prediction
20. Player Valuation
21. RAPM (when data ready)
22. Anomaly Detection

---

## Part 7: Technical Stack Recommendations

### Frontend
- **Framework:** Next.js 14 (React)
- **Charts:** Recharts, D3.js, Chart.js
- **Tables:** TanStack Table (React Table)
- **Maps:** Custom Rink Diagrams (SVG/Canvas)
- **UI Components:** shadcn/ui, Tailwind CSS

### Backend
- **API:** Next.js API Routes / Supabase Edge Functions
- **Database:** Supabase (PostgreSQL)
- **Real-time:** Supabase Realtime
- **Caching:** Redis (for expensive queries)

### ML/Data Science
- **ML Framework:** scikit-learn, XGBoost, LightGBM
- **Deep Learning:** PyTorch, TensorFlow (if needed)
- **Time Series:** Prophet, ARIMA
- **API:** Python FastAPI service (for ML models)

### Reports
- **PDF Generation:** Puppeteer, PDFKit
- **Excel:** ExcelJS
- **Templates:** React-PDF, PDFMake

---

## Conclusion

This vision document outlines a comprehensive strategy to utilize **ALL** of BenchSight's data infrastructure across 50+ dashboard pages, 30+ report types, and 20+ ML models. The key is to:

1. **Start with core dashboards** (Player/Goalie/Team profiles)
2. **Build advanced analytics** (xG, WAR, Micro Stats)
3. **Add reporting capabilities** (PDF/CSV exports)
4. **Implement ML models** (Predictions, Valuations, Optimizations)

The data is there. The infrastructure is solid. Now it's time to build the interfaces that make this data accessible, actionable, and valuable for coaches, players, and analysts.

**Next Steps:**
1. Review and prioritize features
2. Create detailed wireframes for Phase 1
3. Set up development environment
4. Begin implementation

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-13  
**Status:** Draft - Ready for Review
