# Data Validation & Verification Guide

**Version:** 1.0  
**Date:** December 30, 2025

---

## How to Verify Supabase Loaded 100% Accurately

### Quick Verification Checklist

```
□ 1. Row counts match CSV files
□ 2. All 96 tables exist
□ 3. No loading errors in logs
□ 4. Sample data spot checks pass
□ 5. Goals match noradhockey.com
□ 6. Referential integrity tests pass
□ 7. Primary key uniqueness verified
```

---

## Step 1: Verify Row Counts

### Run This SQL in Supabase

```sql
-- Get row counts for all tables
SELECT 
    schemaname,
    relname as table_name,
    n_live_tup as row_count
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY relname;
```

### Compare to Expected Counts

| Table | Expected Rows | Check |
|-------|---------------|-------|
| dim_player | 337 | □ |
| dim_team | 26 | □ |
| dim_schedule | 562 | □ |
| fact_events | 5,833 | □ |
| fact_events_player | 11,635 | □ |
| fact_shifts | 672 | □ |
| fact_shifts_player | 4,626 | □ |
| fact_player_game_stats | 107 | □ |
| fact_team_game_stats | 8 | □ |
| fact_h2h | 684 | □ |
| fact_wowy | 641 | □ |
| fact_line_combos | 332 | □ |
| fact_player_boxscore_all | 14,473 | □ |
| fact_gameroster | 14,471 | □ |

### Automated Row Count Check (Python)

```python
import pandas as pd
from supabase import create_client

# Load expected counts from CSVs
expected = {}
for csv_file in Path('data/output').glob('*.csv'):
    table = csv_file.stem
    df = pd.read_csv(csv_file)
    expected[table] = len(df)

# Get actual counts from Supabase
actual = {}
for table in expected.keys():
    response = supabase.table(table).select('*', count='exact').execute()
    actual[table] = response.count

# Compare
mismatches = []
for table in expected:
    if expected[table] != actual.get(table, 0):
        mismatches.append({
            'table': table,
            'expected': expected[table],
            'actual': actual.get(table, 0),
            'diff': expected[table] - actual.get(table, 0)
        })

if mismatches:
    print("⚠️ MISMATCHES FOUND:")
    for m in mismatches:
        print(f"  {m['table']}: expected {m['expected']}, got {m['actual']}")
else:
    print("✅ All row counts match!")
```

---

## Step 2: Verify All Tables Exist

### SQL Check

```sql
-- Count tables (should be 96 + logging tables)
SELECT COUNT(*) as table_count
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_type = 'BASE TABLE';

-- List all tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;
```

### Expected: 96 data tables + 5 logging tables = 101+ tables

---

## Step 3: Check Loading Logs

### File Logs
```bash
# Check latest log file
cat logs/$(ls -t logs/ | head -1)/run.log | grep -E "ERROR|FAILED|SUCCESS"

# Count errors
grep -c "ERROR" logs/*/run.log
```

### Supabase Logs (if logging enabled)
```sql
-- Check recent ETL runs
SELECT * FROM log_etl_runs 
ORDER BY started_at DESC 
LIMIT 5;

-- Check for failed tables
SELECT * FROM log_etl_tables 
WHERE status = 'failed'
ORDER BY created_at DESC;

-- Check errors
SELECT * FROM log_errors 
WHERE resolved = false;
```

---

## Step 4: Sample Data Spot Checks

### Check Primary Keys Are Unique

```sql
-- Events should have unique keys
SELECT event_key, COUNT(*) 
FROM fact_events 
GROUP BY event_key 
HAVING COUNT(*) > 1;
-- Should return 0 rows (except known duplicate EV1896901594)

-- Shifts should have unique keys
SELECT shift_key, COUNT(*) 
FROM fact_shifts 
GROUP BY shift_key 
HAVING COUNT(*) > 1;
-- Should return 0 rows

-- Players should have unique IDs
SELECT player_id, COUNT(*) 
FROM dim_player 
GROUP BY player_id 
HAVING COUNT(*) > 1;
-- Should return 0 rows
```

### Check Sample Values Match CSV

```sql
-- Compare a specific player
SELECT * FROM dim_player WHERE player_id = 'P100023';

-- Compare a specific event
SELECT * FROM fact_events WHERE event_key = 'EV1896900001';

-- Compare a specific shift
SELECT * FROM fact_shifts WHERE shift_key = '18969_1';
```

---

## Step 5: Validate Against Official Stats (noradhockey.com)

### Goals Validation

```sql
-- Get goals per team per game
SELECT 
    game_id,
    CASE WHEN team_venue = 'Home' THEN 'Home' ELSE 'Away' END as venue,
    COUNT(*) as goals
FROM fact_events
WHERE event_type = 'Goal'
GROUP BY game_id, team_venue
ORDER BY game_id;
```

### Compare to Official

| Game | Official Home | Calculated Home | Official Away | Calculated Away | Match |
|------|---------------|-----------------|---------------|-----------------|-------|
| 18969 | ? | ? | ? | ? | □ |
| 18977 | ? | ? | ? | ? | □ |
| 18981 | ? | ? | ? | ? | □ |
| 18987 | ? | ? | ? | ? | □ |

### Player Points Validation

```sql
-- Top scorers for a game
SELECT 
    player_name,
    goals,
    assists,
    points
FROM fact_player_game_stats
WHERE game_id = '18969'
ORDER BY points DESC
LIMIT 10;
```

---

## Step 6: Referential Integrity Tests

### Run the Test Suite

```bash
# Run all integrity tests
python -m pytest tests/test_fk_relationships.py -v

# Run comprehensive integrity
python -m pytest tests/test_comprehensive_integrity.py -v
```

### Manual FK Checks

```sql
-- Events should reference valid shifts
SELECT COUNT(*) as orphan_events
FROM fact_events e
LEFT JOIN fact_shifts s ON e.shift_key = s.shift_key
WHERE s.shift_key IS NULL 
  AND e.shift_key IS NOT NULL
  AND e.shift_key NOT LIKE '%nan%';
-- Acceptable: 0 or small number

-- Event players should reference valid events
SELECT COUNT(*) as orphan_event_players
FROM fact_events_player ep
LEFT JOIN fact_events e ON ep.event_key = e.event_key
WHERE e.event_key IS NULL;
-- Should be 0

-- Players should exist in dim_player
SELECT COUNT(*) as orphan_players
FROM fact_player_game_stats pgs
LEFT JOIN dim_player p ON pgs.player_id = p.player_id
WHERE p.player_id IS NULL;
-- Should be 0
```

---

## Step 7: Data Quality Checks

### Check for NULL Values in Required Fields

```sql
-- Events without type
SELECT COUNT(*) FROM fact_events WHERE event_type IS NULL;

-- Shifts without game
SELECT COUNT(*) FROM fact_shifts WHERE game_id IS NULL;

-- Players without name
SELECT COUNT(*) FROM dim_player WHERE player_full_name IS NULL;
```

### Check for Invalid Values

```sql
-- Events with invalid period
SELECT COUNT(*) FROM fact_events 
WHERE period NOT IN (1, 2, 3, 4, 5) AND period IS NOT NULL;

-- Negative durations
SELECT COUNT(*) FROM fact_shifts WHERE shift_duration < 0;

-- Invalid percentages
SELECT COUNT(*) FROM fact_wowy WHERE cf_pct_together > 100 OR cf_pct_together < 0;
```

---

## Known Data Issues (Expected)

These are documented issues that are acceptable:

| Issue | Count | Impact | Notes |
|-------|-------|--------|-------|
| Events without shift match | 58 | Minor | shift_key contains 'nan' |
| Events with NULL period | 2 | Minor | Filter in queries |
| Shifts without player attribution | 283 | Minor | Some games shift-only |
| Duplicate event_key | 1 | Minor | EV1896901594, use UPSERT |

---

## Automated Validation Script

```python
#!/usr/bin/env python3
"""
Comprehensive data validation for Supabase
Run after every load to verify accuracy
"""

import pandas as pd
from pathlib import Path
from supabase import create_client
import json

def validate_all():
    results = {
        'row_counts': validate_row_counts(),
        'primary_keys': validate_primary_keys(),
        'foreign_keys': validate_foreign_keys(),
        'data_quality': validate_data_quality(),
        'business_rules': validate_business_rules()
    }
    
    # Summary
    total_checks = sum(r['total'] for r in results.values())
    passed_checks = sum(r['passed'] for r in results.values())
    
    print(f"\n{'='*50}")
    print(f"VALIDATION SUMMARY")
    print(f"{'='*50}")
    print(f"Total Checks: {total_checks}")
    print(f"Passed: {passed_checks}")
    print(f"Failed: {total_checks - passed_checks}")
    print(f"Pass Rate: {passed_checks/total_checks*100:.1f}%")
    
    if passed_checks == total_checks:
        print("\n✅ ALL VALIDATIONS PASSED!")
    else:
        print("\n⚠️ SOME VALIDATIONS FAILED - Review above")
    
    return results

def validate_row_counts():
    """Compare CSV row counts to Supabase"""
    print("\n--- Row Count Validation ---")
    passed = 0
    failed = 0
    
    for csv_file in Path('data/output').glob('*.csv'):
        table = csv_file.stem
        expected = len(pd.read_csv(csv_file))
        
        try:
            response = supabase.table(table).select('*', count='exact').limit(1).execute()
            actual = response.count
        except:
            actual = 0
        
        if expected == actual:
            print(f"  ✓ {table}: {actual} rows")
            passed += 1
        else:
            print(f"  ✗ {table}: expected {expected}, got {actual}")
            failed += 1
    
    return {'total': passed + failed, 'passed': passed}

def validate_primary_keys():
    """Check primary key uniqueness"""
    print("\n--- Primary Key Validation ---")
    checks = [
        ('fact_events', 'event_key'),
        ('fact_shifts', 'shift_key'),
        ('dim_player', 'player_id'),
        ('dim_team', 'team_id'),
    ]
    
    passed = 0
    for table, pk in checks:
        # Check for duplicates
        response = supabase.rpc('check_duplicates', {
            'table_name': table, 
            'column_name': pk
        }).execute()
        
        if response.data == 0:
            print(f"  ✓ {table}.{pk} is unique")
            passed += 1
        else:
            print(f"  ✗ {table}.{pk} has {response.data} duplicates")
    
    return {'total': len(checks), 'passed': passed}

if __name__ == '__main__':
    validate_all()
```

---

## Verification Checklist Summary

### Before Go-Live

```
LOAD VERIFICATION
□ All 96 tables created
□ Row counts match 100%
□ No ERROR entries in logs
□ Primary keys unique
□ Foreign keys valid (>95%)

DATA ACCURACY  
□ Goals match noradhockey.com
□ Player points match
□ Team stats match
□ Sample spot checks pass

DATA QUALITY
□ No unexpected NULLs
□ No invalid values
□ No orphan records
□ Test suite passes (326 tests)

SIGN-OFF
□ Verified by: _____________
□ Date: _____________
□ Version: _____________
```

---

## Troubleshooting Load Issues

### Issue: Row count mismatch

**Cause:** Duplicate key caused skip
**Fix:** 
```bash
python scripts/load_all_tables.py --table TABLE_NAME --upsert
```

### Issue: Table missing

**Cause:** Schema not deployed
**Fix:** Run `sql/05_FINAL_COMPLETE_SCHEMA.sql` in Supabase

### Issue: Foreign key violation

**Cause:** Dimension not loaded before fact
**Fix:** Load dimensions first, then facts

### Issue: Connection timeout

**Cause:** Large batch size or slow network
**Fix:** Reduce batch size in config
```ini
[loader]
batch_size = 100  # Reduce from 500
```
