# BenchSight API Integration Guide

**How the API integrates with ETL, portal, and dashboard**

Last Updated: 2026-01-15  
Version: 1.0.0

---

## Overview

This document explains how the BenchSight API integrates with other components: ETL pipeline, admin portal, and dashboard.

**API Role:** Bridge between frontend and backend services  
**Integration Points:** ETL, Supabase, Admin Portal, Dashboard

---

## Integration Architecture

```mermaid
graph TB
    subgraph "Frontend"
        Portal[Admin Portal]
        Dashboard[Dashboard]
    end
    
    subgraph "API Layer"
        FastAPI[FastAPI API]
    end
    
    subgraph "Backend Services"
        ETL[ETL Pipeline]
        Supabase[(Supabase)]
    end
    
    Portal -->|ETL Triggers| FastAPI
    Portal -->|Upload Commands| FastAPI
    Dashboard -->|Data Queries| Supabase
    FastAPI -->|Execute| ETL
    FastAPI -->|Upload Data| Supabase
    ETL -->|Generate Tables| CSV Files
    CSV Files -->|Upload| Supabase
    
    style FastAPI fill:#e1f5ff
    style Supabase fill:#fff3cd
```

---

## ETL Integration

### How API Triggers ETL

**Flow:**
1. Admin Portal calls `POST /api/etl/trigger`
2. API creates job and starts ETL in background thread
3. ETL runs `run_etl.py` via subprocess
4. ETL generates CSV files in `data/output/`
5. Job status updated as ETL progresses
6. Client polls `GET /api/etl/status/{job_id}` for updates

**Implementation:**
```python
# api/services/etl_service.py
def run_etl_async(self, job_id: str, mode: str, ...):
    # Update job status to running
    job_manager.update_job(job_id, status=JobStatus.RUNNING)
    
    # Run ETL in background thread
    thread = threading.Thread(
        target=self._run_etl_sync,
        args=(job_id, mode, ...),
        daemon=True
    )
    thread.start()

def _run_etl_sync(self, job_id: str, mode: str, ...):
    # Build command
    cmd = ['python', 'run_etl.py']
    if mode == 'single' and game_ids:
        cmd.extend(['--games'] + [str(g) for g in game_ids])
    
    # Run ETL
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Update job status
    if result.returncode == 0:
        job_manager.update_job(job_id, status=JobStatus.COMPLETED)
    else:
        job_manager.update_job(job_id, status=JobStatus.FAILED, error=result.stderr)
```

### ETL Options

**Supported Options:**
- `wipe`: Delete all output before running
- `upload_to_supabase`: Auto-upload after ETL completes
- `source`: Data source (`excel` or `supabase`)
- `exclude_game_ids`: Games to exclude

---

## Supabase Integration

### Upload Integration

**Flow:**
1. Client calls `POST /api/upload/to-supabase`
2. API creates upload job
3. Upload service reads CSV files from `data/output/`
4. Upload service uploads to Supabase using Supabase client
5. Job status updated with progress
6. Client polls for completion

**Implementation:**
```python
# api/services/upload_service.py
def upload_tables(self, tables: List[str], mode: str):
    # Get Supabase client
    supabase = get_supabase_client()
    
    # Determine tables to upload
    if mode == 'all':
        tables = get_all_tables()
    elif mode == 'dims':
        tables = get_dimension_tables()
    # ... etc
    
    # Upload each table
    for table in tables:
        csv_path = OUTPUT_DIR / f"{table}.csv"
        df = pd.read_csv(csv_path)
        
        # Upload to Supabase
        supabase.table(table).upsert(df.to_dict('records'))
        
        # Update progress
        update_upload_progress(table, len(df))
```

### Schema Generation

**Flow:**
1. Client calls `POST /api/upload/generate-schema`
2. API reads table definitions from CSV files
3. API generates SQL CREATE TABLE statements
4. API writes to `sql/reset_supabase.sql`
5. Returns schema file location

---

## Admin Portal Integration

### Portal → API Flow

**ETL Trigger:**
```javascript
// ui/portal/index.html (or React component)
async function triggerETL() {
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
  })
  
  const job = await response.json()
  console.log('Job ID:', job.job_id)
  
  // Poll for status
  pollJobStatus(job.job_id)
}

async function pollJobStatus(jobId) {
  const response = await fetch(`http://localhost:8000/api/etl/status/${jobId}`)
  const job = await response.json()
  
  if (job.status === 'running') {
    // Update UI with progress
    updateProgress(job.progress, job.current_step)
    // Poll again
    setTimeout(() => pollJobStatus(jobId), 1000)
  } else if (job.status === 'completed') {
    // Show success
    showSuccess('ETL completed successfully!')
  }
}
```

### Upload Trigger

```javascript
async function uploadToSupabase() {
  const response = await fetch('http://localhost:8000/api/upload/to-supabase', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      mode: 'all'
    })
  })
  
  const job = await response.json()
  pollUploadStatus(job.job_id)
}
```

---

## Dashboard Integration

### Current Integration

**Direct Supabase:**
- Dashboard queries Supabase directly (not through API
- Uses Supabase client library
- Queries views and tables directly

**Future Integration:**
- Dashboard may use API for:
  - ETL status (if needed)
  - Upload status (if needed)
  - ML predictions (future)

---

## Staging Integration

### BLB Tables Upload

**Flow:**
1. Admin uploads BLB table data via portal
2. Portal calls `POST /api/staging/blb-tables/upload`
3. API validates data
4. API uploads to Supabase staging tables
5. Returns upload results

**Use Case:**
- Update master data (players, teams, schedule)
- Before running ETL

### Tracking Data Upload

**Flow:**
1. Tracker exports game data
2. Admin uploads via portal
3. Portal calls `POST /api/staging/tracking/upload`
4. API uploads events and shifts to staging
5. ETL can read from staging (future feature)

---

## Job Management Integration

### Job Lifecycle

```
Job Created
    ↓
Status: PENDING
    ↓
ETL Started
    ↓
Status: RUNNING
    ↓
Progress Updates (0-100%)
    ↓
ETL Complete
    ↓
Status: COMPLETED
    ↓
Result: { tables_created: 139, duration_seconds: 80 }
```

### Job Status Polling

**Recommended Pattern:**
```javascript
async function pollJobStatus(jobId, onUpdate, onComplete, onError) {
  const maxAttempts = 300  // 5 minutes max
  let attempts = 0
  
  const poll = async () => {
    if (attempts >= maxAttempts) {
      onError('Job timeout')
      return
    }
    
    const response = await fetch(`/api/etl/status/${jobId}`)
    const job = await response.json()
    
    onUpdate(job)  // Update UI
    
    if (job.status === 'completed') {
      onComplete(job)
    } else if (job.status === 'failed') {
      onError(job.error)
    } else {
      attempts++
      setTimeout(poll, 1000)  // Poll every second
    }
  }
  
  poll()
}
```

---

## Error Handling Integration

### API Error Responses

**Standard Format:**
```json
{
  "detail": "Error message"
}
```

**Client Handling:**
```javascript
try {
  const response = await fetch('/api/etl/trigger', {...})
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail)
  }
  const job = await response.json()
  // Handle success
} catch (error) {
  // Handle error
  showError(error.message)
}
```

---

## Configuration Integration

### Environment Variables

**API Configuration:**
```bash
ENVIRONMENT=production
CORS_ORIGINS=https://your-dashboard.vercel.app,https://your-portal.vercel.app
```

**Portal Configuration:**
```javascript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
```

---

## Future Integration Points

### WebSocket Integration

**Real-Time Updates:**
- Replace polling with WebSocket
- Real-time job status updates
- Real-time progress updates

### Authentication Integration

**API Keys:**
- Portal uses API key for authentication
- Dashboard uses API key (if needed)
- Rate limiting per API key

### ML Integration

**Predictions:**
- Dashboard calls ML endpoints
- Real-time predictions
- Batch predictions

---

## Related Documentation

- [API_REFERENCE.md](API_REFERENCE.md) - Endpoint reference
- [API_ARCHITECTURE.md](API_ARCHITECTURE.md) - Architecture overview

---

*Last Updated: 2026-01-15*
