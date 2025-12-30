# BenchSight Data Validation Guide

## Overview

Multiple validation layers ensure data accuracy and consistency.

## Validation Scripts

### 1. `scripts/validate_against_ground_truth.py`
Compares calculated stats against official NORAD website data.

```bash
python scripts/validate_against_ground_truth.py
```

**Checks:**
- Goals match noradhockey.com
- Assists match noradhockey.com
- Points match noradhockey.com
- Game scores verified

### 2. `scripts/validate_stats.py`
Validates statistical calculations.

```bash
python scripts/validate_stats.py
```

**Checks:**
- Points = Goals + Assists
- Shooting % = Goals / SOG
- FO % = FO Wins / FO Total
- TOI Minutes = TOI Seconds / 60

### 3. `scripts/qa_comprehensive.py`
Full quality assurance sweep.

```bash
python scripts/qa_comprehensive.py
```

**Checks:**
- No negative values where impossible
- Percentages between 0-100
- No orphaned foreign keys
- Required fields populated

### 4. `scripts/qa_dynamic.py`
Dynamic validation based on data patterns.

```bash
python scripts/qa_dynamic.py
```

### 5. `scripts/etl_validation.py`
Post-ETL validation.

```bash
python scripts/etl_validation.py
```

## Validation Reports

### Location: `data/output/`
- `ETL_VALIDATION_REPORT.json` - ETL validation results
- `VALIDATION_REPORT.json` - Stats validation results

### Sample Report Structure
```json
{
  "timestamp": "2025-12-30T12:00:00",
  "tables_validated": 96,
  "rows_validated": 125000,
  "errors": [],
  "warnings": [
    {"table": "fact_player_game_stats", "issue": "2 players with 0 TOI"}
  ],
  "status": "PASSED"
}
```

## QA Table

`qa_suspicious_stats` tracks anomalies:
- Unusually high stats
- Potential data entry errors
- Players with missing data

## Manual Verification

1. **Goal Verification**
   - Compare `fact_player_game_stats.goals` to noradhockey.com box scores
   - Check goal scorers match game reports

2. **Roster Verification**
   - Verify player names spelled correctly
   - Check jersey numbers match rosters

3. **Game Verification**
   - Final scores match official results
   - Period scores add up correctly

## Known Data Quality Issues

See `docs/HONEST_ASSESSMENT.md` for known issues:
- Some tracking files have incomplete shift data
- XY coordinates may have gaps
- Some derived stats depend on tracking quality

## Running Full Validation

```bash
# Run all validations
python scripts/validate_stats.py
python scripts/qa_comprehensive.py
python scripts/validate_against_ground_truth.py

# Run tests
python -m pytest tests/ -v
```
