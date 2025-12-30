# BenchSight Hockey Analytics Platform

**Version:** 2.0  
**Status:** 85% Production Ready  
**Date:** December 30, 2025

---

## Overview

BenchSight is a comprehensive hockey analytics platform for the NORAD recreational hockey league. It processes game tracking data through an ETL pipeline and stores it in a Supabase PostgreSQL database.

## Quick Start

```bash
# 1. Setup config
cp config/config_local.ini.example config/config_local.ini
# Edit with your Supabase credentials

# 2. Create schema in Supabase SQL Editor
# Run: sql/05_FINAL_COMPLETE_SCHEMA.sql

# 3. Load all data
python scripts/load_all_tables.py --upsert

# 4. Verify
python -m pytest tests/ -v
```

---

## Documentation

| Role | Start Here |
|------|------------|
| **Tracker Dev** | `docs/handoffs/TRACKER_DEV_HANDOFF.md` |
| **Dashboard Dev** | `docs/handoffs/DASHBOARD_DEV_HANDOFF.md` |
| **Portal Dev** | `docs/handoffs/PORTAL_DEV_HANDOFF.md` |
| **Project Manager** | `docs/handoffs/PROJECT_MANAGER_HANDOFF.md` |

### HTML Versions
Open `docs/html/` in a browser for formatted documentation.

### Claude Prompts
Use prompts from `prompts/` to start new Claude chats with full context.

---

## Project Structure

```
benchsight/
├── config/              # Configuration
├── data/output/         # 96 CSV files
├── sql/                 # Database scripts
├── scripts/             # Loaders
├── src/                 # ETL code
├── tests/               # 326 tests
├── docs/                # Documentation
│   ├── handoffs/        # Role guides
│   ├── guides/          # How-tos
│   └── html/            # HTML docs
├── dashboard/           # Prototypes
└── prompts/             # Claude prompts
```

---

## Key Commands

```bash
# Load data
python scripts/load_all_tables.py --upsert

# Run tests  
python -m pytest tests/ -v

# Check config
python scripts/flexible_loader_with_logging.py --show-config
```

---

## Status

✅ Database Schema (96 tables)  
✅ ETL Pipeline  
✅ Data Loader  
✅ Logging System  
✅ Test Suite (326 passing)  
🔄 Tracker (prototype)  
🔄 Dashboard (prototype)  
❌ Admin Portal (planned)

---

## Contact

Supabase: https://supabase.com/dashboard/project/uuaowslhpgyiudmbvqze
