# NHL-Grade Analytics Benchmark

> **Purpose:** Comprehensive comparison of BenchSight analytics capabilities against industry-leading platforms (Evolving Hockey, MoneyPuck, NHL Edge, Sportslogiq) to identify gaps and prioritize improvements.

**Version:** 1.0
**Last Updated:** 2026-01-21
**Owner:** Analytics Team

---

## Table of Contents

1. [Industry Landscape](#1-industry-landscape)
2. [Platform Profiles](#2-platform-profiles)
3. [Capability Matrix](#3-capability-matrix)
4. [Detailed Gap Analysis](#4-detailed-gap-analysis)
5. [Methodology Comparison](#5-methodology-comparison)
6. [Data Requirements](#6-data-requirements)
7. [Priority Assessment](#7-priority-assessment)

---

## 1. Industry Landscape

### 1.1 Evolution of Hockey Analytics

| Era | Period | Key Developments |
|-----|--------|------------------|
| Traditional | Pre-2010 | Goals, assists, +/-, basic counting stats |
| Corsi Era | 2010-2015 | Shot attempt metrics, possession proxy |
| xG Era | 2015-2020 | Expected goals models, danger zones |
| Tracking Era | 2020+ | Player/puck tracking, speed, gap control |
| AI Era | 2023+ | Computer vision, automated event detection |

### 1.2 Current Industry Leaders

| Platform | Focus | Data Access | Business Model |
|----------|-------|-------------|----------------|
| **Evolving Hockey** | WAR/Player Value | Public NHL data | Subscription |
| **MoneyPuck** | xG/Goalie Models | Public NHL data | Free + Premium |
| **NHL Edge** | Tracking Metrics | NHL proprietary | Official NHL |
| **Sportslogiq** | Micro-Stats | Commercial | Enterprise B2B |
| **Natural Stat Trick** | Basic Analytics | Public NHL data | Free |
| **HockeyViz** | Visualization | Public NHL data | Free + Patreon |

### 1.3 BenchSight Context

**Unique Position:** Recreational hockey league analytics
- **Advantage:** Complete data ownership and access
- **Challenge:** Smaller sample sizes, variable player skill
- **Opportunity:** Apply NHL-grade methods to underserved market

---

## 2. Platform Profiles

### 2.1 Evolving Hockey

**Specialization:** WAR (Wins Above Replacement)

**Key Methodologies:**
- RAPM-based WAR with 6 components (EVO, EVD, PPO, PKD, PEN, FOW)
- Ridge regression on stint-level data
- Daisy-chain priors (use previous season as prior)
- Replacement level baseline (13th F, 7th D by TOI)
- Score/venue adjustments

**Unique Features:**
- SPAR (Standings Points Above Replacement)
- Contract projections
- Trade value analysis
- Prospect modeling

**Public Methodology:** Yes (detailed blog posts)

**Data Sources:**
- NHL play-by-play (public)
- NHL shifts (public)
- No tracking data

### 2.2 MoneyPuck

**Specialization:** Expected Goals & Goalie Models

**Key Methodologies:**
- XGBoost xG model with 22+ features
- Flurry adjustment (probability-based)
- GSAx (Goals Saved Above Expected)
- Win probability model
- Playoff odds simulation

**Unique Features:**
- Real-time xG during games
- Shot maps with xG overlay
- Goalie workload tracking
- Season simulations (10,000 iterations)

**Public Methodology:** Partial (high-level descriptions)

**Data Sources:**
- NHL play-by-play (public)
- NHL shifts (public)
- Shot location data

### 2.3 NHL Edge (Official)

**Specialization:** Tracking Metrics

**Key Methodologies:**
- Player tracking (position, speed, acceleration)
- Puck tracking (velocity, spin)
- Derived metrics from tracking data

**Unique Features:**
- Skating speed (top speed, avg speed)
- Shot speed
- Gap control (defender positioning)
- Zone time (precise to milliseconds)
- Breakaway detection

**Public Methodology:** Limited (marketing-focused)

**Data Sources:**
- Proprietary tracking system
- Chip-in-puck technology
- Arena sensors

### 2.4 Sportslogiq

**Specialization:** Micro-Statistics & Commercial Analytics

**Key Methodologies:**
- Manual event tagging (detailed)
- WDBE faceoff classification
- Board battle tracking
- Forechecking patterns
- Breakout classification

**Unique Features:**
- 50+ micro-stat types
- Video-linked events
- Team tactical analysis
- Opponent scouting reports

**Public Methodology:** No (proprietary)

**Data Sources:**
- Manual video tagging
- NHL feed data
- Multi-league coverage

---

## 3. Capability Matrix

### 3.1 Core Metrics Comparison

| Metric | BenchSight | Evolving Hockey | MoneyPuck | NHL Edge | Sportslogiq |
|--------|------------|-----------------|-----------|----------|-------------|
| Goals/Assists/Points | YES | YES | YES | YES | YES |
| TOI | YES | YES | YES | YES | YES |
| Corsi (CF/CA/CF%) | YES | YES | YES | YES | YES |
| Fenwick (FF/FA/FF%) | YES | YES | YES | YES | YES |
| Faceoff Win % | YES | YES | YES | YES | YES |
| Blocks | YES | YES | YES | YES | YES |
| Hits | PARTIAL | YES | YES | YES | YES |
| Giveaways/Takeaways | YES | YES | YES | YES | YES |

### 3.2 Expected Goals (xG)

| Feature | BenchSight | Evolving Hockey | MoneyPuck | NHL Edge | Sportslogiq |
|---------|------------|-----------------|-----------|----------|-------------|
| xG Model | LOOKUP | GBM | XGBoost | UNKNOWN | GBM |
| Distance/Angle | ZONE | CONTINUOUS | CONTINUOUS | CONTINUOUS | CONTINUOUS |
| Shot Type | YES | YES | YES | YES | YES |
| Rebound | YES | YES | YES | YES | YES |
| Rush | YES | YES | YES | YES | YES |
| One-Timer | YES | YES | YES | YES | YES |
| Royal Road | NO | YES | YES | UNKNOWN | YES |
| Flurry Adjustment | NO | YES | YES | UNKNOWN | YES |
| Shooter Talent | NO | YES | YES | UNKNOWN | YES |
| Game State | NO | YES | YES | YES | YES |

### 3.3 Player Value (WAR/GAR)

| Feature | BenchSight | Evolving Hockey | MoneyPuck | NHL Edge | Sportslogiq |
|---------|------------|-----------------|-----------|----------|-------------|
| WAR/GAR | WEIGHTED | RAPM | RAPM | NO | CUSTOM |
| Stint-Based | NO | YES | YES | N/A | UNKNOWN |
| Ridge Regression | NO | YES | YES | N/A | UNKNOWN |
| Linemate Adjustment | NO | YES | YES | N/A | YES |
| Opponent Adjustment | NO | YES | YES | N/A | YES |
| Replacement Baseline | NO | YES | YES | N/A | UNKNOWN |
| Component Breakdown | 5 | 6 | 5 | N/A | CUSTOM |

### 3.4 Transition Metrics

| Feature | BenchSight | Evolving Hockey | MoneyPuck | NHL Edge | Sportslogiq |
|---------|------------|-----------------|-----------|----------|-------------|
| Zone Entries | YES | YES | YES | YES | YES |
| Entry Type (Carry/Dump) | YES | YES | YES | YES | YES |
| Entry Success Rate | YES | YES | YES | YES | YES |
| Zone Exits | YES | YES | YES | YES | YES |
| Exit Type | YES | YES | YES | YES | YES |
| Rush Chances | YES | YES | YES | YES | YES |
| xG per Entry | PARTIAL | YES | YES | UNKNOWN | YES |

### 3.5 Micro-Statistics

| Feature | BenchSight | Evolving Hockey | MoneyPuck | NHL Edge | Sportslogiq |
|---------|------------|-----------------|-----------|----------|-------------|
| Screens | YES | NO | NO | YES | YES |
| Tips/Deflections | YES | NO | NO | YES | YES |
| Board Battles | YES | NO | NO | NO | YES |
| Poke Checks | YES | NO | NO | NO | YES |
| Forechecking | YES | NO | NO | NO | YES |
| WDBE Faceoffs | NO | NO | NO | NO | YES |
| Pass Types | YES | NO | NO | NO | YES |
| Cycle Events | YES | NO | NO | NO | YES |

### 3.6 Tracking/Spatial

| Feature | BenchSight | Evolving Hockey | MoneyPuck | NHL Edge | Sportslogiq |
|---------|------------|-----------------|-----------|----------|-------------|
| XY Coordinates | PARTIAL | LIMITED | YES | YES | YES |
| Player Speed | NO | NO | NO | YES | NO |
| Puck Speed | NO | NO | NO | YES | NO |
| Gap Control | NO | NO | NO | YES | NO |
| Heat Maps | NO | YES | YES | YES | YES |
| Shot Maps | PARTIAL | YES | YES | YES | YES |

### 3.7 Goalie Metrics

| Feature | BenchSight | Evolving Hockey | MoneyPuck | NHL Edge | Sportslogiq |
|---------|------------|-----------------|-----------|----------|-------------|
| Save % | YES | YES | YES | YES | YES |
| HD Save % | YES | YES | YES | YES | YES |
| GSAx | YES | YES | YES | YES | YES |
| Goalie WAR | YES | YES | YES | NO | CUSTOM |
| Rebound Control | YES | YES | YES | YES | YES |
| Position Tracking | NO | NO | NO | YES | NO |

---

## 4. Detailed Gap Analysis

### 4.1 Critical Gaps (P0)

#### Gap 1: No RAPM Methodology
**Current:** Weighted formula GAR
**Target:** Ridge regression RAPM
**Impact:** Cannot isolate player from linemate/opponent context
**Effort:** LARGE
**Dependencies:** Stint table

#### Gap 2: No Stint Table
**Current:** Game-level and shift-level data only
**Target:** Stint-level data (10 skaters constant)
**Impact:** Cannot implement RAPM
**Effort:** MEDIUM
**Dependencies:** Shift data (available)

#### Gap 3: No Flurry Adjustment
**Current:** Naive xG summation
**Target:** Probability-based adjustment
**Impact:** ~5% xG overstatement
**Effort:** SMALL
**Dependencies:** None

### 4.2 High Priority Gaps (P1)

#### Gap 4: Lookup-Based xG
**Current:** Zone + modifier lookup table
**Target:** GBM/XGBoost model
**Impact:** Lower accuracy (~70% vs ~78% AUC)
**Effort:** LARGE
**Dependencies:** XY coordinates, training data

#### Gap 5: No Royal Road Detection
**Current:** Not tracked
**Target:** Boolean feature for xG
**Impact:** Missing key pre-shot indicator
**Effort:** MEDIUM
**Dependencies:** XY coordinates

#### Gap 6: No Game State Features
**Current:** xG ignores score/period
**Target:** Score state and period in model
**Impact:** Context-blind predictions
**Effort:** SMALL
**Dependencies:** None

### 4.3 Medium Priority Gaps (P2)

#### Gap 7: No WDBE Faceoffs
**Current:** Win/loss only
**Target:** Won/Draw/Back/Exit classification
**Impact:** Missing faceoff quality metric
**Effort:** MEDIUM
**Dependencies:** Event detail enhancement

#### Gap 8: No Replacement Level
**Current:** Average baseline
**Target:** Replacement level (13th F, 7th D)
**Impact:** Misvalues below-average players
**Effort:** SMALL
**Dependencies:** RAPM implementation

#### Gap 9: No Shooting Talent Adjustment
**Current:** Raw xG for all shooters
**Target:** Bayesian-adjusted xG
**Impact:** Over/under credits individual skill
**Effort:** SMALL
**Dependencies:** Historical data

### 4.4 Low Priority Gaps (P3)

#### Gap 10: No Gap Control
**Current:** Not tracked
**Target:** Defender distance from puck carrier
**Impact:** Missing defensive spatial metric
**Effort:** LARGE
**Dependencies:** XY tracking + player identification

#### Gap 11: No Speed Metrics
**Current:** Not tracked
**Target:** Player/puck velocity
**Impact:** Missing dynamic context
**Effort:** VERY LARGE
**Dependencies:** Tracking infrastructure

#### Gap 12: No xT (Expected Threat)
**Current:** Not implemented
**Target:** Markov chain position value
**Impact:** Missing possession valuation
**Effort:** LARGE
**Dependencies:** XY coordinates, pass tracking

---

## 5. Methodology Comparison

### 5.1 xG Model Architecture

| Aspect | BenchSight | Industry Best Practice |
|--------|------------|----------------------|
| **Model Type** | Lookup table | XGBoost/LightGBM |
| **Features** | ~10 | 20-30 |
| **Spatial** | Zone-based | Continuous XY |
| **Interactions** | Linear (multiplicative) | Nonlinear (tree-based) |
| **Calibration** | None | Isotonic/Platt |
| **Training** | N/A | 10+ seasons |

### 5.2 WAR/GAR Architecture

| Aspect | BenchSight | Industry Best Practice |
|--------|------------|----------------------|
| **Method** | Weighted formula | RAPM (Ridge Regression) |
| **Data Grain** | Game | Stint |
| **Linemate Control** | None | Implicit in regression |
| **Opponent Control** | None | Implicit in regression |
| **Baseline** | Average (50th pct) | Replacement level |
| **Priors** | None | Daisy-chain (previous season) |

### 5.3 Transition Analysis

| Aspect | BenchSight | Industry Best Practice |
|--------|------------|----------------------|
| **Entry Types** | Carry/Pass/Dump | Same |
| **Exit Types** | Controlled/Dump | Same |
| **Outcome Linking** | Partial (entry to shot) | Full chain analysis |
| **xG Attribution** | Per-shot | Per-entry |
| **Breakout Patterns** | Basic | Detailed classification |

---

## 6. Data Requirements

### 6.1 Current Data Availability

| Data Type | BenchSight | Required For |
|-----------|------------|--------------|
| Play-by-play events | AVAILABLE | All analytics |
| Shift data | AVAILABLE | WAR, H2H |
| XY coordinates | PARTIAL | xG model, spatial |
| Shot outcomes | AVAILABLE | xG, save % |
| Game rosters | AVAILABLE | Player identification |
| Historical seasons | AVAILABLE (limited) | Priors, talent models |

### 6.2 Data Gaps

| Gap | Impact | Remediation |
|-----|--------|-------------|
| Incomplete XY | Blocks spatial features | Enhance tracking |
| No puck tracking | No speed metrics | Out of scope |
| No player tracking | No gap control | Out of scope |
| Limited seasons | Weak priors | Time (accumulate data) |

### 6.3 Data Quality Requirements

| Metric | Current | Target |
|--------|---------|--------|
| Event coverage | ~95% | >99% |
| XY accuracy | ~80% | >95% |
| Shift accuracy | ~98% | >99% |
| Goal verification | ~100% | 100% |

---

## 7. Priority Assessment

### 7.1 Priority Framework

**Scoring Criteria:**
| Criterion | Weight | Description |
|-----------|--------|-------------|
| Impact | 40% | Improvement to analytics accuracy |
| Effort | 30% | Development complexity |
| Dependencies | 20% | What must be done first |
| Visibility | 10% | User-facing benefit |

### 7.2 Prioritized Gap List

| Rank | Gap | Priority | Impact | Effort | Dependencies |
|------|-----|----------|--------|--------|--------------|
| 1 | Flurry Adjustment | P0 | MEDIUM | SMALL | None |
| 2 | Stint Table | P0 | HIGH | MEDIUM | None |
| 3 | RAPM Methodology | P0 | HIGH | LARGE | Stint Table |
| 4 | Game State Features | P1 | MEDIUM | SMALL | None |
| 5 | Royal Road Detection | P1 | MEDIUM | MEDIUM | XY Coords |
| 6 | XGBoost xG Model | P1 | HIGH | LARGE | XY Coords |
| 7 | Shooting Talent | P1 | LOW | SMALL | None |
| 8 | WDBE Faceoffs | P2 | LOW | MEDIUM | None |
| 9 | Replacement Level | P2 | MEDIUM | SMALL | RAPM |
| 10 | Gap Control | P3 | MEDIUM | LARGE | XY Tracking |
| 11 | xT Model | P3 | MEDIUM | LARGE | XY Coords |
| 12 | Speed Metrics | P3 | LOW | VERY LARGE | Tracking Infra |

### 7.3 Implementation Waves

**Wave 1: Quick Wins (No Dependencies)**
- Flurry adjustment
- Game state features
- Shooting talent adjustment

**Wave 2: Foundation (Enables RAPM)**
- Stint table
- RAPM methodology
- Replacement level

**Wave 3: XY-Dependent**
- Royal road detection
- XGBoost xG model (if XY available)
- Enhanced spatial features

**Wave 4: Future (Requires Infrastructure)**
- Gap control
- xT model
- Speed metrics

### 7.4 Success Metrics

| Gap Closed | Success Metric |
|------------|----------------|
| Flurry Adjustment | xG sum reduced by ~5% |
| RAPM | WAR correlation with weighted: 0.7-0.9 |
| XGBoost xG | AUC improved from ~70% to ~78% |
| Royal Road | xG accuracy on cross-ice plays +5% |

---

## Appendix: Industry Resources

### Public Methodologies

| Source | Link | Content |
|--------|------|---------|
| Evolving Hockey | evolving-hockey.com | WAR methodology, RAPM details |
| MoneyPuck | moneypuck.com | xG model overview, GSAx |
| Hockey-Graphs | hockey-graphs.com | Academic articles, visualizations |
| TopDownHockey | topdownhockey.com | Alternative WAR methods |

### Key Papers

1. "A Regularized Adjusted Plus-Minus Statistic for NHL Players" - Macdonald (2011)
2. "Expected Goals in Hockey" - Various (Sportslogiq, CrowdScout)
3. "Wins Above Replacement: History, Development, and Shortcomings" - Evolving Hockey

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-21 | Analytics Team | Initial benchmark comparison |
