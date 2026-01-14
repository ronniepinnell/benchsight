# Admin Portal

Admin portal for BenchSight - Control ETL jobs and manage games.

## Features

- **ETL Pipeline Control** - Trigger ETL jobs from the web UI
- **Job Status Tracking** - Real-time status updates with progress bars
- **Game Management** - View and manage tracked games
- **Data Browser** - Browse database tables
- **System Status** - Monitor system health

## Setup

### 1. Start the API

The portal requires the ETL API to be running:

```bash
# From project root
uvicorn api.main:app --reload --port 8000
```

### 2. Open the Portal

Simply open `index.html` in your browser, or serve it via a web server:

```bash
# Using Python's built-in server
cd ui/portal
python3 -m http.server 8080

# Then open: http://localhost:8080
```

## API Connection

The portal connects to the ETL API at `http://localhost:8000` by default.

To change the API URL, edit `js/config.js`:

```javascript
const API_CONFIG = {
  baseUrl: 'http://localhost:8000',  // Change this
  timeout: 30000
};
```

## Usage

### Trigger ETL Job

1. Go to **⚙️ ETL Pipeline** section
2. Select mode:
   - **Full**: Process all games
   - **Incremental**: Process new games only (not yet implemented)
   - **Single**: Process specific game IDs
3. Configure options:
   - **Clean Output**: Wipe output directory before ETL
   - **Sync to Supabase**: Automatically upload to Supabase after ETL
   - **Regenerate Schema**: Generate schema SQL after ETL (you still need to run it manually)
   - **Verify Goals**: Validate goal data
4. Click **▶ Run ETL**
5. Watch progress in real-time

### View Job Status

- Job status updates automatically every 2 seconds
- Progress bar shows completion percentage
- Logs show current step and any errors
- Badge shows current status (RUNNING, COMPLETED, FAILED, etc.)

### Cancel Job

Click **⏹ Stop** to cancel a running job.

## File Structure

```
ui/portal/
├── index.html          # Main portal page
├── js/
│   ├── config.js      # API configuration
│   ├── api.js         # API client
│   └── etl.js         # ETL controls
└── README.md          # This file
```

## Development

### Adding New Features

1. Create JavaScript file in `js/` directory
2. Include it in `index.html` before the main script tag
3. Wire up UI elements to functions

### API Integration

All API calls go through the `api` client (from `js/api.js`):

```javascript
// Trigger ETL
const response = await api.triggerETL('full', null, {
  wipe: false,
  upload_to_supabase: true,
  regenerate_schema: false
});

// Check status
const status = await api.getETLStatus(jobId);

// Get history
const history = await api.getETLHistory(10);
```

## Troubleshooting

**Portal can't connect to API:**
- Make sure API is running: `uvicorn api.main:app --reload --port 8000`
- Check API URL in `js/config.js`
- Check browser console for CORS errors

**Job status not updating:**
- Check browser console for errors
- Verify API is responding: `curl http://localhost:8000/api/health`
- Check job ID is correct

**Buttons not working:**
- Make sure JavaScript files are loaded (check Network tab)
- Check browser console for errors
- Verify functions are defined (check Sources tab)
