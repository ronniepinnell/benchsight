/**
 * Zone Calculation Utilities
 * Extracted from tracker_index_v23.5.html
 */

import type { Zone, Team, Period, XYCoordinate } from '../types'

/**
 * Calculate zone from XY coordinate
 */
export function calculateZone(
  xy: XYCoordinate | null | undefined,
  period: Period,
  evtTeam: Team,
  homeAttacksRightP1: boolean
): Zone | '' {
  if (!xy) return ''
  
  // NHL Rink: 200 wide
  // Blue lines at x=75 and x=125
  // 0-75 = left zone, 75-125 = neutral, 125-200 = right zone
  const x = xy.x
  const isOddPeriod = period === 1 || period === 3 || period === 4 // 4 = OT
  
  // Determine which end is offensive for each team
  const homeOffensiveRight = isOddPeriod ? homeAttacksRightP1 : !homeAttacksRightP1
  
  if (evtTeam === 'home') {
    if (homeOffensiveRight) {
      if (x > 125) return 'o'      // Home offensive (right in odd periods)
      else if (x < 75) return 'd'  // Home defensive (left in odd periods)
      else return 'n'
    } else {
      if (x < 75) return 'o'       // Home offensive (left in even periods)
      else if (x > 125) return 'd' // Home defensive (right in even periods)
      else return 'n'
    }
  } else {
    // Away team is opposite
    if (homeOffensiveRight) {
      if (x < 75) return 'o'       // Away offensive (left in odd periods)
      else if (x > 125) return 'd' // Away defensive (right in odd periods)
      else return 'n'
    } else {
      if (x > 125) return 'o'      // Away offensive (right in even periods)
      else if (x < 75) return 'd'  // Away defensive (left in even periods)
      else return 'n'
    }
  }
}

/**
 * Get zone from SVG click position (0-200)
 */
export function getZoneFromClick(
  svgX: number,
  period: Period,
  evtTeam: Team,
  homeAttacksRightP1: boolean
): Zone {
  const isOddPeriod = period === 1 || period === 3 || period === 4 // 4 = OT
  const homeOffensiveRight = isOddPeriod ? homeAttacksRightP1 : !homeAttacksRightP1
  
  let rawZone = ''
  if (svgX < 75) rawZone = 'left'
  else if (svgX > 125) rawZone = 'right'
  else rawZone = 'neutral'
  
  if (rawZone === 'neutral') return 'n'
  
  // Convert to offensive/defensive based on event team
  if (evtTeam === 'home') {
    if (homeOffensiveRight) {
      return rawZone === 'right' ? 'o' : 'd'
    } else {
      return rawZone === 'left' ? 'o' : 'd'
    }
  } else {
    if (homeOffensiveRight) {
      return rawZone === 'left' ? 'o' : 'd'
    } else {
      return rawZone === 'right' ? 'o' : 'd'
    }
  }
}

/**
 * Get zone label for display
 */
export function getZoneLabel(zone: Zone | ''): string {
  const labels: Record<Zone, string> = {
    o: 'OFFENSIVE',
    d: 'DEFENSIVE',
    n: 'NEUTRAL'
  }
  return zone ? labels[zone] : ''
}
