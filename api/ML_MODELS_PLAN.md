# ML Models Plan - Dream Big 🚀

## Overview

Comprehensive ML models for hockey analytics covering predictions, comparisons, and advanced insights.

---

## 🎯 Model Categories

### 1. Game Outcome Predictions

#### 1.1 Matchup Winner Prediction
**Goal:** Predict game winner and score

**Features:**
- Team stats (GF/GA, CF%, PP%, PK%)
- Head-to-head history
- Home/away records
- Recent form (last 10 games)
- Goalie matchups
- Injury reports
- Rest days

**Output:**
- Win probability (home/away)
- Predicted score
- Over/under probability
- Key factors (why team X wins)

**Use Cases:**
- Pre-game predictions
- Betting insights
- Game previews

---

#### 1.2 Real-Time Win Probability
**Goal:** Update win probability during live game

**Features:**
- Current score
- Time remaining
- Period
- Power play status
- Shot attempts
- xG differential
- Momentum (recent goals)

**Output:**
- Win probability (updates every second)
- Next goal probability
- Comeback probability

**Use Cases:**
- Live game dashboard
- In-game analytics
- Broadcast graphics

---

#### 1.3 Power Play Success Prediction
**Goal:** Predict if power play will score

**Features:**
- Team PP% (season, recent)
- Opponent PK%
- Players on ice
- Zone entry success rate
- Shot generation rate
- Time remaining in PP

**Output:**
- PP goal probability
- Expected goals on PP
- Key players to watch

**Use Cases:**
- In-game strategy
- Player deployment decisions

---

### 2. Player Performance Predictions

#### 2.1 Season Projections
**Goal:** Predict final season stats

**Features:**
- Current stats (goals, assists, points)
- Games played / remaining
- Historical performance
- Age/experience
- Team quality
- TOI trends
- Injury history

**Output:**
- Projected goals/assists/points
- Confidence intervals
- Milestone probabilities (50 goals, 100 points)
- Percentile rankings

**Use Cases:**
- Player pages
- Season projections dashboard
- Fantasy hockey

---

#### 2.2 Game-by-Game Predictions
**Goal:** Predict player performance in next game

**Features:**
- Recent form (last 5/10 games)
- Opponent quality
- Home/away
- Line matchups
- Historical vs opponent
- Rest days
- Injury status

**Output:**
- Predicted goals/assists/points
- Multi-point game probability
- Hat trick probability
- WAR prediction

**Use Cases:**
- Pre-game player previews
- Lineup optimization
- Fantasy lineups

---

#### 2.3 Breakout Player Detection
**Goal:** Identify players about to break out

**Features:**
- Underlying metrics (xG, CF%, etc.)
- Recent trends
- Age/experience
- TOI changes
- Line promotion
- Shot quality improvements

**Output:**
- Breakout probability
- Expected improvement
- Timeline (when breakout happens)

**Use Cases:**
- Scouting reports
- Trade targets
- Fantasy pickups

---

#### 2.4 Rookie Performance Prediction
**Goal:** Predict rookie season performance

**Features:**
- Pre-draft stats
- Draft position
- Team quality
- Expected role/TOI
- Position
- Age
- Junior/college stats

**Output:**
- Rookie season projections
- Calder Trophy probability
- Development trajectory

**Use Cases:**
- Draft analysis
- Rookie rankings
- Long-term projections

---

### 3. Player Comparisons & Similarity

#### 3.1 Similar Player Finder
**Goal:** Find players with similar play styles

**Features:**
- All 317 stat columns
- Micro stats (zone entries, rushes, etc.)
- Physical attributes
- Position
- Role (scorer, playmaker, defensive)

**Output:**
- Top 10 similar players
- Similarity score (0-100)
- Key similarities
- Key differences

**Use Cases:**
- Player comparisons
- Scouting
- Trade value estimation

---

#### 3.2 Player Value Comparison
**Goal:** Compare player value across different metrics

**Features:**
- WAR/GAR
- Points
- Advanced metrics
- Contract/salary (if available)
- Age
- Position scarcity

**Output:**
- Value score
- Value per dollar
- Trade value ranking

**Use Cases:**
- Trade analysis
- Free agent evaluation
- Contract negotiations

---

#### 3.3 Player Archetype Classification
**Goal:** Classify players into archetypes

**Archetypes:**
- Elite Scorer
- Playmaker
- Two-Way Forward
- Defensive Specialist
- Power Forward
- Speedster
- Clutch Performer
- etc.

**Features:**
- All stats
- Micro stats
- Physical play
- Situational performance

**Output:**
- Primary archetype
- Secondary archetype
- Archetype confidence

**Use Cases:**
- Player profiles
- Team composition analysis
- Scouting

---

### 4. Line Chemistry & Optimization

#### 4.1 Line Chemistry Score
**Goal:** Predict how well players work together

**Features:**
- Historical performance together
- Complementary skills
- Position fit
- Play style compatibility
- xG when together
- CF% when together

**Output:**
- Chemistry score (0-100)
- Expected goals together
- Expected CF% together
- Optimal deployment (5v5, PP, PK)

**Use Cases:**
- Lineup optimization
- Line combinations
- Trade analysis

---

#### 4.2 Optimal Lineup Generator
**Goal:** Generate best possible line combinations

**Features:**
- All player stats
- Chemistry scores
- Opponent matchups
- Fatigue/rest
- Injury status

**Output:**
- Optimal forward lines
- Optimal defense pairs
- Power play units
- Penalty kill units
- Expected performance

**Use Cases:**
- Coach's assistant
- Lineup suggestions
- What-if scenarios

---

### 5. Goalie Analytics

#### 5.1 Goalie Performance Prediction
**Goal:** Predict goalie stats for next game/season

**Features:**
- Recent form
- Opponent shot quality
- Team defense quality
- Home/away
- Rest days
- Historical vs opponent

**Output:**
- Predicted save %
- Predicted GAA
- Shutout probability
- Quality start probability

**Use Cases:**
- Goalie deployment
- Fantasy hockey
- Game predictions

---

#### 5.2 Goalie Matchup Analysis
**Goal:** Analyze goalie vs team matchups

**Features:**
- Historical performance vs team
- Team shot locations
- Team shot types
- Goalie strengths/weaknesses

**Output:**
- Matchup advantage/disadvantage
- Expected save %
- Key matchups to watch

**Use Cases:**
- Pre-game analysis
- Goalie selection

---

### 6. Advanced Analytics Predictions

#### 6.1 WAR/GAR Predictions
**Goal:** Predict future WAR/GAR

**Features:**
- Current WAR/GAR
- Underlying metrics
- Trends
- Age
- Role changes

**Output:**
- Projected WAR/GAR
- Confidence intervals
- Percentile projections

**Use Cases:**
- Player value
- Contract negotiations
- Trade analysis

---

#### 6.2 xG Model Enhancement
**Goal:** Improve xG predictions using ML

**Features:**
- Shot location (XY coordinates)
- Shot type
- Shot angle
- Distance
- Traffic/screens
- Rush vs set play
- Time since entry

**Output:**
- Enhanced xG value
- Goal probability
- Shot quality score

**Use Cases:**
- Better xG calculations
- Shot quality analysis
- Finishing skill assessment

---

#### 6.3 Zone Entry Success Prediction
**Goal:** Predict if zone entry will be successful

**Features:**
- Entry type (controlled vs dump)
- Players involved
- Opponent players
- Zone (OZ, NZ, DZ)
- Game state
- Time on shift

**Output:**
- Entry success probability
- Shot generation probability
- Goal generation probability

**Use Cases:**
- Strategy optimization
- Player deployment
- Coaching insights

---

### 7. Injury & Health Predictions

#### 7.1 Injury Risk Assessment
**Goal:** Predict injury risk for players

**Features:**
- Age
- Injury history
- Games played
- TOI trends
- Physical play (hits, blocks)
- Fatigue metrics
- Position

**Output:**
- Injury risk score (0-100)
- Most likely injury type
- Recommended rest days

**Use Cases:**
- Player management
- Load management
- Fantasy hockey

---

#### 7.2 Performance After Injury
**Goal:** Predict performance recovery after injury

**Features:**
- Injury type
- Injury duration
- Age
- Historical recovery
- Position
- Pre-injury performance

**Output:**
- Recovery timeline
- Performance degradation
- Full recovery probability

**Use Cases:**
- Return-to-play decisions
- Fantasy hockey
- Team planning

---

### 8. Team Performance Predictions

#### 8.1 Playoff Probability
**Goal:** Predict playoff chances

**Features:**
- Current standings
- Remaining schedule
- Team quality metrics
- Recent form
- Strength of schedule
- Head-to-head records

**Output:**
- Playoff probability
- Seed probability
- Championship probability

**Use Cases:**
- Standings page
- Season projections
- Fan engagement

---

#### 8.2 Championship Odds
**Goal:** Predict championship probability

**Features:**
- Team quality (WAR, GAR, CF%)
- Playoff experience
- Goalie quality
- Depth
- Recent form
- Health

**Output:**
- Championship probability
- Conference final probability
- Round-by-round odds

**Use Cases:**
- Pre-season predictions
- Trade deadline analysis
- Fan engagement

---

#### 8.3 Team Chemistry Score
**Goal:** Measure team cohesion

**Features:**
- Player compatibility
- Line chemistry
- Locker room factors (if available)
- Performance vs expectations
- Clutch performance

**Output:**
- Team chemistry score
- Chemistry trends
- Impact on performance

**Use Cases:**
- Team analysis
- Trade impact
- Coaching decisions

---

### 9. Draft & Scouting

#### 9.1 Prospect Evaluation
**Goal:** Evaluate draft prospects

**Features:**
- Junior/college stats
- Age
- Position
- Physical attributes
- Scouting reports (if available)

**Output:**
- NHL readiness score
- Ceiling projection
- Floor projection
- Development timeline

**Use Cases:**
- Draft analysis
- Scouting reports
- Prospect rankings

---

#### 9.2 Draft Position Prediction
**Goal:** Predict where player will be drafted

**Features:**
- Prospect evaluation
- Team needs
- Draft position
- Historical draft patterns

**Output:**
- Draft position range
- Probability by round
- Best fit teams

**Use Cases:**
- Draft preview
- Mock drafts
- Scouting

---

### 10. Real-Time Game Analytics

#### 10.1 Next Goal Scorer Prediction
**Goal:** Predict who scores next goal

**Features:**
- Current game state
- Player on-ice
- Recent form
- Historical vs opponent
- Shot attempts in game
- xG in game

**Output:**
- Top 10 most likely scorers
- Goal probability for each
- Time until next goal (expected)

**Use Cases:**
- Live game dashboard
- Broadcast graphics
- Fan engagement

---

#### 10.2 Momentum Detection
**Goal:** Detect game momentum shifts

**Features:**
- Recent events (goals, shots, saves)
- Time between events
- Score differential
- Period
- Special teams

**Output:**
- Momentum score (-100 to +100)
- Momentum trend
- Momentum impact on win probability

**Use Cases:**
- Live game analysis
- Coaching insights
- Broadcast commentary

---

## 🏗️ Implementation Priority

### Phase 1: Core Predictions (MVP)
1. ✅ Game Outcome Prediction
2. ✅ Season Projections
3. ✅ Similar Player Finder
4. ✅ Playoff Probability

### Phase 2: Advanced Predictions
5. ✅ Game-by-Game Predictions
6. ✅ Line Chemistry
7. ✅ Goalie Predictions
8. ✅ Real-Time Win Probability

### Phase 3: Advanced Analytics
9. ✅ xG Enhancement
10. ✅ Injury Risk
11. ✅ Breakout Detection
12. ✅ Optimal Lineup Generator

### Phase 4: Specialized Features
13. ✅ Rookie Predictions
14. ✅ Draft Analysis
15. ✅ Next Goal Scorer
16. ✅ Momentum Detection

---

## 📊 Model Types by Use Case

| Model | Type | Training Frequency | Inference Frequency |
|-------|------|-------------------|---------------------|
| Game Outcome | XGBoost/LightGBM | Weekly | Pre-game |
| Season Projections | Regression | Daily | Daily |
| Similar Players | Clustering/Embeddings | Weekly | On-demand |
| Line Chemistry | Regression | Weekly | On-demand |
| Real-Time Win Prob | Logistic Regression | Weekly | Every second |
| Next Goal Scorer | XGBoost | Weekly | Every event |
| Injury Risk | Classification | Weekly | Daily |
| xG Enhancement | Neural Network | Monthly | Every shot |

---

## 🎯 Success Metrics

### Prediction Accuracy
- Game outcome: >60% accuracy
- Season projections: Within 10% of actual
- Player comparisons: >80% similarity match

### Business Impact
- User engagement: +50% on prediction pages
- Time on site: +30%
- Return visits: +40%

---

## 🚀 Next Steps

1. **Data Preparation**
   - Feature engineering pipeline
   - Historical data collection
   - Real-time data feeds

2. **Model Development**
   - Start with Phase 1 models
   - Baseline models first
   - Iterate and improve

3. **Infrastructure**
   - ML training pipeline
   - Model serving (FastAPI)
   - Database views for pre-computed

4. **UI Integration**
   - Prediction dashboards
   - Real-time updates
   - Interactive visualizations

---

**Total Models Planned:** 20+  
**Priority Models:** 4 (Phase 1)  
**Dream Features:** All of them! 🎉
