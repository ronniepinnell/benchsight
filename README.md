# BenchSight Hockey Analytics Platform

**Complete data warehouse and API for recreational hockey analytics**

[![Tests](https://img.shields.io/badge/tests-485%20passed-brightgreen)]()
[![Tables](https://img.shields.io/badge/tables-111-blue)]()
[![Version](https://img.shields.io/badge/version-16.1-orange)]()

---

## What is BenchSight?

BenchSight transforms raw hockey game tracking data into a dimensional data warehouse powering:
- **Dashboard**: Analytics visualizations and leaderboards
- **Tracker**: Live game event recording
- **Portal**: League management interface

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   TRACKER   │────▶│   ETL API   │────▶│  SUPABASE   │
│  (record)   │     │  (process)  │     │   (store)   │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                    ┌──────────────────────────┴──────────────────────────┐
                    │                                                      │
              ┌─────▼─────┐                                         ┌─────▼─────┐
              │ DASHBOARD │                                         │  PORTAL   │
              │  (view)   │                                         │ (manage)  │
              └───────────┘                                         └───────────┘
```

---

## Quick Start

### For Frontend Developers

**Dashboard/Portal** - Read data from Supabase:
```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

// Get standings
const { data } = await supabase
  .from('fact_team_standings_snapshot')
  .select('*')
  .order('points', { ascending: false })

// Get player stats
const { data } = await supabase
  .from('fact_player_game_stats')
  .select('*')
  .eq('game_id', '18969')
```

**Tracker** - Upload and process games:
```javascript
// Upload tracking file
const formData = new FormData()
formData.append('file', file)
await fetch('http://localhost:5000/api/upload', { method: 'POST', body: formData })

// Process game
await fetch('http://localhost:5000/api/games/18969/process', { method: 'POST' })
```

### For Backend/ETL Developers

```bash
# Install dependencies
pip install -r requirements.txt

# Start API server
python -m src.api.server

# Or run ETL directly
python src/main.py --process-all
```

---

## Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| [DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) | Complete integration guide | All developers |
| [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) | ETL API reference | Backend, Tracker |
| [DATA_MODELS.md](docs/DATA_MODELS.md) | All 111 tables documented | All developers |
| [SUPABASE_QUERIES.md](docs/SUPABASE_QUERIES.md) | Ready-to-use queries | Frontend |
| [ETL_ARCHITECTURE.md](docs/ETL_ARCHITECTURE.md) | Pipeline internals | Backend |

### Frontend-Specific Guides

| Guide | For |
|-------|-----|
| [DASHBOARD_INTEGRATION.md](docs/frontend/DASHBOARD_INTEGRATION.md) | Dashboard developers |
| [TRACKER_INTEGRATION.md](docs/frontend/TRACKER_INTEGRATION.md) | Tracker developers |
| [PORTAL_INTEGRATION.md](docs/frontend/PORTAL_INTEGRATION.md) | Portal developers |

---

## Data Access

### Option 1: Supabase Direct (Dashboard, Portal)

```bash
npm install @supabase/supabase-js
```

```javascript
const supabase = createClient(URL, KEY)
const { data } = await supabase.from('dim_player').select('*')
```

### Option 2: ETL API (Tracker, Admin)

```bash
# Start server
python -m src.api.server

# Test connection
curl http://localhost:5000/api/health
```

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Health check |
| `/api/status` | GET | Pipeline status |
| `/api/games` | GET | List all games |
| `/api/games/{id}/process` | POST | Process single game |
| `/api/upload` | POST | Upload tracking file |
| `/api/tables` | GET | List all tables |
| `/api/tables/{name}` | GET | Get table data |
| `/api/stats/players` | GET | Player statistics |

---

## Database Schema

### 111 Tables Total

| Category | Count | Examples |
|----------|-------|----------|
| Dimensions | 48 | dim_player, dim_team, dim_schedule |
| Facts | 58 | fact_events, fact_player_game_stats |
| ETL Metadata | 2 | etl_run_log, etl_table_log |
| QA | 3 | qa_goal_accuracy, qa_validation_log |

### Key Tables

```
dim_player          - Player master data (450 players)
dim_team            - Team information (12 teams)
dim_schedule        - Game schedule and results (200+ games)
fact_events         - Play-by-play (15,000+ events)
fact_player_game_stats - Per-game statistics (8,000+ rows)
fact_team_standings_snapshot - Current standings
```

### Primary Key Convention

Every table's first column is its primary key. Examples:
- `dim_player.player_id` → "P001"
- `fact_events.event_key` → "EVT_18969_1_001"
- `fact_player_game_stats.player_game_key` → "PGK_18969_P001"

---

## Project Structure

```
benchsight/
├── config/                 # Configuration files
│   └── config_local.ini    # Supabase credentials (create from template)
├── data/
│   ├── output/             # 111 CSV files for deployment
│   └── raw/                # Source data files
├── docs/                   # Documentation
│   ├── frontend/           # Frontend-specific guides
│   ├── DEVELOPER_GUIDE.md
│   ├── API_DOCUMENTATION.md
│   ├── DATA_MODELS.md
│   └── SUPABASE_QUERIES.md
├── scripts/
│   ├── deploy_supabase.py  # Deploy data to Supabase
│   ├── supabase_schema.py  # Generate SQL schema
│   └── verify_delivery.py  # Pre-deploy validation
├── sql/
│   ├── create_all_tables.sql
│   └── drop_all_tables.sql
├── src/
│   ├── api/                # REST API server
│   │   └── server.py       # Flask API
│   ├── pipeline/           # ETL pipeline
│   └── database/           # Database operations
├── tests/                  # Test suite (485 tests)
├── dashboard/              # Dashboard HTML files
├── tracker/                # Tracker HTML files
└── requirements.txt
```

---

## Deployment

### First-Time Setup

1. **Create Supabase Project** at supabase.com

2. **Configure Credentials**
   ```bash
   cp config/config_local.ini.template config/config_local.ini
   # Edit with your Supabase URL and service key
   ```

3. **Create Tables**
   - Run `sql/create_all_tables.sql` in Supabase SQL Editor

4. **Deploy Data**
   ```bash
   python scripts/deploy_supabase.py --all
   ```

### Updating Data

```bash
# Process new games through ETL
python src/main.py --process-all

# Deploy updates (upsert mode)
python scripts/deploy_supabase.py --all --mode upsert
```

### API Server

```bash
# Development
python -m src.api.server --debug

# Production (with gunicorn)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 'src.api.server:app'
```

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_integration_etl.py -v

# Run with coverage
pytest tests/ --cov=src
```

Current status: **485 passed, 6 skipped**

---

## Environment Variables

```bash
# .env or config/config_local.ini
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
SUPABASE_ANON_KEY=your-anon-key
```

---

## CI/CD

GitHub Actions workflow in `.github/workflows/ci.yml`:
- Runs tests on push/PR
- Validates SQL files
- Checks CSV integrity

---

## Support

### Troubleshooting

**API won't start:**
```bash
pip install flask flask-cors
python -m src.api.server
```

**Supabase connection fails:**
- Check config/config_local.ini exists
- Verify URL and key are correct
- Ensure tables are created in Supabase

**Tests failing:**
```bash
# Regenerate test data
python src/main.py --export
pytest tests/ -v
```

### Key Files for Debugging

| File | Purpose |
|------|---------|
| `config/config_local.ini` | Credentials |
| `data/output/*.csv` | Exported data |
| `sql/create_all_tables.sql` | Database schema |
| `src/api/server.py` | API endpoints |

---

## Version History

- **16.1** (Dec 31, 2025) - Code cleanup, API server, frontend docs
- **16.0** (Dec 31, 2025) - Full Supabase deployment, 111 tables
- **15.0** - ETL pipeline refactor
- **14.0** - Data warehouse schema

---

## License

Proprietary - NORAD Hockey League
