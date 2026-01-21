# Development Sandbox Setup Guide

**Complete guide for setting up separate dev/sandbox environments for Supabase and Vercel**

---

## Overview

This guide shows you how to:
1. **Create separate Supabase projects** (dev vs production)
2. **Set up separate Vercel projects** (dev vs production)
3. **Use GitHub branches** to connect code to different environments
4. **Work safely** without breaking production

---

## Why Separate Environments?

**Production** = Your live site that users see
- Must always work
- Never break it
- Test everything first

**Development/Sandbox** = Your testing playground
- Try new features safely
- Break things without consequences
- Test before deploying to production

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GITHUB REPOSITORY                        │
│                                                              │
│  main branch ──────────────► Production (Vercel + Supabase)│
│  develop branch ────────────► Dev (Vercel + Supabase)       │
│  feature/* branches ────────► Local development             │
└─────────────────────────────────────────────────────────────┘
```

---

## Step 1: Create Supabase Projects

### 1.1: Production Supabase Project

**If you already have one, skip this step.**

1. Go to: https://supabase.com/dashboard
2. Click **"New Project"**
3. Fill in:
   - **Name:** `benchsight-production`
   - **Database Password:** (save this securely!)
   - **Region:** Choose closest to your users
4. Click **"Create new project"**
5. Wait for setup (~2 minutes)
6. **Save credentials:**
   - Go to **Settings** → **API**
   - Copy **Project URL** and **anon public** key
   - Save in a secure place (password manager)

### 1.2: Development/Sandbox Supabase Project

1. Go to: https://supabase.com/dashboard
2. Click **"New Project"**
3. Fill in:
   - **Name:** `benchsight-dev` (or `benchsight-sandbox`)
   - **Database Password:** (can be simpler, it's just for dev)
   - **Region:** Same as production (for consistency)
4. Click **"Create new project"**
5. Wait for setup (~2 minutes)
6. **Save credentials:**
   - Go to **Settings** → **API**
   - Copy **Project URL** and **anon public** key
   - Save separately from production credentials

### 1.3: Set Up Dev Database Schema

**Option A: Copy from Production (Recommended)**
```bash
# Export schema from production
# In Supabase Dashboard → SQL Editor, run:
# Copy the contents of sql/setup_supabase.sql

# Then in dev project → SQL Editor, paste and run
```

**Option B: Run ETL to Dev**
```bash
# Update config/config_local.ini with dev Supabase URL
# Run ETL
python run_etl.py

# Upload to dev Supabase
python upload.py
```

---

## Step 2: Set Up Vercel Projects

### 2.1: Production Vercel Project

**If you already have one, skip this step.**

1. Go to: https://vercel.com/dashboard
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Configure:
   - **Project Name:** `benchsight-production`
   - **Root Directory:** `ui/dashboard`
   - **Framework:** Next.js
5. **Environment Variables:**
   - `NEXT_PUBLIC_SUPABASE_URL` = Production Supabase URL
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY` = Production anon key
6. **Branch:** `main` (production branch)
7. Click **"Deploy"**

### 2.2: Development Vercel Project

1. Go to: https://vercel.com/dashboard
2. Click **"Add New..."** → **"Project"**
3. Import the **same** GitHub repository
4. Configure:
   - **Project Name:** `benchsight-dev` (or `benchsight-sandbox`)
   - **Root Directory:** `ui/dashboard`
   - **Framework:** Next.js
5. **Environment Variables:**
   - `NEXT_PUBLIC_SUPABASE_URL` = Dev Supabase URL
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY` = Dev anon key
6. **Branch:** `develop` (development branch)
7. Click **"Deploy"**

**Important:** Vercel will auto-deploy when you push to the configured branch!

---

## Step 3: Set Up GitHub Branch Strategy

### 3.1: Branch Structure

```
main          → Production (stable, tested code)
develop       → Development (integration branch)
feature/*     → Individual features
fix/*         → Bug fixes
```

### 3.2: Create Branches

```bash
# Make sure you're on main and it's up to date
git checkout main
git pull origin main

# Create develop branch
git checkout -b develop
git push -u origin develop
```

### 3.3: Configure Branch Protection (Optional but Recommended)

**For Production (main branch):**
1. Go to GitHub → Your repo → **Settings** → **Branches**
2. Add rule for `main`:
   - ✅ Require pull request before merging
   - ✅ Require approvals (1 person)
   - ✅ Require status checks to pass (if you have CI)

**For Development (develop branch):**
- Usually less strict, but you can require PRs if you want

---

## Step 4: Local Development Setup

### 4.1: Create Environment Files

**Production config (for reference):**
```bash
# config/config_local.production.ini
[supabase]
url = https://your-prod-project.supabase.co
service_key = your-prod-service-key
```

**Development config:**
```bash
# config/config_local.dev.ini
[supabase]
url = https://your-dev-project.supabase.co
service_key = your-dev-service-key
```

**Dashboard environment files:**

**Production:**
```bash
# ui/dashboard/.env.local.production
NEXT_PUBLIC_SUPABASE_URL=https://your-prod-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-prod-anon-key
```

**Development:**
```bash
# ui/dashboard/.env.local.dev
NEXT_PUBLIC_SUPABASE_URL=https://your-dev-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-dev-anon-key
```

### 4.2: Use the Switch Script

You already have a script! Use it:

```bash
# Switch to dev environment
./scripts/switch_env.sh sandbox

# Switch to production (be careful!)
./scripts/switch_env.sh production
```

**Or manually:**
```bash
# For dev
cp config/config_local.dev.ini config/config_local.ini
cp ui/dashboard/.env.local.dev ui/dashboard/.env.local

# For production
cp config/config_local.production.ini config/config_local.ini
cp ui/dashboard/.env.local.production ui/dashboard/.env.local
```

---

## Step 5: Workflow Examples

### Scenario 1: Adding a New Feature

```bash
# 1. Start from develop branch
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/add-player-ratings

# 3. Make changes locally
# ... edit files ...

# 4. Test locally (connected to dev Supabase)
npm run dev  # in ui/dashboard

# 5. Commit and push
git add .
git commit -m "Add player ratings feature"
git push origin feature/add-player-ratings

# 6. Create PR: feature/add-player-ratings → develop
# 7. Review and merge to develop
# 8. Vercel auto-deploys develop to dev environment
# 9. Test on dev Vercel URL
# 10. If good, create PR: develop → main
# 11. Review and merge to main
# 12. Vercel auto-deploys main to production
```

### Scenario 2: Hotfix (Urgent Production Bug)

```bash
# 1. Start from main (production)
git checkout main
git pull origin main

# 2. Create hotfix branch
git checkout -b fix/critical-bug

# 3. Fix the bug
# ... edit files ...

# 4. Test locally (switch to production config temporarily)
./scripts/switch_env.sh production
# ... test ...
./scripts/switch_env.sh sandbox  # Switch back

# 5. Commit and push
git add .
git commit -m "Fix critical production bug"
git push origin fix/critical-bug

# 6. Create PR: fix/critical-bug → main
# 7. Fast-track review and merge
# 8. Also merge to develop (so dev has the fix too)
git checkout develop
git merge main
git push origin develop
```

### Scenario 3: Daily Development

```bash
# Morning: Get latest changes
git checkout develop
git pull origin develop

# Work on feature
git checkout -b feature/my-feature
# ... work ...

# End of day: Push and create PR
git push origin feature/my-feature
# Create PR on GitHub
```

---

## Step 6: Vercel Branch Configuration

### 6.1: Production Project Settings

1. Go to Vercel → `benchsight-production` → **Settings** → **Git**
2. **Production Branch:** `main`
3. **Preview Branches:** Leave default (all branches get previews)

### 6.2: Development Project Settings

1. Go to Vercel → `benchsight-dev` → **Settings** → **Git**
2. **Production Branch:** `develop`
3. **Preview Branches:** All other branches

**Result:**
- Pushing to `main` → Deploys to production Vercel
- Pushing to `develop` → Deploys to dev Vercel
- Pushing to `feature/*` → Creates preview deployment

---

## Step 7: Environment Variables Management

### 7.1: Vercel Environment Variables

**Production Project:**
- Set variables for **Production** environment only
- Or set for **Production, Preview, Development** (they'll use same values)

**Development Project:**
- Set variables for **Production** environment (which maps to `develop` branch)
- Use dev Supabase credentials

### 7.2: Local Development

Use `.env.local` files (already in `.gitignore`):
- `ui/dashboard/.env.local` - Your current active config
- `ui/dashboard/.env.local.dev` - Dev backup
- `ui/dashboard/.env.local.production` - Prod backup

---

## Step 8: Testing Workflow

### 8.1: Local Testing
```bash
# Switch to dev
./scripts/switch_env.sh sandbox

# Run dashboard
cd ui/dashboard
npm run dev

# Test at http://localhost:3000
```

### 8.2: Dev Environment Testing
```bash
# Push to develop branch
git push origin develop

# Vercel auto-deploys
# Test at: https://benchsight-dev.vercel.app
```

### 8.3: Production Testing
```bash
# Only after thorough testing in dev!
# Push to main branch
git push origin main

# Vercel auto-deploys
# Test at: https://benchsight-production.vercel.app
```

---

## Recommended Branch Strategy

### Branch Types

| Branch | Purpose | Deploys To | When to Use |
|--------|---------|------------|-------------|
| `main` | Production-ready code | Production Vercel + Supabase | Stable, tested features |
| `develop` | Integration branch | Dev Vercel + Supabase | Features ready for testing |
| `feature/*` | New features | Preview Vercel (optional) | Active development |
| `fix/*` | Bug fixes | Depends on severity | Fixing issues |

### Branch Naming

**Features:**
```bash
feature/add-ml-predictions
feature/improve-dashboard-ui
feature/add-player-comparison
```

**Fixes:**
```bash
fix/goal-counting-bug
fix/etl-memory-issue
fix/dashboard-loading-error
```

**Hotfixes (production):**
```bash
hotfix/critical-data-bug
hotfix/security-patch
```

---

## Quick Reference

### Switch Environments Locally
```bash
./scripts/switch_env.sh sandbox    # Dev
./scripts/switch_env.sh production # Production (careful!)
```

### Branch Workflow
```bash
git checkout develop              # Switch to dev branch
git checkout -b feature/new-feat  # Create feature branch
git push origin feature/new-feat # Push feature
# Create PR on GitHub
```

### Deploy to Dev
```bash
git checkout develop
git merge feature/my-feature
git push origin develop
# Vercel auto-deploys
```

### Deploy to Production
```bash
git checkout main
git merge develop
git push origin main
# Vercel auto-deploys
```

---

## Important: How Environment Variables Work

**Key Point:** Your code doesn't hardcode which Supabase project to use. It reads from environment variables that are set separately in each Vercel project.

**This means:**
- ✅ Committing to `main` won't break production
- ✅ Same code works with different Supabase projects
- ✅ Each Vercel project has its own environment variables

**The only risk:** If dev and prod Supabase databases have different schemas (different tables/views), code might work in dev but break in prod.

**Solution:** Keep schemas in sync! See [ENVIRONMENT_VARIABLES_EXPLAINED.md](ENVIRONMENT_VARIABLES_EXPLAINED.md) for complete details.

---

## Troubleshooting

### "Vercel deployed wrong branch"
- Check Vercel project settings → Git → Production Branch
- Make sure it matches your intended branch

### "Wrong Supabase project connected"
- Check environment variables in Vercel
- Verify you're looking at the right Vercel project
- Check local `.env.local` file

### "Changes not showing in dev"
- Make sure you pushed to `develop` branch
- Check Vercel deployment logs
- Verify environment variables are set

### "Accidentally pushed to main"
```bash
# If you haven't merged yet, you can:
git checkout main
git reset --hard origin/main  # Reset to remote state
# Or create a revert commit
```

---

## Best Practices

### ✅ Do
- Always test in dev before production
- Use feature branches for new work
- Keep `main` branch stable
- Review PRs before merging
- Use descriptive branch names
- Commit often with clear messages

### ❌ Don't
- Push directly to `main` (use PRs)
- Skip testing in dev
- Mix multiple features in one branch
- Use production credentials in dev
- Force push to shared branches

---

## Checklist

### Initial Setup
- [ ] Created production Supabase project
- [ ] Created dev Supabase project
- [ ] Set up production Vercel project (connected to `main`)
- [ ] Set up dev Vercel project (connected to `develop`)
- [ ] Created `develop` branch in GitHub
- [ ] Configured environment variables in both Vercel projects
- [ ] Created local environment files (`.env.local.dev`, `.env.local.production`)

### Daily Workflow
- [ ] Working on feature branch
- [ ] Testing locally with dev config
- [ ] Pushing to feature branch
- [ ] Creating PR to `develop`
- [ ] Testing on dev Vercel URL
- [ ] Merging to `develop` when ready
- [ ] Creating PR to `main` when stable
- [ ] Testing on production Vercel URL
- [ ] Merging to `main` when approved

---

## Next Steps

1. **Set up your environments** following this guide
2. **Read [ENVIRONMENT_VARIABLES_EXPLAINED.md](ENVIRONMENT_VARIABLES_EXPLAINED.md)** to understand how the same code works with different Supabase projects
3. **Create your first feature branch** and try the workflow
4. **Test the deployment pipeline** with a small change
5. **Keep schemas in sync** between dev and prod Supabase projects
6. **Document your URLs:**
   - Production: `https://benchsight-production.vercel.app`
   - Dev: `https://benchsight-dev.vercel.app`

**For complete setup including GitHub, CodeRabbit, and environments together, see: [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)**

---

*Last updated: 2026-01-13*
