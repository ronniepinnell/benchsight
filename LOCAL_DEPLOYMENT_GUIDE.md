# BenchSight Local Deployment Guide
## Get Your Database Running in 15 Minutes

---

## Prerequisites

Before starting, ensure you have:
- [ ] Python 3.8+ installed
- [ ] The `benchsight_complete_v2.zip` file downloaded and extracted
- [ ] Your Supabase project credentials (URL and service_role key)

---

## Step 1: Extract the Project

```bash
# Create a working directory
mkdir ~/benchsight
cd ~/benchsight

# Extract the zip (adjust path as needed)
unzip ~/Downloads/benchsight_complete_v2.zip

# Verify structure
ls -la
# You should see: data/, sql/, scripts/, developer_handoffs/, etc.
```

---

## Step 2: Install Python Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install supabase pandas python-dotenv

# Verify installation
python -c "from supabase import create_client; print('Supabase OK')"
```

---

## Step 3: Get Your Supabase Credentials

1. Go to https://supabase.com/dashboard
2. Select your project (or create one)
3. Go to **Settings** → **API**
4. Copy these values:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **service_role key** (under "Project API keys" - the secret one!)

⚠️ **IMPORTANT**: Use the `service_role` key, NOT the `anon` key. The service_role key has full database access.

---

## Step 4: Set Environment Variables

### Option A: Export directly (temporary)
```bash
export SUPABASE_URL="https://uuaowslhpgyiudmbvqze.supabase.co"
export SUPABASE_SERVICE_KEY="your-service-role-key-here"
```

### Option B: Create .env file (persistent)
```bash
# Create .env file in project root
cat > .env << 'EOF'
SUPABASE_URL=https://uuaowslhpgyiudmbvqze.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key-here
EOF

# Load it
source .env
# Or add to your shell profile
```

### Option C: Edit config file
```bash
# Edit config/config_local.ini
nano config/config_local.ini

# Add your credentials:
# [supabase]
# url = https://uuaowslhpgyiudmbvqze.supabase.co
# key = your-service-role-key-here
```

---

## Step 5: Create Database Tables

### Option A: Via Supabase Web UI (Easiest)

1. Go to your Supabase Dashboard
2. Click **SQL Editor** in the left sidebar
3. Click **New Query**
4. Open `sql/01_RECREATE_SCHEMA.sql` in a text editor
5. Copy the ENTIRE contents
6. Paste into the SQL Editor
7. Click **Run** (or Cmd/Ctrl + Enter)
8. Wait for "Success" message

You should see output like:
```
NOTICE: Dropping all BenchSight tables...
NOTICE: All tables dropped successfully.
NOTICE: Creating dimension tables...
...
NOTICE: BenchSight schema recreation complete!
```

### Option B: Via psql (Command Line)

```bash
# Get connection string from Supabase Dashboard → Settings → Database
psql "postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres"

# Run the schema script
\i sql/01_RECREATE_SCHEMA.sql

# Verify tables were created
\dt

# Exit
\q
```

---

## Step 6: Load the Data

### Option A: Using the Python Loader (Recommended)

```bash
# Make sure you're in the project directory
cd ~/benchsight

# Verify environment variables are set
echo $SUPABASE_URL
echo $SUPABASE_SERVICE_KEY

# Check current table counts (should all be 0)
python scripts/flexible_loader.py --counts

# Load ALL data (full refresh)
python scripts/flexible_loader.py --scope full --operation replace

# This will take 2-5 minutes and show progress like:
# [12:34:56] Loading category 'all' (12 tables)...
# [12:34:57]   Loading dim_player...
# [12:34:58]     ✓ 337 rows
# ...
```

### Option B: Via Supabase Table Editor (Manual)

1. Go to Supabase Dashboard → **Table Editor**
2. For each table (in this order!):
   - Click the table name
   - Click **Insert** → **Import data from CSV**
   - Select the corresponding CSV from `data/output/`
   - Click **Import**

**Load order (important!):**
1. `dim_player.csv` → dim_player
2. `dim_team.csv` → dim_team
3. `dim_schedule.csv` → dim_schedule
4. `fact_shifts.csv` → fact_shifts
5. `fact_events.csv` → fact_events
6. `fact_events_player.csv` → fact_events_player
7. `fact_shifts_player.csv` → fact_shifts_player
8. `fact_player_game_stats.csv` → fact_player_game_stats
9. `fact_team_game_stats.csv` → fact_team_game_stats
10. `fact_goalie_game_stats.csv` → fact_goalie_game_stats
11. `fact_h2h.csv` → fact_h2h
12. `fact_wowy.csv` → fact_wowy

---

## Step 7: Verify the Deployment

### Check Row Counts

```bash
# Via Python
python scripts/flexible_loader.py --counts
```

**Expected output:**
```
Table Row Counts:
----------------------------------------
  dim_player: 337
  dim_schedule: 562
  dim_team: 26
  fact_events: 5833
  fact_events_player: 11635
  fact_goalie_game_stats: 8
  fact_h2h: 684
  fact_player_game_stats: 107
  fact_shifts: 672
  fact_shifts_player: 4626
  fact_team_game_stats: 8
  fact_wowy: 641
----------------------------------------
  TOTAL: 24654
```

### Via Supabase SQL Editor

```sql
SELECT * FROM get_all_table_counts();
```

### Check Games Status

```sql
SELECT * FROM get_games_status();
```

Expected:
```
game_id | game_date  | matchup                    | events_count | shifts_count | has_stats
--------|------------|----------------------------|--------------|--------------|----------
18987   | 2024-12-21 | Team A vs Team B           | 1467         | 168          | true
18981   | 2024-12-17 | Team C vs Team D           | 1460         | 168          | true
18977   | 2024-12-14 | Team E vs Team F           | 1456         | 168          | true
18969   | 2024-12-07 | Puck Hogs vs Blades        | 1450         | 168          | true
```

---

## Step 8: Test a Query

Run this in Supabase SQL Editor to see top scorers:

```sql
SELECT 
    player_full_name,
    team_name,
    goals,
    assists,
    points,
    shooting_pct
FROM fact_player_game_stats
ORDER BY points DESC
LIMIT 10;
```

---

## 🎉 Deployment Complete!

Your BenchSight database is now live with:
- **337** players
- **26** teams  
- **562** scheduled games
- **4 fully tracked games** with complete event/shift data
- **24,654 total rows** across 12 tables

---

## What's Next?

### Connect Dashboard
```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  'https://uuaowslhpgyiudmbvqze.supabase.co',
  'your-anon-key'  // Use anon key for frontend!
)

// Get top scorers
const { data } = await supabase
  .from('fact_player_game_stats')
  .select('player_full_name, goals, assists, points')
  .order('points', { ascending: false })
  .limit(10)
```

### Connect Tracker (for live game entry)
See `developer_handoffs/tracker_dev/README.md`

### Set Up Admin Portal
See `developer_handoffs/portal_dev/README.md`

---

## Troubleshooting

### "Invalid API key"
- Make sure you're using `service_role` key, not `anon` key
- Check for extra spaces or newlines in your key

### "relation does not exist"
- Run the schema creation script first (Step 5)
- Make sure it completed without errors

### "duplicate key value"
- Data was partially loaded before
- Run: `SELECT truncate_all_facts();` then reload

### "foreign key constraint"
- Load tables in the correct order (dims first, then facts)
- Or temporarily disable FK constraints

### Loader shows 0 rows
- Check that CSV files exist in `data/output/`
- Verify the data directory path is correct

---

## Quick Reference Commands

```bash
# Check status
python scripts/flexible_loader.py --counts

# Full reload
python scripts/flexible_loader.py --scope full --operation replace

# Reload just dimensions
python scripts/flexible_loader.py --scope category --category dims --operation upsert

# Reload single game
python scripts/flexible_loader.py --scope game --game-id 18969 --operation replace

# Dry run (see what would happen)
python scripts/flexible_loader.py --scope full --operation replace --dry-run
```

---

*Created: December 2024*
