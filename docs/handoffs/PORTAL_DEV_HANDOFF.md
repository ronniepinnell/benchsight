# Portal/Admin Developer Handoff

**Role:** Admin Portal Developer  
**Version:** 2.0  
**Date:** December 30, 2025

---

## Your Mission

Build a web-based admin portal that provides:
1. Complete database management and monitoring
2. ETL execution and monitoring
3. Data quality validation and reporting
4. Log viewing and error tracking
5. Dimension table management (CRUD)
6. Game data upload and processing
7. System health dashboards

---

## Quick Start

### 1. Get the Codebase
```bash
unzip benchsight_COMPLETE_FULL.zip
cd benchsight_COMPLETE_FULL
```

### 2. Understand the Architecture
```
Portal ←→ Supabase API ←→ PostgreSQL Database
                ↓
         Python Scripts (ETL, Loaders)
                ↓
         CSV Files (data/output/)
                ↓
         Raw Excel Files (data/raw/)
```

### 3. Key Components You'll Manage

| Component | Location | Purpose |
|-----------|----------|---------|
| Database | Supabase | 98 tables + logs |
| ETL | `etl.py` | Process raw → CSV |
| Loader | `scripts/load_all_tables.py` | CSV → Supabase |
| Logs | `logs/` + `log_*` tables | Audit trail |
| Config | `config/config_local.ini` | Credentials |
| Tests | `tests/` | 326 validation tests |

---

## Portal Features Specification

### 1. DATABASE HEALTH DASHBOARD

```
┌─────────────────────────────────────────────────────────────────┐
│  DATABASE HEALTH                           Last Check: 2 min ago│
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   TABLES    │  │    ROWS     │  │    SIZE     │             │
│  │     96      │  │   120,000   │  │    45 MB    │             │
│  │   ✅ OK     │  │   ✅ OK     │  │   ✅ OK     │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
│  RECENT ACTIVITY                                                │
│  ├─ 10:30 AM - ETL completed (4 games)                         │
│  ├─ 10:15 AM - Data load successful (24,639 rows)              │
│  └─ 09:00 AM - Scheduled validation passed                     │
│                                                                 │
│  ALERTS                                                         │
│  ⚠️ 1 duplicate key found in fact_events (non-critical)        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Implementation:

```javascript
// Get table counts
async function getTableStats() {
  const { data } = await supabase.rpc('get_all_table_counts');
  return data;
}

// Get recent ETL runs
async function getRecentRuns() {
  const { data } = await supabase
    .from('log_etl_runs')
    .select('*')
    .order('started_at', { ascending: false })
    .limit(10);
  return data;
}

// Get unresolved errors
async function getAlerts() {
  const { data } = await supabase
    .from('v_unresolved_errors')
    .select('*');
  return data;
}
```

### 2. TABLE BROWSER

```
┌─────────────────────────────────────────────────────────────────┐
│  TABLE BROWSER                                                  │
├────────────────────────┬────────────────────────────────────────┤
│  TABLES (96)           │  dim_player (337 rows)                 │
│  ├─ Dimensions (44)    │  ┌─────────────────────────────────────┤
│  │  ├─ dim_player  337 │  │ player_id | player_name | position  │
│  │  ├─ dim_team     26 │  ├───────────┼─────────────┼──────────│
│  │  ├─ dim_schedule 562│  │ P001      │ John Smith  │ C        │
│  │  └─ ...             │  │ P002      │ Jane Doe    │ LW       │
│  ├─ Facts (51)         │  │ ...       │ ...         │ ...      │
│  │  ├─ fact_events 5833│  └─────────────────────────────────────┤
│  │  ├─ fact_shifts 672 │                                        │
│  │  └─ ...             │  [Export CSV] [Edit] [Delete Selected] │
│  └─ Logs (5)           │                                        │
└────────────────────────┴────────────────────────────────────────┘
```

#### Implementation:

```javascript
// Browse any table
async function browseTable(tableName, page = 1, pageSize = 50) {
  const from = (page - 1) * pageSize;
  const to = from + pageSize - 1;
  
  const { data, count } = await supabase
    .from(tableName)
    .select('*', { count: 'exact' })
    .range(from, to);
    
  return { data, count, page, pageSize };
}

// Export to CSV
async function exportTable(tableName) {
  const { data } = await supabase.from(tableName).select('*');
  return convertToCSV(data);
}
```

### 3. DIMENSION TABLE EDITOR

Allow CRUD operations on dimension tables:

```
┌─────────────────────────────────────────────────────────────────┐
│  EDIT: dim_event_type                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  event_type_id: [EVT015    ]  (auto-generated)                 │
│  event_type:    [Deflection ]                                  │
│  description:   [Puck redirected by player's stick or body   ] │
│  parent_type:   [Shot ▼]                                       │
│  active:        [✓]                                            │
│                                                                 │
│  [Cancel] [Save]                                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Implementation:

```javascript
// Add new dimension record
async function addDimRecord(tableName, record) {
  const { data, error } = await supabase
    .from(tableName)
    .insert([record])
    .select();
    
  if (error) throw error;
  
  // Log the change
  await logChange('INSERT', tableName, null, record);
  
  return data;
}

// Update dimension record
async function updateDimRecord(tableName, id, updates) {
  const primaryKey = getPrimaryKey(tableName);
  
  // Get old values for audit
  const { data: oldRecord } = await supabase
    .from(tableName)
    .select('*')
    .eq(primaryKey, id)
    .single();
  
  const { data, error } = await supabase
    .from(tableName)
    .update(updates)
    .eq(primaryKey, id)
    .select();
    
  if (error) throw error;
  
  // Log the change
  await logChange('UPDATE', tableName, oldRecord, data[0]);
  
  return data;
}

// Delete dimension record
async function deleteDimRecord(tableName, id) {
  const primaryKey = getPrimaryKey(tableName);
  
  // Get old values for audit
  const { data: oldRecord } = await supabase
    .from(tableName)
    .select('*')
    .eq(primaryKey, id)
    .single();
  
  const { error } = await supabase
    .from(tableName)
    .delete()
    .eq(primaryKey, id);
    
  if (error) throw error;
  
  // Log the change
  await logChange('DELETE', tableName, oldRecord, null);
}

// Log all changes for audit
async function logChange(operation, tableName, oldValues, newValues) {
  await supabase.from('log_data_changes').insert([{
    table_name: tableName,
    operation: operation,
    old_values: oldValues,
    new_values: newValues,
    changed_by: getCurrentUser(),
    changed_at: new Date().toISOString()
  }]);
}
```

### 4. FILE UPLOAD & ETL

```
┌─────────────────────────────────────────────────────────────────┐
│  UPLOAD & PROCESS                                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  UPLOAD NEW DATA                                                │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                                                           │ │
│  │     Drag & drop files here or click to browse             │ │
│  │                                                           │ │
│  │     Supported: .xlsx, .csv                                │ │
│  │                                                           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  PENDING FILES                                                  │
│  ├─ game_19001_tracking.xlsx (2.3 MB) [Process] [Remove]       │
│  └─ BLB_Tables_updated.xlsx (500 KB) [Process] [Remove]        │
│                                                                 │
│  OPTIONS                                                        │
│  ☐ Run validation after processing                             │
│  ☐ Auto-load to Supabase on success                            │
│  ☑ Send notification on completion                             │
│                                                                 │
│  [Process All]                                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Backend API Endpoints Needed:

```python
# Flask/FastAPI backend endpoints

@app.post("/api/upload")
async def upload_file(file: UploadFile):
    """Upload file to processing queue"""
    # Save to data/raw/pending/
    filepath = save_uploaded_file(file)
    return {"status": "uploaded", "path": filepath}

@app.post("/api/etl/run")
async def run_etl(game_ids: List[str] = None):
    """Run ETL pipeline"""
    # Call etl.py
    result = subprocess.run(
        ["python", "etl.py"] + (["--games", ",".join(game_ids)] if game_ids else []),
        capture_output=True
    )
    return {"status": "completed", "output": result.stdout}

@app.post("/api/loader/run")
async def run_loader(tables: List[str] = None, operation: str = "upsert"):
    """Run data loader"""
    cmd = ["python", "scripts/load_all_tables.py", f"--{operation}"]
    if tables:
        for table in tables:
            subprocess.run(cmd + ["--table", table])
    else:
        subprocess.run(cmd)
    return {"status": "completed"}

@app.get("/api/etl/status")
async def get_etl_status():
    """Get current ETL status"""
    # Check for running processes
    # Return progress if running
    pass
```

### 5. LOG VIEWER

```
┌─────────────────────────────────────────────────────────────────┐
│  LOG VIEWER                                                     │
├─────────────────────────────────────────────────────────────────┤
│  Filter: [All ▼] [Last 24h ▼] [Search...          ] [Apply]    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📋 ETL RUNS                                                    │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ Run ID          │ Status  │ Tables │ Rows   │ Duration   │ │
│  ├─────────────────┼─────────┼────────┼────────┼────────────│ │
│  │ etl_20251229... │ ✅ OK   │ 96     │ 24,639 │ 31s        │ │
│  │ etl_20251228... │ ⚠️ PART │ 95     │ 24,100 │ 45s        │ │
│  │ etl_20251227... │ ❌ FAIL │ 12     │ 0      │ 5s         │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  📋 ERRORS                                                      │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ ⚠️ Duplicate key in fact_events (EV1896901594)           │ │
│  │    Occurred: 2025-12-29 19:04:55                          │ │
│  │    [View Details] [Mark Resolved]                         │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Implementation:

```javascript
// Get ETL runs
async function getETLRuns(filters = {}) {
  let query = supabase
    .from('log_etl_runs')
    .select('*')
    .order('started_at', { ascending: false });
    
  if (filters.status) {
    query = query.eq('status', filters.status);
  }
  if (filters.after) {
    query = query.gte('started_at', filters.after);
  }
  
  return query;
}

// Get table load details for a run
async function getRunDetails(runId) {
  const { data } = await supabase
    .from('log_etl_tables')
    .select('*')
    .eq('run_id', runId);
  return data;
}

// Get errors
async function getErrors(resolved = false) {
  const { data } = await supabase
    .from('log_errors')
    .select('*')
    .eq('resolved', resolved)
    .order('created_at', { ascending: false });
  return data;
}

// Resolve error
async function resolveError(errorId, notes) {
  await supabase.rpc('resolve_error', {
    error_id: errorId,
    resolved_by: getCurrentUser(),
    resolution_notes: notes
  });
}
```

### 6. TEST RESULTS VIEWER

```
┌─────────────────────────────────────────────────────────────────┐
│  TEST RESULTS                          Last Run: 10 min ago     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  SUMMARY                                                        │
│  ├─ Total Tests: 326                                           │
│  ├─ Passed: 326 ✅                                             │
│  ├─ Failed: 0                                                  │
│  └─ Pass Rate: 100%                                            │
│                                                                 │
│  BY CATEGORY                                                    │
│  ├─ Referential Integrity: 45/45 ✅                            │
│  ├─ Business Logic: 89/89 ✅                                   │
│  ├─ Data Quality: 112/112 ✅                                   │
│  └─ Deployment: 80/80 ✅                                       │
│                                                                 │
│  [Run Tests Now] [View Full Report] [Export]                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Backend:

```python
@app.post("/api/tests/run")
async def run_tests():
    """Run pytest suite"""
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/", "-v", "--json-report"],
        capture_output=True
    )
    # Parse and store results
    return parse_test_results(result)

@app.get("/api/tests/results")
async def get_test_results():
    """Get latest test results"""
    return supabase.from('log_test_results').select('*').order('run_at', descending=True).limit(1)
```

### 7. DATA VALIDATION PANEL

```
┌─────────────────────────────────────────────────────────────────┐
│  DATA VALIDATION                                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  INTEGRITY CHECKS                                               │
│  ├─ Referential Integrity: ✅ All FKs valid                    │
│  ├─ Primary Key Uniqueness: ⚠️ 1 duplicate found               │
│  ├─ Null Constraints: ✅ No unexpected nulls                   │
│  └─ Data Types: ✅ All valid                                   │
│                                                                 │
│  BUSINESS RULES                                                 │
│  ├─ Goals Match Official: ✅ 4/4 games match                   │
│  ├─ Events in Shifts: ⚠️ 58 events without shift              │
│  ├─ Linked Events Valid: ✅ All links valid                    │
│  └─ Player Stats Sum: ✅ Totals match                          │
│                                                                 │
│  DETAILS                                                        │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ Issue: 58 events have shift_key containing 'nan'          │ │
│  │ Impact: Minor - events still usable                        │ │
│  │ Games: 18969, 18977, 18981, 18987                         │ │
│  │ [View Events] [Auto-fix] [Ignore]                         │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  [Run Full Validation] [Export Report]                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 8. UPLOAD NEW TABLES (SCHEMA EXTENSION)

Allow users to upload entirely new dimension or fact tables:

```
┌─────────────────────────────────────────────────────────────────┐
│  CREATE NEW TABLE                                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  TABLE TYPE: [Dimension ▼]                                     │
│  TABLE NAME: dim_[                    ]                        │
│                                                                 │
│  UPLOAD CSV TO DEFINE SCHEMA                                    │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │     Drop CSV here to auto-detect columns                  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  DETECTED COLUMNS                                               │
│  ┌──────────────┬──────────┬─────────────┬───────────────────┐ │
│  │ Column       │ Type     │ Primary Key │ Nullable          │ │
│  ├──────────────┼──────────┼─────────────┼───────────────────│ │
│  │ shot_zone_id │ TEXT     │ ☑           │ ☐                 │ │
│  │ zone_name    │ TEXT     │ ☐           │ ☐                 │ │
│  │ x_min        │ DECIMAL  │ ☐           │ ☑                 │ │
│  │ x_max        │ DECIMAL  │ ☐           │ ☑                 │ │
│  │ danger_level │ INTEGER  │ ☐           │ ☐                 │ │
│  └──────────────┴──────────┴─────────────┴───────────────────┘ │
│                                                                 │
│  [Preview SQL] [Create Table] [Create & Load Data]             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Implementation:

```javascript
// Generate CREATE TABLE SQL from CSV
function generateCreateTableSQL(tableName, columns) {
  const colDefs = columns.map(col => {
    let def = `    "${col.name}" ${col.type}`;
    if (col.primaryKey) def += ' PRIMARY KEY';
    if (!col.nullable) def += ' NOT NULL';
    return def;
  });
  
  return `CREATE TABLE ${tableName} (\n${colDefs.join(',\n')}\n);`;
}

// Execute via Supabase
async function createTable(sql) {
  // Need to use Supabase Management API or direct SQL
  // This requires service role key
  const { error } = await supabase.rpc('exec_sql', { sql });
  return !error;
}
```

---

## Python Scripts Reference

### Data Loader Commands

```bash
# Load ALL tables (98 tables)
python scripts/load_all_tables.py

# Load with upsert (handles duplicates)
python scripts/load_all_tables.py --upsert

# Dry run (preview only)
python scripts/load_all_tables.py --dry-run

# Load single table
python scripts/load_all_tables.py --table dim_player --upsert

# Skip dimension tables
python scripts/load_all_tables.py --skip-dims --upsert
```

### Flexible Loader (with logging)

```bash
# Show config
python scripts/flexible_loader_with_logging.py --show-config

# Test connection
python scripts/flexible_loader_with_logging.py --test-connection

# Full load with replace
python scripts/flexible_loader_with_logging.py --scope full --operation replace

# Single table upsert
python scripts/flexible_loader_with_logging.py --scope table --table fact_events --operation upsert

# With Supabase logging
python scripts/flexible_loader_with_logging.py --scope full --operation replace --log-to-supabase

# View last run
python scripts/flexible_loader_with_logging.py --show-last-run
```

### ETL Commands

```bash
# Run full ETL
python etl.py

# ETL specific games
python etl.py --games 18969,18977

# ETL with validation
python etl.py --validate

# ETL dry run
python etl.py --dry-run
```

### Test Commands

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_deployment_readiness.py -v

# Run with coverage
python -m pytest tests/ --cov=src

# Generate HTML report
python -m pytest tests/ --html=reports/test_report.html
```

---

## Database Management SQL

### Clear All Data (Keep Schema)

```sql
-- Run sql/06_TRUNCATE_ALL_DATA.sql
-- Or individually:
TRUNCATE TABLE fact_events CASCADE;
TRUNCATE TABLE fact_shifts CASCADE;
-- etc.
```

### Recreate Schema

```sql
-- Run sql/05_FINAL_COMPLETE_SCHEMA.sql
-- This drops and recreates all 98 tables
```

### Useful Admin Queries

```sql
-- Table row counts
SELECT * FROM get_all_table_counts();

-- Recent ETL runs
SELECT * FROM v_recent_runs;

-- Daily statistics
SELECT * FROM v_daily_run_stats;

-- Table load performance
SELECT * FROM v_table_load_stats;

-- Unresolved errors
SELECT * FROM v_unresolved_errors;

-- Run summary
SELECT get_run_summary('etl_run_20251229_123456_abc12345');

-- Clean old logs (keep 30 days)
SELECT * FROM cleanup_old_logs(30);

-- Database size
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname || '.' || tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname || '.' || tablename) DESC;
```

---

## Logging Tables Schema

### log_etl_runs
| Column | Type | Description |
|--------|------|-------------|
| run_id | TEXT PK | Unique run identifier |
| started_at | TIMESTAMPTZ | Start time |
| completed_at | TIMESTAMPTZ | End time |
| status | TEXT | success/partial/failed |
| total_tables | INTEGER | Tables processed |
| successful_tables | INTEGER | Tables succeeded |
| failed_tables | INTEGER | Tables failed |
| total_rows | INTEGER | Rows loaded |
| duration_seconds | DECIMAL | Total duration |
| environment | TEXT | dev/prod |
| triggered_by | TEXT | manual/scheduled/api |

### log_etl_tables
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PK | Auto ID |
| run_id | TEXT FK | Links to run |
| table_name | TEXT | Table loaded |
| status | TEXT | success/failed |
| rows_before | INTEGER | Count before |
| rows_after | INTEGER | Count after |
| rows_inserted | INTEGER | New rows |
| rows_updated | INTEGER | Updated rows |
| rows_deleted | INTEGER | Deleted rows |
| duration_seconds | DECIMAL | Table duration |
| error_message | TEXT | Error if failed |

### log_errors
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PK | Auto ID |
| run_id | TEXT | Related run |
| table_name | TEXT | Related table |
| error_type | TEXT | Type of error |
| error_message | TEXT | Message |
| error_details | JSONB | Full context |
| stack_trace | TEXT | Python traceback |
| resolved | BOOLEAN | Is resolved |
| resolved_by | TEXT | Who resolved |
| resolved_at | TIMESTAMPTZ | When resolved |
| resolution_notes | TEXT | How fixed |

---

## Security Considerations

### API Keys

```
ANON_KEY: For read-only public access (dashboards)
SERVICE_ROLE_KEY: For admin operations (portal backend)
```

**NEVER expose SERVICE_ROLE_KEY to frontend!**

### Portal Authentication

Implement proper auth:
```javascript
// Use Supabase Auth
const { data: { user } } = await supabase.auth.getUser();

// Check admin role
if (!user || !user.app_metadata?.role === 'admin') {
  throw new Error('Unauthorized');
}
```

### Audit Trail

Log all admin actions:
```javascript
async function logAdminAction(action, details) {
  await supabase.from('log_admin_actions').insert([{
    user_id: getCurrentUser(),
    action: action,
    details: details,
    timestamp: new Date().toISOString(),
    ip_address: getClientIP()
  }]);
}
```

---

## Deployment Architecture

### Recommended Stack

```
┌─────────────────────────────────────────────────────────────────┐
│  FRONTEND (React/Next.js)                                       │
│  - Admin Dashboard UI                                           │
│  - Table browser                                                │
│  - Log viewer                                                   │
│  - File upload                                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  BACKEND API (FastAPI/Flask)                                    │
│  - ETL orchestration                                            │
│  - File processing                                              │
│  - Script execution                                             │
│  - Admin operations                                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  SUPABASE                                                       │
│  - PostgreSQL Database                                          │
│  - Auth                                                         │
│  - Storage (for file uploads)                                   │
│  - Realtime subscriptions                                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Future Considerations

### ML/CV Integration
- Add tables for tracking data (player positions, puck tracking)
- Create pipelines for model predictions (xG, xA)
- Store model outputs alongside traditional stats

### NHL Data Integration
- Add NHL API connector
- Map NHL player IDs to internal IDs
- Import historical NHL data for comparison

### Scaling
- Consider read replicas for dashboards
- Implement caching layer (Redis)
- Use background job queue (Celery) for ETL

---

## Resources

- Schema: `sql/05_FINAL_COMPLETE_SCHEMA.sql`
- Logging Tables: `sql/02_CREATE_LOGGING_TABLES.sql`
- Loader Script: `scripts/load_all_tables.py`
- Config: `config/config_loader.py`
- Tests: `tests/` directory

---

## Questions?

See `prompts/portal_dev_prompt.md` for a prompt to start a new Claude chat with full context.
