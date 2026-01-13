# Dashboard Quick Start

Get your dashboard running in 2 minutes!

## Setup

```bash
# 1. Navigate to dashboard
cd ui/dashboard

# 2. Install dependencies (first time only)
npm install

# 3. Set up environment variables
cp .env.example .env.local
# Edit .env.local with your Supabase credentials:
# NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
# NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key

# 4. Start dev server
npm run dev
```

Visit **http://localhost:3000**

## Create Your First Prototype

### Option 1: Use the Script

```bash
# From project root
./scripts/create-dashboard-page.sh my-first-prototype
```

### Option 2: Manual

1. Create: `src/app/(dashboard)/prototypes/my-prototype/page.tsx`
2. Copy from: `src/app/(dashboard)/prototypes/example/page.tsx`
3. Modify as needed
4. Add to sidebar: `src/components/layout/sidebar.tsx`

## Example: Simple Stats Page

```tsx
// src/app/(dashboard)/prototypes/my-prototype/page.tsx
import { PrototypeTemplate, StatCard } from '@/components/prototypes/prototype-template'
import { createClient } from '@/lib/supabase/server'
import { Trophy } from 'lucide-react'

export default async function MyPrototype() {
  const supabase = await createClient()
  const { data } = await supabase
    .from('v_standings_current')
    .select('*')
    .limit(1)
    .single()

  return (
    <PrototypeTemplate title="My Prototype">
      <div className="grid grid-cols-4 gap-4">
        <StatCard label="Teams" value={data?.total_teams || 0} icon={Trophy} />
      </div>
    </PrototypeTemplate>
  )
}
```

## Available Data Views

- `v_standings_current` - Current standings
- `v_leaderboard_points` - Points leaders
- `v_leaderboard_goals` - Goals leaders
- `v_player_season_stats` - Player stats
- `v_team_season_stats` - Team stats
- `v_game_summary` - Game summaries
- `v_summary_league` - League stats

## Next Steps

- See [PROTOTYPING.md](./PROTOTYPING.md) for detailed guide
- Check [example prototype](./src/app/(dashboard)/prototypes/example/page.tsx)
- Review existing pages for patterns
