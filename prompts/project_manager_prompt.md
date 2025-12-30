# Claude Prompt: Project Manager

Copy this entire prompt when starting a new Claude chat for Project Management.

---

## Context

I'm the Project Manager for BenchSight, a hockey analytics platform for the NORAD recreational hockey league.

## Current State

- **Overall:** 85% production ready
- **Database:** Complete (96 tables, Supabase)
- **ETL:** Working (4 games processed)
- **Apps:** Prototypes only (Tracker, Dashboard, Portal)

## Team Roles
- DB Admin/Portal Dev - Build admin interface (not started)
- Dashboard Dev - Build analytics dashboards (prototype)
- Tracker Dev - Build game tracking interface (prototype)
- Data Engineer - ETL and data quality (complete)

## What's Done ✅
- Database schema (96 tables)
- ETL pipeline (raw → CSV → Supabase)
- Comprehensive logging
- 326 tests passing
- 4 games fully tracked and validated
- Developer handoffs

## What's Not Done ❌
- Production tracker with Supabase integration
- Production dashboard with live data
- Admin portal
- Video playback integration
- User authentication
- Additional games

## Recommended Timeline
- Sprint 1 (2 weeks): Get all apps functional
- Sprint 2 (2 weeks): Core features complete
- Sprint 3 (2 weeks): Production ready

## What I Need Help With

[Describe your specific question here]

## Files Available
- Full handoff: `docs/handoffs/PROJECT_MANAGER_HANDOFF.md`
- Project status: `docs/PROJECT_STATUS.md`
- All developer handoffs in `docs/handoffs/`
