# Environment Variables Explained

**Understanding how your code works with different Supabase projects**

---

## The Short Answer

**✅ No, it won't break!** 

Your code doesn't hardcode which Supabase project to use. It reads from **environment variables** that are set separately in each Vercel project.

---

## How It Works

### Your Code is Environment-Agnostic

Look at your Supabase client code:

```typescript
// ui/dashboard/src/lib/supabase/client.ts
export function createClient() {
  return createBrowserClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,      // ← Reads from env var
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY! // ← Reads from env var
  )
}
```

**Key point:** The code doesn't say "connect to project X". It says "connect to whatever URL/key is in the environment variables."

### Environment Variables Are NOT in Git

Environment variables are:
- ✅ Set in Vercel dashboard (per project)
- ✅ Set in local `.env.local` files (not committed to git)
- ❌ NOT stored in your code
- ❌ NOT in git commits

This means:
- Same code → Different environments
- Each environment has its own variables
- Committing to `main` doesn't change which Supabase project it uses

---

## How Vercel Handles This

### Production Vercel Project
- **Connected to:** `main` branch
- **Environment Variables:**
  - `NEXT_PUBLIC_SUPABASE_URL` = Production Supabase URL
  - `NEXT_PUBLIC_SUPABASE_ANON_KEY` = Production anon key
- **Result:** When you push to `main`, it uses production Supabase

### Dev Vercel Project
- **Connected to:** `develop` branch
- **Environment Variables:**
  - `NEXT_PUBLIC_SUPABASE_URL` = Dev Supabase URL
  - `NEXT_PUBLIC_SUPABASE_ANON_KEY` = Dev anon key
- **Result:** When you push to `develop`, it uses dev Supabase

### The Magic

```
Same code in both branches
    ↓
Different environment variables
    ↓
Connects to different Supabase projects
```

---

## Visual Example

```
┌─────────────────────────────────────────────────────────┐
│                    GITHUB REPOSITORY                     │
│                                                           │
│  main branch ────┐                                        │
│                  │                                        │
│  develop branch ─┼─── Same code, same commits            │
│                  │                                        │
│  feature/* ──────┘                                        │
└─────────────────────────────────────────────────────────┘
         │                    │
         │                    │
         ▼                    ▼
┌─────────────────┐  ┌─────────────────┐
│ Vercel Prod     │  │ Vercel Dev     │
│                 │  │                 │
│ Env Vars:       │  │ Env Vars:       │
│ - Prod Supabase │  │ - Dev Supabase  │
└─────────────────┘  └─────────────────┘
         │                    │
         ▼                    ▼
┌─────────────────┐  ┌─────────────────┐
│ Supabase Prod   │  │ Supabase Dev    │
│                 │  │                 │
│ - Real data     │  │ - Test data     │
│ - Live users    │  │ - Safe to break │
└─────────────────┘  └─────────────────┘
```

---

## What Could Break?

### ⚠️ Schema Mismatch (The Only Real Risk)

**Problem:** If your dev and prod Supabase databases have different schemas (different tables, columns, or views), the code might work in dev but break in prod.

**Example:**
- Dev has table `v_player_stats_v2`
- Prod only has `v_player_stats`
- Code queries `v_player_stats_v2` → Works in dev, breaks in prod

**Solution:** Keep schemas in sync!

### ✅ How to Keep Schemas in Sync

**Option 1: Copy Schema from Prod to Dev**
```bash
# 1. Export schema from production
# In Supabase Dashboard → SQL Editor
# Copy all your CREATE TABLE, CREATE VIEW statements

# 2. Apply to dev
# In Dev Supabase Dashboard → SQL Editor
# Paste and run the same SQL
```

**Option 2: Use Migration Scripts**
```bash
# Create a migration script
# sql/migrations/001_initial_schema.sql

# Run it in both environments
# Production: Apply via Supabase Dashboard
# Dev: Apply via Supabase Dashboard
```

**Option 3: Run ETL to Both**
```bash
# Update config for production
python run_etl.py
python upload.py

# Switch to dev config
./scripts/switch_env.sh sandbox
python run_etl.py
python upload.py
```

---

## Best Practices

### ✅ Do This

1. **Keep schemas identical** between dev and prod
2. **Test schema changes in dev first**
3. **Document schema changes** in migration files
4. **Use the same SQL scripts** for both environments

### ❌ Don't Do This

1. **Don't test schema changes directly in production**
2. **Don't let dev and prod schemas drift apart**
3. **Don't hardcode table/view names** (use constants if needed)

---

## Workflow for Schema Changes

### Adding a New View

```bash
# 1. Create SQL file
# sql/views/13_new_view.sql

# 2. Test in dev first
# - Switch to dev: ./scripts/switch_env.sh sandbox
# - Run SQL in dev Supabase Dashboard
# - Test dashboard locally
# - Push to develop branch
# - Test on dev Vercel URL

# 3. When ready, apply to production
# - Run SQL in production Supabase Dashboard
# - Push to main branch
# - Test on production Vercel URL
```

### Changing Table Structure

```bash
# 1. Create migration script
# sql/migrations/002_add_column.sql

# 2. Test in dev
# - Apply to dev Supabase
# - Update ETL code if needed
# - Run ETL: python run_etl.py
# - Test dashboard

# 3. Apply to production
# - Apply migration to prod Supabase
# - Run ETL in production
# - Deploy dashboard
```

---

## Testing Your Setup

### Verify Environment Variables

**In Vercel:**
1. Go to project → Settings → Environment Variables
2. Verify each project has correct Supabase credentials
3. Production project → Production Supabase
4. Dev project → Dev Supabase

**Locally:**
```bash
# Check current environment
cat ui/dashboard/.env.local

# Should show:
# NEXT_PUBLIC_SUPABASE_URL=https://your-dev-project.supabase.co
# NEXT_PUBLIC_SUPABASE_ANON_KEY=your-dev-key
```

### Test Connection

**Dev Environment:**
```bash
# Switch to dev
./scripts/switch_env.sh sandbox

# Start dashboard
cd ui/dashboard
npm run dev

# Visit: http://localhost:3000/prototypes/test-connection
# Should connect to dev Supabase
```

**Production Environment:**
```bash
# Switch to production (careful!)
./scripts/switch_env.sh production

# Start dashboard
cd ui/dashboard
npm run dev

# Visit: http://localhost:3000/prototypes/test-connection
# Should connect to production Supabase
```

---

## Common Questions

### Q: "If I commit code that queries a new table, will it break production?"

**A:** Only if:
- The new table doesn't exist in production Supabase
- But it does exist in dev Supabase

**Solution:** Create the table in production before (or at the same time as) deploying the code.

### Q: "Can I use different table names in dev vs prod?"

**A:** Technically yes, but **strongly discouraged**. It makes debugging harder and increases risk of errors.

**Better approach:** Use the same schema, but different data.

### Q: "What if I accidentally push dev credentials to production?"

**A:** Environment variables in Vercel are separate. Even if you had dev credentials in a local file and committed it (which you shouldn't), Vercel would still use the variables you set in the Vercel dashboard.

**Protection:** `.env.local` files are in `.gitignore`, so they won't be committed.

### Q: "How do I know which environment I'm connected to?"

**A:** Check the Supabase URL in your environment variables:
- Dev: `https://your-dev-project.supabase.co`
- Prod: `https://your-prod-project.supabase.co`

Or add a debug page that shows the current environment.

---

## Summary

✅ **Your code is safe** - It reads from environment variables, not hardcoded values

✅ **Committing to main won't break it** - Vercel uses the environment variables you set in the dashboard

⚠️ **Keep schemas in sync** - This is the only thing that could cause issues

✅ **Test in dev first** - Always test schema changes in dev before production

---

## Quick Checklist

Before deploying to production:
- [ ] Schema changes tested in dev
- [ ] Same tables/views exist in both environments
- [ ] Environment variables set correctly in Vercel
- [ ] Tested on dev Vercel URL first
- [ ] Production Supabase has required schema

---

*Last updated: 2026-01-13*
