# Documentation Maintenance

**Strategy for keeping documentation in sync with code**

Last Updated: 2026-01-21

---

## Overview

Documentation must stay in sync with code. This document outlines the strategy for maintaining documentation consistency.

---

## When to Update Documentation

### Code Changes

**Update docs when:**
- Adding new features
- Changing APIs
- Modifying architecture
- Updating data models
- Changing workflows

### Documentation Changes

**Update code references when:**
- Restructuring docs
- Updating examples
- Changing processes
- Adding new docs

---

## Documentation Sync Strategy

### Immediate Updates

**Update immediately:**
- API documentation (when API changes)
- Architecture docs (when architecture changes)
- Setup guides (when setup changes)
- Workflow docs (when workflows change)

### Periodic Updates

**Update periodically:**
- Weekly: Review recent changes
- Monthly: Comprehensive review
- Quarterly: Major documentation audit

---

## Documentation Review Process

### Weekly Review

**Check:**
- Recent code changes
- New features added
- Documentation gaps
- Outdated information

### Monthly Review

**Comprehensive check:**
- All documentation
- Cross-references
- Broken links
- Consistency

### Quarterly Audit

**Major review:**
- Documentation structure
- Archive outdated docs
- Update master index
- Consolidate duplicates

---

## Documentation Consistency Checks

### Automated Checks

**Use:** `./scripts/docs-check.sh`

**Checks:**
- Broken links
- Cross-references
- Outdated docs
- Doc structure

### Suggested Automation

- **Pre-commit:** Run docs check on `docs/**` changes
- **CI:** Run docs check on PRs touching docs
- **Weekly:** Schedule a docs link check and update `MASTER_INDEX.md` if needed

### Pre-Commit Setup

```bash
pip install pre-commit
pre-commit install
```

**Config:** `.pre-commit-config.yaml`

### Manual Checks

**Review:**
- Code examples
- Screenshots
- Process descriptions
- Accuracy

---

## Documentation Update Workflow

### Step 1: Code Changes

**When code changes:**
1. Identify affected docs
2. Update relevant documentation
3. Check cross-references
4. Verify examples

### Step 2: Documentation Review

**Review updated docs:**
1. Check accuracy
2. Verify examples
3. Test links
4. Check formatting

### Step 3: Documentation Sync

**Sync documentation:**
1. Run `./benchsight.sh docs check`
2. Fix any issues
3. Update master index if needed
4. Commit changes

---

## Documentation Versioning

### Version Strategy

**Version docs when:**
- Major changes
- Breaking changes
- Architecture changes

**Version format:**
- Major.Minor (e.g., 29.0)
- Update in doc header

### Archive Strategy

**Archive when:**
- Superseded by new docs
- No longer relevant
- Replaced by better version

**Archive location:**
- `docs/archive/`
- Keep for reference

---

## Documentation Structure

### Master Index

**File:** `docs/MASTER_INDEX.md`

**Purpose:**
- Central index
- Navigation
- Quick reference

**Update when:**
- New docs added
- Docs restructured
- Docs archived

### Component Documentation

**Structure:**
- Component-specific docs
- Clear organization
- Easy navigation

---

## Best Practices

### ✅ Do:

- Update docs with code changes
- Keep examples current
- Test documentation
- Review regularly
- Archive outdated docs

### ❌ Don't:

- Let docs get outdated
- Skip documentation
- Forget cross-references
- Ignore broken links
- Duplicate information

---

## Tools

### Documentation Check Script

**Location:** `scripts/docs-check.sh`

**Usage:**
```bash
./benchsight.sh docs check
```

**Checks:**
- Broken links
- Cross-references
- Doc structure

### Manual Review

**Checklist:**
- [ ] All code examples work
- [ ] All links work
- [ ] Cross-references correct
- [ ] Examples current
- [ ] Formatting consistent

---

## Related Documentation

- [MASTER_INDEX.md](../MASTER_INDEX.md) - Documentation index
- [WORKFLOW.md](WORKFLOW.md) - Development workflow
- `scripts/docs-check.sh` - Documentation check script

---

*Last Updated: 2026-01-15*
