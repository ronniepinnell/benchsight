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

// Get all seasons (excluding Spring seasons and Summer seasons)
// Optionally include the current season even if it's not in standings yet
export async function getAllSeasons(includeCurrentSeason: boolean = true): Promise<string[]> {
  const supabase = await createClient()
  const { data, error } = await supabase
    .from('v_standings_all_seasons')
    .select('season_id, season')
  
  if (error) throw error
  
  // Get current season first (before filtering)
  const currentSeason = includeCurrentSeason ? await getCurrentSeason() : null
  
  // Get unique season IDs and filter out Spring seasons (ending with 'S'), Summer seasons, and future 2025-2026 seasons
  let seasons = [...new Set((data ?? []).map(d => d.season_id))]
    .filter(seasonId => {
      // Always include current season, even if it would normally be filtered
      if (currentSeason && seasonId === currentSeason) return true
      
      // Filter out Spring seasons (ending with 'S')
      if (seasonId.endsWith('S')) return false
      
      // Filter out Summer seasons by checking the season string
      const seasonData = data?.find(d => d.season_id === seasonId)
      const seasonString = String(seasonData?.season || '')
      if (seasonString.toLowerCase().includes('summer')) return false
      
      // Filter out 2025-2026 seasons (seasons starting with 2025, like "20252026")
      // But keep 2024-2025 seasons (like "20242025")
      if (seasonId.startsWith('2025')) return false
      
      // Also filter out season strings that specifically mention "2025-2026" or start with "2025"
      if (seasonString.includes('2025-2026') || seasonString.startsWith('2025')) return false
      
      return true
    })
  
  // Ensure current season is included (in case it wasn't in the standings data)
  if (currentSeason && !seasons.includes(currentSeason)) {
    seasons.push(currentSeason)
  }
  
  return seasons
}
