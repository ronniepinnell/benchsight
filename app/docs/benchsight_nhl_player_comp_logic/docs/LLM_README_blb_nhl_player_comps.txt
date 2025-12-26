Benchsight – BLB vs NHL Player Comparison Logic (LLM README)
============================================================

This README is written for an LLM that is helping develop / extend the Benchsight project.

High–level purpose
------------------
Benchsight has two data "universes":

  1. BLB (Beer League Beauties) tracking data:
     - Very granular microstats: custom events, shifts, chains, x/y coordinates, video-linked plays.
     - Small number of games, high feature richness.
  2. NHL public data (e.g., MoneyPuck, NHL API, Natural Stat Trick, etc.):
     - Many games and seasons, but less granular (mostly event-/shot-/shift-level, fewer microstats).

The goal of the BLB–NHL comparison layer is:
  - For each BLB player–season (or game), find *similar* NHL players.
  - Use these comps to:
      * contextualize BLB performance (e.g., "most like Cale Makar 2023–24"),
      * suggest realistic development paths,
      * measure BLB players against pro-like archetypes.

This file explains the *logic only* (not the code) and points you to the relevant tables and stats
that other docs describe in more detail.

Where to look in this zip
-------------------------
- `stats_catalog/benchsight_stats_catalog_master.csv`
    Master catalog of all stats and microstats available or planned, across BLB and NHL contexts.
    Columns include name, definition, formula, required tables, filters, normalization notes, etc.

- `tables_catalog/benchsight_tables_catalog.csv`
    List of all core tables in the BLB datamart (dim/fact), with keys, grain, and join paths.

- `docs/benchsight_nhl_resources_and_strategy.txt`
    Overview of external NHL data sources and how they can feed the project.

- `docs/benchsight_blb_nhl_player_comp_logic.txt`
    This is the human-facing detailed logic explanation that mirrors (and expands on) this LLM README.

- `docs/roadmap/benchsight_roadmap_and_checklist.txt`
    Overall short-/mid-/long-term roadmap. The BLB–NHL comp work is a "Mid-Term" and "Long-Term" item.

Conceptual architecture for player comps
----------------------------------------
To reason about BLB–NHL comps, treat it as a small "sub-mart" layered on top of:

  - BLB datamart:
      * `fact_player_boxscore` (or equivalent final player-game/match table)
      * `dim_player`, `dim_team`, `dim_game`, `dim_season`
  - NHL datamart:
      * `fact_nhl_player_stats` (one row per NHL player-season or player-game)
      * same-style dims: `dim_nhl_player`, `dim_nhl_team`, `dim_nhl_season`, `dim_nhl_game`

The comparison layer primarily introduces three conceptual objects:

  1. A *feature space* shared by BLB and NHL.
  2. A *normalization scheme* that makes BLB and NHL numbers comparable.
  3. A *similarity engine* (distance / similarity metrics + nearest-neighbor retrieval).

1. Feature-space design
-----------------------
A "feature vector" for each player is a combination of:
  - Basic rates:
      * Goals / 60, Assists / 60, Shots / 60
      * Primary points / 60, OZ entries / 60, controlled entries %, etc.
  - On-ice shot share metrics:
      * Corsi For%, Fenwick For%, xG For%, etc. (team-based while player on ice).
  - Contextual usage:
      * TOI, % of team TOI, offensive/defensive zone start %, PP/PK share.
  - Microstats (where available):
      * Entry carry-in %, pass completion %, controlled exits, retrievals, etc.
  - Qualitative / positional flags:
      * Position group (F/D/G), handedness if known, rating tier (for BLB).

LLM action:
  - When asked to define a feature space, consult both:
      * `stats_catalog/benchsight_stats_catalog_master.csv`
      * Inspiration links listed in `docs/benchsight_nhl_resources_and_strategy.txt`
  - Pick 15–40 stable, interpretable features that exist in BOTH BLB and NHL data, or can be approximated.

2. Normalization logic
----------------------
To make BLB vs NHL comparable, we must normalize for:
  - Game length differences.
  - Quality and volume of competition.
  - Sample size (small n for BLB).
  - Era and league context (NHL seasons differ in scoring environment).

Typical steps:

  - First, express metrics as *rates*:
      * Per 60 minutes, per 100 events, per 100 entries, etc.
  - Then standardize within each data universe:
      * For NHL: compute league-wide mean and standard deviation for each stat at a given position and season.
      * For BLB: start with BLB-wide mean/std; later calibrate to NHL distribution if desired.
  - Output standardized scores:
      * z_score = (value - mean) / std
      * optionally cap/clamp extremes to avoid outlier dominance.

LLM action:
  - When creating new stats or features, always define:
      * "numerator", "denominator", "filter context" (which events/rows),
      * whether it's a rate or percentage,
      * whether it should be normalized to league or team baseline.

3. Similarity logic
-------------------
Once you have standardized feature vectors for:
  - BLB players (e.g., player-season, player-game, or player-rolling-10-games).
  - NHL players (e.g., player-season records).

You can define similarity as:

  - Cosine similarity, or
  - Euclidean distance in z-score space, optionally weighted by feature importance.

Example:
  - Let f_BL = (z1, z2, ..., zk) be a BLB player's standardized feature vector.
  - Let f_NHLi be each NHL player's vector.
  - Compute distance d(f_BL, f_NHLi).
  - The top-N smallest distances (or highest cosine similarity) are "closest comps."

LLM action:
  - When asked to build a comp table or view, you should:
      * Document the feature set.
      * Document the distance metric and any weights.
      * Show how to store the top N comps per BLB player in a fact table.

Proposed comparison tables / views
----------------------------------
For the high-level model, assume the following "logical tables":

  1. `fact_blb_player_features`
     - Grain: one row per BLB player-season (or player-game).
     - Key: blb_player_feature_id, plus (player_id, season_id, grain_type).
     - Columns: standardized features + raw features + metadata (sample size, games played, etc.).

  2. `fact_nhl_player_features`
     - Grain: one row per NHL player-season (or player-game).
     - Key: nhl_player_feature_id, plus (nhl_player_id, nhl_season_id, grain_type).
     - Columns: same feature set as above, standardized separately.

  3. `fact_blb_nhl_player_comps`
     - Grain: one row per BLB player feature row per NHL comparable (top K, e.g., 10 comps).
     - Key: blb_nhl_comp_id.
     - Columns:
         * blb_player_feature_id (FK → fact_blb_player_features)
         * nhl_player_feature_id (FK → fact_nhl_player_features)
         * rank (1 = closest)
         * similarity_score or distance
         * summary breakdown (optional JSON: feature-by-feature diffs)

  4. `vw_blb_player_comp_cards`
     - Grain: one row per BLB player feature row, aggregated view for dashboards.
     - Pre-joins with `dim_player`, `dim_nhl_player`, `dim_team`, etc.
     - Optionally includes short natural-language "comp blurbs."

LLM action:
  - When asked for SQL DDL/ETL, implement these as real tables/views pointing at:
      * existing BLB datamart (player boxscore, microstats),
      * imported NHL stats tables.

Dashboard & UX implications
---------------------------
The Benchsight design includes dashboards like:
  - "Player card" view:
      * Show BLB player's profile + 3–5 closest NHL comps and radar charts.
  - "Archetype explorer":
      * Cluster NHL players into archetypes; place BLB players in these clusters.
  - "Development path view":
      * Show how a BLB player would need to shift features to resemble specific NHL targets.

LLM action:
  - When asked to generate Power BI measures, DAX, or Python/Dash components for comps:
      * Use `fact_blb_nhl_player_comps` (or equivalent) as the base.
      * Use the dim tables to show names, seasons, teams, and feature breakdowns.

How this relates to the rest of the project
-------------------------------------------
- BLB datamart is already designed to support microstats and advanced metrics.
- The NHL integration adds:
    * ingestion + normalization pipelines,
    * alignment of stat definitions,
    * a "player_features" layer for each world,
    * a "comps" layer that ties them together.
- The same feature space can also power:
    * "Moneyball" style roster building,
    * trade/lineup simulations,
    * contract value heuristics (if salary data is added).

Summary of what you, the LLM, should do
---------------------------------------
1. Respect the existing tables and stats catalogs included in this bundle.
2. When asked about BLB–NHL comps:
     - Propose or refine feature sets,
     - Define normalization logic clearly,
     - Choose similarity metrics and explain tradeoffs,
     - Emit well-documented SQL/Python to build:
         * fact_blb_player_features
         * fact_nhl_player_features
         * fact_blb_nhl_player_comps
         * vw_blb_player_comp_cards
3. Keep everything explainable:
     - For each new metric, write a plain-English description,
     - Note any assumptions or approximations, especially where BLB data is sparser.