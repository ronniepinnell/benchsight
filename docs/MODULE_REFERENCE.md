# Module Reference v13.18

**Last Updated:** January 7, 2026

---

## Entry Point

| File | Purpose |
|------|---------|
| `run_etl.py` | Main ETL runner - `python run_etl.py` |

---

## src/core/ (Core ETL Logic)

### base_etl.py (3159 lines)
The main ETL processing file.

| Line | Function | Purpose |
|------|----------|---------|
| 57 | `discover_games()` | Find games in data/raw/games/ |
| 124 | `save_excluded_games()` | Write excluded games to config |
| 142 | `class ETLLogger` | Logging with categories |
| 193 | `drop_underscore_columns()` | Remove _ prefix columns |
| 200 | `drop_index_and_unnamed()` | Clean DataFrame |
| 218 | `correct_venue_from_schedule()` | Fix venue from schedule data |
| 303 | `validate_key()` | Check key uniqueness |
| 321 | `save_table()` | Write CSV to data/output/ |
| 337 | `enhance_gameroster()` | Add season/schedule to roster |
| 420 | `load_blb_tables()` | Load BLB Excel sheets |
| 498 | `build_player_lookup()` | Create player_id lookup |
| 541 | `load_tracking_data()` | Load tracking spreadsheets |
| 738 | `link_player_ids()` | Map names to player_id |
| 772 | `create_derived_tables()` | Build fact tables from tracking |
| 942 | `create_reference_tables()` | Build dimension tables |
| 1115 | `_create_dim_event_detail_2()` | Secondary event details |
| 1146 | `_create_dim_zone_entry_type()` | Zone entry types |
| 1166 | `_create_dim_zone_exit_type()` | Zone exit types |
| 1186 | `_create_dim_stoppage_type()` | Stoppage types |
| 1207 | `_create_dim_giveaway_type()` | Giveaway types |
| 1228 | `_create_dim_takeaway_type()` | Takeaway types |
| 1259 | `_create_dim_play_detail()` | Play detail dimension |
| 1326 | `_create_dim_play_detail_2()` | Secondary play details |
| 1375 | `validate_all()` | Run all validations |
| 1524 | `main()` | Main entry point |
| 1613 | `enhance_event_tables()` | Add FKs to events/tracking |

### key_utils.py (836 lines)
Key generation and validation.

| Function | Purpose |
|----------|---------|
| `generate_player_id()` | Create P_LASTNAME_N format |
| `generate_game_id()` | Create game identifiers |
| `generate_event_id()` | Create event identifiers |
| `validate_foreign_keys()` | Check FK integrity |

### add_all_fkeys.py (864 lines)
Foreign key population.

| Function | Purpose |
|----------|---------|
| `populate_all_fks()` | Add all FK columns to tables |
| `add_period_id()` | Map period to dim_period |
| `add_event_type_id()` | Map event_type to dim |
| `add_venue_id()` | Map venue to dim_venue |

### populate_all_fks_v2.py (884 lines)
Updated FK population.

### safe_csv.py (330 lines)
Safe CSV reading/writing with dtype handling.

### safe_sql.py (237 lines)
SQL generation utilities.

### combine_tracking.py (225 lines)
Merge multiple tracking sheets.

---

## src/advanced/ (Advanced Analytics)

### extended_tables.py (Lines: ~400)
Creates additional fact tables:
- fact_player_game_position
- fact_game_status
- fact_suspicious_stats

### v11_enhancements.py (~350 lines)
Session 11 table improvements.

### enhance_all_stats.py (~300 lines)
Statistical enhancements.

### final_stats_enhancement.py (~250 lines)
Final stat calculations.

### create_additional_tables.py (~300 lines)
Extra derived tables.

### event_time_context.py (~200 lines)
Time-based event context.

---

## src/qa/ (Quality Assurance)

### build_qa_facts.py (~300 lines)
Creates QA tables:
- qa_goal_accuracy
- qa_data_completeness
- qa_scorer_comparison

### validate_h2h_wowy.py (~200 lines)
Validates H2H and WOWY tables.

---

## src/transformation/

### transform_pipeline.py (~400 lines)
Main transformation orchestration.

### data_transformer.py (~350 lines)
Data transformation utilities.

### standardize_play_details.py (~200 lines)
Normalize play detail naming.

### play_detail_counter.py (~150 lines)
Count play detail occurrences.

### league_stats_processor.py (~200 lines)
League-level statistics.

---

## src/ingestion/

### game_loader.py (~300 lines)
Load game data from raw files.

### blb_loader.py (~200 lines)
Load BLB Excel workbook.

### xy_loader.py (~250 lines)
Load XY coordinate data.

### supabase_source.py (~200 lines)
Load from Supabase.

---

## src/stats/

### stats_builder.py (~300 lines)
Build player/team statistics.

### calculate_stats.py (~250 lines)
Statistical calculations.

---

## src/xy/

### xy_tables.py (~250 lines)
XY coordinate table creation.

### create_dim_rink_zone.py (~200 lines)
Rink zone dimension.

---

## src/norad/

### norad_verifier.py (~200 lines)
Verify against noradhockey.com.

### norad_schedule.py (~150 lines)
Load NORAD schedule.

### roster_loader.py (~150 lines)
Load roster data.

### extract_roster.py (~150 lines)
Extract roster from game data.

---

## scripts/validation/

| File | Purpose |
|------|---------|
| `etl_validation.py` | ETL output validation |
| `qa_all_tables.py` | QA all tables |
| `validate_against_ground_truth.py` | Check vs noradhockey.com |
| `validate_stats.py` | Validate statistics |

---

## scripts/utilities/

| File | Purpose |
|------|---------|
| `md_to_html.py` | Convert MD to HTML |
| `verify_delivery.py` | Verify package contents |
| `generate_data_dictionary_complete.py` | Generate data dictionary |

---

## Working Tables Created by ETL (59)

### Dimensions (34)
- dim_assist_type
- dim_danger_level
- dim_event_detail
- dim_event_detail_2
- dim_event_type
- dim_game_state
- dim_giveaway_type
- dim_league
- dim_pass_type
- dim_period
- dim_play_detail
- dim_play_detail_2
- dim_player
- dim_player_role
- dim_playerurlref
- dim_position
- dim_randomnames
- dim_schedule
- dim_season
- dim_shift_duration
- dim_shift_quality_tier
- dim_shift_start_type
- dim_shift_stop_type
- dim_shot_type
- dim_situation
- dim_stoppage_type
- dim_success
- dim_takeaway_type
- dim_team
- dim_time_bucket
- dim_venue
- dim_zone
- dim_zone_entry_type
- dim_zone_exit_type

### Facts (25)
- fact_breakouts
- fact_cycle_events
- fact_draft
- fact_events
- fact_event_players
- fact_faceoffs
- fact_game_status
- fact_gameroster
- fact_high_danger_chances
- fact_leadership
- fact_penalties
- fact_player_game_position
- fact_plays
- fact_registration
- fact_rushes
- fact_saves
- fact_scoring_chances_detailed
- fact_season_summary
- fact_sequences
- fact_shift_players
- fact_shifts
- fact_shifts
- fact_tracking
- fact_turnovers_detailed
- fact_zone_entries
- fact_zone_exits

### QA (2)
- qa_data_completeness
- qa_goal_accuracy

---

## Missing Tables (70) - See docs/MISSING_TABLES.md
