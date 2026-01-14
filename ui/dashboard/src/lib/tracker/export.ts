/**
 * Excel Export Functionality
 * 
 * Exports tracker data to Excel format using SheetJS
 */

import type { GameState, Event, Shift, Player, XYCoordinate } from './types'
import { getPeriodLengthSeconds } from './utils/time'

interface ExportRow {
  // Event metadata
  event_index: number
  period: number
  event_id?: string
  Type: string
  
  // Time fields
  start_time: string
  end_time: string
  start_time_seconds: number
  end_time_seconds: number
  running_time_start: number
  running_time_end: number
  duration: number
  
  // Event details
  team: string
  zone: string
  zone_change_index: number
  success?: boolean
  strength: string
  detail1?: string
  detail2?: string
  is_highlight: number
  video_url?: string // v23.7: Individual highlight video URL
  
  // Player fields (one row per player per event)
  player_game_number_?: string
  player_game_number?: string
  role_abrev?: string
  role_abrev_binary_?: string
  player_role?: string
  player_name?: string
  
  // Player-specific details
  play_detail1_?: string
  play_detail2_?: string
  play_detail_successful_?: string
  pressured_pressurer_?: string
  side_of_puck_?: string
  play_detail1?: string
  play_detail_2?: string
  play_detail_successful?: string
  pressured_pressurer?: string
  side_of_puck?: string
  
  // XY coordinates
  puck_x_1?: number
  puck_y_1?: number
  puck_x_2?: number
  puck_y_2?: number
  net_x?: number
  net_y?: number
  player_x_1?: number
  player_y_1?: number
  player_x_2?: number
  player_y_2?: number
  
  // Shift linkage
  shift_index?: number
}

interface ShiftExportRow {
  shift_index: number
  period: number
  start_time: string
  end_time: string
  start_type: string
  stop_type: string
  strength: string
  duration_seconds: number
  stoppage_time_seconds: number
  
  // Home lineup
  home_F1?: string
  home_F2?: string
  home_F3?: string
  home_D1?: string
  home_D2?: string
  home_G?: string
  home_X?: string
  
  // Away lineup
  away_F1?: string
  away_F2?: string
  away_F3?: string
  away_D1?: string
  away_D2?: string
  away_G?: string
  away_X?: string
}

/**
 * Build export rows from events (LONG format - one row per player per event)
 */
export function buildEventExportRows(
  events: Event[],
  periodLengths: { [key: number]: number } = { 1: 18, 2: 18, 3: 18, 4: 5 }
): ExportRow[] {
  const rows: ExportRow[] = []
  let zoneChangeIdx = 0
  let lastZone: string | null = null
  
  events.forEach((evt, i) => {
    const startTime = evt.start_time || evt.time || ''
    const endTime = evt.end_time || evt.start_time || evt.time || ''
    const [startMin, startSec] = (startTime || '').split(':').map(Number)
    const [endMin, endSec] = (endTime || '').split(':').map(Number)
    
    // Zone tracking
    const zoneAbbr = evt.zone || 'n'
    if (zoneAbbr !== lastZone) {
      zoneChangeIdx++
      lastZone = zoneAbbr
    }
    
    // Time calculations
    const period = evt.period || 1
    const periodLengthSec = getPeriodLengthSeconds(period, periodLengths)
    
    // Remaining time at start/end (clock counts down)
    const startRemainingSec = (startMin || 0) * 60 + (startSec || 0)
    const endRemainingSec = (endMin || startMin || 0) * 60 + (endSec || startSec || 0)
    
    // Elapsed time (time that has passed in period)
    const startTotalSec = periodLengthSec - startRemainingSec
    const endTotalSec = periodLengthSec - endRemainingSec
    
    // Running time (across all periods)
    let periodOffset = 0
    for (let p = 1; p < period; p++) {
      periodOffset += getPeriodLengthSeconds(p, periodLengths)
    }
    const eventRunningStart = periodOffset + startTotalSec
    const eventRunningEnd = periodOffset + endTotalSec
    const duration = endTotalSec - startTotalSec
    
    // Base row data
    const base: ExportRow = {
      event_index: evt.idx ?? i,
      period,
      event_id: evt.eventId || evt.event_id,
      Type: evt.type,
      start_time: startTime,
      end_time: endTime,
      start_time_seconds: startTotalSec,
      end_time_seconds: endTotalSec,
      running_time_start: eventRunningStart,
      running_time_end: eventRunningEnd,
      duration,
      team: evt.team,
      zone: zoneAbbr,
      zone_change_index: zoneChangeIdx,
      success: evt.success,
      strength: evt.strength || '5v5',
      detail1: evt.detail1,
      detail2: evt.detail2,
      is_highlight: evt.isHighlight ? 1 : 0,
      video_url: evt.isHighlight && evt.videoUrl ? evt.videoUrl : '', // v23.7: Individual highlight video URL
      shift_index: (evt as any).shiftIdx
    }
    
    // Add puck XY
    if (evt.puckXY) {
      evt.puckXY.forEach((xy, j) => {
        base[`puck_x_${j + 1}` as keyof ExportRow] = xy.x
        base[`puck_y_${j + 1}` as keyof ExportRow] = xy.y
      })
    }
    
    // Add net XY
    if (evt.netXY) {
      base.net_x = evt.netXY.x
      base.net_y = evt.netXY.y
    }
    
    // One row per player
    if (evt.players && evt.players.length > 0) {
      evt.players.forEach((player: Player) => {
        const row: ExportRow = { ...base }
        
        row.player_game_number_ = String(player.num)
        row.player_game_number = String(player.num)
        
        // Role abbreviation (e1, e2, o1, o2, etc.)
        const isOpp = player.role?.includes('opp')
        const rolePrefix = isOpp ? 'o' : 'e'
        const roleNum = player.roleNum || 1
        row.role_abrev = `${rolePrefix}${roleNum}`
        row.role_abrev_binary_ = rolePrefix
        row.player_role = player.role
        row.player_name = player.name
        
        // Player-specific details
        row.play_detail1_ = player.playD1 || ''
        row.play_detail2_ = player.playD2 || ''
        row.play_detail_successful_ = player.playSuccess || ''
        row.pressured_pressurer_ = player.pressuredBy || ''
        row.side_of_puck_ = player.sideOfPuck || ''
        
        // Duplicate fields (legacy)
        row.play_detail1 = player.playD1 || ''
        row.play_detail_2 = player.playD2 || ''
        row.play_detail_successful = player.playSuccess || ''
        row.pressured_pressurer = player.pressuredBy || ''
        row.side_of_puck = player.sideOfPuck || ''
        
        // Player XY
        if (player.xy) {
          player.xy.forEach((xy, j) => {
            row[`player_x_${j + 1}` as keyof ExportRow] = xy.x
            row[`player_y_${j + 1}` as keyof ExportRow] = xy.y
          })
        }
        
        rows.push(row)
      })
    } else {
      // Event with no players still needs a row
      base.player_game_number_ = ''
      base.role_abrev = ''
      rows.push(base)
    }
  })
  
  return rows
}

/**
 * Build shift export rows
 */
export function buildShiftExportRows(
  shifts: Shift[],
  events: Event[] = [],
  periodLengths: { [key: number]: number } = { 1: 18, 2: 18, 3: 18, 4: 5 }
): ShiftExportRow[] {
  return shifts.map((shift, i) => {
    const [startMin, startSec] = (shift.start_time || '').split(':').map(Number)
    const [endMin, endSec] = (shift.end_time || '').split(':').map(Number)
    
    const periodLengthSec = getPeriodLengthSeconds(shift.period, periodLengths)
    const startRemainingSec = (startMin || 0) * 60 + (startSec || 0)
    const endRemainingSec = (endMin || 0) * 60 + (endSec || 0)
    
    const startElapsedSec = periodLengthSec - startRemainingSec
    const endElapsedSec = periodLengthSec - endRemainingSec
    const duration = endElapsedSec - startElapsedSec
    
    // Calculate stoppage time (stoppage events within shift window)
    let stoppageTime = 0
    events
      .filter(e => e.period === shift.period)
      .filter(e => ['Stoppage', 'Clockstop', 'Timeout'].includes(e.type))
      .forEach(e => {
        const evtTime = e.start_time || e.time || ''
        const [evtMin, evtSec] = evtTime.split(':').map(Number)
        const evtRemainingSec = (evtMin || 0) * 60 + (evtSec || 0)
        const evtElapsedSec = periodLengthSec - evtRemainingSec
        
        if (evtElapsedSec >= startElapsedSec && evtElapsedSec <= endElapsedSec) {
          // TODO: Calculate actual stoppage duration if available
          stoppageTime += 0 // Placeholder
        }
      })
    
    const row: ShiftExportRow = {
      shift_index: shift.idx ?? i,
      period: shift.period,
      start_time: shift.start_time || '',
      end_time: shift.end_time || '',
      start_type: shift.start_type || '',
      stop_type: shift.stop_type || '',
      strength: shift.strength || '5v5',
      duration_seconds: duration,
      stoppage_time_seconds: stoppageTime
    }
    
    // Add lineups
    if (shift.home) {
      Object.entries(shift.home).forEach(([pos, player]) => {
        if (player) {
          row[`home_${pos}` as keyof ShiftExportRow] = String(player.num)
        }
      })
    }
    
    if (shift.away) {
      Object.entries(shift.away).forEach(([pos, player]) => {
        if (player) {
          row[`away_${pos}` as keyof ShiftExportRow] = String(player.num)
        }
      })
    }
    
    return row
  })
}

/**
 * Export game data to Excel (requires SheetJS/XLSX)
 * 
 * @param videoLinks - Optional array of video links to include in export
 */
export async function exportToExcel(
  gameId: string,
  homeTeam: string,
  awayTeam: string,
  events: Event[],
  shifts: Shift[],
  periodLengths: { [key: number]: number } = { 1: 18, 2: 18, 3: 18, 4: 5 },
  homeAttacksRightP1: boolean = true,
  videoLinks?: Array<{
    video_url: string
    video_type: string
    video_id?: string
    title?: string
    description?: string
    start_time?: string
    end_time?: string
    period?: number
    notes?: string
  }>
): Promise<void> {
  // Dynamically import XLSX
  const XLSX = await import('xlsx').catch(() => {
    throw new Error('XLSX library not installed. Run: npm install xlsx')
  }).then(m => m.default || m)
  
  // Build export data
  const eventRows = buildEventExportRows(events, periodLengths)
  const shiftRows = buildShiftExportRows(shifts, events, periodLengths)
  
  // Metadata
  const metadata = [{
    game_id: gameId,
    home_team: homeTeam,
    away_team: awayTeam,
    home_attacks_right_p1: homeAttacksRightP1 ? 1 : 0,
    export_date: new Date().toISOString(),
    total_events: events.length,
    total_shifts: shifts.length,
    total_videos: videoLinks?.length || 0
  }]
  
  // Create workbook
  const wb = XLSX.utils.book_new()
  
  // Add sheets
  const wsMeta = XLSX.utils.json_to_sheet(metadata)
  XLSX.utils.book_append_sheet(wb, wsMeta, 'metadata')
  
  if (eventRows.length > 0) {
    const wsEvents = XLSX.utils.json_to_sheet(eventRows)
    XLSX.utils.book_append_sheet(wb, wsEvents, 'events')
  }
  
  if (shiftRows.length > 0) {
    const wsShifts = XLSX.utils.json_to_sheet(shiftRows)
    XLSX.utils.book_append_sheet(wb, wsShifts, 'shifts')
  }
  
  // Add videos sheet if provided
  if (videoLinks && videoLinks.length > 0) {
    const videoRows = videoLinks.map(v => ({
      video_url: v.video_url,
      video_type: v.video_type,
      video_id: v.video_id || '',
      title: v.title || '',
      description: v.description || '',
      start_time: v.start_time || '',
      end_time: v.end_time || '',
      period: v.period || '',
      notes: v.notes || ''
    }))
    const wsVideos = XLSX.utils.json_to_sheet(videoRows)
    XLSX.utils.book_append_sheet(wb, wsVideos, 'videos')
  }
  
  // Generate filename
  const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
  const filename = `${gameId}_tracking_${timestamp}.xlsx`
  
  // Write file
  XLSX.writeFile(wb, filename)
}
