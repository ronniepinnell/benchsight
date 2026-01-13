// src/app/(dashboard)/prototypes/macro/team-comparison/page.tsx
// Team comparison and power rankings

import { PrototypeTemplate, StatCard } from '@/components/prototypes/prototype-template'
import { createClient } from '@/lib/supabase/server'
import { Trophy, TrendingUp, Target, Users, BarChart3 } from 'lucide-react'
import { ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts'
import Link from 'next/link'
import { cn } from '@/lib/utils'

export const revalidate = 300

export default async function TeamComparisonPage() {
  const supabase = await createClient()
  
  // Fetch team data
  const [standings, teamStats] = await Promise.all([
    supabase.from('v_standings_current').select('*').order('standing', { ascending: true }),
    supabase.from('v_summary_team_season').select('*'),
  ])

  const standingsData = standings.data || []
  const teams = teamStats.data || []

  // Calculate power rankings (weighted by wins, goal diff, recent form)
  const powerRankings = standingsData.map(team => {
    const winPct = team.games_played > 0 ? (team.wins / team.games_played) : 0
    const goalDiffPerGame = team.games_played > 0 ? (team.goal_diff / team.games_played) : 0
    
    // Simple power ranking formula
    const powerScore = (winPct * 40) + (goalDiffPerGame * 2) + (team.wins * 2)
    
    return {
      ...team,
      powerScore: Math.round(powerScore * 100) / 100,
      winPct: winPct * 100,
    }
  }).sort((a, b) => b.powerScore - a.powerScore)

  // Prepare comparison data
  const comparisonData = powerRankings.slice(0, 8).map(team => ({
    name: team.team_name?.substring(0, 10) || 'Team',
    wins: team.wins || 0,
    losses: team.losses || 0,
    goalDiff: team.goal_diff || 0,
    powerScore: team.powerScore,
    winPct: team.winPct,
  }))

  // Radar chart data (top 3 teams)
  const radarData = powerRankings.slice(0, 3).map(team => ({
    team: team.team_name?.substring(0, 8) || 'Team',
    Wins: (team.wins || 0) * 10,
    'Win %': team.winPct,
    'Goal Diff': (team.goal_diff || 0) + 20, // Normalize for radar
    'Goals For': (team.goals_for || 0) / 2,
    'Power Score': team.powerScore * 10,
  }))

  return (
    <PrototypeTemplate 
      title="Team Comparison & Power Rankings" 
      description="Compare teams across multiple dimensions"
    >
      {/* Power Rankings */}
      <div className="bg-card rounded-xl border border-border p-6">
        <h2 className="font-display text-lg font-semibold mb-4 flex items-center gap-2">
          <Trophy className="w-5 h-5 text-assist" />
          Power Rankings
        </h2>
        <div className="space-y-2">
          {powerRankings.map((team, idx) => {
            const rankChange = team.standing - (idx + 1)
            return (
              <div
                key={team.team_id}
                className={cn(
                  'flex items-center justify-between p-3 rounded-lg border',
                  idx < 3 ? 'bg-assist/10 border-assist' : 'bg-muted/30 border-border'
                )}
              >
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <span className={cn(
                      'font-display font-bold w-8 text-center',
                      idx < 3 ? 'text-lg text-assist' : 'text-muted-foreground'
                    )}>
                      {idx + 1}
                    </span>
                    {rankChange !== 0 && (
                      <span className={cn(
                        'text-xs font-mono',
                        rankChange < 0 ? 'text-save' : 'text-goal'
                      )}>
                        {rankChange < 0 ? '↑' : '↓'} {Math.abs(rankChange)}
                      </span>
                    )}
                  </div>
                  <Link 
                    href={`/teams/${encodeURIComponent(team.team_name || '')}`}
                    className="font-display text-sm hover:text-primary transition-colors"
                  >
                    {team.team_name}
                  </Link>
                </div>
                <div className="flex items-center gap-6 text-sm">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-save">{team.wins}W</span>
                    <span className="font-mono text-goal">{team.losses}L</span>
                  </div>
                  <span className={cn(
                    'font-mono font-semibold',
                    team.goal_diff > 0 ? 'text-save' : team.goal_diff < 0 ? 'text-goal' : ''
                  )}>
                    {team.goal_diff > 0 ? '+' : ''}{team.goal_diff}
                  </span>
                  <span className="font-mono text-xs text-muted-foreground">
                    {team.powerScore.toFixed(1)}
                  </span>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Comparison Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Teams Comparison */}
        <div className="bg-card rounded-xl border border-border p-6">
          <h2 className="font-display text-lg font-semibold mb-4">Top 8 Teams Comparison</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={comparisonData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="wins" fill="hsl(var(--save))" name="Wins" />
              <Bar dataKey="losses" fill="hsl(var(--goal))" name="Losses" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Power Score Chart */}
        <div className="bg-card rounded-xl border border-border p-6">
          <h2 className="font-display text-lg font-semibold mb-4">Power Score</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={comparisonData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="powerScore" fill="hsl(var(--assist))" name="Power Score" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top 3 Teams Radar */}
      {radarData.length > 0 && (
        <div className="bg-card rounded-xl border border-border p-6">
          <h2 className="font-display text-lg font-semibold mb-4">Top 3 Teams - Multi-Dimensional View</h2>
          <ResponsiveContainer width="100%" height={400}>
            <RadarChart data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="team" />
              <PolarRadiusAxis angle={90} domain={[0, 100]} />
              <Radar 
                name="Team 1" 
                dataKey={radarData[0]?.team} 
                stroke="hsl(var(--save))" 
                fill="hsl(var(--save))" 
                fillOpacity={0.6} 
              />
              {radarData[1] && (
                <Radar 
                  name="Team 2" 
                  dataKey={radarData[1]?.team} 
                  stroke="hsl(var(--assist))" 
                  fill="hsl(var(--assist))" 
                  fillOpacity={0.6} 
                />
              )}
              {radarData[2] && (
                <Radar 
                  name="Team 3" 
                  dataKey={radarData[2]?.team} 
                  stroke="hsl(var(--goal))" 
                  fill="hsl(var(--goal))" 
                  fillOpacity={0.6} 
                />
              )}
              <Tooltip />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard 
          label="Total Teams" 
          value={standingsData.length} 
          icon={Users}
          color="text-primary"
        />
        <StatCard 
          label="Avg Win %" 
          value={`${(powerRankings.reduce((sum, t) => sum + t.winPct, 0) / powerRankings.length).toFixed(1)}%`} 
          icon={TrendingUp}
          color="text-assist"
        />
        <StatCard 
          label="Total Games" 
          value={standingsData.reduce((sum, t) => sum + (t.games_played || 0), 0)} 
          icon={BarChart3}
          color="text-save"
        />
        <StatCard 
          label="Top Power Score" 
          value={powerRankings[0]?.powerScore.toFixed(1) || '0.0'} 
          icon={Trophy}
          color="text-goal"
        />
      </div>
    </PrototypeTemplate>
  )
}
