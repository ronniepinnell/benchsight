'use client'

/**
 * Player Roster Component
 * 
 * Display and select players from roster
 */

import { useTrackerStore } from '@/lib/tracker/state'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import type { Player, Team } from '@/lib/tracker/types'

interface PlayerRosterProps {
  team: Team
  onPlayerSelect?: (player: Player) => void
  className?: string
}

export function PlayerRoster({ team, onPlayerSelect, className }: PlayerRosterProps) {
  const {
    rosters,
    curr,
    evtTeam,
    selectedPlayer,
    addCurrentPlayer,
    removeCurrentPlayer,
    setSelectedPlayer
  } = useTrackerStore()

  const roster = rosters[team]
  const currentPlayers = curr.players || []

  const handlePlayerClick = (player: Player) => {
    // Check if player is already in current event
    const isInEvent = currentPlayers.some(p => p.num === player.num && p.team === player.team)
    
    if (isInEvent) {
      // Remove from event
      // Find the player in current event
      const playerInEvent = currentPlayers.find(p => p.num === player.num && p.team === player.team)
      if (playerInEvent) {
        removeCurrentPlayer(playerInEvent)
      }
    } else {
      // Add to event
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
      onPlayerSelect?.(player)
    }
    
    setSelectedPlayer(player)
  }

  if (!roster || roster.length === 0) {
    return (
      <div className={cn('p-4 text-center text-sm text-muted-foreground', className)}>
        No roster loaded. Load roster to select players.
      </div>
    )
  }

  return (
    <div className={cn('space-y-2', className)}>
      <div className={cn(
        'text-xs font-semibold uppercase mb-2 px-2',
        team === 'home' ? 'text-blue-500' : 'text-red-500'
      )}>
        {team === 'home' ? 'Home' : 'Away'} Roster
      </div>

      <div className="flex flex-wrap gap-1 p-2">
        {roster.map((player) => {
          const isInEvent = currentPlayers.some(p => p.num === player.num && p.team === player.team)
          const isSelected = selectedPlayer?.num === player.num && selectedPlayer?.team === player.team

          return (
            <button
              key={`${team}-${player.num}`}
              onClick={() => handlePlayerClick(player)}
              className={cn(
                'px-2 py-1 text-xs rounded border-2 transition-all',
                'flex flex-col items-center min-w-[44px]',
                isInEvent
                  ? 'bg-accent text-foreground border-accent font-bold'
                  : isSelected
                  ? 'bg-muted border-accent'
                  : team === 'home'
                  ? 'bg-blue-500/10 border-blue-500/50 hover:border-blue-500'
                  : 'bg-red-500/10 border-red-500/50 hover:border-red-500'
              )}
            >
              <span className="font-bold">#{player.num}</span>
              {player.name && (
                <span className="text-[10px] text-muted-foreground truncate w-full text-center">
                  {player.name}
                </span>
              )}
              {isInEvent && (
                <span className="text-[8px] text-accent-foreground">✓</span>
              )}
            </button>
          )
        })}
      </div>
    </div>
  )
}
