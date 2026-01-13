# BenchSight Architecture

**Technical Design Documentation**

Updated: 2026-01-10

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA FLOW                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐         │
│   │  Tracker │────▶│   Raw    │────▶│   ETL    │────▶│  Supabase │         │
│   │  (HTML)  │     │  (Excel) │     │ (Python) │     │   (DB)    │         │
│   └──────────┘     └──────────┘     └──────────┘     └──────────┘         │
│                                           │                │               │
│                                           ▼                ▼               │
│                                    ┌──────────┐     ┌──────────┐          │
│                                    │   CSVs   │     │ Dashboard │          │
│                                    │  (131)   │     │  (HTML)   │          │
│                                    └──────────┘     └──────────┘          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Architecture

### Dimensional Model

```
                    ┌─────────────────────┐
                    │    FACT TABLES      │
                    │  (Events, Stats)    │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  dim_player   │    │  dim_schedule │    │  dim_team     │
│  dim_season   │    │  dim_venue    │    │  dim_period   │
│  dim_league   │    │  dim_event_*  │    │  dim_stat     │
└───────────────┘    └───────────────┘    └───────────────┘
```

### Table Categories

| Category | Count | Examples |
|----------|-------|----------|
| Dimensions | 55 | dim_player, dim_team, dim_event_type |
| Facts | 71 | fact_events, fact_player_game_stats |
| QA | 4 | qa_goal_verification |
| **Total** | **131** | |

---

## ETL Pipeline

### Phases

```
Phase 1: EXTRACT
├── Load BLB_TABLES.xlsx (master dimensions)
├── Load game tracking files
└── Load roster data

Phase 2: TRANSFORM - DIMENSIONS
├── Build dim_player
├── Build dim_team
├── Build dim_schedule
└── Build all other dims

Phase 3: TRANSFORM - CORE FACTS
├── Build fact_gameroster
├── Build fact_events
└── Build fact_shifts

Phase 4: TRANSFORM - DERIVED FACTS
├── Build fact_player_game_stats
├── Build fact_team_game_stats
└── Build fact_lines

Phase 5: TRANSFORM - ANALYTICS
├── Build H2H tables
├── Build WOWY tables
└── Build shot chains

Phase 6: LOAD
├── Export to CSVs
└── (Optional) Upload to Supabase
```

### Key Files

| File | Purpose |
|------|---------|
| `run_etl.py` | Main entry point |
| `src/core/base_etl.py` | Core ETL logic |
| `src/tables/*.py` | Table builders |
| `src/stats/*.py` | Stats calculations |

---

## Database Schema

### Primary Keys

| Table Pattern | Key Format |
|---------------|------------|
| dim_* | `{entity}_id` (integer) |
| fact_events | `event_key` (string) |
| fact_player_game_stats | `player_game_key` (string) |
| fact_team_game_stats | `team_game_key` (string) |

### Key Formats

```
event_key:        {game_id}_{period}_{event_num}
player_game_key:  {game_id}_{player_id}
team_game_key:    {game_id}_{team_id}
shift_key:        {game_id}_{player_id}_{shift_num}
```

### Foreign Key Relationships

```
fact_events
├── game_id → dim_schedule.game_id
├── player_id → dim_player.player_id
├── team_id → dim_team.team_id
├── event_type_id → dim_event_type.event_type_id
└── event_detail_id → dim_event_detail.event_detail_id

fact_player_game_stats
├── game_id → dim_schedule.game_id
├── player_id → dim_player.player_id
└── team_id → dim_team.team_id
```

---

## Code Structure

```
src/
├── core/               # Core utilities
│   ├── base_etl.py     # Main ETL orchestrator
│   ├── table_writer.py # CSV/Supabase output
│   └── key_utils.py    # Key generation
│
├── calculations/       # Calculation functions (v29.1)
│   ├── goals.py        # Goal counting (single source of truth)
│   ├── corsi.py        # Corsi/Fenwick calculations
│   ├── ratings.py      # Player rating calculations
│   └── time.py         # Time on ice calculations
│
├── tables/             # Table builders
│   ├── dimension_tables.py
│   ├── core_facts.py
│   └── remaining_facts.py
│
├── utils/              # Utility modules
│   ├── game_type_aggregator.py  # Game type splits (v29.0)
│   └── key_parser.py
│
├── supabase/           # Database
│   └── supabase_manager.py
│
└── ingestion/          # Data loading
    ├── blb_loader.py
    └── game_loader.py
```

---

## Configuration

### config/config_local.ini
```ini
[supabase]
url = https://xxx.supabase.co
service_key = your_key

[etl]
batch_size = 500
log_level = INFO
```

### Environment Variables
```bash
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_key
```

---

## Data Quality

### Validation Rules

| Rule | Check |
|------|-------|
| Goal counting | event_type='Goal' AND event_detail='Goal_Scored' |
| Player attribution | event_player_1 = primary actor |
| FK integrity | All references resolve |
| No orphans | Every fact has matching dims |

### Expected Counts

| Metric | Value |
|--------|-------|
| Total tables | 131 |
| Goals | 17 (16 tracked) |
| Games | 4 |
| Players | ~50 |

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| ETL | Python 3.11 | Data processing |
| Data | Pandas | DataFrames |
| Database | PostgreSQL | Storage (via Supabase) |
| Backend | Supabase | Auth + API + DB |
| Frontend | HTML/JS | Tracker, Dashboard |

---

## Future Architecture (Phase 2+)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PRODUCTION ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                  │
│   │   Vercel    │     │   Railway   │     │  Supabase   │                  │
│   │  (Next.js)  │────▶│  (FastAPI)  │────▶│ (Postgres)  │                  │
│   │  Frontend   │     │   ETL API   │     │  Database   │                  │
│   └─────────────┘     └─────────────┘     └─────────────┘                  │
│         │                                        │                          │
│         └────────────────────────────────────────┘                          │
│                     Direct queries via Supabase client                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

*Last updated: 2026-01-10*
