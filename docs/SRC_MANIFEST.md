# BenchSight Source Code Manifest

**Version:** 22.1  
**Date:** 2026-01-10  
**Total Active Files:** 34 Python modules

---

## Core ETL Pipeline (21 files)

These files are directly imported by `run_etl.py`:

### src/core/ (6 files)
| File | Purpose |
|------|---------|
| base_etl.py | Main ETL engine - loads BLB, tracking, creates derived tables |
| add_all_fkeys.py | Adds foreign keys to all tables |
| key_utils.py | Key generation utilities |
| safe_csv.py | Safe CSV reading/writing |
| safe_sql.py | Safe SQL operations |
| table_writer.py | Table output management |

### src/tables/ (5 files)
| File | Purpose |
|------|---------|
| dimension_tables.py | Creates static dimension tables |
| core_facts.py | Player, team, goalie game stats |
| shift_analytics.py | H2H, WOWY, line combinations |
| remaining_facts.py | Additional fact tables |
| event_analytics.py | Scoring chances, shot danger, rush events |

### src/advanced/ (3 files)
| File | Purpose |
|------|---------|
| event_time_context.py | Time-based event context |
| extended_tables.py | Extended analytics tables |
| v11_enhancements.py | V11 feature enhancements |

### src/chains/ (1 file)
| File | Purpose |
|------|---------|
| shot_chain_builder.py | Zone entry → shot chain analysis |

### src/xy/ (2 files)
| File | Purpose |
|------|---------|
| xy_table_builder.py | XY coordinate tables |
| xy_tables.py | Spatial analytics support |

### src/qa/ (1 file used by ETL)
| File | Purpose |
|------|---------|
| build_qa_facts.py | QA validation tables |

### Other ETL Support (3 files)
| File | Purpose |
|------|---------|
| src/etl/post_etl_processor.py | Post-processing |
| src/transformation/standardize_play_details.py | Play detail standardization |
| src/utils/key_parser.py | Key parsing utilities |
| src/models/dimensions.py | Dimension model definitions |

---

## Standalone Tools (13 files)

Not part of ETL but useful utilities:

### src/norad/ (4 files)
| File | Purpose |
|------|---------|
| norad_verifier.py | Verify data against noradhockey.com |
| norad_schedule.py | Fetch schedule from NORAD |
| roster_loader.py | Load roster data |
| extract_roster.py | Extract roster from pages |

### src/supabase/ (3 files)
| File | Purpose |
|------|---------|
| supabase_manager.py | Manage Supabase database |
| add_game.py | Add game to database |
| add_video.py | Add video to database |

### src/qa/ (1 file)
| File | Purpose |
|------|---------|
| validate_h2h_wowy.py | Validate H2H/WOWY tables |

### Other Tools (5 files)
| File | Purpose |
|------|---------|
| src/data_quality/cleaner.py | Data cleaning utilities |
| src/ingestion/supabase_source.py | Load from Supabase |
| src/models/master_dims.py | Master dimension definitions |
| src/utils/logging_system.py | Logging configuration |
| src/core/safe_sql.py | SQL safety utilities |

---

## Config Files (6 active)

| File | Purpose |
|------|---------|
| config/config.ini | Main configuration |
| config/config_local.ini | Local overrides (Supabase keys) |
| config/config_loader.py | Configuration loading |
| config/excluded_games.txt | Games to skip |
| config/IMMUTABLE_FACTS.json | Business rules |
| config/VERSION.json | Version tracking |

---

## Archived Files

Files moved to `archive/` for reference but not used:

- `archive/unused_src/` - 38 Python files
- `archive/unused_config/` - 12 config files
- `archive/deprecated_scripts/` - Old ETL scripts
- `archive/deprecated_docs/` - Old documentation

---

## Quick Reference

```bash
# Run ETL
python run_etl.py --wipe

# Upload to Supabase
python upload.py

# Validate
python validate.py

# Verify against NORAD
python -m src.norad.norad_verifier
```
