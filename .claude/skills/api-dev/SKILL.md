---
name: api-dev
description: Start the FastAPI backend server for ETL operations, data uploads, and ML predictions. Use when developing API features or debugging backend issues.
allowed-tools: Bash, Read, Write, Edit
---

# API Development

The FastAPI backend provides ETL control, data upload, and ML prediction endpoints.

## Quick Start

```bash
cd api && uvicorn main:app --reload --port 8000
```

API runs at: http://localhost:8000
Docs at: http://localhost:8000/docs

## Environment Setup

Create `api/.env`:
```bash
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:8000,http://localhost:8080
SUPABASE_URL=https://amuisqvhhiigxetsfame.supabase.co
SUPABASE_SERVICE_KEY=<service_key>
```

## API Structure

```
api/
├── main.py           # FastAPI app
├── config.py         # Configuration
├── routes/
│   ├── health.py     # Health check
│   ├── etl.py        # ETL endpoints
│   ├── upload.py     # Upload endpoints
│   ├── staging.py    # Staging tables
│   └── ml.py         # ML predictions
├── services/
│   ├── etl_service.py
│   ├── upload_service.py
│   └── ml_service.py
└── models/
    ├── request_models.py
    └── response_models.py
```

## Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/api/etl/trigger` | POST | Trigger ETL job |
| `/api/etl/status/{job_id}` | GET | Get job status |
| `/api/etl/history` | GET | Job history |
| `/api/upload/tables` | POST | Upload CSVs |
| `/api/staging/blb` | POST | BLB staging |
| `/api/staging/tracking` | POST | Tracking staging |
| `/api/ml/predict` | POST | ML predictions |

## Testing

```bash
cd api && pytest tests/
```

## Development Standards

1. **Error handling**: All endpoints must have proper error handling
2. **Validation**: Use Pydantic models for request/response
3. **Logging**: Log all operations for debugging
4. **CORS**: Configure for portal and dashboard origins
5. **Background tasks**: Use for long-running ETL jobs

## Performance Targets

- Health check: < 50ms
- ETL trigger: < 200ms (returns job ID immediately)
- Upload: < 5s for typical CSV
- Status check: < 100ms
