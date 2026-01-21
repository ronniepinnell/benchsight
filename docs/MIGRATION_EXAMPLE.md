# Migration Example: Using Centralized Table I/O

## Before (Old Pattern)

```python
#!/usr/bin/env python3
"""
OLD: Each module has its own load_table/save_table implementation
"""
import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path('data/output')

def load_table(name: str, required: bool = False) -> pd.DataFrame:
    """Duplicate implementation (exists in 5 files!)"""
    try:
        from src.core.table_store import get_table
        df = get_table(name, OUTPUT_DIR)
        if len(df) > 0:
            return df
    except:
        pass

    path = OUTPUT_DIR / f'{name}.csv'
    if path.exists():
        return pd.read_csv(path, low_memory=False)
    return pd.DataFrame()

def save_table(df: pd.DataFrame, name: str) -> int:
    """Duplicate implementation (exists in 5 files!)"""
    if df is not None and len(df) > 0:
        df = add_names_to_table(df)  # Local implementation
    path = OUTPUT_DIR / f"{name}.csv"
    df.to_csv(path, index=False)
    return len(df)

def create_my_table():
    """Example function using old pattern"""
    # Load dependencies
    events = load_table('fact_events', required=True)
    roster = load_table('fact_gameroster')

    # Do calculations...
    result = events.groupby('player_id').size()

    # Save result
    save_table(result, 'my_new_table')
```

---

## After (New Pattern)

```python
#!/usr/bin/env python3
"""
NEW: Use centralized table I/O from table_writer
"""
import pandas as pd
from pathlib import Path
from src.core.table_writer import load_table, save_output_table
from src.utils.constants_loader import get_xg_base_rates, get_gar_weights

OUTPUT_DIR = Path('data/output')

def create_my_table():
    """Example function using new pattern"""
    # Load dependencies (centralized function)
    events = load_table('fact_events', required=True, output_dir=OUTPUT_DIR)
    roster = load_table('fact_gameroster', output_dir=OUTPUT_DIR)

    # Load constants from config
    xg_rates = get_xg_base_rates()
    gar_weights = get_gar_weights('player')

    # Do calculations using externalized constants
    result = events.groupby('player_id').size()

    # Calculate xG using config values
    result['xg'] = result['danger_zone'].map(xg_rates).fillna(xg_rates['default'])

    # Save result (automatically adds player_name column, optimizes dtypes, etc.)
    save_output_table(result, 'my_new_table', output_dir=OUTPUT_DIR)
```

---

## Benefits of New Pattern

### 1. No Code Duplication
- **Before:** 5 files with duplicate `load_table()` implementations
- **After:** 1 centralized `load_table()` in `table_writer.py`
- **Impact:** Bug fixes in 1 place instead of 5

### 2. Automatic Enhancements
- `save_output_table()` automatically:
  - Adds `player_name`/`team_name` columns (via `add_names_to_table()`)
  - Optimizes data types to reduce memory
  - Removes 100% null columns
  - Stores in cache for later phases
  - Uploads to Supabase (if enabled)

### 3. Externalized Configuration
- **Before:** xG rates and GAR weights hardcoded in `core_facts.py`
- **After:** Loaded from `config/analytics_constants.yaml`
- **Impact:** Tune models without code changes

---

## Migration Steps for Existing Files

### Step 1: Update Imports

```python
# OLD
from pathlib import Path
OUTPUT_DIR = Path('data/output')

# NEW
from pathlib import Path
from src.core.table_writer import load_table, save_output_table
OUTPUT_DIR = Path('data/output')
```

### Step 2: Remove Duplicate Functions

Delete these functions from your module:
- `load_table()`
- `save_table()`
- `add_names_to_table()` (if present)

They're now centralized in `table_writer.py`.

### Step 3: Update Function Calls

```python
# OLD
df = load_table('fact_events')
rows = save_table(result_df, 'my_table')

# NEW
df = load_table('fact_events', required=True, output_dir=OUTPUT_DIR)
rows, cols = save_output_table(result_df, 'my_table', output_dir=OUTPUT_DIR)
```

### Step 4: Update Constants

```python
# OLD
XG_BASE_RATES = {'high_danger': 0.25, 'medium_danger': 0.08, ...}
GAR_WEIGHTS = {'goals': 1.0, 'primary_assists': 0.7, ...}

xg_value = XG_BASE_RATES.get(danger_zone, 0.06)
gar = stats['goals'] * GAR_WEIGHTS['goals']

# NEW
from src.utils.constants_loader import get_xg_base_rates, get_gar_weights

xg_base_rates = get_xg_base_rates()
gar_weights = get_gar_weights('player')

xg_value = xg_base_rates.get(danger_zone, xg_base_rates['default'])
gar = stats['goals'] * gar_weights['goals']
```

---

## Testing After Migration

### 1. Syntax Check
```bash
python -m py_compile src/tables/your_module.py
```

### 2. Import Check
```bash
python -c "from src.tables.your_module import create_all_tables; print('OK')"
```

### 3. Run ETL
```bash
python run_etl.py
```

### 4. Verify Output
```bash
# Check table was created
ls -lh data/output/your_table.csv

# Check row count matches previous run
wc -l data/output/your_table.csv
```

---

## Files to Migrate

### High Priority
1. ✅ `src/core/table_writer.py` - Already updated (centralized I/O)
2. ⏳ `src/tables/core_facts.py` - Remove duplicate functions, use imports
3. ⏳ `src/tables/remaining_facts.py` - Remove duplicate functions
4. ⏳ `src/tables/shift_analytics.py` - Remove duplicate functions
5. ⏳ `src/tables/event_analytics.py` - Remove duplicate functions

### Medium Priority
6. ⏳ `src/tables/dimension_tables.py` - Use centralized I/O
7. ⏳ `src/tables/macro_stats.py` - Use centralized I/O
8. ⏳ `src/advanced/extended_tables.py` - Use centralized I/O
9. ⏳ `src/xy/xy_table_builder.py` - Use centralized I/O

### Low Priority
10. ⏳ Any custom scripts or utilities that read/write tables

---

## Rollback Plan

If migration causes issues:

1. **Revert the file:**
   ```bash
   git checkout src/tables/your_module.py
   ```

2. **Keep using old pattern temporarily:**
   - Old pattern still works (duplicate functions still exist)
   - Migrate gradually, one file at a time
   - Test thoroughly after each migration

3. **Report issues:**
   - Document what broke
   - Check import errors vs logic errors
   - Verify constants are loading correctly

---

## Common Issues

### Issue 1: Import Error
```
ImportError: cannot import name 'load_table' from 'src.core.table_writer'
```

**Solution:** Check that `table_writer.py` has the `load_table()` function (should be at line ~228).

### Issue 2: Missing Constants
```
KeyError: 'high_danger'
```

**Solution:** Install pyyaml and verify `config/analytics_constants.yaml` exists:
```bash
pip install pyyaml>=6.0.0
ls -lh config/analytics_constants.yaml
```

### Issue 3: Different Results
```
Table has different row count than before
```

**Solution:** `save_output_table()` automatically removes 100% null columns. Check if columns were removed:
```
  my_table: Removed 3 all-null columns: col1, col2, col3
```

This is expected behavior and improves data quality.

---

## Example: Migrating core_facts.py

### Before Migration

```python
# src/tables/core_facts.py (lines 93-164)
def save_table(df: pd.DataFrame, name: str) -> int:
    # ... 20 lines of duplicate code ...
    pass

def load_table(name: str, required: bool = False) -> pd.DataFrame:
    # ... 50 lines of duplicate code ...
    pass

def add_names_to_table(df: pd.DataFrame) -> pd.DataFrame:
    # ... 100 lines of duplicate code ...
    pass

# Constants (lines 56-87)
XG_BASE_RATES = {'high_danger': 0.25, 'medium_danger': 0.08, ...}
GAR_WEIGHTS = {'goals': 1.0, 'primary_assists': 0.7, ...}
```

### After Migration

```python
# src/tables/core_facts.py (updated)
from src.core.table_writer import load_table, save_output_table, add_names_to_table
from src.utils.constants_loader import (
    get_xg_base_rates, get_xg_modifiers, get_shot_type_xg_modifiers,
    get_gar_weights, get_league_constants, get_rating_game_score_map
)

# Load constants from config
XG_BASE_RATES = get_xg_base_rates()
XG_MODIFIERS = get_xg_modifiers()
SHOT_TYPE_XG_MODIFIERS = get_shot_type_xg_modifiers()
GAR_WEIGHTS = get_gar_weights('player')
GOALIE_GAR_WEIGHTS = get_gar_weights('goalie')
league_constants = get_league_constants()
GOALS_PER_WIN = league_constants['goals_per_win']
GAMES_PER_SEASON = league_constants['games_per_season']
LEAGUE_AVG_SV_PCT = league_constants['avg_save_pct']
RATING_GAME_SCORE_MAP = get_rating_game_score_map()

# Delete old duplicate functions (lines 93-164)
# They're now imported from table_writer

# Update save calls
def create_fact_player_game_stats():
    # ... calculations ...
    save_output_table(result, 'fact_player_game_stats')  # Updated
```

**Lines Removed:** ~170 lines (duplicate functions + hardcoded constants)
**Lines Added:** ~15 lines (imports + constant loading)
**Net Reduction:** ~155 lines
