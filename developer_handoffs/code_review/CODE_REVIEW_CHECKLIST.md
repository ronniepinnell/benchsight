# Code Review Checklist

## Pre-Review Setup
- [ ] Extract zip and navigate to project root
- [ ] Run `pip install pandas supabase openpyxl`
- [ ] Run tests: `python -m pytest tests/ -v`
- [ ] Check ETL status: `./run_etl.sh --status`

---

## 1. bulletproof_loader.py Review

### Functionality
- [ ] All 98 tables have correct primary keys defined
- [ ] Load modes (upsert, replace, append) work correctly
- [ ] Batch size (500) is optimal for Supabase
- [ ] Error handling catches all failure modes
- [ ] Status reporting is accurate

### Code Quality
- [ ] Type hints on all functions
- [ ] Docstrings present and accurate
- [ ] No bare except clauses
- [ ] Logging is consistent
- [ ] No hardcoded values (use constants)

### Edge Cases
- [ ] Empty CSV handling
- [ ] Malformed CSV handling
- [ ] Network timeout handling
- [ ] Schema mismatch handling
- [ ] Duplicate key handling

### Tests Needed
- [ ] test_load_table_upsert()
- [ ] test_load_table_replace()
- [ ] test_load_table_append()
- [ ] test_load_missing_tables()
- [ ] test_schema_mismatch_error()
- [ ] test_empty_csv()
- [ ] test_batch_processing()

---

## 2. src/main.py Review

### Structure
- [ ] Identify sections that should be separate modules
- [ ] Check for duplicated code
- [ ] Verify CLI argument handling

### Suggested Splits
- [ ] CLI handling → `src/cli.py`
- [ ] Game processing → `src/processing/game_processor.py`
- [ ] Stats calculation → `src/stats/calculator.py`
- [ ] Export logic → `src/export/csv_exporter.py`

### Code Quality
- [ ] Functions under 50 lines
- [ ] Classes have single responsibility
- [ ] No global state mutations
- [ ] Proper error propagation

---

## 3. ETL Pipeline Review

### Data Flow
- [ ] Stage → Intermediate → Datamart flow is clear
- [ ] Dependencies between layers documented
- [ ] No circular dependencies

### Transforms
- [ ] Event attribution logic correct (event_player_1 = primary)
- [ ] Goal detection covers both methods
- [ ] Shift calculations accurate
- [ ] Stats formulas match documentation

### Robustness
- [ ] Partial load recovery possible
- [ ] Idempotent re-processing
- [ ] Data validation at each stage

---

## 4. Stats Calculations Review

### Accuracy
- [ ] Verify 5 random stats against manual calculation
- [ ] Check edge cases (0 TOI, no shots, etc.)
- [ ] Verify percentage calculations handle div/0

### Performance
- [ ] No N+1 queries
- [ ] Vectorized operations where possible
- [ ] Memory usage reasonable

---

## 5. SQL Schema Review

### 01_CREATE_ALL_TABLES.sql
- [ ] All 98 tables present
- [ ] Primary keys correct
- [ ] Foreign keys defined
- [ ] Indexes on FK columns
- [ ] Indexes on common query columns

### 04_VIDEO_HIGHLIGHTS.sql
- [ ] Schema matches spec
- [ ] Constraints valid
- [ ] Indexes appropriate

---

## 6. Test Suite Review

### Current Tests (290)
- [ ] All tests pass
- [ ] Tests are meaningful (not just existence checks)
- [ ] Edge cases covered

### Missing Tests
- [ ] Integration tests for ETL
- [ ] Loader function tests
- [ ] Error handling tests
- [ ] Performance tests

---

## 7. Documentation Review

### Accuracy
- [ ] STATS_REFERENCE matches actual columns
- [ ] DATA_DICTIONARY matches actual schema
- [ ] Code comments match implementation

### Completeness
- [ ] All public functions documented
- [ ] All tables documented
- [ ] Error codes documented

---

## 8. Security Review

- [ ] No credentials in code
- [ ] Config file excluded from git
- [ ] No SQL injection vectors
- [ ] Input validation present

---

## 9. Performance Review

### Memory
- [ ] Large files streamed, not loaded fully
- [ ] DataFrames cleaned up after use

### Speed
- [ ] Batch sizes optimized
- [ ] No unnecessary loops
- [ ] Caching for repeated lookups

---

## 10. Final Sign-Off

- [ ] All critical issues resolved
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Ready for production

### Sign-Off

Reviewer: _________________
Date: _________________
Notes: _________________
