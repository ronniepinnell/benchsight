# 11 - API: FastAPI Backend

**Learning Objectives:**
- Understand the API structure
- Know how to add new endpoints
- Understand the service layer pattern

---

## API Overview

The API is a **FastAPI** application that provides:
- ETL triggering and status
- Database upload endpoints
- Health checks
- Future: ML predictions

📍 **Location:** `api/`

---

## Directory Structure

```
api/
├── main.py                 # Application entry point
├── routes/                 # Endpoint handlers
│   ├── health.py           # Health check endpoints
│   ├── etl.py              # ETL trigger/status
│   ├── upload.py           # Database upload
│   ├── staging.py          # Staging operations
│   └── ml.py               # ML predictions (future)
├── services/               # Business logic
│   ├── etl_service.py      # ETL operations
│   ├── upload_service.py   # Upload operations
│   └── ml_service.py       # ML operations
├── models/                 # Request/response schemas
│   ├── etl_models.py       # ETL request/response
│   └── upload_models.py    # Upload request/response
└── utils/                  # Helpers
    └── logging.py          # Logging setup
```

---

## Main Application

📍 **File:** `api/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import health, etl, upload, staging, ml

# Create app
app = FastAPI(
    title="BenchSight API",
    description="API for BenchSight hockey analytics",
    version="1.0.0"
)

# CORS middleware (allow dashboard to call API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Dashboard
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(etl.router, prefix="/etl", tags=["ETL"])
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(staging.router, prefix="/staging", tags=["Staging"])
app.include_router(ml.router, prefix="/ml", tags=["ML"])
```

---

## Routes

### Health Route

📍 **File:** `api/routes/health.py`

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def health_check():
    """Basic health check."""
    return {"status": "ok"}

@router.get("/detailed")
async def detailed_health():
    """Detailed health check with dependencies."""
    return {
        "status": "ok",
        "database": check_database(),
        "etl": check_etl_status(),
    }
```

### ETL Route

📍 **File:** `api/routes/etl.py`

```python
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

from api.services.etl_service import ETLService

router = APIRouter()
etl_service = ETLService()

class ETLRequest(BaseModel):
    wipe: bool = False
    games: list[int] | None = None

class ETLResponse(BaseModel):
    job_id: str
    status: str
    message: str

@router.post("/run", response_model=ETLResponse)
async def run_etl(
    request: ETLRequest,
    background_tasks: BackgroundTasks
):
    """Trigger ETL run."""
    job_id = etl_service.create_job()

    # Run ETL in background
    background_tasks.add_task(
        etl_service.run_etl,
        job_id,
        wipe=request.wipe,
        games=request.games
    )

    return ETLResponse(
        job_id=job_id,
        status="started",
        message="ETL job started"
    )

@router.get("/status/{job_id}")
async def get_status(job_id: str):
    """Get ETL job status."""
    status = etl_service.get_status(job_id)
    return status
```

---

## Services

### ETL Service

📍 **File:** `api/services/etl_service.py`

```python
import subprocess
import uuid
from pathlib import Path

class ETLService:
    """Service for ETL operations."""

    def __init__(self):
        self.jobs = {}  # In-memory job tracking
        self.project_root = Path(__file__).parent.parent.parent

    def create_job(self) -> str:
        """Create new job and return ID."""
        job_id = str(uuid.uuid4())[:8]
        self.jobs[job_id] = {
            "status": "pending",
            "progress": 0,
            "message": "Job created"
        }
        return job_id

    def run_etl(self, job_id: str, wipe: bool = False, games: list[int] | None = None):
        """Run ETL process."""
        try:
            self.jobs[job_id]["status"] = "running"
            self.jobs[job_id]["message"] = "Running ETL..."

            # Build command
            cmd = ["python", "run_etl.py"]
            if wipe:
                cmd.append("--wipe")
            if games:
                cmd.extend(["--games"] + [str(g) for g in games])

            # Run ETL
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                self.jobs[job_id]["status"] = "completed"
                self.jobs[job_id]["message"] = "ETL completed successfully"
            else:
                self.jobs[job_id]["status"] = "failed"
                self.jobs[job_id]["message"] = result.stderr

        except Exception as e:
            self.jobs[job_id]["status"] = "failed"
            self.jobs[job_id]["message"] = str(e)

    def get_status(self, job_id: str) -> dict:
        """Get job status."""
        return self.jobs.get(job_id, {"status": "not_found"})
```

---

## Models (Pydantic)

📍 **File:** `api/models/etl_models.py`

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ETLRunRequest(BaseModel):
    """Request to run ETL."""
    wipe: bool = False
    games: Optional[list[int]] = None
    exclude_games: Optional[list[int]] = None

class ETLStatusResponse(BaseModel):
    """ETL job status response."""
    job_id: str
    status: str  # pending, running, completed, failed
    progress: int  # 0-100
    message: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    tables_created: Optional[int] = None

class TableInfo(BaseModel):
    """Information about a table."""
    name: str
    rows: int
    columns: int
    size_bytes: int
```

---

## Adding a New Endpoint

### Step 1: Create Route File

```python
# api/routes/analytics.py
from fastapi import APIRouter
from api.services.analytics_service import AnalyticsService

router = APIRouter()
analytics = AnalyticsService()

@router.get("/player/{player_id}/summary")
async def player_summary(player_id: str):
    """Get player analytics summary."""
    return analytics.get_player_summary(player_id)
```

### Step 2: Create Service

```python
# api/services/analytics_service.py
from api.utils.database import get_supabase

class AnalyticsService:
    def __init__(self):
        self.db = get_supabase()

    def get_player_summary(self, player_id: str) -> dict:
        """Get player analytics summary."""
        stats = self.db.table('fact_player_season_stats') \
            .select('*') \
            .eq('player_id', player_id) \
            .execute()

        return {
            "player_id": player_id,
            "seasons": stats.data
        }
```

### Step 3: Register in main.py

```python
# api/main.py
from api.routes import analytics

app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
```

---

## Running the API

```bash
# From project root
./benchsight.sh api dev     # Start dev server (port 8000)

# Or directly
cd api
uvicorn main:app --reload --port 8000
```

### Testing Endpoints

```bash
# Health check
curl http://localhost:8000/health/

# Trigger ETL
curl -X POST http://localhost:8000/etl/run \
  -H "Content-Type: application/json" \
  -d '{"wipe": true}'

# Check status
curl http://localhost:8000/etl/status/{job_id}
```

### API Documentation

FastAPI auto-generates docs:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Key Takeaways

1. **FastAPI** provides fast, type-safe REST APIs
2. **Routes** define endpoints, **Services** contain logic
3. **Pydantic models** validate request/response data
4. **Background tasks** for long-running operations (ETL)
5. **CORS middleware** allows dashboard to call API

---

**Next:** [12-tracker.md](12-tracker.md) - The game tracking application
