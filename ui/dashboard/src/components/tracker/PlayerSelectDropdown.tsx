'use client'

/**
 * Player Select Dropdown Component
 * 
 * Dropdown select for adding players to events
 */

import { useState } from 'react'
import { useTrackerStore } from '@/lib/tracker/state'
import { cn } from '@/lib/utils'
import type { Player, Team } from '@/lib/tracker/types'

interface PlayerSelectDropdownProps {
  team: Team
  className?: string
  currentPlayers?: Player[] // Optional: for use in modals with local state
  onPlayerSelect?: (player: Player) => void // Optional: callback for modals
  evtTeam?: Team // Optional: for determining role
}

export function PlayerSelectDropdown({ 
  team, 
  className,
  currentPlayers: externalCurrentPlayers,
  onPlayerSelect,
  evtTeam: externalEvtTeam
}: PlayerSelectDropdownProps) {
  const {
    rosters,
    curr,
    evtTeam: globalEvtTeam,
    addCurrentPlayer
  } = useTrackerStore()

  // Use external props if provided (for modals), otherwise use global state
  const currentPlayers = externalCurrentPlayers || curr.players || []
  const evtTeam = externalEvtTeam || globalEvtTeam
  const roster = rosters[team]
  const [selectedValue, setSelectedValue] = useState('')

  // Filter out players already in the event
  const availablePlayers = roster.filter(player => 
    !currentPlayers.some(p => p.num === player.num && p.team === player.team)
  )

  const handlePlayerSelect = (value: string) => {
    if (!value || value === '') {
      setSelectedValue('')
      return
    }

    const player = roster.find(p => `${p.num}` === value)
    if (!player) {
      setSelectedValue('')
      return
    }

    // If callback provided (for modals), use it
    if (onPlayerSelect) {
      onPlayerSelect(player)
      setSelectedValue('')
      return
    }

    // Otherwise use global state (for EventForm)
    // Determine role based on current players
    const eventPlayers = currentPlayers.filter(p => p.role?.startsWith('event'))
    const oppPlayers = currentPlayers.filter(p => p.role?.startsWith('opp'))
    
    let role: string
    if (team === evtTeam) {
      // Event team player
      const roleNum = eventPlayers.length + 1
      role = `event_team_player_${roleNum}`
    } else {
      // Opponent player
      const roleNum = oppPlayers.length + 1
      role = `opponent_player_${roleNum}`
    }
    
    addCurrentPlayer({
      ...player,
      team,
      role: role as any
    })

    // Reset dropdown
    setSelectedValue('')
  }

  if (!roster || roster.length === 0) {
    return (
      <div className={cn('p-2 text-center text-xs text-muted-foreground', className)}>
        No roster loaded. Load roster to select players.
      </div>
    )
  }

  return (
    <div className={cn('space-y-2', className)}>
      <select
        value={selectedValue}
        onChange={(e) => handlePlayerSelect(e.target.value)}
        className={cn(
          'w-full px-2 py-1.5 text-sm bg-input border border-border rounded',
          'text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
          team === 'home' ? 'focus:ring-blue-500' : 'focus:ring-red-500'
        )}
      >
        <option value="">-- Select Player --</option>
        {availablePlayers.length === 0 ? (
          <option value="" disabled>All players already added</option>
        ) : (
          availablePlayers.map((player) => (
            <option key={`${team}-${player.num}`} value={player.num}>
              #{player.num} {player.name || ''}
            </option>
          ))
        )}
      </select>
      {availablePlayers.length === 0 && currentPlayers.length > 0 && (
        <p className="text-xs text-muted-foreground">
          All players from this team are already in the event
        </p>
      )}
    </div>
  )
}
