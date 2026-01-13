// src/app/(dashboard)/analytics/teams/page.tsx
// Team Comparison & Power Rankings - Production Page

import { createClient } from '@/lib/supabase/server'
import { Trophy, TrendingUp, Users, BarChart3 } from 'lucide-react'
import { TeamComparisonChart } from '@/components/charts/team-comparison-chart'
import { PowerScoreChart } from '@/components/charts/power-score-chart'
import Link from 'next/link'
import { cn } from '@/lib/utils'

export const revalidate = 300

export const metadata = {
  title: 'Team Comparison | BenchSight',
  description: 'Compare teams across multiple dimensions with power rankings',
}

export default async function TeamComparisonPage() {
  const supabase = await createClient()
  
  // Fetch team data
  const [standings, teamStats] = await Promise.all([
    supabase.from('v_standings_current').select('*').order('standing', { ascending: true }),
    supabase.from('v_summary_team_season').select('*'),
  ])

  const standingsData = standings.data || []
  const teams = teamStats.data || []

  // Calculate power rankings (weighted by wins, goal diff, win percentage)
  const powerRankings = standingsData.map(team => {
    const winPct = team.games_played > 0 ? (team.wins / team.games_played) : 0
    const goalDiffPerGame = team.games_played > 0 ? (team.goal_diff / team.games_played) : 0
    
    // Power ranking formula: win% (40pts) + goal diff/game (2pts per) + wins (2pts each)
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


  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="font-display text-2xl font-bold tracking-wider uppercase flex items-center gap-3">
          <span className="w-1 h-6 bg-primary rounded" />
          Team Comparison & Power Rankings
        </h1>
        <p className="text-sm text-muted-foreground mt-2 ml-4">
          Compare teams across multiple dimensions
        </p>
      </div>

      {/* Power Rankings */}
      <div className="bg-card rounded-xl border border-border p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-display text-lg font-semibold flex items-center gap-2">
            <Trophy className="w-5 h-5 text-assist" />
            Power Rankings
          </h2>
          <Link 
            href="/standings" 
            className="text-xs text-muted-foreground hover:text-primary transition-colors"
          >
            View Official Standings →
          </Link>
        </div>
        <div className="space-y-2">
          {powerRankings.map((team, idx) => {
            const rankChange = team.standing - (idx + 1)
            return (
              <div
                key={`power-${team.team_id}`}
                className={cn(
                  'flex items-center justify-between p-3 rounded-lg border transition-colors hover:bg-muted/50',
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
          <TeamComparisonChart data={comparisonData.map(t => ({ name: t.name, wins: t.wins, losses: t.losses }))} />
        </div>

        {/* Power Score Chart */}
        <div className="bg-card rounded-xl border border-border p-6">
          <h2 className="font-display text-lg font-semibold mb-4">Power Score</h2>
          <PowerScoreChart data={comparisonData.map(t => ({ name: t.name, powerScore: t.powerScore }))} />
        </div>
      </div>

      {/* Top 3 Teams Comparison Table */}
      {powerRankings.slice(0, 3).length > 0 && (
        <div className="bg-card rounded-xl border border-border p-6">
          <h2 className="font-display text-lg font-semibold mb-4">Top 3 Teams - Detailed Comparison</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {powerRankings.slice(0, 3).map((team, idx) => (
              <div
                key={`detail-${team.team_id}`}
                className={cn(
                  'p-4 rounded-lg border',
                  idx === 0 ? 'bg-assist/10 border-assist' : 'bg-muted/30 border-border'
                )}
              >
                <div className="flex items-center justify-between mb-3">
                  <Link 
                    href={`/teams/${encodeURIComponent(team.team_name || '')}`}
                    className="font-display font-semibold hover:text-primary transition-colors"
                  >
                    {team.team_name}
                  </Link>
                  <span className="text-xs font-mono text-muted-foreground">#{idx + 1}</span>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Record:</span>
                    <span className="font-mono">
                      <span className="text-save">{team.wins}W</span>
                      {' - '}
                      <span className="text-goal">{team.losses}L</span>
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Win %:</span>
                    <span className="font-mono">{team.winPct.toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Goal Diff:</span>
                    <span className={cn(
                      'font-mono font-semibold',
                      team.goal_diff > 0 ? 'text-save' : team.goal_diff < 0 ? 'text-goal' : ''
                    )}>
                      {team.goal_diff > 0 ? '+' : ''}{team.goal_diff}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Power Score:</span>
                    <span className="font-mono text-assist font-semibold">{team.powerScore.toFixed(1)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-card rounded-lg p-4 border border-border">
          <div className="flex items-center gap-2 mb-2">
            <Users className="w-4 h-4 text-primary" />
            <span className="text-xs font-mono text-muted-foreground uppercase">Teams</span>
          </div>
          <div className="font-mono text-2xl font-bold text-foreground">{standingsData.length}</div>
        </div>
        <div className="bg-card rounded-lg p-4 border border-border">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-4 h-4 text-assist" />
            <span className="text-xs font-mono text-muted-foreground uppercase">Avg Win %</span>
          </div>
          <div className="font-mono text-2xl font-bold text-foreground">
            {powerRankings.length > 0 
              ? `${(powerRankings.reduce((sum, t) => sum + t.winPct, 0) / powerRankings.length).toFixed(1)}%`
              : '0.0%'
            }
          </div>
        </div>
        <div className="bg-card rounded-lg p-4 border border-border">
          <div className="flex items-center gap-2 mb-2">
            <BarChart3 className="w-4 h-4 text-save" />
            <span className="text-xs font-mono text-muted-foreground uppercase">Total Games</span>
          </div>
          <div className="font-mono text-2xl font-bold text-foreground">
            {standingsData.reduce((sum, t) => sum + (t.games_played || 0), 0)}
          </div>
        </div>
        <div className="bg-card rounded-lg p-4 border border-border">
          <div className="flex items-center gap-2 mb-2">
            <Trophy className="w-4 h-4 text-goal" />
            <span className="text-xs font-mono text-muted-foreground uppercase">Top Power</span>
          </div>
          <div className="font-mono text-2xl font-bold text-foreground">
            {powerRankings[0]?.powerScore.toFixed(1) || '0.0'}
          </div>
        </div>
      </div>
    </div>
  )
}
