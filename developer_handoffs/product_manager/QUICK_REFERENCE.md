# BenchSight Quick Reference for PMs

## One-Liner
NHL-level analytics for rec hockey: 317 stats, video highlights, beautiful dashboards.

## Key Numbers

| Metric | Value |
|--------|-------|
| Player stats per game | 317 |
| Database tables | 98 |
| Games processed | 9 |
| Total data rows | ~125,000 |
| Test coverage | 290 tests passing |

## User Types

| User | App | Key Features |
|------|-----|--------------|
| Players | Dashboard | Personal stats, trends, comparisons |
| Coaches | Dashboard | Line combos, H2H matchups, WOWY |
| Scorekeepers | Tracker | Real-time event entry |
| Admins | Portal | Teams, schedules, registrations |
| Fans | Dashboard/Mobile | Highlights, box scores |

## Competitive Advantages

1. **Depth**: 317 stats vs ~20 typical
2. **Advanced**: Corsi, xG, WOWY (NHL-level)
3. **Micro-stats**: Dekes, screens, backchecks
4. **Video**: Highlights linked to events (coming)

## Timeline Overview

| Phase | Timeline | Status |
|-------|----------|--------|
| 1. Foundation | Done | ✅ Complete |
| 2. Production Apps | Q1 2025 | 🔄 In Progress |
| 3. Video Highlights | Q2 2025 | 📋 Spec'd |
| 4. Portal/Admin | Q2-Q3 2025 | 📋 Planned |
| 5. Mobile App | Q3-Q4 2025 | 📋 Planned |
| 6. ML/Advanced | 2026 | 💡 Ideas |

## Monthly Costs (Projected)

| Phase | Cost |
|-------|------|
| Current (Dev) | $0 (free tier) |
| Production | ~$50/mo |
| With Video | ~$80/mo |

## Risk Summary

| Risk | Level | Mitigation |
|------|-------|------------|
| Scorer adoption | Medium | Training, simple UX |
| Stats accuracy | Medium | Validation system |
| Scale performance | Medium | Caching, indexes |
| Developer availability | Medium | Documentation |

## Decision Points Needed

1. Video storage provider (S3 vs R2 vs Supabase)
2. Auth provider (Supabase Auth vs Auth0)
3. Hosting (Vercel vs Netlify vs AWS)
4. Mobile framework (React Native vs Flutter)

## Stakeholder Map

| Stakeholder | Interest | Engagement |
|-------------|----------|------------|
| League Board | Approval, funding | Monthly updates |
| Team Captains | Adoption | Beta testers |
| Scorekeepers | Training | Weekly during rollout |
| Players | Usage | Launch announcements |

## Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Games tracked | 80% of league | DB count |
| Dashboard MAU | 200+ | Analytics |
| Load time | <2 sec | Monitoring |
| Player satisfaction | 4.5/5 | Survey |
