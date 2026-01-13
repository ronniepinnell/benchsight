// src/app/(dashboard)/teams/[teamId]/page.tsx
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getTeamById, getStandings, getTeamHistory } from '@/lib/supabase/queries/teams'
import { getRecentGames } from '@/lib/supabase/queries/games'
import { getPlayers } from '@/lib/supabase/queries/players'
import { createClient } from '@/lib/supabase/server'
import { ArrowLeft, Users, Trophy, Calendar, TrendingUp, Target } from 'lucide-react'
import { cn } from '@/lib/utils'
import { TeamLogo } from '@/components/teams/team-logo'
import { PlayerPhoto } from '@/components/players/player-photo'

export const revalidate = 300

export async function generateMetadata({ params }: { params: Promise<{ teamId: string }> }) {
  const { teamId } = await params
  const supabase = await createClient()
  const { data: team } = await supabase
    .from('dim_team')
    .select('team_name')
    .eq('team_id', teamId)
    .single()
    
  return {
    title: team ? `${team.team_name} | BenchSight` : 'Team | BenchSight',
    description: team ? `${team.team_name} team profile and statistics` : 'Team profile',
  }
}

export default async function TeamDetailPage({ 
  params 
}: { 
  params: Promise<{ teamId: string }> 
}) {
  const { teamId } = await params
  
  if (!teamId) {
    notFound()
  }
  
  const supabase = await createClient()
  
  // Fetch team data
  const [team, standings, games, players] = await Promise.all([
    getTeamById(teamId),
    getStandings(),
    getRecentGames(50), // Get more games to filter
    getPlayers()
  ])
  
  if (!team) {
    notFound()
  }
  
  // Get team standing
  const teamStanding = standings.find(s => s.team_id === teamId)
  
  // Get team's games - handle both string and numeric team IDs
  const teamGames = games.filter(g => {
    if (!g.home_team_id || !g.away_team_id) return false
    const homeId = String(g.home_team_id)
    const awayId = String(g.away_team_id)
    return homeId === teamId || awayId === teamId
  }).slice(0, 10)
  
  // Fetch roster from fact_player_game_stats (players who played for this team)
  const { data: roster } = await supabase
    .from('v_rankings_players_current')
    .select('*')
    .eq('team_id', teamId)
    .order('points', { ascending: false })
  
  // Fetch goalies
  const { data: goalies } = await supabase
    .from('v_leaderboard_goalie_gaa')
    .select('*')
    .eq('team_id', teamId)
    .order('gaa', { ascending: true })
  
  // Create players map for photos
  const playersMap = new Map(players.map(p => [String(p.player_id), p]))
  
  // Get opponent team info for recent games
  const opponentIds = [...new Set(teamGames.map(g => {
    if (!g.home_team_id || !g.away_team_id) return null
    const homeId = String(g.home_team_id)
    const awayId = String(g.away_team_id)
    return homeId === teamId ? awayId : homeId
  }))].filter((id): id is string => Boolean(id))
  const opponentTeams = await Promise.all(
    opponentIds.map(id => getTeamById(String(id)))
  )
  const opponentTeamsMap = new Map(
    opponentTeams.filter(Boolean).map(t => [String(t!.team_id), t!])
  )
  
  const wins = teamStanding?.wins ?? 0
  const losses = teamStanding?.losses ?? 0
  const ties = teamStanding?.ties ?? 0
  const goalsFor = teamStanding?.goals_for ?? 0
  const goalsAgainst = teamStanding?.goals_against ?? 0
  const differential = goalsFor - goalsAgainst
  const points = teamStanding?.points ?? (wins * 2 + ties)
  const gamesPlayed = teamStanding?.games_played ?? 0
  // Win percentage = points / (games_played * 2) * 100
  const winPct = gamesPlayed > 0 ? (points / (gamesPlayed * 2)) * 100 : 0
  
  return (
    <div className="space-y-6">
      {/* Back Link */}
      <Link 
        href="/teams" 
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Teams
      </Link>
      
      {/* Team Header */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div 
          className="h-3"
          style={{ backgroundColor: team.primary_color || team.team_color1 || '#3b82f6' }}
        />
        <div className="p-6">
          <div className="flex items-center gap-6">
            <TeamLogo
              src={team.team_logo || null}
              name={team.team_name || ''}
              abbrev={team.team_cd}
              primaryColor={team.primary_color || team.team_color1}
              secondaryColor={team.team_color2}
              size="xl"
            />
            <div>
              <h1 className="font-display text-3xl font-bold tracking-wider text-foreground">
                {team.team_name}
              </h1>
              {teamStanding && (
                <div className="flex items-center gap-4 mt-2">
                  <div className="flex items-center gap-2">
                    <Trophy className="w-4 h-4 text-assist" />
                    <span className="text-sm text-muted-foreground">
                      #{teamStanding.standing} in standings
                    </span>
                  </div>
                  <span className="text-sm font-mono text-muted-foreground">
                    {teamStanding.games_played} GP
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      
      {/* Stats Overview */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-card rounded-lg p-4 border border-border text-center">
          <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Record</div>
          <div className="font-display text-2xl font-bold text-foreground">
            {wins}-{losses}-{ties}
          </div>
        </div>
        <div className="bg-card rounded-lg p-4 border border-border text-center">
          <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Win %</div>
          <div className="font-mono text-2xl font-bold text-primary">
            {winPct.toFixed(1)}%
          </div>
        </div>
        <div className="bg-card rounded-lg p-4 border border-border text-center">
          <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Goals For</div>
          <div className="font-mono text-2xl font-bold text-save">{goalsFor}</div>
        </div>
        <div className="bg-card rounded-lg p-4 border border-border text-center">
          <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Goals Against</div>
          <div className="font-mono text-2xl font-bold text-goal">{goalsAgainst}</div>
        </div>
        <div className="bg-card rounded-lg p-4 border border-border text-center">
          <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Differential</div>
          <div className={cn(
            'font-mono text-2xl font-bold',
            differential > 0 && 'text-save',
            differential < 0 && 'text-goal',
            differential === 0 && 'text-muted-foreground'
          )}>
            {differential > 0 ? '+' : ''}{differential}
          </div>
        </div>
      </div>
      
      {/* Content Grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Roster */}
        <div className="lg:col-span-2 bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Users className="w-4 h-4" />
              Roster ({roster?.length ?? 0} skaters)
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-accent/50">
                  <th className="px-3 py-2 text-left font-display text-xs text-muted-foreground">Player</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">GP</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-goal">G</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-assist">A</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-primary">P</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">P/G</th>
                </tr>
              </thead>
              <tbody>
                {roster?.slice(0, 15).map((player) => {
                  const playerInfo = playersMap.get(String(player.player_id))
                  return (
                    <tr key={player.player_id} className="border-b border-border hover:bg-muted/50">
                      <td className="px-3 py-2">
                        <Link 
                          href={`/players/${player.player_id}`}
                          className="flex items-center gap-2 text-foreground hover:text-primary transition-colors"
                        >
                          <PlayerPhoto
                            src={playerInfo?.player_image || null}
                            name={player.player_name || ''}
                            primaryColor={team.primary_color || team.team_color1}
                            size="sm"
                          />
                          <span>{player.player_name}</span>
                        </Link>
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-muted-foreground">{player.games_played}</td>
                      <td className="px-2 py-2 text-center font-mono text-goal font-semibold">{player.goals}</td>
                      <td className="px-2 py-2 text-center font-mono text-assist">{player.assists}</td>
                      <td className="px-2 py-2 text-center font-mono text-primary font-semibold">{player.points}</td>
                      <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                        {player.points_per_game?.toFixed(2) ?? '-'}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
        
        {/* Sidebar */}
        <div className="space-y-6">
          {/* Goalies */}
          {goalies && goalies.length > 0 && (
            <div className="bg-card rounded-xl border border-border overflow-hidden">
              <div className="px-4 py-3 bg-accent border-b border-border">
                <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                  <Target className="w-4 h-4 text-save" />
                  Goaltending
                </h2>
              </div>
              <div className="divide-y divide-border">
                {goalies.map((goalie) => {
                  const goalieInfo = playersMap.get(String(goalie.player_id))
                  return (
                    <Link
                      key={goalie.player_id}
                      href={`/players/${goalie.player_id}`}
                      className="flex items-center gap-3 p-3 hover:bg-muted/50 transition-colors"
                    >
                      <PlayerPhoto
                        src={goalieInfo?.player_image || null}
                        name={goalie.player_name || ''}
                        primaryColor={team.primary_color || team.team_color1}
                        size="sm"
                      />
                      <div className="flex-1">
                        <div className="font-display text-sm font-semibold text-foreground">
                          {goalie.player_name}
                        </div>
                        <div className="flex items-center gap-4 mt-1 text-xs font-mono">
                          <span className="text-muted-foreground">{goalie.games_played} GP</span>
                          <span className="text-primary">{goalie.gaa?.toFixed(2)} GAA</span>
                          <span className="text-save">{goalie.save_pct ? (goalie.save_pct * 100).toFixed(1) : '-'}%</span>
                        </div>
                      </div>
                    </Link>
                  )
                })}
              </div>
            </div>
          )}
          
          {/* Recent Games */}
          <div className="bg-card rounded-xl border border-border overflow-hidden">
            <div className="px-4 py-3 bg-accent border-b border-border">
              <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                Recent Games
              </h2>
            </div>
            <div className="divide-y divide-border">
              {teamGames.slice(0, 5).map((game) => {
                if (!game.home_team_id || !game.away_team_id || !game.game_id) return null
                
                const homeId = String(game.home_team_id)
                const awayId = String(game.away_team_id)
                const isHome = homeId === teamId
                const teamGoals = isHome ? game.home_total_goals : game.away_total_goals
                const oppGoals = isHome ? game.away_total_goals : game.home_total_goals
                const opponentId = isHome ? awayId : homeId
                const opponentName = isHome ? game.away_team_name : game.home_team_name
                const won = teamGoals > oppGoals
                const gameDate = new Date(game.date).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                })
                
                // Get opponent team info for logo
                const opponentTeam = opponentId ? opponentTeamsMap.get(opponentId) : null
                
                return (
                  <Link
                    key={game.game_id}
                    href={`/games/${game.game_id}`}
                    className="block p-3 hover:bg-muted/50 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {opponentTeam && (
                          <TeamLogo
                            src={opponentTeam.team_logo || null}
                            name={opponentTeam.team_name || opponentName || ''}
                            abbrev={opponentTeam.team_cd}
                            primaryColor={opponentTeam.primary_color || opponentTeam.team_color1}
                            secondaryColor={opponentTeam.team_color2}
                            size="xs"
                          />
                        )}
                        <div>
                          <div className="text-xs font-mono text-muted-foreground">
                            {gameDate} • {isHome ? 'vs' : '@'}
                          </div>
                          <div className="font-display text-sm text-foreground">
                            {opponentName}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={cn(
                          'font-mono text-lg font-bold',
                          won ? 'text-save' : 'text-goal'
                        )}>
                          {teamGoals}-{oppGoals}
                        </div>
                        <div className={cn(
                          'text-xs font-mono uppercase',
                          won ? 'text-save' : 'text-goal'
                        )}>
                          {won ? 'W' : teamGoals === oppGoals ? 'T' : 'L'}
                        </div>
                      </div>
                    </div>
                  </Link>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
