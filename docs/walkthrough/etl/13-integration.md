# 13 - Systems Integration: How Everything Connects

**Learning Objectives:**
- Understand the complete data flow
- Know what crosses each system boundary
- Debug data issues across systems

---

## Complete System Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BENCHSIGHT DATA FLOW                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────────┐
│   TRACKER   │────►│     ETL     │────►│  DATABASE   │────►│    DASHBOARD    │
│  (Input)    │     │ (Transform) │     │  (Store)    │     │   (Display)     │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────────┘
      │                   │                   │                     │
      │                   │                   │                     │
   Excel              CSV files          PostgreSQL           React/Next.js
   files              (139 tables)       (Supabase)            components
      │                   │                   │                     │
      ▼                   ▼                   ▼                     ▼
data/raw/games/     data/output/        Cloud DB              Browser
{game_id}/          *.csv               Tables + Views        Charts + Tables

      │                                       │
      │                                       │
      └───────────────────────────────────────┘
                      ↑
                  API (optional)
                  FastAPI endpoints
```

---

## Data at Each Boundary

### Boundary 1: Tracker → ETL

**What crosses:** Excel files

**Location:**
```
data/raw/
├── BLB_Tables.xlsx           # League master data
└── games/
    ├── 19001/
    │   └── 19001_tracking.xlsx
    ├── 19002/
    │   └── 19002_tracking.xlsx
    └── ...
```

**Format:**
- Excel workbooks with multiple sheets
- Events sheet: One row per event
- Shifts sheet: One row per shift
- Jersey numbers (not player IDs)

### Boundary 2: ETL → Database

**What crosses:** CSV files (then uploaded)

**Location:**
```
data/output/
├── dim_player.csv
├── dim_team.csv
├── fact_events.csv
├── fact_player_game_stats.csv
└── ... (139 total)
```

**Format:**
- CSV files with headers
- Player IDs resolved
- All calculations complete
- Foreign keys populated

**Upload mechanism:**
```bash
./benchsight.sh db upload
# Reads CSVs, uploads to Supabase
```

### Boundary 3: Database → Dashboard

**What crosses:** SQL query results (JSON)

**Method:** Supabase JavaScript client

```typescript
// Dashboard queries database directly
const { data, error } = await supabase
  .from('fact_player_game_stats')
  .select('goals, assists, points')
  .eq('player_id', 'P001');
```

### Boundary 4: API → Database/ETL

**What crosses:** JSON (REST API)

**Endpoints:**
- `POST /etl/run` - Trigger ETL
- `GET /etl/status/{job_id}` - Check status
- `POST /upload/tables` - Upload to database

---

## End-to-End Example: Following a Goal

### Step 1: Recorded in Tracker

User clicks on rink canvas to record goal:
```
Event Type: Goal
Event Detail: Goal_Scored
Team: Blue
Jersey 1: 12 (scorer)
Jersey 2: 7 (primary assist)
Jersey 3: 22 (secondary assist)
Period: 2
Time: 8:45
X: 172
Y: 42
```

Saved to: `data/raw/games/19001/19001_tracking.xlsx`

### Step 2: ETL Loads and Transforms

```bash
./benchsight.sh etl run
```

**Phase 1:** Load dim_player to get player lookup
```python
# dim_player has:
# player_id, player_name, jersey_number, team_id
```

**Phase 2:** Build lookup
```python
player_lookup = {
    (19001, 'Blue', 12): 'P001',
    (19001, 'Blue', 7): 'P002',
    (19001, 'Blue', 22): 'P003',
}
```

**Phase 3:** Load tracking, resolve players
```python
event = {
    'event_id': 'E19001_P2_0845_001',
    'game_id': 19001,
    'event_type': 'Goal',
    'event_detail': 'Goal_Scored',
    'event_player_1': 'P001',  # Was jersey 12
    'event_player_2': 'P002',  # Was jersey 7
    'event_player_3': 'P003',  # Was jersey 22
    'x_coord': 172,
    'y_coord': 42,
    'danger_level': 'high',
}
```

**Phase 6:** Aggregate to player stats
```python
# fact_player_game_stats for P001:
{
    'player_game_key': 'PG19001P001',
    'player_id': 'P001',
    'game_id': 19001,
    'goals': 1,
    'xg_for': 0.32,  # Based on location
    'goals_above_xg': 0.68,
}
```

Output: `data/output/fact_player_game_stats.csv`

### Step 3: Upload to Database

```bash
./benchsight.sh db upload
```

- Reads `data/output/fact_player_game_stats.csv`
- Uploads to Supabase `fact_player_game_stats` table

### Step 4: Display in Dashboard

User visits `/norad/players/P001`:

```typescript
// Page component
export default async function PlayerPage({ params }) {
  const stats = await supabase
    .from('fact_player_game_stats')
    .select('*')
    .eq('player_id', params.playerId);

  return <PlayerStats data={stats} />;
}
```

Browser shows: "Goals: 1 | xG: 0.32 | Goals Above Expected: +0.68"

---

## System Contracts

### What Each System Expects

| System | Input Contract | Output Contract |
|--------|---------------|-----------------|
| **Tracker** | User clicks | Excel with events/shifts |
| **ETL** | Excel files in expected format | 139 CSV files |
| **Database** | CSV files matching schema | SQL tables |
| **Dashboard** | Tables with expected columns | React components |

### Breaking Changes

| If you change... | These break... |
|------------------|----------------|
| Tracker column names | ETL loading |
| ETL output columns | Database upload, dashboard queries |
| Database schema | Dashboard queries |
| dim_player structure | Everything downstream |

---

## Debugging Across Systems

### Issue: Wrong goal count on dashboard

**Step 1: Check dashboard query**
```typescript
// Is the query correct?
const { data } = await supabase
  .from('fact_player_game_stats')
  .select('goals')
  .eq('player_id', 'P001');
console.log(data);  // What does this return?
```

**Step 2: Check database table**
```sql
SELECT goals
FROM fact_player_game_stats
WHERE player_id = 'P001' AND game_id = 19001;
-- Does this match dashboard?
```

**Step 3: Check CSV output**
```bash
# Look at the CSV
grep "P001.*19001" data/output/fact_player_game_stats.csv
```

**Step 4: Check ETL calculation**
```python
# In fact_events, count goals for this player
events = pd.read_csv('data/output/fact_events.csv')
goals = events[(events['event_player_1'] == 'P001') &
               (events['event_type'] == 'Goal') &
               (events['event_detail'] == 'Goal_Scored') &
               (events['game_id'] == 19001)]
print(len(goals))  # Should match
```

**Step 5: Check tracking file**
```python
# Look at raw tracking data
tracking = pd.read_excel('data/raw/games/19001/19001_tracking.xlsx', 'Events')
goals = tracking[(tracking['event_type'] == 'Goal') &
                 (tracking['event_detail'] == 'Goal_Scored') &
                 (tracking['jersey_1'] == 12)]
print(goals)  # Is the event there?
```

### Common Issues

| Symptom | Likely Cause | Check |
|---------|--------------|-------|
| Missing player stats | Player not in roster | fact_gameroster |
| Wrong goals | Goal filter issue | ETL goal counting |
| Missing game | Game excluded | config/excluded_games.txt |
| Zero TOI | Shifts not loaded | fact_shifts |
| NaN values | Division by zero | Rate calculations |

---

## Configuration Files

### ETL Configuration

```
config/
├── config.ini              # Main ETL config
├── config_local.ini        # Local overrides (gitignored)
├── excluded_games.txt      # Games to skip
└── formulas.json           # Calculation weights
```

### Dashboard Configuration

```
ui/dashboard/
├── .env.local              # Environment variables (gitignored)
│   NEXT_PUBLIC_SUPABASE_URL=...
│   NEXT_PUBLIC_SUPABASE_ANON_KEY=...
└── .env.example            # Template
```

### API Configuration

```
api/
├── .env                    # Environment variables
│   ENVIRONMENT=development
│   CORS_ORIGINS=http://localhost:3000
│   SUPABASE_URL=...
│   SUPABASE_SERVICE_KEY=...
```

---

## Development Workflow

### Full Pipeline Test

```bash
# 1. Modify code
# 2. Run ETL
./benchsight.sh etl run --wipe

# 3. Validate
./benchsight.sh etl validate

# 4. Upload to database
./benchsight.sh db upload

# 5. Start dashboard
./benchsight.sh dashboard dev

# 6. Check results in browser
open http://localhost:3000/norad/players/P001
```

### Quick Iteration (Dashboard Only)

```bash
# If ETL output is already correct:
./benchsight.sh dashboard dev
# Make UI changes, hot-reload automatically
```

### Quick Iteration (ETL Only)

```bash
# If only checking CSV output:
./benchsight.sh etl run
# Check CSVs directly
cat data/output/fact_player_game_stats.csv | head
```

---

## Key Takeaways

1. **Data flows one direction:** Tracker → ETL → Database → Dashboard
2. **Each boundary has a contract:** Excel → CSV → SQL → JSON
3. **Debug by tracing backwards:** Dashboard → DB → CSV → ETL → Tracking
4. **Configuration lives in config files:** Not hardcoded
5. **Breaking changes cascade:** Upstream changes affect everything downstream

---

**Next:** [14-making-changes.md](14-making-changes.md) - How to safely modify the system
