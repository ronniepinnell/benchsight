# Complete Setup Guide: GitHub, CodeRabbit, and Dev/Prod Environments

**Master guide for setting up everything you need for professional development workflow**

---

## Table of Contents

1. [GitHub Repository Setup](#1-github-repository-setup)
2. [Development & Production Environments](#2-development--production-environments)
3. [CodeRabbit Integration](#3-coderabbit-integration)
4. [Complete Workflow](#4-complete-workflow)
5. [Best Practices](#5-best-practices)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. GitHub Repository Setup

### Step 1.1: Initialize Git Repository

**If you haven't already:**

```bash
# Navigate to your project
cd /Users/ronniepinnell/Documents/Documents\ -\ Ronnie\'s\ MacBook\ Pro\ -\ 1/Programming_HD/Hockey/Benchsight/git/benchsight

# Initialize git (if not already done)
git init

# Check status
git status
```

### Step 1.2: Create GitHub Repository

1. **Go to GitHub:**
   - Visit: https://github.com/new
   - Or: https://github.com → Click "+" → "New repository"

2. **Repository Settings:**
   - **Name:** `benchsight`
   - **Description:** "Hockey Analytics Platform for NORAD Recreational League"
   - **Visibility:** Private (recommended) or Public
   - **Don't** initialize with README (you already have one)
   - **Don't** add .gitignore or license (you have them)

3. **Click "Create repository"**

### Step 1.3: Connect Local to GitHub

```bash
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/benchsight.git

# Verify remote
git remote -v
# Should show:
# origin  https://github.com/YOUR_USERNAME/benchsight.git (fetch)
# origin  https://github.com/YOUR_USERNAME/benchsight.git (push)
```

### Step 1.4: Create Initial Branches

```bash
# Make sure you're on main
git checkout -b main  # If not already on main

# Create develop branch
git checkout -b develop

# Push both branches
git push -u origin main
git push -u origin develop
```

### Step 1.5: First Commit and Push

```bash
# Stage all files
git add .

# Create initial commit
git commit -m "Initial commit: BenchSight v29.0"

# Push to main
git checkout main
git push origin main

# Push to develop
git checkout develop
git push origin develop
```

**Note:** If you get authentication errors, see [GitHub Authentication Guide](troubleshooting/QUICK_FIX_GITHUB_AUTH.md)

---

## 2. Development & Production Environments

### Step 2.1: Create Supabase Projects

**Option A: Use Supabase Branching (Recommended if available)**

If your Supabase plan supports branching, you can use branches instead of separate projects:

1. **Enable Branching:**
   - Go to Supabase Dashboard → Your Project
   - Look for "Branches" in sidebar
   - Enable if available

2. **Create Develop Branch:**
   - Go to Branches → New Branch
   - Name: `develop`
   - Source: `main`
   - This creates an isolated database branch

3. **Benefits:**
   - Easier to manage (one project)
   - Easy schema merging
   - Automatic branch creation from PRs (if GitHub integrated)

**See [SUPABASE_BRANCHING.md](SUPABASE_BRANCHING.md) for complete guide.**

**Option B: Separate Supabase Projects (Current Guide)**

#### Production Supabase Project

1. **Go to Supabase:**
   - Visit: https://supabase.com/dashboard
   - Sign in or create account

2. **Create Production Project:**
   - Click **"New Project"**
   - **Name:** `benchsight` (production)
   - **Database Password:** Create strong password (save it!)
   - **Region:** Choose closest to your users
   - Click **"Create new project"**
   - Wait ~2 minutes for setup

3. **Save Production Credentials:**
   - Go to **Settings** → **API**
   - Copy:
     - **Project URL:** `https://xxxxx.supabase.co`
     - **anon public** key: `eyJ...` (long string)
   - Save in password manager or secure file

#### Development Supabase Project

1. **Create Dev Project:**
   - Click **"New Project"** again
   - **Name:** `benchsight-dev` (or `benchsight-sandbox`)
   - **Database Password:** Can be simpler (dev only)
   - **Region:** Same as production
   - Click **"Create new project"**
   - Wait ~2 minutes

2. **Save Dev Credentials:**
   - Go to **Settings** → **API**
   - Copy:
     - **Project URL:** `https://yyyyy.supabase.co`
     - **anon public** key: `eyJ...`
   - Save separately from production

### Step 2.2: Set Up Supabase Schemas

#### Option A: Copy Schema from Production to Dev

```bash
# 1. Export schema from production
# In Production Supabase → SQL Editor
# Copy contents of: sql/setup_supabase.sql

# 2. Apply to dev
# In Dev Supabase → SQL Editor
# Paste and run the SQL
```

#### Option B: Run ETL to Both

```bash
# 1. Set up production config
# Edit config/config_local.ini with production Supabase URL
# Run ETL
python run_etl.py
python upload.py

# 2. Set up dev config
./scripts/switch_env.sh sandbox
# Edit config/config_local.ini with dev Supabase URL
python run_etl.py
python upload.py
```

### Step 2.3: Create Vercel Projects

#### Production Vercel Project

1. **Go to Vercel:**
   - Visit: https://vercel.com
   - Sign in with GitHub (easiest)

2. **Create Production Project:**
   - Click **"Add New..."** → **"Project"**
   - Find **"benchsight"** repository
   - Click **"Import"**

3. **Configure Production Project:**
   - **Project Name:** `benchsight` (production project)
   - **Framework Preset:** Next.js (auto-detected)
   - **Root Directory:** `ui/dashboard`
   - **Build Command:** `npm run build` (auto-filled)
   - **Output Directory:** `.next` (auto-filled)
   - **Install Command:** `npm install` (auto-filled)

4. **Set Production Branch:**
   - **Production Branch:** `main`
   - This means: pushing to `main` → deploys to production

5. **Add Environment Variables:**
   - Go to **Settings** → **Environment Variables**
   - Add:
     - **Name:** `NEXT_PUBLIC_SUPABASE_URL`
     - **Value:** Production Supabase URL (main branch)
     - **Environment:** Production, Preview, Development
   - Add:
     - **Name:** `NEXT_PUBLIC_SUPABASE_ANON_KEY`
     - **Value:** Production anon key
     - **Environment:** Production, Preview, Development

6. **Click "Deploy"**
   - Wait for deployment (~2 minutes)
   - Note the URL: `https://benchsight.vercel.app`

#### Development Vercel Project

1. **Create Dev Project:**
   - Click **"Add New..."** → **"Project"**
   - Select **same** "benchsight" repository
   - Click **"Import"**

2. **Configure Dev Project:**
   - **Project Name:** `benchsight-dev`
   - **Framework Preset:** Next.js
   - **Root Directory:** `ui/dashboard`
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`
   - **Install Command:** `npm install`

3. **Set Production Branch to `develop`:**
   - **Production Branch:** `develop`
   - This means: pushing to `develop` → deploys to dev Vercel
   - **Yes, you can use the active branch for dev!**

4. **Add Environment Variables (Supabase Develop Branch):**
   - Go to **Settings** → **Environment Variables**
   - Add:
     - **Name:** `NEXT_PUBLIC_SUPABASE_URL`
     - **Value:** Your Supabase **develop branch URL** (not main project URL!)
     - **Environment:** Production, Preview, Development (all)
   - Add:
     - **Name:** `NEXT_PUBLIC_SUPABASE_ANON_KEY`
     - **Value:** Your Supabase develop branch anon key
     - **Environment:** Production, Preview, Development (all)

5. **Click "Deploy"**
   - Wait for deployment
   - Note the URL: `https://benchsight-dev.vercel.app`

**Important:** Use the Supabase **develop branch URL**, not the main project URL!

### Step 2.4: Set Up Local Development

```bash
# Create dev environment file
cd ui/dashboard
cat > .env.local.dev << EOF
NEXT_PUBLIC_SUPABASE_URL=https://your-dev-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-dev-anon-key
EOF

# Create production environment file (for reference)
cat > .env.local.production << EOF
NEXT_PUBLIC_SUPABASE_URL=https://your-prod-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-prod-anon-key
EOF

# Switch to dev (default)
cp .env.local.dev .env.local
```

**Use the switch script:**
```bash
# Switch to dev
./scripts/switch_env.sh sandbox

# Switch to production (careful!)
./scripts/switch_env.sh production
```

---

## 3. CodeRabbit Integration

### Step 3.1: Install CodeRabbit GitHub App

1. **Go to CodeRabbit:**
   - Visit: https://coderabbit.ai
   - Click **"Get Started"** or **"Sign Up"**

2. **Install GitHub App:**
   - Click **"Install GitHub App"**
   - Sign in with GitHub
   - Select **"Only select repositories"**
   - Choose **"benchsight"**
   - Click **"Install"**

3. **Authorize Permissions:**
   - CodeRabbit needs:
     - ✅ Read access to code
     - ✅ Write access to comments (for reviews)
     - ✅ Read access to pull requests
   - Click **"Authorize"**

### Step 3.2: Verify Configuration

The project already includes `.coderabbit.yaml` with BenchSight-specific settings:

```yaml
# Configured for:
# - Python code review (ETL, API)
# - TypeScript/React review (Dashboard)
# - SQL review (Views, migrations)
# - BenchSight-specific patterns
```

**Check it exists:**
```bash
cat .coderabbit.yaml
```

### Step 3.3: Test CodeRabbit

1. **Create Test PR:**
   ```bash
   git checkout -b test/coderabbit-setup
   # Make a small change
   echo "# Test" >> README.md
   git add README.md
   git commit -m "Test CodeRabbit integration"
   git push origin test/coderabbit-setup
   ```

2. **Create Pull Request:**
   - Go to GitHub → Your repo
   - Click **"Compare & pull request"**
   - Base: `main`, Compare: `test/coderabbit-setup`
   - Click **"Create pull request"**

3. **Wait for CodeRabbit:**
   - CodeRabbit should start reviewing within 1-2 minutes
   - Look for comments from `coderabbit[bot]`
   - Review will appear in PR comments

4. **Clean Up:**
   ```bash
   # Delete test branch
   git checkout main
   git branch -d test/coderabbit-setup
   git push origin --delete test/coderabbit-setup
   ```

---

## 4. Complete Workflow

### Daily Development Workflow

```bash
# 1. Morning: Get latest changes
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/add-player-ratings

# 3. Work locally (connected to dev Supabase)
./scripts/switch_env.sh sandbox
cd ui/dashboard
npm run dev
# Test at http://localhost:3000

# 4. Make changes
# ... edit files ...

# 5. Test thoroughly
python run_etl.py  # If ETL changes
python validate.py  # Validate data
# Test dashboard locally

# 6. Commit changes
git add .
git commit -m "[FEAT] Add player ratings feature"
git push origin feature/add-player-ratings

# 7. Create Pull Request
# Go to GitHub → Create PR: feature/add-player-ratings → develop
# CodeRabbit automatically reviews

# 8. Address CodeRabbit feedback
# ... make improvements ...
git push origin feature/add-player-ratings
# CodeRabbit reviews new commits automatically

# 9. Get human review (if needed)
# Ask teammate to review

# 10. Merge to develop
# On GitHub, click "Merge pull request"
# Vercel auto-deploys to dev environment
# Test at: https://benchsight-dev.vercel.app

# 11. When ready for production
# Create PR: develop → main
# CodeRabbit reviews again
# After merge, Vercel auto-deploys to production
# Test at: https://benchsight.vercel.app
```

### Branch Strategy

```
main (production)
  ↑
develop (dev/sandbox)
  ↑
feature/* (your work)
```

**Branch Rules:**
- `main` → Production (stable, tested)
- `develop` → Development (integration)
- `feature/*` → New features
- `fix/*` → Bug fixes
- `hotfix/*` → Urgent production fixes

### Environment Mapping

| Git Branch | Supabase Branch | Config File | Vercel Project | Purpose |
|------------|----------------|-------------|----------------|---------|
| `main` | `main` | `config_local.ini` | `benchsight` | Production |
| `develop` | `develop` | `config_local.develop.ini` | `benchsight-dev` | Development |
| `feature/*` | `develop` (or auto-created) | Uses dev config | Preview (auto) | Feature work |

---

## 5. Best Practices

### GitHub Best Practices

#### ✅ Commit Messages

```bash
# Format: [TYPE] Brief description

[FEAT] Add player ratings calculation
[FIX] Correct goal counting filter
[DOCS] Update setup instructions
[REFACTOR] Extract common filtering logic
[TEST] Add tests for goal counting
```

#### ✅ Branch Naming

```bash
feature/add-ml-predictions    # New feature
fix/goal-counting-bug          # Bug fix
hotfix/critical-security       # Urgent production fix
docs/update-readme            # Documentation
refactor/cleanup-stats        # Code improvement
```

#### ✅ Pull Request Descriptions

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] ETL runs successfully
- [ ] Validation passes
- [ ] Manual testing completed
- [ ] Tested on dev environment

## Checklist
- [ ] Code follows CODE_STANDARDS.md
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] CodeRabbit review addressed
```

#### ✅ Branch Protection (Recommended)

1. Go to GitHub → Settings → Branches
2. Add rule for `main`:
   - ✅ Require pull request before merging
   - ✅ Require approvals (1 person)
   - ✅ Require status checks (if you have CI)

### CodeRabbit Best Practices

#### ✅ How to Use CodeRabbit

1. **Read all feedback** - CodeRabbit catches real issues
2. **Fix critical issues** - Errors and security problems
3. **Consider suggestions** - They often improve code quality
4. **Learn from feedback** - Understand why suggestions are made
5. **Don't dismiss blindly** - Review each suggestion

#### ✅ CodeRabbit Checks For

- **BenchSight Patterns:**
  - GOAL_FILTER usage
  - Single source of truth
  - Type consistency
  - Error handling

- **Code Quality:**
  - Duplication
  - Magic numbers
  - Security issues
  - Performance problems

- **Best Practices:**
  - Documentation
  - Testing
  - Maintainability

### Environment Best Practices

#### ✅ Keep Schemas in Sync

**Critical:** Dev and prod Supabase must have same schema!

```bash
# When adding new table/view:
# 1. Add to dev Supabase first
# 2. Test in dev environment
# 3. When ready, add to production Supabase
# 4. Deploy code to production
```

#### ✅ Test in Dev First

**Always:**
1. Test locally (dev Supabase)
2. Deploy to dev Vercel
3. Test on dev URL
4. Only then deploy to production

#### ✅ Environment Variables

**Never commit:**
- `.env.local` files
- API keys
- Passwords
- Secrets

**Always:**
- Set in Vercel dashboard
- Use `.env.local` for local dev
- Keep `.env.local` in `.gitignore`

### Workflow Best Practices

#### ✅ Daily Routine

```bash
# Morning
git checkout develop
git pull origin develop

# Work
git checkout -b feature/my-feature
# ... work ...

# End of day
git push origin feature/my-feature
# Create PR on GitHub
```

#### ✅ Before Merging to Main

- [ ] All tests pass
- [ ] CodeRabbit review addressed
- [ ] Tested in dev environment
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] Schema changes applied to production

#### ✅ Emergency Hotfixes

```bash
# 1. Start from main
git checkout main
git pull origin main

# 2. Create hotfix branch
git checkout -b hotfix/critical-bug

# 3. Fix bug
# ... fix ...

# 4. Test locally (switch to production config temporarily)
./scripts/switch_env.sh production
# ... test ...
./scripts/switch_env.sh sandbox

# 5. Commit and push
git commit -m "[HOTFIX] Fix critical production bug"
git push origin hotfix/critical-bug

# 6. Create PR: hotfix → main
# Fast-track review and merge

# 7. Also merge to develop
git checkout develop
git merge main
git push origin develop
```

---

## 6. Troubleshooting

### GitHub Issues

#### "Authentication Error"

**Solution:** See [GitHub Authentication Guide](troubleshooting/QUICK_FIX_GITHUB_AUTH.md)

```bash
# Use Personal Access Token
# Or set up SSH keys
```

#### "Can't Push to Branch"

**Check:**
- Do you have write access?
- Is branch protected?
- Are you on the right branch?

#### "Merge Conflicts"

```bash
# Resolve conflicts
git checkout develop
git pull origin develop
git checkout feature/my-feature
git merge develop
# Resolve conflicts in files
git add .
git commit -m "Resolve merge conflicts"
git push origin feature/my-feature
```

### CodeRabbit Issues

#### "CodeRabbit Not Reviewing"

**Check:**
1. Is app installed? (GitHub → Settings → Applications)
2. Is repository selected? (CodeRabbit dashboard)
3. Did you push to branch? (CodeRabbit reviews on push)
4. Check PR comments for status

**Fix:**
- Reinstall CodeRabbit app
- Check CodeRabbit dashboard for errors
- Try creating new PR

#### "Too Many/Little Reviews"

**Adjust:**
- Edit `.coderabbit.yaml`
- Change `severity` levels
- Add/remove `focus_areas`

### Environment Issues

#### "Wrong Supabase Project Connected"

**Check:**
- Vercel environment variables
- Local `.env.local` file
- Which Vercel project you're looking at

**Fix:**
- Verify environment variables in Vercel
- Check local `.env.local`
- Use switch script: `./scripts/switch_env.sh sandbox`

#### "Schema Mismatch"

**Problem:** Code works in dev but breaks in prod

**Solution:**
- Keep schemas identical
- Apply schema changes to both environments
- Test in dev before production

#### "Vercel Deployed Wrong Branch"

**Check:**
- Vercel project settings → Git → Production Branch
- Make sure it matches intended branch

**Fix:**
- Update Production Branch setting in Vercel
- Redeploy if needed

---

## Quick Reference

### URLs

**Production:**
- Dashboard: `https://benchsight.vercel.app`
- Supabase: `https://your-project.supabase.co` (main branch)
- Config: `config_local.ini` (default, no switching needed)

**Development:**
- Dashboard: `https://benchsight-dev.vercel.app`
- Supabase: `https://your-project-branch-ref.supabase.co` (develop branch)
- Config: `config_local.develop.ini` (switch to this for dev)

**Local:**
- Dashboard: `http://localhost:3000`
- Supabase: Uses develop branch (via .env.local)

### Commands

```bash
# Git
git checkout develop              # Switch to dev branch
git checkout -b feature/new-feat  # Create feature branch
git push origin feature/new-feat # Push branch

# Environment
./scripts/switch_env.sh sandbox    # Switch to dev
./scripts/switch_env.sh production # Switch to prod

# Development
cd ui/dashboard && npm run dev     # Start dashboard
python run_etl.py                  # Run ETL
python validate.py                 # Validate data
```

### Checklist

**Initial Setup:**
- [ ] GitHub repository created
- [ ] Local repo connected to GitHub
- [ ] `main` and `develop` branches created
- [ ] Production Supabase project created
- [ ] Dev Supabase project created
- [ ] Production Vercel project created (connected to `main`)
- [ ] Dev Vercel project created (connected to `develop`)
- [ ] Environment variables set in both Vercel projects
- [ ] Local environment files created
- [ ] CodeRabbit app installed
- [ ] Test PR created and CodeRabbit reviewed

**Daily Workflow:**
- [ ] Working on feature branch
- [ ] Testing locally with dev config
- [ ] CodeRabbit review addressed
- [ ] Tested on dev Vercel URL
- [ ] Ready for production merge

---

## Next Steps

1. **Complete initial setup** following this guide
2. **Create your first feature branch** and try the workflow
3. **Get familiar with CodeRabbit** feedback
4. **Test the full pipeline** with a small change
5. **Document your URLs** and credentials securely

---

## Additional Resources

- **Dev Environment Setup:** [DEV_ENVIRONMENT_SETUP.md](DEV_ENVIRONMENT_SETUP.md) ⭐ **Start here for dev setup**
- **Supabase Branching:** [SUPABASE_BRANCHING.md](SUPABASE_BRANCHING.md) - Supabase branching details
- **Running ETL to Dev:** [RUN_ETL_TO_DEV.md](RUN_ETL_TO_DEV.md) - ETL workflow
- **Git/GitHub:** [GIT_GITHUB_GUIDE.md](GIT_GITHUB_GUIDE.md)
- **CodeRabbit:** [CODERABBIT_SETUP.md](CODERABBIT_SETUP.md)
- **Environment Variables:** [ENVIRONMENT_VARIABLES_EXPLAINED.md](ENVIRONMENT_VARIABLES_EXPLAINED.md)
- **Branch Strategy:** [BRANCH_STRATEGY_QUICK_REFERENCE.md](BRANCH_STRATEGY_QUICK_REFERENCE.md)
- **Industry Standards:** [INDUSTRY_STANDARDS_WORKFLOW.md](INDUSTRY_STANDARDS_WORKFLOW.md) ⭐

---

*Last updated: 2026-01-13*
