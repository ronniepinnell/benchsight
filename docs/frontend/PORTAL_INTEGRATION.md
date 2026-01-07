# Portal Integration Guide

**For developers building the BenchSight league management portal**

---

## Overview

The Portal is the administrative interface for managing:
- Player rosters and profiles
- Team configurations
- Game scheduling
- Season management
- League-wide reports and analytics

**Data Source:** Supabase (read + write)  
**Tech Stack:** React recommended  
**Key Operations:** CRUD on dimension tables, reports

---

## Permissions Model

```
┌─────────────────────────────────────────────────────────┐
│                    PORTAL USERS                          │
├─────────────────┬─────────────────┬─────────────────────┤
│   League Admin  │   Team Manager  │      Viewer         │
│   (Full CRUD)   │  (Team only)    │   (Read only)       │
├─────────────────┼─────────────────┼─────────────────────┤
│ • All tables    │ • Own team      │ • All tables        │
│ • All teams     │ • Own players   │ • No writes         │
│ • Schedule      │ • Read others   │                     │
│ • Season config │                 │                     │
└─────────────────┴─────────────────┴─────────────────────┘
```

Note: Implement authorization in your app layer. Supabase Row Level Security (RLS) can enforce this at the database level.

---

## Quick Start

### 1. Initialize Supabase Client

```javascript
// lib/supabase.js
import { createClient } from '@supabase/supabase-js'

export const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
)
```

### 2. Basic CRUD Operations

```javascript
// Create
const { data, error } = await supabase
  .from('dim_player')
  .insert({ player_id: 'P999', player_full_name: 'New Player', ... })
  .select()

// Read
const { data } = await supabase
  .from('dim_player')
  .select('*')
  .eq('team_id', 'T001')

// Update
const { error } = await supabase
  .from('dim_player')
  .update({ skill_rating: '8' })
  .eq('player_id', 'P001')

// Delete (soft delete - set is_active = '0')
const { error } = await supabase
  .from('dim_player')
  .update({ is_active: '0' })
  .eq('player_id', 'P001')
```

---

## Player Management

### List All Players

```jsx
// components/PlayerList.jsx
import { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'

export function PlayerList() {
  const [players, setPlayers] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    fetchPlayers()
  }, [])

  async function fetchPlayers() {
    const { data, error } = await supabase
      .from('dim_player')
      .select(`
        player_id,
        player_full_name,
        jersey_number,
        primary_position,
        skill_rating,
        is_active,
        team_id,
        dim_team!team_id (team_name)
      `)
      .order('player_full_name')

    if (!error) setPlayers(data)
    setLoading(false)
  }

  const filteredPlayers = players.filter(p =>
    p.player_full_name.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div>
      <input
        type="text"
        placeholder="Search players..."
        value={search}
        onChange={e => setSearch(e.target.value)}
      />

      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Team</th>
            <th>#</th>
            <th>Pos</th>
            <th>Skill</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {filteredPlayers.map(player => (
            <tr key={player.player_id}>
              <td>{player.player_full_name}</td>
              <td>{player.dim_team?.team_name || 'Free Agent'}</td>
              <td>{player.jersey_number}</td>
              <td>{player.primary_position}</td>
              <td>{player.skill_rating}/10</td>
              <td>{player.is_active === '1' ? 'Active' : 'Inactive'}</td>
              <td>
                <button onClick={() => editPlayer(player)}>Edit</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
```

### Add/Edit Player Form

```jsx
// components/PlayerForm.jsx
export function PlayerForm({ player, teams, onSave, onCancel }) {
  const [form, setForm] = useState(player || {
    player_full_name: '',
    first_name: '',
    last_name: '',
    jersey_number: '',
    primary_position: 'C',
    skill_rating: '5',
    team_id: '',
    is_active: '1'
  })
  const [saving, setSaving] = useState(false)

  const handleChange = (field, value) => {
    setForm(prev => ({ ...prev, [field]: value }))
    
    // Auto-populate first/last from full name
    if (field === 'player_full_name') {
      const parts = value.trim().split(' ')
      if (parts.length >= 2) {
        setForm(prev => ({
          ...prev,
          first_name: parts[0],
          last_name: parts.slice(1).join(' ')
        }))
      }
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)

    try {
      if (player?.player_id) {
        // Update existing
        const { error } = await supabase
          .from('dim_player')
          .update(form)
          .eq('player_id', player.player_id)

        if (error) throw error
      } else {
        // Generate new player_id
        const newId = `P${Date.now()}`
        const { error } = await supabase
          .from('dim_player')
          .insert({ ...form, player_id: newId })

        if (error) throw error
      }

      onSave()
    } catch (err) {
      alert('Error saving player: ' + err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Full Name</label>
        <input
          value={form.player_full_name}
          onChange={e => handleChange('player_full_name', e.target.value)}
          required
        />
      </div>

      <div>
        <label>Team</label>
        <select
          value={form.team_id}
          onChange={e => handleChange('team_id', e.target.value)}
        >
          <option value="">Free Agent</option>
          {teams.map(t => (
            <option key={t.team_id} value={t.team_id}>{t.team_name}</option>
          ))}
        </select>
      </div>

      <div>
        <label>Jersey Number</label>
        <input
          type="number"
          value={form.jersey_number}
          onChange={e => handleChange('jersey_number', e.target.value)}
        />
      </div>

      <div>
        <label>Position</label>
        <select
          value={form.primary_position}
          onChange={e => handleChange('primary_position', e.target.value)}
        >
          <option value="C">Center</option>
          <option value="LW">Left Wing</option>
          <option value="RW">Right Wing</option>
          <option value="D">Defense</option>
          <option value="G">Goalie</option>
        </select>
      </div>

      <div>
        <label>Skill Rating (1-10)</label>
        <input
          type="range"
          min="1"
          max="10"
          value={form.skill_rating}
          onChange={e => handleChange('skill_rating', e.target.value)}
        />
        <span>{form.skill_rating}</span>
      </div>

      <div>
        <label>
          <input
            type="checkbox"
            checked={form.is_active === '1'}
            onChange={e => handleChange('is_active', e.target.checked ? '1' : '0')}
          />
          Active
        </label>
      </div>

      <div>
        <button type="submit" disabled={saving}>
          {saving ? 'Saving...' : 'Save Player'}
        </button>
        <button type="button" onClick={onCancel}>Cancel</button>
      </div>
    </form>
  )
}
```

---

## Team Management

### Team List with Roster Count

```jsx
// components/TeamList.jsx
export function TeamList() {
  const [teams, setTeams] = useState([])

  useEffect(() => {
    async function fetchTeams() {
      const { data } = await supabase
        .from('dim_team')
        .select(`
          *,
          dim_player!team_id (player_id)
        `)
        .order('team_name')

      // Add player count
      const teamsWithCounts = data.map(team => ({
        ...team,
        player_count: team.dim_player?.length || 0
      }))

      setTeams(teamsWithCounts)
    }
    fetchTeams()
  }, [])

  return (
    <div className="team-grid">
      {teams.map(team => (
        <div key={team.team_id} className="team-card">
          <h3>{team.team_name}</h3>
          <p>{team.team_short_name}</p>
          <p>Division: {team.division}</p>
          <p>Players: {team.player_count}</p>
          <p>Status: {team.is_active === '1' ? 'Active' : 'Inactive'}</p>
          <button onClick={() => viewRoster(team.team_id)}>View Roster</button>
          <button onClick={() => editTeam(team)}>Edit</button>
        </div>
      ))}
    </div>
  )
}
```

### Team Roster Management

```jsx
// components/TeamRoster.jsx
export function TeamRoster({ teamId }) {
  const [team, setTeam] = useState(null)
  const [players, setPlayers] = useState([])
  const [availablePlayers, setAvailablePlayers] = useState([])

  useEffect(() => {
    fetchData()
  }, [teamId])

  async function fetchData() {
    // Get team
    const { data: teamData } = await supabase
      .from('dim_team')
      .select('*')
      .eq('team_id', teamId)
      .single()

    // Get roster
    const { data: rosterData } = await supabase
      .from('dim_player')
      .select('*')
      .eq('team_id', teamId)
      .eq('is_active', '1')
      .order('jersey_number')

    // Get free agents
    const { data: freeAgents } = await supabase
      .from('dim_player')
      .select('*')
      .or('team_id.is.null,team_id.eq.')
      .eq('is_active', '1')

    setTeam(teamData)
    setPlayers(rosterData)
    setAvailablePlayers(freeAgents)
  }

  async function addToRoster(playerId) {
    await supabase
      .from('dim_player')
      .update({ team_id: teamId })
      .eq('player_id', playerId)

    fetchData()
  }

  async function removeFromRoster(playerId) {
    await supabase
      .from('dim_player')
      .update({ team_id: null })
      .eq('player_id', playerId)

    fetchData()
  }

  return (
    <div className="roster-manager">
      <h2>{team?.team_name} Roster</h2>

      <div className="current-roster">
        <h3>Current Players ({players.length})</h3>
        <ul>
          {players.map(p => (
            <li key={p.player_id}>
              #{p.jersey_number} {p.player_full_name} ({p.primary_position})
              <button onClick={() => removeFromRoster(p.player_id)}>Remove</button>
            </li>
          ))}
        </ul>
      </div>

      <div className="available-players">
        <h3>Available Free Agents</h3>
        <ul>
          {availablePlayers.map(p => (
            <li key={p.player_id}>
              {p.player_full_name} ({p.primary_position})
              <button onClick={() => addToRoster(p.player_id)}>Add</button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
```

---

## Schedule Management

### Schedule Calendar View

```jsx
// components/ScheduleCalendar.jsx
export function ScheduleCalendar() {
  const [games, setGames] = useState([])
  const [month, setMonth] = useState(new Date())

  useEffect(() => {
    fetchGames()
  }, [month])

  async function fetchGames() {
    const startOfMonth = new Date(month.getFullYear(), month.getMonth(), 1).toISOString().split('T')[0]
    const endOfMonth = new Date(month.getFullYear(), month.getMonth() + 1, 0).toISOString().split('T')[0]

    const { data } = await supabase
      .from('dim_schedule')
      .select('*')
      .gte('game_date_str', startOfMonth)
      .lte('game_date_str', endOfMonth)
      .order('game_date_str')

    setGames(data)
  }

  return (
    <div>
      <div className="month-nav">
        <button onClick={() => setMonth(prev => new Date(prev.getFullYear(), prev.getMonth() - 1))}>
          Previous
        </button>
        <h2>{month.toLocaleString('default', { month: 'long', year: 'numeric' })}</h2>
        <button onClick={() => setMonth(prev => new Date(prev.getFullYear(), prev.getMonth() + 1))}>
          Next
        </button>
      </div>

      <div className="games-list">
        {games.map(game => (
          <div key={game.game_id} className={`game-item ${game.game_status}`}>
            <span className="date">{game.game_date_str}</span>
            <span className="matchup">
              {game.away_team_name} @ {game.home_team_name}
            </span>
            {game.game_status === 'completed' && (
              <span className="score">
                {game.away_total_goals} - {game.home_total_goals}
              </span>
            )}
            <span className="status">{game.game_status}</span>
            <button onClick={() => editGame(game)}>Edit</button>
          </div>
        ))}
      </div>

      <button onClick={() => addGame()}>Add Game</button>
    </div>
  )
}
```

### Add/Edit Game Form

```jsx
// components/GameForm.jsx
export function GameForm({ game, teams, venues, onSave, onCancel }) {
  const [form, setForm] = useState(game || {
    game_date_str: '',
    game_time: '19:30',
    home_team_id: '',
    away_team_id: '',
    venue_id: '',
    game_status: 'scheduled'
  })

  const handleSubmit = async (e) => {
    e.preventDefault()

    // Populate team names
    const homeTeam = teams.find(t => t.team_id === form.home_team_id)
    const awayTeam = teams.find(t => t.team_id === form.away_team_id)
    const venue = venues.find(v => v.venue_id === form.venue_id)

    const gameData = {
      ...form,
      home_team_name: homeTeam?.team_name,
      away_team_name: awayTeam?.team_name,
      venue_name: venue?.venue_name
    }

    if (game?.game_id) {
      // Update
      await supabase
        .from('dim_schedule')
        .update(gameData)
        .eq('game_id', game.game_id)
    } else {
      // Insert with new ID
      await supabase
        .from('dim_schedule')
        .insert({
          ...gameData,
          game_id: `G${Date.now()}`
        })
    }

    onSave()
  }

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Date</label>
        <input
          type="date"
          value={form.game_date_str}
          onChange={e => setForm({ ...form, game_date_str: e.target.value })}
          required
        />
      </div>

      <div>
        <label>Time</label>
        <input
          type="time"
          value={form.game_time}
          onChange={e => setForm({ ...form, game_time: e.target.value })}
        />
      </div>

      <div>
        <label>Home Team</label>
        <select
          value={form.home_team_id}
          onChange={e => setForm({ ...form, home_team_id: e.target.value })}
          required
        >
          <option value="">Select team...</option>
          {teams.map(t => (
            <option key={t.team_id} value={t.team_id}>{t.team_name}</option>
          ))}
        </select>
      </div>

      <div>
        <label>Away Team</label>
        <select
          value={form.away_team_id}
          onChange={e => setForm({ ...form, away_team_id: e.target.value })}
          required
        >
          <option value="">Select team...</option>
          {teams.filter(t => t.team_id !== form.home_team_id).map(t => (
            <option key={t.team_id} value={t.team_id}>{t.team_name}</option>
          ))}
        </select>
      </div>

      <div>
        <label>Venue</label>
        <select
          value={form.venue_id}
          onChange={e => setForm({ ...form, venue_id: e.target.value })}
        >
          <option value="">Select venue...</option>
          {venues.map(v => (
            <option key={v.venue_id} value={v.venue_id}>{v.venue_name}</option>
          ))}
        </select>
      </div>

      <div>
        <label>Status</label>
        <select
          value={form.game_status}
          onChange={e => setForm({ ...form, game_status: e.target.value })}
        >
          <option value="scheduled">Scheduled</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
          <option value="postponed">Postponed</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>

      {form.game_status === 'completed' && (
        <>
          <div>
            <label>Home Score</label>
            <input
              type="number"
              value={form.home_total_goals || ''}
              onChange={e => setForm({ ...form, home_total_goals: e.target.value })}
            />
          </div>
          <div>
            <label>Away Score</label>
            <input
              type="number"
              value={form.away_total_goals || ''}
              onChange={e => setForm({ ...form, away_total_goals: e.target.value })}
            />
          </div>
        </>
      )}

      <button type="submit">Save</button>
      <button type="button" onClick={onCancel}>Cancel</button>
    </form>
  )
}
```

---

## Reports & Analytics

### League Summary Dashboard

```jsx
// components/LeagueDashboard.jsx
export function LeagueDashboard() {
  const [stats, setStats] = useState(null)

  useEffect(() => {
    async function fetchStats() {
      const [teams, players, games] = await Promise.all([
        supabase.from('dim_team').select('team_id').eq('is_active', '1'),
        supabase.from('dim_player').select('player_id').eq('is_active', '1'),
        supabase.from('dim_schedule').select('game_id, game_status')
      ])

      setStats({
        totalTeams: teams.data.length,
        totalPlayers: players.data.length,
        completedGames: games.data.filter(g => g.game_status === 'completed').length,
        scheduledGames: games.data.filter(g => g.game_status === 'scheduled').length
      })
    }
    fetchStats()
  }, [])

  if (!stats) return <div>Loading...</div>

  return (
    <div className="dashboard-grid">
      <div className="stat-card">
        <h3>Teams</h3>
        <div className="value">{stats.totalTeams}</div>
      </div>
      <div className="stat-card">
        <h3>Players</h3>
        <div className="value">{stats.totalPlayers}</div>
      </div>
      <div className="stat-card">
        <h3>Games Played</h3>
        <div className="value">{stats.completedGames}</div>
      </div>
      <div className="stat-card">
        <h3>Upcoming Games</h3>
        <div className="value">{stats.scheduledGames}</div>
      </div>
    </div>
  )
}
```

### Data Export

```jsx
// components/DataExport.jsx
export function DataExport() {
  const [exporting, setExporting] = useState(false)

  async function exportTable(tableName) {
    setExporting(true)

    const { data } = await supabase
      .from(tableName)
      .select('*')

    // Convert to CSV
    if (data.length === 0) {
      alert('No data to export')
      setExporting(false)
      return
    }

    const headers = Object.keys(data[0])
    const csv = [
      headers.join(','),
      ...data.map(row => headers.map(h => JSON.stringify(row[h] || '')).join(','))
    ].join('\n')

    // Download
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${tableName}_export.csv`
    a.click()

    setExporting(false)
  }

  return (
    <div>
      <h2>Export Data</h2>
      <button onClick={() => exportTable('dim_player')} disabled={exporting}>
        Export Players
      </button>
      <button onClick={() => exportTable('dim_team')} disabled={exporting}>
        Export Teams
      </button>
      <button onClick={() => exportTable('dim_schedule')} disabled={exporting}>
        Export Schedule
      </button>
      <button onClick={() => exportTable('fact_player_stats_core')} disabled={exporting}>
        Export Player Stats
      </button>
    </div>
  )
}
```

---

## Tables Reference

### Read/Write Tables (Portal manages these)

| Table | Operations | Purpose |
|-------|------------|---------|
| dim_player | CRUD | Player roster management |
| dim_team | CRUD | Team configuration |
| dim_schedule | CRUD | Game scheduling |
| dim_season | CRUD | Season configuration |
| dim_venue | CRUD | Venue management |

### Read-Only Tables (ETL populates these)

| Table | Purpose |
|-------|---------|
| fact_player_game_stats | Per-game stats |
| fact_team_game_stats | Team per-game stats |
| fact_team_standings_snapshot | Current standings |
| fact_events | Play-by-play |

---

## Validation Rules

```javascript
// lib/validation.js

export function validatePlayer(player) {
  const errors = []

  if (!player.player_full_name?.trim()) {
    errors.push('Name is required')
  }

  if (player.jersey_number && (player.jersey_number < 0 || player.jersey_number > 99)) {
    errors.push('Jersey number must be 0-99')
  }

  if (player.skill_rating && (player.skill_rating < 1 || player.skill_rating > 10)) {
    errors.push('Skill rating must be 1-10')
  }

  const validPositions = ['C', 'LW', 'RW', 'D', 'G']
  if (player.primary_position && !validPositions.includes(player.primary_position)) {
    errors.push('Invalid position')
  }

  return errors
}

export function validateGame(game) {
  const errors = []

  if (!game.game_date_str) {
    errors.push('Date is required')
  }

  if (!game.home_team_id) {
    errors.push('Home team is required')
  }

  if (!game.away_team_id) {
    errors.push('Away team is required')
  }

  if (game.home_team_id === game.away_team_id) {
    errors.push('Home and away teams must be different')
  }

  return errors
}
```

---

## Error Handling

```javascript
// lib/api.js
export async function safeUpdate(table, data, match) {
  try {
    const { data: result, error } = await supabase
      .from(table)
      .update(data)
      .match(match)
      .select()

    if (error) {
      console.error(`Error updating ${table}:`, error)
      return { success: false, error: error.message }
    }

    return { success: true, data: result }
  } catch (err) {
    console.error(`Exception updating ${table}:`, err)
    return { success: false, error: err.message }
  }
}

// Usage
const result = await safeUpdate('dim_player', { skill_rating: '8' }, { player_id: 'P001' })
if (!result.success) {
  alert('Update failed: ' + result.error)
}
```
