# Dashboard Integration Guide

**For developers building the BenchSight analytics dashboard**

---

## Overview

The Dashboard displays hockey analytics visualizations including:
- League standings
- Player/team leaderboards
- Game summaries and box scores
- Statistical trends and charts

**Data Source:** Supabase (read-only)  
**Tech Stack:** HTML/JS or React  
**Primary Tables:** dim_schedule, fact_player_game_stats, fact_team_standings_snapshot

---

## Quick Start

### 1. Install Supabase Client

```bash
npm install @supabase/supabase-js
```

### 2. Initialize Connection

```javascript
// src/lib/supabase.js
import { createClient } from '@supabase/supabase-js'

export const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
)
```

### 3. Environment Variables

```bash
# .env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

---

## Key Components

### 1. Standings Table

```jsx
// components/Standings.jsx
import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'

export function Standings() {
  const [standings, setStandings] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchStandings() {
      const { data, error } = await supabase
        .from('fact_team_standings_snapshot')
        .select('team_name, wins, losses, ties, points, goals_for, goals_against')
        .order('points', { ascending: false })

      if (!error) setStandings(data)
      setLoading(false)
    }
    fetchStandings()
  }, [])

  if (loading) return <div>Loading standings...</div>

  return (
    <table className="standings-table">
      <thead>
        <tr>
          <th>Team</th>
          <th>W</th>
          <th>L</th>
          <th>T</th>
          <th>PTS</th>
          <th>GF</th>
          <th>GA</th>
        </tr>
      </thead>
      <tbody>
        {standings.map((team, idx) => (
          <tr key={team.team_name}>
            <td>{idx + 1}. {team.team_name}</td>
            <td>{team.wins}</td>
            <td>{team.losses}</td>
            <td>{team.ties}</td>
            <td><strong>{team.points}</strong></td>
            <td>{team.goals_for}</td>
            <td>{team.goals_against}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
```

### 2. Scoring Leaders

```jsx
// components/ScoringLeaders.jsx
export function ScoringLeaders({ limit = 10 }) {
  const [leaders, setLeaders] = useState([])

  useEffect(() => {
    async function fetchLeaders() {
      const { data } = await supabase
        .from('fact_player_stats_core')
        .select('player_name, team_name, total_goals, total_assists, total_points, games_played')
        .order('total_points', { ascending: false })
        .limit(limit)

      setLeaders(data || [])
    }
    fetchLeaders()
  }, [limit])

  return (
    <table>
      <thead>
        <tr>
          <th>Rank</th>
          <th>Player</th>
          <th>Team</th>
          <th>GP</th>
          <th>G</th>
          <th>A</th>
          <th>PTS</th>
        </tr>
      </thead>
      <tbody>
        {leaders.map((player, idx) => (
          <tr key={player.player_name}>
            <td>{idx + 1}</td>
            <td>{player.player_name}</td>
            <td>{player.team_name}</td>
            <td>{player.games_played}</td>
            <td>{player.total_goals}</td>
            <td>{player.total_assists}</td>
            <td><strong>{player.total_points}</strong></td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
```

### 3. Recent Games

```jsx
// components/RecentGames.jsx
export function RecentGames({ limit = 5 }) {
  const [games, setGames] = useState([])

  useEffect(() => {
    async function fetchGames() {
      const { data } = await supabase
        .from('dim_schedule')
        .select('game_id, game_date_str, home_team_name, away_team_name, home_total_goals, away_total_goals')
        .eq('game_status', 'completed')
        .order('game_date_str', { ascending: false })
        .limit(limit)

      setGames(data || [])
    }
    fetchGames()
  }, [limit])

  return (
    <div className="recent-games">
      {games.map(game => (
        <div key={game.game_id} className="game-card">
          <div className="game-date">{game.game_date_str}</div>
          <div className="matchup">
            <span className={parseInt(game.away_total_goals) > parseInt(game.home_total_goals) ? 'winner' : ''}>
              {game.away_team_name} {game.away_total_goals}
            </span>
            <span className="at">@</span>
            <span className={parseInt(game.home_total_goals) > parseInt(game.away_total_goals) ? 'winner' : ''}>
              {game.home_team_name} {game.home_total_goals}
            </span>
          </div>
        </div>
      ))}
    </div>
  )
}
```

### 4. Game Box Score

```jsx
// components/BoxScore.jsx
export function BoxScore({ gameId }) {
  const [game, setGame] = useState(null)
  const [stats, setStats] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchBoxScore() {
      // Fetch game info
      const { data: gameData } = await supabase
        .from('dim_schedule')
        .select('*')
        .eq('game_id', gameId)
        .single()

      // Fetch player stats
      const { data: statsData } = await supabase
        .from('fact_player_game_stats')
        .select('*')
        .eq('game_id', gameId)
        .order('points', { ascending: false })

      setGame(gameData)
      setStats(statsData || [])
      setLoading(false)
    }
    fetchBoxScore()
  }, [gameId])

  if (loading) return <div>Loading...</div>
  if (!game) return <div>Game not found</div>

  const homeStats = stats.filter(s => s.team_id === game.home_team_id)
  const awayStats = stats.filter(s => s.team_id === game.away_team_id)

  return (
    <div className="box-score">
      <div className="score-header">
        <h2>{game.away_team_name} {game.away_total_goals} @ {game.home_team_name} {game.home_total_goals}</h2>
        <p>{game.game_date_str}</p>
      </div>

      <div className="team-stats">
        <TeamStats team={game.home_team_name} players={homeStats} />
        <TeamStats team={game.away_team_name} players={awayStats} />
      </div>
    </div>
  )
}

function TeamStats({ team, players }) {
  return (
    <div className="team-section">
      <h3>{team}</h3>
      <table>
        <thead>
          <tr>
            <th>Player</th>
            <th>G</th>
            <th>A</th>
            <th>P</th>
            <th>SOG</th>
            <th>+/-</th>
            <th>TOI</th>
          </tr>
        </thead>
        <tbody>
          {players.map(p => (
            <tr key={p.player_game_key}>
              <td>{p.player_name}</td>
              <td>{p.goals}</td>
              <td>{p.assists}</td>
              <td>{p.points}</td>
              <td>{p.shots}</td>
              <td>{p.plus_minus}</td>
              <td>{p.toi_minutes}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
```

### 5. Player Profile

```jsx
// components/PlayerProfile.jsx
export function PlayerProfile({ playerId }) {
  const [player, setPlayer] = useState(null)
  const [stats, setStats] = useState(null)
  const [games, setGames] = useState([])

  useEffect(() => {
    async function fetchPlayer() {
      const [playerRes, statsRes, gamesRes] = await Promise.all([
        supabase.from('dim_player').select('*').eq('player_id', playerId).single(),
        supabase.from('fact_player_stats_core').select('*').eq('player_id', playerId).single(),
        supabase.from('fact_player_game_stats').select('*').eq('player_id', playerId).order('game_id', { ascending: false }).limit(10)
      ])

      setPlayer(playerRes.data)
      setStats(statsRes.data)
      setGames(gamesRes.data || [])
    }
    fetchPlayer()
  }, [playerId])

  if (!player) return <div>Loading...</div>

  return (
    <div className="player-profile">
      <div className="player-header">
        <h1>#{player.jersey_number} {player.player_full_name}</h1>
        <p>{player.team_name} | {player.primary_position}</p>
        <p>Skill Rating: {player.skill_rating}/10</p>
      </div>

      {stats && (
        <div className="season-stats">
          <h2>Season Stats</h2>
          <div className="stat-grid">
            <div><strong>{stats.games_played}</strong><br/>GP</div>
            <div><strong>{stats.total_goals}</strong><br/>G</div>
            <div><strong>{stats.total_assists}</strong><br/>A</div>
            <div><strong>{stats.total_points}</strong><br/>P</div>
          </div>
        </div>
      )}

      <div className="game-log">
        <h2>Recent Games</h2>
        <table>
          <thead>
            <tr><th>Game</th><th>G</th><th>A</th><th>P</th><th>SOG</th></tr>
          </thead>
          <tbody>
            {games.map(g => (
              <tr key={g.player_game_key}>
                <td>{g.game_id}</td>
                <td>{g.goals}</td>
                <td>{g.assists}</td>
                <td>{g.points}</td>
                <td>{g.shots}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
```

---

## Custom Hooks

### useSupabaseQuery

```jsx
// hooks/useSupabaseQuery.js
import { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'

export function useSupabaseQuery(table, options = {}) {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const { select = '*', filters = {}, order, limit } = options

  useEffect(() => {
    async function fetch() {
      let query = supabase.from(table).select(select)

      // Apply filters
      Object.entries(filters).forEach(([key, value]) => {
        query = query.eq(key, value)
      })

      // Apply order
      if (order) {
        query = query.order(order.column, { ascending: order.ascending ?? false })
      }

      // Apply limit
      if (limit) {
        query = query.limit(limit)
      }

      const { data, error } = await query

      if (error) setError(error)
      else setData(data)
      setLoading(false)
    }
    fetch()
  }, [table, JSON.stringify(options)])

  return { data, loading, error }
}

// Usage
function MyComponent() {
  const { data: players, loading } = useSupabaseQuery('fact_player_stats_core', {
    select: 'player_name, total_points',
    order: { column: 'total_points' },
    limit: 10
  })

  if (loading) return <div>Loading...</div>
  return <ul>{players.map(p => <li key={p.player_name}>{p.player_name}: {p.total_points}</li>)}</ul>
}
```

---

## Charts & Visualizations

### Using Recharts

```bash
npm install recharts
```

```jsx
// components/GoalsChart.jsx
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export function GoalsChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <XAxis dataKey="player_name" />
        <YAxis />
        <Tooltip />
        <Bar dataKey="total_goals" fill="#0ea5e9" name="Goals" />
      </BarChart>
    </ResponsiveContainer>
  )
}
```

### Points Trend Line

```jsx
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export function PointsTrend({ playerId }) {
  const [games, setGames] = useState([])

  useEffect(() => {
    supabase
      .from('fact_player_game_stats')
      .select('game_id, points')
      .eq('player_id', playerId)
      .order('game_id')
      .then(({ data }) => {
        // Calculate cumulative points
        let cumulative = 0
        const trend = data.map(g => {
          cumulative += parseInt(g.points) || 0
          return { game: g.game_id, points: cumulative }
        })
        setGames(trend)
      })
  }, [playerId])

  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={games}>
        <XAxis dataKey="game" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="points" stroke="#10b981" />
      </LineChart>
    </ResponsiveContainer>
  )
}
```

---

## Data Tables Required

| Purpose | Table | Key Columns |
|---------|-------|-------------|
| Standings | fact_team_standings_snapshot | team_name, wins, losses, points |
| Scoring leaders | fact_player_stats_core | player_name, total_goals, total_assists, total_points |
| Recent games | dim_schedule | game_id, game_date_str, home/away_team_name, home/away_total_goals |
| Box score | fact_player_game_stats | player_name, goals, assists, shots, toi_minutes |
| Player info | dim_player | player_full_name, team_name, position, skill_rating |
| Team info | dim_team | team_name, division |

---

## Styling Tips

```css
/* Basic dashboard styles */
.standings-table {
  width: 100%;
  border-collapse: collapse;
}

.standings-table th,
.standings-table td {
  padding: 8px 12px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.standings-table tr:hover {
  background: #f3f4f6;
}

.game-card {
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin-bottom: 8px;
}

.winner {
  font-weight: bold;
  color: #059669;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  text-align: center;
}
```

---

## Performance Tips

1. **Limit queries** - Always use `.limit()` for leaderboards
2. **Select only needed columns** - Don't `select('*')` for large tables
3. **Cache data** - Use React Query or SWR for caching
4. **Paginate** - Use `.range()` for large result sets

```jsx
// Using React Query
import { useQuery } from '@tanstack/react-query'

function useStandings() {
  return useQuery({
    queryKey: ['standings'],
    queryFn: () => supabase.from('fact_team_standings_snapshot').select('*').order('points', { ascending: false }),
    staleTime: 60000 // Cache for 1 minute
  })
}
```
