'use client'

import { useRouter } from 'next/navigation'
import { Filter } from 'lucide-react'
import Link from 'next/link'

interface PlayerGamesFiltersProps {
  playerId: string
  season?: string
  opponent?: string
  gameType?: string
  search?: string
  playerSeasons: Array<{ season_id: string; season: string | number }>
  uniqueOpponents: string[]
}

export function PlayerGamesFilters({
  playerId,
  season,
  opponent,
  gameType,
  search,
  playerSeasons,
  uniqueOpponents,
}: PlayerGamesFiltersProps) {
  const router = useRouter()
  
  const buildFilterUrl = (updates: Record<string, string | null>) => {
    const params = new URLSearchParams()
    if (updates.season !== undefined) {
      if (updates.season) params.set('season', updates.season)
    } else if (season) {
      params.set('season', season)
    }
    if (updates.opponent !== undefined) {
      if (updates.opponent) params.set('opponent', updates.opponent)
    } else if (opponent) {
      params.set('opponent', opponent)
    }
    if (updates.gameType !== undefined) {
      if (updates.gameType && updates.gameType !== 'All') params.set('gameType', updates.gameType)
    } else if (gameType && gameType !== 'All') {
      params.set('gameType', gameType)
    }
    if (updates.search !== undefined) {
      if (updates.search) params.set('search', updates.search)
    } else if (search) {
      params.set('search', search)
    }
    const queryString = params.toString()
    return `/norad/players/${playerId}/games${queryString ? `?${queryString}` : ''}`
  }
  
  const handleFilterChange = (updates: Record<string, string | null>) => {
    router.push(buildFilterUrl(updates))
  }
  
  return (
    <div className="bg-card rounded-xl border border-border p-6">
      <div className="flex items-center gap-2 mb-4">
        <Filter className="w-4 h-4 text-muted-foreground" />
        <h2 className="font-display text-sm font-semibold uppercase tracking-wider">Filters</h2>
      </div>
      
      <div className="grid md:grid-cols-4 gap-4">
        {/* Season Filter */}
        <div>
          <label className="text-xs font-mono text-muted-foreground uppercase mb-2 block">Season</label>
          <select
            value={season || ''}
            onChange={(e) => handleFilterChange({ season: e.target.value || null })}
            className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="">All Seasons</option>
            {playerSeasons.map(s => (
              <option key={s.season_id} value={s.season_id}>
                {typeof s.season === 'number' 
                  ? `${Math.floor(s.season / 10000)}-${s.season % 10000}`
                  : s.season || s.season_id}
              </option>
            ))}
          </select>
        </div>
        
        {/* Opponent Filter */}
        <div>
          <label className="text-xs font-mono text-muted-foreground uppercase mb-2 block">Opponent</label>
          <select
            value={opponent || ''}
            onChange={(e) => handleFilterChange({ opponent: e.target.value || null })}
            className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="">All Opponents</option>
            {uniqueOpponents.map(opp => (
              <option key={opp} value={opp}>
                {opp}
              </option>
            ))}
          </select>
        </div>
        
        {/* Game Type Filter */}
        <div>
          <label className="text-xs font-mono text-muted-foreground uppercase mb-2 block">Game Type</label>
          <select
            value={gameType || 'All'}
            onChange={(e) => handleFilterChange({ gameType: e.target.value || null })}
            className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="All">All Games</option>
            <option value="Regular">Regular Season</option>
            <option value="Playoffs">Playoffs</option>
          </select>
        </div>
        
        {/* Search */}
        <div>
          <label className="text-xs font-mono text-muted-foreground uppercase mb-2 block">Search</label>
          <input
            type="text"
            defaultValue={search || ''}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleFilterChange({ search: e.currentTarget.value || null })
              }
            }}
            placeholder="Team, game ID..."
            className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
      </div>
      
      {/* Clear Filters */}
      {(season || opponent || (gameType && gameType !== 'All') || search) && (
        <div className="mt-4">
          <Link
            href={`/norad/players/${playerId}/games`}
            className="text-xs text-muted-foreground hover:text-foreground underline"
          >
            Clear all filters
          </Link>
        </div>
      )}
    </div>
  )
}
