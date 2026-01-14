# API Quick Start

## Run from Project Root

**IMPORTANT:** You must be in the project root directory (where `run_etl.py` is located).

### Steps:

1. **Navigate to project root:**
   ```bash
   cd "/Users/ronniepinnell/Documents/Documents - Ronnie's MacBook Pro - 1/Programming_HD/Hockey/Benchsight/git/benchsight"
   # Or use your path to the project
   ```

2. **Verify you're in the right place:**
   ```bash
   ls -la run_etl.py api/main.py
   # Should show both files exist
   ```

3. **Run the API:**
   ```bash
   uvicorn api.main:app --reload --port 8000
   ```

### Quick Test:

Once running, visit:
- http://localhost:8000/api/health
- http://localhost:8000/docs (Swagger UI)

### Troubleshooting

**Error: "No module named 'api'"**
→ You're not in the project root. Run `cd` to the project directory first.

**Error: "ModuleNotFoundError"**
→ Make sure you installed dependencies: `pip install -r api/requirements.txt`
