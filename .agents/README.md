# BenchSight Agent Rules - Modular Architecture

**On-demand context loading for efficient AI assistance**

Last Updated: 2026-01-15

---

## Overview

This directory contains modular rules organized by concern. Rules are loaded on-demand based on context, keeping conversations lean and focused.

**Principle:** Split by concern, load only what's relevant.

---

## Structure

```
.agents/
├── README.md              # This file - rules index
├── core.md                # Core rules (always loaded)
└── reference/             # On-demand context
    ├── etl.md            # ETL-specific rules
    ├── dashboard.md      # Dashboard-specific rules
    ├── api.md            # API-specific rules
    ├── tracker.md        # Tracker-specific rules
    ├── portal.md         # Portal-specific rules
    ├── data.md           # Data/validation rules
    ├── testing.md        # Testing rules
    ├── deployment.md     # Deployment rules
    └── git.md            # Git workflow rules
```

---

## Loading Strategy

### Automatic Loading

**Cursor AI automatically loads:**
- `core.md` - Always loaded (critical rules)
- Context-based files based on files you're editing

### Manual Loading

**In comments, reference specific files:**
```markdown
<!-- Load: reference/etl.md -->
<!-- Load: reference/dashboard.md -->
```

**In conversation, mention:**
```
Please reference .agents/reference/etl.md for ETL patterns
```

---

## Core Rules (Always Loaded)

**File:** `core.md`

**Contains:**
- Critical rules (goal counting, single source of truth)
- Project overview
- Code standards basics
- Naming conventions

**Always loaded** - These are fundamental to the project.

---

## Reference Rules (On-Demand)

### ETL Rules (`reference/etl.md`)

**Load when working on:**
- `src/` Python code
- `run_etl.py`
- `validate.py`
- ETL calculations

**Contains:**
- ETL patterns
- Table creation patterns
- Calculation patterns
- Performance requirements

### Dashboard Rules (`reference/dashboard.md`)

**Load when working on:**
- `ui/dashboard/` code
- Next.js components
- TypeScript/React code

**Contains:**
- Component patterns
- Data fetching patterns
- Supabase client usage
- UI/UX guidelines

### API Rules (`reference/api.md`)

**Load when working on:**
- `api/` code
- FastAPI endpoints
- API services

**Contains:**
- Endpoint patterns
- Error handling
- Request/response patterns
- Authentication

### Tracker Rules (`reference/tracker.md`)

**Load when working on:**
- `ui/tracker/` code
- Tracker conversion
- Game tracking logic

**Contains:**
- Tracker patterns
- Event tracking logic
- State management
- Export patterns

### Portal Rules (`reference/portal.md`)

**Load when working on:**
- `ui/portal/` code
- Admin interface
- ETL management UI

**Contains:**
- Portal patterns
- Admin UI patterns
- ETL control patterns

### Data Rules (`reference/data.md`)

**Load when working on:**
- Data validation
- Schema changes
- Data quality
- Database operations

**Contains:**
- Validation patterns
- Schema rules
- Data quality standards
- Type consistency

### Testing Rules (`reference/testing.md`)

**Load when working on:**
- `tests/` code
- Test creation
- Test maintenance

**Contains:**
- Test patterns
- Testing requirements
- Test organization

### Deployment Rules (`reference/deployment.md`)

**Load when working on:**
- Deployment scripts
- CI/CD
- Environment setup

**Contains:**
- Deployment patterns
- Environment management
- CI/CD requirements

### Git Rules (`reference/git.md`)

**Load when working on:**
- Git operations
- Branch management
- Commit messages

**Contains:**
- Git workflow
- Commit message format
- Branch naming
- PR process

---

## Usage Examples

### Example 1: Working on ETL

**Files:** `src/tables/player_stats.py`

**Auto-loaded:**
- `core.md` (always)
- `reference/etl.md` (context-based)

**Manual load if needed:**
```
<!-- Load: reference/data.md -->
```

### Example 2: Working on Dashboard

**Files:** `ui/dashboard/src/app/players/page.tsx`

**Auto-loaded:**
- `core.md` (always)
- `reference/dashboard.md` (context-based)

### Example 3: Working on API Integration

**Files:** `api/routes/etl.py`

**Auto-loaded:**
- `core.md` (always)
- `reference/api.md` (context-based)

**Manual load if needed:**
```
<!-- Load: reference/etl.md -->
<!-- Load: reference/testing.md -->
```

---

## Best Practices

### ✅ Do:

- Let Cursor auto-load based on context
- Manually load additional files when needed
- Reference specific files in comments
- Keep rules modular and focused

### ❌ Don't:

- Load all files at once
- Duplicate rules across files
- Put everything in core.md
- Mix concerns in one file

---

## Updating Rules

### When to Update

- **Bug occurs** → Add rule to prevent recurrence
- **Pattern emerges** → Document in relevant file
- **Best practice identified** → Add to appropriate file

### How to Update

1. Identify which file to update
2. Add rule/pattern to that file
3. Update this README if structure changes
4. Document in `docs/system-evolution/`

---

## Related Documentation

- `.cursorrules` - Main rules file (references this structure)
- `docs/MASTER_RULES.md` - Complete rules reference
- `docs/SYSTEM_EVOLUTION_WORKFLOW.md` - How rules evolve

---

*Last Updated: 2026-01-15*
