# Implementation Priority Roadmap

> **Purpose:** Prioritized roadmap for closing analytics gaps, with dependency graphs, effort estimates, and implementation order.

**Version:** 1.0
**Last Updated:** 2026-01-21
**Owner:** Analytics Team

---

## Table of Contents

1. [Priority Framework](#1-priority-framework)
2. [Dependency Graph](#2-dependency-graph)
3. [Prioritized Backlog](#3-prioritized-backlog)
4. [Implementation Phases](#4-implementation-phases)
5. [Technical Specifications](#5-technical-specifications)
6. [Success Criteria](#6-success-criteria)

---

## 1. Priority Framework

### 1.1 Priority Definitions

| Priority | Label | Criteria |
|----------|-------|----------|
| **P0** | Critical | Blocks core analytics accuracy; no workaround |
| **P1** | High | Significant improvement; should be next after P0 |
| **P2** | Medium | Nice-to-have; improves specific use cases |
| **P3** | Low | Future consideration; depends on infrastructure |

### 1.2 Effort Estimates

| Size | Definition | Typical Duration |
|------|------------|------------------|
| **XS** | Configuration change only | Hours |
| **S** | Single function/file change | 1-2 days |
| **M** | Multi-file change, new table | 3-5 days |
| **L** | New module, significant logic | 1-2 weeks |
| **XL** | Architecture change, ML model | 2-4 weeks |

### 1.3 Scoring Formula

```
Priority Score = (Impact * 0.4) + (Inverse Effort * 0.3) + (No Dependencies * 0.2) + (Visibility * 0.1)
```

---

## 2. Dependency Graph

### 2.1 Visual Dependency Map

```
                            ┌─────────────────────────────────────────────────────────────┐
                            │                    CURRENT STATE                            │
                            └─────────────────────────────────────────────────────────────┘
                                                      │
                    ┌─────────────────────────────────┼─────────────────────────────────┐
                    │                                 │                                 │
                    ▼                                 ▼                                 ▼
        ┌───────────────────┐            ┌───────────────────┐            ┌───────────────────┐
        │ Flurry Adjustment │            │    Stint Table    │            │ Game State Feats  │
        │      (P0, S)      │            │     (P0, M)       │            │     (P1, S)       │
        │   No Dependencies │            │  No Dependencies  │            │  No Dependencies  │
        └───────────────────┘            └─────────┬─────────┘            └───────────────────┘
                    │                              │
                    │                              │
                    ▼                              ▼
        ┌───────────────────┐            ┌───────────────────┐
        │ Shooting Talent   │            │  RAPM Methodology │
        │      (P1, S)      │            │     (P0, L)       │
        │   No Dependencies │            │   Needs: Stints   │
        └───────────────────┘            └─────────┬─────────┘
                                                   │
                                   ┌───────────────┼───────────────┐
                                   │               │               │
                                   ▼               ▼               ▼
                        ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
                        │ WAR Rebuild  │ │ Replacement  │ │ Goalie RAPM  │
                        │   (P1, M)    │ │ Level (P2,S) │ │   (P2, M)    │
                        │ Needs: RAPM  │ │ Needs: RAPM  │ │ Needs: RAPM  │
                        └──────────────┘ └──────────────┘ └──────────────┘


        ┌─────────────────────────────────────────────────────────────────────────────────┐
        │                         XY COORDINATES AVAILABLE                                │
        └─────────────────────────────────────────────────────────────────────────────────┘
                                                   │
                    ┌──────────────────────────────┼──────────────────────────────┐
                    │                              │                              │
                    ▼                              ▼                              ▼
        ┌───────────────────┐            ┌───────────────────┐        ┌───────────────────┐
        │ Coord Normalize   │            │  Royal Road Det   │        │    Heat Maps      │
        │     (P1, S)       │            │     (P1, M)       │        │     (P2, M)       │
        │  Needs: XY Data   │            │   Needs: XY Data  │        │   Needs: XY Data  │
        └─────────┬─────────┘            └───────────────────┘        └───────────────────┘
                  │
                  ▼
        ┌───────────────────┐
        │ Distance/Angle    │
        │     (P1, S)       │
        │ Needs: Normalized │
        └─────────┬─────────┘
                  │
                  ▼
        ┌───────────────────┐
        │  XGBoost xG Model │
        │     (P1, XL)      │
        │Needs: Dist/Angle, │
        │ Royal Road, Data  │
        └───────────────────┘


        ┌─────────────────────────────────────────────────────────────────────────────────┐
        │                         FUTURE (TRACKING REQUIRED)                              │
        └─────────────────────────────────────────────────────────────────────────────────┘
                                                   │
                    ┌──────────────────────────────┼──────────────────────────────┐
                    │                              │                              │
                    ▼                              ▼                              ▼
        ┌───────────────────┐            ┌───────────────────┐        ┌───────────────────┐
        │   Gap Control     │            │    xT Model       │        │  Speed Metrics    │
        │     (P3, L)       │            │     (P3, L)       │        │     (P3, XL)      │
        │Needs: Player XY   │            │ Needs: Pass XY    │        │Needs: Tracking    │
        └───────────────────┘            └───────────────────┘        └───────────────────┘
```

### 2.2 Dependency Matrix

| Item | Depends On | Unlocks |
|------|------------|---------|
| Flurry Adjustment | None | - |
| Stint Table | None | RAPM |
| Game State Features | None | - |
| Shooting Talent | None | - |
| RAPM Methodology | Stint Table | WAR Rebuild, Replacement Level, Goalie RAPM |
| WAR Rebuild | RAPM | - |
| Replacement Level | RAPM | - |
| Coord Normalization | XY Data | Distance/Angle |
| Royal Road Detection | XY Data | XGBoost xG |
| Distance/Angle | Normalized XY | XGBoost xG |
| XGBoost xG Model | Distance/Angle, Royal Road, Training Data | - |
| WDBE Faceoffs | None | - |
| Gap Control | Player XY Tracking | - |
| xT Model | Pass XY Data | - |

---

## 3. Prioritized Backlog

### 3.1 Complete Ranked List

| Rank | Item | Priority | Effort | Dependencies | Score |
|------|------|----------|--------|--------------|-------|
| 1 | Flurry Adjustment | P0 | S | None | 92 |
| 2 | Stint Table | P0 | M | None | 88 |
| 3 | Game State Features | P1 | S | None | 82 |
| 4 | Shooting Talent Adjustment | P1 | S | None | 78 |
| 5 | RAPM Methodology | P0 | L | Stint Table | 75 |
| 6 | Coordinate Normalization | P1 | S | XY Data | 72 |
| 7 | Royal Road Detection | P1 | M | XY Data | 70 |
| 8 | Distance/Angle Calculation | P1 | S | Normalized XY | 68 |
| 9 | WAR Rebuild | P1 | M | RAPM | 65 |
| 10 | Replacement Level | P2 | S | RAPM | 62 |
| 11 | WDBE Faceoffs | P2 | M | None | 58 |
| 12 | XGBoost xG Model | P1 | XL | Dist/Angle, Royal Road | 55 |
| 13 | Heat Maps | P2 | M | XY Data | 52 |
| 14 | Goalie RAPM | P2 | M | RAPM | 48 |
| 15 | Gap Control | P3 | L | Player XY Tracking | 35 |
| 16 | xT Model | P3 | L | Pass XY Data | 32 |
| 17 | Speed Metrics | P3 | XL | Tracking Infrastructure | 20 |

### 3.2 Quick Reference by Priority

**P0 - Critical:**
1. Flurry Adjustment (S)
2. Stint Table (M)
3. RAPM Methodology (L)

**P1 - High:**
4. Game State Features (S)
5. Shooting Talent Adjustment (S)
6. Coordinate Normalization (S)
7. Royal Road Detection (M)
8. Distance/Angle Calculation (S)
9. WAR Rebuild (M)
10. XGBoost xG Model (XL)

**P2 - Medium:**
11. Replacement Level (S)
12. WDBE Faceoffs (M)
13. Heat Maps (M)
14. Goalie RAPM (M)

**P3 - Low:**
15. Gap Control (L)
16. xT Model (L)
17. Speed Metrics (XL)

---

## 4. Implementation Phases

### 4.1 Phase 1: Foundation (No Dependencies)

**Duration:** 1-2 weeks
**Goal:** Implement all items with no dependencies

| Item | Effort | Owner | Files Affected |
|------|--------|-------|----------------|
| Flurry Adjustment | S | TBD | `src/tables/event_analytics.py`, `src/calculations/xg.py` |
| Stint Table | M | TBD | NEW: `src/tables/stint_builder.py`, `fact_stints` schema |
| Game State Features | S | TBD | `src/tables/core_facts.py` |
| Shooting Talent Adjustment | S | TBD | `src/calculations/xg.py`, NEW: talent lookup |

**Deliverables:**
- [ ] `fact_stints` table populated
- [ ] Flurry-adjusted xG in `fact_player_game_stats`
- [ ] Game state columns in xG calculation
- [ ] Shooting talent lookup table

### 4.2 Phase 2: RAPM Implementation

**Duration:** 2-3 weeks
**Goal:** Implement RAPM-based WAR

| Item | Effort | Owner | Files Affected |
|------|--------|-------|----------------|
| RAPM Methodology | L | TBD | NEW: `src/calculations/rapm.py` |
| WAR Rebuild | M | TBD | `src/tables/core_facts.py`, WAR columns |
| Replacement Level | S | TBD | `src/calculations/rapm.py` |

**Deliverables:**
- [ ] RAPM coefficients table
- [ ] WAR based on RAPM (not weighted)
- [ ] Replacement level calculated per position

### 4.3 Phase 3: XY-Dependent Features

**Duration:** 2-3 weeks
**Goal:** Enhance xG model with spatial features
**Prerequisite:** XY coordinates available

| Item | Effort | Owner | Files Affected |
|------|--------|-------|----------------|
| Coordinate Normalization | S | TBD | `src/tables/event_analytics.py` |
| Royal Road Detection | M | TBD | `src/tables/event_analytics.py` |
| Distance/Angle Calculation | S | TBD | `src/calculations/xg.py` |

**Deliverables:**
- [ ] Normalized XY coordinates
- [ ] `is_royal_road` flag on shots
- [ ] Continuous distance/angle in xG

### 4.4 Phase 4: ML Model

**Duration:** 3-4 weeks
**Goal:** Replace lookup xG with XGBoost model
**Prerequisite:** Phase 3 complete

| Item | Effort | Owner | Files Affected |
|------|--------|-------|----------------|
| XGBoost xG Model | XL | TBD | NEW: `src/models/xg_model.py`, training pipeline |

**Deliverables:**
- [ ] Trained XGBoost model
- [ ] Calibrated probabilities
- [ ] Feature importance analysis
- [ ] Model versioning

### 4.5 Phase 5: Enhancements

**Duration:** 2-4 weeks
**Goal:** Secondary improvements

| Item | Effort | Owner | Files Affected |
|------|--------|-------|----------------|
| WDBE Faceoffs | M | TBD | Event detail enhancement |
| Heat Maps | M | TBD | Dashboard visualization |
| Goalie RAPM | M | TBD | `src/calculations/rapm.py` |

**Deliverables:**
- [ ] WDBE classification on faceoffs
- [ ] Shot/event heat maps on dashboard
- [ ] Goalie-specific RAPM

### 4.6 Phase 6: Future (Infrastructure Required)

**Duration:** TBD
**Goal:** Advanced tracking metrics
**Prerequisite:** Player/puck tracking infrastructure

| Item | Effort | Owner | Files Affected |
|------|--------|-------|----------------|
| Gap Control | L | TBD | NEW: tracking module |
| xT Model | L | TBD | NEW: expected threat module |
| Speed Metrics | XL | TBD | Infrastructure project |

---

## 5. Technical Specifications

### 5.1 Flurry Adjustment

**Location:** `src/calculations/xg.py`

**Algorithm:**
```python
def calculate_flurry_adjusted_xg(shots_df, window=3.0):
    """
    Adjust xG for shot flurries using probability formula.

    P(at least one goal) = 1 - Product(1 - xG_i)
    """
    # Group shots into flurries (shots within window seconds)
    shots_df['flurry_id'] = detect_flurries(shots_df, window)

    # Calculate per-flurry adjusted xG
    flurry_xg = shots_df.groupby('flurry_id').apply(
        lambda g: 1 - np.prod(1 - g['xg'])
    )

    return flurry_xg
```

**Output:** `xg_adjusted` column in shot tables

### 5.2 Stint Table

**Location:** `src/tables/stint_builder.py`

**Schema:**
```sql
CREATE TABLE fact_stints (
    stint_id VARCHAR(50) PRIMARY KEY,
    game_id INTEGER NOT NULL,
    period INTEGER NOT NULL,
    stint_number INTEGER NOT NULL,
    start_time INTEGER NOT NULL,
    end_time INTEGER NOT NULL,
    duration_seconds INTEGER NOT NULL,

    -- Home players (by position)
    home_f1 VARCHAR(20),
    home_f2 VARCHAR(20),
    home_f3 VARCHAR(20),
    home_d1 VARCHAR(20),
    home_d2 VARCHAR(20),
    home_goalie VARCHAR(20),

    -- Away players (by position)
    away_f1 VARCHAR(20),
    away_f2 VARCHAR(20),
    away_f3 VARCHAR(20),
    away_d1 VARCHAR(20),
    away_d2 VARCHAR(20),
    away_goalie VARCHAR(20),

    -- Context
    strength VARCHAR(10),
    zone_start VARCHAR(1),
    home_score INTEGER,
    away_score INTEGER,

    -- Outcomes
    gf INTEGER DEFAULT 0,
    ga INTEGER DEFAULT 0,
    xgf DECIMAL(5,3) DEFAULT 0,
    xga DECIMAL(5,3) DEFAULT 0,
    cf INTEGER DEFAULT 0,
    ca INTEGER DEFAULT 0,

    INDEX idx_game (game_id),
    INDEX idx_strength (strength)
);
```

### 5.3 RAPM Module

**Location:** `src/calculations/rapm.py`

**Interface:**
```python
class RAPMCalculator:
    def __init__(self, lambda_range=[1, 5, 10, 20, 50]):
        self.lambda_range = lambda_range
        self.best_lambda = None
        self.coefficients = None

    def fit(self, stints_df, target='xgf60'):
        """Fit RAPM model on stint data."""
        X = self._build_player_matrix(stints_df)
        y = self._extract_target(stints_df, target)
        weights = stints_df['duration_seconds'].values

        self.best_lambda = self._cross_validate(X, y, weights)
        self.coefficients = self._fit_ridge(X, y, weights, self.best_lambda)

        return self

    def get_player_rapm(self):
        """Return DataFrame of player RAPM values."""
        return pd.DataFrame({
            'player_id': self.player_ids,
            'rapm': self.coefficients
        })
```

### 5.4 Royal Road Detection

**Location:** `src/tables/event_analytics.py`

**Algorithm:**
```python
def detect_royal_road(events_df, shot, window=3.0):
    """
    Detect if shot was preceded by royal road pass.

    Royal road = pass crossing y=0 within window seconds before shot.
    """
    # Get passes before this shot
    passes = events_df[
        (events_df['event_type'] == 'Pass') &
        (events_df['game_id'] == shot['game_id']) &
        (events_df['time'] < shot['time']) &
        (events_df['time'] >= shot['time'] - window)
    ]

    if passes.empty:
        return False

    # Check if any pass crossed center (y=0)
    for _, pass_event in passes.iterrows():
        if pass_event['start_y'] * pass_event['end_y'] < 0:
            return True

    return False
```

---

## 6. Success Criteria

### 6.1 Phase 1 Success

| Metric | Target |
|--------|--------|
| Flurry-adjusted xG sum | 3-5% lower than naive |
| Stint table coverage | 100% of shifts mapped to stints |
| Game state xG variance | Score-adjusted xG shows meaningful difference |

### 6.2 Phase 2 Success

| Metric | Target |
|--------|--------|
| RAPM convergence | Cross-validation MSE < baseline |
| WAR correlation | 0.7-0.9 with weighted WAR |
| Replacement level | Distinct from average |

### 6.3 Phase 3 Success

| Metric | Target |
|--------|--------|
| Royal road detection rate | 8-12% of shots flagged |
| Continuous xG variance | Higher than zone-based |
| XY normalization accuracy | <2ft error |

### 6.4 Phase 4 Success

| Metric | Target |
|--------|--------|
| XGBoost AUC | >0.75 (vs ~0.70 lookup) |
| Calibration | Brier score < 0.08 |
| Feature importance | Distance, angle, royal road in top 5 |

### 6.5 Overall Success

| Metric | Target |
|--------|--------|
| Industry alignment | 80%+ of MoneyPuck features |
| User satisfaction | Positive feedback on WAR/xG |
| Dashboard adoption | Increased usage of advanced stats pages |

---

## Appendix: Implementation Checklist

### Pre-Implementation
- [ ] Review existing code in `src/calculations/` and `src/tables/`
- [ ] Confirm XY data availability
- [ ] Set up testing framework for calculations
- [ ] Document baseline metrics

### Phase 1 Checklist
- [ ] Implement flurry detection function
- [ ] Add flurry-adjusted xG column
- [ ] Create stint builder module
- [ ] Generate `fact_stints` table
- [ ] Add game state to xG calculation
- [ ] Implement shooting talent lookup

### Phase 2 Checklist
- [ ] Implement player indicator matrix builder
- [ ] Add ridge regression with CV
- [ ] Calculate RAPM coefficients
- [ ] Define replacement level
- [ ] Rebuild WAR on RAPM

### Phase 3 Checklist
- [ ] Normalize XY coordinates
- [ ] Implement royal road detection
- [ ] Add continuous distance/angle
- [ ] Update xG to use new features

### Phase 4 Checklist
- [ ] Build feature engineering pipeline
- [ ] Train XGBoost model
- [ ] Calibrate probabilities
- [ ] Validate on holdout data
- [ ] Deploy model to production

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-21 | Analytics Team | Initial priority roadmap |
