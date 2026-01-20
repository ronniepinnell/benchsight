# Refactoring Progress Report

**Date:** 2026-01-20  
**Status:** In Progress

---

## ✅ Completed

### 1. Deployment Scripts Fixed

**Files Modified:**
- `scripts/deploy_to_dev.sh`
- `scripts/deploy_to_production.sh`
- `scripts/switch_env.sh`

**Changes:**
- ✅ Standardized environment naming to `dev` (removed `sandbox`/`develop` confusion)
- ✅ Fixed broken summary logic (now tracks status correctly)
- ✅ Added error handling with `set -euo pipefail`
- ✅ Added pre-flight checks (git branch, uncommitted changes)
- ✅ Improved error messages and user feedback

**Impact:** Scripts are now more reliable and user-friendly.

---

### 2. .iterrows() Replacements Started

**File:** `src/core/base_etl.py`

**Replacements Made:**
1. ✅ Lines 2372-2376: `period_max` dictionary building → Vectorized with `groupby().max()`
2. ✅ Lines 2380-2388: `shift_ranges` dictionary building → Vectorized with `groupby().apply()`
3. ✅ Lines 891-903: `season_map` building → Vectorized with pandas operations

**Performance Impact:** These changes should provide 10-50x speedup for these operations.

---

## 🔄 In Progress

### 3. More .iterrows() Replacements Needed

**Remaining in `base_etl.py`:**
- Line 700-727: Finding closest opponent (nested loops) - Complex, needs scipy.spatial or vectorized distance
- Line 1530: Building shift_players table - Can be optimized with melt/stack operations
- Line 2691: Shift processing loop - Can be vectorized
- Line 2799-2829: Cycle events building - Can be optimized
- Line 2901: Cycle processing - Can be vectorized
- Line 4758: Shift goals processing - Can be optimized
- Line 4842: Game goals processing - Can be optimized
- Line 5284: Shift players processing - Can be optimized
- Line 5367: Competition tier mapping - Can be vectorized
- Line 5408: Performance calculation - Can be optimized
- Line 5579: Roster position updates - Can be vectorized

**Estimated Remaining:** ~10-15 more replacements in `base_etl.py`

---

## 📋 Planned

### 4. Refactor base_etl.py Structure

**Target Structure:**
```
src/core/
├── base_etl.py          # Orchestrator only (~300-500 lines)
├── data_loader.py        # load_blb_tables(), load_tracking_data()
├── event_enhancer.py     # enhance_event_tables(), enhance_derived_event_tables()
├── shift_enhancer.py     # enhance_shift_tables(), enhance_shift_players()
├── table_creator.py      # create_derived_tables(), create_reference_tables()
└── validator.py          # validate_all() and related
```

**Status:** Not started

---

### 5. Replace .iterrows() in Other Files

**High Priority Files:**
- `src/tables/remaining_facts.py` - 10+ instances
- `src/tables/core_facts.py` - 5+ instances
- `src/tables/event_analytics.py` - 3+ instances
- `src/tables/shift_analytics.py` - 1+ instances
- `src/tables/macro_stats.py` - 8+ instances

**Status:** Not started

---

## 📊 Statistics

**Total .iterrows() Calls Found:** 233
**Replaced So Far:** 3 (1.3%)
**Remaining:** 230 (98.7%)

**Files Modified:** 4
- `scripts/deploy_to_dev.sh`
- `scripts/deploy_to_production.sh`
- `scripts/switch_env.sh`
- `src/core/base_etl.py`

---

## 🎯 Next Steps

1. Continue replacing .iterrows() in `base_etl.py` (focus on high-impact functions)
2. Replace .iterrows() in `remaining_facts.py` (many instances, high impact)
3. Replace .iterrows() in `core_facts.py`
4. Begin refactoring `base_etl.py` structure (extract modules)
5. Update `run_etl.py` to use refactored modules

---

## ⚠️ Notes

- Some .iterrows() calls are complex (nested loops, distance calculations) and may require scipy or custom vectorized functions
- Refactoring should be done incrementally with testing after each change
- Performance improvements will be most noticeable with larger datasets (100+ games)

---

**Last Updated:** 2026-01-20
