# BenchSight Dashboard Guide

**Complete Navigation Guide - Where to Find Everything**

Last Updated: 2026-01-15  
**Version:** 2.0 - Feature Complete

---

## 📋 Table of Contents

1. [Quick Navigation](#quick-navigation)
2. [Player Pages](#player-pages)
3. [Goalie Pages](#goalie-pages)
4. [Team Pages](#team-pages)
5. [Game Pages](#game-pages)
6. [Analytics Pages](#analytics-pages)
7. [Leaderboards](#leaderboards)
8. [Comparison Tools](#comparison-tools)
9. [Key Features](#key-features)

---

## 🚀 Quick Navigation

### Main Sections
- **Players**: `/players` - Player directory and rankings
- **Goalies**: `/goalies` - Goalie leaders and statistics
- **Teams**: `/teams` - Team directory and standings
- **Games**: `/games` - Game schedule and results
- **Analytics**: `/analytics/overview` - Advanced analytics hub
- **Standings**: `/standings` - League standings table
- **Schedule**: `/schedule` - Upcoming and past games

---

## 👤 Player Pages

### Player Directory
**Path**: `/players`

**Features**:
- Current season player rankings
- Quick stats cards (Points Leader, Goals Leader, Assists Leader)
- Sortable player table
- Links to individual player profiles

**What You'll Find**:
- Points, Goals, Assists leaders
- Quick links to top performers
- Search and filter capabilities

---

### Individual Player Profile
**Path**: `/players/[playerId]`

**Features**:
- **Header Section**: Player photo, name, team, position, jersey number
- **Quick Stats Cards**: GP, G, A, P, +/-, TOI
- **Tab Navigation**: Overview | Season | Career | Advanced
- **Action Links**: "View Trends" and "Compare with another player"

#### Overview Tab
- Performance trend charts
- Game log table
- Stat breakdown (radar chart)
- Recent games timeline
- Shot map

#### Season Tab
- Season summary statistics
- Goals/Game trend chart
- Advanced metrics cards
- Game-by-game stats table
- Period and strength splits

#### Career Tab
- Career totals
- Career trends (multi-line chart)
- Season-by-season comparison table
- Career trajectory visualization

#### Advanced Tab
- xG Analysis (bar + line charts)
- WAR/GAR metrics
- Zone analytics (heat maps)
- Micro stats breakdown
- Competition tier analysis
- Quality metrics

**Key Stats Available**:
- All 317 columns from `fact_player_game_stats`
- Advanced metrics (Corsi, Fenwick, xG, WAR, GAR)
- Zone entry/exit statistics
- Rush statistics
- Micro stats (dekes, drives, puck battles, etc.)
- Competition tier splits

---

### Player Trends Page
**Path**: `/players/[playerId]/trends`

**Features**:
- **Time-Series Charts**:
  - Goals Per Game Trend (with 5-game and 10-game rolling averages)
  - Points Per Game Trend
  - xG Trend (if available)
  - WAR Trend (if available)
  - Advanced Metrics Trend (CF%, +/-, Game Score)
- **Summary Stats**: Games Played, Avg Goals/Game, Avg Points/Game, Current Streak
- **Streak Analysis**: Point streaks, goal streaks, scoreless streaks
- **Recent Games Table**: Last 10 games with detailed stats and links

**Access**: Click "View Trends" button on player profile page

---

### Player Game Page
**Path**: `/players/[playerId]/games/[gameId]`

**Features**:
- **Game Context**: Team vs Opponent, date, tracked game indicator
- **Core Stats**: Goals, Assists, Points, +/-, Shots, TOI, Shifts
- **Possession Metrics**: Corsi, Fenwick, xG (if tracking available)
- **Zone Transitions**: Zone entries/exits, success rates
- **Passing Stats**: Pass attempts, completions, percentage
- **Micro Statistics**: Dekes, drives, forechecks, backchecks, puck battles, etc.
- **Physical Play**: Hits, blocks, faceoffs
- **Player Events Timeline**: All events involving this player in the game
- **Shot Map**: All shots taken by the player
- **Shifts**: Complete shift breakdown with times and duration

**Access**: Click on any game in the game log table on player profile

---

### Player Comparison
**Path**: `/players/compare?p1=[playerId]&p2=[playerId]&p3=[playerId]&p4=[playerId]`

**Features**:
- Side-by-side comparison of 2-4 players
- Stat comparison table (sortable)
- Radar chart for multi-dimensional comparison
- Advanced metrics comparison
- Trend comparisons
- Micro stats comparison

**Access**: Click "Compare with another player" on player profile, or visit `/players/compare` and add players

---

## 🥅 Goalie Pages

### Goalie Leaders
**Path**: `/goalies`

**Features**:
- **Tabs**: GAA | Wins | Save % | All Stats
- **GAA Leaders**: Goals Against Average rankings
- **Wins Leaders**: Win totals and win percentage
- **Save % Leaders**: Save percentage rankings
- **All Stats**: Comprehensive goalie statistics table

**Access**: Main navigation → Goalies

---

### Individual Goalie Profile
**Path**: `/goalies/[goalieId]`

**Features**:
- **Header**: Goalie photo, name, team
- **Quick Stats**: GP, W, L, SV%, GAA, SO
- **Save % Trend**: Line chart with 5-game and 10-game rolling averages
- **GAA Trend**: Goals Against Average trend chart
- **Advanced Statistics**:
  - GSAx (Goals Saved Above Expected)
  - WAR (Wins Above Replacement)
  - GAR (Goals Above Replacement)
  - HD Save %
  - Quality Starts and QS Rate
  - Total Saves and Shots Against
- **Career Summary**: Career totals and averages
- **Recent Games Table**: Last 20 games with results and stats

**Access**: Click on any goalie name in goalie leaderboards

---

### Goalie Comparison
**Path**: `/goalies/compare?g1=[goalieId]&g2=[goalieId]&g3=[goalieId]&g4=[goalieId]`

**Features**:
- Side-by-side comparison of 2-4 goalies
- Stat comparison table
- Performance comparison radar chart
- Save % comparison
- GAA comparison
- Advanced metrics comparison

**Access**: Click "Compare Goalies" on goalie profile page

---

## 🏒 Team Pages

### Team Directory
**Path**: `/teams`

**Features**:
- Team list with logos
- Quick stats (Wins, Losses, Points)
- Links to team profiles

---

### Team Profile
**Path**: `/team/[teamName]` or `/teams/[teamId]`

**Features**:
- **Header**: Team logo, name, season record
- **Quick Stats**: W, L, PTS, GF, GA, Diff
- **Tabs**: Overview | Roster | Lines | Analytics | Matchups
- **Roster Section**: Player list with stats
- **Goaltending Section**: Goalie statistics
- **Recent Games**: Game results timeline
- **Team Statistics**: Comprehensive team stats

---

### Team Comparison
**Path**: `/teams/compare?t1=[teamId]&t2=[teamId]&t3=[teamId]&t4=[teamId]`

**Features**:
- Side-by-side comparison of 2-4 teams
- Stat comparison table
- Win/Loss records
- Goals For/Against
- Goal differential
- Win percentage

**Access**: Visit `/teams/compare` and add team IDs to URL parameters

---

## 🎮 Game Pages

### Game Schedule
**Path**: `/games`

**Features**:
- List of all games
- Game results
- Links to individual game pages

---

### Game Detail Page
**Path**: `/games/[gameId]`

**Features**:
- **Game Header**: Teams, date, score, tracked game indicator
- **Goal Summary**: Goals grouped by period with:
  - Team logos
  - Player photos for scorers and assists
  - Running score (e.g., "1-0", "2-0")
  - Period breakdown
- **Play-by-Play Timeline**: 
  - All events chronologically
  - Team logos and player names
  - Event descriptions with player details
  - Filters: Period, Team, Player, Event Type
  - View Modes: Basic (important events only) | Detailed (all events)
  - Time display with start and end times
- **Shot Maps**: Enhanced shot maps with filters
- **Game Highlights**: Video links if available
- **Boxscore**: Player and goalie statistics
- **Team Statistics**: Team-level stats comparison

**Key Features**:
- **Basic View**: Shows only important events (game state, faceoffs, shots, goals, penalties, takeaways, giveaways, zone entries/exits)
- **Detailed View**: Shows all events
- **Event Filtering**: By period, team, player, event type
- **Event Descriptions**: 
  - Shots: "Shot by {player} saved by {goalie}"
  - Faceoffs: "Faceoff won by {winner} against {opponent}"
  - Goals: Shows scorer and assists
  - Turnovers: Uses `event_detail_2` for description
  - Zone entries/exits: Uses `event_detail_2` for description

---

## 📊 Analytics Pages

### Analytics Overview
**Path**: `/analytics/overview`

**Features**:
- League summary statistics
- Standings table
- Leaders (Points, Goals, Assists, Goalies)
- Recent games
- **Analytics Tools Grid**:
  - xG Analysis
  - Trends
  - Statistics
  - WAR/GAR Leaders
  - Micro Stats
  - Zone Analytics
  - Rush Analysis
  - Faceoff Analysis
  - Line Combinations

---

### xG Analysis Dashboard
**Path**: `/analytics/xg`

**Features**:
- **Summary Stats**: Total xG, Total Goals, Avg xG/Game, Total GAE
- **xG Trends by Season**: Line chart showing average xG and goals over time
- **xG Leaders Table**: 
  - Rank, Player, GP, Goals, xG, Goals Above Expected (GAE)
  - xG/G, G/G, Shooting %
  - Links to player profiles
- **Top Goals Above Expected**: Players with highest GAE
- **Top xG Per Game**: Players with highest xG per game (min 10 GP)

**What It Shows**:
- Expected Goals (xG) measures shot quality
- Goals Above Expected shows finishing ability
- Positive GAE = finishing above expected (good shooter)
- Negative GAE = finishing below expected

---

### WAR/GAR Leaders
**Path**: `/analytics/war`

**Features**:
- **Summary Stats**: Total WAR, Total GAR, Average WAR, Average GAR
- **WAR/GAR Trends by Season**: Line chart showing trends over time
- **WAR Leaders Table**:
  - Rank, Player, GP, G, A, P, WAR, GAR
  - WAR/G, CF%, Rating
  - Links to player profiles
- **Top WAR Per Game**: Players with highest WAR per game (min 10 GP)
- **Top GAR Leaders**: Players with highest total GAR

**What It Shows**:
- **WAR (Wins Above Replacement)**: Total wins added above replacement-level player
- **GAR (Goals Above Replacement)**: Total goals added above replacement level
- Higher values = more valuable players
- 1.0 WAR = 1 additional win per season
- 2.0+ WAR = elite player

---

### Micro Stats Explorer
**Path**: `/analytics/micro-stats`

**Features**:
- **Summary Stats**: Players tracked, Total Dekes, Total Drives, Total Puck Battles
- **Top Performers by Category**:
  - Top Dekes Per Game
  - Top Drives Per Game
  - Top Puck Battles Per Game
  - Top Forechecks Per Game
- **Comprehensive Micro Stats Table**:
  - Player, GP, Dekes, Drives, Puck Battles
  - Forechecks, Backchecks, Loose Puck Wins
  - Play Success Rate

**Micro Stats Tracked**:
- **Offensive Skills**: Dekes, drives (middle/wide/corner), cutbacks, delays, crash net, screens, give-and-go, second touch, cycles
- **Defensive Skills**: Poke checks, stick checks, zone entry denials, backchecks, forechecks, breakouts
- **Puck Battles**: Total puck battles, loose puck wins, puck recoveries, board battles
- **Passing**: Stretch passes, rim passes, bank passes, cross-ice passes
- **Shooting**: One-timers, snap shots, wrist shots, slap shots, tips, deflections

---

### Zone Analytics Dashboard
**Path**: `/analytics/zone`

**Features**:
- **Summary Stats**: Total Entries, Total Exits, Controlled entries/exits, Avg success rates
- **Top Performers**:
  - Top Zone Entry Leaders (per game)
  - Top Controlled Entry Rate (min 10 entries)
  - Top Zone Exit Leaders (per game)
  - Top Controlled Exit Rate (min 10 exits)
- **Comprehensive Zone Stats Table**:
  - Player, GP, Entries, Controlled Entries, Entry %
  - Exits, Controlled Exits, Exit %

**What It Shows**:
- **Zone Entries**: How players enter the offensive zone
  - Controlled entries: Maintain possession (more valuable)
  - Dump entries: Safer but less effective
- **Zone Exits**: How players exit the defensive zone
  - Controlled exits: Maintain possession
  - Clear exits: Safer but less effective
- **Success Rates**: Percentage of successful entries/exits

---

### Rush Analysis Dashboard
**Path**: `/analytics/rushes`

**Features**:
- **Summary Stats**: Total Rush Shots, Total Rush Goals, Total Breakaways, Total Rush Involvement
- **Top Performers**:
  - Top Rush Involvement
  - Top Rush Goals
  - Top Rush Success Rate (min 10 rushes)
  - Top Breakaway Goals
- **Comprehensive Rush Stats Table**:
  - Player, GP, Rush Involvement, Rush Shots, Rush Goals
  - Rush Points, Breakaways, Success Rate

**What It Shows**:
- **Rushes**: Zone entries that lead to shots within 7 seconds
- **Rush Involvement**: Total number of rushes a player is involved in
- **Rush Success Rate**: Percentage of rushes that generate shots
- **Breakaway Goals**: Goals scored on breakaway opportunities
- **Odd-Man Rushes**: 2-on-1, 3-on-2 situations

---

### Faceoff Analysis Dashboard
**Path**: `/analytics/faceoffs`

**Features**:
- **Summary Stats**: Total Faceoffs, Total Wins, Avg Win %, Players Tracked
- **Top Performers**:
  - Top Win % (min 20 faceoffs)
  - Top Faceoff Wins
  - Top Faceoff Volume
- **Comprehensive Faceoff Stats Table**:
  - Player, GP, Total, Wins, Losses, Win %, FO/Game

**What It Shows**:
- **Faceoff Win Percentage**: Percentage of faceoffs won
- **Faceoff Volume**: Total number of faceoffs taken
- **Zone Analysis**: Faceoff performance by zone (if available)
- **WDBE Analysis**: Win Direction Based Events (if available)

---

### Line Combinations Analysis
**Path**: `/analytics/lines`

**Features**:
- **Summary Stats**: Total Lines, Total TOI, Avg CF%, Total Goals
- **Top Performing Lines**:
  - Top CF% (min 3 GP)
  - Top GF% (min 3 GP)
  - Most Used Lines (by TOI)
- **Comprehensive Line Stats Table**:
  - Line (3 forwards), Team, GP, TOI
  - GF, GA, CF%, GF%, xGF%

**What It Shows**:
- **Line Performance**: How forward lines perform together
- **CF% (Corsi For %)**: Shot attempt percentage
- **GF% (Goals For %)**: Goal percentage
- **xGF% (Expected Goals For %)**: Expected goal percentage
- **WOWY Analysis**: With Or Without You - how players perform together vs. apart

---

### Trends Analysis
**Path**: `/analytics/trends`

**Features**:
- **Team Statistics Trends**: Wins, losses, points over seasons
- **Goals Per Game Trends**: Goals for vs. goals against
- **Player Scoring Trends**: Average goals, assists, points per season
- **Available Seasons**: List of all tracked seasons

---

### League Statistics
**Path**: `/analytics/statistics`

**Features**:
- Comprehensive league-wide statistics
- Team statistics
- Player statistics
- Goalie statistics

---

## 🏆 Leaderboards

### Main Leaderboards
**Path**: `/leaders`

**Features**:
- **Tabs**: Points | Goals | Assists | Goalies
- Sortable columns
- Filters by season
- Links to player/goalie profiles

---

## 🔗 Comparison Tools

### Player Comparison
**Path**: `/players/compare?p1=[id]&p2=[id]&p3=[id]&p4=[id]`

**How to Use**:
1. Visit a player profile page
2. Click "Compare with another player"
3. Add additional players via URL parameters
4. View side-by-side stat comparison
5. See radar chart comparison

---

### Goalie Comparison
**Path**: `/goalies/compare?g1=[id]&g2=[id]&g3=[id]&g4=[id]`

**How to Use**:
1. Visit a goalie profile page
2. Click "Compare Goalies"
3. Add additional goalies via URL parameters
4. View side-by-side stat comparison
5. See radar chart comparison

---

### Team Comparison
**Path**: `/teams/compare?t1=[id]&t2=[id]&t3=[id]&t4=[id]`

**How to Use**:
1. Visit team profile pages to get team IDs
2. Add team IDs to URL parameters
3. View side-by-side stat comparison

---

## ✨ Key Features

### Filtering & Views

**Play-by-Play Timeline**:
- **Period Filter**: Filter events by period (1, 2, 3, OT, All)
- **Team Filter**: Filter by home team, away team, or all
- **Player Filter**: Filter events involving specific players
- **Event Type Filter**: Filter by event type (Goals, Penalties, Highlights, All)
- **View Mode**: 
  - **Basic**: Important events only (game state, faceoffs, shots, goals, penalties, takeaways, giveaways, zone entries/exits)
  - **Detailed**: All events

**Shot Maps**:
- Period filter
- Strength situation filter (5v5, PP, PK)
- Player filter
- Shot result filter (Goals, Saves, Misses)

---

### Data Display Features

**Time Display**:
- Normalized to 18:00 period start
- Shows start time and end time (e.g., "12:30 → 12:35")
- Handles variable period lengths

**Team Logos**:
- Displayed in timelines, summaries, and headers
- Team-specific colors for team names
- No gradient background (clean look)

**Player Photos**:
- Displayed in player profiles, game pages, leaderboards
- Fallback to initials if photo unavailable

**Event Descriptions**:
- **Goals**: "Goal by {scorer} (Assists: {assist1}, {assist2})"
- **Shots**: "Shot by {shooter} saved by {goalie}"
- **Faceoffs**: "Faceoff won by {winner} against {opponent}"
- **Turnovers**: Uses `event_detail_2` (e.g., "Bad Pass by {player}")
- **Zone Entries/Exits**: Uses `event_detail_2` (e.g., "Controlled Entry - {player}")
- **Deadice/Stoppage**: No player/team information shown

---

### Navigation Tips

1. **Breadcrumbs**: Use back arrows (←) to navigate back
2. **Quick Links**: Many stats are clickable and link to detailed pages
3. **URL Parameters**: Many pages support URL parameters for filtering/comparison
4. **Search**: Use browser search (Cmd/Ctrl+F) to find specific players/teams
5. **Tabs**: Many pages use tabs to organize content (Overview, Season, Career, Advanced)

---

### Data Sources

**Player Data**:
- `fact_player_game_stats` (317 columns)
- `fact_player_season_stats`
- `fact_player_career_stats`
- `fact_player_micro_stats`
- `dim_player`

**Goalie Data**:
- `fact_goalie_game_stats` (128 columns)
- `fact_goalie_season_stats`
- `fact_goalie_career_stats`
- `fact_saves`
- `dim_player`

**Team Data**:
- `fact_team_game_stats`
- `fact_team_season_stats`
- `fact_team_zone_time`
- `fact_line_combos`
- `fact_wowy`
- `dim_team`

**Game Data**:
- `fact_events` (140 columns)
- `fact_shifts`
- `fact_shot_xy`
- `dim_schedule`

**Analytics Data**:
- `fact_zone_entries` / `fact_zone_exits`
- `fact_rushes` / `fact_rush_events`
- `fact_faceoffs`
- `fact_line_combos`
- `fact_wowy`

---

## 🎯 Common Use Cases

### "I want to see a player's performance over time"
→ Go to `/players/[playerId]` → Click "View Trends" → See time-series charts and rolling averages

### "I want to compare two players"
→ Go to `/players/[playerId]` → Click "Compare with another player" → Add second player → View comparison

### "I want to see all events in a game"
→ Go to `/games/[gameId]` → Scroll to "Play-by-Play Timeline" → Use filters to narrow down

### "I want to find the best faceoff takers"
→ Go to `/analytics/faceoffs` → See "Top Win %" and "Top Faceoff Wins" sections

### "I want to see which lines perform best"
→ Go to `/analytics/lines` → See "Top CF%" and "Top GF%" sections

### "I want to see a player's game-by-game breakdown"
→ Go to `/players/[playerId]` → Season Tab → Scroll to "Game-by-Game Stats Table"

### "I want to see a goalie's save percentage trend"
→ Go to `/goalies/[goalieId]` → See "Save Percentage Trend" chart

### "I want to see zone entry/exit leaders"
→ Go to `/analytics/zone` → See top performers by entry/exit rates

### "I want to see rush leaders"
→ Go to `/analytics/rushes` → See top rush involvement and rush goals

### "I want to see WAR/GAR leaders"
→ Go to `/analytics/war` → See WAR Leaders table

---

## 📱 Mobile Navigation

All pages are responsive and work on mobile devices. Key navigation elements:
- Hamburger menu (if implemented)
- Back arrows for navigation
- Tab navigation for organized content
- Collapsible sections for advanced stats

---

## 🔍 Search & Filter Tips

1. **Player Search**: Use browser search on player directory pages
2. **Season Filter**: Many pages support `?season=[seasonId]` URL parameter
3. **Game Type Filter**: Many pages support `?gameType=[Regular|Playoffs|All]` URL parameter
4. **Period Filter**: Play-by-play timeline has period dropdown
5. **Team Filter**: Play-by-play timeline has team dropdown
6. **Player Filter**: Play-by-play timeline has player dropdown

---

## 💡 Pro Tips

1. **Bookmark Frequently Used Pages**: Save player/goalie/team profiles you check often
2. **Use Trends Pages**: Great for identifying hot/cold streaks
3. **Compare Players**: Use comparison tools to evaluate similar players
4. **Check Advanced Stats**: Don't just look at goals/points - check WAR, xG, CF% for deeper insights
5. **Use Filters**: Play-by-play timeline filters help focus on specific game situations
6. **View Mode Toggle**: Switch between Basic and Detailed views in play-by-play to focus on important events
7. **Drill Down**: Click on stats to see game-by-game breakdowns
8. **Check Micro Stats**: See detailed player actions that don't show in box scores

---

## 🆘 Need Help?

- **Data Not Loading**: Check if the game/player has tracking data available
- **Missing Stats**: Some stats only appear for tracked games
- **Can't Find a Page**: Use the main navigation or search for player/team names
- **Stats Look Wrong**: Check the season filter - make sure you're looking at the right season

---

**Last Updated**: 2026-01-15  
**Dashboard Version**: 2.0  
**Total Pages**: 50+ dashboard pages

---

## 🆕 New Features (v2.0)

### CSV Export
- **Export Buttons**: Available on Players and Goalies pages
- **Export Format**: CSV files with formatted data
- **Usage**: Click "Export CSV" button on any stat table

### Enhanced Team Pages
- **5 Tabs**: Overview, Roster, Lines, Analytics, Matchups
- **Lines Tab**: Team-specific line combination analysis
- **Analytics Tab**: Zone time breakdown and WOWY analysis
- **Matchups Tab**: Head-to-head records against all opponents

### Enhanced Goalie Pages
- **5 Tabs**: Overview, Season, Career, Advanced, Saves
- **Saves Tab**: Save-by-save breakdown with save type distribution
- **Advanced Tab**: GSAx, WAR, GAR, HD Save %, Quality Starts
- **Trend Charts**: Save % and GAA trends with rolling averages

### Shift Charts
- **Location**: Game detail pages
- **Visualization**: Bar charts showing TOI and shifts by period
- **Usage**: Automatically displayed when shift data is available

### Matchup Analysis
- **Player Matchups**: `/players/matchups?p1=[id]&p2=[id]`
- **Team Matchups**: Available in team profile Matchups tab
- **Features**: Head-to-head stat comparison, common games analysis

### Quality of Competition (QoC)
- **Location**: Player profile → Advanced tab
- **Metrics**: Average opponent rating, own rating, rating differential
- **Usage**: Shows difficulty of competition faced

### Shot Chains Analysis
- **Location**: `/analytics/shot-chains`
- **Features**: Shot sequence analysis and pattern visualization
- **Access**: Analytics Overview → Shot Chains

---

## 📊 Export Functionality

### CSV Export
Most data tables now include an "Export CSV" button in the header:
- **Players Page**: Export player rankings
- **Goalies Page**: Export goalie leaderboards (all tabs)
- **Format**: CSV files with formatted column headers
- **Filename**: Includes date stamp (e.g., `players_2026-01-15.csv`)

---

## 🎯 Quick Access Guide

### Finding Player Stats
1. **Main Stats**: `/players` → Click player name
2. **Trends**: Player profile → "View Trends" button
3. **Game Stats**: Player profile → Season tab → Click game
4. **Advanced Stats**: Player profile → Advanced tab

### Finding Goalie Stats
1. **Main Stats**: `/goalies` → Click goalie name
2. **Saves**: Goalie profile → Saves tab
3. **Advanced**: Goalie profile → Advanced tab
4. **Compare**: Goalie profile → "Compare Goalies" link

### Finding Team Stats
1. **Main Stats**: `/teams` → Click team name
2. **Line Combos**: Team profile → Lines tab
3. **Zone Time**: Team profile → Analytics tab
4. **Matchups**: Team profile → Matchups tab

### Finding Game Stats
1. **Game List**: `/games`
2. **Game Detail**: Click any game
3. **Shift Chart**: Automatically shown on game pages
4. **Play-by-Play**: Scroll to "Play-by-Play Timeline"

### Finding Analytics
1. **Overview**: `/analytics/overview`
2. **xG**: `/analytics/xg`
3. **WAR/GAR**: `/analytics/war`
4. **Micro Stats**: `/analytics/micro-stats`
5. **Zone Analytics**: `/analytics/zone`
6. **Rushes**: `/analytics/rushes`
7. **Faceoffs**: `/analytics/faceoffs`
8. **Line Combos**: `/analytics/lines`
9. **Shot Chains**: `/analytics/shot-chains`

---

## 🔍 Search & Filtering

### Player Search
- **Component**: `PlayerSearchFilters` (ready for integration)
- **Features**: Search by name, filter by position/team/min GP
- **Status**: Component created, ready to integrate into pages

### Game Filtering
- **Available Filters**: Season, team, game type
- **Location**: `/games` page
- **Usage**: Use filter dropdowns at top of page

---

## 📈 Visualizations Available

### Charts
- **Trend Line Charts**: Time-series with rolling averages
- **Radar Charts**: Multi-dimensional player comparisons
- **Bar Charts**: Shift charts, stat comparisons
- **Shot Maps**: Enhanced shot location visualization

### Data Tables
- **Sortable Tables**: Most stat tables are sortable
- **Exportable**: Key tables have CSV export
- **Filterable**: Many tables support filtering

---

## 🎨 Design Patterns

### Consistent Components
- **StatCard**: Collapsible stat sections
- **StatRow**: Individual stat rows with descriptions
- **PlayerPhoto**: Player photos with fallback initials
- **TeamLogo**: Team logos with colors
- **ExportButton**: Reusable CSV export button

### Color Coding
- **Goals**: Red/orange (`text-goal`)
- **Assists**: Blue (`text-assist`)
- **Saves**: Green (`text-save`)
- **Primary**: Theme primary color
- **Positive Stats**: Green
- **Negative Stats**: Red

---

## 🚀 Performance Tips

1. **Use Filters**: Filter by season/game type to reduce data load
2. **Export Data**: Use CSV export for offline analysis
3. **Bookmark Pages**: Save frequently used player/team pages
4. **Use Tabs**: Navigate efficiently using tab interfaces
5. **Check Advanced Stats**: Don't miss the Advanced tab on player/goalie profiles

---

## 📱 Mobile Experience

All pages are fully responsive:
- Tables scroll horizontally on mobile
- Cards stack vertically
- Navigation adapts to screen size
- Touch-friendly buttons and links

---

## 🔗 Integration Points

### Navigation Flow
- **Players** → Player Profile → Trends → Game Pages
- **Goalies** → Goalie Profile → Compare → Game Pages
- **Teams** → Team Profile → Lines/Analytics/Matchups
- **Games** → Game Detail → Player Pages → Player Game Pages
- **Analytics** → Overview → Specific Analytics Pages

### Cross-Linking
- Player names link to profiles
- Team names link to team pages
- Game dates link to game pages
- Stat values often link to detailed views

---

## 💡 Pro Tips

1. **Use Export**: Export data for deeper analysis in Excel/Google Sheets
2. **Compare Players**: Use comparison tools to evaluate similar players
3. **Check Trends**: Look at rolling averages to identify patterns
4. **Explore Advanced Stats**: Don't just look at goals/points
5. **Use Matchups**: See how players/teams perform head-to-head
6. **Check QoC**: Understand competition difficulty
7. **Review Shift Charts**: See TOI distribution by period
8. **Explore Line Combos**: Find effective line combinations

---

**Dashboard is now feature-complete!** 🎉
