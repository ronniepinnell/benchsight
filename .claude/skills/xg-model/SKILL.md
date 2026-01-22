---
name: xg-model
description: Work specifically on Expected Goals (xG) model development, training, and evaluation. Use when building or improving the xG prediction model.
allowed-tools: Bash, Read, Write, Edit
argument-hint: [train|evaluate|features|deploy]
---

# Expected Goals (xG) Model

Build and maintain the xG prediction model.

## What is xG?

Expected Goals (xG) measures the probability that a shot becomes a goal, based on historical data and shot characteristics.

**Industry Standards:**
- MoneyPuck: Public xG model
- Natural Stat Trick: Fenwick-based
- Evolving Hockey: WAR integration

## Features

### Core Features
| Feature | Type | Description |
|---------|------|-------------|
| `distance` | Float | Distance to goal center |
| `angle` | Float | Shooting angle |
| `shot_type` | Category | Wrist, slap, snap, etc. |
| `x_coord` | Float | Rink X coordinate |
| `y_coord` | Float | Rink Y coordinate |

### Contextual Features
| Feature | Type | Description |
|---------|------|-------------|
| `strength_state` | Category | 5v5, 5v4, 4v5, etc. |
| `period` | Integer | 1, 2, 3, OT |
| `seconds_elapsed` | Integer | Time in period |
| `score_diff` | Integer | Home - Away |
| `is_rebound` | Boolean | Shot within 3s of prior |
| `rush` | Boolean | Entry within 5s |

### Advanced Features
| Feature | Type | Description |
|---------|------|-------------|
| `prev_event_type` | Category | Pass, carry, etc. |
| `zone_time` | Integer | Seconds in O-zone |
| `traffic` | Integer | Defenders in lane |
| `shooter_handedness` | Category | L/R |
| `goalie_movement` | Float | Lateral movement |

## Model Architecture

**Current: XGBoost**
```python
model = XGBClassifier(
    n_estimators=500,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective='binary:logistic',
    eval_metric='logloss'
)
```

**Future: Neural Network**
```python
class xGModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(num_features, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, 1)
        self.dropout = nn.Dropout(0.3)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = torch.sigmoid(self.fc3(x))
        return x
```

## Training Pipeline

```bash
# 1. Extract features
python src/ml/features/shot_features.py \
  --input data/output/fact_shots.csv \
  --output data/ml/shot_features.parquet

# 2. Train model
python src/ml/training/train_xg.py \
  --data data/ml/shot_features.parquet \
  --model xgboost \
  --output models/xg/v2

# 3. Evaluate
python src/ml/training/evaluate.py \
  --model models/xg/v2 \
  --test data/ml/test_shots.parquet

# 4. Deploy
cp models/xg/v2/model.pkl models/xg/production/
```

## Evaluation Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| Log Loss | < 0.25 | Primary metric |
| AUC-ROC | > 0.75 | Discrimination |
| Calibration | ±0.02 | Predicted vs actual |
| Brier Score | < 0.08 | Overall accuracy |

## Calibration

```python
# Check calibration by xG bucket
bins = [0, 0.05, 0.1, 0.2, 0.3, 0.5, 1.0]
for i in range(len(bins)-1):
    mask = (xg >= bins[i]) & (xg < bins[i+1])
    actual = goals[mask].mean()
    predicted = xg[mask].mean()
    print(f"{bins[i]:.2f}-{bins[i+1]:.2f}: Pred={predicted:.3f}, Actual={actual:.3f}")
```

## Integration

### ETL Integration
```python
# In src/calculations/xg.py
def calculate_xg(shots_df):
    model = load_model('models/xg/production/model.pkl')
    features = prepare_features(shots_df)
    shots_df['xg'] = model.predict_proba(features)[:, 1]
    return shots_df
```

### Dashboard Integration
- Shot charts colored by xG
- xG vs actual goals comparison
- Player xG rankings
- Team xG differential

## Versioning

```
models/xg/
├── v1/                    # Initial model
│   ├── model.pkl
│   ├── features.json
│   └── metrics.json
├── v2/                    # Improved features
│   ├── model.pkl
│   ├── features.json
│   └── metrics.json
└── production/            # Active model
    └── model.pkl → ../v2/model.pkl
```
