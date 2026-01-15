// src/app/(dashboard)/players/[playerId]/trends/page.tsx
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getPlayerById, getPlayerGameLog } from '@/lib/supabase/queries/players'
import { getTeamById } from '@/lib/supabase/queries/teams'
import { createClient } from '@/lib/supabase/server'
import { ArrowLeft, TrendingUp, Activity, Target, BarChart3, Zap, Calendar } from 'lucide-react'
import { PlayerPhoto } from '@/components/players/player-photo'
import { TeamLogo } from '@/components/teams/team-logo'
import { TrendLineChart } from '@/components/charts/trend-line-chart'
import { cn } from '@/lib/utils'

export const revalidate = 300

export async function generateMetadata({ params }: { params: Promise<{ playerId: string }> }) {
  const { playerId } = await params
  const player = await getPlayerById(playerId).catch(() => null)
  return {
    title: `${player?.player_name || 'Player'} Trends | BenchSight`,
    description: `Performance trends and analytics for ${player?.player_name || 'player'}`,
  }
}

export default async function PlayerTrendsPage({ 
  params 
}: { 
  params: Promise<{ playerId: string }> 
}) {
  const { playerId } = await params
  const supabase = await createClient()
  
  // Fetch player and game log
  const [player, gameLog] = await Promise.all([
    getPlayerById(playerId).catch(() => null),
    getPlayerGameLog(playerId, 100).catch(() => [])
  ])
  
  if (!player) {
    notFound()
  }
  
  // Get team info
  const team = player.team_id ? await getTeamById(player.team_id).catch(() => null) : null
  
  // Sort game log by date (most recent first, then reverse for chronological)
  const sortedGameLog = [...gameLog].sort((a, b) => {
    const dateA = a.date ? new Date(a.date).getTime() : 0
    const dateB = b.date ? new Date(b.date).getTime() : 0
    return dateA - dateB
  })
  
  // Calculate rolling averages (5-game and 10-game)
  const calculateRollingAverage = (data: any[], key: string, window: number) => {
    return data.map((_, index) => {
      const start = Math.max(0, index - window + 1)
      const windowData = data.slice(start, index + 1)
      const sum = windowData.reduce((acc, item) => acc + (Number(item[key]) || 0), 0)
      return windowData.length > 0 ? (sum / windowData.length) : 0
    })
  }
  
  // Prepare trend data
  const trendData = sortedGameLog.map((game, index) => {
    const gameNumber = index + 1
    return {
      gameNumber,
      gameId: game.game_id,
      date: game.date,
      goals: game.goals || 0,
      assists: game.assists || 0,
      points: game.points || 0,
      shots: game.shots || game.shots_on_goal || 0,
      toi: game.toi_seconds ? game.toi_seconds / 60 : 0, // Convert to minutes
      plusMinus: game.plus_minus || 0,
      cfPct: game.cf_pct || 0,
      xg: game.xg_for || 0,
      war: game.war || 0,
      gameScore: game.game_score || 0,
      opponent: game.opponent_team_name || 'Unknown',
      result: game.goals > 0 || game.assists > 0 ? 'productive' : 'quiet'
    }
  })
  
  // Calculate rolling averages
  const goals5Game = calculateRollingAverage(trendData, 'goals', 5)
  const goals10Game = calculateRollingAverage(trendData, 'goals', 10)
  const points5Game = calculateRollingAverage(trendData, 'points', 5)
  const points10Game = calculateRollingAverage(trendData, 'points', 10)
  const xg5Game = calculateRollingAverage(trendData, 'xg', 5)
  const xg10Game = calculateRollingAverage(trendData, 'xg', 10)
  const war5Game = calculateRollingAverage(trendData, 'war', 5)
  const war10Game = calculateRollingAverage(trendData, 'war', 10)
  
  // Add rolling averages to trend data
  const trendDataWithRolling = trendData.map((game, index) => ({
    ...game,
    goals5Game: goals5Game[index],
    goals10Game: goals10Game[index],
    points5Game: points5Game[index],
    points10Game: points10Game[index],
    xg5Game: xg5Game[index],
    xg10Game: xg10Game[index],
    war5Game: war5Game[index],
    war10Game: war10Game[index],
  }))
  
  // Calculate streaks
  const calculateStreak = (data: any[], key: string, threshold: number, direction: 'above' | 'below') => {
    let currentStreak = 0
    let maxStreak = 0
    let currentStreakStart = 0
    let maxStreakStart = 0
    
    for (let i = 0; i < data.length; i++) {
      const value = Number(data[i][key]) || 0
      const meetsThreshold = direction === 'above' ? value >= threshold : value <= threshold
      
      if (meetsThreshold) {
        currentStreak++
        if (currentStreak === 1) {
          currentStreakStart = i
        }
        if (currentStreak > maxStreak) {
          maxStreak = currentStreak
          maxStreakStart = currentStreakStart
        }
      } else {
        currentStreak = 0
      }
    }
    
    return {
      length: maxStreak,
      start: maxStreakStart,
      end: maxStreakStart + maxStreak - 1
    }
  }
  
  const pointStreak = calculateStreak(trendData, 'points', 1, 'above')
  const goalStreak = calculateStreak(trendData, 'goals', 1, 'above')
  const coldStreak = calculateStreak(trendData, 'points', 0, 'below')
  
  // Calculate season totals and averages
  const totalGames = sortedGameLog.length
  const totalGoals = sortedGameLog.reduce((sum, game) => sum + (game.goals || 0), 0)
  const totalAssists = sortedGameLog.reduce((sum, game) => sum + (game.assists || 0), 0)
  const totalPoints = sortedGameLog.reduce((sum, game) => sum + (game.points || 0), 0)
  const avgGoals = totalGames > 0 ? (totalGoals / totalGames) : 0
  const avgAssists = totalGames > 0 ? (totalAssists / totalGames) : 0
  const avgPoints = totalGames > 0 ? (totalPoints / totalGames) : 0
  
  // Recent form (last 10 games)
  const recentGames = sortedGameLog.slice(-10)
  const recentGoals = recentGames.reduce((sum, game) => sum + (game.goals || 0), 0)
  const recentAssists = recentGames.reduce((sum, game) => sum + (game.assists || 0), 0)
  const recentPoints = recentGames.reduce((sum, game) => sum + (game.points || 0), 0)
  const recentAvgGoals = recentGames.length > 0 ? (recentGoals / recentGames.length) : 0
  const recentAvgPoints = recentGames.length > 0 ? (recentPoints / recentGames.length) : 0
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link 
            href={`/players/${playerId}`}
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div className="flex items-center gap-4">
            <PlayerPhoto
              src={player.player_photo || null}
              name={player.player_name || ''}
              size="md"
            />
            <div>
              <h1 className="font-display text-2xl font-bold tracking-wider uppercase flex items-center gap-3">
                <span className="w-1 h-6 bg-primary rounded" />
                {player.player_name || player.player_full_name || 'Player'} - Trends
              </h1>
              <p className="text-sm text-muted-foreground mt-2 ml-4">
                Performance trends and rolling averages
              </p>
            </div>
          </div>
        </div>
        {team && (
          <TeamLogo
            src={team.team_logo || null}
            name={team.team_name || ''}
            abbrev={team.team_cd}
            primaryColor={team.primary_color || team.team_color1}
            secondaryColor={team.team_color2}
            size="sm"
          />
        )}
      </div>
      
      {/* Summary Stats */}
      <div className="grid md:grid-cols-4 gap-4">
        <div className="bg-card rounded-xl border border-border p-4">
          <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Games Played</div>
          <div className="font-mono text-2xl font-bold text-foreground">{totalGames}</div>
          <div className="text-xs text-muted-foreground mt-1">
            {recentGames.length} recent games
          </div>
        </div>
        <div className="bg-card rounded-xl border border-border p-4">
          <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Avg Goals/Game</div>
          <div className="font-mono text-2xl font-bold text-goal">
            {avgGoals.toFixed(2)}
          </div>
          <div className={cn(
            "text-xs mt-1",
            recentAvgGoals > avgGoals ? "text-save" : recentAvgGoals < avgGoals ? "text-goal" : "text-muted-foreground"
          )}>
            Recent: {recentAvgGoals.toFixed(2)} {recentAvgGoals > avgGoals ? '↑' : recentAvgGoals < avgGoals ? '↓' : '→'}
          </div>
        </div>
        <div className="bg-card rounded-xl border border-border p-4">
          <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Avg Points/Game</div>
          <div className="font-mono text-2xl font-bold text-primary">
            {avgPoints.toFixed(2)}
          </div>
          <div className={cn(
            "text-xs mt-1",
            recentAvgPoints > avgPoints ? "text-save" : recentAvgPoints < avgPoints ? "text-goal" : "text-muted-foreground"
          )}>
            Recent: {recentAvgPoints.toFixed(2)} {recentAvgPoints > avgPoints ? '↑' : recentAvgPoints < avgPoints ? '↓' : '→'}
          </div>
        </div>
        <div className="bg-card rounded-xl border border-border p-4">
          <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Current Streak</div>
          <div className="font-mono text-2xl font-bold text-assist">
            {pointStreak.length > 0 ? `${pointStreak.length}G` : '0G'}
          </div>
          <div className="text-xs text-muted-foreground mt-1">
            Best: {pointStreak.length} games
          </div>
        </div>
      </div>
      
      {/* Goals Trend Chart */}
      {trendDataWithRolling.length > 0 && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Target className="w-4 h-4" />
              Goals Per Game Trend
            </h2>
          </div>
          <div className="p-6">
            <TrendLineChart
              data={trendDataWithRolling}
              xAxisKey="gameNumber"
              dataKeys={[
                { key: 'goals', name: 'Goals', color: 'hsl(var(--goal))', strokeWidth: 2 },
                { key: 'goals5Game', name: '5-Game Avg', color: 'hsl(var(--primary))', strokeWidth: 2, strokeDasharray: '5 5' },
                { key: 'goals10Game', name: '10-Game Avg', color: 'hsl(var(--muted-foreground))', strokeWidth: 2, strokeDasharray: '3 3' },
              ]}
              height={300}
            />
          </div>
        </div>
      )}
      
      {/* Points Trend Chart */}
      {trendDataWithRolling.length > 0 && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Points Per Game Trend
            </h2>
          </div>
          <div className="p-6">
            <TrendLineChart
              data={trendDataWithRolling}
              xAxisKey="gameNumber"
              dataKeys={[
                { key: 'points', name: 'Points', color: 'hsl(var(--primary))', strokeWidth: 2 },
                { key: 'points5Game', name: '5-Game Avg', color: 'hsl(var(--assist))', strokeWidth: 2, strokeDasharray: '5 5' },
                { key: 'points10Game', name: '10-Game Avg', color: 'hsl(var(--muted-foreground))', strokeWidth: 2, strokeDasharray: '3 3' },
              ]}
              height={300}
            />
          </div>
        </div>
      )}
      
      {/* xG Trend Chart */}
      {trendDataWithRolling.length > 0 && trendDataWithRolling.some(d => d.xg > 0) && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              Expected Goals (xG) Trend
            </h2>
          </div>
          <div className="p-6">
            <TrendLineChart
              data={trendDataWithRolling}
              xAxisKey="gameNumber"
              dataKeys={[
                { key: 'xg', name: 'xG', color: 'hsl(var(--goal))', strokeWidth: 2 },
                { key: 'xg5Game', name: '5-Game Avg', color: 'hsl(var(--primary))', strokeWidth: 2, strokeDasharray: '5 5' },
                { key: 'xg10Game', name: '10-Game Avg', color: 'hsl(var(--muted-foreground))', strokeWidth: 2, strokeDasharray: '3 3' },
              ]}
              height={300}
            />
          </div>
        </div>
      )}
      
      {/* WAR Trend Chart */}
      {trendDataWithRolling.length > 0 && trendDataWithRolling.some(d => d.war !== 0) && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Zap className="w-4 h-4" />
              WAR (Wins Above Replacement) Trend
            </h2>
          </div>
          <div className="p-6">
            <TrendLineChart
              data={trendDataWithRolling}
              xAxisKey="gameNumber"
              dataKeys={[
                { key: 'war', name: 'WAR', color: 'hsl(var(--assist))', strokeWidth: 2 },
                { key: 'war5Game', name: '5-Game Avg', color: 'hsl(var(--primary))', strokeWidth: 2, strokeDasharray: '5 5' },
                { key: 'war10Game', name: '10-Game Avg', color: 'hsl(var(--muted-foreground))', strokeWidth: 2, strokeDasharray: '3 3' },
              ]}
              height={300}
            />
          </div>
        </div>
      )}
      
      {/* Advanced Metrics Trend */}
      {trendDataWithRolling.length > 0 && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Activity className="w-4 h-4" />
              Advanced Metrics Trend
            </h2>
          </div>
          <div className="p-6">
            <TrendLineChart
              data={trendDataWithRolling}
              xAxisKey="gameNumber"
              dataKeys={[
                { key: 'cfPct', name: 'CF%', color: 'hsl(var(--primary))', strokeWidth: 2 },
                { key: 'plusMinus', name: '+/-', color: 'hsl(var(--assist))', strokeWidth: 2 },
                { key: 'gameScore', name: 'Game Score', color: 'hsl(var(--goal))', strokeWidth: 2 },
              ]}
              height={300}
            />
          </div>
        </div>
      )}
      
      {/* Streak Analysis */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="px-4 py-3 bg-accent border-b border-border">
          <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
            <Calendar className="w-4 h-4" />
            Streak Analysis
          </h2>
        </div>
        <div className="p-6">
          <div className="grid md:grid-cols-3 gap-4">
            <div className="bg-muted/30 rounded-lg p-4">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-2">Point Streak</div>
              <div className="font-mono text-xl font-bold text-primary">
                {pointStreak.length} games
              </div>
              {pointStreak.length > 0 && (
                <div className="text-xs text-muted-foreground mt-1">
                  Games {pointStreak.start + 1}-{pointStreak.end + 1}
                </div>
              )}
            </div>
            <div className="bg-muted/30 rounded-lg p-4">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-2">Goal Streak</div>
              <div className="font-mono text-xl font-bold text-goal">
                {goalStreak.length} games
              </div>
              {goalStreak.length > 0 && (
                <div className="text-xs text-muted-foreground mt-1">
                  Games {goalStreak.start + 1}-{goalStreak.end + 1}
                </div>
              )}
            </div>
            <div className="bg-muted/30 rounded-lg p-4">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-2">Scoreless Streak</div>
              <div className="font-mono text-xl font-bold text-muted-foreground">
                {coldStreak.length} games
              </div>
              {coldStreak.length > 0 && (
                <div className="text-xs text-muted-foreground mt-1">
                  Games {coldStreak.start + 1}-{coldStreak.end + 1}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      
      {/* Recent Games Table */}
      {sortedGameLog.length > 0 && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Activity className="w-4 h-4" />
              Recent Games (Last 10)
            </h2>
          </div>
          <div className="p-6">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left py-2 font-mono text-xs text-muted-foreground uppercase">Game</th>
                    <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">G</th>
                    <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">A</th>
                    <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">P</th>
                    <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">+/-</th>
                    <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">CF%</th>
                    <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">xG</th>
                    <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">WAR</th>
                  </tr>
                </thead>
                <tbody>
                  {recentGames.reverse().map((game, index) => (
                    <tr key={game.game_id} className="border-b border-border/50 hover:bg-muted/30">
                      <td className="py-2">
                        <Link 
                          href={`/norad/players/${playerId}/games/${game.game_id}`}
                          className="text-foreground hover:text-primary transition-colors"
                        >
                          <div className="font-mono text-xs">
                            #{sortedGameLog.length - recentGames.length + index + 1}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            vs {game.opponent_team_name || 'Unknown'}
                          </div>
                        </Link>
                      </td>
                      <td className="text-right py-2 font-mono">{game.goals || 0}</td>
                      <td className="text-right py-2 font-mono">{game.assists || 0}</td>
                      <td className="text-right py-2 font-mono font-semibold text-primary">{game.points || 0}</td>
                      <td className={cn(
                        "text-right py-2 font-mono",
                        (game.plus_minus || 0) > 0 && "text-save",
                        (game.plus_minus || 0) < 0 && "text-goal"
                      )}>
                        {(game.plus_minus || 0) > 0 ? '+' : ''}{game.plus_minus || 0}
                      </td>
                      <td className="text-right py-2 font-mono">{game.cf_pct ? game.cf_pct.toFixed(1) : '-'}%</td>
                      <td className="text-right py-2 font-mono">{game.xg_for ? game.xg_for.toFixed(2) : '-'}</td>
                      <td className="text-right py-2 font-mono">{game.war ? game.war.toFixed(2) : '-'}</td>
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
