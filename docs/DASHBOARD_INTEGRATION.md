# BenchSight Dashboard Integration Guide

## 🏆 Recommended Stack

| Layer | Technology | Why |
|-------|------------|-----|
| Framework | **Next.js 14+ (App Router)** | Server components, great caching, Vercel-native |
| Language | **TypeScript** | Type safety with Supabase, fewer bugs |
| Styling | **Tailwind CSS + shadcn/ui** | Rapid development, beautiful components |
| Database | **Supabase (PostgreSQL)** | Already configured, real-time ready |
| Charts | **Recharts + Custom SVG** | React-native charts + hockey rink |
| Deployment | **Vercel** | Free tier, auto-deploy from GitHub, preview URLs |
| Data Fetching | **Server Components + Supabase** | No client-side loading spinners |

> **📖 See `docs/NEXTJS_DASHBOARD_GUIDE.md` for full Next.js implementation details**

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        YOUR DASHBOARD (HTML/React)                       │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│   │  Standings   │  │  Leaderboard │  │  Player Page │                 │
│   │    Page      │  │     Page     │  │              │                 │
│   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                 │
└──────────┼─────────────────┼─────────────────┼──────────────────────────┘
           │                 │                 │
           ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      SUPABASE CLIENT (JavaScript)                        │
│   supabase.from('v_standings_current').select('*')                      │
│   supabase.from('v_leaderboard_points').select('*').limit(10)          │
│   supabase.from('v_detail_player_games').select('*').eq('player_id',x) │
└──────────┬─────────────────┬─────────────────┬──────────────────────────┘
           │                 │                 │
           ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         SUPABASE (PostgreSQL)                            │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │                        VIEW LAYER                                 │  │
│   │  v_standings_current    v_leaderboard_*    v_detail_*            │  │
│   │  v_rankings_*           v_summary_*        v_compare_*           │  │
│   └──────────────────────────────────────────────────────────────────┘  │
│                                 │                                        │
│                                 ▼                                        │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │                        TABLE LAYER (ETL)                          │  │
│   │  fact_player_season_stats_basic    fact_goalie_game_stats        │  │
│   │  fact_team_season_stats_basic      fact_player_game_stats        │  │
│   │  dim_player    dim_team    dim_schedule                          │  │
│   └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

## Step 1: Install Supabase Client

```bash
npm install @supabase/supabase-js
```

## Step 2: Initialize Connection

```javascript
// supabase-client.js
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://YOUR_PROJECT.supabase.co'
const supabaseKey = 'YOUR_ANON_KEY'  // Safe for client-side

export const supabase = createClient(supabaseUrl, supabaseKey)
```

## Step 3: Query Views (Same as Tables!)

### Basic Query
```javascript
// Get current standings
const { data, error } = await supabase
  .from('v_standings_current')
  .select('*')
  
// Returns all rows from the view
console.log(data)
```

### With Filters
```javascript
// Get top 10 points leaders for current season
const { data, error } = await supabase
  .from('v_leaderboard_points')
  .select('*')
  .eq('season_id', 'N20252026F')
  .limit(10)
```

### Player Detail Page
```javascript
// Get all games for a specific player
const { data, error } = await supabase
  .from('v_detail_player_games')
  .select('*')
  .eq('player_id', 'P100123')
  .order('date', { ascending: false })
```

### Player Comparison
```javascript
// Compare two players
const { data, error } = await supabase
  .from('v_compare_players')
  .select('*')
  .in('player_id', ['P100123', 'P100456'])
  .eq('season_id', 'N20252026F')
```

## Step 4: Dashboard Page Examples

### Standings Page
```javascript
async function loadStandings() {
  const { data } = await supabase
    .from('v_standings_current')
    .select('team_name, wins, losses, goal_diff, standing')
    .order('standing')
  
  return data
}
```

### Leaderboard Page
```javascript
async function loadLeaderboard(category, limit = 10) {
  const viewMap = {
    'points': 'v_leaderboard_points',
    'goals': 'v_leaderboard_goals',
    'assists': 'v_leaderboard_assists',
    'goalie_wins': 'v_leaderboard_goalie_wins'
  }
  
  const { data } = await supabase
    .from(viewMap[category])
    .select('*')
    .limit(limit)
  
  return data
}
```

### Player Profile Page
```javascript
async function loadPlayerProfile(playerId) {
  // Career stats
  const { data: career } = await supabase
    .from('v_summary_player_career')
    .select('*')
    .eq('player_id', playerId)
    .single()
  
  // Recent games
  const { data: games } = await supabase
    .from('v_detail_player_games')
    .select('*')
    .eq('player_id', playerId)
    .limit(10)
  
  return { career, games }
}
```

### Team Profile Page
```javascript
async function loadTeamProfile(teamId, seasonId) {
  // Team stats
  const { data: team } = await supabase
    .from('v_compare_teams')
    .select('*')
    .eq('team_id', teamId)
    .eq('season_id', seasonId)
    .single()
  
  // Team roster
  const { data: roster } = await supabase
    .from('v_compare_players')
    .select('player_name, position, goals, assists, points')
    .eq('team_id', teamId)
    .eq('season_id', seasonId)
    .order('points', { ascending: false })
  
  return { team, roster }
}
```

## View-to-Dashboard Mapping

| Dashboard Page | View(s) to Use |
|----------------|----------------|
| **Home/Dashboard** | v_standings_current, v_leaderboard_points (limit 5), v_recent_games |
| **Standings** | v_standings_current, v_standings_team_history |
| **Leaderboards** | v_leaderboard_points, v_leaderboard_goals, v_leaderboard_assists, v_leaderboard_goalie_wins |
| **Player Profile** | v_summary_player_career, v_detail_player_games, v_rankings_players |
| **Goalie Profile** | v_summary_goalie_career, v_detail_goalie_games, v_rankings_goalies |
| **Team Profile** | v_compare_teams, v_compare_players (filtered by team) |
| **Game Detail** | v_recent_games, fact_player_game_stats (filtered) |
| **Compare Players** | v_compare_players |
| **Compare Goalies** | v_compare_goalies |
| **Season Stats** | v_summary_league, v_rankings_players |

## Real-Time Updates (Optional)

```javascript
// Subscribe to changes in standings
const subscription = supabase
  .channel('standings-changes')
  .on('postgres_changes', 
    { event: '*', schema: 'public', table: 'fact_team_season_stats_basic' },
    (payload) => {
      console.log('Standings updated!', payload)
      loadStandings() // Refresh
    }
  )
  .subscribe()
```

## Error Handling

```javascript
async function safeQuery(viewName, query = '*', filters = {}) {
  try {
    let q = supabase.from(viewName).select(query)
    
    for (const [key, value] of Object.entries(filters)) {
      q = q.eq(key, value)
    }
    
    const { data, error } = await q
    
    if (error) throw error
    return { data, error: null }
    
  } catch (err) {
    console.error(`Query failed for ${viewName}:`, err)
    return { data: null, error: err.message }
  }
}

// Usage
const { data, error } = await safeQuery('v_standings_current')
```

## Performance Tips

1. **Use `select()` to limit columns** - Don't fetch all 444 columns if you only need 5
2. **Use `limit()` for leaderboards** - No need to fetch 295 career records for top 10
3. **Use views, not tables** - Views are optimized and always fresh
4. **Cache on client** - Store rarely-changing data (career stats) locally
5. **Paginate large results** - Use `.range(0, 19)` for pagination
