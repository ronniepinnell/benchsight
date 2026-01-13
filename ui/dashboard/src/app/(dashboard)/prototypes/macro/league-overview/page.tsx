// src/app/(dashboard)/prototypes/macro/league-overview/page.tsx
// Comprehensive league overview dashboard

import { PrototypeTemplate, StatCard } from '@/components/prototypes/prototype-template'
import { createClient } from '@/lib/supabase/server'
import { 
  Trophy, 
  Target, 
  Users, 
  Calendar, 
  TrendingUp,
  Award,
  BarChart3,
  Activity
} from 'lucide-react'
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, LineChart, Line } from 'recharts'
import Link from 'next/link'
import { cn } from '@/lib/utils'

export const revalidate = 300

export default async function LeagueOverviewPage() {
  const supabase = await createClient()
  
  // Fetch all macro data
  const [
    leagueSummary,
    standings,
    pointsLeaders,
    goalsLeaders,
    assistsLeaders,
    goalieLeaders,
    recentGames
  ] = await Promise.all([
    supabase.from('v_summary_league').select('*').single(),
    supabase.from('v_standings_current').select('*').order('standing', { ascending: true }),
    supabase.from('v_leaderboard_points').select('*').order('season_rank', { ascending: true }).limit(5),
    supabase.from('v_leaderboard_goals').select('*').order('season_rank', { ascending: true }).limit(5),
    supabase.from('v_leaderboard_assists').select('*').order('season_rank', { ascending: true }).limit(5),
    supabase.from('v_leaderboard_goalie_wins').select('*').order('wins', { ascending: false }).limit(5),
    supabase.from('v_recent_games').select('*').limit(5),
  ])

  const summary = leagueSummary.data
  const standingsData = standings.data || []
  const topPoints = pointsLeaders.data || []
  const topGoals = goalsLeaders.data || []
  const topAssists = assistsLeaders.data || []
  const topGoalies = goalieLeaders.data || []
  const recent = recentGames.data || []

  // Calculate league averages
  const avgGoalsPerGame = summary 
    ? (summary.total_goals / (summary.total_games || 1)).toFixed(2)
    : '0.00'
  
  const avgPointsPerPlayer = summary
    ? (summary.total_points / (summary.total_players || 1)).toFixed(1)
    : '0.0'

  // Prepare chart data
  const standingsChart = standingsData.map(team => ({
    name: team.team_name?.substring(0, 8) || 'Team',
    wins: team.wins || 0,
    losses: team.losses || 0,
    goalDiff: team.goal_diff || 0,
  }))

  return (
    <PrototypeTemplate 
      title="League Overview" 
      description="Complete league-wide statistics and key metrics"
    >
      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <StatCard 
          label="Teams" 
          value={summary?.total_teams || 0} 
          icon={Users}
          color="text-primary"
        />
        <StatCard 
          label="Players" 
          value={summary?.total_players || 0} 
          icon={Users}
          color="text-assist"
        />
        <StatCard 
          label="Games" 
          value={summary?.total_games || 0} 
          icon={Calendar}
          color="text-save"
        />
        <StatCard 
          label="Goals" 
          value={summary?.total_goals || 0} 
          icon={Target}
          color="text-goal"
        />
        <StatCard 
          label="Avg Goals/Game" 
          value={avgGoalsPerGame} 
          icon={BarChart3}
          color="text-primary"
        />
        <StatCard 
          label="Avg Points/Player" 
          value={avgPointsPerPlayer} 
          icon={TrendingUp}
          color="text-assist"
        />
      </div>

      {/* Standings Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top 5 Standings */}
        <div className="bg-card rounded-xl border border-border p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-display text-lg font-semibold flex items-center gap-2">
              <Trophy className="w-5 h-5 text-assist" />
              Top 5 Standings
            </h2>
            <Link 
              href="/standings" 
              className="text-xs text-muted-foreground hover:text-primary transition-colors"
            >
              View All →
            </Link>
          </div>
          <div className="space-y-2">
            {standingsData.slice(0, 5).map((team, idx) => (
              <div
                key={team.team_id}
                className={cn(
                  'flex items-center justify-between p-3 rounded-lg border',
                  idx === 0 ? 'bg-assist/10 border-assist' : 'bg-muted/30 border-border'
                )}
              >
                <div className="flex items-center gap-3">
                  <span className={cn(
                    'font-display font-bold w-6 text-center',
                    idx === 0 ? 'text-lg text-assist' : 'text-muted-foreground'
                  )}>
                    {team.standing}
                  </span>
                  <Link 
                    href={`/teams/${encodeURIComponent(team.team_name || '')}`}
                    className="font-display text-sm hover:text-primary transition-colors"
                  >
                    {team.team_name}
                  </Link>
                </div>
                <div className="flex items-center gap-4 text-sm font-mono">
                  <span className="text-save">{team.wins}W</span>
                  <span className="text-goal">{team.losses}L</span>
                  <span className={cn(
                    'font-semibold',
                    team.goal_diff > 0 ? 'text-save' : team.goal_diff < 0 ? 'text-goal' : ''
                  )}>
                    {team.goal_diff > 0 ? '+' : ''}{team.goal_diff}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Standings Chart */}
        <div className="bg-card rounded-xl border border-border p-6">
          <h2 className="font-display text-lg font-semibold mb-4">Wins vs Losses</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={standingsChart}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="wins" fill="hsl(var(--save))" name="Wins" />
              <Bar dataKey="losses" fill="hsl(var(--goal))" name="Losses" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Leaders Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Points Leaders */}
        <div className="bg-card rounded-xl border border-border p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-display text-lg font-semibold flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-primary" />
              Points Leaders
            </h2>
            <Link 
              href="/leaders?tab=points" 
              className="text-xs text-muted-foreground hover:text-primary transition-colors"
            >
              View All →
            </Link>
          </div>
          <div className="space-y-2">
            {topPoints.map((player, idx) => (
              <div
                key={player.player_id}
                className="flex items-center justify-between p-2 rounded hover:bg-muted/50"
              >
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono text-muted-foreground w-4">
                    {idx + 1}
                  </span>
                  <Link 
                    href={`/players/${player.player_id}`}
                    className="text-sm hover:text-primary transition-colors"
                  >
                    {player.player_name}
                  </Link>
                </div>
                <span className="font-mono font-semibold text-primary">
                  {player.points}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Goals Leaders */}
        <div className="bg-card rounded-xl border border-border p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-display text-lg font-semibold flex items-center gap-2">
              <Target className="w-5 h-5 text-goal" />
              Goals Leaders
            </h2>
            <Link 
              href="/leaders?tab=goals" 
              className="text-xs text-muted-foreground hover:text-primary transition-colors"
            >
              View All →
            </Link>
          </div>
          <div className="space-y-2">
            {topGoals.map((player, idx) => (
              <div
                key={player.player_id}
                className="flex items-center justify-between p-2 rounded hover:bg-muted/50"
              >
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono text-muted-foreground w-4">
                    {idx + 1}
                  </span>
                  <Link 
                    href={`/players/${player.player_id}`}
                    className="text-sm hover:text-primary transition-colors"
                  >
                    {player.player_name}
                  </Link>
                </div>
                <span className="font-mono font-semibold text-goal">
                  {player.goals}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Goalie Leaders */}
        <div className="bg-card rounded-xl border border-border p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-display text-lg font-semibold flex items-center gap-2">
              <Award className="w-5 h-5 text-save" />
              Goalie Leaders
            </h2>
            <Link 
              href="/goalies" 
              className="text-xs text-muted-foreground hover:text-primary transition-colors"
            >
              View All →
            </Link>
          </div>
          <div className="space-y-2">
            {topGoalies.map((goalie, idx) => (
              <div
                key={goalie.player_id}
                className="flex items-center justify-between p-2 rounded hover:bg-muted/50"
              >
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono text-muted-foreground w-4">
                    {idx + 1}
                  </span>
                  <Link 
                    href={`/players/${goalie.player_id}`}
                    className="text-sm hover:text-primary transition-colors"
                  >
                    {goalie.player_name}
                  </Link>
                </div>
                <span className="font-mono font-semibold text-save">
                  {goalie.wins}W
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Games */}
      {recent.length > 0 && (
        <div className="bg-card rounded-xl border border-border p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-display text-lg font-semibold flex items-center gap-2">
              <Activity className="w-5 h-5 text-primary" />
              Recent Games
            </h2>
            <Link 
              href="/games" 
              className="text-xs text-muted-foreground hover:text-primary transition-colors"
            >
              View All →
            </Link>
          </div>
          <div className="space-y-2">
            {recent.map((game: any) => (
              <div
                key={game.game_id}
                className="flex items-center justify-between p-3 rounded border border-border hover:bg-muted/50"
              >
                <div className="flex items-center gap-4 text-sm">
                  <span className="text-muted-foreground font-mono text-xs">
                    {game.date ? new Date(game.date).toLocaleDateString() : 'TBD'}
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="font-display">{game.home_team_name || 'TBD'}</span>
                    <span className="text-muted-foreground">vs</span>
                    <span className="font-display">{game.away_team_name || 'TBD'}</span>
                  </div>
                </div>
                {game.home_score !== null && game.away_score !== null && (
                  <div className="flex items-center gap-2 font-mono font-semibold">
                    <span className={game.home_score > game.away_score ? 'text-save' : 'text-muted-foreground'}>
                      {game.home_score}
                    </span>
                    <span className="text-muted-foreground">-</span>
                    <span className={game.away_score > game.home_score ? 'text-save' : 'text-muted-foreground'}>
                      {game.away_score}
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </PrototypeTemplate>
  )
}
