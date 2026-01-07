# BenchSight Complete Technical Guide v13.18

**Last Updated:** January 7, 2026

---

## ✅ CURRENT STATE (v13.18)

| Metric | Count |
|--------|-------|
| Tables created by ETL | 59 (59 (33 dim, 24 fact, 2 qa)) |
| Games tracked | 4 (18969, 18977, 18981, 18987) |
| Total goals (verified) | 17 |
| Tier 1 tests | 32 (blocking) |
| Tier 2 tests | 17 (warning) |

**One Command Verification:**
```bash
python scripts/pre_delivery.py
```

---

## Table of Contents

1. [Safeguards & Verification](#1-safeguards--verification)
2. [LLM Instructions](#2-llm-instructions)
3. [Quick Reference](#3-quick-reference)
4. [ETL Workflow](#4-etl-workflow)
5. [Scripts Reference](#5-scripts-reference)
6. [Working Tables (59)](#6-working-tables-59)
7. [Table Details & Data Dictionary](#7-table-details--data-dictionary)

---

## 1. Safeguards & Verification

### Pre-Delivery Pipeline (MANDATORY)

Every package must be created with:
```bash
python scripts/pre_delivery.py
```

This runs 12 phases:
1. Nuclear wipe (delete all output)
2. Fresh ETL run
3. Compute ground truth
4. Verify goals against IMMUTABLE_FACTS
5. Check for regressions
5b. Schema comparison
6. File size check (truncation detection)
7. Tier 1 tests (BLOCKING)
7b. Tier 2 tests (warnings)
8. Version bump + doc consistency
9. Create package with MANIFEST
10. Final report

### Tiered Test System

| Tier | File | Tests | Effect |
|------|------|-------|--------|
| 1 | `test_tier1_blocking.py` | 32 | BLOCKS delivery |
| 2 | `test_tier2_warning.py` | 17 | Warnings only |
| 3 | `test_tier3_future.py` | - | Skipped (future) |

### Config Files

| File | Purpose | Editable By |
|------|---------|-------------|
| `config/IMMUTABLE_FACTS.json` | Verified goal counts | Human only |
| `config/GROUND_TRUTH.json` | Auto-computed tables/goals | Pipeline only |
| `config/SCHEMA_SNAPSHOT.json` | Column tracking | Pipeline only |
| `config/FILE_SIZES.json` | Truncation detection | Pipeline only |
| `config/VERSION.json` | Version management | Pipeline only |

---

## 2. LLM Instructions

### Copy-Paste This At Start of Every Chat

```
MANDATORY RULES - VIOLATIONS WILL WASTE TIME AND MONEY:

1. READ LLM_REQUIREMENTS.md, README.md AND MASTER_GUIDE.md FIRST
2. NO NEW FILES unless I explicitly ask for one. Fix existing code.
3. NO PLACEHOLDER DATA. Ever. If data is missing, fix why it's missing.
4. NO POST-PROCESSING SCRIPTS. Fix the source.
5. Before ANY code change, show me:
   - WHICH FILE you will modify
   - WHAT LINE(S) you will change
   - WHY this is the root cause, not a symptom
6. After ANY code change, run tests and show results.
7. If you cannot find the root cause, SAY SO. Don't fake a fix.
8. This is Chat 14, so outputs should be v14.01, v14.02, etc.
9. Goals: event_type='Goal' AND event_detail='Goal_Scored' (NOT Shot_Goal)
10. event_player_1 is the primary player (scorer for goals)
11. HTML docs in docs/html/ - start with index.html
12. Run ETL: python -m src.etl_orchestrator full
13. Run tests: python3 -m pytest tests/test_etl.py -v
14. EVERY output must update ALL doc timestamps and CHANGELOG and to reflect current state

CURRENT STATE:
- ETL creates ~59 tables from scratch
- ~68 tables are BROKEN (no source code)
- Full 59 tables available ONLY from backup

VERIFICATION AFTER EVERY CHANGE:
rm -rf data/output/*.csv && python run_etl.py
Expected: ~59 tables, 32 passing tests

TO GET ALL 130 TABLES:
cp data/output_backup_v13.02/*.csv data/output/

NEVER:
- Delete code without running tests first
- Use Shot_Goal to count goals
- Skip updating timestamps on docs
- Output without incrementing version number

My memory instructions say:
- Always provide complete project zip with updated docs
- Always read LLM_REQUIREMENTS.md first
- Upon first message back, provide summary and acknowledge requirements

```

### Red Flags - STOP IMMEDIATELY If You Have These Responses

- "Let me create a script to fix this..."
- "I'll add a post-processing step..."
- "Let me generate the missing tables..."
- Creating any file named `fix_*.py`, `patch_*.py`, `enhancement_*.py`
- Using backup data to "fill in" missing output
- "This should work" without running actual tests
- Saying there are 130 working tables (there are only ~62)

### Testing Checklist

After EVERY change:
```bash
# 1. Clear output
rm -rf data/output/*.csv

# 2. Run ETL
python run_etl.py

# 3. Count tables (should be ~62 from scratch)
ls data/output/*.csv | wc -l

# 4. Run tests
python -m pytest tests/test_etl.py -v

# 5. If you need all 59 tables
cp data/output_backup_v13.02/*.csv data/output/


```


### Files New Chat MUST Read First
1. `LLM_REQUIREMENTS.md` - This file, all rules
2. `docs/html/index.html` - HTML documentation hub
3. `docs/LLM_HANDOFF.md` - Architecture context
4. `docs/HONEST_ASSESSMENT.md` - Known issues
5. `CHANGELOG.md` - Recent changes


---

## 2. Quick Reference

### Directory Structure
```
benchsight_v13.02/
├── run_etl.py                  # ONLY ETL entry point
├── LLM_REQUIREMENTS.md         # Detailed LLM rules
├── MASTER_GUIDE.md             # This file
├── data/
│   ├── raw/
│   │   ├── BLB_TABLES.xlsx     # Source dimension data
│   │   └── games/              # Game tracking (18969, 18977, 18981, 18987)
│   ├── output/                 # Generated CSVs
│   └── output_backup_v13.02/   # Known good 59 tables
├── src/
│   ├── core/                   # Core ETL (base_etl.py, add_all_fkeys.py)
│   ├── advanced/               # Enhancement modules
│   ├── etl/                    # Post-processing
│   ├── qa/                     # Quality assurance
│   └── etl_orchestrator.py     # Orchestration logic
├── tests/                      # 23 tests
├── docs/
│   ├── html/                   # HTML documentation (179 files)
│   │   └── tables/             # Per-table HTML docs
│   ├── reference/              # Technical reference docs
│   └── guides/                 # How-to guides
└── config/                     # Configuration files
```

### Key Commands
```bash
# Run ETL (creates ~59 tables)
python run_etl.py

# Restore all 59 tables
cp data/output_backup_v13.02/*.csv data/output/

# Run tests
python -m pytest tests/test_etl.py -v

# Count tables
ls data/output/*.csv | wc -l
```

---

## 3. ETL Workflow

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                              │
├─────────────────────────────────────────────────────────────────┤
│  BLB_TABLES.xlsx          Game Tracking Files                   │
│  (Master Reference)       (18969, 18977, 18981, 18987)          │
└──────────┬───────────────────────────┬──────────────────────────┘
           │                           │
           ▼                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 1: base_etl.main()                      │
│                    src/core/base_etl.py                          │
├─────────────────────────────────────────────────────────────────┤
│  Creates ~53 tables:                                            │
│  • dim_* (dimensions from BLB)                                  │
│  • fact_event_players (raw tracking)                          │
│  • fact_shifts (shift data)                                     │
│  • fact_sequences, fact_plays                                   │
│  • Zone tables, event tables                                    │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 2: build_player_stats                   │
│                    ❌ BROKEN - Module Missing                    │
├─────────────────────────────────────────────────────────────────┤
│  Should create: fact_player_game_stats base                     │
│  Status: No source code exists                                  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 3: add_all_fkeys.main()                 │
│                    src/core/add_all_fkeys.py                     │
├─────────────────────────────────────────────────────────────────┤
│  Creates: fact_shift_players                                    │
│  Adds foreign key relationships to existing tables              │
│  ⚠️ Partially fails without Phase 2                             │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 4: extended_tables                      │
│                    src/advanced/extended_tables.py               │
├─────────────────────────────────────────────────────────────────┤
│  Creates summary/aggregate tables                               │
│  ✅ Working                                                      │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 5: post_etl_processor                   │
│                    src/etl/post_etl_processor.py                 │
├─────────────────────────────────────────────────────────────────┤
│  Creates: fact_events (enhanced from tracking)                  │
│  ✅ Working                                                      │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 6-8: Enhancements                       │
│                    event_time_context, v11_enhancements, qa      │
├─────────────────────────────────────────────────────────────────┤
│  Creates: dim_shift_duration, qa_* tables                       │
│  ✅ Working                                                      │
└─────────────────────────────────────────────────────────────────┘
```

### run_etl.py Execution Order

| Phase | Module | What It Does | Status |
|-------|--------|--------------|--------|
| 1 | `base_etl.main()` | Core table creation | ✅ ~53 tables |
| 2 | `build_player_stats.main()` | Player stats base | ❌ Missing module |
| 3 | `add_all_fkeys.main()` | FK relationships | ⚠️ Partial |
| 4 | `extended_tables.create_extended_tables()` | Summary tables | ✅ Working |
| 5 | `post_etl_processor.main()` | Enhanced events | ✅ Working |
| 6 | `event_time_context.enhance_event_tables()` | Time context | ✅ Working |
| 7 | `v11_enhancements.run_all_enhancements()` | dim_shift_duration | ✅ Working |
| 8 | `build_qa_facts.main()` | QA tables | ⚠️ Partial |

---

## 4. Module Reference

### Core Modules (src/core/)

| File | Lines | Purpose | Key Functions |
|------|-------|---------|---------------|
| `base_etl.py` | 3200+ | Main table creation | `main()`, `load_blb_tables()`, `load_tracking_data()`, `create_dim_*()`, `create_fact_*()` |
| `add_all_fkeys.py` | 900+ | FK relationships | `main()`, `ForeignKeyManager` class |
| `populate_all_fks_v2.py` | 900+ | FK population (alt) | Various FK functions |
| `key_utils.py` | 300+ | Key generation | `generate_pk()`, `load_keys()` |
| `safe_csv.py` | 150+ | Safe CSV I/O | `safe_read_csv()`, `safe_write_csv()` |
| `safe_sql.py` | 100+ | SQL injection prevention | `validate_identifier()` |
| `combine_tracking.py` | 200+ | Merge tracking data | `combine_game_tracking()` |

### Advanced Modules (src/advanced/)

| File | Lines | Purpose | Key Functions |
|------|-------|---------|---------------|
| `extended_tables.py` | 400+ | Summary tables | `create_extended_tables()` |
| `enhance_all_stats.py` | 1100+ | Stats enhancement | `main()`, `aggregate_micro_stats()` |
| `create_additional_tables.py` | 500+ | Extra fact tables | `main()` |
| `v11_enhancements.py` | 200+ | v11 additions | `run_all_enhancements()` |
| `event_time_context.py` | 300+ | Time-based context | `enhance_event_tables()` |
| `final_stats_enhancement.py` | 400+ | Final stats calcs | `enhance_player_stats()` |

### ETL/Post-Processing (src/etl/)

| File | Lines | Purpose | Key Functions |
|------|-------|---------|---------------|
| `post_etl_processor.py` | 600+ | Post-processing | `main()`, `process_events()` |

### QA Modules (src/qa/)

| File | Lines | Purpose | Key Functions |
|------|-------|---------|---------------|
| `build_qa_facts.py` | 450+ | QA tables | `main()`, `create_qa_goal_accuracy()` |
| `validate_h2h_wowy.py` | 200+ | H2H/WOWY validation | `validate_h2h()`, `validate_wowy()` |

### Key File → Table Mapping

| Need to modify... | Look in... |
|-------------------|------------|
| Core dimensions (dim_player, dim_team) | `src/core/base_etl.py` (BLB load section) |
| Event dimensions (dim_event_type) | `src/core/base_etl.py` lines 1000-1400 |
| fact_events | `src/etl/post_etl_processor.py` line 360 |
| fact_event_players | `src/core/base_etl.py` lines 541-737 |
| fact_shifts | `src/core/base_etl.py` line 883 |
| fact_shift_players | `src/core/add_all_fkeys.py` line 144 |
| fact_player_game_stats | **BROKEN** - no source |
| H2H/WOWY enhancements | `src/advanced/enhance_all_stats.py` |
| Shift quality tables | `src/advanced/create_additional_tables.py` |
| QA tables | `src/qa/build_qa_facts.py` |

---

## 5. Working Tables (~62)

These tables ARE created when you run `python run_etl.py` from scratch:

### Dimensions Created by base_etl.py

| Table | Line | Columns |
|-------|------|---------|
| dim_player_role | 977 | player_role_id, role_code, role_name |
| dim_position | 989 | position_id, position_code, position_name |
| dim_zone | 998 | zone_id, zone_code, zone_name |
| dim_period | 1009 | period_id, period_number, period_name |
| dim_venue | 1017 | venue_id, venue_code, venue_name |
| dim_event_type | 1033 | event_type_id, event_type_code, event_type_name |
| dim_event_detail | 1052 | event_detail_id, event_detail_code, event_detail_name |
| dim_success | 1064 | success_id, success_code, success_name |
| dim_shot_type | 1077 | shot_type_id, shot_type_code, shot_type_name |
| dim_pass_type | 1090 | pass_type_id, pass_type_code, pass_type_name |
| dim_event_detail_2 | 1138 | event_detail_2_id, detail_code, detail_name |
| dim_zone_entry_type | 1162 | zone_entry_type_id, entry_type_code, entry_type_name |
| dim_zone_exit_type | 1182 | zone_exit_type_id, exit_type_code, exit_type_name |
| dim_stoppage_type | 1203 | stoppage_type_id, stoppage_code, stoppage_name |
| dim_giveaway_type | 1224 | giveaway_type_id, giveaway_code, giveaway_name |
| dim_takeaway_type | 1246 | takeaway_type_id, takeaway_code, takeaway_name |
| dim_play_detail | 1322 | play_detail_id, detail_code, detail_name |
| dim_play_detail_2 | 1361 | play_detail_2_id, detail_code, detail_name |
| dim_danger_level | 2619 | danger_level_id, level_code, level_name |
| dim_shift_stop_type | 3033 | shift_stop_type_id, stop_code, stop_name |
| dim_situation | 3045 | situation_id, situation_code, situation_name |

### Facts Created by base_etl.py

| Table | Line | Key Columns |
|-------|------|-------------|
| fact_tracking | 860 | tracking_key, game_id, period, event_type, etc. |
| fact_shifts | 883 | shift_key, game_id, player_id, period, duration |
| fact_event_players | 541-737 | All raw tracking columns |
| fact_sequences | 2360 | sequence_key, game_id, events_in_sequence |
| fact_plays | 2465 | play_key, game_id, play_type |
| fact_rushes | 2626 | rush_key, game_id, rush_type |
| fact_breakouts | 2648 | breakout_key, game_id, breakout_type |
| fact_zone_entries | 2655 | entry_key, game_id, entry_type |
| fact_zone_exits | 2662 | exit_key, game_id, exit_type |
| fact_scoring_chances_detailed | 2667 | chance_key, game_id, danger_level |
| fact_high_danger_chances | 2673 | hd_chance_key, game_id, is_goal |
| fact_saves | 2679 | save_key, game_id, goalie_id |
| fact_turnovers_detailed | 2685 | turnover_key, game_id, turnover_type |
| fact_faceoffs | 2692 | faceoff_key, game_id, winner_id |
| fact_penalties | 2698 | penalty_key, game_id, player_id |
| fact_gameroster | 3150 | roster_key, game_id, player_id |
| fact_cycle_events | 2025 | cycle_key, game_id, cycle_type |

### Tables Created by Other Modules

| Table | Module | File:Line |
|-------|--------|-----------|
| fact_events | post_etl_processor | post_etl_processor.py:360 |
| fact_shift_players | add_all_fkeys | add_all_fkeys.py:144 |
| dim_shift_duration | v11_enhancements | v11_enhancements.py:70 |
| fact_game_status | build_qa_facts | build_qa_facts.py:213 |
| fact_player_game_position | build_qa_facts | build_qa_facts.py:432 |

---

## 6. Broken Tables (~68)

These tables exist in `data/output_backup_v13.02/` but have **NO SOURCE CODE** that creates them. They were created manually during previous sessions and never integrated.

### Broken Dimensions (21)

| Table | Columns | Rows |
|-------|---------|------|
| dim_assist_type | assist_type_id, assist_type_code, assist_type_name | 4 |
| dim_comparison_type | comparison_type_id, comparison_type_code, comparison_type_name, description, analysis_scope | 7 |
| dim_competition_tier | competition_tier_id, tier_name, min_rating, max_rating | 5 |
| dim_composite_rating | rating_id, rating_code, rating_name, description, scale_min, scale_max | 9 |
| dim_danger_zone | danger_zone_id, danger_zone_code, danger_zone_name, xg_base, description | 5 |
| dim_game_state | game_state_id, state_code, state_name | 4 |
| dim_league | league_id, league_code, league_name | 2 |
| dim_micro_stat | micro_stat_id, stat_code, stat_name, category | 23 |
| dim_net_location | net_location_id, net_location_code, net_location_name, x_pct, y_pct | 11 |
| dim_pass_outcome | pass_outcome_id, pass_outcome_code, pass_outcome_name, is_successful | 5 |
| dim_player | player_id, player_name, first_name, last_name, birth_date, etc. | ~200 |
| dim_playerurlref | player_id, url_ref | ~200 |
| dim_randomnames | random_name_id, name | 100 |
| dim_rating | rating_id, rating_value, rating_name | 6 |
| dim_rating_matchup | matchup_id, matchup_name, min_diff, max_diff | 6 |
| dim_rink_zone | rink_zone_id, zone_code, zone_name, granularity, x_min, x_max, y_min, y_max | 268 |
| dim_save_outcome | save_outcome_id, save_outcome_code, save_outcome_name, causes_stoppage | 4 |
| dim_schedule | schedule_id, game_id, date, home_team, away_team, home_score, away_score | ~50 |
| dim_season | season_id, season_name, start_date, end_date | 2 |
| dim_shift_quality_tier | tier_id, tier_name, min_score, max_score | 5 |
| dim_shift_slot | slot_id, slot_code, slot_name | 8 |
| dim_shot_outcome | shot_outcome_id, shot_outcome_code, shot_outcome_name, is_goal, is_save | 6 |
| dim_stat | stat_id, stat_code, stat_name, category, description, formula | 84 |
| dim_stat_category | stat_category_id, category_code, category_name, description | 14 |
| dim_stat_type | stat_id, stat_name, stat_category, stat_level, computable_now | 58 |
| dim_strength | strength_id, strength_code, strength_name, situation_type, xg_multiplier | 19 |
| dim_team | team_id, team_name, team_code, arena | ~10 |
| dim_terminology_mapping | dimension, old_value, new_value, match_type | 85 |
| dim_time_bucket | time_bucket_id, bucket_name, start_seconds, end_seconds | 10 |
| dim_turnover_quality | turnover_quality_id, turnover_quality_code, turnover_quality_name | 4 |
| dim_turnover_type | turnover_type_id, turnover_type_code, turnover_type_name, category | 22 |
| dim_zone_outcome | zone_outcome_id, zone_outcome_code, zone_outcome_name, is_controlled | 7 |

### Broken Facts (43)

| Table | Key Columns | Rows |
|-------|-------------|------|
| fact_draft | draft_key, player_id, draft_round, draft_position | ~50 |
| fact_event_chains | chain_id, game_id, entry_event_key, shot_event_key, events_to_shot | 228 |
| fact_goalie_game_stats | goalie_game_key, game_id, player_id, saves, goals_against, save_pct | 9 |
| fact_h2h | game_id, player_1_id, player_2_id, toi_together, cf_pct | 685 |
| fact_head_to_head | game_id, player_1_id, player_2_id, shifts_against, toi_against_seconds | 573 |
| fact_leadership | leadership_key, player_id, leadership_type | ~50 |
| fact_league_leaders_snapshot | game_id, player_id, gp, goals, assists, pts | 14474 |
| fact_line_combos | line_combo_key, game_id, forward_combo, defense_combo, toi_together | 333 |
| fact_linked_events | linked_event_key, game_id, primary_event_index, event_count | 474 |
| fact_matchup_performance | game_id, player_id, matchup_id, toi_seconds, rating_advantage | 266 |
| fact_matchup_summary | game_id, player_1_id, player_2_id, cf_pct_together, synergy_score | 685 |
| fact_period_momentum | momentum_key, game_id, period, events_count, goals, shots | 13 |
| fact_player_boxscore_all | game_id, player_id, g, a, pts, pim | 14474 |
| fact_player_career_stats | player_career_key, player_id, games_played, career_goals | 69 |
| fact_player_event_chains | event_chain_key, game_id, event_key, event_type, period | 5118 |
| fact_player_game_stats | player_game_id, game_id, player_id, goals, assists, shots (300+ cols) | 108 |
| fact_player_micro_stats | micro_stat_key, player_game_key, micro_stat, count | 213 |
| fact_player_pair_stats | game_id, player_1_id, player_2_id, shifts_together | 476 |
| fact_player_period_stats | player_period_key, game_id, player_id, period, shots, goals | 322 |
| fact_player_position_splits | position_split_key, position, player_count, avg_goals | 4 |
| fact_player_qoc_summary | game_id, player_id, toi_seconds, player_rating, qoc | 106 |
| fact_player_season_stats | player_season_key, player_id, games_played, goals, assists (90+ cols) | 69 |
| fact_player_stats_by_competition_tier | game_id, player_id, competition_tier_id, toi_seconds | 241 |
| fact_player_stats_long | player_stat_key, player_game_key, stat_name, stat_value | 13885 |
| fact_player_trends | player_trend_key, player_id, game_number, cumulative_points | 108 |
| fact_player_xy_long | player_xy_key, game_id, event_index, player_id, x, y | 1 |
| fact_player_xy_wide | player_xy_key, game_id, player_id, x_1, y_1, x_2, y_2... | 1 |
| fact_playergames | ID, Date, Team, Player, G, A, GA, PIM | 3011 |
| fact_possession_time | possession_key, game_id, player_id, zone_entries | 108 |
| fact_puck_xy_long | puck_xy_key, game_id, event_index, x, y, z | 1 |
| fact_puck_xy_wide | puck_xy_key, game_id, x_1, y_1, z_1, x_2, y_2, z_2... | 1 |
| fact_registration | registration_key, player_id, team_id, season_id | ~200 |
| fact_rush_events | game_id, entry_event_index, shot_event_index, is_rush, is_goal | 200 |
| fact_scoring_chances | scoring_chance_key, game_id, event_id, danger_level, is_goal | 456 |
| fact_season_summary | season_summary_key, season_id, games_played, total_goals | 2 |
| fact_shift_quality | shift_quality_key, game_id, player_id, shift_duration, quality_score | 4560 |
| fact_shift_quality_logical | game_id, player_id, logical_shifts, avg_quality_score | 106 |
| fact_shot_danger | shot_danger_key, game_id, event_index, danger_zone, xg | 436 |
| fact_shot_xy | shot_xy_key, game_id, event_index, shot_x, shot_y, shot_distance | 1 |
| fact_special_teams_summary | special_teams_key, team_id, total_corsi_for, total_xg_for | 6 |
| fact_suspicious_stats | game_id, player_id, stat_name, stat_value, flag_type | 19 |
| fact_team_game_stats | team_game_key, game_id, goals, shots, cf_pct, xg_for | 9 |
| fact_team_season_stats | team_season_key, team_id, season_goals, avg_goals_per_game | 6 |
| fact_team_standings_snapshot | game_id, team_name, wins, losses, points | 1125 |
| fact_team_zone_time | various zone time metrics | ~50 |
| fact_video | video_key, game_id, timestamp | ~100 |
| fact_wowy | game_id, player_id, cf_with, cf_without, cf_pct_delta | ~500 |
| fact_zone_entry_summary | zone entry aggregates | ~50 |
| fact_zone_exit_summary | zone exit aggregates | ~50 |

### Broken Lookup/QA (4)

| Table | Purpose |
|-------|---------|
| lookup_player_game_rating | Player ratings per game |
| qa_data_completeness | Data quality metrics |
| qa_goal_accuracy | Goal verification |
| qa_scorer_comparison | Scorer verification |
| qa_suspicious_stats | Outlier detection |

---

## 7. Table Details & Data Dictionary

For detailed column definitions and table documentation, see:

- **HTML docs:** `docs/html/tables/` - One HTML file per table
- **Data dictionary:** `docs/reference/DATA_DICTIONARY.csv`
- **Schema diagram:** `docs/html/diagrams/schema_diagram.html`

### Goal Counting (CRITICAL)

```python
# CORRECT - Only count actual goals
goals = events[(events['event_type'] == 'Goal') & 
               (events['event_detail'] == 'Goal_Scored')]

# WRONG - Shot_Goal is the shot that resulted in a goal, NOT the goal itself
# Do NOT count Shot_Goal as a goal!
```

### Key Format Standard

All entity keys use format: `{PREFIX}{game_id}{index:05d}`

| Key | Prefix | Example |
|-----|--------|---------|
| event_id | EV | EV1896901000 |
| shift_id | SH | SH1896900001 |
| sequence_key | SQ | SQ1896905001 |
| play_key | PL | PL1896906001 |

---

## Appendix: Source Code Line References

### base_etl.py Key Sections

| Lines | What It Does |
|-------|--------------|
| 1-100 | Imports, constants |
| 100-420 | Helper functions |
| 420-540 | BLB table loading |
| 541-737 | Tracking data load (fact_event_players) |
| 738-880 | Event processing |
| 881-940 | Shift creation (fact_shifts) |
| 941-1400 | Dimension table creation |
| 1401-2000 | Additional dimension logic |
| 2001-2600 | Fact table creation |
| 2601-3000 | Zone/danger tables |
| 3001-3200 | Final tables and main() |

### enhance_all_stats.py Key Lines

| Line | Creates/Enhances |
|------|------------------|
| 1037 | fact_player_game_stats enhancement |
| 1048 | fact_h2h enhancement |
| 1052 | fact_wowy enhancement |
| 1063 | fact_goalie_game_stats enhancement |
| 1076 | fact_player_period_stats |
| 1081 | fact_shot_danger |
| 1086 | dim_danger_zone |
| 1090 | dim_composite_rating |

### create_additional_tables.py Key Lines

| Line | Creates |
|------|---------|
| 61 | fact_player_stats_long |
| 159 | fact_team_game_stats |
| 224 | fact_line_combos |
| 253 | fact_matchup_summary |
| 299 | fact_shift_quality |
| 331 | fact_team_zone_time |
| 369 | fact_scoring_chances |
| 408 | dim_stat_category |
| 447 | dim_micro_stat |
| 486 | fact_player_micro_stats |

---

*End of guide. For questions, grep the source code or check docs/html/tables/*
