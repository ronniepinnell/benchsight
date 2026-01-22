# Dashboard Wireframes

**Comprehensive wireframe documentation based on UI inspiration screenshots**

Last Updated: 2026-01-21

---

## Overview

This document provides detailed wireframe layouts and design patterns extracted from professional hockey analytics UI inspiration screenshots. These wireframes serve as the design reference for BenchSight dashboard development.

**Screenshot Sources:**
- `docs/reference/inspiration/screenshots/analytics/` - 65 screenshots
- `docs/reference/inspiration/screenshots/game-pages/` - 15 screenshots
- `docs/reference/inspiration/screenshots/player-pages/` - 9 screenshots

**Inspired by:** Evolving Hockey, HockeyViz, Natural Stat Trick, MoneyPuck, Hockey Reference

---

## Table of Contents

1. [Player Page Wireframes](#player-page-wireframes)
2. [Game Page Wireframes](#game-page-wireframes)
3. [Team Page Wireframes](#team-page-wireframes)
4. [Analytics Dashboard Wireframes](#analytics-dashboard-wireframes)
5. [Data Tables Wireframes](#data-tables-wireframes)
6. [Chart & Visualization Wireframes](#chart--visualization-wireframes)
7. [Filter Panel Wireframes](#filter-panel-wireframes)
8. [Common Patterns](#common-patterns)
9. [Design Guidelines](#design-guidelines)

---

## Player Page Wireframes

### Player Profile Card (Compact)

```
┌────────────────────────────────────────────────────────────────────────┐
│  ┌──────────┐                                                          │
│  │  Player  │   Luke Evangelista #77                                   │
│  │  Photo   │   Nashville Predators                                    │
│  │          │                                                          │
│  └──────────┘   Position: R | Shoots: Right | Size: 6'0", 183lb       │
│                 Birthdate: February 21, 2002 (23y, 10m, 25d)          │
│                 Born: Toronto, ON, CAN | Nationality: CAN              │
│                 Draft: NHL Entry 2020, 2nd Round, 42nd Overall        │
└────────────────────────────────────────────────────────────────────────┘
```

### Player Dashboard (Season Summary)

```
┌────────────────────────────────────────────────────────────────────────┐
│  Dashboard                                                              │
├────────────────────────────────────────────────────────────────────────┤
│  Player    Season   Team       GP   TOI     G   A   Pts  Sh%   FO%    │
│  ────────────────────────────────────────────────────────────────────  │
│  Evangelista 22-23  Predators  24   397.8   7   8   15   13    -      │
│  Evangelista 23-24  Predators  80   1116.4  16  23  39   9.3   25     │
│  Evangelista 24-25  Predators  68   943.3   10  22  32   7.5   0      │
│  Evangelista 25-26  Predators  45   746.8   6   25  31   5.9   11     │
│  ────────────────────────────────────────────────────────────────────  │
│  Total              -          217  3204.2  39  78  117  8.4   12.5   │
├────────────────────────────────────────────────────────────────────────┤
│  Box Score - All Situations                                            │
├────────────────────────────────────────────────────────────────────────┤
│  Player    Season   Team       GP   TOI/GP  G   A1  A2  Pts  ISF  Sh%  │
│  ────────────────────────────────────────────────────────────────────  │
│  [Season-by-season breakdown with advanced metrics]                    │
└────────────────────────────────────────────────────────────────────────┘
```

### Player Shot Chart

```
┌────────────────────────────────────────────────────────────────────────┐
│  ┌─────────────────────┐   MacKenzie Weegar (D)                        │
│  │ Skater Shot Charts  │   Skaters For / Against                       │
│  └─────────────────────┘                                               │
├────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐           Strength: 5v5                               │
│  │ Player ▼    │           Team(s): CGY                                │
│  │ MacKenzie   │           Season(s): 25-26                            │
│  │ Weegar      │           Fenwick Shots: 115                          │
│  └─────────────┘           Total Goals: 3                              │
│  ┌─────────────┐           Total xG: 2.2                               │
│  │ Season(s) ▼ │                                                       │
│  │ 2025/2026   │   ┌─────────────────────────────────────────────────┐ │
│  └─────────────┘   │                 RINK DIAGRAM                     │ │
│  ┌─────────────┐   │        ┌─────────────────────┐                   │ │
│  │ Span ▼      │   │        │    ○   ○    ○      │                   │ │
│  │ Regular     │   │    ┌───┤      ○  ●  ○       │───┐               │ │
│  └─────────────┘   │    │   │   ○    ○   ○  ○   │   │               │ │
│  ┌─────────────┐   │    │   │ ○   ○    ○   ○  ○ │   │               │ │
│  │ Strength ▼  │   │    │   │○  ○   (G)  ○   ○ ○│   │               │ │
│  │ 5v5         │   │    │   │ ○   ○    ○   ○    │   │               │ │
│  └─────────────┘   │    │   │   ○    ○   ○      │   │               │ │
│  ┌─────────────┐   │    └───┤      ○  ○  ○      │───┘               │ │
│  │ Scale to xG │   │        │    ○   ○          │                   │ │
│  │ Yes ▼       │   │        └─────────────────────┘                   │ │
│  └─────────────┘   │                                                   │ │
│                    │  ○ Shot  ● Goal  Size = xG value                 │ │
│  [Submit]          └─────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

### Player Card (Advanced Metrics)

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Player Cards                                     │
├────────────────────────────────────────────────────────────────────────┤
│  Dylan Strome, WSH                    ┌──────┐   Team: All             │
│  5v5 TOI: 305.4                       │[Photo]│  Year: 2022-23         │
│  Year: 2022-23                        └──────┘                         │
├────────────────────────────────────────────────────────────────────────┤
│  General Offense        Z-Scores [Relative to league average]          │
│  ─────────────────      ─────────────────────────────────────          │
│  Shot Attempts/60       █████████████████████░░░░  1.43                │
│  Time Shot Contribution █████████████████░░░░░░░░  0.94                │
│  Rush Chances/60        ██████████████████░░░░░░░  1.02                │
│  Chances/60             ████████████░░░░░░░░░░░░░  0.47                │
│                                                                         │
│  Passing               Z-Scores                                         │
│  ─────────────────     ─────────────────────────────────────           │
│  Point Assist Attempts  ████████████████░░░░░░░░░  0.75                │
│  High-Danger Assists/60 █████████████████░░░░░░░░  0.97                │
│                                                                         │
│  Offensive Types       Z-Scores                                         │
│  ─────────────────     ─────────────────────────────────────           │
│  Cycle & Forecheck %   ░░░░░░░░░░░░░░░░░░░░░░░░░  -0.63                │
│  Setup off Hit Pass/60 ███████████████░░░░░░░░░░░  0.39                │
│  Wraparound            ██████████░░░░░░░░░░░░░░░░  -0.18               │
│  One Timer             ████████████████████████░░  1.23                │
│                                                                         │
│  Zone Entries          Z-Scores                                         │
│  ─────────────────     ─────────────────────────────────────           │
│  Controlled Entries    ░░░░░░░░░░░░░░░░░░░░░░░░░  -0.36                │
│  Entry as Passing Play ░░░░░░░░░░░░░░░░░░░░░░░░░  -0.45                │
│                                                                         │
│  Zone Exits            Z-Scores                                         │
│  ─────────────────     ─────────────────────────────────────           │
│  Controlled Entry vs O ░░░░░░░░░░░░░░░░░░░░░░░░░  -0.36                │
│  Retrievals/60         ████████████████████░░░░░  1.04                 │
│                                                                         │
│  Forechecking          Z-Scores                                         │
│  ─────────────────     ─────────────────────────────────────           │
│  Forecheck %           ███████████████████████░░░  1.44                │
│  F/C as Possession/60  ██████████████████████░░░░  1.21                │
└────────────────────────────────────────────────────────────────────────┘
```

### Player Overview (Dark Theme - HockeySkytte Style)

```
┌────────────────────────────────────────────────────────────────────────┐
│ ████████████████████████████████████████████████████████████████████████│
│ ██                      Skaters        Goalies                       ██│
├────────────────────────────────────────────────────────────────────────┤
│ ██  ┌──────┐    Joe Thornton  ▼   Position  ┌─────┬─────┬─────┬─────┐██│
│ ██  │Photo │                        F       │ GP  │Goals│Assists│Pts │██│
│ ██  │      │                               │1,714│ 430 │1,109│1,539│██│
│ ██  └──────┘                                └─────┴─────┴─────┴─────┘██│
├────────────────────────────────────────────────────────────────────────┤
│ ██  Overview  │  Career Stats  │  Versus  │  Table View  │  About    ██│
├────────────────────────────────────────────────────────────────────────┤
│ ██  Season ▼     Ice time              Giveaways/Takeaways          ██│
│ ██  All          ───────────────       ─────────────────────         ██│
│ ██               GP  ████████████ 1714 Give ████████████████ 1306    ██│
│ ██  Season State TOI ████████████ 35,069 Take ██████████████ 1274    ██│
│ ██  regular ▼                                                        ██│
│ ██               Production            Shooting                      ██│
│ ██  Totals/Rates ───────────────       ─────────────────────         ██│
│ ██  Totals ▼     Goals ██████████ 430   SOG ████████████████ 4860    ██│
│ ██               Assists █████████ 1109 Sh% █████░░░░░░░░░░░ 8.85    ██│
│ ██  Raw/Percentile Points █████████ 1539                             ██│
│ ██  Raw ▼        PPG ░░░░░░░░░░░░ 0.9   ┌────────────────────────┐   ██│
│ ██                                      │  [Player Action Photo]  │   ██│
│ ██  Era Adjusted Defense                │                          │   ██│
│ ██  Raw ▼        ───────────────        └────────────────────────┘   ██│
│ ██               Hits ██████████ 1300                                ██│
│ ██               +/- █████████░░ 185                                 ██│
│ ██               PIM ██████████ 1272                                 ██│
│ ██                                                                   ██│
│ ██  Viz by HockeySkytte                                              ██│
│ ██  Data from NHL API                                                ██│
│ ████████████████████████████████████████████████████████████████████████│
└────────────────────────────────────────────────────────────────────────┘
```

### Key Components

- **Header Section**
  - Player name, team logo, position
  - Photo placeholder (optional)
  - Quick stats summary (GP, G, A, Pts)

- **Stats Display**
  - Season totals
  - Per-game averages (per 60 minutes)
  - Career totals
  - Z-scores for league comparison

- **Tab Navigation**
  - Overview (default)
  - Career Stats
  - Versus (matchup data)
  - Table View
  - About (bio)

---

## Game Page Wireframes

### Game Overview with Win Probability Chart

```
┌────────────────────────────────────────────────────────────────────────┐
│  Overview │ Cumulative Charts │ Shot Charts │ Skater Charts │          │
│           │                   │             │ Shift Charts  │ Player   │
│           │                   │             │               │ Tables   │
├────────────────────────────────────────────────────────────────────────┤
│  Season:        Team:         Game:                                    │
│  ┌───────────┐  ┌───────────┐  ┌─────────────────────────┐             │
│  │ 2025/2026 │▼ │ LA       │▼  │ VGK at LA, 2026-01-14   │▼  [Submit] │
│  └───────────┘  └───────────┘  └─────────────────────────┘             │
├────────────────────────────────────────────────────────────────────────┤
│              Vegas Golden Knights at Los Angeles Kings - 2026-01-14    │
│                           Score: VGK 3 - LA 2 (OT)                     │
│                                                                         │
│  100%┤                                                    ▲ Kings      │
│      │                                                   ╱             │
│   75%├────────────────────────────────────────────────  ╱──────────── │
│      │                                                ╱                │
│   50%├══════════════════════════════════════════════╤════════════════ │
│      │                              ●              ╱                   │
│   25%├─────────────────────────────●──────────────╱────────────────── │
│      │            ░░░░░│░░░░░░░░░░│             ╱    PP Team          │
│    0%├────────────────────────────────────────────────────────────────│
│      0         20         40         60         ▼ Golden Knights      │
│                        Game Minutes                                    │
│  Legend: █ LA Power Play  ░ VGK Power Play  ● Goal Scored             │
└────────────────────────────────────────────────────────────────────────┘
```

### Cumulative Corsi/xG Charts

```
┌────────────────────────────────────────────────────────────────────────┐
│  Season:        Team:         Game:           Strength: Score Adj:    │
│  ┌───────────┐  ┌───────────┐  ┌────────────┐ ┌──────┐  ┌─────┐       │
│  │ 2025/2026 │▼ │ LA       │▼  │VGK@LA 01-14│▼│ All ▼│  │Yes ▼│       │
│  └───────────┘  └───────────┘  └────────────┘ └──────┘  └─────┘       │
│  CF SD: [ 3 ]   xGF SD: [ 2.5 ]                           [Submit]    │
├────────────────────────────────────────────────────────────────────────┤
│              Vegas Golden Knights at Los Angeles Kings - 2026-01-14    │
│                           Score: VGK 3 - LA 2 (OT)                     │
│                   CF (All, Adj): VGK 46.2 - LA 52.2 (OT)              │
│                                                                         │
│   70 ┤                                           ●──────●  Team       │
│      │                          ░░░░░│        ●╱         ▬▬ LA        │
│   60 ├─────────────────────NHL Average──────────────────── ── VGK     │
│      │                                    ●                            │
│   50 ├─────────────────────────────────●──────────────────────────── │
│      │                              ●                                  │
│   40 ├──────────────────────────●─────────────────────────────────── │
│      │                  ●──●──●                                        │
│   30 ├──────────────●───────────────────────────────────────────────  │
│      │        ●──●                                                     │
│   20 ├────●──●───────────────────────────────────────────────────── │
│      │  ●                                                              │
│   10 ├●──────────────────────────────────────────────────────────── │
│      │                                                                 │
│    0 ├─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────── │
│      0    10    20    30    40    50    60    65                      │
│                         Game Minutes                                   │
│                                                                         │
│  █ Period Break   ░ Power Play   ● Goal Event                         │
└────────────────────────────────────────────────────────────────────────┘
```

### Skater Scatter Charts (Quadrant View)

```
┌────────────────────────────────────────────────────────────────────────┐
│  Overview │ Cumulative Charts │ Shot Charts │ Skater Charts │ Shift   │
├────────────────────────────────────────────────────────────────────────┤
│  Season:        Team:         Game:           Corsi SDs:  xG SDs:     │
│  ┌───────────┐  ┌───────────┐  ┌────────────┐ [ 3 ]       [ 3 ]       │
│  │ 2025/2026 │▼ │ LA       │▼  │VGK@LA 01-14│▼                        │
│  └───────────┘  └───────────┘  └────────────┘            [Submit]     │
├────────────────────────────────────────────────────────────────────────┤
│  Away Skaters                                                          │
├────────────────────────────────────────────────────────────────────────┤
│  Vegas Golden Knights at LA Kings          VGK at LA Kings             │
│  VGK skaters - on ice CF/CA per 60        VGK skaters - on ice xGF/xGA │
│                                                                         │
│        Bad │ Good                                Bad │ Good             │
│  4 ┤  ○Kolesar  ○Hertl               4 ┤  ○Stephenson   ●Kolesar      │
│    │      ○T.Hague ○B.Bowman            │     ○Hertl  ○T.Hague         │
│  3 ├──────○K.Korczak────────────     3 ├────●Eichel──○Korczak─────── │
│    │ ○Eichel ○Bayer                      │         ○Bayer              │
│  2 ├───────●Reinhardt────────────    2 ├──────────────────────────── │
│    │  ○M.Marner                          │   ○M.Marner                  │
│  1 ├─────────●Dorofeyev──────────    1 ├───────○Dorofeyev────────── │
│    │ ○P.Dorofeyev  ○Sissons             │ ○P.Dorofeyev                 │
│  0 ├──────────────●──────────────    0 ├───────────●─────────────── │
│    │ ○J.Harrod                           │ ○N.Hanifin                   │
│ -1 ├────○R.Smith─────○Stone──────   -1 ├───○R.Smith──○Z.Whitecloud── │
│    │                                     │                              │
│ -2 ├─────────────────────────────   -2 ├──────────────────────────── │
│      Fun │                                  Fun │                       │
│    ├─────┼─────┼─────┼─────┼───        ├─────┼─────┼─────┼─────┼──   │
│      0   20   40   60   80                 0   20   40   60   80       │
│           EV CF per 60                          EV xGF per 60          │
│                                                                         │
│  TOI: Size of dot indicates time on ice                                │
│       ● = High TOI (>15 min)  ○ = Lower TOI                            │
└────────────────────────────────────────────────────────────────────────┘
```

### Player Tables (Game Box Score)

```
┌────────────────────────────────────────────────────────────────────────┐
│  Overview │ Cumulative │ Shot Charts │ Skater Charts │ Shift │ Player │
│           │   Charts   │             │               │ Charts│ Tables │
├────────────────────────────────────────────────────────────────────────┤
│  Season:        Team:         Game:                                    │
│  ┌───────────┐  ┌───────────┐  ┌────────────────────────────┐          │
│  │ 2025/2026 │▼ │ LA       │▼  │ VGK at LA, 2026-01-14     │▼         │
│  └───────────┘  └───────────┘  └────────────────────────────┘          │
│  Table Type: Position: Strength: Adjustment: Display:                  │
│  ┌──────────┐  ┌──────┐  ┌─────┐  ┌────────────┐  ┌────────┐          │
│  │ Box Score│▼ │ All ▼│  │All ▼│  │No Adjustment│▼ │ Totals │▼         │
│  └──────────┘  └──────┘  └─────┘  └────────────┘  └────────┘          │
│                                                             [Submit]   │
├────────────────────────────────────────────────────────────────────────┤
│  Away Team                                                             │
├────────────────────────────────────────────────────────────────────────┤
│  Player        Position Team  TOI   TOI%  G  A1  A2  Points ISF  iFF  │
│  ─────────────────────────────────────────────────────────────────────│
│  Shea Theodore    D     VGK   23.6  39.1  0  1   0    1     2    3    │
│  Jeremy Lauzon    D     VGK   22    36.4  0  0   0    0     1    4    │
│  Noah Hanifin     D     VGK   21    34.8  0  1   0    1     0    0    │
│  Zach Whitecloud  D     VGK   20.7  34.3  0  0   0    0     0    0    │
│  Mark Stone       R     VGK   20    33    1  0   0    1     3    4    │
│  Jack Eichel      C     VGK   19    31.5  0  1   1    2     5    7    │
│  Ivan Barbashev   L     VGK   18.4  30.4  0  0   0    0     4    6    │
│  Mitch Marner     R     VGK   17    28    0  0   0    0     0    2    │
│  Pavel Dorofeyev  R     VGK   16    26.5  0  0   0    0     0    2    │
│  ─────────────────────────────────────────────────────────────────────│
│  Show: [50 ▼] entries                              Search: [_______]  │
└────────────────────────────────────────────────────────────────────────┘
```

### Game Summary Dashboard (Multi-Chart View)

```
┌────────────────────────────────────────────────────────────────────────┐
│                    CAR 4 at 1 NSH on 17 Dec 2025                       │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐ ┌─────────────────────┐ ┌──────────────────────┐ │
│  │   Shot Pressure  │ │      xG Worm        │ │    xG Breakdown      │ │
│  │                  │ │                     │ │                      │ │
│  │   CAR │ NSH      │ │  CAR 4 at 1 NSH     │ │  ┌───┬───┬───┬───┐  │ │
│  │  ████ │          │ │  ↗                  │ │  │HI │MD │LO │   │  │ │
│  │  ████ │ ██       │ │    ↗               │ │  ├───┼───┼───┼───┤  │ │
│  │  ████ │ ████     │ │      ↗             │ │  │CAR│   │   │   │  │ │
│  │  ████ │ ██       │ │        ↗           │ │  ├───┼───┼───┼───┤  │ │
│  │       │          │ │          ↘         │ │  │NSH│   │   │   │  │ │
│  └──────────────────┘ └─────────────────────┘ └──────────────────────┘ │
│                                                                         │
│  ┌──────────────────────────────────────────┐                          │
│  │        Expected Standings Points         │                          │
│  │                                          │                          │
│  │  CAR 4 at 1 NSH on 17 Dec 2025           │                          │
│  │  ┌────────────────────────────┐          │                          │
│  │  │  xPts: CAR 1.85 - NSH 0.15 │          │                          │
│  │  └────────────────────────────┘          │                          │
│  └──────────────────────────────────────────┘                          │
│                                                                         │
│           Shot Locations (Unblocked Only)                              │
│  ┌──────────────────────┐  ┌──────────────────────┐                    │
│  │  CAR All Situations  │  │  NSH All Situations  │                    │
│  │                      │  │                      │                    │
│  │    ○  ● ○           │  │      ○ ○            │                    │
│  │  ○  ●  ○  ○ ○       │  │    ○   ○ ○          │                    │
│  │    ○ ●●○ ○ ○        │  │      ○ ○            │                    │
│  │      (G)            │  │      (G)            │                    │
│  └──────────────────────┘  └──────────────────────┘                    │
└────────────────────────────────────────────────────────────────────────┘
```

### Key Components

- **Game Header**
  - Team names and logos
  - Final score (with OT/SO indicator)
  - Game date and time
  - Venue information

- **Tab Navigation**
  - Overview (win probability)
  - Cumulative Charts (Corsi/xG flow)
  - Shot Charts (rink diagrams)
  - Skater Charts (scatter plots)
  - Shift Charts (timeline)
  - Player Tables (box score)

- **Chart Types**
  - Win probability line chart
  - Cumulative shot attempt chart
  - xG flow chart
  - Quadrant scatter plots (CF/CA, xGF/xGA)
  - Shot location rink diagrams

---

## Team Page Wireframes

### Team Presence & Importance Chart

```
┌────────────────────────────────────────────────────────────────────────┐
│                       Presence and Importance                          │
├────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐ ┌──────────┐│
│  │  Power Players │ │    Forwards    │ │   Defenders    │ │Penalty   ││
│  │                │ │                │ │                │ │Killers   ││
│  │  Presence and  │ │  Presence and  │ │  Presence and  │ │          ││
│  │  Importance,   │ │  Importance,   │ │  Importance,   │ │Presence  ││
│  │  CAR           │ │  CAR           │ │  CAR           │ │and Imp.  ││
│  │                │ │                │ │                │ │CAR       ││
│  │  2025-2026, PP │ │ 2025-2026, All │ │ 2025-2026, All │ │          ││
│  │                │ │  Situations,   │ │  Situations,   │ │2025-2026 ││
│  │                │ │  Forwards      │ │  Defenders     │ │PK        ││
│  │  ▬▬▬▬▬▬▬▬     │ │                │ │                │ │          ││
│  │  ▬▬▬▬▬        │ │  ═══════════   │ │  ════════      │ │▬▬▬▬▬    ││
│  │  ▬▬▬▬         │ │  ════════      │ │  ═══════       │ │▬▬▬▬     ││
│  │  ▬▬▬          │ │  ═══════       │ │  ══════        │ │▬▬▬      ││
│  │  ▬▬           │ │  ══════        │ │  ═════         │ │▬▬       ││
│  │  ▬            │ │  ═════         │ │  ════          │ │▬        ││
│  │               │ │  ════          │ │  ═══           │ │         ││
│  │               │ │  ═══           │ │  ══            │ │         ││
│  │               │ │  ══            │ │  ═             │ │         ││
│  │               │ │  ═             │ │                │ │         ││
│  └────────────────┘ └────────────────┘ └────────────────┘ └──────────┘│
│                                                                        │
│                          ┌────────────────┐                            │
│                          │    Goalies     │                            │
│                          │                │                            │
│                          │  Presence and  │                            │
│                          │  Importance,   │                            │
│                          │  CAR           │                            │
│                          │                │                            │
│                          │  2025-2026, All│                            │
│                          │  Situations,   │                            │
│                          │  Goalies       │                            │
│                          │                │                            │
│                          │  ║ ║ ║        │                            │
│                          │  ║ ║ ║        │                            │
│                          │  ║ ║          │                            │
│                          └────────────────┘                            │
│                                                                        │
│  Legend: Bar height = Ice time (presence)                              │
│          Bar color intensity = Impact (importance)                     │
└────────────────────────────────────────────────────────────────────────┘
```

### Team Passing Grid (Connection Matrix)

```
┌────────────────────────────────────────────────────────────────────────┐
│  Passing Grid  │  Player Passing Targets                               │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                         SEA Passing Combo Grid                         │
│                                                                         │
│                              Passers →                                  │
│              ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐   │
│              │W.B│A.L│J.E│C.S│M.B│T.K│B.T│J.S│J.M│E.T│O.B│J.O│Y.G│   │
│  ┌───────────┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤   │
│  │Will Borgen│   │ 3 │   │   │   │ 1 │   │   │   │   │   │   │   │   │
│  │Adam Larson│ 1 │   │ 3 │ 2 │   │ 1 │   │   │   │   │   │   │   │   │
│  │Jord.Eberle│   │ 2 │   │ 1 │   │   │ 2 │   │ 1 │   │   │   │   │   │
│S │Chandl.Step│   │   │ 4 │   │ 1 │   │ 1 │   │ 1 │ 1 │   │   │   │   │
│h │Matty Benrs│   │ 1 │   │ 4 │   │ 1 │   │   │   │   │   │   │   │   │
│o │Tye Kartye │   │   │   │   │ 1 │   │ 6 │   │   │   │   │   │   │   │
│o │Brandon Tan│   │   │ 1 │ 2 │   │ 3 │   │ 1 │   │ 2 │   │ 1 │   │   │
│t │Jaden Schw.│ 2 │   │ 1 │   │ 3 │   │   │   │ 6 │   │   │   │   │   │
│e │Jared McCan│   │ 2 │   │   │   │   │   │ 1 │   │ 1 │   │   │   │   │
│r │Eeli Tolvan│   │   │   │   │   │   │ 2 │   │ 1 │   │ 1 │   │ 1 │   │
│s │Oliver Bjor│   │   │   │   │ 2 │   │   │ 4 │   │ 1 │   │   │ 2 │   │
│↓ │Jamie Oleks│   │   │   │   │   │   │   │   │ 2 │   │ 2 │   │   │   │
│  │Josh Mahura│ 1 │   │   │   │   │   │   │   │   │ 2 │   │ 1 │   │   │
│  │Vince Dunn │   │   │   │   │ 1 │   │ 2 │   │   │   │ 2 │   │   │   │
│  │Yanni Gourd│   │   │ 3 │ 1 │   │   │ 1 │ 5 │   │ 3 │   │ 8 │   │   │
│  │Ryker Evans│   │ 3 │   │ 1 │   │   │   │ 1 │   │   │ 2 │   │ 1 │   │
│  │Shane Wrigt│   │   │   │   │ 4 │   │ 1 │   │   │   │   │   │   │   │
│  │Ben Meyers │   │   │   │ 1 │   │   │   │   │   │   │ 1 │   │   │   │
│  │Brandon Mon│   │ 3 │   │   │ 1 │   │   │ 1 │   │   │   │   │ 5 │   │
│  │Andre Burak│ 1 │   │   │   │   │   │   │   │   │ 1 │   │   │   │   │
│  └───────────┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘   │
│                                                                         │
│  Cell Color:  ░ 1-2 passes  ▒ 3-4 passes  █ 5+ passes                 │
└────────────────────────────────────────────────────────────────────────┘
```

### Key Components

- **Header Section**
  - Team name and logo
  - Season record (W-L-OTL)
  - Conference/division position

- **Tab Navigation**
  - Overview
  - Roster
  - Schedule
  - Team statistics

- **Visualization Types**
  - Presence & Importance bars (by position group)
  - Passing connection matrix
  - Team shot charts
  - Line combination analysis

---

## Analytics Dashboard Wireframes

### Advanced Stats Leaderboard Table

```
┌────────────────────────────────────────────────────────────────────────┐
│  Team:      Position:  Baseline:      Display:     Column Select:     │
│  ┌──────┐   ┌──────┐   ┌───────────┐  ┌────────┐   ┌───────────┐      │
│  │ All ▼│   │ All ▼│   │Replacement│▼ │ Totals │▼  │ Basic    ▼│      │
│  └──────┘   └──────┘   └───────────┘  └────────┘   └───────────┘      │
│  Add Info:   Status:                                                   │
│  ┌──────┐   ┌──────┐                                                   │
│  │ No  ▼│   │ All ▼│                                                   │
│  └──────┘   └──────┘                                                   │
│                                                                         │
│  Filter Type:    Season(s):      Span:          Grouping:              │
│  ┌───────────┐   ┌───────────┐   ┌───────────┐  ┌─────────────┐        │
│  │ Seasons  ▼│   │ 2025/2026│▼  │ Regular  ▼│  │ Team,Season▼│        │
│  └───────────┘   └───────────┘   └───────────┘  └─────────────┘        │
│                                                                         │
│  Draft Year:   Age Low:    Age High:                                   │
│  ┌───────┐     ┌───────┐   ┌───────┐                                   │
│  │ All  ▼│     │  17   │   │  50   │                                   │
│  └───────┘     └───────┘   └───────┘                                   │
│                                                                         │
│  Player(s):         Min TOI All: Min TOI EV: Min TOI PP: Min TOI SH:   │
│  ┌──────────────┐   ┌───────┐    ┌───────┐   ┌───────┐   ┌───────┐     │
│  │ [Search...] │   │  50   │    │   0   │   │   0   │   │   0   │     │
│  └──────────────┘   └───────┘    └───────┘   └───────┘   └───────┘     │
│                                                                         │
│                               [Glossary]                    [Submit]   │
├────────────────────────────────────────────────────────────────────────┤
│  Show [50 ▼] entries                                 Search: [______]  │
├────────────────────────────────────────────────────────────────────────┤
│  # │Player       │Season│Team│Pos│GP │TOI All│EVO │EVO │PPO │SHD │... │
│  ──┼─────────────┼──────┼────┼───┼───┼───────┼────┼────┼────┼────┼────│
│  1 │A.J. Greer   │25-26 │FLA │ L │45 │ 526.4 │5.5 │0.4 │0.0 │-0.8│... │
│  2 │Aaron Ekblad │25-26 │FLA │ D │44 │ 987   │3.7 │2.4 │-0.9│-0.7│... │
│  3 │Aatu Raty    │25-26 │VAN │ C │38 │ 457.9 │1.9 │-1.2│0.0 │0.6 │... │
│  4 │Adam Boqvist │25-26 │NYI │ D │14 │ 173.2 │0.2 │1   │    │0.4 │... │
│  5 │Adam Edstrom │25-26 │NYR │ C │24 │ 229.6 │2.1 │0.1 │    │-0.5│... │
│  6 │Adam Engstrom│25-26 │MTL │ D │11 │ 137.9 │0.6 │    │    │-0.2│... │
│  7 │Adam Erne    │25-26 │DAL │ L │19 │ 180   │    │    │    │    │... │
│  8 │Adam Fantilli│25-26 │CBJ │ C │46 │ 857.5 │1.6 │0.0 │-1.5│    │... │
│  9 │Adam Fox     │25-26 │NYR │ D │30 │ 707.2 │4.9 │3.4 │-0.3│-0.1│... │
│ 10 │Adam Gaudette│25-26 │S.J │ R │36 │ 431.2 │1.9 │1.9 │-0.1│0.4 │... │
│  ──┴─────────────┴──────┴────┴───┴───┴───────┴────┴────┴────┴────┴────│
│                                                                         │
│  Columns: GP, TOI All, EVO, EVO, PPO, SHD, Take, Draw, Off, Def, Pens, │
│           GAR, WAR, SPAR                                               │
└────────────────────────────────────────────────────────────────────────┘
```

### Microstat Game Score Dashboard

```
┌────────────────────────────────────────────────────────────────────────┐
│  Game Score │ Game Recaps │ Zone Entries │ Shots & Passes │ Zone Exits│
│  Entry Def. │ Series Breakdown │ Game Score Breakdown │ Individual   │
│  Stats      │ Players By Game                                         │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│           Microstat Game Score by Game, 2024 NHL Playoffs              │
│                                                                         │
│                                            Measure Names               │
│                                            ┌────────────────┐          │
│                                            │Microstat Game ▼│          │
│                                            │Score           │          │
│                                            └────────────────┘          │
│                                                                         │
│                                            Team                        │
│   3.6 ┤                                    ● CAR  ○ COL               │
│       │        ●                           ● DAL  ○ EDM               │
│   3.2 ┤            ●                       ● FLA  ○ LA                │
│       │    ●           ●                   ● MIN  ○ MTL               │
│   2.8 ┤        ●   ●       ●              ● N.J  ○ OTT               │
│       │  ●         ● ●   ● ●    ●        ● STL  ○ T.B                │
│   2.4 ┤    ●    ●     ●     ●       ●    ● TOR  ○ VGK                │
│       │      ●    ●  ●   ●  ● ●  ●       ● WPG  ○ WSH                │
│   2.0 ┤  ●     ● ●  ●● ●●  ● ●  ● ●  ●                               │
│       │    ●  ●  ●●●● ●●●● ●● ●●●●●                                   │
│   1.6 ┤  ● ● ●●●●●●●●●●●●●●●●●●●●●●●●                                 │
│       │ ●●●●●●●●●●●●●●●●●●●●●●●●●●●●●                                 │
│   1.2 ┤●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●                                │
│       │●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●                                │
│   0.8 ┤●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●                                │
│       │●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●                                 │
│   0.4 ┤●●●●●●●●●●●●●●●●●●●●●●●●●●●●●                                  │
│       │●●●●●●●●●●●●●●●●●●●●●●●●●●●●                                   │
│   0.0 ├─┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──                                │
│       Game 1  2  3  4  5  6  7  8  9 10                                │
│                                                                         │
│  Highlight Player: ┌────────────────────┐                              │
│                    │ Highlight Player  ▼│                              │
│                    └────────────────────┘                              │
└────────────────────────────────────────────────────────────────────────┘
```

### Key Components

- **Header Section**
  - Dashboard title
  - Multi-level filter dropdowns
  - Min TOI thresholds

- **Stat Cards**
  - Key metrics at a glance
  - League percentile indicators

- **Chart Area**
  - Scatter plots with team coloring
  - Time series by game
  - Distribution charts

- **Data Tables**
  - Sortable columns
  - Search functionality
  - Pagination controls
  - Column selection

---

## Data Tables Wireframes

### Comprehensive Stats Table with Filters

```
┌────────────────────────────────────────────────────────────────────────┐
│  Table Type:   Position:   Strength:   Adjustment:      Display:       │
│  ┌──────────┐  ┌────────┐  ┌────────┐  ┌─────────────┐  ┌──────────┐  │
│  │Box Score▼│  │ All   ▼│  │ All   ▼│  │No Adjustment▼│  │ Totals  ▼│  │
│  └──────────┘  └────────┘  └────────┘  └─────────────┘  └──────────┘  │
│  Filter Type:  Season(s):     Span:          Grouping:   Add Info:    │
│  ┌──────────┐  ┌───────────┐  ┌───────────┐  ┌────────┐  ┌────────┐   │
│  │Seasons  ▼│  │ 2025/2026▼│  │ Regular  ▼│  │Team,Ssn▼│  │ No    ▼│   │
│  └──────────┘  └───────────┘  └───────────┘  └────────┘  └────────┘   │
│  Player(s):          Age Low:   Age High:   Draft Year:  Status:  Min │
│  ┌───────────────┐   ┌──────┐   ┌──────┐    ┌─────────┐  ┌──────┐ TOI:│
│  │ [Search...]   │   │  17  │   │  50  │    │  All   ▼│  │ All ▼│ 50  │
│  └───────────────┘   └──────┘   └──────┘    └─────────┘  └──────┘     │
│                                                           [Submit]    │
├────────────────────────────────────────────────────────────────────────┤
│  Show [50 ▼] entries                             Search: [__________] │
├────────────────────────────────────────────────────────────────────────┤
│  Player        │Season│Team│Position│GP │TOI  │TOI%│ G │A1 │A2 │Points│
│  ──────────────┼──────┼────┼────────┼───┼─────┼────┼───┼───┼───┼──────│
│  ▲ A.J. Greer  │25-26 │FLA │  L     │45 │526.4│39.1│ 5 │ 4 │ 3 │  12  │
│    Aaron Ekblad│25-26 │FLA │  D     │44 │987  │36.4│ 8 │18 │ 5 │  31  │
│    Aatu Raty   │25-26 │VAN │  C     │38 │457.9│33  │ 4 │ 7 │ 4 │  15  │
│    Adam Boqvist│25-26 │NYI │  D     │14 │173.2│31.5│ 0 │ 3 │ 1 │   4  │
│  ──────────────┴──────┴────┴────────┴───┴─────┴────┴───┴───┴───┴──────│
│                                                                        │
│  Additional Columns: ISF, iFF, ICF, ixG, Sh%, FSh%, iSCF, iHDCF,      │
│                      iBLK, iHA, GIVE, TAKE, PENT, PEND, FO%           │
├────────────────────────────────────────────────────────────────────────┤
│  Showing 1 to 50 of 847 entries              [< Prev] [1 2 3...] [Next>]│
└────────────────────────────────────────────────────────────────────────┘
```

### Box Score Table (Game-Specific)

```
┌────────────────────────────────────────────────────────────────────────┐
│  Away Team - Vegas Golden Knights                                      │
├────────────────────────────────────────────────────────────────────────┤
│  Player        │Pos│Team│ TOI │TOI%│ G │A1│A2│Pts│ISF│iFF│ICF│ixG│Sh%│
│  ──────────────┼───┼────┼─────┼────┼───┼──┼──┼───┼───┼───┼───┼───┼───│
│  Shea Theodore │ D │VGK │23.6 │39.1│ 0 │ 1│ 0│ 1 │ 2 │ 3 │ 1 │0.01│ 0 │
│  Jeremy Lauzon │ D │VGK │22   │36.4│ 0 │ 0│ 0│ 0 │ 1 │ 4 │ 1 │0.01│ 0 │
│  Noah Hanifin  │ D │VGK │21   │34.8│ 0 │ 1│ 0│ 1 │ 0 │ 0 │ 0 │0   │ 0 │
│  Zach Whitecloud│D │VGK │20.7 │34.3│ 0 │ 0│ 0│ 0 │ 0 │ 0 │ 0 │0   │ 0 │
│  Mark Stone    │ R │VGK │20   │33  │ 1 │ 0│ 0│ 1 │ 3 │ 4 │0.52│ 0 │33 │
│  Jack Eichel   │ C │VGK │19   │31.5│ 0 │ 1│ 1│ 2 │ 5 │ 7 │0.22│ 0 │ 0 │
│  Ivan Barbashev│ L │VGK │18.4 │30.4│ 0 │ 0│ 0│ 0 │ 4 │ 6 │0.33│ 0 │ 0 │
│  ──────────────┴───┴────┴─────┴────┴───┴──┴──┴───┴───┴───┴───┴───┴───│
├────────────────────────────────────────────────────────────────────────┤
│  Home Team - Los Angeles Kings                                         │
├────────────────────────────────────────────────────────────────────────┤
│  [Similar structure for home team players]                             │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Chart & Visualization Wireframes

### Rink Shot Chart

```
┌────────────────────────────────────────────────────────────────────────┐
│                           Shot Location Chart                          │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│    ┌─────────────────────────────────────────────────────────────┐     │
│    │                                                             │     │
│    │    ┌─────────────────────────────────────────────────┐     │     │
│    │    │                    ○  ○                         │     │     │
│    │    │               ○  ○    ○  ○                      │     │     │
│    ├────┤           ○  ○  ○  ○    ○  ○                    ├────┤     │
│    │    │        ○  ●  ○  ○  ○  ○    ○                    │    │     │
│    │    │     ○  ○  ○  ●  ○  ○  ○  ○    ○                 │    │     │
│    │    │   ○  ○  ○  ○  ●●  ○  ○  ○  ○    ○               │    │     │
│    │    │  ○  ○  ○  ○  ○(●)○  ○  ○  ○  ○                  │    │     │
│    │    │   ○  ○  ○  ○  ●  ○  ○  ○  ○  ○                  │    │     │
│    │    │     ○  ○  ○  ○  ○  ○  ○  ○                      │    │     │
│    │    │        ○  ○  ●  ○  ○  ○                         │    │     │
│    ├────┤           ○  ○  ○  ○                            ├────┤     │
│    │    │               ○  ○                              │    │     │
│    │    │                    ○                            │    │     │
│    │    └─────────────────────────────────────────────────┘     │     │
│    │                                                             │     │
│    └─────────────────────────────────────────────────────────────┘     │
│                                                                         │
│    Legend:  ○ Shot (miss/save)   ● Goal   Size = xG value              │
│             Color intensity = Danger level                              │
│             (●) = Goalie position                                       │
└────────────────────────────────────────────────────────────────────────┘
```

### Quadrant Scatter Plot

```
┌────────────────────────────────────────────────────────────────────────┐
│              Player Performance Quadrant (CF% vs xGF%)                 │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│       Bad Offense │ Good Offense                                        │
│       Good Defense│ Good Defense                                        │
│   4 ┤             │                     ● Player A                     │
│     │     ○B      │  ●C                                                │
│   3 ┤         ○D  │      ●E                                            │
│     │             │                                                     │
│   2 ┤──────────────────────────────── League Average                   │
│     │             │                                                     │
│   1 ┤    ○F       │   ○G                                               │
│     │             │                                                     │
│   0 ┤─────────────┼──────────────────────────────────────             │
│     │             │                                                     │
│  -1 ┤   ○H        │     ○I                                             │
│     │             │                                                     │
│       Bad Offense │ Good Offense                                        │
│       Bad Defense │ Bad Defense                                         │
│     ├─────┬───────┼───────┬─────┬─────┬─────┬─────┬─────              │
│          40      50      60     70    80    90   100                   │
│                        Corsi For %                                      │
│                                                                         │
│  Dot size = Time on Ice    Color = Team                                │
└────────────────────────────────────────────────────────────────────────┘
```

### Cumulative Flow Chart

```
┌────────────────────────────────────────────────────────────────────────┐
│                    Cumulative xG Flow by Period                        │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│      │                                      Team A ▬▬▬                 │
│   6  ┤                              ●══════════●     Team B ════        │
│      │                         ●═══╱                                   │
│   5  ┤                    ●═══╱                                        │
│      │               ●═══╱                                             │
│   4  ┤          ●═══╱                         ●▬▬▬▬▬▬▬●                │
│      │      ●══╱                         ●▬▬▬╱                         │
│   3  ┤  ●══╱                        ●▬▬▬╱                              │
│      │ ╱                       ●▬▬▬╱                                   │
│   2  ┤●                   ●▬▬▬╱                                        │
│      │               ●▬▬▬╱                                             │
│   1  ┤          ●▬▬▬╱                                                  │
│      │     ●▬▬▬╱                                                       │
│   0  ├●▬▬▬╱─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬────      │
│      0    │    10    │    20    │    30    │    40    │    50         │
│           P1        P1/P2     P2        P2/P3     P3                   │
│                           Game Time (minutes)                          │
│                                                                         │
│  █ Period break   ░ Power Play   ● Goal scored                         │
└────────────────────────────────────────────────────────────────────────┘
```

### Horizontal Bar Chart (Z-Scores)

```
┌────────────────────────────────────────────────────────────────────────┐
│                 Player Z-Scores vs League Average                      │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Metric                  -2    -1     0     1     2    Z-Score         │
│  ───────────────────     ├─────┼─────┼─────┼─────┼─────┤               │
│  Shot Attempts/60        │░░░░░│░░░░░│████████████│     │  +1.43       │
│  Chances/60              │░░░░░│░░░░░│███████░░░░░│     │  +0.47       │
│  High-Danger Assists/60  │░░░░░│░░░░░│█████████░░│     │  +0.97       │
│  Controlled Entries      │░░░░░│░░░░░│░░░░░░░░░░░│     │  -0.36       │
│  Retrievals/60           │░░░░░│░░░░░│████████████│     │  +1.04       │
│  Forecheck %             │░░░░░│░░░░░│█████████████│    │  +1.44       │
│  ───────────────────     └─────┴─────┴─────┴─────┴─────┘               │
│                                                                         │
│  Legend: ████ Above average   ░░░░ Below average                       │
│          │ = League average (0)                                         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Filter Panel Wireframes

### Multi-Select Filter Panel

```
┌────────────────────────────────────────────────────────────────────────┐
│  FILTERS                                                   [Clear All] │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Season                    Position              Situation              │
│  ┌──────────────────┐     ┌───────────────┐     ┌─────────────────┐   │
│  │ [x] 2025-2026    │     │ [x] All       │     │ [x] All         │   │
│  │ [ ] 2024-2025    │     │ [ ] Forwards  │     │ [ ] 5v5         │   │
│  │ [ ] 2023-2024    │     │ [ ] Centers   │     │ [ ] PP          │   │
│  │ [ ] 2022-2023    │     │ [ ] Wings     │     │ [ ] PK          │   │
│  └──────────────────┘     │ [ ] Defense   │     │ [ ] 4v4         │   │
│                           └───────────────┘     └─────────────────┘   │
│                                                                         │
│  Team                      Min TOI               Age Range             │
│  ┌──────────────────┐     ┌───────────────┐     ┌─────────────────┐   │
│  │ Search teams...  │     │ Min: [  50  ] │     │ Min: [ 17 ]     │   │
│  │ [x] All Teams    │     │               │     │ Max: [ 50 ]     │   │
│  │ [ ] ANA          │     │ Max: [ 2000 ] │     │                 │   │
│  │ [ ] ARI          │     └───────────────┘     └─────────────────┘   │
│  │ [ ] BOS          │                                                  │
│  │ ...              │     Score State            Adjustment            │
│  └──────────────────┘     ┌───────────────┐     ┌─────────────────┐   │
│                           │ ( ) All       │     │ ( ) Raw         │   │
│  Player Search            │ ( ) Tied      │     │ (x) Score Adj.  │   │
│  ┌──────────────────┐     │ ( ) Leading   │     │ ( ) Era Adj.    │   │
│  │ [Search player]  │     │ ( ) Trailing  │     └─────────────────┘   │
│  └──────────────────┘     └───────────────┘                           │
│                                                                         │
│                                        [Reset Filters]  [Apply]        │
└────────────────────────────────────────────────────────────────────────┘
```

### Compact Inline Filters

```
┌────────────────────────────────────────────────────────────────────────┐
│  Season:       Team:        Game:          Strength:    Adjustment:    │
│  ┌──────────┐  ┌─────────┐  ┌────────────┐ ┌─────────┐  ┌──────────┐  │
│  │2025/2026▼│  │   LA   ▼│  │VGK@LA 01-14│▼│  All   ▼│  │Score Adj▼│  │
│  └──────────┘  └─────────┘  └────────────┘ └─────────┘  └──────────┘  │
│                                                                         │
│  CF SD: [ 3.0 ]    xGF SD: [ 2.5 ]    Min TOI: [ 10 ]      [Submit]   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Common Patterns

### Tab Navigation Pattern

```
┌────────────────────────────────────────────────────────────────────────┐
│  [Tab 1] │ [Tab 2] │ [Tab 3] │ [Tab 4] │ [Tab 5] │ [Tab 6]            │
│  ════════                                                              │
│  (active tab underlined)                                               │
└────────────────────────────────────────────────────────────────────────┘

Examples:
- Game Page: Overview │ Cumulative Charts │ Shot Charts │ Skater Charts │
             Shift Charts │ Player Tables
- Player Page: Overview │ Career Stats │ Versus │ Table View │ About
- Analytics: Game Score │ Game Recaps │ Zone Entries │ Shots & Passes │
             Zone Exits │ Entry Defense │ Series Breakdown
```

### Sidebar Navigation

```
┌─────────────────┐
│  [Logo]         │
├─────────────────┤
│  ■ Dashboard    │  ← Active (highlighted)
│  □ Players      │
│  □ Teams        │
│  □ Games        │
│  □ Analytics    │
│  □ Reports      │
├─────────────────┤
│  □ Settings     │
│  □ Help         │
└─────────────────┘
```

### Breadcrumb Navigation

```
Home > Players > [Team Name] > [Player Name]
Home > Games > [Season] > [Game Date] > [Matchup]
Home > Analytics > [Chart Type]
```

### Data Display Patterns

**Sortable Table Header:**
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Player ▲▼  │ GP ▲▼       │ Goals ▲▼    │ Points ▲▼   │
├─────────────┼─────────────┼─────────────┼─────────────┤
│ [sorted by this column shows arrow direction]         │
```

**Pagination Controls:**
```
Show [50 ▼] entries    Search: [___________]

Showing 1 to 50 of 847 entries   [< Prev] [1] [2] [3] ... [17] [Next >]
```

**Table Cell Formatting:**
- Numbers: Right-aligned, consistent decimal places
- Text: Left-aligned
- Percentages: Show % symbol, colored (green > 50%, red < 50%)
- Rankings: Bold for top 10, muted for bottom quartile

### Chart Interaction Patterns

**Tooltip on Hover:**
```
┌─────────────────────┐
│ Player: Jack Eichel │
│ CF%: 54.2%          │
│ xGF%: 51.8%         │
│ TOI: 19:34          │
└─────────────────────┘
```

**Legend Toggle:**
```
Team Legend: [■ LA (click to hide)] [□ VGK (hidden)]
```

**Zoom/Pan Controls:**
```
[🔍+] [🔍-] [⟲ Reset] [📥 Export PNG]
```

### Responsive Design

**Desktop (1200px+):**
```
┌──────────┬─────────────────────────────────────────────────┐
│ Sidebar  │  Main Content Area                              │
│          │  ┌─────────────────┬─────────────────┐          │
│          │  │ Chart 1         │ Chart 2         │          │
│          │  └─────────────────┴─────────────────┘          │
│          │  ┌─────────────────────────────────────┐        │
│          │  │ Data Table                          │        │
│          │  └─────────────────────────────────────┘        │
└──────────┴─────────────────────────────────────────────────┘
```

**Tablet (768px-1199px):**
```
┌────────────────────────────────────────────────────────────┐
│ [☰] Navigation Menu (collapsible)                          │
├────────────────────────────────────────────────────────────┤
│ Main Content Area                                          │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ Chart (full width)                                     │ │
│ └────────────────────────────────────────────────────────┘ │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ Data Table (horizontal scroll if needed)               │ │
│ └────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

**Mobile (< 768px):**
```
┌──────────────────────┐
│ [☰] BenchSight       │
├──────────────────────┤
│ Filters (collapsed)  │
│ [▼ Tap to expand]    │
├──────────────────────┤
│ Chart (stacked)      │
├──────────────────────┤
│ Table (card view)    │
│ ┌──────────────────┐ │
│ │ Player: Name     │ │
│ │ GP: 45 │ G: 12   │ │
│ │ A: 23  │ Pts: 35 │ │
│ └──────────────────┘ │
└──────────────────────┘
```

---

## Design Guidelines

### Color Scheme

**Light Theme (Default):**
```
Background:        #FFFFFF (white)
Secondary BG:      #F8F9FA (light gray)
Border:            #DEE2E6 (gray)
Text Primary:      #212529 (dark gray)
Text Secondary:    #6C757D (medium gray)
Primary Accent:    #0D6EFD (blue)
Success:           #198754 (green) - positive stats
Danger:            #DC3545 (red) - negative stats
Warning:           #FFC107 (yellow) - caution/neutral
```

**Dark Theme (HockeySkytte Style):**
```
Background:        #1A1A2E (dark navy)
Secondary BG:      #16213E (darker navy)
Border:            #0F3460 (blue-gray)
Text Primary:      #EAEAEA (off-white)
Text Secondary:    #94A3B8 (muted blue-gray)
Primary Accent:    #E94560 (coral red)
Charts:            Use team colors
```

**Team Colors:**
- Use official NHL team colors for team-specific visualizations
- Maintain accessibility contrast ratios (4.5:1 minimum)
- Provide color-blind friendly alternatives where needed

### Typography

```
Font Family:       'Inter', -apple-system, sans-serif
Headers (H1):      24px, Bold (700), #212529
Headers (H2):      20px, Semi-bold (600), #212529
Headers (H3):      16px, Semi-bold (600), #495057
Body:              14px, Regular (400), #212529
Small/Labels:      12px, Medium (500), #6C757D, uppercase
Data/Numbers:      14px, Tabular nums, monospace preferred
Table Headers:     12px, Bold (700), uppercase, #495057
```

### Spacing System

```
Base unit: 4px

Spacing Scale:
- xs: 4px   (tight spacing within components)
- sm: 8px   (default internal spacing)
- md: 16px  (between related elements)
- lg: 24px  (between sections)
- xl: 32px  (major section breaks)
- 2xl: 48px (page-level spacing)

Grid: 12-column system with 24px gutters
Container max-width: 1440px
Sidebar width: 240px (collapsed: 64px)
```

### Component Specifications

**Cards:**
```
Border radius:     8px
Shadow:            0 1px 3px rgba(0,0,0,0.12)
Padding:           16px
Background:        #FFFFFF
Border:            1px solid #E5E7EB
```

**Buttons:**
```
Primary:           Blue (#0D6EFD), white text, 8px padding
Secondary:         Gray (#6C757D), white text
Height:            36px (default), 32px (small)
Border radius:     6px
```

**Dropdowns/Selects:**
```
Height:            36px
Border:            1px solid #DEE2E6
Border radius:     4px
Padding:           8px 12px
Arrow:             Chevron down icon
```

**Tables:**
```
Header BG:         #F8F9FA
Row height:        40px
Border:            1px solid #DEE2E6 (bottom only)
Hover state:       #F1F3F4 background
Sticky header:     Yes, for scrollable tables
```

---

## Implementation Notes

### React Component Structure

**Player Page Components:**
```
src/app/players/[id]/
├── page.tsx                    # Server component, data fetching
├── PlayerHeader.tsx            # Photo, name, team, position
├── PlayerStats.tsx             # Season summary stats
├── PlayerTabs.tsx              # Tab navigation
├── tabs/
│   ├── OverviewTab.tsx         # Default view
│   ├── CareerStatsTab.tsx      # Season-by-season
│   ├── ShotChartTab.tsx        # Rink visualization
│   └── AdvancedTab.tsx         # Z-scores, micro-stats
└── components/
    ├── StatCard.tsx            # Individual stat display
    ├── SeasonTable.tsx         # Season stats table
    └── ShotChart.tsx           # Rink diagram component
```

**Game Page Components:**
```
src/app/games/[id]/
├── page.tsx
├── GameHeader.tsx              # Teams, score, date
├── GameTabs.tsx
├── tabs/
│   ├── OverviewTab.tsx         # Win probability chart
│   ├── CumulativeChartsTab.tsx # Corsi/xG flow
│   ├── ShotChartsTab.tsx       # Rink diagrams
│   ├── SkaterChartsTab.tsx     # Quadrant scatter
│   ├── ShiftChartsTab.tsx      # Timeline view
│   └── PlayerTablesTab.tsx     # Box score
└── components/
    ├── WinProbabilityChart.tsx
    ├── CumulativeFlowChart.tsx
    ├── QuadrantScatter.tsx
    └── BoxScoreTable.tsx
```

**Analytics Dashboard Components:**
```
src/app/analytics/
├── page.tsx
├── FilterPanel.tsx             # Multi-select filters
├── LeaderboardTable.tsx        # Sortable stats table
└── components/
    ├── FilterDropdown.tsx
    ├── MultiSelect.tsx
    ├── StatTable.tsx
    └── ChartContainer.tsx
```

### Data Fetching Strategy

**Server Components (Default):**
- Initial page load data
- SEO-critical content
- Static filters and options

**Client Components (Interactive):**
- Filter state management
- Chart interactions
- Real-time updates
- User preferences

**Caching Strategy:**
```typescript
// Example: Player stats with revalidation
export const revalidate = 3600; // 1 hour

async function getPlayerStats(playerId: string) {
  const supabase = createServerClient();
  const { data } = await supabase
    .from('fact_player_season_stats')
    .select('*')
    .eq('player_id', playerId);
  return data;
}
```

### Chart Library Recommendations

**Primary: Recharts**
- Line charts, bar charts, area charts
- Good React integration
- Responsive by default

**For Complex Visualizations:**
- D3.js for custom rink diagrams
- Victory Charts for scatter plots
- Visx for advanced data viz

**Rink Diagram Implementation:**
```typescript
// Use SVG viewBox for responsive scaling
<svg viewBox="0 0 200 85" preserveAspectRatio="xMidYMid meet">
  {/* Rink outline */}
  {/* Zones, circles, creases */}
  {/* Shot markers */}
</svg>
```

---

## Accessibility Guidelines

### WCAG 2.1 AA Compliance

**Color Contrast:**
- Text: Minimum 4.5:1 contrast ratio
- Large text (18px+): Minimum 3:1
- UI components: Minimum 3:1

**Keyboard Navigation:**
- All interactive elements focusable
- Visible focus indicators
- Logical tab order
- Skip links for main content

**Screen Reader Support:**
- Descriptive alt text for charts
- ARIA labels on interactive elements
- Table headers properly associated
- Live regions for dynamic updates

**Data Visualization:**
- Don't rely solely on color
- Provide text alternatives
- Pattern fills in addition to colors
- Data tables as alternative to charts

---

## Related Documentation

- [DASHBOARD_ROADMAP.md](../../../dashboard/DASHBOARD_ROADMAP.md) - Dashboard development plan
- [DASHBOARD_COMPONENT_CATALOG.md](../../../dashboard/DASHBOARD_COMPONENT_CATALOG.md) - Existing components
- [inspiration/README.md](../../inspiration/README.md) - Inspiration materials
- [inspiration/screenshots/](../../inspiration/screenshots/) - Source screenshots

---

## Screenshot Reference Index

| Category | Count | Key Patterns |
|----------|-------|--------------|
| Analytics | 65 | Tables, filters, scatter plots, bar charts |
| Game Pages | 15 | Win probability, cumulative charts, box scores |
| Player Pages | 9 | Shot charts, player cards, Z-score displays |

**Recommended Review Order:**
1. `analytics/11.33.47` - Stats table with filters
2. `game-pages/11.35.55` - Win probability chart
3. `player-pages/11.34.09` - Shot chart layout
4. `analytics/11.46.31` - Player overview (dark theme)
5. `game-pages/11.36.41` - Quadrant scatter charts
6. `analytics/11.55.06` - Passing grid matrix
7. `player-pages/11.50.59` - Player cards with Z-scores

---

*Last Updated: 2026-01-21*
*Based on analysis of 89 inspiration screenshots*
