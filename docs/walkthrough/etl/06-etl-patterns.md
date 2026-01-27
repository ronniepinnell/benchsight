# 06 - ETL Patterns: Good, Bad, and Technical Debt

**Learning Objectives:**
- Recognize good patterns to learn from and replicate
- Understand technical debt and why it exists
- Know how to improve the codebase safely

---

## Good Patterns (Learn From These)

### ✅ Pattern 1: Single Source of Truth

**Where:** `src/calculations/goals.py`

**What It Is:**
Critical business logic lives in ONE place. Every use goes through that one place.

**Example:**
```python
# src/calculations/goals.py - THE definition
def get_goal_filter(events_df: pd.DataFrame) -> pd.Series:
    return (
        (events_df['event_type'] == 'Goal') &
        (events_df['event_detail'] == 'Goal_Scored')
    )

# Everywhere else:
from src.calculations.goals import get_goal_filter, filter_goals
goals = filter_goals(events_df)
```

**Why It's Good:**
- One place to fix bugs
- One place to change logic
- Consistent behavior everywhere
- Easy to find the definition

**How to Apply:**
1. Identify business rules that must be consistent
2. Create a dedicated module for each
3. Import and use - never reimplement

---

### ✅ Pattern 2: CSV as Debuggable Intermediate

**Where:** Throughout ETL

**What It Is:**
Write CSV files after each major transformation. Don't just keep data in memory.

**Example:**
```python
def create_fact_events(event_players_df):
    # Transform
    fact_events = build_fact_events(event_players_df)

    # Write immediately
    save_table(fact_events, 'fact_events')  # Creates data/output/fact_events.csv

    return fact_events
```

**Why It's Good:**
- Can inspect output at any phase
- If ETL fails later, earlier CSVs are preserved
- Can compare outputs between runs
- Easy to share data with non-Python users

**How to Apply:**
1. After any significant transformation, write to CSV
2. Name files consistently (`fact_*.csv`, `dim_*.csv`)
3. Include row counts in logs for quick verification

---

### ✅ Pattern 3: Validation at Critical Points

**Where:** QA tables, goal verification

**What It Is:**
Validate calculated values against trusted external sources.

**Example:**
```python
def validate_goal_counts():
    """
    Calculated goals MUST match official league records.
    """
    # Get official counts from dim_schedule
    official = dim_schedule[['game_id', 'home_score', 'away_score']]

    # Get calculated counts from fact_events
    calculated = fact_events[fact_events['is_goal']].groupby(
        ['game_id', 'team_venue']
    ).size()

    # Compare
    for game_id in games:
        official_home = official.loc[game_id, 'home_score']
        calculated_home = calculated.get((game_id, 'home'), 0)

        if official_home != calculated_home:
            raise DataValidationError(
                f"Game {game_id}: Official {official_home} vs Calculated {calculated_home}"
            )
```

**Why It's Good:**
- Catches bugs before they reach users
- Builds trust in analytics
- Documents expected behavior
- Regression prevention

**How to Apply:**
1. Identify metrics with external truth (official scores, league stats)
2. Create QA tables that compare calculated vs official
3. Fail loudly if they don't match

---

### ✅ Pattern 4: Phase Isolation

**Where:** `run_etl.py`

**What It Is:**
Wrap each phase in try/except. Continue processing even if one phase fails.

**Example:**
```python
errors = []

# Phase 4: Core stats
try:
    from src.tables.core_facts import create_all_core_facts
    create_all_core_facts()
except Exception as e:
    errors.append(f"Core facts: {e}")
    log(f"Phase 4 FAILED: {e}", "ERROR")
    # Continue to Phase 5...

# Phase 5: Shift analytics
try:
    from src.tables.shift_analytics import create_all_shift_analytics
    create_all_shift_analytics()
except Exception as e:
    errors.append(f"Shift analytics: {e}")
```

**Why It's Good:**
- One broken phase doesn't stop everything
- Get partial results for debugging
- Clear error attribution
- Can identify independent failures

**How to Apply:**
1. Wrap each phase in try/except
2. Collect errors in a list
3. Report all errors at the end
4. Only hard-fail for critical phases (like Phase 1)

---

### ✅ Pattern 5: Builder Functions (Pure Functions)

**Where:** `src/builders/*.py`

**What It Is:**
Functions that take input DataFrames and return output DataFrames. No side effects.

**Example:**
```python
def build_fact_events(fact_event_players: pd.DataFrame) -> pd.DataFrame:
    """
    Transform fact_event_players into fact_events.

    Args:
        fact_event_players: Input DataFrame

    Returns:
        Transformed DataFrame (fact_events)
    """
    df = fact_event_players.copy()  # Don't modify input

    # Transform
    df = _add_priority(df)
    df = _collapse_to_events(df)
    df = _add_derived_columns(df)

    return df  # Return result, don't write to file
```

**Why It's Good:**
- Testable (can test with mock data)
- Predictable (same input → same output)
- Composable (can chain builders)
- Debuggable (can inspect intermediate results)

**How to Apply:**
1. Take input as parameters, return output
2. Don't modify input DataFrames (use `.copy()`)
3. Don't write to files inside builders
4. Let the caller decide what to do with results

---

### ✅ Pattern 6: Formulas in Configuration

**Where:** `config/formulas.json`

**What It Is:**
Define calculation weights and constants in JSON, not hardcoded in Python.

**Example:**
```json
// config/formulas.json
{
  "xg_base_rates": {
    "high_danger": 0.25,
    "medium_danger": 0.08,
    "low_danger": 0.03
  },
  "war_weights": {
    "goals": 1.0,
    "primary_assists": 0.7,
    "secondary_assists": 0.4
  }
}
```

```python
# In code:
import json

with open('config/formulas.json') as f:
    formulas = json.load(f)

xg_base = formulas['xg_base_rates'][danger_level]
```

**Why It's Good:**
- Change weights without code changes
- Non-developers can review/audit formulas
- Easy to version control formula changes
- Self-documenting

**How to Apply:**
1. Identify constants that might change
2. Move them to config/formulas.json
3. Load at runtime
4. Document what each value means

---

## Technical Debt (Understand and Improve)

### ✅ Debt 1: Monolithic base_etl.py - RESOLVED

**Where:** `src/core/base_etl.py` + `src/core/etl_phases/`

**What It Was:**
One file containing all ETL orchestration (4,400 lines).

**Current State (Refactored):**
```
# Before:
src/core/base_etl.py  (4,400 lines)

# After:
src/core/
├── base_etl.py           # Main orchestrator (~1,065 lines)
└── etl_phases/           # Modular implementations (~4,700 lines)
    ├── utilities.py
    ├── derived_columns.py
    ├── validation.py
    ├── event_enhancers.py
    ├── shift_enhancers.py
    ├── derived_event_tables.py
    └── reference_tables.py
```

**Refactoring Strategy:**
1. Extract one phase at a time
2. Keep old function as wrapper calling new module
3. Test thoroughly after each extraction
4. Eventually remove wrappers

---

### ⚠️ Debt 2: iterrows() Usage

**Where:** Multiple files including `base_etl.py`

**What It Is:**
Using pandas `iterrows()` for row-by-row processing.

**Example (Bad):**
```python
for idx, row in df.iterrows():
    df.at[idx, 'new_col'] = calculate_something(row['col1'], row['col2'])
```

**Why It's Bad:**
- Very slow (Python loop overhead)
- Doesn't use pandas optimizations
- Memory inefficient

**Better Approaches:**

```python
# Option 1: Vectorized operation (fastest)
df['new_col'] = df['col1'] * df['col2']

# Option 2: Apply with function (medium)
df['new_col'] = df.apply(
    lambda row: calculate_something(row['col1'], row['col2']),
    axis=1
)

# Option 3: Vectorized function (good for complex logic)
def calculate_something_vectorized(col1_series, col2_series):
    return col1_series * col2_series

df['new_col'] = calculate_something_vectorized(df['col1'], df['col2'])
```

**Where to Fix:**
- `build_player_lookup()` - Convert to dict comprehension
- Enhancement functions - Use vectorized operations

---

### ⚠️ Debt 3: Hardcoded Paths and Magic Numbers

**Where:** Various files

**What It Is:**
Paths and numbers embedded in code instead of configuration.

**Example (Bad):**
```python
# Hardcoded path
xlsx = pd.ExcelFile('data/raw/BLB_Tables.xlsx')

# Magic number
if shift_duration > 45:  # What is 45?
    quality = 'good'
```

**Better:**
```python
# From config
from config import PATHS, THRESHOLDS

xlsx = pd.ExcelFile(PATHS.BLB_TABLES)

# Named constant
if shift_duration > THRESHOLDS.GOOD_SHIFT_DURATION:
    quality = 'good'
```

**Where to Fix:**
1. Create `config/paths.py` for all file paths
2. Create `config/thresholds.py` for numeric thresholds
3. Document what each threshold means

---

### ⚠️ Debt 4: Sequential Phase Execution

**Where:** `run_etl.py`, `base_etl.py`

**What It Is:**
All phases run sequentially, even when some could parallelize.

**Current:**
```python
# These run one after another
create_fact_events()      # 5 seconds
create_fact_shifts()      # 3 seconds
create_fact_tracking()    # 2 seconds
# Total: 10 seconds
```

**Could Be:**
```python
# These could run in parallel (no dependencies)
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [
        executor.submit(create_fact_events),
        executor.submit(create_fact_shifts),
        executor.submit(create_fact_tracking),
    ]
    # Total: ~5 seconds (limited by slowest)
```

**Why It's Not Done:**
- Added complexity
- Need to identify true dependencies
- Debugging parallel code is harder
- Current runtime (~80s) is acceptable

**When to Fix:**
- When ETL runtime becomes a bottleneck
- When adding more games increases runtime significantly
- When moving to production with many users

---

### ⚠️ Debt 5: Inconsistent Error Handling

**Where:** Throughout ETL

**What It Is:**
Some functions raise exceptions, some return None, some log warnings.

**Example (Inconsistent):**
```python
# Function A raises
def process_game(game_id):
    if not validate(game_id):
        raise ValueError(f"Invalid game: {game_id}")

# Function B returns None
def load_tracking(game_id):
    if not file_exists(game_id):
        return None  # Caller must check!

# Function C logs and continues
def enhance_events(events):
    if events.empty:
        log.warning("Empty events, skipping")
        return events
```

**Better (Consistent):**
```python
# Define clear contract:
# - Functions raise exceptions for errors
# - Callers use try/except
# - Empty data is valid (not an error)

def process_game(game_id):
    """Process game. Raises GameError if invalid."""
    if not validate(game_id):
        raise GameError(f"Invalid game: {game_id}")

def load_tracking(game_id):
    """Load tracking. Raises FileNotFoundError if missing."""
    path = get_tracking_path(game_id)
    if not path.exists():
        raise FileNotFoundError(f"No tracking file: {path}")
    return pd.read_excel(path)
```

---

### ⚠️ Debt 6: No Caching Between Runs

**Where:** ETL pipeline

**What It Is:**
Every run recalculates everything from scratch.

**Impact:**
- 80 seconds for 4 games
- Linear scaling: 20 games = ~400 seconds
- Wastes time if only one game changed

**Potential Improvement:**
```python
def get_or_calculate_game_stats(game_id):
    """Load cached stats or calculate fresh."""
    cache_path = f'cache/game_{game_id}_stats.pkl'

    # Check if source data is newer than cache
    source_time = get_tracking_mtime(game_id)
    cache_time = get_cache_mtime(cache_path)

    if cache_time > source_time:
        return pd.read_pickle(cache_path)

    # Calculate fresh
    stats = calculate_game_stats(game_id)
    stats.to_pickle(cache_path)
    return stats
```

**Why It's Not Done:**
- Added complexity
- Cache invalidation is hard
- Current runtime acceptable
- --wipe option provides clean slate when needed

---

## Refactoring Priorities

If you're going to improve the codebase, prioritize:

### High Impact, Low Risk
1. **Replace `iterrows()` with vectorized operations**
   - Easy to do function by function
   - Immediate performance improvement
   - Low risk of breaking things

2. **Move magic numbers to config**
   - Search for numeric literals
   - Create named constants
   - Document what they mean

### Medium Impact, Medium Risk
3. **Split base_etl.py**
   - Extract one phase at a time
   - Keep wrappers for compatibility
   - Test after each extraction

4. **Standardize error handling**
   - Define clear patterns
   - Apply consistently
   - Add type hints

### Low Priority (Future)
5. **Add caching**
   - Only when runtime becomes a problem
   - Complex to implement correctly

6. **Parallelize phases**
   - Requires dependency analysis
   - Added complexity

---

## Testing Your Changes

Before and after any refactoring:

```bash
# 1. Run ETL with wipe
./benchsight.sh etl run --wipe

# 2. Validate outputs
./benchsight.sh etl validate

# 3. Check goal counts
python -c "
import pandas as pd
events = pd.read_csv('data/output/fact_events.csv')
goals = events[(events['event_type'] == 'Goal') & (events['event_detail'] == 'Goal_Scored')]
print(f'Goals: {len(goals)}')
"

# 4. Compare table counts
ls data/output/*.csv | wc -l
# Should be 138+
```

---

## Key Takeaways

### Good Patterns to Use
1. Single source of truth for business logic
2. CSV as debuggable intermediate
3. Validation at critical points
4. Phase isolation with try/except
5. Builder functions (pure functions)
6. Formulas in configuration

### Technical Debt to Address
1. Monolithic base_etl.py → Split into modules
2. iterrows() → Vectorized operations
3. Hardcoded values → Configuration
4. Sequential execution → (Future) Parallelize
5. Inconsistent errors → Standardize patterns
6. No caching → (Future) Add intelligent caching

### Refactoring Safely
1. One change at a time
2. Test before and after
3. Keep old interfaces as wrappers
4. Document what you changed

---

**Next:** [07-data-model.md](07-data-model.md) - Understanding the 139 tables
