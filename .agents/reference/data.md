# Data Rules

**Data validation and schema rules**

Last Updated: 2026-01-15

---

## Data Validation

### Validation Pattern

```python
def validate_data(df: pd.DataFrame) -> bool:
    """
    Validate DataFrame.
    
    Args:
        df: DataFrame to validate
    
    Returns:
        True if valid, raises exception if invalid
    """
    # Check required columns
    required_cols = ['col1', 'col2']
    missing = set(required_cols) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    
    # Check data types
    if df['col1'].dtype != 'int64':
        raise TypeError(f"col1 must be int64, got {df['col1'].dtype}")
    
    # Check for nulls
    if df['col1'].isnull().any():
        raise ValueError("col1 contains null values")
    
    return True
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

### Type Validation

```python
def ensure_types(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure correct types for DataFrame."""
    df['player_id'] = df['player_id'].astype(str)
    df['game_id'] = df['game_id'].astype(str)
    df['date'] = pd.to_datetime(df['date'])
    return df
```

---

## Schema Rules

### Table Naming

- `dim_*` - Dimension tables
- `fact_*` - Fact tables
- `qa_*` - QA tables
- `lookup_*` - Lookup tables
- `v_*` - Views

### Column Naming

- Use snake_case
- Be descriptive
- Follow existing patterns

---

## Data Quality

### Quality Checks

```python
def check_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """Check data quality metrics."""
    return {
        'row_count': len(df),
        'null_counts': df.isnull().sum().to_dict(),
        'duplicate_count': df.duplicated().sum(),
        'type_consistency': check_types(df)
    }
```

---

## Related Rules

- `core.md` - Core rules (single source of truth)
- `etl.md` - ETL validation patterns
- `testing.md` - Data testing requirements

---

*Last Updated: 2026-01-15*
