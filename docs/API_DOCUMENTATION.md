# BenchSight API Documentation

**Base URL**: `http://localhost:5000/api`  
**Version**: 16.1  
**Content-Type**: `application/json`

---

## Quick Start

### 1. Start the API Server

```bash
# Install dependencies
pip install -r requirements.txt

# Start server
python -m src.api.server

# Or with options
python -m src.api.server --host 0.0.0.0 --port 8080 --debug
```

### 2. Test Connection

```bash
curl http://localhost:5000/api/health
```

### 3. JavaScript Example

```javascript
const API_BASE = 'http://localhost:5000/api';

// Health check
const health = await fetch(`${API_BASE}/health`).then(r => r.json());
console.log(health.data.status); // "healthy"

// Get player stats
const stats = await fetch(`${API_BASE}/stats/players?limit=10`).then(r => r.json());
console.log(stats.data.players);
```

---

## Response Format

All endpoints return JSON with this structure:

```json
{
  "success": true,
  "timestamp": "2025-12-31T19:15:00.000000",
  "data": { ... }
}
```

On error:

```json
{
  "success": false,
  "timestamp": "2025-12-31T19:15:00.000000",
  "error": "Error message here"
}
```

---

## Endpoints

### Health & Status

#### `GET /api/health`
Health check - verify API is running.

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "database": "connected",
    "version": "16.1"
  }
}
```

#### `GET /api/status`
Get pipeline status including table counts and game processing status.

**Response:**
```json
{
  "success": true,
  "data": {
    "tables": {
      "stage": 15,
      "intermediate": 20,
      "datamart": 111
    },
    "games": {
      "available": 25,
      "processed": 20,
      "unprocessed": 5
    },
    "last_export": "2025-12-31T18:00:00"
  }
}
```

---

### Games

#### `GET /api/games`
List all games with their processing status.

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| status | string | "all" | Filter: "all", "available", "processed", "unprocessed" |

**Response:**
```json
{
  "success": true,
  "data": {
    "games": [
      {"game_id": 18969, "status": "processed"},
      {"game_id": 18970, "status": "available"}
    ],
    "total": 25
  }
}
```

#### `GET /api/games/available`
List games available for processing (have tracking files).

#### `GET /api/games/processed`
List games that have been processed.

#### `GET /api/games/unprocessed`
List games available but not yet processed.

#### `GET /api/games/<game_id>`
Get details for a specific game.

**Response:**
```json
{
  "success": true,
  "data": {
    "game_id": 18969,
    "status": "processed",
    "has_tracking_file": true,
    "date": "2025-01-15",
    "home_team": "Ice Dogs",
    "away_team": "Polar Bears",
    "home_goals": "5",
    "away_goals": "3"
  }
}
```

---

### Processing

#### `POST /api/games/<game_id>/process`
Process a single game.

**Request Body (optional):**
```json
{
  "force": true  // Reprocess even if already done
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "game_id": 18969,
    "processed": true,
    "result": {
      "stages": { ... },
      "duration_seconds": 12.5
    }
  }
}
```

#### `POST /api/process`
Process multiple games.

**Request Body:**
```json
{
  "game_ids": [18969, 18970, 18971],  // Specific games
  "all_unprocessed": false,           // Or process all unprocessed
  "force": false                      // Force reprocess
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "requested": [18969, 18970, 18971],
    "result": {
      "games_processed": [18969, 18970, 18971],
      "errors": [],
      "duration_seconds": 45.2
    }
  }
}
```

#### `POST /api/process/full`
Run the complete ETL pipeline (BLB + all games + export).

**Request Body (optional):**
```json
{
  "reload_blb": false,   // Force reload reference data
  "export_csv": true     // Export to CSV after processing
}
```

---

### File Upload

#### `POST /api/upload`
Upload a game tracking file.

**Request:** `multipart/form-data`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| file | File | Yes | xlsx, xls, or csv file |
| game_id | string | No | Associate file with game |

**Example (JavaScript):**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('game_id', '18969');

const response = await fetch(`${API_BASE}/upload`, {
  method: 'POST',
  body: formData
});
```

**Response:**
```json
{
  "success": true,
  "data": {
    "filename": "18969_tracking.xlsx",
    "path": "/data/raw/uploads/18969_tracking.xlsx",
    "size": 245760,
    "game_id": "18969"
  }
}
```

---

### Export

#### `GET /api/export` or `POST /api/export`
Trigger CSV export of all datamart tables.

**Response:**
```json
{
  "success": true,
  "data": {
    "tables_exported": 111,
    "output_dir": "/home/user/benchsight/data/output",
    "timestamp": "2025-12-31T19:15:00"
  }
}
```

---

### Tables

#### `GET /api/tables`
List all exported tables with metadata.

**Response:**
```json
{
  "success": true,
  "data": {
    "tables": [
      {"name": "dim_player", "columns": 28, "rows": 450, "category": "dim"},
      {"name": "fact_events", "columns": 54, "rows": 15000, "category": "fact"}
    ],
    "total": 111
  }
}
```

#### `GET /api/tables/<table_name>`
Get data from a specific table (paginated).

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| limit | int | 100 | Max rows (max 1000) |
| offset | int | 0 | Rows to skip |
| columns | string | all | Comma-separated column names |

**Example:**
```
GET /api/tables/dim_player?limit=10&columns=player_id,player_full_name,skill_rating
```

**Response:**
```json
{
  "success": true,
  "data": {
    "table": "dim_player",
    "columns": ["player_id", "player_full_name", "skill_rating"],
    "rows": [
      {"player_id": "P001", "player_full_name": "John Smith", "skill_rating": "7"},
      ...
    ],
    "total_rows": 450,
    "limit": 10,
    "offset": 0,
    "has_more": true
  }
}
```

#### `GET /api/tables/<table_name>/download`
Download table as CSV file.

---

### Stats (Dashboard Helpers)

#### `GET /api/stats/players`
Get player statistics (optimized for dashboards).

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| game_id | string | Filter by game |
| player_id | string | Filter by player |
| limit | int | Max rows (default 50) |

**Response:**
```json
{
  "success": true,
  "data": {
    "players": [
      {
        "player_game_key": "PGK18969_P001",
        "game_id": "18969",
        "player_id": "P001",
        "player_name": "John Smith",
        "goals": "2",
        "assists": "1",
        "points": "3",
        "shots": "5",
        "toi_minutes": "18.5"
      }
    ],
    "count": 1
  }
}
```

#### `GET /api/stats/teams`
Get team statistics.

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| game_id | string | Filter by game |

---

## Error Codes

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Resource doesn't exist |
| 500 | Server Error - Something went wrong |

---

## CORS

CORS is enabled for all origins. You can call the API from any domain.

---

## Rate Limits

No rate limits are enforced, but processing endpoints are synchronous and will block until complete.

For long-running operations (processing multiple games), consider:
1. Processing in smaller batches
2. Implementing client-side polling for status

---

## JavaScript Client Example

```javascript
class BenchSightAPI {
  constructor(baseUrl = 'http://localhost:5000/api') {
    this.baseUrl = baseUrl;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      headers: { 'Content-Type': 'application/json' },
      ...options
    });
    const data = await response.json();
    if (!data.success) throw new Error(data.error);
    return data.data;
  }

  // Health
  health() { return this.request('/health'); }
  status() { return this.request('/status'); }

  // Games
  listGames(status = 'all') { 
    return this.request(`/games?status=${status}`); 
  }
  
  getGame(gameId) { 
    return this.request(`/games/${gameId}`); 
  }
  
  processGame(gameId, force = false) {
    return this.request(`/games/${gameId}/process`, {
      method: 'POST',
      body: JSON.stringify({ force })
    });
  }

  // Tables
  listTables() { return this.request('/tables'); }
  
  getTable(name, limit = 100, offset = 0) {
    return this.request(`/tables/${name}?limit=${limit}&offset=${offset}`);
  }

  // Stats
  getPlayerStats(gameId = null, limit = 50) {
    const params = new URLSearchParams({ limit });
    if (gameId) params.set('game_id', gameId);
    return this.request(`/stats/players?${params}`);
  }

  // Upload
  async uploadFile(file, gameId = null) {
    const formData = new FormData();
    formData.append('file', file);
    if (gameId) formData.append('game_id', gameId);
    
    const response = await fetch(`${this.baseUrl}/upload`, {
      method: 'POST',
      body: formData
    });
    const data = await response.json();
    if (!data.success) throw new Error(data.error);
    return data.data;
  }
}

// Usage
const api = new BenchSightAPI();

// Get all games
const games = await api.listGames();

// Process a game
await api.processGame(18969);

// Get player stats for a game
const stats = await api.getPlayerStats(18969);

// Upload tracking file
const fileInput = document.querySelector('input[type="file"]');
await api.uploadFile(fileInput.files[0], '18969');
```

---

## React Hook Example

```jsx
import { useState, useEffect } from 'react';

const API_BASE = 'http://localhost:5000/api';

function usePlayerStats(gameId) {
  const [stats, setStats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const params = gameId ? `?game_id=${gameId}` : '';
        const response = await fetch(`${API_BASE}/stats/players${params}`);
        const data = await response.json();
        if (data.success) {
          setStats(data.data.players);
        } else {
          setError(data.error);
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [gameId]);

  return { stats, loading, error };
}

// Usage
function PlayerStatsTable({ gameId }) {
  const { stats, loading, error } = usePlayerStats(gameId);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <table>
      <thead>
        <tr>
          <th>Player</th>
          <th>Goals</th>
          <th>Assists</th>
          <th>Points</th>
        </tr>
      </thead>
      <tbody>
        {stats.map(player => (
          <tr key={player.player_game_key}>
            <td>{player.player_name}</td>
            <td>{player.goals}</td>
            <td>{player.assists}</td>
            <td>{player.points}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

---

## Deployment

### Local Development
```bash
python -m src.api.server --debug
```

### Production (Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 'src.api.server:app'
```

### Docker
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt gunicorn
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "src.api.server:app"]
```

### Railway/Render
1. Connect GitHub repo
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `gunicorn -w 2 -b 0.0.0.0:$PORT src.api.server:app`
