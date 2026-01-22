---
name: portal-dev
description: Work on the admin portal for ETL control, job management, and system monitoring. Use when developing portal features or debugging admin functionality.
allowed-tools: Bash, Read, Write, Edit
---

# Portal Development

The admin portal controls ETL operations, monitors jobs, and manages the BenchSight system.

## Current Status

- UI mockup: 100% complete
- API integration: 10% complete
- Authentication: Not implemented
- Real functionality: Placeholder only

## Start Portal

```bash
# Serve portal locally (simple HTTP server)
cd ui/portal && python -m http.server 8080
```

Portal runs at: http://localhost:8080

## API Server (Required for functionality)

```bash
cd api && uvicorn main:app --reload --port 8000
```

## Portal Structure

```
ui/portal/
├── index.html      # Main portal page
├── js/
│   ├── config.js   # API configuration
│   ├── api.js      # API client
│   ├── etl.js      # ETL controls
│   ├── sync.js     # Supabase sync
│   ├── schema.js   # Schema management
│   └── tables.js   # Table browser
└── README.md
```

## Key Features to Implement

1. **ETL Control Panel**
   - Trigger ETL jobs
   - Monitor job progress
   - View job history
   - Cancel running jobs

2. **Game Management**
   - Upload tracking data
   - Manage game files
   - View processing status

3. **Database Browser**
   - View tables
   - Query data
   - Export functionality

4. **System Monitoring**
   - Health checks
   - Performance metrics
   - Error logs

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/etl/trigger` | POST | Trigger ETL |
| `/api/etl/status/{job_id}` | GET | Job status |
| `/api/etl/history` | GET | Job history |
| `/api/upload/tables` | POST | Upload CSVs |
| `/api/health` | GET | Health check |

## Development Priority

1. Connect ETL trigger to real API
2. Implement job status polling
3. Add authentication
4. Enable file upload
5. Add table browser functionality
