# BenchSight Strategic Plan & Roadmap

**Version:** 1.0  
**Date:** January 8, 2026  
**Status:** Planning Document

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current State Assessment](#current-state-assessment)
3. [Architecture Vision](#architecture-vision)
4. [Phase 1: MVP (Current Tracker)](#phase-1-mvp-current-tracker)
5. [Phase 2: Production Rebuild](#phase-2-production-rebuild)
6. [Phase 3: Portal & Automation](#phase-3-portal--automation)
7. [Phase 4: Commercial Platform](#phase-4-commercial-platform)
8. [Technical Specifications](#technical-specifications)
9. [Testing Strategy](#testing-strategy)
10. [Hosting & Deployment](#hosting--deployment)
11. [API Design](#api-design)
12. [Timeline & Milestones](#timeline--milestones)

---

## Executive Summary

### Goal
Transform BenchSight from a single-user hockey tracking tool into a commercially viable SaaS platform for recreational hockey analytics.

### Strategy
1. **Use current MVP tracker** for immediate needs (backlog games)
2. **Build production system in parallel** using modern architecture
3. **Create unified portal** for tracking, ETL, dashboards
4. **Host publicly** with authentication for paid features

### Key Deliverables
| Phase | Deliverable | Timeline |
|-------|-------------|----------|
| Phase 1 | MVP Tracker (current) | Now |
| Phase 2 | React Tracker + API | 8-12 weeks |
| Phase 3 | Admin Portal + Auto-ETL | 4-6 weeks |
| Phase 4 | Public Dashboard + Auth | 4-6 weeks |

---

## Current State Assessment

### What Exists
| Component | Status | Tech | Notes |
|-----------|--------|------|-------|
| Tracker | 70% complete | Vanilla JS | Single 7K line file |
| ETL Pipeline | 95% complete | Python/SQL | 111+ tables |
| Dashboard | 60% complete | TBD | Needs hosting solution |
| API | 0% | - | Supabase direct access only |
| Portal | 0% | - | All via bash commands |
| Auth | 0% | - | No user management |

### Technical Debt
- Single HTML file (unmaintainable)
- Two conflicting keyboard handlers
- No component architecture
- No automated tests
- Manual ETL execution
- No CI/CD pipeline

### Data Quality
- Goals verified against noradhockey.com ✅
- 326+ tests passing ✅
- 4 games fully tracked ✅

---

## Architecture Vision

### Target Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PUBLIC INTERNET                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    CLOUDFLARE / CDN                          │
│                    (SSL, DDoS, Caching)                      │
└─────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   PUBLIC DASH   │  │    TRACKER      │  │   ADMIN PORTAL  │
│   (React/Next)  │  │   (React/Next)  │  │   (React/Next)  │
│   No Auth       │  │   Auth Required │  │   Admin Auth    │
└─────────────────┘  └─────────────────┘  └─────────────────┘
          │                   │                   │
          └───────────────────┼───────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    API GATEWAY                               │
│              (Supabase Edge Functions / Vercel)             │
│                                                              │
│  /api/v1/games        - Game CRUD                           │
│  /api/v1/events       - Event CRUD                          │
│  /api/v1/shifts       - Shift CRUD                          │
│  /api/v1/etl/trigger  - Run ETL pipeline                    │
│  /api/v1/stats        - Pre-computed stats                  │
│  /api/v1/auth         - Authentication                      │
└─────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│    SUPABASE     │  │   ETL WORKER    │  │   FILE STORAGE  │
│   (PostgreSQL)  │  │   (Scheduled)   │  │   (S3/Supabase) │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### Technology Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| Frontend | Next.js 14 (React) | SSR, API routes, excellent DX |
| UI Components | shadcn/ui + Tailwind | Consistent, accessible |
| State Management | Zustand or Jotai | Simpler than Redux |
| Backend | Supabase | Already in use, scales well |
| Auth | Supabase Auth | Integrated, OAuth support |
| ETL | Python + Supabase Functions | Existing code, easy to port |
| Hosting | Vercel | Free tier, excellent Next.js support |
| CDN | Cloudflare | Free tier, global edge |

---

## Phase 1: MVP (Current Tracker)

### Objective
Use current tracker v17.00 for immediate needs while building production system.

### Tasks
- [x] Fix keyboard shortcuts (1-6, Ctrl+1-6)
- [x] Fix event_detail_2 loading (code prefix filter)
- [x] Add auto-calc buttons (success, pressure)
- [x] Smaller XY markers with click-through
- [x] Alt+1-6 for opponent players (v17.00)
- [x] Shift edit dropdown fix (v17.00)
- [x] Event log toggle (v17.00)
- [ ] Document all workarounds
- [ ] Track backlog of 10+ games

### Deliverables
- `benchsight_tracker_v17.00.html` - Standalone tracker
- `docs/WORKAROUNDS.md` - Known issues and workarounds

### Success Criteria
- Can track a full game in < 2 hours
- All events export to Excel correctly
- ETL processes tracker exports without errors

---

## Phase 2: Production Rebuild

### Objective
Build a proper React application with component architecture.

### Project Structure

```
benchsight-app/
├── apps/
│   ├── tracker/           # Tracking application
│   │   ├── components/
│   │   │   ├── EventPanel/
│   │   │   ├── RinkVisualization/
│   │   │   ├── ShiftManager/
│   │   │   ├── PlayerSlots/
│   │   │   └── ...
│   │   ├── hooks/
│   │   │   ├── useSupabase.ts
│   │   │   ├── useKeyboard.ts
│   │   │   ├── useGameState.ts
│   │   │   └── ...
│   │   ├── stores/
│   │   │   ├── gameStore.ts
│   │   │   ├── eventStore.ts
│   │   │   └── ...
│   │   └── pages/
│   │       ├── index.tsx
│   │       └── game/[id].tsx
│   │
│   ├── dashboard/         # Public analytics dashboard
│   │   ├── components/
│   │   ├── pages/
│   │   └── ...
│   │
│   └── portal/            # Admin portal
│       ├── components/
│       ├── pages/
│       └── ...
│
├── packages/
│   ├── ui/                # Shared components
│   ├── api/               # API client
│   ├── types/             # TypeScript types
│   └── etl/               # ETL functions
│
├── supabase/
│   ├── functions/         # Edge functions
│   ├── migrations/        # Database migrations
│   └── seed/              # Seed data
│
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

### Component Breakdown

#### Tracker Components

| Component | Responsibility | Props/State |
|-----------|----------------|-------------|
| `EventPanel` | Event type selection, details | currentEvent, onEventChange |
| `RinkVisualization` | SVG rink with XY points | coordinates, onClickRink |
| `ShiftManager` | Shift start/end, players | shifts, onShiftChange |
| `PlayerSlots` | Player assignment grid | slots, onSlotChange |
| `EventLog` | List of recorded events | events, onEditEvent |
| `KeyboardListener` | Global keyboard handling | bindings, onKeyPress |
| `ExportDialog` | Export to Excel/CSV | data, format |

#### Shared Types

```typescript
// packages/types/index.ts

interface Game {
  id: string;
  game_id: number;
  home_team: Team;
  away_team: Team;
  date: Date;
  status: 'scheduled' | 'tracking' | 'completed' | 'published';
}

interface Event {
  id: string;
  game_id: string;
  period: number;
  time: string;
  event_type: EventType;
  event_detail_1: string;
  event_detail_2: string;
  team: 'home' | 'away';
  players: EventPlayer[];
  puck_xy: Coordinate[];
  success: 's' | 'u' | null;
  zone: 'o' | 'n' | 'd';
  strength: string;
}

interface Shift {
  id: string;
  game_id: string;
  period: number;
  start_time: string;
  end_time: string;
  players: ShiftPlayer[];
}

interface Coordinate {
  x: number;  // -100 to +100 (center-relative)
  y: number;  // -42.5 to +42.5
  seq: number;
}
```

### Tasks

1. **Setup (Week 1)**
   - [ ] Initialize monorepo with Turborepo
   - [ ] Configure Next.js apps
   - [ ] Set up Supabase connection
   - [ ] Configure TypeScript

2. **Core Components (Weeks 2-4)**
   - [ ] RinkVisualization with D3 or SVG
   - [ ] EventPanel with dropdown cascades
   - [ ] PlayerSlots with drag-drop
   - [ ] ShiftManager with timeline

3. **State Management (Week 5)**
   - [ ] Game state store
   - [ ] Event store with undo/redo
   - [ ] Keyboard bindings store
   - [ ] Auto-save with conflict resolution

4. **Integration (Weeks 6-8)**
   - [ ] Supabase real-time subscriptions
   - [ ] Export functionality
   - [ ] Import from legacy tracker
   - [ ] Video player integration

5. **Testing (Weeks 9-10)**
   - [ ] Unit tests for all components
   - [ ] Integration tests for stores
   - [ ] E2E tests for critical flows

6. **Polish (Weeks 11-12)**
   - [ ] Performance optimization
   - [ ] Accessibility audit
   - [ ] Mobile responsiveness
   - [ ] Documentation

### Estimated Effort

| Task | Hours | Complexity |
|------|-------|------------|
| Setup & scaffolding | 8-12 | Low |
| Rink visualization | 16-24 | High |
| Event panel | 12-16 | Medium |
| Player management | 12-16 | Medium |
| Shift tracking | 8-12 | Medium |
| Keyboard shortcuts | 8-12 | Medium |
| State management | 12-16 | High |
| Supabase integration | 8-12 | Medium |
| Video integration | 24-32 | High |
| Export/Import | 8-12 | Medium |
| Testing | 16-24 | Medium |
| Polish & docs | 12-16 | Low |
| **TOTAL** | **144-204** | - |

---

## Phase 3: Portal & Automation

### Objective
Create admin portal for ETL automation and game management.

### Features

#### Game Management
- Create/edit/delete games
- Import schedules from NORAD
- Track completion status
- Assign trackers

#### ETL Automation
- One-click ETL run
- Scheduled ETL (hourly/daily)
- ETL status dashboard
- Error notifications

#### Data Validation
- Pre-ETL validation checks
- Post-ETL verification
- Comparison with official stats
- Anomaly detection

### Portal Pages

| Page | Description | Auth Level |
|------|-------------|------------|
| `/admin` | Dashboard overview | Admin |
| `/admin/games` | Game management | Admin |
| `/admin/games/[id]` | Game detail + tracker link | Admin |
| `/admin/etl` | ETL control panel | Admin |
| `/admin/etl/runs` | ETL run history | Admin |
| `/admin/users` | User management | Super Admin |
| `/admin/settings` | System settings | Super Admin |

### ETL API Endpoints

```typescript
// Trigger ETL run
POST /api/v1/etl/trigger
{
  "game_ids": [18969, 18977],  // Optional: specific games
  "full_refresh": false        // Optional: rebuild all
}

// Get ETL status
GET /api/v1/etl/status

// Get ETL run history
GET /api/v1/etl/runs?limit=10

// Get validation report
GET /api/v1/etl/validate?game_id=18969
```

### ETL Worker Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Portal UI     │────▶│   API Gateway   │────▶│   ETL Queue     │
│  (trigger ETL)  │     │  (validate req) │     │   (Redis/SQS)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │   ETL Worker    │
                                               │  (Python/Node)  │
                                               └─────────────────┘
                                                        │
                        ┌───────────────────────────────┼───────────────────────────────┐
                        ▼                               ▼                               ▼
               ┌─────────────────┐             ┌─────────────────┐             ┌─────────────────┐
               │  Run SQL Steps  │             │  Update Status  │             │  Send Notifs    │
               │  (execute ETL)  │             │  (log progress) │             │  (email/slack)  │
               └─────────────────┘             └─────────────────┘             └─────────────────┘
```

### Tasks

1. **Portal Setup (Week 1)**
   - [ ] Create portal Next.js app
   - [ ] Set up admin authentication
   - [ ] Create dashboard layout

2. **Game Management (Week 2)**
   - [ ] Game list page
   - [ ] Game create/edit forms
   - [ ] Schedule import

3. **ETL Integration (Weeks 3-4)**
   - [ ] ETL trigger API
   - [ ] Worker process (Python or Node)
   - [ ] Progress tracking
   - [ ] Error handling

4. **Validation (Week 5)**
   - [ ] Pre-run checks
   - [ ] Post-run verification
   - [ ] Comparison reports

5. **Notifications (Week 6)**
   - [ ] Email notifications
   - [ ] Slack integration
   - [ ] In-app alerts

---

## Phase 4: Commercial Platform

### Objective
Transform into a multi-tenant SaaS platform for recreational hockey leagues.

### Business Model

| Tier | Price | Features |
|------|-------|----------|
| Free | $0/mo | Public dashboards, 1 team view |
| Basic | $9.99/mo | Full dashboard, 1 league, basic export |
| Pro | $29.99/mo | Multiple leagues, API access, custom reports |
| Enterprise | Custom | White-label, dedicated support, SLA |

### Multi-Tenancy Architecture

```typescript
// All tables have organization_id for isolation
interface Organization {
  id: string;
  name: string;
  slug: string;  // e.g., "norad" for norad.benchsight.io
  tier: 'free' | 'basic' | 'pro' | 'enterprise';
  settings: OrganizationSettings;
}

// Row-level security in Supabase
CREATE POLICY "Users can only see their org data"
ON events
FOR ALL
USING (organization_id = auth.jwt() ->> 'organization_id');
```

### User Roles

| Role | Tracker | Dashboard | Portal | Billing |
|------|---------|-----------|--------|---------|
| Viewer | ❌ | ✅ Read | ❌ | ❌ |
| Tracker | ✅ | ✅ Read | ❌ | ❌ |
| Admin | ✅ | ✅ Full | ✅ | ❌ |
| Owner | ✅ | ✅ Full | ✅ | ✅ |

### Custom Domain Support

```
norad.benchsight.io     → NORAD league
springville.benchsight.io → Springville league
stats.customdomain.com  → Enterprise white-label
```

### Payment Integration

- Stripe for subscriptions
- Supabase for user management
- Webhook for tier changes

---

## Technical Specifications

### Database Schema Updates

```sql
-- Multi-tenancy support
ALTER TABLE dim_game ADD COLUMN organization_id UUID REFERENCES organizations(id);
ALTER TABLE fact_event ADD COLUMN organization_id UUID REFERENCES organizations(id);
-- ... all tables

-- Indexing for performance
CREATE INDEX idx_events_org_game ON fact_event(organization_id, game_id);
CREATE INDEX idx_events_type ON fact_event(event_type_id);
```

### API Rate Limits

| Tier | Requests/min | Requests/day |
|------|--------------|--------------|
| Free | 60 | 1,000 |
| Basic | 300 | 10,000 |
| Pro | 1,000 | 100,000 |
| Enterprise | Unlimited | Unlimited |

### Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Page load | < 2s | ~3-4s |
| API response | < 200ms | ~500ms |
| ETL run time | < 5 min | ~2 min |
| Dashboard render | < 1s | TBD |

---

## Testing Strategy

### Unit Tests

```typescript
// Example: Event validation tests
describe('EventValidator', () => {
  it('should reject goal without event_player_1', () => {
    const event = { type: 'Goal', players: [] };
    expect(validateEvent(event)).toEqual({
      valid: false,
      errors: ['Goal requires event_player_1']
    });
  });

  it('should auto-derive success for shots on net', () => {
    const event = { type: 'Shot', detail1: 'Shot_OnNet' };
    expect(deriveSuccess(event)).toBe('s');
  });
});
```

### Integration Tests

```typescript
// Example: ETL pipeline test
describe('ETL Pipeline', () => {
  it('should process tracker export correctly', async () => {
    const exportData = loadTestExport('game_18969.xlsx');
    await runETL(exportData);
    
    const goals = await supabase
      .from('fact_event')
      .select('*')
      .eq('game_id', 18969)
      .eq('event_type', 'Goal');
    
    expect(goals.data.length).toBe(4);  // Verified count
  });
});
```

### E2E Tests (Playwright)

```typescript
// Example: Track and export a game
test('track full game flow', async ({ page }) => {
  await page.goto('/tracker');
  await page.click('[data-testid="select-game"]');
  await page.click('[data-testid="game-18969"]');
  
  // Add a shot event
  await page.press('body', 's');  // Shot hotkey
  await page.click('[data-testid="rink"]', { position: { x: 150, y: 40 } });
  await page.click('[data-testid="log-event"]');
  
  // Verify event was added
  await expect(page.locator('[data-testid="event-list"] tr')).toHaveCount(1);
  
  // Export
  await page.click('[data-testid="export"]');
  const download = await page.waitForEvent('download');
  expect(download.suggestedFilename()).toMatch(/game_18969.*\.xlsx/);
});
```

### Test Coverage Targets

| Component | Unit | Integration | E2E |
|-----------|------|-------------|-----|
| Event tracking | 90% | 80% | 5 flows |
| Shift tracking | 90% | 80% | 3 flows |
| Export | 80% | 90% | 2 flows |
| ETL | 70% | 90% | 1 flow |
| Dashboard | 70% | 60% | 5 flows |

---

## Hosting & Deployment

### Recommended Stack

| Service | Provider | Cost | Notes |
|---------|----------|------|-------|
| Frontend | Vercel | Free-$20/mo | Excellent Next.js support |
| Database | Supabase | Free-$25/mo | Already in use |
| CDN | Cloudflare | Free | Global edge |
| Email | Resend | Free-$20/mo | Transactional email |
| ETL Worker | Railway/Render | $5-20/mo | Background jobs |
| File Storage | Supabase Storage | Included | Video uploads |

### Deployment Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm test

  deploy-staging:
    needs: test
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      - uses: vercel/action@v1
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - uses: vercel/action@v1
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
```

### Domain Structure

```
benchsight.io              → Marketing site
app.benchsight.io          → Tracker (auth required)
dashboard.benchsight.io    → Public dashboards
admin.benchsight.io        → Admin portal (admin auth)
api.benchsight.io          → API gateway
```

### Alternative: Wix/Squarespace Hybrid

If you prefer simpler marketing site:
- Wix/Squarespace for benchsight.io (marketing)
- Vercel for app subdomain (tracker/dashboard)
- Use DNS CNAME records to connect

---

## API Design

### REST API Endpoints

```
# Games
GET    /api/v1/games                 # List games
GET    /api/v1/games/:id             # Get game
POST   /api/v1/games                 # Create game
PUT    /api/v1/games/:id             # Update game
DELETE /api/v1/games/:id             # Delete game

# Events
GET    /api/v1/games/:id/events      # List events for game
POST   /api/v1/games/:id/events      # Create event
PUT    /api/v1/events/:id            # Update event
DELETE /api/v1/events/:id            # Delete event

# Shifts
GET    /api/v1/games/:id/shifts      # List shifts for game
POST   /api/v1/games/:id/shifts      # Create shift
PUT    /api/v1/shifts/:id            # Update shift
DELETE /api/v1/shifts/:id            # Delete shift

# Stats (pre-computed)
GET    /api/v1/stats/player/:id      # Player stats
GET    /api/v1/stats/team/:id        # Team stats
GET    /api/v1/stats/game/:id        # Game stats
GET    /api/v1/stats/leaderboard     # League leaders

# ETL
POST   /api/v1/etl/trigger           # Trigger ETL run
GET    /api/v1/etl/status            # Current ETL status
GET    /api/v1/etl/runs              # ETL run history

# Auth
POST   /api/v1/auth/login            # Login
POST   /api/v1/auth/logout           # Logout
GET    /api/v1/auth/me               # Current user
```

### GraphQL Alternative

```graphql
type Query {
  game(id: ID!): Game
  games(status: GameStatus): [Game!]!
  player(id: ID!): Player
  stats(gameId: ID, playerId: ID, teamId: ID): Stats
}

type Mutation {
  createEvent(input: EventInput!): Event!
  updateEvent(id: ID!, input: EventInput!): Event!
  deleteEvent(id: ID!): Boolean!
  triggerETL(gameIds: [ID!]): ETLRun!
}

type Subscription {
  eventAdded(gameId: ID!): Event!
  etlProgress(runId: ID!): ETLProgress!
}
```

### Webhook Events

```json
// POST to customer webhook URL
{
  "event": "game.completed",
  "timestamp": "2026-01-08T18:00:00Z",
  "data": {
    "game_id": 18969,
    "home_team": "Ace",
    "away_team": "Outlaws",
    "score": { "home": 4, "away": 3 }
  }
}
```

---

## Timeline & Milestones

### 2026 Q1 (Now - March)

| Week | Focus | Deliverable |
|------|-------|-------------|
| 1-2 | MVP tracker polish | v16.08 release, track backlog |
| 3-4 | React setup | Monorepo scaffolding |
| 5-8 | Core components | Tracker beta |
| 9-10 | Testing | Test suite |
| 11-12 | Video integration | Video sync MVP |

### 2026 Q2 (April - June)

| Week | Focus | Deliverable |
|------|-------|-------------|
| 13-14 | Portal setup | Admin portal scaffolding |
| 15-18 | ETL automation | One-click ETL |
| 19-22 | Dashboard rebuild | Public dashboard v1 |
| 23-24 | Auth & multi-tenant | User management |

### 2026 Q3 (July - September)

| Week | Focus | Deliverable |
|------|-------|-------------|
| 25-28 | Polish & testing | Production readiness |
| 29-32 | Soft launch | Beta users |
| 33-36 | Feedback iteration | Bug fixes, features |

### 2026 Q4 (October - December)

| Week | Focus | Deliverable |
|------|-------|-------------|
| 37-40 | Marketing site | Public launch prep |
| 41-44 | Payment integration | Stripe, subscriptions |
| 45-48 | Public launch | v1.0 release |

---

## Appendix: Document Audit Checklist

### Main Directory
- [ ] README.md - Updated to v16.08
- [ ] LLM_REQUIREMENTS.md - Updated
- [ ] CHANGELOG.md - All versions documented

### docs/ Directory
- [ ] HONEST_ASSESSMENT.md - Current status
- [ ] TODO.md - All known issues
- [ ] STRATEGIC_PLAN.md - This document
- [ ] TRACKER_ETL_SPECIFICATION.md - Export format
- [ ] SUPABASE_SETUP_GUIDE.md - Connection guide

### docs/html/ Directory
- [ ] index.html - Documentation portal
- [ ] All linked pages functional

### Handoff Docs
- [ ] docs/handoff/*.md - Role-specific guides
- [ ] All 14 developer types covered

---

## Next Steps

1. **Immediate:** Package v16.08 with this plan
2. **This week:** Track 2-3 backlog games with MVP
3. **Next week:** Start React scaffold if approved
4. **Ongoing:** Document all decisions and progress

---

*This document is version 1.0. Update as plans evolve.*
