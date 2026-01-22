# 01 - Mental Models for Reading Large Codebases

**Learning Objectives:**
- Understand how to approach a large codebase systematically
- Learn "data flow thinking" - following data instead of functions
- Recognize the layers pattern in software architecture
- Build intuition for navigating unfamiliar code

---

## The "Why Before What" Principle

🔑 **The most important skill when reading code is asking "why does this exist?"**

When you encounter a function, file, or module, don't start by reading line-by-line. Instead, ask:

1. **What problem does this solve?**
2. **Why is it a separate file/function?**
3. **What would break if this didn't exist?**

### Example: Why does `goals.py` exist?

📍 **File:** `src/calculations/goals.py` (~135 lines)

**Bad approach:** "Let me read every line and understand the implementation..."

**Good approach:** "Why does this file exist as a separate module?"

**Answer:** Goal counting is a **critical business rule** that:
- Must match official league records exactly
- Is used in 20+ places throughout the codebase
- Has a subtle but important filter: `event_type='Goal' AND event_detail='Goal_Scored'`

By isolating it in one file, we create a **single source of truth**. Every part of the system uses `goals.py` for goal counting, so if the rule changes, we only fix it once.

✅ **Good Pattern:** Single source of truth for critical business logic

---

## Data Flow Thinking

🔑 **Follow the data, not the functions**

Large codebases have hundreds of functions calling each other. Trying to trace function calls leads to confusion. Instead, trace the **data**.

### The Pipe Analogy

Think of data transformation like water flowing through pipes:

```
Raw Data → [Transform 1] → Intermediate → [Transform 2] → Intermediate → [Transform 3] → Output
```

Each transform:
- Takes input data
- Applies some logic
- Produces output data

**Your job:** Understand what data goes in and what comes out at each step.

### BenchSight Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           DATA FLOW                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  BLB_Tables.xlsx ──┐                                                     │
│  (league master)   │                                                     │
│                    ├──► Phase 1-2 ──► Player Lookup Dictionary           │
│  Tracking Files ───┘                                                     │
│  (game events)         ↓                                                 │
│                                                                          │
│                   Phase 3 ──► fact_event_players (raw, expanded)         │
│                               fact_shifts (raw)                          │
│                        ↓                                                 │
│                                                                          │
│                   Phase 4 ──► fact_events (one row per event)            │
│                               fact_shifts (deduplicated)                 │
│                        ↓                                                 │
│                                                                          │
│                   Phase 5 ──► dim_* tables (23 reference tables)         │
│                        ↓                                                 │
│                                                                          │
│               Phase 5.5-5.12 ──► Enhanced tables (FKs, flags added)      │
│                        ↓                                                 │
│                                                                          │
│                   Phase 6 ──► fact_player_game_stats (317 columns!)      │
│                               fact_goalie_game_stats                     │
│                               fact_team_game_stats                       │
│                        ↓                                                 │
│                                                                          │
│                   Phase 7 ──► *_season_stats, *_career_stats             │
│                        ↓                                                 │
│                                                                          │
│               Phase 8-10 ──► Analytics tables (H2H, WOWY, etc.)          │
│                        ↓                                                 │
│                                                                          │
│                  Phase 11 ──► QA tables (validation)                     │
│                        ↓                                                 │
│                                                                          │
│                   data/output/*.csv (139 files)                          │
│                        ↓                                                 │
│                                                                          │
│                   Supabase (cloud database)                              │
│                        ↓                                                 │
│                                                                          │
│                   Dashboard (Next.js)                                    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Exercise: Trace a Goal

Let's trace a single goal from the tracker to the dashboard:

**1. Tracker Input (game tracking):**
```
Event: Goal
Player: Jersey #12, Blue team
Time: Period 2, 8:45
Location: x=172, y=42
```

**2. fact_event_players (Phase 3):**
```python
{
    'event_id': 'E19001_P2_0845_001',
    'game_id': 19001,
    'event_type': 'Goal',
    'event_detail': 'Goal_Scored',
    'event_player_1': 'P001',  # Resolved from jersey lookup
    'event_player_2': 'P002',  # Primary assist
    'period': 2,
    'x_coord': 172,
    'y_coord': 42
}
```

**3. fact_events (Phase 4):**
Same data, but one row per event (not per player)

**4. fact_player_game_stats (Phase 6):**
```python
# For player P001:
{
    'player_id': 'P001',
    'game_id': 19001,
    'goals': 1,  # Incremented from this goal
    'xg_for': 0.32,  # xG for this shot location
    'goals_above_xg': 0.68,  # 1 - 0.32
    ...
}
```

**5. Supabase:**
Same data in PostgreSQL cloud database

**6. Dashboard:**
```typescript
// Player profile page shows:
// Goals: 1
// xG: 0.32
// Goals Above Expected: +0.68
```

💡 **Insight:** By tracing data, you understand the system without reading every function.

---

## The Layers Pattern

🔑 **Code is organized in layers, from high-level to low-level**

### Layer Types

| Layer | Purpose | Example |
|-------|---------|---------|
| **Entry Point** | Where execution starts | `run_etl.py` |
| **Orchestrator** | Coordinates the process | `base_etl.py` |
| **Builder** | Creates specific outputs | `events.py`, `player_stats.py` |
| **Calculator** | Pure business logic | `goals.py`, `xg.py` |
| **Utility** | Helper functions | `key_utils.py` |

### BenchSight Layer Map

```
┌─────────────────────────────────────────────────────────────┐
│ ENTRY POINT                                                  │
│ run_etl.py                                                   │
│ "Start the ETL process"                                      │
└─────────────────────────┬───────────────────────────────────┘
                          │ calls
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ ORCHESTRATOR                                                 │
│ src/core/base_etl.py                                         │
│ "Run Phase 1, then Phase 2, then Phase 3..."                 │
│ "Load this, transform that, save here"                       │
└─────────────────────────┬───────────────────────────────────┘
                          │ calls
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ BUILDERS                                                     │
│ src/builders/events.py      - Creates fact_events            │
│ src/builders/shifts.py      - Creates fact_shifts            │
│ src/builders/player_stats.py - Creates fact_player_game_stats│
│ src/tables/dimension_tables.py - Creates dim_* tables        │
└─────────────────────────┬───────────────────────────────────┘
                          │ calls
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ CALCULATORS                                                  │
│ src/calculations/goals.py   - Goal counting logic            │
│ src/calculations/corsi.py   - Corsi/Fenwick logic            │
│ src/calculations/xg.py      - Expected goals calculation     │
│ src/calculations/war.py     - WAR/GAR calculation            │
└─────────────────────────┬───────────────────────────────────┘
                          │ calls
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ UTILITIES                                                    │
│ src/core/key_utils.py       - Key generation (PG001, etc.)   │
│ src/utils/time_utils.py     - Time conversions               │
│ src/core/safe_csv.py        - Safe CSV reading/writing       │
└─────────────────────────────────────────────────────────────┘
```

### How to Identify Layers

When you open a file, ask:

1. **Does it start the process?** → Entry Point
2. **Does it call many other functions in sequence?** → Orchestrator
3. **Does it create a specific table/output?** → Builder
4. **Does it contain pure business logic?** → Calculator
5. **Does it help other code do its job?** → Utility

---

## Reading Code You Didn't Write

### Strategy 1: Start with Tests

Tests show you:
- What inputs the function expects
- What output it should produce
- Edge cases the author considered

📍 **Example:** `tests/test_goal_verification.py`
```python
def test_goal_count_matches_official():
    """Goals calculated from events must match official count."""
    # This test tells you:
    # 1. There's a function that counts goals
    # 2. It must match "official" counts
    # 3. The official counts come from somewhere else
```

### Strategy 2: Start with Types/Interfaces

Types tell you the "contract" - what goes in and what comes out.

📍 **Example:** `ui/dashboard/src/types/player.ts`
```typescript
interface PlayerGameStats {
    player_id: string;
    game_id: number;
    goals: number;
    assists: number;
    // ... tells you exactly what data structure to expect
}
```

### Strategy 3: Use Import Statements as a Map

Imports show you dependencies:

```python
# In player_stats.py:
from src.calculations.goals import count_goals
from src.calculations.xg import calculate_xg
from src.calculations.war import calculate_war

# This tells you:
# - player_stats.py uses goals.py, xg.py, war.py
# - Those are separate calculation modules
# - You might need to read them to understand player_stats.py
```

### Strategy 4: Zoom Out, Then Zoom In

1. **Zoom out:** Read the file's docstring and function names
2. **Identify the main function:** Usually called `main()`, `run()`, `build_*()`, or `create_*()`
3. **Read that function first:** It shows the high-level flow
4. **Zoom in:** Read helper functions as needed

📍 **Example:** `src/builders/events.py`

```python
"""
Builds fact_events from fact_event_players.
Creates one row per event (collapses player rows).
"""

def build_fact_events(fact_event_players: pd.DataFrame) -> pd.DataFrame:
    """Main function - read this first."""
    df = _validate_input(fact_event_players)
    df = _add_event_priority(df)
    df = _collapse_to_events(df)
    df = _add_derived_columns(df)
    return df

def _validate_input(df):
    """Helper - read if you need to understand validation."""
    ...

def _add_event_priority(df):
    """Helper - read if you need to understand priority logic."""
    ...
```

---

## This Codebase's Personality

Every codebase has conventions and patterns. Here are BenchSight's:

### Naming Conventions

| Convention | Example | Meaning |
|------------|---------|---------|
| `dim_*` | `dim_player` | Dimension table (lookup/reference) |
| `fact_*` | `fact_events` | Fact table (transactional data) |
| `qa_*` | `qa_goal_accuracy` | QA/validation table |
| `v_*` | `v_player_leaders` | Database view |
| `PG*` | `PG19001P001` | Player-game key |
| `TG*` | `TG19001T001` | Team-game key |
| `_*` | `_helper()` | Private/helper function |

### Code Style

| Language | Convention |
|----------|------------|
| Python | snake_case for functions/variables |
| Python | PascalCase for classes |
| TypeScript | camelCase for functions/variables |
| TypeScript | PascalCase for components/interfaces |

### Key Patterns

1. **Single Source of Truth:** Critical logic in dedicated files
   - Goals: `src/calculations/goals.py`
   - xG: `src/calculations/xg.py`

2. **Builders Return DataFrames:** Builder functions take inputs, return outputs (pure functions)
   ```python
   def build_fact_events(input_df: pd.DataFrame) -> pd.DataFrame:
       # Transform and return
       return output_df
   ```

3. **Formulas in JSON:** Some calculations defined in config
   - 📍 `config/formulas.json`

4. **Validation Obsession:** Goal counts MUST match official records
   - 📍 `tests/test_goal_verification.py`

---

## Practice Exercise

Open your editor to `/Users/ronniepinnell/Documents/Programming_HD/Hockey/Benchsight/git/benchsight/` and answer these questions:

1. **What layer is `run_etl.py`?**
   <details>
   <summary>Answer</summary>
   Entry Point - it starts the ETL process
   </details>

2. **What does `src/core/base_etl.py` do?**
   <details>
   <summary>Answer</summary>
   Orchestrator - it coordinates all ETL phases
   </details>

3. **Why is goal counting in a separate file (`goals.py`)?**
   <details>
   <summary>Answer</summary>
   Single source of truth for a critical business rule
   </details>

4. **What does the `dim_` prefix mean?**
   <details>
   <summary>Answer</summary>
   Dimension table - a lookup/reference table
   </details>

5. **If you need to change how Corsi is calculated, where would you look?**
   <details>
   <summary>Answer</summary>
   `src/calculations/corsi.py` (or similar in calculations folder)
   </details>

---

## Key Takeaways

1. **Ask "why" before reading code** - understand purpose first
2. **Follow the data** - trace transformations, not function calls
3. **Identify layers** - entry point → orchestrator → builder → calculator → utility
4. **Use tests and types as documentation** - they show contracts
5. **Learn the codebase's conventions** - naming patterns reveal purpose

---

**Next:** [02-system-map.md](02-system-map.md) - The five systems and how to navigate them
