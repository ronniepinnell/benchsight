# BenchSight Code Quality Standards

Last Updated: 2026-01-13
Version: 29.0

## Purpose

This document defines coding standards for BenchSight. **All code must be production-quality, not patchwork.**

---

## Core Principles

### 1. Root-Level Architecture (Not Patchwork)

```
❌ BAD: Patches on patches
- Quick fixes that don't address root cause
- Workarounds that add complexity
- "It works" without understanding why

✅ GOOD: Root-level solutions
- Fix the actual problem, not symptoms
- Understand the full data flow
- Clean, maintainable code
```

### 2. Single Source of Truth

```python
# ❌ BAD: Duplicated logic
def count_goals_v1():
    return events[events.event_type == 'Goal']

def count_goals_v2():  # Different logic!
    return events[events.event_detail == 'Goal_Scored']

# ✅ GOOD: One canonical implementation
GOAL_FILTER = (events.event_type == 'Goal') & (events.event_detail == 'Goal_Scored')

def count_goals():
    return events[GOAL_FILTER]
```

### 3. Explicit Over Implicit

```python
# ❌ BAD: Magic numbers, unclear intent
df = df[df.col > 5]

# ✅ GOOD: Named constants, clear purpose
MIN_GAMES_FOR_STATS = 5
df = df[df.games_played > MIN_GAMES_FOR_STATS]
```

---

## Real Example: game_type_aggregator (v29.0)

This is the canonical example of proper architecture vs patchwork.

### The Problem

Six different functions needed to split season stats by game_type (Regular/Playoffs/All).

### ❌ BAD (patchwork) - What NOT to do:

```python
# File: macro_stats.py
def create_fact_team_season_stats_basic():
    GAME_TYPES = ['Regular', 'Playoffs', 'All']  # Duplicated constant
    df = df.merge(schedule[['game_id', 'game_type']], ...)  # Duplicated join
    df['game_type'] = df['game_type'].fillna('Regular')  # Duplicated logic
    ...

# File: remaining_facts.py  
def create_fact_player_season_stats():
    GAME_TYPES = ['Regular', 'Playoffs', 'All']  # Same constant, different file!
    df = df.merge(schedule[['game_id', 'game_type']], ...)  # Same pattern!
    df['game_type'] = df['game_type'].fillna('Regular')  # Copy-paste!
    ...
```

**Problems:**
- Same logic in 6 places across 2 files
- If we add 'Preseason', we must edit 6 functions
- Each function might have subtle differences
- No tests for the shared pattern

### ✅ GOOD (root-level) - What we did:

Created `src/utils/game_type_aggregator.py`:

```python
# SINGLE SOURCE OF TRUTH
GAME_TYPE_SPLITS = ['Regular', 'Playoffs', 'All']

def add_game_type_to_df(df, schedule):
    """Add game_type column via schedule join."""
    df = df.merge(schedule[['game_id', 'game_type']], on='game_id', how='left')
    df['game_type'] = df['game_type'].fillna('Regular')
    return df

def get_team_record_from_schedule(schedule, team_id, season_id, game_type):
    """Calculate W-L-T from schedule."""
    ...
```

Now all 6 functions use the shared utility:

```python
from src.utils.game_type_aggregator import GAME_TYPE_SPLITS, add_game_type_to_df

def create_fact_team_season_stats_basic():
    df = add_game_type_to_df(df, schedule)  # One-liner
    for game_type in GAME_TYPE_SPLITS:      # Uses constant
        ...
```

**Benefits:**
- Change `GAME_TYPE_SPLITS` once → affects all 6 tables
- Shared join logic is tested once
- Easy to understand and maintain
- Pattern is documented in one place

---

## Data Engineering Standards

### ETL Pipeline Rules

1. **Idempotent**: Running ETL twice produces same result
2. **Atomic**: Either all tables update or none do
3. **Traceable**: Every value can be traced to source
4. **Validated**: Automated checks catch errors

### Column Naming

```
snake_case for all columns
- player_id (not playerId, PlayerID)
- goals_scored (not GoalsScored)
- created_at (not createdAt)
```

### Type Consistency

```python
# Define types explicitly
COLUMN_TYPES = {
    'player_id': str,      # Always string IDs
    'game_id': int,        # Always integer
    'goals': int,          # Counts are integers
    'shooting_pct': float, # Percentages are floats
    'game_date': datetime, # Dates are datetime
}
```

### Null Handling

```python
# ❌ BAD: Inconsistent null handling
df['col'].fillna(0)  # Sometimes
df['col'].fillna('')  # Other times

# ✅ GOOD: Explicit null strategy per column type
NULL_STRATEGY = {
    'count_columns': 0,      # Nulls become 0
    'text_columns': None,    # Nulls stay null
    'percentage_columns': None,  # Can't calculate = null
}
```

---

## Software Development Standards

### Function Design

```python
# ❌ BAD: Does too much, unclear purpose
def process_data(df):
    # 200 lines of mixed logic
    pass

# ✅ GOOD: Single responsibility, clear purpose
def load_events(filepath: Path) -> pd.DataFrame:
    """Load raw events from CSV."""
    pass

def filter_goals(events: pd.DataFrame) -> pd.DataFrame:
    """Filter events to only goals."""
    pass

def aggregate_by_player(goals: pd.DataFrame) -> pd.DataFrame:
    """Sum goals per player."""
    pass
```

### Error Handling

```python
# ❌ BAD: Silent failures
try:
    result = risky_operation()
except:
    pass

# ✅ GOOD: Explicit error handling
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"Invalid value in risky_operation: {e}")
    raise
except FileNotFoundError:
    logger.warning("File not found, using defaults")
    result = default_value
```

### Logging

```python
# ❌ BAD: Print statements
print("Processing...")

# ✅ GOOD: Structured logging
logger.info(f"Processing {len(df)} rows from {source}")
logger.debug(f"Column types: {df.dtypes.to_dict()}")
```

### Testing

```python
# Every calculation should have a test
def test_goal_counting():
    """Verify goals counted correctly."""
    events = create_test_events(goals=5, shots=10)
    result = count_goals(events)
    assert result == 5, f"Expected 5 goals, got {result}"
```

---

## Documentation Standards

### Every Table Must Have

```markdown
## table_name

**Description:** What this table contains
**Purpose:** Why it exists, what queries it enables
**Source Module:** src/path/to/module.py:function_name()
**Logic:** How rows are generated
**Grain:** What one row represents
**Rows:** Current count
**Columns:** Current count

### Column Documentation

| Column | Type | Description | Calculation | Validated |
|--------|------|-------------|-------------|-----------|
| col1   | int  | ...         | SUM(...)    | ✓         |
```

### Every Column Must Have

1. **Data Type**: PostgreSQL type
2. **Description**: What it represents
3. **Context/Mapping**: FK relationships, source field
4. **Calculation/Formula**: How it's computed (if derived)
5. **Column Type**: Explicit/Calculated/Derived/FK
6. **Validation Status**: Yes/No/Partial

---

## Code Review Checklist

Before any code is committed:

```
□ Does it solve the root problem (not a workaround)?
□ Is there a single source of truth for each calculation?
□ Are all constants named and documented?
□ Is error handling explicit?
□ Are there tests for new calculations?
□ Is the data dictionary updated?
□ Does validate.py catch potential errors?
```

---

## Anti-Patterns to Avoid

### 1. Copy-Paste Programming
```
❌ Copying code instead of creating reusable functions
```

### 2. Stringly Typed
```
❌ Using strings where enums/constants should be used
   event_type == "goal"  # Typo-prone
✅ event_type == EventType.GOAL
```

### 3. Premature Optimization
```
❌ Making code complex for "performance" before measuring
✅ Write clear code first, optimize with profiling data
```

### 4. Comment-Driven Development
```
❌ # TODO: Fix this later
❌ # HACK: This shouldn't work but it does
✅ Fix it now or create a tracked issue
```

### 5. Magic Values
```
❌ if status == 3:  # What is 3?
✅ if status == GameStatus.COMPLETED:
```

---

## Version Control

### Commit Messages

```
# Format: [TYPE] Brief description

[FIX] Correct goal counting to use Goal_Scored filter
[FEAT] Add player career stats table
[DOCS] Update data dictionary for fact_events
[REFACTOR] Extract common filtering logic
```

### Branch Strategy

```
main          - Production-ready code
feature/*     - New features
fix/*         - Bug fixes
docs/*        - Documentation updates
```

---

## Memory for Future Chats

Claude should remember:
1. **Root-level solutions** - Fix actual problems, not symptoms
2. **Single source of truth** - One canonical implementation per calculation
3. **Explicit over implicit** - Named constants, clear types
4. **Document everything** - Data dictionary must be current
5. **Test calculations** - Every formula should be verifiable

---

## Quick Reference

```python
# Goal Counting (THE canonical way)
GOAL_FILTER = (
    (df['event_type'] == 'Goal') & 
    (df['event_detail'] == 'Goal_Scored')
)

# Player Attribution - CRITICAL
PRIMARY_PLAYER = 'event_player_1'    # Gets credit for ALL events (goals, shots, passes, etc.)

# Assists - via play_detail1 on the ASSIST event (not on goal event)
# AssistPrimary = A1, AssistSecondary = A2
# The assister is event_player_1 on their pass/shot event with play_detail1='AssistPrimary'

# Faceoffs
# Winner = event_player_1 on faceoff event
# Loser = opp_player_1 on faceoff event

# play_detail counts - use DISTINCT by linked_event_index_flag to avoid double-counting

# Null-like values
NULL_VALUES = ('nan', 'none', 'null', 'nat', 'n/a', 'na', '-', 'fa', 'ir', 'tbd', 'unknown')
```

---

## v26.2 Critical Player Attribution Rules

### CORRECTED: event_player_1 Gets Credit

**Shots, Passes, Zone Entries/Exits, Turnovers:**
```python
pe_primary = pe[pe['player_role'].astype(str).str.lower() == 'event_player_1']
shots = pe_primary[pe_primary['event_type'] == 'shot']
```

**Assists - Via play_detail1:**
```python
primary_assists = pe_primary[pe_primary['play_detail1'] == 'AssistPrimary']
secondary_assists = pe_primary[pe_primary['play_detail1'] == 'AssistSecondary']
```

**Faceoffs:**
```python
fo_wins = faceoffs[faceoffs['player_role'] == 'event_player_1']
fo_losses = faceoffs[faceoffs['player_role'] == 'opp_player_1']
```

**Blocks - Avoid Double Counting:**
```python
blocks_df = pe[pe['play_detail1'].str.contains('BlockedShot')]
if 'linked_event_index_flag' in blocks_df.columns:
    linked = blocks_df[blocks_df['linked_event_index_flag'].notna()]
    unlinked = blocks_df[blocks_df['linked_event_index_flag'].isna()]
    blocks = linked['linked_event_index_flag'].nunique() + len(unlinked)
```

### CORRECTED: Shift Counting

```python
# WRONG:
shift_count = len(shift_player_rows)  # Overcounts

# CORRECT:
shift_count = shift_players['logical_shift_number'].nunique()
avg_shift = toi_seconds / shift_count
```

### CORRECTED: Rating Diff

```python
# WRONG:
rating_diff = player_rating - opp_avg_rating  # Backwards

# CORRECT:
rating_diff = opp_avg_rating - player_rating
# Positive = facing tougher competition
# Negative = facing weaker competition
```

### Rush Success Metrics

```python
# Offensive success = event_successful OR shot within 10s
quick_shot = rush_events['time_to_next_sog'] <= 10
success = (rush_events['event_successful'] == True) | quick_shot

# Defensive success = no shot within 15s
def_success = (rush_events['time_to_next_sog'].isna()) | (rush_events['time_to_next_sog'] > 15)
```

### play_detail_successful Values (CRITICAL)

```python
# play_detail_successful column tracks outcome of micro plays
# s = Successful (play achieved its purpose)
# u = Unsuccessful (play failed)
# blank/NaN = Not tracked/not applicable - DO NOT COUNT

# Example: Deke with 's' = beat the defender, 'u' = got stopped
# NEVER count blanks as successful OR unsuccessful
```

### Zone Entry Shot Generation

```python
# Get time_to_next_sog from events table
merged = zone_events.merge(events[['event_id', 'time_to_next_sog']], on='event_id')
shot_generated = (merged['time_to_next_sog'].notna()) & (merged['time_to_next_sog'] <= 10)
goal_generated = (merged['time_to_next_goal'].notna()) & (merged['time_to_next_goal'] <= 15)
```

---

## Type Safety for Merges

Always ensure consistent types before merging:

```python
# Fix type mismatch
zone_events[type_col] = zone_events[type_col].astype(str)
types_df[type_col] = types_df[type_col].astype(str)
merged = zone_events.merge(types_df, on=type_col, how='left')
```

---
