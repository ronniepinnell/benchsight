# Unified Site Integration Guide

## Overview

This guide explains how the **Tracker**, **Portal**, and **Dashboard** are integrated into a single unified site using Next.js 14.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    BENCHSIGHT UNIFIED SITE                   │
│                    (Next.js 14 Dashboard)                    │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Dashboard   │  │   Tracker    │  │    Portal    │      │
│  │   Pages      │  │   (React)    │  │  (Embedded)  │      │
│  │              │  │              │  │              │      │
│  │ /standings   │  │ /tracker     │  │ /admin       │      │
│  │ /leaders     │  │ /tracker/[id]│  │              │      │
│  │ /players     │  │              │  │              │      │
│  │ /teams       │  │              │  │              │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼─────────────────┼─────────────────┼──────────────┘
          │                 │                 │
          └─────────────────┴─────────────────┘
                            │
                            ▼
          ┌─────────────────────────────────┐
          │         Supabase Database        │
          │  (Shared data source for all)   │
          └─────────────────────────────────┘
                            │
          ┌─────────────────┴─────────────────┐
          │                                   │
          ▼                                   ▼
  ┌──────────────┐                  ┌──────────────┐
  │  ETL API     │                  │   Tracker    │
  │  (Backend)   │                  │   Data Sync  │
  │              │                  │              │
  │ localhost:   │                  │  Real-time   │
  │   8000       │                  │  Updates     │
  └──────────────┘                  └──────────────┘
```

## Components

### 1. Dashboard (Next.js Pages)

**Location:** `ui/dashboard/src/app/(dashboard)/`

**Routes:**
- `/standings` - League standings
- `/leaders` - Player/goalie leaderboards
- `/players` - Player search and profiles
- `/teams` - Team pages
- `/games` - Game listings and details
- `/analytics/*` - Advanced analytics pages

**Technology:**
- Next.js 14 App Router
- React Server Components
- TypeScript
- Tailwind CSS
- Supabase client

### 2. Tracker (React Components)

**Location:** `ui/dashboard/src/app/(dashboard)/tracker/`

**Routes:**
- `/tracker` - Game selection page
- `/tracker/[gameId]` - Active tracking session

**Components:**
- `TrackerLayout` - Main layout wrapper
- `TrackerHeader` - Game info, clock, score
- `Rink` - Interactive hockey rink for XY positioning
- `EventForm` - Event entry form
- `EventList` - List of tracked events
- `ShiftPanel` - Shift management

**Technology:**
- React (client components)
- Zustand for state management
- Supabase for data persistence
- SVG for rink visualization

**Integration:**
The tracker is fully integrated as React components within the Next.js app, sharing:
- Same navigation sidebar
- Same authentication (if added)
- Same Supabase connection
- Same styling system

### 3. Admin Portal (Embedded HTML)

**Location:** `ui/dashboard/src/app/(dashboard)/admin/`

**Route:**
- `/admin` - Admin portal page

**Implementation:**
The portal is embedded as an iframe pointing to `/portal/index.html` in the public folder.

**Files:**
- `public/portal/index.html` - Main portal HTML
- `public/portal/js/config.js` - API configuration
- `public/portal/js/api.js` - API client
- `public/portal/js/etl.js` - ETL controls

**Technology:**
- Standalone HTML/JavaScript
- Supabase JS SDK
- Fetch API for ETL API calls

**Integration:**
- Embedded via iframe in Next.js page
- Shares Supabase connection (via environment variables)
- Connects to ETL API backend (separate service)

## Navigation

All three components are accessible through the unified sidebar navigation:

```typescript
// src/components/layout/sidebar.tsx
{
  name: 'Tools',
  icon: '🛠️',
  items: [
    { name: 'Game Tracker', href: '/tracker', icon: <Timer /> },
    { name: 'Admin Portal', href: '/admin', icon: <Database /> },
  ],
}
```

## Environment Variables

All components share the same environment variables:

```bash
# .env.local
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=http://localhost:8000  # For portal
```

## Data Flow

### Dashboard → Supabase
```
Dashboard Page → Supabase Client → Supabase Views → PostgreSQL
```

### Tracker → Supabase
```
Tracker Component → Zustand Store → Supabase Client → fact_events, fact_shifts
```

### Portal → ETL API → Supabase
```
Portal → ETL API (FastAPI) → ETL Process → CSV Output → Supabase Upload
```

## Deployment

### Single Deployment (Recommended)

Deploy everything as one Next.js app to Vercel:

```bash
cd ui/dashboard
vercel
```

**Benefits:**
- Single domain (e.g., `benchsight.vercel.app`)
- Shared authentication
- Shared environment variables
- Unified navigation
- Easier maintenance

### Separate Deployments (Alternative)

If needed, components can be deployed separately:

1. **Dashboard:** Vercel (Next.js)
2. **Tracker:** Vercel (static export) or same as dashboard
3. **Portal:** Vercel (static) or same as dashboard
4. **ETL API:** Railway/Render (FastAPI)

## Development Workflow

### Running Locally

```bash
# Terminal 1: Dashboard (includes tracker)
cd ui/dashboard
npm run dev
# → http://localhost:3000

# Terminal 2: ETL API (for portal)
cd api
uvicorn main:app --reload --port 8000
# → http://localhost:8000
```

### Access Points

- **Dashboard:** http://localhost:3000/standings
- **Tracker:** http://localhost:3000/tracker
- **Admin Portal:** http://localhost:3000/admin

## File Structure

```
ui/dashboard/
├── src/
│   ├── app/
│   │   ├── (dashboard)/
│   │   │   ├── tracker/          # Tracker routes
│   │   │   │   ├── page.tsx      # Game selection
│   │   │   │   └── [gameId]/
│   │   │   │       └── page.tsx  # Active tracker
│   │   │   ├── admin/
│   │   │   │   └── page.tsx      # Portal wrapper
│   │   │   ├── standings/
│   │   │   ├── leaders/
│   │   │   └── ...
│   │   └── layout.tsx
│   ├── components/
│   │   ├── tracker/              # Tracker React components
│   │   └── layout/
│   │       └── sidebar.tsx       # Unified navigation
│   └── lib/
│       └── tracker/              # Tracker utilities
├── public/
│   └── portal/                   # Portal static files
│       ├── index.html
│       └── js/
└── package.json
```

## Migration Path

### Current State
- ✅ Dashboard: Fully integrated in Next.js
- ✅ Tracker: React components in Next.js (partially complete)
- ⚠️ Portal: Standalone HTML (needs embedding)

### Future Enhancements

1. **Convert Portal to React** (Optional)
   - Replace iframe with React components
   - Better integration with dashboard
   - Shared state management

2. **Add Authentication**
   - Protect `/admin` route
   - User roles (admin, viewer, etc.)
   - Supabase Auth integration

3. **Unified State Management**
   - Shared Zustand stores
   - Real-time updates across components
   - Cache management

## Troubleshooting

### Portal Not Loading

1. Check that `public/portal/index.html` exists
2. Verify API URL in portal config matches ETL API
3. Check browser console for CORS errors
4. Ensure ETL API is running

### Tracker Not Saving

1. Verify Supabase connection
2. Check environment variables
3. Review browser console for errors
4. Check Supabase RLS policies

### Navigation Issues

1. Verify all routes are in `(dashboard)` route group
2. Check sidebar navigation items match routes
3. Ensure layout is wrapping all pages

## Benefits of Unified Site

1. **Single Domain:** Everything accessible from one URL
2. **Shared Navigation:** Easy movement between features
3. **Consistent UI:** Same design system throughout
4. **Shared Auth:** One login for all features
5. **Easier Deployment:** One deployment instead of three
6. **Better UX:** Seamless transitions between components
7. **Simplified Maintenance:** One codebase to manage

## Next Steps

1. ✅ Add portal route to dashboard
2. ✅ Update sidebar navigation
3. ⏳ Test all integrations
4. ⏳ Add authentication (optional)
5. ⏳ Convert portal to React (optional)
6. ⏳ Deploy to production
