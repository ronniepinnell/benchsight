# BenchSight Development Guide

## Running Multiple Development Processes in Parallel

Yes! You can absolutely run multiple development processes simultaneously. They don't conflict with each other.

### Quick Start

**Option 1: Use the helper script**
```bash
./dev.sh
```

This will start:
- Next.js Dashboard on http://localhost:3000
- Keep Python ETL ready to run manually

**Option 2: Run manually in separate terminals**

**Terminal 1 - Dashboard:**
```bash
cd ui/dashboard
npm install  # First time only
npm run dev
# Dashboard available at http://localhost:3000
```

**Terminal 2 - ETL (when needed):**
```bash
# Run ETL when you need to process data
python run_etl.py

# Or with options
python run_etl.py --wipe
python run_etl.py --games 18969 18977
```

**Terminal 3 - Other tasks:**
```bash
# Validation
python validate.py

# Upload to Supabase
python upload.py
```

### What Runs on What Ports?

| Service | Port | Description |
|---------|------|-------------|
| Next.js Dashboard | 3000 | Frontend development server |
| Python ETL | N/A | Data processing (no web server) |
| Supabase | External | Cloud database (shared resource) |

### Development Workflow

1. **Start Dashboard** (runs continuously)
   ```bash
   cd ui/dashboard && npm run dev
   ```
   - Hot reloads on file changes
   - Access at http://localhost:3000

2. **Run ETL** (when data changes)
   ```bash
   python run_etl.py
   ```
   - Processes data and generates CSV files
   - Takes ~80 seconds for full run
   - No port conflicts

3. **Upload to Supabase** (when ready)
   ```bash
   python upload.py
   ```
   - Uploads CSV files to Supabase
   - Dashboard will see new data after upload

### Tips

- **Dashboard development**: Keep `npm run dev` running while you work on UI components
- **ETL runs**: Run `python run_etl.py` when you need fresh data
- **No conflicts**: These processes are completely independent
- **Shared resource**: Both connect to Supabase, but that's fine - it's designed for concurrent access

### Troubleshooting

**Port 3000 already in use?**
```bash
# Find what's using port 3000
lsof -i :3000

# Kill it if needed
kill -9 <PID>

# Or use a different port for Next.js
cd ui/dashboard
PORT=3001 npm run dev
```

**Dashboard not updating?**
- Check browser console for errors
- Verify Supabase connection in `.env.local`
- Restart the dev server: `Ctrl+C` then `npm run dev`

**ETL conflicts?**
- ETL writes to `data/output/` directory
- Multiple ETL runs will overwrite files (this is expected)
- Use `--wipe` flag to start fresh
