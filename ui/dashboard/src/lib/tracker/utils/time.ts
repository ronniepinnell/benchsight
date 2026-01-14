/**
 * Time and Period Utilities
 * Extracted from tracker_index_v23.5.html
 */

import type { Period, PeriodLengths } from '../types'

/**
 * Get the length of a specific period in minutes
 */
export function getPeriodLength(
  period: Period | string,
  periodLengths: PeriodLengths,
  defaultLength = 18
): number {
  const p = String(period).toUpperCase()
  if (p === 'OT' || p === '4') {
    return periodLengths?.OT || 5
  }
  const num = parseInt(String(period)) || 1
  return periodLengths?.[num as keyof PeriodLengths] || defaultLength
}

/**
 * Get the length of a specific period in seconds
 */
export function getPeriodLengthSeconds(
  period: Period | string,
  periodLengths: PeriodLengths,
  defaultLength = 18
): number {
  return getPeriodLength(period, periodLengths, defaultLength) * 60
}

/**
 * Format time from MM:SS string to total seconds
 */
export function timeToSeconds(time: string): number {
  const [min, sec] = (time || '').split(':').map(Number)
  return (min || 0) * 60 + (sec || 0)
}

/**
 * Format total seconds to MM:SS string
 */
export function secondsToTime(totalSeconds: number): string {
  const min = Math.floor(totalSeconds / 60)
  const sec = totalSeconds % 60
  return `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`
}

/**
 * Calculate running time (across periods) for an event
 */
export function calculateRunningTime(
  period: Period,
  time: string,
  periodLengths: PeriodLengths,
  defaultLength = 18
): number {
  // Get period length in seconds
  const periodLengthSec = getPeriodLengthSeconds(period, periodLengths, defaultLength)
  
  // Calculate elapsed time in this period
  const [min, sec] = (time || '').split(':').map(Number)
  const remainingSec = (min || 0) * 60 + (sec || 0)
  const elapsedSec = periodLengthSec - remainingSec
  
  // Sum all previous periods
  let periodOffset = 0
  const periodNum = typeof period === 'number' ? period : 4 // OT = 4
  for (let p = 1; p < periodNum; p++) {
    periodOffset += getPeriodLengthSeconds(p as Period, periodLengths, defaultLength)
  }
  
  return periodOffset + elapsedSec
}
