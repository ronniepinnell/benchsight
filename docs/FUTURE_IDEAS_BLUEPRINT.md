# BenchSight Future Ideas & Blueprint

**Version:** 1.0  
**Date:** December 30, 2025

---

## Table of Contents

1. [Missing Metrics to Add](#missing-metrics-to-add)
2. [Power Play / Penalty Kill Stats](#power-play--penalty-kill-stats)
3. [Advanced Analytics Roadmap](#advanced-analytics-roadmap)
4. [ML/AI Integration](#mlai-integration)
5. [CV/Tracking Data](#cvtracking-data)
6. [NHL Data Integration](#nhl-data-integration)
7. [Technical Improvements](#technical-improvements)
8. [UI/UX Enhancements](#uiux-enhancements)

---

## Missing Metrics to Add

### Priority 1: Power Play / Penalty Kill (NOT CURRENTLY IMPLEMENTED)

**Current State:**
- ✅ `dim_situation` has PP/PK situations defined
- ✅ `dim_strength` has strength states (5v4, 4v5, etc.)
- ✅ `fact_shifts` tracks `situation`, `strength`, `home_team_pp`, `home_team_pk`
- ✅ `fact_player_game_stats` has `shorthanded_goals`
- ❌ NO aggregated PP/PK success metrics

**Metrics to Add:**

#### Team Level (`fact_team_game_stats`)
```
pp_opportunities      -- Number of power plays
pp_goals              -- Goals scored on PP
pp_pct                -- PP% = pp_goals / pp_opportunities
pp_toi                -- Time on power play (seconds)
pp_shots              -- Shots on PP
pp_xg                 -- Expected goals on PP

pk_opportunities      -- Times shorthanded
pk_goals_against      -- Goals allowed on PK
pk_pct                -- PK% = 1 - (pk_goals_against / pk_opportunities)
pk_toi                -- Time on penalty kill (seconds)
pk_shots_against      -- Shots against on PK
shg                   -- Shorthanded goals scored
sha                   -- Shorthanded goals against
```

#### Player Level (`fact_player_game_stats`)
```
pp_toi                -- PP time on ice
pp_goals              -- PP goals
pp_assists            -- PP assists (PP1, PP2)
pp_points             -- PP points
pp_shots              -- Shots on PP
pp_cf_pct             -- Corsi % on PP

pk_toi                -- PK time on ice
pk_goals_against      -- Goals against on PK
pk_blocks             -- Blocks on PK
pk_cf_pct             -- Corsi % on PK
shg                   -- Shorthanded goals
sha                   -- Shorthanded assists
```

#### Implementation SQL
```sql
-- Calculate PP stats from shifts
SELECT 
    game_id,
    team_id,
    COUNT(DISTINCT shift_key) FILTER (WHERE situation LIKE '%PowerPlay%') as pp_opportunities,
    SUM(CASE WHEN situation LIKE '%PowerPlay%' THEN home_goals ELSE 0 END) as pp_goals,
    SUM(CASE WHEN situation LIKE '%PowerPlay%' THEN shift_duration ELSE 0 END) as pp_toi
FROM fact_shifts
GROUP BY game_id, team_id;
```

---

## Power Play / Penalty Kill Stats

### Full Implementation Plan

#### Step 1: Add columns to `fact_team_game_stats`

```python
# In ETL, add to team stats calculation
def calculate_pp_pk_stats(shifts_df, events_df):
    """Calculate power play and penalty kill statistics"""
    
    # PP opportunities = unique PP shifts
    pp_shifts = shifts_df[shifts_df['situation'].str.contains('PowerPlay')]
    pp_opportunities = pp_shifts.groupby(['game_id', 'team_id']).size()
    
    # PP goals from events during PP shifts
    pp_goals = events_df[
        (events_df['event_type'] == 'Goal') & 
        (events_df['shift_key'].isin(pp_shifts['shift_key']))
    ].groupby(['game_id', 'team_id']).size()
    
    # PP%
    pp_pct = (pp_goals / pp_opportunities * 100).round(1)
    
    return {
        'pp_opportunities': pp_opportunities,
        'pp_goals': pp_goals,
        'pp_pct': pp_pct
    }
```

#### Step 2: Add columns to `fact_player_game_stats`

```python
def calculate_player_pp_stats(shifts_player_df, events_player_df):
    """Calculate player-level PP/PK stats"""
    
    # PP TOI
    pp_toi = shifts_player_df[
        shifts_player_df['situation'].str.contains('PowerPlay')
    ].groupby(['game_id', 'player_id'])['shift_duration'].sum()
    
    # PP goals/assists from events
    pp_goals = events_player_df[
        (events_player_df['event_type'] == 'Goal') &
        (events_player_df['is_pp'] == True)
    ].groupby(['game_id', 'player_id']).size()
    
    return {
        'pp_toi': pp_toi,
        'pp_goals': pp_goals
    }
```

#### Step 3: Create new view for PP/PK leaderboards

```sql
CREATE VIEW v_pp_leaders AS
SELECT 
    player_name,
    SUM(pp_goals) as total_pp_goals,
    SUM(pp_assists) as total_pp_assists,
    SUM(pp_points) as total_pp_points,
    SUM(pp_toi) / 60 as total_pp_minutes,
    ROUND(SUM(pp_goals)::numeric / NULLIF(SUM(pp_toi) / 3600, 0), 2) as pp_goals_per_60
FROM fact_player_game_stats
GROUP BY player_id, player_name
ORDER BY total_pp_points DESC;
```

---

## Advanced Analytics Roadmap

### Phase 1: Basic Advanced Stats (Q1)
- [ ] PP/PK success metrics
- [ ] Individual expected goals (ixG)
- [ ] Goals Above Expected (GAE)
- [ ] High-danger scoring chances

### Phase 2: Possession Metrics (Q2)
- [ ] Zone time percentages
- [ ] Controlled entry/exit rates
- [ ] Possession time per shift
- [ ] Cycle time in offensive zone

### Phase 3: Player Impact (Q3)
- [ ] RAPM (Regularized Adjusted Plus-Minus)
- [ ] WAR (Wins Above Replacement)
- [ ] Defensive impact metrics
- [ ] Goalie Quality Starts

### Phase 4: Predictive Analytics (Q4)
- [ ] Win probability model
- [ ] Player projection system
- [ ] Line optimization algorithm
- [ ] Game outcome predictions

---

## ML/AI Integration

### Expected Goals (xG) Model

**Current State:** xG columns exist but are mostly 0 (no model trained)

**Implementation Plan:**

1. **Data Collection**
   - Shot location (x, y coordinates)
   - Shot type (wrist, slap, snap, backhand)
   - Shot distance from net
   - Shot angle
   - Is rebound (yes/no)
   - Is rush (yes/no)
   - Game state (score differential)
   - Strength state (5v5, PP, PK)

2. **Model Training**
   ```python
   from sklearn.ensemble import GradientBoostingClassifier
   
   features = ['distance', 'angle', 'shot_type', 'is_rebound', 
               'is_rush', 'score_diff', 'strength']
   
   model = GradientBoostingClassifier()
   model.fit(X_train[features], y_train['is_goal'])
   
   # Predict xG
   shots['xg'] = model.predict_proba(shots[features])[:, 1]
   ```

3. **Integration**
   - Add xG to `fact_events` for each shot
   - Aggregate to player/team level
   - Create xG leaderboards

### Player Similarity Model

Find players with similar playing styles:

```python
from sklearn.metrics.pairwise import cosine_similarity

# Feature vector per player
features = ['goals_per_60', 'assists_per_60', 'shots_per_60', 
            'hits_per_60', 'blocks_per_60', 'cf_pct']

player_vectors = player_stats[features].values
similarity_matrix = cosine_similarity(player_vectors)

# Find most similar players
def find_similar_players(player_id, top_n=5):
    idx = player_index[player_id]
    similarities = similarity_matrix[idx]
    top_indices = similarities.argsort()[-top_n-1:-1][::-1]
    return players.iloc[top_indices]
```

### Line Optimization

Optimize line combinations using WOWY data:

```python
from scipy.optimize import linear_sum_assignment

def optimize_lines(wowy_matrix, players):
    """Find optimal line combinations"""
    # Build synergy matrix from WOWY
    synergy = wowy_matrix.pivot(
        index='player_1_id', 
        columns='player_2_id', 
        values='cf_pct_delta'
    )
    
    # Use Hungarian algorithm to maximize total synergy
    row_ind, col_ind = linear_sum_assignment(-synergy.values)
    
    return optimal_pairings
```

---

## CV/Tracking Data

### Tables Ready for CV Data (Currently Empty)

| Table | Purpose | Status |
|-------|---------|--------|
| `fact_player_xy_long` | Player positions over time | Schema ready |
| `fact_player_xy_wide` | Player positions (wide format) | Schema ready |
| `fact_puck_xy_long` | Puck positions over time | Schema ready |
| `fact_puck_xy_wide` | Puck positions (wide format) | Schema ready |
| `fact_shot_xy` | Shot coordinates | Schema ready |

### CV Integration Plan

1. **Video Processing Pipeline**
   ```
   Game Video → Frame Extraction → Object Detection → Position Tracking → Database
   ```

2. **Required Data Format**
   ```csv
   game_id,frame_number,timestamp,player_id,x,y,team,jersey_number
   18969,1500,125.5,P100023,45.2,22.1,home,17
   ```

3. **Metrics from Tracking**
   - Player speed
   - Distance skated
   - Space creation
   - Defensive positioning
   - Passing lanes

---

## NHL Data Integration

### API Integration

```python
import requests

def fetch_nhl_game(nhl_game_id):
    """Fetch game data from NHL API"""
    url = f"https://statsapi.web.nhl.com/api/v1/game/{nhl_game_id}/feed/live"
    response = requests.get(url)
    return response.json()

def map_to_benchsight_schema(nhl_data):
    """Transform NHL data to BenchSight format"""
    events = []
    for play in nhl_data['liveData']['plays']['allPlays']:
        events.append({
            'event_type': play['result']['event'],
            'period': play['about']['period'],
            'time': play['about']['periodTime'],
            # ... map other fields
        })
    return events
```

### Use Cases

1. **Benchmarking** - Compare rec league stats to NHL averages
2. **Context** - "Your CF% of 55% would rank top-10 in NHL"
3. **Learning** - Show NHL video of similar plays
4. **Scouting** - Compare rec players to NHL player archetypes

---

## Technical Improvements

### Performance Optimization

1. **Database Indexes**
   ```sql
   CREATE INDEX idx_events_game_type ON fact_events(game_id, event_type);
   CREATE INDEX idx_shifts_game_period ON fact_shifts(game_id, period);
   CREATE INDEX idx_wowy_players ON fact_wowy(player_1_id, player_2_id);
   ```

2. **Materialized Views**
   ```sql
   CREATE MATERIALIZED VIEW mv_player_season_stats AS
   SELECT player_id, SUM(goals), SUM(assists), ...
   FROM fact_player_game_stats
   GROUP BY player_id;
   ```

3. **Caching Layer**
   - Redis for frequently accessed data
   - CDN for static assets

### Data Quality

1. **Automated Validation**
   - Run tests after every ETL
   - Alert on anomalies
   - Track data quality scores

2. **Reconciliation**
   - Compare to noradhockey.com nightly
   - Flag discrepancies
   - Auto-correct where possible

---

## UI/UX Enhancements

### Mobile App
- React Native or Flutter
- Push notifications for game updates
- Offline mode for tracking

### Real-time Features
- Live game tracking
- WebSocket updates
- Live leaderboards

### Gamification
- Achievements (First Hat Trick, etc.)
- Season challenges
- Player rankings

### Social Features
- Share highlights
- Comment on plays
- Team chat

---

## Priority Matrix

| Feature | Impact | Effort | Priority |
|---------|--------|--------|----------|
| PP/PK Stats | High | Low | **P1** |
| xG Model | High | Medium | P2 |
| CV Tracking | High | High | P3 |
| NHL Integration | Medium | Medium | P3 |
| Mobile App | Medium | High | P4 |
| Real-time | Medium | High | P4 |

---

## Timeline Estimate

| Quarter | Focus |
|---------|-------|
| Q1 2025 | PP/PK stats, Data validation, Portal MVP |
| Q2 2025 | xG model, Dashboard polish, More games |
| Q3 2025 | CV integration pilot, NHL benchmarking |
| Q4 2025 | Mobile app, Real-time tracking |
