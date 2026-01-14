# Data Dictionary Enhancement - TODO

**Created:** 2026-01-13  
**Status:** Pending  
**Priority:** Medium

---

## Task Overview

Enhance `docs/DATA_DICTIONARY_FULL.md` with complete calculation formulas for all calculated columns.

Currently, `DATA_DICTIONARY_FULL.md` exists (6,577 lines, 131 tables) but the "Calculation / Formula" column is mostly empty or marked as "Unknown" for calculated fields.

---

## Requirements

The data dictionary should include:

1. **Complete calculation formulas** for all calculated/derived columns
2. **Source references** - where formulas come from (CALCULATION_LOG.md, FORMULA_MANAGEMENT.md, code)
3. **Formula types** - percentage, rate, sum, difference, ratio, custom
4. **Dependencies** - which source columns are used
5. **Conditions** - when formulas apply (e.g., "if TOI > 0")

---

## Source Materials

### Primary Sources:
- `docs/CALCULATION_LOG.md` - Detailed formulas for player stats, game score, etc.
- `docs/FORMULA_MANAGEMENT.md` - Formula system documentation
- `config/formulas.json` - JSON-based formula definitions
- `src/formulas/player_stats_formulas.py` - Python formula implementations
- `src/calculations/` - Calculation functions (goals, corsi, ratings, time)

### Key Formula Categories:

1. **Player Stats Formulas** (from FORMULA_MANAGEMENT.md):
   - Percentage formulas: `shooting_pct = goals / sog * 100`
   - Rate formulas: `goals_per_60 = goals / toi_minutes * 60`
   - Sum formulas: `points = goals + assists`
   - Difference formulas: `plus_minus = plus_total - minus_total`

2. **Game Score Components** (from CALCULATION_LOG.md):
   - `gs_scoring = goals * 1.0 + primary_assists * 0.8 + secondary_assists * 0.5`
   - `gs_shots = sog * 0.1 + shots_high_danger * 0.15`
   - `game_score = 2.0 + game_score_raw`

3. **Advanced Stats**:
   - Corsi/Fenwick percentages
   - Expected Goals (xG) model
   - WAR/GAR calculations
   - Relative stats

---

## Implementation Approach

### Option 1: Update Existing DATA_DICTIONARY_FULL.md
- Pros: Single source of truth
- Cons: Large file (6,577 lines), requires careful updates

### Option 2: Create Separate CALCULATIONS_REFERENCE.md
- Pros: Easier to maintain, can cross-reference
- Cons: Information split across files

### Option 3: Enhance Auto-Generation Script
- Pros: Formulas stay in sync with code
- Cons: Requires script updates, formulas must be extractable

**Recommendation:** Start with Option 2 (separate reference), then merge into full dictionary once complete.

---

## Tables Requiring Formula Documentation

Priority tables (most used calculated columns):

1. **fact_player_game_stats** - ~317 columns, many calculated
2. **fact_goalie_game_stats** - ~128 columns
3. **fact_events** - Time calculations, derived columns
4. **fact_shifts** - TOI, ratings, percentages
5. **fact_player_period_stats** - Period-level aggregations
6. **fact_team_game_stats** - Team-level calculations

---

## Example Enhancement

**Before:**
```
| shooting_pct | float64 | - |  |  | Unknown | 67 | 0.0% | No |
```

**After:**
```
| shooting_pct | float64 | Shooting percentage | Percentage of shots on goal that result in goals | goals / sog * 100 (if sog > 0, else 0.0) | Calculated | 67 | 0.0% | Yes |
```

---

## Next Steps

1. [ ] Review CALCULATION_LOG.md and extract all formulas
2. [ ] Map formulas to columns in DATA_DICTIONARY_FULL.md
3. [ ] Create/update calculation reference document
4. [ ] Update dictionary generation script (if using auto-gen)
5. [ ] Validate formulas match actual code implementations
6. [ ] Update documentation index/links

---

## Related Files

- `docs/DATA_DICTIONARY_FULL.md` - Main dictionary (needs enhancement)
- `docs/DATA_DICTIONARY.md` - Shorter version (may also need updates)
- `docs/CALCULATION_LOG.md` - Formula source
- `docs/FORMULA_MANAGEMENT.md` - Formula system docs
- `scripts/generate_data_dictionary.py` - Auto-generation script (if exists)

---

## Notes

- This is a significant documentation task requiring careful mapping of formulas to columns
- Should be done incrementally, starting with most-used tables
- Consider automated testing to ensure formulas match code implementations
- May need to coordinate with code changes if formulas are updated
