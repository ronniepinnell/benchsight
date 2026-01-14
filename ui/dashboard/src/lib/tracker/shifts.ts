/**
 * Shift Management Functions
 * Extracted from tracker_index_v23.5.html
 */

import type { Shift, Period, Lineup, Event } from './types'
import { deriveStrength } from './utils/strength'
import { timeToSeconds } from './utils/time'
import type { PeriodLengths } from './types'

export interface CreateShiftParams {
  period: Period
  startTime: string
  endTime: string
  startType?: string
  stopType?: string
  strength?: string
  home: Lineup
  away: Lineup
  events?: Event[]
}

/**
 * Calculate shift duration in seconds
 * Clock counts down, so start > end (e.g., 18:00 to 16:30)
 */
export function calculateShiftDuration(shift: Shift): number {
  const startSec = timeToSeconds(shift.start_time)
  const endSec = timeToSeconds(shift.end_time)
  
  // Clock counts down, so start > end
  // Duration = start - end (in remaining time)
  return Math.max(0, startSec - endSec)
}

/**
 * Calculate stoppage time during a shift
 */
export function calculateShiftStoppageTime(
  shift: Shift,
  events: Event[],
  period: Period
): number {
  let stoppageTime = 0
  
  // Filter events in this period and time range
  const shiftStartSec = timeToSeconds(shift.start_time)
  const shiftEndSec = timeToSeconds(shift.end_time)
  
  const periodEvents = events.filter(e => {
    if (e.period !== period) return false
    const evtTime = timeToSeconds(e.start_time)
    return evtTime >= shiftStartSec && evtTime <= shiftEndSec
  })
  
  // Check for stoppage events
  periodEvents.forEach(evt => {
    if (evt.type === 'Stoppage' || evt.type === 'Faceoff') {
      // Add estimated stoppage time (default 2 seconds for faceoff, 5 for other stoppages)
      const stoppageSec = evt.type === 'Faceoff' ? 2 : 5
      stoppageTime += stoppageSec
    }
  })
  
  return stoppageTime
}

/**
 * Create a shift object (matches logShift logic)
 */
export function createShift(params: CreateShiftParams): Omit<Shift, 'idx'> {
  const {
    period,
    startTime,
    endTime,
    startType = 'OnTheFly',
    stopType = 'OnTheFly',
    strength: providedStrength,
    home,
    away,
    events = []
  } = params

  // Auto-derive strength if not provided
  let strength = providedStrength
  if (!strength) {
    strength = deriveStrength(home, away)
  }

  const shift: Omit<Shift, 'idx'> = {
    period,
    start_time: startTime,
    end_time: endTime,
    start_type: startType,
    stop_type: stopType,
    strength,
    home: { ...home },
    away: { ...away }
  }

  // Calculate stoppage time
  const stoppageTime = calculateShiftStoppageTime(shift, events, period)
  shift.stoppageTime = stoppageTime

  // Calculate duration (clock counts down)
  const duration = calculateShiftDuration(shift)
  ;(shift as any).duration = duration

  return shift
}

/**
 * Derive shift start type from previous shift/event
 */
export function deriveShiftStartType(
  shiftIndex: number,
  previousShift: Shift | null,
  lastEvent: Event | null
): string {
  if (shiftIndex === 0) return 'GameStart'
  
  if (previousShift) {
    if (previousShift.stop_type === 'GoalScored') return 'FaceoffAfterGoal'
    if (previousShift.stop_type === 'Penalty') return 'FaceoffAfterPenalty'
    if (previousShift.stop_type === 'PeriodEnd') return 'PeriodStart'
    if (previousShift.stop_type === 'Intermission') return 'PeriodStart'
  }
  
  // Check last event
  if (lastEvent) {
    if (lastEvent.type === 'Goal') return 'FaceoffAfterGoal'
    if (lastEvent.type === 'Penalty') return 'FaceoffAfterPenalty'
    if (lastEvent.type === 'Stoppage') return 'Stoppage'
  }
  
  return 'OnTheFly'
}

/**
 * Derive shift stop type from last event
 */
export function deriveShiftStopType(lastEvent: Event | null): string {
  if (!lastEvent) return 'OnTheFly'
  
  if (lastEvent.type === 'Goal' && lastEvent.detail1 === 'Goal_Scored') {
    return 'GoalScored'
  }
  if (lastEvent.type === 'Penalty') return 'Penalty'
  if (lastEvent.type === 'Stoppage') return 'Stoppage'
  if (lastEvent.type === 'Intermission') return 'Intermission'
  
  return 'OnTheFly'
}
