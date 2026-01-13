// src/components/leaders/season-filter.tsx
'use client'

import { useRouter, useSearchParams } from 'next/navigation'

interface SeasonFilterProps {
  seasons: string[]
  currentSeason: string | null
  selectedSeason: string | null
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
        {seasons.map((season) => (
          <option key={season} value={season}>
            {season}
          </option>
        ))}
      </select>
      {selectedSeason === currentSeason && (
        <span className="text-xs text-muted-foreground font-mono">(Current)</span>
      )}
    </div>
  )
}
