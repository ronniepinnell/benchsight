# 02 - The BenchSight System Map

**Learning Objectives:**
- Understand the five major systems in BenchSight
- Know what each system owns and produces
- Navigate to the right code for any task
- Understand system boundaries and data formats

---

## The Five Systems

BenchSight is composed of five interconnected systems:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                              BENCHSIGHT                                   │
├────────────┬────────────┬────────────┬────────────┬─────────────────────┤
│  TRACKER   │    ETL     │  DATABASE  │    API     │     DASHBOARD       │
│   (Input)  │ (Transform)│  (Store)   │  (Access)  │     (Display)       │
├────────────┼────────────┼────────────┼────────────┼─────────────────────┤
│ ui/tracker │    src/    │  Supabase  │    api/    │   ui/dashboard/     │
│            │  scripts/  │    sql/    │            │                     │
├────────────┼────────────┼────────────┼────────────┼─────────────────────┤
│  HTML/JS   │   Python   │ PostgreSQL │  FastAPI   │ Next.js/TypeScript  │
│  (legacy)  │   pandas   │   (cloud)  │   Python   │     React           │
├────────────┼────────────┼────────────┼────────────┼─────────────────────┤
│ Game event │ 139 CSV    │ Cloud DB   │ REST       │ Analytics charts    │
│ tracking   │ tables     │ + views    │ endpoints  │ and pages           │
└────────────┴────────────┴────────────┴────────────┴─────────────────────┘
```

---

## System 1: Tracker (Input)

**Purpose:** Manually track game events in real-time
**Location:** `ui/tracker/`
**Tech:** HTML/JavaScript (legacy single-file architecture)

### What It Does

- Records game events (shots, goals, passes, faceoffs)
- Captures XY coordinates on a rink canvas
- Tracks player shifts (who's on ice)
- Syncs with game video timestamps
- Exports data to Excel files

### Key Files

| File | Purpose |
|------|---------|
| `ui/tracker/index.html` | Main tracker application (~16,000 lines) |
| `ui/tracker/src/` | TypeScript components (partial rewrite) |

### Data Output

Exports to: `data/raw/games/{game_id}/`
- `{game_id}_tracking.xlsx` → Events sheet, Shifts sheet

### Current State

⚠️ **Technical Debt:** The tracker is a single 16,000-line HTML file with global state. A Rust/Next.js rewrite is planned.

---

## System 2: ETL (Transform)

**Purpose:** Transform raw tracking data into analytics-ready tables
**Location:** `src/`, `scripts/`, `run_etl.py`
**Tech:** Python, pandas

### What It Does

- Loads league master data (BLB_Tables.xlsx)
- Loads game tracking data (Excel files)
- Resolves player identities (jersey → player_id)
- Calculates 300+ statistics per player per game
- Generates 139 output tables
- Validates data quality

### Key Files

| File | Lines | Purpose |
|------|-------|---------|
| `run_etl.py` | ~150 | Entry point |
| `src/core/base_etl.py` | ~1,065 | Main orchestrator (11 phases) |
| `src/core/etl_phases/` | ~4,700 | Modular phase implementations |
| `src/builders/events.py` | ~300 | Creates fact_events |
| `src/builders/shifts.py` | ~250 | Creates fact_shifts |
| `src/builders/player_stats.py` | ~800 | Creates fact_player_game_stats |
| `src/calculations/goals.py` | ~135 | Goal counting logic |
| `src/tables/dimension_tables.py` | ~400 | 23 static dimension tables |

### Data Flow

```
Input:
  data/raw/BLB_Tables.xlsx        (league master data)
  data/raw/games/{id}/*.xlsx      (tracking data)
                ↓
Processing:
  11 ETL phases in base_etl.py
                ↓
Output:
  data/output/*.csv               (139 tables)
```

### Commands

```bash
./benchsight.sh etl run           # Run full ETL
./benchsight.sh etl run --wipe    # Clean slate + run
./benchsight.sh etl validate      # Check outputs
```

---

## System 3: Database (Store)

**Purpose:** Store analytics data for querying
**Location:** `sql/`, Supabase cloud
**Tech:** PostgreSQL (via Supabase)

### What It Does

- Stores 139 tables from ETL output
- Provides SQL views for complex queries
- Handles authentication and authorization
- Enables real-time subscriptions (if needed)

### Key Files

| File | Purpose |
|------|---------|
| `sql/setup_supabase.sql` | Initial schema setup |
| `sql/reset_supabase.sql` | Database reset script |
| `sql/views/01_leaderboard_views.sql` | Player/team leaderboards |
| `sql/views/02_standings_views.sql` | Season standings |
| `sql/views/99_DEPLOY_ALL_VIEWS.sql` | Deploy all views |

### Table Categories

| Prefix | Count | Purpose |
|--------|-------|---------|
| `dim_*` | ~50 | Dimension tables (lookups) |
| `fact_*` | ~81 | Fact tables (transactional) |
| `qa_*` | ~8 | Quality assurance |
| `v_*` | ~20 | Views (pre-aggregated) |

### Commands

```bash
./benchsight.sh db upload         # Upload CSVs to Supabase
./benchsight.sh db reset          # Reset database
```

---

## System 4: API (Access)

**Purpose:** Provide programmatic access to data and ETL operations
**Location:** `api/`
**Tech:** FastAPI (Python)

### What It Does

- Exposes REST endpoints for data queries
- Triggers ETL runs remotely
- Manages background jobs
- Provides ML predictions (future)

### Key Files

| File | Purpose |
|------|---------|
| `api/main.py` | FastAPI application entry |
| `api/routes/health.py` | Health check endpoints |
| `api/routes/etl.py` | ETL trigger endpoints |
| `api/routes/upload.py` | Database upload endpoints |
| `api/services/etl_service.py` | ETL business logic |

### Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Server status |
| `/etl/run` | POST | Trigger ETL |
| `/etl/status/{job_id}` | GET | Check job status |
| `/upload/tables` | POST | Upload to Supabase |

### Commands

```bash
./benchsight.sh api dev           # Start dev server (port 8000)
./benchsight.sh api test          # Run API tests
```

---

## System 5: Dashboard (Display)

**Purpose:** Display analytics to users
**Location:** `ui/dashboard/`
**Tech:** Next.js 14, TypeScript, React, Tailwind CSS

### What It Does

- Displays player/team/game statistics
- Shows leaderboards and rankings
- Visualizes trends with charts
- Provides drill-down navigation

### Key Directories

| Directory | Purpose |
|-----------|---------|
| `src/app/` | Next.js App Router pages |
| `src/app/norad/` | NORAD league pages |
| `src/components/` | React components |
| `src/lib/supabase/` | Database queries |
| `src/types/` | TypeScript interfaces |

### Page Structure

```
/norad/
├── dashboard/          # Main dashboard
├── players/
│   ├── page.tsx       # Player list
│   └── [playerId]/    # Player profile
├── teams/
│   ├── page.tsx       # Team list
│   └── [teamId]/      # Team profile
├── games/
│   ├── page.tsx       # Game list
│   └── [gameId]/      # Game detail
├── leaders/           # Leaderboards
└── stats/             # Stat explorer
```

### Commands

```bash
./benchsight.sh dashboard dev     # Start dev server (port 3000)
./benchsight.sh dashboard build   # Production build
```

---

## System Boundaries

### What Crosses Each Boundary

| From → To | Data Format | Transfer Method |
|-----------|-------------|-----------------|
| Tracker → ETL | Excel files | File system |
| ETL → Database | CSV files | Upload script |
| Database → API | SQL queries | Supabase client |
| Database → Dashboard | SQL queries | Supabase client |
| API → Dashboard | JSON | HTTP REST |

### Data Format at Each Stage

```
Tracker:
  Excel: rows with jersey numbers, times, coordinates

ETL Input:
  pandas DataFrame with raw tracking columns

ETL Output:
  CSV files with calculated stats, proper keys

Database:
  PostgreSQL tables with indexes, FKs

Dashboard:
  TypeScript interfaces, React state
```

---

## Navigation Cheat Sheet

🔑 **"I need to change X, where do I look?"**

### Data/Stats Changes

| Task | Location |
|------|----------|
| Change goal counting logic | `src/calculations/goals.py` |
| Change xG calculation | `src/calculations/xg.py` |
| Change WAR/GAR weights | `config/formulas.json` |
| Add new stat to player stats | `src/builders/player_stats.py` |
| Add new dimension table | `src/tables/dimension_tables.py` |
| Add new fact table | `src/tables/remaining_facts.py` |
| Change how events are processed | `src/builders/events.py` |
| Change how shifts are processed | `src/builders/shifts.py` |

### Dashboard Changes

| Task | Location |
|------|----------|
| Add new page | `ui/dashboard/src/app/norad/` |
| Add new component | `ui/dashboard/src/components/` |
| Change database query | `ui/dashboard/src/lib/supabase/queries/` |
| Add new TypeScript type | `ui/dashboard/src/types/` |
| Change styling | Component file (Tailwind classes) |

### API Changes

| Task | Location |
|------|----------|
| Add new endpoint | `api/routes/` |
| Add business logic | `api/services/` |
| Add request/response types | `api/models/` |

### Database Changes

| Task | Location |
|------|----------|
| Add/modify view | `sql/views/` |
| Change schema | `sql/setup_supabase.sql` |
| Reset database | `sql/reset_supabase.sql` |

### Configuration

| Task | Location |
|------|----------|
| Change ETL behavior | `config/config.ini` |
| Change formula weights | `config/formulas.json` |
| Exclude games from ETL | `config/excluded_games.txt` |
| Change dashboard env | `ui/dashboard/.env.local` |

---

## The Complete Data Journey

Let's trace data from a goal being tracked to appearing on the dashboard:

### Step 1: Tracker (Input)
```
User clicks "Goal" in tracker
├── Player: #12 Blue
├── Time: P2, 8:45
├── Location: x=172, y=42
└── Saves to: data/raw/games/19001/19001_tracking.xlsx
```

### Step 2: ETL (Transform)
```
run_etl.py executes
├── Phase 1: Loads BLB_Tables.xlsx (gets player_id for jersey #12)
├── Phase 2: Builds player lookup
├── Phase 3: Loads tracking file
│   └── Creates fact_event_players with event_type='Goal'
├── Phase 4: Collapses to fact_events
├── Phase 6: Aggregates to fact_player_game_stats
│   └── goals=1 for this player
└── Outputs: data/output/fact_player_game_stats.csv
```

### Step 3: Database (Store)
```
./benchsight.sh db upload
├── Reads data/output/*.csv
├── Uploads to Supabase
└── fact_player_game_stats table updated
```

### Step 4: Dashboard (Display)
```
User visits /norad/players/P001
├── Page component calls: getPlayerStats(P001)
├── Query hits: fact_player_game_stats WHERE player_id='P001'
├── Returns: { goals: 1, ... }
└── Renders: "Goals: 1" on player profile
```

---

## Quick Start Commands

```bash
# Full pipeline (tracker → dashboard)
./benchsight.sh etl run --wipe    # 1. Run ETL
./benchsight.sh db upload         # 2. Upload to DB
./benchsight.sh dashboard dev     # 3. Start dashboard

# Check status
./benchsight.sh status            # Project overview
./benchsight.sh etl validate      # Verify ETL output

# Development
./benchsight.sh api dev           # API server (port 8000)
./benchsight.sh dashboard dev     # Dashboard (port 3000)
```

---

## Key Takeaways

1. **Five systems:** Tracker → ETL → Database → API → Dashboard
2. **ETL is the heart:** Transforms raw data into 139 analytics tables
3. **Data flows one direction:** Input → Transform → Store → Display
4. **Each system has clear boundaries:** Know what crosses each boundary
5. **Use the cheat sheet:** "I need to change X" → Go to Y

---

**Next:** [03-etl-overview.md](03-etl-overview.md) - Why ETL exists and its design decisions
