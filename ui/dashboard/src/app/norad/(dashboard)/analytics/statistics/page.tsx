// src/app/(dashboard)/analytics/statistics/page.tsx
// League Statistics - Production Page

import { createClient } from '@/lib/supabase/server'
import { BarChart3, TrendingUp, Target, Users, Activity } from 'lucide-react'
import { ScorersChart } from '@/components/charts/scorers-chart'
import { GoalDiffChart } from '@/components/charts/goal-diff-chart'
import { PrototypeTable } from '@/components/prototypes/prototype-template'
import { cn } from '@/lib/utils'
import Link from 'next/link'

export const revalidate = 300

export const metadata = {
  title: 'League Statistics | BenchSight',
  description: 'Comprehensive league-wide analytics and distributions',
}

export default async function LeagueStatisticsPage() {
  const supabase = await createClient()
  
  // Fetch comprehensive league data
  const [
    leagueSummary,
    standings,
    pointsLeaders,
    teamStats
  ] = await Promise.all([
    supabase.from('v_summary_league').select('*').single(),
    supabase.from('v_standings_current').select('*').order('standing', { ascending: true }),
    supabase.from('v_leaderboard_points').select('*').order('season_rank', { ascending: true }).limit(10),
    supabase.from('v_summary_team_season').select('*').limit(20),
  ])

  const summary = leagueSummary.data
  const standingsData = standings.data || []
  const leaders = pointsLeaders.data || []
  const teams = teamStats.data || []

  // Calculate league-wide metrics
  const totalGoals = summary?.total_goals || 0
  const totalAssists = summary?.total_assists || 0
  const totalPoints = summary?.total_points || 0
  const totalGames = summary?.total_games || 1
  const totalPlayers = summary?.total_players || 1

  const goalsPerGame = (totalGoals / totalGames).toFixed(2)
  const pointsPerGame = (totalPoints / totalGames).toFixed(2)
  const pointsPerPlayer = (totalPoints / totalPlayers).toFixed(1)
  const assistsPerGoal = totalGoals > 0 ? (totalAssists / totalGoals).toFixed(2) : '0.00'

  // Goal differential distribution
  const goalDiffData = standingsData.map(team => ({
    name: team.team_name?.substring(0, 10) || 'Team',
    diff: team.goal_diff || 0,
  })).sort((a, b) => b.diff - a.diff)

  // Top scorers chart
  const topScorersChart = leaders.slice(0, 10).map(player => ({
    name: player.player_name?.substring(0, 10) || 'Player',
    points: player.points || 0,
    goals: player.goals || 0,
    assists: player.assists || 0,
  }))

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="font-display text-2xl font-bold tracking-wider uppercase flex items-center gap-3">
          <span className="w-1 h-6 bg-primary rounded" />
          League Statistics
        </h1>
        <p className="text-sm text-muted-foreground mt-2 ml-4">
          Comprehensive league-wide analytics and distributions
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-card rounded-lg p-4 border border-border">
          <div className="flex items-center gap-2 mb-2">
            <Target className="w-4 h-4 text-goal" />
            <span className="text-xs font-mono text-muted-foreground uppercase">Goals/Game</span>
          </div>
          <div className="font-mono text-2xl font-bold text-goal">{goalsPerGame}</div>
        </div>
        <div className="bg-card rounded-lg p-4 border border-border">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-4 h-4 text-primary" />
            <span className="text-xs font-mono text-muted-foreground uppercase">Points/Game</span>
          </div>
          <div className="font-mono text-2xl font-bold text-foreground">{pointsPerGame}</div>
        </div>
        <div className="bg-card rounded-lg p-4 border border-border">
          <div className="flex items-center gap-2 mb-2">
            <Users className="w-4 h-4 text-assist" />
            <span className="text-xs font-mono text-muted-foreground uppercase">Points/Player</span>
          </div>
          <div className="font-mono text-2xl font-bold text-foreground">{pointsPerPlayer}</div>
        </div>
        <div className="bg-card rounded-lg p-4 border border-border">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="w-4 h-4 text-save" />
            <span className="text-xs font-mono text-muted-foreground uppercase">Assists/Goal</span>
          </div>
          <div className="font-mono text-2xl font-bold text-foreground">{assistsPerGoal}</div>
        </div>
        <div className="bg-card rounded-lg p-4 border border-border">
          <div className="flex items-center gap-2 mb-2">
            <Target className="w-4 h-4 text-goal" />
            <span className="text-xs font-mono text-muted-foreground uppercase">Total Goals</span>
          </div>
          <div className="font-mono text-2xl font-bold text-goal">{totalGoals}</div>
        </div>
        <div className="bg-card rounded-lg p-4 border border-border">
          <div className="flex items-center gap-2 mb-2">
            <BarChart3 className="w-4 h-4 text-primary" />
            <span className="text-xs font-mono text-muted-foreground uppercase">Total Points</span>
          </div>
          <div className="font-mono text-2xl font-bold text-foreground">{totalPoints}</div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Scorers */}
        <div className="bg-card rounded-xl border border-border p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-display text-lg font-semibold">Top 10 Scorers</h2>
            <Link 
              href="/norad/leaders?tab=points" 
              className="text-xs text-muted-foreground hover:text-primary transition-colors"
            >
              View All →
            </Link>
          </div>
          <ScorersChart data={topScorersChart} />
        </div>

        {/* Goal Differential */}
        <div className="bg-card rounded-xl border border-border p-6">
          <h2 className="font-display text-lg font-semibold mb-4">Goal Differential</h2>
          <GoalDiffChart data={goalDiffData} />
        </div>
      </div>

      {/* Team Performance Table */}
      {teams && teams.length > 0 ? (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="p-6 pb-4">
            <h2 className="font-display text-lg font-semibold">Team Season Performance</h2>
          </div>
          <PrototypeTable
            data={teams}
            columns={[
              { 
                key: 'team_name', 
                label: 'Team',
                align: 'left',
                render: (value, row) => (
                  <Link 
                    href={`/teams/${encodeURIComponent(value || '')}`}
                    className="font-display text-sm hover:text-primary transition-colors"
                  >
                    {value}
                  </Link>
                )
              },
              { 
                key: 'games_played', 
                label: 'GP',
                align: 'center',
                render: (value) => <span className="font-mono text-sm text-muted-foreground">{value}</span>
              },
              { 
                key: 'wins', 
                label: 'W',
                align: 'center',
                render: (value) => <span className="font-mono text-sm text-save font-semibold">{value}</span>
              },
              { 
                key: 'losses', 
                label: 'L',
                align: 'center',
                render: (value) => <span className="font-mono text-sm text-goal">{value}</span>
              },
              { 
                key: 'win_pct', 
                label: 'WIN%',
                align: 'center',
                render: (value, row) => {
                  // Calculate win percentage correctly: points / (games_played * 2) * 100
                  const ties = row.ties || 0
                  const points = row.points || (row.wins * 2 + ties)
                  const gamesPlayed = row.games_played || 0
                  const winPct = gamesPlayed > 0 ? (points / (gamesPlayed * 2)) * 100 : 0
                  return <span className="font-mono text-sm text-foreground">{winPct.toFixed(1)}%</span>
                }
              },
              { 
                key: 'goals_for', 
                label: 'GF',
                align: 'center',
                render: (value) => <span className="font-mono text-sm text-muted-foreground">{value}</span>
              },
              { 
                key: 'goals_against', 
                label: 'GA',
                align: 'center',
                render: (value) => <span className="font-mono text-sm text-muted-foreground">{value}</span>
              },
              { 
                key: 'goal_diff', 
                label: 'DIFF',
                align: 'center',
                render: (value) => (
                  <span className={cn(
                    'font-mono text-sm font-bold',
                    value > 0 ? 'text-save' : value < 0 ? 'text-goal' : 'text-muted-foreground'
                  )}>
                    {value > 0 ? '+' : ''}{value}
                  </span>
                )
              },
              { 
                key: 'goals_for_per_game', 
                label: 'GF/GP',
                align: 'center',
                render: (value) => <span className="font-mono text-sm text-muted-foreground">{value?.toFixed(2)}</span>
              },
              { 
                key: 'goals_against_per_game', 
                label: 'GA/GP',
                align: 'center',
                render: (value) => <span className="font-mono text-sm text-muted-foreground">{value?.toFixed(2)}</span>
              },
            ]}
          />
        </div>
      ) : (
        <div className="bg-card rounded-xl border border-border p-12 text-center">
          <p className="text-muted-foreground">No team statistics available</p>
        </div>
      )}
    </div>
  )
}
