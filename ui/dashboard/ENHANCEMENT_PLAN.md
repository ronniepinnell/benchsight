# Comprehensive Enhancement Plan

## 1. Matchup Predictor & Win Probability

### Data Needed:
- **Team Season Stats** (`fact_team_season_stats_basic`):
  - Win percentage, goals for/against, CF%, FF%
  - Recent form (last 5-10 games)
  - Home/away splits
  
- **Head-to-Head History** (`fact_team_game_stats` or `dim_schedule`):
  - Historical matchups between teams
  - Win/loss record
  - Average goals for/against in matchups
  
- **Team Advanced Stats** (`fact_team_game_stats`):
  - Corsi For %, Fenwick For %
  - Expected Goals (xG)
  - Special teams (PP%, PK%)
  - Goaltending stats (GAA, SV%)

### Prediction Model:
```typescript
// Win Probability Calculation
function calculateWinProbability(homeTeam: TeamStats, awayTeam: TeamStats, h2hHistory?: H2HStats) {
  // Base win probability from team strength
  const homeStrength = (homeTeam.winPct * 0.4) + (homeTeam.cfPct / 100 * 0.3) + (homeTeam.goalsFor / homeTeam.goalsAgainst * 0.3)
  const awayStrength = (awayTeam.winPct * 0.4) + (awayTeam.cfPct / 100 * 0.3) + (awayTeam.goalsFor / awayTeam.goalsAgainst * 0.3)
  
  // Home ice advantage (+5-8% boost)
  const homeAdvantage = 0.06
  
  // Head-to-head adjustment
  const h2hAdjustment = h2hHistory ? (h2hHistory.homeWins / h2hHistory.totalGames - 0.5) * 0.1 : 0
  
  // Recent form (last 5 games)
  const homeRecentForm = homeTeam.recentWinPct * 0.1
  const awayRecentForm = awayTeam.recentWinPct * 0.1
  
  const homeWinProb = 0.5 + (homeStrength - awayStrength) + homeAdvantage + h2hAdjustment + (homeRecentForm - awayRecentForm)
  
  return {
    homeWinProb: Math.max(0.1, Math.min(0.9, homeWinProb)),
    awayWinProb: 1 - homeWinProb,
    confidence: calculateConfidence(homeTeam, awayTeam)
  }
}
```

### Implementation:
- Component: `MatchupPredictor` in schedule/upcoming games
- Display: Win probability bars, key matchup stats, prediction confidence
- Data source: `fact_team_season_stats_basic`, `fact_team_game_stats`, `dim_schedule`

---

## 2. Video Highlights for Tracked Games

### Data Needed:
- **Game Tracking Status** (`fact_game_status`):
  - `tracking_status`: 'Complete', 'Partial', 'Not Tracked'
  - `tracking_pct`: Percentage of game tracked
  - `events_row_count`: Number of events tracked
  
- **Event Data** (`fact_events`):
  - `is_highlight`: Flag for highlight-worthy events
  - `is_goal`: Goals (always highlights)
  - `event_type`: Shot, Goal, Save, etc.
  - `time_start_total_seconds`: Timestamp for video sync
  
- **Video URLs** (if available):
  - Game video URL from `dim_schedule` or separate table
  - Highlight timestamps

### Implementation:
- Component: `GameHighlights` on game detail pages
- Display: List of highlight events with timestamps
- Video player integration (if video URLs available)
- Filter by event type (goals, saves, hits, etc.)

---

## 3. Maximum Detail for All Levels

### Team Level:
- **Season Stats**: All columns from `fact_team_season_stats_basic`
- **Game Stats**: Aggregated from `fact_team_game_stats`
- **Advanced Stats**: CF%, FF%, xG, special teams, goaltending
- **Roster Analysis**: Player contributions, line combinations
- **Trends**: Season-over-season comparisons
- **Head-to-Head**: Matchup history with all teams

### Game Level:
- **Complete Box Score**: All players with full stats
- **Play-by-Play**: Event timeline from `fact_events`
- **Shift Charts**: Shift-by-shift analysis
- **Shot Chart**: Heatmap with all shots
- **Advanced Stats**: Team and player aggregates
- **Highlights**: Video timestamps and events
- **Matchup Context**: Head-to-head history

### Player Level:
- **Season Stats**: All columns from `fact_player_season_stats_basic`
- **Game Log**: Every game with full stats (from `dim_schedule` + `fact_gameroster`)
- **Advanced Stats**: All micro and macro stats
- **Trends**: Performance over time
- **Situational**: 5v5, PP, PK breakdowns
- **Matchups**: Head-to-head vs specific players
- **Line Combinations**: Performance with different linemates

### Season Level:
- **League Leaders**: All categories
- **Team Rankings**: Multiple metrics
- **Player Rankings**: Comprehensive leaderboards
- **Trends**: League-wide statistics
- **Awards**: MVP, scoring titles, etc.

---

## 4. Stat Tooltips with Formulas

### Stat Definitions Database:
```typescript
const STAT_DEFINITIONS = {
  'CF%': {
    name: 'Corsi For Percentage',
    formula: 'CF% = (CF / (CF + CA)) × 100',
    description: 'Percentage of shot attempts (shots, blocks, misses) for vs against when player is on ice',
    calculation: 'Corsi For / (Corsi For + Corsi Against) × 100',
    context: 'Higher is better. 50% = even, >50% = outshooting opponent'
  },
  'FF%': {
    name: 'Fenwick For Percentage',
    formula: 'FF% = (FF / (FF + FA)) × 100',
    description: 'Percentage of unblocked shot attempts (shots + misses) for vs against',
    calculation: 'Fenwick For / (Fenwick For + Fenwick Against) × 100',
    context: 'Similar to CF% but excludes blocked shots. Better predictor of future goals.'
  },
  'xG': {
    name: 'Expected Goals',
    formula: 'xG = Σ(shot_xg) where shot_xg = base_rate × modifiers',
    description: 'Expected goals based on shot quality, location, and context',
    calculation: 'Sum of individual shot xG values. Base rates: High danger=0.25, Medium=0.08, Low=0.03. Modifiers: Rush=1.3x, Rebound=1.5x, Screen=1.2x',
    context: 'Measures shot quality. Goals - xG shows finishing ability.'
  },
  'WAR': {
    name: 'Wins Above Replacement',
    formula: 'WAR = GAR / 4.5',
    description: 'Wins added above a replacement-level player',
    calculation: 'Goals Above Replacement divided by 4.5 (goals per win in rec hockey)',
    context: 'Higher is better. 1.0 WAR = 1 additional win per season'
  },
  'GAR': {
    name: 'Goals Above Replacement',
    formula: 'GAR = GAR_offense + GAR_defense + GAR_possession + GAR_transition',
    description: 'Total goals added above replacement level',
    calculation: 'GAR_offense = G×1.0 + A1×0.7 + A2×0.4 + SOG×0.015 + xG×0.8\nGAR_defense = TK×0.05 + BLK×0.02 + ZE×0.03\nGAR_possession = (CF% - 50) / 100 × 0.02 × TOI_hours × 60\nGAR_transition = Controlled entries × 0.04',
    context: 'Comprehensive value metric. 4.5 GAR = 1 WAR'
  },
  // ... more stats
}
```

### Implementation:
- Enhanced `StatRow` component with tooltip on hover
- Formula display in tooltip
- Calculation explanation
- Context/interpretation

---

## 5. Game Logs Using dim_schedule + fact_gameroster

### Current Issue:
- Game logs only show if `fact_player_game_stats` has advanced stats
- Need fallback to `dim_schedule` + `fact_gameroster` for basic stats

### Solution:
```typescript
// Priority order:
1. fact_player_game_stats (if available) - most complete
2. fact_gameroster + dim_schedule (fallback) - basic stats
3. dim_schedule only (minimal) - just game info

// Query logic:
async function getPlayerGameLog(playerId: string, seasonId?: string) {
  // Try advanced stats first
  const advancedStats = await getFromFactPlayerGameStats(playerId, seasonId)
  
  // Fallback to gameroster
  if (advancedStats.length === 0) {
    const rosterStats = await getFromFactGameroster(playerId, seasonId)
    const scheduleData = await getScheduleForGames(rosterStats.map(r => r.game_id))
    
    // Merge roster + schedule
    return mergeRosterAndSchedule(rosterStats, scheduleData)
  }
  
  return advancedStats
}
```

---

## Implementation Priority

### Phase 1 (Immediate):
1. ✅ Game logs using dim_schedule + fact_gameroster
2. ✅ Enhanced stat tooltips with formulas
3. ✅ Matchup predictor component
4. ✅ Game highlights component (if tracking data exists)

### Phase 2 (Next):
1. Maximum detail expansion for all pages
2. Video integration (if URLs available)
3. Advanced matchup analysis
4. Trend visualizations

### Phase 3 (Future):
1. Machine learning win probability model
2. Interactive video player with event sync
3. Advanced analytics dashboards
4. Custom report builder

---

## Data Requirements Checklist

### For Matchup Predictor:
- [x] Team season stats (win %, goals for/against)
- [x] Team advanced stats (CF%, FF%, xG)
- [ ] Head-to-head history (need to aggregate from dim_schedule)
- [ ] Recent form (last 5-10 games)
- [ ] Home/away splits

### For Highlights:
- [x] fact_game_status (tracking status)
- [x] fact_events (is_highlight, is_goal flags)
- [ ] Video URLs (if available in database)
- [ ] Event timestamps

### For Game Logs:
- [x] dim_schedule (game info, dates)
- [x] fact_gameroster (basic player stats)
- [x] fact_player_game_stats (advanced stats)

### For Tooltips:
- [x] Formula definitions (from code/docs)
- [ ] Calculation examples
- [ ] Context/interpretation guides
