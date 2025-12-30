# BenchSight Supabase Developer - Session Prompt

Copy and paste this prompt to start your session:

---

I'm the Supabase/Backend Developer for BenchSight, a hockey analytics platform.

## CRITICAL: Current Blockers

**18 tables failed to load due to schema mismatches.** This is blocking all frontend work.

See `docs/SUPABASE_SCHEMA_ISSUES.md` for the full error log.

## Project Context

- **Database:** Supabase PostgreSQL
- **Total Tables:** 98 (44 dimensions + 51 facts + 1 QA + 2 video)
- **Total Columns:** 1,909 across all tables
- **Data Source:** CSV files in `data/output/`

## Table Breakdown

**Dimensions (44 tables):**
- Core: `dim_player`, `dim_team`, `dim_schedule`, `dim_season`, `dim_league`, `dim_venue`
- Events: `dim_event_type`, `dim_event_detail`, `dim_event_detail_2`, `dim_play_detail`, `dim_play_detail_2`
- Positions: `dim_position`, `dim_player_role`, `dim_shift_slot`
- Stats: `dim_stat`, `dim_stat_type`, `dim_stat_category`, `dim_micro_stat`
- Zones: `dim_zone`, `dim_danger_zone`, `dim_rink_coord`, `dim_rinkboxcoord`, `dim_rinkcoordzones`
- Types: `dim_shot_type`, `dim_pass_type`, `dim_giveaway_type`, `dim_takeaway_type`, `dim_turnover_type`, `dim_turnover_quality`
- Shifts: `dim_shift_start_type`, `dim_shift_stop_type`
- Zone transitions: `dim_zone_entry_type`, `dim_zone_exit_type`
- Other: `dim_period`, `dim_strength`, `dim_situation`, `dim_success`, `dim_net_location`
- Reference: `dim_comparison_type`, `dim_composite_rating`, `dim_stoppage_type`, `dim_terminology_mapping`
- Lookup: `dim_playerurlref`, `dim_randomnames`
- Video: `dim_highlight_type` (NEW - needs creation)

**Facts (51 tables):**
- Core events: `fact_events`, `fact_events_long`, `fact_events_player`, `fact_events_tracking`
- Core shifts: `fact_shifts`, `fact_shifts_long`, `fact_shifts_player`, `fact_shifts_tracking`
- Player stats: `fact_player_game_stats` (317 columns), `fact_player_period_stats`, `fact_player_stats_long`, `fact_player_micro_stats`, `fact_player_boxscore_all`, `fact_player_game_position`, `fact_playergames`
- Team stats: `fact_team_game_stats`
- Goalie stats: `fact_goalie_game_stats`
- Analytics: `fact_h2h`, `fact_wowy`, `fact_head_to_head`, `fact_line_combos`, `fact_matchup_summary`, `fact_player_pair_stats`
- Shifts analytics: `fact_shift_quality`, `fact_shift_quality_logical`, `fact_shift_players`
- Zone analytics: `fact_cycle_events`, `fact_rush_events`, `fact_possession_time`, `fact_team_zone_time`, `fact_scoring_chances`, `fact_shot_danger`
- XY tracking: `fact_player_xy_long`, `fact_player_xy_wide`, `fact_puck_xy_long`, `fact_puck_xy_wide`, `fact_shot_xy`
- Chains: `fact_linked_events`, `fact_event_chains`, `fact_player_event_chains`
- Other: `fact_plays`, `fact_sequences`, `fact_video`, `fact_draft`, `fact_registration`, `fact_leadership`
- Snapshots: `fact_league_leaders_snapshot`, `fact_team_standings_snapshot`, `fact_game_status`
- QA: `fact_suspicious_stats`
- Roster: `fact_gameroster`
- Video: `fact_video_highlights` (NEW - needs creation)

**QA (1 table):**
- `qa_suspicious_stats`

## My Priority Tasks

1. **Fix 15 schema mismatches** - Tables exist but missing PK columns
2. **Create 2 video tables** - `dim_highlight_type`, `fact_video_highlights`
3. **Fix 1 constraint issue** - `fact_game_status` needs PRIMARY KEY
4. **Verify all 98 tables load** - `bulletproof_loader.py --load all` = 0 failures

## Key Files

- Schema issues: `docs/SUPABASE_SCHEMA_ISSUES.md`
- Full schema: `sql/01_CREATE_ALL_TABLES.sql`
- Video tables: `sql/04_VIDEO_HIGHLIGHTS.sql`
- Loader: `scripts/bulletproof_loader.py`
- Table definitions: See `TABLE_DEFINITIONS` dict in bulletproof_loader.py (all 98 tables with PKs)

## Verification Command

```bash
python scripts/bulletproof_loader.py --load all --mode upsert
# Success = "Tables: 98/98 successful, Failed: 0"
```

## My Specific Task Today

[DESCRIBE YOUR TASK]
