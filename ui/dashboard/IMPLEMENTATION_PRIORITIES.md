# Implementation Priorities - Quick Reference

**Quick decision guide for what to build next**

---

## 🎯 This Week (High Priority)

### 1. Collapsible Accordion Sections ⏱️ 15-20 min
**Why:** Reduces scrolling, better UX  
**What:** Group advanced stats (FO, PEN, STOP, etc.) into collapsible sections  
**Impact:** High - Immediate UX improvement  
**Dependencies:** None

### 2. Matchup Predictor ⏱️ 30-45 min
**Why:** Useful feature for schedule page  
**What:** Win probability calculation, key matchup stats  
**Impact:** Medium-High - Adds value to schedule page  
**Dependencies:** `fact_team_season_stats_basic`, `fact_team_game_stats`

### 3. Play-by-Play Timeline ⏱️ 45-60 min
**Why:** Enhances game pages significantly  
**What:** Event timeline with filters, click for details  
**Impact:** High - Major game page enhancement  
**Dependencies:** `fact_events`

---

## 🚀 Next 2 Weeks (Medium Priority)

### 4. xG Analysis Dashboard ⏱️ 2-3 hours
**Why:** Core advanced analytics feature  
**What:** xG leaders, goals above expected, shot quality analysis  
**Impact:** Very High - Key analytics feature  
**Dependencies:** `fact_player_game_stats` (xg columns)

### 5. WAR/GAR Leaders Page ⏱️ 2-3 hours
**Why:** Important player valuation metric  
**What:** WAR leaders, GAR breakdown, trends  
**Impact:** High - Advanced analytics  
**Dependencies:** `fact_player_game_stats` (war, gar columns)

### 6. Micro Stats Explorer ⏱️ 3-4 hours
**Why:** Unique detailed stats  
**What:** Interactive micro stats breakdown  
**Impact:** Medium-High - Detailed analysis  
**Dependencies:** `fact_player_micro_stats`

### 7. Zone Analytics Dashboard ⏱️ 3-4 hours
**Why:** Advanced zone analysis  
**What:** Zone entry/exit analysis, heat maps  
**Impact:** Medium-High - Tactical analysis  
**Dependencies:** `fact_zone_entries`, `fact_zone_exits`

---

## 📊 Quick Wins (< 1 Hour Each)

1. **Enhanced Game Highlights** - Better filtering (30 min)
2. **Player Search Improvements** - Better filters (45 min)
3. **Team Comparison Tool** - Side-by-side stats (45 min)
4. **Export to CSV** - Enhanced export (30 min)
5. **Loading States** - Better UX (30 min)
6. **Empty States** - Better messaging (20 min)

---

## 🎨 UI/UX Improvements

1. **Collapsible Sections** - Reduce scrolling (15-20 min)
2. **Better Mobile Responsiveness** - Improve mobile UX (2-3 hours)
3. **Dark Mode Toggle** - User preference (1-2 hours)
4. **Keyboard Shortcuts** - Power user feature (2-3 hours)
5. **Breadcrumbs** - Better navigation (30 min)

---

## 🔧 Technical Debt

1. **Remove @ts-nocheck** - Fix TypeScript properly (1-2 hours)
2. **Add Error Boundaries** - Better error handling (1-2 hours)
3. **Add Unit Tests** - Component testing (4-6 hours)
4. **Performance Optimization** - ISR, caching (2-3 hours)
5. **Code Splitting** - Reduce bundle size (2-3 hours)

---

## 💡 Feature Ideas (From Vision Doc)

### High Impact Features
- **Player Comparison Enhancement** - Multi-player radar charts
- **Goalie Advanced Metrics** - GSAx, save types, heat maps
- **Line Combinations Analysis** - WOWY, optimal lines
- **Shift Charts** - Visual shift timeline
- **Game Flow Visualization** - xG timeline, momentum

### Medium Impact Features
- **Rush Analysis Dashboard** - Rush leaders, success rates
- **Faceoff Analysis Dashboard** - Advanced faceoff stats
- **Team Zone Time** - Zone time heat maps
- **Player Trends** - Performance trends over time
- **Matchup Analysis** - Head-to-head records

### Future Features (ML/AI)
- **Game Outcome Prediction** - Win probability model
- **Player Performance Prediction** - Forecast stats
- **Player Valuation Model** - Value scoring
- **Line Optimization** - Optimal line suggestions
- **Player Similarity** - Find similar players

---

## 📋 Decision Framework

**Choose features based on:**
1. **User Value** - How much does it help users?
2. **Effort** - How long will it take?
3. **Data Availability** - Do we have the data?
4. **Dependencies** - What needs to be done first?
5. **Impact** - How many users will benefit?

**Quick Decision:**
- **< 1 hour?** → Do it if it adds value
- **1-3 hours?** → High priority if high impact
- **3+ hours?** → Plan carefully, ensure data available

---

**Last Updated:** 2026-01-14
