# BenchSight Refactoring Guide

**Code refactoring progress and guidelines**

Last Updated: 2026-01-13  
Version: 29.1

---

## Overview

This document tracks the ongoing refactoring effort to improve code quality, maintainability, and testability.

**Goal:** Break up monolithic files, extract reusable functions, and add comprehensive unit tests.

---

## Completed Refactoring (v29.1)

### 1. Calculations Module ✅

**Created:** `src/calculations/` module

**Extracted Functions:**
- Goal counting (`goals.py`)
- Corsi/Fenwick calculations (`corsi.py`)
- Rating calculations (`ratings.py`)
- Time on ice calculations (`time.py`)

**Benefits:**
- ✅ Pure functions (easier to test)
- ✅ Single source of truth for calculations
- ✅ Reusable across codebase
- ✅ 24 unit tests added

**Usage:**
```python
from src.calculations import (
    filter_goals,
    calculate_cf_pct,
    calculate_team_ratings,
    calculate_per_60_rate
)

# Use in any module
goals = filter_goals(events_df)
cf_pct = calculate_cf_pct(cf=10, ca=5)  # Returns 66.67
```

---

## In Progress

### 2. Table Builders Module (Next)

**Plan:** Extract table building logic from `base_etl.py`

**Target Structure:**
```
src/builders/
├── events.py      # fact_events builder
├── shifts.py      # fact_shifts builder
├── players.py     # Player stats builder
└── teams.py       # Team stats builder
```

**Current Status:** Planning phase

---

## Planned Refactoring

### 3. Performance Optimization

**Target:** Replace `.iterrows()` with vectorized operations

**Example:**
```python
# BEFORE (slow)
for _, row in df.iterrows():
    result = calculate_something(row)

# AFTER (fast)
df['result'] = df.apply(lambda row: calculate_something(row), axis=1)
# OR even better: vectorized operation
df['result'] = df['col1'] + df['col2']
```

**Impact:** 10-100x speedup for large datasets

### 4. Dependency Injection

**Target:** Reduce tight coupling between modules

**Current:** Global state, direct imports
**Target:** Dependency injection, interfaces

---

## Refactoring Principles

### 1. Single Responsibility Principle

Each module/function should do one thing well.

**Example:**
```python
# BAD: Does too much
def process_player_data(df):
    # Load data
    # Calculate stats
    # Format output
    # Save to file
    pass

# GOOD: Single responsibility
def calculate_player_stats(df):
    # Only calculates stats
    return stats_df

def format_player_output(stats_df):
    # Only formats
    return formatted_df
```

### 2. Testability

Functions should be easy to test with unit tests.

**Requirements:**
- Pure functions (no side effects)
- Clear inputs/outputs
- No global state
- Mockable dependencies

### 3. Single Source of Truth

Each calculation/constant should be defined once.

**Example:**
```python
# BAD: Duplicated
# In file1.py
GAME_TYPES = ['Regular', 'Playoffs']

# In file2.py
GAME_TYPES = ['Regular', 'Playoffs']  # Duplicate!

# GOOD: Single source
# In utils/game_type_aggregator.py
GAME_TYPE_SPLITS = ['Regular', 'Playoffs', 'All']
```

### 4. Documentation

All refactored code must have:
- Docstrings
- Type hints (where applicable)
- Usage examples
- Unit tests

---

## Testing Strategy

### Unit Tests

Test individual functions in isolation.

**Location:** `tests/test_calculations.py`

**Example:**
```python
def test_calculate_cf_pct():
    """Test CF% calculation."""
    assert calculate_cf_pct(10, 10) == 50.0
    assert calculate_cf_pct(0, 0) is None
```

### Integration Tests

Test full ETL pipeline end-to-end.

**Location:** `tests/test_etl.py`, `tests/test_integration.py`

### Performance Tests

Benchmark refactored code vs original.

**Target:** Same or better performance

---

## Migration Guide

### Using New Calculation Functions

**Before:**
```python
# In base_etl.py
goals = events[(events['event_type'] == 'Goal') & 
               (events['event_detail'] == 'Goal_Scored')]
```

**After:**
```python
from src.calculations import filter_goals

goals = filter_goals(events)
```

### Updating Existing Code

1. **Import new functions:**
   ```python
   from src.calculations import calculate_cf_pct
   ```

2. **Replace inline logic:**
   ```python
   # OLD
   cf_pct = (cf / (cf + ca)) * 100 if (cf + ca) > 0 else None
   
   # NEW
   cf_pct = calculate_cf_pct(cf, ca)
   ```

3. **Run tests:**
   ```bash
   pytest tests/test_calculations.py
   pytest tests/test_integration.py
   ```

---

## Code Review Checklist

Before merging refactored code:

- [ ] Functions extracted to appropriate modules
- [ ] Unit tests added and passing
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Performance maintained or improved
- [ ] Integration tests still pass
- [ ] CHANGELOG.md updated

---

## Metrics

### Code Quality Metrics

| Metric | Before | Target | Current |
|--------|--------|--------|---------|
| Largest file (lines) | 4,700 | < 500 | 4,700 |
| Unit test coverage | 0% | 80% | 15% |
| Function length (avg) | 200+ | < 50 | 150 |
| Code duplication | High | Low | Medium |

### Progress Tracking

- ✅ Calculations module (v29.1)
- ⏳ Table builders (v29.2)
- ⏳ Performance optimization (v29.3)
- ⏳ Dependency injection (v30.0)

---

## Resources

- [CODE_STANDARDS.md](CODE_STANDARDS.md) - Coding standards
- [CODEBASE_ASSESSMENT.md](CODEBASE_ASSESSMENT.md) - Code quality assessment
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines

---

*Last updated: 2026-01-13*
