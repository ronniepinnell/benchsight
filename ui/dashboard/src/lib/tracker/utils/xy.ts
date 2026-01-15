/**
 * XY Positioning Utilities
 * Extracted from tracker_index_v23.5.html
 */

import type { XYCoordinate, Zone, Team, Period, Player } from '../types'

/**
 * Calculate distance between two XY points
 */
export function calculateDistance(p1: XYCoordinate, p2: XYCoordinate): number {
  return Math.sqrt(
    Math.pow(p1.x - p2.x, 2) + 
    Math.pow(p1.y - p2.y, 2)
  )
}

/**
 * Convert SVG coordinates (0-200, 0-85) to center-relative coordinates
 * Center ice in SVG: (100, 42.5)
 * Center-relative: (0, 0) = center ice, X: -100 to +100, Y: -42.5 to +42.5
 */
export function svgToRelative(svgX: number, svgY: number): XYCoordinate {
  return {
    x: svgX - 100,  // Convert to center-relative (center ice = 0)
    y: svgY - 42.5  // Convert to center-relative (center ice = 0)
  }
}

/**
 * Convert center-relative coordinates to SVG coordinates
 * Center-relative: (0, 0) = center ice, X: -100 to +100, Y: -42.5 to +42.5
 * SVG: (100, 42.5) = center ice, X: 0-200, Y: 0-85
 */
export function relativeToSvg(relative: XYCoordinate): { x: number; y: number } {
  // Check if coordinates are already in SVG format (0-200, 0-85)
  // If x is between 0-200 and y is between 0-85, assume they're already SVG coords
  if (relative.x >= 0 && relative.x <= 200 && relative.y >= 0 && relative.y <= 85) {
    return {
      x: relative.x,
      y: relative.y
    }
  }
  
  // Otherwise, convert from center-relative to SVG
  return {
    x: relative.x + 100,
    y: relative.y + 42.5
  }
}

/**
 * Detect if click is near a faceoff dot
 * Faceoff dots at specific positions on rink
 */
export function detectFaceoffDot(
  svgX: number,
  svgY: number,
  threshold: number = 5
): { x: number; y: number; zone: Zone } | null {
  // Faceoff dot positions (approximate, adjust based on rink SVG)
  const faceoffDots = [
    { x: 25, y: 20, zone: 'o' as Zone },    // Offensive zone left
    { x: 25, y: 65, zone: 'o' as Zone },    // Offensive zone left (low)
    { x: 175, y: 20, zone: 'o' as Zone },   // Offensive zone right
    { x: 175, y: 65, zone: 'o' as Zone },   // Offensive zone right (low)
    { x: 75, y: 42.5, zone: 'n' as Zone },  // Neutral zone left
    { x: 125, y: 42.5, zone: 'n' as Zone }, // Neutral zone right
    { x: 100, y: 42.5, zone: 'n' as Zone }, // Center ice
  ]

  for (const dot of faceoffDots) {
    const dist = calculateDistance({ x: svgX, y: svgY }, dot)
    if (dist <= threshold) {
      return dot
    }
  }

  return null
}

/**
 * Smart auto-link XY based on event type
 * Auto-assigns player positions based on event patterns
 */
export function smartAutoLinkXY(
  xy: XYCoordinate,
  slot: number,
  eventType: string | null,
  players: Player[]
): void {
  if (!eventType) return

  // Shot: E1 at start (shooter position)
  if (eventType === 'Shot' && slot === 1) {
    const e1 = players.find(p => 
      p.role === 'event_team_player_1' || 
      p.role === 'event_player_1'
    )
    if (e1 && !e1.xy?.length) {
      e1.xy = [xy]
    }
  }

  // Pass: E1 at start (passer), E2 at end (receiver)
  if (eventType === 'Pass') {
    if (slot === 1) {
      const e1 = players.find(p => 
        p.role === 'event_team_player_1' || 
        p.role === 'event_player_1'
      )
      if (e1 && !e1.xy?.length) {
        e1.xy = [xy]
      }
    } else if (slot === 2) {
      const e2 = players.find(p => 
        p.role === 'event_team_player_2' || 
        p.role === 'event_player_2'
      )
      if (e2 && !e2.xy?.length) {
        e2.xy = [xy]
      }
    }
  }

  // Faceoff: E1 and O1 at faceoff dot
  if (eventType === 'Faceoff' && slot === 1) {
    const e1 = players.find(p => 
      p.role === 'event_team_player_1' || 
      p.role === 'event_player_1'
    )
    const o1 = players.find(p => 
      p.role === 'opponent_player_1' || 
      p.role === 'opp_player_1'
    )
    if (e1 && !e1.xy?.length) {
      e1.xy = [xy]
    }
    if (o1 && !o1.xy?.length) {
      o1.xy = [{ ...xy }] // Separate instance
    }
  }
}

/**
 * Handle faceoff dot click
 * Auto-assigns E1 and O1 positions
 */
export function handleFaceoffDotClick(
  dot: { x: number; y: number; zone: Zone },
  players: Player[]
): void {
  const e1 = players.find(p => 
    p.role === 'event_team_player_1' || 
    p.role === 'event_player_1'
  )
  const o1 = players.find(p => 
    p.role === 'opponent_player_1' || 
    p.role === 'opp_player_1'
  )

  const xy: XYCoordinate = { x: dot.x, y: dot.y }

  if (e1) {
    e1.xy = e1.xy || []
    if (!e1.xy.find(pos => pos.x === xy.x && pos.y === xy.y)) {
      e1.xy.push(xy)
    }
  }

  if (o1) {
    o1.xy = o1.xy || []
    if (!o1.xy.find(pos => pos.x === xy.x && pos.y === xy.y)) {
      o1.xy.push({ ...xy }) // Separate instance for opponent
    }
  }
}
