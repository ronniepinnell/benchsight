
# Power BI: WOWY, Head-to-Head, and Line Combo Analytics

This document explains how to use the datamart tables from the Beer League Beauties (BLB) project to build advanced analytics in Power BI: WOWY (With-Or-Without-You), Head-to-Head (H2H), and Line Combo reports.

---

## 1. Core Tables Used

### 1.1 Fact Tables

- **mart.fact_events_wide**
  - Grain: one row per on-ice event.
  - Examples of key columns:
    - `event_key`
    - `game_id`
    - `event_index`
    - `shift_key`
    - `event_team_id`, `opp_team_id`
    - `event_player1_id`, `opp_player1_id`
    - `type` (e.g. `shot`, `pass`, `turnover`)
    - `event_detail_1`, `event_detail_2`
    - `event_successful` (boolean)

- **mart.fact_shifts_tracking**
  - Grain: one row per logical shift **per team side**.
  - Examples of key columns:
    - `shift_key`
    - `game_id`
    - `team_id`, `team_side` (`home` / `away`)
    - `period`
    - `shift_index`, `logical_shift_id`
    - `shift_start_total_seconds`, `shift_end_total_seconds`
    - `shift_duration_seconds`
    - `toi_seconds_net_stoppage`

- **mart.fact_shift_players_tracking**
  - Grain: one row per **player** per logical shift.
  - Examples of key columns:
    - `player_shift_key`
    - `shift_key`
    - `game_id`
    - `team_id`
    - `team_side`
    - `player_id`
    - `position_group` (`F`, `D`, `G`)
    - `shift_number_in_game`
    - `toi_seconds_net_stoppage`
    - On-ice metrics: `on_ice_corsi_for`, `on_ice_corsi_against`, etc.

- **mart.fact_shift_event_summary** (analytics layer)
  - Grain: one row per **shift** and team side.
  - Derived by joining `dim_shift_lineup` with `fact_events_wide`.
  - Examples of columns:
    - `game_id`
    - `shift_key`
    - `shift_index`
    - `team_side`
    - `full_line_player_ids` (array of player_ids on the ice)
    - `toi_seconds_net_stoppage`
    - `shots_for`, `shots_against`
    - `goals_for`, `goals_against`

- **mart.fact_line_combo_stats**
  - Grain: one row per **line combination** per game and team.
  - Based on `dim_line` (unique player sets) and `fact_shift_event_summary`.
  - Examples of columns:
    - `game_id`
    - `line_id`
    - `team_side`
    - `toi_seconds`
    - `shots_for`, `shots_against`
    - `goals_for`, `goals_against`

- **mart.fact_wowy_pairs**
  - Grain: one row per player pair (A,B) per team side.
  - Summarizes “WITH” performance (when both players are on ice together).
  - Examples of columns:
    - `player_a_id`
    - `player_b_id`
    - `team_side`
    - `toi_seconds_with`
    - `shots_for_with`, `shots_against_with`
    - `goals_for_with`, `goals_against_with`

- **mart.fact_h2h_matchups**
  - Grain: one row per shift, capturing home vs away lines.
  - Examples of columns:
    - `game_id`
    - `shift_key`, `shift_index`
    - `toi_seconds_net_stoppage`
    - `home_line_player_ids`, `away_line_player_ids`
    - `home_shots`, `away_shots`
    - `home_goals`, `away_goals`

### 1.2 Dimension Tables

- **dim_player**
  - `player_id`, `player_name`, `jersey_number`
  - `shoots`, `position_group`
  - `skill_rating` (2–6)

- **dim_team**
  - `team_id`, `team_name`, `team_abbrev`

- **dim_game**
  - `game_id`, `game_date_key`, `home_team_id`, `away_team_id`, `league_id`, `season_id`

- **dim_date**
  - `date_key`, `calendar_date`, `year`, `month`, `week`, etc.

- **dim_line**
  - `line_id`
  - `full_line_player_ids` (array or text representation)

---

## 2. Relationships in Power BI

Recommended relationships (simplified):

- `fact_events_wide[game_id]` → `dim_game[game_id]` (many-to-one)
- `fact_events_wide[game_date_key]` → `dim_date[date_key]`
- `fact_events_wide[event_player1_id]` → `dim_player[player_id]`
- `fact_events_wide[event_team_id]` → `dim_team[team_id]`

- `fact_shifts_tracking[game_id]` → `dim_game[game_id]`
- `fact_shifts_tracking[team_id]` → `dim_team[team_id]`

- `fact_shift_players_tracking[player_id]` → `dim_player[player_id]`
- `fact_shift_players_tracking[shift_key]` → `fact_shifts_tracking[shift_key]`

- `fact_shift_event_summary[shift_key]` → `fact_shifts_tracking[shift_key]`

- `dim_line[line_id]` → `fact_line_combo_stats[line_id]`
- `dim_line[line_id]` → (optionally) `fact_h2h_matchups[home_line_id]` and `fact_h2h_matchups[away_line_id]` if you add these IDs.

This model lets you:
- Drill from player → shifts → events.
- Analyze shots/goals by line or WOWY / H2H pairs.

---

## 3. Suggested Report Pages

(See the ChatGPT conversation for the full detailed DAX examples and layouts.)
