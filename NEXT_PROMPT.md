# BenchSight v28.6 - Next Session Prompt

## Status
- **139 tables + 26 views** deployed to Supabase
- All SQL views validated and deployed successfully
- ETL pipeline operational with game-specific filtering

## What Was Just Completed (v28.6)
Fixed all SQL view column mismatches:
- Column renames: gaa, home_team_name, away_team_name, home_total_goals, away_total_goals, plus_minus_total
- Removed non-existent columns: ties, venue, pg.pim
- Fixed GROUP BY clauses and trailing commas
- Rebalanced performance tier thresholds

## Views Available
26 views in Supabase covering:
- Leaderboards (points, goals, assists, PPG, career, goalie)
- Standings (current, all seasons, team history, H2H)
- Rankings (players, goalies)
- Summaries (player, goalie, team, league)
- Recent activity (games, player games)
- Comparisons (player vs player, league avg)
- Detail views (player games, goalie games)

## Known Issues Remaining
1. player_id linkage needs jersey mapping
2. TOI columns need shift join
3. home_gf_all=0 bug in some tables

## Suggested Next Tasks
1. **Dashboard Development** - Build Next.js components using the 26 views
2. **Game Tracker Enhancements** - Mirror Mode, Auto Zone detection, event macros
3. **Data Validation** - Continue table-by-table verification
4. **Additional Analytics** - More advanced stats views

## Files to Upload
- benchsight_v28.6.zip (complete package)

## Key Reminders
- Goals ONLY via event_type='Goal' AND event_detail='Goal_Scored'
- event_player_1 = primary player (credit)
- Read LLM_REQUIREMENTS.md and MAINTENANCE.md first
- Run scripts/verify_delivery.py before packaging
