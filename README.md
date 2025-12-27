# BenchSight - Beer League Hockey Analytics

**Version:** 2.0.0  
**Last Updated:** December 27, 2025

---

## Overview

BenchSight is a comprehensive hockey analytics platform for tracking and analyzing beer league games. It includes:

- **ETL Pipeline** - Python scripts to process game data
- **Supabase Database** - PostgreSQL with 36 tables
- **Tracker UI** - HTML interface for live game tracking
- **Dashboards** - Visualization of player and team stats
- **Power BI Ready** - Direct database connection support

---

## Quick Start

### 1. Set Up Database

```bash
# Go to Supabase SQL Editor and run:
sql/supabase_schema_complete.sql
```

### 2. Upload Data

```bash
pip install supabase pandas --break-system-packages
python src/supabase_upload.py
```

### 3. Open Tracker

Open `html/tracker.html` in a browser.

---

## Database Schema

| Category | Tables | Rows |
|----------|--------|------|
| Core Dimensions | 8 | 1,281 |
| Lookup Dimensions | 16 | 218 |
| Fact Tables | 12 | 41,921 |
| **Total** | **36** | **~43,400** |

See `docs/DATA_DICTIONARY_COMPLETE.md` for full schema documentation.

---

## Project Structure

```
benchsight/
├── data/
│   ├── BLB_Tables.xlsx       # Master data
│   ├── raw/games/            # Raw tracking files
│   └── output/               # 36 CSV files
├── docs/
│   ├── DATA_DICTIONARY_COMPLETE.md
│   ├── SCHEMA_DIAGRAMS.md
│   ├── LLM_HANDOFF.md
│   └── CHANGELOG.md
├── html/
│   └── tracker.html
├── sql/
│   └── supabase_schema_complete.sql
├── src/
│   ├── combine_tracking.py
│   └── supabase_upload.py
└── README.md
```

---

## Supabase Connection

```javascript
const SUPABASE_URL = 'https://uuaowslhpgyiudmbvqze.supabase.co';
const SUPABASE_KEY = 'sb_publishable_t1lIOebbbCjAu_YBKc8tLg_B_zH_l73';
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [DATA_DICTIONARY_COMPLETE.md](docs/DATA_DICTIONARY_COMPLETE.md) | All 36 tables with columns |
| [SCHEMA_DIAGRAMS.md](docs/SCHEMA_DIAGRAMS.md) | Visual ERD and flow diagrams |
| [LLM_HANDOFF.md](docs/LLM_HANDOFF.md) | Context for LLM sessions |
| [CHANGELOG.md](docs/CHANGELOG.md) | Version history |

---

## License

Private project - All rights reserved.

---

*Built with Claude AI assistance*
