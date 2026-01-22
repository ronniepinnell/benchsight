# 03 - ETL Overview: Why It Exists

**Learning Objectives:**
- Understand what problem the ETL pipeline solves
- Know why specific design decisions were made
- Understand the tradeoffs in the current architecture

---

## What is ETL?

**ETL** stands for **Extract, Transform, Load**:

| Phase | What It Means | BenchSight Example |
|-------|---------------|-------------------|
| **Extract** | Get data from sources | Read Excel files, BLB_Tables.xlsx |
| **Transform** | Clean, calculate, reshape | Calculate xG, aggregate stats |
| **Load** | Put data somewhere useful | Write CSV files, upload to Supabase |

---

## The Problem ETL Solves

### Without ETL

Imagine querying raw tracking data directly:

```sql
-- "How many goals did player #12 score?"
SELECT COUNT(*)
FROM tracking_events
WHERE jersey_number = 12
  AND team_name = 'Blue'
  AND event_type = 'Goal'
  AND event_detail = 'Goal_Scored'  -- Easy to forget!
  AND game_id = 19001;

-- But wait, which player IS jersey #12 on Blue in game 19001?
-- We need to join to the roster...
-- And what about games where they wore a different number?
-- And how do we handle the player who switched teams mid-season?
```

**Problems with raw data:**
1. **Identity:** Players are tracked by jersey number, not ID
2. **Consistency:** Same stat might be calculated differently in different places
3. **Performance:** Complex calculations repeated on every query
4. **Validation:** No guarantee data matches official records
5. **Complexity:** Every dashboard query becomes a complex join

### With ETL

```sql
-- Same question, but after ETL:
SELECT goals
FROM fact_player_game_stats
WHERE player_id = 'P001' AND game_id = 19001;
-- Returns: 1

-- Or get career stats:
SELECT goals, assists, points
FROM fact_player_career_stats
WHERE player_id = 'P001';
```

**ETL provides:**
1. **Resolved identities:** Jersey #12 → player_id='P001'
2. **Pre-calculated stats:** Goals, assists, xG, WAR already computed
3. **Validated data:** Goal counts match official records
4. **Consistent logic:** One place defines how goals are counted
5. **Simple queries:** Dashboard just reads pre-computed values

---

## Why These Design Decisions?

### Decision 1: CSV as Intermediate Format

🔑 **Why CSV instead of direct database writes?**

```
Tracking Files → ETL → CSV Files → Upload → Database
                       ↑
                 Why this step?
```

**Reasons:**

1. **Debuggable:** You can open CSV in Excel and verify data
2. **Recoverable:** If upload fails, CSVs are still there
3. **Version-able:** Can compare CSV outputs between ETL runs
4. **Portable:** Works without database connection
5. **Fast iteration:** Change ETL, re-run, check CSVs without touching DB

✅ **Good Pattern:** Human-readable intermediate format for debugging

### Decision 2: 11 Phases (Not One Big Script)

🔑 **Why phases instead of one giant function?**

```
Phase 1 → Phase 2 → Phase 3 → ... → Phase 11
```

**Reasons:**

1. **Dependency management:** Phase 4 needs Phase 3 outputs
2. **Isolation:** Bug in Phase 6 doesn't affect Phase 1-5
3. **Restartability:** Can re-run from Phase 6 if earlier phases are good
4. **Parallelization (future):** Some phases could run concurrently
5. **Testing:** Can test each phase independently

⚠️ **Technical Debt:** Currently all phases run sequentially even when they could parallelize.

### Decision 3: Modular ETL Architecture ✅ REFACTORED

🔑 **Current structure (refactored from monolithic 4,400 lines):**

- `base_etl.py` (~1,065 lines) - Core orchestrator
- `etl_phases/` (~4,700 lines) - Modular phase implementations

**Module breakdown:**
| Module | Purpose |
|--------|---------|
| `utilities.py` | Common utility functions |
| `derived_columns.py` | Calculate derived columns |
| `validation.py` | ETL validation |
| `event_enhancers.py` | Event table enhancement |
| `shift_enhancers.py` | Shift table enhancement |
| `derived_event_tables.py` | Derived event tables |
| `reference_tables.py` | Reference/dimension tables |

**Benefits:**
| Pros | Cons |
|------|------|
| Easier to navigate | Requires understanding module structure |
| Faster editor performance | More files to maintain |
| No import complexity | Hard to test parts |
| Clear execution order | Can't parallelize development |

⚠️ **Technical Debt:** Should be split into separate files per phase.

**Future structure (proposed):**
```
src/core/
├── base_etl.py          # Orchestrator only (~200 lines)
├── phase1_blb.py        # BLB loading
├── phase2_lookup.py     # Player lookup
├── phase3_tracking.py   # Tracking data
├── phase4_derived.py    # Derived tables
├── phase5_reference.py  # Reference tables
├── phase6_stats.py      # Player/team stats
├── phase7_macro.py      # Season/career aggregations
└── phase8_analytics.py  # Advanced analytics
```

### Decision 4: 139 Tables

🔑 **Why so many tables?**

| Category | Count | Why |
|----------|-------|-----|
| Dimension tables | ~50 | Lookup/reference data (players, teams, zones) |
| Fact tables | ~81 | Different grains and use cases |
| QA tables | ~8 | Validation and debugging |

**Different grains require different tables:**

```
fact_events           - One row per event
fact_player_game_stats - One row per player per game
fact_player_season_stats - One row per player per season
fact_player_career_stats - One row per player (career)
```

**Dashboard needs require different aggregations:**

```
fact_h2h              - Head-to-head matchups
fact_wowy             - With/without you analysis
fact_line_combos      - Forward line combinations
```

✅ **Good Pattern:** Pre-aggregate for dashboard performance

### Decision 5: Single Source of Truth for Calculations

🔑 **Why centralize calculation logic?**

**Problem it solves:**
```python
# BAD: Goals calculated differently in different places
# File A:
goals = df[df['event_type'] == 'Goal'].count()  # Wrong!

# File B:
goals = df[(df['event_type'] == 'Goal') &
           (df['event_detail'] == 'Goal_Scored')].count()  # Correct

# File C:
goals = df[df['event_detail'] == 'Shot_Goal'].count()  # Also wrong!
```

**Solution:**
```python
# GOOD: One canonical implementation
# src/calculations/goals.py
def count_goals(df: pd.DataFrame) -> int:
    """
    CRITICAL: Goals are ONLY counted when:
    - event_type = 'Goal'
    - event_detail = 'Goal_Scored'

    NEVER count event_type='Shot' with event_detail='Goal' - that's a shot attempt.
    """
    return len(df[(df['event_type'] == 'Goal') &
                  (df['event_detail'] == 'Goal_Scored')])
```

Then everywhere else:
```python
from src.calculations.goals import count_goals
goals = count_goals(events_df)
```

✅ **Good Pattern:** Single source of truth for critical business logic

### Decision 6: Validation Obsession

🔑 **Why validate so aggressively?**

**The core requirement:**
> Calculated goal counts MUST match official league records.

If our analytics show different goals than the official scoreboard, users lose trust in all our numbers.

**Validation approach:**
```python
# In QA phase:
official_goals = dim_schedule['home_score'] + dim_schedule['away_score']
calculated_goals = fact_events.query("event_type=='Goal' and event_detail=='Goal_Scored'").count()

if official_goals != calculated_goals:
    raise DataValidationError(f"Goal count mismatch: {official_goals} vs {calculated_goals}")
```

**QA tables created:**
- `qa_goal_accuracy` - Goal count verification
- `qa_data_completeness` - Missing data check
- `qa_scorer_comparison` - Cross-verify calculations
- `qa_suspicious_stats` - Flag anomalies

✅ **Good Pattern:** Validate critical data against trusted sources

---

## What Makes Hockey ETL Different

### Challenge 1: Player Identity

Players are identified by jersey number in tracking, but:
- Same number used by different players on different teams
- Players change numbers mid-season
- Players traded between teams

**Solution:** Build a lookup table per game:
```python
# (game_id, team_name, jersey_number) → player_id
lookup = {
    (19001, 'Blue', 12): 'P001',
    (19001, 'Blue', 7): 'P002',
    (19002, 'Red', 12): 'P003',  # Different player!
}
```

### Challenge 2: Shift/Event Correlation

Events happen at specific times. Shifts define who's on ice. To calculate "on-ice stats" (Corsi for/against), we need to know who was on ice when each event happened.

**Solution:** Join events to shifts by time range:
```python
# For each event, find shifts where:
# shift_start <= event_time <= shift_end
events_with_shifts = events.merge(
    shifts,
    on=['game_id', 'period'],
    how='left'
).query('shift_start <= event_time <= shift_end')
```

### Challenge 3: Complex Calculations

Hockey analytics involves sophisticated metrics:

| Metric | Complexity |
|--------|------------|
| Goals | Simple count (but tricky filter!) |
| Corsi | Shot attempts for/against while on ice |
| xG | Probability model based on shot location |
| WAR | Multi-component weighted formula |

Each requires different input data and calculation logic.

### Challenge 4: Time Representation

Tracking uses two different time formats:
- **Event time:** Counts UP from period start (0 → 1200 seconds)
- **Shift time:** Counts DOWN from period start (1200 → 0 seconds)

**Solution:** Normalize all times:
```python
# Convert shift time to event time format
normalized_time = period_length - shift_time
```

---

## Performance Characteristics

### Current Performance

| Metric | Value |
|--------|-------|
| Full ETL (4 games) | ~80 seconds |
| Tables generated | 139 |
| Total rows | ~50,000 |
| Output CSV size | ~15 MB |

### Bottlenecks

1. **`iterrows()` usage** - Slow row-by-row iteration
2. **Sequential phases** - No parallelization
3. **Repeated calculations** - Some stats computed multiple times
4. **No caching** - Re-calculates everything on every run

⚠️ **Technical Debt:** Should use vectorized pandas operations instead of iterrows()

**Bad:**
```python
for idx, row in df.iterrows():  # SLOW!
    df.at[idx, 'new_col'] = calculate(row)
```

**Good:**
```python
df['new_col'] = df.apply(calculate, axis=1)  # Better
# Or even better - vectorized:
df['new_col'] = df['col1'] * df['col2']  # FAST!
```

---

## Key Takeaways

1. **ETL transforms messy tracking data into clean analytics tables**
2. **CSV intermediate format enables debugging and recovery**
3. **11 phases manage dependencies and enable isolation**
4. **139 tables serve different use cases and grains**
5. **Single source of truth prevents calculation inconsistencies**
6. **Validation ensures data matches official records**

### What's Good (Learn From)
- Single source of truth for calculations
- CSV as debuggable intermediate
- Phase-based execution
- QA validation

### What's Technical Debt (Understand But Improve)
- ✅ ~~Monolithic 4,400-line base_etl.py~~ (refactored to ~1,065 + modules)
- `iterrows()` usage (should vectorize)
- Sequential execution (could parallelize)
- No caching between runs

---

**Next:** [04-etl-architecture.md](04-etl-architecture.md) - Module organization and the 11 phases
