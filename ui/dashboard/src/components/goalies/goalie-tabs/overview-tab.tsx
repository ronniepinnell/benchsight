// src/components/goalies/goalie-tabs/overview-tab.tsx
import Link from 'next/link'
import { Clock, TrendingUp, Target } from 'lucide-react'
import { TrendLineChart } from '@/components/charts/trend-line-chart'
import { StatCard } from '@/components/players/stat-card'

interface OverviewTabProps {
  goalieId?: string
  gameLog: any[]
  currentStats: any
  trendData: any[]
}

export function OverviewTab({ gameLog, currentStats, trendData }: OverviewTabProps) {
  const formatPercent = (val: number | null | undefined) => {
    if (val === null || val === undefined) return '-'
    return Number(val).toFixed(1) + '%'
  }

  const formatDecimal = (val: number | null | undefined, decimals: number = 2) => {
    if (val === null || val === undefined) return '-'
    return Number(val).toFixed(decimals)
  }

  return (
    <div className="space-y-6">
      {/* Quick Stats */}
      <div className="grid md:grid-cols-6 gap-4">
        <StatCard 
          label="Games" 
          value={currentStats?.games_played || 0} 
        />
        <StatCard 
          label="Wins" 
          value={currentStats?.wins || 0}
          className="text-save"
        />
        <StatCard 
          label="Losses" 
          value={currentStats?.losses || 0}
          className="text-goal"
        />
        <StatCard 
          label="Save %" 
          value={currentStats?.save_pct ? formatPercent(currentStats.save_pct * 100) : '-'}
          className="text-primary"
        />
        <StatCard 
          label="GAA" 
          value={currentStats?.gaa ? formatDecimal(currentStats.gaa) : '-'}
        />
        <StatCard 
          label="Shutouts" 
          value={currentStats?.shutouts || 0}
          className="text-assist"
        />
      </div>

      {/* Save % Trend */}
      {trendData && trendData.length > 0 && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Save Percentage Trend
            </h2>
          </div>
          <div className="p-6">
            <TrendLineChart
              data={trendData}
              xAxisKey="gameNumber"
              dataKeys={[
                { key: 'savePct', name: 'Save %', color: 'hsl(var(--primary))', strokeWidth: 2 },
                { key: 'savePct5Game', name: '5-Game Avg', color: 'hsl(var(--assist))', strokeWidth: 2, strokeDasharray: '5 5' },
                { key: 'savePct10Game', name: '10-Game Avg', color: 'hsl(var(--muted-foreground))', strokeWidth: 2, strokeDasharray: '3 3' },
              ]}
              height={300}
            />
          </div>
        </div>
      )}
      
      {/* GAA Trend */}
      {trendData && trendData.length > 0 && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Target className="w-4 h-4" />
              Goals Against Average Trend
            </h2>
          </div>
          <div className="p-6">
            <TrendLineChart
              data={trendData}
              xAxisKey="gameNumber"
              dataKeys={[
                { key: 'gaa', name: 'GAA', color: 'hsl(var(--goal))', strokeWidth: 2 },
                { key: 'gaa5Game', name: '5-Game Avg', color: 'hsl(var(--primary))', strokeWidth: 2, strokeDasharray: '5 5' },
                { key: 'gaa10Game', name: '10-Game Avg', color: 'hsl(var(--muted-foreground))', strokeWidth: 2, strokeDasharray: '3 3' },
              ]}
              height={300}
            />
          </div>
        </div>
      )}

      {/* Recent Games */}
      {gameLog && gameLog.length > 0 && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Clock className="w-4 h-4" />
              Recent Games
            </h2>
          </div>
          <div className="p-6">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left py-2 font-mono text-xs text-muted-foreground uppercase">Date</th>
                    <th className="text-left py-2 font-mono text-xs text-muted-foreground uppercase">Opponent</th>
                    <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">Result</th>
                    <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">SV</th>
                    <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">GA</th>
                    <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">SV%</th>
                    <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">GAA</th>
                  </tr>
                </thead>
                <tbody>
                  {gameLog.slice(0, 10).map((game) => (
                    <tr key={game.game_id} className="border-b border-border/50 hover:bg-muted/30">
                      <td className="py-2">
                        <Link 
                          href={`/norad/games/${game.game_id}`}
                          className="text-foreground hover:text-primary transition-colors"
                        >
                          {game.date ? new Date(game.date).toLocaleDateString() : '-'}
                        </Link>
                      </td>
                      <td className="py-2">{game.opponent_team_name || 'Unknown'}</td>
                      <td className={`text-right py-2 font-mono font-semibold ${
                        game.win ? 'text-save' : game.loss ? 'text-goal' : 'text-muted-foreground'
                      }`}>
                        {game.win ? 'W' : game.loss ? 'L' : game.ot_loss ? 'OTL' : '-'}
                      </td>
                      <td className="text-right py-2 font-mono">{game.saves || 0}</td>
                      <td className="text-right py-2 font-mono">{game.goals_against || 0}</td>
                      <td className="text-right py-2 font-mono">
                        {game.save_pct ? formatPercent(game.save_pct * 100) : '-'}
                      </td>
                      <td className="text-right py-2 font-mono">
                        {game.gaa ? formatDecimal(game.gaa) : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
