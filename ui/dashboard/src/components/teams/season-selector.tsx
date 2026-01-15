'use client'

import { useRouter, useSearchParams } from 'next/navigation'
import { Calendar } from 'lucide-react'
import { SearchableSelect, SearchableSelectOption } from '@/components/common/searchable-select'

interface SeasonSelectorProps {
  seasons: Array<{ season_id: string; season: string }>
  currentSeason: string
}

export function SeasonSelector({ seasons, currentSeason }: SeasonSelectorProps) {
  const router = useRouter()
  const searchParams = useSearchParams()
  
  const handleSeasonChange = (seasonId: string) => {
    const params = new URLSearchParams(searchParams.toString())
    if (seasonId === currentSeason || !seasonId) {
      params.delete('season')
    } else {
      params.set('season', seasonId)
    }
    router.push(`?${params.toString()}`)
  }

  const options: SearchableSelectOption[] = seasons.map((s) => ({
    value: s.season_id,
    label: s.season,
    searchText: s.season,
  }))
  
  return (
    <div className="flex items-center gap-2">
      <Calendar className="w-4 h-4 text-muted-foreground" />
      <SearchableSelect
        options={options}
        value={currentSeason}
        onChange={handleSeasonChange}
        placeholder="Select season..."
        className="min-w-[200px]"
      />
    </div>
  )
}
