# BenchSight Dashboard Pages Inventory

**Complete inventory of all pages, routes, and their status**

Last Updated: 2026-01-21
Version: 2.00

---

## Overview

This document catalogs all pages in the BenchSight dashboard, their routes, features, and completion status.

**Total Pages:** 50+ pages  
**Route Prefix:** `/norad/*`

---

## Page Categories

### Player Pages

| Route | Page | Status | Features |
|-------|------|--------|----------|
| `/norad/players` | Player Directory | ✅ Complete | Rankings, search, filters |
| `/norad/players/[playerId]` | Player Profile | ✅ Complete | Overview, Season, Career, Advanced tabs |
| `/norad/players/[playerId]/games` | Player Games | ✅ Complete | Game log table |
| `/norad/players/[playerId]/games/[gameId]` | Player Game Detail | ✅ Complete | Individual game stats |
| `/norad/players/[playerId]/trends` | Player Trends | ✅ Complete | Trend charts, streaks |
| `/norad/players/compare` | Player Comparison | ✅ Complete | Side-by-side comparison |
| `/norad/players/matchups` | Player Matchups | ✅ Complete | H2H matchups |

### Goalie Pages

| Route | Page | Status | Features |
|-------|------|--------|----------|
| `/norad/goalies` | Goalie Leaders | ✅ Complete | GAA, Wins, Save % tabs |
| `/norad/goalies/[goalieId]` | Goalie Profile | ✅ Complete | Trends, stats, game log |
| `/norad/goalies/compare` | Goalie Comparison | ✅ Complete | Side-by-side comparison |

### Team Pages

| Route | Page | Status | Features |
|-------|------|--------|----------|
| `/norad/teams` | Team Directory | ✅ Complete | All teams grid |
| `/norad/teams/[teamId]` | Team Profile | ✅ Complete | Overview, Roster, Lines, Analytics, Matchups tabs |
| `/norad/teams/compare` | Team Comparison | ✅ Complete | Side-by-side comparison |
| `/norad/teams/free-agents` | Free Agents | ✅ Complete | Free agent list |

### Game Pages

| Route | Page | Status | Features |
|-------|------|--------|----------|
| `/norad/games` | Game Directory | ✅ Complete | Recent games list |
| `/norad/games/[gameId]` | Game Detail | ✅ Complete | Box score, scoring summary, play-by-play |
| `/norad/games/shots` | Shot Analysis | ✅ Complete | Shot charts, analysis |

### Analytics Pages

| Route | Page | Status | Features |
|-------|------|--------|----------|
| `/norad/analytics/overview` | Analytics Overview | ✅ Complete | Analytics hub |
| `/norad/analytics/statistics` | Statistics | ✅ Complete | Statistical analysis |
| `/norad/analytics/trends` | Trends | ✅ Complete | Trend analysis |
| `/norad/analytics/xg` | xG Analysis | 🚧 In Progress | Expected goals analysis |
| `/norad/analytics/war` | WAR Analysis | 🚧 In Progress | WAR/GAR analysis |
| `/norad/analytics/zone` | Zone Analytics | ✅ Complete | Zone time, entries, exits |
| `/norad/analytics/rushes` | Rush Analysis | ✅ Complete | Rush events analysis |
| `/norad/analytics/shot-chains` | Shot Chains | ✅ Complete | Shot sequence analysis |
| `/norad/analytics/shifts` | Shift Analysis | ✅ Complete | Shift analytics |
| `/norad/analytics/lines` | Line Combinations | ✅ Complete | Line effectiveness |
| `/norad/analytics/faceoffs` | Faceoff Analysis | ✅ Complete | Faceoff statistics |
| `/norad/analytics/micro-stats` | Micro Stats | ✅ Complete | Micro statistics explorer |

### League Pages

| Route | Page | Status | Features |
|-------|------|--------|----------|
| `/norad/standings` | Standings | ✅ Complete | League standings table |
| `/norad/leaders` | Leaders | ✅ Complete | Scoring leaders |
| `/norad/schedule` | Schedule | ✅ Complete | Upcoming and past games |

### Tracker Pages

| Route | Page | Status | Features |
|-------|------|--------|----------|
| `/norad/tracker` | Tracker Home | ✅ Complete | Game tracker list |
| `/norad/tracker/[gameId]` | Tracker | ✅ Complete | Game tracking interface |
| `/norad/tracker/videos` | Video Management | ✅ Complete | Video management |

### Admin Pages

| Route | Page | Status | Features |
|-------|------|--------|----------|
| `/norad/admin` | Admin Portal | ✅ Complete | Admin controls |

---

## Page Status Summary

### ✅ Complete (40+ pages)
- All player pages
- All goalie pages
- All team pages
- All game pages
- Most analytics pages
- League pages
- Tracker pages
- Admin pages

### 🚧 In Progress (2 pages)
- xG Analysis (partial)
- WAR Analysis (partial)

### 📋 Planned (Future)
- RAPM Analysis
- Predictive Analytics
- AI Insights

---

## Page Features Matrix

### Core Features

| Feature | Players | Goalies | Teams | Games | Analytics |
|---------|---------|---------|-------|-------|-----------|
| Profile Page | ✅ | ✅ | ✅ | ✅ | ✅ |
| Comparison | ✅ | ✅ | ✅ | - | - |
| Trends | ✅ | ✅ | - | - | ✅ |
| Game Log | ✅ | ✅ | - | ✅ | - |
| Advanced Stats | ✅ | ✅ | ✅ | ✅ | ✅ |
| Export | ✅ | ✅ | 🚧 | 🚧 | ✅ |

### Advanced Features

| Feature | Players | Goalies | Teams | Games | Analytics |
|---------|---------|---------|-------|-------|-----------|
| Shot Maps | ✅ | - | - | 🚧 | ✅ |
| Heat Maps | - | - | ✅ | - | ✅ |
| Radar Charts | ✅ | ✅ | ✅ | - | - |
| Trend Charts | ✅ | ✅ | - | - | ✅ |
| H2H Analysis | ✅ | - | ✅ | - | - |

---

## Route Structure

```
/norad
├── /players
│   ├── /[playerId]
│   │   ├── /games
│   │   │   └── /[gameId]
│   │   └── /trends
│   ├── /compare
│   └── /matchups
├── /goalies
│   ├── /[goalieId]
│   └── /compare
├── /teams
│   ├── /[teamId]
│   ├── /compare
│   └── /free-agents
├── /games
│   ├── /[gameId]
│   └── /shots
├── /analytics
│   ├── /overview
│   ├── /statistics
│   ├── /trends
│   ├── /xg
│   ├── /war
│   ├── /zone
│   ├── /rushes
│   ├── /shot-chains
│   ├── /shifts
│   ├── /lines
│   ├── /faceoffs
│   └── /micro-stats
├── /standings
├── /leaders
├── /schedule
├── /tracker
│   ├── /[gameId]
│   └── /videos
└── /admin
```

---

## Related Documentation

- [DASHBOARD_ARCHITECTURE.md](DASHBOARD_ARCHITECTURE.md) - Architecture overview
- [DASHBOARD_COMPONENT_CATALOG.md](DASHBOARD_COMPONENT_CATALOG.md) - Component reference
- [DASHBOARD_DATA_FLOW.md](DASHBOARD_DATA_FLOW.md) - Data flow
- [DASHBOARD_ROADMAP.md](DASHBOARD_ROADMAP.md) - Development roadmap

---

*Last Updated: 2026-01-15*
