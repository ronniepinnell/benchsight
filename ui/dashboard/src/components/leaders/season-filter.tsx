// src/components/leaders/season-filter.tsx
'use client'

import { useRouter, useSearchParams, usePathname } from 'next/navigation'
import { SearchableSelect, SearchableSelectOption } from '@/components/common/searchable-select'

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
  const pathname = usePathname()

  const handleSeasonChange = (season: string) => {
    const params = new URLSearchParams(searchParams.toString())
    if (season && season !== currentSeason) {
      params.set('season', season)
    } else {
      params.delete('season')
    }
    // Preserve tab parameter if it exists
    const tab = searchParams.get('tab')
    if (tab) {
      params.set('tab', tab)
    }
    
    // Determine the base path from current route
    const basePath = pathname.includes('/goalies') ? '/norad/goalies' : '/norad/leaders'
    router.push(`${basePath}?${params.toString()}`)
  }

  const options: SearchableSelectOption[] = seasons.map((season) => {
    const displayName = formatSeasonName(season)
    const isCurrent = season === currentSeason
    return {
      value: season,
      label: `${displayName}${isCurrent ? ' (Current)' : ''}`,
      searchText: displayName,
    }
  })

  return (
    <div className="flex items-center gap-4">
      <label className="text-sm font-mono text-muted-foreground uppercase">Season:</label>
      <SearchableSelect
        options={options}
        value={selectedSeason || currentSeason || ''}
        onChange={handleSeasonChange}
        placeholder="Select season..."
        className="min-w-[200px]"
      />
      {selectedSeason === currentSeason && (
        <span className="text-xs text-muted-foreground font-mono">(Current)</span>
      )}
    </div>
  )
}
