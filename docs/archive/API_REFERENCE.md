# BenchSight API Reference

**Complete API endpoint documentation**

Last Updated: 2026-01-21
Version: 2.00

---

## Overview

The BenchSight API is a FastAPI application that provides REST endpoints for ETL job management, data upload, staging, and ML predictions.

**Base URL:** `http://localhost:8000` (development)  
**API Prefix:** `/api`  
**Documentation:** `/docs` (Swagger UI), `/redoc` (ReDoc)

---

## Authentication

Currently, the API does not require authentication (development mode). Future versions will implement API key authentication.

---

## Endpoints

### Health & Status

#### `GET /api/health`

Simple health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-01-15T10:00:00Z"
}
```

#### `GET /api/status`

Detailed system status.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "etl_available": true,
  "supabase_connected": true,
  "timestamp": "2026-01-15T10:00:00Z"
}
```

---

### ETL Jobs

#### `POST /api/etl/trigger`

Trigger an ETL job.

**Request Body:**
```json
{
  "mode": "full",
  "game_ids": [18969, 18977],
  "source": "excel",
  "exclude_game_ids": [18965],
  "options": {
    "wipe": false,
    "upload_to_supabase": true
  }
}
```

**Modes:**
- `full`: Run full ETL (all games)
- `incremental`: Run incremental ETL (new games only - not yet implemented)
- `single`: Run ETL for specific game IDs
- `test`: Test mode (validation only)

**Response:**
```json
{
  "job_id": "abc123",
  "status": "running",
  "mode": "full",
  "created_at": "2026-01-15T10:00:00Z",
  "progress": 0,
  "current_step": "Starting ETL..."
}
```

#### `GET /api/etl/status/{job_id}`

Get status of an ETL job.

**Response:**
```json
{
  "job_id": "abc123",
  "status": "completed",
  "mode": "full",
  "created_at": "2026-01-15T10:00:00Z",
  "completed_at": "2026-01-15T10:01:20Z",
  "progress": 100,
  "current_step": "ETL complete",
  "result": {
    "tables_created": 139,
    "duration_seconds": 80
  }
}
```

#### `GET /api/etl/history`

Get ETL job history.

**Query Parameters:**
- `limit` (optional): Maximum number of jobs to return (default: 10)
- `status` (optional): Filter by status (`pending`, `running`, `completed`, `failed`, `cancelled`)

**Response:**
```json
[
  {
    "job_id": "abc123",
    "status": "completed",
    "mode": "full",
    "created_at": "2026-01-15T10:00:00Z"
  },
  {
    "job_id": "def456",
    "status": "running",
    "mode": "single",
    "created_at": "2026-01-15T09:00:00Z"
  }
]
```

#### `POST /api/etl/cancel/{job_id}`

Cancel a running ETL job.

**Response:**
```json
{
  "job_id": "abc123",
  "status": "cancelled",
  "cancelled_at": "2026-01-15T10:00:30Z"
}
```

---

### Upload Endpoints

#### `POST /api/upload/to-supabase`

Upload tables to Supabase.

**Request Body:**
```json
{
  "tables": ["fact_events", "dim_player"],
  "mode": "all",
  "options": {
    "replace": false,
    "batch_size": 1000
  }
}
```

**Modes:**
- `all`: Upload all tables (default)
- `dims`: Upload dimension tables only (`dim_*`)
- `facts`: Upload fact tables only (`fact_*`)
- `qa`: Upload QA/lookup tables only (`qa_*`, `lookup_*`)
- `basic`: Upload basic stats tables only (`*_basic`)
- `tracking`: Upload tracking-derived tables

**Response:**
```json
{
  "job_id": "upload123",
  "status": "running",
  "mode": "all",
  "created_at": "2026-01-15T10:00:00Z"
}
```

#### `POST /api/upload/generate-schema`

Generate Supabase schema SQL.

**Request Body:**
```json
{
  "options": {}
}
```

**Response:**
```json
{
  "job_id": "schema123",
  "status": "completed",
  "result": {
    "schema_file": "sql/reset_supabase.sql",
    "tables_count": 139
  }
}
```

#### `GET /api/upload/status/{job_id}`

Get status of an upload job.

**Response:**
```json
{
  "job_id": "upload123",
  "status": "completed",
  "progress": 100,
  "result": {
    "tables_uploaded": 139,
    "rows_uploaded": 50000
  }
}
```

---

### Staging Endpoints

#### `POST /api/staging/blb-tables/upload`

Upload BLB table data to staging.

**Request Body:**
```json
{
  "table_name": "dim_player",
  "data": [
    {
      "player_id": "P001",
      "first_name": "John",
      "last_name": "Doe"
    },
    {
      "player_id": "P002",
      "first_name": "Jane",
      "last_name": "Smith"
    }
  ],
  "replace": false
}
```

**Response:**
```json
{
  "success": true,
  "rows_inserted": 2,
  "rows_updated": 0,
  "errors": []
}
```

#### `PUT /api/staging/blb-tables/update`

Update rows in BLB staging table.

**Request Body:**
```json
{
  "table_name": "dim_player",
  "filter_column": "player_id",
  "filter_value": "P001",
  "updates": {
    "first_name": "Johnny",
    "current_skill_rating": 85
  }
}
```

**Response:**
```json
{
  "success": true,
  "rows_updated": 1
}
```

#### `GET /api/staging/blb-tables/list`

Get list of valid BLB table names.

**Response:**
```json
[
  "dim_player",
  "dim_team",
  "dim_schedule",
  "fact_gameroster"
]
```

#### `POST /api/staging/tracking/upload`

Upload tracking data (events/shifts) to staging.

**Request Body:**
```json
{
  "game_id": 18969,
  "events": [
    {
      "tracking_event_index": "1",
      "period": "1",
      "Type": "Shot",
      "event_player_1": "P100001"
    }
  ],
  "shifts": [
    {
      "shift_index": "1",
      "Period": "1",
      "shift_start_type": "Faceoff",
      "player_id": "P100001"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "events_inserted": 1,
  "shifts_inserted": 1,
  "errors": []
}
```

#### `DELETE /api/staging/blb-tables/{table_name}`

Clear all data from a BLB staging table.

**Query Parameters:**
- `confirm` (required): Must be `true` to confirm deletion

**Response:**
```json
{
  "success": true,
  "rows_deleted": 100
}
```

---

### ML Endpoints

#### `POST /api/ml/predict`

Get ML predictions (future feature).

**Request Body:**
```json
{
  "model": "goal_prediction",
  "features": {
    "player_id": "P100001",
    "game_context": {}
  }
}
```

**Response:**
```json
{
  "prediction": 0.75,
  "confidence": 0.85
}
```

---

## Error Responses

### Standard Error Format

```json
{
  "detail": "Error message here"
}
```

### Error Codes

- `400`: Bad Request (invalid parameters)
- `404`: Not Found (resource doesn't exist)
- `500`: Internal Server Error (server error)

### Example Error Response

```json
{
  "detail": "Job abc123 not found"
}
```

---

## Rate Limiting

Currently, there is no rate limiting. Future versions will implement rate limiting per API key.

---

## Related Documentation

- [API_ARCHITECTURE.md](API_ARCHITECTURE.md) - API architecture
- [API_INTEGRATION.md](API_INTEGRATION.md) - Integration guide

---

*Last Updated: 2026-01-15*
