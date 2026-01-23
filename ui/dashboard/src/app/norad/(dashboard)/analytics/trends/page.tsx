// src/app/(dashboard)/analytics/trends/page.tsx
import Link from 'next/link'
import { createClient } from '@/lib/supabase/server'
import { ArrowLeft, TrendingUp, BarChart3, Activity, Target } from 'lucide-react'
import { cn } from '@/lib/utils'
import { TrendLineChart } from '@/components/charts/trend-line-chart'

export const revalidate = 300

export const metadata = {
  title: 'Trends | BenchSight Analytics',
  description: 'View league and player trends over time',
}

export default async function TrendsPage() {
  const supabase = await createClient()
  
  // Get season data for trends
  const { data: seasons } = await supabase
    .from('dim_season')
    .select('*')
    .order('season', { ascending: false })
    .limit(10)
  
  // Get team trends aggregated by season
  const { data: rawTeamTrendsData } = await supabase
    .from('fact_team_season_stats_basic')
    .select('season, season_id, wins, losses, goals_for, goals_against, points')
    .order('season', { ascending: true })
  
  const teamTrends = (rawTeamTrendsData || []).filter(t => {
    const season = t.season || t.season_id || ''
    return typeof season === 'string' && !season.toLowerCase().includes('summer')
  })
  
  // Get player trends aggregated by season (top players)
  const { data: rawPlayerTrendsData } = await supabase
    .from('fact_player_season_stats_basic')
    .select('season, season_id, goals, assists, points, games_played')
    .order('season', { ascending: true })
  
  const playerTrends = (rawPlayerTrendsData || []).filter(p => {
    const season = p.season || p.season_id || ''
    return typeof season === 'string' && !season.toLowerCase().includes('summer')
  })
  
  // Aggregate team stats by season
  const teamStatsBySeason = (teamTrends || []).reduce((acc: any, stat: any) => {
    const season = stat.season || stat.season_id
    if (!acc[season]) {
      acc[season] = {
        season,
        totalWins: 0,
        totalLosses: 0,
        totalGoalsFor: 0,
        totalGoalsAgainst: 0,
        totalPoints: 0,
        teamCount: 0
      }
    }
    acc[season].totalWins += Number(stat.wins || 0)
    acc[season].totalLosses += Number(stat.losses || 0)
    acc[season].totalGoalsFor += Number(stat.goals_for || 0)
    acc[season].totalGoalsAgainst += Number(stat.goals_against || 0)
    acc[season].totalPoints += Number(stat.points || 0)
    acc[season].teamCount += 1
    return acc
  }, {})
  
  const teamTrendsData = Object.values(teamStatsBySeason)
    .map((stat: any) => ({
      season: stat.season,
      avgWins: stat.teamCount > 0 ? (stat.totalWins / stat.teamCount).toFixed(1) : 0,
      avgLosses: stat.teamCount > 0 ? (stat.totalLosses / stat.teamCount).toFixed(1) : 0,
      avgGoalsFor: stat.teamCount > 0 ? (stat.totalGoalsFor / stat.teamCount).toFixed(1) : 0,
      avgGoalsAgainst: stat.teamCount > 0 ? (stat.totalGoalsAgainst / stat.teamCount).toFixed(1) : 0,
      avgPoints: stat.teamCount > 0 ? (stat.totalPoints / stat.teamCount).toFixed(1) : 0,
    }))
    .sort((a, b) => String(a.season).localeCompare(String(b.season)))
  
  // Aggregate player stats by season (top scorers)
  const playerStatsBySeason = (playerTrends || []).reduce((acc: any, stat: any) => {
    const season = stat.season || stat.season_id
    if (!acc[season]) {
      acc[season] = {
        season,
        totalGoals: 0,
        totalAssists: 0,
        totalPoints: 0,
        totalGames: 0,
        playerCount: 0
      }
    }
    acc[season].totalGoals += Number(stat.goals || 0)
    acc[season].totalAssists += Number(stat.assists || 0)
    acc[season].totalPoints += Number(stat.points || 0)
    acc[season].totalGames += Number(stat.games_played || 0)
    acc[season].playerCount += 1
    return acc
  }, {})
  
  const playerTrendsData = Object.values(playerStatsBySeason)
    .map((stat: any) => ({
      season: stat.season,
      avgGoals: stat.playerCount > 0 ? (stat.totalGoals / stat.playerCount).toFixed(1) : 0,
      avgAssists: stat.playerCount > 0 ? (stat.totalAssists / stat.playerCount).toFixed(1) : 0,
      avgPoints: stat.playerCount > 0 ? (stat.totalPoints / stat.playerCount).toFixed(1) : 0,
      avgGames: stat.playerCount > 0 ? (stat.totalGames / stat.playerCount).toFixed(1) : 0,
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
            <TrendingUp className="w-5 h-5" />
            Trends Analysis
          </h1>
        </div>
        <div className="p-6">
          <div className="space-y-6">
            {/* Overview Stats */}
            <div className="grid md:grid-cols-4 gap-4">
              <div className="bg-muted/30 rounded-lg p-4 text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Seasons</div>
                <div className="font-mono text-2xl font-bold text-foreground">
                  {seasons?.length || 0}
                </div>
              </div>
              <div className="bg-muted/30 rounded-lg p-4 text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Teams Tracked</div>
                <div className="font-mono text-2xl font-bold text-primary">
                  {new Set(teamTrends?.map((t: any) => t.season) || []).size}
                </div>
              </div>
              <div className="bg-muted/30 rounded-lg p-4 text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Data Points</div>
                <div className="font-mono text-2xl font-bold text-assist">
                  {(teamTrends?.length || 0) + (playerTrends?.length || 0)}
                </div>
              </div>
              <div className="bg-muted/30 rounded-lg p-4 text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Avg Points/Season</div>
                <div className="font-mono text-2xl font-bold text-goal">
                  {playerTrendsData.length > 0 
                    ? Number(playerTrendsData[playerTrendsData.length - 1]?.avgPoints || 0).toFixed(0)
                    : '0'}
                </div>
              </div>
            </div>
            
            {/* Team Trends Chart */}
            {teamTrendsData.length > 0 && (
              <div className="bg-card rounded-xl border border-border overflow-hidden">
                <div className="px-4 py-3 bg-accent border-b border-border">
                  <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                    <BarChart3 className="w-4 h-4" />
                    Team Statistics Trends
                  </h2>
                </div>
                <div className="p-6">
                  <TrendLineChart
                    data={teamTrendsData}
                    xAxisKey="season"
                    dataKeys={[
                      { key: 'avgWins', name: 'Avg Wins', color: 'hsl(var(--save))' },
                      { key: 'avgLosses', name: 'Avg Losses', color: 'hsl(var(--goal))' },
                      { key: 'avgPoints', name: 'Avg Points', color: 'hsl(var(--primary))' },
                    ]}
                    height={300}
                  />
                </div>
              </div>
            )}
            
            {/* Goals Trends Chart */}
            {teamTrendsData.length > 0 && (
              <div className="bg-card rounded-xl border border-border overflow-hidden">
                <div className="px-4 py-3 bg-accent border-b border-border">
                  <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                    <Target className="w-4 h-4" />
                    Goals Per Game Trends
                  </h2>
                </div>
                <div className="p-6">
                  <TrendLineChart
                    data={teamTrendsData}
                    xAxisKey="season"
                    dataKeys={[
                      { key: 'avgGoalsFor', name: 'Avg Goals For', color: 'hsl(var(--goal))' },
                      { key: 'avgGoalsAgainst', name: 'Avg Goals Against', color: 'hsl(var(--assist))' },
                    ]}
                    height={300}
                  />
                </div>
              </div>
            )}
            
            {/* Player Trends Chart */}
            {playerTrendsData.length > 0 && (
              <div className="bg-card rounded-xl border border-border overflow-hidden">
                <div className="px-4 py-3 bg-accent border-b border-border">
                  <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                    <Activity className="w-4 h-4" />
                    Player Scoring Trends
                  </h2>
                </div>
                <div className="p-6">
                  <TrendLineChart
                    data={playerTrendsData}
                    xAxisKey="season"
                    dataKeys={[
                      { key: 'avgGoals', name: 'Avg Goals', color: 'hsl(var(--goal))' },
                      { key: 'avgAssists', name: 'Avg Assists', color: 'hsl(var(--assist))' },
                      { key: 'avgPoints', name: 'Avg Points', color: 'hsl(var(--primary))' },
                    ]}
                    height={300}
                  />
                </div>
              </div>
            )}
            
            {/* Available Seasons */}
            {seasons && seasons.length > 0 && (
              <div className="bg-muted/10 rounded-lg p-4">
                <h3 className="font-display text-xs font-semibold uppercase text-muted-foreground mb-3">
                  Available Seasons
                </h3>
                <div className="flex flex-wrap gap-2">
                  {seasons.map((season: any) => (
                    <span
                      key={season.season_id}
                      className="text-xs font-mono bg-accent px-2 py-1 rounded uppercase"
                    >
                      {season.season || season.season_id}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
