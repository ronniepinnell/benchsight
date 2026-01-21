# Files Changed for Deployment Fix

## Files Modified

### 1. `ui/dashboard/src/app/(dashboard)/games/[gameId]/page.tsx`
**Fix:** TypeScript error - `stat.cf` property access
- Changed: Added type assertion `const statAny = stat as Record<string, any>` to safely access `cf`, `ca`, `ff`, `fa` properties
- Line 70-73: Now uses `statAny.cf`, `statAny.ca`, `statAny.ff`, `statAny.fa` instead of direct `stat.cf` access

### 2. `ui/dashboard/src/app/(dashboard)/schedule/page.tsx`
**Fix:** Removed direct `.catch()` calls on Supabase queries
- Changed: Replaced `.catch()` with proper error destructuring `{ data, error }`
- Lines 51-64: Now properly handles errors from Supabase queries

## To Commit

```bash
cd "/Users/ronniepinnell/Documents/Documents - Ronnie's MacBook Pro - 1/Programming_HD/Hockey/Benchsight/git/benchsight"

# Check what files changed
git status

# Add the changed files
git add ui/dashboard/src/app/(dashboard)/games/[gameId]/page.tsx
git add ui/dashboard/src/app/(dashboard)/schedule/page.tsx

# Commit
git commit -m "Fix TypeScript errors: stat.cf property access and Supabase query error handling"

# Push
git push
```

## Error Fixed

**TypeScript Error:**
```
Property 'cf' does not exist on type 'FactPlayerGameStats | Record<string, any>'.
Property 'cf' does not exist on type 'FactPlayerGameStats'.
```

**Solution:** Use type assertion to access properties that may not exist on the base type.
