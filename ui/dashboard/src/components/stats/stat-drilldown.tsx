'use client'

import Link from 'next/link'
import { Calendar, TrendingUp, TrendingDown } from 'lucide-react'
import { cn } from '@/lib/utils'

interface GameStatRow {
  game_id: number
  date?: string
  opponent?: string
  value: number | string
  opponent_value?: number | string
  context?: string
}

interface StatDrilldownProps {
  statLabel: string
  games: GameStatRow[]
  formatValue?: (val: number | string) => string
  showOpponent?: boolean
  compareWithOpponent?: boolean
}

export function StatDrilldown({
  statLabel,
  games,
  formatValue = (val) => String(val),
  showOpponent = false,
  compareWithOpponent = false
}: StatDrilldownProps) {
  if (!games || games.length === 0) {
    return (
      <div className="text-xs text-muted-foreground italic p-2">
        No game data available for this stat.
      </div>
    )
  }

  // Calculate average and trend
  const numericValues = games
    .map(g => typeof g.value === 'number' ? g.value : parseFloat(String(g.value)) || 0)
    .filter(v => !isNaN(v))
  
  const avg = numericValues.length > 0 
    ? numericValues.reduce((a, b) => a + b, 0) / numericValues.length 
    : 0
  
  // Recent vs overall trend (last 5 games vs average)
  const recentGames = numericValues.slice(0, 5)
  const recentAvg = recentGames.length > 0
    ? recentGames.reduce((a, b) => a + b, 0) / recentGames.length
    : 0

  return (
    <div className="space-y-3 pt-2">
      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-2 pb-2 border-b border-border">
        <div className="text-center">
          <div className="text-[10px] font-mono text-muted-foreground uppercase mb-1">Games</div>
          <div className="font-mono text-sm font-semibold text-foreground">{games.length}</div>
        </div>
        <div className="text-center">
          <div className="text-[10px] font-mono text-muted-foreground uppercase mb-1">Average</div>
          <div className="font-mono text-sm font-semibold text-primary">
            {formatValue(avg)}
          </div>
        </div>
        <div className="text-center">
          <div className="text-[10px] font-mono text-muted-foreground uppercase mb-1">Recent</div>
          <div className={cn(
            'font-mono text-sm font-semibold flex items-center justify-center gap-1',
            recentAvg > avg ? 'text-save' : recentAvg < avg ? 'text-goal' : 'text-muted-foreground'
          )}>
            {recentAvg > avg ? (
              <TrendingUp className="w-3 h-3" />
            ) : recentAvg < avg ? (
              <TrendingDown className="w-3 h-3" />
            ) : null}
            {formatValue(recentAvg)}
          </div>
        </div>
      </div>

      {/* Game-by-Game List */}
      <div className="space-y-1 max-h-48 overflow-y-auto">
        {games.slice(0, 10).map((game, idx) => {
          const gameDate = game.date 
            ? new Date(game.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
            : 'Unknown'
          
          const numericValue = typeof game.value === 'number' 
            ? game.value 
            : parseFloat(String(game.value)) || 0
          
          const isAboveAvg = !isNaN(numericValue) && numericValue > avg
          const isBelowAvg = !isNaN(numericValue) && numericValue < avg

          return (
            <Link
              key={game.game_id || idx}
              href={`/games/${game.game_id}`}
              className="flex items-center justify-between py-1.5 px-2 rounded hover:bg-muted/50 transition-colors group"
            >
              <div className="flex items-center gap-2 flex-1 min-w-0">
                <Calendar className="w-3 h-3 text-muted-foreground flex-shrink-0" />
                <span className="text-xs font-mono text-muted-foreground flex-shrink-0">
                  {gameDate}
                </span>
                {game.opponent && (
                  <span className="text-xs text-muted-foreground truncate">
                    vs {game.opponent}
                  </span>
                )}
              </div>
              <div className="flex items-center gap-3 flex-shrink-0">
                {compareWithOpponent && game.opponent_value !== undefined && (
                  <div className="text-xs font-mono text-muted-foreground">
                    {game.opponent_value}
                  </div>
                )}
                <span className={cn(
                  'font-mono text-sm font-semibold',
                  isAboveAvg && 'text-save',
                  isBelowAvg && 'text-goal',
                  !isAboveAvg && !isBelowAvg && 'text-foreground'
                )}>
                  {formatValue(game.value)}
                </span>
              </div>
            </Link>
          )
        })}
      </div>
      
      {games.length > 10 && (
        <div className="text-xs text-muted-foreground text-center pt-2 border-t border-border">
          Showing 10 of {games.length} games
        </div>
      )}
    </div>
  )
}
