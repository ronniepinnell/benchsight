# Fix for ETL Error: Rating Columns Not in Index

## Error
```
KeyError: "['home_avg_rating', 'home_min_rating', 'home_max_rating', 'away_avg_rating', 'away_min_rating', 'away_max_rating', 'rating_differential'] not in index"
```

**Location:** `src/core/base_etl.py`, line 5099 in `enhance_shift_players()`

## Problem

The code tries to merge columns from `shifts_for_merge` that don't exist:
```python
sp = sp.merge(shifts_for_merge[all_pull_cols], left_on='shift_id', right_index=True, how='left')
```

The `all_pull_cols` list includes rating columns that haven't been created yet or don't exist in `shifts_for_merge`.

## Solution

Filter `all_pull_cols` to only include columns that actually exist in `shifts_for_merge` before the merge.

### Option 1: Filter before merge (Recommended)

Find line 5099 (or search for `shifts_for_merge[all_pull_cols]`) and replace:

**Before:**
```python
sp = sp.merge(shifts_for_merge[all_pull_cols], left_on='shift_id', right_index=True, how='left')
```

**After:**
```python
# Filter all_pull_cols to only existing columns
existing_pull_cols = [col for col in all_pull_cols if col in shifts_for_merge.columns]
sp = sp.merge(shifts_for_merge[existing_pull_cols], left_on='shift_id', right_index=True, how='left')
```

### Option 2: Inline filter

Replace:
```python
sp = sp.merge(shifts_for_merge[all_pull_cols], ...)
```

With:
```python
sp = sp.merge(shifts_for_merge[[col for col in all_pull_cols if col in shifts_for_merge.columns]], ...)
```

## Why This Happens

The rating columns (`home_avg_rating`, `away_avg_rating`, etc.) are created in `enhance_shift_tables()` but `enhance_shift_players()` may be called before those columns exist, or `shifts_for_merge` may be a filtered/copied DataFrame that doesn't include all columns.

## Verification

After applying the fix, the ETL should continue past this error. The merge will only include columns that actually exist, preventing the KeyError.
