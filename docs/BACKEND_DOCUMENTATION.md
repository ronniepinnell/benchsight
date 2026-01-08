# BenchSight Backend Documentation

**Version:** 16.08  
**Updated:** January 8, 2026


## Project Structure Overview

```
benchsight/
├── src/                    # BACKEND CODE - Python ETL & Processing
│   ├── etl_orchestrator.py # Main ETL entry point
│   ├── core/               # Core ETL modules
│   ├── advanced/           # Advanced stats & enhancements
│   ├── ingestion/          # Data loading
│   ├── transformation/     # Data transformation
│   └── supabase/           # Supabase upload/sync
│
├── ui/                     # FRONTEND CODE - HTML/JS
│   ├── tracker/            # Game Tracker App
│   ├── dashboard/          # Analytics Dashboard
│   └── portal/             # Admin Portal
│
├── docs/html/              # HTML Documentation & Old UI Versions
│   ├── tracker/            # Tracker prototypes
│   └── dashboard/          # Dashboard prototypes
│
├── data/                   # Data Files
│   ├── raw/games/          # Raw tracking Excel files
│   ├── output/             # ETL output CSV files
│   └── staging/            # Temporary staging
│
├── config/                 # Configuration
│   ├── VERSION.json        # Current version
│   └── settings.py         # Config loader
│
├── sql/                    # SQL Scripts
│   └── setup_supabase.sql  # Supabase schema
│
└── tests/                  # Test Suite
```

## Backend Code (Python ETL)

### Entry Point: `src/etl_orchestrator.py`
Main ETL orchestrator that runs all processing phases.

```bash
# Run full ETL
python -m src.etl_orchestrator full

# Run specific stage
python -m src.etl_orchestrator base     # Base tables only
python -m src.etl_orchestrator extended # Extended tables
```

### Core Modules: `src/core/`

| File | Purpose |
|------|---------|
| `base_etl.py` | Main ETL processing - loads tracking, creates fact tables |
| `key_utils.py` | Key generation (event_id, shift_id, etc.) |
| `safe_csv.py` | Safe CSV read/write with type handling |
| `combine_tracking.py` | Combines multiple tracking files |

### Advanced Modules: `src/advanced/`

| File | Purpose |
|------|---------|
| `extended_tables.py` | Creates additional dimension tables |
| `enhance_all_stats.py` | Adds advanced stats to tables |
| `event_time_context.py` | Adds time-based context to events |

### Data Flow

```
1. Raw Excel Files (data/raw/games/*/tracking.xlsx)
   ↓
2. Load & Validate (base_etl.py Phase 3)
   ↓
3. Create Dimensions (Phase 5)
   ↓
4. Create Facts (Phase 4)
   ↓
5. Enhance with Stats (Phase 5.5-5.12)
   ↓
6. Output CSVs (data/output/*.csv)
   ↓
7. Upload to Supabase (supabase/sync_to_supabase.py)
```

## Frontend Code (HTML/JavaScript)

### Tracker App: `ui/tracker/index.html`
Single-page application for game tracking.

**Key Functions:**
- `loadGames()` - Load tracked games from Supabase
- `loadRosters(gid)` - Load player rosters for a game
- `selectGame(gid)` - Select and initialize a game
- `submitEvent()` - Record a new event
- `submitShift()` - Record a new shift
- `exportToSupabase()` - Upload tracked data

**State Object (`S`):**
```javascript
S = {
  connected: false,        // Supabase connection status
  sb: null,               // Supabase client
  gameId: null,           // Current game ID
  games: [],              // All tracked games
  rosters: {home:[], away:[]}, // Player rosters
  events: [],             // Tracked events
  shifts: [],             // Tracked shifts
  slots: {home:{}, away:{}}, // Players on ice
  curr: {...},            // Current event being recorded
  ...
}
```

### Dashboard: `ui/dashboard/`

| File | Purpose |
|------|---------|
| `index.html` | Main dashboard with stats overview |
| `player.html` | Player profile page |
| `team.html` | Team profile page |
| `game.html` | Game recap with play-by-play |

### Portal: `ui/portal/index.html`
Admin portal for ETL control and data management.

## Database Schema

### Supabase Tables (59 total)

**Dimensions (33):**
- `dim_player` - Player master data
- `dim_team` - Team master data
- `dim_schedule` - Game schedule
- `dim_event_type` - Event type reference
- `dim_event_detail` - Event detail reference
- ... and more

**Facts (24):**
- `fact_events` - Core event data
- `fact_event_players` - Player involvement in events
- `fact_shifts` - Shift data
- `fact_shift_players` - Players in shifts
- `fact_tracking` - XY tracking data
- ... and more

**QA (2):**
- `qa_goal_accuracy` - Goal verification
- `qa_data_completeness` - Data completeness checks

## Key Workflows

### 1. Running ETL
```bash
cd benchsight/project
python -m src.etl_orchestrator full
```

### 2. Syncing to Supabase
```bash
python supabase/sync_to_supabase.py
```

### 3. Testing
```bash
pytest tests/ -v
```

### 4. Adding a New Game
1. Create folder: `data/raw/games/{game_id}/`
2. Add tracking Excel file: `{game_id}_tracking.xlsx`
3. Run ETL: `python -m src.etl_orchestrator full`
4. Sync to Supabase: `python supabase/sync_to_supabase.py`

## Configuration

### `config/VERSION.json`
```json
{
  "version_string": "v16.08",
  "major": 14,
  "minor": 12
}
```

### Supabase Connection
Set in tracker UI via Settings modal:
- Project URL: `https://{project}.supabase.co`
- Anon Key: `eyJ...` (public anon key)

## HTML Documentation

All HTML documentation is in `docs/html/`:

| Category | Path |
|----------|------|
| Main Docs | `docs/html/*.html` |
| Table Docs | `docs/html/tables/*.html` |
| Tracker Docs | `docs/html/tracker/*.html` |
| Dashboard Versions | `docs/html/dashboard/*.html` |
| Prototypes | `docs/html/prototypes/*.html` |

## Critical Files

### Must-Read Before Development
1. `LLM_REQUIREMENTS.md` - Development rules
2. `MASTER_GUIDE.md` - Full project guide
3. `docs/TRACKER_ETL_SPECIFICATION.md` - Export format
4. `docs/KEY_FORMATS.md` - Key generation rules

### ETL Core
1. `src/core/base_etl.py` - Main ETL logic
2. `src/core/key_utils.py` - Key generation
3. `src/etl_orchestrator.py` - ETL runner

### Frontend Core
1. `ui/tracker/index.html` - Tracker app
2. `ui/dashboard/index.html` - Dashboard
3. `ui/portal/index.html` - Admin portal

## Goal Counting Rule

**CRITICAL:** Goals are ONLY counted when:
```
event_type = 'Goal' AND event_detail = 'Goal_Scored'
```

- `Shot_Goal` = the shot that became a goal (NOT the goal itself)
- `Goal_Scored` = the actual goal event
- Only `event_player_1` is the scorer

## Verification

### ETL Output Verification
```bash
# Check goals match
cat data/output/qa_goal_accuracy.csv

# Expected output:
# Game 18969: 7 goals ✓
# Game 18977: 6 goals ✓
# Game 18981: 3 goals ✓
# Game 18987: 1 goal ✓
```

### Tracker Verification
1. Open Verification Panel (✅ button)
2. Enter official score from noradhockey.com
3. Click Verify to compare

## Troubleshooting

### "No players loading"
- Check Supabase connection
- Verify fact_gameroster has data for game_id
- Check browser console for errors

### "Games duplicating in dropdown"
- Fixed in v16.08 - uses deduplication
- Only loads TRACKED games (games in fact_events)

### "ETL fails"
- Check data/raw/games/{id}/tracking.xlsx exists
- Verify tracking_event_index column has valid numbers
- Check ETL log for specific errors

---

*Last Updated: 2026-01-08*
*Version: v16.08*
