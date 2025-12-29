# BenchSight Package Creation Checklist

## CRITICAL: Read This Before Creating ANY Package

### Data Requirements
- [ ] All tables have proper PRIMARY KEYS (no nulls, no duplicates)
- [ ] All FOREIGN KEYS reference valid dimension values
- [ ] Keys use player_id NOT player_number (e.g., E_18969_1001_P100192)
- [ ] dim_position includes X (Extra Attacker)
- [ ] dim_stat_type exists with all microstats
- [ ] dim_shift_slot, dim_strength, dim_event_type exist
- [ ] No columns ending in _ (formula columns removed)
- [ ] dim_rinkcoordzones has no blank rows
- [ ] Excluded games (18965, 18993, 19032) NOT in tracking tables
- [ ] Valid games (18969, 18977, 18981, 18987, 18991) ARE in tracking tables

### Package MUST Include ALL Of These
```
benchsight/
├── etl.py                      # Main ETL script
├── upload.py                   # Supabase upload
├── HANDOFF.md                  # Current state documentation
├── README.md                   # Project overview
├── PACKAGE_CHECKLIST.md        # This file
├── pytest.ini
├── requirements.txt
│
├── data/
│   ├── BLB_Tables.xlsx         # Master data source
│   ├── output/                 # All clean CSVs (28+ tables)
│   └── games/                  # Game tracking folders (if present)
│
├── sql/
│   ├── create_tables.sql
│   └── drop_tables.sql
│
├── config/
│   └── supabase_schema.json
│
├── src/                        # ALL SOURCE CODE - DO NOT REMOVE
│   ├── main.py
│   ├── admin_portal.py
│   ├── calculate_stats.py      # Stats calculation
│   ├── tracker_backend.py
│   ├── database/
│   ├── analytics/
│   ├── ingestion/
│   ├── loading/
│   └── models/
│
├── tracker/                    # ALL TRACKER FILES
│   ├── tracker_v16.html
│   ├── tracker_v17.html
│   ├── tracker_v18.html
│   └── tracker_v19.html
│
├── dashboard/                  # ALL DASHBOARD FILES
│   ├── app.py
│   ├── dashboard.html
│   ├── dashboard_game.html
│   ├── dashboard_player.html
│   ├── dashboard_team.html
│   └── blb_portal.html
│
├── docs/                       # ALL DOCUMENTATION
│   ├── SCHEMA.md
│   ├── schema_diagram.html
│   ├── schema_er_diagram.png
│   ├── benchsight_stats_catalog_*.md
│   ├── benchsight_stats_catalog_*.csv
│   └── (all other docs)
│
├── tests/                      # ALL TEST FILES
│   ├── test_data_integrity.py
│   ├── test_*.py (all tests)
│   ├── conftest.py
│   └── __init__.py
│
├── powerbi/                    # Power BI files (if present)
│
└── logs/                       # ETL logs
```

### Validation Before Packaging
1. Run: `pytest tests/ -v` - ALL TESTS MUST PASS
2. Verify table count matches expected (28+ tables)
3. Verify row counts are reasonable
4. Spot check FK linkages (>95% for player_id)
5. Verify no duplicate PKs

### NEVER REMOVE
- Source code (src/)
- Tracker files (tracker/)
- Dashboard files (dashboard/)
- Documentation (docs/)
- Power BI files (powerbi/)
- Test files (tests/)
- Any file that "might be used later"

### ONLY REMOVE
- Obvious duplicates (same file, different name)
- Files explicitly in _archive/ folder
- Temporary/cache files (__pycache__, .pyc, etc.)

### After Creating Package
1. Unzip and verify all folders present
2. Run tests from unzipped location
3. Check file count matches expectation
4. Update HANDOFF.md with current state
