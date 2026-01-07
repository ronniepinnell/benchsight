# BenchSight Supabase Integration

## Quick Start

### 1. Create Schema in Supabase

1. Go to your [Supabase Dashboard](https://supabase.com/dashboard/project/uuaowslhpgyiudmbvqze)
2. Open **SQL Editor**
3. Copy the contents of `schema.sql` 
4. Paste and run

### 2. Configure Credentials

```bash
# Copy example and edit
cp .env.example .env

# Fill in your values:
# - SUPABASE_KEY: Found in Settings > API > anon public / service_role
# - SUPABASE_DB_URL: Found in Settings > Database > Connection string
```

### 3. Install Dependencies

```bash
pip install supabase psycopg2-binary python-dotenv pandas
```

### 4. Sync Data

```bash
# Full wipe and reload (recommended for initial setup)
python supabase/sync_to_supabase.py --wipe

# Incremental sync (just add new data)
python supabase/sync_to_supabase.py

# Sync specific table
python supabase/sync_to_supabase.py --table fact_events

# Preview without changes
python supabase/sync_to_supabase.py --dry-run
```

## Files

| File | Purpose |
|------|---------|
| `schema.sql` | Complete PostgreSQL DDL for all 59 tables |
| `sync_to_supabase.py` | Script to push CSV data to Supabase |
| `generate_schema.py` | Regenerates schema.sql from current CSVs |

## Regenerating Schema

If tables change, regenerate the schema:

```bash
python supabase/generate_schema.py
```

## Connection Options

### Option A: Direct PostgreSQL (Recommended for bulk data)

```
SUPABASE_DB_URL=postgresql://postgres:PASSWORD@db.uuaowslhpgyiudmbvqze.supabase.co:5432/postgres
```

Faster for bulk inserts, uses psycopg2.

### Option B: Supabase Client (REST API)

```
SUPABASE_KEY=your-key-here
```

Works without direct DB access, uses Supabase REST API.

## Useful Views

The schema includes these pre-built views:

- `v_goals` - All goals with scorer info
- `v_player_game_summary` - Player stats per game
- `v_game_summary` - Game-level summaries

## Troubleshooting

### "relation does not exist"

Run schema.sql first to create tables.

### "permission denied"

Use service_role key instead of anon key for full access.

### Slow sync

Use direct PostgreSQL connection (SUPABASE_DB_URL) instead of REST API.

### Data type errors

Regenerate schema with `python supabase/generate_schema.py` to match current CSV structure.
