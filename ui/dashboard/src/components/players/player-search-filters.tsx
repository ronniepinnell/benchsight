'use client'

import { useRouter, useSearchParams } from 'next/navigation'
import { Search, Filter, X } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useState } from 'react'
import { SearchableSelect, SearchableSelectOption } from '@/components/common/searchable-select'

interface PlayerSearchFiltersProps {
  teams: Array<{ team_id: string; team_name: string }>
  seasons?: Array<{ season_id: string; season: string }>
  currentSeason?: string | null
  selectedSeason?: string | null
}

export function PlayerSearchFilters({ 
  teams, 
  seasons = [], 
  currentSeason = null, 
  selectedSeason = null 
}: PlayerSearchFiltersProps) {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [search, setSearch] = useState(searchParams.get('search') || '')
  const [position, setPosition] = useState(searchParams.get('position') || '')
  const [team, setTeam] = useState(searchParams.get('team') || '')
  const [season, setSeason] = useState(searchParams.get('season') || '')
  const [minGP, setMinGP] = useState(searchParams.get('minGP') || '')
  const [maxGP, setMaxGP] = useState(searchParams.get('maxGP') || '')
  const [minRating, setMinRating] = useState(searchParams.get('minRating') || '')
  const [maxRating, setMaxRating] = useState(searchParams.get('maxRating') || '')
  const [playerId, setPlayerId] = useState(searchParams.get('playerId') || '')

  const updateFilters = () => {
    const params = new URLSearchParams()
    
    if (search) params.set('search', search)
    if (position) params.set('position', position)
    if (team) params.set('team', team)
    if (season && season !== currentSeason) params.set('season', season)
    if (minGP) params.set('minGP', minGP)
    if (maxGP) params.set('maxGP', maxGP)
    if (minRating) params.set('minRating', minRating)
    if (maxRating) params.set('maxRating', maxRating)
    if (playerId) params.set('playerId', playerId)
    
    router.push(`/players?${params.toString()}`)
  }

  const clearFilters = () => {
    setSearch('')
    setPosition('')
    setTeam('')
    setSeason('')
    setMinGP('')
    setMaxGP('')
    setMinRating('')
    setMaxRating('')
    setPlayerId('')
    router.push('/norad/players')
  }

  const hasActiveFilters = search || position || team || (season && season !== currentSeason) || minGP || maxGP || minRating || maxRating || playerId

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
          <Filter className="w-4 h-4" />
          Search & Filters
        </h3>
        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="text-xs font-mono text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1"
          >
            <X className="w-3 h-3" />
            Clear All
          </button>
        )}
      </div>
      
      <form
        onSubmit={(e) => {
          e.preventDefault()
          updateFilters()
        }}
        className="space-y-4"
      >
        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by name, team, or player ID..."
            className="w-full pl-10 pr-4 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
        
        {/* Filter Row 1 */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {/* Season */}
          {seasons.length > 0 && (
            <div>
              <label className="text-xs font-mono text-muted-foreground uppercase mb-1 block">
                Season
              </label>
              <SearchableSelect
                options={seasons.map(s => ({
                  value: s.season_id,
                  label: `${s.season}${s.season_id === currentSeason ? ' (Current)' : ''}`,
                  searchText: s.season,
                }))}
                value={season || currentSeason || ''}
                onChange={(val) => setSeason(val === currentSeason ? '' : val)}
                placeholder="Select season..."
              />
            </div>
          )}
          
          {/* Position */}
          <div>
            <label className="text-xs font-mono text-muted-foreground uppercase mb-1 block">
              Position
            </label>
            <SearchableSelect
              options={[
                { value: '', label: 'All Positions', searchText: 'all positions' },
                { value: 'forward', label: 'Forward', searchText: 'forward' },
                { value: 'defense', label: 'Defense', searchText: 'defense' },
                { value: 'goalie', label: 'Goalie', searchText: 'goalie' },
              ]}
              value={position}
              onChange={setPosition}
              placeholder="All Positions"
            />
          </div>
          
          {/* Team */}
          <div>
            <label className="text-xs font-mono text-muted-foreground uppercase mb-1 block">
              Team
            </label>
            <SearchableSelect
              options={[
                { value: '', label: 'All Teams', searchText: 'all teams' },
                ...teams.map(t => ({
                  value: t.team_id,
                  label: t.team_name,
                  searchText: t.team_name,
                })),
              ]}
              value={team}
              onChange={setTeam}
              placeholder="All Teams"
            />
          </div>
          
          {/* Min GP */}
          <div>
            <label className="text-xs font-mono text-muted-foreground uppercase mb-1 block">
              Min GP
            </label>
            <input
              type="number"
              value={minGP}
              onChange={(e) => setMinGP(e.target.value)}
              placeholder="0"
              min="0"
              className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm font-mono focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
        </div>
        
        {/* Filter Row 2 */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {/* Max GP */}
          <div>
            <label className="text-xs font-mono text-muted-foreground uppercase mb-1 block">
              Max GP
            </label>
            <input
              type="number"
              value={maxGP}
              onChange={(e) => setMaxGP(e.target.value)}
              placeholder="∞"
              min="0"
              className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm font-mono focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          
          {/* Min Rating */}
          <div>
            <label className="text-xs font-mono text-muted-foreground uppercase mb-1 block">
              Min Rating
            </label>
            <input
              type="number"
              value={minRating}
              onChange={(e) => setMinRating(e.target.value)}
              placeholder="0.0"
              min="0"
              max="6"
              step="0.1"
              className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm font-mono focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          
          {/* Max Rating */}
          <div>
            <label className="text-xs font-mono text-muted-foreground uppercase mb-1 block">
              Max Rating
            </label>
            <input
              type="number"
              value={maxRating}
              onChange={(e) => setMaxRating(e.target.value)}
              placeholder="6.0"
              min="0"
              max="6"
              step="0.1"
              className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm font-mono focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          
          {/* Player ID */}
          <div>
            <label className="text-xs font-mono text-muted-foreground uppercase mb-1 block">
              Player ID
            </label>
            <input
              type="text"
              value={playerId}
              onChange={(e) => setPlayerId(e.target.value)}
              placeholder="P######"
              className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm font-mono focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          
          {/* Apply Button */}
          <div className="flex items-end">
            <button
              type="submit"
              className="w-full px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-semibold hover:bg-primary/90 transition-colors"
            >
              Apply Filters
            </button>
          </div>
        </div>
      </form>
    </div>
  )
}
