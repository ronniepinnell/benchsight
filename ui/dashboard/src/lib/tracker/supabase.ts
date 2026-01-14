/**
 * Supabase Integration for Tracker
 * 
 * Functions to load rosters and game data from Supabase
 */

import { createClient } from '@/lib/supabase/client'
import type { Player } from './types'

interface RosterPlayer {
  player_id?: string
  player_game_number: number | string
  player_full_name?: string
  player_position?: string
  team_name: string
  team_id?: string
}

/**
 * Load roster for a specific game
 */
export async function loadGameRoster(gameId: string): Promise<{ home: Player[]; away: Player[] }> {
  const supabase = createClient()

  try {
    // Query fact_gameroster or stage_fact_gameroster
    // Try fact_gameroster first (production), fallback to stage (development)
    let { data: rosterData, error } = await supabase
      .from('fact_gameroster')
      .select('*')
      .eq('game_id', gameId)

    // Fallback to stage table if fact table is empty or doesn't exist
    if (!rosterData || rosterData.length === 0 || error) {
      const stageResult = await supabase
        .from('stage_fact_gameroster')
        .select('*')
        .eq('game_id', gameId)
      
      if (stageResult.data) {
        rosterData = stageResult.data
        error = stageResult.error
      }
    }

    if (error) {
      console.error('Error loading roster:', error)
      return { home: [], away: [] }
    }

    if (!rosterData || rosterData.length === 0) {
      console.warn(`No roster found for game ${gameId}`)
      return { home: [], away: [] }
    }

    // Get game info to determine home/away
    let { data: gameData } = await supabase
      .from('stage_dim_schedule')
      .select('home_team, away_team')
      .eq('game_id', gameId)
      .single()

    if (!gameData) {
      // Try fact_game_status as fallback
      const { data: gameStatusData } = await supabase
        .from('fact_game_status')
        .select('home_team, away_team')
        .eq('game_id', gameId)
        .single()
      
      if (gameStatusData) {
        gameData = {
          home_team: gameStatusData.home_team || '',
          away_team: gameStatusData.away_team || ''
        }
      } else {
        gameData = { home_team: '', away_team: '' }
      }
    }

    const homeTeamName = gameData?.home_team || ''
    const awayTeamName = gameData?.away_team || ''

    // Group players by team
    const homePlayers: Player[] = []
    const awayPlayers: Player[] = []

    rosterData.forEach((row: any) => {
      const player: Player = {
        num: String(row.player_game_number || row.player_game_number || ''),
        name: row.player_full_name || row.player_name || '',
        team: (row.team_name || '').toLowerCase() === homeTeamName.toLowerCase() ? 'home' : 'away',
        role: undefined,
        roleNum: undefined,
        xy: [],
        playD1: '',
        playD2: '',
        playSuccess: '',
        pressuredBy: '',
        sideOfPuck: ''
      }

      // Determine if home or away based on team name match
      if ((row.team_name || '').toLowerCase() === homeTeamName.toLowerCase()) {
        homePlayers.push(player)
      } else if ((row.team_name || '').toLowerCase() === awayTeamName.toLowerCase()) {
        awayPlayers.push(player)
      } else {
        // Fallback: use position or other heuristics
        // For now, default to home if can't determine
        homePlayers.push(player)
      }
    })

    // Sort by jersey number
    homePlayers.sort((a, b) => {
      const numA = parseInt(a.num) || 999
      const numB = parseInt(b.num) || 999
      return numA - numB
    })

    awayPlayers.sort((a, b) => {
      const numA = parseInt(a.num) || 999
      const numB = parseInt(b.num) || 999
      return numA - numB
    })

    return { home: homePlayers, away: awayPlayers }
  } catch (error) {
    console.error('Error in loadGameRoster:', error)
    return { home: [], away: [] }
  }
}

/**
 * Load game data (teams, date, etc.)
 */
export async function loadGameData(gameId: string): Promise<{
  gameId: string
  homeTeam: string
  awayTeam: string
  gameDate?: string
  homeScore?: number
  awayScore?: number
} | null> {
  const supabase = createClient()

  try {
    // Try stage_dim_schedule first
    let { data: gameData, error } = await supabase
      .from('stage_dim_schedule')
      .select('*')
      .eq('game_id', gameId)
      .single()

    // Fallback to fact_game_status
    if (!gameData || error) {
      const statusResult = await supabase
        .from('fact_game_status')
        .select('*')
        .eq('game_id', gameId)
        .single()
      
      if (statusResult.data) {
        gameData = statusResult.data
        error = statusResult.error
      }
    }

    if (error || !gameData) {
      console.error('Error loading game data:', error)
      return null
    }

    return {
      gameId,
      homeTeam: gameData.home_team || 'Home',
      awayTeam: gameData.away_team || 'Away',
      gameDate: gameData.game_date || gameData.date,
      homeScore: gameData.home_score || gameData.official_home_goals,
      awayScore: gameData.away_score || gameData.official_away_goals
    }
  } catch (error) {
    console.error('Error in loadGameData:', error)
    return null
  }
}

/**
 * Load tracking data (events and shifts) for a game
 * Note: This assumes tracking data is stored in Supabase tables
 */
export async function loadTrackingData(gameId: string): Promise<{
  events: any[]
  shifts: any[]
} | null> {
  const supabase = createClient()

  try {
    // Try to load from tracking tables if they exist
    // This is a placeholder - actual table structure may vary
    const { data: eventsData, error: eventsError } = await supabase
      .from('stage_events_tracking')
      .select('*')
      .eq('game_id', gameId)
      .order('period', { ascending: true })
      .order('start_time', { ascending: false })

    const { data: shiftsData, error: shiftsError } = await supabase
      .from('stage_shifts_tracking')
      .select('*')
      .eq('game_id', gameId)
      .order('period', { ascending: true })
      .order('start_time', { ascending: false })

    if (eventsError || shiftsError) {
      console.warn('Tracking tables may not exist or have different structure:', eventsError, shiftsError)
      // Return empty arrays - data will be loaded from localStorage if available
      return { events: [], shifts: [] }
    }

    return {
      events: eventsData || [],
      shifts: shiftsData || []
    }
  } catch (error) {
    console.error('Error in loadTrackingData:', error)
    // Return empty - will fall back to localStorage
    return { events: [], shifts: [] }
  }
}
