# BenchSight Logging System

Comprehensive logging for ETL pipelines and Supabase deployments.

## Configuration

### Setting Up Credentials

**Option 1: Config File (Recommended)**

Edit `config/config_local.ini`:

```ini
[supabase]
url = https://YOUR_PROJECT_ID.supabase.co
service_key = your-service-role-key-here
```

**Option 2: Environment Variables**

```bash
export SUPABASE_URL="https://YOUR_PROJECT_ID.supabase.co"
export SUPABASE_SERVICE_KEY="your-service-role-key"
```

### Getting Your Credentials

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Go to **Settings > API**
4. Copy:
   - **Project URL** → `url` in config
   - **service_role key** (NOT anon key) → `service_key` in config

### Verify Configuration

```bash
# Show current config
python scripts/flexible_loader_with_logging.py --show-config

# Test connection
python scripts/flexible_loader_with_logging.py --test-connection
```

## Overview

The logging system provides:
- **File-based logging** with date/run organized subdirectories
- **Supabase table logging** for centralized audit trails
- **Per-table tracking** with row counts and timing
- **Error capture** with full tracebacks
- **Test result tracking**
- **Human-readable summaries**

## Quick Start

### Using the Enhanced Loader

```bash
# Full load with logging
python scripts/flexible_loader_with_logging.py --scope full --operation replace

# Dry run (preview without changes)
python scripts/flexible_loader_with_logging.py --scope full --operation replace --dry-run

# Single game load
python scripts/flexible_loader_with_logging.py --scope game --game-id 18969 --operation replace

# Also log to Supabase tables
python scripts/flexible_loader_with_logging.py --scope full --operation replace --log-to-supabase

# View last run summary
python scripts/flexible_loader_with_logging.py --show-last-run
```

### Using the Logger Directly

```python
from src.logging_system import BenchSightLogger, TableLoadResult, Status

# Create logger
logger = BenchSightLogger(run_type="my_etl_run")
logger.start_run()

# Log operations
logger.log_info("Starting process...")
logger.log_warning("This might take a while")

# Log table results
result = TableLoadResult(
    table_name="dim_player",
    operation="upsert",
    status=Status.SUCCESS.value,
    rows_inserted=100,
    rows_updated=50,
    duration_seconds=2.5
)
logger.log_table_result(result)

# Handle errors
try:
    risky_operation()
except Exception as e:
    logger.log_error("Operation failed", exception=e)

# End run and get summary
summary = logger.end_run()
print(f"Logs saved to: {logger.run_dir}")
```

## Log Directory Structure

```
logs/
├── 2025-12-30/                          # Date directory
│   ├── supabase_load_20251230_123456_abc123/   # Run directory
│   │   ├── run.log                      # Main log file
│   │   ├── run.jsonl                    # JSON log (machine-readable)
│   │   ├── summary.json                 # Run summary (JSON)
│   │   ├── SUMMARY.md                   # Run summary (human-readable)
│   │   ├── errors/
│   │   │   └── errors.log               # Error details with tracebacks
│   │   ├── tables/
│   │   │   ├── dim_player.json          # Per-table details
│   │   │   ├── dim_team.json
│   │   │   └── ...
│   │   └── tests/
│   │       └── test_results.json        # Test results (if run)
│   └── etl_run_20251230_143022_def456/  # Another run
└── 2025-12-29/                          # Previous date
```

## Supabase Logging Tables

### Setup

Run the SQL script to create logging tables:

```sql
-- In Supabase SQL Editor
\i sql/02_CREATE_LOGGING_TABLES.sql
```

### Tables Created

| Table | Purpose |
|-------|---------|
| `log_etl_runs` | Main run tracking (status, timing, counts) |
| `log_etl_tables` | Per-table load details |
| `log_errors` | Error tracking with resolution workflow |
| `log_test_results` | Test execution results |
| `log_data_changes` | Audit trail of data changes |

### Useful Views

```sql
-- Recent runs
SELECT * FROM v_recent_runs;

-- Daily statistics
SELECT * FROM v_daily_run_stats;

-- Table load performance
SELECT * FROM v_table_load_stats;

-- Unresolved errors
SELECT * FROM v_unresolved_errors;

-- Test pass rates
SELECT * FROM v_test_pass_rate;
```

### Useful Functions

```sql
-- Get full run summary as JSON
SELECT get_run_summary('etl_run_20251230_123456_abc12345');

-- Mark error as resolved
SELECT resolve_error(123, 'ronnie', 'Fixed by updating CSV encoding');

-- Clean up logs older than 30 days
SELECT * FROM cleanup_old_logs(30);
```

## Log Levels

| Level | Usage |
|-------|-------|
| DEBUG | Detailed diagnostic info (batch progress, etc.) |
| INFO | General operational messages |
| WARNING | Potential issues that don't stop execution |
| ERROR | Failures with tracebacks |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_SERVICE_KEY` | Service role key (not anon key) |

## Features

### Automatic Capture

- Python version and platform
- Working directory
- Process ID
- Timestamp for every entry

### Per-Table Metrics

- Rows before/after operation
- Rows inserted/updated/deleted
- Duration in seconds
- CSV source file info
- Error messages

### Run Summary

- Total duration
- Success/failure counts
- Total rows processed
- Error/warning lists
- Markdown and JSON formats

### Error Handling

- Full Python tracebacks
- Exception type and message
- Context information
- Resolution tracking (in Supabase)

## Best Practices

1. **Always use dry-run first** when testing new operations
2. **Log to Supabase** for production deployments
3. **Check summaries** after each run
4. **Resolve errors** in the log_errors table
5. **Clean up old logs** periodically

## Integration with CI/CD

```bash
# Example GitHub Actions step
- name: Load to Supabase
  env:
    SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
    SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
  run: |
    python scripts/flexible_loader_with_logging.py \
      --scope full \
      --operation replace \
      --log-to-supabase
    
    # Check result
    python scripts/flexible_loader_with_logging.py --show-last-run
```
