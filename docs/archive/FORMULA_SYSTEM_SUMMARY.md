# Formula Management System - Summary

**Making formula updates easy for fact_player_game_stats**

Date: 2026-01-13  
Version: 29.1

---

## Problem

`fact_player_game_stats` has 300+ columns with formulas scattered throughout code:
- Hard to find where formulas are defined
- Hard to update formulas (requires code changes)
- Risk of inconsistencies
- No centralized formula documentation

## Solution

Created a **Formula Management System** that:
- ✅ Centralizes formulas in `config/formulas.json`
- ✅ Allows formula updates without code changes
- ✅ Provides formula groups for easy application
- ✅ Validates dependencies automatically
- ✅ Documents formulas clearly

---

## How It Works

### 1. Formula Configuration

Formulas are defined in `config/formulas.json`:

```json
{
  "formulas": {
    "shooting_pct": {
      "type": "percentage",
      "expression": "goals / sog * 100",
      "description": "Shooting percentage",
      "dependencies": ["goals", "sog"],
      "default_value": 0.0,
      "condition": "sog > 0"
    }
  }
}
```

### 2. Apply Formulas

```python
from src.formulas.formula_applier import apply_player_stats_formulas

# Apply all formulas
df = apply_player_stats_formulas(df)

# Or apply specific ones
df = apply_player_stats_formulas(df, formula_names=['shooting_pct', 'cf_pct'])
```

### 3. Update Formulas

**Just edit the JSON file!**

```json
{
  "shooting_pct": {
    "expression": "goals / (sog + shots_missed) * 100"  // Updated!
  }
}
```

---

## Benefits

### For Developers
- ✅ Easy to find formulas (all in one place)
- ✅ Easy to update (just edit JSON)
- ✅ No code changes needed
- ✅ Version control friendly (JSON diffs)

### For Users
- ✅ Can update formulas without coding
- ✅ Clear documentation of what each formula does
- ✅ Easy to test formula changes
- ✅ Can see all formulas at a glance

---

## Files Created

### Core System
- `src/formulas/__init__.py` - Module exports
- `src/formulas/registry.py` - Formula registry system
- `src/formulas/player_stats_formulas.py` - Formula definitions (code)
- `src/formulas/formula_applier.py` - Apply formulas to DataFrames
- `src/formulas/config_loader.py` - Load formulas from JSON

### Configuration
- `config/formulas.json` - Formula definitions (JSON)

### Documentation
- `docs/FORMULA_MANAGEMENT.md` - Complete usage guide

---

## Example: Updating Shooting Percentage

### Before (Hard Way)
1. Find formula in `core_facts.py` (line ~1637)
2. Understand the code context
3. Modify Python code
4. Test changes
5. Commit code changes

### After (Easy Way)
1. Open `config/formulas.json`
2. Find `shooting_pct` formula
3. Update `expression` field
4. Save file
5. Run ETL

**That's it!**

---

## Formula Types Supported

| Type | Example | Use Case |
|------|---------|----------|
| Percentage | `goals / sog * 100` | Shooting %, CF%, etc. |
| Rate (Per-60) | `goals / toi_minutes * 60` | Goals/60, Points/60 |
| Sum | `goals + assists` | Points, Total shots |
| Difference | `plus_total - minus_total` | Plus/minus |
| Ratio | `toi_seconds / shifts / 60` | Avg shift length |

---

## Next Steps

### Integration (v29.2)
1. Update `create_fact_player_game_stats()` to use formula system
2. Replace hardcoded formulas with formula registry calls
3. Add formula validation tests

### Enhancement (v29.3+)
1. Formula versioning
2. Formula change history
3. Formula testing UI
4. Formula impact analysis

---

## Usage Examples

### Apply All Formulas
```python
df = apply_player_stats_formulas(df)
```

### Apply Specific Formulas
```python
df = apply_player_stats_formulas(
    df,
    formula_names=['shooting_pct', 'cf_pct', 'goals_per_60']
)
```

### Apply Formula Groups
```python
# Apply all percentage formulas
df = apply_player_stats_formulas(
    df,
    formula_groups=['all_percentages']
)
```

### Update Formula in Code
```python
from src.formulas.formula_applier import update_formula

def new_formula(df):
    return (df['goals'] / df['sog'] * 100).where(df['sog'] > 0, 0.0)

update_formula('shooting_pct', new_formula)
```

---

## Current Formulas Defined

### Percentages
- `shooting_pct` - Goals / SOG
- `pass_pct` - Pass completion %
- `fo_pct` - Faceoff win %
- `cf_pct` - Corsi For %
- `ff_pct` - Fenwick For %

### Per-60 Rates
- `goals_per_60` - Goals per 60 min
- `assists_per_60` - Assists per 60 min
- `points_per_60` - Points per 60 min
- `sog_per_60` - Shots on goal per 60 min

### Sums
- `points` - Goals + Assists
- `assists` - Primary + Secondary
- `shots` - SOG + Blocked + Missed

### Differences
- `plus_minus` - Plus total - Minus total
- `corsi_diff` - CF - CA
- `fenwick_diff` - FF - FA

---

## Benefits Summary

| Aspect | Before | After |
|--------|--------|-------|
| Update formula | Edit Python code | Edit JSON file |
| Find formula | Search codebase | Check JSON file |
| Test formula | Run full ETL | Apply to test DataFrame |
| Document formula | Code comments | JSON description |
| Version control | Code diffs | JSON diffs |

---

*System created: 2026-01-13*
