# BenchSight Test Suite

## Overview

290 tests covering data integrity, stats calculations, and deployment readiness.

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_stats_calculations.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

## Test Categories

### test_stats_calculations.py (250+ tests)
Tests all statistical calculations:
- **Scoring**: goals, assists, points consistency
- **Shooting**: shots, SOG, shooting percentage
- **Passing**: pass attempts, completion rate
- **Faceoffs**: FO wins/losses, FO percentage
- **Time on Ice**: TOI seconds/minutes, shift counts
- **Per-60 Stats**: goals/60, assists/60, etc.
- **Corsi/Fenwick**: possession metrics
- **Plus/Minus**: +/- calculations
- **Composite Ratings**: offensive/defensive ratings

### test_supabase_config.py (15 tests)
Deployment readiness:
- Configuration files exist
- SQL files exist
- Loader scripts exist
- Documentation complete
- Data files present

### test_validation.py (6 tests)
Data integrity:
- Output files exist
- Tables have data
- Column counts correct

### test_comprehensive_integrity.py (3 tests)
Project structure validation

### test_data_integrity.py
Foreign key relationships and data consistency

### test_etl.py
ETL pipeline functionality

## Test Data

Tests use actual data from `data/output/`:
- `fact_player_game_stats.csv` - 317 columns
- `dim_player.csv` - Player dimension
- `dim_team.csv` - Team dimension

## Adding New Tests

```python
# tests/test_new_feature.py
import pytest
from pathlib import Path
import pandas as pd

class TestNewFeature:
    def test_something(self):
        df = pd.read_csv("data/output/fact_player_game_stats.csv")
        assert len(df) > 0
```

## Expected Results

All 290 tests should pass:
```
============================= 290 passed in 6.23s ==============================
```
