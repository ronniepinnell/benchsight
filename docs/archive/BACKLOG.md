# BenchSight Backlog

## Priority Legend
- 🔴 P0: Blocking - must fix before anything else
- 🟠 P1: High - needed for MVP
- 🟡 P2: Medium - important but not blocking
- 🟢 P3: Low - nice to have

---

## Phase 2 (Next Session)

| ID | Priority | Task | Notes |
|----|----------|------|-------|
| B001 | 🟠 P1 | Implement Plus/Minus stats | Rules documented in VALIDATION_LOG.tsv |
| B002 | 🟠 P1 | Implement Corsi/Fenwick | Via shift_index matching |
| B003 | 🟠 P1 | Implement remaining 72 stats | See skipped tests in validate_stats.py |
| B004 | 🟡 P2 | Fix tracker (consolidate v16-v19) | Multiple broken versions |
| B005 | 🟡 P2 | Add games 18965, 18991, 19032 | Need to verify data completeness first |
| B006 | 🟡 P2 | Full Supabase integration testing | After upload works |
| B007 | 🟡 P2 | Build automated NORAD cross-check | Scrape and compare |
| B008 | 🟢 P3 | Verbiage normalization for older games | Different event_detail values |
| B009 | 🟢 P3 | xG model integration | Expected goals from shot location |
| B010 | 🟢 P3 | Video URL integration | YouTube links from timestamps |

---

## Known Issues

| ID | Severity | Issue | Discovered |
|----|----------|-------|------------|
| I001 | Medium | Tipped goals - scorer appears as player_2 | 2024-12-28 |
| I002 | Medium | Some games have fewer goals than NORAD | 2024-12-28 |
| I003 | Low | Older games use different event_detail values | 2024-12-28 |

---

## Completed

| ID | Task | Completed | Session |
|----|------|-----------|---------|
| | | | |

---

*Last updated: 2024-12-29*
