// src/app/(dashboard)/games/[gameId]/page.tsx
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getGameById, getGameBoxScore, getGameGoals } from '@/lib/supabase/queries/games'
import { ArrowLeft, Target, User } from 'lucide-react'
import { cn } from '@/lib/utils'

export const revalidate = 300

export async function generateMetadata({ params }: { params: Promise<{ gameId: string }> }) {
  const { gameId } = await params
  return {
    title: `Game ${gameId} | BenchSight`,
    description: `Box score and stats for game ${gameId}`,
  }
}

export default async function GameDetailPage({ 
  params 
}: { 
  params: Promise<{ gameId: string }> 
}) {
  const { gameId } = await params
  const gameIdNum = parseInt(gameId)
  
  if (isNaN(gameIdNum)) {
    notFound()
  }
  
  const [game, boxScore, goals] = await Promise.all([
    getGameById(gameIdNum),
    getGameBoxScore(gameIdNum),
    getGameGoals(gameIdNum)
  ])
  
  if (!game) {
    notFound()
  }
  
  // Separate players by team
  const homeTeamId = game.home_team_id
  const homePlayers = boxScore.players.filter(p => p.team_id === homeTeamId)
  const awayPlayers = boxScore.players.filter(p => p.team_id !== homeTeamId)
  
  const homeGoals = (game as any).home_total_goals ?? 0
  const awayGoals = (game as any).away_total_goals ?? 0
  
  return (
    <div className="space-y-6">
      {/* Back Link */}
      <Link 
        href="/games" 
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Games
      </Link>
      
      {/* Scoreboard */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="bg-gradient-to-r from-primary/10 via-transparent to-primary/10 p-6">
          <div className="flex items-center justify-between">
            {/* Away Team */}
            <div className="flex-1 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-2">Away</div>
              <div className="font-display text-lg font-semibold text-foreground mb-2">
                {(game as any).away_team_name ?? 'Away Team'}
              </div>
              <div className={cn(
                'font-display text-5xl font-bold',
                awayGoals > homeGoals ? 'text-save' : 'text-muted-foreground'
              )}>
                {awayGoals}
              </div>
            </div>
            
            <div className="px-8">
              <div className="text-2xl font-display font-bold text-muted-foreground">@</div>
            </div>
            
            {/* Home Team */}
            <div className="flex-1 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-2">Home</div>
              <div className="font-display text-lg font-semibold text-foreground mb-2">
                {(game as any).home_team_name ?? 'Home Team'}
              </div>
              <div className={cn(
                'font-display text-5xl font-bold',
                homeGoals > awayGoals ? 'text-save' : 'text-muted-foreground'
              )}>
                {homeGoals}
              </div>
            </div>
          </div>
        </div>
        
        <div className="px-6 py-3 bg-accent/50 border-t border-border text-center">
          <span className="text-xs font-mono text-muted-foreground uppercase">Final</span>
        </div>
      </div>
      
      {/* Scoring Summary */}
      {goals.length > 0 && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Target className="w-4 h-4 text-goal" />
              Scoring Summary
            </h2>
          </div>
          <div className="divide-y divide-border">
            {goals.map((goal, index) => {
              const period = goal.period
              const minutes = Math.floor((goal.time_seconds ?? 0) / 60)
              const seconds = (goal.time_seconds ?? 0) % 60
              const timeStr = `${minutes}:${seconds.toString().padStart(2, '0')}`
              
              return (
                <div key={index} className="p-4 flex items-center gap-4">
                  <div className="w-16 text-center">
                    <span className="text-xs font-mono text-muted-foreground uppercase">P{period}</span>
                    <div className="font-mono text-sm text-foreground">{timeStr}</div>
                  </div>
                  <div className="flex-1">
                    <div className="font-display text-sm font-semibold text-foreground">
                      {goal.event_player_1 ?? 'Unknown'}
                    </div>
                    {goal.event_player_2 && (
                      <div className="text-xs text-muted-foreground">Assist: {goal.event_player_2}</div>
                    )}
                  </div>
                  <div className="text-xs font-mono text-muted-foreground">{goal.team_id}</div>
                </div>
              )
            })}
          </div>
        </div>
      )}
      
      {/* Box Score Tables */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Away Team Box Score */}
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <User className="w-4 h-4" />
              {(game as any).away_team_name ?? 'Away'} Box Score
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-accent/50">
                  <th className="px-3 py-2 text-left font-display text-xs text-muted-foreground">Player</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-goal">G</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-assist">A</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-primary">P</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">S</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">+/-</th>
                </tr>
              </thead>
              <tbody>
                {awayPlayers.slice(0, 15).map((player) => (
                  <tr key={player.player_game_key} className="border-b border-border hover:bg-muted/50">
                    <td className="px-3 py-2">
                      <Link href={`/players/${player.player_id}`} className="text-foreground hover:text-primary">
                        {player.player_name}
                      </Link>
                    </td>
                    <td className="px-2 py-2 text-center font-mono text-goal">{player.goals}</td>
                    <td className="px-2 py-2 text-center font-mono text-assist">{player.assists}</td>
                    <td className="px-2 py-2 text-center font-mono font-semibold">{player.points}</td>
                    <td className="px-2 py-2 text-center font-mono text-muted-foreground">{player.shots}</td>
                    <td className={cn(
                      'px-2 py-2 text-center font-mono',
                      player.plus_minus_total > 0 && 'text-save',
                      player.plus_minus_total < 0 && 'text-goal'
                    )}>
                      {player.plus_minus_total > 0 ? '+' : ''}{player.plus_minus_total}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        
        {/* Home Team Box Score */}
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <User className="w-4 h-4" />
              {(game as any).home_team_name ?? 'Home'} Box Score
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-accent/50">
                  <th className="px-3 py-2 text-left font-display text-xs text-muted-foreground">Player</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-goal">G</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-assist">A</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-primary">P</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">S</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">+/-</th>
                </tr>
              </thead>
              <tbody>
                {homePlayers.slice(0, 15).map((player) => (
                  <tr key={player.player_game_key} className="border-b border-border hover:bg-muted/50">
                    <td className="px-3 py-2">
                      <Link href={`/players/${player.player_id}`} className="text-foreground hover:text-primary">
                        {player.player_name}
                      </Link>
                    </td>
                    <td className="px-2 py-2 text-center font-mono text-goal">{player.goals}</td>
                    <td className="px-2 py-2 text-center font-mono text-assist">{player.assists}</td>
                    <td className="px-2 py-2 text-center font-mono font-semibold">{player.points}</td>
                    <td className="px-2 py-2 text-center font-mono text-muted-foreground">{player.shots}</td>
                    <td className={cn(
                      'px-2 py-2 text-center font-mono',
                      player.plus_minus_total > 0 && 'text-save',
                      player.plus_minus_total < 0 && 'text-goal'
                    )}>
                      {player.plus_minus_total > 0 ? '+' : ''}{player.plus_minus_total}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      
      {/* Goalie Stats */}
      {boxScore.goalies.length > 0 && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider">Goaltending</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-accent/50">
                  <th className="px-3 py-2 text-left font-display text-xs text-muted-foreground">Goalie</th>
                  <th className="px-3 py-2 text-left font-display text-xs text-muted-foreground">Team</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-save">Saves</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-goal">GA</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">Shots</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-primary">SV%</th>
                </tr>
              </thead>
              <tbody>
                {boxScore.goalies.map((goalie) => (
                  <tr key={goalie.goalie_game_key} className="border-b border-border hover:bg-muted/50">
                    <td className="px-3 py-2">
                      <Link href={`/players/${goalie.player_id}`} className="text-foreground hover:text-primary">
                        {goalie.player_name}
                      </Link>
                    </td>
                    <td className="px-3 py-2 text-muted-foreground">{goalie.team_name}</td>
                    <td className="px-2 py-2 text-center font-mono text-save font-semibold">{goalie.saves}</td>
                    <td className="px-2 py-2 text-center font-mono text-goal">{goalie.goals_against}</td>
                    <td className="px-2 py-2 text-center font-mono text-muted-foreground">{goalie.shots_against}</td>
                    <td className="px-2 py-2 text-center font-mono text-primary font-semibold">
                      {goalie.save_pct ? (goalie.save_pct * 100).toFixed(1) + '%' : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
