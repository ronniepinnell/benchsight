# Role: Frontend Developer

**Version:** 16.08  
**Updated:** January 8, 2026


## Scope
Build React components, UI interfaces, and user-facing features.

## First Steps
1. Read `LLM_REQUIREMENTS.md` for project context
2. Check `supabase/schema.sql` for available data
3. Review `config/TABLE_METADATA.json` for column meanings
4. Look at `docs/html/` for existing UI patterns

## Tech Stack
- **Framework**: React + TypeScript
- **Styling**: Tailwind CSS
- **State**: React Query for server state
- **Backend**: Supabase client library
- **Charts**: Recharts or D3

## Supabase Connection

```typescript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  'https://uuaowslhpgyiudmbvqze.supabase.co',
  'your-anon-key'
)

// Query example
const { data: players } = await supabase
  .from('dim_player')
  .select('player_id, player_name')
  .order('player_name')
```

## Key Tables for UI

| Table | Use Case |
|-------|----------|
| `dim_player` | Player dropdowns, profiles |
| `dim_team` | Team selectors |
| `dim_schedule` | Game selection |
| `fact_events` | Event display, stats |
| `fact_gameroster` | Game-specific rosters |
| `v_player_game_summary` | Player stats (view) |
| `v_goals` | Goal display (view) |

## Component Patterns

### Player Selector
```tsx
function PlayerSelect({ gameId, onSelect }) {
  const { data: roster } = useQuery(['roster', gameId], () =>
    supabase
      .from('fact_gameroster')
      .select('player_id, player_name, jersey_number')
      .eq('game_id', gameId)
  )
  
  return (
    <select onChange={(e) => onSelect(e.target.value)}>
      {roster?.map(p => (
        <option key={p.player_id} value={p.player_id}>
          #{p.jersey_number} {p.player_name}
        </option>
      ))}
    </select>
  )
}
```

### Event Type Dropdown
```tsx
// Get valid event types from dimension table
const { data: eventTypes } = useQuery('eventTypes', () =>
  supabase.from('dim_event_type').select('*')
)
```

## Data Display Rules

### Goals
Always filter: `event_type='Goal' AND event_detail='Goal_Scored'`

### Player Stats
- Goals: `player_role='event_player_1'` in `fact_event_players`
- Assists: `player_role IN ('event_player_2', 'event_player_3')`

### Time Display
- Convert elapsed_time (seconds) to MM:SS for display
- Game clock counts DOWN, elapsed counts UP

## UI Guidelines
- Show player jersey number with name
- Color-code teams consistently
- Use period + time format: "P2 15:30"
- Highlight goals differently from shots

## Real-time Updates

```typescript
// Subscribe to new events
supabase
  .channel('events')
  .on('postgres_changes', {
    event: 'INSERT',
    schema: 'public',
    table: 'fact_events'
  }, (payload) => {
    // Handle new event
  })
  .subscribe()
```

## Testing
- Test with game 18969 (7 goals)
- Verify player names display correctly
- Check responsive design
- Test error states (no data, loading)
