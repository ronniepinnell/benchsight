# BenchSight Extension Guide

## How to Add a New Stat Column

### Step 1: Add Calculation
Edit `src/analytics/` or the relevant stats builder:

```python
# Example: Adding "clutch_goals_pct"
df['clutch_goals_pct'] = (df['clutch_goals'] / df['goals'].replace(0, 1)) * 100
```

### Step 2: Update Schema
Add column to `sql/01_CREATE_ALL_TABLES.sql`:

```sql
ALTER TABLE fact_player_game_stats ADD COLUMN clutch_goals_pct DECIMAL(5,2);
```

Or find the CREATE TABLE and add:
```sql
clutch_goals_pct DECIMAL(5,2),
```

### Step 3: Document
Add to `docs/STATS_REFERENCE_COMPLETE.md`:

```markdown
| `clutch_goals_pct` | Percentage of goals scored in clutch situations | (clutch_goals / goals) * 100 | 20%+ | <5% |
```

### Step 4: Add Test
Add to `tests/test_stats_calculations.py`:

```python
def test_clutch_goals_pct_valid(self):
    """Check clutch_goals_pct is between 0-100."""
    if 'clutch_goals_pct' in self.df.columns:
        valid = self.df['clutch_goals_pct'].between(0, 100, inclusive='both')
        assert valid.all() or self.df['clutch_goals_pct'].isna().all()
```

### Step 5: Deploy
```bash
./run_etl.sh --export
./run_deploy.sh
```

---

## How to Add a New Table

### Step 1: Design the Table
Determine:
- Table name (use `dim_` for dimensions, `fact_` for facts)
- Primary key
- Foreign keys to existing tables
- All columns with types

### Step 2: Create SQL
Add to `sql/01_CREATE_ALL_TABLES.sql`:

```sql
-- ============================================
-- NEW TABLE: fact_video_highlights
-- ============================================
CREATE TABLE IF NOT EXISTS fact_video_highlights (
    highlight_id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES dim_schedule(game_id),
    event_index INTEGER,
    player_id INTEGER REFERENCES dim_player(player_id),
    highlight_type TEXT,
    title TEXT,
    description TEXT,
    video_url TEXT,
    start_timestamp DECIMAL(10,3),
    end_timestamp DECIMAL(10,3),
    duration_seconds DECIMAL(10,3),
    camera_angle TEXT,
    quality_rating INTEGER,
    is_featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    created_by TEXT
);

CREATE INDEX idx_video_highlights_game ON fact_video_highlights(game_id);
CREATE INDEX idx_video_highlights_player ON fact_video_highlights(player_id);
CREATE INDEX idx_video_highlights_type ON fact_video_highlights(highlight_type);
```

### Step 3: Create CSV Generator
Add to ETL pipeline or create standalone script:

```python
# scripts/generate_video_highlights.py
import pandas as pd

def generate_video_highlights(events_df):
    """Generate video highlights from notable events."""
    
    # Find highlight-worthy events
    highlights = events_df[
        (events_df['event_type'].isin(['Goal', 'Save'])) |
        (events_df['event_detail'].isin(['Big Hit', 'Breakaway']))
    ].copy()
    
    highlights['highlight_id'] = range(1, len(highlights) + 1)
    highlights['highlight_type'] = highlights['event_type']
    # ... more processing
    
    return highlights

# Export
df = generate_video_highlights(events)
df.to_csv('data/output/fact_video_highlights.csv', index=False)
```

### Step 4: Add to Loader
Edit `scripts/flexible_loader.py`, add to `TABLE_CATEGORIES`:

```python
"other_facts": [
    # ... existing tables
    "fact_video_highlights",
],
```

### Step 5: Document
Add to `docs/DATA_DICTIONARY.md`:

```markdown
### fact_video_highlights
Video highlight clips linked to game events.

| Column | Type | Description |
|--------|------|-------------|
| highlight_id | INTEGER | Primary key |
| game_id | INTEGER | FK to dim_schedule |
| event_index | INTEGER | Link to fact_events |
| ... | ... | ... |
```

### Step 6: Deploy
```bash
# Create table in Supabase SQL Editor
# Run the CREATE TABLE statement

# Generate and load data
python scripts/generate_video_highlights.py
python scripts/flexible_loader.py --scope table --table fact_video_highlights --operation replace
```

---

## How to Add a Flag/Column to Existing Table

### Example: Adding `is_highlight` to fact_events

### Step 1: Alter Table
```sql
ALTER TABLE fact_events ADD COLUMN is_highlight BOOLEAN DEFAULT FALSE;
ALTER TABLE fact_events ADD COLUMN highlight_id INTEGER;
```

### Step 2: Update ETL
Edit the events processing to set the flag:

```python
# In src/ingestion/game_loader.py or transformation
events_df['is_highlight'] = events_df['event_type'].isin(['Goal', 'Save']) | \
                            events_df['event_detail'].isin(['Big Hit', 'Breakaway'])
```

### Step 3: Update CSV Export
Ensure the new column is in the export.

### Step 4: Deploy
```bash
./run_etl.sh --export
./run_deploy.sh --scope table --table fact_events --operation replace
```

---

## Adding Foreign Key Relationships

### Step 1: Ensure Referenced Table Exists
The referenced table must exist first.

### Step 2: Add FK Constraint
```sql
ALTER TABLE fact_video_highlights 
ADD CONSTRAINT fk_video_event 
FOREIGN KEY (game_id, event_index) 
REFERENCES fact_events(game_id, event_index);
```

### Step 3: Use Utility Script
```bash
python scripts/utilities/add_all_fkeys.py
```

---

## Quick Reference: Column Types

| Data Type | Use For | Example |
|-----------|---------|---------|
| INTEGER | IDs, counts | player_id, goals |
| DECIMAL(10,3) | Precise numbers | toi_seconds, x_coord |
| DECIMAL(5,2) | Percentages | shooting_pct, cf_pct |
| TEXT | Strings | player_name, event_type |
| BOOLEAN | True/False | is_home, is_highlight |
| TIMESTAMP | Date/time | created_at |
| DATE | Date only | game_date |
