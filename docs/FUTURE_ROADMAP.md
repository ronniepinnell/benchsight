# Future Roadmap

**Last Updated:** January 7, 2026  
**Version:** 12.03

## Current Status

✅ **v13.18 Complete:** 62 working tables, 4 games, 100% goal verification

## Priority 1: Data Expansion

### More Games
- Process remaining Fall 2024 games (15+ available)
- Add historical seasons for trends
- Automate new game detection

### XY Coordinates
- Integrate shot location data (`src/xy/xy_tables.py` exists)
- Create heat maps and shot charts
- Calculate expected goals (xG)

## Priority 2: Missing Tables

| Table | Purpose | Status |
|-------|---------|--------|
| fact_player_game_stats | Per-game player stats | Needs regen |
| fact_goalie_game_stats | Goalie performance | Needs regen |
| fact_team_game_stats | Per-game team stats | Needs regen |
| fact_player_season_stats | Season aggregates | Not built |

## Priority 3: Dashboard

- Complete Streamlit dashboard (`dashboard/app.py`)
- Player profile pages
- Game summary reports
- Team comparisons
- Leaderboards

## Priority 4: Deployment

- Supabase schema finalization
- Automated ETL scheduling
- User authentication
- API endpoints

## Suggested Timeline

| Phase | Tasks | Effort |
|-------|-------|--------|
| v12.x-v13.x | Process all Fall 2024 games, fix stats tables | 2-3 sessions |
| v14.x | XY integration, shot charts | 2-3 sessions |
| v15.x | Dashboard completion | 3-4 sessions |
| v16.x | Supabase deployment | 2-3 sessions |

## Future Ideas

- **Video Integration:** Link events to video timestamps
- **Player Comparison Tool:** Head-to-head analysis
- **Game Prediction:** ML model for outcomes
- **Mobile App:** React Native companion

---

See also: [HTML Version](html/FUTURE_ROADMAP.html)
