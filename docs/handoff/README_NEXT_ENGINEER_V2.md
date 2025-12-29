# README FOR NEXT ENGINEER
## BenchSight Hockey Analytics

---

## TL;DR

You're inheriting a **working hockey analytics ETL pipeline**. It processes game tracking data from Excel files into a dimensional data model with 77 CSV tables. The core is complete, validations pass, and it's ready for Supabase deployment.

**Start here:** Read `docs/handoff/HANDOFF_COMPLETE_V2.md`

---

## 5-Minute Orientation

### What This Is
- Hockey analytics for NORAD recreational league
- ETL pipeline: Excel → Python → CSV → Supabase
- 40 dimension tables + 37 fact tables
- Star schema design with 12-character primary keys

### What Works
✅ Full ETL pipeline (runs in ~20 seconds)  
✅ All stat calculations (goals, TOI, Corsi, H2H, etc.)  
✅ FK population with fuzzy matching (77.8% fill)  
✅ 54 validation tests (all passing)  
✅ Documentation and diagrams  

### What's Next
❌ Supabase deployment (DDL ready, not executed)  
❌ More test games (4 of 10 tracked)  
❌ xG model (not started)  
❌ Real-time tracker backend  

---

## Quick Commands

```bash
# Run everything
cd benchsight_combined
python -m src.etl_orchestrator      # ETL
python src/populate_all_fks_v2.py   # FK population
python scripts/test_validations.py   # Validate

# Expected output
# ETL: ~20s, 16 tables, 0 errors
# FK: ~170k FKs populated
# Validation: 54 passed, 0 failed
```

---

## Key Files

| Purpose | File |
|---------|------|
| Start reading | `docs/handoff/HANDOFF_COMPLETE_V2.md` |
| Honest status | `docs/handoff/HONEST_ASSESSMENT_V2.md` |
| Gap analysis | `docs/handoff/GAP_ANALYSIS_V2.md` |
| Schema details | `docs/SCHEMA.md` |
| Stat formulas | `docs/STAT_DEFINITIONS.md` |
| Main ETL | `src/etl_orchestrator.py` |
| FK script | `src/populate_all_fks_v2.py` |
| Tests | `scripts/test_validations.py` |
| Supabase DDL | `sql/01_create_tables_generated.sql` |

---

## Project Structure

```
benchsight_combined/
├── src/                    # Python ETL code
├── data/
│   ├── raw/games/          # Source Excel files
│   └── output/             # Generated CSVs (dim_* + fact_*)
├── scripts/                # Validation and utilities
├── docs/                   # Documentation
│   └── handoff/            # 👈 START HERE
├── sql/                    # Supabase DDL
└── tracker/                # HTML game tracker app
```

---

## Domain Knowledge

### Primary Keys
- `P100001` = Player
- `TM00001` = Team  
- `ET0001` = Event Type
- All 12 characters for consistency

### Key Rules
- `event_player_1` (first row per event) = primary player
- `'s'` = successful, `'u'` = unsuccessful
- Goals: `event_type="Goal"` OR `event_detail` contains "Shot Goal"

### Test Games
Currently tracked: 18969, 18977, 18987, 18981

---

## Common Tasks

### Deploy to Supabase
1. Open Supabase SQL editor
2. Run `sql/01_create_tables_generated.sql`
3. Run `python src/supabase_upload_v3.py`
4. Verify row counts match

### Add New Game
1. Create `data/raw/games/XXXXX/`
2. Add `XXXXX_tracking.xlsx`
3. Run ETL + FK population
4. Validate

### Fix FK Issues
1. Check unmapped values in FK population output
2. Add to dim table's `potential_values` or `old_equiv` column
3. Re-run `populate_all_fks_v2.py`

---

## Contact

- **User:** Ronnie (SQL Server expert)
- **Data Source:** noradhockey.com
- **Video:** YouTube channel

---

## LLM Session Tips

If you're an LLM picking this up:

1. Read the handoff docs in `docs/handoff/` first
2. Check `scripts/test_validations.py` for validation rules
3. The ETL is modular - check `src/etl_orchestrator.py`
4. FK matching uses fuzzy logic - see `src/populate_all_fks_v2.py`
5. Always run validations after changes
6. Package with updated docs before delivery

**Memory notes:**
- Always provide complete project zip
- Verify goals match noradhockey.com
- Run verify_delivery.py before packaging

---

*Last Updated: December 29, 2024*
