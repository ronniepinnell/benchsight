# Environments Guide

**Complete guide to dev/prod environments, branches, and Supabase**

Last Updated: 2026-01-21

---

## Quick Reference

| Environment | Config File | Supabase | Vercel | Git Branch |
|------------|-------------|----------|--------|------------|
| **Production** | `config_local.ini` | Main project | `benchsight` | `main` |
| **Dev** | `config_local.dev.ini` | Develop branch | `benchsight-dev` | `develop` |

---

## Branch Strategy

```
main (production)
  ↑
develop (dev/sandbox)
  ↑
feature/* (your work)
```

### Branch → Environment Mapping

| Branch | Vercel Project | Supabase Project | Use For |
|--------|---------------|------------------|---------|
| `main` | `benchsight-production` | `benchsight-production` | Live site |
| `develop` | `benchsight-dev` | `benchsight-dev` | Testing |
| `feature/*` | Preview (optional) | Local dev | Active work |

---

## Switching Environments

### To Dev
```bash
./benchsight.sh env switch dev
# Or: ./scripts/switch_env.sh dev
```

### To Production (careful!)
```bash
./benchsight.sh env switch production
# Or: ./scripts/switch_env.sh production
```

---

## Environment Variables

### How It Works

Your code doesn't hardcode which Supabase project to use. It reads from **environment variables**:

```typescript
// ui/dashboard/src/lib/supabase/client.ts
export function createClient() {
  return createBrowserClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,      // ← Reads from env var
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY! // ← Reads from env var
  )
}
```

### Vercel Configuration

**Production Vercel Project:**
- Connected to: `main` branch
- Environment Variables:
  - `NEXT_PUBLIC_SUPABASE_URL` = Production Supabase URL
  - `NEXT_PUBLIC_SUPABASE_ANON_KEY` = Production anon key

**Dev Vercel Project:**
- Connected to: `develop` branch
- Environment Variables:
  - `NEXT_PUBLIC_SUPABASE_URL` = Dev Supabase URL
  - `NEXT_PUBLIC_SUPABASE_ANON_KEY` = Dev anon key

### Local Configuration

**Dev:**
```bash
# Switch to dev
./scripts/switch_env.sh dev
# Uses: config_local.dev.ini and .env.local.dev
```

**Production:**
```bash
# Switch to production (careful!)
./scripts/switch_env.sh production
# Uses: config_local.ini and .env.local.production
```

---

## Git Branches vs Supabase Projects

### Key Concept

**Git Branches ≠ Supabase Projects**

- **Git Branches:** Code version control (main, develop, feature/*)
- **Supabase Projects:** Separate database instances (benchsight-production, benchsight-dev)

### How They Connect

```
Git Branch → Vercel Project → Environment Variables → Supabase Project
```

**Example:**
- `main` branch → `benchsight-production` Vercel → Production env vars → `benchsight-production` Supabase
- `develop` branch → `benchsight-dev` Vercel → Dev env vars → `benchsight-dev` Supabase

---

## Recommended Workflow

### For Most Features

```bash
# 1. Create branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/my-feature

# 2. Use dev Supabase (already set up)
./scripts/switch_env.sh dev

# 3. Work locally
cd ui/dashboard && npm run dev
# Connects to: benchsight-dev Supabase

# 4. Push and create PR
git push origin feature/my-feature
# PR: feature/my-feature → develop

# 5. When merged to develop
# Vercel auto-deploys to dev environment
```

### For Major Features (New Supabase Project)

```bash
# 1. Create new Supabase project
# 2. Set up schema
# 3. Create branch
git checkout -b feature/major-feature

# 4. Use new Supabase project
# Update .env.local with new project credentials

# 5. Work and test
# 6. When ready, merge to develop
```

---

## URLs

**Production:**
- Vercel: `https://benchsight.vercel.app`
- Supabase: Your main project URL

**Development:**
- Vercel: `https://benchsight-dev.vercel.app`
- Supabase: Your develop branch URL

**Local:**
- Dashboard: `http://localhost:3000`

---

## Schema Synchronization

### ⚠️ Critical: Keep Schemas in Sync

**Problem:** If dev and prod Supabase databases have different schemas, code might work in dev but break in prod.

**Solution:** Keep schemas identical between dev and prod.

### Workflow for Schema Changes

```bash
# 1. Test in dev first
./scripts/switch_env.sh dev
# Apply schema changes in dev Supabase
# Test dashboard locally

# 2. When ready, apply to production
./scripts/switch_env.sh production
# Apply same schema changes in production Supabase
# Test on production Vercel URL
```

---

## Branch Naming

```bash
feature/add-player-ratings    # New feature
fix/goal-counting-bug         # Bug fix
hotfix/critical-security      # Urgent production fix
docs/update-readme            # Documentation
refactor/cleanup-stats        # Code improvement
```

## Common Commands

```bash
# Check current branch
git branch

# Switch branch
git checkout branch-name

# Create and switch to new branch
git checkout -b feature/new-feature

# See what changed
git status
git diff

# Commit changes
git add .
git commit -m "Description"

# Push branch
git push origin branch-name

# Update local branch
git pull origin branch-name

# Switch environment
./scripts/switch_env.sh dev
./scripts/switch_env.sh production

# Check environment
./benchsight.sh env status
```

## PR Workflow

1. **Create feature branch** → Work → Push
2. **Create PR** on GitHub: `feature/*` → `develop`
3. **Review** → Make changes if needed
4. **Merge** → Auto-deploys to dev Vercel
5. **Test** on dev URL
6. **Create PR**: `develop` → `main` (when ready)
7. **Review** → Merge → Auto-deploys to production

---

## Options for New Branches

### Option 1: Use Dev Supabase Project (Recommended Default)

**When to use:**
- Most feature development
- Standard workflow
- Team collaboration

**How it works:**
- Create new Git branch
- Use existing `benchsight-dev` Supabase project
- All feature branches share dev database
- Merge to `develop` when ready

**Setup:**
```bash
# Create branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/my-feature

# Use dev environment
./scripts/switch_env.sh dev

# Work normally
cd ui/dashboard && npm run dev
```

**This is the recommended approach!**

### Option 2: Create New Supabase Project

**When to use:**
- Major features
- Schema changes
- Production-like testing
- Team collaboration

**How it works:**
- Create new Git branch
- Create new Supabase project
- Set up new Vercel project (optional)
- Use new environment variables

**Pros:**
- ✅ Isolated database
- ✅ Safe to test schema changes
- ✅ No data conflicts
- ✅ Can experiment freely

**Cons:**
- ❌ More setup time
- ❌ Another project to manage
- ❌ Need to sync schema

## Common Scenarios

### Scenario 1: Quick Feature Branch

**Question:** "I want to add a small feature, can I just create a branch?"

**Answer:** Yes! Use the dev Supabase project:
```bash
git checkout -b feature/small-feature
./scripts/switch_env.sh dev
# Work normally - uses benchsight-dev Supabase
```

### Scenario 2: Testing Schema Changes

**Question:** "I need to test database schema changes safely"

**Answer:** Create a new Supabase project:
1. Create new Supabase project
2. Copy schema from dev
3. Test your changes
4. When ready, apply to dev Supabase

### Scenario 3: Multiple People Working

**Question:** "Can multiple people work on different branches?"

**Answer:** Yes, they can all use the same dev Supabase:
- Everyone uses `benchsight-dev` Supabase
- Each person has their own Git branch
- All branches point to same database
- Coordinate if making schema changes

### Scenario 4: Production Hotfix

**Question:** "I need to fix production urgently"

**Answer:** Use production Supabase carefully:
```bash
git checkout main
git checkout -b hotfix/critical-bug
./scripts/switch_env.sh production  # ⚠️ Be careful!
# Test locally with production config
# Fix bug
# Create PR: hotfix → main
```

## Troubleshooting

**Wrong environment?**
- Check Vercel project settings → Git → Production Branch
- Check environment variables
- Check local `.env.local` file

**Changes not showing?**
- Verify you pushed to correct branch
- Check Vercel deployment logs
- Restart local dev server

**Need to undo?**
```bash
git reset --hard origin/branch-name  # Reset to remote state
```

## Safety Rules

✅ **DO:**
- Test in dev before production
- Use feature branches
- Review PRs before merging
- Keep main stable
- Keep schemas in sync
- Use dev Supabase for feature branches
- Create new Supabase project for major changes
- Keep schemas in sync

❌ **DON'T:**
- Push directly to main
- Skip testing
- Mix multiple features in one branch
- Use production credentials in dev
- Let dev and prod schemas drift apart
- Use production Supabase for development
- Create too many Supabase projects
- Forget to sync schemas

## Common Questions

**"Can I use the same Supabase for multiple branches?"**  
→ Yes! That's the recommended approach.

**"Do I need a new Supabase project for each branch?"**  
→ No, only for major features or schema testing.

**"Which Supabase should I use?"**  
→ Use `benchsight-dev` for most work.

**"If I commit code that queries a new table, will it break production?"**  
→ Only if the new table doesn't exist in production Supabase. Create the table in production before deploying.

**"Can I use different table names in dev vs prod?"**  
→ Technically yes, but strongly discouraged. Use the same schema, but different data.

**"What if I accidentally push dev credentials to production?"**  
→ Environment variables in Vercel are separate. Vercel uses the variables you set in the dashboard.

**"How do I know which environment I'm connected to?"**  
→ Check the Supabase URL in your environment variables.

---

*Last Updated: 2026-01-15*
