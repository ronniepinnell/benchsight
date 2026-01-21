# ETL Rules

**ETL-specific patterns and rules**

Last Updated: 2026-01-15

---

## ETL Architecture

### Main Entry Point
- `run_etl.py` - Main ETL entry point
- `src/core/base_etl.py` - Core ETL logic

### Key Components
- `src/tables/*.py` - Table creation modules
- `src/calculations/*.py` - Calculation modules
- `src/utils/*.py` - Utility functions
- `config/formulas.json` - Formula definitions

---

## ETL Patterns

### Table Creation Pattern

```python
def create_table_name(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create table_name table.
    
    Args:
        df: Source DataFrame
    
    Returns:
        DataFrame with table data
    """
    # Use vectorized operations
    result = df.groupby(['key']).agg({
        'column': 'sum'
    }).reset_index()
    return result
```

### Goal Counting Pattern

**ALWAYS use GOAL_FILTER:**
```python
GOAL_FILTER = (
    (df['event_type'] == 'Goal') & 
    (df['event_detail'] == 'Goal_Scored')
)

goals = df[GOAL_FILTER]
```

### Calculation Pattern

```python
def calculate_stat(
    events_df: pd.DataFrame,
    player_id: str,
    team_id: str
) -> Dict[str, int]:
    """
    Calculate stat for a player.
    
    Args:
        events_df: DataFrame with events
        player_id: Player ID
        team_id: Team ID
    
    Returns:
        Dictionary with stat values
    """
    # Use vectorized operations
    player_events = events_df[
        (events_df['event_player_1'] == player_id) |
        (events_df['event_player_2'] == player_id)
    ]
    # ... implementation
    return result
```

---

## Performance Requirements

### Vectorized Operations

**NEVER use:**
```python
for index, row in df.iterrows():  # ❌ BAD
    # process row
```

**ALWAYS use:**
```python
# Vectorized operations
result = df.groupby(['key']).agg({
    'column': 'sum'
}).reset_index()  # ✅ GOOD
```

### Performance Targets

- **ETL Runtime:** < 90 seconds for 4 games
- **Memory:** Efficient DataFrame operations
- **Optimization:** Profile before optimizing

---

## Data Flow

### ETL Phases

1. Load BLB Tables
2. Load Game Data
3. Process Events
4. Create Tables
5. Calculate Stats
6. Validate Data
7. Upload to Supabase

### Data Validation

**Always run validation:**
```bash
python validate.py
```

**After ETL changes:**
- Run validation
- Check data integrity
- Verify table counts

---

## Error Handling

### ETL Error Pattern

```python
try:
    result = process_data(df)
except ValueError as e:
    logger.error(f"Invalid data: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
```

---

## Type Consistency

### Before Merges

**Always ensure type consistency:**
```python
# Convert types before merge
df1['player_id'] = df1['player_id'].astype(str)
df2['player_id'] = df2['player_id'].astype(str)
merged = df1.merge(df2, on='player_id')
```

---

## Related Rules

- `core.md` - Core rules (goal counting, single source of truth)
- `data.md` - Data validation rules
- `testing.md` - Testing requirements

---

*Last Updated: 2026-01-15*
