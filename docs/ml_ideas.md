# ML Ideas for BenchSight

This file lists example machine learning projects that can be built on
top of the datamart. When the user asks for ML help, use this as a
starting point.

## 1. Expected Goals (xG) Model

**Goal:** Estimate the probability that a shot becomes a goal.

**Level:** Event-level (shots only).

**Candidate Features:**

- Shot location:
  - `distance_from_net` (from XY + rink coords).
  - `shot_angle` relative to net center.
- Shot type:
  - From `event_detail_1/2` (slap, wrist, backhand, tip, etc.).
- Pre-shot context:
  - Seconds since last event.
  - Was there a cross-ice pass?
  - Was it off the rush vs cycle?
  - Odd-man rush flag.
- Traffic:
  - Number of defenders between shooter and net.
  - Number of teammates near the net (if approximated).
- Goalie context:
  - Goalie rating (from dim_players).
  - Shot against a tired line? (shift length).
- Score & game state:
  - Score differential.
  - Period, time remaining.
  - Strength (5v5, PP, PK, EN).

**Possible labels:**

- 1 if goal, 0 if any non-goal shot on target / attempt, or
- 1 if goal, 0 if missed/blocked/saved (depending on definition).

**Implementation hints:**

- Start with logistic regression / XGBoost.
- Use `fact_events` filtered to shot events joined to XY tables.

## 2. Player Microstat Profiles & Comps

**Goal:** Describe players by their microstats and find similar players.

**Features:**

- Rates per 60:
  - Controlled zone entries/exits.
  - Entries with shot.
  - Pass completions (by lane / zone).
  - Turnovers & takeaways (non-dump/clear).
  - Quality pass chains leading to xG.
- On-ice impact:
  - Corsi/Fenwick on-ice per 60.
  - xG for and against per 60.
- Role indicators:
  - OZ vs DZ starts.
  - PK/PP usage.
  - Line-mate and matchup profiles.

**Methods:**

- Standardize features per league/season.
- Use PCA or UMAP for dimensionality reduction.
- kNN or cosine similarity for comps.

## 3. Line Combo & Matchup Models

**Goal:** Quantify how different forward/defense combos perform together
vs specific opponent lines.

**Features:**

- On-ice line IDs for both teams (from shift data).
- Outcome metrics:
  - Goals, xG, shots, Corsi, microstat counts while both lines are on ice.
- Context:
  - Deployment (zone start, score state).
  - Time-on-ice together.

**Approach:**

- Build a `fact_line_matchups` derived table summarizing these interactions.
- Use regression / hierarchical models to estimate adjusted impacts.

## 4. Game-State & Win-Probability Models

**Goal:** Given current score, time, and stats, estimate win probability.

**Features:**

- Score differential & time remaining.
- Shot/xG differential so far.
- Penalty state (PP/PK).
- On-ice personnel strengths (ratings).

**Approach:**

- Train on many games (NHL data if available) and apply to BLB games.
- Use logistic regression, gradient boosting, or time-series models.

## 5. Computer Vision Extensions (Future)

**Goal:** Auto-track player and puck positions from video and feed into
the same pipeline.

**Outline:**

- Use pose estimation / object detection models (e.g., YOLO, Detectron2,
  OpenCV-based pipelines).
- Map video coordinates to rink coordinates using homography.
- Reconstruct trajectories and event times, link to existing events_table
  via timestamps.
- Compute speed, acceleration, gap control, lane usage, etc.

These vision features can feed into xG models and new microstats such as:

- Maximum speed in a rush.
- Gap distance at shot release.
- Time-to-close by defenders.

Use this doc as a menu when the user wants to explore ML directions.
