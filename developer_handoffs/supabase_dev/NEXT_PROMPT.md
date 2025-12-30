# BenchSight Supabase Developer - Next Prompt

Copy and paste this prompt to start or continue Supabase integration work.

---

## PROMPT START

I'm working on BenchSight, a hockey analytics platform. My role is **Supabase integration and deployment**.

### Project Context
- **Database:** Supabase PostgreSQL at `https://uuaowslhpgyiudmbvqze.supabase.co`
- **Data Source:** CSV files from ETL pipeline in `/data/output/`
- **Schema:** Star schema with 3 dimension tables and 9 fact tables
- **Total:** 317 columns across 12 tables

### Tables to Deploy
**Dimensions:**
- dim_player (player master data)
- dim_team (team master data)  
- dim_schedule (game schedule with scores)

**Facts:**
- fact_events (wide format - one row per event)
- fact_events_player (long format - player per event)
- fact_shifts (shift data)
- fact_shifts_player (player-shift assignments)
- fact_player_game_stats (29 player metrics per game)
- fact_team_game_stats (18 team metrics per game)
- fact_goalie_game_stats (19 goalie metrics including microstats)
- fact_h2h (head-to-head matchups)
- fact_wowy (with-or-without-you analysis)

### Primary Key Format
All PKs use: `{prefix}{game_id}{5-digit-index}`
- Events: `E1896900001`
- Shifts: `S1896900001`
- Player stats: `PG18969P100192`

### Known Issues
1. Need to check for duplicate PKs before upload
2. Must load dimension tables before fact tables (FK dependencies)
3. Some columns have nulls that need defaults
4. Need to create indexes for query performance

### What I Need Help With Today
[DESCRIBE YOUR SPECIFIC TASK - examples below]

**Examples:**
- "Help me write the CREATE TABLE statements for all 12 tables"
- "I'm getting FK constraint errors when loading fact_events"
- "Help me write validation queries to verify the data loaded correctly"
- "I need to set up RLS policies for public read access"
- "The dashboard developer says queries are slow - help optimize"

### Files I Have Access To
- `/data/output/*.csv` - All data files
- `/data/output/data_dictionary/*.csv` - Column definitions
- `docs/SCHEMA_AND_ERD.md` - Schema documentation
- `docs/MASTER_INSTRUCTIONS.md` - Business rules

---

## PROMPT END

---

## Alternative Prompts for Specific Tasks

### For Initial Setup
```
I'm setting up BenchSight's Supabase database from scratch. I have CSV files ready to load.

Tables needed: dim_player, dim_team, dim_schedule, fact_events, fact_events_player, fact_shifts, fact_shifts_player, fact_player_game_stats, fact_team_game_stats, fact_goalie_game_stats, fact_h2h, fact_wowy

Please help me:
1. Generate CREATE TABLE statements with proper data types
2. Determine the correct load order for FK dependencies
3. Write the COPY commands to import CSVs

Key constraints:
- PKs are VARCHAR(20), format: {prefix}{game_id}{5d}
- game_id is INTEGER
- Percentages are DECIMAL(5,2)
- Names are VARCHAR(100)
```

### For Troubleshooting FK Errors
```
I'm getting foreign key constraint errors when loading BenchSight data into Supabase.

Error: [PASTE ERROR MESSAGE]

Table I'm trying to load: [TABLE NAME]
Tables already loaded: [LIST]

The FK relationships are:
- fact_events.game_id → dim_schedule.game_id
- fact_events.shift_key → fact_shifts.shift_key
- fact_events_player.event_key → fact_events.event_key
- fact_events_player.player_id → dim_player.player_id

Help me diagnose and fix this.
```

### For Performance Optimization
```
BenchSight dashboard queries are slow. Current tables in Supabase:
- fact_events (~5000 rows)
- fact_player_game_stats (~300 rows)
- fact_team_game_stats (~20 rows)

Slow query example:
[PASTE QUERY]

Current indexes: [LIST OR "none"]

Help me:
1. Identify missing indexes
2. Optimize the query
3. Consider if materialized views would help
```

### For Data Validation
```
I've loaded BenchSight data into Supabase and need to validate it.

Expected counts (from CSVs):
- fact_events: [X] rows
- fact_player_game_stats: [X] rows
- [etc.]

Please help me write validation queries to:
1. Verify row counts match
2. Check for orphaned FKs
3. Validate data ranges (percentages 0-100, etc.)
4. Find any duplicate PKs
```

---

## Quick Reference

### Load Order (Dependencies)
```
1. dim_player        (no deps)
2. dim_team          (no deps)
3. dim_schedule      (no deps)
4. fact_shifts       (→ dim_schedule)
5. fact_events       (→ dim_schedule, fact_shifts)
6. fact_events_player(→ fact_events, dim_player)
7. fact_shifts_player(→ fact_shifts, dim_player)
8. fact_player_game_stats (→ dim_player, dim_schedule)
9. fact_team_game_stats   (→ dim_team, dim_schedule)
10. fact_goalie_game_stats (→ dim_player, dim_schedule)
11. fact_h2h              (→ dim_player, dim_schedule)
12. fact_wowy             (→ dim_player, dim_schedule)
```

### Common Data Types
```sql
-- Primary keys
event_key VARCHAR(20) PRIMARY KEY
game_id INTEGER NOT NULL

-- Stats
goals INTEGER DEFAULT 0
shooting_pct DECIMAL(5,2)
toi_seconds INTEGER

-- Text
player_name VARCHAR(100)
event_type VARCHAR(50)
event_detail VARCHAR(100)

-- Flags
event_successful CHAR(1) -- 's' or 'u'
empty_net_goal BOOLEAN
```

### Supabase CLI Commands
```bash
# Connect to database
supabase db connect

# Run SQL file
supabase db execute -f 01_create_tables.sql

# Import CSV (alternative)
psql $DATABASE_URL -c "\copy dim_player FROM 'dim_player.csv' CSV HEADER"
```

---

*Last Updated: December 2024*
