# BenchSight Analytics Glossary, Gaps, and Upgrade Plan

**Purpose:** Single reference for key definitions, what exists today, what's missing vs. NHL-grade models, and a staged plan to close the gaps. Built from `BENCHSIGHT_CALCULATION_DEEP_DIVE_v34.md`, `BENCHSIGHT_DATA_DICTIONARY_v34.md`, and `RESEARCH_PAPER_ANALYSIS.md`.

> **Note:** This document has been superseded by the comprehensive reference documentation created in January 2026. For authoritative definitions, calculations, and implementation details, see:
>
> - **[Canonical Definitions](definitions/CANONICAL_DEFINITIONS.md)** - Authoritative term definitions (stint, rush, play, sequence, etc.)
> - **[Calculation Catalog](calculations/CALCULATION_CATALOG.md)** - All formulas with mathematical notation
> - **[WAR Methodology](calculations/WAR_METHODOLOGY.md)** - Current weighted GAR vs. RAPM target
> - **[xG Model Specification](calculations/XG_MODEL_SPEC.md)** - Lookup-based vs. GBM model
> - **[NHL-Grade Benchmark](gaps/NHL_GRADE_BENCHMARK.md)** - Industry comparison matrix
> - **[Implementation Priority](gaps/IMPLEMENTATION_PRIORITY.md)** - Prioritized roadmap with dependencies

---

## Glossary (operational definitions)
- **Rush (team rush event):** Zone entry (carry/dump) followed by a shot/goal within the next 5 events (`fact_rush_events`, `event_analytics.py`). Captures odd-man/quick-attack sequences; stored with entry/shot IDs and events_to_shot.
- **Scoring chance:** Shot classified into danger buckets (high/medium/low/perimeter) via XY model (distance/angle + modifiers) or heuristic flags (rush/rebound/slot/one-timer, etc.) when XY is absent. Lives in `fact_scoring_chances` and `fact_shot_danger` with xG and danger_zone.
- **Flurry:** Cluster of rebound/second-chance shots in the same possession/stoppage; should be probability-adjusted so cumulative xG = 1 - Π(1 - xG_i) instead of naive summation (not yet implemented).
- **Rebound:** Shot taken shortly after a saved/blocked/missed shot in the same sequence/possession (flagged in shot detail; used as xG modifier).
- **Royal Road pass:** Pass crossing the centerline (y=0) within ~3s before a shot; not yet implemented but a required feature for xG once XY exists.
- **Play:** Possession-linked chain of events with a `play_key` (PL{game}{idx}); typically a micro-possession from start trigger (entry/faceoff) to a terminal action (shot/clear/turnover/stoppage).
- **Sequence:** Longer chain with `sequence_key` (SQ{game}{idx}) spanning related events/plays; used to link flurries/possessions and in `fact_event_chains`/`fact_shot_chains`.
- **Possession chain:** Team-controlled stretch within a zone or across zones bounded by faceoff/change-of-possession/stoppage; basis for shot chains and potential xT crediting.
- **Zone entry/exit:** Discrete events with type (carry/dump/pass/failed) and outcome (successful/failed). Summaries in `fact_zone_entries`/`fact_zone_exits` and player-level summaries.
- **Transition (offense):** Controlled entries/exits plus rushes leading to shots/goals; captured via zone entry/exit tables and rush detector.
- **Strength state:** Encoded strength (e.g., 5v5/5v4/4v5/3v3) and situation (EV/PP/PK/EN) on every event/shift; critical for split models.
- **Stint:** Continuous interval with unchanged skaters/goalies on ice; required grain for RAPM. Not yet materialized—must be derived from shifts/events (new stint table).
- **Faceoff directionality (WDBE concept):** Classifies wins by cleanliness (clean/scrum) and exit vector (back/forward/inside/outside) to value the downstream event probability; not implemented.
- **Gap (defense on entries):** Distance between puck carrier and nearest defender at the blue line crossing (x=±25), optionally adjusted by defender velocity (“effective gap”); requires XY tracking.
- **Expected Threat (xT):** Grid-based Markov model valuing puck movement between rink zones and shots; requires XY coordinates and transition matrix.

---

## What exists vs. what’s missing (by area)

### Expected Goals (xG)
- **Exists:** Lookup/heuristic xG with danger levels; modifiers for rush/rebound/one-timer/breakaway; optional XY distance/angle model (piecewise distance + cosine angle factor) in `event_analytics.py`; stored in `fact_scoring_chances` / `fact_shot_danger`.
- **Missing:** GBM model (XGBoost/LightGBM); Royal Road feature; flurry adjustment; shooter talent adjustment; speed-from-previous-event; systematic distance/angle from normalized XY; shot-type integration into model training; calibration/validation harness.

### WAR/GAR and Player Isolation
- **Exists:** Component-based GAR/WAR with fixed weights (offense/defense/possession/transition/poise) in `core_facts.py`; goals-per-win = 4.5 (rec calibration); goalie GAR with GSAx-style weights.
- **Missing:** Stint data structure; Ridge/RAPM models for 6 WAR components (EV off/def, PP off, PK def, Penalties, Finishing); multicollinearity handling; lambda CV; replacement level baseline (top-13F/7D exclusion); daisy-chain priors across seasons; NHL goals-per-win calibration (≈6).

### Rush/Transition and Possession
- **Exists:** Rush detector (entry → shot within 5 events); zone entry/exit events + summaries; shot chains and event chains tables; transition metrics in player stats.
- **Missing:** Possession-valued chains (xT); standardized “play/sequence” grains tied to possession value; rush quality features (speed, manpower, royal road).

### Faceoffs (WDBE)
- **Exists:** Faceoff wins/losses and zone context.
- **Missing:** Directional buckets; clean vs scrum; expected next-event valuation; player-level WDBE aggregation.

### Tracking/Microstats
- **Exists:** Framework for XY tables (`fact_player_xy_*`, `fact_puck_xy_*`); zone grids; gap placeholders in research docs.
- **Missing:** Actual XY ingestion; coordinate normalization (period flip/offensive standardization); gap distance/effective gap; velocity features; puck speed; pass lanes/cross-slot; spatial xT grid transitions.

---

## Data and feature dependencies
- **Ready now:** Event/shift data, zone entry/exit, rush flags, scoring chance flags, GAR/WAR weights, shot chains, play/sequence keys.
- **Needed to unlock spatial/micro models:** XY coordinates (player + puck), period-aware normalization, velocity vectors.
- **Needed for RAPM:** Stint builder that detects player changes/goals/penalties/period ends; sparse design matrix with player +/- encoding and context (zone start, score state, strength); cross-validation.

---

## Implementation plan (staged)

### Immediate (no XY required)
1) **Flurry adjustment for xG:** Group shots by possession/stoppage and apply `1 - Π(1 - xG_i)`; store flurry_xg in shot chains and scoring chance tables.  
2) **WDBE v1:** Use event detail to tag clean vs scrum; approximate direction from faceoff metadata if available; assign outcome weights from historical next-event rates.  
3) **Glossary + grains:** Lock definitions above into ETL docs and ensure `play_key`/`sequence_key` usage is consistent.  
4) **Stint schema design:** Spec `fact_stints` structure and triggers (player sub, goal, penalty, period end); wire generation from shifts/events (no modeling yet).  
5) **xG hygiene:** Ensure modifiers (rush/rebound/one-timer) applied consistently; add unit tests on xG ranges and caps.

### Short-term (once XY lands)
1) **Coordinate normalization:** Flip by period/attacking side so net is always at x=89, y=0; persist normalized x/y on shots, passes, entries.  
2) **Distance/angle + Royal Road:** Standardize shot distance/angle; implement royal_road boolean and angle-change features; add speed-from-previous-event.  
3) **GBM xG prototype:** Train LightGBM/XGBoost with spatial + contextual features; calibrate with reliability curves; backtest vs goals and current lookup.  
4) **Gap control v1:** Compute static and effective gap at blue-line entries; store per entry and per defender.  
5) **Shot/puck speed:** Derive puck and pass speed from consecutive XY timestamps; surface as model features.

### Medium-term (modeling & valuation)
1) **RAPM/WAR overhaul:** Build `fact_stints`, generate sparse design matrix, run RidgeCV for 6 components (EV off/def, PP off, PK def, Penalties, Finishing); replace fixed weights with coefficients; implement replacement level and daisy-chain priors; convert GAR→WAR with NHL 6 goals/win.  
2) **xT grid model:** Discretize rink (e.g., 16×12), estimate transition matrix and shot-to-goal by cell, solve xT; credit players on puck moves (xT_end - xT_start).  
3) **Faceoff WDBE full:** Directional vectors from XY; clean vs scrum; expected-value weighting to possession/shot/clear outcomes; per-player/zone splits.  
4) **Shooting talent adjustment:** Bayesian shrinkage of (Goals - xG) residuals with shot-volume prior; integrate into reported xG/finishing components.  
5) **Validation harness:** Cross-val for GBM and Ridge; backtests on holdout seasons; calibration plots; sensitivity on flurry grouping and royal-road windows.

---

## Quick current→target mapping (high level)
- **xG:** From lookup + heuristic → GBM with spatial/context features, flurry-adjusted, shooter-talent aware.  
- **WAR:** From weighted box-score blend → RAPM-based, stint-grain, replacement-level anchored, multi-strength components.  
- **Rush/Transition:** From entry→shot flag → speed/royal-road enriched, possession-valued via xT.  
- **Faceoffs:** From win% → direction/outcome-valued WDBE.  
- **Defense (entries):** From entry outcomes → gap/effective-gap deterrence metrics.  
- **Possession value:** From counts → xT credit per pass/entry/exit.

---

## Validation approach
- **xG:** Reliability curves, Brier/LogLoss vs holdout, sharpness by shot type/angle bins, flurry grouping sanity.  
- **RAPM:** MSE vs CV folds, ridge λ grid search, stability across seasons, impact deltas when players separate, GOF on target rates (xGF/60, xGA/60).  
- **WAR:** Compare distributions to NHL baselines; replacement-level check; sensitivity to goals-per-win.  
- **Faceoffs (WDBE):** Expected next-event lift vs raw FO%; zone and direction stratification.  
- **Gap/xT:** Correlate gap to entry shot quality; xT to subsequent goal probability; ensure monotonic zone values.

---

## Deliverables to produce next
1) Spec + schema draft for `fact_stints` and normalization of XY (period flip).  
2) Flurry-adjusted xG prototype + unit tests.  
3) WDBE v1 tagging rules from existing event detail.  
4) GBM xG feature list and training plan (once XY is live).  
5) RAPM modeling workbook (design matrix encoding, λ tuning, replacement level method).
