import { createClient } from '@/lib/supabase/server'
import type { 
  VLeaderboardGoalieGAA,
  VLeaderboardGoalieWins,
  VRankingsGoaliesCurrent,
  VSummaryGoalieCareer,
  VDetailGoalieGames,
  FactGoalieGameStats
} from '@/types/database'

// Get goalie GAA leaderboard
export async function getGoalieGAALeaders(limit: number = 20): Promise<VLeaderboardGoalieGAA[]> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('v_leaderboard_goalie_gaa')
    .select('*')
    .order('season_rank', { ascending: true })
    .limit(limit)
  
  if (error) throw error
  return data ?? []
}

// Get goalie wins leaderboard
export async function getGoalieWinsLeaders(limit: number = 20): Promise<VLeaderboardGoalieWins[]> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('v_leaderboard_goalie_wins')
    .select('*')
    .order('season_rank', { ascending: true })
    .limit(limit)
  
  if (error) throw error
  return data ?? []
}

// Get current goalie rankings
export async function getGoalieRankings(limit: number = 20): Promise<VRankingsGoaliesCurrent[]> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('v_rankings_goalies_current')
    .select('*')
    .order('wins_rank', { ascending: true })
    .limit(limit)
  
  if (error) throw error
  return data ?? []
}

// Get goalie career summary
export async function getGoalieCareerSummary(playerId: string): Promise<VSummaryGoalieCareer | null> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('v_summary_goalie_career')
    .select('*')
    .eq('player_id', playerId)
    .single()
  
  if (error) return null
  return data
}

// Get goalie's game log
export async function getGoalieGameLog(playerId: string, limit: number = 20): Promise<VDetailGoalieGames[]> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('v_detail_goalie_games')
    .select('*')
    .eq('player_id', playerId)
    .order('date', { ascending: false })
    .limit(limit)
  
  if (error) throw error
  return data ?? []
}

// Get goalie's detailed game stats
export async function getGoalieGameStats(playerId: string, gameId: number): Promise<FactGoalieGameStats | null> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('fact_goalie_game_stats')
    .select('*')
    .eq('player_id', playerId)
    .eq('game_id', gameId)
    .single()
  
  if (error) return null
  return data
}

// Get goalie current stats
export async function getGoalieCurrentStats(playerId: string): Promise<VRankingsGoaliesCurrent | null> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('v_rankings_goalies_current')
    .select('*')
    .eq('player_id', playerId)
    .single()
  
  if (error) return null
  return data
}
