// src/app/(dashboard)/analytics/overview/page.tsx
// League Overview - Production Page

import Link from 'next/link'
import { createClient } from '@/lib/supabase/server'
import { getCurrentSeason } from '@/lib/supabase/queries/league'
import { getTeams } from '@/lib/supabase/queries/teams'
import { getPlayers } from '@/lib/supabase/queries/players'
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
import { TeamLogo } from '@/components/teams/team-logo'
import { PlayerPhoto } from '@/components/players/player-photo'
import { cn } from '@/lib/utils'

export const revalidate = 300

export const metadata = {
  title: 'League Overview | BenchSight',
  description: 'Complete league-wide statistics and key metrics for NORAD Hockey',
}

export default async function LeagueOverviewPage() {
  const supabase = await createClient()
  
  // Get current season ID to filter leaderboards
  const currentSeasonId = await getCurrentSeason()
  
  // Fetch all macro data with error handling
  const [
    leagueSummary,
    standings,
    pointsLeaders,
    goalsLeaders,
    assistsLeaders,
    goalieLeaders,
    recentGames,
    teams,
    players
  ] = await Promise.all([
    supabase.from('v_summary_league').select('*').single(),
    supabase.from('v_standings_current').select('*').order('standing', { ascending: true }),
    currentSeasonId 
      ? supabase.from('v_leaderboard_points').select('*').eq('season_id', currentSeasonId).order('season_rank', { ascending: true }).limit(5)
      : supabase.from('v_leaderboard_points').select('*').order('season_rank', { ascending: true }).limit(5),
    currentSeasonId
      ? supabase.from('v_leaderboard_goals').select('*').eq('season_id', currentSeasonId).order('season_rank', { ascending: true }).limit(5)
      : supabase.from('v_leaderboard_goals').select('*').order('season_rank', { ascending: true }).limit(5),
    currentSeasonId
      ? supabase.from('v_leaderboard_assists').select('*').eq('season_id', currentSeasonId).order('season_rank', { ascending: true }).limit(5)
      : supabase.from('v_leaderboard_assists').select('*').order('season_rank', { ascending: true }).limit(5),
    currentSeasonId
      ? supabase.from('v_leaderboard_goalie_wins').select('*').eq('season_id', currentSeasonId).order('wins', { ascending: false }).limit(5)
      : supabase.from('v_leaderboard_goalie_wins').select('*').order('wins', { ascending: false }).limit(5),
    supabase.from('v_recent_games').select('*').limit(5),
    getTeams(),
    getPlayers(),
  ])

  const summary = leagueSummary.data
  const standingsData = standings.data || []
  const topPoints = pointsLeaders.data || []
  const topGoals = goalsLeaders.data || []
  const topAssists = assistsLeaders.data || []
  const topGoalies = goalieLeaders.data || []
  const recent = recentGames.data || []
  const teamsList = teams || []
  const playersList = players || []
  
  // Create lookup maps for team and player data
  // Note: team_id might be string or number, so we handle both
  const teamsMap = new Map(teamsList.map(t => [String(t.team_id), t]))
  const playersMap = new Map(playersList.map(p => [String(p.player_id), p]))

  // Calculate league averages
  const avgGoalsPerGame = summary 
    ? (summary.total_goals / (summary.total_games || 1)).toFixed(2)
    : '0.00'
  
  const avgPointsPerPlayer = summary
    ? (summary.total_points / (summary.total_players || 1)).toFixed(1)
    : '0.0'

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="font-display text-2xl font-bold tracking-wider uppercase flex items-center gap-3">
          <span className="w-1 h-6 bg-primary rounded" />
          League Overview
        </h1>
        <p className="text-sm text-muted-foreground mt-2 ml-4">
          Complete league-wide statistics and key metrics
        </p>
      </div>

      {/* Key Metrics */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <div className="bg-card rounded-lg p-4 border border-border">
            <div className="flex items-center gap-2 mb-2">
              <Users className="w-4 h-4 text-primary" />
              <span className="text-xs font-mono text-muted-foreground uppercase">Teams</span>
            </div>
            <div className="font-mono text-2xl font-bold text-foreground">{summary.total_teams || 0}</div>
          </div>
          <div className="bg-card rounded-lg p-4 border border-border">
            <div className="flex items-center gap-2 mb-2">
              <Users className="w-4 h-4 text-assist" />
              <span className="text-xs font-mono text-muted-foreground uppercase">Players</span>
            </div>
            <div className="font-mono text-2xl font-bold text-foreground">{summary.total_players || 0}</div>
          </div>
          <div className="bg-card rounded-lg p-4 border border-border">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="w-4 h-4 text-save" />
              <span className="text-xs font-mono text-muted-foreground uppercase">Games</span>
            </div>
            <div className="font-mono text-2xl font-bold text-foreground">{summary.total_games || 0}</div>
          </div>
          <div className="bg-card rounded-lg p-4 border border-border">
            <div className="flex items-center gap-2 mb-2">
              <Target className="w-4 h-4 text-goal" />
              <span className="text-xs font-mono text-muted-foreground uppercase">Goals</span>
            </div>
            <div className="font-mono text-2xl font-bold text-goal">{summary.total_goals || 0}</div>
          </div>
          <div className="bg-card rounded-lg p-4 border border-border">
            <div className="flex items-center gap-2 mb-2">
              <BarChart3 className="w-4 h-4 text-primary" />
              <span className="text-xs font-mono text-muted-foreground uppercase">Avg G/GP</span>
            </div>
            <div className="font-mono text-2xl font-bold text-foreground">{avgGoalsPerGame}</div>
          </div>
          <div className="bg-card rounded-lg p-4 border border-border">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-4 h-4 text-assist" />
              <span className="text-xs font-mono text-muted-foreground uppercase">Avg P/Player</span>
            </div>
            <div className="font-mono text-2xl font-bold text-foreground">{avgPointsPerPlayer}</div>
          </div>
        </div>
      )}

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
          {standingsData.length > 0 ? standingsData.slice(0, 5).map((team, idx) => {
            const teamInfo = teamsMap.get(String(team.team_id))
            return (
              <div
                key={team.team_id}
                className={cn(
                  'flex items-center justify-between p-3 rounded-lg border transition-colors hover:bg-muted/50',
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
                  <TeamLogo
                    src={teamInfo?.team_logo || null}
                    name={team.team_name || ''}
                    abbrev={teamInfo?.team_cd}
                    primaryColor={teamInfo?.primary_color || teamInfo?.team_color1}
                    secondaryColor={teamInfo?.team_color2}
                    size="sm"
                  />
                  {team.team_name ? (
                    <Link 
                      href={`/team/${team.team_name.replace(/\s+/g, '_')}`}
                      className="font-display text-sm hover:text-primary transition-colors"
                    >
                      {team.team_name}
                    </Link>
                  ) : (
                    <span className="font-display text-sm text-foreground">
                      {team.team_name || '-'}
                    </span>
                  )}
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
            )
          }) : (
            <div className="text-center py-8 text-muted-foreground text-sm">
              No standings data available
            </div>
          )}
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
            {topPoints.length > 0 ? topPoints.map((player, idx) => {
              const playerInfo = playersMap.get(String(player.player_id))
              if (!player.player_id) return null
              return (
                <Link
                  key={`points-${player.player_id}`}
                  href={`/players/${player.player_id}`}
                  className="flex items-center justify-between p-2 rounded hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-muted-foreground w-4">
                      {idx + 1}
                    </span>
                    <PlayerPhoto
                      src={playerInfo?.player_image || null}
                      name={player.player_name || ''}
                      primaryColor={null}
                      size="sm"
                    />
                    <span className="text-sm hover:text-primary transition-colors">
                      {player.player_name}
                    </span>
                  </div>
                  <span className="font-mono font-semibold text-primary">
                    {player.points}
                  </span>
                </Link>
              )
            }) : (
              <div className="text-center py-4 text-muted-foreground text-sm">
                No data available
              </div>
            )}
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
            {topGoals.length > 0 ? topGoals.map((player, idx) => {
              const playerInfo = playersMap.get(String(player.player_id))
              if (!player.player_id) return null
              return (
                <Link
                  key={`goals-${player.player_id}`}
                  href={`/players/${player.player_id}`}
                  className="flex items-center justify-between p-2 rounded hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-muted-foreground w-4">
                      {idx + 1}
                    </span>
                    <PlayerPhoto
                      src={playerInfo?.player_image || null}
                      name={player.player_name || ''}
                      primaryColor={null}
                      size="sm"
                    />
                    <span className="text-sm hover:text-primary transition-colors">
                      {player.player_name}
                    </span>
                  </div>
                  <span className="font-mono font-semibold text-goal">
                    {player.goals}
                  </span>
                </Link>
              )
            }) : (
              <div className="text-center py-4 text-muted-foreground text-sm">
                No data available
              </div>
            )}
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
            {topGoalies.length > 0 ? topGoalies.map((goalie, idx) => {
              const playerInfo = playersMap.get(String(goalie.player_id))
              if (!goalie.player_id) return null
              return (
                <Link
                  key={`goalie-${goalie.player_id}`}
                  href={`/players/${goalie.player_id}`}
                  className="flex items-center justify-between p-2 rounded hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-muted-foreground w-4">
                      {idx + 1}
                    </span>
                    <PlayerPhoto
                      src={playerInfo?.player_image || null}
                      name={goalie.player_name || ''}
                      primaryColor={playerInfo?.primary_color}
                      size="sm"
                    />
                    <span className="text-sm hover:text-primary transition-colors">
                      {goalie.player_name}
                    </span>
                  </div>
                  <span className="font-mono font-semibold text-save">
                    {goalie.wins}W
                  </span>
                </Link>
              )
            }) : (
              <div className="text-center py-4 text-muted-foreground text-sm">
                No data available
              </div>
            )}
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
            {recent.map((game: any) => {
              if (!game.game_id) return null
              return (
                <Link
                  key={game.game_id}
                  href={`/games/${game.game_id}`}
                  className="flex items-center justify-between p-3 rounded border border-border hover:bg-muted/50 transition-colors"
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
              </Link>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
