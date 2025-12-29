# BenchSight

Beer league hockey analytics platform tracking 200+ statistics.

## Quick Start

```bash
# 1. Install dependencies
pip3 install pandas requests pytest openpyxl --break-system-packages

# 2. Run tests (REQUIRED before upload)
pytest tests/ -v

# 3. Upload to Supabase
python PRODUCTION_ETL.py --dry-run  # Preview
python PRODUCTION_ETL.py            # Upload
```

## Project Structure

```
benchsight/
├── PRODUCTION_ETL.py          # Main upload script
├── UPLOAD_GUIDE.md            # Upload instructions
├── config/
│   └── supabase_schema.json   # Schema source of truth (50 tables)
├── data/
│   ├── BLB_Tables.xlsx        # Master Excel workbook
│   ├── raw/                   # Raw tracking files
│   ├── clean/                 # Cleaned CSVs
│   └── output/                # Upload-ready CSVs
├── docs/
│   ├── MASTER_HANDOFF.md      # Primary handoff document
│   ├── CHANGELOG.md           # Version history
│   └── ...
├── html/                      # Dashboard previews
├── tracker/                   # Game tracker app (v16-v19)
├── src/                       # Source code
├── sql/                       # Database schemas
├── tests/                     # Test suites
└── powerbi/                   # Power BI documentation
```

## Key Files

| File | Purpose |
|------|---------|
| `PRODUCTION_ETL.py` | Upload CSVs to Supabase |
| `config/supabase_schema.json` | Defines valid columns per table |
| `docs/MASTER_HANDOFF.md` | Complete project documentation |
| `tests/test_schema_compliance.py` | Schema validation tests |
| `tests/test_delivery_checklist.py` | Delivery verification |

## Test Suites

```bash
# All tests (82 total)
pytest tests/ -v

# Schema compliance only (25 tests)
pytest tests/test_schema_compliance.py -v

# ETL data cleaning (29 tests)  
pytest tests/test_etl_upload.py -v

# Delivery checklist (28 tests)
pytest tests/test_delivery_checklist.py -v
```

## Documentation

- [Master Handoff](docs/MASTER_HANDOFF.md) - Complete project guide
- [Upload Guide](UPLOAD_GUIDE.md) - Step-by-step upload
- [Changelog](docs/CHANGELOG.md) - Version history
- [Data Dictionary](docs/DATA_DICTIONARY.md) - Column definitions

## Version

v2.1.0 - December 28, 2025
