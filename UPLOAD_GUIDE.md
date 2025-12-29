# BenchSight Upload Guide

## Pre-Upload Checklist

### 1. Run Tests (REQUIRED)
```bash
pytest tests/test_schema_compliance.py -v
```
All 25 tests must pass before uploading.

### 2. Validate Data (Recommended)
```bash
python PRODUCTION_ETL.py --dry-run
```
Shows what would be uploaded without actually uploading.

### 3. Upload
```bash
python PRODUCTION_ETL.py
```

## Single Table Upload
```bash
python PRODUCTION_ETL.py --table dim_player
```

## Key Files

| File | Purpose |
|------|---------|
| `config/supabase_schema.json` | Source of truth for Supabase columns |
| `PRODUCTION_ETL.py` | Main upload script |
| `tests/test_schema_compliance.py` | Schema validation tests |
| `data/output/*.csv` | Data files to upload |

## If Schema Changes in Supabase

1. Run in Supabase SQL Editor:
```sql
SELECT table_name, column_name 
FROM information_schema.columns 
WHERE table_schema = 'public' 
ORDER BY table_name, ordinal_position;
```

2. Export as JSON and save to `config/supabase_schema.json`

3. Re-run tests to verify CSVs still match

## Troubleshooting

### "extra columns" error
Your CSV has columns not in Supabase schema. Either:
- Remove the column from CSV
- Add the column to Supabase

### "Column not found" error
The column exists in CSV but has wrong name. Check case sensitivity:
- Supabase: `Type` (capital T)
- CSV might have: `type` (lowercase)

### Tests fail after adding new data
1. Check `config/supabase_schema.json` matches current Supabase
2. Ensure new CSVs don't add extra columns
3. Run `pytest -v` to see specific failures
