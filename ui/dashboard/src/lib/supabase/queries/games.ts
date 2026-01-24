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

// Get game videos from fact_video (can have multiple per game)
export interface GameVideo {
  video_key: string
  game_id: number
  video_type_id: string
  video_type: string
  video_description: string | null
  video_url: string
  period_1_start: number | null
  period_2_start: number | null
  period_3_start: number | null
}

export async function getGameVideos(gameId: number): Promise<GameVideo[]> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('fact_video')
    .select('*')
    .eq('game_id', gameId)
    .order('video_type_id', { ascending: true })

  if (error) return []
  return data as GameVideo[]
}

// Get game highlights from fact_events with player images
export interface GameHighlight {
  event_id: string
  event_type: string
  event_detail: string | null
  period: number
  player_name: string
  player_team: string
  player_id: string | null
  player_image: string | null
  primary_color: string | null
  is_goal: number
  is_highlight: number
  running_video_time: number
  event_start_min: number | null
  event_start_sec: number | null
  // Additional event details
  event_team_zone: string | null
  strength: string | null
  is_rebound: number
  is_rush: number
  play_detail1: string | null
  play_detail_2: string | null
  event_player_2: string | null
  team_venue: string | null
  // Shot location and goalie info
  puck_x_start: number | null
  puck_y_start: number | null
  goalie_player_id: string | null
  goalie_name: string | null
  // Future: separate highlight video
  highlight_video_url: string | null
}

export async function getGameHighlights(gameId: number): Promise<GameHighlight[]> {
  const supabase = await createClient()

  // Get highlights from fact_events - filter on database side to avoid 1000 row limit
  // Include events where is_highlight = 1 OR is_goal = 1 OR event_type = 'Goal'
  const { data: events, error } = await supabase
    .from('fact_events')
    .select('*')
    .eq('game_id', gameId)
    .or('is_highlight.eq.1,is_goal.eq.1,event_type.eq.Goal')
    .order('running_video_time', { ascending: true })

  if (error) {
    console.error('Error fetching highlights:', error.message)
    return []
  }

  if (!events || events.length === 0) {
    return []
  }

  // Extract player IDs - use event_player_ids (may be comma-separated, take first) or shooter_player_id
  const getPlayerId = (e: any): string | null => {
    // Try shooter_player_id first for goals
    if (e.shooter_player_id && e.shooter_player_id !== '0' && !e.shooter_player_id.startsWith('SH')) {
      return e.shooter_player_id
    }
    // Try event_player_ids (take first if comma-separated)
    if (e.event_player_ids) {
      const ids = String(e.event_player_ids).split(',')
      const firstId = ids[0]?.trim()
      if (firstId && firstId.startsWith('P')) {
        return firstId
      }
    }
    return null
  }

  // Get unique player IDs
  const playerIds = Array.from(new Set(events.map(getPlayerId).filter(Boolean))) as string[]

  // Also get unique player names for fallback lookup
  const playerNames = Array.from(new Set(events.map(e => e.player_name).filter(Boolean)))

  // Fetch player images by ID and by name
  let playerImageById = new Map<string, string | null>()
  let playerImageByName = new Map<string, string | null>()

  if (playerIds.length > 0 || playerNames.length > 0) {
    // Fetch by ID
    if (playerIds.length > 0) {
      const { data: playersById } = await supabase
        .from('dim_player')
        .select('player_id, player_image, player_full_name')
        .in('player_id', playerIds)

      if (playersById) {
        playersById.forEach(p => {
          playerImageById.set(p.player_id, p.player_image || null)
          if (p.player_full_name) {
            playerImageByName.set(p.player_full_name, p.player_image || null)
          }
        })
      }
    }

    // Also fetch by name for fallback
    if (playerNames.length > 0) {
      const { data: playersByName } = await supabase
        .from('dim_player')
        .select('player_id, player_image, player_full_name')
        .in('player_full_name', playerNames)

      if (playersByName) {
        playersByName.forEach(p => {
          if (p.player_full_name) {
            playerImageByName.set(p.player_full_name, p.player_image || null)
          }
          playerImageById.set(p.player_id, p.player_image || null)
        })
      }
    }
  }

  // Get team colors
  const { data: teams } = await supabase
    .from('dim_team')
    .select('team_name, primary_color')

  const teamColorMap = new Map((teams || []).map(t => [t.team_name, t.primary_color]))

  // Map events with player data
  return events.map(e => {
    const playerId = getPlayerId(e)
    const playerImage = playerImageById.get(playerId || '') || playerImageByName.get(e.player_name) || null

    return {
      event_id: e.event_id,
      event_type: e.event_type,
      event_detail: e.event_detail,
      period: e.period,
      player_name: e.player_name,
      player_team: e.player_team,
      player_id: playerId,
      player_image: playerImage,
      primary_color: teamColorMap.get(e.player_team) || null,
      is_goal: e.is_goal,
      is_highlight: e.is_highlight,
      running_video_time: e.running_video_time,
      event_start_min: e.event_start_min,
      event_start_sec: e.event_start_sec,
      // Additional details
      event_team_zone: e.event_team_zone || null,
      strength: e.strength || null,
      is_rebound: e.is_rebound || 0,
      is_rush: e.is_rush || 0,
      play_detail1: e.play_detail1 || null,
      play_detail_2: e.play_detail_2 || null,
      event_player_2: e.event_player_2_name_x || null,
      team_venue: e.team_venue || null,
      // Shot location and goalie info
      puck_x_start: e.puck_x_start ?? null,
      puck_y_start: e.puck_y_start ?? null,
      goalie_player_id: e.goalie_player_id || null,
      goalie_name: e.goalie_name || null,
      highlight_video_url: null, // Future: separate highlight compilation
    }
  })
}

// Event context for play sequence display
export interface EventContext {
  event_id: string
  event_type: string
  event_detail: string | null
  player_name: string | null
  player_team: string | null
  period: number
  event_start_min: number | null
  event_start_sec: number | null
  running_video_time: number
}

// Get previous events leading up to a highlight for context
export async function getEventContext(
  gameId: number,
  eventId: string,
  count: number = 10
): Promise<EventContext[]> {
  const supabase = await createClient()

  // First get the target event to find its running_video_time
  const { data: targetEvent, error: targetError } = await supabase
    .from('fact_events')
    .select('running_video_time, period')
    .eq('event_id', eventId)
    .single()

  if (targetError || !targetEvent) return []

  // Get events before this one (by running_video_time), same period preferred
  const { data: events, error } = await supabase
    .from('fact_events')
    .select(`
      event_id, event_type, event_detail, player_name, player_team,
      period, event_start_min, event_start_sec, running_video_time
    `)
    .eq('game_id', gameId)
    .lt('running_video_time', targetEvent.running_video_time)
    .order('running_video_time', { ascending: false })
    .limit(count)

  if (error || !events) return []

  // Return in chronological order (oldest first) so the current event is at the end
  return events.reverse().map(e => ({
    event_id: e.event_id,
    event_type: e.event_type,
    event_detail: e.event_detail,
    player_name: e.player_name || null,
    player_team: e.player_team || null,
    period: e.period,
    event_start_min: e.event_start_min,
    event_start_sec: e.event_start_sec,
    running_video_time: e.running_video_time,
  }))
}

// ============================================================================
// Game Detail Data Fetching (extracted from page component)
// ============================================================================

export interface PriorGamesResult {
  homeGames: any[]
  awayGames: any[]
  headToHeadGames: any[]
}

/**
 * Fetch prior games and head-to-head matchups for a game
 */
export async function getPriorGames(
  gameId: number,
  seasonId: string | number | null | undefined,
  homeTeamId: string | number | null | undefined,
  awayTeamId: string | number | null | undefined,
  game: { date?: string; home_team_name?: string; away_team_name?: string; game_type?: string }
): Promise<PriorGamesResult> {
  if (!seasonId) {
    return { homeGames: [], awayGames: [], headToHeadGames: [] }
  }

  const supabase = await createClient()

  // Get prior games for home team
  const { data: homeTeamGames } = await supabase
    .from('dim_schedule')
    .select('game_id, date, home_team_name, away_team_name, home_total_goals, away_total_goals, official_home_goals, official_away_goals, home_team_id, away_team_id')
    .eq('season_id', seasonId)
    .or(`home_team_id.eq.${homeTeamId},away_team_id.eq.${homeTeamId}`)
    .neq('game_id', gameId)
    .not('home_total_goals', 'is', null)
    .not('away_total_goals', 'is', null)
    .order('date', { ascending: false })
    .limit(10)

  // Get prior games for away team
  const { data: awayTeamGames } = await supabase
    .from('dim_schedule')
    .select('game_id, date, home_team_name, away_team_name, home_total_goals, away_total_goals, official_home_goals, official_away_goals, home_team_id, away_team_id')
    .eq('season_id', seasonId)
    .or(`home_team_id.eq.${awayTeamId},away_team_id.eq.${awayTeamId}`)
    .neq('game_id', gameId)
    .not('home_total_goals', 'is', null)
    .not('away_total_goals', 'is', null)
    .order('date', { ascending: false })
    .limit(10)

  // Get head-to-head games between these two teams in the same season
  const { data: allSeasonGames } = await supabase
    .from('dim_schedule')
    .select('game_id, date, home_team_name, away_team_name, home_total_goals, away_total_goals, official_home_goals, official_away_goals, home_team_id, away_team_id, game_type')
    .eq('season_id', seasonId)
    .order('date', { ascending: true })
    .order('game_id', { ascending: true })

  // Normalize team identifiers for matching
  const homeTeamIds = new Set<string>()
  const awayTeamIds = new Set<string>()
  const homeTeamNames = new Set<string>()
  const awayTeamNames = new Set<string>()

  if (homeTeamId) {
    homeTeamIds.add(String(homeTeamId).trim())
    homeTeamIds.add(String(homeTeamId).trim().toLowerCase())
  }
  if (game.home_team_name) {
    const normalized = String(game.home_team_name).trim()
    homeTeamNames.add(normalized)
    homeTeamNames.add(normalized.toLowerCase())
  }
  if (awayTeamId) {
    awayTeamIds.add(String(awayTeamId).trim())
    awayTeamIds.add(String(awayTeamId).trim().toLowerCase())
  }
  if (game.away_team_name) {
    const normalized = String(game.away_team_name).trim()
    awayTeamNames.add(normalized)
    awayTeamNames.add(normalized.toLowerCase())
  }

  // Filter games to find head-to-head matchups
  const headToHeadGames = (allSeasonGames || [])
    .filter((g: any) => {
      if (Number(g.game_id) === gameId) return true

      const gHomeId = g.home_team_id ? String(g.home_team_id).trim() : null
      const gAwayId = g.away_team_id ? String(g.away_team_id).trim() : null
      const gHomeName = g.home_team_name ? String(g.home_team_name).trim() : null
      const gAwayName = g.away_team_name ? String(g.away_team_name).trim() : null

      const homeMatchesHome = (gHomeId && (homeTeamIds.has(gHomeId) || homeTeamIds.has(gHomeId.toLowerCase()))) ||
        (gHomeName && (homeTeamNames.has(gHomeName) || homeTeamNames.has(gHomeName.toLowerCase())))
      const homeMatchesAway = (gHomeId && (awayTeamIds.has(gHomeId) || awayTeamIds.has(gHomeId.toLowerCase()))) ||
        (gHomeName && (awayTeamNames.has(gHomeName) || awayTeamNames.has(gHomeName.toLowerCase())))
      const awayMatchesHome = (gAwayId && (homeTeamIds.has(gAwayId) || homeTeamIds.has(gAwayId.toLowerCase()))) ||
        (gAwayName && (homeTeamNames.has(gAwayName) || homeTeamNames.has(gAwayName.toLowerCase())))
      const awayMatchesAway = (gAwayId && (awayTeamIds.has(gAwayId) || awayTeamIds.has(gAwayId.toLowerCase()))) ||
        (gAwayName && (awayTeamNames.has(gAwayName) || awayTeamNames.has(gAwayName.toLowerCase())))

      return (homeMatchesHome && awayMatchesAway) || (homeMatchesAway && awayMatchesHome)
    })
    .map((g: any) => ({
      game_id: Number(g.game_id),
      date: g.date,
      home_team_name: g.home_team_name,
      away_team_name: g.away_team_name,
      home_total_goals: g.home_total_goals,
      away_total_goals: g.away_total_goals,
      official_home_goals: g.official_home_goals,
      official_away_goals: g.official_away_goals,
      home_team_id: g.home_team_id,
      away_team_id: g.away_team_id,
      game_type: g.game_type || 'Regular',
    }))
    .sort((a: any, b: any) => {
      const dateA = a.date ? new Date(a.date).getTime() : 0
      const dateB = b.date ? new Date(b.date).getTime() : 0
      if (dateA === dateB) {
        return (a.game_id || 0) - (b.game_id || 0)
      }
      return dateA - dateB
    })

  // Always include current game if not already in the list
  const hasCurrentGame = headToHeadGames.some((g: any) => g.game_id === gameId)
  if (!hasCurrentGame) {
    headToHeadGames.push({
      game_id: gameId,
      date: game.date,
      home_team_name: game.home_team_name,
      away_team_name: game.away_team_name,
      home_total_goals: null,
      away_total_goals: null,
      official_home_goals: null,
      official_away_goals: null,
      home_team_id: homeTeamId,
      away_team_id: awayTeamId,
      game_type: game.game_type || 'Regular',
    })
    headToHeadGames.sort((a: any, b: any) => {
      const dateA = a.date ? new Date(a.date).getTime() : 0
      const dateB = b.date ? new Date(b.date).getTime() : 0
      if (dateA === dateB) {
        return (a.game_id || 0) - (b.game_id || 0)
      }
      return dateA - dateB
    })
  }

  return {
    homeGames: homeTeamGames || [],
    awayGames: awayTeamGames || [],
    headToHeadGames: headToHeadGames.length > 0 ? headToHeadGames : [{
      game_id: gameId,
      date: game.date,
      home_team_name: game.home_team_name,
      away_team_name: game.away_team_name,
      home_total_goals: null,
      away_total_goals: null,
      official_home_goals: null,
      official_away_goals: null,
      home_team_id: homeTeamId,
      away_team_id: awayTeamId,
      game_type: game.game_type || 'Regular',
    }]
  }
}

/**
 * Fetch all player game stats for a game
 */
export async function getGamePlayerStats(gameId: number): Promise<any[]> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('fact_player_game_stats')
    .select('*')
    .eq('game_id', gameId)

  if (error) {
    console.error('Error fetching player game stats:', error)
    return []
  }
  return data || []
}

/**
 * Fetch team game stats for a game
 */
export async function getTeamGameStats(gameId: number): Promise<any[]> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('fact_team_game_stats')
    .select('*')
    .eq('game_id', gameId)

  if (error) {
    console.error('Error fetching team game stats:', error)
    return []
  }
  return data || []
}

/**
 * Fetch assist events for goals in a game
 */
export async function getGameAssistEvents(gameId: number): Promise<any[]> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('fact_events')
    .select('event_id, sequence_key, play_key, player_name, event_player_ids, play_detail1, play_detail_2, linked_event_key, time_start_total_seconds')
    .eq('game_id', gameId)

  if (error) {
    console.error('Error fetching assist events:', error)
    return []
  }
  return data || []
}

/**
 * Fetch player images for a list of player IDs
 */
export async function getPlayerImages(playerIds: string[]): Promise<Map<string, string | null>> {
  const playerImageMap = new Map<string, string | null>()

  if (playerIds.length === 0) {
    return playerImageMap
  }

  const supabase = await createClient()
  const { data: playerImages } = await supabase
    .from('dim_player')
    .select('player_id, player_image')
    .in('player_id', playerIds)

  if (playerImages) {
    playerImages.forEach((p: any) => {
      playerImageMap.set(String(p.player_id), p.player_image || null)
    })
  }

  return playerImageMap
}

/**
 * Check if a game is a championship game (last game of a completed season)
 */
export async function checkIsChampionshipGame(
  gameId: number,
  seasonId: string | number | null | undefined
): Promise<boolean> {
  if (!seasonId) return false

  const supabase = await createClient()

  // Get current season to exclude it
  const { data: currentSeasonData } = await supabase
    .from('v_standings_current')
    .select('season_id')
    .limit(1)
    .maybeSingle()

  const currentSeason = currentSeasonData?.season_id || null

  // Only check for championship if this is NOT the current season
  if (currentSeason && String(seasonId) === String(currentSeason)) {
    return false
  }

  const { data: lastGame } = await supabase
    .from('dim_schedule')
    .select('game_id')
    .eq('season_id', seasonId)
    .not('home_total_goals', 'is', null)
    .not('away_total_goals', 'is', null)
    .order('date', { ascending: false })
    .order('game_id', { ascending: false })
    .limit(1)
    .maybeSingle()

  return lastGame?.game_id === gameId
}

/**
 * Fetch all events for play-by-play timeline
 */
export async function getGameAllEvents(gameId: number): Promise<any[]> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('fact_events')
    .select('*')
    .eq('game_id', gameId)
    .order('event_id', { ascending: true })
    .limit(5000)

  if (error) {
    console.error('Error fetching all events:', error)
    return []
  }
  return data || []
}

/**
 * Fetch shifts for shift chart
 */
export async function getGameShifts(gameId: number): Promise<any[]> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('fact_shifts')
    .select('*')
    .eq('game_id', gameId)
    .order('shift_start_total_seconds', { ascending: true })
    .limit(3000)

  if (error) {
    console.error('Error fetching shifts:', error)
    return []
  }
  return data || []
}

/**
 * Fetch highlight events (goals, saves, highlights)
 */
export async function getGameHighlightEvents(gameId: number): Promise<any[]> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('fact_events')
    .select('*')
    .eq('game_id', gameId)
    .or('is_goal.eq.1,is_highlight.eq.1,is_save.eq.1')
    .order('time_start_total_seconds', { ascending: true })
    .limit(50)

  if (error) {
    console.error('Error fetching highlight events:', error)
    return []
  }
  return data || []
}
