'use client'

import { useRouter, useSearchParams } from 'next/navigation'
import { Users } from 'lucide-react'
import { useCallback } from 'react'
import { SearchableSelect, SearchableSelectOption } from '@/components/common/searchable-select'

interface Player {
  player_id: number
  player_name: string
  team_name?: string
}

interface PlayerSelectDropdownProps {
  players: Player[]
  selectedPlayerId?: string | null
  paramName: 'p1' | 'p2'
  label: string
  selectedPlayer?: {
    player_name?: string
    team_name?: string
  } | null
}

export function PlayerSelectDropdown({
  players,
  selectedPlayerId,
  paramName,
  label,
  selectedPlayer,
}: PlayerSelectDropdownProps) {
  const router = useRouter()
  const searchParams = useSearchParams()

  const handleChange = useCallback((newValue: string) => {
    const params = new URLSearchParams(searchParams.toString())
    if (newValue) {
      params.set(paramName, newValue)
    } else {
      params.delete(paramName)
    }
    router.push(`?${params.toString()}`)
  }, [paramName, router, searchParams])

  const options: SearchableSelectOption[] = players.map((player) => ({
    value: String(player.player_id),
    label: `${player.player_name}${player.team_name ? ` (${player.team_name})` : ''}`,
    searchText: `${player.player_name} ${player.team_name || ''}`,
  }))

  return (
    <div className="bg-card rounded-xl border border-border overflow-hidden">
      <div className="px-4 py-3 bg-accent border-b border-border">
        <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
          <Users className="w-4 h-4" />
          {label}
        </h2>
      </div>
      <div className="p-4">
        <SearchableSelect
          options={options}
          value={selectedPlayerId ?? ''}
          onChange={handleChange}
          placeholder="Select a player..."
        />
        
        {selectedPlayer && selectedPlayer.player_name && (
          <div className="mt-4 text-center">
            <div className="font-display text-xl font-bold text-foreground">
              {selectedPlayer.player_name}
            </div>
            {selectedPlayer.team_name && (
              <div className="text-sm text-muted-foreground">
                {selectedPlayer.team_name}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
