
# Beer League Beauties – Datamart Table Catalog (Draft)

This document summarizes the intended **dim_*** and **fact_*** tables for the Beer League Beauties (BLB) project, how they relate to each other, and how they map back to the current snapshot workbook:

`blb_all_games_datamart_snapshot.xlsx`

The goal is to give you a clear mental model of:

- The **grain** of each table (what one row represents)
- The **keys** (primary and foreign)
- Which **source tables** feed it (stage / snapshot)
- How these tables fit together into a **star / snowflake schema** for Power BI and ML

---

## 1. Core Dimensions

These tables are mostly “slow-changing” and reused across all games.

### 1.1 `dim_player`

**Grain**: one row per unique player across all games.

**Primary key**: `player_id` (surrogate/business key from BLB_Tables).

**Important columns (examples)**

- Identity & naming:
  - `player_id`
  - `player_first_name`
  - `player_last_name`
  - `player_full_name`
- Attributes:
  - `player_primary_position` (C/LW/RW/D/G, etc.)
  - `player_hand` (L/R)
  - `birth_year`, `player_gender`
  - `highest_beer_league` (if present)
- Ratings & roles:
  - `current_skill_rating` (2–6 scale)
  - `player_rating_ly` (last year)
  - `player_leadership`, `player_notes`

**Used by**

- `fact_event` (via `fact_event_role.player_id`)
- `fact_shift_player`
- `fact_boxscore_player`
- `fact_game_roster`

**Source**

- BLB master workbook: `BLB_Tables.xlsx` → `dim_player` sheet / table.

---

### 1.2 `dim_team`

**Grain**: one row per unique team.

**Primary key**: `team_id`

**Important columns**

- `team_id`
- `team_name`
- (Optional) `league_id`
- (Optional) `team_abbreviation`, colors, etc.

**Used by**

- `dim_game` (home/away teams)
- Almost all facts that have `team_id`:
  - `fact_event`, `fact_event_role`
  - `fact_shift_player`, `fact_shift_line_state`
  - `fact_boxscore_player`
  - `fact_game_roster`

**Source**

- BLB master workbook: `BLB_Tables.xlsx` → `dim_team`.

---

### 1.3 `dim_league`

**Grain**: one row per league (Beer League, NHL, etc.).

**Primary key**: `league_id`

**Used by**

- `dim_game` (each game belongs to a league)
- Season-level visualizations and filters.

**Source**

- BLB master workbook: `BLB_Tables.xlsx` → `dim_league`.

---

### 1.4 `dim_game`

**Grain**: one row per game across all seasons.

**Primary key**: `game_id`

**Important columns**

- `game_id` (used throughout stage/intermediate/mart)
- `league_id` → `dim_league`
- `home_team_id`, `away_team_id` → `dim_team`
- `game_date` → `dim_date`
- Score and meta:
  - `home_goals`, `away_goals`
  - `game_status` (final, scheduled, etc.)
  - `game_location` (rink)
  - `season_id` (optional)

**Used by**

- All facts with a `game_id`:
  - `fact_event`, `fact_event_role`
  - `fact_shift_player`, `fact_shift_line_state`
  - `fact_boxscore_player`
  - `fact_game_roster`
  - `fact_game_coverage`
  - `fact_xy_event`, `fact_xy_shot`

**Source**

- Combination of:
  - BLB master tables (e.g. `dim_schedule` / `fact_gameroster`)
  - Aggregated data from events & shifts.

---

### 1.5 `dim_date`

**Grain**: one row per calendar date.

**Primary key**: `date` (or `date_id` surrogate).

**Typical columns**

- `date`
- `year`, `quarter`, `month`, `day`, `week_of_year`
- `day_of_week`, weekend flag, etc.

**Used by**

- `dim_game` (via `game_date`)
- Any time-series analysis.

**Source**

- BLB master workbook: `BLB_Tables.xlsx` → `dim_dates` (your preferred date table).

---

### 1.6 `dim_event_type` / `dim_event_detail`

**Grain**

- `dim_event_type`: one row per unique event type (SHOT, PASS, TURNOVER, etc.).
- `dim_event_detail`: one row per unique combination of `(event_type, event_detail_1, event_detail_2)`.

**Keys**

- `event_type_id` in `dim_event_type`
- `event_detail_id` in `dim_event_detail`

**Used by**

- `fact_event` and `fact_event_role`:
  - Every event row references `event_type_id` and optionally `event_detail_id`.

**Source**

- Distinct values from `events_long_all` (`event_type`, `event_detail_1`, `event_detail_2`, `play_details_*`).

---

### 1.7 `dim_zone` / `dim_rink_zone`

**Grain**

- One row per logical rink zone (OZ / NZ / DZ, plus finer zones like “high slot”, “behind net”, etc.).

**Primary key**: `zone_id`

**Used by**

- `fact_event` and `fact_xy_event`/`fact_xy_shot` to categorize where events occur.
- Zone entry/exit stats (OZ entry, DZ exit, neutral plays).

**Source**

- Rink coordinate mapping tables (`rinkcoordzones`, `rinkboxcoords`) and derived logic.

---

### 1.8 `dim_strength_situation`

**Grain**: one row per unique combination of strength and situation.

**Primary key**: `strength_situation_id`

**Typical columns**

- `strength` (e.g., 5v5, 5v4, 4v4)
- `situation` (e.g., “Full Strength”, “Delayed Penalty”, “Empty Net”)

**Used by**

- `fact_event`
- `fact_shift_player`
- `fact_shift_line_state`

**Source**

- Distinct combinations from events and shifts stage tables.

---

### 1.9 `dim_sequence` / `dim_play` / `dim_chain_type` (logical plays)

**Grain**

- `dim_sequence`: high-level possession/sequence (can span zones and teams).
- `dim_play`: smaller, same-team & same-zone tactical units (e.g., OZ entry → shot).
- `dim_chain_type`: describes the kind of chain (rush, cycle, counter-rush, etc.).

**Keys**

- `sequence_id`
- `play_id`
- `chain_type_id`

**Used by**

- `fact_event` and `fact_chain_event` to group events into sequences/plays.
- Advanced visualizations and ML around “what leads to goals”.

**Source**

- Computed from events_long using rules on:
  - possession changes
  - zone changes
  - `sequence_index`, `play_index`, `linked_event_index`

---

### 1.10 `dim_video_source`

**Grain**: one row per unique video source (game + camera angle).

**Primary key**: `video_source_id`

**Important columns**

- `video_source_id`
- `game_id`
- `camera_label` (e.g., “Broadcast”, “Behind Net”, etc.)
- `base_youtube_url` (without timestamp)

**Used by**

- `fact_video_bookmark` (jump to specific shift/event).

**Source**

- Master “video links” file per game (or BLB_Tables tab) and per-game video metadata.

---

## 2. Core Fact Tables

These hold the “meat” of your stats and are where measures are defined.

### 2.1 `fact_game_roster`

**Grain**: one row per (game, team, player) for league-provided stats.

**Primary key**: composite `(game_id, team_id, player_id)` or surrogate `game_roster_sk`.

**Key foreign keys**

- `game_id` → `dim_game`
- `player_id` → `dim_player`
- `team_id` → `dim_team`

**Typical measures**

- `goals`, `assists`, `points`, `shots`, `pim`, `plus_minus`, etc.

**Source**

- BLB master: `BLB_Tables.xlsx` → `fact_gameroster` tab.

---

### 2.2 `fact_event` (event header)

**Grain**: one row per **event_index per game**.

**Primary key**

- `event_sk` (e.g., `EV{game_id}{event_index+1000}`)
- Natural key: `(game_id, event_index)`.

**Key foreign keys**

- `game_id` → `dim_game`
- `event_type_id` → `dim_event_type`
- `event_detail_id` → `dim_event_detail`
- `strength_situation_id` → `dim_strength_situation`
- `zone_id` → `dim_zone` (if derived from XY)
- `sequence_id` → `dim_sequence` (if part of a sequence)
- `play_id` → `dim_play`

**Important columns**

- Timing:
  - `period`
  - `event_start_min`, `event_start_sec`
  - `event_end_min`, `event_end_sec`
  - `event_duration`
  - `event_running_start_seconds` (for video join)
- Context:
  - `event_successful`, `play_successful`
  - `home_goals_before`, `away_goals_before`
  - `home_goals_after`, `away_goals_after`
  - On-ice strength/situation
- Derived:
  - `is_shot`, `is_unblocked_shot`, `is_goal`, `is_entry`, `is_exit`, `is_turnover`, etc.
  - Rating context (`event_team_avg_rating_on_ice`, `opp_team_avg_rating_on_ice`).

**Source**

- Stage `events_long_all` (already appended across games), after normalization & enrichment.

---

### 2.3 `fact_event_role` (player involvement per event)

**Grain**: one row per (event, player, role).

**Primary key**

- `event_role_sk` (surrogate), or composite `(game_id, event_index, player_id, role)`.

**Key foreign keys**

- `event_sk` → `fact_event`
- `player_id` → `dim_player`
- `team_id` → `dim_team`
- `role_id` → `dim_player_role` (or simple text column `role`)

**Important columns**

- `role` (event_player_1, event_player_2, opp_player_1, etc.)
- `is_primary_actor` (e.g., shooter, passer, turnover owner)
- Microstats:
  - `shots_for`, `shots_against`, `passes_attempted`, `passes_completed`
  - `giveaways`, `takeaways` (with your refined definitions)
  - Success/failure tags from `event_successful` / `play_successful`.

**Source**

- Derived by **exploding** role columns in `events_long_all` into one row per player+role.

---

### 2.4 `fact_shift_line_state`

**Grain**: one row per (game, period, shift_index) describing **who is on the ice** and the line state.

**Primary key**

- `shift_line_sk` or composite `(game_id, shift_index)`.

**Key foreign keys**

- `game_id` → `dim_game`
- (Optionally) separate link to `fact_shift_player` via `shift_index` + `game_id`.

**Important columns**

- `shift_index`
- `period`
- `shift_start_total_seconds`, `shift_end_total_seconds`, `shift_duration`
- Strength/situation at that segment:
  - `strength`, `situation`
  - `home_team_strength`, `away_team_strength`
- Score state:
  - `home_goals`, `away_goals`
- On-ice players by slot (wide):
  - `home_forward_1`..`home_forward_3`
  - `home_defense_1`..`home_defense_2`
  - `home_goalie`, `home_xtra_*`
  - `away_*` equivalents.

**Source**

- Stage `shifts_wide_all` (already appended across games).

---

### 2.5 `fact_shift_player_onice` (from `shifts_long_all`)

**Grain**: one row per (game, shift_index, player, team_side).

**Primary key**

- Composite `(game_id, shift_index, team_side, player_id)` or surrogate `shift_player_onice_sk`.

**Key foreign keys**

- `game_id` → `dim_game`
- `player_id` → `dim_player`
- `team_id` → `dim_team` (derived from team_side + game)

**Important columns**

- `team_side` (home/away)
- `position_group` (F/D/G)
- `position_slot`
- `shift_start_total_seconds`, `shift_end_total_seconds`
- `shift_duration`
- Score and strength snapshots for that player-row.

**Source**

- Stage `shifts_long_all`, but with `player_number` normalized to `player_id` via `dim_player` lookups.

---

### 2.6 `fact_shift_player` (logical shifts per player)

**Grain**: one row per **logical shift** for each player in each game.

**Primary key**

- `player_shift_sk`
- Natural key: `(game_id, team_side, player_id, logical_shift_id)`.

**Key foreign keys**

- `game_id` → `dim_game`
- `player_id` → `dim_player`
- `team_id` → `dim_team`

**Important columns**

- `period`
- `logical_shift_id`
- `first_shift_index`, `last_shift_index`
- `shift_start_total_seconds`, `shift_end_total_seconds`
- `shift_duration_seconds`
- `num_component_rows` (how many raw segments merged)
- `shift_number_in_game` (running count)
- Score context (start & end goal differentials)
- Strength/situation start fields
- Rating context (teammates/opponents on ice).

**Source**

- Derived from `shifts_long_all` using window functions and grouping (as in your SQL script).

---

### 2.7 `fact_xy_event`

**Grain**: one row per (game, linked_event_index, player or puck location).

**Primary key**

- `xy_event_sk` (or composite of `game_id, linked_event_index, player_id, team_side, role_type`).

**Key foreign keys**

- `game_id` → `dim_game`
- `event_sk` → `fact_event` (via `linked_event_index` → `event_index`)
- `player_id` → `dim_player` (if not the puck)
- `zone_id` → `dim_zone` (via rink coordinate mapping)

**Important columns**

- XY coordinates and derived geometry:
  - `x_coord`, `y_coord`
  - `distance_from_net`, `angle_from_center` (derived)
- Role of this point:
  - `is_puck` (player_number == 'p')
  - `team_side` / `team_indicator` (event team vs opp)
- Context for joining:
  - `linked_event_index`
  - `game_id`
  - Optional `team` (e/o) when jersey numbers overlap.

**Source**

- Combined from per-game CSV files in `xy` or `events`/`shots` folders and rink coordinate dims.

---

### 2.8 `fact_xy_shot`

**Grain**: one row per shot location on the net (using net XY schema).

**Primary key**

- `xy_shot_sk`

**Key foreign keys**

- `game_id` → `dim_game`
- `event_sk` → `fact_event`
- `player_id` → `dim_player` (shooter)
- `zone_id` → `dim_zone` (optional, for shooting lane/angle)

**Important columns**

- Shot location on the net (e.g., from shot-plotter format):
  - `x_net`, `y_net`
  - `shot_target_zone` (high glove, low blocker, etc.)
- Derived metrics:
  - `shot_angle_net`, `shot_height`, etc.

**Source**

- Per-game shot CSVs in `shots/` folder, joined via `linked_event_index` and `game_id`.

---

### 2.9 `fact_boxscore_player`

**Grain**: one row per (game, player, team) with combined basic + advanced stats.

**Primary key**

- `boxscore_sk`
- Natural key: `(game_id, player_id, team_id)`

**Key foreign keys**

- `game_id` → `dim_game`
- `player_id` → `dim_player`
- `team_id` → `dim_team`

**Measures (examples)**

- Basic:
  - `goals`, `assists`, `points`
  - `shots_on_goal`, `shot_attempts` (Corsi)
  - `unblocked_attempts` (Fenwick)
  - `plus_minus`
  - `penalty_minutes`
- Microstats (from event_details & play_details):
  - `zone_entries_controlled`, `zone_entries_dump`, `zone_exits_controlled`
  - `passes_attempted`, `passes_completed`, `pass_completion_pct`
  - `giveaways` (excluding dump/clear/miss criteria)
  - `takeaways`
  - `faceoffs_won`, `faceoffs_lost`
- Rating-aware:
  - `avg_teammate_rating_on_ice`, `avg_opponent_rating_on_ice`
  - `events_vs_stronger_opponents`, `events_vs_weaker_opponents`

**Source**

- Aggregations over:
  - `fact_event`
  - `fact_event_role`
  - `fact_shift_player`
  - Joined to `dim_player` ratings and `dim_team` info.

---

### 2.10 `fact_game_coverage`

**Grain**: one row per game describing tracking coverage and quality flags.

**Primary key**: `game_id` (or `game_coverage_sk` with FK to `dim_game`).

**Key columns**

- Coverage flags:
  - `has_events`, `has_shifts`, `has_xy`, `has_shots`, `has_video`
- Coverage range:
  - `min_tracked_time_seconds`, `max_tracked_time_seconds`
  - per period: `p1_start_tracked`, `p1_end_tracked`, etc.
- Data quality flags:
  - `num_rows_with_errors`
  - `num_negative_durations`
  - `num_events_with_18_min_start`
  - `num_shifts_faceoff_no_stoppage`
  - `num_events_missing_seconds`

**Source**

- QA pass over stage/intermediate tables per game.

---

## 3. Additional Diagnostic / Link Tables

There are a few more tables implied by your long-term goals; these are typically built on top of the core facts above.

### 3.1 `fact_chain_event` / `fact_sequence_event`

**Grain**: one row per (sequence or play, event).

**Purpose**

- Link events into sequences, plays, and chains (rushes, cycles, counter-rushes).
- Make it easy to analyze “what sequences lead to goals”.

**Keys**

- `sequence_id` / `play_id` → `dim_sequence` / `dim_play`
- `event_sk` → `fact_event`

### 3.2 `fact_video_bookmark`

**Grain**: one row per (game, entity → shift or event) with a complete YouTube URL timestamp.

**Keys**

- `video_bookmark_sk`
- `game_id`, and either `event_sk` or `player_shift_sk`

**Columns**

- `video_source_id` → `dim_video_source`
- `start_seconds`
- `youtube_url_with_timestamp` (constructed as `base_url + ?t=start_seconds`)

**Source**

- `video_times` sheet + `event_running_start_seconds` / `shift_running_start_seconds` columns.


---

## 4. Mapping Snapshot Sheets to Final Model

Here is a direct mapping from your current snapshot workbook sheets to the conceptual tables above:

- `dim_player` (sheet) → **`dim_player`**
- `dim_team` (sheet) → **`dim_team`**
- `dim_league` (sheet) → **`dim_league`**
- `fact_gameroster` (BLB_Tables) → **`fact_game_roster`**
- `events_long_all` (sheet) → feeds:
  - **`fact_event`** (event header)
  - **`fact_event_role`** (exploded per player & role)
  - **`fact_chain_event`**, `dim_event_type`, `dim_event_detail`
- `shifts_wide_all` (sheet) → **`fact_shift_line_state`**
- `shifts_long_all` (sheet) → **`fact_shift_player_onice`**
- `player_shifts_all` (sheet) → **`fact_shift_player`**
- `games_coverage` (sheet) → **`fact_game_coverage`**
- Per-game XY and shot CSVs (in folders) → **`fact_xy_event`**, **`fact_xy_shot`**
- Boxscore exports (from previous steps) → **`fact_boxscore_player`**

From these, your **Power BI** and **Dashboard** layers can attach:

- Dim tables on the top (players, teams, dates, event types, zones, sequences)
- Fact tables in the middle (events, shifts, boxscore, roster, coverage)
- Specific report pages for:
  - Game summaries (ESPN/NHL style)
  - Player cards (NHL Edge style)
  - Line combos and matchup analysis
  - Microstats and advanced metrics
  - Sequence / play trees and chain-based xG models

---

This catalog is a living document: as we refine column names and add or drop tables in the code, this should be updated so you always have a **single source of truth** for the schema.
