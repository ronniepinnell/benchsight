// src/components/leaders/season-filter.tsx
'use client'

import { useRouter, useSearchParams } from 'next/navigation'

interface SeasonFilterProps {
  seasons: string[]
  currentSeason: string | null
  selectedSeason: string | null
}

// Format season ID to readable name (e.g., "N20242025F" -> "2024-2025 Fall")
function formatSeasonName(seasonId: string): string {
  // Format: N20242025F or N20242025S
  // Extract: N (prefix), YYYY (start year), YYYY (end year), F/S (Fall/Spring)
  const match = seasonId.match(/^N?(\d{4})(\d{4})([FS])$/)
  if (match) {
    const [, startYear, endYear, session] = match
    const sessionName = session === 'F' ? 'Fall' : 'Spring'
    return `${startYear}-${endYear} ${sessionName}`
  }
  // Fallback: try to extract just years if format is different
  const yearMatch = seasonId.match(/(\d{4})(\d{4})/)
  if (yearMatch) {
    const [, startYear, endYear] = yearMatch
    return `${startYear}-${endYear}`
  }
  // Final fallback: return as-is
  return seasonId
}

export function SeasonFilter({ seasons, currentSeason, selectedSeason }: SeasonFilterProps) {
  const router = useRouter()
  const searchParams = useSearchParams()

  const handleSeasonChange = (season: string) => {
    const params = new URLSearchParams(searchParams.toString())
    if (season && season !== currentSeason) {
      params.set('season', season)
    } else {
      params.delete('season')
    }
    // Preserve tab parameter
    const tab = searchParams.get('tab') || 'skaters'
    if (tab) {
      params.set('tab', tab)
    }
    router.push(`/leaders?${params.toString()}`)
  }

  return (
    <div className="flex items-center gap-4">
      <label className="text-sm font-mono text-muted-foreground uppercase">Season:</label>
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
      {selectedSeason === currentSeason && (
        <span className="text-xs text-muted-foreground font-mono">(Current)</span>
      )}
    </div>
  )
}
