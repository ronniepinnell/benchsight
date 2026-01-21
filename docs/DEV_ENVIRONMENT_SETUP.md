# Development Environment Setup

**Complete guide: GitHub dev branch → Supabase dev branch → Vercel dev**

---

## Overview

This guide sets up a clean, integrated development workflow:

```
GitHub develop branch → Supabase develop branch → Vercel dev project
```

**Benefits:**
- ✅ One Supabase project with branches (not separate projects)
- ✅ Automatic branch creation from GitHub PRs (optional)
- ✅ Vercel previews automatically connect to Supabase branches
- ✅ Clean, maintainable workflow
- ✅ Easy schema merging

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GITHUB REPOSITORY                        │
│                                                              │
│  main branch ──────────────► Production                    │
│  develop branch ────────────► Development                   │
│  feature/* branches ────────► Feature work                  │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Supabase        │  │ Supabase        │  │ Supabase        │
│ main branch     │  │ develop branch  │  │ feature branch  │
│ (Production)    │  │ (Dev)           │  │ (Auto-created)  │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                    │                    │
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Vercel          │  │ Vercel          │  │ Vercel          │
│ Production      │  │ Dev             │  │ Preview         │
│ (main branch)   │  │ (develop)       │  │ (feature/*)     │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## Step 1: Set Up Supabase Branching

### 1.1: Enable Branching in Supabase

1. **Go to Supabase Dashboard:**
   - Visit: https://supabase.com/dashboard
   - Select your main project

2. **Check for Branching:**
   - Look for **"Branches"** in the left sidebar
   - If you see it, branching is available!

3. **Note:** Branching requires:
   - Supabase Pro plan or above
   - Or may be in beta/early access

### 1.2: Create Develop Branch

1. **Go to Branches:**
   - Click **"Branches"** in sidebar
   - You'll see your main branch listed

2. **Create Develop Branch:**
   - Click **"New Branch"** or **"Create Branch"**
   - **Name:** `develop`
   - **Source:** `main` (or your production branch)
   - Click **"Create"**

3. **Wait for Setup:**
   - Branch creation takes 1-2 minutes
   - You'll get a new database with same schema as main
   - Branch gets its own URL and credentials

4. **Get Branch Credentials:**
   - Select the `develop` branch
   - Go to **Settings** → **API**
   - Copy:
     - **Project URL** (branch-specific URL)
     - **anon public** key (usually same as main)
     - **service_role** key (for ETL/uploads)

### 1.3: (Optional) Enable GitHub Integration

**For automatic branch creation from PRs:**

1. **Connect GitHub:**
   - Go to Supabase → Settings → Integrations
   - Click **"Connect GitHub"**
   - Authorize and select your repository

2. **Configure Auto-Branching:**
   - Enable **"Automatic branch creation"**
   - Choose which branches trigger Supabase branches
   - Set migration path (if using Supabase CLI)

**Benefits:**
- Opening a PR automatically creates a Supabase branch
- Vercel previews automatically connect to the branch
- Merging PR applies changes and deletes branch

---

## Step 2: Set Up Vercel Dev Project

### 2.1: Create Vercel Dev Project

1. **Go to Vercel:**
   - Visit: https://vercel.com/dashboard
   - Sign in with GitHub

2. **Create New Project:**
   - Click **"Add New..."** → **"Project"**
   - Find your **"benchsight"** repository
   - Click **"Import"**

3. **Configure Dev Project:**
   - **Project Name:** `benchsight-dev`
   - **Framework Preset:** Next.js (auto-detected)
   - **Root Directory:** `ui/dashboard`
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`
   - **Install Command:** `npm install`

4. **Set Production Branch:**
   - **Production Branch:** `develop`
   - This means: pushing to `develop` → deploys to dev Vercel

5. **Click "Deploy"**

### 2.2: Configure Environment Variables

1. **Go to Project Settings:**
   - Vercel → `benchsight-dev` → **Settings** → **Environment Variables**

2. **Add Supabase Develop Branch Credentials:**
   - **Name:** `NEXT_PUBLIC_SUPABASE_URL`
   - **Value:** Your Supabase develop branch URL
   - **Environment:** Production, Preview, Development (all)

3. **Add Anon Key:**
   - **Name:** `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - **Value:** Your Supabase develop branch anon key
   - **Environment:** Production, Preview, Development (all)

4. **Save and Redeploy:**
   - Go to **Deployments** tab
   - Click **"..."** on latest deployment → **"Redeploy"**

### 2.3: (Optional) Install Supabase Vercel Integration

**For automatic branch linking:**

1. **Install Integration:**
   - Vercel → Project → Settings → Integrations
   - Find **"Supabase"** integration
   - Click **"Add"**

2. **Connect Supabase:**
   - Select your Supabase project
   - Authorize connection

3. **Benefits:**
   - Vercel automatically gets branch credentials
   - Preview deployments link to correct Supabase branch
   - No manual environment variable updates needed

---

## Step 3: Set Up Local Development

### 3.1: Create Local Environment Files

```bash
# Create dev environment file
cd ui/dashboard
cat > .env.local.dev << EOF
NEXT_PUBLIC_SUPABASE_URL=https://your-develop-branch.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-develop-anon-key
EOF
```

**Get credentials from:**
- Supabase Dashboard → Branches → develop → Settings → API

### 3.2: Create ETL Config for Dev

```bash
# Create dev ETL config
cp config/config_local.ini config/config_local.develop.ini

# Edit with develop branch credentials
nano config/config_local.develop.ini
```

**Update the Supabase section:**
```ini
[supabase]
url = https://your-develop-branch.supabase.co
service_key = your-develop-service-role-key
anon_key = your-develop-anon-key
```

### 3.3: Update Switch Script

The switch script should work, but verify it handles the develop branch:

```bash
# Test switching
./scripts/switch_env.sh sandbox
# Should copy config_local.develop.ini → config_local.ini
```

---

## Step 4: Set Up GitHub Branch

### 4.1: Create Develop Branch in GitHub

```bash
# Make sure you're on main
git checkout main
git pull origin main

# Create develop branch
git checkout -b develop
git push -u origin develop
```

### 4.2: Configure Branch Protection (Optional)

1. **Go to GitHub:**
   - Repository → Settings → Branches

2. **Add Rule for `develop`:**
   - Branch name pattern: `develop`
   - ✅ Require pull request before merging
   - ✅ Require approvals (optional, 1 person)
   - ✅ Require status checks (if you have CI)

---

## Complete Workflow

### Daily Development

```bash
# 1. Start from develop
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/my-feature

# 3. Switch to dev environment locally
./scripts/switch_env.sh sandbox

# 4. Work locally
cd ui/dashboard && npm run dev
# Connects to Supabase develop branch

# 5. Run ETL to dev (if needed)
python run_etl.py
python upload.py
# Uploads to Supabase develop branch

# 6. Commit and push
git add .
git commit -m "feat: add new feature"
git push origin feature/my-feature

# 7. Create PR: feature/my-feature → develop
# If GitHub integration enabled:
#   - Supabase auto-creates feature branch
#   - Vercel creates preview deployment
#   - Preview connects to Supabase feature branch

# 8. Test on preview URL
# 9. Merge PR to develop
# 10. Vercel auto-deploys develop → dev Vercel
# 11. Uses Supabase develop branch
```

### Deploying to Production

```bash
# 1. When develop is stable
git checkout main
git pull origin main

# 2. Merge develop to main
git merge develop
git push origin main

# 3. Merge Supabase develop branch to main
# In Supabase Dashboard:
#   - Go to Branches
#   - Select develop branch
#   - Click "Merge" or "Promote"
#   - Target: main branch

# 4. Vercel auto-deploys main → production
# 5. Uses Supabase main branch
```

---

## Environment Mapping

| Git Branch | Supabase Branch | Config File | Vercel Project | Purpose |
|------------|----------------|-------------|----------------|---------|
| `main` | `main` | `config_local.ini` | `benchsight` | Production |
| `develop` | `develop` | `config_local.develop.ini` | `benchsight-dev` | Development |
| `feature/*` | `develop` (or auto-created) | Uses dev config | Preview (auto) | Feature work |

---

## Running ETL to Dev

### Quick Commands

```bash
# 1. Switch to dev
./scripts/switch_env.sh sandbox

# 2. Verify you're on dev
cat config/config_local.ini | grep url
# Should show develop branch URL

# 3. Run ETL
python run_etl.py

# 4. Upload to Supabase develop branch
python upload.py
```

### Detailed Steps

See [RUN_ETL_TO_DEV.md](RUN_ETL_TO_DEV.md) for complete ETL guide.

---

## Vercel Branch Configuration

### Dev Project Settings

**Vercel → benchsight-dev → Settings → Git:**

- **Production Branch:** `develop`
- **Preview Branches:** All other branches

**Result:**
- Pushing to `develop` → Deploys to dev Vercel
- Pushing to `feature/*` → Creates preview deployment
- Preview can auto-connect to Supabase feature branch (if integration enabled)

### Using Active Branch for Dev

**Yes! You can use the active branch for dev:**

1. **Set Production Branch to `develop`:**
   - This makes `develop` the "production" branch for the dev project
   - Pushing to `develop` triggers deployment

2. **Preview Deployments:**
   - Other branches get preview deployments
   - Each preview can connect to its own Supabase branch

3. **Benefits:**
   - Clean separation: dev project uses develop branch
   - Feature branches get isolated previews
   - Automatic deployments

---

## Troubleshooting

### "Supabase branching not available"

**Check:**
- Do you have Supabase Pro plan?
- Is feature in beta/early access?
- Contact Supabase support

**Alternative:**
- Use separate Supabase projects (see old docs)
- Less integrated but works

### "Vercel not connecting to Supabase branch"

**Check:**
- Environment variables set correctly?
- Using branch URL (not main project URL)?
- Integration installed?

**Fix:**
- Verify environment variables in Vercel
- Use Supabase branch URL (not main project URL)
- Install Supabase Vercel integration

### "ETL uploading to wrong Supabase"

**Check:**
```bash
cat config/config_local.ini | grep url
```

**Fix:**
```bash
./scripts/switch_env.sh sandbox
# Verify it shows develop branch URL
```

---

## Best Practices

### ✅ Do This

1. **Use Supabase branches** instead of separate projects
2. **Keep develop branch in sync** with main
3. **Test in develop** before merging to main
4. **Use feature branches** for all new work
5. **Merge Supabase branches** when merging Git branches

### ❌ Don't Do This

1. **Don't work directly on main** (use develop)
2. **Don't skip testing in develop**
3. **Don't let branches drift** (keep schemas in sync)
4. **Don't forget to merge Supabase branches** when deploying

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

### Commands

```bash
# Switch to dev
./scripts/switch_env.sh sandbox

# Run ETL to dev
python run_etl.py
python upload.py

# Check environment
cat config/config_local.ini | grep url

# Git workflow
git checkout develop
git checkout -b feature/my-feature
```

---

## Next Steps

1. **Set up Supabase develop branch** (Step 1)
2. **Configure Vercel dev project** (Step 2)
3. **Set up local development** (Step 3)
4. **Create GitHub develop branch** (Step 4)
5. **Test the workflow** with a small feature

---

## Related Documentation

- [SUPABASE_BRANCHING.md](SUPABASE_BRANCHING.md) - Supabase branching details
- [RUN_ETL_TO_DEV.md](RUN_ETL_TO_DEV.md) - Running ETL to dev
- [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md) - Complete setup
- [BRANCHES_AND_SUPABASE.md](BRANCHES_AND_SUPABASE.md) - Branch strategy

---

*Last updated: 2026-01-13*
