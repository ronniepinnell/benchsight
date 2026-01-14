# Fix Deployment Error

**The deployment is failing because GitHub has old code**

## The Error

The error shows:
```
42 |   const homePlayers = boxScore.players.filter(p => p.team_id === homeTeamId)
```

But your local code already has the fix:
```
58 |   const homePlayers = boxScoreResult?.homeStats || []
```

## Solution: Push Your Changes to GitHub

Your local code is correct, but GitHub has the old version. You need to push your changes:

```bash
# Check what files have changed
git status

# Add all changes
git add .

# Commit the changes
git commit -m "Fix TypeScript errors in games page"

# Push to GitHub
git push
```

After pushing, Vercel will automatically redeploy with the fixed code.

## Quick Fix Commands

```bash
# From your project root directory
git add ui/dashboard/src/app/(dashboard)/games/[gameId]/page.tsx
git commit -m "Fix TypeScript error: use boxScoreResult.homeStats instead of boxScore.players"
git push
```

---

## Alternative: If you haven't committed other changes

If you want to only commit the game page fix:

```bash
# Add just this file
git add ui/dashboard/src/app/\(dashboard\)/games/\[gameId\]/page.tsx

# Commit
git commit -m "Fix games page TypeScript error"

# Push
git push
```

---

After pushing, Vercel should automatically trigger a new deployment with the fixed code!
