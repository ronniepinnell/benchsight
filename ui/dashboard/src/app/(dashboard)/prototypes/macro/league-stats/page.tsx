// src/app/(dashboard)/prototypes/macro/league-stats/page.tsx
// Deep dive into league-wide statistics

import { PrototypeTemplate, StatCard, PrototypeTable } from '@/components/prototypes/prototype-template'
import { createClient } from '@/lib/supabase/server'
import { BarChart3, TrendingUp, Target, Users, Activity } from 'lucide-react'
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, PieChart, Pie, Cell } from 'recharts'

export const revalidate = 300

export default async function LeagueStatsPage() {
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

  // Team performance distribution
  const winDistribution = standingsData.reduce((acc: any, team) => {
    const wins = team.wins || 0
    const range = Math.floor(wins / 5) * 5
    acc[range] = (acc[range] || 0) + 1
    return acc
  }, {})

  const distributionData = Object.entries(winDistribution).map(([wins, count]) => ({
    name: `${wins}-${parseInt(wins) + 4} wins`,
    value: count,
  }))

  // Goal differential distribution
  const goalDiffData = standingsData.map(team => ({
    name: team.team_name?.substring(0, 8) || 'Team',
    diff: team.goal_diff || 0,
  })).sort((a, b) => b.diff - a.diff)

  // Top scorers chart
  const topScorersChart = leaders.slice(0, 10).map(player => ({
    name: player.player_name?.substring(0, 10) || 'Player',
    points: player.points || 0,
    goals: player.goals || 0,
    assists: player.assists || 0,
  }))

  const COLORS = [
    'hsl(var(--save))',
    'hsl(var(--assist))',
    'hsl(var(--goal))',
    'hsl(var(--primary))',
    'hsl(var(--shot))',
  ]

  return (
    <PrototypeTemplate 
      title="League Statistics" 
      description="Comprehensive league-wide analytics and distributions"
    >
      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <StatCard 
          label="Goals/Game" 
          value={goalsPerGame} 
          icon={Target}
          color="text-goal"
        />
        <StatCard 
          label="Points/Game" 
          value={pointsPerGame} 
          icon={TrendingUp}
          color="text-primary"
        />
        <StatCard 
          label="Points/Player" 
          value={pointsPerPlayer} 
          icon={Users}
          color="text-assist"
        />
        <StatCard 
          label="Assists/Goal" 
          value={assistsPerGoal} 
          icon={Activity}
          color="text-save"
        />
        <StatCard 
          label="Total Goals" 
          value={totalGoals} 
          icon={Target}
          color="text-goal"
        />
        <StatCard 
          label="Total Points" 
          value={totalPoints} 
          icon={BarChart3}
          color="text-primary"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Scorers */}
        <div className="bg-card rounded-xl border border-border p-6">
          <h2 className="font-display text-lg font-semibold mb-4">Top 10 Scorers</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={topScorersChart}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="points" fill="hsl(var(--primary))" name="Points" />
              <Bar dataKey="goals" fill="hsl(var(--goal))" name="Goals" />
              <Bar dataKey="assists" fill="hsl(var(--assist))" name="Assists" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Goal Differential */}
        <div className="bg-card rounded-xl border border-border p-6">
          <h2 className="font-display text-lg font-semibold mb-4">Goal Differential</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={goalDiffData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
              <YAxis />
              <Tooltip />
              <Bar 
                dataKey="diff" 
                fill={(entry: any) => entry.diff > 0 ? 'hsl(var(--save))' : 'hsl(var(--goal))'}
                name="Goal Diff"
              >
                {goalDiffData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.diff > 0 ? 'hsl(var(--save))' : 'hsl(var(--goal))'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Team Performance Table */}
      {teams.length > 0 && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <h2 className="font-display text-lg font-semibold p-6 pb-4">Team Season Performance</h2>
          <PrototypeTable
            data={teams}
            columns={[
              { key: 'team_name', label: 'Team' },
              { 
                key: 'games_played', 
                label: 'GP',
                render: (value) => <span className="font-mono">{value}</span>
              },
              { 
                key: 'wins', 
                label: 'W',
                render: (value) => <span className="font-mono font-semibold text-save">{value}</span>
              },
              { 
                key: 'losses', 
                label: 'L',
                render: (value) => <span className="font-mono text-goal">{value}</span>
              },
              { 
                key: 'win_pct', 
                label: 'Win %',
                render: (value) => <span className="font-mono">{(value * 100).toFixed(1)}%</span>
              },
              { 
                key: 'goals_for', 
                label: 'GF',
                render: (value) => <span className="font-mono">{value}</span>
              },
              { 
                key: 'goals_against', 
                label: 'GA',
                render: (value) => <span className="font-mono">{value}</span>
              },
              { 
                key: 'goal_diff', 
                label: 'Diff',
                render: (value) => (
                  <span className={`font-mono font-semibold ${
                    value > 0 ? 'text-save' : value < 0 ? 'text-goal' : ''
                  }`}>
                    {value > 0 ? '+' : ''}{value}
                  </span>
                )
              },
              { 
                key: 'goals_for_per_game', 
                label: 'GF/GP',
                render: (value) => <span className="font-mono">{value?.toFixed(2)}</span>
              },
              { 
                key: 'goals_against_per_game', 
                label: 'GA/GP',
                render: (value) => <span className="font-mono">{value?.toFixed(2)}</span>
              },
            ]}
          />
        </div>
      )}
    </PrototypeTemplate>
  )
}
