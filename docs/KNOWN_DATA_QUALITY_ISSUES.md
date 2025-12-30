# BenchSight Known Data Quality Issues

This document catalogs known data quality issues in the BenchSight dataset. These issues are inherited from the source tracking data and have been validated as consistent between original and processed outputs.

## Summary

| Issue | Count | Impact | Resolution |
|-------|-------|--------|------------|
| Events without shift match | 58 | Low | `shift_key` contains 'Snan' |
| Events with NULL period | 2 | Low | Edge cases in tracking |
| Shifts without player attribution | 283 | Medium | Partial game tracking |
| Shifts with 0 team strength | 9 | Low | Partial game tracking |
| Game coverage gap | 3 games | Medium | Events: 4 games, Shifts: 7 games |

## Detailed Issues

### 1. Events Without Matching Shifts (58 events)

**Description:** 58 events have `shift_key` values containing 'Snan' (e.g., '18969_Snan'), indicating these events couldn't be matched to a specific shift during ETL processing.

**Affected Tables:** `fact_events`

**Root Cause:** Events recorded during transition periods or tracking gaps where shift boundaries weren't clearly defined.

**Workaround:** Filter these events when joining to `fact_shifts`:
```sql
SELECT * FROM fact_events 
WHERE shift_key NOT LIKE '%Snan%'
```

### 2. Events with NULL Period (2 events)

**Description:** 2 events have NULL values in the `period` column.

**Affected Tables:** `fact_events`

**Root Cause:** Edge cases in source tracking data.

**Workaround:** Exclude or handle NULL periods:
```sql
SELECT * FROM fact_events WHERE period IS NOT NULL
```

### 3. Shifts Without Player Attribution (283 shifts)

**Description:** 283 shifts in `fact_shifts` don't have corresponding records in `fact_shifts_player`.

**Affected Tables:** `fact_shifts`, `fact_shifts_player`

**Root Cause:** These shifts come from games with partial tracking (shifts recorded but not individual player assignments).

**Games Affected:** 18965, 18991, 19032 (shift-only tracking)

**Workaround:** Use only fully-tracked games when requiring player-level shift data:
```sql
SELECT * FROM fact_shifts s
WHERE EXISTS (SELECT 1 FROM fact_shifts_player sp WHERE sp.shift_key = s.shift_key)
```

### 4. Shifts with Zero Team Strength (9 shifts)

**Description:** 9 shifts have `home_team_strength` or `away_team_strength` = 0.

**Affected Tables:** `fact_shifts`

**Root Cause:** Partial game tracking where strength wasn't recorded.

**Workaround:** Filter to valid strength values:
```sql
SELECT * FROM fact_shifts 
WHERE home_team_strength > 0 AND away_team_strength > 0
```

### 5. Game Coverage Gap

**Description:** Different tables have different game coverage:
- `fact_events`: 4 games (18969, 18977, 18981, 18987)
- `fact_shifts`: 7 games (adds 18965, 18991, 19032)
- `fact_player_game_stats`: 4 games (derived from events)

**Root Cause:** Some games have shift tracking but not full event tracking.

**Fully Tracked Games:** 18969, 18977, 18981, 18987
**Shift-Only Games:** 18965, 18991, 19032

**Workaround:** For complete analytics, use only fully tracked games:
```sql
SELECT DISTINCT game_id FROM fact_events
-- Returns: 18969, 18977, 18981, 18987
```

## Validation Status

All issues have been verified to exist in both:
1. Original uploaded data (`data.zip`)
2. Processed ETL output (`data/output/`)

The data is **not corrupted** - these are limitations in the source tracking data.

## Test Coverage

These issues are documented in:
- `tests/test_comprehensive_integrity.py` - Calibrated to known tolerances
- Test suite passes with 326 tests accounting for these issues

## Recommendations

1. **For Dashboard Users:** Use fully-tracked games (18969, 18977, 18981, 18987) for complete statistics.

2. **For Analysts:** Be aware of NULL handling when aggregating across all games.

3. **For Developers:** When adding new games, validate tracking completeness before loading.

4. **For ETL:** Consider adding a `tracking_completeness` column to flag partial vs full tracking.

---
*Last Updated: 2025-12-30*
*Validated against: 96 CSV files, 24,654 total rows*
