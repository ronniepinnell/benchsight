# Table Sorting Status

**Last Updated:** 2026-01-15  
**Goal:** All tables in the dashboard should be sortable by any column

---

## ✅ Sortable Tables (Completed)

1. **Standings Table** (`SortableStandingsTable`)
   - Location: `src/components/teams/sortable-standings-table.tsx`
   - Status: ✅ Fully sortable
   - Columns: Standing, Team, GP, W, L, T, Pts, Win%, GF, GA, Diff, etc.

2. **Player Leaders Table** (`SortableLeadersTable`)
   - Location: `src/components/leaders/sortable-leaders-table.tsx`
   - Status: ✅ Fully sortable
   - Columns: Rank, Player, Team, GP, G, A, P, P/G, etc.

3. **Goalie Leaders Table** (`SortableGoaliesTable`)
   - Location: `src/components/leaders/sortable-goalies-table.tsx`
   - Status: ✅ Fully sortable
   - Columns: Rank, Player, Team, GP, GAA, SV%, etc.

4. **Team Roster Table** (`SortableRosterTable`)
   - Location: `src/components/teams/sortable-roster-table.tsx`
   - Status: ✅ Fully sortable
   - Columns: Player, #, Rating, GP, G, A, P, P/G, +/-, CF%, TOI/G, PIM

5. **Prior Teams Table** (`SortablePriorTeamsTable`)
   - Location: `src/components/players/sortable-prior-teams-table.tsx`
   - Status: ✅ Fully sortable
   - Columns: Team, GP, G, A, P, PIM, G/G, A/G, P/G

6. **Game Goalies Table** (`SortableGoaliesTable`)
   - Location: `src/components/games/sortable-goalies-table.tsx`
   - Status: ✅ Fully sortable
   - Columns: Goalie, Team, Saves, Shots, SV%, GA, GAA

---

## 🚧 Tables Needing Sorting (In Progress)

### Game Page Boxscore Tables

1. **Away Forwards Table**
   - Location: `src/app/norad/(dashboard)/games/[gameId]/page.tsx` (line ~1743)
   - Status: ❌ Not sortable
   - Columns: Player, #, Rating, G, A, P, S, +/-, PIM, TOI, Shifts, CF%, P, GvA, TkA
   - Complexity: High - conditional columns based on tracking data
   - Solution: Create `SortableBoxscoreTable` component (already created, needs integration)

2. **Home Forwards Table**
   - Location: `src/app/norad/(dashboard)/games/[gameId]/page.tsx` (line ~1947)
   - Status: ❌ Not sortable
   - Same structure as Away Forwards

3. **Away Defense Table**
   - Location: `src/app/norad/(dashboard)/games/[gameId]/page.tsx` (line ~2151)
   - Status: ❌ Not sortable
   - Same structure as Forwards

4. **Home Defense Table**
   - Location: `src/app/norad/(dashboard)/games/[gameId]/page.tsx` (line ~2348)
   - Status: ❌ Not sortable
   - Same structure as Forwards

5. **Team Totals Table**
   - Location: `src/app/norad/(dashboard)/games/[gameId]/page.tsx` (line ~2519)
   - Status: ❌ Not sortable (but only 2 rows - away/home totals)
   - Note: This is a totals table with only 2 rows, sorting may not be necessary

---

## 📋 Tables That Don't Need Sorting

1. **Team Stats Comparison Table**
   - Location: `src/app/norad/(dashboard)/games/[gameId]/page.tsx` (line ~978)
   - Reason: Comparison table (Stat | Away | Home) - not a list to sort

2. **Career Totals Table** (Player Page)
   - Location: `src/app/norad/(dashboard)/players/[playerId]/page.tsx` (line ~2768)
   - Reason: Single row totals - no sorting needed

3. **Season Totals Table** (Prior Teams)
   - Location: `src/app/norad/(dashboard)/players/[playerId]/page.tsx`
   - Reason: Single row totals - no sorting needed

---

## 🔧 Implementation Plan

### Phase 1: Game Page Boxscore Tables (Priority)

**Task:** Integrate `SortableBoxscoreTable` component into game page

**Steps:**
1. ✅ Created `SortableBoxscoreTable` component
2. ⏳ Update game page to use component for:
   - Away Forwards
   - Home Forwards
   - Away Defense
   - Home Defense

**Challenges:**
- Tables are in server component
- Need to pass players, playersMap, teamColor, hasTracking, hasShifts, hasEvents
- Need to handle advanced stats mapping
- Need to preserve padding rows for alignment

**Solution:**
- Create client wrapper components that receive pre-processed data
- Or convert table sections to client components with data fetching

---

## 📝 Notes

- All sortable tables should:
  - Show sort icons (ArrowUpDown when unsorted, ArrowUp/ArrowDown when sorted)
  - Be clickable on column headers
  - Toggle between asc/desc on same column click
  - Default to sensible sort (e.g., points desc for players, GAA asc for goalies)

- Performance considerations:
  - Client-side sorting is fine for most tables (< 100 rows)
  - For larger tables, consider server-side sorting with query params

---

## Next Steps

1. ✅ Complete Prior Teams table sorting
2. ✅ Complete Goalies table sorting on game page
3. ⏳ Integrate SortableBoxscoreTable for game page forward/defense tables
4. ⏳ Test all sortable tables
5. ⏳ Verify no tables are missing sorting
