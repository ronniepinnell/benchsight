# BenchSight ETL Documentation

**Extract, Transform, Load Pipeline**

Updated: 2026-01-10

---

## Quick Start

```bash
# Run full ETL
python run_etl.py

# Validate output
python validate.py

# Upload to Supabase
python upload.py
```

---

## Input Files

### Master Data
```
data/raw/BLB_TABLES.xlsx
```
Contains all dimension definitions (teams, players, event types, etc.)

### Game Data
```
data/raw/games/{game_id}/
├── tracking_export.xlsx    # Event data from tracker
├── roster.xlsx             # Game roster
└── shifts.xlsx             # Shift data (if available)
```

---

## Output

### CSVs
```
data/output/
├── dim_*.csv       # 55 dimension tables
├── fact_*.csv      # 71 fact tables
└── qa_*.csv        # 4 QA tables
```

### Supabase Schema
```
sql/reset_supabase.sql
```

---

## ETL Phases

### Phase 1: Extract
Load raw data from Excel files.

```python
# Loads BLB_TABLES.xlsx
blb_loader.load_master_data()

# Loads game tracking exports
game_loader.load_game(game_id)
```

### Phase 2: Build Dimensions
Create all `dim_*` tables.

```python
# Core dimensions
dim_player      # All players
dim_team        # All teams
dim_schedule    # All games
dim_season      # Seasons
dim_league      # Leagues

# Event dimensions
dim_event_type
dim_event_detail
dim_play_detail
dim_shot_type
dim_zone
```

### Phase 3: Build Core Facts
Create primary fact tables.

```python
fact_gameroster    # Who played in each game
fact_events        # All game events
fact_shifts        # Player shifts (ice time)
```

### Phase 4: Build Derived Facts
Calculate statistics from core facts.

```python
fact_player_game_stats   # 317 columns per player per game
fact_team_game_stats     # Team-level stats
fact_goalie_game_stats   # Goalie-specific stats
fact_lines               # Line combinations
```

### Phase 5: Build Analytics
Advanced analytical tables.

```python
fact_h2h_*        # Head-to-head matchups
fact_wowy_*       # With/without analysis
fact_shot_chains  # Possession sequences
```

### Phase 6: Export
Write all tables to CSV and optionally upload.

```python
table_writer.write_all()      # CSVs
supabase_manager.upload_all() # Database
```

---

## Critical Rules

### Goal Counting
```
✅ CORRECT: event_type='Goal' AND event_detail='Goal_Scored'
❌ WRONG:   event_detail='Shot_Goal' (this is a shot, not a goal)
```

### Player Attribution
```
event_player_1 = Primary actor (scorer, shooter, passer)
event_player_2 = Secondary actor (assist, target)
event_player_3 = Tertiary actor (second assist)
```

### Data Source
```
ALL dimension values come from: data/raw/BLB_TABLES.xlsx
Do NOT hardcode dimension values in code.
```

---

## Common Commands

```bash
# Full ETL (default)
python run_etl.py

# Validate before upload
python validate.py

# Quick validation (counts only)
python validate.py --quick

# Generate schema only
python upload.py --schema

# Upload all tables
python upload.py

# Upload single table
python upload.py --table dim_player

# Upload dimensions only
python upload.py --dims

# Upload facts only
python upload.py --facts
```

---

## Troubleshooting

### "Table not found" error
```bash
# Check CSV was generated
ls data/output/*.csv | wc -l  # Should be 131
```

### "Foreign key violation"
```bash
# Validate FK relationships
python validate.py --data
```

### "Goal count mismatch"
```bash
# Check goal counting
python validate.py --goals
```

### Wrong number of tables
```bash
# Should be 131
python validate.py --tables
```

---

## Adding a New Game

1. **Track the game** using `ui/tracker/index.html`
2. **Export** to Excel
3. **Copy files** to `data/raw/games/{game_id}/`
4. **Run ETL**: `python run_etl.py`
5. **Validate**: `python validate.py`
6. **Upload**: `python upload.py`

---

## Performance

| Phase | Time |
|-------|------|
| Extract | ~5 sec |
| Transform | ~60 sec |
| Load (CSV) | ~10 sec |
| Upload | ~120 sec |
| **Total** | **~3 min** |

---

## Configuration

### config/config_local.ini
```ini
[etl]
batch_size = 500
log_level = INFO
output_dir = data/output

[supabase]
url = https://xxx.supabase.co
service_key = your_key
```

---

## Error Handling

The ETL continues on non-critical errors:
- Missing optional columns → uses defaults
- Empty tables → creates empty CSV
- Duplicate keys → logs warning, keeps first

Critical errors stop the ETL:
- Missing required input files
- Invalid data types in required columns
- Database connection failures

---

*Last updated: 2026-01-10*
