# PRD: ETL Vectorization

**Status:** Draft
**Priority:** P0
**Phase:** 2 (ETL Optimization)
**Owner:** [Your Name]
**Created:** 2025-01-22
**GitHub Issues:** #5, #25, #26, #27, #28, #29

---

## Overview

### Problem Statement
The ETL pipeline uses `.iterrows()` in multiple locations, which is:
- **Slow:** 100-1000x slower than vectorized pandas operations
- **Against CLAUDE.md rules:** Explicitly forbidden
- **A maintenance burden:** Hard to read and modify

### Solution
Replace all `.iterrows()` usage with vectorized pandas operations using `.groupby()`, `.apply()`, `.merge()`, and boolean indexing.

---

## Goals

1. **Zero `.iterrows()` calls** in the codebase
2. **Maintain data integrity** - same outputs as before
3. **Improve performance** - measurable speedup
4. **Follow CLAUDE.md standards** - use approved patterns

### Success Criteria

- [ ] `grep -r "iterrows" src/` returns 0 results
- [ ] All 139 tables produce identical output
- [ ] ETL runtime reduced (target: 20%+ faster)
- [ ] All tests pass
- [ ] Code review approved

---

## Non-Goals

- General performance optimization (separate effort)
- Refactoring unrelated code
- Adding new features

---

## Current State

### Known `.iterrows()` Locations

| File | Function | Purpose | Priority |
|------|----------|---------|----------|
| `shift_enhancers.py` | `match_goals_to_shifts()` | Match goals to on-ice players | P0 |
| `shift_enhancers.py` | `process_player_roster()` | Process roster data | P1 |
| `derived_columns.py` | `calculate_pressure()` | Calculate pressure metrics | P1 |
| `event_enhancers.py` | `infer_zone()` | Infer zone from coordinates | P1 |
| `event_enhancers.py` | `detect_cycles()` | Detect cycling patterns | P1 |

### Finding All Violations

```bash
# Find all iterrows usage
grep -rn "\.iterrows()" src/

# Find all iteritems (also slow)
grep -rn "\.iteritems()" src/

# Find all itertuples (acceptable but review)
grep -rn "\.itertuples()" src/
```

---

## Requirements

### Functional Requirements

#### FR-1: Replace Goal-Shift Matching (#25)
**Current:**
```python
for idx, goal in goals_df.iterrows():
    # Find players on ice during goal
    on_ice = shifts_df[
        (shifts_df['start'] <= goal['time']) &
        (shifts_df['end'] >= goal['time'])
    ]
```

**Target:**
```python
# Vectorized using merge and boolean indexing
goals_with_shifts = goals_df.merge(
    shifts_df,
    how='cross'
).query('start <= time <= end')
```

#### FR-2: Replace Roster Processing (#26)
**Current:**
```python
for idx, player in roster_df.iterrows():
    # Process each player
```

**Target:**
```python
# Vectorized using groupby
roster_df.groupby('team_id').apply(process_team_roster)
```

#### FR-3: Replace Pressure Calculation (#27)
**Current:**
```python
for idx, event in events_df.iterrows():
    # Calculate pressure based on context
```

**Target:**
```python
# Vectorized using rolling windows and shifts
events_df['pressure'] = (
    events_df.groupby('game_id')
    .apply(lambda g: calculate_pressure_vectorized(g))
)
```

#### FR-4: Replace Zone Inference (#28)
**Current:**
```python
for idx, event in events_df.iterrows():
    if event['x'] > threshold:
        zone = 'offensive'
```

**Target:**
```python
# Vectorized using np.where
events_df['zone'] = np.where(
    events_df['x'] > offensive_threshold, 'offensive',
    np.where(events_df['x'] < defensive_threshold, 'defensive', 'neutral')
)
```

#### FR-5: Replace Cycle Detection (#29)
**Current:**
```python
for idx, event in events_df.iterrows():
    # Check if event is part of cycle
```

**Target:**
```python
# Vectorized using shift() and cumsum()
events_df['is_cycle'] = (
    events_df.groupby('possession_id')
    .apply(detect_cycle_vectorized)
)
```

---

## Technical Design

### Vectorization Patterns

#### Pattern 1: Boolean Indexing
```python
# Instead of iterating to filter
df_filtered = df[df['column'] > threshold]
```

#### Pattern 2: np.where for Conditionals
```python
df['new_col'] = np.where(condition, value_if_true, value_if_false)
```

#### Pattern 3: groupby + apply
```python
result = df.groupby('key').apply(vectorized_function)
```

#### Pattern 4: merge for Joins
```python
result = df1.merge(df2, on='key', how='left')
```

#### Pattern 5: shift() for Row Comparisons
```python
df['prev_value'] = df.groupby('id')['value'].shift(1)
df['changed'] = df['value'] != df['prev_value']
```

#### Pattern 6: cumsum() for Running Totals
```python
df['running_total'] = df.groupby('id')['value'].cumsum()
```

### Verification Strategy

For each replacement:
1. Capture output before change
2. Make vectorized change
3. Compare output (should be identical)
4. Measure performance improvement

```python
# Verification helper
def verify_identical(before_df, after_df, name):
    pd.testing.assert_frame_equal(before_df, after_df)
    print(f"✅ {name}: Outputs identical")
```

---

## Implementation Plan

### Phase 1: Audit (0.5 day)
1. Run grep to find all violations
2. Document each location
3. Prioritize by impact/complexity
4. Create test fixtures for each

### Phase 2: Goal-Shift Matching (1 day) - #25
1. Create test with known output
2. Implement vectorized version
3. Verify identical output
4. Measure performance gain

### Phase 3: Roster Processing (0.5 day) - #26
1. Create test with known output
2. Implement vectorized version
3. Verify identical output

### Phase 4: Pressure Calculation (1 day) - #27
1. Create test with known output
2. Implement vectorized version
3. Verify identical output

### Phase 5: Zone Inference (0.5 day) - #28
1. Create test with known output
2. Implement vectorized version
3. Verify identical output

### Phase 6: Cycle Detection (1 day) - #29
1. Create test with known output
2. Implement vectorized version
3. Verify identical output

### Phase 7: Final Verification (0.5 day)
1. Run full ETL
2. Compare all 139 tables
3. Run performance benchmark
4. Update documentation

---

## Testing Strategy

### Before Each Change
```python
# Save baseline output
baseline_df = function_under_test(test_input)
baseline_df.to_csv('tests/fixtures/baseline_{function}.csv')
```

### After Each Change
```python
def test_function_vectorized():
    baseline = pd.read_csv('tests/fixtures/baseline_{function}.csv')
    result = function_under_test_vectorized(test_input)
    pd.testing.assert_frame_equal(baseline, result)
```

### Performance Benchmarks
```python
import timeit

# Before
time_before = timeit.timeit(lambda: old_function(data), number=10)

# After
time_after = timeit.timeit(lambda: new_function(data), number=10)

print(f"Speedup: {time_before / time_after:.1f}x")
```

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Subtle output differences | Medium | High | Comprehensive test fixtures |
| Performance regression | Low | Medium | Benchmark before/after |
| Complex logic hard to vectorize | Medium | Medium | Use `.apply()` as fallback |

---

## Open Questions

1. Is `.itertuples()` acceptable as intermediate step?
2. What's the minimum acceptable speedup?
3. Should we add a CI check to prevent new `.iterrows()` usage?

---

## Appendix

### Related Documents
- [CLAUDE.md](../../../CLAUDE.md) - Vectorization requirement
- [ETL_ARCHITECTURE.md](../../etl/ETL_ARCHITECTURE.md)

### Related Issues
- #5: Replace .iterrows() with vectorized operations
- #25: Vectorize goal-shift matching
- #26: Vectorize player/roster loops
- #27: Vectorize pressure calculation
- #28: Vectorize zone inference
- #29: Vectorize cycle detection

### Helpful Resources
- [Pandas Vectorization Guide](https://pandas.pydata.org/docs/user_guide/enhancingperf.html)
- [NumPy Broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html)
