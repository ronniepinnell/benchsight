# BenchSight TODO

## Completed v29.0
- [x] SQL views deployed to Supabase (26 views)
- [x] Column name mismatches fixed
- [x] Performance tier thresholds rebalanced
- [x] Fixed season_id mapping for scrimmage games (N2025S)
- [x] Fixed games_played season filter bug
- [x] Added game_type grain to ALL 6 season stats tables
- [x] Added ties column to team and goalie tables
- [x] Fixed points calculation (wins×2 + ties×1)
- [x] Created game_type_aggregator.py (single source of truth)
- [x] Refactored all season stats to use shared utility

## Data Validation Status
- [x] fact_team_season_stats_basic - VALIDATED ✅
- [ ] Remaining 138 tables to validate

## Next Steps
- [ ] Test all views in Supabase dashboard
- [ ] Build Next.js dashboard components using views
- [ ] Add player_id linkage (needs jersey mapping)
- [ ] Add TOI columns (needs shift join)
- [ ] Fix home_gf_all=0 bug
- [ ] Game tracker workflow improvements
- [ ] **Enhance DATA_DICTIONARY_FULL.md with calculation formulas** (See `docs/DATA_DICTIONARY_ENHANCEMENT_TODO.md`)
- [ ] **Add flexible ETL workflow options** (See `docs/ETL_WORKFLOW_FLEXIBLE_OPTIONS.md`)
  - Separate ETL, Schema Generation, Schema Loading, and Sync operations
  - Add flexible options for what to run ETL on (games, tables, source selection)
  - Add flexible options for what to sync (tables, modes, patterns)

## Future
- [ ] Commercial SaaS deployment
- [ ] Additional seasons data
- [ ] Real-time game tracking integration
