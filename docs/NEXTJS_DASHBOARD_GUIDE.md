# BenchSight Dashboard - Next.js 14 Implementation Guide

## Recommended Stack

| Layer | Technology | Why |
|-------|------------|-----|
| Framework | Next.js 14+ (App Router) | Server components, great caching, Vercel-native |
| Language | TypeScript | Type safety with Supabase, fewer bugs |
| Styling | Tailwind CSS + shadcn/ui | Rapid development, beautiful components |
| Database | Supabase (PostgreSQL) | Already configured, real-time ready |
| Charts | Recharts + Custom SVG | React-native charts + hockey rink |
| Deployment | Vercel | Free tier, auto-deploy from GitHub |
| Data Fetching | Server Components + Supabase | No client-side loading spinners |

---

## Project Setup

### 1. Create Next.js Project

```bash
npx create-next-app@latest benchsight-dashboard --typescript --tailwind --eslint --app --src-dir
cd benchsight-dashboard
```

### 2. Install Dependencies

```bash
# Supabase client
npm install @supabase/supabase-js @supabase/ssr

# UI Components
npx shadcn-ui@latest init
npx shadcn-ui@latest add card table badge tabs select button

# Charts
npm install recharts

# Types
npm install -D @types/node
```

### 3. Environment Variables

Create `.env.local`:
```env
NEXT_PUBLIC_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

---

## Directory Structure

```
src/
├── app/
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Home/Dashboard
│   ├── standings/
│   │   └── page.tsx         # Team standings
│   ├── leaderboards/
│   │   └── page.tsx         # Stat leaders
│   ├── players/
│   │   ├── page.tsx         # Player list
│   │   └── [id]/
│   │       └── page.tsx     # Player profile
│   ├── goalies/
│   │   ├── page.tsx         # Goalie list
│   │   └── [id]/
│   │       └── page.tsx     # Goalie profile
│   ├── teams/
│   │   ├── page.tsx         # Team list
│   │   └── [id]/
│   │       └── page.tsx     # Team profile
│   └── games/
│       └── [id]/
│           └── page.tsx     # Game detail
├── components/
│   ├── ui/                  # shadcn components
│   ├── charts/
│   │   ├── StatsChart.tsx
│   │   └── HockeyRink.tsx   # Custom SVG rink
│   ├── tables/
│   │   ├── StandingsTable.tsx
│   │   ├── LeaderboardTable.tsx
│   │   └── PlayerGameLog.tsx
│   └── cards/
│       ├── StatCard.tsx
│       └── PlayerCard.tsx
├── lib/
│   ├── supabase/
│   │   ├── client.ts        # Browser client
│   │   ├── server.ts        # Server client
│   │   └── types.ts         # Generated types
│   └── utils.ts
└── types/
    └── database.ts          # Supabase types
```

---

## Supabase Client Setup

### Server Client (for Server Components)

```typescript
// src/lib/supabase/server.ts
import { createClient } from '@supabase/supabase-js'
import { Database } from '@/types/database'

export function createServerClient() {
  return createClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}
```

### Browser Client (for Client Components)

```typescript
// src/lib/supabase/client.ts
import { createClient } from '@supabase/supabase-js'
import { Database } from '@/types/database'

export const supabase = createClient<Database>(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)
```

---

## Server Component Data Fetching (No Loading Spinners!)

### Home Page with Standings + Leaderboard

```typescript
// src/app/page.tsx
import { createServerClient } from '@/lib/supabase/server'
import { StandingsTable } from '@/components/tables/StandingsTable'
import { LeaderboardTable } from '@/components/tables/LeaderboardTable'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export const revalidate = 60 // Revalidate every 60 seconds

export default async function HomePage() {
  const supabase = createServerClient()
  
  // Parallel data fetching
  const [standingsRes, leadersRes, recentGamesRes] = await Promise.all([
    supabase.from('v_standings_current').select('*').limit(10),
    supabase.from('v_leaderboard_points').select('*').limit(5),
    supabase.from('v_recent_games').select('*').limit(5)
  ])
  
  return (
    <div className="container mx-auto p-6 space-y-6">
      <h1 className="text-3xl font-bold">NORAD Hockey Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Standings</CardTitle>
          </CardHeader>
          <CardContent>
            <StandingsTable data={standingsRes.data ?? []} />
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Points Leaders</CardTitle>
          </CardHeader>
          <CardContent>
            <LeaderboardTable data={leadersRes.data ?? []} />
          </CardContent>
        </Card>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Recent Games</CardTitle>
        </CardHeader>
        <CardContent>
          <RecentGamesTable data={recentGamesRes.data ?? []} />
        </CardContent>
      </Card>
    </div>
  )
}
```

### Player Profile Page

```typescript
// src/app/players/[id]/page.tsx
import { createServerClient } from '@/lib/supabase/server'
import { notFound } from 'next/navigation'

interface Props {
  params: { id: string }
}

export default async function PlayerPage({ params }: Props) {
  const supabase = createServerClient()
  
  const [careerRes, gamesRes, rankingsRes] = await Promise.all([
    supabase
      .from('v_summary_player_career')
      .select('*')
      .eq('player_id', params.id)
      .single(),
    supabase
      .from('v_detail_player_games')
      .select('*')
      .eq('player_id', params.id)
      .order('date', { ascending: false })
      .limit(20),
    supabase
      .from('v_rankings_players')
      .select('*')
      .eq('player_id', params.id)
  ])
  
  if (!careerRes.data) notFound()
  
  const player = careerRes.data
  
  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center gap-4">
        <h1 className="text-3xl font-bold">{player.player_name}</h1>
        <span className="text-muted-foreground">{player.position}</span>
      </div>
      
      {/* Career Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Games" value={player.career_games} />
        <StatCard label="Goals" value={player.career_goals} />
        <StatCard label="Assists" value={player.career_assists} />
        <StatCard label="Points" value={player.career_points} />
      </div>
      
      {/* Game Log */}
      <PlayerGameLog games={gamesRes.data ?? []} />
    </div>
  )
}
```

---

## Reusable Components

### Stat Card

```typescript
// src/components/cards/StatCard.tsx
import { Card, CardContent } from '@/components/ui/card'

interface StatCardProps {
  label: string
  value: number | string
  subtitle?: string
}

export function StatCard({ label, value, subtitle }: StatCardProps) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="text-2xl font-bold">{value}</div>
        <p className="text-xs text-muted-foreground">{label}</p>
        {subtitle && (
          <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
        )}
      </CardContent>
    </Card>
  )
}
```

### Standings Table

```typescript
// src/components/tables/StandingsTable.tsx
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import Link from 'next/link'

interface Standing {
  team_id: string
  team_name: string
  wins: number
  losses: number
  goal_diff: number
  standing: number
}

export function StandingsTable({ data }: { data: Standing[] }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="w-12">#</TableHead>
          <TableHead>Team</TableHead>
          <TableHead className="text-right">W</TableHead>
          <TableHead className="text-right">L</TableHead>
          <TableHead className="text-right">+/-</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {data.map((team) => (
          <TableRow key={team.team_id}>
            <TableCell className="font-medium">{team.standing}</TableCell>
            <TableCell>
              <Link 
                href={`/teams/${team.team_id}`}
                className="hover:underline"
              >
                {team.team_name}
              </Link>
            </TableCell>
            <TableCell className="text-right">{team.wins}</TableCell>
            <TableCell className="text-right">{team.losses}</TableCell>
            <TableCell className="text-right">
              <span className={team.goal_diff > 0 ? 'text-green-600' : 'text-red-600'}>
                {team.goal_diff > 0 ? '+' : ''}{team.goal_diff}
              </span>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
```

---

## View-to-Route Mapping

| Route | View(s) | Caching |
|-------|---------|---------|
| `/` | v_standings_current, v_leaderboard_points, v_recent_games | 60s |
| `/standings` | v_standings_current, v_standings_team_history | 60s |
| `/leaderboards` | v_leaderboard_* (all) | 60s |
| `/leaderboards/[stat]` | v_leaderboard_points/goals/assists/etc | 60s |
| `/players` | v_rankings_players | 60s |
| `/players/[id]` | v_summary_player_career, v_detail_player_games | 300s |
| `/goalies` | v_rankings_goalies | 60s |
| `/goalies/[id]` | v_summary_goalie_career, v_detail_goalie_games | 300s |
| `/teams` | v_standings_current | 60s |
| `/teams/[id]` | v_compare_teams, v_compare_players | 300s |
| `/games/[id]` | v_summary_game, v_detail_game_roster | 3600s |
| `/compare` | v_compare_players, v_compare_goalies | dynamic |

---

## Recharts Integration

### Points Trend Chart

```typescript
// src/components/charts/PointsTrendChart.tsx
'use client'

import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

interface Game {
  date: string
  points: number
}

export function PointsTrendChart({ games }: { games: Game[] }) {
  // Reverse for chronological order
  const data = [...games].reverse().map((g, i) => ({
    game: i + 1,
    points: g.points,
    date: g.date
  }))
  
  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={data}>
        <XAxis dataKey="game" />
        <YAxis />
        <Tooltip 
          labelFormatter={(value) => `Game ${value}`}
          formatter={(value: number) => [`${value} pts`, 'Points']}
        />
        <Line 
          type="monotone" 
          dataKey="points" 
          stroke="#2563eb" 
          strokeWidth={2}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
```

---

## TypeScript Types (Generate from Supabase)

```bash
# Generate types from your Supabase schema
npx supabase gen types typescript --project-id YOUR_PROJECT_ID > src/types/database.ts
```

Or manually define key types:

```typescript
// src/types/database.ts
export interface Database {
  public: {
    Views: {
      v_standings_current: {
        Row: {
          team_id: string
          team_name: string
          wins: number
          losses: number
          goal_diff: number
          standing: number
        }
      }
      v_leaderboard_points: {
        Row: {
          player_id: string
          player_name: string
          team_name: string
          points: number
          season_rank: number
        }
      }
      // ... add more as needed
    }
  }
}
```

---

## Deployment to Vercel

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial BenchSight dashboard"
git remote add origin https://github.com/yourusername/benchsight-dashboard.git
git push -u origin main
```

### 2. Connect to Vercel

1. Go to vercel.com
2. Import your GitHub repo
3. Add environment variables:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
4. Deploy!

### 3. Auto-Deploy

Every push to `main` will auto-deploy. PRs get preview URLs.

---

## Performance Tips

1. **Use Server Components** - No loading spinners, data fetches on server
2. **Parallel Data Fetching** - Use `Promise.all()` for multiple queries
3. **Revalidate Strategically** - 60s for live data, 300s for profiles, 3600s for historical
4. **Select Only Needed Columns** - `.select('player_name, points')` not `*`
5. **Limit Results** - Always use `.limit()` for lists
6. **Use Views** - Pre-aggregated, always fresh, no extra computation
