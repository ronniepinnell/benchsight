# Dashboard Prototyping Guide

Quick guide for prototyping new dashboard pages and visualizations.

## Quick Start

### 1. Start the Dev Server

```bash
cd ui/dashboard
npm install  # First time only
npm run dev
```

Visit http://localhost:3000

### 2. Create a New Prototype Page

**Option A: Use the template script**
```bash
# From project root
./scripts/create-dashboard-page.sh analytics/my-prototype
```

**Option B: Manual creation**

Create a new file: `src/app/(dashboard)/prototypes/[your-name]/page.tsx`

```tsx
// src/app/(dashboard)/prototypes/[your-name]/page.tsx
export default function YourPrototypePage() {
  return (
    <div className="space-y-6">
      <h1 className="font-display text-2xl font-bold">Your Prototype</h1>
      {/* Your prototype content */}
    </div>
  )
}
```

Then add it to the sidebar navigation in `src/components/layout/sidebar.tsx`:

```tsx
{
  name: 'Prototypes',
  icon: '🧪',
  items: [
    { name: 'Your Prototype', href: '/prototypes/your-name', icon: <TestTube className="w-4 h-4" /> },
  ],
}
```

## Available Data Sources

### Supabase Views (Recommended)

The dashboard uses pre-aggregated views for performance:

- `v_standings_current` - Current season standings
- `v_leaderboard_points` - Points leaders
- `v_leaderboard_goals` - Goals leaders
- `v_leaderboard_assists` - Assists leaders
- `v_player_season_stats` - Player season aggregates
- `v_team_season_stats` - Team season aggregates
- `v_game_summary` - Game summaries
- `v_summary_league` - League-wide statistics

### Query Examples

```tsx
// In your page component
import { createClient } from '@/lib/supabase/server'

export default async function MyPage() {
  const supabase = await createClient()
  
  // Get standings
  const { data: standings } = await supabase
    .from('v_standings_current')
    .select('*')
    .order('standing', { ascending: true })
  
  // Get player stats
  const { data: players } = await supabase
    .from('v_player_season_stats')
    .select('*')
    .order('points', { ascending: false })
    .limit(20)
  
  return (
    <div>
      {/* Your UI */}
    </div>
  )
}
```

## Reusable Components

### Card Component

```tsx
<div className="bg-card rounded-xl border border-border p-6">
  <h2 className="font-display text-lg font-semibold mb-4">Title</h2>
  {/* Content */}
</div>
```

### Stat Card

```tsx
<div className="bg-card rounded-lg p-4 border border-border">
  <div className="flex items-center gap-2 mb-2">
    <Icon className="w-4 h-4 text-primary" />
    <span className="text-xs font-mono text-muted-foreground uppercase">Label</span>
  </div>
  <div className="font-mono text-2xl font-bold text-foreground">{value}</div>
</div>
```

### Table Template

```tsx
<div className="bg-card rounded-xl border border-border overflow-hidden">
  <div className="overflow-x-auto">
    <table className="w-full">
      <thead>
        <tr className="bg-accent border-b-2 border-border">
          <th className="px-4 py-3 text-left font-display text-xs font-semibold text-muted-foreground uppercase">
            Column
          </th>
        </tr>
      </thead>
      <tbody>
        {data.map((item) => (
          <tr key={item.id} className="border-b border-border hover:bg-muted/50">
            <td className="px-4 py-3">{item.value}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
</div>
```

## Chart Components (Recharts)

```tsx
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export function MyChart({ data }) {
  return (
    <div className="bg-card rounded-xl border border-border p-6">
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="value" fill="hsl(var(--primary))" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
```

## Design System

### Colors (Tailwind)

- `text-primary` - Primary accent
- `text-goal` - Goal color (red/orange)
- `text-assist` - Assist color (blue)
- `text-save` - Save color (green)
- `text-shot` - Shot color (yellow)
- `bg-card` - Card background
- `bg-muted` - Muted background
- `border-border` - Border color

### Typography

- `font-display` - Display font (headings)
- `font-mono` - Monospace (numbers, stats)
- `text-xs` - Extra small
- `text-sm` - Small
- `text-2xl` - Large headings

### Spacing

- Use `space-y-6` for vertical spacing between sections
- Use `gap-4` for grid gaps
- Use `p-6` for card padding

## Common Patterns

### Page Header

```tsx
<div>
  <h1 className="font-display text-2xl font-bold tracking-wider uppercase flex items-center gap-3">
    <span className="w-1 h-6 bg-primary rounded" />
    Page Title
  </h1>
  <p className="text-sm text-muted-foreground mt-2 ml-4">Description</p>
</div>
```

### Grid Layout

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
  {/* Cards */}
</div>
```

### Tabs

```tsx
import Link from 'next/link'
import { cn } from '@/lib/utils'

const tabs = [
  { id: 'tab1', label: 'Tab 1', href: '/page?tab=tab1' },
  { id: 'tab2', label: 'Tab 2', href: '/page?tab=tab2' },
]

<div className="flex gap-2 border-b border-border pb-2">
  {tabs.map((tab) => (
    <Link
      key={tab.id}
      href={tab.href}
      className={cn(
        'px-4 py-2 rounded-t-lg',
        isActive ? 'bg-card border border-b-0' : 'hover:bg-muted/50'
      )}
    >
      {tab.label}
    </Link>
  ))}
</div>
```

## Testing Your Prototype

1. **Hot Reload**: Changes auto-reload in browser
2. **Type Checking**: `npm run type-check`
3. **Linting**: `npm run lint`

## Next Steps

1. Create your prototype page
2. Add it to sidebar navigation
3. Fetch data from Supabase
4. Build your visualization
5. Test and iterate!

## Tips

- Start simple - get data displaying first
- Use the existing components as reference
- Check `src/app/(dashboard)/standings/page.tsx` for a complete example
- Use TypeScript types from `src/types/database.ts`
- Server components (async) for data fetching
- Client components ('use client') for interactivity
