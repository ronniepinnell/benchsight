/**
 * Validation Utilities
 * Extracted from tracker_index_v23.5.html
 */

import type { EventType, Zone, Player } from '../types'

/**
 * Derive success from event type and detail
 */
export function deriveSuccess(
  type: EventType | null,
  detail1: string
): 's' | 'u' | '' {
  if (!type) return ''
  
  // Auto-derive based on event type and detail
  if (type === 'Shot') {
    if (detail1.includes('OnNet') || detail1.includes('Goal')) return 's'
    if (detail1.includes('Missed') || detail1.includes('Blocked')) return 'u'
  }
  if (type === 'Pass') {
    if (detail1.includes('Completed')) return 's'
    if (detail1.includes('Missed') || detail1.includes('Intercepted')) return 'u'
  }
  if (type === 'Zone_Entry_Exit') {
    if (detail1.includes('Failed')) return 'u'
    if (detail1.includes('Entry') || detail1.includes('Exit') || detail1.includes('Keepin')) return 's'
  }
  if (type === 'Turnover') {
    if (detail1.includes('Takeaway')) return 's'
    if (detail1.includes('Giveaway')) return 'u'
  }
  if (type === 'Goal') return 's'
  if (type === 'Save') return 's'
  
  return ''
}

/**
 * Detect pressure for event players based on opponent proximity
 */
export function detectPressure(
  eventPlayers: Player[],
  opponentPlayers: Player[],
  pressureDistance: number = 10
): void {
  const threshold = pressureDistance // pixels
  
  eventPlayers.forEach(ep => {
    if (!ep.xy?.length) return
    const epPos = ep.xy[ep.xy.length - 1]
    
    let closestOpp: Player | null = null
    let closestDist = Infinity
    
    opponentPlayers.forEach(op => {
      if (!op.xy?.length) return
      const opPos = op.xy[op.xy.length - 1]
      
      const dist = Math.sqrt(
        Math.pow(epPos.x - opPos.x, 2) + 
        Math.pow(epPos.y - opPos.y, 2)
      )
      
      if (dist <= threshold && dist < closestDist) {
        closestDist = dist
        closestOpp = op
      }
    })
    
    // Auto-set pressure if closest opponent is within threshold
    if (closestOpp) {
      // Store pressure as opponent number (assuming Player has a pressure field)
      ;(ep as any).pressure = closestOpp.num
    }
  })
}
