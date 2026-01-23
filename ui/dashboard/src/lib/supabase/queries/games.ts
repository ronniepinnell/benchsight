import { createClient } from '@/lib/supabase/server'
import type { 
  VRecentGames,
  FactPlayerGameStats,
  FactGoalieGameStats,
  FactEvents,
  FactShotXY
} from '@/types/database'

// Enhanced get games function with filtering support
export async function getGames({
  limit = 20,
  seasonId,
  teamId,
  teamName,
  gameType,
  search,
  offset = 0
}: {
  limit?: number
  seasonId?: string | null
  teamId?: string | null
  teamName?: string | null
  gameType?: string | null
  search?: string | null
  offset?: number
} = {}): Promise<{ games: VRecentGames[], hasMore: boolean }> {
  const supabase = await createClient()
  
  // Build base query - only completed games (have scores)
  let query = supabase
    .from('dim_schedule')
    .select('*', { count: 'exact' })
    .not('home_total_goals', 'is', null)
    .not('away_total_goals', 'is', null)
  
  // Apply filters
  if (seasonId) {
    query = query.eq('season_id', seasonId)
  }
  
  if (gameType && gameType !== 'All') {
    query = query.eq('game_type', gameType)
  }
  
  // For team filtering, use .or() once (this replaces previous filters, so we need to be careful)
  // Since we already filtered for completed games with .not(), we'll filter team/search in JS
  // This is simpler and more reliable
  
  // Order and paginate - get more than limit to account for JS filtering
  const fetchLimit = Math.max(limit * 3, 100) // Get more to filter in JS
  const { data: scheduleGames, error: scheduleError, count } = await query
    .order('date', { ascending: false })
    .order('game_time', { ascending: false, nullsLast: true })
    .range(offset, offset + fetchLimit - 1)
  
  if (scheduleError) {
    console.error('Error fetching from dim_schedule:', scheduleError)
    return { games: [], hasMore: false }
  }
  
  if (!scheduleGames || scheduleGames.length === 0) {
    return { games: [], hasMore: false }
  }
  
  // Filter by team/search in JavaScript (after fetching)
  let filteredGames = scheduleGames
  if (teamId) {
    filteredGames = filteredGames.filter(g => 
      String(g.home_team_id) === String(teamId) || String(g.away_team_id) === String(teamId)
    )
  } else if (teamName) {
    const teamNameLower = teamName.toLowerCase()
    filteredGames = filteredGames.filter(g => 
      (g.home_team_name?.toLowerCase().includes(teamNameLower)) ||
      (g.away_team_name?.toLowerCase().includes(teamNameLower))
    )
  }
  
  if (search) {
    const searchLower = search.toLowerCase()
    const searchNum = parseInt(search)
    filteredGames = filteredGames.filter(g => 
      (g.home_team_name?.toLowerCase().includes(searchLower)) ||
      (g.away_team_name?.toLowerCase().includes(searchLower)) ||
      (g.game_id === searchNum)
    )
  }
  
  // Apply pagination after filtering
  const paginatedGames = filteredGames.slice(0, limit)
  
  // Get all game IDs to fetch additional data
  const gameIds = paginatedGames.map(g => g.game_id).filter((id): id is number => id !== null && id !== undefined && !isNaN(Number(id)))
  
  // Get official scores from fact_game_status
  const { data: gameStatusData } = gameIds.length > 0 ? await supabase
    .from('fact_game_status')
    .select('game_id, official_home_goals, official_away_goals, game_date')
    .in('game_id', gameIds)
    .then(({ data }) => ({ data }))
    .catch(() => ({ data: [] })) : { data: [] }
  
  const statusMap = new Map(
    (gameStatusData || []).map(s => [s.game_id, { home: s.official_home_goals, away: s.official_away_goals }])
  )
  
  // Also get from fact_team_game_stats as additional fallback
  const { data: teamGameStats } = gameIds.length > 0 ? await supabase
    .from('fact_team_game_stats')
    .select('game_id, team_id, team_name, goals')
    .in('game_id', gameIds)
    .then(({ data }) => ({ data }))
    .catch(() => ({ data: [] })) : { data: [] }
  
  // Build a map of game_id -> { homeGoals, awayGoals, homeTeamId, awayTeamId }
  const teamScoresMap = new Map<number, { home?: number, away?: number }>()
  if (teamGameStats && paginatedGames) {
    paginatedGames.forEach(game => {
      const homeTeamId = game.home_team_id
      const awayTeamId = game.away_team_id
      const homeStats = teamGameStats.filter(s => s.game_id === game.game_id && String(s.team_id) === String(homeTeamId))
      const awayStats = teamGameStats.filter(s => s.game_id === game.game_id && String(s.team_id) === String(awayTeamId))
      
      if (homeStats.length > 0 || awayStats.length > 0) {
        teamScoresMap.set(game.game_id, {
          home: homeStats[0]?.goals || 0,
          away: awayStats[0]?.goals || 0,
        })
      }
    })
  }
  
  // Process games - prioritize: fact_game_status > dim_schedule official > dim_schedule total > fact_team_game_stats
  const games = paginatedGames.map(game => {
    const status = statusMap.get(game.game_id)
    const teamStats = teamScoresMap.get(game.game_id)
    
    // Priority order: official from fact_game_status > official from dim_schedule > total from dim_schedule > fact_team_game_stats
    let homeGoals: number | null = null
    let awayGoals: number | null = null
    
    if (status && status.home !== null && status.away !== null) {
      homeGoals = status.home
      awayGoals = status.away
    } else if (game.official_home_goals !== null && game.official_away_goals !== null) {
      homeGoals = game.official_home_goals
      awayGoals = game.official_away_goals
    } else if (game.home_total_goals !== null && game.away_total_goals !== null) {
      homeGoals = game.home_total_goals
      awayGoals = game.away_total_goals
    } else if (teamStats) {
      homeGoals = teamStats.home ?? null
      awayGoals = teamStats.away ?? null
    }
    
    // Only return games with valid scores
    if (homeGoals === null || awayGoals === null) {
      return null
    }
    
    return {
      ...game,
      game_id: game.game_id,
      date: game.date || game.game_date,
      home_team_id: game.home_team_id,
      home_team_name: game.home_team_name,
      away_team_id: game.away_team_id,
      away_team_name: game.away_team_name,
      home_total_goals: homeGoals,
      away_total_goals: awayGoals,
      official_home_goals: status?.home ?? game.official_home_goals ?? homeGoals,
      official_away_goals: status?.away ?? game.official_away_goals ?? awayGoals,
    }
  }).filter((game): game is NonNullable<typeof game> => game !== null && game.game_id !== null && game.game_id !== undefined)
  
  // Calculate hasMore based on filtered results
  const hasMore = filteredGames.length > limit || (count !== null && (offset + filteredGames.length) < count)
  
  return { games, hasMore }
}

// Get recent games - show ALL games from dim_schedule, not just tracked
export async function getRecentGames(limit: number = 10): Promise<VRecentGames[]> {
  const supabase = await createClient()
  
  // Get ALL games from dim_schedule - filter for completed games (have any score data)
  const { data: scheduleGames, error: scheduleError } = await supabase
    .from('dim_schedule')
    .select('*')
    .or('home_total_goals.not.is.null,away_total_goals.not.is.null')
    .order('date', { ascending: false })
    .order('game_time', { ascending: false, nullsLast: true })
    .limit(limit * 2) // Get more to filter properly
  
  if (scheduleError) {
    console.error('Error fetching from dim_schedule:', scheduleError)
    return []
  }
  
  if (!scheduleGames || scheduleGames.length === 0) {
    return []
  }
  
  // Get all game IDs to fetch additional data
  const gameIds = scheduleGames.map(g => g.game_id).filter((id): id is number => id !== null && id !== undefined && !isNaN(Number(id)))
  
  // Get official scores from fact_game_status
  const { data: gameStatusData } = gameIds.length > 0 ? await supabase
    .from('fact_game_status')
    .select('game_id, official_home_goals, official_away_goals, game_date')
    .in('game_id', gameIds)
    .then(({ data }) => ({ data }))
    .catch(() => ({ data: [] })) : { data: [] }
  
  const statusMap = new Map(
    (gameStatusData || []).map(s => [s.game_id, { home: s.official_home_goals, away: s.official_away_goals }])
  )
  
  // Also get from fact_team_game_stats as additional fallback
  const { data: teamGameStats } = gameIds.length > 0 ? await supabase
    .from('fact_team_game_stats')
    .select('game_id, team_id, team_name, goals')
    .in('game_id', gameIds)
    .then(({ data }) => ({ data }))
    .catch(() => ({ data: [] })) : { data: [] }
  
  // Build a map of game_id -> { homeGoals, awayGoals, homeTeamId, awayTeamId }
  const teamScoresMap = new Map<number, { home?: number, away?: number }>()
  if (teamGameStats && scheduleGames) {
    scheduleGames.forEach(game => {
      const homeTeamId = game.home_team_id
      const awayTeamId = game.away_team_id
      const homeStats = teamGameStats.filter(s => s.game_id === game.game_id && String(s.team_id) === String(homeTeamId))
      const awayStats = teamGameStats.filter(s => s.game_id === game.game_id && String(s.team_id) === String(awayTeamId))
      
      if (homeStats.length > 0 || awayStats.length > 0) {
        teamScoresMap.set(game.game_id, {
          home: homeStats[0]?.goals || 0,
          away: awayStats[0]?.goals || 0,
        })
      }
    })
  }
  
  // Process games - prioritize: fact_game_status > dim_schedule official > dim_schedule total > fact_team_game_stats
  const games = scheduleGames.map(game => {
    const status = statusMap.get(game.game_id)
    const teamStats = teamScoresMap.get(game.game_id)
    
    // Priority order: official from fact_game_status > official from dim_schedule > total from dim_schedule > fact_team_game_stats
    let homeGoals: number | null = null
    let awayGoals: number | null = null
    
    if (status && status.home !== null && status.away !== null) {
      homeGoals = status.home
      awayGoals = status.away
    } else if (game.official_home_goals !== null && game.official_away_goals !== null) {
      homeGoals = game.official_home_goals
      awayGoals = game.official_away_goals
    } else if (game.home_total_goals !== null && game.away_total_goals !== null) {
      homeGoals = game.home_total_goals
      awayGoals = game.away_total_goals
    } else if (teamStats) {
      homeGoals = teamStats.home ?? null
      awayGoals = teamStats.away ?? null
    }
    
    // Only return games with valid scores
    if (homeGoals === null || awayGoals === null) {
      return null
    }
    
    return {
      ...game,
      game_id: game.game_id,
      date: game.date || game.game_date,
      home_team_id: game.home_team_id,
      home_team_name: game.home_team_name,
      away_team_id: game.away_team_id,
      away_team_name: game.away_team_name,
      home_total_goals: homeGoals,
      away_total_goals: awayGoals,
      official_home_goals: status?.home ?? game.official_home_goals ?? homeGoals,
      official_away_goals: status?.away ?? game.official_away_goals ?? awayGoals,
    }
  }).filter((game): game is NonNullable<typeof game> => game !== null && game.game_id !== null && game.game_id !== undefined)
  
  return games.slice(0, limit)
}

// Get game by ID
export async function getGameById(gameId: number): Promise<VRecentGames | null> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('v_recent_games')
    .select('*')
    .eq('game_id', gameId)
    .single()
  
  if (error) return null
  return data
}

// Get game box score (player stats for both teams)
export async function getGameBoxScore(gameId: number): Promise<{
  homeStats: FactPlayerGameStats[]
  awayStats: FactPlayerGameStats[]
}> {
  const supabase = await createClient()
  
  // Get the game info first to determine home/away teams
  const game = await getGameById(gameId)
  if (!game) return { homeStats: [], awayStats: [] }
  
  const { data, error } = await supabase
    .from('fact_player_game_stats')
    .select('*')
    .eq('game_id', gameId)
    .order('points', { ascending: false })
  
  if (error) throw error
  
  const stats = data ?? []
  return {
    homeStats: stats.filter(s => s.team_name === game.home_team_name),
    awayStats: stats.filter(s => s.team_name === game.away_team_name)
  }
}

// Get game goalie stats
export async function getGameGoalieStats(gameId: number): Promise<FactGoalieGameStats[]> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('fact_goalie_game_stats')
    .select('*')
    .eq('game_id', gameId)
  
  if (error) throw error
  return data ?? []
}

// Get game events (play-by-play)
export async function getGameEvents(gameId: number): Promise<FactEvents[]> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('fact_events')
    .select('*')
    .eq('game_id', gameId)
    .order('time_start_total_seconds', { ascending: true })
  
  if (error) throw error
  return data ?? []
}

// Get game goals only (event_type='Goal' AND event_detail='Goal_Scored')
export async function getGameGoals(gameId: number): Promise<FactEvents[]> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('fact_events')
    .select('*')
    .eq('game_id', gameId)
    .eq('event_type', 'Goal')
    .eq('event_detail', 'Goal_Scored')
    .order('time_start_total_seconds', { ascending: true })
  
  if (error) throw error
  return data ?? []
}

// Get game shots (for shot maps)
export async function getGameShots(gameId: number): Promise<FactShotXY[]> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('fact_shot_xy')
    .select('*')
    .eq('game_id', gameId)
    // Remove ordering by time_seconds if column doesn't exist - order by shot_id or event_id instead
    .order('shot_id', { ascending: true })
  
  if (error) throw error
  return data ?? []
}

// Get player's shots (for shot chart)
export async function getPlayerShots(playerId: string, limit: number = 100): Promise<FactShotXY[]> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('fact_shot_xy')
    .select('*')
    .eq('player_id', playerId)
    .order('game_id', { ascending: false })
    .limit(limit)
  
  if (error) throw error
  return data ?? []
}

// Get upcoming schedule
export async function getUpcomingSchedule(limit: number = 10) {
  const supabase = await createClient()
  const today = new Date().toISOString().split('T')[0]
  const { data, error } = await supabase
    .from('dim_schedule')
    .select('*')
    .or(`date.gte.${today},and(date.eq.${today},game_time.gte.${new Date().toTimeString().slice(0, 5)})`)
    .order('date', { ascending: true })
    .order('game_time', { ascending: true, nullsLast: true })
    .limit(limit)

  if (error) throw error
  return data ?? []
}

// Get team schedule
export async function getTeamSchedule(teamName: string, limit: number = 20) {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('dim_schedule')
    .select('*')
    .or(`home_team_name.eq.${teamName},away_team_name.eq.${teamName}`)
    .order('date', { ascending: true })
    .limit(limit)

  if (error) throw error
  return data ?? []
}

// Get game roster from fact_gameroster
export async function getGameRoster(gameId: number) {
  const supabase = await createClient()
  
  try {
    // Try with number first (most common case)
    let { data, error } = await supabase
      .from('fact_gameroster')
      .select('*, sub, player_game_number')
      .eq('game_id', gameId)
      .order('goals', { ascending: false })
    
    // If no data and no error, try with string format (some tables store game_id as text)
    if ((!data || data.length === 0) && !error) {
      const { data: dataStr, error: errorStr } = await supabase
        .from('fact_gameroster')
        .select('*, sub, player_game_number')
        .eq('game_id', String(gameId))
        .order('goals', { ascending: false })
      
      if (dataStr && dataStr.length > 0) {
        data = dataStr
      }
      if (errorStr) {
        error = errorStr
      }
    }
    
    if (error) {
      // Log detailed error information
      const errorInfo = {
        message: error?.message || 'Unknown error',
        details: error?.details || null,
        hint: error?.hint || null,
        code: error?.code || null,
        error: error
      }
      console.error(`Error fetching roster for game ${gameId}:`, JSON.stringify(errorInfo, null, 2))
      return []
    }
    
    return data ?? []
  } catch (err) {
    // Catch any unexpected errors
    console.error(`Unexpected error fetching roster for game ${gameId}:`, err)
    return []
  }
}

// Get game from dim_schedule
export async function getGameFromSchedule(gameId: number) {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('dim_schedule')
    .select('*')
    .eq('game_id', gameId)
    .single()
  
  if (error) return null
  return data
}
