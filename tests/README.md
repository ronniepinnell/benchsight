# BenchSight Tests

Test suite for ETL pipeline and data validation.

## Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_data_validation.py

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src
```

## Test Categories

### Data Validation
- `test_data_validation.py`: Core data integrity checks
- `test_data_validation_comprehensive.py`: Extended validation
- `test_schema_data_quality.py`: Schema conformance

### ETL Pipeline
- `test_etl.py`: ETL transformation tests
- `test_etl_integration.py`: End-to-end pipeline tests
- `test_etl_column_preservation.py`: Column integrity

### Statistics
- `test_stats_calculations.py`: Statistical accuracy
- `test_goal_verification.py`: Goal count validation
- `test_ground_truth.py`: Verification against official data

### Foreign Keys
- `test_fk_relationships.py`: Referential integrity

### Production Readiness
- `test_production_etl.py`: Production deployment tests
- `test_failure_modes.py`: Error handling

## Key Tests

### Data Integrity
```bash
pytest tests/test_data_integrity.py -v
```
- Primary key uniqueness
- Foreign key validity
- Required field checks

### Goal Verification
```bash
pytest tests/test_goal_verification.py -v
```
- Compares calculated goals to noradhockey.com
- Critical for data accuracy

### Schema Validation
```bash
pytest tests/test_schema_data_quality.py -v
```
- Column types match expectations
- All required columns present

## Test Fixtures

Defined in `conftest.py`:
- Database connections
- Sample data fixtures
- Test configuration

## Adding New Tests

1. Create test file: `tests/test_new_feature.py`
2. Import fixtures from conftest
3. Follow naming convention: `test_*`
4. Add docstrings explaining test purpose
