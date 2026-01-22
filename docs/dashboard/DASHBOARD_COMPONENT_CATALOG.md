# BenchSight Dashboard Component Catalog

**Complete reference for all React components in the dashboard**

Last Updated: 2026-01-21
Version: 2.00

---

## Overview

This document catalogs all React components in the BenchSight dashboard, organized by category with props, usage, and examples.

**Total Components:** 80+ components  
**Component Library:** shadcn/ui + custom components

---

## Component Categories

### Layout Components (`components/layout/`)

#### `sidebar.tsx`
**Purpose:** Main navigation sidebar  
**Type:** Client Component  
**Props:** None  
**Usage:**
```tsx
<Sidebar />
```

#### `topbar.tsx`
**Purpose:** Top navigation bar with user menu  
**Type:** Client Component  
**Props:** None  
**Usage:**
```tsx
<Topbar />
```

---

### Player Components (`components/players/`)

#### `player-profile-tabs.tsx`
**Purpose:** Player profile with tabs (Overview, Season, Career, Advanced)  
**Type:** Server Component  
**Props:**
- `playerId: string`
- `player: Player`
- `stats: PlayerStats`

**Usage:**
```tsx
<PlayerProfileTabs playerId={playerId} player={player} stats={stats} />
```

#### `player-photo.tsx`
**Purpose:** Player photo with fallback  
**Type:** Client Component  
**Props:**
- `playerId: string`
- `playerName: string`
- `size?: 'sm' | 'md' | 'lg'`

**Usage:**
```tsx
<PlayerPhoto playerId={playerId} playerName={playerName} size="lg" />
```

#### `sortable-prior-teams-table.tsx`
**Purpose:** Sortable table of player's prior teams  
**Type:** Client Component  
**Props:**
- `teams: PriorTeam[]`

**Usage:**
```tsx
<SortablePriorTeamsTable teams={teams} />
```

#### `player-search-filters.tsx`
**Purpose:** Search and filter controls for players  
**Type:** Client Component  
**Props:**
- `onFilterChange: (filters: PlayerFilters) => void`

**Usage:**
```tsx
<PlayerSearchFilters onFilterChange={handleFilterChange} />
```

---

### Goalie Components (`components/goalies/`)

#### `goalie-profile-tabs.tsx`
**Purpose:** Goalie profile with tabs  
**Type:** Server Component  
**Props:**
- `goalieId: string`
- `goalie: Goalie`
- `stats: GoalieStats`

**Usage:**
```tsx
<GoalieProfileTabs goalieId={goalieId} goalie={goalie} stats={stats} />
```

#### `sortable-goalies-table.tsx`
**Purpose:** Sortable goalie statistics table  
**Type:** Client Component  
**Props:**
- `goalies: Goalie[]`
- `sortBy?: string`
- `sortOrder?: 'asc' | 'desc'`

**Usage:**
```tsx
<SortableGoaliesTable goalies={goalies} sortBy="save_pct" />
```

---

### Team Components (`components/teams/`)

#### `team-profile-tabs.tsx`
**Purpose:** Team profile with tabs (Overview, Roster, Lines, Analytics, Matchups)  
**Type:** Server Component  
**Props:**
- `teamId: string`
- `team: Team`
- `stats: TeamStats`

**Usage:**
```tsx
<TeamProfileTabs teamId={teamId} team={team} stats={stats} />
```

#### `team-roster-table.tsx`
**Purpose:** Team roster table  
**Type:** Client Component  
**Props:**
- `players: Player[]`
- `teamId: string`

**Usage:**
```tsx
<TeamRosterTable players={players} teamId={teamId} />
```

---

### Game Components (`components/games/`)

#### `game-summary.tsx`
**Purpose:** Game summary card  
**Type:** Server Component  
**Props:**
- `game: Game`

**Usage:**
```tsx
<GameSummary game={game} />
```

#### `sortable-boxscore-table.tsx`
**Purpose:** Sortable box score table  
**Type:** Client Component  
**Props:**
- `players: PlayerGameStats[]`
- `team: 'home' | 'away'`

**Usage:**
```tsx
<SortableBoxscoreTable players={players} team="home" />
```

#### `PlayByPlayTimeline.tsx`
**Purpose:** Play-by-play timeline visualization  
**Type:** Client Component  
**Props:**
- `events: GameEvent[]`

**Usage:**
```tsx
<PlayByPlayTimeline events={events} />
```

#### `shift-chart.tsx`
**Purpose:** Shift timeline chart  
**Type:** Client Component  
**Props:**
- `shifts: Shift[]`
- `players: Player[]`

**Usage:**
```tsx
<ShiftChart shifts={shifts} players={players} />
```

---

### Chart Components (`components/charts/`)

#### `trend-line-chart.tsx`
**Purpose:** Trend line chart (Recharts)  
**Type:** Client Component  
**Props:**
- `data: TrendData[]`
- `metric: string`
- `title?: string`

**Usage:**
```tsx
<TrendLineChart data={trendData} metric="goals" title="Goals Per Game" />
```

#### `radar-chart.tsx`
**Purpose:** Radar chart for multi-dimensional comparison  
**Type:** Client Component  
**Props:**
- `data: RadarData[]`
- `metrics: string[]`

**Usage:**
```tsx
<RadarChart data={playerData} metrics={['goals', 'assists', 'points']} />
```

#### `enhanced-shot-map.tsx`
**Purpose:** Enhanced shot map visualization  
**Type:** Client Component  
**Props:**
- `shots: Shot[]`
- `rinkDimensions?: RinkDimensions`

**Usage:**
```tsx
<EnhancedShotMap shots={shots} />
```

#### `shot-heatmap.tsx`
**Purpose:** Shot heatmap  
**Type:** Client Component  
**Props:**
- `shots: Shot[]`

**Usage:**
```tsx
<ShotHeatmap shots={shots} />
```

---

### Common Components (`components/common/`)

#### `sortable-table.tsx`
**Purpose:** Generic sortable table  
**Type:** Client Component  
**Props:**
- `data: any[]`
- `columns: ColumnDef[]`
- `defaultSort?: { column: string; order: 'asc' | 'desc' }`

**Usage:**
```tsx
<SortableTable 
  data={players} 
  columns={playerColumns}
  defaultSort={{ column: 'points', order: 'desc' }}
/>
```

#### `searchable-select.tsx`
**Purpose:** Searchable dropdown select  
**Type:** Client Component  
**Props:**
- `options: Option[]`
- `value: string`
- `onChange: (value: string) => void`
- `placeholder?: string`

**Usage:**
```tsx
<SearchableSelect
  options={playerOptions}
  value={selectedPlayer}
  onChange={setSelectedPlayer}
  placeholder="Select player..."
/>
```

#### `collapsible-section.tsx`
**Purpose:** Collapsible content section  
**Type:** Client Component  
**Props:**
- `title: string`
- `defaultOpen?: boolean`
- `children: React.ReactNode`

**Usage:**
```tsx
<CollapsibleSection title="Advanced Stats" defaultOpen={false}>
  <AdvancedStatsTable />
</CollapsibleSection>
```

---

### UI Components (`components/ui/`)

#### `button.tsx`
**Purpose:** Button component (shadcn/ui)  
**Type:** Client Component  
**Props:**
- `variant?: 'default' | 'outline' | 'ghost' | 'destructive'`
- `size?: 'sm' | 'md' | 'lg'`
- `children: React.ReactNode`

**Usage:**
```tsx
<Button variant="default" size="md">Click Me</Button>
```

#### `tooltip.tsx`
**Purpose:** Tooltip component (shadcn/ui)  
**Type:** Client Component  
**Props:**
- `content: string`
- `children: React.ReactNode`

**Usage:**
```tsx
<Tooltip content="This is a tooltip">
  <Button>Hover me</Button>
</Tooltip>
```

---

### Export Components (`components/export/`)

#### `ExportButton.tsx`
**Purpose:** CSV export button  
**Type:** Client Component  
**Props:**
- `data: any[]`
- `filename: string`
- `columns?: string[]`

**Usage:**
```tsx
<ExportButton 
  data={players} 
  filename="players_export.csv"
  columns={['name', 'goals', 'assists', 'points']}
/>
```

---

## Component Patterns

### Server Component Pattern

```tsx
// app/norad/players/[playerId]/page.tsx
export default async function PlayerPage({ params }: { params: { playerId: string } }) {
  const player = await getPlayer(params.playerId)
  const stats = await getPlayerStats(params.playerId)
  
  return (
    <PlayerProfileTabs playerId={params.playerId} player={player} stats={stats} />
  )
}
```

### Client Component Pattern

```tsx
'use client'

// components/charts/trend-line-chart.tsx
export function TrendLineChart({ data, metric }: { data: TrendData[], metric: string }) {
  const [selectedPeriod, setSelectedPeriod] = useState('all')
  
  return (
    <LineChart data={filteredData}>
      {/* Chart content */}
    </LineChart>
  )
}
```

### Compound Component Pattern

```tsx
// components/players/player-profile-tabs.tsx
export function PlayerProfileTabs({ playerId, player, stats }: Props) {
  return (
    <Tabs defaultValue="overview">
      <TabsList>
        <TabsTrigger value="overview">Overview</TabsTrigger>
        <TabsTrigger value="season">Season</TabsTrigger>
        <TabsTrigger value="career">Career</TabsTrigger>
        <TabsTrigger value="advanced">Advanced</TabsTrigger>
      </TabsList>
      <TabsContent value="overview">
        <PlayerOverviewTab player={player} stats={stats} />
      </TabsContent>
      {/* Other tabs */}
    </Tabs>
  )
}
```

---

## Component Dependencies

### External Libraries

- **Recharts:** Chart components
- **shadcn/ui:** UI component library
- **Tailwind CSS:** Styling
- **React Hook Form:** Form handling (if used)

### Internal Dependencies

- **`lib/supabase/queries/*`:** Data fetching
- **`lib/utils/*`:** Utility functions
- **`types/database.ts`:** TypeScript types

---

## Component Best Practices

### 1. Server vs Client Components

- **Default:** Server components (faster, better SEO)
- **Use client components for:**
  - Interactive features (hover, click, etc.)
  - State management (`useState`, `useEffect`)
  - Browser APIs

### 2. Props Typing

```tsx
// Always type props
interface PlayerProfileProps {
  playerId: string
  player: Player
  stats: PlayerStats
}

export function PlayerProfile({ playerId, player, stats }: PlayerProfileProps) {
  // Component code
}
```

### 3. Error Handling

```tsx
export default async function PlayerPage({ params }: { params: { playerId: string } }) {
  try {
    const player = await getPlayer(params.playerId)
    if (!player) {
      return <NotFound />
    }
    return <PlayerProfile player={player} />
  } catch (error) {
    return <ErrorPage error={error} />
  }
}
```

### 4. Loading States

```tsx
export default async function PlayerPage({ params }: { params: { playerId: string } }) {
  const player = await getPlayer(params.playerId)
  
  return (
    <Suspense fallback={<PlayerProfileSkeleton />}>
      <PlayerProfile player={player} />
    </Suspense>
  )
}
```

---

## Related Documentation

- [DASHBOARD_ARCHITECTURE.md](DASHBOARD_ARCHITECTURE.md) - Architecture overview
- [DASHBOARD_DATA_FLOW.md](DASHBOARD_DATA_FLOW.md) - Data flow
- [DASHBOARD_ROADMAP.md](DASHBOARD_ROADMAP.md) - Development roadmap
- [DASHBOARD_PAGES_INVENTORY.md](DASHBOARD_PAGES_INVENTORY.md) - Pages inventory

---

*Last Updated: 2026-01-15*
