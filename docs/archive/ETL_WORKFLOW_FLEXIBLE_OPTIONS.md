# ETL Workflow - Flexible Options TODO

**Created:** 2026-01-13  
**Status:** Pending  
**Priority:** High

---

## Current State

The ETL workflow currently has:
- ETL runs with mode (full/incremental/single) and game_ids
- Schema generation via `/api/upload/generate-schema` (creates SQL file)
- Schema loading is **manual** (must paste SQL in Supabase SQL Editor)
- Sync via `/api/upload/to-supabase` with modes (all, dims, facts, qa, basic, tracking)

---

## Desired State

Users want more flexible options:

1. **ETL Options:**
   - Run ETL on specific games
   - Run ETL on specific tables
   - Select data source (local Excel files vs Supabase staging tables)

2. **Schema Management:**
   - Generate schema (already exists)
   - **Load schema** (apply SQL to Supabase - currently manual)
   - Options for what to include in schema

3. **Sync Options:**
   - Sync specific tables
   - Sync by mode (dims, facts, qa, basic, tracking)
   - Sync by pattern
   - Options for what to sync

---

## Implementation Plan

### 1. Enhance ETL Options

**Add to `TriggerETLRequest`:**
- `tables: Optional[List[str]]` - Filter which tables to generate
- `source: str = "excel"` - Data source: "excel" or "supabase"
- `exclude_tables: Optional[List[str]]` - Tables to skip

**Update `run_etl.py` to support:**
- `--tables` - Process only specific tables
- `--source` - Data source selection (excel/supabase)

### 2. Schema Loading

**Challenge:** Supabase Python client doesn't support raw SQL execution.

**Options:**
- **Option A:** Use Supabase Management API (requires additional setup)
- **Option B:** Keep manual (recommend user runs SQL in Supabase SQL Editor)
- **Option C:** Create helper endpoint that returns SQL file for download

**Recommendation:** Option B (manual) for now, document the workflow clearly.

**API Endpoint (if needed):**
- `GET /api/upload/schema-file` - Download generated schema SQL
- `POST /api/upload/load-schema` - Attempt to execute SQL (requires Management API)

### 3. Enhance Sync Options

**Already supports:**
- `tables: Optional[List[str]]` - Specific tables
- `mode: str` - all, dims, facts, qa, basic, tracking

**Could add:**
- `pattern: Optional[str]` - Table name pattern (e.g., "fact_player*")
- `exclude_tables: Optional[List[str]]` - Tables to skip

### 4. Update Portal UI

**Separate sections:**
1. **ETL Pipeline** - Run ETL only
2. **Schema Management** - Generate schema, Load schema (with instructions)
3. **Data Sync** - Sync to Supabase with flexible options

---

## Recommended Workflow

```
1. Run ETL → Generates CSV files
2. Generate Schema → Creates sql/reset_supabase.sql
3. Load Schema → Manual: Paste SQL in Supabase SQL Editor
4. Sync to Supabase → Upload data with flexible options
```

---

## Next Steps

1. [ ] Enhance `TriggerETLRequest` model with table/source options
2. [ ] Update `run_etl.py` to support `--tables` and `--source` flags
3. [ ] Update `ETLService` to pass table/source options
4. [ ] Document schema loading workflow (manual for now)
5. [ ] Enhance `UploadRequest` model with pattern/exclude options
6. [ ] Update portal UI to separate ETL, Schema, and Sync sections
7. [ ] Add UI controls for flexible options (table selection, modes, etc.)

---

## Related Files

- `api/models/job.py` - TriggerETLRequest model
- `api/models/upload.py` - UploadRequest model
- `api/routes/etl.py` - ETL endpoints
- `api/routes/upload.py` - Upload endpoints
- `api/services/etl_service.py` - ETL service
- `api/services/upload_service.py` - Upload service
- `run_etl.py` - ETL script
- `upload.py` - Upload script
- `ui/portal/index.html` - Portal UI
- `ui/portal/js/etl.js` - ETL JavaScript
