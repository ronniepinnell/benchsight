# BenchSight Goals Roadmap
## Short, Mid, and Long-Term Objectives

---

## 🎯 SHORT-TERM GOALS (Next 1-2 Sessions)

### 1. Deploy to Supabase ⭐ TOP PRIORITY
**Status:** Ready to execute  
**Effort:** 1-2 hours  
**Dependencies:** None

Steps:
1. Create Supabase project
2. Run `sql/01_create_tables_generated.sql`
3. Import CSVs from `data/output/`
4. Verify row counts
5. Test sample queries

### 2. Track Remaining Games
**Status:** Blocked (need manual tracking)  
**Effort:** 1-2 hours per game (tracking)  
**Games:** 18965, 18991, 19032

Once tracked:
1. Place `{game_id}_tracking.xlsx` in `data/raw/games/{game_id}/`
2. Run full ETL pipeline
3. Verify goals match official

### 3. Clean Up Exception Handling
**Status:** In progress  
**Effort:** 1 hour  
**Files:** Admin scripts in `src/`

Replace remaining bare `except:` with specific exceptions.

---

## 📈 MID-TERM GOALS (1-2 Months)

### 1. Load Full Season
**Target:** 50+ games loaded  
**Prerequisites:** Games need to be tracked

Benefits:
- Better statistical significance
- Season-long player trends
- Team performance analysis

### 2. Build Power BI Dashboard
**Status:** HTML prototypes exist  
**Effort:** 3-5 hours

Features:
- Player comparison tool
- Game-by-game breakdown
- Team standings
- Top performers

### 3. Add Incremental Loading
**Status:** Not started  
**Effort:** 4-6 hours

Currently reprocesses all games each run. Need:
- Track which games already processed
- Only process new/changed games
- Append to existing tables

### 4. Improve Test Coverage
**Status:** ~3% coverage  
**Target:** 50% coverage

Add pytest tests for:
- Core stat calculations
- Key transformations
- Edge cases

---

## 🚀 LONG-TERM GOALS (3-6 Months)

### 1. Expected Goals (xG) Model
**Status:** Placeholders exist  
**Effort:** 20+ hours

Requirements:
- XY coordinate tracking in source
- Historical shot data
- ML model training

Approach:
1. Collect XY data for shots
2. Build shot quality model
3. Calculate expected goals from shot location/type
4. Compare actual vs expected

### 2. Real-Time Game Tracking
**Status:** Not started  
**Effort:** 40+ hours

Vision:
- Live event entry during game
- Real-time stat updates
- In-game dashboards

### 3. Multi-League Support
**Status:** Structure exists  
**Effort:** 10+ hours

Enable:
- Multiple leagues (NORAD, CSAHA, etc.)
- Cross-league player tracking
- League comparison analytics

### 4. Player Development Tracking
**Status:** Season-over-season framework exists  
**Effort:** 5-10 hours

Features:
- Year-over-year stat comparison
- Skill rating progression
- Improvement areas identification

### 5. Video Integration
**Status:** URLs stored, not integrated  
**Effort:** 15+ hours

Features:
- Click event → jump to video timestamp
- Auto-clip generation for highlights
- Goal/save replay access

---

## 🎯 SUCCESS METRICS

### Short-Term
- [ ] Supabase deployment working
- [ ] All current games verified
- [ ] QA monitoring active

### Mid-Term
- [ ] 50+ games loaded
- [ ] Dashboard published
- [ ] <1 minute ETL for new game

### Long-Term
- [ ] xG model accurate to ±0.5 goals/game
- [ ] Real-time tracking operational
- [ ] 200+ games in system

---

## 📊 PRIORITY MATRIX

| Goal | Impact | Effort | Priority |
|------|--------|--------|----------|
| Supabase Deploy | High | Low | 🔴 NOW |
| Track More Games | High | High | 🟡 NEXT |
| Power BI Dashboard | Medium | Medium | 🟡 NEXT |
| Incremental Loading | Medium | Medium | 🟢 SOON |
| xG Model | High | Very High | 🔵 LATER |
| Real-Time Tracking | High | Very High | 🔵 LATER |

---

## 🗓️ Suggested Timeline

### Week 1-2
- Deploy to Supabase
- Verify deployment working
- Document any issues

### Week 3-4
- Track and load remaining games
- Build basic Power BI dashboard
- Clean up technical debt

### Month 2
- Load 20+ games
- Incremental loading
- Improve test coverage

### Month 3+
- Full season loaded
- Advanced dashboards
- Begin xG model research

---

## 📝 Notes

- Goals depend on source data quality
- XY tracking requires tracker software update
- Real-time tracking is major undertaking
- Focus on deployment first - everything else can wait
