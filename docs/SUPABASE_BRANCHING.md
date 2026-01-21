# Using Supabase Branching for Dev/Test

**Guide to using Supabase's built-in branching feature for development and testing**

---

## What is Supabase Branching?

Supabase **branching** is a feature that lets you create isolated database branches from your main project. Think of it like Git branches, but for your database!

**Benefits:**
- ✅ Create isolated database copies for testing
- ✅ Test schema changes safely
- ✅ No need for separate Supabase projects
- ✅ Easy to create and delete branches
- ✅ Merge branches back to main
- ✅ Automatic branch creation from GitHub PRs (if integrated)
- ✅ Each branch has its own API credentials
- ✅ Ephemeral branches (auto-deleted) or persistent branches

---

## How Supabase Branching Works

### Concept

```
Main Database (Production)
    │
    ├── Branch: develop (Dev database)
    │   └── Test schema changes here
    │
    └── Branch: feature/add-ratings (Feature database)
        └── Test specific feature
```

### Features

1. **Isolated Databases** - Each branch is a separate database
2. **Schema Copy** - Branches start with same schema as main
3. **Independent Data** - Each branch has its own data
4. **Easy Cleanup** - Delete branches when done
5. **Merge Support** - Merge schema changes back to main

---

## Setting Up Supabase Branching

### Step 1: Enable Branching

**Check if available:**
1. Go to your Supabase project dashboard
2. Look for **"Branches"** in the left sidebar
3. If you see it, branching is available!

**Note:** Branching features:
- Available on Supabase Pro plan and above
- Can be linked to GitHub for automatic branch creation
- Supports both ephemeral (PR-based) and persistent branches

**Enable GitHub Integration (Recommended):**
1. Go to Supabase Dashboard → Settings → Integrations
2. Connect your GitHub repository
3. Enable automatic branch creation for PRs
4. Configure which branches trigger Supabase branches

### Step 2: Create a Development Branch

1. **Go to Branches:**
   - Supabase Dashboard → Your Project
   - Click **"Branches"** in sidebar

2. **Create Branch:**
   - Click **"New Branch"** or **"Create Branch"**
   - **Name:** `develop` (or `dev`)
   - **Source:** `main` (or your production branch)
   - Click **"Create"**

3. **Wait for Setup:**
   - Branch creation takes 1-2 minutes
   - You'll get a new database URL

### Step 3: Get Branch Credentials

1. **Select Your Branch:**
   - In Branches view, click on your branch
   - Or use branch selector in top bar

2. **Get Connection Info:**
   - Go to **Settings** → **API**
   - Copy:
     - **Project URL** (branch-specific)
     - **anon public** key (usually same as main)

3. **Save Credentials:**
   ```bash
   # Create env file for branch
   cd ui/dashboard
   cat > .env.local.develop << EOF
   NEXT_PUBLIC_SUPABASE_URL=https://your-branch-ref.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
   EOF
   ```

---

## Using Branches in Your Workflow

### Option 1: Single Dev Branch (Recommended)

**Setup:**
- Main branch = Production database
- `develop` branch = Development database

**Workflow:**
```bash
# 1. Create Git branch
git checkout -b feature/my-feature

# 2. Use Supabase develop branch
# Update .env.local to point to develop branch URL
./scripts/switch_env.sh sandbox  # Or manually update

# 3. Work normally
cd ui/dashboard && npm run dev
```

**Benefits:**
- ✅ One dev branch for all feature work
- ✅ Simple to manage
- ✅ Easy to coordinate with team
- ✅ Matches your Git branch strategy

### Option 2: Feature-Specific Branches

**Setup:**
- Main branch = Production
- `develop` branch = Integration testing
- Feature branches = Individual features

**Workflow:**
```bash
# 1. Create Supabase branch for feature
# In Supabase: Create branch "feature-add-ratings"

# 2. Create Git branch
git checkout -b feature/add-ratings

# 3. Use feature Supabase branch
# Update .env.local with feature branch URL

# 4. Work and test
# 5. When done, merge Supabase branch to develop
# 6. Delete feature Supabase branch
```

**Benefits:**
- ✅ Complete isolation per feature
- ✅ Safe for major schema changes
- ✅ Can test independently

**Drawbacks:**
- ❌ More branches to manage
- ❌ Need to sync schemas
- ❌ More setup time

---

## Recommended Setup for BenchSight

### Architecture

```
Supabase Project: benchsight-production
    │
    ├── Branch: main (Production database)
    │   └── Connected to: main Git branch → Production Vercel
    │
    ├── Branch: develop (Persistent dev database)
    │   └── Connected to: develop Git branch → Dev Vercel
    │       └── Used by: All feature/* Git branches
    │
    └── Branch: feature-* (Ephemeral, auto-created from PRs)
        └── Auto-created when PR opened
        └── Auto-deleted when PR merged/closed
        └── Used for: Testing specific features in isolation
```

### With GitHub Integration

If you enable GitHub integration:
- Opening a PR automatically creates a Supabase branch
- The branch gets its own database and API credentials
- Vercel preview deployments automatically use the branch
- Merging the PR applies changes to main and deletes the branch

### Step-by-Step Setup

1. **Create Develop Branch in Supabase:**
   ```
   Main Project → Branches → New Branch
   Name: develop
   Source: main
   ```

2. **Update Vercel Dev Project:**
   - Go to Vercel → `benchsight-dev` project
   - Settings → Environment Variables
   - Update `NEXT_PUBLIC_SUPABASE_URL` to develop branch URL

3. **Update Local Development:**
   ```bash
   # Update .env.local.dev with develop branch URL
   cd ui/dashboard
   nano .env.local.dev
   # Change URL to develop branch URL
   ```

4. **Work on Features:**
   ```bash
   git checkout -b feature/my-feature
   ./scripts/switch_env.sh sandbox
   # Uses Supabase develop branch automatically
   ```

---

## Branch Management

### Creating Branches

**In Supabase Dashboard:**
1. Go to **Branches**
2. Click **"New Branch"**
3. Enter name (e.g., `feature-add-ratings`)
4. Select source branch (usually `main` or `develop`)
5. Click **"Create"**

**Via Supabase CLI (if available):**
```bash
supabase branches create feature-add-ratings --source main
```

### Switching Branches

**In Supabase Dashboard:**
- Use branch selector in top bar
- Or go to Branches and click on branch

**In Your Code:**
- Update environment variables
- Point to branch-specific URL

### Merging Branches

**When to merge:**
- Feature branch → develop (when feature is ready)
- develop → main (when releasing to production)

**How to merge:**
1. Go to Supabase → Branches
2. Select source branch (e.g., `develop`)
3. Click **"Merge"** or **"Promote"**
4. Select target branch (e.g., `main`)
5. Review changes
6. Confirm merge

**Note:** Merging typically merges **schema changes**, not data.

### Deleting Branches

**When to delete:**
- Feature is merged
- Branch is no longer needed
- Cleanup old branches

**How to delete:**
1. Go to Supabase → Branches
2. Find branch
3. Click **"Delete"** or **"Remove"**
4. Confirm deletion

---

## Integration with Git Workflow

### Recommended Mapping

**Option 1: Manual Branching (Current Setup)**
```
Git Branch          →  Supabase Branch  →  Vercel Project
─────────────────────────────────────────────────────────
main                →  main             →  benchsight-production
develop             →  develop          →  benchsight-dev
feature/*           →  develop          →  (local dev)
feature/major-*     →  feature-*        →  (local dev)
```

**Option 2: Automatic Branching (With GitHub Integration)**
```
Git Branch          →  Supabase Branch  →  Vercel Project
─────────────────────────────────────────────────────────
main                →  main             →  benchsight-production
develop             →  develop          →  benchsight-dev
feature/* (PR)      →  auto-created     →  Vercel preview
                    →  ephemeral        →  (auto-linked)
```

### GitHub Integration Benefits

**Automatic Branch Creation:**
- Open PR → Supabase creates branch automatically
- Branch gets unique URL and credentials
- Vercel preview automatically connects to branch
- No manual setup needed!

**Automatic Cleanup:**
- Merge PR → Branch changes applied to main
- Branch automatically deleted
- No orphaned branches

**Migration Management:**
- Supabase applies migrations to branch
- Test migrations before production
- Safe schema testing

### Workflow Example

```bash
# 1. Create Git branch
git checkout -b feature/add-player-ratings

# 2. (Optional) Create Supabase branch for isolation
# In Supabase: Create branch "feature-add-ratings"
# Or use existing "develop" branch

# 3. Update local environment
# Point .env.local to appropriate Supabase branch

# 4. Work and test
cd ui/dashboard && npm run dev

# 5. Push and create PR
git push origin feature/add-player-ratings
# PR: feature/add-player-ratings → develop

# 6. When merged to develop Git branch
# - Code deployed to dev Vercel
# - Uses Supabase develop branch
# - Test on dev environment

# 7. When ready for production
# - Merge develop Git branch → main
# - Merge Supabase develop branch → main
# - Deploy to production Vercel
```

---

## Advantages of Supabase Branching

### vs. Separate Supabase Projects

**Supabase Branches:**
- ✅ Easier to manage (one project)
- ✅ Easier to merge schemas
- ✅ Better for team collaboration
- ✅ Lower cost (one project)
- ✅ Unified billing and settings

**Separate Projects:**
- ✅ Complete isolation
- ✅ Different regions possible
- ✅ Independent scaling
- ❌ Harder to sync schemas
- ❌ More projects to manage

### Best Use Cases

**Use Supabase Branches for:**
- Development and testing
- Schema change testing
- Feature isolation
- Team collaboration
- Staging environments

**Use Separate Projects for:**
- Production vs. development (if you want complete separation)
- Different regions
- Different scaling needs
- Complete isolation requirements

---

## Practical Examples

### Example 1: Standard Feature Development

```bash
# 1. Use existing develop Supabase branch
git checkout -b feature/add-stats

# 2. Point to develop branch (already configured)
./scripts/switch_env.sh sandbox

# 3. Work normally
# All changes test against develop Supabase branch

# 4. When ready, merge to develop Git branch
# Supabase develop branch already has your changes
```

### Example 2: Major Schema Change

```bash
# 1. Create Supabase branch for testing
# In Supabase: Create branch "schema-v2-test"

# 2. Create Git branch
git checkout -b refactor/schema-v2

# 3. Point to new Supabase branch
# Update .env.local with schema-v2-test branch URL

# 4. Test schema changes
# Apply migrations, test thoroughly

# 5. When ready, merge Supabase branch to develop
# Then merge Git branch to develop
```

### Example 3: Hotfix

```bash
# 1. Use main Supabase branch (careful!)
git checkout -b hotfix/critical-bug

# 2. Point to main Supabase branch
./scripts/switch_env.sh production

# 3. Fix bug and test
# 4. Merge to main (both Git and Supabase)
```

---

## Troubleshooting

### "I don't see Branches option"

**Possible reasons:**
- Feature not available on your plan
- Feature in beta (need access)
- UI location changed

**Solutions:**
- Check Supabase documentation
- Contact Supabase support
- Use separate projects as alternative

### "Branch creation failed"

**Check:**
- Do you have permissions?
- Is source branch accessible?
- Are there any active connections?

**Solutions:**
- Wait and try again
- Check Supabase status
- Contact support if persistent

### "How do I know which branch I'm using?"

**Check:**
- Supabase dashboard (branch selector)
- Environment variables (URL contains branch name)
- Connection string

### "Can I merge data between branches?"

**Typically:**
- Schema changes can be merged
- Data usually stays separate
- Check Supabase documentation for data migration options

---

## Best Practices

### ✅ Do This

1. **Use develop branch for most work**
   - One dev branch for team
   - Easy to coordinate
   - Simple workflow

2. **Create feature branches for major changes**
   - Schema changes
   - Major refactoring
   - When you need isolation

3. **Keep branches in sync**
   - Regularly merge develop → main
   - Keep schemas aligned
   - Document schema changes

4. **Clean up old branches**
   - Delete merged feature branches
   - Keep only active branches
   - Regular maintenance

### ❌ Don't Do This

1. **Don't create too many branches**
   - Hard to manage
   - Schema drift
   - Confusion

2. **Don't forget to merge**
   - Keep develop updated
   - Merge to main regularly
   - Don't let branches diverge

3. **Don't use production branch for development**
   - Risk of breaking production
   - Use develop branch instead
   - Test in isolation first

---

## Comparison: Branches vs. Separate Projects

| Feature | Supabase Branches | Separate Projects |
|--------|------------------|-------------------|
| Setup | Easy (one click) | More complex |
| Isolation | Good | Complete |
| Schema Sync | Easy merge | Manual sync |
| Cost | One project | Multiple projects |
| Management | Centralized | Distributed |
| Best For | Dev/Test | Production separation |

---

## Quick Reference

### Create Branch
```
Supabase Dashboard → Branches → New Branch
Name: develop
Source: main
```

### Switch to Branch
```
Update .env.local with branch URL
Or use branch selector in dashboard
```

### Merge Branch
```
Supabase Dashboard → Branches → Select Branch → Merge
Source: develop
Target: main
```

### Delete Branch
```
Supabase Dashboard → Branches → Select Branch → Delete
```

---

## Setting Up GitHub Integration

### Step 1: Connect GitHub to Supabase

1. **Go to Supabase Dashboard:**
   - Your Project → Settings → Integrations
   - Or look for "GitHub" in sidebar

2. **Connect Repository:**
   - Click "Connect GitHub"
   - Authorize Supabase
   - Select your `benchsight` repository

3. **Configure Branching:**
   - Enable "Automatic branch creation"
   - Choose which branches trigger branches (e.g., all PRs)
   - Set up migration path (if using Supabase CLI migrations)

### Step 2: Configure Vercel Integration

**If using Vercel:**
1. Install Supabase Vercel Integration
2. Connect your Supabase project
3. Vercel will automatically:
   - Get branch credentials for previews
   - Update environment variables per branch
   - Link preview deployments to correct branch

### Step 3: Test the Workflow

```bash
# 1. Create feature branch
git checkout -b feature/test-branching

# 2. Make a change
# ... edit files ...

# 3. Push and create PR
git push origin feature/test-branching
# Create PR on GitHub

# 4. Supabase automatically:
# - Creates branch database
# - Applies any migrations
# - Provides branch URL

# 5. Vercel automatically:
# - Creates preview deployment
# - Connects to Supabase branch
# - Provides preview URL

# 6. Test on preview URL
# 7. Merge PR when ready
# 8. Supabase applies changes to main
# 9. Branch automatically deleted
```

## Next Steps

1. **Check if branching is available** in your Supabase project
2. **Enable GitHub integration** (if available)
3. **Create develop branch** manually (for persistent dev)
4. **Test automatic branching** with a PR
5. **Update your workflow** to use branches
6. **Document your setup** for your team

---

## Resources

- **Supabase Docs:** Check latest documentation on branching
- **Supabase Dashboard:** Look for "Branches" in your project
- **Support:** Contact Supabase if feature not visible

---

*Last updated: 2026-01-13*
