# ML Layer Architecture

## Overview

The ML layer should **NOT** be directly accessible from the UI dashboard. It should be accessed through the FastAPI backend for security, performance, and proper architecture separation.

---

## Architecture Diagram

```
┌─────────────────┐
│  UI Dashboard   │
│   (Next.js)     │
└────────┬────────┘
         │
         │ HTTP Requests
         │
    ┌────┴────┬──────────────────┐
    │         │                  │
    │         │                  │
    ▼         ▼                  ▼
┌─────────┐ ┌──────────┐ ┌──────────┐
│Supabase │ │ FastAPI  │ │FastAPI   │
│(Views)  │ │(/api/ml) │ │(ETL)     │
└────┬────┘ └────┬─────┘ └──────────┘
     │           │
     │           ▼
     │      ┌─────────┐
     │      │ ML Layer│
     │      │ (Python)│
     │      └────┬────┘
     │           │
     └───────────┘
           │
           ▼
     ┌──────────┐
     │ Database │
     │(Supabase)│
     └──────────┘
```

---

## Three Access Patterns

### 1. Pre-Computed ML Results (Best for Historical Analytics)

**How it works:**
- ML models run during ETL (offline/batch)
- Results stored in Supabase views/materialized views
- UI queries views directly (like current stats)

**Implementation:**
```sql
-- Example: Pre-computed player predictions
CREATE MATERIALIZED VIEW mv_player_predictions AS
SELECT 
    player_id,
    season_id,
    predicted_goals,
    predicted_points,
    prediction_confidence,
    model_version,
    updated_at
FROM ml_predictions
```

**UI Usage:**
```typescript
// UI queries pre-computed results directly from Supabase
const { data } = await supabase
  .from('mv_player_predictions')
  .select('*')
  .eq('player_id', playerId)
```

**When to use:**
- ✅ Historical predictions (season projections)
- ✅ Model results that don't change often
- ✅ Analytics dashboards
- ✅ Performance-critical queries

---

### 2. FastAPI ML Endpoints (Best for Real-Time Predictions)

**How it works:**
- UI makes HTTP requests to FastAPI
- FastAPI loads ML models and makes predictions
- Results returned to UI (not stored in DB)

**Implementation:**

**FastAPI Route (`api/routes/ml.py`):**
```python
from fastapi import APIRouter, HTTPException
from ..services.ml_service import ml_service
from ..models.ml import PredictPlayerStatsRequest, PredictPlayerStatsResponse

router = APIRouter(prefix="/api/ml", tags=["ml"])

@router.post("/predict/player-stats", response_model=PredictPlayerStatsResponse)
async def predict_player_stats(request: PredictPlayerStatsRequest):
    """
    Predict player stats for remainder of season.
    
    Uses trained ML models to predict goals, assists, points, etc.
    """
    try:
        predictions = ml_service.predict_player_stats(
            player_id=request.player_id,
            season_id=request.season_id,
            games_remaining=request.games_remaining
        )
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**ML Service (`api/services/ml_service.py`):**
```python
import joblib
import numpy as np
from pathlib import Path

class MLService:
    def __init__(self):
        # Load pre-trained models
        self.model_dir = Path(__file__).parent.parent / "models"
        self.goals_model = joblib.load(self.model_dir / "goals_model.pkl")
        self.assists_model = joblib.load(self.model_dir / "assists_model.pkl")
        self.points_model = joblib.load(self.model_dir / "points_model.pkl")
    
    def predict_player_stats(self, player_id: str, season_id: str, games_remaining: int):
        # Fetch player features from database
        features = self._get_player_features(player_id, season_id)
        
        # Make predictions
        predicted_goals = self.goals_model.predict([features])[0]
        predicted_assists = self.assists_model.predict([features])[0]
        predicted_points = self.points_model.predict([features])[0]
        
        return {
            "player_id": player_id,
            "season_id": season_id,
            "games_remaining": games_remaining,
            "predicted_goals": float(predicted_goals),
            "predicted_assists": float(predicted_assists),
            "predicted_points": float(predicted_points),
            "confidence": 0.85,
            "model_version": "1.0.0"
        }
```

**UI Usage:**
```typescript
// UI calls FastAPI endpoint
const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/ml/predict/player-stats`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    player_id: playerId,
    season_id: seasonId,
    games_remaining: 20
  })
})

const predictions = await response.json()
```

**When to use:**
- ✅ Real-time predictions (what-if scenarios)
- ✅ Interactive model exploration
- ✅ Model inference on-demand
- ✅ Custom prediction parameters

---

### 3. Scheduled ML Jobs (Best for Batch Processing)

**How it works:**
- ML jobs run on schedule (e.g., daily/weekly)
- Results stored in database
- UI queries results like any other stat

**Implementation:**

**Scheduled Job (run via cron or ETL):**
```python
# Scheduled to run daily at 2 AM
def daily_ml_predictions_job():
    ml_service = MLService()
    
    # Get all active players
    players = get_active_players()
    
    for player in players:
        # Generate predictions
        predictions = ml_service.predict_player_stats(
            player_id=player.id,
            season_id=get_current_season(),
            games_remaining=get_games_remaining()
        )
        
        # Store in database
        store_predictions(predictions)
```

**UI Usage:**
```typescript
// UI queries stored predictions
const { data } = await supabase
  .from('ml_player_predictions')
  .select('*')
  .eq('player_id', playerId)
  .eq('season_id', seasonId)
  .single()
```

**When to use:**
- ✅ Daily/weekly predictions
- ✅ Season projections
- ✅ League-wide predictions
- ✅ Resource-intensive models

---

## Recommended Implementation Plan

### Phase 1: Pre-Computed Results (Start Here)

1. **Create ML views in SQL:**
   ```sql
   -- Store ML predictions as materialized views
   CREATE MATERIALIZED VIEW mv_ml_player_predictions AS ...
   ```

2. **Update ETL to generate predictions:**
   ```python
   # In ETL post-processing
   def generate_ml_predictions():
       # Load models
       # Make predictions
       # Store in database
   ```

3. **UI queries views directly:**
   ```typescript
   // Same pattern as current stats queries
   const { data } = await supabase.from('mv_ml_player_predictions').select('*')
   ```

### Phase 2: Add FastAPI ML Endpoints (Later)

1. **Add ML routes to FastAPI:**
   ```python
   # api/routes/ml.py
   @router.post("/predict/player-stats")
   async def predict_player_stats(...)
   ```

2. **Create ML service:**
   ```python
   # api/services/ml_service.py
   class MLService:
       def predict_player_stats(...)
   ```

3. **UI calls FastAPI:**
   ```typescript
   // For real-time predictions
   const response = await fetch('/api/ml/predict/player-stats', {...})
   ```

---

## Why NOT Direct Access?

### Security Reasons:
- ❌ ML models shouldn't be exposed to frontend
- ❌ Training data shouldn't be accessible
- ❌ Model files should stay on server

### Performance Reasons:
- ❌ ML inference is CPU/GPU intensive (should be server-side)
- ❌ Large model files shouldn't be downloaded to browser
- ❌ Batch processing should run on server

### Architecture Reasons:
- ❌ Violates separation of concerns
- ❌ Makes caching/deduplication harder
- ❌ Harder to version and deploy models

---

## Example: Player Prediction Feature

### Step 1: Create ML View (Pre-computed)

```sql
CREATE MATERIALIZED VIEW mv_ml_player_season_predictions AS
SELECT 
    p.player_id,
    p.season_id,
    -- Current stats
    p.goals as current_goals,
    p.assists as current_assists,
    p.points as current_points,
    -- Predicted stats (populated by ML job)
    ml.predicted_goals,
    ml.predicted_assists,
    ml.predicted_points,
    ml.prediction_confidence,
    ml.games_remaining,
    -- Calculated
    ml.predicted_goals - p.goals as goals_remaining,
    ml.predicted_points - p.points as points_remaining
FROM fact_player_season_stats_basic p
LEFT JOIN ml_player_predictions ml 
    ON p.player_id = ml.player_id 
    AND p.season_id = ml.season_id
WHERE p.game_type = 'All';
```

### Step 2: UI Queries View

```typescript
// ui/dashboard/src/app/norad/(dashboard)/players/[playerId]/page.tsx

const { data: predictions } = await supabase
  .from('mv_ml_player_season_predictions')
  .select('*')
  .eq('player_id', playerId)
  .eq('season_id', seasonId)
  .single()

// Display predictions in UI
<p>Predicted Goals: {predictions.predicted_goals}</p>
<p>Goals Remaining: {predictions.goals_remaining}</p>
```

### Step 3: ML Job Updates Predictions (Daily)

```python
# Run via cron or ETL post-processing
def update_ml_predictions():
    ml_service = MLService()
    
    # Get all active players
    players = get_active_players()
    
    predictions = []
    for player in players:
        pred = ml_service.predict_player_stats(
            player_id=player.id,
            season_id=get_current_season()
        )
        predictions.append(pred)
    
    # Store in database
    store_predictions(predictions)
    
    # Refresh materialized view
    refresh_materialized_view('mv_ml_player_season_predictions')
```

---

## FastAPI ML Endpoints (For Real-Time)

### Add ML Routes

```python
# api/routes/ml.py
from fastapi import APIRouter, HTTPException
from ..services.ml_service import ml_service

router = APIRouter(prefix="/api/ml", tags=["ml"])

@router.post("/predict/player-stats")
async def predict_player_stats(request: PredictPlayerStatsRequest):
    """Real-time player stats prediction."""
    try:
        return ml_service.predict_player_stats(
            player_id=request.player_id,
            season_id=request.season_id,
            games_remaining=request.games_remaining
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict/game-outcome")
async def predict_game_outcome(request: PredictGameRequest):
    """Predict game winner and score."""
    return ml_service.predict_game_outcome(
        home_team_id=request.home_team_id,
        away_team_id=request.away_team_id
    )
```

### Register Routes

```python
# api/main.py
from api.routes import ml_router  # Add this

app.include_router(ml_router)  # Add this
```

### UI Calls FastAPI

```typescript
// ui/dashboard/src/components/players/prediction-card.tsx

const predictStats = async () => {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/ml/predict/player-stats`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        player_id: playerId,
        season_id: seasonId,
        games_remaining: gamesRemaining
      })
    }
  )
  
  const predictions = await response.json()
  // Display in UI
}
```

---

## Environment Variables

```env
# .env.local (UI Dashboard)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=https://your-api.railway.app  # Add this for ML endpoints

# .env (FastAPI)
ML_MODELS_DIR=/app/models
ML_MODEL_VERSION=1.0.0
```

---

## Summary

| Approach | When to Use | Performance | Implementation |
|----------|-------------|-------------|----------------|
| **Pre-Computed (Views)** | Historical analytics, season projections | ⚡⚡⚡ Fastest | ETL job → DB views → UI queries |
| **FastAPI Endpoints** | Real-time predictions, what-if scenarios | ⚡⚡ Fast | UI → FastAPI → ML → Response |
| **Scheduled Jobs** | Daily/weekly batch predictions | ⚡⚡⚡ Fastest | Cron → ML → DB → UI queries |

**Recommendation:** Start with **pre-computed views** (Phase 1), then add **FastAPI endpoints** (Phase 2) for interactive features.
