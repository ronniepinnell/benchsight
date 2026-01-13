# BenchSight

**Hockey Analytics Platform for NORAD Recreational League**

Version: 28.3  
Updated: 2026-01-12

---

## Quick Start

```bash
# 1. Run ETL (generates 139 tables)
python run_etl.py

# 2. Validate output
python validate.py

# 3. Generate Supabase schema
python upload.py --schema

# 4. Create tables in Supabase SQL Editor
# Run: sql/reset_supabase.sql

# 5. Upload data to Supabase
python upload.py

# 6. Deploy views in Supabase SQL Editor
# Run: sql/views/99_DEPLOY_ALL_VIEWS.sql
```

### Upload Commands

| Command | Description |
|---------|-------------|
| `python upload.py` | Upload all 139 tables |
| `python upload.py --dims` | Dimension tables only |
| `python upload.py --facts` | Fact tables only |
| `python upload.py --tables dim_player fact_events` | Specific tables |
| `python upload.py --pattern "fact_player*"` | Pattern matching |
| `python upload.py --list` | List available tables |
| `python upload.py --dry-run` | Preview without uploading |

### ETL Commands

| Command | Description |
|---------|-------------|
| `python run_etl.py` | Full ETL (all games) |
| `python run_etl.py --wipe` | Clean slate then full ETL |
| `python run_etl.py --list-games` | List available game IDs |
| `python run_etl.py --games 18969 18977` | Process specific games |
| `python run_etl.py --exclude-games 18969` | Exclude specific games |
| `python run_etl.py --validate` | Validate tables exist |
| `python run_etl.py --status` | Show current status |

---

## What's New in v28.3

- **139 ETL tables** (removed 3 redundant aggregation tables)
- **30 Supabase views** for dashboard consumption
- **Next.js 14 dashboard guide** with TypeScript, Tailwind, shadcn/ui
- **Advanced goalie stats** (128 columns including rush/set play SV%, rebound control)
- **Basic + Advanced stats tiers** (official league data vs tracking-derived)

---

## Database Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      NEXT.JS DASHBOARD (Vercel)                         │
│   Standings | Leaderboards | Player Profiles | Game Details            │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         SUPABASE VIEW LAYER                             │
│   30 views: v_leaderboard_*, v_standings_*, v_rankings_*, etc.         │
│   Pre-aggregated, always fresh, no additional computation              │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         ETL TABLE LAYER                                  │
│   139 tables: dim_*, fact_*, qa_*, lookup_*                            │
│   Source of truth, validated, versioned                                 │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
benchsight_v28/
├── run_etl.py          # Main ETL (generates 139 tables)
├── upload.py           # Upload to Supabase
├── validate.py         # Data validation
│
├── data/
│   ├── raw/            # Input Excel files
│   │   ├── BLB_Tables.xlsx
│   │   └── games/[game_id]/
│   └── output/         # Generated CSVs (139 tables)
│
├── docs/
│   ├── CHANGELOG.md
│   ├── TODO.md
│   ├── DATA_DICTIONARY.md
│   ├── NEXTJS_DASHBOARD_GUIDE.md    # ← New: Full Next.js implementation
│   ├── DASHBOARD_INTEGRATION.md
│   └── SUPABASE_RESET_GAMEPLAN.md
│
├── sql/
│   └── views/
│       ├── 99_DEPLOY_ALL_VIEWS.sql  # ← Deploy all 30 views
│       └── VIEW_CATALOG.md          # ← View documentation
│
├── src/
│   ├── core/           # Core ETL logic
│   ├── tables/         # Table builders (macro_stats.py for aggregations)
│   └── advanced/       # Advanced analytics
│
├── ui/
│   └── tracker/        # Game tracking interface
│
└── NEXT_PROMPT.md      # ← What to do next
```

---

## Key Documentation

| File | Purpose |
|------|---------|
| `NEXT_PROMPT.md` | **Start here** - What to do next |
| `docs/NEXTJS_DASHBOARD_GUIDE.md` | Full Next.js 14 dashboard implementation |
| `docs/SUPABASE_RESET_GAMEPLAN.md` | Step-by-step Supabase deployment |
| `sql/views/99_DEPLOY_ALL_VIEWS.sql` | Deploy all views to Supabase |
| `docs/DATA_DICTIONARY.md` | Table/column definitions |
| `docs/CHANGELOG.md` | Version history |

---

## Output Summary

| Metric | Count |
|--------|-------|
| **ETL Tables** | 139 |
| **Supabase Views** | 30 |
| **Total Database Objects** | 169 |
| **Tracked Games** | 4 |
| **Goals Verified** | 17 |
| **Player Game Stats Columns** | 444 |
| **Goalie Game Stats Columns** | 128 |

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| ETL | Python, Pandas |
| Database | Supabase (PostgreSQL) |
| Tracker | HTML/JavaScript |
| **Dashboard** | Next.js 14, TypeScript, Tailwind, shadcn/ui, Recharts |
| Deployment | Vercel |

---

## Critical Rules

### Goal Counting
```
Goals ONLY via: event_type='Goal' AND event_detail='Goal_Scored'
Shot_Goal = the shot attempt, NOT the goal itself
```

### Player Attribution
```
event_player_1 = Primary actor (shooter, passer, faceoff winner)
```

### Basic vs Advanced Stats
```
Basic (_basic tables) = Official noradhockey.com data (G, A, PIM)
Advanced (other tables) = Tracking-derived micro-stats
```

---

## Next Steps

See `NEXT_PROMPT.md` for:
1. Supabase reset commands
2. Table upload instructions
3. View deployment
4. Next.js dashboard setup

---

*BenchSight v28.3 - NORAD Hockey Analytics*
