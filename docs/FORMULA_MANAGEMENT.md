# Formula Management Guide

**How to update formulas in fact_player_game_stats**

Last Updated: 2026-01-13  
Version: 29.1

---

## Overview

The formula management system allows you to update statistical formulas without modifying code. Formulas are defined in configuration files and can be easily updated.

---

## Quick Start

### Update a Formula

1. **Edit `config/formulas.json`**
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

2. **Reload formulas** (if using hot-reload)
   ```python
   from src.formulas.config_loader import reload_formulas
   reload_formulas()
   ```

3. **Run ETL** - Formulas will be applied automatically

---

## Formula Types

### Percentage Formulas

Calculate percentages from numerator and denominator.

**Example:**
```json
{
  "shooting_pct": {
    "type": "percentage",
    "expression": "goals / sog * 100",
    "dependencies": ["goals", "sog"],
    "default_value": 0.0,
    "condition": "sog > 0"
  }
}
```

### Rate Formulas (Per-60)

Calculate per-60 minute rates.

**Example:**
```json
{
  "goals_per_60": {
    "type": "rate",
    "expression": "goals / toi_minutes * 60",
    "dependencies": ["goals", "toi_minutes"],
    "default_value": null,
    "condition": "toi_minutes > 0"
  }
}
```

### Sum Formulas

Add multiple columns together.

**Example:**
```json
{
  "points": {
    "type": "sum",
    "expression": "goals + assists",
    "dependencies": ["goals", "assists"]
  }
}
```

### Difference Formulas

Subtract one column from another.

**Example:**
```json
{
  "plus_minus": {
    "type": "difference",
    "expression": "plus_total - minus_total",
    "dependencies": ["plus_total", "minus_total"]
  }
}
```

### Ratio Formulas

Calculate ratios between columns.

**Example:**
```json
{
  "avg_shift_length": {
    "type": "ratio",
    "expression": "toi_seconds / shifts / 60",
    "dependencies": ["toi_seconds", "shifts"],
    "default_value": 0.0,
    "condition": "shifts > 0"
  }
}
```

---

## Formula Configuration Format

```json
{
  "formula_name": {
    "type": "percentage|rate|sum|difference|ratio|custom",
    "expression": "mathematical expression using column names",
    "description": "Human-readable description",
    "dependencies": ["list", "of", "required", "columns"],
    "default_value": 0.0,
    "condition": "optional condition (e.g., 'sog > 0')"
  }
}
```

### Expression Syntax

- Use column names directly (they'll be replaced with `df['col']`)
- Supports: `+`, `-`, `*`, `/`, `()`
- Can reference multiple columns
- Examples:
  - `goals / sog * 100`
  - `(goals + assists) / toi_minutes * 60`
  - `cf / (cf + ca) * 100`

### Conditions

Optional condition that must be true for formula to calculate. If false, uses `default_value`.

**Example:**
```json
{
  "condition": "sog > 0",
  "default_value": 0.0
}
```

---

## Using Formulas in Code

### Apply All Formulas

```python
from src.formulas.formula_applier import apply_player_stats_formulas

# Apply all formulas
df = apply_player_stats_formulas(df)
```

### Apply Specific Formulas

```python
# Apply specific formulas
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

# Apply multiple groups
df = apply_player_stats_formulas(
    df,
    formula_groups=['all_percentages', 'all_per_60']
)
```

---

## Available Formula Groups

| Group | Formulas |
|-------|----------|
| `all_percentages` | shooting_pct, pass_pct, fo_pct, cf_pct, ff_pct |
| `all_per_60` | goals_per_60, assists_per_60, points_per_60, sog_per_60 |
| `core_formulas` | Most commonly used formulas |

---

## Adding New Formulas

### Step 1: Add to `config/formulas.json`

```json
{
  "formulas": {
    "new_formula": {
      "type": "percentage",
      "expression": "numerator / denominator * 100",
      "description": "Description of what this calculates",
      "dependencies": ["numerator", "denominator"],
      "default_value": 0.0,
      "condition": "denominator > 0"
    }
  }
}
```

### Step 2: Add to Formula Groups (Optional)

```json
{
  "formula_groups": {
    "all_percentages": [
      "shooting_pct",
      "new_formula"
    ]
  }
}
```

### Step 3: Use in Code

```python
# Formula will be automatically available
df = apply_player_stats_formulas(df, formula_names=['new_formula'])
```

---

## Updating Existing Formulas

### Method 1: Edit JSON Config (Recommended)

1. Open `config/formulas.json`
2. Find the formula you want to update
3. Modify the `expression` field
4. Save file
5. Reload formulas (if using hot-reload) or restart ETL

**Example - Change shooting percentage calculation:**
```json
{
  "shooting_pct": {
    "expression": "goals / (sog + shots_missed) * 100",  // Changed formula
    ...
  }
}
```

### Method 2: Update in Code

```python
from src.formulas.formula_applier import update_formula

def new_shooting_pct(df):
    return (df['goals'] / df['sog'] * 100).where(df['sog'] > 0, 0.0)

update_formula('shooting_pct', new_shooting_pct, 'Updated shooting percentage')
```

---

## Formula Dependencies

Formulas automatically check for dependencies. If a required column is missing, the formula is skipped.

**Example:**
```json
{
  "shooting_pct": {
    "dependencies": ["goals", "sog"]
  }
}
```

If `goals` or `sog` columns don't exist, `shooting_pct` won't be calculated.

---

## Validation

### Check Formula Dependencies

```python
from src.formulas.config_loader import load_formulas_from_config
from pathlib import Path

registry = load_formulas_from_config(Path('config/formulas.json'))

# Check if formula can be applied
formula = registry.get_formula('shooting_pct')
print(f"Dependencies: {formula['dependencies']}")
```

### Test Formula

```python
import pandas as pd
from src.formulas.formula_applier import apply_player_stats_formulas

# Test data
test_df = pd.DataFrame({
    'goals': [5, 3, 0],
    'sog': [10, 8, 5]
})

# Apply formula
result = apply_player_stats_formulas(test_df, formula_names=['shooting_pct'])
print(result['shooting_pct'])  # Should show: 50.0, 37.5, 0.0
```

---

## Best Practices

### 1. Always Specify Dependencies

```json
{
  "dependencies": ["col1", "col2", "col3"]
}
```

### 2. Use Conditions for Division

```json
{
  "condition": "denominator > 0",
  "default_value": 0.0
}
```

### 3. Provide Default Values

```json
{
  "default_value": 0.0  // or null for optional formulas
}
```

### 4. Document Formulas

```json
{
  "description": "Clear description of what this formula calculates"
}
```

### 5. Group Related Formulas

```json
{
  "formula_groups": {
    "all_percentages": ["shooting_pct", "pass_pct", "fo_pct"]
  }
}
```

---

## Troubleshooting

### Formula Not Calculating

1. **Check dependencies:** Ensure all required columns exist
2. **Check condition:** Formula may be skipped if condition fails
3. **Check default value:** Formula may be returning default

### Formula Returns Wrong Values

1. **Verify expression:** Check math in expression
2. **Check data types:** Ensure columns are numeric
3. **Test with sample data:** Use test DataFrame

### Formula Not Found

1. **Check spelling:** Formula name must match exactly
2. **Check config file:** Ensure formula is in `config/formulas.json`
3. **Reload formulas:** May need to reload if updated

---

## Examples

### Example 1: Update Shooting Percentage

**Before:**
```json
{
  "shooting_pct": {
    "expression": "goals / sog * 100"
  }
}
```

**After (include missed shots):**
```json
{
  "shooting_pct": {
    "expression": "goals / (sog + shots_missed) * 100",
    "dependencies": ["goals", "sog", "shots_missed"]
  }
}
```

### Example 2: Add New Per-60 Rate

```json
{
  "xg_per_60": {
    "type": "rate",
    "expression": "xg_for / toi_minutes * 60",
    "description": "Expected goals per 60 minutes",
    "dependencies": ["xg_for", "toi_minutes"],
    "default_value": null,
    "condition": "toi_minutes > 0"
  }
}
```

### Example 3: Complex Formula

```json
{
  "pdo": {
    "type": "sum",
    "expression": "on_ice_sh_pct + on_ice_sv_pct",
    "description": "PDO (shooting % + save %)",
    "dependencies": ["on_ice_sh_pct", "on_ice_sv_pct"]
  }
}
```

---

## Integration with ETL

Formulas are automatically applied when building `fact_player_game_stats`:

```python
# In create_fact_player_game_stats()
from src.formulas.formula_applier import apply_player_stats_formulas

# After calculating base stats
df = pd.DataFrame(all_stats)

# Apply all formulas
df = apply_player_stats_formulas(df, formula_groups=['core_formulas'])
```

---

## Future Enhancements

- [ ] Formula versioning
- [ ] Formula validation UI
- [ ] Formula testing framework
- [ ] Formula change history
- [ ] Formula impact analysis

---

*Last updated: 2026-01-13*
