// src/app/(dashboard)/teams/[teamId]/page.tsx
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getTeamById, getStandings, getTeamHistory } from '@/lib/supabase/queries/teams'
import { getRecentGames } from '@/lib/supabase/queries/games'
import { getPlayers } from '@/lib/supabase/queries/players'
import { getCurrentSeason } from '@/lib/supabase/queries/league'
import { createClient } from '@/lib/supabase/server'
import { ArrowLeft, Users, Trophy, Calendar, TrendingUp, Target, ExternalLink } from 'lucide-react'
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
  
  // Get current season to determine roster logic
  const currentSeasonId = await getCurrentSeason()
  
  // Determine if we're viewing current season or historical
  // For now, we'll assume current season (can add season selector later)
  const isCurrentSeason = true // TODO: Add season selector
  
  let roster: any[] = []
  let rosterGoalies: any[] = []
  let subSkaters: any[] = []
  let subGoalies: any[] = []
  
  // Get all players who played for this team from fact_gameroster
  // For current season, filter by current season ID if available
  let gameRosterQuery = supabase
    .from('fact_gameroster')
    .select('player_id, team_id, game_id, player_position, player_full_name, goals, assist, points, season_id')
    .eq('team_id', teamId)
  
  // If current season, filter by season_id
  if (isCurrentSeason && currentSeasonId) {
    gameRosterQuery = gameRosterQuery.eq('season_id', currentSeasonId)
  }
  
  const { data: allGameRoster } = await gameRosterQuery
  
  if (allGameRoster) {
    // Count games per player and aggregate stats
    const playerGameCounts = new Map<string, number>()
    const playerStats = new Map<string, { goals: number; assists: number; points: number; position?: string }>()
    
    allGameRoster.forEach(gr => {
      const pid = String(gr.player_id)
      playerGameCounts.set(pid, (playerGameCounts.get(pid) || 0) + 1)
      
      const existing = playerStats.get(pid) || { goals: 0, assists: 0, points: 0 }
      playerStats.set(pid, {
        goals: existing.goals + (Number(gr.goals) || 0),
        assists: existing.assists + (Number(gr.assist) || 0),
        points: existing.points + (Number(gr.points) || (Number(gr.goals) || 0) + (Number(gr.assist) || 0)),
        position: gr.player_position || existing.position,
      })
    })
    
    const allPlayerIds = Array.from(playerGameCounts.keys())
    
    if (allPlayerIds.length > 0) {
      // Get player details
      const { data: allPlayers } = await supabase
        .from('dim_player')
        .select('*')
        .in('player_id', allPlayerIds)
      
      const playersMap = new Map((allPlayers || []).map(p => [String(p.player_id), p]))
      
      // Separate into goalies and skaters
      const goalieIds: string[] = []
      const skaterIds: string[] = []
      
      allPlayerIds.forEach(pid => {
        const player = playersMap.get(pid)
        const stats = playerStats.get(pid)
        const position = player?.player_primary_position || stats?.position || ''
        const isGoalie = position && position.toLowerCase().includes('goalie')
        
        if (isGoalie) {
          goalieIds.push(pid)
        } else {
          skaterIds.push(pid)
        }
      })
      
      if (isCurrentSeason && currentSeasonId) {
        // CURRENT SEASON: Main roster from dim_player.current_team
        const { data: mainRosterPlayers } = await supabase
          .from('dim_player')
          .select('*')
          .eq('player_norad_current_team_id', teamId)
          .not('player_norad_current_team_id', 'is', null)
        
        const mainRosterPlayerIds = new Set((mainRosterPlayers || []).map(p => String(p.player_id)))
        
        // Separate main roster skaters and goalies
        const mainRosterSkaterIds = skaterIds.filter(id => mainRosterPlayerIds.has(id))
        const mainRosterGoalieIds = goalieIds.filter(id => mainRosterPlayerIds.has(id))
        
        // Get stats for main roster players
        if (mainRosterSkaterIds.length > 0) {
          const { data: rosterStats } = await supabase
            .from('v_rankings_players_current')
            .select('*')
            .in('player_id', mainRosterSkaterIds)
            .eq('team_id', teamId)
          
          const statsMap = new Map((rosterStats || []).map(s => [String(s.player_id), s]))
          roster = mainRosterSkaterIds.map(pid => {
            const player = playersMap.get(pid)
            const stats = statsMap.get(pid) || playerStats.get(pid)
            const games = playerGameCounts.get(pid) || 0
            return {
              ...player,
              ...stats,
              player_id: pid,
              player_name: player?.player_name || player?.player_full_name || '',
              games_played: stats?.games_played ?? games,
              goals: stats?.goals ?? (playerStats.get(pid)?.goals || 0),
              assists: stats?.assists ?? (playerStats.get(pid)?.assists || 0),
              points: stats?.points ?? (playerStats.get(pid)?.points || 0),
              points_per_game: stats?.points_per_game ?? (games > 0 ? ((playerStats.get(pid)?.points || 0) / games) : 0),
              jersey_number: player?.jersey_number,
              current_skill_rating: player?.current_skill_rating,
              player_primary_position: player?.player_primary_position,
            }
          }).filter(p => p.player_id).sort((a, b) => (b.points ?? 0) - (a.points ?? 0))
        }
        
        // Get main roster goalies
        if (mainRosterGoalieIds.length > 0) {
          const { data: goalieStats } = await supabase
            .from('v_leaderboard_goalie_gaa')
            .select('*')
            .in('player_id', mainRosterGoalieIds)
            .eq('team_id', teamId)
          
          const statsMap = new Map((goalieStats || []).map(s => [String(s.player_id), s]))
          rosterGoalies = mainRosterGoalieIds.map(pid => {
            const player = playersMap.get(pid)
            const stats = statsMap.get(pid)
            const games = playerGameCounts.get(pid) || 0
            return {
              ...player,
              ...stats,
              player_id: pid,
              player_name: player?.player_name || player?.player_full_name || '',
              games_played: stats?.games_played ?? games,
              gaa: stats?.gaa ?? null,
              save_pct: stats?.save_pct ?? null,
              jersey_number: player?.jersey_number,
              current_skill_rating: player?.current_skill_rating,
              player_primary_position: player?.player_primary_position,
            }
          }).filter(p => p.player_id).sort((a, b) => (a.gaa ?? 999) - (b.gaa ?? 999))
        }
        
        // SUBS: Players who played games but aren't on main roster (1+ games)
        const subSkaterIds = skaterIds.filter(id => !mainRosterPlayerIds.has(id))
        const subGoalieIds = goalieIds.filter(id => !mainRosterPlayerIds.has(id))
        
        if (subSkaterIds.length > 0) {
          const { data: subStats } = await supabase
            .from('v_rankings_players_current')
            .select('*')
            .in('player_id', subSkaterIds)
            .eq('team_id', teamId)
          
          const statsMap = new Map((subStats || []).map(s => [String(s.player_id), s]))
          subSkaters = subSkaterIds.map(pid => {
            const player = playersMap.get(pid)
            const stats = statsMap.get(pid) || playerStats.get(pid)
            const games = playerGameCounts.get(pid) || 0
            return {
              ...player,
              ...stats,
              player_id: pid,
              player_name: player?.player_name || player?.player_full_name || '',
              games_played: games,
              goals: stats?.goals ?? (playerStats.get(pid)?.goals || 0),
              assists: stats?.assists ?? (playerStats.get(pid)?.assists || 0),
              points: stats?.points ?? (playerStats.get(pid)?.points || 0),
              points_per_game: games > 0 ? ((playerStats.get(pid)?.points || 0) / games) : 0,
              jersey_number: player?.jersey_number,
              current_skill_rating: player?.current_skill_rating,
              player_primary_position: player?.player_primary_position,
            }
          }).filter(p => p.player_id).sort((a, b) => (b.points ?? 0) - (a.points ?? 0))
        }
        
        if (subGoalieIds.length > 0) {
          const { data: subGoalieStats } = await supabase
            .from('v_leaderboard_goalie_gaa')
            .select('*')
            .in('player_id', subGoalieIds)
            .eq('team_id', teamId)
          
          const statsMap = new Map((subGoalieStats || []).map(s => [String(s.player_id), s]))
          subGoalies = subGoalieIds.map(pid => {
            const player = playersMap.get(pid)
            const stats = statsMap.get(pid)
            const games = playerGameCounts.get(pid) || 0
            return {
              ...player,
              ...stats,
              player_id: pid,
              player_name: player?.player_name || player?.player_full_name || '',
              games_played: games,
              gaa: stats?.gaa ?? null,
              save_pct: stats?.save_pct ?? null,
              jersey_number: player?.jersey_number,
              current_skill_rating: player?.current_skill_rating,
              player_primary_position: player?.player_primary_position,
            }
          }).filter(p => p.player_id).sort((a, b) => (a.gaa ?? 999) - (b.gaa ?? 999))
        }
      } else {
        // PRIOR SEASONS: Count games played, 5+ = main roster, <5 = subs
        // Reuse allGameRoster from above, but we need to get player positions
        if (allGameRoster && allGameRoster.length > 0) {
          // PRIOR SEASONS: Separate main roster (5+ games) and subs (<5 games)
          // Note: playerGameCounts was already populated above at line 95
          const mainRosterSkaterIds: string[] = []
          const mainRosterGoalieIds: string[] = []
          const subSkaterIds: string[] = []
          const subGoalieIds: string[] = []
          
          playerGameCounts.forEach((games, playerId) => {
            const isGoalie = goalieIds.includes(playerId)
            if (games >= 5) {
              if (isGoalie) {
                mainRosterGoalieIds.push(playerId)
              } else {
                mainRosterSkaterIds.push(playerId)
              }
            } else {
              if (isGoalie) {
                subGoalieIds.push(playerId)
              } else {
                subSkaterIds.push(playerId)
              }
            }
          })
          
          // Fetch main roster skaters
          if (mainRosterSkaterIds.length > 0) {
            const { data: mainStats } = await supabase
              .from('fact_player_game_stats')
              .select('player_id, goals, assists, points')
              .in('player_id', mainRosterSkaterIds)
              .eq('team_id', teamId)
            
            const statsMap = new Map<string, any>()
            ;(mainStats || []).forEach(stat => {
              const pid = String(stat.player_id)
              const existing = statsMap.get(pid) || { goals: 0, assists: 0, points: 0 }
              statsMap.set(pid, {
                goals: existing.goals + (Number(stat.goals) || 0),
                assists: existing.assists + (Number(stat.assists) || 0),
                points: existing.points + (Number(stat.points) || 0),
              })
            })
            
            roster = mainRosterSkaterIds.map(pid => {
              const player = playersMap.get(pid)
              const stats = statsMap.get(pid) || playerStats.get(pid) || { goals: 0, assists: 0, points: 0 }
              const games = playerGameCounts.get(pid) || 0
              return {
                ...player,
                ...stats,
                player_id: pid,
                player_name: player?.player_name || player?.player_full_name || '',
                games_played: games,
                points_per_game: games > 0 ? (stats.points / games) : 0,
              }
            }).filter(p => p.player_id).sort((a, b) => (b.points ?? 0) - (a.points ?? 0))
          }
          
          // Fetch main roster goalies
          if (mainRosterGoalieIds.length > 0) {
            const { data: goalieStats } = await supabase
              .from('v_leaderboard_goalie_gaa')
              .select('*')
              .in('player_id', mainRosterGoalieIds)
              .eq('team_id', teamId)
            
            const statsMap = new Map((goalieStats || []).map(s => [String(s.player_id), s]))
            rosterGoalies = mainRosterGoalieIds.map(pid => {
              const player = playersMap.get(pid)
              const stats = statsMap.get(pid)
              const games = playerGameCounts.get(pid) || 0
              return {
                ...player,
                ...stats,
                player_id: pid,
                player_name: player?.player_name || player?.player_full_name || '',
                games_played: stats?.games_played ?? games,
                gaa: stats?.gaa ?? 0,
                save_pct: stats?.save_pct ?? 0,
              }
            }).filter(p => p.player_id).sort((a, b) => (a.gaa ?? 999) - (b.gaa ?? 999))
          }
          
          // Fetch sub skaters
          if (subSkaterIds.length > 0) {
            const { data: subStats } = await supabase
              .from('fact_player_game_stats')
              .select('player_id, goals, assists, points')
              .in('player_id', subSkaterIds)
              .eq('team_id', teamId)
            
            const statsMap = new Map<string, any>()
            ;(subStats || []).forEach(stat => {
              const pid = String(stat.player_id)
              const existing = statsMap.get(pid) || { goals: 0, assists: 0, points: 0 }
              statsMap.set(pid, {
                goals: existing.goals + (Number(stat.goals) || 0),
                assists: existing.assists + (Number(stat.assists) || 0),
                points: existing.points + (Number(stat.points) || 0),
              })
            })
            
            subSkaters = subSkaterIds.map(pid => {
              const player = playersMap.get(pid)
              const stats = statsMap.get(pid) || playerStats.get(pid) || { goals: 0, assists: 0, points: 0 }
              const games = playerGameCounts.get(pid) || 0
              return {
                ...player,
                ...stats,
                player_id: pid,
                player_name: player?.player_name || player?.player_full_name || '',
                games_played: games,
                points_per_game: games > 0 ? (stats.points / games) : 0,
              }
            }).filter(p => p.player_id).sort((a, b) => (b.points ?? 0) - (a.points ?? 0))
          }
          
          // Fetch sub goalies
          if (subGoalieIds.length > 0) {
            const { data: subGoalieStats } = await supabase
              .from('v_leaderboard_goalie_gaa')
              .select('*')
              .in('player_id', subGoalieIds)
              .eq('team_id', teamId)
            
            const statsMap = new Map((subGoalieStats || []).map(s => [String(s.player_id), s]))
            subGoalies = subGoalieIds.map(pid => {
              const player = playersMap.get(pid)
              const stats = statsMap.get(pid)
              const games = playerGameCounts.get(pid) || 0
              return {
                ...player,
                ...stats,
                player_id: pid,
                player_name: player?.player_name || player?.player_full_name || '',
                games_played: games,
                gaa: stats?.gaa ?? 0,
                save_pct: stats?.save_pct ?? 0,
              }
            }).filter(p => p.player_id).sort((a, b) => (a.gaa ?? 999) - (b.gaa ?? 999))
          }
        }
      }
    }
  }
  
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
        href="/norad/teams" 
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
              <div className="flex items-center gap-3">
                <h1 className="font-display text-3xl font-bold tracking-wider text-foreground">
                  {team.team_name}
                </h1>
                {team.team_url && (
                  <a
                    href={team.team_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-primary transition-colors"
                    title="View on NORAD Hockey"
                  >
                    <ExternalLink className="w-4 h-4" />
                    <span>View on NORAD</span>
                  </a>
                )}
              </div>
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
        <div className="lg:col-span-2 space-y-4">
          {/* Main Roster */}
          <div className="bg-card rounded-xl border border-border overflow-hidden">
            <div className="px-4 py-3 bg-accent border-b border-border">
              <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                <Users className="w-4 h-4" />
                {isCurrentSeason ? 'Roster' : 'Main Roster (5+ games)'} ({roster?.length ?? 0} skaters)
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
                  {roster && roster.length > 0 ? (
                    roster.map((player) => {
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
                          <td className="px-2 py-2 text-center font-mono text-muted-foreground">{player.games_played ?? 0}</td>
                          <td className="px-2 py-2 text-center font-mono text-goal font-semibold">{player.goals ?? 0}</td>
                          <td className="px-2 py-2 text-center font-mono text-assist">{player.assists ?? 0}</td>
                          <td className="px-2 py-2 text-center font-mono text-primary font-semibold">{player.points ?? 0}</td>
                          <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                            {player.points_per_game ? player.points_per_game.toFixed(2) : '-'}
                          </td>
                        </tr>
                      )
                    })
                  ) : (
                    <tr>
                      <td colSpan={6} className="px-3 py-4 text-center text-sm text-muted-foreground">
                        No roster data available
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
          
          {/* Sub Skaters Section */}
          {subSkaters && subSkaters.length > 0 && (
            <div className="bg-card rounded-xl border border-border overflow-hidden">
              <div className="px-4 py-3 bg-accent border-b border-border">
                <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                  <Users className="w-4 h-4" />
                  {isCurrentSeason ? 'Sub Skaters' : 'Sub Skaters (<5 games)'} ({subSkaters.length})
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
                    {subSkaters.map((player) => {
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
                          <td className="px-2 py-2 text-center font-mono text-muted-foreground">{player.games_played ?? 0}</td>
                          <td className="px-2 py-2 text-center font-mono text-goal font-semibold">{player.goals ?? 0}</td>
                          <td className="px-2 py-2 text-center font-mono text-assist">{player.assists ?? 0}</td>
                          <td className="px-2 py-2 text-center font-mono text-primary font-semibold">{player.points ?? 0}</td>
                          <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                            {player.points_per_game ? player.points_per_game.toFixed(2) : '-'}
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
        
        {/* Sidebar */}
        <div className="space-y-6">
          {/* Main Roster Goalies */}
          {rosterGoalies && rosterGoalies.length > 0 && (
            <div className="bg-card rounded-xl border border-border overflow-hidden">
              <div className="px-4 py-3 bg-accent border-b border-border">
                <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                  <Target className="w-4 h-4 text-save" />
                  Goaltending ({rosterGoalies.length})
                </h2>
              </div>
              <div className="divide-y divide-border">
                {rosterGoalies.map((goalie) => {
                  const goalieInfo = playersMap.get(String(goalie.player_id))
                  return (
                    <Link
                      key={goalie.player_id}
                      href={`/norad/players/${goalie.player_id}`}
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
                          <span className="text-muted-foreground">{goalie.games_played ?? 0} GP</span>
                          <span className="text-primary">{goalie.gaa != null && goalie.gaa > 0 ? goalie.gaa.toFixed(2) : '-'} GAA</span>
                          <span className="text-save">{goalie.save_pct ? (goalie.save_pct * 100).toFixed(1) : '-'}%</span>
                        </div>
                      </div>
                    </Link>
                  )
                })}
              </div>
            </div>
          )}
          
          {/* Sub Goalies */}
          {subGoalies && subGoalies.length > 0 && (
            <div className="bg-card rounded-xl border border-border overflow-hidden">
              <div className="px-4 py-3 bg-accent border-b border-border">
                <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                  <Target className="w-4 h-4 text-muted-foreground" />
                  Sub Goalies ({subGoalies.length})
                </h2>
              </div>
              <div className="divide-y divide-border">
                {subGoalies.map((goalie) => {
                  const goalieInfo = playersMap.get(String(goalie.player_id))
                  return (
                    <Link
                      key={goalie.player_id}
                      href={`/norad/players/${goalie.player_id}`}
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
                          <span className="text-muted-foreground">{goalie.games_played ?? 0} GP</span>
                          <span className="text-primary">{goalie.gaa != null && goalie.gaa > 0 ? goalie.gaa.toFixed(2) : '-'} GAA</span>
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
                    href={`/norad/games/${game.game_id}`}
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
