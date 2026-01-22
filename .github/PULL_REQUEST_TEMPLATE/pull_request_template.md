## Summary

<!-- Brief description of changes (1-3 sentences) -->

## Type of Change

- [ ] `FEAT` - New feature
- [ ] `FIX` - Bug fix
- [ ] `REFACTOR` - Code restructuring
- [ ] `PERF` - Performance improvement
- [ ] `DOCS` - Documentation only
- [ ] `TEST` - Tests only
- [ ] `CHORE` - Maintenance

## Component

- [ ] ETL Pipeline (`src/`)
- [ ] Dashboard (`ui/dashboard/`)
- [ ] Tracker (`ui/tracker/`)
- [ ] Portal (`ui/portal/`)
- [ ] API (`api/`)
- [ ] Data/Schema
- [ ] Documentation
- [ ] Infrastructure

## Related Issues

<!-- Link issues this PR addresses -->
Closes #

## PRD Reference

<!-- Link PRD if applicable -->
- [ ] PRD exists: `docs/prds/...`
- [ ] N/A - No PRD needed

## Changes Made

<!-- Bullet list of specific changes -->
-
-
-

## Testing Performed

- [ ] Manual testing completed
- [ ] ETL validation passed (`./benchsight.sh etl validate`)
- [ ] Unit tests pass (`pytest`)
- [ ] No regressions introduced
- [ ] Dashboard loads correctly

## Checklist

### Code Quality
- [ ] Code follows [MASTER_RULES.md](docs/MASTER_RULES.md)
- [ ] No `.iterrows()` usage (ETL code)
- [ ] Goal counting uses correct filter (if applicable)
- [ ] Type hints added (Python)
- [ ] TypeScript strict mode passes

### Documentation
- [ ] Documentation updated for user-visible changes
- [ ] API docs updated (if API changes)
- [ ] Code comments added for complex logic

### Safety
- [ ] No secrets committed
- [ ] No breaking changes (or documented if intentional)
- [ ] Data integrity maintained

## Screenshots/Demos

<!-- If UI changes, add screenshots -->

## Notes for Reviewers

<!-- Any context that helps review -->
