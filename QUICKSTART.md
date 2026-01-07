# BenchSight Quick Start Guide

**Pick your role and get started in 5 minutes**

---

## 🎨 Dashboard Developer

You're building analytics visualizations. You need **read-only access** to Supabase.

### Step 1: Install
```bash
npm install @supabase/supabase-js
```

### Step 2: Connect
```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  'YOUR_SUPABASE_URL',
  'YOUR_SUPABASE_ANON_KEY'
)
```

### Step 3: Query Data
```javascript
// Get standings
const { data: standings } = await supabase
  .from('fact_team_standings_snapshot')
  .select('team_name, wins, losses, points')
  .order('points', { ascending: false })

// Get scoring leaders
const { data: leaders } = await supabase
  .from('fact_player_stats_core')
  .select('player_name, total_goals, total_assists, total_points')
  .order('total_points', { ascending: false })
  .limit(10)

// Get game box score
const { data: boxScore } = await supabase
  .from('fact_player_game_stats')
  .select('player_name, goals, assists, points, shots')
  .eq('game_id', '18969')
```

### Your Tables
| Table | What It Has |
|-------|-------------|
| `fact_team_standings_snapshot` | Current standings |
| `fact_player_stats_core` | Season totals |
| `fact_player_game_stats` | Per-game stats |
| `dim_schedule` | Game results |
| `dim_player` | Player info |

### Full Docs
📖 [docs/frontend/DASHBOARD_INTEGRATION.md](docs/frontend/DASHBOARD_INTEGRATION.md)

---

## 🏒 Tracker Developer

You're building the live game tracking interface. You need the **ETL API** for uploads.

### Step 1: Start API Server
```bash
cd benchsight
pip install -r requirements.txt
python -m src.api.server
```

### Step 2: Test Connection
```bash
curl http://localhost:5000/api/health
# {"success": true, "data": {"status": "healthy"}}
```

### Step 3: Upload & Process
```javascript
// Upload tracking file
const formData = new FormData()
formData.append('file', trackingFile)
formData.append('game_id', '18969')

await fetch('http://localhost:5000/api/upload', {
  method: 'POST',
  body: formData
})

// Process the game
await fetch('http://localhost:5000/api/games/18969/process', {
  method: 'POST'
})
```

### Your Endpoints
| Endpoint | Purpose |
|----------|---------|
| `POST /api/upload` | Upload tracking file |
| `POST /api/games/{id}/process` | Process game |
| `GET /api/status` | Check pipeline status |
| `GET /api/games/unprocessed` | Games needing processing |

### Full Docs
📖 [docs/frontend/TRACKER_INTEGRATION.md](docs/frontend/TRACKER_INTEGRATION.md)  
📖 [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)

---

## 🏢 Portal Developer

You're building league management. You need **read/write access** to Supabase.

### Step 1: Install
```bash
npm install @supabase/supabase-js
```

### Step 2: Connect
```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  'YOUR_SUPABASE_URL',
  'YOUR_SUPABASE_ANON_KEY'
)
```

### Step 3: CRUD Operations
```javascript
// List players
const { data: players } = await supabase
  .from('dim_player')
  .select('*, dim_team!team_id(team_name)')
  .order('player_full_name')

// Update player
await supabase
  .from('dim_player')
  .update({ skill_rating: '8', team_id: 'T002' })
  .eq('player_id', 'P001')

// Add game to schedule
await supabase
  .from('dim_schedule')
  .insert({
    game_id: 'G_NEW',
    game_date_str: '2025-02-15',
    home_team_id: 'T001',
    away_team_id: 'T002',
    game_status: 'scheduled'
  })
```

### Your Tables
| Table | Operations |
|-------|------------|
| `dim_player` | Full CRUD |
| `dim_team` | Full CRUD |
| `dim_schedule` | Full CRUD |
| `dim_season` | Full CRUD |
| `dim_venue` | Full CRUD |

### Full Docs
📖 [docs/frontend/PORTAL_INTEGRATION.md](docs/frontend/PORTAL_INTEGRATION.md)

---

## 📚 All Documentation

| Document | Description |
|----------|-------------|
| [README.md](README.md) | Project overview |
| [HANDOFF.md](HANDOFF.md) | Current state & deployment |
| [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) | Complete integration guide |
| [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) | Full API reference |
| [docs/DATA_MODELS.md](docs/DATA_MODELS.md) | All 111 tables |
| [docs/SUPABASE_QUERIES.md](docs/SUPABASE_QUERIES.md) | Ready-to-use queries |
| [docs/ETL_ARCHITECTURE.md](docs/ETL_ARCHITECTURE.md) | Pipeline internals |

---

## 🔑 Getting Credentials

Contact the project admin for:
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_ANON_KEY` - Public API key (for frontend)
- `SUPABASE_SERVICE_KEY` - Admin key (for ETL only)

---

## ❓ Common Questions

**Q: Where's the data?**  
A: Supabase (PostgreSQL). 111 tables, 116,000+ rows.

**Q: How do I see all tables?**  
A: Check [docs/DATA_MODELS.md](docs/DATA_MODELS.md) or query `GET /api/tables`

**Q: How often is data updated?**  
A: After each game is processed through the ETL pipeline.

**Q: Can I write to fact tables?**  
A: No, fact tables are ETL-populated. Only dim_ tables support direct writes.

**Q: API server won't start?**  
A: `pip install flask flask-cors` then `python -m src.api.server`
