# BenchSight v10 - Complete Package

## 🏒 Welcome to BenchSight

BenchSight is a hockey analytics platform for the NORAD recreational hockey league. This package contains everything needed to continue development.

---

## 📍 Start Here Based on Your Role

### I'm Setting Up the Database (Supabase)
```
GO TO: developer_handoffs/supabase_dev/README.md
```
- Deploy schema to Supabase PostgreSQL
- Load CSV data into tables
- Create indexes and validate

### I'm Building the Admin Portal
```
GO TO: developer_handoffs/portal_dev/README.md
```
- Build admin UI for ETL control
- Create table viewer/editor
- Monitoring and validation dashboard

### I'm Building Dashboards
```
GO TO: developer_handoffs/dashboard_dev/README.md
```
- Build visualization components
- Connect to Supabase
- Display stats and analytics

### I'm Working on the Game Tracker
```
GO TO: developer_handoffs/tracker_dev/README.md
```
- Fix existing tracker bugs
- Add new features
- Integrate with Supabase writes

### I'm Continuing General Development
```
GO TO: docs/handoff/MASTER_INSTRUCTIONS.md
```
- Project overview and business rules

---

## 📊 Current Project Status

| Component | Status | Notes |
|-----------|--------|-------|
| ETL Pipeline | ✅ 293 tests passing | Production ready |
| Data Dictionary | ✅ Complete | 11 CSV files, 317 columns |
| Supabase Schema | ⚠️ Needs deployment | SQL scripts ready |
| Admin Portal | 🔲 Not started | Specs complete |
| Game Tracker | ⚠️ Bugs to fix | Roster loading, event ordering |
| Dashboards | 🔲 Not started | Specs complete |

---

## 🔄 Development Workflow (4 Roles)

```
Week 1: SUPABASE         ← Foundation (MUST BE FIRST)
Week 2-3: PARALLEL       ← Portal + Tracker + Dashboard
Week 4: INTEGRATION      ← Connect everything
```

**See:** `developer_handoffs/DEVELOPER_WORKFLOW_4ROLES.md`

---

## 📁 Package Contents

```
benchsight_FINAL_v10/
├── START_HERE_V10.md                ← YOU ARE HERE
│
├── developer_handoffs/              ← ROLE-SPECIFIC GUIDES
│   ├── DEVELOPER_WORKFLOW_4ROLES.md ← Timeline for all 4 roles
│   ├── SUPABASE_WRITE_STRATEGY.md   ← Data flow architecture
│   ├── supabase_dev/                ← Database deployment
│   ├── portal_dev/                  ← Admin UI (NEW)
│   ├── dashboard_dev/               ← Visualization
│   └── tracker_dev/                 ← Game tracking
│
├── data/output/                     ← ETL output CSVs
│   └── data_dictionary/             ← Column definitions
│
├── docs/handoff/                    ← All documentation
├── src/, scripts/, tests/           ← ETL code
└── tracker/                         ← Tracker HTML files
```

---

## 🔑 Key Information

### Database
```
Supabase URL: https://uuaowslhpgyiudmbvqze.supabase.co
Tables: 12 (3 dimension, 9 fact)
Columns: 317 total
```

### Critical Business Rules
1. **player_role determines stat credit** - Only event_team_player_1 gets stats
2. **Shots = Corsi** - All shot attempts (60-70 per team is normal)
3. **Assists in play_detail1** - Look for 'AssistPrimary', 'AssistSecondary'

---

## 📋 Quick Commands

### Run ETL Pipeline
```bash
python etl.py
python scripts/fix_data_integrity.py
python scripts/fix_final_data.py
python scripts/etl_validation.py
pytest tests/
```

---

## 🆕 What's New in v10

- **4-Role Developer Workflow** - Supabase, Portal, Tracker, Dashboard
- **Portal Admin Handoff** - New role for admin UI development
- **Supabase Write Strategy** - How Tracker/Dashboard connect to DB
- **Updated Data Dictionaries** - All 11 files current
- **Complete ETL Fixes** - All scripts from latest session

---

*BenchSight v10 | December 2024*
