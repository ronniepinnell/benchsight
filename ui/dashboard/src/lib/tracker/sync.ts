/**
 * Cloud Sync Functionality
 * 
 * Saves events and shifts to Supabase for cloud persistence
 */

import { createClient } from '@/lib/supabase/client'
import type { Event, Shift, GameState } from './types'
import { toast } from './utils/toast'

/**
 * Transform event to Supabase format
 */
function transformEventForSupabase(event: Event, gameId: string): any {
  return {
    game_id: gameId,
    event_index: event.idx ?? 0,
    period: event.period,
    type: event.type,
    team: event.team,
    start_time: event.start_time,
    end_time: event.end_time || null,
    zone: event.zone || null,
    success: event.success ?? null,
    strength: event.strength || '5v5',
    detail1: event.detail1 || null,
    detail2: event.detail2 || null,
    is_highlight: event.isHighlight || false,
    video_url: event.isHighlight && event.videoUrl ? event.videoUrl : null, // v23.7: Individual highlight video URL
    
    // XY coordinates (JSON)
    puck_xy: event.puckXY ? JSON.stringify(event.puckXY) : null,
    net_xy: event.netXY ? JSON.stringify(event.netXY) : null,
    
    // Players (JSON array)
    players: event.players ? JSON.stringify(event.players) : null,
    
    // Linked event
    linked_event_idx: (event as any).linkedEventIdx ?? null,
    
    // Metadata
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
}

/**
 * Transform shift to Supabase format
 */
function transformShiftForSupabase(shift: Shift, gameId: string): any {
  return {
    game_id: gameId,
    shift_index: shift.idx ?? 0,
    period: shift.period,
    start_time: shift.start_time,
    end_time: shift.end_time || null,
    start_type: shift.start_type || null,
    stop_type: shift.stop_type || null,
    strength: shift.strength || '5v5',
    
    // Lineups (JSON)
    home_lineup: shift.home ? JSON.stringify(shift.home) : null,
    away_lineup: shift.away ? JSON.stringify(shift.away) : null,
    
    // Metadata
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
}

/**
 * Save events to Supabase
 */
export async function saveEventsToSupabase(
  gameId: string,
  events: Event[]
): Promise<{ success: boolean; saved: number; errors: number }> {
  const supabase = createClient()
  
  if (!gameId || events.length === 0) {
    return { success: true, saved: 0, errors: 0 }
  }

  try {
    // Delete existing events for this game first (upsert strategy)
    // Or use upsert if we have unique constraints
    const { error: deleteError } = await supabase
      .from('stage_events_tracking')
      .delete()
      .eq('game_id', gameId)

    if (deleteError) {
      console.warn('Error deleting existing events (may not exist):', deleteError)
      // Continue anyway - table might not exist or be empty
    }

    // Transform and insert events
    const eventsToInsert = events.map(evt => transformEventForSupabase(evt, gameId))

    // Insert in batches to avoid payload size limits
    const batchSize = 100
    let saved = 0
    let errors = 0

    for (let i = 0; i < eventsToInsert.length; i += batchSize) {
      const batch = eventsToInsert.slice(i, i + batchSize)
      
      const { error: insertError } = await supabase
        .from('stage_events_tracking')
        .insert(batch)

      if (insertError) {
        console.error('Error inserting events batch:', insertError)
        errors += batch.length
      } else {
        saved += batch.length
      }
    }

    return { success: errors === 0, saved, errors }
  } catch (error: any) {
    console.error('Error saving events to Supabase:', error)
    return { success: false, saved: 0, errors: events.length }
  }
}

/**
 * Save shifts to Supabase
 */
export async function saveShiftsToSupabase(
  gameId: string,
  shifts: Shift[]
): Promise<{ success: boolean; saved: number; errors: number }> {
  const supabase = createClient()
  
  if (!gameId || shifts.length === 0) {
    return { success: true, saved: 0, errors: 0 }
  }

  try {
    // Delete existing shifts for this game
    const { error: deleteError } = await supabase
      .from('stage_shifts_tracking')
      .delete()
      .eq('game_id', gameId)

    if (deleteError) {
      console.warn('Error deleting existing shifts (may not exist):', deleteError)
    }

    // Transform and insert shifts
    const shiftsToInsert = shifts.map(shift => transformShiftForSupabase(shift, gameId))

    // Insert in batches
    const batchSize = 100
    let saved = 0
    let errors = 0

    for (let i = 0; i < shiftsToInsert.length; i += batchSize) {
      const batch = shiftsToInsert.slice(i, i + batchSize)
      
      const { error: insertError } = await supabase
        .from('stage_shifts_tracking')
        .insert(batch)

      if (insertError) {
        console.error('Error inserting shifts batch:', insertError)
        errors += batch.length
      } else {
        saved += batch.length
      }
    }

    return { success: errors === 0, saved, errors }
  } catch (error: any) {
    console.error('Error saving shifts to Supabase:', error)
    return { success: false, saved: 0, errors: shifts.length }
  }
}

/**
 * Save entire game state to Supabase
 */
export async function saveGameStateToSupabase(
  gameState: GameState
): Promise<{ success: boolean; message: string }> {
  if (!gameState.gameId) {
    return { success: false, message: 'No game ID' }
  }

  const gameId = String(gameState.gameId)

  try {
    // Save events
    const eventsResult = await saveEventsToSupabase(gameId, gameState.events)
    
    // Save shifts
    const shiftsResult = await saveShiftsToSupabase(gameId, gameState.shifts)

    const totalSaved = eventsResult.saved + shiftsResult.saved
    const totalErrors = eventsResult.errors + shiftsResult.errors

    if (totalErrors > 0) {
      return {
        success: false,
        message: `Saved ${totalSaved} items, ${totalErrors} errors`
      }
    }

    return {
      success: true,
      message: `Saved ${totalSaved} items to cloud`
    }
  } catch (error: any) {
    return {
      success: false,
      message: `Sync failed: ${error.message}`
    }
  }
}

/**
 * Load events from Supabase
 */
export async function loadEventsFromSupabase(
  gameId: string
): Promise<Event[]> {
  const supabase = createClient()

  try {
    const { data, error } = await supabase
      .from('stage_events_tracking')
      .select('*')
      .eq('game_id', gameId)
      .order('period', { ascending: true })
      .order('start_time', { ascending: false })

    if (error) {
      console.error('Error loading events:', error)
      return []
    }

    if (!data) return []

    // Transform Supabase format back to Event format
    return data.map((row: any, idx: number): Event => {
      const event: Event = {
        idx,
        period: row.period || 1,
        type: row.type as any,
        team: row.team as 'home' | 'away',
        start_time: row.start_time || '',
        end_time: row.end_time || undefined,
        zone: row.zone || undefined,
        success: row.success ?? undefined,
        strength: row.strength || '5v5',
        detail1: row.detail1 || undefined,
        detail2: row.detail2 || undefined,
        isHighlight: row.is_highlight || false,
        videoUrl: row.video_url || undefined, // v23.7: Individual highlight video URL
        players: row.players ? JSON.parse(row.players) : [],
        puckXY: row.puck_xy ? JSON.parse(row.puck_xy) : [],
        netXY: row.net_xy ? JSON.parse(row.net_xy) : undefined
      }

      // Add linked event if present
      if (row.linked_event_idx !== null) {
        (event as any).linkedEventIdx = row.linked_event_idx
      }

      return event
    })
  } catch (error) {
    console.error('Error in loadEventsFromSupabase:', error)
    return []
  }
}

/**
 * Load shifts from Supabase
 */
export async function loadShiftsFromSupabase(
  gameId: string
): Promise<Shift[]> {
  const supabase = createClient()

  try {
    const { data, error } = await supabase
      .from('stage_shifts_tracking')
      .select('*')
      .eq('game_id', gameId)
      .order('period', { ascending: true })
      .order('start_time', { ascending: false })

    if (error) {
      console.error('Error loading shifts:', error)
      return []
    }

    if (!data) return []

    // Transform Supabase format back to Shift format
    return data.map((row: any, idx: number): Shift => {
      return {
        idx,
        period: row.period || 1,
        start_time: row.start_time || '',
        end_time: row.end_time || undefined,
        start_type: row.start_type || undefined,
        stop_type: row.stop_type || undefined,
        strength: row.strength || '5v5',
        home: row.home_lineup ? JSON.parse(row.home_lineup) : undefined,
        away: row.away_lineup ? JSON.parse(row.away_lineup) : undefined
      }
    })
  } catch (error) {
    console.error('Error in loadShiftsFromSupabase:', error)
    return []
  }
}
