# BenchSight ETL/Data Engineer - Session Prompt

Copy and paste this prompt to start your session:

---

I'm the ETL/Data Engineer for BenchSight, a hockey analytics platform.

## Project Context

- **Database:** Supabase PostgreSQL
- **Total Tables:** 98 (44 dimensions + 51 facts + 1 QA + 2 video)
- **Player Stats:** 317 columns per player per game
- **Games Processed:** 9 currently, ~125K rows total

## Table Breakdown

### Dimensions (44 tables)
**Core:** dim_player, dim_team, dim_schedule, dim_season, dim_league, dim_venue
**Events:** dim_event_type, dim_event_detail, dim_event_detail_2, dim_play_detail, dim_play_detail_2
**Stats:** dim_stat, dim_stat_type, dim_stat_category, dim_micro_stat
**Zones:** dim_zone, dim_danger_zone, dim_rink_coord, dim_rinkboxcoord, dim_rinkcoordzones
**Types:** dim_shot_type, dim_pass_type, dim_giveaway_type, dim_takeaway_type, dim_turnover_type, dim_turnover_quality
**Shifts:** dim_shift_start_type, dim_shift_stop_type, dim_shift_slot
**Zone transitions:** dim_zone_entry_type, dim_zone_exit_type
**Other:** dim_period, dim_strength, dim_situation, dim_success, dim_net_location, dim_position, dim_player_role
**Reference:** dim_comparison_type, dim_composite_rating, dim_stoppage_type, dim_terminology_mapping, dim_playerurlref, dim_randomnames
**Video:** dim_highlight_type (NEW)

### Facts (51 tables)
**Core events:** fact_events, fact_events_long, fact_events_player, fact_events_tracking
**Core shifts:** fact_shifts, fact_shifts_long, fact_shifts_player, fact_shifts_tracking
**Player stats:** fact_player_game_stats (317 cols), fact_player_period_stats, fact_player_stats_long, fact_player_micro_stats, fact_player_boxscore_all, fact_player_game_position, fact_playergames
**Team/Goalie:** fact_team_game_stats, fact_goalie_game_stats
**Analytics:** fact_h2h, fact_wowy, fact_head_to_head, fact_line_combos, fact_matchup_summary, fact_player_pair_stats
**Shifts analytics:** fact_shift_quality, fact_shift_quality_logical, fact_shift_players
**Zone:** fact_cycle_events, fact_rush_events, fact_possession_time, fact_team_zone_time, fact_scoring_chances, fact_shot_danger
**XY tracking:** fact_player_xy_long, fact_player_xy_wide, fact_puck_xy_long, fact_puck_xy_wide, fact_shot_xy
**Chains:** fact_linked_events, fact_event_chains, fact_player_event_chains
**Other:** fact_plays, fact_sequences, fact_video, fact_draft, fact_registration, fact_leadership, fact_gameroster
**Snapshots:** fact_league_leaders_snapshot, fact_team_standings_snapshot, fact_game_status, fact_suspicious_stats
**Video:** fact_video_highlights (NEW)

**QA:** qa_suspicious_stats

## ETL Pipeline

```
Raw Excel → Stage Layer → Intermediate Layer → Datamart Layer → CSV Export → Supabase
```

**Entry point:** `src/main.py`
**Orchestrator:** `src/pipeline/orchestrator.py`
**Loaders:** `src/ingestion/game_loader.py`, `blb_loader.py`, `xy_loader.py`
**Analytics:** `src/analytics/`
**Deployment:** `scripts/bulletproof_loader.py`

## Critical Data Rules

1. **event_player_1** = PRIMARY player (first row per event_index gets the stat)
2. **Goals detected TWO ways:**
   - `event_type = 'Goal'`
   - `event_detail IN ('Shot Goal', 'Goal Scored')`
3. **success** = 's' (successful) or 'u' (unsuccessful)
4. **Primary keys:** `{table_prefix}_{game_id}_{index}` format

## Key Commands

```bash
# Run ETL for all games
./run_etl.sh

# Run ETL for specific game
./run_etl.sh --game 18969

# Check status
./run_etl.sh --status

# Deploy to Supabase
python scripts/bulletproof_loader.py --load all --mode upsert

# Run tests
python -m pytest tests/ -v
```

## Key Documentation

- All 317 stats: `docs/STATS_REFERENCE_COMPLETE.md`
- All 98 tables: `docs/DATA_DICTIONARY.md`
- Schema SQL: `sql/01_CREATE_ALL_TABLES.sql`
- Handoff: `docs/ETL_DATA_ENGINEER_HANDOFF.md`

## My Specific Task Today

[DESCRIBE YOUR TASK]
