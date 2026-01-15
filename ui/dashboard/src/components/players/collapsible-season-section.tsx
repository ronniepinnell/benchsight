'use client'

import { useState } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'
import { cn, formatSeason } from '@/lib/utils'

interface CollapsibleSeasonSectionProps {
  seasonId: string
  season: string | number
  games: any[]
  children: React.ReactNode
}

export function CollapsibleSeasonSection({
  seasonId,
  season,
  games,
  children
}: CollapsibleSeasonSectionProps) {
  const [isExpanded, setIsExpanded] = useState(true)

  const regularGames = games.filter(g => !g.game_type || g.game_type === 'Regular' || g.game_type === 'regular')
  const playoffGames = games.filter(g => g.game_type === 'Playoffs' || g.game_type === 'playoffs' || g.game_type === 'Playoff')

  return (
    <div className="bg-card rounded-xl border border-border overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 bg-accent border-b border-border hover:bg-accent/80 transition-colors flex items-center justify-between"
      >
        <div className="flex items-center gap-3">
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-muted-foreground" />
          ) : (
            <ChevronDown className="w-4 h-4 text-muted-foreground" />
          )}
          <h2 className="font-display text-sm font-semibold uppercase tracking-wider">
            {formatSeason(season)} Season
          </h2>
          <span className="text-xs font-mono text-muted-foreground">
            ({games.length} game{games.length !== 1 ? 's' : ''})
          </span>
          {regularGames.length > 0 && playoffGames.length > 0 && (
            <span className="text-xs font-mono text-muted-foreground">
              • {regularGames.length} Regular, {playoffGames.length} Playoff
            </span>
          )}
        </div>
      </button>
      
      {isExpanded && (
        <div className="p-4">
          {children}
        </div>
      )}
    </div>
  )
}
