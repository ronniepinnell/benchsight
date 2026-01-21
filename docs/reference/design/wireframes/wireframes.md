# Dashboard Wireframes

**Wireframe documentation based on UI inspiration screenshots**

Last Updated: 2026-01-15

---

## Overview

This document provides wireframe layouts and design patterns extracted from UI inspiration screenshots. These wireframes serve as reference for BenchSight dashboard development.

**Screenshot Source:** `docs/reference/inspiration/screenshots/`

---

## Player Page Wireframes

### Layout Pattern

```
┌─────────────────────────────────────────────────────────────┐
│ Header: Player Name, Team, Position                          │
├─────────────────────────────────────────────────────────────┤
│ [Player Photo]  │  Basic Stats (G, A, P, +/-)               │
│                 │  Season Stats Summary                      │
├─────────────────────────────────────────────────────────────┤
│ Tabs: Overview | Stats | Games | Advanced                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Main Content Area                                           │
│  - Stats tables                                              │
│  - Charts/Graphs                                             │
│  - Game log                                                  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

- **Header Section**
  - Player name, team logo, position
  - Quick stats summary
  
- **Stats Display**
  - Season totals
  - Per-game averages
  - Career totals
  
- **Tab Navigation**
  - Overview (default)
  - Detailed stats
  - Game log
  - Advanced analytics

---

## Game Page Wireframes

### Layout Pattern

```
┌─────────────────────────────────────────────────────────────┐
│ Game Header: Teams, Score, Date, Status                      │
├─────────────────────────────────────────────────────────────┤
│ Tabs: Summary | Play-by-Play | Box Score | Stats            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Main Content Area                                           │
│  - Game summary                                              │
│  - Period scores                                             │
│  - Key events                                                │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│ Team Stats Comparison                                        │
│ [Team 1 Stats]  vs  [Team 2 Stats]                          │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

- **Game Header**
  - Team names and logos
  - Final score
  - Game date and time
  - Game status
  
- **Tab Navigation**
  - Summary (default)
  - Play-by-play timeline
  - Box score
  - Team/player stats
  
- **Content Area**
  - Game events
  - Scoring plays
  - Period breakdown

---

## Team Page Wireframes

### Layout Pattern

```
┌─────────────────────────────────────────────────────────────┐
│ Header: Team Name, Logo, Record                              │
├─────────────────────────────────────────────────────────────┤
│ Tabs: Overview | Roster | Schedule | Stats                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Main Content Area                                           │
│  - Team stats summary                                        │
│  - Recent games                                              │
│  - Standings position                                        │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│ Roster Section (if on Roster tab)                           │
│ [Player List with Stats]                                     │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

- **Header Section**
  - Team name and logo
  - Season record (W-L-OTL)
  - Conference/division position
  
- **Tab Navigation**
  - Overview
  - Roster
  - Schedule
  - Team statistics
  
- **Content Area**
  - Team performance metrics
  - Recent game results
  - Upcoming schedule

---

## Analytics Dashboard Wireframes

### Layout Pattern

```
┌─────────────────────────────────────────────────────────────┐
│ Header: Dashboard Title, Filters                             │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Stat Card 1  │  │ Stat Card 2  │  │ Stat Card 3  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Chart/Graph Area                                      │   │
│  │                                                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Data Table                                            │   │
│  │                                                       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

- **Header Section**
  - Dashboard title
  - Date range filters
  - Team/player filters
  
- **Stat Cards**
  - Key metrics at a glance
  - Trend indicators
  
- **Chart Area**
  - Time series charts
  - Comparison charts
  - Distribution charts
  
- **Data Tables**
  - Sortable columns
  - Filterable rows
  - Export functionality

---

## Common Patterns

### Navigation

**Sidebar Navigation:**
- Dashboard home
- Players
- Teams
- Games
- Analytics
- Settings

**Breadcrumbs:**
- Home > Players > Player Name
- Home > Teams > Team Name
- Home > Games > Game Date

### Data Display

**Tables:**
- Sortable columns
- Filterable rows
- Pagination
- Export options

**Charts:**
- Interactive tooltips
- Zoom/pan capabilities
- Legend toggle
- Data point selection

### Responsive Design

**Mobile:**
- Stacked layout
- Collapsible sections
- Touch-friendly controls

**Desktop:**
- Multi-column layout
- Side-by-side comparisons
- Expanded data views

---

## Design Guidelines

### Color Scheme

- **Primary:** Team colors (contextual)
- **Secondary:** Neutral grays
- **Accent:** Highlight important data
- **Background:** Light theme (default)

### Typography

- **Headers:** Bold, larger size
- **Body:** Regular weight, readable size
- **Data:** Monospace for numbers
- **Labels:** Small, uppercase or lowercase

### Spacing

- **Padding:** Consistent spacing between elements
- **Margins:** Clear separation between sections
- **Grid:** 12-column grid system

---

## Implementation Notes

### Component Structure

**Player Page:**
- `PlayerHeader` component
- `PlayerStats` component
- `PlayerTabs` component
- `PlayerContent` component

**Game Page:**
- `GameHeader` component
- `GameTabs` component
- `PlayByPlayTimeline` component (existing)
- `BoxScore` component

**Team Page:**
- `TeamHeader` component
- `TeamTabs` component
- `TeamRoster` component
- `TeamStats` component

### Data Fetching

- Server components for initial load
- Client components for interactivity
- Supabase for data source
- Caching for performance

---

## Related Documentation

- [DASHBOARD_ROADMAP.md](../../../DASHBOARD_ROADMAP.md) - Dashboard development plan
- [inspiration/README.md](../../inspiration/README.md) - Inspiration materials
- [inspiration/screenshots/](../../inspiration/screenshots/) - Source screenshots

---

*Last Updated: 2026-01-15*
