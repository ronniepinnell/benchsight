# Prototyping Cheat Sheet

Quick reference for rapid dashboard prototyping.

## 🚀 Quick Start

```bash
# Create new prototype
./scripts/create-dashboard-page.sh analytics/my-idea

# Start dev server
npm run dev

# View at http://localhost:3000/prototypes/analytics/my-idea
```

## 📊 Data Fetching

```tsx
import { createClient } from '@/lib/supabase/server'

export default async function MyPage() {
  const supabase = await createClient()
  
  // Simple query
  const { data } = await supabase
    .from('v_standings_current')
    .select('*')
    .order('standing', { ascending: true })
  
  // With filters
  const { data } = await supabase
    .from('v_player_season_stats')
    .select('*')
    .eq('team_name', 'Team Name')
    .gte('points', 10)
    .limit(20)
  
  return <div>{/* Use data */}</div>
}
```

## 🎨 Components

```tsx
// Page wrapper
<PrototypeTemplate title="Title" description="Description">
  {/* Content */}
</PrototypeTemplate>

// Stat card
<StatCard 
  label="Label" 
  value={42} 
  icon={Trophy}
  color="text-assist"
/>

// Table
<PrototypeTable
  data={data}
  columns={[
    { key: 'name', label: 'Name' },
    { key: 'value', label: 'Value' },
  ]}
/>
```

## 🎨 Colors

```tsx
text-goal      // Goals, losses, negative
text-assist    // Assists, positive
text-save      // Saves, wins
text-shot      // Shots
text-primary   // Primary accent
text-muted     // Secondary text
bg-card        // Card background
border-border  // Borders
```

## 📐 Layout Patterns

```tsx
// Grid of cards
<div className="grid grid-cols-1 md:grid-cols-4 gap-4">
  <StatCard ... />
</div>

// Card container
<div className="bg-card rounded-xl border border-border p-6">
  {/* Content */}
</div>

// Page spacing
<div className="space-y-6">
  {/* Sections */}
</div>
```

## 📈 Charts (Recharts)

```tsx
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer } from 'recharts'

<ResponsiveContainer width="100%" height={300}>
  <BarChart data={data}>
    <XAxis dataKey="name" />
    <YAxis />
    <Bar dataKey="value" fill="hsl(var(--save))" />
  </BarChart>
</ResponsiveContainer>
```

## 🔍 Common Queries

```tsx
// Standings
const { data } = await supabase
  .from('v_standings_current')
  .select('*')

// Player leaders
const { data } = await supabase
  .from('v_leaderboard_points')
  .select('*')
  .limit(20)

// Team stats
const { data } = await supabase
  .from('v_team_season_stats')
  .select('*')
  .eq('team_id', teamId)
```

## 📝 Workflow

1. **Prototype** (15 min) - Get data showing
2. **Design** (30 min) - Make it look good
3. **Iterate** (ongoing) - Refine based on usage

## 🎯 Tips

- Start with mock data to test layout
- Use `console.log()` to inspect data shape
- Copy existing prototypes as starting point
- One prototype = one idea
- Delete failures, promote successes
