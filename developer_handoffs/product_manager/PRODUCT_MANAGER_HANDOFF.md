# BenchSight Product Manager Handoff

## Executive Summary

BenchSight is a comprehensive hockey analytics platform for the NORAD recreational hockey league. It transforms raw game tracking data into actionable insights through a 98-table data warehouse, enabling players, coaches, and league administrators to make data-driven decisions.

### Current State: MVP Complete ✅

| Component | Status | Notes |
|-----------|--------|-------|
| Data Pipeline (ETL) | ✅ Complete | 9 games processed, 125K rows |
| Data Warehouse | ✅ Complete | 98 tables, 317 player stats |
| Supabase Backend | ✅ Complete | PostgreSQL, ready for apps |
| Dashboard Prototype | 🟡 HTML Only | Needs React/production build |
| Tracker Prototype | 🟡 HTML Only | Needs React/production build |
| Portal Prototype | 🟡 HTML Only | Needs React/production build |
| Video Highlights | 📋 Spec'd | SQL ready, needs implementation |
| Mobile App | ❌ Not Started | Future phase |

---

## Product Vision

### Mission
Bring NHL-level analytics to recreational hockey, making every player feel like a pro.

### Target Users

| User Type | Primary Needs | Key Features |
|-----------|---------------|--------------|
| **Players** | Personal stats, improvement tracking | Dashboard, player cards |
| **Coaches** | Line optimization, matchup analysis | H2H, WOWY, line combos |
| **League Admins** | Scheduling, standings, registrations | Portal, management tools |
| **Fans/Parents** | Game recaps, highlights | Video highlights, box scores |

### Competitive Advantage
- **Depth**: 317 stats per player (vs ~20 for typical rec league)
- **Advanced Analytics**: Corsi, Fenwick, xG, WOWY - NHL-level metrics
- **Micro-Stats**: Dekes, screens, backchecks - granular tracking
- **Video Integration**: Highlight clips linked to events (coming soon)

---

## System Architecture (Big Picture)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER-FACING APPS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│   │  Dashboard  │    │   Tracker   │    │   Portal    │    │  Mobile App │ │
│   │  (Players)  │    │  (Scorers)  │    │  (Admins)   │    │  (Everyone) │ │
│   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘ │
│          │                  │                  │                  │         │
└──────────┼──────────────────┼──────────────────┼──────────────────┼─────────┘
           │                  │                  │                  │
           └──────────────────┴────────┬─────────┴──────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SUPABASE                                        │
│                         (PostgreSQL + Auth + API)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│   • 98 Tables (dims + facts)                                                │
│   • Real-time subscriptions                                                 │
│   • Row-level security                                                      │
│   • Auto-generated REST API                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                       ▲
                                       │
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA PIPELINE                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│   │   Tracker   │───►│  Excel/CSV  │───►│     ETL     │───►│   Supabase  │ │
│   │   Input     │    │   Files     │    │   Pipeline  │    │   Upload    │ │
│   └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Feature Roadmap

### Phase 1: Foundation (COMPLETE) ✅
**Timeline**: Completed
**Goal**: Core data infrastructure

| Deliverable | Status |
|-------------|--------|
| ETL Pipeline | ✅ Done |
| 98-table schema | ✅ Done |
| 317 player stats | ✅ Done |
| Supabase deployment | ✅ Done |
| Documentation | ✅ Done |

### Phase 2: Production Apps (Q1 2025)
**Timeline**: 8-12 weeks
**Goal**: Production-ready web applications

| Deliverable | Effort | Dependencies |
|-------------|--------|--------------|
| Dashboard v1 (React) | 4 weeks | Supabase complete |
| Tracker v1 (React) | 4 weeks | Dashboard complete |
| Auth integration | 1 week | Supabase Auth |
| Testing & QA | 2 weeks | All apps |

**Key Milestones**:
- Week 4: Dashboard beta to players
- Week 8: Tracker beta to scorekeepers
- Week 12: Public launch

### Phase 3: Video Highlights (Q2 2025)
**Timeline**: 4-6 weeks
**Goal**: Video clip integration

| Deliverable | Effort | Dependencies |
|-------------|--------|--------------|
| Video storage setup | 1 week | S3 or similar |
| Highlight tables | Done | SQL ready |
| Tracker clip UI | 2 weeks | Tracker v1 |
| Dashboard playback | 2 weeks | Dashboard v1 |
| Auto-highlight detection | 2 weeks | ML exploration |

**Key Milestones**:
- Week 2: Manual clip creation working
- Week 4: Clips visible in dashboard
- Week 6: Auto-suggestions for highlights

### Phase 4: Portal & Admin (Q2-Q3 2025)
**Timeline**: 6-8 weeks
**Goal**: League administration tools

| Deliverable | Effort | Dependencies |
|-------------|--------|--------------|
| Portal v1 (React) | 4 weeks | Auth complete |
| Team management | 2 weeks | Portal v1 |
| Schedule management | 2 weeks | Portal v1 |
| Registration system | 2 weeks | Portal v1 |

### Phase 5: Mobile App (Q3-Q4 2025)
**Timeline**: 12-16 weeks
**Goal**: Native mobile experience

| Deliverable | Effort | Dependencies |
|-------------|--------|--------------|
| React Native setup | 2 weeks | - |
| Dashboard mobile | 4 weeks | Dashboard v1 |
| Push notifications | 2 weeks | - |
| Offline support | 4 weeks | - |
| App store submission | 2 weeks | - |

### Phase 6: Advanced Analytics (2026)
**Timeline**: Ongoing
**Goal**: ML-powered insights

| Feature | Description |
|---------|-------------|
| Player similarity | Find comparable players |
| Lineup optimization | Suggest optimal lines |
| Injury prediction | Flag fatigue/risk |
| xG model | Custom expected goals |
| Game outcome prediction | Win probability |

---

## Component Interactions

### Data Flow: Game Day

```
GAME DAY FLOW
─────────────

1. PRE-GAME
   ┌─────────────┐
   │   Portal    │──► Create game in schedule
   └─────────────┘    Set rosters, assign refs
   
2. DURING GAME
   ┌─────────────┐
   │   Tracker   │──► Real-time event entry
   └─────────────┘    Goals, shots, passes, penalties
                      Shifts tracked automatically
   
3. POST-GAME (Automatic)
   ┌─────────────┐
   │     ETL     │──► Process tracking data
   └─────────────┘    Calculate 317 stats
                      Update standings
                      Generate box score
   
4. POST-GAME (Manual - Future)
   ┌─────────────┐
   │   Tracker   │──► Create video highlights
   └─────────────┘    Link clips to events
   
5. CONSUMPTION
   ┌─────────────┐
   │  Dashboard  │──► Players view stats
   └─────────────┘    Coaches analyze matchups
                      Fans watch highlights
```

### User Journey: Player

```
PLAYER JOURNEY
──────────────

┌─────────────────────────────────────────────────────────────────────────────┐
│ REGISTRATION                                                                 │
│ Portal → Sign up → Select team → Pay fees → Get jersey number              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ PRE-SEASON                                                                   │
│ Dashboard → View schedule → See teammates → Check opponent stats            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ GAME DAY                                                                     │
│ (Play game) → Stats tracked by scorer → ETL runs after game                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ POST-GAME                                                                    │
│ Dashboard → View box score → See personal stats → Watch highlights          │
│           → Compare to teammates → Track progress over season               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ END OF SEASON                                                                │
│ Dashboard → Season summary → Awards/rankings → Historical comparison        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Key Metrics to Track

### Product Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Games processed | 100+ | 9 |
| Active players | 300+ | - |
| Dashboard MAU | 200+ | - |
| Tracker sessions/week | 20+ | - |
| Video highlights created | 50+/week | - |

### Technical Metrics

| Metric | Target | Current |
|--------|--------|---------|
| ETL processing time | <5 min/game | ~2 min |
| Dashboard load time | <2 sec | - |
| API response time | <200ms | - |
| Uptime | 99.5% | - |
| Test coverage | 80%+ | ~60% |

### Business Metrics

| Metric | Target | Notes |
|--------|--------|-------|
| Cost per game | <$1 | Supabase free tier |
| Player satisfaction | 4.5/5 | Survey needed |
| Scorer adoption | 90%+ | Training needed |

---

## Risk Assessment

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Supabase outage | Low | High | Local CSV backup |
| ETL data loss | Low | High | Transaction support (in progress) |
| Schema changes break apps | Medium | Medium | Versioned API |
| Performance at scale | Medium | Medium | Caching, indexes |

### Product Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Scorer adoption resistance | Medium | High | Training, UX simplification |
| Stats accuracy questioned | Medium | High | Validation against official |
| Feature creep | High | Medium | Strict roadmap adherence |
| Mobile demand exceeds web | Medium | Low | Prioritize mobile in Phase 5 |

### Resource Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Developer availability | Medium | High | Document everything |
| Knowledge loss | Medium | High | Comprehensive handoffs |
| Budget constraints | Low | Medium | Use free tiers, open source |

---

## Team Structure (Recommended)

### Minimum Viable Team

| Role | Responsibility | Effort |
|------|----------------|--------|
| **Product Manager** | Roadmap, priorities, stakeholders | 0.5 FTE |
| **Full-Stack Dev** | Dashboard, Tracker, Portal | 1 FTE |
| **Backend/Data Eng** | ETL, Supabase, performance | 0.5 FTE |

### Ideal Team (Phase 3+)

| Role | Responsibility | Effort |
|------|----------------|--------|
| Product Manager | Strategy, roadmap | 0.5 FTE |
| Frontend Dev | React apps | 1 FTE |
| Backend Dev | API, ETL | 1 FTE |
| Mobile Dev | React Native | 1 FTE |
| Data Analyst | Stats, ML | 0.5 FTE |
| QA Engineer | Testing | 0.5 FTE |

---

## Decision Log

### Architectural Decisions

| Decision | Date | Rationale | Alternatives Considered |
|----------|------|-----------|------------------------|
| PostgreSQL (Supabase) | 2024 | Free tier, real-time, auth built-in | Firebase, AWS RDS |
| Python ETL | 2024 | Pandas for data manipulation | Node.js, Go |
| Star schema | 2024 | Optimized for analytics queries | Normalized, document DB |
| 317 stats | 2024 | Comprehensive = competitive advantage | Fewer stats, simpler |
| HTML prototypes first | 2024 | Fast iteration, validate UX | React from start |

### Pending Decisions

| Decision | Options | Deadline | Owner |
|----------|---------|----------|-------|
| Video storage | S3, Cloudflare R2, Supabase Storage | Phase 3 start | Backend Dev |
| Mobile framework | React Native, Flutter, PWA | Phase 5 start | Tech Lead |
| Auth provider | Supabase Auth, Auth0, Clerk | Phase 2 start | Backend Dev |
| Hosting | Vercel, Netlify, AWS | Phase 2 start | DevOps |

---

## Budget Estimate

### Phase 2 (Production Apps)

| Item | Monthly Cost | Notes |
|------|--------------|-------|
| Supabase Pro | $25 | 8GB DB, 50GB bandwidth |
| Vercel Pro | $20 | Hosting, CI/CD |
| Domain | $1 | Annual amortized |
| **Total** | **$46/mo** | |

### Phase 3+ (With Video)

| Item | Monthly Cost | Notes |
|------|--------------|-------|
| Supabase Pro | $25 | |
| Video Storage (100GB) | $15 | S3 or R2 |
| CDN | $20 | Video delivery |
| Vercel Pro | $20 | |
| **Total** | **$80/mo** | |

### Phase 5 (Mobile)

| Item | One-Time Cost | Notes |
|------|---------------|-------|
| Apple Developer | $99/yr | Required for App Store |
| Google Play | $25 | One-time |
| **Total** | **$124** | First year |

---

## Success Criteria

### Phase 2 Launch Criteria

- [ ] Dashboard loads in <2 seconds
- [ ] All 317 stats visible and accurate
- [ ] 10 players successfully onboarded
- [ ] 3 games tracked with new Tracker
- [ ] Zero critical bugs
- [ ] Documentation complete

### Phase 3 Launch Criteria

- [ ] Video upload working
- [ ] Clips linked to events
- [ ] Playback in dashboard
- [ ] 20 highlights created
- [ ] Storage costs within budget

### Overall Product Success (End of Year 1)

- [ ] 80% of league games tracked
- [ ] 200+ active dashboard users
- [ ] 4.0+ app store rating (mobile)
- [ ] <$100/month operating cost
- [ ] Positive player feedback

---

## Appendix: Quick Reference

### Key Documents

| Document | Location | Purpose |
|----------|----------|---------|
| Stats Reference | `docs/STATS_REFERENCE_COMPLETE.md` | All 317 stats explained |
| Data Dictionary | `docs/DATA_DICTIONARY.md` | All 98 tables |
| Deployment Guide | `docs/DEPLOYMENT_GUIDE.md` | Supabase setup |
| Video Highlights Spec | `docs/VIDEO_HIGHLIGHTS_SPEC.md` | Phase 3 feature |
| Honest Assessment | `docs/HONEST_ASSESSMENT.md` | What works, what doesn't |

### Key Commands

```bash
# Check system status
./run_etl.sh --status
python scripts/bulletproof_loader.py --status

# Process a game
./run_etl.sh --game 18969

# Deploy to Supabase
python scripts/bulletproof_loader.py --load all --mode upsert
```

### Contacts & Resources

| Resource | Link/Location |
|----------|---------------|
| NORAD Hockey | noradhockey.com |
| Supabase Project | [Your Supabase URL] |
| Source Code | This repository |
| Prototypes | `tracker/`, `dashboard/`, `portal/` |

