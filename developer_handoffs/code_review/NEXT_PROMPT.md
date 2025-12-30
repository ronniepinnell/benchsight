# BenchSight Senior Engineer Code Review - Session Prompt

Copy and paste this prompt to start your session:

---

I'm a Senior Engineer conducting a code review and hardening pass on BenchSight, a hockey analytics ETL pipeline.

## Project Context

- **Database:** Supabase PostgreSQL
- **Total Tables:** 98 (44 dimensions + 51 facts + 1 QA + 2 video)
- **Player Stats:** 317 columns per player per game
- **Total Columns:** 1,909 across all tables
- **Games Processed:** 9 currently, ~125K rows
- **Tests:** 290 passing

## Table Breakdown

**Dimensions (44):** dim_player, dim_team, dim_schedule, dim_season, dim_league, dim_venue, dim_event_type, dim_event_detail, dim_event_detail_2, dim_play_detail, dim_play_detail_2, dim_position, dim_player_role, dim_shift_slot, dim_stat, dim_stat_type, dim_stat_category, dim_micro_stat, dim_zone, dim_danger_zone, dim_rink_coord, dim_rinkboxcoord, dim_rinkcoordzones, dim_shot_type, dim_pass_type, dim_giveaway_type, dim_takeaway_type, dim_turnover_type, dim_turnover_quality, dim_shift_start_type, dim_shift_stop_type, dim_zone_entry_type, dim_zone_exit_type, dim_period, dim_strength, dim_situation, dim_success, dim_net_location, dim_comparison_type, dim_composite_rating, dim_stoppage_type, dim_terminology_mapping, dim_playerurlref, dim_randomnames, dim_highlight_type

**Facts (51):** fact_events, fact_events_long, fact_events_player, fact_events_tracking, fact_shifts, fact_shifts_long, fact_shifts_player, fact_shifts_tracking, fact_player_game_stats, fact_player_period_stats, fact_player_stats_long, fact_player_micro_stats, fact_player_boxscore_all, fact_player_game_position, fact_playergames, fact_team_game_stats, fact_goalie_game_stats, fact_h2h, fact_wowy, fact_head_to_head, fact_line_combos, fact_matchup_summary, fact_player_pair_stats, fact_shift_quality, fact_shift_quality_logical, fact_shift_players, fact_cycle_events, fact_rush_events, fact_possession_time, fact_team_zone_time, fact_scoring_chances, fact_shot_danger, fact_player_xy_long, fact_player_xy_wide, fact_puck_xy_long, fact_puck_xy_wide, fact_shot_xy, fact_linked_events, fact_event_chains, fact_player_event_chains, fact_plays, fact_sequences, fact_video, fact_draft, fact_registration, fact_leadership, fact_gameroster, fact_league_leaders_snapshot, fact_team_standings_snapshot, fact_game_status, fact_suspicious_stats, fact_video_highlights

**QA (1):** qa_suspicious_stats

## Current Issues

**18 tables failed to load** - see `docs/SUPABASE_SCHEMA_ISSUES.md`:
- 15 schema mismatches (PK column doesn't exist in Supabase)
- 2 missing CSVs (video tables not implemented)
- 1 missing constraint (fact_game_status)

## My Review Objectives

1. **Code Review** - Find weak points, anti-patterns, bugs
2. **Test Coverage** - Add integration tests, edge case tests  
3. **Refactoring** - Clean up spaghetti code, DRY violations
4. **Performance** - Optimize slow paths, memory usage
5. **Robustness** - Better error handling, transaction support
6. **Documentation** - Ensure code is properly documented

## Priority Files to Review

**P1 - Loader (causing failures):**
- `scripts/bulletproof_loader.py` (477 lines) - Has `TABLE_DEFINITIONS` for all 98 tables

**P2 - Core ETL:**
- `src/main.py` (800+ lines) - Needs splitting
- `src/pipeline/orchestrator.py` (400+ lines)
- `src/ingestion/game_loader.py` (500+ lines)

**P3 - Tests:**
- `tests/` - 290 tests, but gaps in integration tests

## Known Technical Debt

- No transaction support for partial loads
- Memory issues with large files
- No retry logic for network failures
- Duplicate code in stats calculations
- Missing type hints
- Bare except clauses

## Key Documentation

- Schema issues: `docs/SUPABASE_SCHEMA_ISSUES.md`
- Technical diagrams: `developer_handoffs/code_review/TECHNICAL_DIAGRAMS.md`
- Review checklist: `developer_handoffs/code_review/CODE_REVIEW_CHECKLIST.md`
- Full handoff: `developer_handoffs/code_review/CODE_REVIEW_HANDOFF.md`

## My Specific Task Today

[DESCRIBE YOUR TASK]

## Complete Table Reference

See `docs/TABLE_REFERENCE_COMPLETE.md` for all 98 tables.

**Quick summary:**
- 44 dimension tables (dim_*)
- 51 fact tables (fact_*)
- 1 QA table (qa_*)
- 2 video tables (dim_highlight_type, fact_video_highlights)

The `TABLE_DEFINITIONS` dict in `bulletproof_loader.py` has all 98 tables with their primary keys.
