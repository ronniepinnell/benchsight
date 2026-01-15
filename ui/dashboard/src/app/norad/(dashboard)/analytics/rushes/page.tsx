// src/app/(dashboard)/analytics/rushes/page.tsx
import Link from 'next/link'
import { createClient } from '@/lib/supabase/server'
import { ArrowLeft, Zap, Target, TrendingUp, Activity, BarChart3 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { PlayerPhoto } from '@/components/players/player-photo'
import { TeamLogo } from '@/components/teams/team-logo'
import { ExportButton } from '@/components/export/ExportButton'

export const revalidate = 300

export const metadata = {
  title: 'Rush Analysis | BenchSight Analytics',
  description: 'Rush leaders, success rates, and breakaway analysis',
}

export default async function RushAnalysisPage() {
  const supabase = await createClient()
  
  // Get rush stats from player game stats
  const { data: playerStats } = await supabase
    .from('fact_player_game_stats')
    .select(`
      player_id,
      player_name,
      game_id,
      rush_shots,
      rush_goals,
      rush_assists,
      rush_points,
      rush_xg,
      breakaway_goals,
      odd_man_rushes,
      rush_involvement,
      rush_off_success,
      rush_off_shot_generated,
      rush_off_goal_generated
    `)
    .not('rush_shots', 'is', null)
    .limit(1000)
  
  // Aggregate rush stats by player
  const playerRushStats = new Map<string, any>()
  
  if (playerStats) {
    for (const stat of playerStats) {
      const playerId = String(stat.player_id)
      if (!playerRushStats.has(playerId)) {
        playerRushStats.set(playerId, {
          player_id: playerId,
          player_name: stat.player_name,
          games: 0,
          rushShots: 0,
          rushGoals: 0,
          rushAssists: 0,
          rushPoints: 0,
          rushXG: 0,
          breakawayGoals: 0,
          oddManRushes: 0,
          rushInvolvement: 0,
          rushOffSuccess: 0,
          rushOffShotGenerated: 0,
          rushOffGoalGenerated: 0,
        })
      }
      
      const player = playerRushStats.get(playerId)!
      player.games += 1
      player.rushShots += Number(stat.rush_shots || 0)
      player.rushGoals += Number(stat.rush_goals || 0)
      player.rushAssists += Number(stat.rush_assists || 0)
      player.rushPoints += Number(stat.rush_points || 0)
      player.rushXG += Number(stat.rush_xg || 0)
      player.breakawayGoals += Number(stat.breakaway_goals || 0)
      player.oddManRushes += Number(stat.odd_man_rushes || 0)
      player.rushInvolvement += Number(stat.rush_involvement || 0)
      player.rushOffSuccess += Number(stat.rush_off_success || 0)
      player.rushOffShotGenerated += Number(stat.rush_off_shot_generated || 0)
      player.rushOffGoalGenerated += Number(stat.rush_off_goal_generated || 0)
    }
  }
  
  // Convert to array and calculate rates
  const aggregatedStats = Array.from(playerRushStats.values()).map(player => ({
    ...player,
    rushShotsPerGame: player.games > 0 ? (player.rushShots / player.games) : 0,
    rushGoalsPerGame: player.games > 0 ? (player.rushGoals / player.games) : 0,
    rushPointsPerGame: player.games > 0 ? (player.rushPoints / player.games) : 0,
    rushSuccessRate: player.rushInvolvement > 0 ? (player.rushOffSuccess / player.rushInvolvement) * 100 : 0,
    rushShotGenerationRate: player.rushInvolvement > 0 ? (player.rushOffShotGenerated / player.rushInvolvement) * 100 : 0,
    rushGoalGenerationRate: player.rushInvolvement > 0 ? (player.rushOffGoalGenerated / player.rushInvolvement) * 100 : 0,
  }))
  
  // Get players for photos
  const playerIds = aggregatedStats.map(p => p.player_id)
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
  
  // Add player and team data
  const statsWithPlayers = aggregatedStats.map(stat => {
    const player = playersMap.get(stat.player_id)
    const team = player ? teamsMap.get(String(player.team_id)) : null
    return { ...stat, player, team }
  })
  
  // Top performers
  const topRushInvolvement = [...statsWithPlayers]
    .sort((a, b) => b.rushInvolvement - a.rushInvolvement)
    .slice(0, 10)
  
  const topRushGoals = [...statsWithPlayers]
    .filter(p => p.rushGoals > 0)
    .sort((a, b) => b.rushGoals - a.rushGoals)
    .slice(0, 10)
  
  const topRushSuccessRate = [...statsWithPlayers]
    .filter(p => p.rushInvolvement >= 10)
    .sort((a, b) => b.rushSuccessRate - a.rushSuccessRate)
    .slice(0, 10)
  
  const topBreakawayGoals = [...statsWithPlayers]
    .filter(p => p.breakawayGoals > 0)
    .sort((a, b) => b.breakawayGoals - a.breakawayGoals)
    .slice(0, 10)
  
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
            <Zap className="w-5 h-5" />
            Rush Analysis
          </h1>
        </div>
        <div className="p-6">
          <p className="text-sm text-muted-foreground mb-6">
            Rushes are zone entries that lead to shots within 7 seconds. They represent high-speed transition opportunities 
            and are key indicators of offensive skill and speed.
          </p>
          
          {/* Summary Stats */}
          <div className="grid md:grid-cols-4 gap-4 mb-6">
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Total Rush Shots</div>
              <div className="font-mono text-2xl font-bold text-foreground">
                {statsWithPlayers.reduce((sum, p) => sum + p.rushShots, 0)}
              </div>
            </div>
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Total Rush Goals</div>
              <div className="font-mono text-2xl font-bold text-goal">
                {statsWithPlayers.reduce((sum, p) => sum + p.rushGoals, 0)}
              </div>
            </div>
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Total Breakaways</div>
              <div className="font-mono text-2xl font-bold text-primary">
                {statsWithPlayers.reduce((sum, p) => sum + p.breakawayGoals, 0)}
              </div>
            </div>
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Total Rush Involvement</div>
              <div className="font-mono text-2xl font-bold text-assist">
                {statsWithPlayers.reduce((sum, p) => sum + p.rushInvolvement, 0)}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Top Performers Grid */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Top Rush Involvement */}
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Activity className="w-4 h-4" />
              Top Rush Involvement
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {topRushInvolvement.map((player, index) => (
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
                        {player.rushGoals}G, {player.rushPoints}P
                      </div>
                    </div>
                  </div>
                  <div className="font-mono font-bold text-lg text-primary">
                    {player.rushInvolvement}
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
        
        {/* Top Rush Goals */}
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Target className="w-4 h-4" />
              Top Rush Goals
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {topRushGoals.map((player, index) => (
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
                        {player.rushShots} shots, {player.rushInvolvement} rushes
                      </div>
                    </div>
                  </div>
                  <div className="font-mono font-bold text-lg text-goal">
                    {player.rushGoals}
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
        
        {/* Top Rush Success Rate */}
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Top Rush Success Rate (Min 10 Rushes)
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {topRushSuccessRate.map((player, index) => (
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
                        {player.rushInvolvement} rushes
                      </div>
                    </div>
                  </div>
                  <div className="font-mono font-bold text-lg text-save">
                    {player.rushSuccessRate.toFixed(1)}%
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
        
        {/* Top Breakaway Goals */}
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Zap className="w-4 h-4" />
              Top Breakaway Goals
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {topBreakawayGoals.map((player, index) => (
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
                        {player.rushGoals} total rush goals
                      </div>
                    </div>
                  </div>
                  <div className="font-mono font-bold text-lg text-goal">
                    {player.breakawayGoals}
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>
      
      {/* Comprehensive Rush Stats Table */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="px-4 py-3 bg-accent border-b border-border flex items-center justify-between">
          <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
            <BarChart3 className="w-4 h-4" />
            Comprehensive Rush Statistics
          </h2>
          <ExportButton 
            data={statsWithPlayers
              .filter(p => p.rushInvolvement > 0)
              .sort((a, b) => b.rushInvolvement - a.rushInvolvement)
              .map(r => ({
                Player: r.player_name || r.player?.player_full_name || 'Unknown',
                Team: r.team?.team_name || '',
                GP: r.games,
                'Rush Involvement': r.rushInvolvement,
                'Rush Shots': r.rushShots,
                'Rush Goals': r.rushGoals,
                'Rush Assists': r.rushAssists,
                'Rush Points': r.rushPoints,
                'Rush Success %': r.rushSuccessRate > 0 ? r.rushSuccessRate.toFixed(1) + '%' : '-',
                'Breakaway Goals': r.breakawayGoals,
              }))}
            filename="rush_stats"
          />
        </div>
        <div className="p-6">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-2 font-mono text-xs text-muted-foreground uppercase">Player</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">GP</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">Rush Involve</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">Rush Shots</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">Rush Goals</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">Rush Points</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">Breakaways</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">Success Rate</th>
                </tr>
              </thead>
              <tbody>
                {statsWithPlayers
                  .filter(p => p.rushInvolvement > 0)
                  .sort((a, b) => b.rushInvolvement - a.rushInvolvement)
                  .slice(0, 50)
                  .map((stat) => (
                  <tr key={stat.player_id} className="border-b border-border/50 hover:bg-muted/30">
                    <td className="py-3">
                      <Link 
                        href={`/players/${stat.player_id}`}
                        className="flex items-center gap-2 text-foreground hover:text-primary transition-colors"
                      >
                        {stat.player && (
                          <PlayerPhoto
                            src={stat.player.player_image || null}
                            name={stat.player.player_name || ''}
                            size="xs"
                          />
                        )}
                        <span className="font-semibold">
                          {stat.player_name || stat.player?.player_full_name || 'Unknown'}
                        </span>
                        {stat.team && (
                          <TeamLogo
                            src={stat.team.team_logo || null}
                            name={stat.team.team_name || ''}
                            abbrev={stat.team.team_cd}
                            size="xs"
                            showGradient={false}
                          />
                        )}
                      </Link>
                    </td>
                    <td className="text-right py-3 font-mono">{stat.games}</td>
                    <td className="text-right py-3 font-mono font-semibold text-primary">{stat.rushInvolvement}</td>
                    <td className="text-right py-3 font-mono">{stat.rushShots}</td>
                    <td className="text-right py-3 font-mono text-goal">{stat.rushGoals}</td>
                    <td className="text-right py-3 font-mono">{stat.rushPoints}</td>
                    <td className="text-right py-3 font-mono">{stat.breakawayGoals}</td>
                    <td className="text-right py-3 font-mono">
                      {stat.rushSuccessRate > 0 ? stat.rushSuccessRate.toFixed(1) : '-'}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
