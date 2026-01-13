# How to View Dashboard Pages

## Quick Start

### 1. Set Up Environment Variables

First, you need your Supabase credentials:

```bash
cd ui/dashboard

# Create .env.local file
cat > .env.local << EOF
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
EOF
```

**Where to find your Supabase credentials:**
1. Go to https://supabase.com
2. Open your project
3. Go to Settings → API
4. Copy:
   - **Project URL** → `NEXT_PUBLIC_SUPABASE_URL`
   - **anon/public key** → `NEXT_PUBLIC_SUPABASE_ANON_KEY`

### 2. Install Dependencies (First Time Only)

```bash
cd ui/dashboard
npm install
```

### 3. Start the Development Server

```bash
npm run dev
```

You should see:
```
▲ Next.js 14.1.0
- Local:        http://localhost:3000
- Ready in 2.3s
```

### 4. View Pages in Browser

Open your browser and go to:

- **Home/Standings**: http://localhost:3000
- **Example Prototype**: http://localhost:3000/prototypes/example
- **Standings**: http://localhost:3000/standings
- **Leaders**: http://localhost:3000/leaders
- **Players**: http://localhost:3000/players
- **Teams**: http://localhost:3000/teams
- **Games**: http://localhost:3000/games

## Reading Data from Supabase

Yes! The dashboard reads data **directly from Supabase**. Here's how:

### Example: Reading Standings

```tsx
// In any page component
import { createClient } from '@/lib/supabase/server'

export default async function MyPage() {
  const supabase = await createClient()
  
  // Read from a view
  const { data: standings, error } = await supabase
    .from('v_standings_current')
    .select('*')
    .order('standing', { ascending: true })
  
  if (error) {
    console.error('Error:', error)
    return <div>Error loading data</div>
  }
  
  return (
    <div>
      {standings?.map(team => (
        <div key={team.team_id}>{team.team_name}</div>
      ))}
    </div>
  )
}
```

### Available Data Views

The dashboard uses these Supabase views (pre-aggregated for performance):

| View | Description |
|------|-------------|
| `v_standings_current` | Current season standings |
| `v_leaderboard_points` | Points leaders |
| `v_leaderboard_goals` | Goals leaders |
| `v_leaderboard_assists` | Assists leaders |
| `v_player_season_stats` | Player season aggregates |
| `v_team_season_stats` | Team season aggregates |
| `v_game_summary` | Game summaries |
| `v_summary_league` | League-wide statistics |

### Query Examples

**Get top 10 players by points:**
```tsx
const { data } = await supabase
  .from('v_leaderboard_points')
  .select('*')
  .order('points', { ascending: false })
  .limit(10)
```

**Get team stats:**
```tsx
const { data } = await supabase
  .from('v_team_season_stats')
  .select('*')
  .eq('team_id', teamId)
  .single()
```

**Get recent games:**
```tsx
const { data } = await supabase
  .from('v_game_summary')
  .select('*')
  .order('game_date', { ascending: false })
  .limit(10)
```

## Troubleshooting

### "Missing environment variables"

Make sure `.env.local` exists in `ui/dashboard/` with:
```
NEXT_PUBLIC_SUPABASE_URL=...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
```

### "Cannot connect to Supabase"

1. Check your Supabase URL is correct
2. Verify your anon key is correct
3. Check Supabase project is active
4. Verify network connection

### "Table/view does not exist"

Make sure you've:
1. Run the ETL: `python run_etl.py`
2. Uploaded to Supabase: `python upload.py`
3. Created the views in Supabase SQL Editor

### Port 3000 already in use

```bash
# Use a different port
PORT=3001 npm run dev
# Then visit http://localhost:3001
```

## Hot Reload

The dev server automatically reloads when you:
- Save any `.tsx`, `.ts`, or `.css` file
- Changes appear instantly in the browser

No need to restart the server!
