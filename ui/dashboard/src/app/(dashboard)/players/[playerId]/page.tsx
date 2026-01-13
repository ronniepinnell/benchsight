// src/app/(dashboard)/players/[playerId]/page.tsx
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getPlayerById, getPlayerCareerSummary, getPlayerGameLog } from '@/lib/supabase/queries/players'
import { ArrowLeft, Target, Sparkles, TrendingUp, Calendar } from 'lucide-react'
import { cn } from '@/lib/utils'

export const revalidate = 300

export async function generateMetadata({ params }: { params: Promise<{ playerId: string }> }) {
  const { playerId } = await params
  const player = await getPlayerById(parseInt(playerId))
  return {
    title: player ? `${player.player_name} | BenchSight` : 'Player | BenchSight',
    description: player ? `Statistics for ${player.player_name}` : 'Player statistics',
  }
}

export default async function PlayerDetailPage({ 
  params 
}: { 
  params: Promise<{ playerId: string }> 
}) {
  const { playerId } = await params
  const playerIdNum = parseInt(playerId)
  
  if (isNaN(playerIdNum)) {
    notFound()
  }
  
  const [player, career, gameLog] = await Promise.all([
    getPlayerById(playerIdNum),
    getPlayerCareerSummary(playerIdNum),
    getPlayerGameLog(playerIdNum, 10)
  ])
  
  if (!player) {
    notFound()
  }
  
  return (
    <div className="space-y-6">
      {/* Back Link */}
      <Link 
        href="/players" 
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Players
      </Link>
      
      {/* Player Header */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="bg-gradient-to-r from-primary/10 via-transparent to-primary/10 p-6">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="font-display text-3xl font-bold text-foreground">
                {player.player_name}
              </h1>
              <div className="flex items-center gap-4 mt-2">
                <span className="text-sm text-muted-foreground">
                  #{player.jersey_number}
                </span>
                <Link 
                  href={`/teams/${player.team_id}`}
                  className="text-sm text-primary hover:underline"
                >
                  {player.team_name}
                </Link>
                {player.position && (
                  <span className="text-xs font-mono bg-accent px-2 py-1 rounded uppercase">
                    {player.position}
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Season Stats */}
      {career && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="bg-card rounded-lg p-4 border border-border text-center">
            <div className="text-xs font-mono text-muted-foreground uppercase mb-1">GP</div>
            <div className="font-mono text-2xl font-bold text-foreground">{career.games_played}</div>
          </div>
          <div className="bg-card rounded-lg p-4 border border-border text-center">
            <div className="flex items-center justify-center gap-1 mb-1">
              <Target className="w-3 h-3 text-goal" />
              <span className="text-xs font-mono text-goal uppercase">Goals</span>
            </div>
            <div className="font-mono text-2xl font-bold text-goal">{career.goals}</div>
          </div>
          <div className="bg-card rounded-lg p-4 border border-border text-center">
            <div className="flex items-center justify-center gap-1 mb-1">
              <Sparkles className="w-3 h-3 text-assist" />
              <span className="text-xs font-mono text-assist uppercase">Assists</span>
            </div>
            <div className="font-mono text-2xl font-bold text-assist">{career.assists}</div>
          </div>
          <div className="bg-card rounded-lg p-4 border border-border text-center">
            <div className="flex items-center justify-center gap-1 mb-1">
              <TrendingUp className="w-3 h-3 text-primary" />
              <span className="text-xs font-mono text-primary uppercase">Points</span>
            </div>
            <div className="font-mono text-2xl font-bold text-primary">{career.points}</div>
          </div>
          <div className="bg-card rounded-lg p-4 border border-border text-center">
            <div className="text-xs font-mono text-muted-foreground uppercase mb-1">P/G</div>
            <div className="font-mono text-2xl font-bold text-foreground">
              {career.points_per_game?.toFixed(2) ?? '-'}
            </div>
          </div>
        </div>
      )}
      
      {/* Additional Stats */}
      {career && (
        <div className="grid md:grid-cols-2 gap-6">
          {/* Shooting Stats */}
          <div className="bg-card rounded-xl border border-border overflow-hidden">
            <div className="px-4 py-3 bg-accent border-b border-border">
              <h2 className="font-display text-sm font-semibold uppercase tracking-wider">
                Shooting Stats
              </h2>
            </div>
            <div className="p-4 grid grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase">Shots</div>
                <div className="font-mono text-xl font-bold text-shot">{career.shots ?? 0}</div>
              </div>
              <div className="text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase">SH%</div>
                <div className="font-mono text-xl font-bold text-foreground">
                  {career.shooting_pct ? (career.shooting_pct * 100).toFixed(1) + '%' : '-'}
                </div>
              </div>
              <div className="text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase">+/-</div>
                <div className={cn(
                  'font-mono text-xl font-bold',
                  (career.plus_minus ?? 0) > 0 && 'text-save',
                  (career.plus_minus ?? 0) < 0 && 'text-goal'
                )}>
                  {(career.plus_minus ?? 0) > 0 ? '+' : ''}{career.plus_minus ?? 0}
                </div>
              </div>
            </div>
          </div>
          
          {/* Discipline */}
          <div className="bg-card rounded-xl border border-border overflow-hidden">
            <div className="px-4 py-3 bg-accent border-b border-border">
              <h2 className="font-display text-sm font-semibold uppercase tracking-wider">
                Discipline
              </h2>
            </div>
            <div className="p-4 grid grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase">PIM</div>
                <div className="font-mono text-xl font-bold text-foreground">{career.pim ?? 0}</div>
              </div>
              <div className="text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase">Minor</div>
                <div className="font-mono text-xl font-bold text-foreground">{career.minor_penalties ?? 0}</div>
              </div>
              <div className="text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase">Major</div>
                <div className="font-mono text-xl font-bold text-goal">{career.major_penalties ?? 0}</div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Recent Games */}
      {gameLog.length > 0 && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border flex items-center justify-between">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              Recent Games
            </h2>
          </div>
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
                {gameLog.map((game) => {
                  const gameDate = game.date ? new Date(game.date).toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric',
                  }) : '-'
                  
                  return (
                    <tr key={game.player_game_key} className="border-b border-border hover:bg-muted/50">
                      <td className="px-4 py-2 font-mono text-xs text-muted-foreground">
                        <Link href={`/games/${game.game_id}`} className="hover:text-primary">
                          {gameDate}
                        </Link>
                      </td>
                      <td className="px-4 py-2 text-foreground">
                        {game.opponent_team_name ?? '-'}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-goal font-semibold">
                        {game.goals}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-assist">
                        {game.assists}
                      </td>
                      <td className="px-2 py-2 text-center font-mono font-bold text-primary">
                        {game.points}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-shot">
                        {game.shots}
                      </td>
                      <td className={cn(
                        'px-2 py-2 text-center font-mono',
                        (game.plus_minus_total ?? 0) > 0 && 'text-save',
                        (game.plus_minus_total ?? 0) < 0 && 'text-goal'
                      )}>
                        {(game.plus_minus_total ?? 0) > 0 ? '+' : ''}{game.plus_minus_total ?? 0}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
      
      {/* Actions */}
      <div className="flex gap-4">
        <Link
          href={`/players/compare?p1=${playerId}`}
          className="bg-card border border-border rounded-lg px-4 py-2 text-sm font-display hover:border-primary/50 transition-colors"
        >
          Compare with another player →
        </Link>
      </div>
    </div>
  )
}
