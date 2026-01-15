// src/app/(dashboard)/players/matchups/page.tsx
import Link from 'next/link'
import { createClient } from '@/lib/supabase/server'
import { getPlayerById } from '@/lib/supabase/queries/players'
import { ArrowLeft, Target, Users, TrendingUp } from 'lucide-react'
import { cn } from '@/lib/utils'
import { PlayerPhoto } from '@/components/players/player-photo'

export const revalidate = 300

export const metadata = {
  title: 'Player Matchups | BenchSight',
  description: 'Head-to-head player matchup analysis',
}

export default async function PlayerMatchupsPage({
  searchParams,
}: {
  searchParams: Promise<{ p1?: string; p2?: string }>
}) {
  const params = await searchParams
  const player1Id = params.p1
  const player2Id = params.p2
  
  const supabase = await createClient()
  
  if (!player1Id || !player2Id) {
    return (
      <div className="space-y-6">
        <Link 
          href="/norad/players"
          className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Players
        </Link>
        <div className="bg-card rounded-xl border border-border p-8 text-center">
          <h1 className="font-display text-2xl font-bold mb-4">Player Matchups</h1>
          <p className="text-muted-foreground mb-6">
            Compare two players head-to-head. Visit player profiles and use the comparison feature.
          </p>
          <Link
            href="/norad/players"
            className="inline-block bg-primary text-primary-foreground px-6 py-3 rounded-lg hover:bg-primary/90 transition-colors"
          >
            Browse Players
          </Link>
        </div>
      </div>
    )
  }
  
  // Get player data
  const [player1, player2] = await Promise.all([
    getPlayerById(player1Id).catch(() => null),
    getPlayerById(player2Id).catch(() => null),
  ])
  
  if (!player1 || !player2) {
    return (
      <div className="space-y-6">
        <p className="text-muted-foreground">One or both players not found.</p>
      </div>
    )
  }
  
  // Get games where both players played
  const { data: player1Games } = await supabase
    .from('fact_player_game_stats')
    .select('game_id')
    .eq('player_id', player1Id)
  
  const { data: player2Games } = await supabase
    .from('fact_player_game_stats')
    .select('game_id')
    .eq('player_id', player2Id)
  
  const player1GameIds = new Set((player1Games || []).map(g => g.game_id))
  const player2GameIds = new Set((player2Games || []).map(g => g.game_id))
  const commonGames = Array.from(player1GameIds).filter(id => player2GameIds.has(id))
  
  // Get stats for both players in common games
  const { data: p1Stats } = await supabase
    .from('fact_player_game_stats')
    .select('*')
    .eq('player_id', player1Id)
    .in('game_id', commonGames)
  
  const { data: p2Stats } = await supabase
    .from('fact_player_game_stats')
    .select('*')
    .eq('player_id', player2Id)
    .in('game_id', commonGames)
  
  // Aggregate stats
  const p1Totals = (p1Stats || []).reduce((acc, stat) => ({
    games: acc.games + 1,
    goals: acc.goals + (Number(stat.goals) || 0),
    assists: acc.assists + (Number(stat.assists) || 0),
    points: acc.points + (Number(stat.points) || 0),
    shots: acc.shots + (Number(stat.shots) || 0),
    toi: acc.toi + (Number(stat.toi_seconds) || 0),
  }), { games: 0, goals: 0, assists: 0, points: 0, shots: 0, toi: 0 })
  
  const p2Totals = (p2Stats || []).reduce((acc, stat) => ({
    games: acc.games + 1,
    goals: acc.goals + (Number(stat.goals) || 0),
    assists: acc.assists + (Number(stat.assists) || 0),
    points: acc.points + (Number(stat.points) || 0),
    shots: acc.shots + (Number(stat.shots) || 0),
    toi: acc.toi + (Number(stat.toi_seconds) || 0),
  }), { games: 0, goals: 0, assists: 0, points: 0, shots: 0, toi: 0 })
  
  return (
    <div className="space-y-6">
      <Link 
        href="/norad/players"
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Players
      </Link>
      
      {/* Header */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="px-4 py-3 bg-accent border-b border-border">
          <h1 className="font-display text-lg font-semibold uppercase tracking-wider flex items-center gap-2">
            <Target className="w-5 h-5" />
            Head-to-Head Matchup
          </h1>
        </div>
        <div className="p-6">
          <div className="grid md:grid-cols-2 gap-6">
            {/* Player 1 */}
            <Link
              href={`/players/${player1Id}`}
              className="bg-muted/30 rounded-lg p-6 hover:bg-muted/50 transition-colors"
            >
              <div className="flex items-center gap-4">
                <PlayerPhoto
                  src={player1.player_image || null}
                  name={player1.player_name || ''}
                  size="lg"
                />
                <div>
                  <div className="font-display text-xl font-bold text-foreground">
                    {player1.player_full_name || player1.player_name}
                  </div>
                  <div className="text-sm text-muted-foreground mt-1">
                    {p1Totals.games} common games
                  </div>
                </div>
              </div>
            </Link>
            
            {/* Player 2 */}
            <Link
              href={`/players/${player2Id}`}
              className="bg-muted/30 rounded-lg p-6 hover:bg-muted/50 transition-colors"
            >
              <div className="flex items-center gap-4">
                <PlayerPhoto
                  src={player2.player_image || null}
                  name={player2.player_name || ''}
                  size="lg"
                />
                <div>
                  <div className="font-display text-xl font-bold text-foreground">
                    {player2.player_full_name || player2.player_name}
                  </div>
                  <div className="text-sm text-muted-foreground mt-1">
                    {p2Totals.games} common games
                  </div>
                </div>
              </div>
            </Link>
          </div>
        </div>
      </div>
      
      {/* Comparison Table */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="px-4 py-3 bg-accent border-b border-border">
          <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
            <TrendingUp className="w-4 h-4" />
            Stat Comparison (Common Games)
          </h2>
        </div>
        <div className="p-6">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-2 font-mono text-xs text-muted-foreground uppercase">Stat</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">
                    {player1.player_name}
                  </th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">
                    {player2.player_name}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-border/50">
                  <td className="py-3 font-semibold">Games</td>
                  <td className="text-right py-3 font-mono">{p1Totals.games}</td>
                  <td className="text-right py-3 font-mono">{p2Totals.games}</td>
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 font-semibold">Goals</td>
                  <td className="text-right py-3 font-mono text-goal">{p1Totals.goals}</td>
                  <td className="text-right py-3 font-mono text-goal">{p2Totals.goals}</td>
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 font-semibold">Assists</td>
                  <td className="text-right py-3 font-mono text-assist">{p1Totals.assists}</td>
                  <td className="text-right py-3 font-mono text-assist">{p2Totals.assists}</td>
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 font-semibold">Points</td>
                  <td className="text-right py-3 font-mono font-semibold text-primary">{p1Totals.points}</td>
                  <td className="text-right py-3 font-mono font-semibold text-primary">{p2Totals.points}</td>
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 font-semibold">Shots</td>
                  <td className="text-right py-3 font-mono">{p1Totals.shots}</td>
                  <td className="text-right py-3 font-mono">{p2Totals.shots}</td>
                </tr>
                <tr>
                  <td className="py-3 font-semibold">TOI (min)</td>
                  <td className="text-right py-3 font-mono">{Math.round(p1Totals.toi / 60)}</td>
                  <td className="text-right py-3 font-mono">{Math.round(p2Totals.toi / 60)}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
