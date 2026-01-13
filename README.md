# BenchSight

**Hockey Analytics Platform for NORAD Recreational League**

Version: 29.0  
Updated: 2026-01-13

---

## 🚀 Getting Started

**New to BenchSight?** Start here:

1. **[Quick Start Guide](docs/QUICK_START.md)** - Get running in 5 minutes
2. **[Setup Instructions](docs/SETUP.md)** - Complete installation guide
3. **[Architecture Overview](docs/ARCHITECTURE.md)** - Understand the system

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

## What's New in v29.0

- **Game Type Aggregator** - Single source of truth for Regular/Playoffs/All splits
- **Code Refactoring** - Eliminated duplication across 6 season stats tables
- **139 ETL tables** - Complete dimensional data warehouse
- **30 Supabase views** - Pre-aggregated for dashboard consumption
- **Next.js 14 dashboard guide** - Full implementation guide with TypeScript, Tailwind, shadcn/ui
- **Advanced goalie stats** - 128 columns including rush/set play SV%, rebound control

See [CHANGELOG.md](docs/CHANGELOG.md) for complete version history.

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

## 📚 Documentation

### Getting Started
- **[Quick Start](docs/QUICK_START.md)** - 5-minute guide to get running
- **[Setup Guide](docs/SETUP.md)** - Complete installation instructions
- **[Contributing](docs/CONTRIBUTING.md)** - How to contribute

### Core Documentation
| File | Purpose |
|------|---------|
| `docs/ARCHITECTURE.md` | System design and data flow |
| `docs/ETL.md` | ETL pipeline details |
| `docs/DATA_DICTIONARY.md` | Complete table/column definitions |
| `docs/CODE_STANDARDS.md` | Coding standards and best practices |
| `docs/CHANGELOG.md` | Version history and changes |

### Deployment & Integration
| File | Purpose |
|------|---------|
| `docs/NEXTJS_DASHBOARD_GUIDE.md` | Next.js 14 dashboard implementation |
| `docs/SUPABASE_RESET_GAMEPLAN.md` | Step-by-step Supabase deployment |
| `docs/DASHBOARD_INTEGRATION.md` | Dashboard integration guide |
| `sql/views/99_DEPLOY_ALL_VIEWS.sql` | Deploy all 30 views to Supabase |

### Reference
| File | Purpose |
|------|---------|
| `docs/TODO.md` | Current tasks and priorities |
| `docs/HANDOFF.md` | Continuity between sessions |
| `docs/MAINTENANCE.md` | Maintenance procedures |

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

## 🛠️ Development

### Running the ETL

```bash
# Full ETL (all games)
python run_etl.py

# Clean slate (delete output, then run)
python run_etl.py --wipe

# Process specific games
python run_etl.py --games 18969 18977

# Check status
python run_etl.py --status
```

### Validation

```bash
# Quick validation
python validate.py --quick

# Full validation
python validate.py
```

### Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for:
- Code standards
- Development workflow
- Pull request process
- Testing guidelines

---

## 📋 Next Steps

1. **Set up your environment** - See [SETUP.md](docs/SETUP.md)
2. **Run your first ETL** - See [QUICK_START.md](docs/QUICK_START.md)
3. **Explore the data** - Check `data/output/` for generated tables
4. **Deploy to Supabase** - Follow [SUPABASE_RESET_GAMEPLAN.md](docs/SUPABASE_RESET_GAMEPLAN.md)
5. **Build dashboard** - Use [NEXTJS_DASHBOARD_GUIDE.md](docs/NEXTJS_DASHBOARD_GUIDE.md)

---

## 📞 Support

- **Documentation**: See `docs/` directory
- **Issues**: Check existing issues or create new one
- **Questions**: Review [HANDOFF.md](docs/HANDOFF.md) for known issues

---

*BenchSight v29.0 - NORAD Hockey Analytics*
