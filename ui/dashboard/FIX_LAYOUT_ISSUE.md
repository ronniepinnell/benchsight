# CRITICAL: Analytics Pages Showing White Page - No Layout/Styling

## Problem
The analytics pages (`/analytics/overview`, `/analytics/statistics`, `/analytics/teams`) are displaying as white pages with no layout, no sidebar, no styling - completely unstyled.

## Expected Behavior
Pages should have:
- Sidebar navigation (left side)
- Topbar (top)
- Dark background
- Proper styling matching `/standings` page
- All CSS/Tailwind classes working

## Current Status
- ✅ `/standings` page works perfectly (has layout, styling, sidebar)
- ✅ `/leaders` page works perfectly
- ❌ `/analytics/*` pages show white page, no layout

## File Structure
```
src/app/
├── layout.tsx                    # Root layout (fonts, globals.css)
├── (dashboard)/
│   ├── layout.tsx                # Dashboard layout (Sidebar, Topbar)
│   ├── standings/
│   │   └── page.tsx              # ✅ WORKS
│   ├── leaders/
│   │   └── page.tsx              # ✅ WORKS
│   └── analytics/
│       ├── overview/
│       │   └── page.tsx          # ❌ WHITE PAGE
│       ├── statistics/
│       │   └── page.tsx          # ❌ WHITE PAGE
│       └── teams/
│           └── page.tsx          # ❌ WHITE PAGE
```

## Investigation Steps

### 1. Check if Layout is Being Applied
- Verify `(dashboard)/layout.tsx` is wrapping analytics pages
- Check Next.js route groups are working correctly
- Compare with working pages (standings, leaders)

### 2. Check CSS Loading
- Verify `globals.css` is imported in root layout
- Check Tailwind is compiling
- Look for CSS errors in browser console
- Check if dark mode class is applied

### 3. Check for Build Errors
- Look at terminal output for compilation errors
- Check browser console for JavaScript errors
- Verify all imports are correct

### 4. Compare Working vs Broken Pages
- Compare `/standings/page.tsx` (works) with `/analytics/overview/page.tsx` (broken)
- Check for differences in:
  - Imports
  - Component structure
  - Metadata exports
  - Any client/server component issues

## Possible Causes

1. **Route Group Issue**: Analytics pages might not be inheriting `(dashboard)/layout.tsx`
2. **CSS Not Loading**: Tailwind or globals.css not being applied
3. **Build Cache**: Next.js cache might be stale
4. **Import Error**: Missing or incorrect imports causing silent failure
5. **Client Component Issue**: Charts might be breaking the entire page

## Quick Fixes to Try

1. **Clear Next.js Cache**:
   ```bash
   cd ui/dashboard
   rm -rf .next
   npm run dev
   ```

2. **Check Browser Console**: Look for errors

3. **Verify Route**: Make sure you're visiting `/analytics/overview` not `/prototypes/macro/league-overview`

4. **Compare Imports**: Ensure analytics pages have same structure as standings page

## Files to Check

- `src/app/(dashboard)/layout.tsx` - Dashboard layout wrapper
- `src/app/(dashboard)/analytics/overview/page.tsx` - Broken page
- `src/app/(dashboard)/standings/page.tsx` - Working reference
- `src/app/globals.css` - Global styles
- `tailwind.config.ts` - Tailwind configuration

## Expected Fix

The analytics pages should:
1. Inherit the dashboard layout (sidebar, topbar)
2. Have dark background (`bg-background`)
3. Show all styling correctly
4. Match the design of the standings page

## User's Exact Issue
"give me a prompt for next agent. this page looks like shit. white page no layout, no styling. am i doing something wrong? do i need to view somewhere else?"

They're viewing `/analytics/overview` (or similar) and seeing a completely unstyled white page.
