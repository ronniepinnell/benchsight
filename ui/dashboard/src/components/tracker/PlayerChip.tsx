'use client'

/**
 * Player Chip Component
 * 
 * Individual player chip for display in player lists
 */

import { cn } from '@/lib/utils'
import type { Player } from '@/lib/tracker/types'

interface PlayerChipProps {
  player: Player
  role?: string
  onRemove?: () => void
  onClick?: () => void
  selected?: boolean
  className?: string
}

export function PlayerChip({ 
  player, 
  role, 
  onRemove, 
  onClick, 
  selected,
  className 
}: PlayerChipProps) {
  const isEvent = role?.startsWith('event')
  const isOpp = role?.startsWith('opp')

  return (
    <div
      onClick={onClick}
      className={cn(
        'inline-flex items-center gap-1 px-2 py-1 rounded text-xs cursor-pointer',
        'border-2 transition-all',
        isEvent
          ? 'border-accent bg-accent/10 text-foreground'
          : isOpp
          ? 'border-red-500 bg-red-500/10 text-foreground'
          : 'border-border bg-input hover:bg-muted',
        selected && 'ring-2 ring-warning',
        className
      )}
    >
      {role && (
        <span className={cn(
          'text-[10px] px-1 py-0.5 rounded bg-background',
          isEvent ? 'text-accent' : isOpp ? 'text-red-500' : 'text-muted-foreground'
        )}>
          {role.replace('event_team_player_', 'E').replace('opponent_player_', 'O')}
        </span>
      )}
      <span className="font-bold">#{player.num}</span>
      {player.name && (
        <span className="text-[10px] text-muted-foreground truncate max-w-[80px]">
          {player.name}
        </span>
      )}
      {onRemove && (
        <button
          onClick={(e) => {
            e.stopPropagation()
            onRemove()
          }}
          className="ml-1 text-muted-foreground hover:text-destructive text-[10px]"
        >
          ×
        </button>
      )}
    </div>
  )
}
