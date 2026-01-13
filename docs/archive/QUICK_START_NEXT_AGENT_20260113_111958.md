# Quick Start for Next Agent

**Starting point for v29.2 work**

---

## Context

Previous agent (v29.1) completed:
- ✅ Calculations module (`src/calculations/`)
- ✅ Builders module (`src/builders/`)
- ✅ Formula management system (`src/formulas/`)
- ✅ Performance optimizations
- ✅ Documentation

**Status:** All committed and ready. You're starting fresh for v29.2.

---

## Your Tasks (v29.2)

### Priority 1: Integrate Formula System

**Goal:** Use formula registry in `create_fact_player_game_stats()`

**Files to modify:**
- `src/tables/core_facts.py` - Replace hardcoded formulas

**How:**
1. Import formula applier
2. Replace `calculate_rate_stats()` with `apply_player_stats_formulas()`
3. Replace hardcoded percentages with formula registry
4. Test thoroughly

**See:** `docs/FORMULA_MANAGEMENT.md` for details

### Priority 2: Performance Optimization

**Goal:** Optimize slow calculations

**Targets:**
- Team ratings calculation (line ~3868 in base_etl.py)
- Venue stat mapping (line ~4236 in base_etl.py)
- Replace `.iterrows()` loops

**See:** `docs/PERFORMANCE_OPTIMIZATION.md` for guide

### Priority 3: More Refactoring

**Goal:** Extract more builders

**Targets:**
- Player stats builder
- Team stats builder

---

## Key Files to Read

1. `docs/REFACTORING.md` - Refactoring guide
2. `docs/FORMULA_MANAGEMENT.md` - Formula system guide
3. `docs/PERFORMANCE_OPTIMIZATION.md` - Optimization guide
4. `AGENT_HANDOFF.md` - This handoff document

---

## Code Patterns to Follow

### Use Calculations Module
```python
from src.calculations import filter_goals, calculate_cf_pct
```

### Use Builders
```python
from src.builders import build_fact_events, build_fact_shifts
```

### Use Formula System
```python
from src.formulas.formula_applier import apply_player_stats_formulas
df = apply_player_stats_formulas(df)
```

---

## Testing

```bash
# Run unit tests
pytest tests/test_calculations.py -v

# Run ETL
python run_etl.py

# Validate
python validate.py
```

---

## Questions?

- Check `docs/CODEBASE_ASSESSMENT.md` for code quality notes
- Check `docs/CHANGELOG.md` for version history
- Check `REFACTORING_COMPLETE.md` for what was done

---

*Ready to start: 2026-01-13*
