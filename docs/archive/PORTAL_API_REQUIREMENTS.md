# Admin Portal API Requirements

**API endpoints needed for portal functionality**

Last Updated: 2026-01-15  
Version: 1.0

---

## Overview

This document lists all API endpoints required for the admin portal to be fully functional.

**API Base URL:** `http://localhost:8000` (development)  
**API Prefix:** `/api`  
**Status:** Most endpoints exist, some may need enhancements

---

## Required Endpoints

### ETL Endpoints (✅ Exists)

#### `POST /api/etl/trigger`
**Status:** ✅ Implemented  
**Purpose:** Trigger ETL job  
**Required for:** ETL Control section

**Request:**
```json
{
  "mode": "full",
  "game_ids": [18969, 18977],
  "options": {
    "wipe": false,
    "upload_to_supabase": true
  }
}
```

**Response:**
```json
{
  "job_id": "abc123",
  "status": "running"
}
```

#### `GET /api/etl/status/{job_id}`
**Status:** ✅ Implemented  
**Purpose:** Get ETL job status  
**Required for:** Status polling, progress display

#### `GET /api/etl/history`
**Status:** ✅ Implemented  
**Purpose:** Get ETL job history  
**Required for:** Job history display

#### `POST /api/etl/cancel/{job_id}`
**Status:** ✅ Implemented  
**Purpose:** Cancel ETL job  
**Required for:** Cancel button

---

### Upload Endpoints (✅ Exists)

#### `POST /api/upload/to-supabase`
**Status:** ✅ Implemented  
**Purpose:** Upload tables to Supabase  
**Required for:** Upload Control section

**Request:**
```json
{
  "mode": "all",
  "tables": ["fact_events", "dim_player"],
  "options": {}
}
```

#### `GET /api/upload/status/{job_id}`
**Status:** ✅ Implemented  
**Purpose:** Get upload status  
**Required for:** Upload progress display

#### `POST /api/upload/generate-schema`
**Status:** ✅ Implemented  
**Purpose:** Generate schema SQL  
**Required for:** Schema generation button

---

### Staging Endpoints (✅ Exists)

#### `POST /api/staging/blb-tables/upload`
**Status:** ✅ Implemented  
**Purpose:** Upload BLB table data  
**Required for:** BLB data upload

#### `PUT /api/staging/blb-tables/update`
**Status:** ✅ Implemented  
**Purpose:** Update BLB table data  
**Required for:** BLB data editing

#### `GET /api/staging/blb-tables/list`
**Status:** ✅ Implemented  
**Purpose:** List BLB tables  
**Required for:** Table selection

#### `POST /api/staging/tracking/upload`
**Status:** ✅ Implemented  
**Purpose:** Upload tracking data  
**Required for:** Tracking data upload

#### `DELETE /api/staging/blb-tables/{table_name}`
**Status:** ✅ Implemented  
**Purpose:** Clear staging table  
**Required for:** Data cleanup

---

### Game Management Endpoints (❌ Missing)

#### `GET /api/games`
**Status:** ❌ Not implemented  
**Purpose:** List all games  
**Required for:** Game list display

**Expected Response:**
```json
{
  "games": [
    {
      "game_id": 18969,
      "date": "2024-01-15",
      "home_team": "Team A",
      "away_team": "Team B",
      "status": "completed"
    }
  ]
}
```

#### `POST /api/games`
**Status:** ❌ Not implemented  
**Purpose:** Create new game  
**Required for:** Create game functionality

**Request:**
```json
{
  "date": "2024-01-20",
  "home_team_id": "T001",
  "away_team_id": "T002",
  "venue": "Arena 1"
}
```

#### `GET /api/games/{game_id}`
**Status:** ❌ Not implemented  
**Purpose:** Get game details  
**Required for:** Game detail view

#### `PUT /api/games/{game_id}`
**Status:** ❌ Not implemented  
**Purpose:** Update game  
**Required for:** Edit game functionality

#### `DELETE /api/games/{game_id}`
**Status:** ❌ Not implemented  
**Purpose:** Delete game  
**Required for:** Delete game functionality

---

### Data Browser Endpoints (❌ Missing)

#### `GET /api/tables`
**Status:** ❌ Not implemented  
**Purpose:** List all tables  
**Required for:** Table list display

**Expected Response:**
```json
{
  "tables": [
    {
      "name": "fact_events",
      "type": "fact",
      "row_count": 5800,
      "column_count": 25
    }
  ]
}
```

#### `GET /api/tables/{table_name}`
**Status:** ❌ Not implemented  
**Purpose:** Get table data  
**Required for:** Data browser

**Query Parameters:**
- `limit` (optional): Number of rows (default: 100)
- `offset` (optional): Pagination offset (default: 0)
- `filter` (optional): Filter criteria

**Expected Response:**
```json
{
  "table": "fact_events",
  "rows": [...],
  "total_rows": 5800,
  "limit": 100,
  "offset": 0
}
```

#### `GET /api/tables/{table_name}/schema`
**Status:** ❌ Not implemented  
**Purpose:** Get table schema  
**Required for:** Schema display

---

## Implementation Priority

### High Priority (Week 1-2)

1. **ETL Endpoints** - ✅ Already implemented
2. **Upload Endpoints** - ✅ Already implemented
3. **Staging Endpoints** - ✅ Already implemented

### Medium Priority (Week 3-4)

4. **Game Management Endpoints** - ❌ Need to implement
5. **Data Browser Endpoints** - ❌ Need to implement

### Low Priority (Future)

6. **Authentication Endpoints** - ❌ Future feature
7. **User Management Endpoints** - ❌ Future feature

---

## Endpoint Implementation Plan

### Game Management Endpoints

**File:** `api/routes/games.py`

```python
router = APIRouter(prefix="/api/games", tags=["games"])

@router.get("")
async def list_games():
    """List all games."""
    supabase = get_supabase_client()
    result = supabase.table('dim_schedule').select('*').execute()
    return {"games": result.data}

@router.post("")
async def create_game(game: GameCreate):
    """Create new game."""
    supabase = get_supabase_client()
    result = supabase.table('dim_schedule').insert(game.dict()).execute()
    return result.data[0]

@router.get("/{game_id}")
async def get_game(game_id: int):
    """Get game details."""
    supabase = get_supabase_client()
    result = supabase.table('dim_schedule').select('*').eq('game_id', game_id).single().execute()
    return result.data

@router.put("/{game_id}")
async def update_game(game_id: int, game: GameUpdate):
    """Update game."""
    supabase = get_supabase_client()
    result = supabase.table('dim_schedule').update(game.dict()).eq('game_id', game_id).execute()
    return result.data[0]

@router.delete("/{game_id}")
async def delete_game(game_id: int):
    """Delete game."""
    supabase = get_supabase_client()
    supabase.table('dim_schedule').delete().eq('game_id', game_id).execute()
    return {"success": True}
```

### Data Browser Endpoints

**File:** `api/routes/tables.py`

```python
router = APIRouter(prefix="/api/tables", tags=["tables"])

@router.get("")
async def list_tables():
    """List all tables."""
    # Get table list from Supabase
    supabase = get_supabase_client()
    tables = []
    # Query information_schema or use table list
    return {"tables": tables}

@router.get("/{table_name}")
async def get_table_data(
    table_name: str,
    limit: int = 100,
    offset: int = 0,
    filter: Optional[str] = None
):
    """Get table data."""
    supabase = get_supabase_client()
    query = supabase.table(table_name).select('*')
    
    if filter:
        # Apply filter
        pass
    
    query = query.limit(limit).offset(offset)
    result = query.execute()
    
    # Get total count
    count_result = supabase.table(table_name).select('*', count='exact').execute()
    
    return {
        "table": table_name,
        "rows": result.data,
        "total_rows": count_result.count,
        "limit": limit,
        "offset": offset
    }

@router.get("/{table_name}/schema")
async def get_table_schema(table_name: str):
    """Get table schema."""
    supabase = get_supabase_client()
    # Query information_schema for column definitions
    return {"schema": {...}}
```

---

## Portal Integration Examples

### ETL Trigger

```javascript
async function triggerETL() {
  const response = await fetch('/api/etl/trigger', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      mode: 'full',
      options: { wipe: false }
    })
  })
  const job = await response.json()
  startPolling(job.job_id)
}
```

### Game List

```javascript
async function loadGames() {
  const response = await fetch('/api/games')
  const data = await response.json()
  displayGames(data.games)
}
```

### Table Data

```javascript
async function loadTableData(tableName, limit = 100, offset = 0) {
  const response = await fetch(
    `/api/tables/${tableName}?limit=${limit}&offset=${offset}`
  )
  const data = await response.json()
  displayTableData(data)
}
```

---

## Related Documentation

- [PORTAL_CURRENT_STATE.md](PORTAL_CURRENT_STATE.md) - Current state
- [PORTAL_DEVELOPMENT_PLAN.md](PORTAL_DEVELOPMENT_PLAN.md) - Development plan
- [API_REFERENCE.md](API_REFERENCE.md) - Complete API reference

---

*Last Updated: 2026-01-15*
