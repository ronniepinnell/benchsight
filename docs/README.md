# BenchSight Platform - Complete Documentation

## 🎯 Project Overview

BenchSight is a comprehensive hockey analytics platform for the NORAD recreational hockey league. The system processes game tracking data through ETL pipelines into a 111-table dimensional data warehouse hosted on Supabase PostgreSQL.

**Goal:** Reduce manual game tracking time from 8 hours to 1-2 hours per game.

---

## 📦 Project Structure

```
benchsight_restored/
├── tracker/                    # Game Tracking Interface
│   ├── tracker_v22.html       # Production tracker (LATEST)
│   └── tracker_v21.html       # Previous version
├── dashboard/                  # Analytics Dashboards
│   ├── dashboard_v4.html      # NHL-style dashboard (LATEST)
│   ├── dashboard.html         # Original dashboard
│   └── app.py                 # Dash/Plotly server
├── scripts/                    # ETL & Utilities
│   ├── tracker_api.py         # Backend API for tracker
│   ├── flexible_loader.py     # Supabase data loader
│   ├── bulletproof_loader.py  # Robust CSV loader
│   └── qa_comprehensive.py    # Data validation
├── data/
│   ├── raw/                   # Source tracking files
│   └── output/                # Generated CSVs (111 tables)
├── config/                    # Configuration
│   ├── config.yaml           # Main config
│   └── supabase_credentials.yaml
├── docs/                      # Documentation
│   └── handoffs/             # Developer handoffs
└── src/                       # Core modules
    └── database/             # DB operations
```

---

## 🏒 Tracker v22 Features

### Core Functionality
- **12 Event Types:** Faceoff, Shot, Goal, Save, Pass, Turnover, Zone Entry, Zone Exit, Hit, Block, Retrieval, Stoppage
- **Keyboard Shortcuts:** F, S, G, V, P, T, Z, X, H, B, R, W + Space (success), Enter (save)
- **6+6 Player Slots:** 6 event team players + 6 opponent players per event
- **Auto-Linking:** Shot → Save chains automatically linked

### XY Tracking (NEW)
- **Puck Tracking:** Up to 10 XY points per event with trail visualization
- **Player Tracking:** Track player positions on rink
- **Shot Target:** 6-zone net location picker (GH, TM, BH, GL, 5H, BL)
- **Auto Zone Detection:** Zone determined from puck X position

### Supabase Integration
- **Pull:** Load games, rosters, videos, existing tracking data
- **Push:** Save events, shifts, puck XY, player XY, shot XY
- **Tables Written:**
  - `fact_events` - Core event data
  - `fact_events_player` - Player involvement
  - `fact_shifts` - Shift tracking
  - `fact_puck_xy_long` - Puck positions (long format)
  - `fact_puck_xy_wide` - Puck positions (wide format)
  - `fact_player_xy_long` - Player positions
  - `fact_shot_xy` - Shot locations with net targets

### Workflow Features
- **Undo/Redo:** Ctrl+Z / Ctrl+Y with 50-step history
- **Import/Export:** Excel file support (.xlsx)
- **Local Save:** Auto-save to localStorage
- **Video Sync:** YouTube embed with time sync
- **Edit Mode:** Load and modify existing events

---

## 📊 Dashboard v4 Features

### Views
1. **Overview** - Score header, team comparison bars, timeline, top performers
2. **Box Score** - Full player stats table with sorting
3. **Shot Chart** - Interactive rink with shot locations, filtering
4. **Players** - Player cards with stats, filterable by team/position
5. **Advanced** - Corsi, Fenwick, event breakdown
6. **H2H** - Head-to-head player comparison

### Inspired By
- Natural Stat Trick (naturalstattrick.com)
- Evolving Hockey (evolving-hockey.com)
- Money Puck (moneypuck.com)
- Hockey Reference (hockey-reference.com)

---

## 🔧 Backend API (tracker_api.py)

### CLI Usage
```bash
# List games
python scripts/tracker_api.py --action list-games

# Get game data
python scripts/tracker_api.py --action get-game --game-id 18969

# Save tracking data
python scripts/tracker_api.py --action save-tracking --game-id 18969 --file tracking.json

# Export to CSV
python scripts/tracker_api.py --action export-csv --game-id 18969

# Run ETL
python scripts/tracker_api.py --action run-etl --game-id 18969

# Start HTTP API server
python scripts/tracker_api.py --action serve --port 8765
```

### HTTP Endpoints
- `GET /api/games` - List available games
- `GET /api/game?id=XXXXX` - Get game with tracking data
- `GET /api/players` - Get all players
- `GET /api/play-details` - Get play detail options
- `POST /api/save` - Save tracking data
- `POST /api/etl` - Trigger ETL pipeline

### Library Usage
```python
from scripts.tracker_api import TrackerAPI

api = TrackerAPI()
games = api.list_games()
game_data = api.get_game('18969')
api.save_events('18969', events, replace=True)
api.save_puck_xy('18969', puck_data)
api.trigger_etl('18969')
```

---

## 📈 Data Model

### Dimension Tables (44)
- `dim_player` - Player master data
- `dim_schedule` - Game schedule
- `dim_team` - Team information
- `dim_event_type` - Event type definitions
- `dim_play_detail` - Micro-play actions
- `dim_net_location` - Shot target zones
- `dim_rink_coord` - Rink coordinate grid
- ... and 37 more

### Fact Tables (67)
- `fact_events` - Core event tracking
- `fact_events_player` - Player-event relationships
- `fact_shifts` - Shift tracking
- `fact_puck_xy_long/wide` - Puck position tracking
- `fact_player_xy_long/wide` - Player position tracking
- `fact_shot_xy` - Shot location with targets
- `fact_player_game_stats` - Aggregated player stats
- `fact_team_game_stats` - Team-level stats
- `fact_h2h` - Head-to-head matchups
- `fact_wowy` - With/without analysis
- ... and 57 more

### Key Relationships
```
dim_schedule (game_id) 
  → fact_gameroster (player_id → dim_player)
  → fact_events (event_index)
    → fact_events_player (player_id)
    → fact_puck_xy_long (point tracking)
    → fact_shot_xy (shot details)
  → fact_shifts (shift_index)
  → fact_video (camera feeds)
```

---

## 🚀 Deployment

### Supabase Setup
```yaml
URL: https://uuaowslhpgyiudmbvqze.supabase.co
Key: Service role key in config
Tables: 111 tables created via SQL migrations
```

### Local Development
```bash
# Install dependencies
pip install supabase pandas xlsxwriter openpyxl --break-system-packages

# Run tracker
open tracker/tracker_v22.html

# Run dashboard
open dashboard/dashboard_v4.html

# Run API server
python scripts/tracker_api.py --action serve
```

---

## ✅ Current Status

### COMPLETED
- [x] Tracker v22 with full Supabase integration
- [x] Puck XY tracking (10 points per event)
- [x] Player XY tracking
- [x] Shot XY with net location
- [x] Undo/redo functionality
- [x] Import/export Excel
- [x] Dashboard v4 with 6 views
- [x] Backend API (tracker_api.py)
- [x] 111-table data model

### IN PROGRESS
- [ ] Full ETL pipeline restoration
- [ ] Real-time stat calculations
- [ ] Video timestamp linking

### PLANNED
- [ ] Mobile responsive tracker
- [ ] Real-time collaboration
- [ ] Advanced analytics (xG, WAR)
- [ ] Season-level dashboards
- [ ] Player comparison tools

---

## 📋 Gameplan - Next Steps

### Phase 1: Data Validation (Priority)
1. Test tracker with game 18969
2. Verify Supabase push/pull
3. Validate XY data storage
4. Compare results to noradhockey.com

### Phase 2: ETL Completion
1. Restore all 111 table transformations
2. Add stat aggregation pipelines
3. Implement QA validation suite
4. Test with multiple games

### Phase 3: Dashboard Enhancement
1. Add player radar charts
2. Implement line combination tool
3. Add expected goals (xG) model
4. Create season overview page

### Phase 4: Production Polish
1. Error handling improvements
2. Performance optimization
3. Mobile responsiveness
4. User documentation

---

## 🔑 Key Files

| File | Purpose |
|------|---------|
| `tracker/tracker_v22.html` | Production game tracker |
| `dashboard/dashboard_v4.html` | Analytics dashboard |
| `scripts/tracker_api.py` | Backend API |
| `scripts/flexible_loader.py` | Supabase data loader |
| `config/config.yaml` | Configuration |
| `data/output/*.csv` | Generated fact/dim tables |

---

## 📞 Support

For questions about:
- **Tracker:** Check keyboard shortcuts in footer
- **Dashboard:** Use filters and tabs to navigate
- **API:** Run `python scripts/tracker_api.py --help`
- **Data:** Check `docs/DATA_DICTIONARY.md`

---

*Last Updated: January 2026*
*Version: v22*
