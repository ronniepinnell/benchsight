// src/components/goalies/goalie-tabs/season-tab.tsx
import Link from 'next/link'
import { Clock } from 'lucide-react'
import { StatCard } from '@/components/players/stat-card'

interface SeasonTabProps {
  goalieId: string
  seasonId: string
  gameLog: any[]
  gameStats: any[]
}

export function SeasonTab({ gameLog, gameStats }: SeasonTabProps) {
  const formatPercent = (val: number | null | undefined) => {
    if (val === null || val === undefined) return '-'
    return Number(val).toFixed(1) + '%'
  }

  const formatDecimal = (val: number | null | undefined, decimals: number = 2) => {
    if (val === null || val === undefined) return '-'
    return Number(val).toFixed(decimals)
  }

  // Aggregate season stats
  const seasonTotals = gameStats.reduce((acc, game) => {
    acc.games += 1
    acc.wins += Number(game.wins || 0)
    acc.losses += Number(game.losses || 0)
    acc.saves += Number(game.saves || 0)
    acc.goalsAgainst += Number(game.goals_against || 0)
    acc.shotsAgainst += Number(game.shots_against || 0)
    acc.shutouts += Number(game.shutouts || 0)
    return acc
  }, {
    games: 0,
    wins: 0,
    losses: 0,
    saves: 0,
    goalsAgainst: 0,
    shotsAgainst: 0,
    shutouts: 0,
  })

  const savePct = seasonTotals.shotsAgainst > 0
    ? (seasonTotals.saves / seasonTotals.shotsAgainst) * 100
    : 0
  const gaa = seasonTotals.games > 0
    ? (seasonTotals.goalsAgainst / seasonTotals.games) * 60 / 20
    : 0

  return (
    <div className="space-y-6">
      {/* Season Summary */}
      <div className="grid md:grid-cols-4 gap-4">
        <StatCard label="Games Played" value={seasonTotals.games} />
        <StatCard label="Wins" value={seasonTotals.wins} className="text-save" />
        <StatCard label="Losses" value={seasonTotals.losses} className="text-goal" />
        <StatCard label="Shutouts" value={seasonTotals.shutouts} className="text-assist" />
        <StatCard label="Save %" value={formatPercent(savePct)} className="text-primary" />
        <StatCard label="GAA" value={formatDecimal(gaa)} />
        <StatCard label="Total Saves" value={seasonTotals.saves} />
        <StatCard label="Shots Against" value={seasonTotals.shotsAgainst} />
      </div>

      {/* Game Log */}
      {gameLog.length > 0 && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Clock className="w-4 h-4" />
              Game-by-Game Stats
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
                  {gameLog.map((game) => (
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
