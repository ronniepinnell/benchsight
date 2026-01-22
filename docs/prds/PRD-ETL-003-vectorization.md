# PRD: ETL-003 - Replace .iterrows() with Vectorized Operations

**Product Requirements Document**

Created: 2026-01-22
Status: Approved
Owner: Developer
Related Issues: #5, #25, #26, #27, #28, #29

---

## Problem Statement

**What problem are we solving?**

The ETL pipeline uses `.iterrows()` in multiple locations, which is extremely slow for pandas DataFrames. This pattern can be 100-1000x slower than vectorized operations and becomes a significant bottleneck as data grows.

**Why is this important?**

- Current ETL runtime is ~80 seconds for 4 games
- As we scale to full seasons (80+ games), runtime will become unacceptable
- `.iterrows()` is explicitly prohibited in CLAUDE.md rules
- Performance directly impacts developer productivity and user experience

**Who is affected?**

- Developers running ETL locally (wait times)
- Portal users triggering ETL jobs
- CI/CD pipeline (longer build times)

---

## Solution Approach

**How will we solve this problem?**

Replace all `.iterrows()` calls with pandas vectorized operations using:
1. `.groupby()` with `.apply()` or `.transform()`
2. Boolean indexing with `.loc[]`
3. Vectorized string operations (`.str.*`)
4. NumPy vectorized functions where applicable

**What are the key design decisions?**

1. Prioritize by impact: Profile first, fix highest-impact loops
2. Maintain exact same output (regression testing required)
3. Use `.groupby().apply()` for complex row-dependent logic

**What alternatives were considered?**

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| Keep .iterrows() | No code change | Slow, violates rules | Rejected |
| Use Polars | Faster than pandas | Major rewrite | Future consideration |
| Parallel processing | Faster | Complex, memory issues | Rejected for now |
| Vectorization | Fast, standard pandas | Some complexity | **Selected** |

---

## Technical Design

### Architecture

**High-level architecture:**

No architectural changes - this is an internal optimization that preserves all inputs/outputs.

**Component changes:**

Refactor specific functions in these modules:
- `src/core/base_etl.py`
- `src/core/etl_phases/*.py`
- `src/calculations/*.py`

### Implementation Details

**Key files/modules affected:**

| File | Function | Priority |
|------|----------|----------|
| `src/core/base_etl.py` | `_build_event_players()` | P0 |
| `src/core/etl_phases/derived_columns.py` | `add_player_team_columns()` | P0 |
| `src/core/etl_phases/event_enhancers.py` | Various enhancers | P1 |
| `src/calculations/corsi.py` | Corsi calculations | P1 |
| `src/calculations/time.py` | Time calculations | P1 |

**New files/modules needed:**

None - this is pure refactoring.

**Data model changes:**

None - outputs must remain identical.

### Integration Points

**How does this integrate with existing code?**

Direct replacement of implementation details. All function signatures and outputs remain unchanged.

**Dependencies on other components:**

- Requires comprehensive test coverage first (#36)
- Requires validation framework (#35)

---

## Implementation Phases

### Phase 1: Profile and Identify

**Description:** Profile ETL to identify all .iterrows() calls and measure impact.

**Tasks:**
- [ ] Add profiling to ETL run (`cProfile` or `line_profiler`)
- [ ] Run ETL and capture timing per function
- [ ] Identify all `.iterrows()` locations with `grep -r "iterrows" src/`
- [ ] Rank by runtime impact (highest first)
- [ ] Document baseline performance metrics

**Success Criteria:**
- Complete list of `.iterrows()` locations
- Baseline timing for each
- Priority ranking documented

### Phase 2: Vectorize Critical Functions (P0)

**Description:** Replace .iterrows() in highest-impact functions.

**Tasks:**
- [ ] `_build_event_players()` - convert row iteration to groupby
- [ ] `add_player_team_columns()` - use merge instead of iteration
- [ ] Run validation after each change
- [ ] Measure performance improvement

**Success Criteria:**
- No `.iterrows()` in P0 functions
- All 139 tables still generated correctly
- Measurable performance improvement (target: 30%+ faster)

### Phase 3: Vectorize Remaining Functions (P1)

**Description:** Replace .iterrows() in remaining functions.

**Tasks:**
- [ ] Event enhancer functions
- [ ] Shift enhancer functions
- [ ] Calculation modules (corsi, time, etc.)
- [ ] Final cleanup and documentation

**Success Criteria:**
- Zero `.iterrows()` calls in codebase
- All validation passes
- ETL runtime reduced by 50%+

---

## Success Criteria

**How do we know this is complete and successful?**

- [ ] `grep -r "iterrows" src/` returns zero results
- [ ] `./benchsight.sh etl validate` passes
- [ ] All 139 tables generated with correct row counts
- [ ] ETL runtime reduced by at least 50%
- [ ] No regression in goal counting or other critical stats

**Acceptance Tests:**
- Run ETL before and after, compare all CSV outputs
- Verify goal counts match official totals (#13)
- Performance benchmark shows improvement

---

## Dependencies

**What needs to exist or be completed first?**

- [ ] Unit tests for critical calculations (#36) - to catch regressions
- [ ] Table verification framework (#35) - to validate outputs

**Blocking Issues:**
- None (can proceed in parallel with tests)

---

## Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Logic bug during refactor | High | Medium | Comprehensive before/after output comparison |
| Edge cases not handled | Medium | Medium | Test with multiple games, edge case data |
| Performance worse in some cases | Low | Low | Profile after changes, revert if needed |

---

## Testing Strategy

**How will we test this?**

- [ ] Unit tests for each refactored function
- [ ] Integration test: full ETL run comparison
- [ ] Performance test: timing before/after
- [ ] ETL validation suite

**Test scenarios:**
- Single game ETL
- Multi-game ETL (4 games baseline)
- Edge cases (empty events, missing data)

---

## Documentation

**What documentation needs to be updated?**

- [ ] Code comments explaining vectorized approach
- [ ] Performance benchmarks in ETL docs

**New documentation needed:**
- None

---

## Rollout Plan

**How will this be deployed?**

- [ ] Develop on feature branch
- [ ] PR with before/after comparison
- [ ] Merge to develop
- [ ] Run full ETL validation
- [ ] Merge to main when stable

**Rollback plan:**
- Git revert if issues discovered
- Keep original implementation commented until verified

---

## Related Documents

- [ETL Architecture](../etl/ETL_ARCHITECTURE.md)
- [ETL Code Walkthrough](../walkthrough/etl/05-etl-code-walkthrough.md)
- [CLAUDE.md Vectorization Rules](../../CLAUDE.md)

---

## Notes

**Vectorization Patterns to Use:**

```python
# BAD - iterrows
for idx, row in df.iterrows():
    df.loc[idx, 'new_col'] = calculate(row['col1'], row['col2'])

# GOOD - vectorized
df['new_col'] = df.apply(lambda row: calculate(row['col1'], row['col2']), axis=1)

# BETTER - fully vectorized
df['new_col'] = np.where(df['col1'] > 0, df['col1'] * df['col2'], 0)

# BEST - groupby for grouped operations
df['team_total'] = df.groupby('team_id')['goals'].transform('sum')
```

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-01-22 | Initial PRD | Claude |

---

*Status: Approved*
