import { createClient } from '@/lib/supabase/server'
import type { 
  DimPlayer,
  VLeaderboardPoints,
  VLeaderboardGoals,
  VLeaderboardAssists,
  VRankingsPlayersCurrent,
  VComparePlayers,
  VSummaryPlayerCareer,
  VRecentHotPlayers,
  VDetailPlayerGames,
  FactPlayerGameStats
} from '@/types/database'

// Get all players
export async function getPlayers(): Promise<DimPlayer[]> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('dim_player')
    .select('*')
    .order('player_full_name')
  
  if (error) throw error
  return data ?? []
}

// Get player by ID
export async function getPlayerById(playerId: number): Promise<DimPlayer | null> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('dim_player')
    .select('*')
    .eq('player_id', playerId)
    .single()
  
  if (error) return null
  return data
}

// Search players by name
export async function searchPlayers(query: string, limit: number = 10): Promise<DimPlayer[]> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('dim_player')
    .select('*')
    .ilike('player_full_name', `%${query}%`)
    .limit(limit)
  
  if (error) throw error
  return data ?? []
}

// Get points leaderboard
export async function getPointsLeaders(limit: number = 20): Promise<VLeaderboardPoints[]> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('v_leaderboard_points')
    .select('*')
    .order('season_rank', { ascending: true })
    .limit(limit)
  
  if (error) throw error
  return data ?? []
}

// Get goals leaderboard
export async function getGoalsLeaders(limit: number = 20): Promise<VLeaderboardGoals[]> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('v_leaderboard_goals')
    .select('*')
    .order('season_rank', { ascending: true })
    .limit(limit)
  
  if (error) throw error
  return data ?? []
}

// Get assists leaderboard
export async function getAssistsLeaders(limit: number = 20): Promise<VLeaderboardAssists[]> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('v_leaderboard_assists')
    .select('*')
    .order('season_rank', { ascending: true })
    .limit(limit)
  
  if (error) throw error
  return data ?? []
}

// Get current player rankings
export async function getCurrentRankings(limit: number = 50): Promise<VRankingsPlayersCurrent[]> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('v_rankings_players_current')
    .select('*')
    .order('points_rank', { ascending: true })
    .limit(limit)
  
  if (error) throw error
  return data ?? []
}

// Get player comparison data
export async function getPlayerComparison(playerId1: number, playerId2: number): Promise<VComparePlayers[]> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('v_compare_players')
    .select('*')
    .in('player_id', [playerId1, playerId2])
  
  if (error) throw error
  return data ?? []
}

// Get player career summary
export async function getPlayerCareerSummary(playerId: number): Promise<VSummaryPlayerCareer | null> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('v_summary_player_career')
    .select('*')
    .eq('player_id', playerId)
    .single()
  
  if (error) return null
  return data
}

// Get hot players (recent performance)
export async function getHotPlayers(limit: number = 5): Promise<VRecentHotPlayers[]> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('v_recent_hot_players')
    .select('*')
    .order('avg_points', { ascending: false })
    .limit(limit)
  
  if (error) throw error
  return data ?? []
}

// Get player's game log
export async function getPlayerGameLog(playerId: number, limit: number = 20): Promise<FactPlayerGameStats[]> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('fact_player_game_stats')
    .select('*')
    .eq('player_id', playerId)
    .order('date', { ascending: false })
    .limit(limit)
  
  if (error) throw error
  return data ?? []
}

// Get player's detailed game stats
export async function getPlayerGameStats(playerId: number, gameId: number): Promise<FactPlayerGameStats | null> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('fact_player_game_stats')
    .select('*')
    .eq('player_id', playerId)
    .eq('game_id', gameId)
    .single()
  
  if (error) return null
  return data
}

// Get player's current season stats
export async function getPlayerCurrentStats(playerId: number): Promise<VRankingsPlayersCurrent | null> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('v_rankings_players_current')
    .select('*')
    .eq('player_id', playerId)
    .single()
  
  if (error) return null
  return data
}
