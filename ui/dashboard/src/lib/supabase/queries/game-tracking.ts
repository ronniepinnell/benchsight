import { createClient } from '@/lib/supabase/server'

export interface GameTrackingStatus {
  game_id: number
  hasEvents: boolean
  hasShifts: boolean
  hasXY: boolean
  hasVideo: boolean
  eventCount: number
  shiftCount: number
  xyCount: number
  timeRanges: Array<{
    period: number | string
    startTime: string
    endTime: string
  }>
  status: 'full' | 'partial' | 'non-full' | 'none'
  missing: string[]
  coverage: string // e.g., "18:00 P1 - 15:35 P2"
}

/**
 * Check tracking status for a single game
 */
export async function getGameTrackingStatus(gameId: number): Promise<GameTrackingStatus> {
  const supabase = await createClient()
  
  // Check events
  const { count: eventCount } = await supabase
    .from('fact_events')
    .select('*', { count: 'exact', head: true })
    .eq('game_id', gameId)
  
  // Check shifts
  const { count: shiftCount } = await supabase
    .from('fact_shifts')
    .select('*', { count: 'exact', head: true })
    .eq('game_id', gameId)
  
  // Check XY data (try fact_shot_xy first, then fact_puck_xy_wide)
  const { count: xyCount1 } = await supabase
    .from('fact_shot_xy')
    .select('*', { count: 'exact', head: true })
    .eq('game_id', gameId)
  
  // Also check fact_puck_xy_wide if fact_shot_xy has no data
  const xyCount2 = (xyCount1 || 0) === 0 ? await supabase
    .from('fact_puck_xy_wide')
    .select('*', { count: 'exact', head: true })
    .eq('game_id', gameId)
    .then(({ count }) => count || 0)
    .catch(() => 0) : 0
  
  const xyCount = (xyCount1 || 0) + xyCount2
  
  // Check video from dim_schedule
  const { data: scheduleData } = await supabase
    .from('dim_schedule')
    .select('video_url_1, video_url_2, video_start_offset')
    .eq('game_id', gameId)
    .single()
  
  // Check video from tracker_videos table
  const { count: videoCount } = await supabase
    .from('tracker_videos')
    .select('*', { count: 'exact', head: true })
    .eq('game_id', gameId)
  
  const hasEvents = (eventCount || 0) > 0
  const hasShifts = (shiftCount || 0) > 0
  const hasXY = (xyCount || 0) > 0
  const hasVideo = !!(scheduleData?.video_url_1 || scheduleData?.video_url_2 || (videoCount || 0) > 0)
  
  // Get time ranges from events
  const { data: events } = await supabase
    .from('fact_events')
    .select('period, event_start_min, event_start_sec, event_end_min, event_end_sec')
    .eq('game_id', gameId)
    .not('event_start_min', 'is', null)
    .not('event_start_sec', 'is', null)
  
  const timeRanges: Array<{ period: number | string; startTime: string; endTime: string }> = []
  const periodMap = new Map<string, { min: string | null; max: string | null }>()
  
  if (events) {
    events.forEach(event => {
      const period = String(event.period || '1')
      const startMin = String(event.event_start_min || 0).padStart(2, '0')
      const startSec = String(event.event_start_sec || 0).padStart(2, '0')
      const startTime = `${startMin}:${startSec}`
      
      if (!periodMap.has(period)) {
        periodMap.set(period, { min: startTime, max: startTime })
      } else {
        const range = periodMap.get(period)!
        if (startTime < range.min || range.min === null) range.min = startTime
        if (startTime > range.max || range.max === null) range.max = startTime
      }
      
      // Also check end time if available
      if (event.event_end_min !== null && event.event_end_sec !== null) {
        const endMin = String(event.event_end_min).padStart(2, '0')
        const endSec = String(event.event_end_sec).padStart(2, '0')
        const endTime = `${endMin}:${endSec}`
        const range = periodMap.get(period)!
        if (endTime > range.max || range.max === null) range.max = endTime
      }
    })
    
    // Convert period map to time ranges array
    Array.from(periodMap.entries())
      .sort((a, b) => {
        // Sort periods: 1, 2, 3, 4/OT
        const aNum = a[0] === 'OT' || a[0] === '4' ? 4 : parseInt(a[0]) || 1
        const bNum = b[0] === 'OT' || b[0] === '4' ? 4 : parseInt(b[0]) || 1
        return aNum - bNum
      })
      .forEach(([period, range]) => {
        if (range.min && range.max) {
          timeRanges.push({
            period: period === 'OT' || period === '4' ? 'OT' : parseInt(period) || 1,
            startTime: range.min,
            endTime: range.max,
          })
        }
      })
  }
  
  // Build coverage string
  const coverageParts = timeRanges.map(r => {
    const periodLabel = typeof r.period === 'string' ? r.period : `P${r.period}`
    return `${r.startTime} ${periodLabel} - ${r.endTime} ${periodLabel}`
  })
  const coverage = coverageParts.join(', ')
  
  // Determine status
  const missing: string[] = []
  if (!hasEvents) missing.push('Events')
  if (!hasShifts) missing.push('Shifts')
  if (!hasXY) missing.push('XY')
  if (!hasVideo) missing.push('Video')
  
  // Check if periods are complete (start at 18:00/20:00 and have good coverage)
  // A full game should have at least 3 periods, each starting at 18:00 or 20:00
  const hasCompletePeriods = timeRanges.length >= 3 && timeRanges.slice(0, 3).every(r => {
    const start = r.startTime
    // Period should start at 18:00 or 20:00 (or 00:00 for first period)
    return start === '18:00' || start === '20:00' || start === '00:00'
  })
  
  let status: 'full' | 'partial' | 'non-full' | 'none'
  if (!hasEvents && !hasShifts) {
    status = 'none'
  } else if (missing.length === 0 && hasCompletePeriods) {
    // Full tracking: all components present and all periods complete
    status = 'full'
  } else if (missing.length > 0 && missing.length < 4) {
    // Partial tracking: some components missing
    status = 'partial'
  } else if (hasEvents || hasShifts) {
    // Has tracking but incomplete periods or missing components
    status = 'non-full'
  } else {
    status = 'none'
  }
  
  return {
    game_id: gameId,
    hasEvents,
    hasShifts,
    hasXY,
    hasVideo,
    eventCount: eventCount || 0,
    shiftCount: shiftCount || 0,
    xyCount: xyCount || 0,
    timeRanges,
    status,
    missing,
    coverage,
  }
}

/**
 * Check tracking status for multiple games (batch)
 */
export async function getGamesTrackingStatus(gameIds: number[]): Promise<Map<number, GameTrackingStatus>> {
  if (gameIds.length === 0) return new Map()
  
  const supabase = await createClient()
  const statusMap = new Map<number, GameTrackingStatus>()
  
  // Batch fetch events
  const { data: eventsData } = await supabase
    .from('fact_events')
    .select('game_id, period, event_start_min, event_start_sec, event_end_min, event_end_sec')
    .in('game_id', gameIds)
    .not('event_start_min', 'is', null)
    .not('event_start_sec', 'is', null)
  
  // Batch fetch shifts
  const { data: shiftsData } = await supabase
    .from('fact_shifts')
    .select('game_id')
    .in('game_id', gameIds)
  
  // Batch fetch XY (try both tables)
  const { data: xyData1 } = await supabase
    .from('fact_shot_xy')
    .select('game_id')
    .in('game_id', gameIds)
  
  const { data: xyData2 } = await supabase
    .from('fact_puck_xy_wide')
    .select('game_id')
    .in('game_id', gameIds)
    .then(({ data }) => ({ data }))
    .catch(() => ({ data: [] }))
  
  const xyData = [...(xyData1 || []), ...(xyData2?.data || [])]
  
  // Batch fetch schedule (for video)
  const { data: scheduleData } = await supabase
    .from('dim_schedule')
    .select('game_id, video_url_1, video_url_2')
    .in('game_id', gameIds)
  
  // Batch fetch videos
  const { data: videosData } = await supabase
    .from('tracker_videos')
    .select('game_id')
    .in('game_id', gameIds)
  
  // Process data per game
  for (const gameId of gameIds) {
    const gameEvents = eventsData?.filter(e => e.game_id === gameId) || []
    const gameShifts = shiftsData?.filter(s => s.game_id === gameId) || []
    const gameXY = xyData?.filter(x => x.game_id === gameId) || []
    const gameSchedule = scheduleData?.find(s => s.game_id === gameId)
    const gameVideos = videosData?.filter(v => v.game_id === gameId) || []
    
    const hasEvents = gameEvents.length > 0
    const hasShifts = gameShifts.length > 0
    const hasXY = gameXY.length > 0
    const hasVideo = !!(gameSchedule?.video_url_1 || gameSchedule?.video_url_2 || gameVideos.length > 0)
    
    // Build time ranges
    const periodMap = new Map<string, { min: string | null; max: string | null }>()
    gameEvents.forEach(event => {
      const period = String(event.period || '1')
      const startMin = String(event.event_start_min || 0).padStart(2, '0')
      const startSec = String(event.event_start_sec || 0).padStart(2, '0')
      const startTime = `${startMin}:${startSec}`
      
      if (!periodMap.has(period)) {
        periodMap.set(period, { min: startTime, max: startTime })
      } else {
        const range = periodMap.get(period)!
        if (startTime < range.min || range.min === null) range.min = startTime
        if (startTime > range.max || range.max === null) range.max = startTime
      }
    })
    
    const timeRanges = Array.from(periodMap.entries())
      .sort((a, b) => {
        const aNum = a[0] === 'OT' || a[0] === '4' ? 4 : parseInt(a[0]) || 1
        const bNum = b[0] === 'OT' || b[0] === '4' ? 4 : parseInt(b[0]) || 1
        return aNum - bNum
      })
      .map(([period, range]) => ({
        period: period === 'OT' || period === '4' ? 'OT' : parseInt(period) || 1,
        startTime: range.min || '00:00',
        endTime: range.max || '00:00',
      }))
    
    const coverageParts = timeRanges.map(r => {
      const periodLabel = typeof r.period === 'string' ? r.period : `P${r.period}`
      return `${r.startTime} ${periodLabel} - ${r.endTime} ${periodLabel}`
    })
    const coverage = coverageParts.join(', ')
    
    const missing: string[] = []
    if (!hasEvents) missing.push('Events')
    if (!hasShifts) missing.push('Shifts')
    if (!hasXY) missing.push('XY')
    if (!hasVideo) missing.push('Video')
    
    // Check if periods are complete
    const hasCompletePeriods = timeRanges.length >= 3 && timeRanges.slice(0, 3).every(r => {
      const start = r.startTime
      return start === '18:00' || start === '20:00' || start === '00:00'
    })
    
    let status: 'full' | 'partial' | 'non-full' | 'none'
    if (!hasEvents && !hasShifts) {
      status = 'none'
    } else if (missing.length === 0 && hasCompletePeriods) {
      status = 'full'
    } else if (missing.length > 0 && missing.length < 4) {
      status = 'partial'
    } else if (hasEvents || hasShifts) {
      status = 'non-full'
    } else {
      status = 'none'
    }
    
    statusMap.set(gameId, {
      game_id: gameId,
      hasEvents,
      hasShifts,
      hasXY,
      hasVideo,
      eventCount: gameEvents.length,
      shiftCount: gameShifts.length,
      xyCount: gameXY.length,
      timeRanges,
      status,
      missing,
      coverage,
    })
  }
  
  return statusMap
}
