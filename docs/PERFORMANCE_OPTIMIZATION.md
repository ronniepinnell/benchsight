# Performance Optimization Guide

**BenchSight ETL Performance Improvements**

Last Updated: 2026-01-13  
Version: 29.1

---

## Overview

This document tracks performance optimization opportunities and completed improvements.

**Current Performance:**
- 4 games: ~115 seconds
- Extrapolated to 100 games: ~48 minutes (needs improvement)

**Target Performance:**
- 100 games: < 15 minutes
- 1000 games: < 2 hours

---

## Completed Optimizations (v29.1)

### 1. Vectorized Percentage Calculations ✅

**Before:**
```python
sp['cf_pct'] = sp.apply(lambda r: (r['cf'] / (r['cf'] + r['ca']) * 100) if (r['cf'] + r['ca']) > 0 else 50.0, axis=1)
```

**After:**
```python
total_cf = sp['cf'] + sp['ca']
sp['cf_pct'] = (sp['cf'] / total_cf * 100).where(total_cf > 0, 50.0)
```

**Impact:** ~10x faster for percentage calculations

**Applied to:**
- `cf_pct` calculation
- `ff_pct` calculation
- `fo_pct` calculation

---

## High-Priority Optimizations

### 1. Team Ratings Calculation (HIGH IMPACT)

**Location:** `base_etl.py` line ~3868

**Current (Slow):**
```python
home_ratings_data = shifts.apply(lambda r: calc_team_ratings(r, home_skater_cols, player_rating_map), axis=1)
shifts['home_avg_rating'] = [r[0] for r in home_ratings_data]
```

**Optimized Approach:**
```python
# Vectorized: Extract player IDs, map to ratings, calculate stats
for col in home_skater_cols:
    shifts[f'{col}_rating'] = shifts[col].map(player_rating_map)
    
# Calculate stats using vectorized operations
rating_cols = [f'{col}_rating' for col in home_skater_cols]
shifts['home_avg_rating'] = shifts[rating_cols].mean(axis=1)
shifts['home_min_rating'] = shifts[rating_cols].min(axis=1)
shifts['home_max_rating'] = shifts[rating_cols].max(axis=1)
```

**Estimated Speedup:** 50-100x for large datasets

### 2. Venue Stat Mapping (MEDIUM IMPACT)

**Location:** `base_etl.py` line ~4236-4251

**Current (Slow):**
```python
sp['gf'] = sp.apply(lambda r: get_venue_stat(r, 'home_gf_all', 'away_gf_all'), axis=1)
```

**Optimized Approach:**
```python
# Vectorized: Use np.where or .loc with conditions
home_mask = sp['team_venue'] == 'Home'
sp.loc[home_mask, 'gf'] = sp.loc[home_mask, 'home_gf_all']
sp.loc[~home_mask, 'gf'] = sp.loc[~home_mask, 'away_gf_all']
```

**Estimated Speedup:** 20-50x

### 3. Replace .iterrows() Loops (MEDIUM IMPACT)

**Found:** 29 instances of `.iterrows()`

**High-Impact Targets:**
- Line 1034: `build_player_lookup()` - processes all roster rows
- Line 1411: Shift player creation loop
- Line 3914: Shift goals calculation loop

**Optimization Strategy:**
- Use vectorized operations where possible
- Use `.apply()` with vectorized functions
- Use groupby operations instead of loops

**Estimated Speedup:** 10-50x per loop

---

## Medium-Priority Optimizations

### 4. FK Column Mapping (MEDIUM IMPACT)

**Location:** Multiple locations using `.map()` on Series

**Current:**
```python
tracking['position_id'] = tracking.apply(get_position, axis=1)
```

**Optimized:**
```python
# Create lookup dict once, use vectorized .map()
position_map = {value: key for key, value in position_lookup.items()}
tracking['position_id'] = tracking['position'].map(position_map)
```

**Estimated Speedup:** 5-10x

### 5. Groupby Operations (LOW-MEDIUM IMPACT)

**Location:** Multiple groupby operations

**Optimization:**
- Use `as_index=False` consistently
- Pre-filter data before groupby
- Use categorical types for groupby keys

**Estimated Speedup:** 2-5x

---

## Low-Priority Optimizations

### 6. Data Type Optimization

**Opportunities:**
- Use categorical types for repeated strings
- Use int8/int16 for small integers
- Use float32 where precision allows

**Estimated Speedup:** 1.5-2x (memory + speed)

### 7. Parallel Processing

**Opportunities:**
- Process multiple games in parallel
- Use multiprocessing for independent operations

**Estimated Speedup:** 2-4x (depending on CPU cores)

---

## Performance Testing

### Benchmark Script

Create `scripts/benchmark_etl.py`:

```python
import time
from src.core.base_etl import main

start = time.time()
main()
duration = time.time() - start

print(f"ETL Duration: {duration:.2f} seconds")
print(f"Games processed: {len(VALID_TRACKING_GAMES)}")
print(f"Time per game: {duration / len(VALID_TRACKING_GAMES):.2f} seconds")
```

### Profiling

Use cProfile to identify bottlenecks:

```bash
python -m cProfile -o etl_profile.prof run_etl.py
python -m pstats etl_profile.prof
```

---

## Implementation Priority

### Phase 1 (v29.2) - High Impact
1. ✅ Vectorized percentage calculations (DONE)
2. ⏳ Team ratings calculation
3. ⏳ Venue stat mapping

**Target:** 2-3x overall speedup

### Phase 2 (v29.3) - Medium Impact
4. Replace high-impact `.iterrows()` loops
5. Optimize FK column mapping
6. Groupby optimizations

**Target:** Additional 2-3x speedup

### Phase 3 (v30.0) - Low Impact
7. Data type optimization
8. Parallel processing
9. Memory optimization

**Target:** Additional 1.5-2x speedup

---

## Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| 4 games | 115s | 60s | ⏳ |
| 100 games (extrapolated) | 48min | 15min | ⏳ |
| 1000 games (extrapolated) | 8hr | 2hr | ⏳ |

---

## Best Practices

### Do's ✅
- Use vectorized pandas operations
- Use `.where()` for conditional assignments
- Use `.map()` with dicts for lookups
- Pre-filter data before operations
- Use categorical types for repeated values

### Don'ts ❌
- Avoid `.iterrows()` for large DataFrames
- Avoid `.apply(axis=1)` when vectorized alternative exists
- Avoid loops over DataFrame rows
- Avoid repeated calculations

---

## References

- [Pandas Performance Tips](https://pandas.pydata.org/docs/user_guide/enhancingperf.html)
- [NumPy Vectorization](https://numpy.org/doc/stable/reference/ufuncs.html)
- [Python Profiling](https://docs.python.org/3/library/profile.html)

---

*Last updated: 2026-01-13*
