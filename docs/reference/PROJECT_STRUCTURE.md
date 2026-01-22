# BenchSight Project Structure

**Complete project structure reference**

Last Updated: 2026-01-21
Version: 2.00

---

## Overview

This document provides a complete reference to the BenchSight project structure, including directory organization, file locations, and component architecture.

---

## Root Directory Structure

```
benchsight/
├── .claude/              # Claude AI configuration
│   └── settings.json     # Claude project rules
├── .cursorrules          # Cursor AI rules
├── api/                  # FastAPI backend
├── archive/              # Archived/deprecated code
├── config/               # Configuration files
├── data/                 # Data files (raw and output)
├── docs/                 # Documentation
├── logs/                 # Log files
├── scripts/              # Utility scripts
├── src/                  # ETL Python source code
├── sql/                  # SQL scripts and views
├── tests/                # Test files
├── ui/                   # Frontend applications
├── benchsight.sh         # Unified CLI
├── dev.sh                # Development helper script
├── run_etl.py            # ETL entry point
├── upload.py             # Supabase upload script
└── validate.py           # Validation script
```

---

## ETL Structure (`src/`)

```
src/
├── core/                 # Core ETL logic
│   ├── base_etl.py      # Main orchestrator (~1,065 lines)
│   ├── etl_phases/      # Modular phase implementations (~4,700 lines)
│   │   ├── utilities.py
│   │   ├── derived_columns.py
│   │   ├── validation.py
│   │   ├── event_enhancers.py
│   │   ├── shift_enhancers.py
│   │   ├── derived_event_tables.py
│   │   └── reference_tables.py
│   ├── data_loader.py   # Data loading functions
│   ├── key_utils.py     # Key generation utilities
│   └── table_writer.py  # Table writing utilities
├── tables/                # Table creation modules
│   ├── core_facts.py    # Core fact tables
│   ├── remaining_facts.py # Remaining fact tables
│   └── ...
├── calculations/         # Calculation modules
│   ├── goals.py         # Goal counting (CRITICAL)
│   ├── corsi.py         # Corsi calculations
│   └── ...
├── utils/                # Utility functions
│   ├── validation.py    # Validation utilities
│   └── ...
├── advanced/             # Advanced analytics
├── builders/             # Table builders
├── chains/               # Processing chains
├── data_quality/         # Data quality checks
├── formulas/             # Formula management
├── ingestion/            # Data ingestion
├── models/               # Data models
├── qa/                   # QA tables
├── supabase/             # Supabase utilities
├── transformation/       # Data transformation
└── xy/                   # XY coordinate processing
```

---

## API Structure (`api/`)

```
api/
├── routes/               # API endpoints
│   ├── etl.py          # ETL endpoints
│   ├── upload.py       # Upload endpoints
│   ├── staging.py      # Staging endpoints
│   ├── health.py       # Health check
│   └── ml.py           # ML endpoints (future)
├── services/            # Business logic
│   ├── etl_service.py  # ETL service
│   ├── job_manager.py  # Job management
│   └── supabase_service.py # Supabase service
├── models/              # Data models
│   └── job.py          # Job models
├── utils/               # Utilities
├── main.py              # FastAPI app entry point
├── config.py            # Configuration
└── requirements.txt     # Python dependencies
```

---

## Dashboard Structure (`ui/dashboard/`)

```
ui/dashboard/
├── src/
│   ├── app/             # Next.js app directory
│   │   ├── (dashboard)/ # Dashboard routes
│   │   │   ├── players/ # Player pages
│   │   │   ├── teams/   # Team pages
│   │   │   ├── games/   # Game pages
│   │   │   └── ...
│   │   ├── norad/       # NORAD-specific routes
│   │   ├── layout.tsx   # Root layout
│   │   └── page.tsx     # Home page
│   ├── components/       # React components
│   │   ├── charts/      # Chart components
│   │   ├── players/     # Player components
│   │   ├── teams/       # Team components
│   │   └── ui/          # UI components (shadcn)
│   ├── lib/             # Utilities and helpers
│   │   ├── supabase/    # Supabase clients
│   │   └── utils.ts     # Utility functions
│   └── styles/          # Styles
├── public/              # Static assets
├── package.json         # Node.js dependencies
└── .env.local          # Environment variables
```

---

## Tracker Structure (`ui/tracker/`)

```
ui/tracker/
├── tracker_index_v23.5.html  # Current HTML tracker (16,162 lines)
└── [Future Rust/Next.js structure]
    ├── src/
    │   ├── app/
    │   ├── components/
    │   └── lib/
    └── Cargo.toml
```

---

## Portal Structure (`ui/portal/`)

```
ui/portal/
├── index.html          # Current HTML mockup
└── [Future Next.js structure]
    ├── src/
    │   ├── app/
    │   ├── components/
    │   └── lib/
    └── package.json
```

---

## Documentation Structure (`docs/`)

```
docs/
├── MASTER_INDEX.md              # Documentation index
├── MASTER_ROADMAP.md            # Unified roadmap
├── MASTER_RULES.md              # Rules and standards
├── MASTER_NEXT_STEPS.md         # Next steps
├── MASTER_PROJECT_MANAGEMENT.md # Project management
├── PROJECT_STATUS.md            # Current status
├── PROJECT_SCOPE.md             # Project scope
├── PROJECT_STRUCTURE.md         # This file
├── archive/QUICK_START.md       # Quick start guide (archived)
├── COMMANDS.md                  # Command reference
├── DEVELOPMENT_WORKFLOW.md      # Development workflows
├── PROJECT_CHECKLIST.md         # Project checklist
├── MAINTENANCE_GUIDE.md         # Maintenance guide
├── ETL_*.md                     # ETL documentation
├── DASHBOARD_*.md               # Dashboard documentation
├── TRACKER_*.md                 # Tracker documentation
├── API_*.md                     # API documentation
├── PORTAL_*.md                  # Portal documentation
└── archive/                     # Archived documentation
```

---

## Configuration Files

### Root Level

- `.cursorrules` - Cursor AI rules
- `.claude/settings.json` - Claude AI settings
- `benchsight.sh` - Unified CLI
- `dev.sh` - Development helper
- `run_etl.py` - ETL entry point
- `upload.py` - Upload script
- `validate.py` - Validation script

### ETL Configuration (`config/`)

- `config.ini` - Base configuration
- `config_local.ini` - Local configuration (gitignored)
- `config_local.dev.ini` - Dev environment config
- `formulas.json` - Formula definitions
- `analytics_constants.yaml` - Analytics constants
- `VERSION.json` - Version information

### Dashboard Configuration (`ui/dashboard/`)

- `.env.local` - Environment variables (gitignored)
- `.env.local.dev` - Dev environment variables
- `package.json` - Node.js dependencies
- `next.config.js` - Next.js configuration
- `tailwind.config.js` - Tailwind configuration
- `tsconfig.json` - TypeScript configuration

### API Configuration (`api/`)

- `requirements.txt` - Python dependencies
- `.env` - Environment variables (gitignored)
- `config.py` - API configuration

---

## Data Files (`data/`)

```
data/
├── raw/                 # Raw input data
│   ├── BLB_Tables.xlsx # Master data file
│   └── games/          # Game tracking files
│       ├── 18969/      # Game 18969
│       │   └── 18969_tracking.xlsx
│       └── ...
└── output/             # ETL output (CSV files)
    ├── dim_*.csv       # Dimension tables
    ├── fact_*.csv      # Fact tables
    └── qa_*.csv        # QA tables
```

---

## Scripts (`scripts/`)

```
scripts/
├── switch_env.sh           # Environment switching
├── setup-supabase-dev.sh  # Supabase dev setup
├── setup-vercel-dev.sh    # Vercel dev setup
├── deploy_to_dev.sh       # Deploy to dev
├── deploy_to_production.sh # Deploy to production
└── ...                    # Other utility scripts
```

---

## SQL Files (`sql/`)

```
sql/
├── reset_supabase.sql     # Reset database
├── setup_supabase.sql     # Setup database
├── disable_rls.sql         # Disable RLS
├── fix_rls_policies.sql   # Fix RLS policies
└── views/                  # SQL views
    ├── 01_*.sql           # View files
    └── 99_DEPLOY_ALL_VIEWS.sql # Deploy all views
```

---

## Test Files (`tests/`)

```
tests/
├── test_*.py              # Unit tests
├── test_etl.py            # ETL integration tests
└── ...                    # Other test files
```

---

## File Organization Patterns

### Python Files

- **Modules:** `snake_case.py`
- **Classes:** `PascalCase`
- **Functions:** `snake_case()`
- **Constants:** `UPPER_SNAKE_CASE`

### TypeScript Files

- **Files:** `kebab-case.tsx` or `PascalCase.tsx`
- **Components:** `PascalCase.tsx`
- **Functions:** `camelCase()`
- **Types/Interfaces:** `PascalCase`

### Table Names

- **Dimensions:** `dim_*`
- **Facts:** `fact_*`
- **QA:** `qa_*`
- **Lookups:** `lookup_*`
- **Views:** `v_*`

---

## Key File Locations

### ETL Entry Points

- `run_etl.py` - Main ETL script
- `src/core/base_etl.py` - Core ETL logic
- `validate.py` - Validation script
- `upload.py` - Upload script

### Dashboard Entry Points

- `ui/dashboard/src/app/layout.tsx` - Root layout
- `ui/dashboard/src/app/page.tsx` - Home page
- `ui/dashboard/src/lib/supabase/client.ts` - Supabase client

### API Entry Points

- `api/main.py` - FastAPI app
- `api/routes/etl.py` - ETL endpoints
- `api/services/etl_service.py` - ETL service

### Documentation Entry Points

- `docs/MASTER_INDEX.md` - Documentation index
- `docs/archive/QUICK_START.md` - Quick start (archived)
- `README.md` - Root README

---

## Component Locations

### ETL Components

- **Core Logic:** `src/core/`
- **Table Creation:** `src/tables/`
- **Calculations:** `src/calculations/`
- **Utilities:** `src/utils/`

### Dashboard Components

- **Pages:** `ui/dashboard/src/app/`
- **Components:** `ui/dashboard/src/components/`
- **Utilities:** `ui/dashboard/src/lib/`

### API Components

- **Endpoints:** `api/routes/`
- **Services:** `api/services/`
- **Models:** `api/models/`

---

## Related Documentation

- [PROJECT_SCOPE.md](PROJECT_SCOPE.md) - Project scope
- [PROJECT_STATUS.md](PROJECT_STATUS.md) - Current status
- [MASTER_INDEX.md](MASTER_INDEX.md) - Documentation index
- [archive/QUICK_START.md](archive/QUICK_START.md) - Quick start guide (archived)

---

*Last Updated: 2026-01-15*
