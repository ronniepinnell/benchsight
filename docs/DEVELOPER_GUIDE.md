# BenchSight Developer Guide

**For Dashboard, Tracker, and Portal Developers**

Last Updated: December 31, 2025 | Version 16.1

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [Data Access Methods](#data-access-methods)
4. [Key Data Models](#key-data-models)
5. [Common Operations](#common-operations)
6. [Frontend Integration](#frontend-integration)

---

## Quick Start

### Option 1: Direct Supabase Access (Recommended for Read-Only)

```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  'YOUR_SUPABASE_URL',
  'YOUR_SUPABASE_ANON_KEY'
)

// Get all players
const { data: players } = await supabase
  .from('dim_player')
  .select('*')

// Get game stats
const { data: stats } = await supabase
  .from('fact_player_game_stats')
  .select('*')
  .eq('game_id', '18969')
```

### Option 2: ETL API (For Processing/Uploads)

```javascript
const API = 'http://localhost:5000/api'

// Check health
const health = await fetch(`${API}/health`).then(r => r.json())

// Process a game
await fetch(`${API}/games/18969/process`, { method: 'POST' })

// Upload tracking file
const formData = new FormData()
formData.append('file', file)
await fetch(`${API}/upload`, { method: 'POST', body: formData })
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND APPS                                │
├─────────────────┬─────────────────┬─────────────────────────────────┤
│    TRACKER      │    DASHBOARD    │           PORTAL                │
│  (Data Entry)   │  (Visualization)│      (League Management)        │
└────────┬────────┴────────┬────────┴─────────────┬───────────────────┘
         │                 │                       │
         ▼                 ▼                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DATA ACCESS LAYER                               │
├─────────────────────────────────┬───────────────────────────────────┤
│         ETL API                 │         SUPABASE                  │
│    (localhost:5000)             │     (PostgreSQL + REST)           │
│                                 │                                   │
│  • Process games                │  • Read all tables                │
│  • Upload files                 │  • Real-time subscriptions        │
│  • Trigger exports              │  • Direct SQL queries             │
└─────────────────────────────────┴───────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA WAREHOUSE                                │
│                       (111 Tables)                                   │
├───────────────────┬───────────────────┬─────────────────────────────┤
│   DIMENSIONS (48) │    FACTS (58)     │      SUPPORT (5)            │
│   dim_player      │   fact_events     │   etl_run_log               │
│   dim_team        │   fact_shifts     │   qa_goal_accuracy          │
│   dim_schedule    │   fact_stats      │   qa_validation_log         │
└───────────────────┴───────────────────┴─────────────────────────────┘
```

---

## Data Access Methods

### Method 1: Supabase JavaScript Client

**Best for:** Dashboard, Portal (read-heavy operations)

```bash
npm install @supabase/supabase-js
```

```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

// Basic query
const { data, error } = await supabase
  .from('dim_player')
  .select('*')

// With filters
const { data } = await supabase
  .from('fact_player_game_stats')
  .select('player_name, goals, assists, points')
  .eq('game_id', '18969')
  .order('points', { ascending: false })

// Join tables
const { data } = await supabase
  .from('fact_events')
  .select(`
    *,
    dim_player!player_id (player_full_name),
    dim_team!team_id (team_name)
  `)
  .eq('game_id', '18969')
```

### Method 2: Supabase REST API

**Best for:** Simple fetches, no SDK needed

```javascript
const SUPABASE_URL = 'https://xxx.supabase.co'
const SUPABASE_KEY = 'your-anon-key'

// GET request
const response = await fetch(
  `${SUPABASE_URL}/rest/v1/dim_player?select=*`,
  {
    headers: {
      'apikey': SUPABASE_KEY,
      'Authorization': `Bearer ${SUPABASE_KEY}`
    }
  }
)
const players = await response.json()

// With filters (PostgREST syntax)
const url = `${SUPABASE_URL}/rest/v1/fact_player_game_stats?game_id=eq.18969&order=points.desc`
```

### Method 3: ETL API

**Best for:** Tracker (uploads, processing)

```javascript
const ETL_API = 'http://localhost:5000/api'

// Upload tracking file
async function uploadTrackingFile(file, gameId) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('game_id', gameId)
  
  const response = await fetch(`${ETL_API}/upload`, {
    method: 'POST',
    body: formData
  })
  return response.json()
}

// Process game after upload
async function processGame(gameId) {
  const response = await fetch(`${ETL_API}/games/${gameId}/process`, {
    method: 'POST'
  })
  return response.json()
}

// Get processing status
async function getStatus() {
  const response = await fetch(`${ETL_API}/status`)
  return response.json()
}
```

---

## Key Data Models

### Players

**Table:** `dim_player`

| Column | Type | Description |
|--------|------|-------------|
| player_id | TEXT | Primary key (e.g., "P001") |
| player_full_name | TEXT | Full name |
| first_name | TEXT | First name |
| last_name | TEXT | Last name |
| skill_rating | TEXT | 1-10 rating |
| primary_position | TEXT | C, LW, RW, D, G |
| team_id | TEXT | Current team FK |
| jersey_number | TEXT | Jersey number |
| is_active | TEXT | "1" or "0" |

**Common Queries:**
```javascript
// All active players
const { data } = await supabase
  .from('dim_player')
  .select('*')
  .eq('is_active', '1')

// Players on a team
const { data } = await supabase
  .from('dim_player')
  .select('*')
  .eq('team_id', 'T001')

// Search by name
const { data } = await supabase
  .from('dim_player')
  .select('*')
  .ilike('player_full_name', '%smith%')
```

### Teams

**Table:** `dim_team`

| Column | Type | Description |
|--------|------|-------------|
| team_id | TEXT | Primary key |
| team_name | TEXT | Full team name |
| team_short_name | TEXT | Abbreviation |
| division | TEXT | Division name |
| is_active | TEXT | "1" or "0" |

### Games/Schedule

**Table:** `dim_schedule`

| Column | Type | Description |
|--------|------|-------------|
| game_id | TEXT | Primary key |
| game_date_str | TEXT | Date string |
| season_id | TEXT | Season FK |
| home_team_id | TEXT | Home team FK |
| away_team_id | TEXT | Away team FK |
| home_team_name | TEXT | Home team name |
| away_team_name | TEXT | Away team name |
| home_total_goals | TEXT | Final home score |
| away_total_goals | TEXT | Final away score |
| venue_id | TEXT | Venue FK |
| game_status | TEXT | "completed", "scheduled" |

**Common Queries:**
```javascript
// Recent games
const { data } = await supabase
  .from('dim_schedule')
  .select('*')
  .eq('game_status', 'completed')
  .order('game_date_str', { ascending: false })
  .limit(10)

// Games for a team
const { data } = await supabase
  .from('dim_schedule')
  .select('*')
  .or(`home_team_id.eq.T001,away_team_id.eq.T001`)
```

### Events (Play-by-Play)

**Table:** `fact_events`

| Column | Type | Description |
|--------|------|-------------|
| event_key | TEXT | Primary key |
| game_id | TEXT | Game FK |
| event_index | TEXT | Event sequence number |
| period | TEXT | 1, 2, 3, OT |
| event_time | TEXT | MM:SS format |
| event_type | TEXT | "Shot", "Goal", "Faceoff", etc. |
| event_detail | TEXT | Additional detail |
| team_id | TEXT | Team FK |
| zone | TEXT | "offensive", "defensive", "neutral" |
| x_coord | TEXT | Rink X coordinate |
| y_coord | TEXT | Rink Y coordinate |

**Table:** `fact_events_player` (Player involvement in events)

| Column | Type | Description |
|--------|------|-------------|
| event_player_key | TEXT | Primary key |
| event_key | TEXT | Event FK |
| game_id | TEXT | Game FK |
| player_id | TEXT | Player FK |
| player_role | TEXT | "scorer", "assist1", "assist2", "goalie" |
| is_primary | TEXT | "1" if primary player |

**Common Queries:**
```javascript
// All goals in a game
const { data } = await supabase
  .from('fact_events')
  .select('*')
  .eq('game_id', '18969')
  .eq('event_type', 'Goal')

// Events with player details
const { data } = await supabase
  .from('fact_events_player')
  .select(`
    *,
    fact_events!event_key (*),
    dim_player!player_id (player_full_name)
  `)
  .eq('game_id', '18969')
```

### Player Game Stats

**Table:** `fact_player_game_stats`

| Column | Type | Description |
|--------|------|-------------|
| player_game_key | TEXT | Primary key |
| game_id | TEXT | Game FK |
| player_id | TEXT | Player FK |
| player_name | TEXT | Player name |
| team_id | TEXT | Team FK |
| goals | TEXT | Goals scored |
| assists | TEXT | Assists |
| points | TEXT | Total points |
| shots | TEXT | Shots on goal |
| shots_missed | TEXT | Missed shots |
| blocked_shots | TEXT | Blocked shots |
| hits | TEXT | Hits |
| takeaways | TEXT | Takeaways |
| giveaways | TEXT | Giveaways |
| faceoff_wins | TEXT | Faceoffs won |
| faceoff_losses | TEXT | Faceoffs lost |
| toi_seconds | TEXT | Time on ice (seconds) |
| toi_minutes | TEXT | Time on ice (minutes) |
| plus_minus | TEXT | Plus/minus |
| pim | TEXT | Penalty minutes |

**Common Queries:**
```javascript
// Game leaders
const { data } = await supabase
  .from('fact_player_game_stats')
  .select('*')
  .eq('game_id', '18969')
  .order('points', { ascending: false })

// Season totals (aggregate yourself or use fact_player_stats_core)
const { data } = await supabase
  .from('fact_player_stats_core')
  .select('*')
  .order('total_points', { ascending: false })
```

### Shifts

**Table:** `fact_shifts`

| Column | Type | Description |
|--------|------|-------------|
| shift_key | TEXT | Primary key |
| game_id | TEXT | Game FK |
| player_id | TEXT | Player FK |
| period | TEXT | Period number |
| shift_number | TEXT | Shift sequence |
| start_time | TEXT | Shift start (MM:SS) |
| end_time | TEXT | Shift end (MM:SS) |
| duration_seconds | TEXT | Shift length |

---

## Common Operations

### Get Box Score for a Game

```javascript
async function getBoxScore(gameId) {
  // Get game info
  const { data: game } = await supabase
    .from('dim_schedule')
    .select('*')
    .eq('game_id', gameId)
    .single()

  // Get player stats
  const { data: playerStats } = await supabase
    .from('fact_player_game_stats')
    .select('*')
    .eq('game_id', gameId)
    .order('points', { ascending: false })

  // Get team stats
  const { data: teamStats } = await supabase
    .from('fact_team_game_stats')
    .select('*')
    .eq('game_id', gameId)

  return { game, playerStats, teamStats }
}
```

### Get Player Career Stats

```javascript
async function getPlayerCareer(playerId) {
  // Get player info
  const { data: player } = await supabase
    .from('dim_player')
    .select('*')
    .eq('player_id', playerId)
    .single()

  // Get all game stats
  const { data: gameStats } = await supabase
    .from('fact_player_game_stats')
    .select('*')
    .eq('player_id', playerId)
    .order('game_id', { ascending: false })

  // Calculate totals
  const totals = gameStats.reduce((acc, game) => ({
    games: acc.games + 1,
    goals: acc.goals + parseInt(game.goals || 0),
    assists: acc.assists + parseInt(game.assists || 0),
    points: acc.points + parseInt(game.points || 0)
  }), { games: 0, goals: 0, assists: 0, points: 0 })

  return { player, gameStats, totals }
}
```

### Get Live Game Events

```javascript
async function getGameEvents(gameId) {
  const { data } = await supabase
    .from('fact_events')
    .select(`
      *,
      fact_events_player (
        player_id,
        player_role,
        dim_player (player_full_name)
      )
    `)
    .eq('game_id', gameId)
    .order('period')
    .order('event_index')

  return data
}
```

### Get League Standings

```javascript
async function getStandings() {
  const { data } = await supabase
    .from('fact_team_standings_snapshot')
    .select('*')
    .order('points', { ascending: false })

  return data
}
```

### Upload and Process Game (Tracker)

```javascript
async function uploadAndProcess(file, gameId) {
  const ETL_API = 'http://localhost:5000/api'

  // 1. Upload file
  const formData = new FormData()
  formData.append('file', file)
  formData.append('game_id', gameId)

  const uploadResult = await fetch(`${ETL_API}/upload`, {
    method: 'POST',
    body: formData
  }).then(r => r.json())

  if (!uploadResult.success) {
    throw new Error(uploadResult.error)
  }

  // 2. Process game
  const processResult = await fetch(`${ETL_API}/games/${gameId}/process`, {
    method: 'POST'
  }).then(r => r.json())

  return processResult
}
```

---

## Frontend Integration

### Dashboard Integration

The dashboard reads from Supabase to display:
- League standings
- Player leaderboards
- Game summaries
- Team statistics

**Key tables:**
- `dim_schedule` - Game list and scores
- `fact_player_game_stats` - Player box scores
- `fact_team_game_stats` - Team statistics
- `fact_player_stats_core` - Season aggregates

**Example: Leaderboard Component**

```jsx
function Leaderboard() {
  const [players, setPlayers] = useState([])

  useEffect(() => {
    async function load() {
      const { data } = await supabase
        .from('fact_player_stats_core')
        .select('player_id, player_name, total_goals, total_assists, total_points')
        .order('total_points', { ascending: false })
        .limit(10)
      setPlayers(data)
    }
    load()
  }, [])

  return (
    <table>
      <thead>
        <tr><th>Player</th><th>G</th><th>A</th><th>P</th></tr>
      </thead>
      <tbody>
        {players.map(p => (
          <tr key={p.player_id}>
            <td>{p.player_name}</td>
            <td>{p.total_goals}</td>
            <td>{p.total_assists}</td>
            <td>{p.total_points}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
```

### Tracker Integration

The tracker writes game events and uploads files:
- Record play-by-play events
- Track shifts and line changes
- Upload completed game files
- Trigger ETL processing

**Key endpoints:**
- `POST /api/upload` - Upload tracking file
- `POST /api/games/{id}/process` - Process uploaded game
- `GET /api/status` - Check processing status

**Example: Upload Component**

```jsx
function GameUploader({ gameId }) {
  const [status, setStatus] = useState('idle')

  async function handleUpload(e) {
    const file = e.target.files[0]
    setStatus('uploading')

    try {
      // Upload
      const formData = new FormData()
      formData.append('file', file)
      formData.append('game_id', gameId)

      await fetch('http://localhost:5000/api/upload', {
        method: 'POST',
        body: formData
      })

      setStatus('processing')

      // Process
      await fetch(`http://localhost:5000/api/games/${gameId}/process`, {
        method: 'POST'
      })

      setStatus('complete')
    } catch (err) {
      setStatus('error')
    }
  }

  return (
    <div>
      <input type="file" onChange={handleUpload} accept=".xlsx,.csv" />
      <p>Status: {status}</p>
    </div>
  )
}
```

### Portal Integration

The portal manages league data:
- View/edit player rosters
- Manage team information
- Schedule games
- View league-wide reports

**Key tables:**
- `dim_player` - Player management
- `dim_team` - Team management
- `dim_schedule` - Game scheduling
- `dim_season` - Season configuration

**Example: Player Editor**

```jsx
function PlayerEditor({ playerId }) {
  const [player, setPlayer] = useState(null)

  useEffect(() => {
    supabase
      .from('dim_player')
      .select('*')
      .eq('player_id', playerId)
      .single()
      .then(({ data }) => setPlayer(data))
  }, [playerId])

  async function handleSave() {
    const { error } = await supabase
      .from('dim_player')
      .update({
        skill_rating: player.skill_rating,
        primary_position: player.primary_position
      })
      .eq('player_id', playerId)

    if (error) alert('Save failed')
    else alert('Saved!')
  }

  if (!player) return <div>Loading...</div>

  return (
    <form onSubmit={e => { e.preventDefault(); handleSave() }}>
      <label>
        Name: <input value={player.player_full_name} disabled />
      </label>
      <label>
        Skill Rating:
        <input
          type="number"
          min="1"
          max="10"
          value={player.skill_rating}
          onChange={e => setPlayer({...player, skill_rating: e.target.value})}
        />
      </label>
      <label>
        Position:
        <select
          value={player.primary_position}
          onChange={e => setPlayer({...player, primary_position: e.target.value})}
        >
          <option value="C">Center</option>
          <option value="LW">Left Wing</option>
          <option value="RW">Right Wing</option>
          <option value="D">Defense</option>
          <option value="G">Goalie</option>
        </select>
      </label>
      <button type="submit">Save</button>
    </form>
  )
}
```

---

## Additional Resources

- [API Documentation](./API_DOCUMENTATION.md) - Full ETL API reference
- [ETL Architecture](./ETL_ARCHITECTURE.md) - How data processing works
- [Data Dictionary](./DATA_DICTIONARY_COMPLETE.md) - All columns documented
- [Table Inventory](./TABLE_INVENTORY.csv) - All 111 tables listed
- [Supabase Docs](https://supabase.com/docs) - Supabase reference

---

## Support

**Config files:** `config/config_local.ini` (Supabase credentials)

**ETL API:** `python -m src.api.server`

**Test connection:**
```bash
curl http://localhost:5000/api/health
```
