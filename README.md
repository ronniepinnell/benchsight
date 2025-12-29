# BenchSight Hockey Analytics Platform

## Status: 98% Complete | 131 Tests Passing | 100% Goal Accuracy

A comprehensive hockey analytics ETL pipeline for the NORAD recreational hockey league.

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install pandas numpy openpyxl xlrd

# Run full ETL pipeline
python etl.py
python src/etl_orchestrator.py --all
python src/enhance_all_stats.py
python scripts/build_qa_facts.py

# Validate
python scripts/qa_dynamic.py
```

---

## 📊 What's Included

| Component | Count | Description |
|-----------|-------|-------------|
| **Stat Columns** | 317 | Per player-game |
| **Tables** | 45 | 25 dim + 17 fact + 3 QA |
| **Validation Tests** | 131 | All passing |
| **Games Loaded** | 4 | Verified against official |

---

## 📁 Key Documentation

| Document | Purpose |
|----------|---------|
| `docs/handoff/COMPLETE_HANDOFF.md` | Full project overview |
| `docs/handoff/NEXT_SESSION_PROMPT.md` | Prompt for next chat |
| `docs/handoff/HONEST_ASSESSMENT.md` | Status report |
| `docs/handoff/GOALS_ROADMAP.md` | Short/mid/long-term goals |
| `docs/diagrams/SCHEMA_DIAGRAM.md` | Database ERD |
| `docs/diagrams/ETL_FLOW.md` | Pipeline flow |
| `docs/diagrams/ARCHITECTURE.md` | System architecture |
| `docs/diagrams/DIAGRAMS_PREVIEW.html` | Visual diagrams (open in browser) |

---

## ✅ Goal Verification

All goals verified against noradhockey.com:

| Game | Official | Ours | Status |
|------|----------|------|--------|
| 18969 | 7 | 7 | ✅ |
| 18977 | 6 | 6 | ✅ |
| 18981 | 3 | 3 | ✅ |
| 18987 | 1 | 1 | ✅ |
| **Total** | **17** | **17** | **100%** |

---

## 🎯 Next Step: Supabase Deployment

DDL ready in `sql/01_create_tables_generated.sql`

1. Create Supabase project
2. Run DDL to create tables
3. Import CSVs from `data/output/`
4. Verify row counts

---

## 📈 Stats Categories

- **Scoring**: Goals, assists, points, shooting %
- **Possession**: Corsi, Fenwick, CF%, FF%
- **Time**: TOI, shift counts, avg shift length
- **Faceoffs**: Wins, losses, %, by zone
- **Advanced**: Game score, xG, rating adjustments
- **Per-60**: All stats normalized to 60 minutes

---

## 🔧 Tech Stack

- Python 3.12 + pandas
- Supabase (PostgreSQL)
- Power BI / HTML dashboards

---

## 📞 Contact

Project Owner: Ronnie (NORAD League)

---

*BenchSight - NHL-caliber analytics for beer league hockey*
