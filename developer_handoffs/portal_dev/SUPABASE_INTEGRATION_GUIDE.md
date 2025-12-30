# Supabase Integration Guide

## Connection Setup

### JavaScript/React
```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  'https://YOUR_PROJECT.supabase.co',
  'YOUR_ANON_KEY'  // Use anon key for client-side
)
```

### Environment Variables
```env
VITE_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIs...
```

---

## Reading Data (SELECT)

### Basic Query
```javascript
// Get all players
const { data, error } = await supabase
  .from('dim_player')
  .select('*')

// Get specific columns
const { data } = await supabase
  .from('dim_player')
  .select('player_id, player_name, position, jersey_number')
```

### Filtering
```javascript
// Single condition
const { data } = await supabase
  .from('fact_player_game_stats')
  .select('*')
  .eq('game_id', 18969)

// Multiple conditions
const { data } = await supabase
  .from('fact_player_game_stats')
  .select('*')
  .eq('game_id', 18969)
  .eq('team_id', 5)
  .gt('goals', 0)

// Operators: eq, neq, gt, gte, lt, lte, like, ilike, in
```

### Joins (Foreign Tables)
```javascript
// Get player stats with player names
const { data } = await supabase
  .from('fact_player_game_stats')
  .select(`
    *,
    dim_player (player_name, position),
    dim_team (team_name, team_abbrev)
  `)
  .eq('game_id', 18969)
```

### Ordering & Pagination
```javascript
const { data } = await supabase
  .from('fact_player_game_stats')
  .select('*')
  .order('points', { ascending: false })
  .limit(10)
  .range(0, 9)  // First 10 rows
```

---

## Writing Data (INSERT/UPDATE/UPSERT)

### Insert Single Row
```javascript
const { data, error } = await supabase
  .from('fact_events')
  .insert({
    event_key: '18969_1',
    game_id: 18969,
    event_index: 1,
    period_number: 1,
    game_time: 45.5,
    event_type: 'Shot',
    event_detail: 'Wrist Shot',
    event_player_1: 123,
    success: 's',
    x_coord: 75.5,
    y_coord: 22.0
  })
```

### Insert Multiple Rows
```javascript
const { data, error } = await supabase
  .from('fact_events')
  .insert([
    { event_key: '18969_1', game_id: 18969, ... },
    { event_key: '18969_2', game_id: 18969, ... },
    { event_key: '18969_3', game_id: 18969, ... }
  ])
```

### Upsert (Insert or Update)
```javascript
const { data, error } = await supabase
  .from('fact_events')
  .upsert({
    event_key: '18969_1',  // Primary key determines insert vs update
    game_id: 18969,
    event_type: 'Goal',  // Updated value
    // ... other fields
  })
```

### Update Existing Row
```javascript
const { data, error } = await supabase
  .from('fact_events')
  .update({ event_type: 'Goal', event_detail: 'Tip-In' })
  .eq('event_key', '18969_1')
```

### Delete
```javascript
const { data, error } = await supabase
  .from('fact_events')
  .delete()
  .eq('event_key', '18969_1')
```

---

## Real-Time Subscriptions

```javascript
// Subscribe to new events
const subscription = supabase
  .channel('events')
  .on(
    'postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'fact_events' },
    (payload) => {
      console.log('New event:', payload.new)
    }
  )
  .subscribe()

// Unsubscribe
subscription.unsubscribe()
```

---

## Error Handling

```javascript
const { data, error } = await supabase
  .from('fact_events')
  .insert(eventData)

if (error) {
  if (error.code === '23505') {
    console.error('Duplicate key - event already exists')
  } else if (error.code === '23503') {
    console.error('Foreign key violation - invalid player_id or game_id')
  } else {
    console.error('Database error:', error.message)
  }
  return
}

console.log('Success:', data)
```

---

## Common Patterns

### Fetch with Loading State (React)
```javascript
const [players, setPlayers] = useState([])
const [loading, setLoading] = useState(true)
const [error, setError] = useState(null)

useEffect(() => {
  async function fetchPlayers() {
    const { data, error } = await supabase
      .from('dim_player')
      .select('*')
      .order('player_name')
    
    if (error) setError(error)
    else setPlayers(data)
    setLoading(false)
  }
  fetchPlayers()
}, [])
```

### Custom Hook
```javascript
function useGameStats(gameId) {
  const [stats, setStats] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!gameId) return
    
    supabase
      .from('fact_player_game_stats')
      .select(`*, dim_player(player_name)`)
      .eq('game_id', gameId)
      .then(({ data }) => {
        setStats(data || [])
        setLoading(false)
      })
  }, [gameId])

  return { stats, loading }
}
```
