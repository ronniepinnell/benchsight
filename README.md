# BenchSight

**Hockey Analytics Platform for NORAD Recreational League**

[![Status](https://img.shields.io/badge/status-70%25%20complete-yellow)]()
[![Version](https://img.shields.io/badge/version-29.0-blue)]()
[![CodeRabbit](https://img.shields.io/badge/CodeRabbit-enabled-green)]()
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-enabled-green)]()

---

## Quick Start

Get up and running in 5 minutes:

```bash
# Run ETL pipeline
./benchsight.sh etl run

# Start dashboard
./benchsight.sh dashboard dev

# Check project status
./benchsight.sh status
```

**Full Quick Start:** See [docs/QUICK_START.md](docs/QUICK_START.md)

---

## Overview

BenchSight is a comprehensive hockey analytics platform that processes game data, generates advanced statistics, and provides a public-facing dashboard for analytics consumption.

### Components

- **ETL Pipeline** - Processes game data and generates 139 tables
- **Dashboard** - Public-facing analytics dashboard (50+ pages)
- **Tracker** - Game tracking application (HTML/JS → Rust/Next.js)
- **Portal** - Admin interface for ETL management
- **API** - Backend API for ETL and data operations

### Current Status

- **ETL:** ✅ Functional (90% complete)
- **Dashboard:** ✅ Functional (85% complete)
- **Tracker:** ✅ Functional (100% current version)
- **Portal:** 🚧 UI Only (10% complete)
- **API:** ✅ Functional (80% complete)

**Detailed Status:** See [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md)

---

## Development Workflow

### PRD-First Development

**Document before coding:**
```bash
./benchsight.sh prd create feature feature-name
```

**Planning workflow:**
1. Create PRD
2. Plan and design
3. Reset context
4. Implement with PRD reference

**See:** [docs/PLANNING_WORKFLOW.md](docs/PLANNING_WORKFLOW.md)

### GitHub Integration

- **Issue Templates:** Bug reports, feature requests, questions, refactors
- **PR Template:** Checklist and PRD reference
- **CI/CD:** Automated tests and code quality checks
- **CodeRabbit:** AI-powered code reviews

**See:** [docs/CODERABBIT_WORKFLOW.md](docs/CODERABBIT_WORKFLOW.md)

---

## Commands

### Unified CLI

Use `benchsight.sh` for all operations:

```bash
# ETL
./benchsight.sh etl run
./benchsight.sh etl validate
./benchsight.sh etl status

# Dashboard
./benchsight.sh dashboard dev
./benchsight.sh dashboard build
./benchsight.sh dashboard deploy

# API
./benchsight.sh api dev
./benchsight.sh api test

# Database
./benchsight.sh db upload
./benchsight.sh db schema

# Environment
./benchsight.sh env switch dev
./benchsight.sh env status

# Project
./benchsight.sh status
./benchsight.sh docs
./benchsight.sh help
```

**Complete Command Reference:** See [docs/COMMANDS.md](docs/COMMANDS.md)

---

## Project Structure

```
benchsight/
├── src/              # ETL Python code
├── api/              # FastAPI backend
├── ui/               # Frontend applications
│   ├── dashboard/    # Next.js dashboard
│   ├── tracker/      # HTML tracker
│   └── portal/       # Admin portal
├── docs/             # Documentation
├── scripts/          # Utility scripts
└── data/             # Data files
```

**Complete Structure:** See [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)

---

## Documentation

### Getting Started

- [Quick Start Guide](docs/QUICK_START.md) - Get running in 5 minutes
- [Setup Guide](docs/SETUP.md) - Complete installation
- [Development Workflow](docs/DEVELOPMENT_WORKFLOW.md) - Development workflows

### Project Documentation

- [Master Index](docs/MASTER_INDEX.md) - All documentation
- [Project Status](docs/PROJECT_STATUS.md) - Current status
- [Project Scope](docs/PROJECT_SCOPE.md) - Project scope
- [Master Roadmap](docs/MASTER_ROADMAP.md) - Project roadmap
- [Master Rules](docs/MASTER_RULES.md) - Rules and standards

### Component Documentation

- [ETL Documentation](docs/ETL_ARCHITECTURE.md) - ETL system
- [Dashboard Documentation](docs/DASHBOARD_ARCHITECTURE.md) - Dashboard system
- [Tracker Documentation](docs/TRACKER_COMPLETE_LOGIC.md) - Tracker logic
- [API Documentation](docs/API_REFERENCE.md) - API reference
- [Portal Documentation](docs/PORTAL_CURRENT_STATE.md) - Portal status

---

## Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- Supabase account
- Vercel account (for dashboard)

### Setup

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd benchsight
   ```

2. **Set up ETL**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Dashboard**
   ```bash
   cd ui/dashboard
   npm install
   ```

4. **Set up API**
   ```bash
   cd api
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Configure environments**
   ```bash
   ./scripts/setup-supabase-dev.sh
   ./scripts/setup-vercel-dev.sh
   ```

**Complete Setup:** See [docs/DEV_ENV_COMPLETE.md](docs/DEV_ENV_COMPLETE.md)

### Development Workflow

```bash
# Start dashboard (Terminal 1)
./benchsight.sh dashboard dev

# Run ETL (Terminal 2, when needed)
./benchsight.sh etl run

# Start API (Terminal 3, when needed)
./benchsight.sh api dev
```

**Development Guide:** See [docs/DEVELOPMENT_WORKFLOW.md](docs/DEVELOPMENT_WORKFLOW.md)

---

## Features

### ETL Pipeline

- ✅ 139 tables generated (dimensions, facts, QA)
- ✅ Comprehensive stats (317 columns for players, 128 for goalies)
- ✅ Advanced metrics (Corsi, Fenwick, xG, WAR/GAR, QoC/QoT)
- ✅ Data validation framework
- ✅ Formula management system

### Dashboard

- ✅ 50+ pages (players, teams, games, goalies, standings, leaders)
- ✅ Season and game type filtering
- ✅ Historical data support
- ✅ Enhanced visualizations (shot maps, charts)
- ✅ Responsive design

### Tracker

- ✅ Event tracking (15+ event types)
- ✅ Shift tracking
- ✅ Video integration (HTML5, YouTube)
- ✅ XY positioning on rink
- ✅ Export to Excel

### API

- ✅ ETL endpoints (trigger, status, history)
- ✅ Upload endpoints (tables, schema)
- ✅ Staging endpoints (BLB, tracking)
- ✅ Background job processing

---

## Roadmap

### Current Phase: Pre-Deployment & Data Collection

- 🚧 ETL cleanup and optimization
- 🚧 Dashboard enhancements
- 🚧 Portal API integration
- 📋 Documentation completion

### Next Phase: Advanced Analytics

- 📋 Complete xG analysis
- 📋 Complete WAR/GAR analysis
- 📋 RAPM analysis
- 📋 ML feature engineering

### Future Phases

- 📋 Production deployment
- 📋 ML/CV integration
- 📋 Multi-tenancy
- 📋 Commercial launch

**Complete Roadmap:** See [docs/MASTER_ROADMAP.md](docs/MASTER_ROADMAP.md)

---

## Contributing

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for:
- Code standards
- Development workflow
- Pull request process
- Testing guidelines

---

## Support

- **Documentation:** See [docs/MASTER_INDEX.md](docs/MASTER_INDEX.md)
- **Quick Start:** See [docs/QUICK_START.md](docs/QUICK_START.md)
- **Status:** See [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md)
- **Maintenance:** See [docs/MAINTENANCE_GUIDE.md](docs/MAINTENANCE_GUIDE.md)

---

## License

[Add license information]

---

**BenchSight v29.0 - NORAD Hockey Analytics**

*Last Updated: 2026-01-15*
