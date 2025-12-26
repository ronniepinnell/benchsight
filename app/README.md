# BenchSight Hockey Analytics Platform
## Complete Project Package v1.0

**Generated: December 26, 2025**

---

## 🏒 Overview

BenchSight is an end-to-end hockey analytics platform that brings NHL-level analytics to beer league and junior hockey. This package contains the complete implementation including:

- **Python ETL Pipeline** - Extract, Transform, Load from tracking files
- **PostgreSQL Schema** - Complete database design
- **Interactive Portal** - Web-based dashboard and admin interface
- **Documentation** - Stats catalog, table catalog, LLM guides

---

## 📁 Project Structure

```
benchsight/
├── config/                 # Configuration settings
│   └── settings.py
├── data/
│   ├── raw/
│   │   ├── master/         # BenchSight_Tables.xlsx
│   │   └── games/          # Per-game tracking folders
│   │       ├── 18955/
│   │       ├── 18965/
│   │       ├── 18969/      # Platinum 4-3 Velodrome (9/7/2025)
│   │       ├── 18977/
│   │       ├── 18981/
│   │       ├── 18987/
│   │       ├── 18991/
│   │       ├── 18993/
│   │       └── 19032/
│   ├── processed/
│   │   ├── stage/          # Stage layer CSVs
│   │   ├── intermediate/   # Intermediate layer CSVs
│   │   └── mart/           # Mart layer CSVs
│   └── exports/            # Power BI exports
├── src/
│   └── etl/
│       ├── extract.py      # Data extraction
│       ├── transform.py    # Transformations
│       └── orchestrator.py # ETL runner
├── sql/
│   └── create_schema.sql   # PostgreSQL DDL
├── portal/
│   └── index.html          # Complete dashboard
├── docs/
│   ├── BENCHSIGHT_MASTER_STATUS.md
│   ├── catalogs/           # Stats & table catalogs
│   └── llm/                # LLM consultation guides
├── powerbi/                # Power BI templates
├── embed/                  # Wix embedding files
└── README.md               # This file
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install pandas openpyxl sqlalchemy psycopg2-binary
```

### 2. Run ETL Pipeline
```bash
cd src/etl
python orchestrator.py
```

### 3. View Dashboard
Open `portal/index.html` in a web browser.

### 4. Set Up PostgreSQL (Optional)
```bash
psql -U postgres -f sql/create_schema.sql
```

---

## 📊 Data Summary

### Tracked Games (9 Total)
| Game ID | Date | Matchup | Score | Events |
|---------|------|---------|-------|--------|
| 18955 | 2025-08-10 | Velodrome vs Orphans | 5-1 | CSV |
| 18965 | 2025-08-24 | Velodrome vs OS Offices | 2-4 | 3,999 |
| **18969** | **2025-09-07** | **Platinum vs Velodrome** | **4-3** | 3,596 |
| 18977 | 2025-09-14 | Velodrome vs HollowBrook | 4-2 | 2,527 |
| 18981 | 2025-09-28 | Nelson vs Velodrome | 2-1 | 2,428 |
| 18987 | 2025-10-05 | Outlaws vs Velodrome | 0-1 | 3,084 |
| 18991 | 2025-10-12 | Triple J vs Velodrome | 1-5 | 4,000 |
| 18993 | 2025-10-19 | Ace vs Velodrome | 1-2 | 456 |
| 19032 | TBD | TBD vs Velodrome | TBD | 3,999 |

**Total Events: ~24,089 | Total Shifts: ~868**

---

## 📈 Statistics Implemented

### Basic Stats
- Goals, Assists, Points, Shots on Goal
- Time on Ice (seconds/minutes)
- Plus/Minus

### Advanced Stats
- Corsi For/Against (CF%, CA%)
- Fenwick For/Against (FF%, FA%)
- Zone Entry/Exit Success Rates

### Micro Stats (BenchSight Unique)
- Possession Time (duration-based)
- True Giveaways (excludes dumps)
- Takeaways
- Pass Completion %
- Rating-Adjusted Metrics

---

## 🔧 Key Features

### Portal Dashboard
- ✅ Game selector with all 9 games
- ✅ Score display with team logos
- ✅ Period filters (P1/P2/P3)
- ✅ Scrollable event/shift logs
- ✅ Click-through drill-downs
- ✅ Privacy mode toggle
- ✅ Admin ETL runner

### ETL Pipeline
- ✅ Extract from Excel tracking files
- ✅ Stage layer with cleansing
- ✅ Intermediate layer with sequence/play indexing
- ✅ Mart layer with aggregations
- ✅ CSV export for Power BI

### Data Corrections Applied
- ✅ Game 18969: Platinum 4-3 Velodrome (was incorrect)
- ✅ BLB renamed to BenchSight throughout

---

## 🤖 LLM Consultation Guide

When consulting GPT/Gemini about this project:

1. Share `docs/BENCHSIGHT_MASTER_STATUS.md`
2. Share relevant catalog CSVs
3. Provide this context:
   - Hockey analytics for beer league
   - Manual tracking via Excel
   - Goal: NHL-level stats for recreational players

### Questions to Ask
- "What hockey analytics stats should I add?"
- "How would you implement an xG model?"
- "What's the best UI for real-time tracking?"

---

## 📋 Roadmap

### Completed ✅
- ETL pipeline architecture
- PostgreSQL schema
- Interactive portal
- 9 games loaded
- Basic/advanced stats

### In Progress 🔄
- Power BI integration
- Video sync improvements
- Rating-adjusted metrics

### Planned 📋
- Computer vision tracking
- xG/xPlay models
- Multi-tenant support
- Mobile app

---

## 🛠️ Troubleshooting

### Excel Import Errors
Ensure tracking files have standard column names. The ETL handles column name variations.

### Missing Team Logos
Team logos load from NORAD URLs. Check internet connection.

### Period Filters Not Working
Ensure events have period data populated. Check `event_start_running_sec` values.

---

## 📞 Support

This project is actively developed. For issues:
1. Check `docs/BENCHSIGHT_MASTER_STATUS.md` for known issues
2. Review ETL logs in `data/` directory
3. Consult LLM guides for implementation help

---

## 📜 License

This project is for personal/educational use. Commercial deployment requires additional licensing.

---

**BenchSight** - *Bringing NHL Analytics to Every Rink*
