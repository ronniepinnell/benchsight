# Documentation Consolidation Plan

**Files that can be combined or consolidated**

Last Updated: 2026-01-15

---

## Consolidation Opportunities

### 1. environments/ - Merge 4 files into ENVIRONMENTS.md
- BRANCH_STRATEGY_QUICK_REFERENCE.md → Merge into ENVIRONMENTS.md
- BRANCHES_AND_SUPABASE.md → Merge into ENVIRONMENTS.md  
- ENVIRONMENT_MAPPING.md → Merge into ENVIRONMENTS.md
- ENVIRONMENT_VARIABLES_EXPLAINED.md → Merge into ENVIRONMENTS.md
- **Result:** 1 file instead of 5

### 2. setup/ - Consolidate setup guides
- QUICK_START.md + SETUP.md → One SETUP.md with quick start section
- DEV_ENV_COMPLETE.md, DEV_ENV_SUPABASE.md, DEV_ENV_VERCEL.md → Sections in SETUP.md
- COMPLETE_SETUP_GUIDE.md → Archive (redundant)
- **Result:** 1 file instead of 6

### 3. workflows/ - Merge workflow guides
- DEVELOPMENT_WORKFLOW.md + COMPLETE_WORKFLOW_GUIDE.md → One WORKFLOW.md
- Keep others separate (they're specialized)
- **Result:** 6 files instead of 7

### 4. tracker/ - Consolidate tracker docs
- TRACKER_COMPLETE_LOGIC.md + TRACKER_STATE_MANAGEMENT.md + TRACKER_EVENT_FLOW.md → TRACKER_REFERENCE.md
- TRACKER_CONVERSION_SPEC.md + TRACKER_CONVERSION_ROADMAP.md + TRACKER_RUST_PLAN.md + TRACKER_ARCHITECTURE_PLAN.md → TRACKER_CONVERSION.md
- Keep specialized docs (VIDEO_INTEGRATION, XY_POSITIONING, EXPORT_FORMAT, DROPDOWN_MAP, FEATURE_INVENTORY)
- **Result:** 7 files instead of 12

### 5. api/ - Merge into one guide
- API_ARCHITECTURE.md + API_INTEGRATION.md + API_REFERENCE.md → API.md
- **Result:** 1 file instead of 3

### 6. portal/ - Merge into one guide
- PORTAL_CURRENT_STATE.md + PORTAL_DEVELOPMENT_PLAN.md + PORTAL_API_REQUIREMENTS.md + ADMIN_PORTAL_SPEC.md → PORTAL.md
- **Result:** 1 file instead of 4

### 7. data/ - Merge into one guide
- DATA_LINEAGE.md + TABLE_MANIFEST.md → DATA.md
- **Result:** 1 file instead of 2

### 8. checklists/ - Merge all checklists
- Merge all checklist files into CHECKLISTS.md
- **Result:** 1 file instead of 5

---

## Total Reduction

**Before:** 56 files in folders  
**After:** ~25 files in folders  
**Reduction:** ~55% fewer files

---

*Last Updated: 2026-01-15*
