# Workflow Quick Start

**5-minute guide to BenchSight development workflow**

---

## The Basics

### 1. Issue → Branch → PR → Merge

```
Create Issue → Create Branch → Make Changes → Create PR → Review → Merge
```

### 2. Branch Strategy

```
main (production)
  ↑
develop (dev/sandbox)
  ↑
feature/* (your work)
```

---

## Daily Workflow

### Morning: Get Latest

```bash
git checkout develop
git pull origin develop
```

### Start New Work

```bash
# 1. Create issue on GitHub (optional but recommended)
# 2. Create branch
git checkout -b feature/my-feature

# 3. Work locally
./scripts/switch_env.sh sandbox
cd ui/dashboard && npm run dev

# 4. Make changes
# ... edit files ...

# 5. Commit
git add .
git commit -m "feat(etl): add player ratings"

# 6. Push
git push origin feature/my-feature
```

### Create Pull Request

1. Go to GitHub
2. Click "Compare & pull request"
3. Fill in PR template
4. Submit

**CodeRabbit automatically reviews!**

### Address Feedback

```bash
# Make changes
git add .
git commit -m "fix: address CodeRabbit feedback"
git push origin feature/my-feature
```

### Merge When Ready

1. Get approval
2. Merge on GitHub
3. Delete branch

---

## Commit Message Format

```bash
type(scope): description

feat(etl): add player ratings calculation
fix(stats): correct goal counting filter
docs(setup): update installation guide
```

**Types:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

---

## PR Checklist

- [ ] Code follows standards
- [ ] Tests pass
- [ ] Documentation updated
- [ ] CodeRabbit review addressed
- [ ] Self-review completed

---

## Quick Commands

```bash
# Switch branches
git checkout develop
git checkout -b feature/new-feature

# Commit
git add .
git commit -m "type(scope): description"

# Push
git push origin feature/new-feature

# Update from develop
git checkout develop
git pull origin develop
git checkout feature/my-feature
git merge develop
```

---

## Resources

- **Complete Guide:** [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)
- **Industry Standards:** [INDUSTRY_STANDARDS_WORKFLOW.md](INDUSTRY_STANDARDS_WORKFLOW.md)
- **Git Basics:** [GIT_GITHUB_GUIDE.md](GIT_GITHUB_GUIDE.md)

---

*Last updated: 2026-01-13*
