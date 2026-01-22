# 05 - ETL Code Walkthrough (Annotated)

**Learning Objectives:**
- Read and understand actual ETL code with explanations
- Trace a goal from tracking input to final statistics
- Understand key functions and why they're written this way

---

## Overview

This walkthrough covers three key files:
1. `run_etl.py` - Entry point (~450 lines)
2. `src/core/base_etl.py` - Orchestrator (~4,400 lines)
3. `src/calculations/goals.py` - Critical calculation (~135 lines)

We'll read the actual code with annotations explaining WHY each part exists.

---

## File 1: run_etl.py (Entry Point)

📍 **File:** `/run_etl.py`

### The Docstring (Lines 1-34)

```python
#!/usr/bin/env python3
"""
================================================================================
BENCHSIGHT ETL - SINGLE SOURCE OF TRUTH
================================================================================

THIS IS THE ONLY FILE YOU SHOULD RUN FOR ETL.

Creates 128 tables including:
- 55 dimension tables (dim_*)
- 65 fact tables (fact_*)
- 4 QA tables (qa_*)
- 1 lookup table

Usage:
    python run_etl.py              # Full ETL (~80 seconds, 128 tables)
    python run_etl.py --wipe       # CLEAN SLATE: Delete all output then run ETL
    python run_etl.py --validate   # Check all tables exist
    python run_etl.py --status     # Show current status
"""
```

💡 **Why This Matters:**
- Clear entry point documentation prevents confusion
- "SINGLE SOURCE OF TRUTH" - don't run other files directly
- Shows expected runtime (~80 seconds) so you know if something's wrong

### Setup and Paths (Lines 36-48)

```python
import sys
import os
from pathlib import Path
from datetime import datetime
import traceback

# Ensure we can import from src
PROJECT_ROOT = Path(__file__).parent          # 🔑 Get project root dynamically
sys.path.insert(0, str(PROJECT_ROOT))         # 🔑 Add to Python path for imports

# Paths
OUTPUT_DIR = PROJECT_ROOT / 'data' / 'output'
EXPECTED_TABLE_COUNT = 138                    # 🔑 Minimum required tables
```

💡 **Why This Pattern:**
- `Path(__file__).parent` - Works regardless of where you run from
- `sys.path.insert(0, ...)` - Allows `from src.core import ...` to work
- `EXPECTED_TABLE_COUNT` - Fail fast if ETL is incomplete

### The Main ETL Function (Lines 75-304)

```python
def run_full_etl():
    """
    Run the complete ETL pipeline.

    This is THE function that creates all tables.
    """
    start_time = datetime.now()

    # ... header printing ...

    errors = []  # 🔑 Collect errors but continue processing
```

💡 **Error Handling Strategy:**
- Collect errors in a list, don't fail immediately
- Some phases can fail without breaking others
- Report all errors at the end

### Phase Execution Pattern (Lines 94-106)

```python
    # =========================================================================
    # PHASE 1 & 2 & 3: Base ETL (BLB data + Tracking + Derived tables)
    # =========================================================================
    log_phase(1, "BASE ETL (BLB + Tracking + Derived Tables)")
    try:
        from src.core.base_etl import main as run_base_etl  # 🔑 Import at runtime
        run_base_etl()
        log(f"Base ETL complete: {count_tables()} tables")
    except Exception as e:
        errors.append(f"Base ETL: {e}")
        log(f"Base ETL FAILED: {e}", "ERROR")
        traceback.print_exc()
        return False  # 🔑 Can't continue without base tables
```

💡 **Key Design Decisions:**

1. **Import at runtime** (`from src.core.base_etl import main as run_base_etl`)
   - Why: Reduces startup time
   - Why: Module might not exist in some configurations
   - Why: Easier to see what each phase depends on

2. **Try/except per phase**
   - Why: Isolate failures
   - Why: Continue with other phases if possible
   - Why: Collect all errors for reporting

3. **`return False` for base phase**
   - Why: All other phases depend on base tables
   - Why: No point continuing with incomplete data

### All Phases Summary (Lines 94-278)

| Phase | Import | Purpose |
|-------|--------|---------|
| 1-3 | `base_etl.main` | BLB + Tracking + Derived |
| 3B | `dimension_tables.create_all_dimension_tables` | Static dims |
| 4 | `core_facts.create_all_core_facts` | Player stats |
| 4B | `shift_analytics.create_all_shift_analytics` | H2H, WOWY |
| 4C | `remaining_facts.build_remaining_tables` | Other facts |
| 4D | `event_analytics.create_all_event_analytics` | Rush events |
| 4E | `shot_chain_builder.build_shot_chains` | Shot chains |
| 5 | `add_all_fkeys.main` | Foreign keys |
| 6 | `extended_tables.create_extended_tables` | Extended tables |
| 7 | `post_etl_processor.main` | Post processing |
| 8 | `event_time_context.enhance_event_tables` | Time context |
| 9 | `build_qa_facts.main` | QA tables |
| 10 | `v11_enhancements.run_all_enhancements` | V11 enhancements |
| 10B | `xy_table_builder.build_all_xy_tables` | XY tables |
| 11 | `macro_stats.create_all_macro_stats` | Season/career stats |

### Command Line Interface (Lines 351-449)

```python
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='BenchSight ETL - Single Source of Truth',
        # ...
    )

    # Action modes
    parser.add_argument('--validate', action='store_true')
    parser.add_argument('--status', action='store_true')
    parser.add_argument('--list-games', action='store_true')

    # ETL options
    parser.add_argument('--wipe', '--clean', action='store_true', dest='wipe')
    parser.add_argument('--games', '-g', nargs='+', type=int)
```

💡 **Why argparse:**
- Standard Python CLI library
- Generates help text automatically
- Handles argument validation

### Wipe Mode (Lines 429-446)

```python
        if args.wipe:
            print("⚠️  WARNING: This will delete ALL tables, including dependencies.")
            csv_files = list(OUTPUT_DIR.glob('*.csv'))
            if csv_files:
                for f in csv_files:
                    f.unlink()  # 🔑 Delete file
                print(f"Deleted {len(csv_files)} CSV files from {OUTPUT_DIR}")
```

💡 **Why Wipe Exists:**
- Later phases depend on earlier phase outputs
- If you change Phase 3 code, Phase 6 outputs become stale
- Wipe ensures clean slate, no orphan data

---

## File 2: goals.py (Critical Calculation)

📍 **File:** `/src/calculations/goals.py`

🔑 **This is the most important 135 lines in the codebase.**

### The Header Comment (Lines 1-11)

```python
"""
Goal Counting Calculations

CRITICAL: This is the SINGLE SOURCE OF TRUTH for goal counting.
All goal counting throughout the codebase MUST use these functions.

Rules:
- Goals ONLY via: event_type='Goal' AND event_detail='Goal_Scored'
- Shot_Goal = the shot attempt, NOT the goal itself
- event_player_1 = Primary actor (scorer)
"""
```

💡 **Why This Header Matters:**
- **SINGLE SOURCE OF TRUTH** - Every developer knows to use this file
- **Rules** - Documents the business logic for non-developers
- **Shot_Goal warning** - Common mistake that this prevents

### The Canonical Goal Filter (Lines 21-37)

```python
def get_goal_filter(events_df: pd.DataFrame) -> pd.Series:
    """
    Get boolean filter for goal events.

    CRITICAL: This is THE canonical way to filter goals.
    Goals ONLY via: event_type='Goal' AND event_detail='Goal_Scored'

    Args:
        events_df: DataFrame with event_type and event_detail columns

    Returns:
        Boolean Series where True indicates a goal event
    """
    return (
        (events_df['event_type'] == 'Goal') &
        (events_df['event_detail'] == 'Goal_Scored')
    )
```

💡 **Why This Function Exists:**

**The Problem It Solves:**
```python
# WITHOUT this function, different developers might write:

# Developer A (WRONG):
goals = df[df['event_type'] == 'Goal']  # Missing event_detail check!

# Developer B (WRONG):
goals = df[df['event_detail'] == 'Shot_Goal']  # Shot_Goal is a shot, not a goal!

# Developer C (WRONG):
goals = df[df['event_type'] == 'Shot'][df['event_detail'] == 'Goal']  # Also wrong!
```

**The Solution:**
```python
# WITH this function, everyone uses the same logic:
from src.calculations.goals import get_goal_filter, filter_goals

# Correct way 1:
goal_mask = get_goal_filter(events_df)
goals = events_df[goal_mask]

# Correct way 2:
goals = filter_goals(events_df)
```

✅ **Good Pattern:** Single source of truth prevents inconsistencies

### Row-Level Check (Lines 40-51)

```python
def is_goal_scored(event_type: str, event_detail: str) -> bool:
    """
    Check if an event represents a scored goal.

    Args:
        event_type: Event type string
        event_detail: Event detail string

    Returns:
        True if this is a scored goal event
    """
    return event_type == 'Goal' and event_detail == 'Goal_Scored'
```

💡 **Why Both Functions:**
- `get_goal_filter()` - For DataFrame operations (fast, vectorized)
- `is_goal_scored()` - For row-by-row checks (when you have single values)

### Player Goal Count (Lines 70-97)

```python
def count_goals_for_player(
    events_df: pd.DataFrame,
    player_id: str,
    team_id: Optional[str] = None
) -> int:
    """
    Count goals scored by a specific player.

    Uses event_player_1 as the scorer (primary actor).
    """
    goals = filter_goals(events_df)  # 🔑 Use canonical filter

    # Filter by player (event_player_1 is the scorer)
    player_goals = goals[goals['event_player_1'] == player_id]

    # Optional team filter
    if team_id is not None:
        player_goals = player_goals[player_goals['team_id'] == team_id]

    return len(player_goals)
```

💡 **Key Insights:**

1. **`event_player_1`** = the scorer
   - Not event_player_2 (primary assist)
   - Not event_player_3 (secondary assist)

2. **Optional team filter**
   - Why: Player might have been traded
   - Why: Allows filtering to "goals with this team only"

3. **Uses `filter_goals()`** internally
   - Why: Ensures consistent filtering
   - Why: If the rule changes, only one place to update

---

## File 3: base_etl.py (Orchestrator Highlights)

📍 **File:** `/src/core/base_etl.py` (~4,400 lines)

This file is large. Here are the key sections:

### Main Function Structure (Lines ~2260-2310)

```python
def main():
    """
    Main ETL orchestration.

    Runs all phases in order.
    """
    log.section("STARTING BENCHSIGHT ETL")

    # Phase 1: Load BLB tables
    blb_tables = load_blb_tables()

    # Phase 2: Build player lookup
    player_lookup = build_player_lookup(blb_tables['fact_gameroster'])

    # Phase 3: Load tracking data
    tracking_data = load_tracking_data(player_lookup)

    # Phase 4: Create derived tables
    derived = create_derived_tables(tracking_data)

    # Phase 5: Create reference tables
    create_reference_tables()

    # Phase 5.5: Enhance event tables
    enhance_event_tables(derived)

    # Phase 5.6-5.12: More enhancements...
    # ...

    # Phase 6: Validate
    validate_data()

    log.section("ETL COMPLETE")
```

### Load BLB Tables (Lines ~956-1090)

```python
def load_blb_tables():
    """
    Load all tables from BLB_Tables.xlsx.

    This is the master data from the league.
    """
    log.section("PHASE 1: LOAD BLB_TABLES.XLSX")

    xlsx = pd.ExcelFile('data/raw/BLB_Tables.xlsx')

    tables = {}

    # Load each sheet
    for sheet_name in xlsx.sheet_names:
        df = pd.read_excel(xlsx, sheet_name)

        # Clean up CSAH-specific columns
        if sheet_name == 'dim_player':
            csah_cols = [c for c in df.columns if 'csah' in c.lower()]
            df = df.drop(columns=csah_cols)

        tables[sheet_name] = df
        save_table(df, sheet_name)  # 🔑 Write CSV immediately

    return tables
```

💡 **Why Immediate CSV Write:**
- If later phases fail, earlier outputs are preserved
- Can inspect intermediate outputs for debugging
- Enables partial reruns (though with caveats)

### Build Player Lookup (Lines ~1095-1150)

```python
def build_player_lookup(gameroster: pd.DataFrame) -> dict:
    """
    Create the player lookup dictionary.

    Maps: (game_id, team_name, jersey_number) → player_id
    """
    log.section("PHASE 2: BUILD PLAYER LOOKUP")

    lookup = {}

    for _, row in gameroster.iterrows():  # ⚠️ iterrows - could be vectorized
        game_id = row['game_id']
        team_name = row['team_name']
        jersey = row['jersey_number']
        player_id = row['player_id']

        # Primary key: (game, team, jersey)
        key = (game_id, team_name, jersey)
        lookup[key] = player_id

        # Fallback key: (game, jersey) - for ambiguous cases
        fallback_key = (game_id, jersey)
        if fallback_key not in lookup:
            lookup[fallback_key] = player_id

    log.info(f"Built lookup with {len(lookup)} entries")
    return lookup
```

💡 **Why Fallback Key:**
- Some tracking data might be missing team info
- Better to guess than to have NULL player_id
- Fallback only used if primary key doesn't match

⚠️ **Technical Debt:** Uses `iterrows()` which is slow. Should use:
```python
# Better approach:
lookup = dict(zip(
    zip(gameroster['game_id'], gameroster['team_name'], gameroster['jersey_number']),
    gameroster['player_id']
))
```

### Goal Filter in Context (Lines ~3312-3400)

```python
def enhance_events_with_flags(fact_events):
    """
    Add boolean flags to events for easier filtering.
    """
    log.section("PHASE 5.9: ENHANCE EVENTS WITH FLAGS")

    df = fact_events.copy()

    # Goal flag - uses canonical filter
    df['is_goal'] = (
        (df['event_type'] == 'Goal') &
        (df['event_detail'] == 'Goal_Scored')
    )

    # Shot on goal flag
    df['is_shot_on_goal'] = (
        (df['event_type'] == 'Shot') &
        (df['event_detail'].isin(['Shot_OnNetSaved', 'Shot_OnNet']))
    ) | df['is_goal']  # 🔑 Goals are also shots on goal

    # Corsi event flag
    df['is_corsi_event'] = is_corsi_event(df)

    # Fenwick event flag
    df['is_fenwick_event'] = is_fenwick_event(df)

    save_table(df, 'fact_events')
    return df
```

💡 **Why Pre-compute Flags:**
- Dashboard queries become simpler: `WHERE is_goal = true`
- No repeated calculation of complex filters
- Ensures consistent definition everywhere

---

## Tracing a Goal: Complete Flow

Let's follow a single goal through the entire system.

### Step 1: Tracker Records Goal

**User clicks in the tracker:**
```
Event Type: Goal
Player: Jersey #12, Blue team
Assisters: #7 (primary), #22 (secondary)
Time: Period 2, 8:45
Location: x=172, y=42
```

**Saved to Excel:**
| event_type | event_detail | team | jersey_1 | jersey_2 | jersey_3 | period | time_min | time_sec | x | y |
|------------|--------------|------|----------|----------|----------|--------|----------|----------|---|---|
| Goal | Goal_Scored | Blue | 12 | 7 | 22 | 2 | 8 | 45 | 172 | 42 |

### Step 2: ETL Phase 1 - Load BLB Tables

**Load from BLB_Tables.xlsx:**
```python
# dim_player includes:
{'player_id': 'P001', 'name': 'John Smith', 'jersey': 12, 'team': 'Blue'}
```

### Step 3: ETL Phase 2 - Build Player Lookup

```python
# Lookup dictionary includes:
{
    (19001, 'Blue', 12): 'P001',  # Jersey 12 → P001
    (19001, 'Blue', 7): 'P002',   # Jersey 7 → P002
    (19001, 'Blue', 22): 'P003',  # Jersey 22 → P003
}
```

### Step 4: ETL Phase 3 - Load Tracking Data

**fact_event_players created:**
| event_id | game_id | event_type | event_detail | team_id | event_player_1 | event_player_2 | event_player_3 | period | x_coord | y_coord |
|----------|---------|------------|--------------|---------|----------------|----------------|----------------|--------|---------|---------|
| E19001_P2_0845_001 | 19001 | Goal | Goal_Scored | T_Blue | P001 | P002 | P003 | 2 | 172 | 42 |

🔑 **Jersey numbers resolved to player IDs!**

### Step 5: ETL Phase 4 - Create fact_events

```python
# fact_events (one row per event):
fact_events = build_fact_events(fact_event_players)
```

Same row, but now with additional derived columns:
- `time_start_total_seconds`: 525 (8*60 + 45)
- `danger_level`: 'high' (based on x=172)

### Step 6: ETL Phase 5.9 - Add Flags

```python
# is_goal flag added:
df['is_goal'] = (df['event_type'] == 'Goal') & (df['event_detail'] == 'Goal_Scored')
# Result: True for this row
```

### Step 7: ETL Phase 6 - Player Stats

**In `src/builders/player_stats.py`:**
```python
# For player P001:
player_events = events_df[events_df['event_player_1'] == 'P001']
goals = filter_goals(player_events)  # Uses canonical filter!
player_stats['goals'] = len(goals)   # = 1
```

**fact_player_game_stats row:**
| player_game_key | player_id | game_id | goals | primary_assists | points | xg_for |
|-----------------|-----------|---------|-------|-----------------|--------|--------|
| PG19001P001 | P001 | 19001 | 1 | 0 | 1 | 0.32 |

### Step 8: ETL Phase 7 - Season Stats

```python
# Aggregate across games:
season_stats = game_stats.groupby(['player_id', 'season_id']).agg({
    'goals': 'sum',
    'assists': 'sum',
    'points': 'sum',
    # ...
})
```

**fact_player_season_stats includes this goal.**

### Step 9: Database Upload

```bash
./benchsight.sh db upload
# Uploads fact_player_game_stats.csv to Supabase
```

### Step 10: Dashboard Display

**Player profile page queries:**
```typescript
const { data } = await supabase
  .from('fact_player_game_stats')
  .select('goals, assists, points')
  .eq('player_id', 'P001')
  .eq('game_id', 19001);

// Returns: { goals: 1, assists: 0, points: 1 }
```

**Rendered on screen:** "Goals: 1"

---

## Key Code Patterns Summary

### Pattern 1: Single Source of Truth

```python
# BAD: Logic duplicated
goals1 = df[df['event_type'] == 'Goal']
goals2 = df[(df['event_type'] == 'Goal') & (df['event_detail'] == 'Goal_Scored')]

# GOOD: Single canonical function
from src.calculations.goals import filter_goals
goals = filter_goals(df)
```

### Pattern 2: Phase Isolation

```python
# Each phase wrapped in try/except
try:
    from src.tables.core_facts import create_all_core_facts
    create_all_core_facts()
except Exception as e:
    errors.append(f"Core facts: {e}")
    # Continue to next phase
```

### Pattern 3: Immediate CSV Output

```python
# Write CSV after each table is created
df = transform_data(input_df)
save_table(df, 'table_name')  # Write immediately
return df
```

### Pattern 4: Runtime Imports

```python
# Import modules when needed, not at file top
def run_phase_4():
    from src.tables.core_facts import create_all_core_facts
    create_all_core_facts()
```

---

## Key Takeaways

1. **`run_etl.py`** is the entry point - runs all phases
2. **`goals.py`** defines THE canonical goal filter
3. **`base_etl.py`** orchestrates data loading and transformation
4. **Player lookup** resolves jersey → player_id
5. **Flags** (`is_goal`, `is_corsi_event`) simplify downstream queries
6. **Data flows:** Tracker → ETL → CSV → Database → Dashboard

---

**Next:** [06-etl-patterns.md](06-etl-patterns.md) - Good patterns and technical debt
