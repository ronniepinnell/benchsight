# BenchSight Dashboard Developer - Next Prompt

Copy and paste this prompt to start or continue dashboard development.

---

## PROMPT START

I'm building dashboards for BenchSight, a hockey analytics platform. Data is in **Supabase PostgreSQL**.

### Database Connection
```
URL: https://uuaowslhpgyiudmbvqze.supabase.co
API: https://uuaowslhpgyiudmbvqze.supabase.co/rest/v1/
```

### Available Tables
**For Player Stats:**
- `fact_player_game_stats` - 29 columns: goals, assists, points, shots, sog, fo_wins, fo_losses, zone_entries, passes, giveaways, takeaways, toi_seconds, etc.
- `dim_player` - player_id, player_name, jersey_number, position

**For Team Stats:**
- `fact_team_game_stats` - 18 columns: goals, shots, sog, fo_wins, fo_losses, pass_pct, shooting_pct, etc.
- `dim_team` - team_id, team_name, team_abbrev

**For Game Data:**
- `dim_schedule` - game_id, game_date, home_team, away_team, home_score, away_score
- `fact_events` - event timeline (event_type, event_detail, period, time)

**For Goalie Stats:**
- `fact_goalie_game_stats` - 19 columns: saves, goals_against, save_pct, saves_glove, saves_blocker, saves_rebound, saves_freeze, etc.

**For Advanced:**
- `fact_h2h` - head-to-head when opponents on ice together
- `fact_wowy` - with-or-without-you for linemates

### Dashboard Hierarchy (Build Order)
1. League Standings & Leaders
2. Team Overview
3. Player Stats
4. Game Summary
5. Goalie Stats
6. Advanced (H2H, WOWY)

### What I Need Help With Today
[DESCRIBE YOUR SPECIFIC TASK]

**Examples:**
- "Help me build the league standings component with React"
- "I need SQL for the player leaderboard aggregations"
- "Design a responsive game summary layout"
- "Create a shot chart visualization from event data"

---

## PROMPT END

---

## Alternative Prompts

### For League Standings
```
I'm building the BenchSight league standings page.

Data source: `dim_schedule` table with columns: game_id, game_date, home_team, away_team, home_score, away_score

Need to calculate per team:
- Wins (home_score > away_score when home, or away_score > home_score when away)
- Losses
- Points (2 per win)
- Goals For / Goals Against
- Goal Differential
- Streak
- Last 10 games record

Tech stack: [React/Vue/Svelte] with Supabase JS client

Help me write the query and component.
```

### For Player Stats Page
```
I'm building a player stats page for BenchSight.

Data: `fact_player_game_stats` with columns: player_id, player_name, game_id, goals, assists, points, shots, sog, shooting_pct, fo_wins, fo_losses, toi_seconds, etc.

Features needed:
1. Player header card with season totals
2. Stats table (per game, per 60, league rank)
3. Game log (sortable table)
4. Trend chart (5-game rolling points average)

Supabase connection ready. Help me build this.
```

### For Game Summary
```
Building a game summary dashboard for BenchSight.

Tables:
- dim_schedule (scores)
- fact_team_game_stats (team comparison)
- fact_player_game_stats (three stars, player stats)
- fact_events (event timeline)

For game_id = 18969, need:
1. Score header with period breakdown
2. Team stats comparison (shots, faceoffs, etc.)
3. Three stars selection (top 3 by points + goalie by saves)
4. Event timeline with filters

Help me design and implement this.
```

### For Data Visualization
```
I need to create visualizations for BenchSight dashboards.

Available data:
- Shot locations (x, y coordinates in fact_events - coming soon)
- Player stats over time
- Team performance trends

Visualization needs:
1. Shot heat map on rink diagram
2. Line chart for rolling stats
3. Radar chart for player comparison
4. Bar chart for team comparison

Using [D3/Chart.js/Recharts]. Help me implement.
```

### For Mobile Optimization
```
BenchSight dashboards need mobile optimization.

Current issues:
- Wide tables don't fit on mobile
- Charts too small to read
- Filters take too much space

Help me:
1. Convert tables to cards on mobile
2. Make charts responsive
3. Create collapsible filter panels
4. Implement touch-friendly interactions
```

---

## Quick Reference

### Supabase Query Patterns
```javascript
// Aggregate stats
const { data } = await supabase
  .from('fact_player_game_stats')
  .select('player_name, goals.sum(), assists.sum(), points.sum()')
  .group('player_name')
  .order('points', { ascending: false })

// Join tables
const { data } = await supabase
  .from('fact_player_game_stats')
  .select(`
    *,
    dim_player(player_name, position),
    dim_schedule(game_date, home_team, away_team)
  `)
  .eq('player_id', 'P100192')

// Filter by date range
const { data } = await supabase
  .from('dim_schedule')
  .select('*')
  .gte('game_date', '2024-01-01')
  .lte('game_date', '2024-12-31')
```

### Key Stats Definitions
| Stat | Calculation |
|------|-------------|
| Points | Goals + Assists |
| Shooting % | Goals / Shots * 100 |
| FO % | FO Wins / (FO Wins + FO Losses) * 100 |
| Pass % | Passes Completed / Passes Attempted * 100 |
| Per 60 | Stat * 3600 / TOI Seconds |
| +/- | Goals For - Goals Against (when on ice) |

### Component Ideas
```
STANDINGS: Table with sort, team logos, sparkline for trend
LEADERS: Cards with player photo, stat highlight, rank badge
TEAM: Split view (offense/defense), gauges for percentages
PLAYER: Header card, tabbed stats sections, game log
GAME: Timeline, shot chart, momentum graph
GOALIE: Save diagram, micro-stat breakdown
```

---

*Last Updated: December 2024*
