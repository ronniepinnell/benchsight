# Dashboard Review & Improvement Plan

**Date:** 2026-01-14  
**Reviewer:** AI Assistant  
**Deployment Target:** Vercel

---

## Executive Summary

The BenchSight dashboard is a well-structured Next.js 16 application with a solid foundation. This review identifies:
- ✅ **Current Strengths:** Good architecture, comprehensive data access, working authentication
- ⚠️ **Gaps:** Missing features from vision doc, incomplete analytics pages, limited visualizations
- 🎯 **Opportunities:** Rich data available but underutilized, many advanced features not yet implemented

---

## 1. Current State Assessment

### ✅ What's Working Well

1. **Architecture & Structure**
   - Clean Next.js 14+ App Router structure
   - Proper separation of concerns (components, lib, types)
   - Good use of server components for data fetching
   - Authentication middleware in place
   - Supabase integration working

2. **Core Features Implemented**
   - ✅ Player profiles with basic stats
   - ✅ Team standings and leaderboards
   - ✅ Game tracker (live game tracking)
   - ✅ Basic analytics pages (overview, statistics, trends)
   - ✅ Schedule viewing
   - ✅ Goalie leaderboards
   - ✅ Player search and comparison

3. **Data Access**
   - ✅ Comprehensive Supabase queries
   - ✅ Views integration (v_leaderboard_*, v_standings_*, etc.)
   - ✅ Proper error handling patterns

### ⚠️ Areas Needing Improvement

1. **Incomplete Analytics Pages**
   - `/analytics/trends` - Shows "Coming Soon" placeholder
   - `/analytics/shifts` - Basic implementation, needs enhancement
   - Missing advanced analytics from vision doc

2. **Limited Visualizations**
   - Basic charts exist but many advanced visualizations missing
   - No shot maps, heat maps, or advanced charts
   - Limited interactive components

3. **Player Profile Gaps**
   - Missing many advanced stats from `fact_player_game_stats` (317 columns!)
   - No micro stats explorer
   - Limited trend visualizations
   - Missing zone analytics, rush analysis

4. **Game Pages**
   - Basic game detail page exists
   - Missing play-by-play timeline
   - No shift charts
   - No shot maps
   - Missing game highlights component

5. **Team Pages**
   - Basic team profile
   - Missing line combinations analysis
   - No zone time analysis
   - Missing WOWY (With Or Without You) analysis

---

## 2. TODOs from Documentation

### From `docs/TODO.md`

- [ ] **Test all views in Supabase dashboard** - Verify all 26 views work correctly
- [ ] **Build Next.js dashboard components using views** - Many views not yet used
- [ ] **Add player_id linkage** - Needs jersey mapping
- [ ] **Add TOI columns** - Needs shift join
- [ ] **Fix home_gf_all=0 bug** - Data issue to resolve
- [ ] **Game tracker workflow improvements** - Enhance UX
- [ ] **Enhance DATA_DICTIONARY_FULL.md with calculation formulas**
- [ ] **Add flexible ETL workflow options**

### From `ui/dashboard/ENHANCEMENT_PLAN.md`

**Phase 1 (Immediate) - Some Completed:**
- [x] Game logs using dim_schedule + fact_gameroster ✅
- [x] Enhanced stat tooltips with formulas ✅
- [ ] **Matchup predictor component** - Not implemented
- [ ] **Game highlights component** - Not implemented

**Phase 2 (Next):**
- [ ] Maximum detail expansion for all pages
- [ ] Video integration (if URLs available)
- [ ] Advanced matchup analysis
- [ ] Trend visualizations

**Phase 3 (Future):**
- [ ] Machine learning win probability model
- [ ] Interactive video player with event sync
- [ ] Advanced analytics dashboards
- [ ] Custom report builder

### Code TODOs Found

From codebase search:
- [ ] `useKeyboardShortcuts.ts:97` - Set current player slot
- [ ] `export.ts:273` - Calculate actual stoppage duration
- [ ] `state.ts:198` - Show modal for passesNeedingReview
- [ ] `ShiftPanel.tsx:74` - Pass events for stoppage calculation

---

## 3. Ideas from Analytics Vision Document

### High-Priority Features (Quick Wins)

#### 3.1 Enhanced Player Profile Page
**Current:** Basic stats, game log  
**Vision:** Comprehensive 4-tab layout with advanced analytics

**Implementation:**
```typescript
// Add tabs: Overview | Season | Career | Advanced
// Overview Tab:
- Performance trend line chart (Goals/Game, Points/Game)
- Game log table (already exists, enhance with more columns)
- Stat breakdown radar chart
- Recent games timeline

// Season Tab:
- Season summary cards (G, A, P, TOI, etc.)
- Goals/Game trend line chart
- Advanced metrics cards (CF%, xG, WAR)
- Game-by-game stats table (enhance existing)

// Career Tab:
- Career totals cards
- Career trends multi-line chart
- Season-by-season comparison table

// Advanced Tab:
- xG Analysis (bar + line chart)
- WAR/GAR cards
- Zone analytics heat maps
- Micro stats cards
- Competition tier analysis
```

**Data Sources:**
- `fact_player_game_stats` (317 columns - use more!)
- `fact_player_season_stats`
- `fact_player_career_stats`
- `fact_player_micro_stats`
- `fact_player_qoc_summary`

#### 3.2 Shot Maps & Heat Maps
**Current:** Missing  
**Vision:** Interactive rink diagrams with shot locations

**Implementation:**
- Create `ShotMap` component using SVG/Canvas
- Use `fact_events` with XY coordinates
- Show shots, goals, xG bubbles
- Filter by period, strength, player

**Data Sources:**
- `fact_events` (with XY coordinates)
- `fact_shot_event`

#### 3.3 Advanced Analytics Dashboard
**Current:** Placeholder pages  
**Vision:** Comprehensive analytics hub

**Features to Add:**
1. **xG Analysis Dashboard**
   - xG Leaders table
   - Goals Above Expected chart
   - xG Timeline (game flow)
   - Shot Quality Analysis

2. **WAR/GAR Leaders**
   - WAR Leaders table
   - GAR Component Breakdown
   - WAR Trends over time
   - WAR by Position

3. **Micro Stats Explorer**
   - Interactive micro stats breakdown
   - Deke success rate, drive success rate
   - Zone entry/exit success rates
   - Rush involvement metrics

4. **Zone Analytics**
   - Zone Entry Analysis
   - Zone Exit Analysis
   - Zone Time Heat Maps
   - Zone Entry/Exit Success Rates

**Data Sources:**
- `fact_zone_entries`, `fact_zone_exits`
- `fact_team_zone_time`
- `fact_player_micro_stats`
- `fact_rushes`, `fact_rush_events`

#### 3.4 Game Center Enhancements
**Current:** Basic game detail page  
**Vision:** Comprehensive game center with live updates

**Features to Add:**
1. **Play-by-Play Timeline**
   - Event timeline from `fact_events`
   - Filter by event type
   - Click to see details

2. **Shift Charts**
   - Shift timeline for each player
   - Line combinations visualization
   - TOI breakdown

3. **Game Highlights**
   - List of highlight events (goals, saves, hits)
   - Video timestamps (if available)
   - Filter by event type

**Data Sources:**
- `fact_events` (140 columns)
- `fact_shifts`, `fact_shift_players`
- `fact_game_status` (tracking status)

#### 3.5 Team Analytics Enhancements
**Current:** Basic team profile  
**Vision:** Comprehensive team analysis

**Features to Add:**
1. **Line Combinations Analysis**
   - Line performance (CF%, xGF%, etc.)
   - WOWY (With Or Without You) analysis
   - Optimal line suggestions

2. **Zone Time Analysis**
   - Zone time breakdown (O-zone, N-zone, D-zone)
   - Zone time heat maps
   - Zone time by period/game state

**Data Sources:**
- `fact_line_combos`
- `fact_wowy`
- `fact_team_zone_time`

### Medium-Priority Features

#### 3.6 Matchup Predictor
**From ENHANCEMENT_PLAN.md** - Not yet implemented

**Implementation:**
- Component for schedule/upcoming games
- Win probability calculation
- Key matchup stats display
- Prediction confidence indicator

**Data Sources:**
- `fact_team_season_stats_basic`
- `fact_team_game_stats`
- `dim_schedule` (for H2H history)

#### 3.7 Goalie Advanced Metrics
**Current:** Basic goalie stats  
**Vision:** Comprehensive goalie analysis

**Features:**
- GSAx (Goals Saved Above Expected)
- Save Type Breakdown (Butterfly, Pad, Glove, etc.)
- Rebound Control metrics
- Danger Zone Stats (High/Medium/Low)
- Save Location Heat Maps

**Data Sources:**
- `fact_goalie_game_stats` (128 columns - use more!)
- `fact_saves`

#### 3.8 Reports & Export
**Current:** Missing  
**Vision:** PDF/CSV export capabilities

**Features:**
- Player Performance Report (PDF/CSV)
- Team Performance Report
- Game Recap Report
- Custom Report Builder (future)

**Implementation:**
- Use Puppeteer or PDFKit for PDF generation
- ExcelJS for Excel exports
- React-PDF for templates

---

## 4. Vercel Deployment Considerations

### ✅ Already Configured

1. **Build Configuration**
   - ✅ `vercel.json` with correct settings
   - ✅ `.npmrc` with `legacy-peer-deps=true`
   - ✅ `next.config.js` with image optimization
   - ✅ TypeScript config allows build with errors (temporary)

2. **Environment Variables**
   - ✅ Supabase URL and keys
   - ✅ Auth callback configured

3. **Deployment Checklist**
   - ✅ Build works locally
   - ✅ All critical TypeScript errors fixed
   - ✅ ESLint updated to v9

### ⚠️ Recommendations for Vercel

1. **Performance Optimization**
   - [ ] Add `revalidate` to more pages (currently only player page has it)
   - [ ] Implement ISR (Incremental Static Regeneration) for leaderboards
   - [ ] Add caching headers for static assets
   - [ ] Consider edge functions for frequently accessed data

2. **Image Optimization**
   - ✅ Next.js Image component configured
   - [ ] Add image CDN if needed
   - [ ] Optimize player photos and team logos

3. **Error Handling**
   - [ ] Add error boundaries for better UX
   - [ ] Implement proper error pages (404, 500)
   - [ ] Add error logging (Sentry, LogRocket, etc.)

4. **Monitoring**
   - [ ] Set up Vercel Analytics
   - [ ] Add performance monitoring
   - [ ] Track API response times

5. **SEO & Metadata**
   - [ ] Add proper metadata to all pages
   - [ ] Implement Open Graph tags
   - [ ] Add structured data (JSON-LD)

---

## 5. Implementation Priority Roadmap

### Phase 1: Quick Wins (1-2 weeks)
**Goal:** Enhance existing pages with more data and visualizations

1. **Player Profile Enhancements**
   - [ ] Add tabs (Overview, Season, Career, Advanced)
   - [ ] Add performance trend charts
   - [ ] Add radar chart for stat breakdown
   - [ ] Display more columns from `fact_player_game_stats`

2. **Analytics Pages Completion**
   - [ ] Implement trends page (replace placeholder)
   - [ ] Add xG analysis dashboard
   - [ ] Add WAR/GAR leaders page
   - [ ] Enhance shifts viewer

3. **Game Page Enhancements**
   - [ ] Add play-by-play timeline
   - [ ] Add game highlights component
   - [ ] Enhance boxscore display

### Phase 2: New Features (2-4 weeks)
**Goal:** Add major features from vision doc

1. **Visualizations**
   - [ ] Shot maps component
   - [ ] Heat maps for zone time
   - [ ] Shift charts visualization
   - [ ] Advanced chart library integration

2. **Advanced Analytics**
   - [ ] Micro stats explorer
   - [ ] Zone analytics dashboard
   - [ ] Rush analysis dashboard
   - [ ] Faceoff analysis

3. **Team Enhancements**
   - [ ] Line combinations analysis
   - [ ] WOWY analysis
   - [ ] Zone time analysis

### Phase 3: Advanced Features (4-8 weeks)
**Goal:** ML models and advanced features

1. **Predictive Features**
   - [ ] Matchup predictor
   - [ ] Win probability model
   - [ ] Performance prediction

2. **Reports**
   - [ ] PDF export functionality
   - [ ] CSV export enhancements
   - [ ] Custom report builder

3. **Video Integration**
   - [ ] Video player with event sync
   - [ ] Highlight timestamps
   - [ ] Video URL management

---

## 6. Technical Recommendations

### Code Quality

1. **TypeScript**
   - [ ] Remove `@ts-nocheck` from player page
   - [ ] Fix all TypeScript errors properly
   - [ ] Add proper types for all database queries
   - [ ] Generate types from Supabase schema

2. **Component Organization**
   - [ ] Create reusable chart components
   - [ ] Build visualization component library
   - [ ] Standardize stat display components

3. **Data Fetching**
   - [ ] Add proper loading states
   - [ ] Implement error boundaries
   - [ ] Add data caching strategies
   - [ ] Optimize query performance

### Performance

1. **Bundle Size**
   - [ ] Code split large components
   - [ ] Lazy load heavy visualizations
   - [ ] Optimize chart library imports

2. **Database Queries**
   - [ ] Add database indexes for common queries
   - [ ] Implement query result caching
   - [ ] Use database views more extensively

3. **Rendering**
   - [ ] Use React Server Components where possible
   - [ ] Implement proper revalidation strategies
   - [ ] Add streaming for large data sets

---

## 7. Specific Action Items

### Immediate (This Week)

1. **Complete Analytics Trends Page**
   - Replace placeholder with actual implementation
   - Add time series charts for league-wide trends
   - Use `fact_player_season_stats` and `fact_team_season_stats`

2. **Enhance Player Profile**
   - Add tab navigation
   - Create performance trend chart component
   - Display more advanced stats

3. **Add Shot Map Component**
   - Create basic SVG rink diagram
   - Plot shots from `fact_events`
   - Add filters (period, strength, player)

### Short Term (Next 2 Weeks)

1. **Game Highlights Component**
   - List highlight events from `fact_events`
   - Add timestamp display
   - Filter by event type

2. **Matchup Predictor**
   - Implement win probability calculation
   - Add to schedule page
   - Display key matchup stats

3. **Advanced Stats Display**
   - Add more columns from `fact_player_game_stats`
   - Create stat tooltips with formulas
   - Add percentile badges

### Medium Term (Next Month)

1. **Micro Stats Explorer**
   - Create dedicated page
   - Interactive micro stats breakdown
   - Success rate visualizations

2. **Zone Analytics Dashboard**
   - Zone entry/exit analysis
   - Zone time heat maps
   - Success rate metrics

3. **Line Combinations Analysis**
   - Team line performance
   - WOWY analysis
   - Optimal line suggestions

---

## 8. Data Utilization Gaps

### Underutilized Tables

Based on the vision doc, these tables have rich data but aren't fully used:

1. **`fact_player_game_stats`** (317 columns)
   - Currently using ~20-30 columns
   - **Opportunity:** Display all advanced stats, micro stats, splits

2. **`fact_goalie_game_stats`** (128 columns)
   - Currently using basic stats only
   - **Opportunity:** GSAx, save types, rebound control, danger zones

3. **`fact_events`** (140 columns)
   - Used for basic event display
   - **Opportunity:** Play-by-play, shot maps, event analysis

4. **`fact_player_micro_stats`**
   - Not used at all
   - **Opportunity:** Micro stats explorer, detailed player analysis

5. **`fact_zone_entries` / `fact_zone_exits`**
   - Not used
   - **Opportunity:** Zone analytics dashboard

6. **`fact_rushes` / `fact_rush_events`**
   - Not used
   - **Opportunity:** Rush analysis dashboard

7. **`fact_wowy`**
   - Not used
   - **Opportunity:** Line combination analysis, player chemistry

8. **`fact_line_combos`**
   - Not used
   - **Opportunity:** Team line analysis

---

## 9. Conclusion

The BenchSight dashboard has a **solid foundation** but is **underutilizing its rich data assets**. With 139 tables and 30 views available, there's tremendous opportunity to build a world-class analytics platform.

### Key Takeaways

1. **Data is Available:** The infrastructure is there - 317 columns in player stats, 128 in goalie stats, comprehensive event tracking
2. **Foundation is Solid:** Next.js architecture, Supabase integration, authentication all working
3. **Vision is Clear:** The analytics vision document provides excellent roadmap
4. **Quick Wins Available:** Many features can be implemented quickly by leveraging existing data

### Recommended Next Steps

1. **This Week:** Complete trends page, enhance player profile, add shot maps
2. **This Month:** Implement advanced analytics dashboards, game highlights, matchup predictor
3. **Next Quarter:** Add ML models, reports, video integration

### Success Metrics

- **User Engagement:** Time on site, pages per session
- **Feature Adoption:** Usage of advanced analytics features
- **Data Utilization:** Percentage of available columns displayed
- **Performance:** Page load times, query performance

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-14  
**Next Review:** After Phase 1 implementation
