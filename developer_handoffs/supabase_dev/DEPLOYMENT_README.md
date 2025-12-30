# BenchSight Deployment Guide

## Quick Start

```bash
# 1. Create tables
psql $DATABASE_URL -f sql/01_RECREATE_SCHEMA.sql

# 2. Load all data
python scripts/flexible_loader.py --scope full --operation replace

# 3. Verify
psql $DATABASE_URL -c "SELECT * FROM get_all_table_counts();"
```

---

## Connection Details

```
Supabase Project: https://uuaowslhpgyiudmbvqze.supabase.co
Dashboard: https://supabase.com/dashboard/project/uuaowslhpgyiudmbvqze

Connection String (psql):
  psql "postgresql://postgres:[PASSWORD]@db.uuaowslhpgyiudmbvqze.supabase.co:5432/postgres"

Environment Variables:
  export SUPABASE_URL="https://uuaowslhpgyiudmbvqze.supabase.co"
  export SUPABASE_SERVICE_KEY="your-service-role-key"
```

---

## SQL Scripts Reference

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `00_MASTER_SQL_OPERATIONS.sql` | Complete reference with all sections | Documentation, selective execution |
| `01_RECREATE_SCHEMA.sql` | Drop & recreate all tables | Fresh start, schema changes |
| `02_QUICK_OPERATIONS.sql` | Common operations | Day-to-day management |

---

## Deployment Options

### Option A: Supabase Web UI (Easiest)

1. Go to SQL Editor in Supabase Dashboard
2. Paste and run `01_RECREATE_SCHEMA.sql`
3. Go to Table Editor → Import CSV for each table (in order!)
4. Run validation from `02_QUICK_OPERATIONS.sql`

### Option B: psql Command Line

```bash
# Connect
psql "postgresql://postgres:[PASSWORD]@db.uuaowslhpgyiudmbvqze.supabase.co:5432/postgres"

# Create schema
\i sql/01_RECREATE_SCHEMA.sql

# Load CSVs (in dependency order)
\copy dim_player FROM 'data/output/dim_player.csv' CSV HEADER;
\copy dim_team FROM 'data/output/dim_team.csv' CSV HEADER;
\copy dim_schedule FROM 'data/output/dim_schedule.csv' CSV HEADER;
\copy fact_shifts FROM 'data/output/fact_shifts.csv' CSV HEADER;
\copy fact_events FROM 'data/output/fact_events.csv' CSV HEADER;
\copy fact_events_player FROM 'data/output/fact_events_player.csv' CSV HEADER;
\copy fact_shifts_player FROM 'data/output/fact_shifts_player.csv' CSV HEADER;
\copy fact_player_game_stats FROM 'data/output/fact_player_game_stats.csv' CSV HEADER;
\copy fact_team_game_stats FROM 'data/output/fact_team_game_stats.csv' CSV HEADER;
\copy fact_goalie_game_stats FROM 'data/output/fact_goalie_game_stats.csv' CSV HEADER;
\copy fact_h2h FROM 'data/output/fact_h2h.csv' CSV HEADER;
\copy fact_wowy FROM 'data/output/fact_wowy.csv' CSV HEADER;

# Verify
SELECT * FROM get_all_table_counts();
```

### Option C: Python Loader (Recommended)

```bash
# Install dependencies
pip install supabase pandas

# Set environment
export SUPABASE_URL="https://uuaowslhpgyiudmbvqze.supabase.co"
export SUPABASE_SERVICE_KEY="your-service-role-key"

# Full refresh
python scripts/flexible_loader.py --scope full --operation replace

# Or specific scopes
python scripts/flexible_loader.py --scope category --category dims --operation upsert
python scripts/flexible_loader.py --scope game --game-id 18969 --operation replace
python scripts/flexible_loader.py --scope table --table fact_h2h --operation append

# Check counts
python scripts/flexible_loader.py --counts
```

---

## Flexible Loading Matrix

| Scope | Options | Use Case |
|-------|---------|----------|
| `--scope full` | All tables | Fresh start |
| `--scope category --category dims` | Dimensions only | Update player/team master data |
| `--scope category --category all_facts` | All fact tables | Recalculate after ETL |
| `--scope category --category stats_facts` | Stats tables | Just update aggregations |
| `--scope game --game-id XXXXX` | Single game | Add/fix one game |
| `--scope table --table TABLE_NAME` | Single table | Testing, targeted fix |

| Operation | Behavior |
|-----------|----------|
| `--operation replace` | Delete existing, insert new |
| `--operation append` | Insert new (fail on duplicates) |
| `--operation upsert` | Insert or update existing |

---

## Load Order (FK Dependencies)

```
1. dim_player       ←─┐
2. dim_team         ←─┼─ No dependencies
3. dim_schedule     ←─┘
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

## Validation Checklist

Run after every load:

```sql
-- Row counts
SELECT * FROM get_all_table_counts();

-- Expected totals
-- dim_player: 337
-- dim_team: 26
-- dim_schedule: 562
-- fact_shifts: 672
-- fact_events: 5,833
-- fact_events_player: 11,635
-- fact_shifts_player: 4,626
-- fact_player_game_stats: 107
-- fact_team_game_stats: 8
-- fact_goalie_game_stats: 8
-- fact_h2h: 684
-- fact_wowy: 641

-- Games with data
SELECT * FROM get_games_status();

-- Validation queries
-- (from 02_QUICK_OPERATIONS.sql)
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "duplicate key" | Use `--operation upsert` or delete first |
| "foreign key violation" | Load dimensions before facts |
| "column doesn't exist" | Regenerate SQL from CSV with `generate_sql.py` |
| "permission denied" | Use service_role key, not anon key |
| "connection refused" | Check Supabase status, verify URL/key |

### Emergency Reset

```sql
-- Delete one game
SELECT delete_game_data(18969);

-- Truncate all facts (keep dims)
SELECT truncate_all_facts();

-- Full reset (need to recreate tables)
DROP TABLE IF EXISTS ... CASCADE;  -- (see 01_RECREATE_SCHEMA.sql)
```

---

## Post-Deployment Tasks

1. **Verify data quality** - Run validation queries
2. **Add foreign keys** (optional) - For referential integrity
3. **Enable RLS** (optional) - For multi-tenant security
4. **Create API keys** - Separate keys for dashboard/tracker/portal
5. **Test integrations** - Verify tracker writes, dashboard reads

---

## File Locations

```
SQL Scripts:
  sql/00_MASTER_SQL_OPERATIONS.sql   # Complete reference
  sql/01_RECREATE_SCHEMA.sql         # Drop & create
  sql/02_QUICK_OPERATIONS.sql        # Common operations
  supabase_deployment/sql/           # Generated from CSV

Python Scripts:
  scripts/flexible_loader.py         # Main loader
  supabase_deployment/generate_sql.py # Regenerate DDL

Documentation:
  docs/MASTER_PROJECT_STRATEGY.md    # Complete strategy
  supabase_deployment/LOADING_STRATEGY.md # Integration details
  developer_handoffs/                # Role-specific guides
```

---

*Last Updated: December 2024*
