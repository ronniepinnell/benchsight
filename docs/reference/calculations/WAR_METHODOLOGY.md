# WAR Methodology: Current State vs. Industry Standard

> **Purpose:** Deep dive documentation on BenchSight's WAR/GAR implementation versus NHL-grade RAPM-based approaches, with a roadmap for closing the methodology gap.

**Version:** 1.0
**Last Updated:** 2026-01-21
**Owner:** Analytics Team

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current Implementation: Weighted GAR](#2-current-implementation-weighted-gar)
3. [Industry Standard: RAPM-Based WAR](#3-industry-standard-rapm-based-war)
4. [Gap Analysis](#4-gap-analysis)
5. [Implementation Roadmap](#5-implementation-roadmap)
6. [Technical Specifications](#6-technical-specifications)

---

## 1. Executive Summary

### Current State
BenchSight uses a **weighted formula approach** to calculate Goals Above Replacement (GAR) and Wins Above Replacement (WAR). This method assigns fixed weights to counting stats (goals, assists, Corsi, etc.) to estimate player value.

### Target State
Industry leaders (Evolving Hockey, MoneyPuck) use **Regularized Adjusted Plus-Minus (RAPM)** with ridge regression to isolate individual player contributions from linemate and opponent effects.

### Key Gap
The weighted formula conflates player ability with usage context. A player with strong linemates will appear better than they are; a player with weak linemates will appear worse. RAPM solves this by regressing on all players simultaneously.

---

## 2. Current Implementation: Weighted GAR

### 2.1 Architecture Overview

**Type:** Weighted counting stat formula
**Components:** 5 (Offense, Defense, Possession, Transition, Poise)
**Baseline:** Average player (50th percentile)
**Conversion:** 4.5 goals per win (recreational hockey estimate)

**Code Location:** `src/tables/core_facts.py:62-78`

### 2.2 Total GAR Formula

```
GAR_total = GAR_off + GAR_def + GAR_poss + GAR_trans + GAR_poise
```

### 2.3 Component Breakdown

#### Offensive GAR
```
GAR_off = Goals * 1.0
        + Primary_Assists * 0.7
        + Secondary_Assists * 0.4
        + SOG * 0.015
        + xG * 0.8
        + Shot_Assists * 0.3
```

**Weight Rationale:**
| Stat | Weight | Justification |
|------|--------|---------------|
| Goals | 1.0 | Direct goal value |
| Primary Assists | 0.7 | ~70% of goal value (direct setup) |
| Secondary Assists | 0.4 | ~40% of goal value (indirect contribution) |
| SOG | 0.015 | Small value for shot generation |
| xG | 0.8 | Expected goal value (unrealized chances) |
| Shot Assists | 0.3 | Passes leading to shots |

#### Defensive GAR
```
GAR_def = Takeaways * 0.05
        + Blocks * 0.02
        + Controlled_Zone_Exits * 0.03
```

**Weight Rationale:**
| Stat | Weight | Justification |
|------|--------|---------------|
| Takeaways | 0.05 | Possession recovery value |
| Blocks | 0.02 | Shot prevention (lower value due to context) |
| Controlled Exits | 0.03 | Transition initiation |

#### Possession GAR
```
GAR_poss = ((CF% - 50) / 100) * 0.02 * (TOI_hours * 60)
```

**Logic:** Rewards/penalizes players based on how much their Corsi% differs from 50%, scaled by ice time.

#### Transition GAR
```
GAR_trans = Controlled_Zone_Entries * 0.04
```

**Logic:** Rewards players who create offensive opportunities through zone entries.

#### Poise GAR
```
GAR_poise = Pressure_Success * 0.02
```

**Logic:** Rewards composure under pressure situations.

### 2.4 WAR Conversion

```
WAR = GAR_total / 4.5
```

**Goals Per Win:** 4.5 (estimated for recreational hockey)
- NHL standard uses 6.0 goals per win
- Lower value reflects tighter games in rec hockey

### 2.5 Goalie GAR

```
GAR_goalie = Saves_Above_Average * 0.1
           + HD_Saves * 0.15
           + Goals_Prevented * 1.0
           + Rebound_Control * 0.05
           + QS_Bonus * 0.5
```

**Where:**
```
Saves_Above_Average = Saves - (Shots_Against * League_Avg_Save_Pct)
Goals_Prevented = xGA - GA
QS_Bonus = 1 if Quality_Start else 0
Quality_Start = (Save_Pct >= 0.900) AND (GA <= 3)
```

### 2.6 Limitations of Weighted Approach

| Limitation | Impact | Example |
|------------|--------|---------|
| No linemate adjustment | Conflates player skill with linemate quality | Player A looks good because of elite center |
| No opponent adjustment | Ignores competition quality | Player B's stats inflated vs. weak opponents |
| Fixed weights | Assumes universal value for all situations | One-timer assist worth same as dump-in assist |
| No regression | Small samples unreliable | 2-game hot streak overvalued |
| Average baseline | Misvalues below-average players | Replacement-level player shows negative WAR |

---

## 3. Industry Standard: RAPM-Based WAR

### 3.1 What is RAPM?

**Regularized Adjusted Plus-Minus (RAPM)** is a regression-based approach that:
1. Builds a design matrix of all players on ice for each "stint"
2. Regresses target outcomes (goals, xG) against player presence
3. Uses ridge regression (L2 regularization) to handle collinearity
4. Produces coefficients representing each player's isolated impact

### 3.2 Industry Leaders Using RAPM

| Source | Model Name | Components | Methodology |
|--------|------------|------------|-------------|
| **Evolving Hockey** | WAR | 6 components | Ridge regression, daisy-chain priors |
| **MoneyPuck** | GAR | 5 components | Logistic regression + ridge |
| **TopDownHockey** | WAR | Alternative | Bayesian hierarchical |

### 3.3 Evolving Hockey WAR Model

**Components:**
1. Even Strength Offense (EVO)
2. Even Strength Defense (EVD)
3. Power Play Offense (PPO)
4. Penalty Kill Defense (PKD)
5. Penalties (PEN)
6. Faceoffs (FOW) - added recently

**Key Features:**
- Stint-based design matrix
- Ridge regression with cross-validated lambda
- "Daisy-chain" priors (use previous season as prior)
- Score/venue adjustment
- Replacement level baseline (13th F, 7th D by TOI)

### 3.4 RAPM Mathematical Framework

**Ridge Regression Objective:**
```
beta_hat = argmin [ SUM(w_i * (y_i - X_i' * beta)^2) + lambda * SUM(beta_j^2) ]
```

**Where:**
- `y_i` = target variable for stint i (e.g., GF/60, xGF/60)
- `X_i` = player indicator vector for stint i
- `w_i` = stint duration weight (longer stints weighted more)
- `beta` = vector of player coefficients
- `lambda` = regularization parameter (shrinks toward 0)

**Player Indicator Matrix:**
```
For each stint:
  +1 if player is on home team
  -1 if player is on away team
  0 if player is not on ice
```

**Example:**
```
Stint 1: Home has players [A, B, C, D, E], Away has [F, G, H, I, J]
X_1 = [+1, +1, +1, +1, +1, -1, -1, -1, -1, -1, 0, 0, ...]
y_1 = GF/60 for this stint
```

### 3.5 Target Variables

RAPM typically runs separate regressions for:

| Target | Description | Unit |
|--------|-------------|------|
| GF/60 | Goals for per 60 minutes | Rate |
| GA/60 | Goals against per 60 minutes | Rate |
| xGF/60 | Expected goals for per 60 | Rate |
| xGA/60 | Expected goals against per 60 | Rate |
| CF/60 | Corsi for per 60 | Rate |
| CA/60 | Corsi against per 60 | Rate |

### 3.6 Regularization (Lambda Selection)

**Purpose:** Prevents overfitting and handles multicollinearity (players who always play together).

**Selection Method:** K-fold cross-validation (typically 10-fold)
```
For each candidate lambda:
  1. Split data into 10 folds
  2. Train on 9 folds, predict on holdout
  3. Calculate mean squared error
  4. Select lambda with lowest average MSE
```

**Typical Lambda Values:** 5-50 depending on sample size

### 3.7 Daisy-Chain Priors (Evolving Hockey)

**Concept:** Use previous season's coefficients as prior information for current season.

**Implementation:**
```
beta_prior = previous_season_beta * decay_factor
beta_current = ridge_regression(y, X, lambda, prior=beta_prior)
```

**Benefits:**
- Stabilizes estimates for players with few games
- Handles injured players who miss time
- Improves early-season predictions

### 3.8 Replacement Level

**Definition:** The performance level of a freely available player (waiver claim, minor league call-up).

**NHL Standard:**
- **Forwards:** 13th forward by TOI (outside top 12)
- **Defensemen:** 7th defenseman by TOI (outside top 6)
- **Goalies:** Replacement-level backup

**Calculation:**
```
Replacement_Level = Percentile(Player_RAPM, position, percentile=replacement_threshold)
```

**WAR Formula:**
```
WAR = (Player_RAPM - Replacement_Level) / Goals_Per_Win
```

---

## 4. Gap Analysis

### 4.1 Methodology Comparison

| Aspect | BenchSight (Current) | Industry (Target) |
|--------|---------------------|-------------------|
| **Approach** | Weighted formula | Ridge regression |
| **Linemate Adjustment** | None | Implicit in regression |
| **Opponent Adjustment** | None | Implicit in regression |
| **Sample Handling** | None | Regularization + priors |
| **Baseline** | Average (50th percentile) | Replacement level |
| **Components** | 5 weighted | 6 regression-based |
| **Data Granularity** | Game-level | Stint-level |

### 4.2 Impact Assessment

| Gap | Severity | Impact |
|-----|----------|--------|
| No RAPM | CRITICAL | Cannot isolate player from context |
| No stint data | CRITICAL | Cannot run RAPM (foundational) |
| Average baseline | MEDIUM | Misvalues below-average players |
| No priors | LOW | Early-season estimates less stable |

### 4.3 Accuracy Implications

**Current Weighted Approach:**
- Good for ranking top players (large sample, clear skill signal)
- Poor for middle-tier players (context confounds)
- Poor for small samples (no regression toward mean)

**RAPM Approach:**
- Better isolation of individual skill
- More reliable for mid-tier players
- Handles small samples via regularization

---

## 5. Implementation Roadmap

### 5.1 Prerequisites

#### Step 1: Stint Table (P0 - Critical)

**Schema:** `fact_stints`
```sql
CREATE TABLE fact_stints (
    stint_id VARCHAR(50) PRIMARY KEY,
    game_id INTEGER NOT NULL,
    period INTEGER NOT NULL,
    stint_number INTEGER NOT NULL,
    start_time INTEGER NOT NULL,      -- Game seconds
    end_time INTEGER NOT NULL,
    duration_seconds INTEGER NOT NULL,

    -- Personnel
    home_f1 VARCHAR(20),
    home_f2 VARCHAR(20),
    home_f3 VARCHAR(20),
    home_d1 VARCHAR(20),
    home_d2 VARCHAR(20),
    home_goalie VARCHAR(20),
    away_f1 VARCHAR(20),
    away_f2 VARCHAR(20),
    away_f3 VARCHAR(20),
    away_d1 VARCHAR(20),
    away_d2 VARCHAR(20),
    away_goalie VARCHAR(20),

    -- Context
    strength VARCHAR(10),             -- 5v5, 5v4, etc.
    zone_start VARCHAR(1),            -- O, N, D
    home_score INTEGER,
    away_score INTEGER,
    score_state INTEGER,              -- home_score - away_score

    -- Outcomes
    gf INTEGER DEFAULT 0,
    ga INTEGER DEFAULT 0,
    xgf DECIMAL(5,3) DEFAULT 0,
    xga DECIMAL(5,3) DEFAULT 0,
    cf INTEGER DEFAULT 0,
    ca INTEGER DEFAULT 0,
    ff INTEGER DEFAULT 0,
    fa INTEGER DEFAULT 0
);
```

**Generation Logic:**
```python
def generate_stints(shifts_df, events_df):
    """
    Generate stints from shift data.

    A new stint begins when:
    - Period starts
    - Any player substitution occurs
    - Goal is scored
    - Penalty starts/ends
    """
    # Implementation in src/tables/stint_builder.py
    pass
```

#### Step 2: Player Indicator Matrix

**Schema:**
```python
def build_player_matrix(stints_df, player_ids):
    """
    Build design matrix X for RAPM.

    Shape: (n_stints, n_players)
    Values: +1 (home), -1 (away), 0 (not on ice)
    """
    n_stints = len(stints_df)
    n_players = len(player_ids)
    X = np.zeros((n_stints, n_players))

    for i, stint in stints_df.iterrows():
        for player in stint['home_players']:
            j = player_ids.index(player)
            X[i, j] = 1
        for player in stint['away_players']:
            j = player_ids.index(player)
            X[i, j] = -1

    return X
```

### 5.2 RAPM Implementation

#### Step 3: Ridge Regression Module

**Location:** `src/calculations/rapm.py`

```python
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score
import numpy as np

def fit_rapm(X, y, weights, lambdas=None):
    """
    Fit RAPM model with cross-validated lambda selection.

    Args:
        X: Player indicator matrix (n_stints x n_players)
        y: Target variable (n_stints,)
        weights: Stint duration weights (n_stints,)
        lambdas: Candidate regularization values

    Returns:
        coefficients: Player RAPM values
        best_lambda: Selected regularization parameter
    """
    if lambdas is None:
        lambdas = [1, 5, 10, 20, 50, 100]

    best_lambda = None
    best_score = -np.inf

    for lam in lambdas:
        model = Ridge(alpha=lam)
        scores = cross_val_score(model, X, y, cv=10,
                                  scoring='neg_mean_squared_error',
                                  sample_weight=weights)
        mean_score = scores.mean()
        if mean_score > best_score:
            best_score = mean_score
            best_lambda = lam

    # Fit final model
    final_model = Ridge(alpha=best_lambda)
    final_model.fit(X, y, sample_weight=weights)

    return final_model.coef_, best_lambda
```

#### Step 4: Multi-Target RAPM

```python
def compute_full_rapm(stints_df, player_ids):
    """
    Compute RAPM for all target variables.

    Returns:
        DataFrame with columns: player_id, rapm_gf, rapm_ga, rapm_xgf, rapm_xga, ...
    """
    X = build_player_matrix(stints_df, player_ids)
    weights = stints_df['duration_seconds'].values

    targets = {
        'rapm_gf60': stints_df['gf'] / stints_df['duration_seconds'] * 3600,
        'rapm_ga60': stints_df['ga'] / stints_df['duration_seconds'] * 3600,
        'rapm_xgf60': stints_df['xgf'] / stints_df['duration_seconds'] * 3600,
        'rapm_xga60': stints_df['xga'] / stints_df['duration_seconds'] * 3600,
    }

    results = {'player_id': player_ids}
    for name, y in targets.items():
        coefs, _ = fit_rapm(X, y.values, weights)
        results[name] = coefs

    return pd.DataFrame(results)
```

### 5.3 WAR Calculation

#### Step 5: RAPM to WAR Conversion

```python
def compute_war(rapm_df, toi_df, replacement_levels):
    """
    Convert RAPM coefficients to WAR.

    Args:
        rapm_df: RAPM coefficients by player
        toi_df: Time on ice by player
        replacement_levels: Dict with 'F', 'D', 'G' replacement baselines

    Returns:
        DataFrame with WAR values
    """
    GOALS_PER_WIN = 6.0  # NHL standard

    war_df = rapm_df.copy()

    # Net RAPM (offense - defense)
    war_df['net_rapm'] = war_df['rapm_xgf60'] - war_df['rapm_xga60']

    # Adjust for replacement level
    for pos in ['F', 'D']:
        mask = war_df['position'] == pos
        replacement = replacement_levels[pos]
        war_df.loc[mask, 'rapm_above_replacement'] = (
            war_df.loc[mask, 'net_rapm'] - replacement
        )

    # Convert to WAR using TOI
    war_df = war_df.merge(toi_df[['player_id', 'toi_hours']], on='player_id')
    war_df['war'] = (
        war_df['rapm_above_replacement'] * war_df['toi_hours'] / GOALS_PER_WIN
    )

    return war_df
```

#### Step 6: Replacement Level Calculation

```python
def calculate_replacement_level(rapm_df, toi_df):
    """
    Calculate replacement level by position.

    Replacement = performance of 13th F / 7th D by TOI
    """
    merged = rapm_df.merge(toi_df, on='player_id')

    replacement_levels = {}

    # Forwards: 13th by TOI
    forwards = merged[merged['position'] == 'F'].nlargest(12, 'toi')
    replacement_f = merged[
        (merged['position'] == 'F') &
        (~merged['player_id'].isin(forwards['player_id']))
    ]['net_rapm'].mean()
    replacement_levels['F'] = replacement_f

    # Defensemen: 7th by TOI
    defense = merged[merged['position'] == 'D'].nlargest(6, 'toi')
    replacement_d = merged[
        (merged['position'] == 'D') &
        (~merged['player_id'].isin(defense['player_id']))
    ]['net_rapm'].mean()
    replacement_levels['D'] = replacement_d

    return replacement_levels
```

### 5.4 Timeline

| Phase | Task | Priority | Dependencies |
|-------|------|----------|--------------|
| 1 | Stint table schema & generation | P0 | Shift data |
| 2 | Player indicator matrix | P0 | Stint table |
| 3 | Ridge regression module | P0 | Matrix |
| 4 | Multi-target RAPM | P0 | Ridge module |
| 5 | Replacement level calculation | P1 | RAPM results |
| 6 | WAR conversion | P1 | RAPM + replacement |
| 7 | Daisy-chain priors (optional) | P2 | Multi-season data |
| 8 | Dashboard integration | P1 | WAR calculation |

---

## 6. Technical Specifications

### 6.1 Data Requirements

| Requirement | Current | Needed |
|-------------|---------|--------|
| Shift data | Available | Yes |
| Event data | Available | Yes |
| Stint table | NOT AVAILABLE | CRITICAL |
| Player indicator matrix | NOT AVAILABLE | CRITICAL |
| Multi-season data | Available | For priors |

### 6.2 Computational Considerations

**Stint Table Size:**
- ~4 games × ~200 stints/game = ~800 stints per season (rec hockey)
- NHL: ~1,312 games × ~100 stints/game = ~130,000 stints

**Matrix Size:**
- ~800 stints × ~300 players = 240,000 cells
- Sparse matrix representation recommended

**Regression Time:**
- Ridge regression on 240K matrix: <1 second
- 10-fold CV with 6 lambdas: ~6 seconds

### 6.3 Validation Strategy

| Test | Expected Outcome |
|------|-----------------|
| Top players | Higher WAR than weighted |
| Bottom players | More negative WAR (replacement baseline) |
| Correlation with weighted | 0.7-0.9 (similar but not identical) |
| Mid-tier spread | Narrower (regression toward mean) |
| Year-over-year stability | Higher with priors |

### 6.4 Output Tables

**New Tables:**
```
fact_stints - Stint-level data (foundation)
fact_rapm_coefficients - Raw RAPM outputs
fact_player_war_rapm - Final WAR values
```

**Modified Tables:**
```
fact_player_season_stats - Add war_rapm column
fact_player_game_stats - Add rapm-based metrics
```

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-21 | Analytics Team | Initial methodology documentation |
