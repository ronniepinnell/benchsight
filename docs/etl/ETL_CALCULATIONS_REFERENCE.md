# BenchSight ETL Calculations Reference

**Complete reference for all stat calculations and formulas**

Last Updated: 2026-01-21
Version: 2.00

---

## Overview

This document catalogs all calculation functions and formulas used in the BenchSight ETL pipeline. Calculations are organized by category and include formulas, dependencies, and usage examples.

**Calculation Modules:** 5 modules in `src/calculations/`  
**Formula Definitions:** `config/formulas.json`  
**Formula Engine:** `src/formulas/formula_applier.py`

---

## Calculation Modules

### 1. Goals (`src/calculations/goals.py`)

**Purpose:** Goal counting and identification

#### Functions

| Function | Purpose | Parameters | Returns |
|----------|---------|------------|---------|
| `is_goal_scored()` | Check if event is a goal | `event_type`, `event_detail` | `bool` |
| `filter_goals()` | Filter events to goals only | `events_df` | `DataFrame` |

#### Goal Counting Rule (CRITICAL)

**Goals are ONLY counted when:**
```python
event_type == 'Goal' AND event_detail == 'Goal_Scored'
```

**NOT counted:**
- `event_type == 'Shot'` with `event_detail == 'Goal'` (this is a shot attempt, not a goal)
- Other event types

**Usage:**
```python
from src.calculations.goals import is_goal_scored, filter_goals

# Check if event is goal
if is_goal_scored(event_type='Goal', event_detail='Goal_Scored'):
    # This is a goal

# Filter to goals only
goals_df = filter_goals(events_df)
```

---

### 2. Corsi/Fenwick (`src/calculations/corsi.py`)

**Purpose:** Corsi and Fenwick shot attempt calculations

#### Functions

| Function | Purpose | Parameters | Returns |
|----------|---------|------------|---------|
| `is_sog_event()` | Check if shot on goal | `event_type`, `event_detail` | `bool` |
| `is_blocked_shot()` | Check if blocked shot | `event_detail` | `bool` |
| `is_missed_shot()` | Check if missed shot | `event_detail` | `bool` |
| `is_corsi_event()` | Check if Corsi event | `event_type`, `event_detail` | `bool` |
| `is_fenwick_event()` | Check if Fenwick event | `event_type`, `event_detail` | `bool` |
| `calculate_corsi_for_player()` | Calculate Corsi for player | `events_df`, `player_id`, `team_id` | `dict` |
| `calculate_fenwick_for_player()` | Calculate Fenwick for player | `events_df`, `player_id`, `team_id` | `dict` |
| `calculate_cf_pct()` | Calculate CF% | `cf`, `ca` | `float` |
| `calculate_ff_pct()` | Calculate FF% | `ff`, `fa` | `float` |

#### Definitions

**Corsi (CF/CA):**
- **CF (Corsi For):** Shots on goal + blocked shots + missed shots (for)
- **CA (Corsi Against):** Shots on goal + blocked shots + missed shots (against)
- **CF%:** `CF / (CF + CA) * 100`

**Fenwick (FF/FA):**
- **FF (Fenwick For):** Shots on goal + missed shots (for) - excludes blocked shots
- **FA (Fenwick Against):** Shots on goal + missed shots (against) - excludes blocked shots
- **FF%:** `FF / (FF + FA) * 100`

**Usage:**
```python
from src.calculations.corsi import is_corsi_event, calculate_cf_pct

# Check if Corsi event
if is_corsi_event(event_type='Shot', event_detail='Wrist_Shot'):
    # This counts toward Corsi

# Calculate CF%
cf_pct = calculate_cf_pct(cf=10, ca=5)  # Returns 66.67
```

---

### 3. Ratings (`src/calculations/ratings.py`)

**Purpose:** Player and team rating calculations

#### Functions

| Function | Purpose | Parameters | Returns |
|----------|---------|------------|---------|
| `calculate_team_ratings()` | Calculate team ratings | `player_stats_df` | `dict` |
| `calculate_rating_differential()` | Calculate rating difference | `player_rating`, `opp_rating` | `float` |
| `calculate_expected_cf_pct()` | Calculate expected CF% | `player_rating`, `opp_rating` | `float` |
| `calculate_cf_pct_vs_expected()` | CF% vs expected | `actual_cf_pct`, `expected_cf_pct` | `float` |
| `calculate_opponent_multiplier()` | Opponent strength multiplier | `opp_avg_rating` | `float` |

**Usage:**
```python
from src.calculations.ratings import calculate_team_ratings

# Calculate team ratings
team_ratings = calculate_team_ratings(player_stats_df)
# Returns: {'avg_rating': 75.5, 'weighted_rating': 78.2, ...}
```

---

### 4. Time (`src/calculations/time.py`)

**Purpose:** Time on ice and time-based calculations

#### Functions

| Function | Purpose | Parameters | Returns |
|----------|---------|------------|---------|
| `calculate_toi_seconds()` | Calculate TOI in seconds | `shift_data` | `float` |
| `calculate_toi_minutes()` | Convert seconds to minutes | `toi_seconds` | `float` |
| `calculate_shift_duration()` | Calculate shift duration | `shift_start`, `shift_end` | `float` |
| `calculate_per_60_rate()` | Calculate per-60 rate | `stat`, `toi_minutes` | `float` |
| `calculate_per_60_from_seconds()` | Per-60 from seconds | `stat`, `toi_seconds` | `float` |

**Usage:**
```python
from src.calculations.time import calculate_toi_minutes, calculate_per_60_rate

# Convert TOI
toi_minutes = calculate_toi_minutes(toi_seconds=1200)  # Returns 20.0

# Calculate per-60 rate
goals_per_60 = calculate_per_60_rate(goals=5, toi_minutes=20)  # Returns 15.0
```

---

### 5. Goalie Calculations (`src/calculations/goalie_calculations.py`)

**Purpose:** Goalie-specific stat calculations

#### Functions

| Function | Purpose | Parameters | Returns |
|----------|---------|------------|---------|
| `calculate_goalie_core_stats()` | Core goalie stats | `saves_df`, `goals_df` | `dict` |
| `calculate_goalie_save_types()` | Save type breakdown | `goalie_saves` | `dict` |
| `calculate_goalie_high_danger()` | High-danger save stats | `saves_df` | `dict` |
| `calculate_goalie_rebound_control()` | Rebound control stats | `saves_df` | `dict` |
| `calculate_goalie_period_splits()` | Period-by-period stats | `saves_df`, `goals_df` | `dict` |
| `calculate_goalie_time_buckets()` | Time bucket stats | `saves_df`, `goals_df` | `dict` |
| `calculate_goalie_shot_context()` | Shot context stats | `saves_df` | `dict` |
| `calculate_goalie_pressure_handling()` | Pressure handling stats | `saves_df` | `dict` |
| `calculate_goalie_quality_indicators()` | Quality indicators | `stats` | `dict` |
| `calculate_goalie_composites()` | Composite metrics | `stats` | `dict` |
| `calculate_goalie_war()` | WAR calculation | `stats` | `dict` |

**Usage:**
```python
from src.calculations.goalie_calculations import calculate_goalie_core_stats

# Calculate core goalie stats
goalie_stats = calculate_goalie_core_stats(saves_df, goals_df)
# Returns: {'saves': 25, 'goals_against': 2, 'save_pct': 0.926, ...}
```

---

## Formula System

### Formula Definition Format

Formulas are defined in `config/formulas.json`:

```json
{
  "formula_name": {
    "type": "percentage|rate|sum|difference|ratio",
    "expression": "mathematical expression",
    "description": "Human-readable description",
    "dependencies": ["column1", "column2"],
    "default_value": 0.0,
    "condition": "optional condition (e.g., 'denominator > 0')"
  }
}
```

### Formula Types

| Type | Purpose | Example |
|------|---------|---------|
| `percentage` | Percentage calculation | `goals / sog * 100` |
| `rate` | Per-60 rate | `goals / toi_minutes * 60` |
| `sum` | Sum of columns | `goals + assists` |
| `difference` | Difference of columns | `plus_total - minus_total` |
| `ratio` | Ratio calculation | `toi_seconds / shifts / 60` |

### Key Formulas

#### Shooting Percentage
```json
{
  "shooting_pct": {
    "type": "percentage",
    "expression": "goals / sog * 100",
    "condition": "sog > 0"
  }
}
```

#### Corsi For Percentage
```json
{
  "cf_pct": {
    "type": "percentage",
    "expression": "cf / (cf + ca) * 100",
    "condition": "(cf + ca) > 0"
  }
}
```

#### Goals Per 60
```json
{
  "goals_per_60": {
    "type": "rate",
    "expression": "goals / toi_minutes * 60",
    "condition": "toi_minutes > 0"
  }
}
```

#### Points
```json
{
  "points": {
    "type": "sum",
    "expression": "goals + assists"
  }
}
```

#### Plus/Minus
```json
{
  "plus_minus": {
    "type": "difference",
    "expression": "plus_total - minus_total"
  }
}
```

---

## Formula Application

### How Formulas Are Applied

1. **Formula Registry** (`src/formulas/registry.py`)
   - Loads formulas from `config/formulas.json`
   - Validates formula syntax
   - Caches formulas

2. **Formula Applier** (`src/formulas/formula_applier.py`)
   - Applies formulas to DataFrames
   - Handles missing values
   - Applies conditions

3. **Usage in Table Builders**
   ```python
   from src.formulas.formula_applier import apply_player_stats_formulas
   
   # Apply all formulas to player stats
   stats_df = apply_player_stats_formulas(stats_df)
   ```

---

## Calculation Patterns

### Pattern 1: Filtering Events

```python
# Filter to specific event types
goals = events_df[events_df['event_type'] == 'Goal']
shots = events_df[events_df['event_type'] == 'Shot']

# Use calculation functions
from src.calculations.goals import filter_goals
goals = filter_goals(events_df)
```

### Pattern 2: Aggregating Stats

```python
# Group by player and aggregate
player_stats = events_df.groupby('player_id').agg({
    'goals': 'sum',
    'assists': 'sum',
    'shots': 'sum'
})
```

### Pattern 3: Calculating Rates

```python
# Calculate per-60 rates
from src.calculations.time import calculate_per_60_rate

player_stats['goals_per_60'] = player_stats.apply(
    lambda row: calculate_per_60_rate(row['goals'], row['toi_minutes']),
    axis=1
)
```

### Pattern 4: Applying Formulas

```python
# Apply formulas from JSON
from src.formulas.formula_applier import apply_player_stats_formulas

stats_df = apply_player_stats_formulas(stats_df)
# Automatically calculates: shooting_pct, goals_per_60, cf_pct, etc.
```

---

## Common Calculations

### Player Stats

| Stat | Formula | Module |
|------|---------|--------|
| Goals | Count `event_type='Goal' AND event_detail='Goal_Scored'` | `goals.py` |
| Assists | Sum of primary + secondary assists | Formula |
| Points | `goals + assists` | Formula |
| SOG | Count shots on goal | `corsi.py` |
| Shooting % | `goals / sog * 100` | Formula |
| CF | Corsi For (shots + blocked + missed) | `corsi.py` |
| CA | Corsi Against | `corsi.py` |
| CF% | `CF / (CF + CA) * 100` | `corsi.py` |
| FF% | `FF / (FF + FA) * 100` | `corsi.py` |
| Goals/60 | `goals / toi_minutes * 60` | Formula |
| Points/60 | `points / toi_minutes * 60` | Formula |

### Goalie Stats

| Stat | Formula | Module |
|------|---------|--------|
| Saves | Count saves | `goalie_calculations.py` |
| Goals Against | Count goals allowed | `goalie_calculations.py` |
| Save % | `saves / (saves + goals_against) * 100` | Formula |
| GAA | `goals_against / toi_minutes * 60` | Formula |
| High-Danger Save % | `hd_saves / hd_shots * 100` | `goalie_calculations.py` |
| Rebound Control | Rebound save stats | `goalie_calculations.py` |

---

## Adding New Calculations

### Step 1: Create Calculation Function

```python
# src/calculations/my_calculation.py
def calculate_my_stat(data: pd.DataFrame) -> float:
    """Calculate my custom stat."""
    return result
```

### Step 2: Add Formula (if needed)

```json
{
  "my_stat_per_60": {
    "type": "rate",
    "expression": "my_stat / toi_minutes * 60",
    "condition": "toi_minutes > 0"
  }
}
```

### Step 3: Use in Table Builder

```python
# src/tables/core_facts.py
from src.calculations.my_calculation import calculate_my_stat

def create_fact_player_game_stats():
    # ... existing code ...
    stats['my_stat'] = calculate_my_stat(events_df)
    # ... apply formulas ...
```

---

## Related Documentation

- [CODE_FLOW_ETL.md](CODE_FLOW_ETL.md) - Execution flow
- [ETL_ARCHITECTURE.md](ETL_ARCHITECTURE.md) - Module architecture
- [ETL_TABLE_DEPENDENCIES.md](ETL_TABLE_DEPENDENCIES.md) - Table dependencies
- [ETL_DATA_FLOW.md](ETL_DATA_FLOW.md) - Data transformations
- [config/formulas.json](../../config/formulas.json) - Formula definitions

---

*Last Updated: 2026-01-15*
