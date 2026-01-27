# Hockey Analytics Replication Manual - Gap Analysis
## Deep Dive: What BenchSight Has vs. What the Research Prescribes

**Date:** 2026-01-13  
**Source:** "Algorithmic Evaluation in Modern Hockey: A Technical Deconstruction"  
**Comparison Target:** BenchSight v29.7 Implementation

---

## Executive Summary

This document compares the methodologies described in the Hockey Analytics Replication Manual against BenchSight's current implementation. The paper describes three core methodologies:

1. **Expected Goals (xG)** - Probabilistic shot quality assessment
2. **Regularized Adjusted Plus-Minus (RAPM)** - Player isolation via Ridge Regression  
3. **Wins Above Replacement (WAR)** - Aggregate value assessment
4. **Tracking/Microstats** - Gap Control, WDBE, Expected Threat (xT)

**Key Finding:** BenchSight has foundational elements but lacks the sophisticated statistical models (GBM xG, RAPM, xT) described in the research.

---

## 1. Expected Goals (xG) Methodology

### 1.1 What the Research Prescribes

**Model Type:** Gradient Boosting Machines (XGBoost/LightGBM)  
**Target:** Classification problem ($p \in [0,1]$ for each shot)

**Key Features:**
- **Royal Road Pass:** Pass crossing y=0 line within 3s before shot
- **Shot Distance:** Euclidean distance to net center (89, 0)
- **Shot Angle:** Absolute angle from central axis
- **Speed from Previous Event:** Puck velocity proxy
- **Flurry Adjustment:** Probabilistic correction for shot sequences
- **Shooting Talent Adjustment:** Bayesian regression on residuals

**Mathematical Formulation:**
- Distance: $d = \sqrt{(89 - x_{norm})^2 + (y_{norm})^2}$
- Angle: $\theta = \left| \arctan \left( \frac{y_{norm}}{89 - x_{norm}} \right) \right| \times \frac{180}{\pi}$
- Flurry Adjusted: $P(AtLeastOneGoal) = 1 - \prod_{i=1}^{n} (1 - xG_i)$
- Shooting Talent: $ST = \frac{R \cdot Shots}{Shots + Reg\_Threshold}$

### 1.2 What BenchSight Currently Has

**Location:** `src/tables/core_facts.py::calculate_xg_stats()`

**Current Implementation:**
- ✅ Basic xG calculation exists
- ✅ Uses danger_level (high/medium/low/default)
- ✅ Rush modifier (1.3x multiplier)
- ❌ **NO Royal Road pass detection**
- ❌ **NO distance/angle calculation from XY coordinates**
- ❌ **NO Flurry Adjustment** (sums xG naively)
- ❌ **NO Shooting Talent adjustment**
- ❌ **Uses simple lookup table**, NOT Gradient Boosting
- ❌ **NO shot type features** (wrist, slap, snap, tip, etc.)

**Current Formula:**
```python
XG_BASE_RATES = {
    'high_danger': 0.25, 
    'medium_danger': 0.08, 
    'low_danger': 0.03, 
    'default': 0.06
}
xg = base_xg * (XG_MODIFIERS['rush'] if is_rush else 1.0)
```

**Gap Analysis:**
| Feature | Research | BenchSight | Gap Severity |
|---------|----------|------------|--------------|
| Model Type | Gradient Boosting (XGBoost/LightGBM) | Lookup table | 🔴 **CRITICAL** |
| Royal Road | ✅ Boolean feature | ❌ Missing | 🔴 **HIGH** |
| Distance/Angle | ✅ Calculated from XY | ⚠️ Placeholder (needs XY) | 🟡 **MEDIUM** |
| Flurry Adjustment | ✅ Probabilistic | ❌ Naive sum | 🔴 **HIGH** |
| Shooting Talent | ✅ Bayesian regression | ❌ Missing | 🟡 **MEDIUM** |
| Shot Type Features | ✅ Wrist/Slap/Snap/Tip | ⚠️ Partial (has shot types, not in xG) | 🟡 **MEDIUM** |
| Rush Detection | ✅ Included | ✅ Included | ✅ **COMPLETE** |

### 1.3 Implementation Recommendations

**Priority 1 - With XY Coordinates (Coming Soon):**
1. Calculate shot distance and angle from XY coordinates
2. Detect Royal Road passes (pass crossing y=0 within 3s of shot)
3. Implement Flurry Adjustment algorithm
4. Build GBM model (XGBoost/LightGBM) with features:
   - Distance, angle, speed
   - Royal Road boolean
   - Shot type (wrist/slap/snap/tip)
   - Rush indicator
   - Previous event type
   - Time since entry

**Priority 2 - Shooting Talent:**
- Apply Bayesian regression to residuals (Goals - xG)
- Use regression threshold of 300-500 shots
- Adjust xG by shooting talent component

**Priority 3 - Model Training:**
- Train XGBoost/LightGBM on historical shot/goal data
- Use cross-validation for hyperparameter tuning
- Retrain periodically as data accumulates

---

## 2. Regularized Adjusted Plus-Minus (RAPM)

### 2.1 What the Research Prescribes

**Model Type:** Ridge Regression ($L_2$ Regularization)  
**Data Structure:** Stints (time intervals where players on ice remain constant)

**Key Concepts:**
- **Stint Definition:** Continuous duration where 10 skaters + 2 goalies remain constant
- **Design Matrix:** Sparse matrix (~50k rows × 1.2k columns per season)
- **Encoding:** Home players = 1, Away players = -1, Goalies = -1 (defense) or 0 (xG)
- **Target Variables:** GF/60, xGF/60, CA/60, xGA/60
- **Contextual Controls:** Zone starts, score state, strength state
- **Lambda Optimization:** 10-fold cross-validation

**Mathematical Formulation:**
$$\hat{\beta}_{ridge} = \underset{\beta}{\text{argmin}} \left( \sum_{i=1}^{N} w_i (y_i - x_i^T \beta)^2 + \lambda \sum_{j=1}^{p} \beta_j^2 \right)$$

**Software:** R with glmnet package (efficient sparse matrix handling)

### 2.2 What BenchSight Currently Has

**Location:** `src/tables/core_facts.py::calculate_war_stats()`

**Current Implementation:**
- ✅ Basic WAR/GAR calculation exists
- ✅ Uses component-based approach (offense, defense, possession, transition, poise)
- ✅ Has TOI-weighted calculations
- ❌ **NO RAPM methodology** (no Ridge Regression)
- ❌ **NO stint data structure**
- ❌ **NO player isolation from teammates**
- ❌ **NO multicollinearity handling**
- ❌ Uses **weighted formula**, NOT regression

**Current Formula:**
```python
GAR_WEIGHTS = {
    'goals': 1.0, 'primary_assists': 0.7, 'secondary_assists': 0.4,
    'shots_generated': 0.015, 'xg_generated': 0.8,
    'takeaways': 0.05, 'blocked_shots': 0.02,
    # ...
}
gar_offense = (goals * 1.0 + primary_assists * 0.7 + ...)
```

**Gap Analysis:**
| Feature | Research | BenchSight | Gap Severity |
|---------|----------|------------|--------------|
| Methodology | Ridge Regression (RAPM) | Weighted formula (GAR) | 🔴 **CRITICAL** |
| Data Structure | Stints (time intervals) | Game-level aggregation | 🔴 **CRITICAL** |
| Player Isolation | ✅ From teammates/opponents | ❌ Not isolated | 🔴 **HIGH** |
| Multicollinearity | ✅ Handled via regularization | ❌ Not addressed | 🔴 **HIGH** |
| Context Controls | ✅ Zone starts, score state | ⚠️ Partial (has some context) | 🟡 **MEDIUM** |
| Cross-Validation | ✅ Lambda optimization | ❌ No optimization | 🟡 **MEDIUM** |
| Component Structure | ✅ 6 components (EV Off/Def, PP, PK, Pen, Fin) | ✅ 5 components (similar structure) | ✅ **COMPLETE** |

### 2.3 Implementation Recommendations

**Priority 1 - Stint Data Structure:**
1. Create `fact_stints` table (derived from `fact_shifts`)
   - Columns: stint_id, game_id, start_time, end_time, duration
   - home_players (6 skaters), away_players (6 skaters)
   - home_goalie, away_goalie
   - zone_start, score_state, strength_state
   - GF, GA, xGF, xGA, CF, CA (accumulated during stint)

2. Stint Detection Logic:
   - New stint triggers: player substitution, goal, penalty, period end
   - Use `fact_shifts` and `fact_shift_players` to identify player changes
   - Aggregate events within stint time window

**Priority 2 - RAPM Implementation:**
1. Build design matrix from stints
   - Encode players as dummy variables (1/-1)
   - Include contextual controls (zone_start, score_state)
   - Weight by stint duration
   
2. Implement Ridge Regression:
   - Use sklearn.linear_model.RidgeCV (Python) or R glmnet
   - 10-fold cross-validation for lambda
   - Target: GF/60, xGF/60, CA/60, xGA/60

3. Run separate models for:
   - EV Offense (5v5, xGF/60)
   - EV Defense (5v5, xGA/60)
   - PP Offense (5v4/5v3, xGF/60)
   - PK Defense (4v5/3v5, xGA/60)
   - Penalties (net penalties/60)
   - Finishing (Goals - xG)/60

**Priority 3 - Integration:**
- Replace current GAR weights with RAPM coefficients
- Use RAPM ratings as input to WAR calculation
- Apply "Daisy Chain" priors for multi-season stability

---

## 3. Wins Above Replacement (WAR)

### 3.1 What the Research Prescribes

**Architecture:** Aggregation of 6 RAPM components  
**Components:** EV Offense, EV Defense, PP Offense, PK Defense, Penalties, Finishing  
**Replacement Level:** Outside top 13 F / 7 D per team by TOI  
**Conversion:** 6 Goals ≈ 1 Win

**Daisy Chain Method:**
- Use Season T-1 RAPM coefficients as priors for Season T
- Stabilizes ratings for players with limited ice time
- Bayesian approach to temporal consistency

### 3.2 What BenchSight Currently Has

**Location:** `src/tables/core_facts.py::calculate_war_stats()`

**Current Implementation:**
- ✅ WAR/GAR calculation exists
- ✅ Component-based structure (offense, defense, possession, transition, poise)
- ✅ Goals-to-Wins conversion (4.5 goals = 1 win for rec hockey)
- ❌ **NO RAPM-based components** (uses weighted formula instead)
- ❌ **NO Daisy Chain priors**
- ❌ **NO replacement level definition** (uses average as baseline)
- ⚠️ Different component structure (5 vs 6 components)

**Current Formula:**
```python
gar_total = gar_offense + gar_defense + gar_possession + gar_transition + gar_poise
war = gar_total / GOALS_PER_WIN  # 4.5 for rec hockey
```

**Gap Analysis:**
| Feature | Research | BenchSight | Gap Severity |
|---------|----------|------------|--------------|
| Component Source | RAPM coefficients | Weighted formula | 🔴 **CRITICAL** |
| Component Count | 6 (EV Off/Def, PP, PK, Pen, Fin) | 5 (Off, Def, Poss, Trans, Poise) | 🟡 **MEDIUM** |
| Replacement Level | ✅ Defined (top 13F/7D) | ❌ Uses average | 🟡 **MEDIUM** |
| Daisy Chain Priors | ✅ Multi-season | ❌ Single-season | 🟡 **MEDIUM** |
| Goals-to-Wins | ✅ 6 goals = 1 win (NHL) | ✅ 4.5 goals = 1 win (rec) | ✅ **CALIBRATED** |

### 3.3 Implementation Recommendations

**Priority 1 - Replace GAR with RAPM-based WAR:**
- Implement 6-component RAPM models (see Section 2)
- Aggregate RAPM coefficients into WAR components
- Calculate GAR from RAPM ratings
- Convert to WAR using goals-to-wins ratio

**Priority 2 - Replacement Level:**
- Define replacement as players outside top 13F/7D per team by TOI
- Calculate baseline RAPM for replacement players
- Subtract replacement baseline from player ratings

**Priority 3 - Daisy Chain Priors:**
- Store RAPM coefficients by season
- Use previous season coefficients as priors/offsets
- Apply to current season regression
- Stabilizes ratings for low-TOI players

---

## 4. Tracking Data and Microstats

### 4.1 Gap Control and Entry Defense

**Research Prescribes:**
- **Gap Definition:** Distance between defender and puck carrier at blue line entry
- **Calculation:** Euclidean distance using XY coordinates
- **Effective Gap:** $Gap_{eff} = Gap_{static} - (v_{def} \cdot \Delta t)$
- **Requires:** 25Hz tracking data (NHL EDGE)

**BenchSight Status:**
- ✅ Has zone entry tracking
- ✅ Has zone entry denials (micro stat)
- ❌ **NO XY coordinate tracking yet** (coming soon)
- ❌ **NO gap distance calculation**
- ❌ **NO velocity-based effective gap**

**Implementation (Once XY Available):**
1. Detect blue line crossing (x = ±25 ft)
2. Identify puck carrier and nearest defender
3. Calculate Euclidean gap distance
4. Calculate defender velocity
5. Compute effective gap

### 4.2 Win Direction Based Events (WDBE) for Faceoffs

**Research Prescribes:**
- Re-evaluate faceoffs by where puck goes (not just win/loss)
- Classify: "Clean" (direct to teammate) vs "Scrum" (puck battle)
- Classify direction: quadrants (Back-Center, Forward, etc.)
- Value by expected next event (Shot, Clear, Turnover)

**BenchSight Status:**
- ✅ Has faceoff win/loss tracking
- ✅ Has faceoff zone tracking
- ❌ **NO directional classification**
- ❌ **NO clean vs scrum distinction**
- ❌ **NO WDBE calculation**

**Implementation:**
1. Track faceoff outcome direction (using XY when available, or event_detail)
2. Classify as Clean/Scrum based on play_detail
3. Classify direction (Forward/Back/Center/Left/Right)
4. Calculate expected next event value
5. Sum WDBE value per player

### 4.3 Expected Threat (xT) and Possession Value

**Research Prescribes:**
- Grid-based Markov model (16×12 grid)
- Transition matrix (Zone i → Zone j probability)
- Score probability per zone
- Recursive formula: $xT_i = S_i + \sum_{j} T_{i \to j} \times xT_j$
- Player credit: $Credit = xT_{end} - xT_{start}$ (for passes)

**BenchSight Status:**
- ✅ Has rink zone dimension (dim_rink_zone)
- ✅ Has zone entry/exit tracking
- ✅ Has transition metrics
- ❌ **NO Expected Threat model**
- ❌ **NO transition probability matrix**
- ❌ **NO zone value scoring**

**Implementation (Once XY Available):**
1. Discretize rink into 16×12 grid (or use existing zones)
2. Calculate transition probabilities from historical data
3. Calculate shot-to-goal probability per zone
4. Solve recursive xT formula (iterative or matrix solve)
5. Calculate xT credit for passes/possessions
6. Aggregate per player

---

## 5. Coordinate Normalization and Rink Standardization

### 5.1 What the Research Prescribes

**Rink Geometry:**
- Center ice: (0, 0)
- X-axis: ±100 ft (goal line at ±89 ft)
- Y-axis: ±42.5 ft (boards)
- **Critical:** Period-dependent transformation (period 2 requires flip)

**Normalization Algorithm:**
- Identify event owner (attacking team)
- Determine rink side (median x of shots)
- Transform if attacking left: $x_{norm} = -1 \cdot x_{raw}$, $y_{norm} = -1 \cdot y_{raw}$

### 5.2 What BenchSight Currently Has

**Status:**
- ✅ Rink dimensions defined (GOAL_LINE_X = 89.0)
- ✅ XY coordinate structure planned (fact_player_xy, fact_puck_xy)
- ⚠️ Coordinate system not yet implemented
- ❌ **NO period-dependent normalization** (yet)

**Implementation (Once XY Available):**
1. Store raw coordinates from tracker
2. Apply period-dependent normalization
3. Standardize to offensive half (x=89, y=0 for net)
4. Use normalized coordinates for all spatial calculations

---

## 6. Summary: Implementation Priority Matrix

### Critical Gaps (Blocking Advanced Analytics)

| Gap | Impact | Dependency | Effort | Priority |
|-----|--------|------------|--------|----------|
| **RAPM Methodology** | 🔴 Cannot isolate player impact | Stint data structure | High | **P0** |
| **GBM xG Model** | 🔴 Inaccurate shot quality | XY coordinates | Medium | **P0** (with XY) |
| **Stint Data Structure** | 🔴 Required for RAPM | Shift/event data | Medium | **P0** |
| **Royal Road Detection** | 🟡 Major xG feature | XY coordinates | Low | **P1** (with XY) |
| **Flurry Adjustment** | 🟡 xG accuracy | Event sequences | Low | **P1** |

### High-Value Enhancements

| Gap | Impact | Dependency | Effort | Priority |
|-----|--------|------------|--------|----------|
| **Gap Control** | 🟡 Defensive evaluation | XY coordinates | Medium | **P2** (with XY) |
| **WDBE Faceoffs** | 🟡 Faceoff value | Event details | Low | **P2** |
| **Expected Threat (xT)** | 🟡 Possession value | XY coordinates | High | **P2** (with XY) |
| **Shooting Talent** | 🟡 xG refinement | xG model | Low | **P2** |
| **Daisy Chain Priors** | 🟡 Multi-season stability | RAPM | Low | **P2** (with RAPM) |

### Medium-Priority Refinements

| Gap | Impact | Dependency | Effort | Priority |
|-----|--------|------------|--------|----------|
| **Replacement Level** | 🟡 WAR baseline | RAPM | Low | **P3** (with RAPM) |
| **6-Component WAR** | 🟡 Component structure | RAPM | Low | **P3** (with RAPM) |
| **Lambda Optimization** | 🟡 RAPM tuning | RAPM | Medium | **P3** (with RAPM) |

---

## 7. Recommended Research Papers

Based on gaps identified, here are additional papers that would complement this analysis:

### 7.1 For xG Modeling
- **"An Expected Goals Model for Evaluating NHL Teams and Players"** (Macdonald, 2012)
- **"The Effect of Shot Location on Goal Probability"** (Schuckers, 2011)
- **"Expected Goals in Soccer: A Bayesian Approach"** (Rathke, 2017) - concepts transfer

### 7.2 For RAPM Methodology
- **"Adjusted Plus-Minus for NHL Players using Ridge Regression"** (Macdonald, 2012)
- **"Regularized Adjusted Plus-Minus for Hockey"** (Custance, 2019)
- **"A Multi-Season Study of Adjusted Plus-Minus in the NHL"** (Gramacy, 2013)

### 7.3 For Tracking/Microstats
- **"Gap Control in Hockey: A Spatial Analysis"** (various NHL EDGE analyses)
- **"Expected Threat in Soccer: A Markov Chain Approach"** (Singh, 2019) - adapt to hockey
- **"Winning Is Not Everything: A Contextual Analysis of Hockey Face-offs"** (cited in paper)

### 7.4 For General Methodology
- **Evolving Hockey blog posts** - practical implementation details
- **TopDownHockey methodology** - WAR component breakdowns
- **MoneyPuck xG methodology** - feature engineering details

---

## 8. Next Steps

### Immediate (Current Data)
1. ✅ Document gaps (this document)
2. ⏭️ Implement WDBE faceoff classification (no XY needed)
3. ⏭️ Add Flurry Adjustment to xG (uses event sequences)
4. ⏭️ Design stint data structure schema

### Short-Term (With XY Coordinates)
1. ⏭️ Implement coordinate normalization
2. ⏭️ Calculate shot distance/angle
3. ⏭️ Detect Royal Road passes
4. ⏭️ Build GBM xG model
5. ⏭️ Calculate Gap Control metrics

### Medium-Term (Advanced Analytics)
1. ⏭️ Build stint data structure
2. ⏭️ Implement RAPM (Ridge Regression)
3. ⏭️ Replace GAR with RAPM-based WAR
4. ⏭️ Implement Expected Threat (xT) model
5. ⏭️ Add Daisy Chain priors

### Long-Term (Refinement)
1. ⏭️ Shooting Talent adjustment
2. ⏭️ Replacement level definition
3. ⏭️ Lambda optimization (cross-validation)
4. ⏭️ Multi-season RAPM stability

---

## Conclusion

BenchSight has a solid foundation with event tracking, zone analytics, and basic WAR/GAR. However, the research paper reveals that modern NHL analytics rely heavily on:

1. **Sophisticated xG models** (GBM, not lookup tables)
2. **RAPM methodology** (Ridge Regression, not weighted formulas)
3. **Spatial tracking** (XY coordinates for gap control, xT, etc.)

The biggest gap is the lack of RAPM methodology, which is the industry standard for isolating player impact. This should be the top priority once XY coordinates are available, as it enables true player valuation independent of teammates.

The second biggest gap is the xG model sophistication. Moving from a lookup table to a Gradient Boosting Machine will dramatically improve shot quality assessment, especially once XY coordinates enable distance/angle calculations.

Overall, BenchSight is well-positioned to implement these methodologies once XY coordinate tracking is added. The event tracking infrastructure is solid, and the zone analytics provide a good foundation for spatial analysis.
