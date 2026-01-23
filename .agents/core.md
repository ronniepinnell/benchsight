# BenchSight Core Rules

**Critical rules that are always loaded**

Last Updated: 2026-01-21

---

## Project Overview

BenchSight is a comprehensive hockey analytics platform for the NORAD Recreational League. The project consists of:

- **ETL Pipeline** (Python): Processes game data and generates 145 tables
- **Dashboard** (Next.js 14, TypeScript): Public-facing analytics dashboard
- **Tracker** (HTML/JS → Rust/Next.js): Game tracking application
- **Portal** (Next.js): Admin interface for ETL management
- **API** (FastAPI): Backend API for ETL and data operations

---

## Critical Rules

### Goal Counting (CRITICAL)

Goals are ONLY counted when:
```python
event_type == 'Goal' AND event_detail == 'Goal_Scored'
```

**NEVER** count:
- `event_type == 'Shot'` with `event_detail == 'Goal'` (this is a shot attempt)
- Any other combination

**Always use:**
```python
GOAL_FILTER = (
    (df['event_type'] == 'Goal') & 
    (df['event_detail'] == 'Goal_Scored')
)
```

### Single Source of Truth

- One canonical implementation per calculation
- No duplicated logic
- Use constants from `config/formulas.json` for formulas
- Reference `src/calculations/` modules for calculations

### Root-Level Solutions

- Fix actual problems, not symptoms
- Understand full data flow before making changes
- Avoid quick fixes that add complexity

---

## Code Standards

### Python

- **Style:** PEP 8
- **Type hints:** Required for all functions
- **Docstrings:** Google style for all functions
- **Line length:** Max 100 characters
- **Functions:** Max 300 lines
- **Files:** Max 1000 lines
- **Performance:** Use vectorized pandas operations, NEVER `.iterrows()`

### TypeScript/React

- **Style:** TypeScript strict mode
- **Components:** Server Components by default
- **Client Components:** Only when needed (interactivity, hooks)
- **Types:** Interfaces for all data structures
- **Async:** Use async/await, not promises
- **Naming:** camelCase for functions, PascalCase for components

---

## Naming Conventions

### Tables
- `dim_*` - Dimension tables
- `fact_*` - Fact tables
- `qa_*` - QA tables
- `lookup_*` - Lookup tables
- `v_*` - Views

### Python
- Functions: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Classes: `PascalCase`

### TypeScript
- Functions: `camelCase`
- Components: `PascalCase`
- Hooks: `use*`
- Types/Interfaces: `PascalCase`

---

## Performance Standards

- **ETL:** < 90 seconds for 4 games
- **Dashboard:** < 2 seconds page load
- **API:** < 200ms endpoint response
- **Optimization:** Profile before optimizing

---

## Documentation Requirements

- **Code:** Docstrings for all functions
- **New features:** Update relevant docs in `docs/`
- **Breaking changes:** Update `CHANGELOG.md`
- **API changes:** Update `docs/API_REFERENCE.md`

---

## Testing Requirements

- **Unit tests:** Required for calculation functions
- **Integration tests:** Required for ETL execution
- **Validation:** Run `python validate.py` after ETL changes
- **Location:** `tests/test_*.py`

---

## When Making Changes

1. **Understand the data flow** - Trace from source to destination
2. **Check existing patterns** - Follow established conventions
3. **Update documentation** - Keep docs in sync with code
4. **Run validation** - Ensure data integrity
5. **Test thoroughly** - Verify changes work correctly

---

## References

- **Complete Rules:** `docs/MASTER_RULES.md`
- **Roadmap:** `docs/MASTER_ROADMAP.md`
- **Status:** `docs/PROJECT_STATUS.md`
- **Modular Rules:** `.agents/README.md`

---

*Last Updated: 2026-01-15*
