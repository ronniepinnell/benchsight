import { Calendar, Target, TrendingUp, Shield } from 'lucide-react'
import { TrendLineChart } from '@/components/charts/trend-line-chart'
import { CollapsibleSection } from '@/components/common/collapsible-section'
import { cn } from '@/lib/utils'
import Link from 'next/link'

interface SeasonTabProps {
  playerStats: any
  gameLog: any[]
  seasonId: string
  hasPlayedGoalie?: boolean
  hasPlayedSkater?: boolean
  isBoth?: boolean
  goalieStats?: any
}

export function SeasonTab({ playerStats, gameLog, seasonId, hasPlayedGoalie = false, hasPlayedSkater = true, isBoth = false, goalieStats }: SeasonTabProps) {
  // Prepare game-by-game trend data
  const gameTrendData = gameLog
    .slice()
    .reverse()
    .map((game: any, index: number) => ({
      game: index + 1,
      goals: Number(game.goals || 0),
      assists: Number(game.assists || 0),
      points: Number(game.points || 0),
      date: game.date,
    }))

  return (
    <div className="space-y-6">
      {/* Season Summary - Skater */}
      {hasPlayedSkater && playerStats && (
        <CollapsibleSection
          title={isBoth ? "Season Summary - Skater" : "Season Summary"}
          icon={<TrendingUp className="w-4 h-4" />}
          defaultExpanded={true}
        >
          <div className="p-6">
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-card rounded-lg p-4 border border-border">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Games Played</div>
                <div className="font-mono text-2xl font-bold text-foreground">{playerStats.games_played || 0}</div>
              </div>
              <div className="bg-card rounded-lg p-4 border border-border">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Goals</div>
                <div className="font-mono text-2xl font-bold text-goal">{playerStats.goals || 0}</div>
              </div>
              <div className="bg-card rounded-lg p-4 border border-border">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Assists</div>
                <div className="font-mono text-2xl font-bold text-assist">{playerStats.assists || 0}</div>
              </div>
              <div className="bg-card rounded-lg p-4 border border-border">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Points</div>
                <div className="font-mono text-2xl font-bold text-primary">{playerStats.points || 0}</div>
              </div>
            </div>
          </div>
        </CollapsibleSection>
      )}
      
      {/* Season Summary - Goalie */}
      {hasPlayedGoalie && goalieStats && (
        <CollapsibleSection
          title={isBoth ? "Season Summary - Goalie" : "Season Summary"}
          icon={<Shield className="w-4 h-4" />}
          defaultExpanded={true}
        >
          <div className="p-6">
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-card rounded-lg p-4 border border-border">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Games Played</div>
                <div className="font-mono text-2xl font-bold text-foreground">{goalieStats.games_played || 0}</div>
              </div>
              <div className="bg-card rounded-lg p-4 border border-border">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">GAA</div>
                <div className="font-mono text-2xl font-bold text-primary">
                  {goalieStats.gaa ? Number(goalieStats.gaa).toFixed(2) : '-'}
                </div>
              </div>
              <div className="bg-card rounded-lg p-4 border border-border">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">SV%</div>
                <div className="font-mono text-2xl font-bold text-foreground">
                  {goalieStats.save_percent 
                    ? Number(goalieStats.save_percent).toFixed(1) + '%'
                    : goalieStats.sv_pct
                      ? Number(goalieStats.sv_pct).toFixed(1) + '%'
                      : '-'}
                </div>
              </div>
              <div className="bg-card rounded-lg p-4 border border-border">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Wins</div>
                <div className="font-mono text-2xl font-bold text-foreground">{goalieStats.wins || 0}</div>
              </div>
            </div>
          </div>
        </CollapsibleSection>
      )}

      {/* Goals/Game Trend - Skater Only */}
      {hasPlayedSkater && gameTrendData.length > 0 && (
        <CollapsibleSection
          title="Goals Per Game Trend"
          icon={<Target className="w-4 h-4" />}
          defaultExpanded={true}
        >
          <div className="p-6">
            <TrendLineChart
              data={gameTrendData}
              xAxisKey="game"
              dataKeys={[
                { key: 'goals', name: 'Goals', color: 'hsl(var(--goal))' },
              ]}
              height={250}
            />
          </div>
        </CollapsibleSection>
      )}

      {/* Points/Game Trend - Skater Only */}
      {hasPlayedSkater && gameTrendData.length > 0 && (
        <CollapsibleSection
          title="Points Per Game Trend"
          icon={<TrendingUp className="w-4 h-4" />}
          defaultExpanded={true}
        >
          <div className="p-6">
            <TrendLineChart
              data={gameTrendData}
              xAxisKey="game"
              dataKeys={[
                { key: 'points', name: 'Points', color: 'hsl(var(--primary))' },
              ]}
              height={250}
            />
          </div>
        </CollapsibleSection>
      )}

      {/* Game Log Table - Skater Stats */}
      {hasPlayedSkater && gameLog.length > 0 && (
        <CollapsibleSection
          title={isBoth ? "Game-by-Game Stats - Skater" : "Game-by-Game Stats"}
          icon={<Calendar className="w-4 h-4" />}
          defaultExpanded={true}
        >
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-accent/50">
                  <th className="px-4 py-2 text-left font-display text-xs text-muted-foreground">Date</th>
                  <th className="px-4 py-2 text-left font-display text-xs text-muted-foreground">Opponent</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-goal">G</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-assist">A</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-primary">P</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-shot">S</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">+/-</th>
                </tr>
              </thead>
              <tbody>
                {gameLog.map((game: any, index: number) => {
                  const gameDate = game.date ? new Date(game.date).toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric',
                  }) : '-'
                  
                  return (
                    <tr key={game.game_id || `game-${index}`} className="border-b border-border hover:bg-muted/50 transition-colors">
                      <td className="px-4 py-2 font-mono text-xs text-muted-foreground">
                        {game.game_id ? (
                          <Link href={`/norad/games/${game.game_id}`} className="hover:text-primary transition-colors">
                            {gameDate}
                          </Link>
                        ) : (
                          <span>{gameDate}</span>
                        )}
                      </td>
                      <td className="px-4 py-2 text-foreground text-sm">
                        {game.opponent_team_name || game.team_name || '-'}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-goal font-semibold">
                        {game.goals || 0}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-assist">
                        {game.assists || 0}
                      </td>
                      <td className="px-2 py-2 text-center font-mono font-bold text-primary">
                        {game.points || 0}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-shot">
                        {game.shots || game.sog || 0}
                      </td>
                      <td className={cn(
                        'px-2 py-2 text-center font-mono',
                        (game.plus_minus_total ?? game.plus_minus ?? 0) > 0 && 'text-save',
                        (game.plus_minus_total ?? game.plus_minus ?? 0) < 0 && 'text-goal'
                      )}>
                        {(game.plus_minus_total ?? game.plus_minus ?? 0) > 0 ? '+' : ''}{(game.plus_minus_total ?? game.plus_minus ?? 0)}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </CollapsibleSection>
      )}
      
      {/* Game Log Table - Goalie Stats */}
      {hasPlayedGoalie && (() => {
        // Fetch goalie game stats for this season
        // This would need to be passed as a prop or fetched in the parent
        // For now, we'll show a message if goalie stats aren't available
        return null // Placeholder - goalie game log would need to be fetched separately
      })()}
    </div>
  )
}
