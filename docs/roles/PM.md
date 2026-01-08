# Role: Project Manager

**Version:** 16.08  
**Updated:** January 8, 2026


## Scope
Coordinate work, track status, plan features, manage documentation.

## First Steps
1. Read `CHANGELOG.md` for recent changes
2. Read `MASTER_GUIDE.md` for current state
3. Check `docs/html/index.html` in browser for overview
4. Review `config/VERSION.json` for version info

## Current State (v16.08)

| Metric | Value |
|--------|-------|
| Tables | 59 (33 dim, 24 fact, 2 QA) |
| Games Tracked | 4 |
| Goals Verified | 17 |
| Tier 1 Tests | 32 |
| Tier 2 Tests | 17 |

## Project Components

| Component | Status | Owner Role |
|-----------|--------|------------|
| ETL Core | ✅ Working | ETL Engineer |
| Safeguards | ✅ Complete | ETL Maintenance |
| Documentation | ✅ Auto-synced | Any |
| Supabase Schema | ✅ Ready | Backend Dev |
| Supabase Sync | 🔶 Ready to deploy | Backend Dev |
| UI Tracker | ❌ Not started | Tracker Dev |
| Dashboard | ❌ Not started | Dashboard Dev |
| Portal | ❌ Not started | Frontend Dev |

## Roadmap

### Phase 1: Data Infrastructure
- [x] ETL creates 59 tables
- [x] Safeguards prevent regression
- [x] Documentation auto-syncs
- [x] Supabase schema generated
- [ ] Deploy schema to Supabase
- [ ] Sync data to Supabase

### Phase 2: Tracker
- [ ] Design event entry UI
- [ ] Implement video timestamp
- [ ] Add auto-fill logic
- [ ] Test with real game

### Phase 3: Dashboard
- [ ] Player stats view
- [ ] Game summary view
- [ ] Team comparisons

### Phase 4: Portal
- [ ] Central hub UI
- [ ] ETL trigger button
- [ ] Status dashboard

## Handoff Process

When starting a new chat:
1. Upload latest `benchsight_vX.XX.zip`
2. Paste the appropriate role guide from `docs/roles/`
3. Describe the task
4. End with `python scripts/pre_delivery.py`

## Version Control

```bash
# After each delivery, on Mac:
cd ~/Projects/benchsight
unzip -o ~/Downloads/benchsight_vX.XX.zip
cp -r benchsight_vX.XX/* .
rm -rf benchsight_vX.XX
git add .
git commit -m "vX.XX: description"
```

## Quality Checks

Before accepting any delivery:
1. Version number incremented
2. All timestamps updated
3. CHANGELOG has entry
4. Tier 1 tests pass
5. Goal count still 17

## Risk Areas

| Risk | Mitigation |
|------|------------|
| LLM deletes code | Safeguards detect regressions |
| Wrong goal counts | Tier 1 tests block delivery |
| Outdated docs | Auto-sync fixes on each build |
| Schema drift | Schema snapshot comparison |

## Communication

When delegating to a role chat:
- Be specific about scope
- Reference exact files if possible
- Set clear success criteria
- Request verification output
