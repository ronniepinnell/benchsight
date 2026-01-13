import { createClient } from '@/lib/supabase/server'
import type { VSummaryLeague } from '@/types/database'

// Get league summary statistics
export async function getLeagueSummary(): Promise<VSummaryLeague | null> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('v_summary_league')
    .select('*')
    .single()
  
  if (error) return null
  return data
}

// Get current season ID
export async function getCurrentSeason(): Promise<string | null> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('v_standings_current')
    .select('season_id')
    .limit(1)
    .single()
  
  if (error) return null
  return data?.season_id ?? null
}

// Get all seasons (excluding Spring seasons)
export async function getAllSeasons(): Promise<string[]> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('v_standings_all_seasons')
    .select('season_id')
  
  if (error) throw error
  
  // Get unique season IDs and filter out Spring seasons (ending with 'S')
  const seasons = [...new Set((data ?? []).map(d => d.season_id))]
    .filter(seasonId => !seasonId.endsWith('S'))
  return seasons
}
