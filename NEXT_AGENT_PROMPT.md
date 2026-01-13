# Next Agent Prompt - Fix Analytics Pages Layout Issue

## CRITICAL ISSUE

The analytics pages (`/analytics/overview`, `/analytics/statistics`, `/analytics/teams`) are displaying as **completely white pages with no layout, no sidebar, no styling**.

## User's Exact Words
> "this page looks like shit. white page no layout, no styling. am i doing something wrong? do i need to view somewhere else?"

## What Works vs What Doesn't

✅ **WORKING PAGES:**
- `/standings` - Perfect layout, sidebar, styling
- `/leaders` - Perfect layout, sidebar, styling  
- `/players` - Perfect layout, sidebar, styling
- `/teams` - Perfect layout, sidebar, styling

❌ **BROKEN PAGES:**
- `/analytics/overview` - White page, no layout
- `/analytics/statistics` - White page, no layout
- `/analytics/teams` - White page, no layout

## File Structure

```
src/app/
├── layout.tsx                    # Root layout (loads fonts, globals.css)
├── (dashboard)/
│   ├── layout.tsx                # Dashboard layout (Sidebar + Topbar wrapper)
│   ├── standings/page.tsx        # ✅ WORKS - Use as reference
│   ├── leaders/page.tsx           # ✅ WORKS
│   └── analytics/
│       ├── overview/page.tsx      # ❌ BROKEN - White page
│       ├── statistics/page.tsx   # ❌ BROKEN - White page
│       └── teams/page.tsx         # ❌ BROKEN - White page
```

## Expected Behavior

Pages should have:
1. **Sidebar** on the left (from `(dashboard)/layout.tsx`)
2. **Topbar** at the top
3. **Dark background** (`bg-background`)
4. **Proper spacing** (`ml-60 mt-14 p-6` from layout)
5. **All Tailwind styling** working

## Investigation Checklist

### 1. Check Route Group Layout Inheritance
- [ ] Verify `(dashboard)/layout.tsx` wraps analytics pages
- [ ] Compare route structure with working pages
- [ ] Check if Next.js is recognizing the route group

### 2. Check for Runtime Errors
- [ ] Look at browser console for JavaScript errors
- [ ] Check terminal for Next.js compilation errors
- [ ] Look for React hydration errors
- [ ] Check for Supabase connection errors

### 3. Compare Working vs Broken Pages
Compare `/standings/page.tsx` (works) with `/analytics/overview/page.tsx` (broken):

**Key Differences to Check:**
- Imports (especially chart components)
- Component structure
- Metadata exports
- Client vs Server components
- Error boundaries

### 4. Check CSS/Tailwind
- [ ] Verify `globals.css` is loading
- [ ] Check Tailwind is compiling
- [ ] Verify dark mode class on `<html>`
- [ ] Check if CSS variables are defined

### 5. Check Chart Components
The analytics pages use client chart components:
- `@/components/charts/standings-chart`
- `@/components/charts/scorers-chart`
- `@/components/charts/goal-diff-chart`
- `@/components/charts/team-comparison-chart`
- `@/components/charts/power-score-chart`

**Check:**
- [ ] All chart components have `'use client'` directive
- [ ] Chart components aren't breaking the page
- [ ] Recharts is installed correctly

## Quick Fixes to Try

### Fix 1: Clear Next.js Cache
```bash
cd ui/dashboard
rm -rf .next
npm run dev
```

### Fix 2: Check Browser Console
Open browser DevTools → Console tab
Look for:
- Red errors
- Failed imports
- React errors
- CSS loading errors

### Fix 3: Verify Route
Make sure visiting:
- ✅ `/analytics/overview` (should work)
- ❌ `/prototypes/macro/league-overview` (old prototype route)

### Fix 4: Check Terminal Output
Look for:
- Compilation errors
- Module not found errors
- TypeScript errors
- Build warnings

## Files to Review

1. **`src/app/(dashboard)/layout.tsx`** - Dashboard layout wrapper
2. **`src/app/(dashboard)/analytics/overview/page.tsx`** - Broken page
3. **`src/app/(dashboard)/standings/page.tsx`** - Working reference
4. **`src/components/charts/*.tsx`** - Chart components (might be breaking)
5. **`src/app/globals.css`** - Global styles
6. **`tailwind.config.ts`** - Tailwind config

## Most Likely Causes

1. **Chart Component Error**: Client components breaking server component page
2. **Import Error**: Missing or incorrect import causing silent failure
3. **Route Group Issue**: Analytics pages not inheriting layout
4. **Build Cache**: Stale Next.js cache
5. **CSS Not Loading**: Tailwind/globals.css not being applied

## Solution Approach

1. **First**: Check browser console and terminal for errors
2. **Second**: Compare analytics page structure with standings page
3. **Third**: Test if removing charts fixes the layout
4. **Fourth**: Verify route group is working
5. **Fifth**: Clear cache and rebuild

## Success Criteria

After fix, pages should:
- ✅ Show sidebar navigation
- ✅ Show topbar
- ✅ Have dark background
- ✅ Display all content with proper styling
- ✅ Match the design of `/standings` page

## Reference Files

- **Working example**: `src/app/(dashboard)/standings/page.tsx`
- **Layout wrapper**: `src/app/(dashboard)/layout.tsx`
- **Root layout**: `src/app/layout.tsx`
- **Global styles**: `src/app/globals.css`

## Additional Context

- Dashboard uses Next.js 14 App Router
- Uses Tailwind CSS for styling
- Uses Recharts for charts (client components)
- All other pages in `(dashboard)` route group work fine
- Only analytics pages are broken

---

**PRIORITY: HIGH** - User cannot use the analytics pages. Fix immediately.
