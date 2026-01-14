'use client'

import { useRouter, useSearchParams } from 'next/navigation'
import { Search } from 'lucide-react'

interface GamesFiltersProps {
  seasons: string[]
  currentSeason: string | null
  selectedSeason: string | null
  teams: Array<{ team_id: string; team_name: string }>
  selectedTeam: string | null
  gameType: string
  search: string | null
  seasonId?: string | null
}

// Format season ID to readable name (e.g., "N20242025F" -> "2024-2025 Fall")
function formatSeasonName(seasonId: string): string {
  const match = seasonId.match(/^N?(\d{4})(\d{4})([FS])$/)
  if (match) {
    const [, startYear, endYear, session] = match
    const sessionName = session === 'F' ? 'Fall' : 'Spring'
    return `${startYear}-${endYear} ${sessionName}`
  }
  const yearMatch = seasonId.match(/(\d{4})(\d{4})/)
  if (yearMatch) {
    const [, startYear, endYear] = yearMatch
    return `${startYear}-${endYear}`
  }
  return seasonId
}

export function GamesFilters({
  seasons,
  currentSeason,
  selectedSeason,
  teams,
  selectedTeam,
  gameType,
  search,
}: GamesFiltersProps) {
  const router = useRouter()
  const searchParams = useSearchParams()
  const currentSearch = searchParams.get('search') || ''

  const updateParams = (updates: Record<string, string | null>) => {
    const params = new URLSearchParams(searchParams.toString())
    
    Object.entries(updates).forEach(([key, value]) => {
      if (value && value !== 'All' && value !== '') {
        params.set(key, value)
      } else {
        params.delete(key)
      }
    })
    
    // Reset offset when filters change
    params.delete('offset')
    
    router.push(`/games?${params.toString()}`)
  }

  const handleSeasonChange = (season: string) => {
    updateParams({ season: season === currentSeason ? null : season })
  }

  const handleTeamChange = (teamId: string) => {
    updateParams({ team: teamId || null })
  }

  const handleGameTypeChange = (type: string) => {
    updateParams({ gameType: type })
  }

  const handleSearchSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const searchValue = formData.get('search') as string
    updateParams({ search: searchValue.trim() || null })
  }

  return (
    <div className="space-y-4">
      {/* Filters Row */}
      <div className="flex flex-wrap items-center gap-4">
        {/* Season Filter */}
        <div className="flex items-center gap-2">
          <label className="text-sm font-mono text-muted-foreground uppercase whitespace-nowrap">
            Season:
          </label>
          <select
            value={selectedSeason || currentSeason || ''}
            onChange={(e) => handleSeasonChange(e.target.value)}
            className="bg-card border border-border rounded-lg px-3 py-2 text-sm font-mono text-foreground hover:border-primary transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
          >
            {seasons.map((season) => {
              const displayName = formatSeasonName(season)
              const isCurrent = season === currentSeason
              return (
                <option key={season} value={season}>
                  {displayName}{isCurrent ? ' (Current)' : ''}
                </option>
              )
            })}
          </select>
        </div>

        {/* Team Filter */}
        <div className="flex items-center gap-2">
          <label className="text-sm font-mono text-muted-foreground uppercase whitespace-nowrap">
            Team:
          </label>
          <select
            value={selectedTeam || ''}
            onChange={(e) => handleTeamChange(e.target.value)}
            className="bg-card border border-border rounded-lg px-3 py-2 text-sm font-mono text-foreground hover:border-primary transition-colors focus:outline-none focus:ring-2 focus:ring-primary min-w-[150px]"
          >
            <option value="">All Teams</option>
            {teams.map((team) => (
              <option key={team.team_id} value={team.team_id}>
                {team.team_name}
              </option>
            ))}
          </select>
        </div>

        {/* Game Type Tabs */}
        <div className="flex gap-2 border border-border rounded-lg p-1">
          {[
            { id: 'All', label: 'All' },
            { id: 'Regular', label: 'Regular' },
            { id: 'Playoffs', label: 'Playoffs' },
          ].map((tab) => {
            const isActive = gameType === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => handleGameTypeChange(tab.id)}
                className={`
                  px-3 py-1.5 text-xs font-mono rounded transition-all
                  ${
                    isActive
                      ? 'bg-primary text-primary-foreground font-semibold'
                      : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                  }
                `}
              >
                {tab.label}
              </button>
            )
          })}
        </div>
      </div>

      {/* Search */}
      <form onSubmit={handleSearchSubmit} className="flex items-center gap-2">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            name="search"
            defaultValue={currentSearch}
            placeholder="Search by team name or game ID..."
            className="w-full pl-10 pr-4 py-2 bg-card border border-border rounded-lg text-sm font-mono text-foreground placeholder:text-muted-foreground hover:border-primary transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
        <button
          type="submit"
          className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-mono hover:bg-primary/90 transition-colors"
        >
          Search
        </button>
        {currentSearch && (
          <button
            type="button"
            onClick={() => updateParams({ search: null })}
            className="px-4 py-2 bg-muted text-muted-foreground rounded-lg text-sm font-mono hover:bg-muted/80 transition-colors"
          >
            Clear
          </button>
        )}
      </form>
    </div>
  )
}
