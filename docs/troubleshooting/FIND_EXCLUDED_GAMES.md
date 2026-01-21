# Where Games Are Excluded

## Two Places Games Get Excluded:

### 1. Config File (Manual Exclusion)
**File:** `config/excluded_games.txt`

Currently has 3 games:
- 18965
- 18993  
- 19032

**To remove exclusions:** Delete or comment out the game IDs in this file.

### 2. Auto-Exclusion (Validation)
**File:** `src/core/base_etl.py`  
**Function:** `discover_games()` (lines 72-149)

Games are **auto-excluded** if they fail validation:
- ❌ No tracking file found (or only temp files like `~$18965_tracking.xlsx`)
- ❌ Missing 'events' sheet
- ❌ Missing `event_index` or `tracking_event_index` column
- ❌ Less than 1 row of data (reduced from 5)
- ❌ Any error reading the Excel file

## Current Status

**Valid games (4):** 18969, 18977, 18981, 18987  
**Excluded games (14):** 18955, 18959, 18965, 18991, 18993, 18998, 19007, 19009, 19014, 19020, 19026, 19032, 19036, 19038

## Why Games Are Being Excluded

Based on your file list, many games have tracking files but are being auto-excluded because:
1. **Temp files** - Games like 18965 and 18991 have `~$` temp files (Excel lock files) that are being picked up
2. **Validation failures** - Games might be missing:
   - 'events' sheet
   - event_index column
   - Enough rows of data
   - Or have file read errors

## Fixes Applied

1. ✅ **Filter out temp files** - Now skips `~$` files
2. ✅ **Reduced row requirement** - Changed from 5 rows to 1 row minimum
3. ✅ **Added logging** - Now shows WHY each game is excluded

## To See Why Games Are Excluded

Run ETL and check the logs - it will now show:
```
Auto-excluding 18955: missing event_index column
Auto-excluding 18991: error reading file - ...
```

## To Force Include All Games

If you want to bypass validation entirely, you can modify `discover_games()` to be more lenient or add a flag to skip validation.
