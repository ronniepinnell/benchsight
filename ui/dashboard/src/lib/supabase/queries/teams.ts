import { createClient } from '@/lib/supabase/server'
import type { 
  DimTeam, 
  VStandingsCurrent
} from '@/types/database'

// Get all teams
export async function getTeams(): Promise<DimTeam[]> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('dim_team')
    .select('*')
    .order('team_name')
  
  if (error) throw error
  return data ?? []
}

// Get teams for a specific season (from dim_schedule)
export async function getTeamsBySeason(seasonId: string | null): Promise<DimTeam[]> {
  if (!seasonId) {
    return getTeams()
  }
  
  const supabase = await createClient()
  
  // Get unique team IDs from games in this season
  const { data: scheduleData, error: scheduleError } = await supabase
    .from('dim_schedule')
    .select('home_team_id, away_team_id')
    .eq('season_id', seasonId)
  
  if (scheduleError) {
    console.error('Error fetching teams for season:', scheduleError)
    return []
  }
  
  if (!scheduleData || scheduleData.length === 0) {
    return []
  }
  
  // Get unique team IDs
  const teamIds = [...new Set(
    scheduleData.flatMap(game => [
      game.home_team_id ? String(game.home_team_id) : null,
      game.away_team_id ? String(game.away_team_id) : null
    ]).filter(Boolean)
  )]
  
  if (teamIds.length === 0) {
    return []
  }
  
  // Fetch team details
  const { data: teams, error: teamsError } = await supabase
    .from('dim_team')
    .select('*')
    .in('team_id', teamIds)
    .order('team_name')
  
  if (teamsError) {
    console.error('Error fetching team details:', teamsError)
    return []
  }
  
  return teams ?? []
}

// Get team by ID
export async function getTeamById(teamId: string): Promise<DimTeam | null> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('dim_team')
    .select('*')
    .eq('team_id', teamId)
    .single()
  
  if (error) return null
  return data
}

// Get team by name
export async function getTeamByName(teamName: string): Promise<DimTeam | null> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('dim_team')
    .select('*')
    .eq('team_name', teamName)
    .single()
  
  if (error) return null
  return data
}

// Get current standings
export async function getStandings(): Promise<VStandingsCurrent[]> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('v_standings_current')
    .select('*')
    .order('standing', { ascending: true })
  
  if (error) throw error
  return data ?? []
}

// Get standings with team info
export async function getStandingsWithTeamInfo(): Promise<(VStandingsCurrent & { team: DimTeam | null })[]> {
  const standings = await getStandings()
  const teams = await getTeams()
  
  return standings.map(standing => ({
    ...standing,
    team: teams.find(t => t.team_id === standing.team_id) ?? null
  }))
}

// Get team roster for current season
export async function getTeamRoster(teamName: string) {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('v_rankings_players_current')
    .select('*')
    .eq('team_name', teamName)
    .order('points', { ascending: false })
  
  if (error) throw error
  return data ?? []
}

// Get team's recent games
export async function getTeamRecentGames(teamName: string, limit: number = 10) {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('v_recent_games')
    .select('*')
    .or(`home_team_name.eq.${teamName},away_team_name.eq.${teamName}`)
    .order('date', { ascending: false })
    .limit(limit)
  
  if (error) throw error
  return data ?? []
}

// Get head-to-head records
export async function getHeadToHead(team1: string, team2: string) {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('v_standings_h2h')
    .select('*')
    .or(`team_name.eq.${team1},team_name.eq.${team2}`)
  
  if (error) throw error
  return data ?? []
}
