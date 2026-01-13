'use client'

import { useRouter, useSearchParams } from 'next/navigation'
import { Calendar } from 'lucide-react'

interface SeasonSelectorProps {
  seasons: Array<{ season_id: string; season: string }>
  currentSeason: string
}

export function SeasonSelector({ seasons, currentSeason }: SeasonSelectorProps) {
  const router = useRouter()
  const searchParams = useSearchParams()
  
  const handleSeasonChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const seasonId = e.target.value
    const params = new URLSearchParams(searchParams.toString())
    if (seasonId === currentSeason || !seasonId) {
      params.delete('season')
    } else {
      params.set('season', seasonId)
    }
    router.push(`?${params.toString()}`)
  }
  
  return (
    <div className="flex items-center gap-2">
      <Calendar className="w-4 h-4 text-muted-foreground" />
      <select
        value={currentSeason}
        onChange={handleSeasonChange}
        className="bg-card border border-border rounded-lg px-3 py-2 text-sm font-mono text-foreground hover:border-primary transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
      >
        {seasons.map((s) => (
          <option key={s.season_id} value={s.season_id}>
            {s.season}
          </option>
        ))}
      </select>
    </div>
  )
}
