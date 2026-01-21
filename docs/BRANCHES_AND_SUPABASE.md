# Git Branches vs Supabase Projects

**Understanding how branches connect to Supabase projects**

---

## Quick Answer

**You can't create "branches" in Supabase**, but you can:
1. ✅ **Create a new Git branch** (for code)
2. ✅ **Use the same Supabase project** for multiple branches (via environment variables)
3. ✅ **Create a new Supabase project** for a new environment

---

## How It Works

### Git Branches ≠ Supabase Projects

**Git Branches:**
- Code version control
- Created in your GitHub repository
- Examples: `main`, `develop`, `feature/add-ratings`

**Supabase Projects:**
- Separate database instances
- Created in Supabase dashboard
- Examples: `benchsight-production`, `benchsight-dev`

### How They Connect

Branches connect to Supabase projects via **environment variables**:

```
Git Branch → Vercel Project → Environment Variables → Supabase Project
```

**Example:**
- `main` branch → `benchsight-production` Vercel → Production env vars → `benchsight-production` Supabase
- `develop` branch → `benchsight-dev` Vercel → Dev env vars → `benchsight-dev` Supabase

---

## Options for New Branches

### Option 1: Use Existing Supabase Project (Quick & Simple)

**When to use:**
- Testing small changes
- Personal development
- Quick experiments

**How it works:**
- Create new Git branch
- Use same environment variables (points to same Supabase)
- All branches share the same database

**Setup:**
```bash
# Create branch
git checkout -b feature/my-feature

# Use existing environment (dev Supabase)
./scripts/switch_env.sh sandbox

# Work normally
cd ui/dashboard && npm run dev
```

**Pros:**
- ✅ Quick setup
- ✅ No new Supabase project needed
- ✅ Easy to test

**Cons:**
- ❌ All branches share same data
- ❌ Can't test schema changes safely
- ❌ Risk of data conflicts

### Option 2: Create New Supabase Project (Recommended for Important Work)

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

**Setup:**

1. **Create Supabase Project:**
   - Go to https://supabase.com/dashboard
   - Click "New Project"
   - Name: `benchsight-feature-ratings` (or your feature name)
   - Wait for setup

2. **Set Up Schema:**
   ```bash
   # Copy schema from dev/prod
   # In Supabase SQL Editor, run your setup SQL
   # Or run ETL to populate
   ```

3. **Update Local Environment:**
   ```bash
   # Create new env file
   cd ui/dashboard
   cat > .env.local.feature-ratings << EOF
   NEXT_PUBLIC_SUPABASE_URL=https://your-new-project.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-new-anon-key
   EOF
   
   # Use it
   cp .env.local.feature-ratings .env.local
   ```

4. **Work on Branch:**
   ```bash
   git checkout -b feature/add-ratings
   # ... work ...
   ```

**Pros:**
- ✅ Isolated database
- ✅ Safe to test schema changes
- ✅ No data conflicts
- ✅ Can experiment freely

**Cons:**
- ❌ More setup time
- ❌ Another project to manage
- ❌ Need to sync schema

### Option 3: Use Dev Supabase Project (Recommended Default)

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
./scripts/switch_env.sh sandbox

# Work normally
cd ui/dashboard && npm run dev
```

**This is the recommended approach!**

---

## Recommended Workflow

### For Most Features

```bash
# 1. Create branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/my-feature

# 2. Use dev Supabase (already set up)
./scripts/switch_env.sh sandbox

# 3. Work locally
cd ui/dashboard && npm run dev
# Connects to: benchsight-dev Supabase

# 4. Push and create PR
git push origin feature/my-feature
# PR: feature/my-feature → develop

# 5. When merged to develop
# Vercel auto-deploys to dev environment
# Uses: benchsight-dev Supabase
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
# 7. Apply schema changes to dev Supabase
# 8. Switch to using dev Supabase
```

---

## Current Setup (What You Have)

Based on the setup guide, you should have:

**Supabase Projects:**
- `benchsight-production` - Production database
- `benchsight-dev` - Development database

**Vercel Projects:**
- `benchsight-production` - Connected to `main` branch → Uses production Supabase
- `benchsight-dev` - Connected to `develop` branch → Uses dev Supabase

**Git Branches:**
- `main` → Production Vercel → Production Supabase
- `develop` → Dev Vercel → Dev Supabase
- `feature/*` → Local development → Dev Supabase (recommended)

---

## Common Scenarios

### Scenario 1: Quick Feature Branch

**Question:** "I want to add a small feature, can I just create a branch?"

**Answer:** Yes! Use the dev Supabase project:

```bash
git checkout -b feature/small-feature
./scripts/switch_env.sh sandbox
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

---

## Best Practices

### ✅ Do This

1. **Use dev Supabase for feature branches**
   - Most common workflow
   - Safe and simple
   - Easy to coordinate

2. **Create new Supabase project for major changes**
   - Schema changes
   - Major refactoring
   - Production-like testing

3. **Keep schemas in sync**
   - Dev and prod should match
   - Apply changes to both
   - Document schema changes

### ❌ Don't Do This

1. **Don't use production Supabase for development**
   - Risk of breaking production
   - Data contamination
   - Hard to test safely

2. **Don't create too many Supabase projects**
   - Hard to manage
   - Schema drift
   - Cost (if on paid plan)

3. **Don't forget to sync schemas**
   - Dev and prod must match
   - Test in dev first
   - Apply to prod when ready

---

## Quick Reference

### Create Branch Using Dev Supabase (Recommended)

```bash
git checkout develop
git checkout -b feature/my-feature
./scripts/switch_env.sh sandbox
# Uses: benchsight-dev Supabase
```

### Create Branch with New Supabase Project

```bash
# 1. Create Supabase project
# 2. Set up schema
# 3. Create branch
git checkout -b feature/major-feature
# 4. Update .env.local with new project
```

### Check Which Supabase You're Using

```bash
# Check environment file
cat ui/dashboard/.env.local

# Should show:
# NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
```

---

## Summary

**Git Branches:**
- ✅ Create as many as you want
- ✅ Use for code version control
- ✅ Connect to Supabase via environment variables

**Supabase Projects:**
- ❌ Can't create "branches" in Supabase
- ✅ Can create new projects for new environments
- ✅ Recommended: Use `benchsight-dev` for most feature branches

**Recommended Workflow:**
1. Create Git branch from `develop`
2. Use existing `benchsight-dev` Supabase project
3. Work locally
4. Create PR to `develop`
5. When merged, deploy to dev environment

---

## Questions?

- **"Can I use the same Supabase for multiple branches?"** → Yes! That's the recommended approach.
- **"Do I need a new Supabase project for each branch?"** → No, only for major features or schema testing.
- **"Which Supabase should I use?"** → Use `benchsight-dev` for most work.

---

*Last updated: 2026-01-13*
