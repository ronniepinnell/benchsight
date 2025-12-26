
# BenchSight Stats & Microstats Catalog – v4 (Extended)

This document is meant to be **LLM‑friendly** and **human‑readable**.  
Each stat entry is designed so that:
- A human can understand what it means and how to interpret it.
- A language model can see **what inputs are required**, **how it is computed**, and **whether it is available with today’s data or needs more tracking/vision data.**

---

## 1. Columns in This Catalog

For every stat / microstat we try to fill:

- **StatID** – Short stable identifier (good for code / column names).
- **Name** – Friendly name.
- **Category** – Broad bucket (Core, Shot, xG, Micro-Offense, Micro-Defense, Transition, Goalie, Tracking, Lineup, Context, Rating-Aware, Video).
- **Level** – Typical grain: Player‑Game, Player‑Season, Team‑Game, Shift, Event, Line‑Combo, etc.
- **Description** – Plain English explanation of what it measures.
- **FormulaConcept** – Conceptual formula (not SQL, but LLM‑friendly math / pseudo‑code).
- **PrimaryInputs** – Which tables / columns you expect to use in the BenchSight / BLB model (or future tables).
- **FilterContext** – Common filters (e.g. 5v5, score‑tied, regular season, etc.). Can be empty.
- **ComputableNow** – One of:
  - `now_manual_tracking` – can be computed today from the **current tracking schema** (BLB events + shifts + boxscore + XY example).
  - `now_boxscore_only` – can be computed today using only **league box scores** (for untracked games).
  - `needs_xy` – needs consistent rink XY per event/shot.
  - `needs_tracking` – needs per‑frame puck/player tracking (Sportlogiq / NHL Edge style).
  - `needs_video_ml` – needs computer‑vision / pose / puck tracking that does not yet exist in the current data.
- **ExtraDataNeeded** – If not fully computable, what additional data is required.
- **LLMNotes** – Hints for an LLM: how to explain the stat, when to use it, caveats, etc.

---

## 2. High‑Level Categories

The catalog is divided into these conceptual groups (inspired by Evolving‑Hockey, AllThreeZones, JFresh, NaturalStatTrick, NHL Edge, Hudl‑InStat, etc.): 

1. **Core boxscore / deployment** – Goals, assists, TOI, shift counts, penalties, etc.
2. **Shot volume and shot quality** – Corsi, Fenwick, on‑ice shot rates, shot distance/angle, danger tiers.
3. **Expected goals (xG)** – Shot‑level models (per shot) and on‑ice aggregates.
4. **Chance‑based & scoring‑chance stats** – Scoring chances, high‑danger chances, rush vs cycle chances.
5. **Micro‑offense** – passes, dangerous passes, royal‑road feeds, slot passes, OZ possession, cycle length.
6. **Micro‑defense** – denials, breakups, stick checks, shot blocks, retrievals, box‑outs, defensive exits.
7. **Transition / forecheck / breakout** – controlled entries/exits, dump‑and‑chase vs controlled, forecheck pressure.
8. **Goalie metrics** – xG vs actual, rebound control, save types, shot lanes.
9. **Lineup / matchup / with‑or‑without‑you (WOWY)** – QoT/QoC, line combo performance, head‑to‑head results.
10. **Tracking / skating / geometry** – speed, distance, accelerations, lane control, gap, path shapes (future vision work).
11. **Rating‑aware metrics** – Contextualizing events by player ratings (2–6 system in BLB dim_player).
12. **Video‑linked metrics** – Stats that rely on mapping events/shifts to specific video timestamps and clips.

The remainder of this doc gives **examples and representative definitions** from each category.  
The CSV in this bundle contains a **much larger list (70+ stats)** that you can extend further in your repo.

---

## 3. Representative Stats (Examples by Category)

> NOTE: These are *examples*. The CSV file contains many more stats; this section is here so that another LLM (or human) can see the patterns and reuse them.

### 3.1 Core Boxscore / Deployment

1. **StatID**: `G`  
   - **Name**: Goals  
   - **Category**: Core  
   - **Level**: Player‑Game, Player‑Season  
   - **Description**: Number of goals a player scores (any strength state).  
   - **FormulaConcept**: Count of events where `type='shot'` and `event_successful=1` and event is recorded as `goal` for `event_player_1`.  
   - **PrimaryInputs**: `fact_events_long`, columns `type`, `event_detail_1/2`, `event_successful`, `event_player_1_id`.  
   - **FilterContext**: All situations or filtered to 5v5, etc.  
   - **ComputableNow**: `now_manual_tracking`  
   - **ExtraDataNeeded**: None (beyond current BLB tracking).  
   - **LLMNotes**: This is the basic scoring output; combine with TOI to get goals/60.

2. **StatID**: `TOI_EV_60`  
   - **Name**: Even‑Strength Time on Ice per 60 minutes  
   - **Category**: Core  
   - **Level**: Player‑Game, Player‑Season  
   - **Description**: Minutes a player skates at 5v5 per 60 minutes of game time.  
   - **FormulaConcept**:  
     `TOI_EV_60 = (sum(shift_duration_seconds where strength='5v5' for player) / 60) / (game_minutes_played / 60)`  
     For single game, `game_minutes_played` is usually 60 (or 3*period_length).  
   - **PrimaryInputs**: `fact_shifts_player` (logical player shifts), `strength`, `shift_duration_seconds`.  
   - **FilterContext**: `strength='5v5'`.  
   - **ComputableNow**: `now_manual_tracking`  
   - **ExtraDataNeeded**: None.  
   - **LLMNotes**: Use for deployment; players with high EV TOI/60 are heavily used at even strength.

3. **StatID**: `PLUS_MINUS`  
   - **Name**: Plus/Minus  
   - **Category**: Core  
   - **Level**: Player‑Game, Player‑Season  
   - **Description**: Traditional plus/minus: goals for minus goals against at even strength while the player is on the ice.  
   - **FormulaConcept**:  
     - For each goal event at `strength` in {5v5, 4v4, 3v3}, check players on ice at that time.  
     - If team scores and player on scoring team is on the ice: plus += 1.  
     - If team is scored on and player is on ice: minus += 1.  
     - `PLUS_MINUS = plus - minus`.  
   - **PrimaryInputs**: `fact_events_wide` joined to `fact_shifts_on_ice` (player on‑ice matrix).  
   - **FilterContext**: EV only by tradition.  
   - **ComputableNow**: `now_manual_tracking` (requires correct on‑ice model from shifts).  
   - **ExtraDataNeeded**: None.  
   - **LLMNotes**: Legacy stat; often noisy; better to pair with xG‑based on‑ice metrics.

4. **StatID**: `GP`  
   - **Name**: Games Played  
   - **Category**: Core  
   - **Level**: Player‑Season  
   - **Description**: Number of games where player has non‑zero TOI or appears on game roster.  
   - **FormulaConcept**: Count of distinct `game_id` where `player_id` appears in `fact_game_roster` or has any shift.  
   - **PrimaryInputs**: `fact_game_roster`, `fact_shifts_player`.  
   - **ComputableNow**: `now_boxscore_only` if you only have rosters per game.  
   - **ExtraDataNeeded**: None.  
   - **LLMNotes**: Building block for per‑game rates, season totals, and durability metrics.

---

### 3.2 Shot Volume & Shot Quality (Corsi, Fenwick, Danger)

5. **StatID**: `CF`  
   - **Name**: Corsi For  
   - **Category**: Shot  
   - **Level**: Player‑On‑Ice‑Game, Team‑Game, Player‑Season  
   - **Description**: Total shot attempts by player’s team while they are on the ice (shots on goal + missed + blocked).  
   - **FormulaConcept**:  
     For each event where `type in {shot, miss, block}` and team is the player’s team and player is on ice:  
     `CF += 1`.  
   - **PrimaryInputs**: `fact_events_long` (to classify events), `fact_shifts_on_ice` (who is on).  
   - **FilterContext**: 5v5, score‑tied, regular season.  
   - **ComputableNow**: `now_manual_tracking` (once you tag miss/block events consistently).  
   - **ExtraDataNeeded**: For NHL data: official shot/miss/block feeds.  
   - **LLMNotes**: Corsi is a proxy for puck possession and territorial advantage.

6. **StatID**: `FF`  
   - **Name**: Fenwick For  
   - **Category**: Shot  
   - **Description**: Like Corsi but **excludes blocked shots**. Often used as a slightly “cleaner” shot‑quality proxy.  
   - **FormulaConcept**:  
     Same as CF but only `type in {shot, miss}`.  

7. **StatID**: `HDCF`  
   - **Name**: High‑Danger Corsi For  
   - **Category**: Shot  
   - **Level**: Player‑On‑Ice‑Game, Team‑Game  
   - **Description**: Shot attempts from **high‑danger** areas (e.g. inner slot) while the player is on ice.  
   - **FormulaConcept**:  
     Use XY coordinates or zone labels (e.g. `danger_zone='high'`). Count Corsi events with `danger_zone='high'` for player’s team while player is on ice.  
   - **PrimaryInputs**: `fact_events_xy`, `dim_rink_zones`, `fact_shifts_on_ice`.  
   - **ComputableNow**: `needs_xy` for your league.  
   - **ExtraDataNeeded**: Reliable XY per event and a zone definition (rink coord tables already started).  
   - **LLMNotes**: Mirrors sites like NaturalStatTrick and HockeyViz high‑danger metrics.

8. **StatID**: `SHOT_DISTANCE`  
   - **Name**: Shot Distance (ft)  
   - **Category**: Shot  
   - **Level**: Event (shot)  
   - **Description**: Distance from shooter’s location to the net at time of shot.  
   - **FormulaConcept**:  
     `distance = sqrt((x - net_x)^2 + (y - net_y)^2)` in rink coordinates.  
   - **PrimaryInputs**: `fact_events_xy` for shots, `dim_rink_goal_location`.  
   - **ComputableNow**: `needs_xy`  
   - **ExtraDataNeeded**: XY locations and consistent rink orientation.  
   - **LLMNotes**: Input feature for xG models; shorter distance → higher xG on average.

---

### 3.3 Expected Goals (xG)

9. **StatID**: `xG_SHOT`  
   - **Name**: Shot‑Level Expected Goals  
   - **Category**: xG  
   - **Level**: Event (shot)  
   - **Description**: Probability a single shot becomes a goal, based on historical shot outcomes.  
   - **FormulaConcept**:  
     Train a model:  
     `P(goal | distance, angle, shot_type, pre-shot movement, rebound, rush, score, time, etc.)`.  
   - **PrimaryInputs**: Shot event features incl. `SHOT_DISTANCE`, angle, rebound flag, rush flag, pre‑shot pass, etc.  
   - **ComputableNow**: `needs_xy` + `needs_model_training`.  
   - **ExtraDataNeeded**: Large historical dataset of shots with outcomes, plus engineered features.  
   - **LLMNotes**: Foundation for xG metrics; heavy inspiration from Evolving‑Hockey, MoneyPuck, JFresh models.

10. **StatID**: `xGF_ON`  
    - **Name**: On‑Ice Expected Goals For  
    - **Category**: xG  
    - **Level**: Player‑On‑Ice‑Game / Season  
    - **Description**: Sum of xG for all shots taken by player’s team while they are on ice.  
    - **FormulaConcept**:  
      `xGF_ON = Σ xG_SHOT for shots where shooting_team == player_team and player is on ice`.  
    - **ComputableNow**: `needs_xy` + xG model.  

11. **StatID**: `GSAx`  
    - **Name**: Goals Saved Above Expected  
    - **Category**: Goalie/xG  
    - **Level**: Goalie‑Game, Goalie‑Season  
    - **Description**: How many goals a goalie prevented relative to expected, given shot quality.  
    - **FormulaConcept**:  
      `GSAx = Σ xG_SHOT_faced - goals_allowed`.  
    - **PrimaryInputs**: Shot events vs goalie, xG_SHOT, goals allowed.  
    - **ComputableNow**: `needs_xy` + xG model.  

---

### 3.4 Micro‑Offense (Passes, Entries, OZ Play)

12. **StatID**: `CONTROLLED_ENTRY_FOR`  
    - **Name**: Controlled Zone Entries For  
    - **Category**: Micro‑Offense / Transition  
    - **Level**: Player‑Game, Team‑Game  
    - **Description**: Number of times a player or team enters the offensive zone with **possession** (carry or successful pass).  
    - **FormulaConcept**:  
      Count events where `type='zone_entry'` and `event_detail_1 in {'carry','pass'}` and `event_successful=1`. Attribute to `event_player_1` and team.  
    - **PrimaryInputs**: `fact_events_long`, event type/detail columns; optionally XY to validate crossing blue line.  
    - **ComputableNow**: `now_manual_tracking` if zone_entry events are recorded.  

13. **StatID**: `ROYAL_ROAD_PASS_FOR`  
    - **Name**: Royal‑Road Passes For  
    - **Category**: Micro‑Offense  
    - **Description**: Completed passes that cross the “royal road” (center line in offensive zone) creating lateral goalie movement.  
    - **FormulaConcept**:  
      - Use pre- and post‑pass XY.  
      - A pass is royal‑road if y‑coordinate changes sign across center or crosses a defined central lane.  
      - Count only successful passes in OZ.  
    - **PrimaryInputs**: `fact_events_xy_pass`, `dim_rink_zones`, pass events.  
    - **ComputableNow**: `needs_xy`.  

14. **StatID**: `OZ_CYCLE_TIME`  
    - **Name**: Offensive Zone Cycle Time  
    - **Category**: Micro‑Offense / Possession  
    - **Level**: Team‑Game, Sequence‑Level  
    - **Description**: Average time a team maintains continuous offensive‑zone possession (no clear, no change of possession).  
    - **FormulaConcept**:  
      For each OZ possession segment in `fact_sequences`: `duration = end_time - start_time`.  
      `OZ_CYCLE_TIME = avg(duration)` across game/season.  
    - **ComputableNow**: `now_manual_tracking` if sequences and possession are derived from event chains.  

---

### 3.5 Micro‑Defense (Denials, Retrivals, Breakups)

15. **StatID**: `ENTRY_DENIAL`  
    - **Name**: Zone Entry Denials  
    - **Category**: Micro‑Defense / Transition  
    - **Level**: Player‑Game  
    - **Description**: Number of times a defender prevents an attempted zone entry at their blue line.  
    - **FormulaConcept**:  
      Count events where `type='zone_entry'` and `event_successful=0` and `event_detail_1 in {'carry','pass'}` and defender is `event_player_1` or `opp_player_1` depending on perspective.  
    - **PrimaryInputs**: `fact_events_long`, event details; optionally XY to confirm location near blue line.  
    - **ComputableNow**: `now_manual_tracking` if denial events or failed entries are logged.  

16. **StatID**: `DZ_RETRIEVAL_WON`  
    - **Name**: Defensive Zone Puck Retrievals Won  
    - **Category**: Micro‑Defense  
    - **Description**: Times a defender recovers a loose puck in DZ under pressure and retains possession.  
    - **FormulaConcept**:  
      Count events where `type='retrieval'` and zone='DZ' and `event_successful=1`.  
    - **PrimaryInputs**: Microstat events from BLB tracker; XY optional.  
    - **ComputableNow**: `now_manual_tracking` if retrieval events exist.  

---

### 3.6 Transition, Forecheck, Counter‑Rush

17. **StatID**: `RUSH_CHANCE_FOR`  
    - **Name**: Rush Chances For  
    - **Category**: Transition  
    - **Description**: Shot attempts generated within a short time window (e.g. 3–5s) of a controlled exit + entry (full‑ice rush).  
    - **FormulaConcept**:  
      In `fact_sequences` (rush sequences): if sequence contains DZ exit with control → NZ possession → OZ entry with control → shot within N seconds, count as rush chance.  
    - **ComputableNow**: `now_manual_tracking` when sequences & chain tables are built.  

18. **StatID**: `COUNTER_RUSH_AGAINST`  
    - **Name**: Counter‑Rush Chances Against  
    - **Category**: Transition  
    - **Description**: After a failed offensive play (giveaway / missed shot), opponent rushes and generates a chance quickly.  
    - **FormulaConcept**:  
      For each turnover or broken OZ play, search next few seconds for an opponent rush sequence with a shot; count against players on ice and originator of turnover.  
    - **ComputableNow**: `now_manual_tracking` plus chain linking; may be approximate at first.  

---

### 3.7 Goalie Metrics

19. **StatID**: `REB_SHOTS_ALLOWED`  
    - **Name**: Rebound Shots Allowed  
    - **Category**: Goalie / xG  
    - **Description**: Number of shots against that occur within a short time window after an initial save (unsuccessful freeze).  
    - **FormulaConcept**:  
      For each shot saved by goalie, if another shot occurs within N seconds and within DZ, count as rebound shot.  
    - **PrimaryInputs**: Event chains, shot types, goalie ID.  
    - **ComputableNow**: `now_manual_tracking` if linked events exist.  

20. **StatID**: `HIGH_DANGER_SV_PCT`  
    - **Name**: High‑Danger Save Percentage  
    - **Category**: Goalie / Shot  
    - **Description**: Save% for high‑danger shots faced.  
    - **FormulaConcept**:  
      `HD_SV% = (HD_shots_faced - HD_goals_allowed) / HD_shots_faced`.  
    - **PrimaryInputs**: `fact_events_xy` for danger zones; goalie events.  
    - **ComputableNow**: `needs_xy` unless danger is encoded as a discrete column.  

---

### 3.8 Lineup / Matchup / WOWY

21. **StatID**: `LINE_CF_PER60`  
    - **Name**: Line Corsi For per 60  
    - **Category**: Lineup  
    - **Level**: Line‑Combo‑Game / Season  
    - **Description**: Shot attempts for by a forward line when that specific trio is on the ice together.  
    - **FormulaConcept**:  
      - Identify segments of time where the three forwards and two defensemen form a stable unit.  
      - Compute Corsi For / TOI * 60.  
    - **PrimaryInputs**: `fact_shifts_player`, `fact_lines_on_ice`, `fact_events`.  
    - **ComputableNow**: `now_manual_tracking`.  

22. **StatID**: `WOWY_GF_DIFF`  
    - **Name**: With‑or‑Without‑You Goal Differential  
    - **Category**: Lineup  
    - **Description**: Goal differential for Teammate X with focal player vs without focal player.  
    - **FormulaConcept**:  
      - Compute `GF%` for segments where both Player A and Teammate B are on ice.  
      - Compute `GF%` where B is on but A is not.  
      - `WOWY_GF_DIFF = GF%(with A) - GF%(without A)`.  
    - **PrimaryInputs**: On‑ice matrix, goal events.  
    - **ComputableNow**: `now_manual_tracking` or `now_boxscore_only` if on‑ice is known from shifts in league feed.  

---

### 3.9 Tracking & Vision‑Heavy Stats (Future)

23. **StatID**: `SKATE_SPEED_MAX`  
    - **Name**: Max Skating Speed  
    - **Category**: Tracking  
    - **Level**: Player‑Game  
    - **Description**: Highest instantaneous speed measured by player within a game.  
    - **FormulaConcept**:  
      `speed_t = distance(position_t, position_{t-1}) / Δt; SKATE_SPEED_MAX = max(speed_t)`.  
    - **PrimaryInputs**: Player coordinates at high frequency (NHL Edge style).  
    - **ComputableNow**: `needs_tracking`.  

24. **StatID**: `ACCEL_RUSH`  
    - **Name**: Rush Acceleration Burst  
    - **Category**: Tracking / Transition  
    - **Description**: Peak acceleration during OZ rush sequences.  
    - **FormulaConcept**:  
      `accel_t = (speed_t - speed_{t-1}) / Δt; track during rush sequences and take max`.  
    - **ComputableNow**: `needs_tracking`.  

25. **StatID**: `DEFENSIVE_GAP_AVG`  
    - **Name**: Average Defensive Gap  
    - **Category**: Tracking / Defense  
    - **Description**: Average distance between defender and puck carrier in OZ / NZ.  
    - **FormulaConcept**:  
      For frames where a defender is the closest to puck carrier: measure distance; average.  
    - **ComputableNow**: `needs_tracking` + identity of puck carrier per frame.  

26. **StatID**: `SHOT_RELEASE_TIME`  
    - **Name**: Shot Release Time  
    - **Category**: Tracking / Shooting  
    - **Description**: Time from receiving pass or puck control to shot release.  
    - **FormulaConcept**:  
      `release_time = t_shot - t_previous_possession_event`.  
    - **ComputableNow**: `needs_video_ml` unless tracking feed includes event timestamps.  

---

### 3.10 Rating‑Aware Context Stats

27. **StatID**: `GIVEAWAY_VS_ELITE`  
    - **Name**: Giveaways vs Elite Opponents  
    - **Category**: Rating‑Aware / Micro‑Offense  
    - **Description**: Number of giveaways a player commits while facing opponents with **average rating >= 5** on the ice.  
    - **FormulaConcept**:  
      For each giveaway event attributed to player, compute average opponent rating from `dim_player.rating` for all opponents on ice; if ≥ threshold, increment counter.  
    - **ComputableNow**: `now_manual_tracking` with ratings.  

28. **StatID**: `OZ_TIME_VS_WEAK`  
    - **Name**: Offensive Zone Time vs Weaker Matchups  
    - **Category**: Rating‑Aware  
    - **Description**: Portion of OZ TOI where player’s line has higher average rating than opposing line.  
    - **FormulaConcept**:  
      For each OZ possession segment with player on ice, if avg_team_rating > avg_opp_rating, add segment duration; divide by total OZ TOI.  

29. **StatID**: `CHAIN_XG_ADJUSTED_FOR_RATINGS`  
    - **Name**: Sequence xG Adjusted for Ratings  
    - **Category**: Rating‑Aware / xG  
    - **Description**: Expected goals for a sequence adjusted for both attacking and defending line strength (ratings).  
    - **FormulaConcept**:  
      `xG_adj = xG_seq * f(avg_att_rating, avg_def_rating)` where f increases xG when attackers are strong and defenders are weak, etc.  
    - **ComputableNow**: `needs_modeling` but uses existing rating + xG infrastructure.

---

### 3.11 Video‑Linked Metrics

30. **StatID**: `CLIP_COUNT_PER_EVENT_TYPE`  
    - **Name**: Clips per Event Type  
    - **Category**: Video  
    - **Level**: Player‑Game / Coach‑View  
    - **Description**: Number of video clips generated for a given event type (e.g. OZ entries, turnovers) for a player or team.  
    - **FormulaConcept**:  
      For each event where `video_url_start` not null and `type=target_type`, count 1.  
    - **ComputableNow**: `now_manual_tracking` once video linking table exists.  

31. **StatID**: `WATCH_TIME_PER_PLAYER`  
    - **Name**: Total Watch Time of Clips per Player  
    - **Category**: Video / Coaching Analytics  
    - **Description**: Total length of video clips generated for a player’s events.  
    - **FormulaConcept**:  
      Sum `(clip_end - clip_start)` for all clips tied to that player’s events.  
    - **ComputableNow**: `now_manual_tracking` with clip metadata.  

---

## 4. Using Only Basic Boxscore Data (Untracked Games)

For games where you **only have league box scores and rosters** (e.g. from NORAD Hockey, HockeyDB, or your league website), you can still compute a subset of advanced‑style stats:

Examples:

1. **Team Shot Rates** (approximate)  
   - Inputs: Shots, Goals, Shots Against, Goals Against, TOI.  
   - Stats: `SF/60`, `SA/60`, `GF/60`, `GA/60`, `GoalDiff/60`.  
   - Use: Benchmark team‑level performance vs manually tracked games.

2. **On‑Ice Shot Share Proxies**  
   - If you know per‑player TOI and team shot totals in those minutes, you can approximate:  
     `Player Shot Rate Contribution ≈ (TeamShots * PlayerTOI / TotalTeamSkaterTOI)` as a rough proxy.

3. **Usage & Deployment Profiles**  
   - `TOI% = PlayerTOI / TotalTeamSkaterTOI`.  
   - Special teams: If you have PP/PK TOI splits, derive PP specialist / PK specialist labels.

4. **On‑Ice Goal Share / Relative Goal Share**  
   - `GF% = GF / (GF + GA)` while player is on ice (if recorded in league stats).  
   - Compare to team GF% without player to get a basic WOWY‑style metric.

5. **Rating‑Based Context Regressions**  
   - Even if you do not have microstats, you can model:  
     `Team GF/60 ~ sum(player_rating * TOI_share)`  
   - Use ridge regression to build **Adjusted Plus‑Minus** approximations using goals, shots, Fenwick, and Corsi analogues, similar to academic work. citeturn1academia20

In the CSV, we flag these stats with `ComputableNow = now_boxscore_only` and describe exactly which boxscore fields are needed.

---

## 5. Files in This Bundle

This zip bundle contains:

1. **`benchsight_stats_catalog_v4.csv`**  
   - Machine‑readable catalog of ~80 stats and microstats with the columns described above.

2. **`benchsight_stats_catalog_v4.md`**  
   - This human‑oriented explanation plus the full table in Markdown form.

3. **`benchsight_stats_catalog_v4_README.txt`**  
   - Short “how to use” guide for humans and LLMs:  
     - How to look up a stat.  
     - How to see what data it needs.  
     - How to extend with new stats as the tracking and vision stack improves.

You can drop these into your project’s `/docs/stats/` folder and reference them from other tools or LLMs.


---

| StatID                | Name                           | Category      | Level                        | Description                                                                          | FormulaConcept                                                                                            | PrimaryInputs                                                              | FilterContext   | ComputableNow       | ExtraDataNeeded                                        | LLMNotes                                                                   |
|:----------------------|:-------------------------------|:--------------|:-----------------------------|:-------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------|:----------------|:--------------------|:-------------------------------------------------------|:---------------------------------------------------------------------------|
| G                     | Goals                          | Core          | Player-Game,Player-Season    | Number of goals scored by the player.                                                | Count events where type='shot' and event_successful=1 and credited as goal to event_player_1.             | fact_events_long(type,event_successful,event_player_1_id)                  |                 | now_manual_tracking |                                                        | Use with TOI or shots to compute rates like goals/60 or shooting%.         |
| A1                    | Primary Assists                | Core          | Player-Game,Player-Season    | Assists that are the final pass before a goal.                                       | Count goal events where player appears as primary assister in play_detail or event_details_1/2.           | fact_events_long(type,play_details_1,play_details_2,event_player_1_id,...) |                 | now_manual_tracking | Needs consistent encoding of assist roles.             | Primary assists often better reflect playmaking than total assists.        |
| A2                    | Secondary Assists              | Core          | Player-Game,Player-Season    | Assists that are one step removed from the goal (secondary pass).                    | Similar to A1 but for secondary assist tags in play detail columns.                                       | fact_events_long(play_details_1,play_details_2)                            |                 | now_manual_tracking | Assist tagging scheme in tracker.                      | Separate from A1 so you can compute A1/A2 mix.                             |
| PTS                   | Points                         | Core          | Player-Game,Player-Season    | Goals + assists.                                                                     | PTS = G + (A1 + A2).                                                                                      | Derived from G,A1,A2                                                       |                 | now_manual_tracking |                                                        | Traditional scoring stat; use with TOI for points/60.                      |
| TOI_EV_60             | Even-Strength TOI per 60       | Core          | Player-Game,Player-Season    | Even-strength time on ice normalized per 60 minutes.                                 | TOI_EV_60 = (sum(shift_duration where strength='5v5') / 60).                                              | fact_shifts_player(shift_duration_seconds,strength)                        | strength='5v5'  | now_manual_tracking |                                                        | Captures 5v5 deployment; compare across games or players.                  |
| PLUS_MINUS            | Plus / Minus                   | Core          | Player-Game,Player-Season    | Goal differential while player is on ice at even strength.                           | PLUS_MINUS = goals_for_on_ice - goals_against_on_ice (EV situations).                                     | fact_events_wide,fact_shifts_on_ice                                        | 5v5 or EV only  | now_manual_tracking |                                                        | Legacy metric; noisy, but familiar for coaches and players.                |
| CF                    | Corsi For                      | Shot          | Player-On-Ice-Game,Team-Game | Shot attempts for while the player/team is on the ice (shots+misses+blocks).         | Count events where type in {shot,miss,block} and on-ice team is shooting team.                            | fact_events_long,fact_shifts_on_ice                                        | 5v5,score-tied  | now_manual_tracking | Need miss & block events consistently logged.          | Puck-possession proxy; use with CA for Corsi%.                             |
| CA                    | Corsi Against                  | Shot          | Player-On-Ice-Game,Team-Game | Shot attempts against while player is on ice.                                        | Same as CF but for opponent team.                                                                         | fact_events_long,fact_shifts_on_ice                                        | 5v5,score-tied  | now_manual_tracking |                                                        | Combine with CF for Corsi differential and share.                          |
| CF_PCT                | Corsi Percentage               | Shot          | Player-On-Ice-Game,Team-Game | Share of Corsi attempts for vs total when player is on ice.                          | CF_PCT = CF / (CF + CA).                                                                                  | Derived from CF,CA                                                         | 5v5,score-tied  | now_manual_tracking |                                                        | Key shot share metric; used heavily in public analytics.                   |
| FF                    | Fenwick For                    | Shot          | Player-On-Ice-Game,Team-Game | Unblocked shot attempts for (shots+misses).                                          | Count type in {shot,miss} for team while player on ice.                                                   | fact_events_long,fact_shifts_on_ice                                        | 5v5,score-tied  | now_manual_tracking |                                                        | Similar to CF but slightly closer to goal probability.                     |
| HDCF                  | High-Danger Corsi For          | Shot          | Player-On-Ice-Game,Team-Game | Shot attempts from high-danger areas while player is on ice.                         | Count Corsi events where danger_zone='high' or shot_xy in HD polygon.                                     | fact_events_xy,dim_rink_zones,fact_shifts_on_ice                           | 5v5,score-tied  | needs_xy            | Danger classification or polygons per rink.            | Mirrors public HD metrics; useful for chance quality, not just volume.     |
| SHOT_DIST             | Shot Distance                  | Shot          | Event                        | Distance from shot location to net (feet).                                           | sqrt((x - net_x)^2 + (y - net_y)^2) in rink coords.                                                       | fact_events_xy,dim_rink_goal_location                                      |                 | needs_xy            | Consistent coordinate system per rink.                 | Important feature for xG and shot profiling.                               |
| SHOT_ANGLE            | Shot Angle                     | Shot          | Event                        | Angle of shot relative to center of net.                                             | atan2(|y - net_y|, |x - net_x|) in degrees.                                                               | fact_events_xy,dim_rink_goal_location                                      |                 | needs_xy            |                                                        | Combined with distance; steep angles usually lower xG.                     |
| xG_SHOT               | Shot-Level Expected Goals      | xG            | Event                        | Probability a single shot becomes a goal.                                            | xG = model(distance,angle,shot_type,pre-shot movement,rebound,rush,etc).                                  | fact_events_xy,shot features,trained ML model                              |                 | needs_xy            | Training data of many shots with outcomes + model.     | Core feature of modern hockey analytics (Evolving-Hockey/MoneyPuck style). |
| xGF_ON                | On-Ice Expected Goals For      | xG            | Player-On-Ice-Game,Team-Game | Sum of xG for shots taken by team while player is on ice.                            | xGF_ON = Σ xG_SHOT where shooting_team==player_team and player on ice.                                    | xG_SHOT,fact_shifts_on_ice                                                 | 5v5,score-tied  | needs_xy            | xG_SHOT values must be computed first.                 | Better on-ice measure than raw GF; adjusts for shot quality.               |
| xGA_ON                | On-Ice Expected Goals Against  | xG            | Player-On-Ice-Game,Team-Game | Sum of xG for shots against while player is on ice.                                  | xGA_ON = Σ xG_SHOT where shooting_team!=player_team and player on ice.                                    | xG_SHOT,fact_shifts_on_ice                                                 | 5v5,score-tied  | needs_xy            |                                                        | Use with xGF_ON to build xGF% and expected goal differential.              |
| xGF_PCT               | xG Percentage                  | xG            | Player-On-Ice-Game,Team-Game | Share of expected goals for vs total while player is on ice.                         | xGF_PCT = xGF_ON / (xGF_ON + xGA_ON).                                                                     | Derived from xGF_ON,xGA_ON                                                 | 5v5,score-tied  | needs_xy            |                                                        | Key quality-adjusted territorial metric.                                   |
| CONTROLLED_ENTRY_FOR  | Controlled Zone Entries For    | Transition    | Player-Game,Team-Game        | Entries into OZ with possession (carry or completed pass).                           | Count events where type='zone_entry' and event_detail_1 in {'carry','pass'} and event_successful=1.       | fact_events_long(type,event_detail_1,event_successful,event_player_1_id)   |                 | now_manual_tracking | Zone_entry tagging must be consistent.                 | Microstat widely used by AllThreeZones/JFresh; correlates with offense.    |
| DUMP_ENTRY_FOR        | Dump-and-Chase Entries For     | Transition    | Player-Game,Team-Game        | Zone entries where team sends puck in without immediate possession (dump, chip).     | Count events type='zone_entry' and event_detail_1 in {'dump','chip'}                                      | fact_events_long                                                           |                 | now_manual_tracking |                                                        | Lets you compare controlled vs dump entry profiles.                        |
| CONTROLLED_ENTRY_RATE | Controlled Entry Rate          | Transition    | Player-Game,Team-Game        | Share of entries that are controlled.                                                | CONTROLLED_ENTRY_RATE = CONTROLLED_ENTRY_FOR / (CONTROLLED_ENTRY_FOR + DUMP_ENTRY_FOR).                   | Derived from entry stats                                                   |                 | now_manual_tracking |                                                        | Higher values suggest better transition puck management.                   |
| ENTRY_DENIAL          | Entry Denials                  | Micro-Defense | Player-Game                  | Number of times player stops an opposition entry at blue line.                       | Count zone_entry attempts by opponent where event_successful=0 and defender is event_player_1.            | fact_events_long                                                           |                 | now_manual_tracking | Defensive attribution logic.                           | Key defensive microstat; especially for defensemen.                        |
| DZ_EXIT_CONTROLLED    | Controlled DZ Exits            | Transition    | Player-Game                  | Defensive-zone exits where team leaves zone with possession.                         | Count events type='zone_exit' and event_detail_1 in {'carry','pass'} and success=1.                       | fact_events_long                                                           |                 | now_manual_tracking |                                                        | Important for breakout analysis and puck-moving defense.                   |
| RUSH_CHANCE_FOR       | Rush Chances For               | Transition    | Player-Game,Team-Game        | Shots or chances generated quickly after a full-ice rush.                            | Identify sequences: DZ exit with control → NZ possession → OZ entry with control → shot within N seconds. | fact_sequences,fact_events_long                                            |                 | now_manual_tracking | Sequence table linking events in time.                 | Used in many public models to distinguish rush vs cycle offense.           |
| GIVEAWAY              | Giveaways                      | Micro-Offense | Player-Game                  | Times a player loses puck directly to opponent while under control.                  | Count events type='turnover' where event_player_1 is giver and not an intentional dump/clear/miss shot.   | fact_events_long(type,event_detail_1,play_details_1)                       |                 | now_manual_tracking | Classification rules distinguishing dumps vs mistakes. | You requested refined giveaways excluding dumps/clears/miss shots.         |
| TAKEAWAY              | Takeaways                      | Micro-Defense | Player-Game                  | Times player steals puck from opponent, gaining possession.                          | Count events type in {'takeaway','stick_lift','interception'} credited to player.                         | fact_events_long                                                           |                 | now_manual_tracking | Event taxonomy for steals.                             | Important defensive disruptor microstat.                                   |
| OZ_POSSESSION_TIME    | Offensive Zone Possession Time | Micro-Offense | Team-Game,Player-Game        | Time spent controlling puck in offensive zone.                                       | Sum durations of sequences labeled zone='OZ' and possession_team=team.                                    | fact_sequences                                                             |                 | now_manual_tracking | Need clear sequences and possession logic.             | Cycle-heavy teams will show high OZ possession time.                       |
| GSAx                  | Goals Saved Above Expected     | Goalie        | Goalie-Game,Goalie-Season    | How many goals a goalie prevents relative to expected based on shot quality.         | GSAx = Σ xG_SHOT_faced - goals_allowed.                                                                   | xG_SHOT,goal events by goalie                                              |                 | needs_xy            | Goalie attribution + xG model.                         | Key modern goalie stat; used widely by Evolving-Hockey/MoneyPuck.          |
| HD_SV_PCT             | High-Danger Save Percentage    | Goalie        | Goalie-Game,Goalie-Season    | Save percentage on high-danger shots.                                                | HD_SV% = (HD_shots_faced - HD_goals_allowed) / HD_shots_faced.                                            | fact_events_xy,goalie_id,danger_zone                                       |                 | needs_xy            | Danger zone classification for shots.                  | Evaluates performance on toughest chances.                                 |
| LINE_CF_PER60         | Line Corsi For per 60          | Lineup        | Line-Combo-Game,Season       | Shot attempts for per 60 whilst a specific line combo is on ice.                     | CF per line / TOI_line * 60.                                                                              | fact_lines_on_ice,fact_events_long                                         | 5v5             | now_manual_tracking | Line identification from shifts.                       | For optimizing line combos and matchups.                                   |
| WOWY_GF_DIFF          | WOWY Goal Diff                 | Lineup        | Pair-Season                  | Change in GF% for a player when a specific teammate is with vs without them.         | WOWY_GF_DIFF = GF%(with) - GF%(without).                                                                  | on-ice tables,goal events                                                  | 5v5             | now_manual_tracking |                                                        | Used for with-or-without-you evaluation and player synergy.                |
| SKATE_SPEED_MAX       | Max Skate Speed                | Tracking      | Player-Game                  | Highest instantaneous skating speed.                                                 | speed_t = distance(pos_t,pos_{t-1})/Δt; SKATE_SPEED_MAX = max(speed_t).                                   | high-frequency tracking positions                                          |                 | needs_tracking      | Per-frame positions for players.                       | NHL Edge publishes similar speed metrics.                                  |
| ACCEL_RUSH            | Rush Acceleration              | Tracking      | Player-Game                  | Peak acceleration during rush sequences.                                             | During rush segments, accel_t=(speed_t-speed_{t-1})/Δt; take max.                                         | tracking positions,sequence labels                                         |                 | needs_tracking      |                                                        | Differentiate elite rush skaters from slower players.                      |
| DEF_GAP_AVG           | Average Defensive Gap          | Tracking      | Player-Game                  | Average distance between defender and puck carrier in NZ/OZ.                         | At each frame, identify nearest defender to carrier; average separation.                                  | tracking positions + puck carrier id                                       |                 | needs_tracking      |                                                        | Key concept in modern defensive coaching.                                  |
| GIVEAWAY_VS_ELITE     | Giveaways vs Elite Opponents   | Rating-Aware  | Player-Season                | Giveaways a player commits while facing lines with avg rating ≥ threshold.           | For each giveaway, compute avg opponent rating on ice; count if >= threshold.                             | fact_events_long,fact_shifts_on_ice,dim_player.rating                      |                 | now_manual_tracking |                                                        | Provides rating-aware turnover context (your request).                     |
| OZ_TIME_VS_WEAK       | OZ Time vs Weaker Lines        | Rating-Aware  | Player-Season                | Proportion of OZ possession time when player’s line is higher-rated than opponent’s. | Sum OZ possession where team_avg_rating > opp_avg_rating / total OZ time.                                 | fact_sequences,dim_player.rating,fact_shifts_on_ice                        |                 | now_manual_tracking | Ratings for all players.                               | Contextualizes OZ dominance vs matchup difficulty.                         |
| CHAIN_XG_RATING_ADJ   | Rating-Adjusted Sequence xG    | Rating-Aware  | Sequence                     | xG for a sequence adjusted for offensive and defensive line ratings.                 | xG_adj = base_xG * f(avg_att_rating,avg_def_rating).                                                      | fact_sequences_xg,dim_player.rating                                        |                 | needs_xy            | Model for f and sequence xG.                           | Brings your rating system into expected-goals logic.                       |
| CLIP_COUNT_ENTRY      | Entry Clips Count              | Video         | Player-Game                  | Number of video clips generated for OZ entries by player.                            | Count events type='zone_entry' with non-null video_url_start for player.                                  | fact_events_long,fact_video_links                                          |                 | now_manual_tracking | Video-link ETL step.                                   | Useful for film review workloads: how many clips to watch.                 |
| WATCH_TIME_PLAYER     | Clip Watch Time per Player     | Video         | Player-Game                  | Total duration of all video clips tagged to player’s events.                         | Sum(clip_end - clip_start) across all clips for player.                                                   | fact_video_links                                                           |                 | now_manual_tracking | Clip duration metadata.                                | Can be used to size coaching workload or generate auto-reels.              |