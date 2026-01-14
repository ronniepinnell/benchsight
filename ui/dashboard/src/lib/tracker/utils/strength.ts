/**
 * Strength Calculation Utilities
 * Extracted from tracker_index_v23.5.html
 */

import type { Lineup } from '../types'

/**
 * Derive game strength from lineups
 */
export function deriveStrength(homeLineup: Lineup, awayLineup: Lineup): string {
  // Count players on ice (excluding empty slots)
  const homeOnIce = Object.values(homeLineup).filter(Boolean).length
  const awayOnIce = Object.values(awayLineup).filter(Boolean).length
  
  // Check for goalie
  const homeHasGoalie = !!homeLineup.G
  const awayHasGoalie = !!awayLineup.G
  
  // Calculate skaters
  const homeSkaters = homeOnIce - (homeHasGoalie ? 1 : 0)
  const awaySkaters = awayOnIce - (awayHasGoalie ? 1 : 0)
  
  // Empty net situations
  if (!homeHasGoalie && homeOnIce >= 5) return 'ENA' // Empty net away (extra attacker for home)
  if (!awayHasGoalie && awayOnIce >= 5) return 'ENH' // Empty net home
  
  // Standard situations
  if (homeSkaters === 5 && awaySkaters === 5) return '5v5'
  if (homeSkaters === 5 && awaySkaters === 4) return '5v4'
  if (homeSkaters === 4 && awaySkaters === 5) return '4v5'
  if (homeSkaters === 4 && awaySkaters === 4) return '4v4'
  if (homeSkaters === 5 && awaySkaters === 3) return '5v3'
  if (homeSkaters === 3 && awaySkaters === 5) return '3v5'
  if (homeSkaters === 3 && awaySkaters === 3) return '3v3'
  
  return `${homeSkaters}v${awaySkaters}`
}
