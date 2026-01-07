# Supabase Query Reference

**Ready-to-use queries for Dashboard, Tracker, and Portal**

---

## Setup

```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_ANON_KEY
)
```

---

## Dashboard Queries

### League Standings

```javascript
// Current standings
const { data: standings } = await supabase
  .from('fact_team_standings_snapshot')
  .select('*')
  .order('points', { ascending: false })

// Format: { team_name, wins, losses, ties, points, goals_for, goals_against }
```

### Scoring Leaders

```javascript
// Top scorers (season)
const { data: leaders } = await supabase
  .from('fact_player_stats_core')
  .select('player_id, player_name, team_name, total_goals, total_assists, total_points, games_played')
  .order('total_points', { ascending: false })
  .limit(20)

// Top scorers (single game)
const { data: gameLeaders } = await supabase
  .from('fact_player_game_stats')
  .select('player_name, goals, assists, points')
  .eq('game_id', gameId)
  .order('points', { ascending: false })
  .limit(10)
```

### Recent Games

```javascript
// Last 10 completed games
const { data: recentGames } = await supabase
  .from('dim_schedule')
  .select('game_id, game_date_str, home_team_name, away_team_name, home_total_goals, away_total_goals')
  .eq('game_status', 'completed')
  .order('game_date_str', { ascending: false })
  .limit(10)
```

### Game Box Score

```javascript
// Full box score
async function getBoxScore(gameId) {
  const [gameResult, statsResult, eventsResult] = await Promise.all([
    // Game info
    supabase
      .from('dim_schedule')
      .select('*')
      .eq('game_id', gameId)
      .single(),
    
    // Player stats
    supabase
      .from('fact_player_game_stats')
      .select('*')
      .eq('game_id', gameId)
      .order('points', { ascending: false }),
    
    // Scoring summary (goals only)
    supabase
      .from('fact_events')
      .select('*, fact_events_player(player_id, player_role)')
      .eq('game_id', gameId)
      .eq('event_type', 'Goal')
      .order('period')
      .order('event_time')
  ])

  return {
    game: gameResult.data,
    playerStats: statsResult.data,
    goals: eventsResult.data
  }
}
```

### Player Profile

```javascript
async function getPlayerProfile(playerId) {
  const [playerResult, statsResult, recentGames] = await Promise.all([
    // Player info
    supabase
      .from('dim_player')
      .select('*')
      .eq('player_id', playerId)
      .single(),
    
    // Season totals
    supabase
      .from('fact_player_stats_core')
      .select('*')
      .eq('player_id', playerId)
      .single(),
    
    // Recent games
    supabase
      .from('fact_player_game_stats')
      .select('game_id, goals, assists, points, shots, toi_minutes')
      .eq('player_id', playerId)
      .order('game_id', { ascending: false })
      .limit(5)
  ])

  return {
    player: playerResult.data,
    seasonStats: statsResult.data,
    recentGames: recentGames.data
  }
}
```

### Team Stats

```javascript
// Team season summary
const { data: teamStats } = await supabase
  .from('fact_team_standings_snapshot')
  .select('*')
  .eq('team_id', teamId)
  .single()

// Team roster
const { data: roster } = await supabase
  .from('dim_player')
  .select('player_id, player_full_name, jersey_number, primary_position, skill_rating')
  .eq('team_id', teamId)
  .eq('is_active', '1')
  .order('jersey_number')
```

---

## Tracker Queries

### Get Game Roster

```javascript
// Players available for a game (both teams)
async function getGameRoster(gameId) {
  // First get the game to find teams
  const { data: game } = await supabase
    .from('dim_schedule')
    .select('home_team_id, away_team_id')
    .eq('game_id', gameId)
    .single()

  // Then get players for both teams
  const { data: players } = await supabase
    .from('dim_player')
    .select('player_id, player_full_name, jersey_number, primary_position, team_id')
    .in('team_id', [game.home_team_id, game.away_team_id])
    .eq('is_active', '1')
    .order('jersey_number')

  return {
    homeTeam: players.filter(p => p.team_id === game.home_team_id),
    awayTeam: players.filter(p => p.team_id === game.away_team_id)
  }
}
```

### Event Types Reference

```javascript
// Get all valid event types
const { data: eventTypes } = await supabase
  .from('dim_event_type')
  .select('event_type_id, event_type_name, category')
  .order('category')
  .order('event_type_name')

// Common event types:
// - Shot, Goal, Save, Blocked Shot
// - Faceoff Won, Faceoff Lost
// - Hit, Penalty
// - Turnover, Takeaway
```

### Get Existing Events (for Resume)

```javascript
// Get events already recorded for a game
const { data: existingEvents } = await supabase
  .from('fact_events')
  .select('*')
  .eq('game_id', gameId)
  .order('period')
  .order('event_index')
```

### Insert New Event

```javascript
// NOTE: Typically use ETL API for inserts, but direct insert possible:
async function recordEvent(event) {
  const { data, error } = await supabase
    .from('fact_events')
    .insert({
      event_key: `EVT_${event.game_id}_${event.period}_${Date.now()}`,
      game_id: event.game_id,
      period: event.period,
      event_time: event.time,
      event_type: event.type,
      event_detail: event.detail,
      team_id: event.teamId,
      zone: event.zone,
      x_coord: event.x,
      y_coord: event.y
    })
    .select()

  return { data, error }
}
```

---

## Portal Queries

### League Overview

```javascript
async function getLeagueOverview() {
  const [teams, players, games, season] = await Promise.all([
    supabase.from('dim_team').select('*').eq('is_active', '1'),
    supabase.from('dim_player').select('player_id').eq('is_active', '1'),
    supabase.from('dim_schedule').select('game_id, game_status'),
    supabase.from('dim_season').select('*').order('season_id', { ascending: false }).limit(1)
  ])

  return {
    totalTeams: teams.data.length,
    totalPlayers: players.data.length,
    completedGames: games.data.filter(g => g.game_status === 'completed').length,
    scheduledGames: games.data.filter(g => g.game_status === 'scheduled').length,
    currentSeason: season.data[0]
  }
}
```

### Manage Players

```javascript
// Get all players with team info
const { data: players } = await supabase
  .from('dim_player')
  .select(`
    *,
    dim_team!team_id (team_name)
  `)
  .order('player_full_name')

// Update player
const { error } = await supabase
  .from('dim_player')
  .update({
    skill_rating: '8',
    team_id: 'T002',
    primary_position: 'C'
  })
  .eq('player_id', 'P001')

// Deactivate player
const { error } = await supabase
  .from('dim_player')
  .update({ is_active: '0' })
  .eq('player_id', 'P001')
```

### Manage Schedule

```javascript
// Get full schedule
const { data: schedule } = await supabase
  .from('dim_schedule')
  .select('*')
  .order('game_date_str')

// Add new game
const { data, error } = await supabase
  .from('dim_schedule')
  .insert({
    game_id: 'NEW_GAME_ID',
    game_date_str: '2025-02-01',
    season_id: 'S2025',
    home_team_id: 'T001',
    away_team_id: 'T002',
    home_team_name: 'Ice Dogs',
    away_team_name: 'Polar Bears',
    venue_id: 'V001',
    game_status: 'scheduled'
  })
  .select()

// Update game result
const { error } = await supabase
  .from('dim_schedule')
  .update({
    home_total_goals: '5',
    away_total_goals: '3',
    game_status: 'completed'
  })
  .eq('game_id', gameId)
```

### Team Management

```javascript
// Get all teams with player counts
const { data: teams } = await supabase
  .from('dim_team')
  .select(`
    *,
    dim_player!team_id (player_id)
  `)

// Add player count
const teamsWithCounts = teams.map(team => ({
  ...team,
  playerCount: team.dim_player?.length || 0
}))

// Update team
const { error } = await supabase
  .from('dim_team')
  .update({ team_name: 'New Team Name' })
  .eq('team_id', 'T001')
```

---

## Real-Time Subscriptions

### Live Game Updates

```javascript
// Subscribe to new events during a game
const subscription = supabase
  .channel('game-events')
  .on(
    'postgres_changes',
    {
      event: 'INSERT',
      schema: 'public',
      table: 'fact_events',
      filter: `game_id=eq.${gameId}`
    },
    (payload) => {
      console.log('New event:', payload.new)
      // Update UI with new event
    }
  )
  .subscribe()

// Unsubscribe when done
subscription.unsubscribe()
```

### Live Stats Updates

```javascript
// Subscribe to player stats changes
const subscription = supabase
  .channel('stats-updates')
  .on(
    'postgres_changes',
    {
      event: '*',
      schema: 'public',
      table: 'fact_player_game_stats'
    },
    (payload) => {
      console.log('Stats updated:', payload)
    }
  )
  .subscribe()
```

---

## Pagination

```javascript
// Paginated player list
async function getPlayers(page = 0, pageSize = 20) {
  const from = page * pageSize
  const to = from + pageSize - 1

  const { data, count } = await supabase
    .from('dim_player')
    .select('*', { count: 'exact' })
    .order('player_full_name')
    .range(from, to)

  return {
    players: data,
    total: count,
    page,
    pageSize,
    totalPages: Math.ceil(count / pageSize)
  }
}
```

---

## Search

```javascript
// Search players by name
const { data } = await supabase
  .from('dim_player')
  .select('*')
  .ilike('player_full_name', `%${searchTerm}%`)
  .limit(10)

// Full-text search (if enabled in Supabase)
const { data } = await supabase
  .from('dim_player')
  .select('*')
  .textSearch('player_full_name', searchTerm)
```

---

## Error Handling

```javascript
async function safeQuery(queryFn) {
  try {
    const { data, error } = await queryFn()
    
    if (error) {
      console.error('Supabase error:', error)
      throw new Error(error.message)
    }
    
    return data
  } catch (err) {
    console.error('Query failed:', err)
    throw err
  }
}

// Usage
const players = await safeQuery(() => 
  supabase.from('dim_player').select('*')
)
```

---

## Environment Setup

```bash
# .env file
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
```

```javascript
// Load environment
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_ANON_KEY
)
```
