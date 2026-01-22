# Dashboard Rules

**Dashboard-specific patterns and rules**

Last Updated: 2026-01-21

---

## Dashboard Architecture

### Framework
- **Next.js 14** - App Router
- **TypeScript** - Strict mode
- **Tailwind CSS** - Styling
- **shadcn/ui** - Component library
- **Recharts** - Data visualization
- **Supabase** - Database and auth

### Key Directories
- `ui/dashboard/src/app/` - Next.js app directory
- `ui/dashboard/src/components/` - React components
- `ui/dashboard/src/lib/` - Utilities and helpers

---

## Component Patterns

### Server Components (Default)

```typescript
// Server Component (default)
export default async function Page({ 
  params 
}: { 
  params: { playerId: string } 
}) {
  const player = await getPlayer(params.playerId)
  return <PlayerProfile player={player} />
}
```

### Client Components (When Needed)

```typescript
'use client'

import { useState } from 'react'

export function InteractiveComponent() {
  const [state, setState] = useState()
  // ... interactivity
  return <div>...</div>
}
```

---

## Data Fetching Patterns

### Server Component Data Fetching

```typescript
// Server Component
export default async function PlayerPage({ 
  params 
}: { 
  params: { playerId: string } 
}) {
  const supabase = createClient()
  const { data, error } = await supabase
    .from('dim_player')
    .select('*')
    .eq('player_id', params.playerId)
    .single()
  
  if (error) {
    // Handle error
  }
  
  return <PlayerProfile player={data} />
}
```

### Supabase Client Usage

```typescript
import { createClient } from '@/lib/supabase/server'

// In Server Components
const supabase = createClient()
const { data } = await supabase.from('table').select('*')
```

---

## Type Safety

### Type Definitions

```typescript
interface Player {
  id: string
  name: string
  team: string
  stats: PlayerStats
}

interface PlayerStats {
  goals: number
  assists: number
  points: number
}
```

### Type Usage

```typescript
export default async function Page({ 
  params 
}: { 
  params: { playerId: string } 
}) {
  const player: Player = await getPlayer(params.playerId)
  return <PlayerProfile player={player} />
}
```

---

## Performance Requirements

### Page Load Time
- **Target:** < 2 seconds
- **Optimization:** Use Server Components
- **Caching:** Leverage Next.js caching

### Data Fetching
- Use Server Components for data fetching
- Minimize client-side data fetching
- Cache when appropriate

---

## UI/UX Guidelines

### Component Structure
- Use shadcn/ui components
- Follow existing component patterns
- Maintain consistent styling

### Error Handling
```typescript
try {
  const data = await fetchData()
  return <Component data={data} />
} catch (error) {
  return <ErrorComponent error={error} />
}
```

---

## Related Rules

- `core.md` - Core rules (naming, code standards)
- `api.md` - API integration patterns
- `data.md` - Data validation rules

---

*Last Updated: 2026-01-15*
