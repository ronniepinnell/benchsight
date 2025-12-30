# BenchSight Supabase Developer Handoff

## 🎯 Your Mission

Deploy and integrate BenchSight's hockey analytics data into Supabase PostgreSQL. The ETL pipeline outputs CSV files that need to be uploaded, properly structured with primary/foreign keys, and made available for dashboard and tracker applications.

---

## 📖 Required Reading (In Order)

Read these documents in sequence before starting any work:

### 1. Start Here (This README)
You're reading it. Continue below for status and issues.

### 2. Schema & ERD (`docs/SCHEMA_AND_ERD.md`)
**CRITICAL** - Understand the data model first:
- Star schema design (dim/fact tables)
- Primary key formats: `{prefix}{game_id}{5d}`
- Foreign key relationships
- Table row counts

### 3. Data Dictionaries (`data_dictionary/`)
Read in this order:
1. `dd_master_column_inventory.csv` - Overview of all 317 columns
2. `dd_fact_events.csv` - Core events table
3. `dd_fact_events_player.csv` - Player-event assignments
4. `dd_fact_player_game_stats.csv` - Player aggregations
5. `dd_fact_team_game_stats.csv` - Team aggregations
6. `dd_fact_goalie_game_stats.csv` - Goalie stats with microstats
7. `dd_fact_shifts.csv` - Shift data
8. `dd_fact_h2h.csv` - Head-to-head matchups
9. `dd_fact_wowy.csv` - With-or-without-you analysis

### 4. Master Instructions (`docs/MASTER_INSTRUCTIONS.md`)
Project overview, workflow, and business rules.

### 5. Honest Assessment (`docs/HONEST_ASSESSMENT.md`)
Current state, known issues, what works/doesn't.

---

## 🔌 Supabase Connection Details

```
Project URL: https://uuaowslhpgyiudmbvqze.supabase.co
Region: [Check Supabase dashboard]
Database: PostgreSQL 15+
```

**To get credentials:**
1. Go to Supabase Dashboard → Project Settings → Database
2. Get connection string for direct PostgreSQL access
3. Get anon/service keys for API access

---

## 📊 Current Data Status

### What Exists
| Table | Status | Rows (per game) | Notes |
|-------|--------|-----------------|-------|
| dim_player | ✅ Ready | ~30 | Player master data |
| dim_team | ✅ Ready | 2 | Team master data |
| dim_schedule | ✅ Ready | 1 | Game schedule |
| fact_events | ✅ Ready | 400-600 | Wide format events |
| fact_events_player | ✅ Ready | 1200-1800 | Long format |
| fact_shifts | ✅ Ready | 140-180 | Shift segments |
| fact_shifts_player | ✅ Ready | 1400-1800 | Player-shift |
| fact_player_game_stats | ✅ Ready | ~30 | Player aggregates |
| fact_team_game_stats | ✅ Ready | 2 | Team aggregates |
| fact_goalie_game_stats | ✅ Ready | 2 | Goalie stats |
| fact_h2h | ✅ Ready | 200-400 | Head-to-head |
| fact_wowy | ✅ Ready | 100-200 | WOWY analysis |

### Data Files Location
```
/data/output/
├── dim_player.csv
├── dim_team.csv
├── dim_schedule.csv
├── fact_events.csv
├── fact_events_player.csv
├── fact_shifts.csv
├── fact_shifts_player.csv
├── fact_player_game_stats.csv
├── fact_team_game_stats.csv
├── fact_goalie_game_stats.csv
├── fact_h2h.csv
├── fact_wowy.csv
└── data_dictionary/
```

---

## ⚠️ Known Issues to Fix

### CRITICAL (Must Fix Before Deploy)

#### 1. Primary Key Uniqueness
**Issue:** Some tables may have duplicate keys from re-runs
**Solution:** 
```sql
-- Check for duplicates before upload
SELECT event_key, COUNT(*) 
FROM fact_events 
GROUP BY event_key 
HAVING COUNT(*) > 1;

-- Delete duplicates, keeping first
DELETE FROM fact_events a
USING fact_events b
WHERE a.ctid < b.ctid 
AND a.event_key = b.event_key;
```

#### 2. Foreign Key Constraints
**Issue:** Some FKs may reference non-existent PKs
**Solution:** Load dimension tables FIRST, then fact tables
```
Load Order:
1. dim_player
2. dim_team
3. dim_schedule
4. fact_shifts (depends on dim_schedule)
5. fact_events (depends on dim_schedule, fact_shifts)
6. fact_events_player (depends on fact_events, dim_player)
7. fact_shifts_player (depends on fact_shifts, dim_player)
8. fact_player_game_stats (depends on dim_player, dim_schedule)
9. fact_team_game_stats (depends on dim_team, dim_schedule)
10. fact_goalie_game_stats (depends on dim_player, dim_schedule)
11. fact_h2h (depends on dim_player, dim_schedule)
12. fact_wowy (depends on dim_player, dim_schedule)
```

#### 3. Null Handling
**Issue:** Some columns have nulls that should be empty strings or defaults
**Solution:**
```sql
-- Example: Replace nulls in event_detail
UPDATE fact_events 
SET event_detail = '' 
WHERE event_detail IS NULL;
```

### IMPORTANT (Should Fix)

#### 4. Data Type Mismatches
**Issue:** CSV imports may interpret types incorrectly
**Solution:** Create tables with explicit types before import:
```sql
CREATE TABLE fact_events (
    event_key VARCHAR(20) PRIMARY KEY,
    game_id INTEGER NOT NULL,
    event_index INTEGER NOT NULL,
    period INTEGER,
    event_type VARCHAR(50),
    event_detail VARCHAR(100),
    event_successful CHAR(1),
    -- ... see full schema in docs
);
```

#### 5. Index Creation
**Issue:** No indexes = slow queries
**Solution:** Add after data load:
```sql
CREATE INDEX idx_events_game ON fact_events(game_id);
CREATE INDEX idx_events_type ON fact_events(event_type);
CREATE INDEX idx_events_player_player ON fact_events_player(player_id);
CREATE INDEX idx_player_stats_game ON fact_player_game_stats(game_id);
CREATE INDEX idx_player_stats_player ON fact_player_game_stats(player_id);
CREATE INDEX idx_team_stats_game ON fact_team_game_stats(game_id);
```

### NICE TO HAVE

#### 6. Row Level Security (RLS)
**Consideration:** If public access needed
```sql
-- Enable RLS
ALTER TABLE fact_player_game_stats ENABLE ROW LEVEL SECURITY;

-- Allow public read
CREATE POLICY "Public read access" ON fact_player_game_stats
    FOR SELECT USING (true);
```

---

## 🛠️ Deployment Steps

### Step 1: Create Tables
Run SQL to create all tables with proper types and constraints.
See `docs/SCHEMA_AND_ERD.md` for full DDL.

### Step 2: Load Dimension Tables
```bash
# Using Supabase CLI or psql
\copy dim_player FROM 'data/output/dim_player.csv' WITH CSV HEADER;
\copy dim_team FROM 'data/output/dim_team.csv' WITH CSV HEADER;
\copy dim_schedule FROM 'data/output/dim_schedule.csv' WITH CSV HEADER;
```

### Step 3: Load Fact Tables (in order)
```bash
\copy fact_shifts FROM 'data/output/fact_shifts.csv' WITH CSV HEADER;
\copy fact_events FROM 'data/output/fact_events.csv' WITH CSV HEADER;
# ... continue in dependency order
```

### Step 4: Add Constraints
```sql
ALTER TABLE fact_events 
    ADD CONSTRAINT fk_events_game 
    FOREIGN KEY (game_id) REFERENCES dim_schedule(game_id);

ALTER TABLE fact_events_player 
    ADD CONSTRAINT fk_events_player_event 
    FOREIGN KEY (event_key) REFERENCES fact_events(event_key);
-- ... add all FKs
```

### Step 5: Create Indexes
See Issue #5 above.

### Step 6: Validate Data
```sql
-- Check row counts match CSVs
SELECT 'fact_events' as tbl, COUNT(*) FROM fact_events
UNION ALL
SELECT 'fact_player_game_stats', COUNT(*) FROM fact_player_game_stats
-- ... etc
```

### Step 7: Test Queries
```sql
-- Test: Get player stats for a game
SELECT * FROM fact_player_game_stats 
WHERE game_id = 18969 
ORDER BY points DESC;

-- Test: Get team comparison
SELECT * FROM fact_team_game_stats 
WHERE game_id = 18969;

-- Test: Join player to events
SELECT e.event_type, ep.player_id, p.player_name
FROM fact_events e
JOIN fact_events_player ep ON e.event_key = ep.event_key
JOIN dim_player p ON ep.player_id = p.player_id
WHERE e.game_id = 18969
LIMIT 10;
```

---

## 📁 Files in This Handoff

```
supabase_dev/
├── README.md                    # This file
├── NEXT_PROMPT.md               # Prompt for continuing work
├── docs/
│   ├── SCHEMA_AND_ERD.md        # Database schema
│   ├── MASTER_INSTRUCTIONS.md   # Project overview
│   └── HONEST_ASSESSMENT.md     # Current state
├── data_dictionary/
│   ├── dd_master_column_inventory.csv
│   ├── dd_fact_events.csv
│   ├── dd_fact_events_player.csv
│   ├── dd_fact_player_game_stats.csv
│   ├── dd_fact_team_game_stats.csv
│   ├── dd_fact_goalie_game_stats.csv
│   ├── dd_fact_shifts.csv
│   ├── dd_fact_h2h.csv
│   └── dd_fact_wowy.csv
└── sql/
    ├── 01_create_tables.sql     # DDL scripts
    ├── 02_load_data.sql         # Import commands
    ├── 03_add_constraints.sql   # FK constraints
    ├── 04_create_indexes.sql    # Performance indexes
    └── 05_validate_data.sql     # Validation queries
```

---

## ✅ Success Criteria

You're done when:
- [ ] All 12 tables created in Supabase
- [ ] All data loaded (match CSV row counts)
- [ ] Primary keys enforced (no duplicates)
- [ ] Foreign keys added and valid
- [ ] Indexes created for common queries
- [ ] Test queries return expected results
- [ ] Dashboard dev can connect and query
- [ ] Tracker dev can insert new records

---

## 🆘 Getting Help

- **ETL Issues:** Re-run `python etl.py` then `fix_data_integrity.py`
- **Data Questions:** Check data dictionaries
- **Schema Questions:** See `SCHEMA_AND_ERD.md`
- **Business Rules:** See `MASTER_INSTRUCTIONS.md`

---

*Last Updated: December 2024*
