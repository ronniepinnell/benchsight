# BenchSight ETL API

REST API for triggering ETL jobs from the web admin portal.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r api/requirements.txt
```

### 2. Run the API

```bash
# From project root
cd api
python main.py

# Or using uvicorn directly
uvicorn api.main:app --reload --port 8000
```

### 3. Test the API

Visit http://localhost:8000/docs for interactive API documentation (Swagger UI).

Or test with curl:

```bash
# Health check
curl http://localhost:8000/api/health

# Trigger ETL
curl -X POST http://localhost:8000/api/etl/trigger \
  -H "Content-Type: application/json" \
  -d '{"mode": "full"}'
```

## API Endpoints

### Health & Status

- `GET /api/health` - Simple health check
- `GET /api/status` - Detailed system status

### ETL Jobs

- `POST /api/etl/trigger` - Trigger an ETL job
- `GET /api/etl/status/{job_id}` - Get job status
- `GET /api/etl/history` - Get job history
- `POST /api/etl/cancel/{job_id}` - Cancel a job

### Upload Endpoints

#### `POST /api/upload/to-supabase`
Upload tables to Supabase.

**Request Body:**
```json
{
  "tables": ["fact_events", "dim_player"],  // Optional: specific table names
  "mode": "all",  // Upload mode: all, dims, facts, qa, basic, tracking
  "options": {}  // Optional upload options
}
```

**Modes:**
- `all`: Upload all tables (default)
- `dims`: Upload dimension tables only (dim_*)
- `facts`: Upload fact tables only (fact_*)
- `qa`: Upload QA/lookup tables only (qa_*, lookup_*)
- `basic`: Upload basic stats tables only (*_basic)
- `tracking`: Upload tracking-derived tables

**Response:** `JobResponse` with job ID and status

**Example:**
```bash
curl -X POST http://localhost:8000/api/upload/to-supabase \
  -H "Content-Type: application/json" \
  -d '{"mode": "all"}'
```

#### `POST /api/upload/generate-schema`
Generate Supabase schema SQL.

Creates/updates `sql/reset_supabase.sql` with DROP and CREATE TABLE statements.

**Request Body:**
```json
{
  "options": {}  // Optional options
}
```

**Response:** `JobResponse` with job ID and status

**Example:**
```bash
curl -X POST http://localhost:8000/api/upload/generate-schema \
  -H "Content-Type: application/json" \
  -d '{}'
```

#### `GET /api/upload/status/{job_id}`
Get status of an upload job.

**Response:** `JobResponse` with job status and progress

**Example:**
```bash
curl http://localhost:8000/api/upload/status/abc123
```

### Staging Endpoints

#### `POST /api/staging/blb-tables/upload`
Upload BLB table data to staging.

**Request Body:**
```json
{
  "table_name": "dim_player",
  "data": [
    {"player_id": "P001", "first_name": "John", "last_name": "Doe"},
    {"player_id": "P002", "first_name": "Jane", "last_name": "Smith"}
  ],
  "replace": false
}
```

**Response:** Upload results with row counts and errors

**Example:**
```bash
curl -X POST http://localhost:8000/api/staging/blb-tables/upload \
  -H "Content-Type: application/json" \
  -d '{
    "table_name": "dim_player",
    "data": [{"player_id": "P001", "first_name": "John"}],
    "replace": false
  }'
```

#### `PUT /api/staging/blb-tables/update`
Update rows in BLB staging table.

**Request Body:**
```json
{
  "table_name": "dim_player",
  "filter_column": "player_id",
  "filter_value": "P001",
  "updates": {"first_name": "Johnny", "current_skill_rating": 85}
}
```

**Response:** Update results with row count

#### `GET /api/staging/blb-tables/list`
Get list of valid BLB table names.

**Response:** List of table names

#### `POST /api/staging/tracking/upload`
Upload tracking data (events/shifts) to staging.

**Request Body:**
```json
{
  "game_id": 18969,
  "events": [
    {"tracking_event_index": "1", "period": "1", "Type": "Shot"}
  ],
  "shifts": [
    {"shift_index": "1", "Period": "1", "shift_start_type": "Faceoff"}
  ]
}
```

**Response:** Upload results

#### `DELETE /api/staging/blb-tables/{table_name}?confirm=true`
Clear all data from a BLB staging table.

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/staging/blb-tables/dim_player?confirm=true"
```

## Development

### Project Structure

```
api/
├── main.py              # FastAPI app entry point
├── config.py            # Configuration
├── requirements.txt     # Dependencies
├── routes/
│   ├── health.py       # Health endpoints
│   └── etl.py          # ETL endpoints
├── services/
│   ├── job_manager.py  # Job tracking (in-memory MVP)
│   └── etl_service.py  # ETL wrapper
├── models/
│   └── job.py          # Data models
└── utils/
    └── logger.py       # Logging utilities
```

### Running in Development

```bash
# Auto-reload on changes
uvicorn api.main:app --reload --port 8000

# Or use the main.py script
python api/main.py
```

### Environment Variables

The API can be configured with environment variables:

- `ENVIRONMENT` - Set to "production" for production mode (default: "development")

## Integration with Admin Portal

The Admin Portal (`ui/portal/index.html`) can call this API to trigger ETL jobs.

Example JavaScript:

```javascript
// Trigger ETL
const response = await fetch('http://localhost:8000/api/etl/trigger', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    mode: 'full',
    options: {
      wipe: false,
      upload_to_supabase: true
    }
  })
});

const job = await response.json();
console.log('Job ID:', job.job_id);

// Check status
const statusResponse = await fetch(`http://localhost:8000/api/etl/status/${job.job_id}`);
const status = await statusResponse.json();
console.log('Status:', status.status);
```

## Deployment

For production deployment, see deployment guides in `docs/deployment/`.

Recommended platforms:
- **Railway** - Easy Python deployment
- **Render** - Free tier available
- **Fly.io** - Good performance

## Notes

- **MVP Implementation**: Currently uses in-memory job tracking. For production, consider:
  - Redis + Celery for job queue
  - Database for job persistence
  - WebSocket for real-time updates

- **ETL Integration**: Wraps existing `run_etl.py` script via subprocess. Future enhancements:
  - Direct Python function calls (no subprocess)
  - Better progress tracking
  - Streaming logs
