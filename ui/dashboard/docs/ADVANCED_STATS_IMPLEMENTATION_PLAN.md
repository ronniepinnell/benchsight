# Advanced Stats Implementation Plan
## Based on Inspiration Sources & Available Data

**Last Updated:** 2026-01-15  
**Status:** Planning Phase  
**Inspiration Sources:** MoneyPuck, Evolving Hockey, Hockey Graphs, NHL EDGE, JFresh, All Three Zones

---

## Executive Summary

This document outlines a comprehensive plan to implement advanced hockey statistics and micro-stats across the BenchSight dashboard, inspired by leading analytics platforms and utilizing our rich data infrastructure (139 tables, 317 columns in `fact_player_game_stats`).

**Key Goals:**
1. Surface existing advanced stats that are calculated but not displayed
2. Add micro-stats visualizations and breakdowns
3. Create advanced analytics pages similar to MoneyPuck, Evolving Hockey
4. Implement player cards, team dashboards, and game analytics
5. Build interactive exploration tools for micro-stats

---

## Part 1: Available Data Inventory

### 1.1 Core Advanced Stats (Already Calculated)

#### From `fact_player_game_stats` (317 columns):

**Possession Metrics:**
- Corsi For/Against/%
- Fenwick For/Against/%
- Expected Goals (xG), Goals Above Expected
- High/Medium/Low Danger Shot Breakdowns
- Zone Time (Offensive/Defensive/Neutral)

**Zone Play:**
- Zone Entries (Total, Successful, Controlled, Uncontrolled)
- Zone Exits (Total, Successful, Controlled, Uncontrolled)
- Controlled Entry % (Pass, Rush, RushBreakaway)
- Controlled Exit % (Pass, Rush)
- Zone Entry Denials

**Rush & Transition:**
- Rush Shots, Goals, Assists, Points
- Rush Shooting %
- Rush Involvement (count, %)
- Breakaway Goals
- Odd-Man Rushes
- Time from Entry to Shot

**Micro Stats (Offensive):**
- Deke Attempts
- Drives (Middle, Wide, Corner, Total)
- Cutbacks
- Delays
- Crash Net
- Screens
- Give-and-Go
- Second Touch
- Cycles
- One-Timers
- Rebounds (Attempts, Generated)

**Micro Stats (Defensive):**
- Poke Checks
- Stick Checks
- Backchecks
- Forechecks
- Zone Entry Denials
- Loose Puck Wins
- Puck Recoveries
- Board Battles (Won, Lost, Win %)

**Passing:**
- Pass Attempts, Completed, %
- Pass Types: Forehand, Backhand, Stretch, Bank, Rim, Drop, Lob, One-Touch
- Cross-Ice Passes
- Royal Road Passes
- Slot Passes
- Behind Net Passes
- Breakout Passes
- Shot Assists

**Shot Types:**
- One-Timer, Snap, Wrist, Slap, Tip, Deflection, Wrap-Around
- Shot Locations (by danger zone)
- Pre-Shot Events
- Shot Assists

**Situational:**
- 5v5, PP, PK, EN splits
- Period splits (P1, P2, P3, OT)
- Game State (Leading, Trailing, Tied)
- Competition Tier (vs Elite, vs Good, vs Average, vs Below Average)

**Advanced Metrics:**
- WAR (Wins Above Replacement)
- GAR (Goals Above Replacement)
- Game Score
- Adjusted Rating
- Ratings-Adjusted Stats (Goals, Points, xG)
- Quality of Competition (QoC)
- Quality of Teammates (QoT)

**Per-60 Rates:**
- Goals/60, Assists/60, Points/60
- Shots/60, xG/60
- Corsi/60, Fenwick/60
- Zone Entries/60, Zone Exits/60

### 1.2 Goalie Advanced Stats (Already Calculated)

#### From `fact_goalie_game_stats` (128 columns):

**Save Types:**
- Butterfly, Pad, Glove, Blocker, Chest, Stick, Scramble
- Glove Side, Blocker Side, Five Hole

**Danger Levels:**
- High/Medium/Low Danger Shots Against
- High/Medium/Low Danger Saves
- High/Medium/Low Danger Save %

**Rebound Control:**
- Saves with Freeze
- Saves with Rebound
- Freeze %, Rebound Rate
- Team/Opponent Recovered Rebounds
- Rebounds → Shots/Flurries
- Rebound Control Rate, Danger Rate
- Second Chance Shots/Goals/Save %

**Period Splits:**
- P1, P2, P3 saves, GA, SV%
- Best/Worst Period
- Period Consistency

**Time Buckets:**
- Early (0-5 min), Mid (5-15 min), Late (15-18 min), Final Minute (18-20 min)
- Clutch Performance (Final Minute SV%)

**Shot Context:**
- Rush Saves (<5s after entry)
- Quick Attack Saves (5-10s)
- Set Play Saves (>10s)
- Transition Defense Rating

**Pressure/Sequence:**
- Single Shot, Multi-Shot, Sustained Pressure Saves
- Sequence Survival Rate
- Pressure Handling Index

**Advanced Composites:**
- Goals Saved Above Average (GSAA)
- Goalie Game Score
- Clutch Rating
- Consistency Rating
- Rebound Rating
- Positioning Rating
- Overall Game Rating
- Win Probability Added

**Goalie WAR:**
- GAR components (GSAA, HD Bonus, Quality Start Bonus, Rebound Bonus)
- Total GAR, WAR, WAR Pace

### 1.3 Event-Level Data

#### From `fact_events` (140 columns):
- Raw event tracking with XY coordinates
- Event sequences
- Rush detection
- Cycle detection
- Pressure indicators
- Zone entry/exit details
- Pass outcomes
- Shot outcomes

#### From `fact_shifts`:
- Shift-level stats
- Line combinations
- On-ice team stats
- Zone time by shift

---

## Part 2: Inspiration Analysis

### 2.1 MoneyPuck (https://moneypuck.com)

**Key Features to Replicate:**
1. **xG Models & Shot Maps**
   - Interactive shot maps with xG values
   - Shot quality visualization
   - Goal probability by location
   - ✅ **We Have:** xG calculations, shot XY coordinates, danger zones

2. **Player Cards**
   - Comprehensive stat breakdowns
   - Percentile rankings
   - Visual stat comparisons
   - ✅ **We Have:** All necessary stats, can add percentile calculations

3. **Power Play Analysis**
   - PP efficiency by team
   - PP shot maps
   - PP zone time
   - ✅ **We Have:** PP stats, zone time, shot data

4. **Game Analytics**
   - xG timeline
   - Shot maps by period
   - Team comparison charts
   - ✅ **We Have:** Event data, shot data, period splits

### 2.2 Evolving Hockey (https://evolving-hockey.com)

**Key Features to Replicate:**
1. **GAR/WAR Leaders**
   - Comprehensive WAR/GAR breakdowns
   - Component analysis
   - ✅ **We Have:** WAR, GAR calculations

2. **RAPM (Regularized Adjusted Plus-Minus)**
   - ⚠️ **We Don't Have:** Requires stint-level data structure
   - **Future:** Could implement with shift data

3. **Player Comparison Tools**
   - Side-by-side stat comparisons
   - Percentile rankings
   - ✅ **We Have:** All stats, can add comparisons

4. **Glossary & Methodology**
   - Stat definitions
   - Calculation explanations
   - ✅ **We Can Add:** Tooltips and documentation

### 2.3 Hockey Graphs (https://hockey-graphs.com)

**Key Features to Replicate:**
1. **Interactive Visualizations**
   - Customizable charts
   - Filterable data
   - ✅ **We Can Build:** Using Recharts, interactive filters

2. **Advanced Metrics**
   - Possession metrics
   - Zone play analysis
   - ✅ **We Have:** All necessary data

### 2.4 NHL EDGE (https://www.nhl.com/nhl-edge)

**Key Features to Replicate:**
1. **Tracking Data Visualization**
   - Speed, distance, time on ice
   - Zone time heat maps
   - ✅ **We Have:** TOI, zone time, shift data

2. **Player Performance Cards**
   - Comprehensive stat displays
   - Visual comparisons
   - ✅ **We Can Build:** Enhanced player cards

3. **Team Analytics**
   - Team-level aggregations
   - Comparison tools
   - ✅ **We Have:** Team stats tables

### 2.5 JFresh / All Three Zones

**Key Features to Replicate:**
1. **Micro Stats Player Compass**
   - 4-quadrant visualization
   - Offensive vs Defensive micro stats
   - ✅ **We Have:** All micro stats needed

2. **Micro Stats Interpretation**
   - Contextual explanations
   - Success rates
   - ✅ **We Have:** Play success tracking

---

## Part 3: Implementation Plan

### Phase 1: Surface Existing Advanced Stats (Weeks 1-2)

**Priority: HIGH** - We have the data, just need to display it

#### 1.1 Enhanced Player Profile Pages

**Add New Sections:**

1. **Micro Stats Section**
   - Cards for: Deke Success Rate, Drive Success Rate, Zone Entry Success Rate
   - Breakdown by: Offensive Zone, Defensive Zone, Neutral Zone
   - Comparison to league average

2. **Rush & Transition Section**
   - Rush Goals, Assists, Points
   - Rush Shooting %
   - Rush Involvement %
   - Breakaway Goals
   - Time from Entry to Shot

3. **Zone Play Section**
   - Controlled Entry % (with breakdown by type)
   - Controlled Exit %
   - Zone Entry Denials
   - Zone Time Heat Map

4. **Passing Analysis Section**
   - Pass Completion % by Type
   - Shot Assists
   - Royal Road Passes
   - Cross-Ice Passes
   - Breakout Passes

5. **Shot Quality Section**
   - High/Medium/Low Danger Breakdown
   - Shot Types (One-Timer, Snap, Wrist, etc.)
   - xG vs Actual Goals
   - Goals Above Expected

6. **Situational Performance**
   - 5v5, PP, PK splits
   - Period Performance
   - Game State Performance (Leading/Trailing/Tied)
   - Competition Tier Performance

#### 1.2 Enhanced Game Pages

**Add New Sections:**

1. **xG Timeline**
   - Line chart showing cumulative xG by period
   - Goal markers
   - Team comparison

2. **Shot Map Enhancements**
   - Color by xG value
   - Filter by period, strength, player
   - Goal markers

3. **Rush Analysis**
   - Rush events timeline
   - Rush shot locations
   - Rush success rate

4. **Zone Entry/Exit Analysis**
   - Zone entry locations
   - Controlled vs Uncontrolled
   - Entry → Shot conversion

#### 1.3 Enhanced Team Pages

**Add New Sections:**

1. **Team Micro Stats**
   - Aggregate micro stats for team
   - League rankings
   - Season trends

2. **Zone Play Analysis**
   - Zone time distribution
   - Zone entry/exit efficiency
   - Controlled entry %

3. **Rush Performance**
   - Team rush stats
   - Rush goals per game
   - Rush conversion rate

### Phase 2: Advanced Analytics Pages (Weeks 3-4)

#### 2.1 Micro Stats Explorer Page

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ Micro Stats Explorer                                    │
├─────────────────────────────────────────────────────────┤
│ [Filters: Season, Position, Min GP]                     │
├─────────────────────────────────────────────────────────┤
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ Player Compass   │ │ Micro Stats      │             │
│ │ (4-Quadrant)     │ │ Leaderboard      │             │
│ └──────────────────┘ └──────────────────┘             │
│ ┌────────────────────────────────────────────┐         │
│ │ Detailed Micro Stats Table                 │         │
│ │ [Sortable, Filterable]                     │         │
│ └────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────┘
```

**Features:**
- Interactive player compass (Offensive vs Defensive micro stats)
- Leaderboards for each micro stat
- Success rate calculations
- League percentile rankings
- Drill-down to player profiles

**Micro Stats to Display:**
- Deke Success Rate
- Drive Success Rate (Middle, Wide, Corner)
- Zone Entry Success Rate (Controlled %)
- Zone Exit Success Rate
- Poke Check Success Rate
- Stick Check Success Rate
- Loose Puck Win %
- Board Battle Win %
- Screen Effectiveness
- One-Timer Success Rate

#### 2.2 Rush Analysis Page

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ Rush Analysis                                           │
├─────────────────────────────────────────────────────────┤
│ [Filters: Season, Team, Player]                         │
├─────────────────────────────────────────────────────────┤
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ Rush Leaders     │ │ Rush Shot Map    │             │
│ │ (Goals, Points)  │ │ (All Rushes)     │             │
│ └──────────────────┘ └──────────────────┘             │
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ Rush Timeline    │ │ Rush Success     │             │
│ │ (Game View)      │ │ Rates            │             │
│ └──────────────────┘ └──────────────────┘             │
└─────────────────────────────────────────────────────────┘
```

**Features:**
- Rush goal leaders
- Rush shot map (all rush shots)
- Rush timeline for games
- Rush conversion rates
- Time from entry to shot distribution
- Breakaway analysis

#### 2.3 Zone Entry/Exit Analysis Page

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ Zone Entry/Exit Analysis                                │
├─────────────────────────────────────────────────────────┤
│ [Filters: Season, Team, Player]                         │
├─────────────────────────────────────────────────────────┤
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ Entry Locations  │ │ Exit Locations   │             │
│ │ (Heat Map)       │ │ (Heat Map)       │             │
│ └──────────────────┘ └──────────────────┘             │
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ Controlled vs    │ │ Entry → Shot     │             │
│ │ Uncontrolled     │ │ Conversion        │             │
│ │ (Stacked Bar)    │ │ (Bar Chart)      │             │
│ └──────────────────┘ └──────────────────┘             │
│ ┌────────────────────────────────────────────┐         │
│ │ Entry/Exit Leaders Table                   │         │
│ └────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────┘
```

**Features:**
- Zone entry location heat map
- Zone exit location heat map
- Controlled vs Uncontrolled breakdown
- Entry type breakdown (Pass, Rush, Dump-In, etc.)
- Entry → Shot conversion rates
- Entry → Goal conversion rates
- League leaders in controlled entries

#### 2.4 xG Analysis Page

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ Expected Goals (xG) Analysis                             │
├─────────────────────────────────────────────────────────┤
│ [Filters: Season, Team, Player]                         │
├─────────────────────────────────────────────────────────┤
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ xG Leaders       │ │ Goals Above      │             │
│ │ (Table)          │ │ Expected         │             │
│ └──────────────────┘ └──────────────────┘             │
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ xG vs Goals      │ │ xG Shot Map      │             │
│ │ (Scatter Plot)   │ │ (Color by xG)    │             │
│ └──────────────────┘ └──────────────────┘             │
│ ┌────────────────────────────────────────────┐         │
│ │ xG Timeline (Game View)                     │         │
│ └────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────┘
```

**Features:**
- xG leaders (total, per game, per 60)
- Goals Above Expected (G-xG)
- xG vs Actual Goals scatter plot
- xG shot maps (color-coded by xG value)
- xG timeline for games
- xG by danger zone
- xG by shot type

#### 2.5 WAR/GAR Leaders Page

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ WAR/GAR Leaders                                         │
├─────────────────────────────────────────────────────────┤
│ [Filters: Season, Position, Min GP]                     │
├─────────────────────────────────────────────────────────┤
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ WAR Leaders      │ │ GAR Leaders      │             │
│ │ (Table)          │ │ (Table)          │             │
│ └──────────────────┘ └──────────────────┘             │
│ ┌──────────────────┐ ┌──────────────────┐             │
│ │ WAR Components   │ │ WAR Trends       │             │
│ │ (Breakdown)      │ │ (Line Chart)     │             │
│ └──────────────────┘ └──────────────────┘             │
└─────────────────────────────────────────────────────────┘
```

**Features:**
- WAR leaders table
- GAR leaders table
- WAR component breakdown (Offensive, Defensive, etc.)
- WAR trends over time
- WAR percentile rankings
- WAR by position

### Phase 3: Enhanced Visualizations (Weeks 5-6)

#### 3.1 Player Cards (JFresh Style)

**Features:**
- Comprehensive stat display
- Percentile rankings (visual bars)
- Micro stats compass (4-quadrant)
- WAR/GAR display
- xG vs Goals
- Zone play efficiency
- Rush performance

#### 3.2 Shot Maps Enhancements

**Features:**
- Color by xG value
- Filter by: Period, Strength, Player, Shot Type, Rush
- Goal markers
- Save markers
- Heat map overlay
- Danger zone boundaries

#### 3.3 Zone Time Heat Maps

**Features:**
- Offensive zone time heat map
- Defensive zone time heat map
- Neutral zone time heat map
- Team comparison
- Player-specific zone time

#### 3.4 Rush Visualization

**Features:**
- Rush event markers on rink
- Rush shot locations
- Entry point → Shot path
- Rush timeline
- Rush success indicators

### Phase 4: Interactive Tools (Weeks 7-8)

#### 4.1 Player Comparison Tool

**Enhancements:**
- Add micro stats comparison
- Add rush stats comparison
- Add zone play comparison
- Add percentile rankings side-by-side
- Radar chart with micro stats

#### 4.2 Custom Stat Explorer

**Features:**
- Select any stat from fact_player_game_stats
- Create custom leaderboards
- Filter by multiple criteria
- Export to CSV
- Save custom views

#### 4.3 Game Flow Visualization

**Features:**
- xG timeline
- Shot timeline
- Rush timeline
- Zone entry timeline
- Momentum shifts
- Key events markers

---

## Part 4: Data Requirements & Availability

### 4.1 Already Available ✅

**All of these are calculated and in the database:**
- ✅ All micro stats (dekes, drives, screens, etc.)
- ✅ Rush stats (rush_goals, rush_shots, rush_involvement)
- ✅ Zone entry/exit stats (controlled, uncontrolled, success rates)
- ✅ xG calculations
- ✅ WAR/GAR calculations
- ✅ Pass type breakdowns
- ✅ Shot type breakdowns
- ✅ Situational splits (5v5, PP, PK, periods, game state)
- ✅ Competition tier stats
- ✅ Per-60 rates
- ✅ Goalie advanced stats (128 columns)

### 4.2 Needs Calculation ⚠️

**These need to be calculated from existing data:**
- ⚠️ **Percentile Rankings** - Need to calculate league-wide percentiles
- ⚠️ **Success Rates** - Some micro stats need success rate calculations
- ⚠️ **League Averages** - For comparison purposes
- ⚠️ **Position-Specific Rankings** - Separate by Forward/Defense/Goalie

### 4.3 Future Enhancements 🔮

**These would require additional data or ML:**
- 🔮 **RAPM** - Requires stint-level data structure (could use shifts)
- 🔮 **Player Tracking** - Speed, distance (would need XY tracking over time)
- 🔮 **Expected Assists (xA)** - Would need pass quality model
- 🔮 **Defensive Impact Metrics** - More sophisticated than current

---

## Part 5: Implementation Priority

### Immediate (This Week)
1. ✅ **Fix boxscore alignment** - DONE
2. ✅ **Add team stats comparison to game pages** - DONE
3. ✅ **Enhance game/team page headers** - DONE
4. **Add micro stats section to player pages**
5. **Add rush stats section to player pages**
6. **Add zone play section to player pages**

### Week 1-2
1. **Enhanced Player Profile - Micro Stats Tab**
   - Deke success rate
   - Drive success rates
   - Zone entry/exit success rates
   - Board battle win %
   - Loose puck win %

2. **Enhanced Player Profile - Rush & Transition Tab**
   - Rush goals, assists, points
   - Rush shooting %
   - Rush involvement
   - Breakaway goals
   - Time from entry to shot

3. **Enhanced Game Pages - xG Timeline**
   - Cumulative xG chart
   - Goal markers
   - Team comparison

### Week 3-4
1. **Micro Stats Explorer Page**
   - Player compass visualization
   - Micro stats leaderboards
   - Success rate calculations
   - League percentiles

2. **Rush Analysis Page**
   - Rush leaders
   - Rush shot maps
   - Rush timelines
   - Conversion rates

3. **Zone Entry/Exit Analysis Page**
   - Entry/exit heat maps
   - Controlled vs uncontrolled
   - Entry → shot conversion

### Week 5-6
1. **xG Analysis Page**
   - xG leaders
   - Goals above expected
   - xG shot maps
   - xG timelines

2. **WAR/GAR Leaders Page**
   - WAR leaders table
   - GAR component breakdown
   - WAR trends

3. **Enhanced Shot Maps**
   - Color by xG
   - Advanced filters
   - Goal/save markers

### Week 7-8
1. **Player Cards (JFresh Style)**
   - Comprehensive stat display
   - Percentile rankings
   - Micro stats compass

2. **Enhanced Player Comparison**
   - Micro stats comparison
   - Rush stats comparison
   - Zone play comparison

3. **Custom Stat Explorer**
   - Select any stat
   - Create custom leaderboards
   - Export functionality

---

## Part 6: Technical Implementation Details

### 6.1 Database Queries

**Percentile Calculations:**
```sql
-- Calculate percentile for a stat
WITH ranked AS (
  SELECT 
    player_id,
    stat_value,
    PERCENT_RANK() OVER (ORDER BY stat_value) * 100 as percentile
  FROM fact_player_season_stats
  WHERE season_id = ? AND games_played >= 10
)
SELECT * FROM ranked WHERE player_id = ?
```

**Success Rate Calculations:**
```sql
-- Micro stat success rate
SELECT 
  player_id,
  dekes,
  dekes_successful,
  CASE 
    WHEN dekes > 0 THEN (dekes_successful::FLOAT / dekes) * 100 
    ELSE 0 
  END as deke_success_rate
FROM fact_player_game_stats
```

**League Averages:**
```sql
-- League average for a stat
SELECT 
  AVG(stat_value) as league_avg,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY stat_value) as median
FROM fact_player_season_stats
WHERE season_id = ? AND games_played >= 10
```

### 6.2 Component Structure

**New Components to Build:**

1. **MicroStatsCompass.tsx**
   - 4-quadrant radar chart
   - Offensive vs Defensive micro stats
   - Interactive tooltips

2. **RushTimeline.tsx**
   - Timeline visualization
   - Rush event markers
   - Shot/goal markers

3. **ZoneEntryHeatMap.tsx**
   - Heat map of zone entry locations
   - Controlled vs uncontrolled overlay
   - Entry type breakdown

4. **xGTimeline.tsx**
   - Cumulative xG line chart
   - Goal markers
   - Team comparison

5. **PlayerCard.tsx**
   - Comprehensive stat display
   - Percentile bars
   - Micro stats compass
   - WAR/GAR display

6. **StatExplorer.tsx**
   - Dynamic stat selection
   - Custom leaderboards
   - Filtering interface

### 6.3 API Endpoints Needed

**New API Routes:**

1. `/api/stats/percentiles`
   - Calculate percentiles for any stat
   - Filter by position, min GP

2. `/api/stats/league-averages`
   - Get league averages for stats
   - Filter by season, position

3. `/api/stats/micro-stats`
   - Get micro stats with success rates
   - Filter by player, team, season

4. `/api/stats/rush-analysis`
   - Get rush stats aggregated
   - Filter by game, team, player

5. `/api/stats/zone-analysis`
   - Get zone entry/exit data
   - Filter by game, team, player

---

## Part 7: Inspiration Screenshot Analysis

### Key Visual Patterns from Screenshots:

1. **Player Cards:**
   - Large stat displays
   - Percentile bars
   - Color coding (green = good, red = bad)
   - Micro stats compass

2. **Shot Maps:**
   - Color by xG or outcome
   - Goal markers (larger)
   - Save markers
   - Heat map overlay

3. **Timeline Charts:**
   - Cumulative xG
   - Event markers
   - Team comparison lines

4. **Heat Maps:**
   - Zone time
   - Zone entries/exits
   - Shot locations

5. **Comparison Tables:**
   - Side-by-side stats
   - Percentile columns
   - Color-coded cells

---

## Part 8: Success Metrics

### Phase 1 Success Criteria:
- [ ] All existing advanced stats displayed on player pages
- [ ] Micro stats section functional
- [ ] Rush stats section functional
- [ ] Zone play section functional
- [ ] xG timeline on game pages

### Phase 2 Success Criteria:
- [ ] Micro Stats Explorer page live
- [ ] Rush Analysis page live
- [ ] Zone Entry/Exit Analysis page live
- [ ] xG Analysis page live
- [ ] WAR/GAR Leaders page live

### Phase 3 Success Criteria:
- [ ] Enhanced shot maps with xG coloring
- [ ] Zone time heat maps
- [ ] Player cards (JFresh style)
- [ ] Rush visualizations

### Phase 4 Success Criteria:
- [ ] Custom stat explorer functional
- [ ] Enhanced player comparison
- [ ] Game flow visualizations
- [ ] Export functionality

---

## Part 9: Next Steps

### This Week:
1. ✅ Complete boxscore alignment fix
2. **Start:** Add micro stats section to player pages
3. **Start:** Add rush stats section to player pages
4. **Plan:** Micro Stats Explorer page structure

### Next Week:
1. **Build:** Micro Stats Explorer page
2. **Build:** Rush Analysis page
3. **Enhance:** Shot maps with xG coloring
4. **Add:** xG timeline to game pages

### Following Weeks:
1. Zone Entry/Exit Analysis page
2. xG Analysis page
3. WAR/GAR Leaders page
4. Player cards (JFresh style)
5. Enhanced visualizations

---

## Appendix: Stat Definitions Reference

### Micro Stats Definitions:

**Deke:** Attempt to beat a defender with a move
**Drive:** Carrying puck toward net (Middle/Wide/Corner)
**Cutback:** Change of direction while driving
**Delay:** Holding puck to create space
**Crash Net:** Driving to net for rebound
**Screen:** Positioning in front of goalie
**Give-and-Go:** Pass and receive return pass
**Second Touch:** Quick second touch on puck
**Cycle:** Sustained offensive zone possession (3+ passes)

**Poke Check:** Using stick to disrupt puck
**Stick Check:** Using stick to disrupt player
**Backcheck:** Defensive effort on backcheck
**Forecheck:** Offensive pressure in opponent's zone
**Zone Entry Denial:** Preventing opponent zone entry

**Controlled Entry:** Maintaining possession on zone entry (Pass, Rush, RushBreakaway)
**Uncontrolled Entry:** Losing possession on entry (Dump-In, Chip, etc.)
**Controlled Exit:** Maintaining possession on zone exit (Pass, Rush)
**Uncontrolled Exit:** Losing possession on exit (Clear, Chip, etc.)

### Advanced Metrics Definitions:

**xG (Expected Goals):** Probability of shot becoming goal based on location, type, context
**G-xG (Goals Above Expected):** Actual goals minus expected goals
**WAR (Wins Above Replacement):** Player's contribution to team wins vs replacement player
**GAR (Goals Above Replacement):** Player's contribution to team goals vs replacement player
**CF% (Corsi For %):** Percentage of shot attempts (for vs against)
**FF% (Fenwick For %):** Percentage of unblocked shot attempts (for vs against)

---

*This document will be updated as implementation progresses.*
