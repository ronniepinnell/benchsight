# BenchSight Dashboard - TODO & Future Roadmap

**Last Updated:** 2026-01-14  
**Status:** Active Development

---

## 🎯 Current TODOs (In Progress)

### High Priority - Immediate
- [ ] **Add collapsible accordion sections** for advanced stats (FO, PEN, STOP, etc.)
  - Group related stats into collapsible sections
  - Reduce scrolling on player profile pages
  - Use Radix UI Accordion component
  - **Effort:** 15-20 min

- [ ] **Test all new components** and verify functionality
  - Test player profile tabs
  - Test enhanced shot maps
  - Test analytics trends page
  - Verify dropdown player selection
  - **Effort:** 30-45 min

- [ ] **Fix any TypeScript/build errors** before Vercel deployment
  - Run `npm run build` locally
  - Fix any type errors
  - Verify all imports work
  - **Effort:** 15-30 min

### Medium Priority - This Week
- [ ] **Matchup Predictor Component**
  - Win probability calculation
  - Add to schedule/upcoming games page
  - Display key matchup stats
  - **Effort:** 30-45 min
  - **Data:** `fact_team_season_stats_basic`, `fact_team_game_stats`, `dim_schedule`

- [ ] **Play-by-Play Timeline**
  - Event timeline on game detail pages
  - Filter by event type
  - Click to see event details
  - **Effort:** 45-60 min
  - **Data:** `fact_events`

- [ ] **Blog / Insights Hub**
  - Add `/norad/blog` list + post detail (MDX/Markdown)
  - Surface latest post on NORAD home and nav
  - Seed with ML idea post and RSS/JSON feed
  - **Effort:** 1-2 hours

- [ ] **Dashboard Landing Page**
  - Marketing/what-is-BenchSight hero with CTA to portal/signup
  - Feature bullets, screenshots, trust/usage highlights
  - Add link from top nav/footer
  - **Effort:** 1-2 hours

- [ ] **Enhanced Game Page**
  - Add shift charts visualization
  - Improve boxscore display
  - Add period-by-period breakdown
  - **Effort:** 1-2 hours

---

## 🚀 Future Roadmap Ideas

### Phase 1: Core Enhancements (Weeks 1-2)

#### 1.1 Advanced Analytics Dashboards
- [ ] **xG Analysis Dashboard**
  - xG Leaders table
  - Goals Above Expected chart
  - xG Timeline (game flow)
  - Shot Quality Analysis
  - **Effort:** 2-3 hours
  - **Data:** `fact_player_game_stats` (xg_for, xg_adj, goals_above_expected)

- [ ] **WAR/GAR Leaders Page**
  - WAR Leaders table
  - GAR Component Breakdown
  - WAR Trends over time
  - WAR by Position
  - **Effort:** 2-3 hours
  - **Data:** `fact_player_game_stats`, `fact_goalie_game_stats`

- [ ] **Micro Stats Explorer**
  - Interactive micro stats breakdown
  - Deke success rate, drive success rate
  - Zone entry/exit success rates
  - Rush involvement metrics
  - **Effort:** 3-4 hours
  - **Data:** `fact_player_micro_stats`

- [ ] **Zone Analytics Dashboard**
  - Zone Entry Analysis
  - Zone Exit Analysis
  - Zone Time Heat Maps
  - Zone Entry/Exit Success Rates
  - **Effort:** 3-4 hours
  - **Data:** `fact_zone_entries`, `fact_zone_exits`, `fact_team_zone_time`

#### 1.2 Player Profile Enhancements
- [ ] **Player Comparison Tool Enhancement**
  - Side-by-side comparison (2-4 players)
  - Radar chart for multi-player comparison
  - Advanced metrics comparison table
  - Trend comparisons
  - **Effort:** 2-3 hours

- [ ] **Player Trends Page**
  - Time series charts (Goals/Game, Points/Game, WAR trend)
  - Rolling averages (5-game, 10-game)
  - Performance vs. rating comparison
  - Streak analysis (hot/cold streaks)
  - **Effort:** 2-3 hours
  - **Data:** `fact_player_game_stats`, `fact_player_season_stats`

- [ ] **Player Micro Stats Tab**
  - Dedicated micro stats explorer
  - Success rate visualizations
  - Detailed micro stat breakdowns
  - **Effort:** 2-3 hours
  - **Data:** `fact_player_micro_stats`

#### 1.3 Team Analytics
- [ ] **Line Combinations Analysis**
  - Line performance (CF%, xGF%, etc.)
  - WOWY (With Or Without You) analysis
  - Optimal line suggestions
  - **Effort:** 3-4 hours
  - **Data:** `fact_line_combos`, `fact_wowy`

- [ ] **Team Zone Time Analysis**
  - Zone time breakdown (O-zone, N-zone, D-zone)
  - Zone time heat maps
  - Zone time by period/game state
  - **Effort:** 2-3 hours
  - **Data:** `fact_team_zone_time`

- [ ] **Team Matchup Analysis**
  - Head-to-head records
  - Matchup statistics
  - Historical performance
  - **Effort:** 2-3 hours
  - **Data:** `fact_team_game_stats`, `dim_schedule`

#### 1.4 Game Page Enhancements
- [ ] **Shift Charts Visualization**
  - Shift timeline for each player
  - Line combinations visualization
  - TOI breakdown
  - **Effort:** 3-4 hours
  - **Data:** `fact_shifts`, `fact_shift_players`

- [ ] **Enhanced Shot Maps**
  - Period-by-period shot maps
  - Strength situation filters
  - Player-specific shot maps
  - **Effort:** 2-3 hours

- [ ] **Game Flow Visualization**
  - xG Timeline
  - Momentum shifts
  - Key moments timeline
  - **Effort:** 2-3 hours
  - **Data:** `fact_events`

---

### Phase 2: Advanced Features (Weeks 3-4)

#### 2.1 Goalie Analytics
- [ ] **Goalie Advanced Metrics Page**
  - GSAx (Goals Saved Above Expected)
  - Save Type Breakdown (Butterfly, Pad, Glove, etc.)
  - Rebound Control metrics
  - Danger Zone Stats (High/Medium/Low)
  - Save Location Heat Maps
  - **Effort:** 4-5 hours
  - **Data:** `fact_goalie_game_stats` (128 columns), `fact_saves`

- [ ] **Goalie Comparison Tool**
  - Side-by-side goalie comparison
  - Save % comparison chart
  - GSAx comparison
  - Save type distribution comparison
  - **Effort:** 2-3 hours

#### 2.2 Reports & Export
- [ ] **PDF Export Functionality**
  - Player Performance Report
  - Team Performance Report
  - Game Recap Report
  - **Effort:** 4-6 hours
  - **Tools:** Puppeteer, PDFKit, or React-PDF

- [ ] **CSV/Excel Export**
  - Enhanced CSV export
  - Excel export with formatting
  - Custom report builder
  - **Effort:** 2-3 hours
  - **Tools:** ExcelJS

- [ ] **Scheduled Reports**
  - Daily/weekly/monthly reports
  - Email delivery
  - Automated generation
  - **Effort:** 4-6 hours

#### 2.3 Rush & Faceoff Analysis
- [ ] **Rush Analysis Dashboard**
  - Rush Leaders
  - Rush Success Rates
  - Breakaway Analysis
  - Odd-Man Rush Analysis
  - Rush xG Analysis
  - **Effort:** 3-4 hours
  - **Data:** `fact_rushes`, `fact_rush_events`

- [ ] **Faceoff Analysis Dashboard**
  - Faceoff Leaders
  - Faceoff Win % by Zone
  - WDBE Faceoff Analysis
  - Faceoff Outcomes
  - **Effort:** 2-3 hours
  - **Data:** `fact_faceoffs`

---

### Phase 3: Machine Learning & Predictive (Weeks 5-8)

#### 3.1 Predictive Models
- [ ] **Game Outcome Prediction**
  - Win probability model
  - Predicted score
  - Model: XGBoost/Random Forest
  - **Effort:** 8-12 hours
  - **Data:** `fact_team_season_stats`, `fact_player_season_stats`, `fact_h2h`

- [ ] **Player Performance Prediction**
  - Predicted goals, points, xG
  - Model: Time series (LSTM/GRU)
  - **Effort:** 10-15 hours
  - **Data:** `fact_player_game_stats`, `fact_player_season_stats`

- [ ] **Goalie Performance Prediction**
  - Predicted save %, GSAx
  - Model: XGBoost
  - **Effort:** 8-12 hours
  - **Data:** `fact_goalie_game_stats`, `fact_saves`

#### 3.2 Player Valuation
- [ ] **Player Value Model**
  - Player value score
  - Model: Regression (XGBoost)
  - **Effort:** 6-8 hours
  - **Data:** `fact_player_career_stats`, `fact_player_season_stats`

- [ ] **Contract Value Prediction**
  - Predicted contract value
  - Model: Regression
  - **Effort:** 6-8 hours

#### 3.3 Advanced Analytics Models
- [ ] **Enhanced xG Model**
  - Current: Lookup table
  - Target: Gradient Boosting Machine (GBM)
  - Features: Shot location, shot type, context
  - **Effort:** 12-16 hours
  - **Data:** `fact_events`, `fact_shot_event`

- [ ] **RAPM (Regularized Adjusted Plus-Minus)**
  - Isolated player impact
  - Model: Ridge Regression
  - **Effort:** 16-20 hours
  - **Data:** `fact_shift_players`, `fact_events` (requires stint structure)

- [ ] **Expected Threat (xT) Model**
  - Zone value, transition value
  - Model: Markov Chain
  - **Effort:** 10-12 hours
  - **Data:** `fact_zone_entries`, `fact_zone_exits`, `fact_events`

- [ ] **Player Similarity Model**
  - Similarity scores
  - Model: Clustering (K-Means), Embeddings
  - **Effort:** 8-10 hours
  - **Data:** `fact_player_career_stats`, `fact_player_micro_stats`

- [ ] **Line Optimization Model**
  - Optimal line combinations
  - Model: Optimization (Genetic Algorithm) + Regression
  - **Effort:** 12-16 hours
  - **Data:** `fact_line_combos`, `fact_wowy`

---

### Phase 4: UI/UX Enhancements (Ongoing)

#### 4.1 Performance Optimization
- [ ] **Add ISR (Incremental Static Regeneration)**
  - For leaderboards
  - For standings
  - For frequently accessed pages
  - **Effort:** 2-3 hours

- [ ] **Implement proper caching**
  - Add `revalidate` tags to more pages
  - Cache expensive queries
  - Add caching headers
  - **Effort:** 2-3 hours

- [ ] **Code splitting**
  - Lazy load heavy visualizations
  - Split large components
  - Optimize bundle size
  - **Effort:** 3-4 hours

#### 4.2 Error Handling & Monitoring
- [ ] **Add error boundaries**
  - React error boundaries
  - Better error pages (404, 500)
  - Error logging
  - **Effort:** 2-3 hours

- [ ] **Add monitoring**
  - Vercel Analytics
  - Performance monitoring
  - Error tracking (Sentry, LogRocket)
  - **Effort:** 2-3 hours

#### 4.3 SEO & Accessibility
- [ ] **Add proper metadata**
  - Open Graph tags
  - Structured data (JSON-LD)
  - Meta descriptions
  - **Effort:** 2-3 hours

- [ ] **Accessibility improvements**
  - ARIA labels
  - Keyboard navigation
  - Screen reader support
  - **Effort:** 4-6 hours

---

### Phase 5: Video Integration (Future)

#### 5.1 Video Features
- [ ] **Video Player with Event Sync**
  - Sync events to video timestamps
  - Jump to highlights
  - Playback controls
  - **Effort:** 8-12 hours

- [ ] **Highlight Management**
  - Video URL management
  - Highlight timestamps
  - Video upload/storage
  - **Effort:** 6-8 hours

#### 5.2 Computer Vision (Future)
- [ ] **Video Analysis Models**
  - Shot recognition
  - Player tracking
  - Event detection
  - Technique analysis
  - **Effort:** 20+ hours (research phase)

---

## 📊 Data Utilization Opportunities

### Underutilized Tables (Rich Data Available)

| Table | Columns | Current Usage | Opportunity |
|-------|---------|---------------|-------------|
| `fact_player_game_stats` | 317 | ~20-30 columns | Display all advanced stats, micro stats, splits |
| `fact_goalie_game_stats` | 128 | ~10-15 columns | GSAx, save types, rebound control, danger zones |
| `fact_events` | 140 | Basic event display | Play-by-play, shot maps, event analysis |
| `fact_player_micro_stats` | Many | Not used | Micro stats explorer, detailed analysis |
| `fact_zone_entries` / `fact_zone_exits` | Many | Not used | Zone analytics dashboard |
| `fact_rushes` / `fact_rush_events` | Many | Not used | Rush analysis dashboard |
| `fact_wowy` | Many | Not used | Line combination analysis, player chemistry |
| `fact_line_combos` | Many | Not used | Team line analysis |
| `fact_faceoffs` | Many | Basic usage | Advanced faceoff analysis |
| `fact_matchup_performance` | Many | Not used | Player matchups, team analysis |

---

## 🎯 Quick Wins (1-2 Hours Each)

1. **Collapsible Accordion Sections** - Organize advanced stats
2. **Matchup Predictor** - Win probability on schedule page
3. **Play-by-Play Timeline** - Event timeline on game pages
4. **Enhanced Game Highlights** - Better filtering and display
5. **Player Search Improvements** - Better filters and sorting
6. **Team Comparison Tool** - Side-by-side team stats
7. **Season Selector Enhancement** - Better season navigation
8. **Export to CSV** - Enhanced export functionality
9. **Loading States** - Better loading indicators
10. **Empty States** - Better "no data" messages

---

## 🔧 Technical Improvements

### Code Quality
- [ ] Remove `@ts-nocheck` from player page
- [ ] Fix all TypeScript errors properly
- [ ] Add proper types for all database queries
- [ ] Generate types from Supabase schema
- [ ] Add unit tests for components
- [ ] Add integration tests for pages

### Component Organization
- [ ] Create reusable chart components library
- [ ] Build visualization component library
- [ ] Standardize stat display components
- [ ] Create shared UI component library

### Data Fetching
- [ ] Add proper loading states everywhere
- [ ] Implement error boundaries
- [ ] Add data caching strategies
- [ ] Optimize query performance
- [ ] Add database indexes for common queries

---

## 📈 Feature Ideas from Analytics Vision

### Dashboard Pages to Build (50+ Pages from Vision Doc)

#### Player Dashboards (15+ Pages)
- [ ] Player Directory / Leaderboard
- [ ] Player Profile (Enhanced - in progress)
- [ ] Player Comparison (Basic exists, enhance)
- [ ] Player Trends
- [ ] Player Micro Stats Explorer
- [ ] Player Matchup Analysis
- [ ] Player Line Combinations
- [ ] Player Situational Stats
- [ ] Player Career Trajectory

#### Goalie Dashboards (10+ Pages)
- [ ] Goalie Directory
- [ ] Goalie Profile (Enhanced)
- [ ] Goalie Comparison
- [ ] Goalie Advanced Metrics
- [ ] Goalie Performance Trends
- [ ] Goalie Save Analysis
- [ ] Goalie Workload Analysis

#### Team Dashboards (12+ Pages)
- [ ] Team Profile (Enhanced)
- [ ] Team Comparison
- [ ] Team Line Combinations
- [ ] Team Zone Time Analysis
- [ ] Team Matchups (H2H)
- [ ] Team Roster Analysis
- [ ] Team Performance Trends

#### Game Dashboards (10+ Pages)
- [ ] Game Center (Live)
- [ ] Game Recap
- [ ] Game Boxscore (Enhanced)
- [ ] Play-by-Play (Add)
- [ ] Shift Charts (Add)
- [ ] Shot Maps (Enhanced - done)
- [ ] Game Analytics

#### Advanced Analytics (15+ Pages)
- [ ] Advanced Metrics Hub
- [ ] xG Analysis Dashboard
- [ ] WAR/GAR Leaders
- [ ] RAPM Analysis (future)
- [ ] Micro Stats Explorer
- [ ] Zone Entry/Exit Analysis
- [ ] Rush Analysis
- [ ] Faceoff Analysis

---

## 🚀 Implementation Priority Matrix

### P0 - Critical (Do First)
1. Collapsible accordion sections
2. Test and fix all components
3. Vercel deployment preparation

### P1 - High Value (This Week)
1. Matchup Predictor
2. Play-by-Play Timeline
3. xG Analysis Dashboard
4. WAR/GAR Leaders Page

### P2 - Important (Next 2 Weeks)
1. Micro Stats Explorer
2. Zone Analytics Dashboard
3. Line Combinations Analysis
4. Goalie Advanced Metrics

### P3 - Nice to Have (Next Month)
1. Reports & Export
2. Rush Analysis Dashboard
3. Faceoff Analysis Dashboard
4. Player Similarity Model

### P4 - Future (When Data Ready)
1. RAPM Implementation
2. Enhanced xG Model (GBM)
3. Video Integration
4. Computer Vision Models

---

## 📝 Notes

- **Data is Available:** 139 tables + 30 views with rich data
- **Foundation is Solid:** Next.js 16, Supabase, good architecture
- **Quick Wins Available:** Many features can be implemented quickly
- **Focus Areas:** Analytics dashboards, visualizations, ML models

---

**Last Updated:** 2026-01-14  
**Next Review:** After Phase 1 completion
