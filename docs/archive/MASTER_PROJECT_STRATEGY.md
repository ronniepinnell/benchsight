# BenchSight Master Project Strategy

## Executive Summary

BenchSight is a comprehensive hockey analytics platform for the NORAD recreational hockey league. This document provides the complete strategy for deployment, integration, and ongoing operations across all system components.

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              BENCHSIGHT SYSTEM ARCHITECTURE                              │
└─────────────────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────┐                                      ┌──────────────────┐
    │   DATA SOURCES   │                                      │    CONSUMERS     │
    └────────┬─────────┘                                      └────────┬─────────┘
             │                                                         │
    ┌────────▼─────────┐                                      ┌────────▼─────────┐
    │  Excel Tracking  │                                      │    Dashboard     │
    │  Files (.xlsx)   │──┐                              ┌────│    (React/Vue)   │
    └──────────────────┘  │                              │    └──────────────────┘
                          │                              │
    ┌──────────────────┐  │    ┌──────────────────┐     │    ┌──────────────────┐
    │   BLB Tables     │──┼───►│   ETL PIPELINE   │─────┼───►│    Power BI      │
    │  (Master Data)   │  │    │    (Python)      │     │    │   Dashboards     │
    └──────────────────┘  │    └────────┬─────────┘     │    └──────────────────┘
                          │             │               │
    ┌──────────────────┐  │    ┌────────▼─────────┐     │    ┌──────────────────┐
    │ Live Tracker     │──┴───►│    SUPABASE      │◄────┴───►│   Admin Portal   │
    │   (HTML/JS)      │───────│   PostgreSQL     │──────────│    (FastAPI)     │
    └──────────────────┘       └──────────────────┘          └──────────────────┘
                                       │
                               ┌───────▼───────┐
                               │   16 Tables   │
                               │   24,654 rows │
                               │   742 columns │
                               └───────────────┘
```

---

## 📁 Project Structure

```
benchsight_project/
├── 📋 ROOT DOCUMENTATION
│   ├── README.md                    # Project overview
│   ├── START_HERE.md                # Quick start guide
│   └── HANDOFF.md                   # Session handoff notes
│
├── 📊 data/
│   ├── BLB_Tables.xlsx              # Master data (rosters, schedules)
│   ├── raw/games/{game_id}/         # Per-game tracking files
│   └── output/                      # ETL output CSVs (100+ files)
│       ├── dim_*.csv                # Dimension tables
│       ├── fact_*.csv               # Fact tables
│       └── data_dictionary/         # Column definitions
│
├── 🔧 src/                          # Python source code
│   ├── pipeline/                    # ETL pipeline modules
│   ├── transformation/              # Data transformations
│   ├── analytics/                   # Stats calculations
│   └── ingestion/                   # Data loading
│
├── 📝 scripts/                      # Utility scripts
│   ├── etl_validation.py            # Data quality checks
│   ├── fix_data_integrity.py        # Data fixes
│   ├── supabase_loader.py           # Database upload
│   └── flexible_loader.py           # Flexible load operations
│
├── 🧪 tests/                        # Test suite (pytest)
│   ├── test_etl.py
│   ├── test_stats_calculations.py
│   └── test_ground_truth.py
│
├── 💾 sql/                          # SQL scripts
│   ├── 00_MASTER_SQL_OPERATIONS.sql # Complete SQL reference
│   └── ddl/                         # Table definitions
│
├── 🚀 supabase_deployment/          # Supabase-specific files
│   ├── sql/                         # Generated SQL scripts
│   ├── scripts/                     # Loader scripts
│   └── LOADING_STRATEGY.md          # Deployment strategy
│
├── 📦 developer_handoffs/           # Role-specific packages
│   ├── supabase_dev/                # Database developer
│   ├── portal_dev/                  # Admin portal developer
│   ├── tracker_dev/                 # Game tracker developer
│   └── dashboard_dev/               # Dashboard developer
│
├── 🖥️ dashboard/                    # Dashboard HTML files
├── 🎮 tracker/                      # Tracker HTML files (v16-v19)
├── 📊 powerbi/                      # Power BI integration
├── 📄 docs/                         # Documentation
└── 🌐 html/                         # Static HTML exports
```

---

## 🗄️ Database Schema

### Table Inventory

| Category | Table | Rows | Columns | Description |
|----------|-------|------|---------|-------------|
| **Dimensions** | dim_player | 337 | 28 | Player master data |
| | dim_team | 26 | 15 | Team definitions |
| | dim_schedule | 562 | 44 | Game schedule (all seasons) |
| **Core Facts** | fact_shifts | 672 | 63 | Shift-level data |
| | fact_events | 5,833 | 54 | Event-level data |
| | fact_events_player | 11,635 | 63 | Player-event mapping |
| | fact_shifts_player | 4,626 | 35 | Player-shift mapping |
| **Stats Facts** | fact_player_game_stats | 107 | **317** | Player game stats |
| | fact_team_game_stats | 8 | 52 | Team game stats |
| | fact_goalie_game_stats | 8 | 19 | Goalie game stats |
| **Analytics** | fact_h2h | 684 | 24 | Head-to-head analysis |
| | fact_wowy | 641 | 28 | With/without you analysis |
| **Staging** | staging_events | - | 30 | Tracker event writes |
| | staging_shifts | - | 28 | Tracker shift writes |
| **Admin** | etl_queue | - | 13 | ETL job queue |
| | load_history | - | 15 | Audit trail |

**Total: 24,654 rows across 12 production tables (742 unique columns)**

### Primary Key Formats

```
dim_player:             P{player_id}          → P100192
dim_team:               T{team_id}            → T15
dim_schedule:           {game_id}             → 18969

fact_shifts:            S{game_id}{index:05d} → S1896900001
fact_events:            E{game_id}{index:05d} → E1896900001
fact_player_game_stats: PG{game_id}{player}   → PG18969P100192
fact_team_game_stats:   TG{game_id}{team}     → TG18969T15
fact_goalie_game_stats: GG{game_id}{player}   → GG18969P100192
fact_h2h:               H2H{game}{p1}{p2}     → H2H18969P100192P100193
fact_wowy:              WOWY{game}{p1}{p2}    → WOWY18969P100192P100193
```

### Load Order (FK Dependencies)

```
1. dim_player       ─┐
2. dim_team         ─┼─ No dependencies (load first)
3. dim_schedule     ─┘
4. fact_shifts      ← dim_schedule
5. fact_events      ← dim_schedule, fact_shifts
6. fact_events_player ← fact_events, dim_player
7. fact_shifts_player ← fact_shifts, dim_player
8. fact_player_game_stats ← dim_player, dim_schedule
9. fact_team_game_stats ← dim_team, dim_schedule
10. fact_goalie_game_stats ← dim_player, dim_schedule
11. fact_h2h        ← dim_player, dim_schedule
12. fact_wowy       ← dim_player, dim_schedule
```

---

## 🔄 Data Flow

### Write Path (Data Entry)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              WRITE PATH                                      │
└─────────────────────────────────────────────────────────────────────────────┘

     LIVE TRACKING                     BATCH PROCESSING
     ─────────────                     ────────────────

┌──────────────┐                    ┌──────────────┐
│   TRACKER    │                    │ Excel Files  │
│  (HTML/JS)   │                    │   (.xlsx)    │
└──────┬───────┘                    └──────┬───────┘
       │                                   │
       │ Real-time writes                  │ Batch load
       │                                   │
       ▼                                   ▼
┌──────────────┐                    ┌──────────────┐
│   STAGING    │                    │     ETL      │
│   TABLES     │────────────────────│   PIPELINE   │
│  (Supabase)  │    ETL processes   │   (Python)   │
└──────────────┘    staging data    └──────┬───────┘
                                           │
                                           │ Transforms & loads
                                           ▼
                                    ┌──────────────┐
                                    │    FACT      │
                                    │   TABLES     │
                                    │  (Supabase)  │
                                    └──────────────┘
```

### Read Path (Data Consumption)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              READ PATH                                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Dashboard   │     │  Power BI    │     │    Portal    │
│  (React/Vue) │     │              │     │  (FastAPI)   │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       │ REST/Realtime      │ DirectQuery        │ Service Role
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │   SUPABASE   │
                     │  PostgreSQL  │
                     │              │
                     │  fact_*      │
                     │  dim_*       │
                     └──────────────┘
```

---

## 👥 Developer Roles

### Role Matrix

| Role | Primary Responsibility | Writes To | Reads From |
|------|----------------------|-----------|------------|
| **Supabase Dev** | Database schema, tables, functions | All tables (DDL) | Schema definitions |
| **Tracker Dev** | Live game entry interface | staging_events, staging_shifts | dim_player, dim_schedule |
| **Portal Dev** | Admin UI, ETL orchestration | etl_queue, load_history | All tables |
| **Dashboard Dev** | Analytics visualization | (Read-only) | fact_*, dim_* |

### Development Timeline

```
WEEK 1: FOUNDATION
├── Supabase Dev: Create all tables, load CSVs, validate
└── Checkpoint: Database ready for other developers

WEEK 2-3: PARALLEL DEVELOPMENT
├── Portal Dev: FastAPI backend, ETL control, table viewer
├── Tracker Dev: Fix roster loading, game dropdown, event ordering
└── Dashboard Dev: Standings, leaders, team/player pages

WEEK 4: INTEGRATION
├── All: End-to-end testing (Track → ETL → Display)
├── All: Bug fixes and polish
└── All: Demo and deploy
```

---

## 🚀 Deployment Strategy

### Phase 1: Database Setup (Week 1)

```bash
# 1. Create tables
psql $DATABASE_URL -f sql/00_MASTER_SQL_OPERATIONS.sql

# 2. Load CSVs (in dependency order)
python scripts/flexible_loader.py --scope full --operation replace

# 3. Verify
SELECT * FROM get_all_table_counts();
```

### Phase 2: Flexible Loading (Ongoing)

| Scenario | Command |
|----------|---------|
| Full refresh | `--scope full --operation replace` |
| Add new game | `--scope game --game-id 18999 --operation append` |
| Fix game data | `--scope game --game-id 18969 --operation replace` |
| Update players | `--scope category --category dims --operation upsert` |
| Reload stats | `--scope category --category stats_facts --operation replace` |

### Phase 3: Live Operations

```
                    ┌─────────────────┐
                    │  ADMIN PORTAL   │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Run ETL        │ │  Upload CSV     │ │  Monitor Health │
│  [Button]       │ │  [Drag & Drop]  │ │  [Dashboard]    │
└─────────────────┘ └─────────────────┘ └─────────────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                    ┌────────▼────────┐
                    │    SUPABASE     │
                    │    DATABASE     │
                    └─────────────────┘
```

---

## 📈 Stat Categories

### Core Stats (All Players)
- Goals, Assists, Points, +/-
- Shots (attempts, on goal, blocked, missed)
- Shooting percentage
- TOI (total, per game, per shift)

### Possession Stats
- Corsi (CF, CA, CF%)
- Fenwick (FF, FA, FF%)
- Zone entries/exits
- Giveaways, Takeaways

### Situational Stats
- 5v5, Power Play, Penalty Kill
- Empty net situations
- Score state (leading, trailing, tied)

### Advanced Analytics
- H2H (player vs player when on ice together)
- WOWY (with or without you impact)
- Per-60 rates for all counting stats
- Expected goals (future)

### Goalie-Specific
- Save percentage, GAA
- Saves by period
- Shot quality faced (future)

---

## 🔐 Security Model

### Access Levels

| Role | Key Type | Permissions |
|------|----------|-------------|
| Dashboard | anon | SELECT on fact_*, dim_* |
| Tracker | anon | INSERT on staging_* |
| Portal | service_role | ALL on ALL tables |
| ETL | service_role | ALL on ALL tables |

### Best Practices
1. Never expose service_role key to frontend
2. Use Row Level Security (RLS) for multi-tenant scenarios
3. Log all destructive operations to load_history
4. Rate limit script execution

---

## 🧪 Validation Checklist

### After Every Load
- [ ] Row counts match expected
- [ ] No duplicate primary keys
- [ ] No orphaned foreign keys
- [ ] Percentage values in valid ranges (0-100 or 0-1)
- [ ] Business logic: points = goals + assists

### Ground Truth Validation
- [ ] Goals match noradhockey.com box scores
- [ ] Player names match rosters
- [ ] Game dates match schedule

### ETL Validation
```bash
pytest tests/ -v --tb=short
python scripts/etl_validation.py
python scripts/validate_against_ground_truth.py
```

---

## 📚 Documentation Index

| Document | Location | Purpose |
|----------|----------|---------|
| Master SQL | sql/00_MASTER_SQL_OPERATIONS.sql | Complete SQL reference |
| Loading Strategy | supabase_deployment/LOADING_STRATEGY.md | Integration architecture |
| Deployment Guide | supabase_deployment/DEPLOYMENT_GUIDE.md | Step-by-step deployment |
| Schema & ERD | docs/SCHEMA.md | Database design |
| Stats Catalog | docs/STATS_CATALOG_COMPLETE.md | All statistics definitions |
| Tracker Guide | developer_handoffs/tracker_dev/docs/TRACKER_DEV_COMPLETE_GUIDE.md | Event tracking rules |
| Dashboard Guide | developer_handoffs/dashboard_dev/docs/DASHBOARD_DEV_COMPLETE_GUIDE.md | Dashboard specifications |
| 4-Role Workflow | developer_handoffs/DEVELOPER_WORKFLOW_4ROLES.md | Team coordination |

---

## 🎯 Success Metrics

### Phase 1 (Foundation)
- [ ] All 12 production tables created
- [ ] 24,654 rows loaded successfully
- [ ] Validation queries pass
- [ ] Indexes created for performance

### Phase 2 (Operations)
- [ ] ETL can be triggered via Portal
- [ ] New games can be added without SQL
- [ ] Data corrections work via flexible loader
- [ ] Full audit trail in load_history

### Phase 3 (Production)
- [ ] Tracker writes directly to Supabase
- [ ] Dashboard shows real-time updates
- [ ] < 3 second query response times
- [ ] Zero data loss incidents

---

## 🆘 Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| FK violation on load | Loading facts before dims | Use correct load order |
| Duplicate key error | Re-running insert without delete | Use upsert or delete first |
| Missing columns | Schema out of sync with CSV | Regenerate SQL from CSV |
| Slow queries | Missing indexes | Add indexes per schema |
| Connection refused | Wrong credentials | Check environment variables |

### Emergency Procedures

```sql
-- Full reset (DANGER!)
SELECT truncate_all_facts();

-- Delete single game
SELECT delete_game_data(18969);

-- Check what's loaded
SELECT * FROM get_all_table_counts();
SELECT * FROM get_games_status();
```

---

## 📞 Quick Reference

### Supabase Connection
```
URL: https://uuaowslhpgyiudmbvqze.supabase.co
Dashboard: https://supabase.com/dashboard/project/uuaowslhpgyiudmbvqze
```

### Key Commands
```bash
# Run ETL
python etl.py

# Load to Supabase
python scripts/flexible_loader.py --scope full --operation replace

# Validate
pytest tests/ -v
python scripts/etl_validation.py

# Generate SQL from CSV
python supabase_deployment/generate_sql.py
```

### Tracked Games
| Game ID | Date | Matchup | Events | Shifts |
|---------|------|---------|--------|--------|
| 18969 | 2024-12-07 | Puck Hogs vs Blades | 1,450 | 168 |
| 18977 | 2024-12-14 | Game 2 | 1,456 | 168 |
| 18981 | 2024-12-17 | Game 3 | 1,460 | 168 |
| 18987 | 2024-12-21 | Game 4 | 1,467 | 168 |

---

*Document Version: 2.0 | Last Updated: December 2024*
