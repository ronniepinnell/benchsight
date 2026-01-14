# Quick Start: Unified Site

This guide shows you how to access all three components (Dashboard, Tracker, Portal) in the unified site.

## Prerequisites

1. **Dashboard running:**
   ```bash
   cd ui/dashboard
   npm run dev
   ```
   → http://localhost:3000

2. **ETL API running** (for portal):
   ```bash
   cd api
   uvicorn main:app --reload --port 8000
   ```
   → http://localhost:8000

## Setup Portal Files

Before using the admin portal, copy the portal files:

```bash
cd ui/dashboard
./scripts/setup-portal.sh
```

This copies `ui/portal/*` to `ui/dashboard/public/portal/`

## Access Points

Once everything is running, access all components from the unified dashboard:

### Dashboard Pages
- **Standings:** http://localhost:3000/standings
- **Leaders:** http://localhost:3000/leaders
- **Players:** http://localhost:3000/players
- **Teams:** http://localhost:3000/teams
- **Games:** http://localhost:3000/games

### Tracker
- **Game Selection:** http://localhost:3000/tracker
- **Active Tracker:** http://localhost:3000/tracker/[gameId]

### Admin Portal
- **Portal:** http://localhost:3000/admin

## Navigation

All components are accessible through the sidebar navigation:

1. **Games** section - Game listings
2. **League** section - Standings, leaders, goalies
3. **Teams** section - Team pages
4. **Players** section - Player search and profiles
5. **Analytics** section - Advanced analytics
6. **Tools** section - **Tracker** and **Admin Portal**
7. **Prototypes** section - Development prototypes

## Environment Variables

Create `ui/dashboard/.env.local`:

```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Troubleshooting

### Portal shows blank page
- Run `./scripts/setup-portal.sh` to copy portal files
- Check that `public/portal/index.html` exists
- Verify ETL API is running on port 8000

### Tracker not saving
- Check Supabase connection in browser console
- Verify environment variables are set
- Check Supabase RLS policies allow writes

### Navigation not working
- Ensure you're in the `(dashboard)` route group
- Check that routes match sidebar hrefs
- Verify layout is wrapping all pages

## Architecture

```
┌─────────────────────────────────────┐
│     Next.js Dashboard (Port 3000)   │
│  ┌─────────┐  ┌─────────┐  ┌──────┐│
│  │Dashboard│  │ Tracker │  │Portal││
│  │  Pages  │  │(React)  │  │(HTML)││
│  └────┬────┘  └────┬────┘  └───┬───┘│
└───────┼────────────┼────────────┼────┘
        │            │            │
        └────────────┴────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
  ┌──────────┐            ┌──────────┐
  │ Supabase │            │ ETL API   │
  │ Database │            │ (Port 8k) │
  └──────────┘            └──────────┘
```

All three components share:
- Same navigation sidebar
- Same Supabase connection
- Same domain/URL
- Same authentication (when added)

## Next Steps

1. ✅ Set up portal files
2. ✅ Start dashboard and API
3. ✅ Access all components via sidebar
4. ⏳ Add authentication (optional)
5. ⏳ Deploy to production

See [UNIFIED_SITE_INTEGRATION.md](./UNIFIED_SITE_INTEGRATION.md) for detailed architecture.
