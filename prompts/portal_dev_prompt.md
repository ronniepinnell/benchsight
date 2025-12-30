# Claude Prompt: Portal/Admin Developer

Copy this entire prompt when starting a new Claude chat for Admin Portal development.

---

## Context

I'm working on BenchSight, a hockey analytics platform for the NORAD recreational hockey league. I need help developing the Admin Portal.

## Current State

- Database: Supabase PostgreSQL with 96 tables + logging tables
- ETL: Python scripts for processing raw Excel → CSV → Supabase
- Logging: File-based and Supabase table logging
- Tests: 326 passing tests

## My Role

I'm the Portal/Admin Developer. I need to build a web-based admin interface that provides:
1. Database health monitoring and table browsing
2. ETL execution and monitoring
3. Data quality validation and reporting
4. Dimension table CRUD management
5. File upload and processing
6. Log viewing and error tracking

## Key Technical Details

### Supabase Connection
```javascript
// BACKEND ONLY - never expose to frontend
const supabaseAdmin = createClient(
  'https://uuaowslhpgyiudmbvqze.supabase.co',
  'SERVICE_ROLE_KEY'  // Admin access
);
```

### Key Python Scripts
```bash
# Load all tables
python scripts/load_all_tables.py --upsert

# With logging
python scripts/flexible_loader_with_logging.py --scope full --operation replace --log-to-supabase

# Run tests
python -m pytest tests/ -v
```

### Logging Tables
- `log_etl_runs` - ETL run tracking
- `log_etl_tables` - Per-table details
- `log_errors` - Error tracking
- `log_data_changes` - Audit trail
- `log_test_results` - Test results

### Useful Views
- `v_recent_runs` - Last 50 runs
- `v_daily_run_stats` - Daily stats
- `v_table_load_stats` - Table performance
- `v_unresolved_errors` - Open errors

### Admin Functions
```sql
SELECT * FROM get_all_table_counts();
SELECT get_run_summary('run_id');
SELECT * FROM cleanup_old_logs(30);
SELECT resolve_error(123, 'user', 'notes');
```

## What I Need Help With

[Describe your specific task here]

## Files Available
- Full handoff: `docs/handoffs/PORTAL_DEV_HANDOFF.md`
- Loader scripts: `scripts/` folder
- SQL schemas: `sql/` folder
- Config: `config/config_loader.py`
