# Git Rules

**Git workflow and commit patterns**

Last Updated: 2026-01-21

---

## Git Workflow

### Branch Strategy

- **main** - Production
- **develop** - Development
- **feature/*** - Features
- **fix/*** - Bug fixes
- **hotfix/*** - Urgent production fixes

### Branch Naming

```bash
feature/add-player-ratings
fix/goal-counting-bug
hotfix/critical-security
docs/update-readme
refactor/cleanup-stats
```

---

## Commit Messages

### Format

```
[TYPE] Brief description

Optional longer description
```

### Types

- `[FEAT]` - New feature
- `[FIX]` - Bug fix
- `[DOCS]` - Documentation
- `[REFACTOR]` - Code refactoring
- `[TEST]` - Tests
- `[DEPLOY]` - Deployment

### Examples

```
[FEAT] Add player ratings calculation
[FIX] Correct goal counting filter
[DOCS] Update setup instructions
[REFACTOR] Extract common filtering logic
```

---

## Pull Request Process

### PR Checklist

- [ ] Code follows standards
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] CodeRabbit feedback addressed

### PR Description

- Clear description
- Related issues
- PRD reference (if applicable)
- Testing performed
- Screenshots (if UI)

---

## Related Rules

- `core.md` - Core rules
- `docs/DEVELOPMENT_WORKFLOW.md` - Complete workflow

---

*Last Updated: 2026-01-15*
