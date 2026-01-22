# 10 - Dashboard: Next.js Overview

**Learning Objectives:**
- Understand Next.js App Router basics
- Know how the dashboard fetches data
- Navigate the dashboard codebase

---

## What is Next.js?

**Next.js** is a React framework that provides:
- Server-side rendering (pages load with data)
- File-based routing (folder structure = URL structure)
- API routes (backend in the same project)
- TypeScript support (type-safe code)

---

## Dashboard Structure

```
ui/dashboard/
├── src/
│   ├── app/                    # Pages (App Router)
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Home page (/)
│   │   ├── norad/              # NORAD league pages
│   │   │   ├── dashboard/      # /norad/dashboard
│   │   │   ├── players/        # /norad/players
│   │   │   │   ├── page.tsx    # /norad/players (list)
│   │   │   │   └── [playerId]/ # /norad/players/P001 (detail)
│   │   │   ├── teams/          # /norad/teams
│   │   │   ├── games/          # /norad/games
│   │   │   └── leaders/        # /norad/leaders
│   │   └── api/                # API routes
│   ├── components/             # React components
│   │   ├── charts/             # Chart visualizations
│   │   ├── players/            # Player-related UI
│   │   ├── teams/              # Team-related UI
│   │   ├── common/             # Shared components
│   │   └── ui/                 # Base UI primitives
│   ├── lib/                    # Utilities
│   │   ├── supabase/           # Database client
│   │   │   ├── client.ts       # Supabase setup
│   │   │   └── queries/        # Query functions
│   │   └── utils/              # Helper functions
│   └── types/                  # TypeScript interfaces
├── package.json                # Dependencies
└── .env.local                  # Environment variables
```

---

## Key Concepts for Python Developers

### Server Components vs Client Components

**Server Components** (default):
- Render on the server
- Can directly query database
- Can't use useState, onClick, etc.
- Faster initial load

**Client Components** (marked with `'use client'`):
- Render in the browser
- Can use React hooks (useState, useEffect)
- Can handle user interactions
- Needed for interactivity

```typescript
// Server Component (default) - can query DB directly
export default async function PlayersPage() {
  const players = await getPlayers();  // Runs on server
  return <PlayerList players={players} />;
}

// Client Component - for interactivity
'use client';
export default function PlayerFilter() {
  const [search, setSearch] = useState('');
  return <input value={search} onChange={(e) => setSearch(e.target.value)} />;
}
```

### File-Based Routing

| File Path | URL |
|-----------|-----|
| `app/page.tsx` | `/` |
| `app/norad/players/page.tsx` | `/norad/players` |
| `app/norad/players/[playerId]/page.tsx` | `/norad/players/P001` |
| `app/norad/games/[gameId]/page.tsx` | `/norad/games/19001` |

**Dynamic routes** use brackets: `[playerId]` becomes a parameter.

```typescript
// app/norad/players/[playerId]/page.tsx
export default async function PlayerPage({
  params,
}: {
  params: { playerId: string }
}) {
  const player = await getPlayer(params.playerId);
  return <PlayerProfile player={player} />;
}
```

---

## Data Fetching

### Supabase Client Setup

📍 **File:** `src/lib/supabase/client.ts`

```typescript
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const supabase = createClient(supabaseUrl, supabaseKey);
```

### Query Functions

📍 **File:** `src/lib/supabase/queries/players.ts`

```typescript
import { supabase } from '../client';
import type { Player, PlayerGameStats } from '@/types';

export async function getPlayers(): Promise<Player[]> {
  const { data, error } = await supabase
    .from('dim_player')
    .select('*')
    .order('player_name');

  if (error) throw error;
  return data;
}

export async function getPlayerStats(playerId: string): Promise<PlayerGameStats[]> {
  const { data, error } = await supabase
    .from('fact_player_game_stats')
    .select('*')
    .eq('player_id', playerId)
    .order('game_id', { ascending: false });

  if (error) throw error;
  return data;
}

export async function getPlayerSeasonStats(playerId: string) {
  const { data, error } = await supabase
    .from('fact_player_season_stats')
    .select('*')
    .eq('player_id', playerId);

  if (error) throw error;
  return data;
}
```

### Using Queries in Pages

```typescript
// app/norad/players/[playerId]/page.tsx
import { getPlayer, getPlayerStats } from '@/lib/supabase/queries/players';

export default async function PlayerPage({
  params,
}: {
  params: { playerId: string }
}) {
  // These run on the server
  const player = await getPlayer(params.playerId);
  const stats = await getPlayerStats(params.playerId);

  return (
    <div>
      <h1>{player.player_name}</h1>
      <StatsTable stats={stats} />
    </div>
  );
}
```

---

## Component Patterns

### Page Component (Server)

```typescript
// app/norad/players/page.tsx
import { getPlayers } from '@/lib/supabase/queries/players';
import { PlayerList } from '@/components/players/PlayerList';

export default async function PlayersPage() {
  const players = await getPlayers();

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-2xl font-bold mb-4">Players</h1>
      <PlayerList players={players} />
    </div>
  );
}
```

### List Component (Client - for filtering)

```typescript
// components/players/PlayerList.tsx
'use client';

import { useState } from 'react';
import type { Player } from '@/types';

interface Props {
  players: Player[];
}

export function PlayerList({ players }: Props) {
  const [search, setSearch] = useState('');

  const filtered = players.filter(p =>
    p.player_name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <input
        type="text"
        placeholder="Search players..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="border p-2 rounded mb-4"
      />
      <ul>
        {filtered.map(player => (
          <li key={player.player_id}>
            <a href={`/norad/players/${player.player_id}`}>
              {player.player_name}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### Chart Component

```typescript
// components/charts/StatsChart.tsx
'use client';

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface Props {
  data: { game_id: number; points: number }[];
}

export function StatsChart({ data }: Props) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <XAxis dataKey="game_id" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="points" stroke="#8884d8" />
      </LineChart>
    </ResponsiveContainer>
  );
}
```

---

## TypeScript Types

📍 **File:** `src/types/player.ts`

```typescript
export interface Player {
  player_id: string;
  player_name: string;
  team_id: string;
  position: string;
  jersey_number: number;
  skill_rating: number;
}

export interface PlayerGameStats {
  player_game_key: string;
  player_id: string;
  game_id: number;
  team_id: string;
  goals: number;
  assists: number;
  points: number;
  shots: number;
  sog: number;
  toi_seconds: number;
  cf_pct: number;
  xg_for: number;
  war: number;
  game_score: number;
}

export interface PlayerSeasonStats {
  player_id: string;
  season_id: string;
  games_played: number;
  goals: number;
  assists: number;
  points: number;
  // ... more fields
}
```

---

## Styling with Tailwind CSS

The dashboard uses Tailwind CSS for styling:

```typescript
// Tailwind classes are utility-first
<div className="container mx-auto py-8">
  <h1 className="text-2xl font-bold mb-4">Players</h1>
  <div className="grid grid-cols-3 gap-4">
    <div className="bg-white rounded-lg shadow p-4">
      Card content
    </div>
  </div>
</div>
```

Common patterns:
- `container mx-auto` - Centered container
- `py-8`, `px-4` - Padding (y-axis, x-axis)
- `text-2xl font-bold` - Text sizing
- `grid grid-cols-3 gap-4` - Grid layout
- `bg-white rounded-lg shadow` - Card styling

---

## Key Files to Know

| File | Purpose |
|------|---------|
| `src/app/layout.tsx` | Root layout (header, footer) |
| `src/app/norad/layout.tsx` | NORAD section layout |
| `src/lib/supabase/client.ts` | Database connection |
| `src/lib/supabase/queries/*.ts` | Query functions |
| `src/components/ui/*.tsx` | Base UI components |
| `src/types/*.ts` | TypeScript interfaces |

---

## Running the Dashboard

```bash
# From ui/dashboard/
npm install          # Install dependencies
npm run dev          # Start dev server (port 3000)
npm run build        # Production build
npm run lint         # Check for errors
npm run type-check   # TypeScript check
```

Or using the CLI:
```bash
./benchsight.sh dashboard dev
./benchsight.sh dashboard build
```

---

## Adding a New Page

1. Create folder: `src/app/norad/new-page/`
2. Create page: `src/app/norad/new-page/page.tsx`
3. Add query: `src/lib/supabase/queries/new-data.ts`
4. Add types: `src/types/new-data.ts`
5. Add components: `src/components/new-feature/`

Example:
```typescript
// src/app/norad/new-page/page.tsx
import { getNewData } from '@/lib/supabase/queries/new-data';

export default async function NewPage() {
  const data = await getNewData();
  return <div>{/* Render data */}</div>;
}
```

---

## Key Takeaways

1. **Next.js App Router** = file-based routing
2. **Server Components** fetch data, **Client Components** handle interactivity
3. **Supabase client** connects to PostgreSQL database
4. **Query functions** in `lib/supabase/queries/`
5. **TypeScript types** ensure type safety
6. **Tailwind CSS** for styling

---

**Next:** [11-api.md](11-api.md) - FastAPI backend overview
