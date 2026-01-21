# Pre-Restructuring Checklist

**Comprehensive checklist to prepare for restructuring and planning work**

Last Updated: 2026-01-15  
Version: 29.0

---

## Overview

This checklist ensures all documentation, environments, workflows, and tools are ready before starting restructuring and planning work.

**Complete all items before beginning restructuring.**

---

## Documentation Readiness

### Master Documents

- [ ] **MASTER_INDEX.md** - All new reference materials listed
- [ ] **MASTER_INDEX.md** - All links verified and working
- [ ] **PROJECT_STATUS.md** - Completion percentages updated
- [ ] **PROJECT_STATUS.md** - Review cleanup marked complete
- [ ] **PROJECT_STATUS.md** - Next steps section updated
- [ ] **MASTER_ROADMAP.md** - Phases and timelines reviewed
- [ ] **MASTER_ROADMAP.md** - Completed phases marked
- [ ] **DEVELOPMENT_WORKFLOW.md** - PRD workflow documented
- [ ] **DEVELOPMENT_WORKFLOW.md** - Context reset steps clear
- [ ] **DEVELOPMENT_WORKFLOW.md** - New commands added

### Review Folder

- [x] **Review folder** - All files reviewed
- [x] **Review folder** - Unique content identified
- [x] **Review folder** - Outdated files archived
- [x] **Review folder** - Duplicates removed
- [x] **Review folder** - Reference materials organized
- [x] **Review folder** - Folder deleted (content archived or integrated)

### Reference Materials

- [ ] **Reference section** - Inspiration materials organized
- [ ] **Reference section** - Screenshots categorized
- [ ] **Reference section** - Research papers indexed
- [ ] **Reference section** - Wireframes created
- [ ] **Reference section** - Links documented

---

## Environment Readiness

### Supabase

- [ ] **Dev Supabase** - Project configured
- [ ] **Dev Supabase** - Credentials in `config_local.dev.ini`
- [ ] **Dev Supabase** - Connection tested
- [ ] **Prod Supabase** - Project configured
- [ ] **Prod Supabase** - Credentials in `config_local.ini`
- [ ] **Prod Supabase** - Connection tested (careful!)
- [ ] **Environment switching** - `./benchsight.sh env switch dev` works
- [ ] **Environment switching** - `./benchsight.sh env switch production` works
- [ ] **Environment switching** - Status command works

### Vercel

- [ ] **Dev Vercel** - Project `benchsight-dev` exists
- [ ] **Dev Vercel** - Connected to `develop` branch
- [ ] **Dev Vercel** - Environment variables set (dev Supabase)
- [ ] **Dev Vercel** - Auto-deploy configured
- [ ] **Prod Vercel** - Project `benchsight` exists
- [ ] **Prod Vercel** - Connected to `main` branch
- [ ] **Prod Vercel** - Environment variables set (prod Supabase)
- [ ] **Prod Vercel** - Auto-deploy configured
- [ ] **Vercel** - Test deployment successful

### Local Development

- [ ] **Python** - Version 3.11+ installed
- [ ] **Node.js** - Version 18+ or 20+ installed
- [ ] **Dependencies** - All installed (`pip install -r requirements.txt`)
- [ ] **Dashboard dependencies** - All installed (`cd ui/dashboard && npm install`)
- [ ] **API dependencies** - All installed (`cd api && pip install -r requirements.txt`)
- [ ] **CLI** - `benchsight.sh` executable and working
- [ ] **Scripts** - All scripts executable

---

## Workflow Readiness

### GitHub

- [ ] **Repository** - Set up and accessible
- [ ] **Branches** - `main` and `develop` exist
- [ ] **Branch protection** - `main` branch protected
- [ ] **Branch protection** - PR required for `main`
- [ ] **Branch protection** - Approvals required
- [ ] **Issue templates** - Bug report template exists
- [ ] **Issue templates** - Feature request template exists
- [ ] **Issue templates** - Question template exists
- [ ] **Issue templates** - Refactor template exists
- [ ] **PR template** - Pull request template exists
- [ ] **CI/CD** - GitHub Actions workflows configured
- [ ] **CI/CD** - Tests run on PRs
- [ ] **CI/CD** - Code quality checks run

### CodeRabbit

- [ ] **Installation** - CodeRabbit app installed
- [ ] **Configuration** - `.coderabbit.yaml` exists
- [ ] **Configuration** - BenchSight-specific rules configured
- [ ] **Testing** - Test PR created and reviewed
- [ ] **Integration** - Reviews appear on PRs

### Git Workflow

- [ ] **Branch strategy** - Understood and documented
- [ ] **Commit format** - Standard format established
- [ ] **PR process** - Workflow documented
- [ ] **Issue linking** - Process established
- [ ] **PRD linking** - Process established

---

## Tool Readiness

### Cursor AI

- [ ] **Configuration** - `.cursorrules` exists
- [ ] **Configuration** - Modular rules referenced
- [ ] **Configuration** - Core rules loaded
- [ ] **Testing** - Rules auto-load correctly
- [ ] **Testing** - Manual loading works

### Claude Settings

- [ ] **Configuration** - `.claude/settings.json` exists
- [ ] **Configuration** - Project rules defined
- [ ] **Configuration** - Project structure documented
- [ ] **Configuration** - Common commands listed

### Modular Rules

- [ ] **Structure** - `.agents/` directory exists
- [ ] **Core rules** - `.agents/core.md` exists
- [ ] **ETL rules** - `.agents/reference/etl.md` exists
- [ ] **Dashboard rules** - `.agents/reference/dashboard.md` exists
- [ ] **API rules** - `.agents/reference/api.md` exists
- [ ] **Tracker rules** - `.agents/reference/tracker.md` exists
- [ ] **Portal rules** - `.agents/reference/portal.md` exists
- [ ] **Data rules** - `.agents/reference/data.md` exists
- [ ] **Testing rules** - `.agents/reference/testing.md` exists
- [ ] **Deployment rules** - `.agents/reference/deployment.md` exists
- [ ] **Git rules** - `.agents/reference/git.md` exists

### MCPs (if using)

- [ ] **Browser extension** - MCP configured
- [ ] **IDE browser** - MCP configured
- [ ] **Testing** - MCP tools accessible
- [ ] **Testing** - Browser navigation works

### CLI Commands

- [ ] **benchsight.sh** - All commands work
- [ ] **benchsight.sh** - Help command shows all options
- [ ] **benchsight.sh** - Environment switching works
- [ ] **benchsight.sh** - ETL commands work
- [ ] **benchsight.sh** - Dashboard commands work
- [ ] **benchsight.sh** - Documentation commands work
- [ ] **benchsight.sh** - PRD commands work
- [ ] **benchsight.sh** - Workflow commands work

---

## Verification Steps

### Step 1: Documentation Verification (30 minutes)

```bash
# 1. Check master docs are updated
grep -r "Review cleanup" docs/PROJECT_STATUS.md
grep -r "COMPLETE_WORKFLOW_GUIDE" docs/MASTER_INDEX.md

# 2. Verify reference materials exist
ls docs/reference/inspiration/
ls docs/reference/design/wireframes/

# 3. Check Review folder status
ls docs/Review/*.md | wc -l  # Should be reduced
ls docs/archive/review/       # Should have archived files
```

### Step 2: Environment Verification (15 minutes)

```bash
# 1. Test dev environment
./benchsight.sh env switch dev
./benchsight.sh env status

# 2. Test production environment (careful!)
./benchsight.sh env switch production
./benchsight.sh env status
./benchsight.sh env switch dev  # Switch back!

# 3. Verify Supabase connections
# Test ETL connection or dashboard connection
```

### Step 3: GitHub Verification (15 minutes)

```bash
# 1. Check branches
git branch -a

# 2. Verify remotes
git remote -v

# 3. Test push/pull
git pull origin develop

# 4. Check GitHub settings
# - Go to GitHub → Settings → Branches
# - Verify branch protection rules
```

### Step 4: Vercel Verification (15 minutes)

1. **Check Vercel projects:**
   - Go to Vercel dashboard
   - Verify `benchsight` (prod) exists
   - Verify `benchsight-dev` (dev) exists

2. **Check environment variables:**
   - Production project: Production Supabase credentials
   - Dev project: Dev Supabase credentials

3. **Test deployment:**
   - Make small change
   - Push to `develop`
   - Verify auto-deployment works

### Step 5: CodeRabbit Verification (10 minutes)

1. **Check installation:**
   - Go to GitHub → Settings → Applications
   - Verify CodeRabbit app installed

2. **Test review:**
   - Create test PR
   - Verify CodeRabbit comments appear

### Step 6: AI Setup Verification (10 minutes)

```bash
# 1. Verify modular rules
ls -la .agents/
ls -la .agents/reference/

# 2. Check Cursor settings
cat .cursorrules | head -20
cat .claude/settings.json | head -20

# 3. Test context loading
# Start conversation about ETL
# Verify rules auto-load
# Test manual loading
```

---

## Success Criteria

All items above should be checked before starting restructuring work.

**Ready when:**
- [ ] All documentation updated
- [ ] All environments verified
- [ ] All workflows established
- [ ] All tools configured
- [ ] All verification steps passed

---

## Next Steps After Checklist

Once all items are complete:

1. **Review COMPLETE_WORKFLOW_GUIDE.md** - Understand full workflow
2. **Start restructuring planning** - Create PRD for restructuring
3. **Begin restructuring** - Follow PRD and workflow guide

---

## Related Documentation

- [COMPLETE_WORKFLOW_GUIDE.md](COMPLETE_WORKFLOW_GUIDE.md) - Complete workflow guide
- [DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md) - Development workflows
- [PLANNING_WORKFLOW.md](PLANNING_WORKFLOW.md) - PRD-first development
- [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md) - Complete setup guide

---

*Last Updated: 2026-01-15*
