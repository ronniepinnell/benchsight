# BenchSight Setup Guide

**Complete installation and configuration instructions**

Last Updated: 2026-01-13

---

## Prerequisites

### Required Software

- **Python 3.11+** (tested with 3.11)
- **pip** (Python package manager)
- **Git** (for cloning the repository)
- **PostgreSQL** (optional, for local database)
- **Supabase account** (for cloud database)

### System Requirements

- **OS**: macOS, Linux, or Windows
- **RAM**: 4GB minimum (8GB recommended)
- **Disk Space**: 500MB for project + data

---

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd benchsight
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

**Required packages:**
- `flask>=2.0.0` - Web framework (for admin portal)
- `pandas>=1.5.0` - Data processing
- `openpyxl>=3.0.0` - Excel file handling

**Additional packages you may need:**
```bash
# For Supabase integration
pip install supabase

# For PostgreSQL (if using local database)
pip install psycopg2-binary

# For data validation
pip install pytest
```

### 4. Configure Environment

#### Create Local Configuration

```bash
# Copy template to local config
cp config/config.ini config/config_local.ini
```

#### Edit `config/config_local.ini`

```ini
[database]
# For Supabase (recommended)
host = db.xxxxx.supabase.co
port = 5432
database = postgres
user = postgres
password = your_supabase_password

# OR for local PostgreSQL
# host = localhost
# port = 5432
# database = hockey_analytics
# user = postgres
# password = your_local_password

[paths]
# Verify these paths exist
blb_tables_file = data/raw/BLB_Tables.xlsx
game_data_root = data/raw/games
output_dir = data/output

[processing]
batch_size = 1000
log_level = INFO
```

#### Supabase Setup (Recommended)

1. **Create Supabase Project**
   - Go to [supabase.com](https://supabase.com)
   - Create new project
   - Note your project URL and service key

2. **Get Connection Details**
   - Project Settings → Database
   - Copy connection string or individual values

3. **Set Environment Variables** (Optional)
   ```bash
   export SUPABASE_URL=https://xxxxx.supabase.co
   export SUPABASE_KEY=your_service_key
   ```

---

## Verify Installation

### 1. Check Python Version

```bash
python --version
# Should show Python 3.11 or higher
```

### 2. Verify Dependencies

```bash
python -c "import pandas; import openpyxl; print('Dependencies OK')"
```

### 3. Check Project Structure

```bash
# Verify key directories exist
ls -la data/raw/
ls -la config/
ls -la src/
```

### 4. Test ETL (Dry Run)

```bash
# List available games
python run_etl.py --list-games

# Check ETL status
python run_etl.py --status
```

---

## First-Time Setup

### 1. Prepare Raw Data

Ensure you have:
- `data/raw/BLB_Tables.xlsx` - Master dimension data
- `data/raw/games/{game_id}/` - Game tracking files
  - `tracking_export.xlsx` - Event data
  - `roster.xlsx` - Game roster
  - `shifts.xlsx` - Shift data (optional)

### 2. Run Initial ETL

```bash
# Full ETL run (generates all 139 tables)
python run_etl.py

# This will:
# - Extract data from Excel files
# - Transform into dimensional model
# - Generate CSV files in data/output/
```

### 3. Validate Output

```bash
# Run validation checks
python validate.py

# Should show:
# - 139 tables generated
# - No validation errors
# - Goal counts match expected values
```

### 4. Set Up Supabase (Optional)

```bash
# Generate schema SQL
python upload.py --schema

# This creates: sql/reset_supabase.sql

# Then in Supabase SQL Editor:
# 1. Run sql/reset_supabase.sql to create tables
# 2. Run sql/views/99_DEPLOY_ALL_VIEWS.sql to create views
# 3. Upload data: python upload.py
```

---

## Common Setup Issues

### Issue: "Module not found"

**Solution:**
```bash
# Ensure you're in project root
cd /path/to/benchsight

# Verify Python path
python -c "import sys; print(sys.path)"

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: "File not found: BLB_Tables.xlsx"

**Solution:**
```bash
# Check file exists
ls -la data/raw/BLB_Tables.xlsx

# If missing, you need to obtain this file
# It contains master dimension data
```

### Issue: "Permission denied" on data/output/

**Solution:**
```bash
# Create output directory
mkdir -p data/output

# Set permissions (macOS/Linux)
chmod 755 data/output
```

### Issue: Supabase connection fails

**Solution:**
1. Verify credentials in `config/config_local.ini`
2. Check Supabase project is active
3. Verify network connectivity
4. Test connection:
   ```python
   from supabase import create_client
   supabase = create_client(url, key)
   print(supabase.table('dim_player').select('*').limit(1).execute())
   ```

---

## Development Setup

### For Contributors

1. **Fork the repository**
2. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Install development dependencies**
   ```bash
   pip install -r requirements.txt
   pip install pytest black flake8  # Optional: testing and linting
   ```
4. **Run tests**
   ```bash
   pytest tests/
   ```

### IDE Setup

**VS Code:**
- Install Python extension
- Set Python interpreter to virtual environment
- Recommended extensions:
  - Python
  - Pylance
  - GitLens

**PyCharm:**
- Open project directory
- Configure Python interpreter (use virtual environment)
- Mark `src/` as source root

---

## Configuration Reference

### Key Configuration Files

| File | Purpose |
|------|---------|
| `config/config.ini` | Template (do not edit) |
| `config/config_local.ini` | Your local settings (gitignored) |
| `config/excluded_games.txt` | Games to skip in ETL |
| `config/IMMUTABLE_FACTS.json` | Protected dimension values |

### Environment Variables

```bash
# Supabase (optional, can use config file instead)
export SUPABASE_URL=https://xxxxx.supabase.co
export SUPABASE_KEY=your_service_key

# ETL Settings (optional)
export ETL_BATCH_SIZE=1000
export ETL_LOG_LEVEL=INFO
```

---

## Next Steps

After setup is complete:

1. **Read the Quick Start Guide**: [QUICK_START.md](QUICK_START.md)
2. **Review Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
3. **Understand ETL Process**: [ETL.md](ETL.md)
4. **Check Documentation Index**: [README.md](README.md) for all available docs
5. **Check TODO**: [TODO.md](TODO.md) for current priorities

---

## Getting Help

- **Documentation**: See `docs/` directory
- **Code Standards**: `docs/CODE_STANDARDS.md`
- **Known Issues**: `docs/HANDOFF.md`
- **Validation**: Run `python validate.py --help`

---

*Last updated: 2026-01-13*
