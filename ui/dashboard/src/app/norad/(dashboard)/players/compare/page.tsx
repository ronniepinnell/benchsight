// src/app/(dashboard)/players/compare/page.tsx
import Link from 'next/link'
import { getPlayers, getPlayerComparison } from '@/lib/supabase/queries/players'
import { ArrowLeft, Users } from 'lucide-react'
import { cn } from '@/lib/utils'
import { PlayerSelectDropdown } from '@/components/players/player-select-dropdown'

export const revalidate = 300

export const metadata = {
  title: 'Compare Players | BenchSight',
  description: 'Compare NORAD Hockey League players side-by-side',
}

export default async function ComparePlayersPage({
  searchParams,
}: {
  searchParams: Promise<{ p1?: string; p2?: string }>
}) {
  const { p1, p2 } = await searchParams
  const player1Id = p1 ? parseInt(p1) : null
  const player2Id = p2 ? parseInt(p2) : null
  
  // Get all players for selection
  const allPlayers = await getPlayers()
  
  // Get comparison data if both players selected
  let comparisonData: any[] = []
  if (player1Id && player2Id) {
    comparisonData = await getPlayerComparison(player1Id, player2Id)
  }
  
  const player1 = comparisonData.find(p => p.player_id === player1Id)
  const player2 = comparisonData.find(p => p.player_id === player2Id)
  
  // Prepare serializable player data for client component
  const player1Data = player1 ? {
    player_name: player1.player_name || '',
    team_name: player1.team_name || '',
  } : null
  
  const player2Data = player2 ? {
    player_name: player2.player_name || '',
    team_name: player2.team_name || '',
  } : null
  
  const stats = [
    { key: 'games_played', label: 'GP', format: (v: number) => v },
    { key: 'goals', label: 'Goals', format: (v: number) => v, highlight: true, color: 'text-goal' },
    { key: 'assists', label: 'Assists', format: (v: number) => v, highlight: true, color: 'text-assist' },
    { key: 'points', label: 'Points', format: (v: number) => v, highlight: true, color: 'text-primary' },
    { key: 'points_per_game', label: 'P/G', format: (v: number) => v?.toFixed(2) ?? '-' },
    { key: 'shots', label: 'Shots', format: (v: number) => v },
    { key: 'shooting_pct', label: 'SH%', format: (v: number) => v ? (v * 100).toFixed(1) + '%' : '-' },
    { key: 'plus_minus', label: '+/-', format: (v: number) => (v > 0 ? '+' : '') + v },
    { key: 'pim', label: 'PIM', format: (v: number) => v },
  ]
  
  return (
    <div className="space-y-6">
      {/* Back Link */}
      <Link 
        href="/norad/players" 
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Players
      </Link>
      
      {/* Page Header */}
      <div>
        <h1 className="font-display text-2xl font-bold tracking-wider uppercase flex items-center gap-3">
          <span className="w-1 h-6 bg-shot rounded" />
          Compare Players
        </h1>
        <p className="text-sm text-muted-foreground mt-2 ml-4">
          Select two players to compare their statistics
        </p>
      </div>
      
      {/* Player Selection */}
      <div className="grid md:grid-cols-2 gap-6">
        <PlayerSelectDropdown
          players={allPlayers.map(p => ({
            player_id: p.player_id,
            player_name: p.player_name || p.player_full_name || '',
            team_name: p.team_name || '',
          }))}
          selectedPlayerId={p1}
          paramName="p1"
          label="Player 1"
          selectedPlayer={player1Data}
        />
        
        <PlayerSelectDropdown
          players={allPlayers.map(p => ({
            player_id: p.player_id,
            player_name: p.player_name || p.player_full_name || '',
            team_name: p.team_name || '',
          }))}
          selectedPlayerId={p2}
          paramName="p2"
          label="Player 2"
          selectedPlayer={player2Data}
        />
      </div>
      
      {/* Comparison Table */}
      {player1 && player2 && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider">
              Statistics Comparison
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="px-4 py-3 text-left font-display text-xs text-primary font-semibold w-1/3">
                    {player1.player_name}
                  </th>
                  <th className="px-4 py-3 text-center font-display text-xs text-muted-foreground uppercase">
                    Stat
                  </th>
                  <th className="px-4 py-3 text-right font-display text-xs text-shot font-semibold w-1/3">
                    {player2.player_name}
                  </th>
                </tr>
              </thead>
              <tbody>
                {stats.map((stat) => {
                  const val1 = player1[stat.key] ?? 0
                  const val2 = player2[stat.key] ?? 0
                  const winner = val1 > val2 ? 1 : val2 > val1 ? 2 : 0
                  
                  return (
                    <tr key={stat.key} className="border-b border-border">
                      <td className={cn(
                        'px-4 py-3 text-left font-mono text-lg',
                        winner === 1 ? (stat.color ?? 'text-save') + ' font-bold' : 'text-muted-foreground'
                      )}>
                        {stat.format(val1)}
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className="text-xs font-mono text-muted-foreground uppercase">
                          {stat.label}
                        </span>
                      </td>
                      <td className={cn(
                        'px-4 py-3 text-right font-mono text-lg',
                        winner === 2 ? (stat.color ?? 'text-save') + ' font-bold' : 'text-muted-foreground'
                      )}>
                        {stat.format(val2)}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
      
      {(!player1 || !player2) && (
        <div className="bg-card rounded-xl border border-border p-8 text-center">
          <Users className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">
            Select two players above to compare their statistics side-by-side
          </p>
        </div>
      )}
    </div>
  )
}
