import { createClient } from '@/lib/supabase/server'

export interface PercentileStats {
  overall: number | null
  byRating: number | null
  byPosition: number | null
  byPositionRating: number | null
}

export interface PercentileContext {
  playerId: string
  statValue: number
  statKey: string
  position?: string
  rating?: number
  seasonId?: string
  gameType?: string
}

/**
 * Calculate percentile for a stat value compared to all players
 * Returns percentile (0-100) where 100 = best
 */
export async function calculatePercentile({
  playerId,
  statValue,
  statKey,
  position,
  rating,
  seasonId,
  gameType = 'All'
}: PercentileContext): Promise<PercentileStats> {
  const supabase = await createClient()
  
  // Try fact_player_season_stats first (has position, rating)
  // If stat not found there, try fact_player_game_stats aggregated
  let query = supabase
    .from('fact_player_season_stats_basic')
    .select('*')
  
  if (seasonId) {
    query = query.eq('season_id', seasonId)
  }
  if (gameType !== 'All') {
    query = query.eq('game_type', gameType)
  } else {
    query = query.eq('game_type', 'All')
  }
  
  const { data: seasonStats } = await query
  
  // Also try fact_player_game_stats if season stats don't have the stat
  let allPlayers: any[] = []
  
  if (seasonStats && seasonStats.length > 0) {
    // Filter to players that have this stat
    allPlayers = seasonStats.filter(p => {
      const val = p[statKey]
      return val !== null && val !== undefined && val !== ''
    }).map(p => ({
      player_id: String(p.player_id),
      [statKey]: p[statKey],
      position: p.position,
      skill_rating: p.skill_rating,
    }))
  }
  
  // If no season stats, try aggregating from game stats
  if (allPlayers.length === 0 && seasonId) {
    const { data: gameStats } = await supabase
      .from('fact_player_game_stats')
      .select('player_id, position, skill_rating, ' + statKey)
      .then(({ data }) => ({ data }))
      .catch(() => ({ data: [] }))
    
    if (gameStats) {
      // Get schedule to filter by season
      const { data: schedule } = await supabase
        .from('dim_schedule')
        .select('game_id')
        .eq('season_id', seasonId)
        .then(({ data }) => ({ data }))
        .catch(() => ({ data: [] }))
      
      const gameIds = (schedule || []).map(s => s.game_id).filter(Boolean)
      const filteredGameStats = gameIds.length > 0 
        ? gameStats.filter(g => gameIds.includes(g.game_id))
        : gameStats
      
      // Aggregate by player
      const playerMap = new Map<string, any>()
      filteredGameStats.forEach((stat: any) => {
        const pid = String(stat.player_id)
        const existing = playerMap.get(pid) || {
          player_id: pid,
          position: stat.position,
          skill_rating: stat.skill_rating,
          [statKey]: 0,
          count: 0,
        }
        const val = stat[statKey]
        if (val !== null && val !== undefined) {
          existing[statKey] = (existing[statKey] || 0) + (typeof val === 'number' ? val : parseFloat(String(val)) || 0)
          existing.count++
        }
        playerMap.set(pid, existing)
      })
      
      allPlayers = Array.from(playerMap.values()).filter(p => p[statKey] > 0)
    }
  }
  
  if (!allPlayers || allPlayers.length === 0) {
    return { overall: null, byRating: null, byPosition: null, byPositionRating: null }
  }
  
  // Filter valid values and convert to numbers
  const validStats = allPlayers
    .map(p => {
      const val = p[statKey]
      const numVal = typeof val === 'number' ? val : parseFloat(String(val))
      return {
        playerId: String(p.player_id),
        value: isNaN(numVal) ? null : numVal,
        position: p.position,
        rating: p.skill_rating ? (typeof p.skill_rating === 'number' ? p.skill_rating : parseFloat(String(p.skill_rating))) : null,
      }
    })
    .filter(p => p.value !== null && p.value !== undefined && !isNaN(p.value!))
  
  if (validStats.length === 0) {
    return { overall: null, byRating: null, byPosition: null, byPositionRating: null }
  }
  
  // Determine if higher is better (most stats, except GAA, PIM, etc.)
  const lowerIsBetter = ['gaa', 'goals_against', 'pim'].some(term => statKey.toLowerCase().includes(term))
  
  // Sort by value
  const sorted = [...validStats].sort((a, b) => 
    lowerIsBetter ? (a.value! - b.value!) : (b.value! - a.value!)
  )
  
  // Calculate overall percentile
  const overallRank = sorted.findIndex(p => p.playerId === playerId)
  const overall = overallRank >= 0 ? ((sorted.length - overallRank) / sorted.length) * 100 : null
  
  // Calculate by position percentile
  let byPosition: number | null = null
  if (position) {
    const positionStats = validStats.filter(p => p.position === position)
    if (positionStats.length > 0) {
      const sortedByPosition = [...positionStats].sort((a, b) => 
        lowerIsBetter ? (a.value! - b.value!) : (b.value! - a.value!)
      )
      const positionRank = sortedByPosition.findIndex(p => p.playerId === playerId)
      byPosition = positionRank >= 0 ? ((sortedByPosition.length - positionRank) / sortedByPosition.length) * 100 : null
    }
  }
  
  // Calculate by rating percentile (within ±0.5 rating)
  let byRating: number | null = null
  if (rating !== undefined && rating !== null && !isNaN(rating)) {
    const ratingRange = [rating - 0.5, rating + 0.5]
    const ratingStats = validStats.filter(p => 
      p.rating !== null && p.rating !== undefined && !isNaN(p.rating) &&
      p.rating >= ratingRange[0] && p.rating <= ratingRange[1]
    )
    if (ratingStats.length > 0) {
      const sortedByRating = [...ratingStats].sort((a, b) => 
        lowerIsBetter ? (a.value! - b.value!) : (b.value! - a.value!)
      )
      const ratingRank = sortedByRating.findIndex(p => p.playerId === playerId)
      byRating = ratingRank >= 0 ? ((sortedByRating.length - ratingRank) / sortedByRating.length) * 100 : null
    }
  }
  
  // Calculate by position/rating percentile
  let byPositionRating: number | null = null
  if (position && rating !== undefined && rating !== null && !isNaN(rating)) {
    const ratingRange = [rating - 0.5, rating + 0.5]
    const positionRatingStats = validStats.filter(p => 
      p.position === position &&
      p.rating !== null && p.rating !== undefined && !isNaN(p.rating) &&
      p.rating >= ratingRange[0] && p.rating <= ratingRange[1]
    )
    if (positionRatingStats.length > 0) {
      const sortedByPositionRating = [...positionRatingStats].sort((a, b) => 
        lowerIsBetter ? (a.value! - b.value!) : (b.value! - a.value!)
      )
      const positionRatingRank = sortedByPositionRating.findIndex(p => p.playerId === playerId)
      byPositionRating = positionRatingRank >= 0 
        ? ((sortedByPositionRating.length - positionRatingRank) / sortedByPositionRating.length) * 100 
        : null
    }
  }
  
  return {
    overall: overall !== null ? Math.round(overall * 10) / 10 : null,
    byRating: byRating !== null ? Math.round(byRating * 10) / 10 : null,
    byPosition: byPosition !== null ? Math.round(byPosition * 10) / 10 : null,
    byPositionRating: byPositionRating !== null ? Math.round(byPositionRating * 10) / 10 : null,
  }
}

/**
 * Get percentile stats for multiple stats at once (batch calculation)
 */
export async function getPlayerPercentiles(
  playerId: string,
  stats: Record<string, number>,
  position?: string,
  rating?: number,
  seasonId?: string,
  gameType: string = 'All'
): Promise<Record<string, PercentileStats>> {
  const percentiles: Record<string, PercentileStats> = {}
  
  // Calculate percentiles for each stat
  const calculations = Object.entries(stats).map(([statKey, statValue]) =>
    calculatePercentile({
      playerId,
      statValue,
      statKey,
      position,
      rating,
      seasonId,
      gameType
    }).then(result => ({ statKey, result }))
  )
  
  const results = await Promise.all(calculations)
  
  results.forEach(({ statKey, result }) => {
    percentiles[statKey] = result
  })
  
  return percentiles
}
