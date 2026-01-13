# Phase 1: ETL API Implementation Plan

**Detailed plan for building web-triggerable ETL API**

Last Updated: 2026-01-13  
Timeline: Weeks 1-2  
Priority: 🔴 CRITICAL

---

## Overview

Build a REST API that allows triggering ETL jobs from the web admin portal. This is the critical missing piece that connects your tracker → ETL → dashboard workflow.

---

## Architecture

```
┌─────────────────┐
│  Admin Portal   │
│   (Frontend)    │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│   ETL API       │ ◄─── NEW
│   (FastAPI)     │
└────────┬────────┘
         │
         ├──► Job Queue (Celery/Redis)
         │
         └──► run_etl.py (existing)
                 │
                 ▼
         ┌───────────────┐
         │  CSV Output   │
         │  Supabase     │
         └───────────────┘
```

---

## Technology Stack

### Recommended
- **Framework:** FastAPI (Python) - Fast, modern, auto-docs
- **Job Queue:** Celery + Redis (or simple async for MVP)
- **Deployment:** Railway or Render
- **Database:** Supabase (for job tracking)

### Alternative (Simpler MVP)
- **Framework:** FastAPI
- **Job Queue:** Background tasks (FastAPI built-in)
- **Deployment:** Railway
- **Storage:** SQLite for job tracking (upgrade later)

---

## Project Structure

```
api/
├── main.py                 # FastAPI app entry point
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── routes/
│   ├── __init__.py
│   ├── etl.py            # ETL endpoints
│   ├── games.py           # Game management
│   ├── upload.py          # Supabase upload
│   └── health.py          # Health checks
├── services/
│   ├── __init__.py
│   ├── etl_service.py     # ETL orchestration
│   ├── job_manager.py     # Job queue management
│   └── supabase_service.py # Supabase operations
├── models/
│   ├── __init__.py
│   ├── job.py             # Job data models
│   └── game.py            # Game data models
├── utils/
│   ├── __init__.py
│   └── logger.py          # Logging utilities
└── tests/
    ├── __init__.py
    └── test_etl_api.py    # API tests
```

---

## API Endpoints

### 1. Health & Status

```python
GET /api/health
# Returns: { "status": "healthy", "version": "1.0.0" }

GET /api/status
# Returns: System status, queue status, etc.
```

### 2. ETL Endpoints

```python
POST /api/etl/trigger
# Body: {
#   "mode": "full" | "incremental" | "single",
#   "game_ids": [18969, 18977],  # Optional
#   "options": {
#     "wipe": false,
#     "upload_to_supabase": true,
#     "validate": true
#   }
# }
# Returns: { "job_id": "abc123", "status": "queued" }

GET /api/etl/status/{job_id}
# Returns: {
#   "job_id": "abc123",
#   "status": "running" | "completed" | "failed",
#   "progress": 45,
#   "current_step": "Building fact tables",
#   "tables_created": 52,
#   "errors": [],
#   "started_at": "2026-01-13T10:00:00Z",
#   "completed_at": null
# }

GET /api/etl/history
# Query params: ?limit=10&status=completed
# Returns: List of recent jobs

GET /api/etl/logs/{job_id}
# Returns: Job logs (streaming or paginated)

POST /api/etl/cancel/{job_id}
# Cancels running job
```

### 3. Game Management

```python
GET /api/games
# Query params: ?status=tracked&limit=20
# Returns: List of games

GET /api/games/{game_id}
# Returns: Game details

POST /api/games
# Body: { "game_id": 19000, "home_team": "...", ... }
# Creates new game

PUT /api/games/{game_id}
# Updates game

DELETE /api/games/{game_id}
# Deletes game (with confirmation)

GET /api/games/{game_id}/status
# Returns: Tracking status, ETL status, etc.
```

### 4. Upload Endpoints

```python
POST /api/upload/to-supabase
# Body: {
#   "tables": ["fact_events", "fact_player_game_stats"],  # Optional: specific tables
#   "mode": "all" | "dims" | "facts" | "qa"
# }
# Returns: { "job_id": "upload_abc123", "status": "queued" }

GET /api/upload/status/{job_id}
# Returns: Upload progress
```

---

## Implementation Details

### Week 1: Core API Structure

#### Day 1-2: Setup & Basic Endpoints

**Tasks:**
1. Create `api/` directory structure
2. Set up FastAPI app
3. Create `requirements.txt`:
   ```txt
   fastapi==0.104.1
   uvicorn==0.24.0
   pydantic==2.5.0
   python-dotenv==1.0.0
   redis==5.0.1  # If using Celery
   celery==5.3.4  # If using Celery
   ```

4. Create basic endpoints:
   - `GET /api/health`
   - `GET /api/status`
   - Basic error handling

5. Test locally:
   ```bash
   cd api
   uvicorn main:app --reload
   ```

**Files to Create:**
- `api/main.py` - FastAPI app
- `api/config.py` - Configuration
- `api/routes/health.py` - Health endpoints
- `api/requirements.txt` - Dependencies

#### Day 3-4: ETL Integration

**Tasks:**
1. Create ETL service wrapper:
   - Import `run_etl.py` functions
   - Wrap in async function
   - Handle errors gracefully

2. Create job manager:
   - Simple in-memory queue (MVP)
   - Or Celery setup (production)
   - Job status tracking

3. Create ETL endpoints:
   - `POST /api/etl/trigger`
   - `GET /api/etl/status/{job_id}`
   - `GET /api/etl/history`

4. Test ETL trigger:
   ```bash
   curl -X POST http://localhost:8000/api/etl/trigger \
     -H "Content-Type: application/json" \
     -d '{"mode": "full"}'
   ```

**Files to Create:**
- `api/services/etl_service.py` - ETL wrapper
- `api/services/job_manager.py` - Job queue
- `api/routes/etl.py` - ETL endpoints
- `api/models/job.py` - Job models

#### Day 5: Game Management

**Tasks:**
1. Create game endpoints:
   - `GET /api/games`
   - `GET /api/games/{game_id}`
   - `POST /api/games`

2. Integrate with existing game discovery:
   - Use `base_etl.py:discover_games()`
   - Read from `data/raw/games/`
   - Return game list

**Files to Create:**
- `api/routes/games.py` - Game endpoints
- `api/models/game.py` - Game models

### Week 2: Advanced Features & Deployment

#### Day 6-7: Upload Integration

**Tasks:**
1. Create upload service:
   - Wrap `upload.py` functions
   - Support table filtering
   - Progress tracking

2. Create upload endpoints:
   - `POST /api/upload/to-supabase`
   - `GET /api/upload/status/{job_id}`

**Files to Create:**
- `api/services/supabase_service.py` - Upload wrapper
- `api/routes/upload.py` - Upload endpoints

#### Day 8-9: Job Persistence & Logging

**Tasks:**
1. Add job persistence:
   - Store jobs in SQLite (MVP) or Supabase
   - Job history
   - Status tracking

2. Add logging:
   - Structured logging
   - Job logs storage
   - Error tracking

**Files to Modify:**
- `api/services/job_manager.py` - Add persistence
- `api/utils/logger.py` - Logging utilities

#### Day 10: Testing & Deployment

**Tasks:**
1. Write tests:
   - API endpoint tests
   - ETL integration tests
   - Error handling tests

2. Deploy to Railway/Render:
   - Set up deployment config
   - Environment variables
   - Health checks

3. Test in production:
   - Trigger ETL from deployed API
   - Verify end-to-end

**Files to Create:**
- `api/tests/test_etl_api.py` - Tests
- `railway.json` or `render.yaml` - Deployment config

---

## Code Examples

### FastAPI App Structure

```python
# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import etl, games, upload, health

app = FastAPI(
    title="BenchSight ETL API",
    version="1.0.0",
    description="API for triggering ETL jobs"
)

# CORS for admin portal
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(etl.router, prefix="/api/etl", tags=["etl"])
app.include_router(games.router, prefix="/api/games", tags=["games"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])

@app.on_event("startup")
async def startup():
    # Initialize job manager, connect to Redis, etc.
    pass
```

### ETL Service

```python
# api/services/etl_service.py
import asyncio
from pathlib import Path
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from run_etl import run_full_etl
from upload import upload_to_supabase

async def run_etl_job(mode: str, game_ids: list = None, options: dict = None):
    """
    Run ETL job asynchronously.
    
    Args:
        mode: "full", "incremental", or "single"
        game_ids: List of game IDs (for single mode)
        options: Dict with wipe, upload_to_supabase, validate flags
    
    Returns:
        dict: Job result with status, tables_created, errors
    """
    try:
        # Set environment variables for game filtering
        if game_ids:
            os.environ['BENCHSIGHT_GAMES'] = ','.join(str(g) for g in game_ids)
        
        # Run ETL
        result = await asyncio.to_thread(run_full_etl)
        
        # Upload to Supabase if requested
        if options and options.get('upload_to_supabase'):
            upload_result = await asyncio.to_thread(
                upload_to_supabase,
                tables=options.get('tables'),
                mode=options.get('upload_mode', 'all')
            )
            result['upload'] = upload_result
        
        return {
            'status': 'completed',
            'success': result,
            'tables_created': count_tables(),
            'errors': []
        }
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e),
            'tables_created': 0,
            'errors': [str(e)]
        }
```

### ETL Endpoint

```python
# api/routes/etl.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from services.etl_service import run_etl_job
from services.job_manager import JobManager

router = APIRouter()
job_manager = JobManager()

class ETLRequest(BaseModel):
    mode: str  # "full", "incremental", "single"
    game_ids: list[int] = None
    options: dict = None

@router.post("/trigger")
async def trigger_etl(request: ETLRequest, background_tasks: BackgroundTasks):
    """Trigger ETL job."""
    # Create job
    job_id = job_manager.create_job(
        mode=request.mode,
        game_ids=request.game_ids,
        options=request.options or {}
    )
    
    # Run in background
    background_tasks.add_task(
        run_etl_job_async,
        job_id=job_id,
        mode=request.mode,
        game_ids=request.game_ids,
        options=request.options
    )
    
    return {"job_id": job_id, "status": "queued"}

@router.get("/status/{job_id}")
async def get_etl_status(job_id: str):
    """Get ETL job status."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

async def run_etl_job_async(job_id: str, mode: str, game_ids: list, options: dict):
    """Run ETL job and update status."""
    job_manager.update_status(job_id, "running")
    result = await run_etl_job(mode, game_ids, options)
    job_manager.complete_job(job_id, result)
```

---

## Job Manager Implementation

### Simple In-Memory (MVP)

```python
# api/services/job_manager.py
from datetime import datetime
from typing import Dict, Optional
import uuid

class JobManager:
    def __init__(self):
        self.jobs: Dict[str, dict] = {}
    
    def create_job(self, mode: str, game_ids: list = None, options: dict = None) -> str:
        """Create new job and return job_id."""
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = {
            'job_id': job_id,
            'mode': mode,
            'game_ids': game_ids,
            'options': options or {},
            'status': 'queued',
            'progress': 0,
            'current_step': None,
            'tables_created': 0,
            'errors': [],
            'started_at': datetime.now().isoformat(),
            'completed_at': None
        }
        return job_id
    
    def get_job(self, job_id: str) -> Optional[dict]:
        """Get job by ID."""
        return self.jobs.get(job_id)
    
    def update_status(self, job_id: str, status: str, progress: int = None, step: str = None):
        """Update job status."""
        if job_id in self.jobs:
            self.jobs[job_id]['status'] = status
            if progress is not None:
                self.jobs[job_id]['progress'] = progress
            if step:
                self.jobs[job_id]['current_step'] = step
    
    def complete_job(self, job_id: str, result: dict):
        """Mark job as complete."""
        if job_id in self.jobs:
            self.jobs[job_id].update(result)
            self.jobs[job_id]['status'] = 'completed'
            self.jobs[job_id]['completed_at'] = datetime.now().isoformat()
    
    def get_history(self, limit: int = 10) -> list:
        """Get recent jobs."""
        jobs = sorted(
            self.jobs.values(),
            key=lambda x: x['started_at'],
            reverse=True
        )
        return jobs[:limit]
```

### Production (Celery + Redis)

```python
# api/services/job_manager.py (Production version)
from celery import Celery
from celery.result import AsyncResult
import redis

# Celery app
celery_app = Celery(
    'benchsight_etl',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

@celery_app.task(name='run_etl_job')
def run_etl_task(mode: str, game_ids: list = None, options: dict = None):
    """Celery task to run ETL."""
    # Import here to avoid circular imports
    from services.etl_service import run_etl_job
    return run_etl_job(mode, game_ids, options)

class JobManager:
    def create_job(self, mode: str, game_ids: list = None, options: dict = None) -> str:
        """Create and queue Celery task."""
        task = run_etl_task.delay(mode, game_ids, options)
        return task.id
    
    def get_job(self, job_id: str) -> dict:
        """Get Celery task result."""
        result = AsyncResult(job_id, app=celery_app)
        return {
            'job_id': job_id,
            'status': result.status.lower(),
            'result': result.result if result.ready() else None,
            'progress': result.info.get('progress', 0) if result.info else 0
        }
```

---

## Integration with Existing Code

### Wrapping run_etl.py

```python
# api/services/etl_service.py
import os
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def run_etl_with_options(mode: str, game_ids: list = None, options: dict = None):
    """
    Wrapper for run_etl.py that supports API options.
    
    This function:
    1. Sets environment variables for game filtering
    2. Calls run_full_etl() from run_etl.py
    3. Handles errors
    4. Returns structured result
    """
    # Set game filtering if provided
    if game_ids:
        os.environ['BENCHSIGHT_GAMES'] = ','.join(str(g) for g in game_ids)
    
    # Handle wipe option
    if options and options.get('wipe'):
        # Delete output files
        output_dir = PROJECT_ROOT / 'data' / 'output'
        for csv_file in output_dir.glob('*.csv'):
            csv_file.unlink()
    
    # Import and run ETL
    try:
        from run_etl import run_full_etl
        success = run_full_etl()
        
        # Count tables created
        table_count = len(list((PROJECT_ROOT / 'data' / 'output').glob('*.csv')))
        
        return {
            'success': success,
            'tables_created': table_count,
            'errors': []
        }
    except Exception as e:
        return {
            'success': False,
            'tables_created': 0,
            'errors': [str(e)]
        }
```

### Wrapping upload.py

```python
# api/services/supabase_service.py
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def upload_to_supabase(tables: list = None, mode: str = 'all'):
    """
    Wrapper for upload.py.
    
    Args:
        tables: List of specific tables to upload (None = all)
        mode: 'all', 'dims', 'facts', 'qa'
    """
    try:
        from upload import upload_tables
        
        if tables:
            # Upload specific tables
            result = upload_tables(tables)
        else:
            # Upload by mode
            if mode == 'dims':
                result = upload_tables(mode='dims')
            elif mode == 'facts':
                result = upload_tables(mode='facts')
            elif mode == 'qa':
                result = upload_tables(mode='qa')
            else:
                result = upload_tables(mode='all')
        
        return {
            'success': True,
            'tables_uploaded': result.get('count', 0),
            'errors': result.get('errors', [])
        }
    except Exception as e:
        return {
            'success': False,
            'tables_uploaded': 0,
            'errors': [str(e)]
        }
```

---

## Error Handling

### Structured Error Responses

```python
# api/utils/errors.py
from fastapi import HTTPException
from typing import Optional

class ETLAPIError(HTTPException):
    """Custom API error."""
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        errors: Optional[list] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.errors = errors or []

# Usage in endpoints
@router.post("/trigger")
async def trigger_etl(request: ETLRequest):
    try:
        job_id = job_manager.create_job(...)
        return {"job_id": job_id}
    except Exception as e:
        raise ETLAPIError(
            status_code=500,
            detail="Failed to create ETL job",
            error_code="ETL_CREATE_FAILED",
            errors=[str(e)]
        )
```

---

## Testing Strategy

### Unit Tests

```python
# api/tests/test_etl_api.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_trigger_etl():
    response = client.post(
        "/api/etl/trigger",
        json={"mode": "full", "options": {"wipe": False}}
    )
    assert response.status_code == 200
    assert "job_id" in response.json()

def test_get_job_status():
    # First create a job
    trigger_response = client.post("/api/etl/trigger", json={"mode": "full"})
    job_id = trigger_response.json()["job_id"]
    
    # Then check status
    status_response = client.get(f"/api/etl/status/{job_id}")
    assert status_response.status_code == 200
    assert status_response.json()["job_id"] == job_id
```

---

## Deployment

### Railway Deployment

```yaml
# railway.json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Environment Variables

```bash
# .env (for local)
BENCHSIGHT_PROJECT_ROOT=/path/to/benchsight
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
REDIS_URL=redis://localhost:6379  # If using Celery
```

---

## Security Considerations

### Authentication (Phase 1 MVP)

```python
# Simple API key for MVP
API_KEY = os.getenv("ETL_API_KEY")

@router.post("/trigger")
async def trigger_etl(
    request: ETLRequest,
    api_key: str = Header(None)
):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    # ... rest of endpoint
```

### Production (Phase 2)

- Use Supabase Auth
- JWT tokens
- Role-based access (admin only for ETL)

---

## Progress Tracking

### Real-time Updates

```python
# WebSocket support (optional, Phase 2)
from fastapi import WebSocket

@router.websocket("/ws/etl/{job_id}")
async def etl_progress(websocket: WebSocket, job_id: str):
    await websocket.accept()
    while True:
        job = job_manager.get_job(job_id)
        await websocket.send_json(job)
        if job['status'] in ['completed', 'failed']:
            break
        await asyncio.sleep(1)
```

---

## Success Criteria

### Week 1
- [ ] API runs locally
- [ ] Health endpoint works
- [ ] Can trigger ETL via API
- [ ] Job status endpoint works

### Week 2
- [ ] Upload endpoint works
- [ ] Game management endpoints work
- [ ] API deployed to Railway/Render
- [ ] Admin portal can trigger ETL

---

## Next Steps After Phase 1

1. **Add authentication** (Phase 2)
2. **Add WebSocket for real-time updates** (Phase 2)
3. **Add job persistence** (Supabase instead of in-memory)
4. **Add incremental ETL** (only process new games)
5. **Add ETL scheduling** (run automatically)

---

*Plan created: 2026-01-13*
