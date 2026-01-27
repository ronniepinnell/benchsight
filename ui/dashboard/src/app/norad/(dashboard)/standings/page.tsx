// src/app/(dashboard)/standings/page.tsx
import { createClient } from '@/lib/supabase/server'
import { getStandings, getTeams } from '@/lib/supabase/queries/teams'
import { getLeagueSummary, getCurrentSeason } from '@/lib/supabase/queries/league'
import { Trophy, Target, Users, Calendar, History, Award } from 'lucide-react'
import { SortableStandingsTable } from '@/components/teams/sortable-standings-table'
import { AllTimeStandingsTable } from '@/components/teams/all-time-standings-table'
import Link from 'next/link'
import { cn } from '@/lib/utils'
import { TeamLogo } from '@/components/teams/team-logo'

export const revalidate = 300

export const metadata = {
  title: 'Standings | BenchSight',
  description: 'NORAD Hockey League standings',
}

export default async function StandingsPage({
  searchParams
}: {
  searchParams: Promise<{ tab?: string; season?: string; gameType?: string }>
}) {
  const params = await searchParams
  const activeTab = params.tab || 'current'
  const selectedSeason = params.season || null
  const selectedGameType = params.gameType || 'All'
  const supabase = await createClient()
  const currentSeason = await getCurrentSeason()
  
  const [standings, leagueSummary, teams, scheduleGamesResult] = await Promise.all([
    getStandings(),
    getLeagueSummary(),
    getTeams(),
    // Get all games from dim_schedule for current season with team IDs for proper matching
    // Only include 'Past' games (exclude 'Upcoming' and 'PPD')
    currentSeason
      ? supabase.from('dim_schedule').select('*').eq('season_id', currentSeason).eq('schedule_type', 'Past').not('home_total_goals', 'is', null).not('away_total_goals', 'is', null).order('date', { ascending: false })
      : supabase.from('dim_schedule').select('*').eq('schedule_type', 'Past').not('home_total_goals', 'is', null).not('away_total_goals', 'is', null).order('date', { ascending: false }).limit(1000)
  ])

  // Create team lookup maps - by ID and by name (for fallback)
  const teamsMap = new Map(teams.map(t => [String(t.team_id), t]))
  const teamsByNameMap = new Map(teams.map(t => [t.team_name, t]))
  const allGames = scheduleGamesResult.data || []
  
  // Log for debugging (remove in production)
  if (scheduleGamesResult.error) {
    console.error('Error fetching games:', scheduleGamesResult.error)
  }

  // Group games by team_id AND team_name for maximum compatibility
  const gamesByTeamId = new Map<string, any[]>()
  const gamesByTeamName = new Map<string, any[]>()
  
  allGames.forEach(game => {
    const homeTeamId = String(game.home_team_id || '')
    const awayTeamId = String(game.away_team_id || '')
    const homeTeamName = game.home_team_name || ''
    const awayTeamName = game.away_team_name || ''
    
    // Group by team_id
    if (homeTeamId && homeTeamId !== '') {
      if (!gamesByTeamId.has(homeTeamId)) {
        gamesByTeamId.set(homeTeamId, [])
      }
      gamesByTeamId.get(homeTeamId)!.push({ 
        ...game, 
        isHome: true,
        home_total_goals: Number(game.home_total_goals) || 0,
        away_total_goals: Number(game.away_total_goals) || 0
      })
    }
    if (awayTeamId && awayTeamId !== '') {
      if (!gamesByTeamId.has(awayTeamId)) {
        gamesByTeamId.set(awayTeamId, [])
      }
      gamesByTeamId.get(awayTeamId)!.push({ 
        ...game, 
        isHome: false,
        home_total_goals: Number(game.home_total_goals) || 0,
        away_total_goals: Number(game.away_total_goals) || 0
      })
    }
    
    // Also group by team_name as fallback
    if (homeTeamName) {
      if (!gamesByTeamName.has(homeTeamName)) {
        gamesByTeamName.set(homeTeamName, [])
      }
      gamesByTeamName.get(homeTeamName)!.push({ 
        ...game, 
        isHome: true,
        home_total_goals: Number(game.home_total_goals) || 0,
        away_total_goals: Number(game.away_total_goals) || 0
      })
    }
    if (awayTeamName) {
      if (!gamesByTeamName.has(awayTeamName)) {
        gamesByTeamName.set(awayTeamName, [])
      }
      gamesByTeamName.get(awayTeamName)!.push({ 
        ...game, 
        isHome: false,
        home_total_goals: Number(game.home_total_goals) || 0,
        away_total_goals: Number(game.away_total_goals) || 0
      })
    }
  })

  // Calculate streak and last 10 for each team
  const standingsWithStats = standings.map((team) => {
    const teamInfo = teamsMap.get(String(team.team_id))
    
    // Try to get games by team_id first, then fallback to team_name
    let teamGames = gamesByTeamId.get(String(team.team_id)) || []
    if (teamGames.length === 0) {
      // Fallback to team_name matching
      teamGames = gamesByTeamName.get(team.team_name) || []
    }
    
    // Filter to games with valid scores and get last 10 (most recent first)
    teamGames = teamGames
      .filter(g => {
        const homeGoals = Number(g.home_total_goals)
        const awayGoals = Number(g.away_total_goals)
        return !isNaN(homeGoals) && !isNaN(awayGoals) && homeGoals !== null && awayGoals !== null && homeGoals >= 0 && awayGoals >= 0
      })
      .sort((a, b) => {
        // Sort by date descending (most recent first)
        const dateA = new Date(a.date || a.game_date || 0).getTime()
        const dateB = new Date(b.date || b.game_date || 0).getTime()
        return dateB - dateA
      })
      .slice(0, 10)
    
    // Calculate last 10 record (W-L-T)
    const last10Wins = teamGames.filter(g => {
      const homeGoals = Number(g.home_total_goals) || 0
      const awayGoals = Number(g.away_total_goals) || 0
      if (g.isHome) {
        return homeGoals > awayGoals
      } else {
        return awayGoals > homeGoals
      }
    }).length
    const last10Losses = teamGames.filter(g => {
      const homeGoals = Number(g.home_total_goals) || 0
      const awayGoals = Number(g.away_total_goals) || 0
      if (g.isHome) {
        return homeGoals < awayGoals
      } else {
        return awayGoals < homeGoals
      }
    }).length
    const last10Ties = teamGames.filter(g => {
      const homeGoals = Number(g.home_total_goals) || 0
      const awayGoals = Number(g.away_total_goals) || 0
      return homeGoals === awayGoals
    }).length
    const last10 = teamGames.length > 0 ? `${last10Wins}-${last10Losses}-${last10Ties}` : '-'

    // Calculate streak (including ties)
    let streak = '-'
    if (teamGames.length > 0) {
      let streakCount = 0
      let streakType: 'W' | 'L' | 'T' | null = null
      
      for (const game of teamGames) {
        const homeGoals = Number(game.home_total_goals) || 0
        const awayGoals = Number(game.away_total_goals) || 0
        const isWin = game.isHome ? homeGoals > awayGoals : awayGoals > homeGoals
        const isTie = homeGoals === awayGoals
        
        let currentType: 'W' | 'L' | 'T'
        if (isTie) {
          currentType = 'T'
        } else {
          currentType = isWin ? 'W' : 'L'
        }
        
        if (streakType === null) {
          streakType = currentType
          streakCount = 1
        } else if (streakType === currentType) {
          streakCount++
        } else {
          break
        }
      }
      
      if (streakCount > 0 && streakType) {
        streak = `${streakType}${streakCount}`
      }
    }

    return {
      ...team,
      teamInfo,
      last_10: last10,
      streak,
    }
  })

  // Get all seasons for prior seasons tab
  const { data: allSeasonsData } = await supabase
    .from('fact_team_season_stats_basic')
    .select('season_id, season')
    .eq('game_type', 'All')
    .order('season', { ascending: false })
  
  const uniqueSeasons = allSeasonsData 
    ? [...new Map(allSeasonsData.map(s => [s.season_id, s])).values()]
        .filter(s => {
          const seasonStr = String(s.season || '')
          return !seasonStr.toLowerCase().includes('summer')
        })
    : []
  
  // Get champions and runner-ups (last game of each season) - MUST BE BEFORE priorSeasonsStandings loop
  const champions: Array<{
    season_id: string
    season: string
    champion_team_id: string
    champion_team_name: string
    runner_up_team_id: string
    runner_up_team_name: string
    game_id: number
    game_date: string
    home_team_id: string
    home_team_name: string
    away_team_id: string
    away_team_name: string
    home_total_goals: number
    away_total_goals: number
  }> = []
  
  for (const season of uniqueSeasons) {
    // Skip summer seasons
    const seasonStr = String(season.season || '')
    if (seasonStr.toLowerCase().includes('summer')) continue
    // Skip current season (champions don't exist yet)
    if (season.season_id === currentSeason) continue
    
    const { data: lastGame } = await supabase
      .from('dim_schedule')
      .select('*')
      .eq('season_id', season.season_id)
      .eq('schedule_type', 'Past')
      .not('home_total_goals', 'is', null)
      .not('away_total_goals', 'is', null)
      .order('date', { ascending: false })
      .order('game_id', { ascending: false })
      .limit(1)
      .single()
    
    if (lastGame) {
      const homeGoals = Number(lastGame.home_total_goals) || 0
      const awayGoals = Number(lastGame.away_total_goals) || 0
      
      if (homeGoals !== awayGoals) {
        const championId = homeGoals > awayGoals ? String(lastGame.home_team_id || '') : String(lastGame.away_team_id || '')
        const championName = homeGoals > awayGoals ? (lastGame.home_team_name || '') : (lastGame.away_team_name || '')
        const runnerUpId = homeGoals > awayGoals ? String(lastGame.away_team_id || '') : String(lastGame.home_team_id || '')
        const runnerUpName = homeGoals > awayGoals ? (lastGame.away_team_name || '') : (lastGame.home_team_name || '')
        
        champions.push({
          season_id: season.season_id,
          season: season.season,
          champion_team_id: championId,
          champion_team_name: championName,
          runner_up_team_id: runnerUpId,
          runner_up_team_name: runnerUpName,
          game_id: Number(lastGame.game_id) || 0,
          game_date: lastGame.date || lastGame.game_date || '',
          home_team_id: String(lastGame.home_team_id || ''),
          home_team_name: lastGame.home_team_name || '',
          away_team_id: String(lastGame.away_team_id || ''),
          away_team_name: lastGame.away_team_name || '',
          home_total_goals: homeGoals,
          away_total_goals: awayGoals,
        })
      }
    }
  }
  
  // Get prior seasons standings - fetch for All, Regular, and Playoffs
  const priorSeasonsStandings: Record<string, Record<string, any[]>> = {}
  const priorSeasonsChampions: Record<string, { champion_team_id?: string; runner_up_team_id?: string }> = {}
  
  for (const season of uniqueSeasons) {
    if (season.season_id === currentSeason) continue
    
    // Get champion and runner-up for this season
    const seasonChampion = champions.find(c => c.season_id === season.season_id)
    if (seasonChampion) {
      priorSeasonsChampions[season.season_id] = {
        champion_team_id: seasonChampion.champion_team_id,
        runner_up_team_id: seasonChampion.runner_up_team_id,
      }
    }
    
    // Fetch standings for All, Regular, and Playoffs
    const [allStandingsResult, regularStandingsResult, playoffStandingsResult] = await Promise.all([
      supabase
        .from('fact_team_season_stats_basic')
        .select('*')
        .eq('season_id', season.season_id)
        .eq('game_type', 'All')
        .order('points', { ascending: false })
        .order('wins', { ascending: false })
        .order('goal_diff', { ascending: false }),
      supabase
        .from('fact_team_season_stats_basic')
        .select('*')
        .eq('season_id', season.season_id)
        .eq('game_type', 'Regular')
        .order('points', { ascending: false })
        .order('wins', { ascending: false })
        .order('goal_diff', { ascending: false }),
      supabase
        .from('fact_team_season_stats_basic')
        .select('*')
        .eq('season_id', season.season_id)
        .eq('game_type', 'Playoffs')
        .order('points', { ascending: false })
        .order('wins', { ascending: false })
        .order('goal_diff', { ascending: false }),
    ])
    
    const allStandings = allStandingsResult.data || []
    const regularStandings = regularStandingsResult.data || []
    const playoffStandings = playoffStandingsResult.data || []
    
    // Process each game type
    const processStandings = (standings: any[], gameType: string) => {
      return standings.map((team, index) => ({
        ...team,
        standing: index + 1,
        teamInfo: teamsMap.get(String(team.team_id)),
        last_10: '-',
        streak: '-',
        game_type: gameType,
        isChampion: seasonChampion && String(team.team_id) === seasonChampion.champion_team_id,
        isRunnerUp: seasonChampion && String(team.team_id) === seasonChampion.runner_up_team_id,
      }))
    }
    
    priorSeasonsStandings[season.season_id] = {
      All: processStandings(allStandings, 'All'),
      Regular: processStandings(regularStandings, 'Regular'),
      Playoffs: processStandings(playoffStandings, 'Playoffs'),
    }
  }
  
  // Get all-time standings (team-season combinations)
  const { data: allTimeData } = await supabase
    .from('fact_team_season_stats_basic')
    .select('*')
    .eq('game_type', 'All')
    .order('win_pct', { ascending: false })
  
  const allTimeStandings = (allTimeData || [])
    .filter(t => {
      const seasonStr = String(t.season || '')
      return !seasonStr.toLowerCase().includes('summer')
    })
    .map((team, index) => {
    const teamInfo = teamsMap.get(String(team.team_id))
    const gfPerGame = team.games_played > 0 ? (Number(team.goals_for) || 0) / team.games_played : 0
    const gaPerGame = team.games_played > 0 ? (Number(team.goals_against) || 0) / team.games_played : 0
    const gfGaDiff = gfPerGame - gaPerGame
    
    return {
      ...team,
      teamInfo,
      team_season_name: `${team.team_name} ${team.season}`,
      rank: index + 1,
      gf_per_game: gfPerGame,
      ga_per_game: gaPerGame,
      gf_ga_diff: gfGaDiff,
      goals_for_abs: Number(team.goals_for) || 0,
      goals_against_abs: Number(team.goals_against) || 0,
      goal_diff_abs: Number(team.goal_diff) || 0,
    }
  })
  
  // Get game rosters for championship games
  const championshipGameIds = champions.map(c => c.game_id).filter(id => id > 0)
  const { data: championshipRosters } = championshipGameIds.length > 0
    ? await supabase
        .from('fact_gameroster')
        .select('*, player_game_number, sub, is_sub')
        .in('game_id', championshipGameIds)
    : { data: null }
  
  const rostersByGameId = new Map<number, any[]>()
  if (championshipRosters) {
    championshipRosters.forEach((r: any) => {
      const gameId = Number(r.game_id)
      if (!rostersByGameId.has(gameId)) {
        rostersByGameId.set(gameId, [])
      }
      rostersByGameId.get(gameId)!.push(r)
    })
  }
  
  // Get all player info for championship games
  const allChampionshipPlayerIds = championshipRosters 
    ? [...new Set(championshipRosters.map((r: any) => String(r.player_id)).filter(Boolean))]
    : []
  
  const { data: championshipPlayers } = allChampionshipPlayerIds.length > 0
    ? await supabase
        .from('dim_player')
        .select('player_id, player_full_name, current_skill_rating, jersey_number')
        .in('player_id', allChampionshipPlayerIds)
    : { data: null }
  
  const playersMapForChampions = new Map(
    (championshipPlayers || []).map((p: any) => [String(p.player_id), p])
  )

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold tracking-wider uppercase flex items-center gap-3">
          <span className="w-1 h-6 bg-primary rounded" />
          League Standings
        </h1>
        <p className="text-sm text-muted-foreground mt-2 ml-4">
          {activeTab === 'current' && 'Current season team rankings'}
          {activeTab === 'prior' && 'Historical season standings'}
          {activeTab === 'alltime' && 'All-time team-season rankings'}
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-border pb-2">
        <Link
          href="/norad/standings?tab=current"
          className={cn(
            'flex items-center gap-2 px-4 py-2 rounded-t-lg transition-all text-sm',
            activeTab === 'current'
              ? 'bg-muted border border-border text-foreground font-semibold'
              : 'hover:bg-muted/50 text-muted-foreground'
          )}
        >
          <Trophy className="w-4 h-4" />
          <span>Current Season</span>
        </Link>
        <Link
          href="/norad/standings?tab=prior"
          className={cn(
            'flex items-center gap-2 px-4 py-2 rounded-t-lg transition-all text-sm',
            activeTab === 'prior'
              ? 'bg-muted border border-border text-foreground font-semibold'
              : 'hover:bg-muted/50 text-muted-foreground'
          )}
        >
          <History className="w-4 h-4" />
          <span>Prior Seasons</span>
        </Link>
        <Link
          href="/norad/standings?tab=alltime"
          className={cn(
            'flex items-center gap-2 px-4 py-2 rounded-t-lg transition-all text-sm',
            activeTab === 'alltime'
              ? 'bg-muted border border-border text-foreground font-semibold'
              : 'hover:bg-muted/50 text-muted-foreground'
          )}
        >
          <Award className="w-4 h-4" />
          <span>All-Time</span>
        </Link>
        <Link
          href="/norad/standings?tab=champions"
          className={cn(
            'flex items-center gap-2 px-4 py-2 rounded-t-lg transition-all text-sm',
            activeTab === 'champions'
              ? 'bg-muted border border-border text-foreground font-semibold'
              : 'hover:bg-muted/50 text-muted-foreground'
          )}
        >
          <Trophy className="w-4 h-4" />
          <span>Champions</span>
        </Link>
      </div>

      {leagueSummary && activeTab === 'current' && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-card rounded-lg p-4 border border-border">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="w-4 h-4 text-primary" />
              <span className="text-xs font-mono text-muted-foreground uppercase">Games</span>
            </div>
            <div className="font-mono text-2xl font-bold text-foreground">{leagueSummary.total_games}</div>
          </div>
          <div className="bg-card rounded-lg p-4 border border-border">
            <div className="flex items-center gap-2 mb-2">
              <Target className="w-4 h-4 text-goal" />
              <span className="text-xs font-mono text-muted-foreground uppercase">Goals</span>
            </div>
            <div className="font-mono text-2xl font-bold text-goal">{leagueSummary.total_goals}</div>
          </div>
          <div className="bg-card rounded-lg p-4 border border-border">
            <div className="flex items-center gap-2 mb-2">
              <Trophy className="w-4 h-4 text-assist" />
              <span className="text-xs font-mono text-muted-foreground uppercase">Teams</span>
            </div>
            <div className="font-mono text-2xl font-bold text-foreground">{leagueSummary.total_teams}</div>
          </div>
          <div className="bg-card rounded-lg p-4 border border-border">
            <div className="flex items-center gap-2 mb-2">
              <Users className="w-4 h-4 text-shot" />
              <span className="text-xs font-mono text-muted-foreground uppercase">Players</span>
            </div>
            <div className="font-mono text-2xl font-bold text-foreground">{leagueSummary.total_players}</div>
          </div>
        </div>
      )}

      {activeTab === 'current' && (
        <SortableStandingsTable standings={standingsWithStats} />
      )}

      {activeTab === 'prior' && (
        <div className="space-y-8">
          {uniqueSeasons.filter(s => s.season_id !== currentSeason).map((season) => {
            const seasonStandingsData = priorSeasonsStandings[season.season_id] || {}
            // If this season is selected, use the selected game type, otherwise default to 'All'
            const currentGameType = selectedSeason === season.season_id ? selectedGameType : 'All'
            const seasonStandings = seasonStandingsData[currentGameType] || seasonStandingsData['All'] || []
            
            return (
              <div key={season.season_id} className="bg-card rounded-xl border border-border overflow-hidden">
                <div className="px-4 py-3 bg-accent border-b border-border">
                  <div className="flex items-center justify-between flex-wrap gap-4">
                    <h2 className="font-display text-lg font-semibold uppercase tracking-wider">
                      {season.season} Season
                    </h2>
                    {/* Game Type Filter */}
                    <div className="flex gap-2">
                      {['All', 'Regular', 'Playoffs'].map((gameType) => {
                        const params = new URLSearchParams()
                        params.set('tab', 'prior')
                        params.set('season', season.season_id)
                        if (gameType !== 'All') {
                          params.set('gameType', gameType)
                        }
                        const isActive = selectedSeason === season.season_id && currentGameType === gameType
                        return (
                          <Link
                            key={gameType}
                            href={`/norad/standings?${params.toString()}`}
                            className={cn(
                              'px-3 py-1 text-xs font-mono rounded transition-colors',
                              isActive
                                ? 'bg-primary text-primary-foreground font-semibold'
                                : 'bg-muted text-muted-foreground hover:bg-muted/80'
                            )}
                          >
                            {gameType}
                          </Link>
                        )
                      })}
                    </div>
                  </div>
                </div>
                {seasonStandings.length > 0 ? (
                  <SortableStandingsTable standings={seasonStandings} seasonId={season.season_id} />
                ) : (
                  <div className="p-8 text-center text-muted-foreground">
                    No standings data available for this season{currentGameType !== 'All' ? ` (${currentGameType})` : ''}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}

      {activeTab === 'alltime' && (
        <AllTimeStandingsTable standings={allTimeStandings} />
      )}

      {activeTab === 'champions' && (
        <div className="space-y-6">
          {champions.map((champ) => {
            const championTeam = teamsMap.get(champ.champion_team_id)
            const runnerUpTeam = teamsMap.get(champ.runner_up_team_id)
            const gameRoster = rostersByGameId.get(champ.game_id) || []
            
            // Separate roster by team
            const homeRoster = gameRoster.filter((r: any) => 
              String(r.team_id) === champ.home_team_id || r.team_name === champ.home_team_name
            )
            const awayRoster = gameRoster.filter((r: any) => 
              String(r.team_id) === champ.away_team_id || r.team_name === champ.away_team_name
            )
            
            // Separate players and goalies
            const homePlayers = homeRoster.filter((r: any) => {
              const pos = (r.player_position || '').toUpperCase()
              return pos !== 'G' && !r.goals_against
            })
            const homeGoalies = homeRoster.filter((r: any) => {
              const pos = (r.player_position || '').toUpperCase()
              return pos === 'G' || r.goals_against
            })
            const awayPlayers = awayRoster.filter((r: any) => {
              const pos = (r.player_position || '').toUpperCase()
              return pos !== 'G' && !r.goals_against
            })
            const awayGoalies = awayRoster.filter((r: any) => {
              const pos = (r.player_position || '').toUpperCase()
              return pos === 'G' || r.goals_against
            })
            
            // Separate forwards and defense
            const homeForwards = homePlayers.filter((r: any) => {
              const pos = (r.player_position || '').toUpperCase()
              return pos === 'F' || pos === 'C' || pos === 'LW' || pos === 'RW' || pos === 'W'
            })
            const homeDefense = homePlayers.filter((r: any) => {
              const pos = (r.player_position || '').toUpperCase()
              return pos === 'D' || pos === 'LD' || pos === 'RD'
            })
            const awayForwards = awayPlayers.filter((r: any) => {
              const pos = (r.player_position || '').toUpperCase()
              return pos === 'F' || pos === 'C' || pos === 'LW' || pos === 'RW' || pos === 'W'
            })
            const awayDefense = awayPlayers.filter((r: any) => {
              const pos = (r.player_position || '').toUpperCase()
              return pos === 'D' || pos === 'LD' || pos === 'RD'
            })
            
            const gameDate = champ.game_date ? new Date(champ.game_date).toLocaleDateString('en-US', {
              month: 'long',
              day: 'numeric',
              year: 'numeric'
            }) : 'Unknown Date'
            
            return (
              <div key={champ.season_id} className="bg-card rounded-xl border border-border overflow-hidden">
                <div className="px-4 py-3 bg-accent border-b border-border">
                  <div className="flex items-center justify-between">
                    <h2 className="font-display text-lg font-semibold uppercase tracking-wider">
                      {champ.season} Season Championship
                    </h2>
                    <Link
                      href={`/norad/games/${champ.game_id}`}
                      className="text-xs font-mono text-primary hover:underline"
                    >
                      View Full Game →
                    </Link>
                  </div>
                </div>
                
                {/* Championship Result */}
                <div className="p-6 bg-gradient-to-r from-assist/10 to-assist/5 border-b border-border">
                  <div className="flex items-center justify-center gap-6">
                    <div className="flex items-center gap-3">
                      {championTeam && (
                        <TeamLogo
                          src={championTeam.team_logo || null}
                          name={champ.champion_team_name}
                          abbrev={championTeam.team_cd}
                          primaryColor={championTeam.primary_color || championTeam.team_color1}
                          secondaryColor={championTeam.team_color2}
                          size="lg"
                        />
                      )}
                      <div>
                        <div className="flex items-center gap-2">
                          <Trophy className="w-5 h-5 text-assist" />
                          <span className="font-display text-xl font-bold text-assist uppercase">
                            Champions
                          </span>
                        </div>
                        <Link
                          href={`/norad/team/${champ.champion_team_name.replace(/\s+/g, '_')}?season=${champ.season_id}`}
                          className="font-display text-2xl font-bold text-foreground hover:text-primary transition-colors"
                        >
                          {champ.champion_team_name}
                        </Link>
                      </div>
                    </div>
                    
                    <div className="text-center">
                      <div className="font-mono text-3xl font-bold text-foreground">
                        {champ.home_team_id === champ.champion_team_id ? champ.home_total_goals : champ.away_total_goals}
                        {' - '}
                        {champ.home_team_id === champ.champion_team_id ? champ.away_total_goals : champ.home_total_goals}
                      </div>
                      <div className="text-xs text-muted-foreground mt-1">{gameDate}</div>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      <div className="text-right">
                        <div className="flex items-center gap-2 justify-end">
                          <span className="font-display text-sm font-semibold text-muted-foreground uppercase">
                            Runner Up
                          </span>
                        </div>
                        <Link
                          href={`/norad/team/${champ.runner_up_team_name.replace(/\s+/g, '_')}?season=${champ.season_id}`}
                          className="font-display text-xl font-bold text-foreground hover:text-primary transition-colors"
                        >
                          {champ.runner_up_team_name}
                        </Link>
                      </div>
                      {runnerUpTeam && (
                        <TeamLogo
                          src={runnerUpTeam.team_logo || null}
                          name={champ.runner_up_team_name}
                          abbrev={runnerUpTeam.team_cd}
                          primaryColor={runnerUpTeam.primary_color || runnerUpTeam.team_color1}
                          secondaryColor={runnerUpTeam.team_color2}
                          size="lg"
                        />
                      )}
                    </div>
                  </div>
                </div>
                
                {/* Box Score */}
                <div className="p-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    {/* Away Team */}
                    <div>
                      <div className="flex items-center gap-2 mb-4">
                        {runnerUpTeam && champ.away_team_id === champ.runner_up_team_id && (
                          <TeamLogo
                            src={runnerUpTeam.team_logo || null}
                            name={champ.away_team_name}
                            abbrev={runnerUpTeam.team_cd}
                            primaryColor={runnerUpTeam.primary_color || runnerUpTeam.team_color1}
                            secondaryColor={runnerUpTeam.team_color2}
                            size="sm"
                          />
                        )}
                        {championTeam && champ.away_team_id === champ.champion_team_id && (
                          <TeamLogo
                            src={championTeam.team_logo || null}
                            name={champ.away_team_name}
                            abbrev={championTeam.team_cd}
                            primaryColor={championTeam.primary_color || championTeam.team_color1}
                            secondaryColor={championTeam.team_color2}
                            size="sm"
                          />
                        )}
                        <h3 className="font-display font-semibold text-lg">{champ.away_team_name}</h3>
                      </div>
                      
                      {/* Forwards */}
                      {awayForwards.length > 0 && (
                        <div className="mb-4">
                          <h4 className="text-xs font-mono text-muted-foreground uppercase mb-2">Forwards</h4>
                          <div className="space-y-1">
                            {awayForwards.map((player: any) => {
                              const playerInfo = playersMapForChampions.get(String(player.player_id))
                              return (
                                <div key={player.player_game_id || player.player_id} className="flex items-center gap-2 text-sm">
                                  <span className="font-mono text-muted-foreground w-8">
                                    #{player.player_game_number || '-'}
                                  </span>
                                  <Link
                                    href={`/norad/players/${player.player_id}`}
                                    className="flex-1 hover:text-primary transition-colors"
                                  >
                                    {player.player_full_name || player.player_name}
                                  </Link>
                                  <span className="font-mono text-xs text-muted-foreground">
                                    {playerInfo?.current_skill_rating || '-'}
                                  </span>
                                  <span className="font-mono text-goal w-8 text-right">{player.goals || 0}</span>
                                  <span className="font-mono text-assist w-8 text-right">{player.assist || 0}</span>
                                  <span className="font-mono text-primary w-8 text-right font-semibold">
                                    {(Number(player.goals) || 0) + (Number(player.assist) || 0)}
                                  </span>
                                </div>
                              )
                            })}
                          </div>
                        </div>
                      )}
                      
                      {/* Defense */}
                      {awayDefense.length > 0 && (
                        <div className="mb-4">
                          <h4 className="text-xs font-mono text-muted-foreground uppercase mb-2">Defense</h4>
                          <div className="space-y-1">
                            {awayDefense.map((player: any) => {
                              const playerInfo = playersMapForChampions.get(String(player.player_id))
                              return (
                                <div key={player.player_game_id || player.player_id} className="flex items-center gap-2 text-sm">
                                  <span className="font-mono text-muted-foreground w-8">
                                    #{player.player_game_number || '-'}
                                  </span>
                                  <Link
                                    href={`/norad/players/${player.player_id}`}
                                    className="flex-1 hover:text-primary transition-colors"
                                  >
                                    {player.player_full_name || player.player_name}
                                  </Link>
                                  <span className="font-mono text-xs text-muted-foreground">
                                    {playerInfo?.current_skill_rating || '-'}
                                  </span>
                                  <span className="font-mono text-goal w-8 text-right">{player.goals || 0}</span>
                                  <span className="font-mono text-assist w-8 text-right">{player.assist || 0}</span>
                                  <span className="font-mono text-primary w-8 text-right font-semibold">
                                    {(Number(player.goals) || 0) + (Number(player.assist) || 0)}
                                  </span>
                                </div>
                              )
                            })}
                          </div>
                        </div>
                      )}
                      
                      {/* Goalies */}
                      {awayGoalies.length > 0 && (
                        <div>
                          <h4 className="text-xs font-mono text-muted-foreground uppercase mb-2">Goalies</h4>
                          <div className="space-y-1">
                            {awayGoalies.map((goalie: any) => {
                              const goalieInfo = playersMapForChampions.get(String(goalie.player_id))
                              return (
                                <div key={goalie.player_game_id || goalie.player_id} className="flex items-center gap-2 text-sm">
                                  <span className="font-mono text-muted-foreground w-8">
                                    #{goalie.player_game_number || '-'}
                                  </span>
                                  <Link
                                    href={`/norad/players/${goalie.player_id}`}
                                    className="flex-1 hover:text-primary transition-colors"
                                  >
                                    {goalie.player_full_name || goalie.player_name}
                                  </Link>
                                  <span className="font-mono text-xs text-muted-foreground">
                                    {goalieInfo?.current_skill_rating || '-'}
                                  </span>
                                  <span className="font-mono text-goal w-16 text-right">
                                    {goalie.goals_against || 0} GA
                                  </span>
                                </div>
                              )
                            })}
                          </div>
                        </div>
                      )}
                    </div>
                    
                    {/* Home Team */}
                    <div>
                      <div className="flex items-center gap-2 mb-4">
                        {championTeam && champ.home_team_id === champ.champion_team_id && (
                          <TeamLogo
                            src={championTeam.team_logo || null}
                            name={champ.home_team_name}
                            abbrev={championTeam.team_cd}
                            primaryColor={championTeam.primary_color || championTeam.team_color1}
                            secondaryColor={championTeam.team_color2}
                            size="sm"
                          />
                        )}
                        {runnerUpTeam && champ.home_team_id === champ.runner_up_team_id && (
                          <TeamLogo
                            src={runnerUpTeam.team_logo || null}
                            name={champ.home_team_name}
                            abbrev={runnerUpTeam.team_cd}
                            primaryColor={runnerUpTeam.primary_color || runnerUpTeam.team_color1}
                            secondaryColor={runnerUpTeam.team_color2}
                            size="sm"
                          />
                        )}
                        <h3 className="font-display font-semibold text-lg">{champ.home_team_name}</h3>
                      </div>
                      
                      {/* Forwards */}
                      {homeForwards.length > 0 && (
                        <div className="mb-4">
                          <h4 className="text-xs font-mono text-muted-foreground uppercase mb-2">Forwards</h4>
                          <div className="space-y-1">
                            {homeForwards.map((player: any) => {
                              const playerInfo = playersMapForChampions.get(String(player.player_id))
                              return (
                                <div key={player.player_game_id || player.player_id} className="flex items-center gap-2 text-sm">
                                  <span className="font-mono text-muted-foreground w-8">
                                    #{player.player_game_number || '-'}
                                  </span>
                                  <Link
                                    href={`/norad/players/${player.player_id}`}
                                    className="flex-1 hover:text-primary transition-colors"
                                  >
                                    {player.player_full_name || player.player_name}
                                  </Link>
                                  <span className="font-mono text-xs text-muted-foreground">
                                    {playerInfo?.current_skill_rating || '-'}
                                  </span>
                                  <span className="font-mono text-goal w-8 text-right">{player.goals || 0}</span>
                                  <span className="font-mono text-assist w-8 text-right">{player.assist || 0}</span>
                                  <span className="font-mono text-primary w-8 text-right font-semibold">
                                    {(Number(player.goals) || 0) + (Number(player.assist) || 0)}
                                  </span>
                                </div>
                              )
                            })}
                          </div>
                        </div>
                      )}
                      
                      {/* Defense */}
                      {homeDefense.length > 0 && (
                        <div className="mb-4">
                          <h4 className="text-xs font-mono text-muted-foreground uppercase mb-2">Defense</h4>
                          <div className="space-y-1">
                            {homeDefense.map((player: any) => {
                              const playerInfo = playersMapForChampions.get(String(player.player_id))
                              return (
                                <div key={player.player_game_id || player.player_id} className="flex items-center gap-2 text-sm">
                                  <span className="font-mono text-muted-foreground w-8">
                                    #{player.player_game_number || '-'}
                                  </span>
                                  <Link
                                    href={`/norad/players/${player.player_id}`}
                                    className="flex-1 hover:text-primary transition-colors"
                                  >
                                    {player.player_full_name || player.player_name}
                                  </Link>
                                  <span className="font-mono text-xs text-muted-foreground">
                                    {playerInfo?.current_skill_rating || '-'}
                                  </span>
                                  <span className="font-mono text-goal w-8 text-right">{player.goals || 0}</span>
                                  <span className="font-mono text-assist w-8 text-right">{player.assist || 0}</span>
                                  <span className="font-mono text-primary w-8 text-right font-semibold">
                                    {(Number(player.goals) || 0) + (Number(player.assist) || 0)}
                                  </span>
                                </div>
                              )
                            })}
                          </div>
                        </div>
                      )}
                      
                      {/* Goalies */}
                      {homeGoalies.length > 0 && (
                        <div>
                          <h4 className="text-xs font-mono text-muted-foreground uppercase mb-2">Goalies</h4>
                          <div className="space-y-1">
                            {homeGoalies.map((goalie: any) => {
                              const goalieInfo = playersMapForChampions.get(String(goalie.player_id))
                              return (
                                <div key={goalie.player_game_id || goalie.player_id} className="flex items-center gap-2 text-sm">
                                  <span className="font-mono text-muted-foreground w-8">
                                    #{goalie.player_game_number || '-'}
                                  </span>
                                  <Link
                                    href={`/norad/players/${goalie.player_id}`}
                                    className="flex-1 hover:text-primary transition-colors"
                                  >
                                    {goalie.player_full_name || goalie.player_name}
                                  </Link>
                                  <span className="font-mono text-xs text-muted-foreground">
                                    {goalieInfo?.current_skill_rating || '-'}
                                  </span>
                                  <span className="font-mono text-goal w-16 text-right">
                                    {goalie.goals_against || 0} GA
                                  </span>
                                </div>
                              )
                            })}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
