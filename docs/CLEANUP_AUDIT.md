# BenchSight Cleanup Audit

**Date:** 2026-01-10

This document identifies files that can be safely removed to reduce codebase complexity.

---

## Executive Summary

| Category | Used | Unused | Can Remove |
|----------|------|--------|------------|
| src/ Python files | 21 | 48 | ~30 |
| config/ files | 6 | 15 | ~10 |
| **Total savings** | | | **~40 files** |

---

## Files REQUIRED by ETL (Do NOT Remove)

These 21 files are actively imported by `run_etl.py`:

```
src/advanced/event_time_context.py
src/advanced/extended_tables.py
src/advanced/v11_enhancements.py
src/chains/shot_chain_builder.py
src/core/add_all_fkeys.py
src/core/base_etl.py
src/core/key_utils.py
src/core/safe_csv.py
src/core/table_writer.py
src/etl/post_etl_processor.py
src/models/dimensions.py
src/qa/build_qa_facts.py
src/tables/core_facts.py
src/tables/dimension_tables.py
src/tables/event_analytics.py
src/tables/remaining_facts.py
src/tables/shift_analytics.py
src/transformation/standardize_play_details.py
src/utils/key_parser.py
src/xy/xy_table_builder.py
src/xy/xy_tables.py
```

---

## Config Files REQUIRED

```
config/config.ini              # Main config
config/config_local.ini        # Local overrides (Supabase keys)
config/config_loader.py        # Config loading
config/excluded_games.txt      # Games to skip
config/IMMUTABLE_FACTS.json    # Business rules
config/VERSION.json            # Version info
```

---

## SAFE TO REMOVE (Unused)

### src/ - Dead Code (20 files)

These files are never imported and have no standalone functionality:

```
src/analytics/player_comparisons.py
src/core/modules/config.py
src/core/modules/logger.py
src/core/modules/table_writer.py
src/core/modules/utils.py
src/database/connection.py
src/database/table_operations.py
src/dimensions/schema_definition.py
src/ingestion/blb_loader.py
src/ingestion/game_loader.py
src/ingestion/xy_loader.py
src/loading/csv_exporter.py
src/transformation/data_transformer.py
src/transformation/league_stats_processor.py
src/transformation/play_detail_counter.py
src/transformation/transform_pipeline.py
src/utils/config_loader.py
src/utils/error_handler.py
src/utils/logger.py
src/utils/shared_lookups.py
src/utils/table_manager.py
```

### config/ - Unused Files (10 files)

```
config/DOC_REGISTRY.json
config/FILE_SIZES.json
config/GROUND_TRUTH.json
config/SCHEMA_SNAPSHOT.json
config/TABLE_METADATA.json
config/config_local.ini.template
config/schema_snapshots/           # entire folder
config/settings.py
config/supabase_config.py
config/supabase_schema.json
config/table_registry.json
config/table_registry.py
```

---

## KEEP BUT OPTIONAL (Standalone Tools)

These are useful utilities that can be run independently:

### Useful Standalone Tools (Keep)
```
src/norad/norad_verifier.py        # Verify against noradhockey.com
src/norad/roster_loader.py         # Load roster data
src/supabase/supabase_manager.py   # Manage Supabase
src/qa/validate_h2h_wowy.py        # Validate H2H tables
scripts/generate_data_dictionary.py # Generate docs
```

### Probably Unnecessary (Safe to Remove)
```
src/advanced/archive/              # Old code, archived
src/advanced/create_additional_tables.py  # Superseded
src/advanced/enhance_all_stats.py         # Superseded
src/advanced/final_stats_enhancement.py   # Superseded
src/core/combine_tracking.py              # Superseded by base_etl
src/core/populate_all_fks_v2.py           # Superseded by add_all_fkeys
src/dimensions/generate_schema.py         # One-time use
src/dimensions/normalize_terminology.py   # One-time use
src/enhance_all_stats.py                  # Duplicate
src/stats/calculate_stats.py              # Superseded
src/stats/stats_builder.py                # Superseded
src/tables/build_missing_tables.py        # Superseded
src/xy/create_dim_rink_zone.py            # Superseded
```

---

## Recommended Cleanup Actions

### Phase 1: Remove Dead Code (Safe)
Remove the 20 unused files in src/ that have no imports and no standalone functionality.

### Phase 2: Remove Unused Config (Safe)
Remove the 10 unused config files.

### Phase 3: Archive Old Tools (Optional)
Move superseded standalone tools to `archive/` folder.

### Phase 4: Remove Empty Folders
After cleanup, remove empty `__init__.py` files and folders.

---

## After Cleanup

**Before:**
- 90 Python files in src/
- 21 files in config/

**After:**
- ~30 Python files in src/
- ~6 files in config/

**Benefits:**
- Clearer codebase
- Easier maintenance
- Less confusion about what's used
- Faster navigation

---

## Cleanup Command (DO NOT RUN YET)

```bash
# This is for reference only - DO NOT RUN without review
# Phase 1: Remove dead code
rm src/analytics/player_comparisons.py
rm -rf src/core/modules/
rm -rf src/database/
rm src/dimensions/schema_definition.py
rm src/ingestion/blb_loader.py
rm src/ingestion/game_loader.py
rm src/ingestion/xy_loader.py
rm src/loading/csv_exporter.py
rm src/transformation/data_transformer.py
rm src/transformation/league_stats_processor.py
rm src/transformation/play_detail_counter.py
rm src/transformation/transform_pipeline.py
rm src/utils/config_loader.py
rm src/utils/error_handler.py
rm src/utils/logger.py
rm src/utils/shared_lookups.py
rm src/utils/table_manager.py

# Phase 2: Remove unused config
rm config/DOC_REGISTRY.json
rm config/FILE_SIZES.json
rm config/GROUND_TRUTH.json
rm config/SCHEMA_SNAPSHOT.json
rm config/TABLE_METADATA.json
rm config/config_local.ini.template
rm -rf config/schema_snapshots/
rm config/settings.py
rm config/supabase_config.py
rm config/supabase_schema.json
rm config/table_registry.json
rm config/table_registry.py
```

---

*This audit was generated automatically. Review before removing any files.*
