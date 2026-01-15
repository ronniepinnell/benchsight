// src/app/(dashboard)/analytics/war/page.tsx
import Link from 'next/link'
import { createClient } from '@/lib/supabase/server'
import { ArrowLeft, TrendingUp, BarChart3, Zap, Activity, Award, Target } from 'lucide-react'
import { TrendLineChart } from '@/components/charts/trend-line-chart'
import { cn } from '@/lib/utils'
import { PlayerPhoto } from '@/components/players/player-photo'
import { TeamLogo } from '@/components/teams/team-logo'

export const revalidate = 300

export const metadata = {
  title: 'WAR/GAR Leaders | BenchSight Analytics',
  description: 'Wins Above Replacement (WAR) and Goals Above Replacement (GAR) leaders and analysis',
}

export default async function WARLeadersPage() {
  const supabase = await createClient()
  
  // Get WAR/GAR leaders from player season stats
  const { data: warLeaders } = await supabase
    .from('fact_player_season_stats_basic')
    .select(`
      player_id,
      player_name,
      season,
      season_id,
      games_played,
      goals,
      assists,
      points,
      war,
      gar,
      player_rating,
      cf_pct,
      xg_for,
      goals_above_expected
    `)
    .not('war', 'is', null)
    .order('war', { ascending: false })
    .limit(100)
  
  // Get players for photos
  const playerIds = [...new Set((warLeaders || []).map(p => p.player_id).filter(Boolean))]
  const { data: playersData } = await supabase
    .from('dim_player')
    .select('player_id, player_name, player_full_name, player_image, team_id, player_primary_position')
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
  
  // Process leaders with additional data
  const leadersWithData = (warLeaders || []).map(leader => {
    const player = playersMap.get(String(leader.player_id))
    const team = player ? teamsMap.get(String(player.team_id)) : null
    const war = Number(leader.war || 0)
    const gar = Number(leader.gar || 0)
    const gamesPlayed = Number(leader.games_played || 0)
    const warPerGame = gamesPlayed > 0 ? (war / gamesPlayed) : 0
    const garPerGame = gamesPlayed > 0 ? (gar / gamesPlayed) : 0
    
    return {
      ...leader,
      player,
      team,
      war,
      gar,
      warPerGame,
      garPerGame,
      gamesPlayed,
      points: Number(leader.points || 0),
      goals: Number(leader.goals || 0),
      assists: Number(leader.assists || 0),
      playerRating: Number(leader.player_rating || 0),
      cfPct: Number(leader.cf_pct || 0),
      xgFor: Number(leader.xg_for || 0),
      goalsAboveExpected: Number(leader.goals_above_expected || 0),
    }
  }).sort((a, b) => b.war - a.war)
  
  // Get top performers by WAR per game (min 10 games)
  const topWARPerGame = [...leadersWithData]
    .filter(p => p.gamesPlayed >= 10)
    .sort((a, b) => b.warPerGame - a.warPerGame)
    .slice(0, 10)
  
  // Get top performers by GAR
  const topGAR = [...leadersWithData]
    .sort((a, b) => b.gar - a.gar)
    .slice(0, 10)
  
  // Aggregate WAR trends by season
  const { data: seasonWAR } = await supabase
    .from('fact_player_season_stats_basic')
    .select('season, war, gar, games_played')
    .not('war', 'is', null)
    .order('season', { ascending: true })
  
  const warTrendsBySeason = (seasonWAR || []).reduce((acc: any, stat: any) => {
    const season = stat.season || 'Unknown'
    if (!acc[season]) {
      acc[season] = {
        season,
        totalWAR: 0,
        totalGAR: 0,
        totalGames: 0,
        playerCount: 0
      }
    }
    acc[season].totalWAR += Number(stat.war || 0)
    acc[season].totalGAR += Number(stat.gar || 0)
    acc[season].totalGames += Number(stat.games_played || 0)
    acc[season].playerCount += 1
    return acc
  }, {})
  
  const warTrendsData = Object.values(warTrendsBySeason)
    .map((stat: any) => ({
      season: stat.season,
      avgWAR: stat.playerCount > 0 ? (stat.totalWAR / stat.playerCount) : 0,
      avgGAR: stat.playerCount > 0 ? (stat.totalGAR / stat.playerCount) : 0,
      avgWARPerGame: stat.totalGames > 0 ? (stat.totalWAR / stat.totalGames) : 0,
      avgGARPerGame: stat.totalGames > 0 ? (stat.totalGAR / stat.totalGames) : 0,
    }))
    .sort((a, b) => String(a.season).localeCompare(String(b.season)))
  
  // Calculate summary stats
  const totalWAR = leadersWithData.reduce((sum, p) => sum + p.war, 0)
  const totalGAR = leadersWithData.reduce((sum, p) => sum + p.gar, 0)
  const avgWAR = leadersWithData.length > 0 ? (totalWAR / leadersWithData.length) : 0
  const avgGAR = leadersWithData.length > 0 ? (totalGAR / leadersWithData.length) : 0
  
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
            <Award className="w-5 h-5" />
            WAR/GAR Leaders
          </h1>
        </div>
        <div className="p-6">
          <p className="text-sm text-muted-foreground mb-6">
            WAR (Wins Above Replacement) and GAR (Goals Above Replacement) measure a player's total contribution 
            compared to a replacement-level player. Higher values indicate more valuable players.
          </p>
          
          {/* Summary Stats */}
          <div className="grid md:grid-cols-4 gap-4 mb-6">
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Total WAR</div>
              <div className="font-mono text-2xl font-bold text-foreground">
                {totalWAR.toFixed(1)}
              </div>
            </div>
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Total GAR</div>
              <div className="font-mono text-2xl font-bold text-primary">
                {totalGAR.toFixed(1)}
              </div>
            </div>
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Avg WAR</div>
              <div className="font-mono text-2xl font-bold text-assist">
                {avgWAR.toFixed(2)}
              </div>
            </div>
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Avg GAR</div>
              <div className="font-mono text-2xl font-bold text-goal">
                {avgGAR.toFixed(2)}
              </div>
            </div>
          </div>
          
          {/* WAR/GAR Trends Chart */}
          {warTrendsData.length > 0 && (
            <div className="mb-6">
              <div className="bg-card rounded-xl border border-border overflow-hidden">
                <div className="px-4 py-3 bg-accent border-b border-border">
                  <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                    <TrendingUp className="w-4 h-4" />
                    WAR/GAR Trends by Season
                  </h2>
                </div>
                <div className="p-6">
                  <TrendLineChart
                    data={warTrendsData}
                    xAxisKey="season"
                    dataKeys={[
                      { key: 'avgWAR', name: 'Avg WAR', color: 'hsl(var(--primary))', strokeWidth: 2 },
                      { key: 'avgGAR', name: 'Avg GAR', color: 'hsl(var(--assist))', strokeWidth: 2 },
                    ]}
                    height={300}
                  />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* WAR Leaders Table */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="px-4 py-3 bg-accent border-b border-border">
          <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
            <BarChart3 className="w-4 h-4" />
            WAR Leaders
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
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">G</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">A</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">P</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">WAR</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">GAR</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">WAR/G</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">CF%</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">Rating</th>
                </tr>
              </thead>
              <tbody>
                {leadersWithData.slice(0, 50).map((leader, index) => (
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
                    <td className="text-right py-3 font-mono">{leader.goals}</td>
                    <td className="text-right py-3 font-mono">{leader.assists}</td>
                    <td className="text-right py-3 font-mono font-semibold text-primary">{leader.points}</td>
                    <td className={cn(
                      "text-right py-3 font-mono font-semibold",
                      leader.war > 0 ? "text-save" : leader.war < 0 ? "text-goal" : "text-muted-foreground"
                    )}>
                      {leader.war > 0 ? '+' : ''}{leader.war.toFixed(2)}
                    </td>
                    <td className={cn(
                      "text-right py-3 font-mono",
                      leader.gar > 0 ? "text-save" : leader.gar < 0 ? "text-goal" : "text-muted-foreground"
                    )}>
                      {leader.gar > 0 ? '+' : ''}{leader.gar.toFixed(2)}
                    </td>
                    <td className="text-right py-3 font-mono">{leader.warPerGame.toFixed(3)}</td>
                    <td className="text-right py-3 font-mono">{leader.cfPct > 0 ? leader.cfPct.toFixed(1) : '-'}%</td>
                    <td className="text-right py-3 font-mono">{leader.playerRating > 0 ? leader.playerRating.toFixed(1) : '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      
      {/* Top Performers */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Zap className="w-4 h-4" />
              Top WAR Per Game (Min 10 GP)
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {topWARPerGame.map((player, index) => (
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
                        {player.gamesPlayed} GP, {player.points}P
                      </div>
                    </div>
                  </div>
                  <div className={cn(
                    "font-mono font-bold text-lg",
                    player.war > 0 ? "text-save" : "text-muted-foreground"
                  )}>
                    {player.warPerGame.toFixed(3)}
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
              Top GAR Leaders
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {topGAR.map((player, index) => (
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
                        {player.gamesPlayed} GP, {player.war.toFixed(1)} WAR
                      </div>
                    </div>
                  </div>
                  <div className={cn(
                    "font-mono font-bold text-lg",
                    player.gar > 0 ? "text-save" : "text-muted-foreground"
                  )}>
                    {player.gar > 0 ? '+' : ''}{player.gar.toFixed(1)}
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
