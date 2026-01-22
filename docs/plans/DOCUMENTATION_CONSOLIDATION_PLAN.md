# Documentation Consolidation & Roadmap Mapping Plan

> **Status:** In Progress
> **Created:** 2025-01-22
> **Source:** Claude Code planning session

## Summary

Consolidate overlapping documentation, fix inaccuracies, update master docs with new additions, and map GitHub issues to roadmap phases.

---

## Priority 1: Fix Critical Inaccuracies

### 1.1 Fix base_etl.py Line Count (was 4,400+, now ~1,065 due to modularization)
**Files to update:**
- `docs/etl/CODE_FLOW_ETL.md` - Change "4,400+ lines" to "~1,100 lines (refactored via etl_phases)"
- `docs/PROJECT_STATUS.md` - Update line count reference
- `CLAUDE.md` - Update "~4,400 lines" reference

### 1.2 Table Count
- Keep target as 139 tables (that's the spec)
- Issue #31 tracks investigation of why ETL produces 132 currently

### 1.3 Update Tracker Version (v27.0 docs, v28.0 code)
- `docs/tracker/TRACKER_REFERENCE.md` - Note v28.0 exists

---

## Priority 2: Dashboard Documentation Consolidation

**Current state:** 11 overlapping files
**Target state:** 2 files + archive

### Consolidation:
1. **Enhance `ui/dashboard/README.md`** - Merge START_HERE.md, NAVIGATE_HERE.md
2. **Consolidate `ui/dashboard/SETUP_GUIDE.md`** - Merge QUICK_START.md, HOW_TO_VIEW.md, INSTALL_NODE.md, VIEWING_PAGES.md, PROTOTYPING*.md

### Archive to `ui/dashboard/_archive/`:
- QUICK_START.md, HOW_TO_VIEW.md, INSTALL_NODE.md, VIEWING_PAGES.md
- PROTOTYPING.md, PROTOTYPING_WORKFLOW.md, PROTOTYPING_CHEATSHEET.md
- START_HERE.md, NAVIGATE_HERE.md

---

## Priority 3: Update MASTER_INDEX.md

### Add new workflow files:
- workflows/COMPLETE_DEVELOPMENT_GUIDE.md
- workflows/COMPLETE_INSTALLATION_GUIDE.md
- workflows/QUICKSTART_WORKFLOW.md
- workflows/DEVELOPMENT_REFERENCE.md
- workflows/RECOMMENDED_PLUGINS_AND_MCPS.md

### Add Skills section (29 skills):
| Category | Skills |
|----------|--------|
| Core Dev | etl, validate, dashboard-dev, portal-dev, tracker-dev, api-dev |
| Database | db-dev, db-prod, env-switch, schema-design |
| Quality | compliance-check, reality-check, post-code, pr-workflow |
| ML/Analytics | xg-model, ml-pipeline, cv-tracking, hockey-stats |
| AI/Advanced | cv (computer vision), rag (retrieval-augmented), text-to-query |

### Add Hooks section (6 hooks):
- bash-validator.py, goal-counting-guard.py, etl-failure-handler.py
- etl-integrity-check.py, post-etl-reminder.py, doc-update-reminder.py

### Add ETL Phases modules:
- utilities.py, derived_columns.py, validation.py
- event_enhancers.py, shift_enhancers.py
- derived_event_tables.py, reference_tables.py

---

## Priority 4: Map GitHub Issues to Roadmap

**Add to `docs/MASTER_ROADMAP.md`:**

### Phase 2 (Current) - 18 issues:
| Priority | Issues |
|----------|--------|
| P0 | #31 Missing 7 tables, #13 Goal counting, #3 Modularize ETL, #5 Vectorize |
| P1 | #4 Profile ETL, #6-8 Table verification, #25-29 Vectorization, #30 Remove wrapper |
| P2 | #9 Document unused tables, #16 Dead code, #32-34 Code quality |

### Phase 3 (Planned) - 12 issues:
| Priority | Issues |
|----------|--------|
| P1 | #10-12 Analytics validation (xG, WAR, Corsi) |
| P2 | #14 CI tests, #17-23 Debug infrastructure |

---

## Priority 5: Clarify CLAUDE.md Files

Add headers to distinguish:
- `/CLAUDE.md` - BenchSight project instructions
- `/.claude/CLAUDE.md` - Subagent collection docs (different purpose)

---

## Priority 6: Doc-Sync Automation

### Proposed: `doc-sync` Hook + Skill

**Trigger:** Pre-commit hook that detects changes and prompts for doc updates

**Docs to Auto-Update on Each Commit:**

| Doc File | Update When |
|----------|-------------|
| `docs/MASTER_INDEX.md` | New .md files added anywhere |
| `docs/PROJECT_STATUS.md` | Code changes to tracked components |
| `docs/etl/CODE_FLOW_ETL.md` | Changes to `src/core/` or `run_etl.py` |
| `docs/architecture/*.md` | Changes to corresponding component code |
| `CLAUDE.md` | New skills, hooks, or major workflow changes |
| `docs/tracker/TRACKER_REFERENCE.md` | Changes to `ui/tracker/` |
| `docs/data/DATA_DICTIONARY.md` | New tables or schema changes |

**Implementation Options:**

1. **Hook: `doc-sync-reminder.py`** (lightweight)
   - Runs pre-commit
   - Detects changed files, maps to affected docs
   - Warns if related docs weren't updated
   - User can proceed or abort to update

2. **Skill: `/doc-sync`** (comprehensive)
   - Runs on-demand or post-commit
   - Scans codebase for changes since last sync
   - Auto-generates doc updates for review
   - Updates line counts, file lists, version numbers

3. **Combined Approach** (recommended)
   - Hook warns at commit time
   - Skill does heavy lifting when invoked
   - `/doc-sync` can be called manually or by hook

**Files to Create:**
- `.claude/hooks/doc-sync-reminder.py` - Pre-commit reminder
- `.claude/skills/doc-sync/SKILL.md` - Doc sync skill definition
- `scripts/doc-sync.py` - Core logic for detecting stale docs

---

## Priority 7: GitHub Issues Gap Analysis

### Current State

**GitHub Issues Created:** 34 (33 open, 1 closed)
**Backlog Documented:** ~211 issues across 8 phases

### Issue Distribution by Phase

| Phase | Status | Documented | In GitHub | Gap |
|-------|--------|------------|-----------|-----|
| Phase 2: ETL Optimization | CURRENT | 40 | 34 | 6 |
| Phase 3: Dashboard Enhancement | PLANNED | 66 | 0 | 66 |
| Phase 4: Portal Development | PLANNED | 16 | 0 | 16 |
| Phase 5: Tracker Conversion | PLANNED | 12 | 0 | 12 |
| Phase 6: ML/CV + Advanced | PLANNED | 20 | 0 | 20 |
| Phase 7: Multi-Tenancy | PLANNED | 12 | 0 | 12 |
| Phase 8: Commercial Launch | PLANNED | 12 | 0 | 12 |
| Phase 9-12: AI Coaching | PLANNED | 20 | 0 | 20 |
| Foundation & Workflow | VARIOUS | 13 | 0 | 13 |
| **TOTAL** | | **~211** | **34** | **~177** |

### Issues Created in GitHub (34 total)

**ETL Phase 2 Issues (#3-#34):**
- #3: ETL-001 Modularize base_etl.py (COMPLETED in codebase)
- #4: ETL-002 Profile ETL bottlenecks
- #5: ETL-003 Replace .iterrows() (P0)
- #6: ETL-004 Create table verification script
- #7: ETL-005 Verify all 139 tables have data
- #8: ETL-006 Validate foreign key relationships
- #9: ETL-007 Identify unused tables
- #10: ETL-008 Validate xG calculations
- #11: ETL-009 Validate WAR/GAR calculations
- #12: ETL-010 Validate Corsi/Fenwick calculations
- #13: ETL-011 Verify goal counting (P0)
- #14: ETL-012 Add verification to CI
- #16: Remove dead code
- #17-23: ETL Debug infrastructure (Docker PostgreSQL)
- #24: Refactor .iterrows() violations (CLOSED)
- #25-29: Vectorize specific functions
- #30: Remove data_loader.py wrapper
- #31: Investigate missing 7 tables (P0)
- #32: Add type hints to etl_phases
- #33: Split long functions
- #34: Address pandas warnings

### Recommended Strategy: Create Issues Phase-by-Phase

**Step 1: Triage Existing Phase 2 Issues**
- Close #3 as complete (already done in code)
- Group issues by priority (P0, P1, P2)
- Identify dependencies and execution order

**Step 2: Create Missing Phase 2 P0/P1 Issues**
Create ~6 additional issues from backlog for Phase 2

**Step 3: Create Phase 3 P0/P1 Issues Only**
Create ~15-20 issues for Dashboard phase when Phase 2 nears completion

**Step 4: Update GitHub Project Board**
- Create milestones: M1 (Phase 2), M2 (Phase 3-4), M3 (Phase 5-6), M4 (Phase 7-8)
- Add labels if not already created
- Organize issues into milestone columns

---

## Verification Checklist

- [ ] All critical line counts fixed
- [ ] Dashboard docs consolidated
- [ ] MASTER_INDEX updated with new sections
- [ ] GitHub issues mapped to roadmap
- [ ] CLAUDE.md files clarified
- [ ] Doc-sync automation documented
- [ ] Gap analysis complete
- [ ] Missing Phase 2 issues created
- [ ] Issue #3 closed as complete
