# Dashboard Live Data Access

## ✅ Yes! Dashboard Developers Can See and Use Live Data

The dashboard is **fully configured** to read data directly from your Supabase database in real-time.

## How It Works

### 1. **Direct Supabase Connection**

The dashboard uses the Supabase JavaScript client to connect directly to your database:

```typescript
// Server-side (pages)
import { createClient } from '@/lib/supabase/server'

export default async function MyPage() {
  const supabase = await createClient()
  
  // Read live data from Supabase
  const { data } = await supabase
    .from('v_standings_current')
    .select('*')
  
  return <div>{/* Use data */}</div>
}
```

```typescript
// Client-side (components)
import { createClient } from '@/lib/supabase/client'

const supabase = createClient()
const { data } = await supabase.from('dim_team').select('*')
```

### 2. **Environment Variables**

The dashboard needs two environment variables (stored in `ui/dashboard/.env.local`):

```bash
NEXT_PUBLIC_SUPABASE_URL=https://uuaowslhpgyiudmbvqze.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
```

**Note:** The dashboard uses the **anon key** (public key), not the service key. This is safe for client-side use and respects Row Level Security (RLS) policies.

### 3. **Available Data**

Dashboard developers can access all your Supabase tables and views:

#### Dimension Tables
- `dim_team` - 17 teams
- `dim_player` - 337 players  
- `dim_schedule` - 572 games
- `dim_season` - 9 seasons
- `dim_league` - 2 leagues
- `dim_play_detail` - 111 play types
- `dim_player_role` - 14 roles
- `dim_venue` - 2 venues

#### Fact Tables
- `fact_events` - 5,823 events
- `fact_shifts` - 399 shifts
- `fact_player_game_stats` - 99 player-game records

#### Views (Pre-aggregated)
- `v_standings_current` - Current standings
- `v_leaderboard_points` - Player points
- `v_leaderboard_goals` - Player goals
- `v_leaderboard_assists` - Player assists
- `v_recent_games` - Recent games

### 4. **Pre-built Query Functions**

The dashboard includes ready-to-use query functions in `src/lib/supabase/queries/`:

- `teams.ts` - Team queries
- `players.ts` - Player queries
- `games.ts` - Game queries
- `league.ts` - League queries
- `goalies.ts` - Goalie queries

Example:
```typescript
import { getStandings, getTeams } from '@/lib/supabase/queries/teams'

const standings = await getStandings()  // Live data!
const teams = await getTeams()          // Live data!
```

## Setup for Dashboard Developers

### Quick Setup (One-Time)

1. **Run the setup script:**
   ```bash
   python3 scripts/setup_dashboard_env.py
   ```
   This will create `ui/dashboard/.env.local` with your Supabase URL.

2. **Add your anon key:**
   - Go to: https://supabase.com/dashboard
   - Select your project
   - Settings → API
   - Copy the "anon" or "public" key
   - Paste it into `ui/dashboard/.env.local`

3. **Start the dashboard:**
   ```bash
   cd ui/dashboard
   npm install  # First time only
   npm run dev
   ```

4. **Open in browser:**
   - http://localhost:3000
   - Test connection: http://localhost:3000/prototypes/test-connection

### Manual Setup

If you prefer to set it up manually:

```bash
cd ui/dashboard
cp .env.example .env.local
```

Edit `.env.local`:
```bash
NEXT_PUBLIC_SUPABASE_URL=https://uuaowslhpgyiudmbvqze.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-from-supabase-dashboard
```

## Data Flow

```
┌─────────────────┐
│   ETL Pipeline  │
│  (Python)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Supabase DB   │ ◄─── Live Data
│  (PostgreSQL)   │
└────────┬────────┘
         │
         │ (anon key)
         ▼
┌─────────────────┐
│   Dashboard     │
│  (Next.js)      │
│                 │
│  Reads directly │
│  from Supabase  │
└─────────────────┘
```

## Real-Time Updates

When you:
1. Run `python run_etl.py` → Updates CSV files
2. Run `python upload.py` → Uploads to Supabase
3. **Dashboard automatically sees new data** (on next page load/refresh)

The dashboard reads directly from Supabase, so:
- ✅ No need to rebuild/restart the dashboard
- ✅ Data is always current
- ✅ Multiple developers can work simultaneously
- ✅ Production and development use the same data source

## Testing the Connection

The dashboard includes a test page:

1. Start dev server: `npm run dev`
2. Visit: http://localhost:3000/prototypes/test-connection
3. This page shows:
   - ✅ Environment variables status
   - ✅ Connection status
   - ✅ Sample data from Supabase
   - ❌ Error messages if something's wrong

## Security Notes

- **Anon key is safe** for client-side use
- **Service key should NEVER** be used in the dashboard (only in Python scripts)
- Row Level Security (RLS) policies control access
- The anon key has read-only access to public tables/views

## Troubleshooting

**"Missing environment variables"**
→ Create `.env.local` in `ui/dashboard/` with Supabase credentials

**"Cannot connect to Supabase"**
→ Check URL and anon key are correct in `.env.local`

**"Table does not exist"**
→ Run ETL and upload: `python run_etl.py && python upload.py`

**"RLS policy violation"**
→ Check Supabase RLS settings or disable RLS for development

## Summary

✅ **Yes, dashboard developers can see and use live data!**

- Dashboard connects directly to Supabase
- No intermediate API layer needed
- Data updates automatically when you upload new data
- All tables and views are accessible
- Pre-built query functions make it easy to use

Just set up `.env.local` once, and you're ready to build with live data!
