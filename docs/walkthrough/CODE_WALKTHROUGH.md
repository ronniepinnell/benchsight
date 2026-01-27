# Code Walkthrough Guide

**Step-by-step code walkthrough for key BenchSight ETL workflows.**

Last Updated: 2026-01-22

---

## Overview

This guide walks through key code paths in the BenchSight ETL pipeline, explaining how data flows and transformations occur.

---

## Walkthrough 1: Goal Counting

**Critical Rule:** Goals are ONLY counted when `event_type == 'Goal' AND event_detail == 'Goal_Scored'`

### Step-by-Step

1. **Load Events** (`src/core/base_etl.py`)
   ```python
   # Events loaded from tracking file
   events_df = pd.read_excel(tracking_file, sheet_name='Events')
   ```

2. **Filter Goals** (`src/calculations/goals.py`)
   ```python
   GOAL_FILTER = (df['event_type'] == 'Goal') & (df['event_detail'] == 'Goal_Scored')
   goals_df = events_df[GOAL_FILTER]
   ```

3. **Count per Player** (`src/tables/core_facts.py`)
   ```python
   player_goals = goals_df.groupby(['player_id', 'game_id']).size()
   ```

4. **Store in Stats** (`fact_player_game_stats`)
   ```python
   stats_df['goals'] = player_goals
   ```

### Key Files
- `src/core/base_etl.py` - Event loading
- `src/calculations/goals.py` - Goal filtering logic
- `src/tables/core_facts.py` - Stats aggregation

---

## Walkthrough 2: Table Generation

### Step-by-Step

1. **Entry Point** (`run_etl.py`)
   ```python
   python run_etl.py
   ```

2. **Phase Execution** (`run_etl.py::run_full_etl()`)
   ```python
   # Phase 1
   from src.core.base_etl import main as run_base_etl
   run_base_etl()
   
   # Phase 3B
   from src.tables.dimension_tables import create_all_dimension_tables
   create_all_dimension_tables()
   
   # Phase 4
   from src.tables.core_facts import create_all_core_facts
   create_all_core_facts()
   ```

3. **Table Writing** (`src/core/table_writer.py`)
   ```python
   save_output_table(df, 'fact_events', OUTPUT_DIR)
   ```

4. **Output** (`data/output/fact_events.csv`)

### Key Files
- `run_etl.py` - Main orchestrator
- `src/core/base_etl.py` - Phase 1 execution
- `src/core/table_writer.py` - Table writing

---

## Walkthrough 3: Calculation Flow

### Step-by-Step

1. **Load Source Data**
   ```python
   events_df = pd.read_csv('data/output/fact_events.csv')
   ```

2. **Apply Calculations** (`src/calculations/`)
   ```python
   from src.calculations.goals import count_goals
   goals = count_goals(events_df)
   ```

3. **Aggregate** (`src/tables/core_facts.py`)
   ```python
   stats = events_df.groupby('player_id').agg({
       'goals': 'sum',
       'assists': 'sum',
       ...
   })
   ```

4. **Save Results**
   ```python
   save_output_table(stats, 'fact_player_game_stats', OUTPUT_DIR)
   ```

---

## Walkthrough 4: Debugging

### Step-by-Step

1. **Start Debug Mode**
   ```bash
   ./benchsight.sh debug start
   python run_etl.py --debug
   ```

2. **Phase Execution** (`src/core/debug/phase_executor.py`)
   ```python
   phase_executor.execute_phase(
       phase_id="1",
       phase_name="BASE ETL",
       target_schema="raw",
       phase_function=run_base_etl
   )
   ```

3. **State Tracking** (`src/core/debug/state_manager.py`)
   ```python
   state_manager.start_phase("1", "BASE ETL", "raw")
   state_manager.complete_phase("1", tables_created=4)
   ```

4. **PostgreSQL Storage** (`src/core/debug/postgres_manager.py`)
   ```python
   postgres_manager.copy_from_csv("raw", "fact_events", csv_path)
   ```

5. **Inspection**
   ```bash
   ./benchsight.sh debug shell
   SELECT * FROM raw.fact_events LIMIT 10;
   ```

---

## Related Documentation

- [ETL Phase Flow](ETL_PHASE_FLOW.md) - Phase overview
- [Core Modules](CORE_MODULES.md) - Module documentation
