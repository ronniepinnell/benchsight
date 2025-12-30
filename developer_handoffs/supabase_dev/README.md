# Supabase Developer Handoff

## ⚠️ CRITICAL: Start Here

**18 tables have schema mismatches that are blocking all frontend work.**

Read `SUPABASE_SCHEMA_ISSUES.md` FIRST.

---

## Your Priority Tasks

| Priority | Task | Document |
|----------|------|----------|
| 🔴 **P0** | Fix 15 schema mismatches | `SUPABASE_SCHEMA_ISSUES.md` |
| 🔴 **P0** | Add video highlight tables | `sql/04_VIDEO_HIGHLIGHTS.sql` |
| 🔴 **P0** | Fix fact_game_status constraint | `SUPABASE_SCHEMA_ISSUES.md` |
| 🟡 **P1** | Verify all 98 tables load | `bulletproof_loader.py --status` |
| 🟢 **P2** | Add Row Level Security | Future |

---

## Reading Order

1. **`SUPABASE_SCHEMA_ISSUES.md`** - Current blockers (30 min)
2. **`DEPLOYMENT_GUIDE.md`** - How deployment works (30 min)
3. **`sql/01_CREATE_ALL_TABLES.sql`** - Full schema reference
4. **`sql/04_VIDEO_HIGHLIGHTS.sql`** - Video tables to add
5. **`scripts/bulletproof_loader.py`** - The loader script

---

## Quick Commands

```bash
# Check what's in Supabase vs CSVs
python scripts/bulletproof_loader.py --status

# See which tables are empty/missing
python scripts/bulletproof_loader.py --missing

# Load only missing tables
python scripts/bulletproof_loader.py --load missing

# Load specific table
python scripts/bulletproof_loader.py --table dim_player --mode replace
```

---

## Success Criteria

You're done when:

```bash
python scripts/bulletproof_loader.py --load all --mode upsert
# Shows: Tables: 98/98 successful, Failed: 0
```

---

## Files in This Package

| File | Purpose |
|------|---------|
| `SUPABASE_SCHEMA_ISSUES.md` | **START HERE** - Current blockers |
| `DEPLOYMENT_GUIDE.md` | Deployment process |
| `README.md` | This file |
| `NEXT_PROMPT.md` | Claude session prompt |
