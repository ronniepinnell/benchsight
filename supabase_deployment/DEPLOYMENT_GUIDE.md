# BenchSight Supabase Deployment Guide

## 📋 Pre-Deployment Checklist

Before starting deployment, ensure you have:

- [ ] Supabase project URL: `https://uuaowslhpgyiudmbvqze.supabase.co`
- [ ] Database password (from Supabase dashboard)
- [ ] Service role API key (for bulk data loading)
- [ ] psql or Supabase CLI installed
- [ ] CSV files in `/data/output/` directory

---

## 🔧 Option 1: Using Supabase SQL Editor (Web UI)

### Step 1: Drop Existing Tables
1. Go to Supabase Dashboard → SQL Editor
2. Copy and run contents of `sql/00_drop_all_tables.sql`

### Step 2: Create Dimension Tables
1. Copy and run contents of `sql/01_create_dim_tables.sql`
2. Verify tables created: Check Table Editor sidebar

### Step 3: Create Fact Tables
1. Copy and run contents of `sql/02_create_fact_tables.sql`
2. Verify all 12 tables exist

### Step 4: Import Data
For each table, use the Table Editor import feature:

**Load Order (IMPORTANT):**
1. dim_player ← `data/output/dim_player.csv`
2. dim_team ← `data/output/dim_team.csv`
3. dim_schedule ← `data/output/dim_schedule.csv`
4. fact_shifts ← `data/output/fact_shifts.csv`
5. fact_events ← `data/output/fact_events.csv`
6. fact_events_player ← `data/output/fact_events_player.csv`
7. fact_shifts_player ← `data/output/fact_shifts_player.csv`
8. fact_player_game_stats ← `data/output/fact_player_game_stats.csv`
9. fact_team_game_stats ← `data/output/fact_team_game_stats.csv`
10. fact_goalie_game_stats ← `data/output/fact_goalie_game_stats.csv`
11. fact_h2h ← `data/output/fact_h2h.csv`
12. fact_wowy ← `data/output/fact_wowy.csv`

### Step 5: Create Indexes
1. Copy and run contents of `sql/03_create_indexes.sql`

### Step 6: Add Foreign Keys
1. Copy and run contents of `sql/04_add_foreign_keys.sql`
2. Note: Some FKs may fail if data has orphans (see troubleshooting)

### Step 7: Validate
1. Run `sql/05_validate_data.sql`
2. Check all counts match expected values
3. Verify no orphan records

---

## 🔧 Option 2: Using psql (Command Line)

### Get Connection String
From Supabase Dashboard → Settings → Database → Connection String (URI)

Format: `postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres`

### Connect
```bash
psql "postgresql://postgres:[PASSWORD]@db.uuaowslhpgyiudmbvqze.supabase.co:5432/postgres"
```

### Execute SQL Files
```bash
# Drop existing tables
\i sql/00_drop_all_tables.sql

# Create tables
\i sql/01_create_dim_tables.sql
\i sql/02_create_fact_tables.sql

# Load data (from local CSV files)
\copy dim_player FROM 'data/output/dim_player.csv' WITH CSV HEADER;
\copy dim_team FROM 'data/output/dim_team.csv' WITH CSV HEADER;
\copy dim_schedule FROM 'data/output/dim_schedule.csv' WITH CSV HEADER;
\copy fact_shifts FROM 'data/output/fact_shifts.csv' WITH CSV HEADER;
\copy fact_events FROM 'data/output/fact_events.csv' WITH CSV HEADER;
\copy fact_events_player FROM 'data/output/fact_events_player.csv' WITH CSV HEADER;
\copy fact_shifts_player FROM 'data/output/fact_shifts_player.csv' WITH CSV HEADER;
\copy fact_player_game_stats FROM 'data/output/fact_player_game_stats.csv' WITH CSV HEADER;
\copy fact_team_game_stats FROM 'data/output/fact_team_game_stats.csv' WITH CSV HEADER;
\copy fact_goalie_game_stats FROM 'data/output/fact_goalie_game_stats.csv' WITH CSV HEADER;
\copy fact_h2h FROM 'data/output/fact_h2h.csv' WITH CSV HEADER;
\copy fact_wowy FROM 'data/output/fact_wowy.csv' WITH CSV HEADER;

# Create indexes and constraints
\i sql/03_create_indexes.sql
\i sql/04_add_foreign_keys.sql

# Validate
\i sql/05_validate_data.sql
```

---

## 🔧 Option 3: Using Python Script

```python
import pandas as pd
from supabase import create_client
import os

# Configuration
SUPABASE_URL = "https://uuaowslhpgyiudmbvqze.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")  # Use service role key

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Load order
tables = [
    ("dim_player", "data/output/dim_player.csv"),
    ("dim_team", "data/output/dim_team.csv"),
    ("dim_schedule", "data/output/dim_schedule.csv"),
    ("fact_shifts", "data/output/fact_shifts.csv"),
    ("fact_events", "data/output/fact_events.csv"),
    ("fact_events_player", "data/output/fact_events_player.csv"),
    ("fact_shifts_player", "data/output/fact_shifts_player.csv"),
    ("fact_player_game_stats", "data/output/fact_player_game_stats.csv"),
    ("fact_team_game_stats", "data/output/fact_team_game_stats.csv"),
    ("fact_goalie_game_stats", "data/output/fact_goalie_game_stats.csv"),
    ("fact_h2h", "data/output/fact_h2h.csv"),
    ("fact_wowy", "data/output/fact_wowy.csv"),
]

for table_name, csv_path in tables:
    print(f"Loading {table_name}...")
    df = pd.read_csv(csv_path)
    
    # Convert NaN to None for JSON serialization
    df = df.where(pd.notnull(df), None)
    
    # Insert in batches
    batch_size = 500
    records = df.to_dict(orient='records')
    
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        supabase.table(table_name).upsert(batch).execute()
    
    print(f"  Loaded {len(records)} records")

print("Done!")
```

---

## 🚨 Troubleshooting

### Error: Duplicate Key Violation
**Cause:** Primary key already exists in table
**Solution:** 
```sql
-- Delete duplicates, keeping first occurrence
DELETE FROM fact_events a
USING fact_events b
WHERE a.ctid < b.ctid 
AND a.event_key = b.event_key;
```

### Error: Foreign Key Constraint Violation
**Cause:** Referenced record doesn't exist in parent table
**Solution:** 
```sql
-- Find orphaned records
SELECT DISTINCT game_id 
FROM fact_events 
WHERE game_id NOT IN (SELECT game_id FROM dim_schedule);

-- Option 1: Delete orphans
DELETE FROM fact_events 
WHERE game_id NOT IN (SELECT game_id FROM dim_schedule);

-- Option 2: Add missing parent record
INSERT INTO dim_schedule (game_id) VALUES (18969);
```

### Error: Data Type Mismatch
**Cause:** CSV value doesn't match column type
**Solution:** Pre-process CSV to fix data types, or adjust column definition

### Error: Table Already Exists
**Solution:** Run `sql/00_drop_all_tables.sql` first

### Error: Column Count Mismatch
**Cause:** CSV has different columns than table definition
**Solution:** Regenerate SQL using `python generate_sql.py`

---

## ✅ Verification Queries

After deployment, run these to verify success:

```sql
-- Quick health check
SELECT 
    'dim_player' as tbl, COUNT(*) as cnt FROM dim_player
UNION ALL SELECT 'dim_team', COUNT(*) FROM dim_team
UNION ALL SELECT 'dim_schedule', COUNT(*) FROM dim_schedule
UNION ALL SELECT 'fact_events', COUNT(*) FROM fact_events
UNION ALL SELECT 'fact_player_game_stats', COUNT(*) FROM fact_player_game_stats
ORDER BY tbl;

-- Test a join
SELECT 
    e.event_type,
    p.player_full_name,
    s.home_team_name,
    s.away_team_name
FROM fact_events e
JOIN dim_schedule s ON e.game_id = s.game_id
JOIN fact_events_player ep ON e.event_key = ep.event_key
JOIN dim_player p ON ep.player_id = p.player_id
WHERE e.event_type = 'Goal'
LIMIT 10;
```

---

## 📊 Expected Row Counts

| Table | Expected Rows |
|-------|---------------|
| dim_player | 337 |
| dim_team | 26 |
| dim_schedule | 562 |
| fact_shifts | 672 |
| fact_events | 5,833 |
| fact_events_player | 11,635 |
| fact_shifts_player | 4,626 |
| fact_player_game_stats | 107 |
| fact_team_game_stats | 8 |
| fact_goalie_game_stats | 8 |
| fact_h2h | 684 |
| fact_wowy | 641 |
| **TOTAL** | **24,654** |

---

## 🔒 RLS Policies (Optional)

To enable public read access:

```sql
-- Enable RLS on all tables
ALTER TABLE dim_player ENABLE ROW LEVEL SECURITY;
ALTER TABLE dim_team ENABLE ROW LEVEL SECURITY;
ALTER TABLE dim_schedule ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_events_player ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_shifts ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_shifts_player ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_player_game_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_team_game_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_goalie_game_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_h2h ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_wowy ENABLE ROW LEVEL SECURITY;

-- Create public read policies
CREATE POLICY "Public read" ON dim_player FOR SELECT USING (true);
CREATE POLICY "Public read" ON dim_team FOR SELECT USING (true);
CREATE POLICY "Public read" ON dim_schedule FOR SELECT USING (true);
CREATE POLICY "Public read" ON fact_events FOR SELECT USING (true);
CREATE POLICY "Public read" ON fact_events_player FOR SELECT USING (true);
CREATE POLICY "Public read" ON fact_shifts FOR SELECT USING (true);
CREATE POLICY "Public read" ON fact_shifts_player FOR SELECT USING (true);
CREATE POLICY "Public read" ON fact_player_game_stats FOR SELECT USING (true);
CREATE POLICY "Public read" ON fact_team_game_stats FOR SELECT USING (true);
CREATE POLICY "Public read" ON fact_goalie_game_stats FOR SELECT USING (true);
CREATE POLICY "Public read" ON fact_h2h FOR SELECT USING (true);
CREATE POLICY "Public read" ON fact_wowy FOR SELECT USING (true);
```

---

## 📞 Support

- **ETL Issues:** Re-run `python etl.py` then `scripts/fix_data_integrity.py`
- **Schema Questions:** See `docs/SCHEMA_AND_ERD.md`
- **Business Rules:** See `docs/MASTER_INSTRUCTIONS.md`

---

*Last Updated: December 2024*
