# Human Guide – Power BI Strategy

This file gives you ideas for how to turn your datamart tables into
Power BI reports, inspired by NHL Edge, Evolving-Hockey, Natural Stat Trick,
and the other links you shared.

## 1. Suggested Power BI Pages

1. **Game Summary (ESPN/NHL-style)**
   - Tables:
     - `fact_box_player`
     - `fact_events`
     - `fact_xg_shots`
     - `dim_games`, `dim_teams`, `dim_players`
   - Visuals:
     - Final score, goal timeline.
     - Shot/xG timeline.
     - Team shot & xG maps.
     - Key player cards (top forwards, D, goalie).

2. **Player Game Card**
   - Zoom in on `fact_box_player` for one game/player.
   - Sections:
     - Boxscore (G, A, SOG, TOI, +/-).
     - Possession (CF, CA, xGF, xGA, CF%, xGF%).
     - Microstats (entries, exits, passes, turnovers).
     - Deployment (zone starts, matchups).
     - Link to video clips via the video URL columns.

3. **Season/Team Trends**
   - Aggregate `fact_box_player` and `fact_events` by game and team.
   - Show rolling averages for team xG, goals, shot share, etc.
   - Compare regular season vs playoffs, different opponents, etc.

4. **Line Combos & Matchups**
   - Use line-level features from `fact_shifts` or a dedicated
     line-combo fact table (if/when built).
   - Show how different forward and D combos perform together and
     against specific matchups.

5. **Microstat Explorer**
   - Use microstat columns in `fact_box_player` and event-level tables.
   - Allow filtering by event type, zone, score state, rating matchups.

## 2. DAX Tips

- Always respect the grain of your fact tables:
  - Measures on `fact_box_player` usually summarize per game or season.
  - Measures on `fact_events` should be event-level counts or sums.
- Use separate measures for:
  - Raw counts (e.g., `Shots For`).
  - Rates (`Shots For per 60`).
  - Percentages (`CF%`, `xGF%`).

See `docs_llm/powerbi_measures_example.dax` for example measure patterns
you can adapt directly.
