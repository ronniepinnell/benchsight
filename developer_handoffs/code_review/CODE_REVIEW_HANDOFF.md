# BenchSight Code Review & Hardening Handoff

## Your Mission

You're a senior engineer tasked with reviewing, hardening, and production-readying the BenchSight ETL pipeline. This system processes hockey game tracking data into a 98-table data warehouse (soon to be 98 with video highlights).

### Objectives

1. **Code Review** - Identify weak points, anti-patterns, spaghetti code
2. **Test Coverage** - Add missing tests, especially integration tests
3. **Refactoring** - Clean up, DRY, improve maintainability
4. **Performance** - Optimize slow paths, reduce memory usage
5. **Robustness** - Error handling, edge cases, data validation
6. **Documentation** - Ensure code is self-documenting with proper docstrings

---

## Project Overview

### What It Does

```
Raw Tracking Files → ETL Pipeline → 96 CSV Files → Supabase (PostgreSQL)
     (Excel)         (Python)       (Star Schema)    (Production DB)
```

### Scale

| Metric | Value |
|--------|-------|
| Tables | 96 (44 dims, 51 facts, 1 QA) + 2 pending |
| Columns | 1,909 total |
| Player Stats | 317 columns per player per game |
| Games Processed | 9 currently |
| Rows | ~125,000 total |

---

## Critical Files to Review

### Priority 1: Core ETL

| File | Lines | Purpose | Concerns |
|------|-------|---------|----------|
| `src/main.py` | 800+ | CLI entry point | Monolithic, could be split |
| `src/pipeline/orchestrator.py` | 400+ | ETL coordinator | Dependency management |
| `src/ingestion/game_loader.py` | 500+ | Game file parsing | Complex Excel parsing |
| `src/ingestion/blb_loader.py` | 300+ | Master data loading | |
| `src/ingestion/xy_loader.py` | 600+ | XY coordinate processing | Memory intensive |

### Priority 2: Data Loading

| File | Lines | Purpose | Concerns |
|------|-------|---------|----------|
| `scripts/bulletproof_loader.py` | 477 | Supabase deployment | NEW - needs review |
| `scripts/flexible_loader.py` | 500+ | Legacy loader | Has bugs, being replaced |

### Priority 3: Stats Calculation

| File | Lines | Purpose | Concerns |
|------|-------|---------|----------|
| `src/analytics/` | Various | Stats calculations | Spread across files |
| `src/transformation/` | Various | Data transforms | |

### Priority 4: Validation

| File | Purpose |
|------|---------|
| `scripts/validate_stats.py` | Stats validation |
| `scripts/qa_comprehensive.py` | QA checks |
| `scripts/validate_against_ground_truth.py` | Compare to official data |

---

## Known Issues & Technical Debt

### 🔴 Critical

1. **No transaction support** - Partial loads can leave DB in inconsistent state
2. **Memory usage** - Large games load entire file into memory
3. **No retry logic** - Network failures cause complete job failure
4. **Hardcoded paths** - Some scripts assume specific directory structure

### 🟡 Important

1. **Duplicate code** - Stats calculations repeated in multiple places
2. **Inconsistent error handling** - Some functions swallow exceptions
3. **Missing type hints** - Many functions lack proper typing
4. **Test gaps** - No integration tests, limited unit tests
5. **Magic numbers** - Thresholds hardcoded without constants

### 🟢 Nice to Have

1. **Logging inconsistency** - Mix of print() and logger
2. **Config scattered** - Some config in code, some in files
3. **No caching** - Recomputes same values multiple times

---

## Architecture Review Points

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA SOURCES                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  data/raw/games/{id}/          data/BLB_Tables.xlsx                         │
│  └── BLB_GameTracking.xlsx     └── Master reference data                    │
│      ├── Events sheet              ├── Players                              │
│      ├── Shifts sheet              ├── Teams                                │
│      └── XY sheet                  └── Schedule                             │
└─────────────────────┬───────────────────────────┬───────────────────────────┘
                      │                           │
                      ▼                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ETL PIPELINE                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  src/main.py                                                                 │
│  └── PipelineOrchestrator                                                   │
│      ├── Stage Layer ──────► Raw data loading                               │
│      ├── Intermediate Layer ► Transforms, joins, enrichment                │
│      └── Datamart Layer ────► Star schema (dims + facts)                   │
│                                                                              │
│  Key Transforms:                                                             │
│  • Event attribution (event_player_1 = primary)                             │
│  • Shift calculation (TOI, logical shifts)                                  │
│  • Stats aggregation (317 columns)                                          │
│  • H2H/WOWY computation                                                      │
└─────────────────────┬───────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              OUTPUT                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  data/output/                                                                │
│  ├── dim_*.csv (44 files) ─────► Dimension tables                           │
│  ├── fact_*.csv (51 files) ────► Fact tables                                │
│  └── qa_*.csv (1 file) ────────► QA tables                                  │
└─────────────────────┬───────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SUPABASE                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  scripts/bulletproof_loader.py                                              │
│  ├── Reads CSVs                                                             │
│  ├── Validates against schema                                               │
│  ├── Batched upserts (500 rows)                                             │
│  └── Error handling & logging                                               │
│                                                                              │
│  96 PostgreSQL tables with:                                                  │
│  • Primary keys defined                                                      │
│  • Foreign key relationships                                                │
│  • Indexes on common queries                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Star Schema Design

```
                              ┌──────────────────┐
                              │   dim_player     │
                              │   (337 rows)     │
                              └────────┬─────────┘
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        │                              │                              │
        ▼                              ▼                              ▼
┌───────────────┐            ┌─────────────────────┐         ┌───────────────┐
│  dim_team     │◄───────────│ fact_player_game    │────────►│ dim_schedule  │
│  (26 rows)    │            │ _stats (317 cols)   │         │ (562 rows)    │
└───────────────┘            └─────────────────────┘         └───────────────┘
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        │                              │                              │
        ▼                              ▼                              ▼
┌───────────────┐            ┌─────────────────────┐         ┌───────────────┐
│ fact_events   │            │    fact_shifts      │         │  fact_h2h     │
│ (5,833 rows)  │            │    (672 rows)       │         │  fact_wowy    │
└───────────────┘            └─────────────────────┘         └───────────────┘
```

---

## Database Schema Review

### Primary Key Conventions

| Pattern | Example | Notes |
|---------|---------|-------|
| `{table}_key` | `player_game_key` | Composite keys as TEXT |
| `{entity}_id` | `player_id` | Single column INTEGER |
| `game_id` | `game_id` | INTEGER, FK to dim_schedule |

### Key Format

```python
# Composite keys follow this pattern:
player_game_key = f"{game_id}_{player_id}"
event_key = f"{game_id}_{event_index}"
shift_key = f"{game_id}_{player_id}_{shift_number}"
h2h_key = f"{game_id}_{player_1_id}_{player_2_id}"
```

### Foreign Key Relationships

```sql
-- Core relationships
fact_player_game_stats.player_id → dim_player.player_id
fact_player_game_stats.team_id → dim_team.team_id
fact_player_game_stats.game_id → dim_schedule.game_id

fact_events.event_player_1 → dim_player.player_id
fact_events.event_type_id → dim_event_type.event_type_id
fact_events.game_id → dim_schedule.game_id

fact_shifts.player_id → dim_player.player_id
fact_shifts.game_id → dim_schedule.game_id
```

---

## Pending Feature: Video Highlights

### New Tables to Add

```sql
-- See sql/04_VIDEO_HIGHLIGHTS.sql for full schema

-- Dimension
dim_highlight_type (9 rows)
  - highlight_type_id, highlight_type, display_name, icon, color

-- Fact  
fact_video_highlights
  - highlight_key (PK)
  - game_id, event_index, player_id, team_id (FKs)
  - video_url, start_timestamp, end_timestamp
  - highlight_type, title, description
  - is_featured, is_approved, is_public

-- Modifications to fact_events
  + is_highlight_candidate BOOLEAN
  + highlight_score INTEGER
  + has_video_highlight BOOLEAN
  + highlight_count INTEGER
```

### Integration Points

1. Add to `TABLE_DEFINITIONS` in `bulletproof_loader.py`
2. Add to `LOAD_ORDER`
3. Create empty CSV templates
4. Add FK constraints after table creation
5. Update ETL to populate `is_highlight_candidate` flag

---

## Test Coverage Analysis

### Current Tests (290 passing)

| Category | Tests | Coverage |
|----------|-------|----------|
| Stats Calculations | 250+ | Good |
| Supabase Config | 15 | Good |
| Data Integrity | 10 | Basic |
| Validation | 6 | Minimal |
| ETL Pipeline | 5 | Minimal |

### Missing Tests (Need to Add)

| Category | What's Needed |
|----------|---------------|
| **Integration** | End-to-end ETL flow |
| **Loader** | bulletproof_loader.py functions |
| **Edge Cases** | Empty files, malformed data |
| **Concurrency** | Parallel game processing |
| **Rollback** | Failed partial loads |
| **Performance** | Large file handling |

### Suggested Test Structure

```
tests/
├── unit/
│   ├── test_stats_calculations.py  ✓ Exists
│   ├── test_loader_functions.py    ← Need
│   ├── test_data_validation.py     ← Need
│   └── test_key_generation.py      ← Need
├── integration/
│   ├── test_etl_pipeline.py        ← Need
│   ├── test_supabase_load.py       ← Need
│   └── test_full_flow.py           ← Need
└── fixtures/
    ├── sample_game_data/           ← Need
    └── expected_outputs/           ← Need
```

---

## Code Quality Issues

### Anti-Patterns Found

```python
# 1. Bare except clauses
try:
    result = process_data()
except:  # Bad - catches everything including KeyboardInterrupt
    pass

# Should be:
try:
    result = process_data()
except (ValueError, KeyError) as e:
    logger.error(f"Processing failed: {e}")
    raise

# 2. Mutable default arguments
def process_events(events=[]):  # Bad - shared mutable state
    events.append(new_event)

# Should be:
def process_events(events=None):
    events = events or []

# 3. String concatenation in loops
result = ""
for item in items:
    result += str(item)  # Bad - O(n²)

# Should be:
result = "".join(str(item) for item in items)

# 4. No type hints
def calculate_stats(df, game_id):  # What types?
    pass

# Should be:
def calculate_stats(df: pd.DataFrame, game_id: int) -> pd.DataFrame:
    pass
```

### Files Needing Refactoring

| File | Issue | Suggestion |
|------|-------|------------|
| `src/main.py` | Too long (800+ lines) | Split into modules |
| `game_loader.py` | Complex parsing | Add intermediate functions |
| `flexible_loader.py` | Inconsistent error handling | Standardize |
| Various | Magic numbers | Extract to constants |

---

## Performance Considerations

### Current Bottlenecks

1. **Full file loading** - Entire Excel files loaded into memory
2. **No streaming** - CSV exports write entire dataframe at once
3. **Sequential processing** - Games processed one at a time
4. **No caching** - BLB_Tables.xlsx reloaded on each run

### Optimization Opportunities

```python
# 1. Chunked reading for large files
for chunk in pd.read_excel(file, chunksize=10000):
    process_chunk(chunk)

# 2. Generator-based CSV writing
def generate_rows():
    for game in games:
        yield from process_game(game)

# 3. Parallel game processing
from concurrent.futures import ProcessPoolExecutor
with ProcessPoolExecutor(max_workers=4) as executor:
    results = executor.map(process_game, game_ids)

# 4. LRU caching for reference data
from functools import lru_cache

@lru_cache(maxsize=1)
def load_blb_tables():
    return pd.read_excel("data/BLB_Tables.xlsx", sheet_name=None)
```

---

## Security Review Points

### Current State

| Area | Status | Notes |
|------|--------|-------|
| Credentials | ⚠️ | In config file, not env vars |
| SQL Injection | ✓ | Using Supabase client (parameterized) |
| Data Validation | ⚠️ | Minimal input validation |
| Logging | ⚠️ | May log sensitive data |

### Recommendations

1. Move credentials to environment variables
2. Add input validation for all user-provided data
3. Sanitize log output
4. Add rate limiting for API calls

---

## Recommended Refactoring Plan

### Phase 1: Foundation (Week 1)

- [ ] Add comprehensive type hints
- [ ] Standardize error handling
- [ ] Extract magic numbers to constants
- [ ] Add missing docstrings
- [ ] Set up proper logging

### Phase 2: Testing (Week 2)

- [ ] Add integration test framework
- [ ] Create test fixtures
- [ ] Add loader unit tests
- [ ] Add edge case tests
- [ ] Set up CI pipeline

### Phase 3: Refactoring (Week 3)

- [ ] Split main.py into modules
- [ ] DRY up stats calculations
- [ ] Implement proper config management
- [ ] Add transaction support for loads

### Phase 4: Optimization (Week 4)

- [ ] Add chunked file processing
- [ ] Implement caching
- [ ] Add parallel processing option
- [ ] Profile and optimize hot paths

---

## Acceptance Criteria

When you're done, the codebase should:

1. [ ] Pass all existing tests
2. [ ] Have 80%+ code coverage
3. [ ] Have zero bare except clauses
4. [ ] Have type hints on all public functions
5. [ ] Have docstrings on all classes and public methods
6. [ ] Handle all edge cases gracefully
7. [ ] Have integration tests for critical paths
8. [ ] Load data atomically (all or nothing)
9. [ ] Log errors without exposing sensitive data
10. [ ] Support the video highlights feature

---

## Resources

| Resource | Location |
|----------|----------|
| Stats Reference | `docs/STATS_REFERENCE_COMPLETE.md` |
| Data Dictionary | `docs/DATA_DICTIONARY.md` |
| Schema SQL | `sql/01_CREATE_ALL_TABLES.sql` |
| Video Highlights | `sql/04_VIDEO_HIGHLIGHTS.sql` |
| Current Tests | `tests/` |
| Extension Guide | `docs/EXTENSION_GUIDE.md` |
| Architecture | `docs/CODE_ARCHITECTURE.md` |

