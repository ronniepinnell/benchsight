# Industry-Standard Workflow & Best Practices

**Complete guide to professional development practices for BenchSight**

---

## Table of Contents

1. [Issue Management](#1-issue-management)
2. [Pull Request Workflow](#2-pull-request-workflow)
3. [Commit Message Standards](#3-commit-message-standards)
4. [Code Review Process](#4-code-review-process)
5. [Release Management](#5-release-management)
6. [Documentation Standards](#6-documentation-standards)
7. [Version Control Best Practices](#7-version-control-best-practices)
8. [CI/CD Practices](#8-cicd-practices)

---

## 1. Issue Management

### Issue Lifecycle

```
New → Triage → In Progress → Review → Done
  ↓       ↓         ↓          ↓       ↓
Open   Labeled   Assigned   Testing  Closed
```

### Issue Types

**Bug Reports:**
- Use `[BUG]` prefix
- Include reproduction steps
- Provide error messages/logs
- Specify environment

**Feature Requests:**
- Use `[FEATURE]` prefix
- Describe problem and solution
- Include use cases
- Consider alternatives

**Questions:**
- Use `[QUESTION]` prefix
- Check docs first
- Provide context
- Link to relevant docs

### Issue Labels

**Priority:**
- `priority: critical` - Production broken
- `priority: high` - Important, needs attention
- `priority: medium` - Normal priority
- `priority: low` - Nice to have

**Type:**
- `bug` - Something broken
- `enhancement` - New feature
- `documentation` - Docs need work
- `question` - Need information
- `refactor` - Code improvement

**Status:**
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `blocked` - Waiting on something
- `wontfix` - Not going to fix

**Area:**
- `etl` - ETL pipeline
- `dashboard` - UI/dashboard
- `api` - API changes
- `data` - Data/schema
- `ml` - Machine learning

### Issue Templates

**Use GitHub issue templates:**
- `.github/ISSUE_TEMPLATE/bug_report.md`
- `.github/ISSUE_TEMPLATE/feature_request.md`
- `.github/ISSUE_TEMPLATE/question.md`

### Best Practices

✅ **Do:**
- Create issue before starting work
- Use clear, descriptive titles
- Include all relevant information
- Link related issues
- Update issue as work progresses
- Close issues when done

❌ **Don't:**
- Create duplicate issues
- Leave issues open indefinitely
- Forget to update status
- Create vague issues

---

## 2. Pull Request Workflow

### PR Lifecycle

```
Draft → Ready for Review → Changes Requested → Approved → Merged
  ↓           ↓                  ↓              ↓         ↓
WIP      CodeRabbit Review   Address Feedback  Ready    Done
```

### PR Types

**Feature PR:**
- New functionality
- Should include tests
- Documentation updated
- Breaking changes documented

**Bug Fix PR:**
- Fixes existing issue
- Includes test case
- Documents root cause
- Links to issue

**Hotfix PR:**
- Urgent production fix
- Fast-tracked review
- Also merged to develop
- Documented in CHANGELOG

### PR Checklist

**Before Creating PR:**
- [ ] Code follows standards
- [ ] All tests pass
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Self-review completed
- [ ] Related issues linked

**PR Description Should Include:**
- Clear description
- Type of change
- Related issues
- Testing performed
- Screenshots (if UI)
- Breaking changes (if any)

### PR Template

Use `.github/pull_request_template.md` which includes:
- Description
- Type of change checklist
- Related issues
- Testing performed
- Deployment notes

### Best Practices

✅ **Do:**
- Create PR early (draft mode)
- Keep PRs small and focused
- Write clear descriptions
- Respond to feedback promptly
- Update PR as you work
- Squash commits before merge (if needed)

❌ **Don't:**
- Create huge PRs (hard to review)
- Mix unrelated changes
- Ignore review feedback
- Merge without approval
- Force push to shared branches

---

## 3. Commit Message Standards

### Conventional Commits

Follow [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Commit Types

**Main Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `style:` - Formatting, missing semicolons, etc.
- `refactor:` - Code restructuring
- `perf:` - Performance improvement
- `test:` - Adding/updating tests
- `chore:` - Maintenance tasks
- `build:` - Build system changes
- `ci:` - CI/CD changes

### Commit Format

**Subject (required):**
- 50 characters or less
- Capitalize first letter
- No period at end
- Use imperative mood: "Add" not "Added"

**Body (optional):**
- Wrap at 72 characters
- Explain what and why vs. how
- Reference issues

**Footer (optional):**
- Breaking changes
- Issue references

### Examples

```bash
# Simple feature
git commit -m "feat(etl): add player ratings calculation"

# Feature with body
git commit -m "feat(dashboard): add player comparison view

Adds ability to compare two players side-by-side with
statistics, trends, and head-to-head matchup data.

Closes #123"

# Bug fix
git commit -m "fix(stats): correct goal counting filter

Use GOAL_FILTER pattern consistently across all
goal counting functions.

Fixes #456"

# Breaking change
git commit -m "feat(api): change endpoint structure

BREAKING CHANGE: /api/v1/players endpoint now requires
authentication. Update client code accordingly.

Closes #789"
```

### Scope

**Common scopes:**
- `etl` - ETL pipeline
- `dashboard` - UI/dashboard
- `api` - API changes
- `data` - Data/schema
- `ml` - Machine learning
- `docs` - Documentation
- `config` - Configuration

### Best Practices

✅ **Do:**
- Use conventional commit format
- Write clear, descriptive messages
- Reference issues when applicable
- Keep commits atomic (one logical change)
- Use present tense, imperative mood

❌ **Don't:**
- Write vague messages like "fix stuff"
- Mix unrelated changes in one commit
- Forget to reference issues
- Use past tense ("Fixed bug")
- Write messages that are too long

---

## 4. Code Review Process

### Review Stages

1. **Automated Review (CodeRabbit)**
   - Runs automatically on PR
   - Checks code quality
   - Finds bugs and issues
   - Suggests improvements

2. **Human Review**
   - Final approval
   - Architecture decisions
   - Business logic validation
   - Documentation review

### Review Checklist

**Code Quality:**
- [ ] Follows CODE_STANDARDS.md
- [ ] No code duplication
- [ ] Proper error handling
- [ ] Type safety
- [ ] Performance considerations

**Functionality:**
- [ ] Solves the problem
- [ ] Root-level solution (not patchwork)
- [ ] Single source of truth
- [ ] Tests included
- [ ] Edge cases handled

**Documentation:**
- [ ] Code is self-documenting
- [ ] Comments for complex logic
- [ ] Documentation updated
- [ ] CHANGELOG updated (if needed)

**Security:**
- [ ] No sensitive data exposed
- [ ] Input validation
- [ ] SQL injection prevention
- [ ] Authentication/authorization

### Review Best Practices

**For Authors:**
- ✅ Create PR early (draft mode)
- ✅ Write clear description
- ✅ Respond to feedback
- ✅ Be open to suggestions
- ✅ Thank reviewers

**For Reviewers:**
- ✅ Be constructive
- ✅ Explain why, not just what
- ✅ Suggest alternatives
- ✅ Approve when ready
- ✅ Be respectful

### Review Comments

**Types of comments:**
- **Must fix** - Blocking issue
- **Should fix** - Important but not blocking
- **Consider** - Suggestion, optional
- **Question** - Need clarification
- **Praise** - Good work!

**Example:**
```markdown
**Must fix:** This uses the wrong goal filter pattern.
Should use `GOAL_FILTER` constant from utils.

**Consider:** This function is getting long. Could we
extract the validation logic into a separate function?

**Question:** Why do we need this null check here?
```

---

## 5. Release Management

### Semantic Versioning

Follow [SemVer](https://semver.org/): `MAJOR.MINOR.PATCH`

- **MAJOR** - Breaking changes
- **MINOR** - New features (backward compatible)
- **PATCH** - Bug fixes (backward compatible)

**Examples:**
- `29.0.0` → `30.0.0` - Breaking change
- `29.0.0` → `29.1.0` - New feature
- `29.0.0` → `29.0.1` - Bug fix

### Release Process

1. **Prepare Release:**
   ```bash
   # Update version
   # Update CHANGELOG.md
   # Create release branch
   git checkout -b release/v29.1.0
   ```

2. **Final Testing:**
   - Run full test suite
   - Test on dev environment
   - Verify documentation
   - Check breaking changes

3. **Create Release:**
   ```bash
   # Merge to main
   git checkout main
   git merge release/v29.1.0
   git tag v29.1.0
   git push origin main --tags
   ```

4. **GitHub Release:**
   - Create release on GitHub
   - Use CHANGELOG for notes
   - Attach assets if needed
   - Announce release

### CHANGELOG Format

Follow [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
## [29.1.0] - 2026-01-15

### Added
- Player ratings calculation
- New dashboard comparison view

### Changed
- Improved ETL performance by 30%

### Fixed
- Goal counting filter now consistent
- Dashboard loading time reduced

### Removed
- Deprecated `old_function()` (use `new_function()`)

### Security
- Fixed SQL injection vulnerability
```

### Release Checklist

- [ ] Version number updated
- [ ] CHANGELOG.md updated
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Breaking changes documented
- [ ] Release notes prepared
- [ ] Tagged in git
- [ ] GitHub release created

---

## 6. Documentation Standards

### Documentation Types

**User Documentation:**
- README.md - Getting started
- QUICK_START.md - Quick start guide
- SETUP.md - Installation
- User guides

**Developer Documentation:**
- CODE_STANDARDS.md - Coding standards
- ARCHITECTURE.md - System design
- API documentation
- Code comments

**Operational Documentation:**
- DEPLOYMENT.md - Deployment guide
- TROUBLESHOOTING.md - Common issues
- MAINTENANCE.md - Maintenance procedures

### Documentation Best Practices

✅ **Do:**
- Write for your audience
- Keep it up to date
- Include examples
- Use clear language
- Cross-reference related docs
- Update "Last Updated" dates

❌ **Don't:**
- Write outdated docs
- Assume prior knowledge
- Skip examples
- Use jargon without explanation
- Leave broken links

### Documentation Structure

```markdown
# Title

Brief description

## Overview
What this is about

## Prerequisites
What you need first

## Steps
1. Step one
2. Step two

## Examples
Code examples

## Troubleshooting
Common issues

## Related
Links to related docs
```

### Code Comments

**Good comments:**
- Explain why, not what
- Clarify complex logic
- Document assumptions
- Note edge cases

**Bad comments:**
- Obvious code explanation
- Outdated information
- TODO without context
- Commented-out code

---

## 7. Version Control Best Practices

### Branch Strategy

```
main (production)
  ↑
develop (integration)
  ↑
feature/* (development)
```

**Branch Rules:**
- `main` - Always deployable
- `develop` - Integration branch
- `feature/*` - Feature development
- `fix/*` - Bug fixes
- `hotfix/*` - Urgent production fixes
- `release/*` - Release preparation

### Branch Protection

**For `main` branch:**
- Require pull request
- Require approvals (1+)
- Require status checks
- No force push
- No deletion

**For `develop` branch:**
- Require pull request
- Optional approvals
- Require status checks

### Git Workflow

**Daily:**
```bash
# Morning
git checkout develop
git pull origin develop

# Work
git checkout -b feature/my-feature
# ... work ...

# End of day
git push origin feature/my-feature
```

**Before PR:**
```bash
# Update from develop
git checkout develop
git pull origin develop
git checkout feature/my-feature
git merge develop  # Or rebase

# Clean up commits
git rebase -i develop  # Interactive rebase
```

### Best Practices

✅ **Do:**
- Commit often with clear messages
- Keep branches up to date
- Use feature branches
- Review before merging
- Delete merged branches

❌ **Don't:**
- Commit directly to main/develop
- Force push to shared branches
- Leave branches unmerged
- Mix unrelated changes
- Commit large files

---

## 8. CI/CD Practices

### Continuous Integration

**What CI Does:**
- Run tests on every PR
- Check code quality
- Validate builds
- Run linters

**GitHub Actions Example:**
```yaml
name: CI

on:
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: pytest tests/
      - name: Run linter
        run: flake8 src/
```

### Continuous Deployment

**Deployment Stages:**
1. **Development** - Auto-deploy from `develop`
2. **Staging** - Manual or auto from release branch
3. **Production** - Manual from `main`

**Vercel Auto-Deployment:**
- `main` → Production
- `develop` → Dev environment
- `feature/*` → Preview deployments

### Best Practices

✅ **Do:**
- Automate testing
- Run tests before merge
- Deploy to dev automatically
- Manual approval for production
- Monitor deployments

❌ **Don't:**
- Skip tests
- Deploy untested code
- Auto-deploy to production
- Ignore failed builds
- Deploy without monitoring

---

## Quick Reference

### Issue Workflow
```
Create Issue → Assign → Work → PR → Review → Merge → Close
```

### PR Workflow
```
Create Branch → Work → Commit → Push → PR → Review → Merge
```

### Release Workflow
```
Develop → Release Branch → Test → Merge to Main → Tag → Release
```

### Commit Format
```
type(scope): subject

body

footer
```

### Version Format
```
MAJOR.MINOR.PATCH
29.1.0
```

---

## Tools & Resources

### GitHub Features
- Issues - Track work
- Pull Requests - Code review
- Projects - Project management
- Actions - CI/CD
- Releases - Version management

### Code Quality
- CodeRabbit - AI code review
- Linters - Code quality
- Tests - Validation
- Type checking - Type safety

### Documentation
- Markdown - Documentation format
- GitHub Pages - Hosted docs
- API docs - Code-generated docs

---

## Checklist

### Starting New Work
- [ ] Issue created
- [ ] Branch created from develop
- [ ] Local environment set up
- [ ] Documentation reviewed

### During Development
- [ ] Code follows standards
- [ ] Tests written
- [ ] Documentation updated
- [ ] Commits are atomic

### Before PR
- [ ] All tests pass
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] PR description written

### After Merge
- [ ] Branch deleted
- [ ] Issue closed
- [ ] CHANGELOG updated (if needed)
- [ ] Release created (if needed)

---

*Last updated: 2026-01-13*
