# Dashboard Pages - GitHub Issues

**Complete list of GitHub issues for existing dashboard pages and proposed new pages**

Last Updated: 2026-01-22

---

## Existing Dashboard Pages - Issues

### Core Pages (Already Implemented)

#### DASH-001: Standings Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/standings`
- **Description:** Enhance standings page with additional features
- **Current State:** Basic standings table exists
- **Enhancements Needed:**
  - [ ] Add team logos to standings
  - [ ] Add win/loss streak indicators
  - [ ] Add goal differential visualization
  - [ ] Add conference/division grouping
  - [ ] Add historical standings comparison
  - [ ] Add playoff race visualization
  - [ ] Add export functionality

#### DASH-002: Players Directory Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/players`
- **Description:** Enhance player directory with better filtering and display
- **Current State:** Basic player list exists
- **Enhancements Needed:**
  - [ ] Add advanced filters (position, team, min GP, age range)
  - [ ] Add player photos to table
  - [ ] Add quick stat cards (leaders)
  - [ ] Add export functionality
  - [ ] Add sorting by advanced metrics
  - [ ] Add player search with autocomplete

#### DASH-003: Player Profile Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p1`, `phase:3`
- **Path:** `/norad/players/[playerId]`
- **Current State:** Has Overview, Season, Career, Advanced tabs
- **Enhancements Needed:**
  - [ ] Add Z-score visualization (from wireframes)
  - [ ] Add player photo to header
  - [ ] Add collapsible accordion sections for advanced stats
  - [ ] Add shot density heatmap (from wireframes)
  - [ ] Add player position heatmap (if tracking data available)
  - [ ] Add career trajectory visualization
  - [ ] Add similar players suggestion
  - [ ] Add export functionality

#### DASH-004: Player Trends Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/players/[playerId]/trends`
- **Current State:** Basic trends exist
- **Enhancements Needed:**
  - [ ] Add more trend metrics (CF%, xG%, WAR trend)
  - [ ] Add streak analysis (hot/cold streaks)
  - [ ] Add performance vs rating comparison
  - [ ] Add rolling average customization (5-game, 10-game, 20-game)
  - [ ] Add export functionality

#### DASH-005: Player Game Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/players/[playerId]/games/[gameId]`
- **Current State:** Basic game stats exist
- **Enhancements Needed:**
  - [ ] Add shift timeline visualization
  - [ ] Add event timeline for player
  - [ ] Add video integration (if available)
  - [ ] Add shot map for this game
  - [ ] Add comparison to season averages
  - [ ] Add export functionality

#### DASH-006: Player Comparison Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/players/compare`
- **Current State:** Basic comparison exists
- **Enhancements Needed:**
  - [ ] Add radar chart for multi-player comparison (from wireframes)
  - [ ] Add trend comparison charts
  - [ ] Add micro stats comparison
  - [ ] Add head-to-head matchup stats
  - [ ] Add export functionality

#### DASH-007: Goalies Directory Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/goalies`
- **Current State:** Has GAA, Wins, Save % tabs
- **Enhancements Needed:**
  - [ ] Add goalie photos to table
  - [ ] Add advanced filters
  - [ ] Add quick stat cards
  - [ ] Add export functionality
  - [ ] Add GSAx (Goals Saved Above Expected) leaders

#### DASH-008: Goalie Profile Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p1`, `phase:3`
- **Path:** `/norad/goalies/[goalieId]`
- **Current State:** Has Overview, Season, Career, Advanced, Saves tabs
- **Enhancements Needed:**
  - [ ] Add save location heatmap (from wireframes)
  - [ ] Add save type distribution chart
  - [ ] Add danger zone save breakdown
  - [ ] Add rebound control metrics visualization
  - [ ] Add goalie photo to header
  - [ ] Add export functionality

#### DASH-009: Goalie Comparison Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/goalies/compare`
- **Current State:** Basic comparison exists
- **Enhancements Needed:**
  - [ ] Add radar chart comparison
  - [ ] Add save type distribution comparison
  - [ ] Add GSAx comparison
  - [ ] Add export functionality

#### DASH-010: Teams Directory Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/teams`
- **Current State:** Basic team list exists
- **Enhancements Needed:**
  - [ ] Add team logos to table
  - [ ] Add quick stat cards
  - [ ] Add filters
  - [ ] Add export functionality

#### DASH-011: Team Profile Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p1`, `phase:3`
- **Path:** `/norad/team/[teamName]` or `/norad/teams/[teamId]`
- **Current State:** Has Overview, Roster, Lines, Analytics, Matchups tabs
- **Enhancements Needed:**
  - [ ] Add passing grid matrix (from wireframes)
  - [ ] Add presence & importance charts (from wireframes)
  - [ ] Add team shot charts
  - [ ] Add zone time heatmaps
  - [ ] Add export functionality

#### DASH-012: Team Comparison Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/teams/compare`
- **Current State:** Basic comparison exists
- **Enhancements Needed:**
  - [ ] Add radar chart comparison
  - [ ] Add head-to-head record visualization
  - [ ] Add export functionality

#### DASH-013: Games List Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/games`
- **Current State:** Basic game list exists
- **Enhancements Needed:**
  - [ ] Add game preview cards with key stats
  - [ ] Add win probability predictions (if ML available)
  - [ ] Add filters (season, team, game type, date range)
  - [ ] Add export functionality

#### DASH-014: Game Detail Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p1`, `phase:3`
- **Path:** `/norad/games/[gameId]`
- **Current State:** Has box score, shot maps, play-by-play, shift charts
- **Enhancements Needed:**
  - [ ] Add win probability chart (from wireframes)
  - [ ] Add cumulative Corsi/xG flow charts (from wireframes)
  - [ ] Add quadrant scatter plots (CF% vs xGF%) (from wireframes)
  - [ ] Add video integration (from wireframes)
  - [ ] Add shift timeline with video (from wireframes)
  - [ ] Add game flow visualization
  - [ ] Add momentum chart
  - [ ] Add export functionality

#### DASH-015: Shot Maps Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/games/shots`
- **Current State:** Basic shot maps exist
- **Enhancements Needed:**
  - [ ] Add shot density heatmap (from wireframes)
  - [ ] Add period-by-period shot maps
  - [ ] Add player-specific shot maps
  - [ ] Add strength situation filters
  - [ ] Add export functionality

#### DASH-016: Schedule Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/schedule`
- **Current State:** Basic schedule exists
- **Enhancements Needed:**
  - [ ] Add calendar view
  - [ ] Add win probability predictions
  - [ ] Add matchup analysis
  - [ ] Add filters
  - [ ] Add export functionality

#### DASH-017: Leaders Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/leaders`
- **Current State:** Has Points, Goals, Assists, Goalies tabs
- **Enhancements Needed:**
  - [ ] Add more leader categories (WAR, xG, CF%, etc.)
  - [ ] Add player photos
  - [ ] Add filters
  - [ ] Add export functionality

#### DASH-018: Analytics Overview Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/analytics/overview`
- **Current State:** Basic overview exists
- **Enhancements Needed:**
  - [ ] Add league summary cards
  - [ ] Add recent games widget
  - [ ] Add analytics tools grid (from wireframes)
  - [ ] Add quick links to all analytics pages

#### DASH-019: Analytics Statistics Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/analytics/statistics`
- **Current State:** Basic statistics exist
- **Enhancements Needed:**
  - [ ] Add comprehensive stats tables with filters (from wireframes)
  - [ ] Add column selection
  - [ ] Add export functionality
  - [ ] Add advanced filtering (position, age, draft year, etc.)

#### DASH-020: Analytics Trends Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/analytics/trends`
- **Current State:** Shows "Coming Soon" placeholder
- **Enhancements Needed:**
  - [ ] Implement team statistics trends
  - [ ] Add goals per game trends
  - [ ] Add player scoring trends
  - [ ] Add multi-season comparison
  - [ ] Add export functionality

#### DASH-021: Analytics Teams Comparison Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/analytics/teams`
- **Current State:** Basic team comparison exists
- **Enhancements Needed:**
  - [ ] Add quadrant scatter plots
  - [ ] Add radar chart comparison
  - [ ] Add export functionality

#### DASH-022: Analytics Shifts Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/analytics/shifts`
- **Current State:** Basic shift viewer exists
- **Enhancements Needed:**
  - [ ] Add shift timeline visualization (from wireframes)
  - [ ] Add line combination grouping
  - [ ] Add shift quality metrics
  - [ ] Add export functionality

#### DASH-023: Analytics xG Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p1`, `phase:3`
- **Path:** `/norad/analytics/xg`
- **Current State:** Basic xG analysis exists
- **Enhancements Needed:**
  - [ ] Add xG timeline (game flow) (from wireframes)
  - [ ] Add shot quality analysis
  - [ ] Add flurry-adjusted xG visualization
  - [ ] Add export functionality

#### DASH-024: Analytics WAR Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p1`, `phase:3`
- **Path:** `/norad/analytics/war`
- **Current State:** Basic WAR leaders exist
- **Enhancements Needed:**
  - [ ] Add GAR component breakdown (from wireframes)
  - [ ] Add WAR trends over time
  - [ ] Add WAR by position visualization
  - [ ] Add export functionality

#### DASH-025: Analytics Micro Stats Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/analytics/micro-stats`
- **Current State:** Basic micro stats exist
- **Enhancements Needed:**
  - [ ] Add interactive micro stats breakdown
  - [ ] Add success rate visualizations
  - [ ] Add detailed micro stat breakdowns
  - [ ] Add export functionality

#### DASH-026: Analytics Zone Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/analytics/zone`
- **Current State:** Basic zone analytics exist
- **Enhancements Needed:**
  - [ ] Add zone time heatmaps (from wireframes)
  - [ ] Add zone entry/exit success rate visualizations
  - [ ] Add zone entry/exit flow diagrams
  - [ ] Add export functionality

#### DASH-027: Analytics Rushes Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/analytics/rushes`
- **Current State:** Basic rush analysis exists
- **Enhancements Needed:**
  - [ ] Add rush success rate visualizations
  - [ ] Add breakaway analysis
  - [ ] Add odd-man rush analysis
  - [ ] Add rush xG analysis
  - [ ] Add export functionality

#### DASH-028: Analytics Faceoffs Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/analytics/faceoffs`
- **Current State:** Basic faceoff stats exist
- **Enhancements Needed:**
  - [ ] Add WDBE (Win/Draw/Back/Exit) faceoff analysis
  - [ ] Add faceoff win % by zone visualization
  - [ ] Add faceoff outcomes breakdown
  - [ ] Add export functionality

#### DASH-029: Analytics Lines Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/analytics/lines`
- **Current State:** Basic line combinations exist
- **Enhancements Needed:**
  - [ ] Add WOWY (With Or Without You) analysis visualization
  - [ ] Add optimal line suggestions
  - [ ] Add line chemistry scoring
  - [ ] Add export functionality

#### DASH-030: Analytics Shot Chains Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/analytics/shot-chains`
- **Current State:** Basic shot chains exist
- **Enhancements Needed:**
  - [ ] Add shot sequence visualization
  - [ ] Add pattern recognition
  - [ ] Add flurry detection visualization
  - [ ] Add export functionality

#### DASH-031: Tracker Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/tracker`
- **Current State:** Basic tracker exists
- **Enhancements Needed:**
  - [ ] Add game selection interface
  - [ ] Add tracking status indicators
  - [ ] Add export functionality

#### DASH-032: Tracker Videos Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/tracker/videos`
- **Current State:** Basic video management exists
- **Enhancements Needed:**
  - [ ] Add video preview thumbnails
  - [ ] Add video player integration
  - [ ] Add video-event synchronization
  - [ ] Add export functionality

#### DASH-033: Player Matchups Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/players/matchups`
- **Current State:** Basic matchups exist
- **Enhancements Needed:**
  - [ ] Add head-to-head visualization
  - [ ] Add common games analysis
  - [ ] Add export functionality

#### DASH-034: Teams Free Agents Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p3`, `phase:3`
- **Path:** `/norad/teams/free-agents`
- **Current State:** Basic free agents list exists
- **Enhancements Needed:**
  - [ ] Add player valuation
  - [ ] Add contract value predictions
  - [ ] Add export functionality

---

## New Dashboard Pages from Wireframes

### Game Pages

#### DASH-035: Game Win Probability Chart
- **Labels:** `type:feature`, `area:dashboard`, `priority:p1`, `phase:3`
- **Path:** `/norad/games/[gameId]` (new tab)
- **Description:** Add win probability chart showing game flow (from wireframes)
- **Features:**
  - [ ] Win probability line chart over game time
  - [ ] Goal markers on timeline
  - [ ] Power play indicators
  - [ ] Period breaks
  - [ ] Interactive tooltips
- **Data Source:** `fact_events`, calculated win probability

#### DASH-036: Game Cumulative Charts (Corsi/xG Flow)
- **Labels:** `type:feature`, `area:dashboard`, `priority:p1`, `phase:3`
- **Path:** `/norad/games/[gameId]` (new tab)
- **Description:** Add cumulative Corsi and xG flow charts (from wireframes)
- **Features:**
  - [ ] Cumulative shot attempts chart
  - [ ] Cumulative xG chart
  - [ ] Period breaks
  - [ ] Goal markers
  - [ ] Power play indicators
  - [ ] Score adjustment toggle
- **Data Source:** `fact_events`, `fact_shot_xy`

#### DASH-037: Game Skater Quadrant Charts
- **Labels:** `type:feature`, `area:dashboard`, `priority:p1`, `phase:3`
- **Path:** `/norad/games/[gameId]` (new tab)
- **Description:** Add quadrant scatter plots for skaters (CF% vs xGF%) (from wireframes)
- **Features:**
  - [ ] Quadrant scatter plot (CF/CA per 60)
  - [ ] Quadrant scatter plot (xGF/xGA per 60)
  - [ ] TOI indicated by dot size
  - [ ] Team coloring
  - [ ] Interactive tooltips
- **Data Source:** `fact_player_game_stats`

#### DASH-038: Game Player Tables (Enhanced Box Score)
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/games/[gameId]` (enhance existing)
- **Description:** Enhance box score with advanced metrics (from wireframes)
- **Features:**
  - [ ] Add ISF, iFF, ICF, ixG columns
  - [ ] Add Sh%, FSh% columns
  - [ ] Add iSCF, iHDCF columns
  - [ ] Add iBLK, iHA columns
  - [ ] Add GIVE, TAKE columns
  - [ ] Add PENT, PEND columns
  - [ ] Add FO% column
- **Data Source:** `fact_player_game_stats`

### Player Pages

#### DASH-039: Player Shot Chart with Density Heatmap
- **Labels:** `type:feature`, `area:dashboard`, `priority:p1`, `phase:3`
- **Path:** `/norad/players/[playerId]` (new tab or enhance existing)
- **Description:** Add shot density heatmap overlay (from wireframes)
- **Features:**
  - [ ] Shot location map with markers
  - [ ] Density heatmap overlay toggle
  - [ ] Zone breakdown (High/Medium/Low danger)
  - [ ] Shot stats sidebar
  - [ ] Filters (season, strength, shot type)
- **Data Source:** `fact_shot_xy`

#### DASH-040: Player Z-Score Card
- **Labels:** `type:feature`, `area:dashboard`, `priority:p1`, `phase:3`
- **Path:** `/norad/players/[playerId]` (new section in Advanced tab)
- **Description:** Add Z-score visualization vs league average (from wireframes)
- **Features:**
  - [ ] Horizontal bar charts for each metric
  - [ ] Z-score values
  - [ ] League average indicator
  - [ ] Categories: General Offense, Passing, Offensive Types, Zone Entries, Zone Exits, Forechecking
- **Data Source:** `fact_player_season_stats`, league averages

#### DASH-041: Player Position Heatmap
- **Labels:** `type:feature`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/players/[playerId]` (new tab)
- **Description:** Add player position heatmap showing time in each zone (from wireframes)
- **Features:**
  - [ ] Zone-based heatmap (O-zone, N-zone, D-zone)
  - [ ] Time in zone percentages
  - [ ] Filters (season, strength, game type)
- **Data Source:** `fact_tracking` (if available), `fact_shifts`

#### DASH-042: Player Career Dashboard View
- **Labels:** `type:feature`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/players/[playerId]` (enhance Career tab)
- **Description:** Add comprehensive career dashboard (from wireframes)
- **Features:**
  - [ ] Season-by-season breakdown table
  - [ ] Career totals
  - [ ] Era-adjusted stats
  - [ ] Career trajectory chart
  - [ ] Milestone tracking
- **Data Source:** `fact_player_season_stats`, `fact_player_career_stats`

### Team Pages

#### DASH-043: Team Passing Grid Matrix
- **Labels:** `type:feature`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/teams/[teamId]` (new section in Analytics tab)
- **Description:** Add passing connection matrix (from wireframes)
- **Features:**
  - [ ] Player-to-player passing grid
  - [ ] Color-coded by pass count
  - [ ] Interactive tooltips
  - [ ] Filters (game, season, strength)
- **Data Source:** `fact_events` (Pass events)

#### DASH-044: Team Presence & Importance Charts
- **Labels:** `type:feature`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/teams/[teamId]` (new section in Analytics tab)
- **Description:** Add presence and importance visualization by position group (from wireframes)
- **Features:**
  - [ ] Bar charts by position group (Forwards, Defense, Goalies)
  - [ ] Power play presence
  - [ ] Penalty kill presence
  - [ ] Bar height = ice time (presence)
  - [ ] Bar color intensity = impact (importance)
- **Data Source:** `fact_shifts`, `fact_player_game_stats`

#### DASH-045: Team Line Combinations Analysis
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/teams/[teamId]` (enhance Lines tab)
- **Description:** Enhance line combinations with WOWY analysis (from wireframes)
- **Features:**
  - [ ] Line performance cards
  - [ ] WOWY (With Or Without You) analysis
  - [ ] Optimal line suggestions
  - [ ] Line chemistry scoring
  - [ ] Visual line combination display
- **Data Source:** `fact_line_combos`, `fact_wowy`

### Analytics Pages

#### DASH-046: Advanced Stats Leaderboard Table
- **Labels:** `type:feature`, `area:dashboard`, `priority:p1`, `phase:3`
- **Path:** `/norad/analytics/statistics` (enhance existing)
- **Description:** Add comprehensive stats table with advanced filtering (from wireframes)
- **Features:**
  - [ ] Multi-level filters (team, position, season, age, draft year, min TOI)
  - [ ] Column selection
  - [ ] Sortable columns
  - [ ] Search functionality
  - [ ] Pagination
  - [ ] Export functionality
- **Data Source:** `fact_player_season_stats`, `fact_goalie_season_stats`

#### DASH-047: Microstat Game Score Dashboard
- **Labels:** `type:feature`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/analytics/micro-stats` (new view)
- **Description:** Add microstat game score visualization by game (from wireframes)
- **Features:**
  - [ ] Time series chart of microstat game score
  - [ ] Team coloring
  - [ ] Game-by-game breakdown
  - [ ] Player highlighting
  - [ ] Filters (team, player, season)
- **Data Source:** `fact_player_micro_stats`

#### DASH-048: Zone Entry/Exit Flow Diagrams
- **Labels:** `type:feature`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/analytics/zone` (new section)
- **Description:** Add zone entry/exit flow visualization (from wireframes)
- **Features:**
  - [ ] Flow diagrams showing entry/exit patterns
  - [ ] Success rate visualization
  - [ ] Entry/exit type breakdown
  - [ ] Team comparison
- **Data Source:** `fact_zone_entries`, `fact_zone_exits`

#### DASH-049: Shot Danger Breakdown Dashboard
- **Labels:** `type:feature`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/analytics/xg` (new section)
- **Description:** Add shot danger breakdown visualization (from wireframes)
- **Features:**
  - [ ] High/Medium/Low danger breakdown
  - [ ] xG by danger zone
  - [ ] Team comparison
  - [ ] Player comparison
- **Data Source:** `fact_shot_xy`, `fact_events`

#### DASH-050: Momentum Chart
- **Labels:** `type:feature`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/games/[gameId]` (new section)
- **Description:** Add momentum chart showing game flow (from wireframes)
- **Features:**
  - [ ] Rolling 5-minute Corsi chart
  - [ ] Momentum score visualization
  - [ ] Goal markers
  - [ ] Period breaks
- **Data Source:** `fact_events`, calculated momentum

---

## Summary

**Total Issues:** 50
- **Existing Pages (Enhancements):** 34 issues
- **New Pages from Wireframes:** 16 issues

**Priority Breakdown:**
- **P1 (High):** 8 issues
- **P2 (Medium):** 38 issues
- **P3 (Low):** 4 issues

**Phase:** All assigned to Phase 3 (Dashboard Enhancement)

---

*This document will be integrated into the main GitHub Issues Backlog.*
