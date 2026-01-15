// src/app/(dashboard)/analytics/xg/page.tsx
import Link from 'next/link'
import { createClient } from '@/lib/supabase/server'
import { ArrowLeft, Target, TrendingUp, BarChart3, Zap, Activity } from 'lucide-react'
import { TrendLineChart } from '@/components/charts/trend-line-chart'
import { cn } from '@/lib/utils'
import { PlayerPhoto } from '@/components/players/player-photo'
import { TeamLogo } from '@/components/teams/team-logo'

export const revalidate = 300

export const metadata = {
  title: 'xG Analysis | BenchSight Analytics',
  description: 'Expected Goals (xG) analysis, leaders, and trends',
}

export default async function XGAnalysisPage() {
  const supabase = await createClient()
  
  // Get xG leaders from player season stats
  const { data: xgLeaders } = await supabase
    .from('fact_player_season_stats_basic')
    .select(`
      player_id,
      player_name,
      season,
      games_played,
      goals,
      xg_for,
      xg_adj,
      goals_above_expected,
      shooting_pct,
      xg_per_game
    `)
    .not('xg_for', 'is', null)
    .order('xg_for', { ascending: false })
    .limit(50)
  
  // Get players for photos
  const playerIds = [...new Set((xgLeaders || []).map(p => p.player_id).filter(Boolean))]
  const { data: playersData } = await supabase
    .from('dim_player')
    .select('player_id, player_name, player_full_name, player_image, team_id')
    .in('player_id', playerIds)
  
  const playersMap = new Map(
    (playersData || []).map(p => [String(p.player_id), p])
  )
  
  // Get teams for logos
  const teamIds = [...new Set((playersData || []).map(p => p.team_id).filter(Boolean))]
  const { data: teamsData } = await supabase
    .from('dim_team')
    .select('team_id, team_name, team_logo, team_cd, primary_color, team_color1')
    .in('team_id', teamIds)
  
  const teamsMap = new Map(
    (teamsData || []).map(t => [String(t.team_id), t])
  )
  
  // Calculate goals above expected
  const leadersWithGAE = (xgLeaders || []).map(leader => {
    const player = playersMap.get(String(leader.player_id))
    const team = player ? teamsMap.get(String(player.team_id)) : null
    const xg = Number(leader.xg_for || 0)
    const goals = Number(leader.goals || 0)
    const goalsAboveExpected = goals - xg
    const xgPerGame = leader.games_played > 0 ? (xg / leader.games_played) : 0
    const goalsPerGame = leader.games_played > 0 ? (goals / leader.games_played) : 0
    
    return {
      ...leader,
      player,
      team,
      xg,
      goals,
      goalsAboveExpected,
      xgPerGame,
      goalsPerGame,
      shootingPct: Number(leader.shooting_pct || 0),
      gamesPlayed: Number(leader.games_played || 0)
    }
  }).sort((a, b) => b.xg - a.xg)
  
  // Get top performers by goals above expected
  const topGAE = [...leadersWithGAE]
    .sort((a, b) => b.goalsAboveExpected - a.goalsAboveExpected)
    .slice(0, 10)
  
  // Get top performers by xG per game (min 10 games)
  const topXGPerGame = [...leadersWithGAE]
    .filter(p => p.gamesPlayed >= 10)
    .sort((a, b) => b.xgPerGame - a.xgPerGame)
    .slice(0, 10)
  
  // Aggregate xG trends by season
  const { data: seasonXG } = await supabase
    .from('fact_player_season_stats_basic')
    .select('season, xg_for, goals, games_played')
    .not('xg_for', 'is', null)
    .order('season', { ascending: true })
  
  const xgTrendsBySeason = (seasonXG || []).reduce((acc: any, stat: any) => {
    const season = stat.season || 'Unknown'
    if (!acc[season]) {
      acc[season] = {
        season,
        totalXG: 0,
        totalGoals: 0,
        totalGames: 0,
        playerCount: 0
      }
    }
    acc[season].totalXG += Number(stat.xg_for || 0)
    acc[season].totalGoals += Number(stat.goals || 0)
    acc[season].totalGames += Number(stat.games_played || 0)
    acc[season].playerCount += 1
    return acc
  }, {})
  
  const xgTrendsData = Object.values(xgTrendsBySeason)
    .map((stat: any) => ({
      season: stat.season,
      avgXG: stat.playerCount > 0 ? (stat.totalXG / stat.playerCount) : 0,
      avgGoals: stat.playerCount > 0 ? (stat.totalGoals / stat.playerCount) : 0,
      avgXGPerGame: stat.totalGames > 0 ? (stat.totalXG / stat.totalGames) : 0,
      avgGoalsPerGame: stat.totalGames > 0 ? (stat.totalGoals / stat.totalGames) : 0,
    }))
    .sort((a, b) => String(a.season).localeCompare(String(b.season)))
  
  return (
    <div className="space-y-6">
      {/* Back Link */}
      <Link 
        href="/norad/analytics/overview" 
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Analytics
      </Link>
      
      {/* Header */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="px-4 py-3 bg-accent border-b border-border">
          <h1 className="font-display text-lg font-semibold uppercase tracking-wider flex items-center gap-2">
            <Target className="w-5 h-5" />
            Expected Goals (xG) Analysis
          </h1>
        </div>
        <div className="p-6">
          <p className="text-sm text-muted-foreground mb-6">
            Expected Goals (xG) measures the quality of scoring chances. Players with high xG create more dangerous opportunities, 
            while Goals Above Expected (GAE) shows who's finishing better than expected.
          </p>
          
          {/* Summary Stats */}
          <div className="grid md:grid-cols-4 gap-4 mb-6">
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Total xG</div>
              <div className="font-mono text-2xl font-bold text-foreground">
                {leadersWithGAE.reduce((sum, p) => sum + p.xg, 0).toFixed(0)}
              </div>
            </div>
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Total Goals</div>
              <div className="font-mono text-2xl font-bold text-goal">
                {leadersWithGAE.reduce((sum, p) => sum + p.goals, 0).toFixed(0)}
              </div>
            </div>
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Avg xG/Game</div>
              <div className="font-mono text-2xl font-bold text-primary">
                {leadersWithGAE.length > 0 
                  ? (leadersWithGAE.reduce((sum, p) => sum + p.xgPerGame, 0) / leadersWithGAE.length).toFixed(2)
                  : '0.00'}
              </div>
            </div>
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Total GAE</div>
              <div className="font-mono text-2xl font-bold text-assist">
                {leadersWithGAE.reduce((sum, p) => sum + p.goalsAboveExpected, 0).toFixed(0)}
              </div>
            </div>
          </div>
          
          {/* xG Trends Chart */}
          {xgTrendsData.length > 0 && (
            <div className="mb-6">
              <div className="bg-card rounded-xl border border-border overflow-hidden">
                <div className="px-4 py-3 bg-accent border-b border-border">
                  <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                    <TrendingUp className="w-4 h-4" />
                    xG Trends by Season
                  </h2>
                </div>
                <div className="p-6">
                  <TrendLineChart
                    data={xgTrendsData}
                    xAxisKey="season"
                    dataKeys={[
                      { key: 'avgXG', name: 'Avg xG', color: 'hsl(var(--primary))', strokeWidth: 2 },
                      { key: 'avgGoals', name: 'Avg Goals', color: 'hsl(var(--goal))', strokeWidth: 2 },
                    ]}
                    height={300}
                  />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* xG Leaders Table */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="px-4 py-3 bg-accent border-b border-border">
          <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
            <BarChart3 className="w-4 h-4" />
            xG Leaders
          </h2>
        </div>
        <div className="p-6">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-2 font-mono text-xs text-muted-foreground uppercase">Rank</th>
                  <th className="text-left py-2 font-mono text-xs text-muted-foreground uppercase">Player</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">GP</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">Goals</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">xG</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">GAE</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">xG/G</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">G/G</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">SH%</th>
                </tr>
              </thead>
              <tbody>
                {leadersWithGAE.slice(0, 25).map((leader, index) => (
                  <tr key={leader.player_id} className="border-b border-border/50 hover:bg-muted/30">
                    <td className="py-3 font-mono text-xs text-muted-foreground">#{index + 1}</td>
                    <td className="py-3">
                      <Link 
                        href={`/players/${leader.player_id}`}
                        className="flex items-center gap-2 text-foreground hover:text-primary transition-colors"
                      >
                        {leader.player && (
                          <PlayerPhoto
                            src={leader.player.player_image || null}
                            name={leader.player.player_name || ''}
                            size="xs"
                          />
                        )}
                        <span className="font-semibold">
                          {leader.player_name || leader.player?.player_full_name || 'Unknown'}
                        </span>
                        {leader.team && (
                          <TeamLogo
                            src={leader.team.team_logo || null}
                            name={leader.team.team_name || ''}
                            abbrev={leader.team.team_cd}
                            size="xs"
                            showGradient={false}
                          />
                        )}
                      </Link>
                    </td>
                    <td className="text-right py-3 font-mono">{leader.gamesPlayed}</td>
                    <td className="text-right py-3 font-mono font-semibold text-goal">{leader.goals}</td>
                    <td className="text-right py-3 font-mono text-primary">{leader.xg.toFixed(2)}</td>
                    <td className={cn(
                      "text-right py-3 font-mono font-semibold",
                      leader.goalsAboveExpected > 0 && "text-save",
                      leader.goalsAboveExpected < 0 && "text-goal"
                    )}>
                      {leader.goalsAboveExpected > 0 ? '+' : ''}{leader.goalsAboveExpected.toFixed(2)}
                    </td>
                    <td className="text-right py-3 font-mono">{leader.xgPerGame.toFixed(2)}</td>
                    <td className="text-right py-3 font-mono">{leader.goalsPerGame.toFixed(2)}</td>
                    <td className="text-right py-3 font-mono">
                      {leader.shootingPct > 0 ? (leader.shootingPct * 100).toFixed(1) : '-'}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      
      {/* Goals Above Expected Leaders */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Zap className="w-4 h-4" />
              Top Goals Above Expected
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {topGAE.map((player, index) => (
                <Link
                  key={player.player_id}
                  href={`/players/${player.player_id}`}
                  className="flex items-center justify-between p-3 bg-muted/30 rounded-lg hover:bg-muted/50 transition-colors group"
                >
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-xs text-muted-foreground w-6">#{index + 1}</span>
                    {player.player && (
                      <PlayerPhoto
                        src={player.player.player_image || null}
                        name={player.player.player_name || ''}
                        size="xs"
                      />
                    )}
                    <div>
                      <div className="font-semibold text-foreground group-hover:text-primary transition-colors">
                        {player.player_name || player.player?.player_full_name || 'Unknown'}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {player.goals}G, {player.xg.toFixed(1)}xG
                      </div>
                    </div>
                  </div>
                  <div className={cn(
                    "font-mono font-bold text-lg",
                    player.goalsAboveExpected > 0 && "text-save",
                    player.goalsAboveExpected < 0 && "text-goal"
                  )}>
                    {player.goalsAboveExpected > 0 ? '+' : ''}{player.goalsAboveExpected.toFixed(1)}
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
        
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Activity className="w-4 h-4" />
              Top xG Per Game (Min 10 GP)
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {topXGPerGame.map((player, index) => (
                <Link
                  key={player.player_id}
                  href={`/players/${player.player_id}`}
                  className="flex items-center justify-between p-3 bg-muted/30 rounded-lg hover:bg-muted/50 transition-colors group"
                >
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-xs text-muted-foreground w-6">#{index + 1}</span>
                    {player.player && (
                      <PlayerPhoto
                        src={player.player.player_image || null}
                        name={player.player.player_name || ''}
                        size="xs"
                      />
                    )}
                    <div>
                      <div className="font-semibold text-foreground group-hover:text-primary transition-colors">
                        {player.player_name || player.player?.player_full_name || 'Unknown'}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {player.gamesPlayed} GP
                      </div>
                    </div>
                  </div>
                  <div className="font-mono font-bold text-lg text-primary">
                    {player.xgPerGame.toFixed(2)}
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
