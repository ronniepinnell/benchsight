# BenchSight Project Strategy

## Vision

BenchSight aims to be the **definitive analytics platform** for NORAD recreational hockey, providing NHL-caliber statistics and insights for amateur players and teams.

---

## Strategic Pillars

### 1. Data Quality First
**Principle:** Accurate data is the foundation. No feature launches until data quality meets thresholds.

**Targets:**
- Goals: ≥98% accuracy vs ground truth
- Assists: ≥95% accuracy
- All percentages: Valid ranges (0-100%)
- No duplicate credits

**Actions:**
- Continuous validation against noradhockey.com
- Automated quality gates in ETL
- Manual review for outliers

### 2. Tracker Reliability
**Principle:** The tracker is the data entry point. If it's unreliable, everything downstream suffers.

**Targets:**
- 100% roster loading success
- Zero data loss from crashes
- <2 second event save time
- Works offline (queue and sync)

**Actions:**
- Prioritize stability over features
- Add comprehensive error handling
- Implement local storage backup

### 3. Progressive Enhancement
**Principle:** Start simple, add complexity only when base is solid.

**Roadmap:**
```
Phase 1: Basic Stats (Current)
├── Goals, Assists, Points
├── Shots, SOG, Shooting%
├── Faceoffs, Passes
└── TOI, Shifts

Phase 2: Advanced Stats
├── Zone Entries/Exits
├── Controlled Entry %
├── H2H Matchups
└── WOWY Analysis

Phase 3: Positional Data
├── XY Coordinates
├── Shot Maps
├── Heat Maps
└── Player Positioning

Phase 4: Predictive Analytics
├── Expected Goals (xG)
├── Win Probability
├── Player Impact Models
└── Game Predictions
```

### 4. User-Centric Design
**Principle:** Analytics are only valuable if users understand and use them.

**Personas:**
1. **Player:** Wants to see personal stats, compare to peers
2. **Coach:** Wants team insights, line optimization
3. **League Admin:** Wants standings, leaders, records
4. **Stats Nerd:** Wants advanced metrics, raw data access

**Actions:**
- Start with player/coach use cases
- Progressive disclosure of complexity
- Mobile-first design

---

## Competitive Advantages

### 1. Granular Tracking
Unlike box score services, BenchSight tracks:
- Every event with timestamps
- All players on ice per event
- Zone context for all plays
- XY coordinates (planned)

### 2. Rec League Focus
Most analytics tools target NHL/pro level. BenchSight is:
- Designed for 2-period games
- Handles rec league pace
- Accounts for player variety
- Affordable (Supabase free tier)

### 3. Open Data Model
- All calculations documented
- Data dictionary available
- Export capabilities
- API access (via Supabase)

---

## Risk Mitigation

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Tracker instability | High | High | Prioritize Phase 1 fixes |
| Data quality issues | Medium | High | Continuous validation |
| Supabase limits | Low | Medium | Monitor usage, plan upgrade |
| Schema changes | Medium | Medium | Version migrations |

### Organizational Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Key person dependency | High | High | Documentation, handoffs |
| Scope creep | High | Medium | Stick to phase roadmap |
| User adoption | Medium | High | Focus on player value |

---

## Success Metrics

### Phase 1 (Foundation)
- [ ] 293+ tests passing
- [ ] <5% variance on all stats vs ground truth
- [ ] Tracker saves 100% of events
- [ ] Full data dictionary

### Phase 2 (Growth)
- [ ] 10+ games processed
- [ ] 50%+ players checking stats
- [ ] Basic dashboard deployed
- [ ] Zero critical bugs

### Phase 3 (Scale)
- [ ] Full season tracked
- [ ] League standings automated
- [ ] Advanced stats adopted
- [ ] Positive NPS from users

### Phase 4 (Innovation)
- [ ] xG model deployed
- [ ] Real-time game tracking
- [ ] Mobile app launched
- [ ] Other leagues interested

---

## Resource Allocation

### Current State
- 1 part-time developer (ETL/Backend)
- Volunteer trackers (game data entry)
- Supabase free tier

### Ideal State
- 1 tracker developer (HTML/JS)
- 1 dashboard developer (React/Vue)
- 1 data engineer (Python/SQL)
- Supabase Pro tier

### Budget Considerations
- Supabase Pro: ~$25/month
- Domain/hosting: ~$15/month
- Total: ~$40/month sustainable

---

## Timeline

### Q1 2025 (Jan-Mar)
- Fix tracker reliability
- Complete data quality validation
- Basic dashboard MVP

### Q2 2025 (Apr-Jun)
- XY coordinate capture
- Shot maps and heat maps
- Player comparison tools

### Q3 2025 (Jul-Sep)
- Full season retrospective
- xG model training
- Mobile optimization

### Q4 2025 (Oct-Dec)
- Real-time tracking pilot
- Advanced analytics suite
- Expansion planning

---

## Decision Framework

### When to Add Features
✅ Add feature if:
- Data quality targets met
- User need validated
- Development capacity available
- Doesn't break existing functionality

❌ Don't add feature if:
- Data quality below threshold
- Nice-to-have vs must-have
- Introduces technical debt
- Users haven't asked for it

### When to Fix vs Build
- **Fix first** if stability <95%
- **Build first** if stability >95% AND user need urgent

### When to Automate
- If task done >3x manually
- If task is error-prone
- If task blocks development

---

## Communication Plan

### Internal
- Weekly status updates
- Decision log maintained
- Handoff docs always current

### External (Users)
- Release notes per version
- Known issues transparent
- Feedback channel open

---

## Conclusion

BenchSight's strategy is **boring by design**: prioritize reliability, validate constantly, add features progressively. The goal isn't to build the most advanced analytics platform—it's to build one that **actually works** for a recreational hockey league.

---

*Document Version: 1.0 | Last Updated: December 2024*
