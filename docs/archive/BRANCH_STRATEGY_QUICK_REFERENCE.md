# Branch Strategy Quick Reference

**One-page cheat sheet for BenchSight development workflow**

---

## Branch Structure

```
main (production)
  ↑
develop (dev/sandbox)
  ↑
feature/* (your work)
```

---

## Branch → Environment Mapping

| Branch | Vercel Project | Supabase Project | Use For |
|--------|---------------|------------------|---------|
| `main` | `benchsight-production` | `benchsight-production` | Live site |
| `develop` | `benchsight-dev` | `benchsight-dev` | Testing |
| `feature/*` | Preview (optional) | Local dev | Active work |

---

## Common Workflows

### Start New Feature
```bash
git checkout develop
git pull origin develop
git checkout -b feature/my-feature
# ... work ...
git push origin feature/my-feature
# Create PR: feature/my-feature → develop
```

### Deploy to Dev
```bash
# After PR is merged to develop
git checkout develop
git pull origin develop
# Vercel auto-deploys to dev environment
```

### Deploy to Production
```bash
# After testing in dev
git checkout main
git merge develop
git push origin main
# Vercel auto-deploys to production
```

### Switch Local Environment
```bash
./scripts/switch_env.sh sandbox      # Use dev Supabase
./scripts/switch_env.sh production   # Use prod Supabase (careful!)
```

---

## URLs

**Production:**
- Dashboard: `https://benchsight-production.vercel.app`
- Supabase: `https://your-prod-project.supabase.co`

**Development:**
- Dashboard: `https://benchsight-dev.vercel.app`
- Supabase: `https://your-dev-project.supabase.co`

**Local:**
- Dashboard: `http://localhost:3000`

---

## Environment Variables

**Production Vercel:**
- `NEXT_PUBLIC_SUPABASE_URL` = Production Supabase URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` = Production anon key

**Dev Vercel:**
- `NEXT_PUBLIC_SUPABASE_URL` = Dev Supabase URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` = Dev anon key

**Local (.env.local):**
- Use `./scripts/switch_env.sh` to switch between dev/prod configs

---

## Branch Naming

```bash
feature/add-player-ratings    # New feature
fix/goal-counting-bug         # Bug fix
hotfix/critical-security      # Urgent production fix
docs/update-readme            # Documentation
refactor/cleanup-stats        # Code improvement
```

---

## Quick Commands

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
```

---

## PR Workflow

1. **Create feature branch** → Work → Push
2. **Create PR** on GitHub: `feature/*` → `develop`
3. **Review** → Make changes if needed
4. **Merge** → Auto-deploys to dev Vercel
5. **Test** on dev URL
6. **Create PR**: `develop` → `main` (when ready)
7. **Review** → Merge → Auto-deploys to production

---

## Safety Rules

✅ **DO:**
- Test in dev before production
- Use feature branches
- Review PRs before merging
- Keep main stable

❌ **DON'T:**
- Push directly to main
- Skip testing
- Mix multiple features in one branch
- Use production credentials in dev

---

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

---

*See [DEV_ENV.md](../setup/DEV_ENV.md) for complete guide*
