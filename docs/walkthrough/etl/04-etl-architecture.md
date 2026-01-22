# 04 - ETL Architecture: Modules and Phases

**Learning Objectives:**
- Understand the ETL module organization
- Know what each of the 11+ phases does
- Understand the builder pattern used throughout
- Navigate the src/ directory effectively

---

## Module Organization

The ETL code is organized into purpose-specific modules:

```
src/
├── core/                   # 🎯 ORCHESTRATION (runs the show)
│   ├── base_etl.py         # Main orchestrator (4,400 lines)
│   ├── key_utils.py        # Key generation (PG001, etc.)
│   ├── table_writer.py     # CSV output writing
│   └── safe_csv.py         # Safe CSV reading
│
├── builders/               # 🔨 TABLE BUILDERS (pure functions)
│   ├── events.py           # Creates fact_events
│   ├── shifts.py           # Creates fact_shifts
│   ├── player_stats.py     # Creates fact_player_game_stats
│   ├── goalie_stats.py     # Creates fact_goalie_game_stats
│   └── team_stats.py       # Creates fact_team_game_stats
│
├── calculations/           # 🧮 BUSINESS LOGIC (reusable)
│   ├── goals.py            # Goal counting
│   ├── corsi.py            # Corsi/Fenwick
│   ├── xg.py               # Expected goals
│   ├── war.py              # WAR/GAR
│   └── time.py             # Time calculations
│
├── tables/                 # 📊 TABLE DEFINITIONS
│   ├── dimension_tables.py # 23 static dims
│   ├── core_facts.py       # Core stat calculations
│   ├── macro_stats.py      # Season/career aggregations
│   ├── event_analytics.py  # Event-derived tables
│   ├── shift_analytics.py  # Shift-derived tables
│   └── remaining_facts.py  # All other facts
│
├── formulas/               # 📝 JSON-DRIVEN CALCULATIONS
│   └── formula_engine.py   # Reads config/formulas.json
│
├── qa/                     # ✅ QUALITY ASSURANCE
│   └── build_qa_facts.py   # Validation tables
│
├── xy/                     # 📍 SPATIAL ANALYTICS
│   ├── xy_tables.py        # XY coordinate tables
│   └── xy_table_builder.py # XY extraction
│
├── advanced/               # 🚀 ADVANCED FEATURES
│   ├── extended_tables.py  # Additional tables
│   └── v11_enhancements.py # Version-specific additions
│
└── utils/                  # 🔧 HELPERS
    ├── key_parsers.py      # Parse composite keys
    └── helpers.py          # General utilities
```

### Module Responsibilities

| Module | Responsibility | Dependencies |
|--------|----------------|--------------|
| **core/** | Orchestrate ETL, manage phases | Everything else |
| **builders/** | Create specific tables | calculations/, core/ |
| **calculations/** | Pure business logic | None (standalone) |
| **tables/** | Table-specific creation | builders/, calculations/ |
| **formulas/** | JSON-driven calculations | config/formulas.json |
| **qa/** | Data validation | All fact tables |
| **xy/** | Coordinate handling | core/ |

---

## The 11+ Phases

The ETL runs in sequential phases, each building on previous outputs.

### Phase Execution Order

📍 **File:** `src/core/base_etl.py` → `run_etl()` function (line ~2260)

```python
def run_etl():
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

    # Phase 5.5-5.12: Enhance tables
    enhance_event_tables(derived)
    # ... more enhancement phases

    # Phase 6: Validate
    validate_data()
```

### Phase Details

#### Phase 1: Load BLB Tables
📍 **Line:** 956 | **Function:** `load_blb_tables()`

**Purpose:** Load league master data from Excel

**Input:** `data/raw/BLB_Tables.xlsx`

**Output Tables:**
| Table | Purpose |
|-------|---------|
| dim_player | Player master list |
| dim_team | Team definitions |
| dim_schedule | Game schedule |
| dim_season | Season definitions |
| dim_league | League info |
| fact_gameroster | Player-game assignments |
| fact_leadership | Team captains |
| fact_registration | Season registrations |
| fact_draft | Draft history |

**Key Logic:**
```python
# Load Excel
xlsx = pd.ExcelFile('data/raw/BLB_Tables.xlsx')

# Load each sheet
dim_player = pd.read_excel(xlsx, 'dim_player')
dim_team = pd.read_excel(xlsx, 'dim_team')

# Clean up CSAH-specific columns (not needed for NORAD)
csah_cols = [c for c in dim_player.columns if 'csah' in c.lower()]
dim_player = dim_player.drop(columns=csah_cols)
```

---

#### Phase 2: Build Player Lookup
📍 **Line:** 1095 | **Function:** `build_player_lookup()`

**Purpose:** Create mapping from jersey numbers to player IDs

**Input:** fact_gameroster

**Output:** In-memory dictionary (not a table)

**Why It Exists:**
Tracking files use jersey numbers, but we need player IDs for analysis.

**Key Logic:**
```python
def build_player_lookup(gameroster: pd.DataFrame) -> dict:
    """
    Build lookup: (game_id, team_name, jersey_number) → player_id
    """
    lookup = {}
    for _, row in gameroster.iterrows():
        key = (row['game_id'], row['team_name'], row['jersey_number'])
        lookup[key] = row['player_id']
    return lookup
```

**Edge Cases:**
- Players who change numbers: Different keys, same player_id
- Players on multiple teams: Different team_name in key
- Missing jerseys: Fallback lookups tried

---

#### Phase 3: Load Tracking Data
📍 **Line:** 1155 | **Function:** (inline)

**Purpose:** Load raw event and shift data from game tracking files

**Input:** `data/raw/games/{game_id}/` Excel files

**Output Tables:**
| Table | Purpose |
|-------|---------|
| fact_event_players | One row per player per event |
| fact_shifts (raw) | Raw shift data |

**File Structure:**
```
data/raw/games/
├── 19001/
│   └── 19001_tracking.xlsx  (Events sheet, Shifts sheet)
├── 19002/
│   └── 19002_tracking.xlsx
└── ...
```

**Key Logic:**
```python
for game_id in discovered_games:
    # Load tracking file
    tracking = pd.ExcelFile(f'data/raw/games/{game_id}/{game_id}_tracking.xlsx')

    # Load events
    events = pd.read_excel(tracking, 'Events')

    # Resolve player identities using Phase 2 lookup
    events['player_id'] = events.apply(
        lambda r: player_lookup.get((game_id, r['team'], r['jersey']), None),
        axis=1
    )

    # Load shifts
    shifts = pd.read_excel(tracking, 'Shifts')
```

---

#### Phase 4: Create Derived Tables
📍 **Line:** 1455 | **Function:** `create_derived_tables()`

**Purpose:** Create core fact tables from tracking data

**Input:** fact_event_players, fact_shifts (raw)

**Output Tables:**
| Table | Builder | Purpose |
|-------|---------|---------|
| fact_events | `builders/events.py` | One row per event |
| fact_shifts | `builders/shifts.py` | Deduplicated shifts |
| fact_shift_players | inline | One row per player per shift |
| fact_tracking | inline | Unique tracking points |

**Key Logic:**
```python
# Collapse fact_event_players to one row per event
fact_events = build_fact_events(fact_event_players)

# Deduplicate shifts
fact_shifts = build_fact_shifts(raw_shifts)

# Expand shifts to player level
fact_shift_players = expand_shifts_to_players(fact_shifts)
```

---

#### Phase 5: Create Reference Tables
📍 **Line:** 1579 | **Function:** `create_reference_tables()`

**Purpose:** Create 23 static dimension tables

**Input:** None (hardcoded values)

**Output:** 23 dimension tables (see `src/tables/dimension_tables.py`)

**Examples:**
```python
# dim_period - Periods in a hockey game
dim_period = pd.DataFrame({
    'period_id': [1, 2, 3, 4, 5],
    'period_name': ['1st', '2nd', '3rd', 'OT', 'SO']
})

# dim_strength - Game situations
dim_strength = pd.DataFrame({
    'strength_id': ['EV', 'PP', 'PK', 'EN', '4v4', '3v3'],
    'strength_name': ['Even Strength', 'Power Play', 'Penalty Kill', ...]
})
```

**Dynamic dims (from tracking data):**
- dim_zone_entry_type
- dim_zone_exit_type
- dim_stoppage_type

---

#### Phases 5.5-5.12: Enhancement Phases

These phases add foreign keys, calculated columns, and flags to existing tables.

| Phase | Line | Function | Purpose |
|-------|------|----------|---------|
| 5.5 | 2337 | `enhance_event_tables()` | Add FKs to fact_events |
| 5.6 | 2995 | `enhance_derived_event_tables()` | Enhance fact_tracking |
| 5.7 | 3063 | `create_fact_sequences()` | Create event sequences |
| 5.8 | 3195 | `create_fact_plays()` | Create play groupings |
| 5.9 | 3310 | `enhance_events_with_flags()` | Add is_goal, is_corsi flags |
| 5.10 | 3973 | `create_derived_event_tables()` | Scoring chances, shot danger |
| 5.11 | 4493 | `enhance_shift_tables()` | Add FKs to shifts |
| 5.11B | 5105 | `enhance_shift_players()` | Add player details to shift_players |
| 5.12 | 5535 | (inline) | Update roster positions |

**Example - Phase 5.5: Add Foreign Keys**
```python
def enhance_event_tables(fact_events):
    # Add shift_id FK (which shift was this event during?)
    fact_events = fact_events.merge(
        fact_shifts[['shift_id', 'game_id', 'period', 'shift_start', 'shift_end']],
        on=['game_id', 'period'],
        how='left'
    )
    # Keep only rows where event_time is within shift_time range
    mask = (fact_events['event_time'] >= fact_events['shift_start']) & \
           (fact_events['event_time'] <= fact_events['shift_end'])
    fact_events = fact_events[mask]

    # Add dimension FKs
    fact_events = fact_events.merge(dim_event_type, on='event_type', how='left')
    fact_events = fact_events.merge(dim_period, on='period', how='left')

    return fact_events
```

---

#### Phase 6: Player/Team Stats
📍 **Location:** `src/tables/core_facts.py`, `src/builders/player_stats.py`

**Purpose:** Calculate comprehensive per-game statistics

**Input:** All previous tables

**Output Tables:**
| Table | Columns | Purpose |
|-------|---------|---------|
| fact_player_game_stats | 317 | All player stats per game |
| fact_goalie_game_stats | ~50 | Goalie stats per game |
| fact_team_game_stats | ~100 | Team totals per game |

**This is where the magic happens!** All the calculations (goals, assists, xG, Corsi, WAR) are computed here.

---

#### Phase 7: Macro Stats
📍 **Location:** `src/tables/macro_stats.py`

**Purpose:** Aggregate game stats to season and career level

**Input:** fact_player_game_stats, fact_goalie_game_stats

**Output Tables:**
| Table | Grain |
|-------|-------|
| fact_player_season_stats_basic | (player_id, season_id) |
| fact_player_career_stats_basic | (player_id) |
| fact_player_season_stats | (player_id, season_id) - advanced |
| fact_player_career_stats | (player_id) - advanced |
| fact_goalie_* variants | Same patterns |
| fact_team_* variants | Same patterns |

---

#### Phases 8-10: Analytics Tables
📍 **Location:** `src/tables/event_analytics.py`, `src/tables/shift_analytics.py`, `src/tables/remaining_facts.py`

**Purpose:** Create specialized analytics tables

**Examples:**
| Table | Purpose |
|-------|---------|
| fact_h2h | Head-to-head matchups |
| fact_wowy | With/without you analysis |
| fact_line_combos | Forward line combinations |
| fact_scoring_chances | High-danger events |
| fact_shift_quality | Shift quality scoring |

---

#### Phase 11: QA Tables
📍 **Location:** `src/qa/build_qa_facts.py`

**Purpose:** Validate data quality

**Output Tables:**
| Table | Purpose |
|-------|---------|
| qa_goal_accuracy | Verify goal counts match official |
| qa_data_completeness | Check for missing data |
| qa_scorer_comparison | Cross-verify calculations |
| qa_suspicious_stats | Flag anomalies |

---

## The Builder Pattern

🔑 **Builders are pure functions that take inputs and return outputs**

### Pattern

```python
def build_fact_something(
    input_df: pd.DataFrame,
    other_input: pd.DataFrame
) -> pd.DataFrame:
    """
    Create fact_something table.

    Args:
        input_df: Source data
        other_input: Additional data needed

    Returns:
        DataFrame ready to write to CSV
    """
    # Transform
    result = input_df.copy()
    result = _apply_transformations(result)
    result = _calculate_derived_columns(result)

    return result
```

### Why This Pattern?

1. **Testable:** Can test with mock data
2. **Predictable:** Same input → same output
3. **Composable:** Can chain builders
4. **No side effects:** Doesn't modify input or global state

### Example: events.py

📍 **File:** `src/builders/events.py`

```python
def build_fact_events(fact_event_players: pd.DataFrame) -> pd.DataFrame:
    """
    Collapse fact_event_players to one row per event.

    The input has one row per player per event (event_player_1, event_player_2, etc.)
    The output has one row per event.

    Priority: Goal > Shot > Pass (when same event has multiple types)
    """
    df = fact_event_players.copy()

    # Add priority for deduplication
    priority_map = {'Goal': 0, 'Shot': 1, 'Pass': 2}
    df['_priority'] = df['event_type'].map(priority_map).fillna(99)

    # Take the highest priority row per event
    df = df.sort_values('_priority')
    fact_events = df.groupby('event_id').first().reset_index()

    # Drop temporary column
    fact_events = fact_events.drop(columns=['_priority'])

    return fact_events
```

---

## The Formula System

🔑 **Some calculations are defined in JSON, not Python**

📍 **File:** `config/formulas.json`

### Why JSON?

1. **Change without code:** Update weights without Python changes
2. **Transparency:** Non-developers can review formulas
3. **Version control:** Easy to track formula changes
4. **Documentation:** Self-documenting

### Example

```json
{
  "xg_base_rates": {
    "high_danger": 0.25,
    "medium_danger": 0.08,
    "low_danger": 0.03,
    "default": 0.06
  },
  "xg_modifiers": {
    "rush": 1.3,
    "rebound": 1.5,
    "one_timer": 1.4,
    "breakaway": 2.5
  },
  "war_weights": {
    "goals": 1.0,
    "primary_assists": 0.7,
    "secondary_assists": 0.4,
    "shots": 0.015,
    "xg": 0.8
  },
  "goals_per_win": 4.5
}
```

### Usage in Code

```python
# src/formulas/formula_engine.py
import json

class FormulaEngine:
    def __init__(self):
        with open('config/formulas.json') as f:
            self.formulas = json.load(f)

    def get_xg_base_rate(self, danger_level: str) -> float:
        return self.formulas['xg_base_rates'].get(danger_level, 0.06)

    def get_war_weight(self, component: str) -> float:
        return self.formulas['war_weights'].get(component, 0.0)
```

---

## Phase Dependency Graph

```
Phase 1 (BLB Tables)
    │
    ├──► dim_player, dim_team, dim_schedule, ...
    │
    └──► fact_gameroster ──► Phase 2 (Player Lookup)
                                  │
                                  ▼
                            player_lookup dict
                                  │
                                  ▼
                            Phase 3 (Tracking)
                                  │
                            ├──► fact_event_players
                            │
                            └──► fact_shifts (raw)
                                  │
                                  ▼
                            Phase 4 (Derived)
                                  │
                            ├──► fact_events
                            ├──► fact_shifts
                            └──► fact_shift_players
                                  │
                                  ▼
                            Phase 5 (Reference)
                                  │
                            └──► 23 dim_* tables
                                  │
                                  ▼
                            Phases 5.5-5.12 (Enhancement)
                                  │
                            ├──► Enhanced fact_events
                            ├──► fact_sequences
                            ├──► fact_plays
                            └──► Enhanced fact_shifts
                                  │
                                  ▼
                            Phase 6 (Stats)
                                  │
                            ├──► fact_player_game_stats
                            ├──► fact_goalie_game_stats
                            └──► fact_team_game_stats
                                  │
                                  ▼
                            Phase 7 (Macro)
                                  │
                            └──► *_season_stats, *_career_stats
                                  │
                                  ▼
                            Phases 8-10 (Analytics)
                                  │
                            └──► fact_h2h, fact_wowy, ...
                                  │
                                  ▼
                            Phase 11 (QA)
                                  │
                            └──► qa_* tables
```

---

## Key Takeaways

1. **Modules are organized by purpose:** core, builders, calculations, tables
2. **11+ phases run sequentially:** Each builds on previous outputs
3. **Builders are pure functions:** Input → Output, no side effects
4. **Formulas can live in JSON:** Change weights without code changes
5. **Phase dependencies are strict:** Can't skip phases

### Where to Look

| Need to... | Go to... |
|------------|----------|
| Understand overall flow | `src/core/base_etl.py` |
| Change how events are created | `src/builders/events.py` |
| Change how stats are calculated | `src/builders/player_stats.py` |
| Change a specific formula | `src/calculations/*.py` or `config/formulas.json` |
| Add a new dimension table | `src/tables/dimension_tables.py` |
| Add a new fact table | `src/tables/remaining_facts.py` |

---

**Next:** [05-etl-code-walkthrough.md](05-etl-code-walkthrough.md) - Annotated code deep dive
