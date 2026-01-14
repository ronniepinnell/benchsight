import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ playerId: string }> }
) {
  try {
    const { playerId } = await params
    const searchParams = request.nextUrl.searchParams
    const stat = searchParams.get('stat')
    const gameIdsParam = searchParams.get('gameIds')
    
    if (!playerId || !stat) {
      return NextResponse.json({ error: 'Missing playerId or stat' }, { status: 400 })
    }

    const supabase = await createClient()
    
    // Get game stats
    let query = supabase
      .from('fact_player_game_stats')
      .select('game_id, date, opponent_team_name, team_name, *')
      .eq('player_id', playerId)
    
    // Filter by game IDs if provided
    if (gameIdsParam) {
      const gameIds = gameIdsParam.split(',').map(id => parseInt(id)).filter(id => !isNaN(id))
      if (gameIds.length > 0) {
        query = query.in('game_id', gameIds)
      }
    }
    
    const { data: gameStats, error: statsError } = await query
      .limit(100)
    
    if (statsError) {
      console.error('Error fetching game stats:', statsError)
      return NextResponse.json({ error: 'Failed to fetch game stats' }, { status: 500 })
    }

    if (!gameStats || gameStats.length === 0) {
      return NextResponse.json({ games: [] })
    }

    // Get schedule data to merge dates and opponent info
    const gameIds = [...new Set(gameStats.map(g => g.game_id).filter(Boolean))]
    const { data: scheduleData } = await supabase
      .from('dim_schedule')
      .select('game_id, date, home_team_name, away_team_name, home_team_id, away_team_id')
      .in('game_id', gameIds.length > 0 ? gameIds : [0])
      .then(({ data }) => ({ data }))
      .catch(() => ({ data: [] }))
    
    const scheduleMap = new Map((scheduleData || []).map(s => [s.game_id, s]))
    
    // Merge schedule data into game stats and sort by date
    const games = gameStats
      .map(game => {
        const schedule = scheduleMap.get(game.game_id)
        const opponent = game.opponent_team_name || 
          (schedule && game.team_name === schedule.home_team_name ? schedule.away_team_name : schedule?.home_team_name) ||
          game.team_name
        const date = game.date || schedule?.date
        
        return {
          ...game,
          date: date,
          opponent_team_name: opponent,
          team_name: game.team_name || schedule?.home_team_name || schedule?.away_team_name,
        }
      })
      .sort((a, b) => {
        const dateA = a.date ? new Date(a.date).getTime() : 0
        const dateB = b.date ? new Date(b.date).getTime() : 0
        return dateB - dateA // Most recent first
      })
      .slice(0, 50)

    return NextResponse.json({ games })
  } catch (error) {
    console.error('Error in game-stats API:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
