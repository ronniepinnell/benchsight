import { createClient } from '@/lib/supabase/server'
import type { 
  VRecentGames,
  FactPlayerGameStats,
  FactGoalieGameStats,
  FactEvents,
  FactShotXY
} from '@/types/database'

// Get recent games
export async function getRecentGames(limit: number = 10): Promise<VRecentGames[]> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('v_recent_games')
    .select('*')
    .order('date', { ascending: false })
    .limit(limit)
  
  if (error) throw error
  return data ?? []
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
    .order('time_seconds', { ascending: true })
  
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
  const { data, error } = await supabase
    .from('dim_schedule')
    .select('*')
    .gte('game_date', new Date().toISOString().split('T')[0])
    .order('game_date', { ascending: true })
    .order('game_time', { ascending: true })
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
    .order('game_date', { ascending: true })
    .limit(limit)
  
  if (error) throw error
  return data ?? []
}
