# Manual Fix for ETL Error: Rating Columns

## Error
```
KeyError: "['home_avg_rating', 'home_min_rating', 'home_max_rating', 'away_avg_rating', 'away_min_rating', 'away_max_rating', 'rating_differential'] not in index"
```

**File:** `src/core/base_etl.py`  
**Line:** 5099  
**Function:** `enhance_shift_players()`

## Quick Fix (Automated)

Run this command from your project root:

```bash
chmod +x apply_fix.sh
./apply_fix.sh
```

## Manual Fix

If the automated script doesn't work, follow these steps:

1. **Open the file:**
   ```bash
   nano src/core/base_etl.py
   # or use your preferred editor
   ```

2. **Go to line 5099** (or search for `shifts_for_merge[all_pull_cols]`)

3. **Find this line:**
   ```python
   sp = sp.merge(shifts_for_merge[all_pull_cols], left_on='shift_id', right_index=True, how='left')
   ```

4. **Replace it with:**
   ```python
   # Filter all_pull_cols to only existing columns
   existing_pull_cols = [col for col in all_pull_cols if col in shifts_for_merge.columns]
   sp = sp.merge(shifts_for_merge[existing_pull_cols], left_on='shift_id', right_index=True, how='left')
   ```

5. **Save the file**

6. **Run ETL again:**
   ```bash
   python3 run_etl.py
   ```

## What This Fix Does

The fix filters `all_pull_cols` to only include columns that actually exist in `shifts_for_merge`. This prevents the KeyError when rating columns are missing.

The rating columns (`home_avg_rating`, `away_avg_rating`, etc.) may not exist if:
- They haven't been created yet in the processing pipeline
- `shifts_for_merge` is a filtered DataFrame
- The columns were dropped or renamed earlier

By filtering to only existing columns, the merge will succeed even if some expected columns are missing.
