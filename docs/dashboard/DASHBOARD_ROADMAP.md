# BenchSight Dashboard Roadmap

**Development roadmap from current state to end goal**

Last Updated: 2026-01-21
Version: 2.00

---

## Overview

This document outlines the roadmap for the BenchSight dashboard, from current state to the complete vision.

**Current State:** ~50% complete (foundation built, many pages functional)  
**End Goal:** Complete analytics platform with all features from vision document

**Design References:**
- [Wireframes](../reference/design/wireframes/wireframes.md) - Layout patterns and wireframes
- [UI Inspiration](../reference/inspiration/) - Screenshots and design inspiration
- [Reference Links](../reference/inspiration/links.md) - Hockey analytics platform references

---

## Current State Assessment

### ✅ Completed Features

**Core Pages:**
- ✅ Standings (All-Time, Prior Seasons, Current Season)
- ✅ Player Rankings (with season filter, summer team filtering)
- ✅ Team Pages (Overview, Roster, Lines, Analytics, Matchups tabs)
- ✅ Game Pages (Box scores, team stats comparison, scoring summary, play-by-play)
- ✅ Player Pages (Overview, Career, Season, Advanced tabs with multi-season support)
- ✅ Leaders Pages (Goals, Assists, Points, GAA, Save %)

**Data Features:**
- ✅ Season filtering across all pages
- ✅ Game type filtering (All, Regular, Playoffs)
- ✅ Historical data support (prior seasons)
- ✅ Sub players/goalies tracking
- ✅ Team-specific GAA calculations for sub goalies
- ✅ Position-based roster organization (Forwards/Defense)
- ✅ Jersey numbers and ratings display
- ✅ Champion/Runner-up tracking

**UI/UX:**
- ✅ NORAD route prefix (`/norad/*`)
- ✅ Responsive design
- ✅ Sortable tables
- ✅ Searchable dropdowns
- ✅ Team logo overflow effect
- ✅ Enhanced game/team page headers

**Analytics Pages:**
- ✅ Analytics Overview
- ✅ Statistics page
- ✅ Trends page
- ✅ Zone Analytics
- ✅ Micro Stats Explorer
- ✅ Lines Analytics
- ✅ Faceoffs Analytics
- ✅ Rushes Analytics
- ✅ Shot Chains Analysis

**Export:**
- ✅ CSV Export (Players, Goalies, Analytics pages)

---

## Roadmap Phases

### Phase 1: Foundation (COMPLETE ✅)

**Goal:** Core infrastructure and basic pages

**Completed:**
- ✅ Next.js 14 setup with App Router
- ✅ Supabase integration
- ✅ Authentication
- ✅ Basic pages (standings, leaders, players, teams, games)
- ✅ Component library
- ✅ Design system

---

### Phase 2: Enhanced Features (IN PROGRESS 🚧)

**Goal:** Complete remaining core features

**In Progress:**
- 🚧 Enhanced visualizations (shot maps, heat maps)
- 🚧 Advanced analytics pages
- 🚧 Search and filter integration
- 🚧 Export functionality expansion

**Remaining:**
- [ ] Enhanced player comparison (radar charts, H2H stats)
- [ ] Enhanced goalie comparison
- [ ] Team comparison enhancements
- [ ] Breadcrumbs navigation
- [ ] Enhanced tooltips with formula explanations
- [ ] Blog/Insights hub (`/norad/blog`) with MDX posts, RSS, and navigation surfacing
- [ ] Marketing/landing page for BenchSight dashboard (hero, features, CTA)
- [ ] Mobile optimization

---

### Phase 3: Advanced Analytics (PLANNED 📋)

**Goal:** Complete advanced analytics features

**Planned:**
- [ ] xG Analysis page (complete)
- [ ] WAR/GAR Analysis page (complete)
- [ ] RAPM Analysis (future)
- [ ] Predictive analytics
- [ ] AI-powered insights
- [ ] Custom report builder

---

### Phase 4: User Experience (PLANNED 📋)

**Goal:** Enhanced user experience and polish

**Planned:**
- [ ] Real-time updates (WebSocket)
- [ ] Notifications system
- [ ] Saved searches/filters
- [ ] User preferences
- [ ] Dark/light mode toggle
- [ ] Accessibility improvements

---

### Phase 5: Performance & Scale (PLANNED 📋)

**Goal:** Optimize for performance and scale

**Planned:**
- [ ] Query optimization
- [ ] Caching strategy
- [ ] Image optimization
- [ ] Code splitting optimization
- [ ] Load time optimization
- [ ] Mobile performance

---

## Feature Priorities

### High Priority (Next 2-4 Weeks)

1. **Enhanced Visualizations**
   - Complete shot maps
   - Heat maps for zone time
   - Enhanced trend charts

2. **Search & Filters**
   - Integrate search into all pages
   - Advanced filter options
   - Saved filter presets

3. **Export Expansion**
   - Export for all pages
   - Custom export formats
   - Scheduled exports

4. **Mobile Optimization**
   - Responsive tables
   - Mobile navigation
   - Touch-friendly interactions

5. **Insights & Landing**
   - `/norad/blog` with MDX posts, RSS, and latest-post surface on home
   - Marketing/landing page with hero, feature highlights, and CTA to portal/signup

### Medium Priority (1-2 Months)

1. **Advanced Analytics**
   - Complete xG analysis
   - Complete WAR/GAR analysis
   - RAPM analysis

2. **User Experience**
   - Breadcrumbs
   - Enhanced tooltips
   - User preferences

3. **Performance**
   - Query optimization
   - Caching improvements
   - Load time reduction

### Low Priority (Future)

1. **Predictive Analytics**
   - Win probability
   - Player performance prediction

2. **AI Features**
   - AI-powered insights
   - Automated reports

3. **Real-Time Features**
   - WebSocket integration
   - Live game updates

---

## End Goal Vision

### Complete Feature Set

**Players:**
- ✅ Player Directory
- ✅ Player Profile (individual)
- ✅ Player Comparison (2+ players)
- 🚧 Player Search & Filters (in progress)
- ✅ Player Trends
- ✅ Player Matchups

**Goalies:**
- ✅ Goalie Directory
- ✅ Goalie Profile
- ✅ Goalie Comparison
- ✅ Goalie Advanced Metrics
- ✅ Goalie Performance Trends

**Teams:**
- ✅ Team Directory
- ✅ Team Profile
- ✅ Team Comparison
- ✅ Team Line Combinations
- ✅ Team Zone Time Analysis
- ✅ Team Matchups (H2H)

**Games:**
- ✅ Game Center (Live)
- ✅ Game Recap
- ✅ Game Boxscore
- ✅ Play-by-Play
- ✅ Shift Charts
- 🚧 Shot Maps (in progress)
- ✅ Game Analytics

**Analytics:**
- ✅ Advanced Metrics Hub
- 🚧 xG Analysis (in progress)
- 🚧 WAR/GAR Leaders (in progress)
- [ ] RAPM Analysis (future)
- ✅ Micro Stats Explorer
- ✅ Zone Entry/Exit Analysis
- ✅ Rush Analysis
- ✅ Faceoff Analysis

---

## Success Metrics

### Phase 2 (Current)

- [ ] All core pages functional
- [ ] Enhanced visualizations complete
- [ ] Search/filter integrated
- [ ] Export functionality complete
- [ ] Mobile optimized

### Phase 3

- [ ] All advanced analytics pages complete
- [ ] Predictive analytics implemented
- [ ] AI insights available

### Phase 4

- [ ] Real-time updates working
- [ ] Notifications system functional
- [ ] User preferences saved

### Phase 5

- [ ] Page load time < 2 seconds
- [ ] Query response time < 500ms
- [ ] Mobile performance optimized

---

## Related Documentation

- [DASHBOARD_ARCHITECTURE.md](DASHBOARD_ARCHITECTURE.md) - Architecture overview
- [DASHBOARD_COMPONENT_CATALOG.md](DASHBOARD_COMPONENT_CATALOG.md) - Component reference
- [DASHBOARD_DATA_FLOW.md](DASHBOARD_DATA_FLOW.md) - Data flow
- [DASHBOARD_PAGES_INVENTORY.md](DASHBOARD_PAGES_INVENTORY.md) - Pages inventory

---

*Last Updated: 2026-01-15*
