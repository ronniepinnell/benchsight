# BenchSight Portal Admin Developer Handoff

## 🎯 Your Mission

Build an admin portal UI that provides complete control over the BenchSight system. This replaces command-line operations with a web interface for running ETL, managing data, monitoring health, and administering the platform.

---

## 📖 Required Reading (In Order)

### 1. This README - Portal requirements and features
### 2. SUPABASE_WRITE_STRATEGY.md - How data flows through the system
### 3. docs/SCHEMA_AND_ERD.md - Database structure
### 4. docs/MASTER_INSTRUCTIONS.md - Business rules
### 5. Data dictionaries - Column definitions

---

## 🔌 System Access Requirements

### Supabase Connection
```
Project URL: https://uuaowslhpgyiudmbvqze.supabase.co
Dashboard: https://supabase.com/dashboard/project/uuaowslhpgyiudmbvqze

Required Keys:
- anon key (for read operations)
- service_role key (for admin operations - NEVER expose to client)
```

### Server/Backend Access
The portal needs a backend server to run Python scripts. Options:
1. **Node.js + child_process** - Spawn Python scripts
2. **Python Flask/FastAPI** - Native Python backend
3. **Serverless functions** - AWS Lambda, Vercel, etc.

---

## 📋 Portal Features Specification

### Feature 1: ETL Pipeline Control

**UI Requirements:**
- Run Full ETL button (etl.py → fix_data_integrity.py → fix_final_data.py)
- Run Validation Only button
- Run Fix Data Only button
- Run Tests button (pytest)
- Real-time log streaming
- Last run status display
- Execution history

**Scripts to Execute:**
```bash
# Full ETL Pipeline
python etl.py
python scripts/fix_data_integrity.py
python scripts/fix_final_data.py
python scripts/etl_validation.py

# Tests
pytest tests/ -v --tb=short
```

**Backend Endpoints Needed:**
- POST /api/etl/run-full
- POST /api/etl/run-validation
- POST /api/etl/fix-data
- POST /api/etl/run-tests
- GET /api/etl/status
- WebSocket /api/etl/stream (real-time logs)

---

### Feature 2: Database Table Viewer

**UI Requirements:**
- Table selector dropdown
- Row count display
- Paginated data grid
- Column sorting
- Filter/search
- CSV download
- Schema viewer

**Tables to Display:**
- dim_player, dim_team, dim_schedule
- fact_events, fact_events_player
- fact_shifts, fact_shifts_player
- fact_player_game_stats, fact_team_game_stats
- fact_goalie_game_stats
- fact_h2h, fact_wowy
- staging_events, staging_shifts (if implemented)

**Backend Endpoints:**
- GET /api/tables (list all with counts)
- GET /api/tables/{name} (paginated data)
- GET /api/tables/{name}/schema
- GET /api/tables/{name}/download

---

### Feature 3: Data Upload

**UI Requirements:**
- CSV file upload
- Target table selector
- Truncate before upload option
- Tracking file upload (xlsx)
- Bulk upload all CSVs
- Upload progress indicator

**Backend Endpoints:**
- POST /api/upload/csv
- POST /api/upload/tracking-file
- POST /api/upload/bulk

---

### Feature 4: Validation Dashboard

**UI Requirements:**
- Run All Validations button
- Validation result cards (pass/fail/warning)
- Error details list
- Ground truth comparison
- Test results display

**Validations to Run:**
- Primary key uniqueness
- Foreign key integrity
- Data type validation
- Percentage range checks (0-100)
- Row count consistency
- Ground truth match

**Backend Endpoints:**
- POST /api/validate/all
- POST /api/validate/ground-truth
- GET /api/validate/results

---

### Feature 5: Documentation Hub

**UI Requirements:**
- List of all docs
- Markdown/HTML viewer
- Individual file download
- Download all as ZIP

**Docs to Include:**
- Master Instructions
- Schema & ERD
- Developer Workflow
- Data Dictionaries (11 files)
- Tracker Dev Guide
- Dashboard Dev Guide

**Backend Endpoints:**
- GET /api/docs
- GET /api/docs/{name}
- GET /api/docs/download-all

---

### Feature 6: System Health

**UI Requirements:**
- Supabase connection status
- ETL last run status
- Table row counts
- Recent activity log
- Data quality percentage

**Backend Endpoints:**
- GET /api/health
- GET /api/health/tables
- GET /api/activity

---

### Feature 7: Game Management

**UI Requirements:**
- List of all games
- Game status (live, gaps, processing)
- Add new game
- Reprocess game
- Delete game
- View game details

**Backend Endpoints:**
- GET /api/games
- GET /api/games/{id}
- POST /api/games/{id}/reprocess
- DELETE /api/games/{id}

---

## 🛠️ Technical Stack Recommendation

```
FRONTEND:
├── React or Vue.js
├── Tailwind CSS
├── React Query or SWR
└── Supabase JS client

BACKEND:
├── Python FastAPI (recommended)
├── Supabase Python client
├── subprocess module
└── WebSocket support
```

---

## 📦 Example Backend Code

### Script Runner
```python
from fastapi import FastAPI
import subprocess

app = FastAPI()

@app.post("/api/etl/run-full")
async def run_full_etl():
    commands = [
        ["python", "etl.py"],
        ["python", "scripts/fix_data_integrity.py"],
        ["python", "scripts/fix_final_data.py"],
        ["python", "scripts/etl_validation.py"]
    ]
    
    results = []
    for cmd in commands:
        result = subprocess.run(cmd, capture_output=True, text=True)
        results.append({
            "command": " ".join(cmd),
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        })
        if result.returncode != 0:
            break
    
    return {"success": all(r["success"] for r in results), "results": results}
```

### Table Viewer
```python
from supabase import create_client

supabase = create_client(URL, SERVICE_KEY)

@app.get("/api/tables/{table_name}")
async def get_table(table_name: str, page: int = 1, limit: int = 50):
    offset = (page - 1) * limit
    result = supabase.table(table_name).select("*").range(offset, offset + limit - 1).execute()
    count = supabase.table(table_name).select("*", count="exact").execute()
    return {"data": result.data, "total": count.count, "page": page}
```

---

## ✅ Success Criteria

### MVP
- [ ] ETL control (run, view status)
- [ ] Table viewer (browse, download)
- [ ] Basic health check
- [ ] Authentication

### Full Release
- [ ] All 7 features implemented
- [ ] Real-time log streaming
- [ ] File uploads working
- [ ] Validation dashboard

---

## 🔐 Security Notes

1. Backend handles all admin operations
2. Never expose service_role key to frontend
3. Require authentication for all endpoints
4. Log all destructive operations
5. Rate limit script execution

---

*Last Updated: December 2024*
