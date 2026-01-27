---
name: ml-pipeline
description: Work on machine learning pipeline for hockey analytics including xG models, win probability, player clustering, and predictions. Use when developing ML features.
allowed-tools: Bash, Read, Write, Edit
argument-hint: [xg|win-prob|clustering|predictions]
---

# ML Pipeline Development

Build machine learning models for hockey analytics.

## ML Models (Planned/In Progress)

### 1. Expected Goals (xG)
**Purpose:** Predict goal probability for each shot
**Features:**
- Shot location (x, y)
- Shot type (wrist, slap, etc.)
- Game situation (even strength, PP, etc.)
- Time since last event
- Shooter angle/distance

### 2. Win Probability
**Purpose:** Real-time game win probability
**Features:**
- Score differential
- Time remaining
- Shot differential
- Power play status
- Recent momentum

### 3. Player Clustering
**Purpose:** Group similar players for comparison
**Features:**
- Scoring patterns
- Usage metrics
- Shot profiles
- Defensive contributions

### 4. Performance Prediction
**Purpose:** Predict player future performance
**Features:**
- Historical stats
- Age curves
- Team context
- Usage trends

## Tech Stack

**Current:**
- scikit-learn (modeling)
- pandas (data processing)
- XGBoost/LightGBM (gradient boosting)

**Planned:**
- PyTorch (deep learning)
- MLflow (experiment tracking)
- Ray (distributed training)

## Pipeline Structure

```
src/ml/
├── models/
│   ├── xg_model.py         # xG prediction
│   ├── win_probability.py   # Win prob model
│   ├── player_clustering.py # Player clusters
│   └── performance_pred.py  # Future performance
├── features/
│   ├── shot_features.py     # Shot-level features
│   ├── game_features.py     # Game-level features
│   └── player_features.py   # Player-level features
├── training/
│   ├── train_xg.py          # xG training script
│   ├── evaluate.py          # Model evaluation
│   └── hyperparameter.py    # Hyperparameter tuning
├── serving/
│   ├── model_server.py      # Model serving API
│   └── batch_predict.py     # Batch predictions
└── utils/
    ├── data_loader.py       # Load training data
    └── metrics.py           # Custom metrics
```

## Training Workflow

```bash
# 1. Prepare training data
python src/ml/features/shot_features.py

# 2. Train model
python src/ml/training/train_xg.py --model xgboost

# 3. Evaluate
python src/ml/training/evaluate.py --model xg_v1

# 4. Deploy
python src/ml/serving/model_server.py
```

## API Integration

```python
# api/routes/ml.py
@router.post("/predict/xg")
async def predict_xg(shot: ShotInput):
    return ml_service.predict_xg(shot)

@router.post("/predict/win-prob")
async def predict_win_prob(game_state: GameState):
    return ml_service.predict_win_probability(game_state)
```

## Model Registry

Track models in:
```
models/
├── xg/
│   ├── v1/model.pkl
│   ├── v2/model.pkl
│   └── production/model.pkl
└── win_prob/
    └── v1/model.pkl
```

## Evaluation Metrics

| Model | Primary Metric | Target |
|-------|----------------|--------|
| xG | Log Loss | < 0.25 |
| Win Prob | Brier Score | < 0.20 |
| Clustering | Silhouette | > 0.5 |
| Prediction | MAE | < 0.3 |

## Output

ML documentation goes to:
```
docs/ml/{model}-documentation.md
```
