/**
 * Event Management Functions
 * Extracted from tracker_index_v23.5.html
 */

import type { Event, EventType, Player, XYCoordinate, Zone, Team, Period } from './types'
import { deriveSuccess } from './utils/validation'
import { detectPressure } from './utils/validation'
import { calculateZone } from './utils/zone'
import { deriveStrength } from './utils/strength'

export interface CreateEventParams {
  type: EventType
  period: Period
  team: Team
  startTime: string
  endTime?: string
  detail1?: string
  detail2?: string
  zone?: Zone
  success?: 's' | 'u' | ''
  strength?: string
  players: Player[]
  puckXY?: XYCoordinate[]
  netXY?: XYCoordinate | null
  isHighlight?: boolean
  videoUrl?: string // v23.7: Individual highlight video URL
  linkedEventIdx?: number | null
  homeAttacksRightP1: boolean
  // For auto-derivation
  autoDeriveZone?: boolean
  autoDeriveSuccess?: boolean
  autoDeriveStrength?: boolean
  pressureDistance?: number
}

/**
 * Create an event object (matches logEventDirect logic)
 */
export function createEvent(params: CreateEventParams): Omit<Event, 'idx'> {
  const {
    type,
    period,
    team,
    startTime,
    endTime = startTime,
    detail1 = '',
    detail2 = '',
    zone: providedZone,
    success: providedSuccess,
    strength: providedStrength,
    players,
    puckXY = [],
    netXY = null,
    isHighlight = false,
    videoUrl,
    linkedEventIdx = null,
    homeAttacksRightP1,
    autoDeriveZone = true,
    autoDeriveSuccess = true,
    autoDeriveStrength = true,
    pressureDistance = 10
  } = params

  // Auto-derive zone if not provided
  let zone: Zone | undefined = providedZone
  if (!zone && autoDeriveZone) {
    const evtP1 = players.find(p => 
      p.role === 'event_team_player_1' || 
      p.role === 'event_player_1' ||
      (p as any).roleNum === 1
    )
    if (evtP1?.xy?.length) {
      const lastXY = evtP1.xy[evtP1.xy.length - 1]
      zone = calculateZone(lastXY, period, team, homeAttacksRightP1) || undefined
    }
  }

  // Auto-derive success if not provided
  let success: 's' | 'u' | '' = providedSuccess || ''
  if (!success && autoDeriveSuccess) {
    success = deriveSuccess(type, detail1)
  }

  // Detect pressure for event players
  const eventPlayers = players.filter(p => p.role?.startsWith('event'))
  const opponentPlayers = players.filter(p => p.role?.startsWith('opp'))
  detectPressure(eventPlayers, opponentPlayers, pressureDistance)

  // For Possession and Zone_Entry_Exit, copy player XY to puck if needed
  const isPossessionEvent = type === 'Possession' || 
    (type === 'Zone_Entry_Exit' && (detail2.includes('Rush') || detail1.includes('Entry')))
  
  let finalPuckXY = [...puckXY]
  if (isPossessionEvent && finalPuckXY.length === 0) {
    const evtPlayer1 = players.find(p => 
      p.role === 'event_team_player_1' || 
      p.role === 'event_player_1' ||
      (p as any).roleNum === 1
    )
    if (evtPlayer1?.xy?.length) {
      finalPuckXY = evtPlayer1.xy.map(xy => ({ ...xy }))
    }
  }

  // Build linked event chain
  let linkedEventChain: number[] = []
  if (linkedEventIdx !== null) {
    linkedEventChain = [linkedEventIdx]
    // In full implementation, would check if linked event has its own chain
    // const linkedEvt = events.find(e => e.idx === linkedEventIdx)
    // if (linkedEvt?.linkedEventChain?.length) {
    //   linkedEventChain = [...linkedEvt.linkedEventChain, linkedEventIdx]
    // }
  }

  const event: Omit<Event, 'idx'> = {
    period,
    start_time: startTime,
    end_time: endTime,
    team,
    type,
    detail1,
    detail2,
    zone,
    success: success || undefined,
    strength: providedStrength || (autoDeriveStrength ? '5v5' : undefined),
    linkedEventIdx: linkedEventIdx !== null ? linkedEventIdx : undefined,
    linkedEventChain: linkedEventChain.length > 0 ? linkedEventChain : undefined,
    isHighlight,
    videoUrl: isHighlight && videoUrl ? videoUrl : undefined, // v23.7: Individual highlight video URL
    puckXY: finalPuckXY,
    netXY: netXY || undefined,
    players: players.map(p => ({
      ...p,
      xy: [...(p.xy || [])]
    }))
  }

  return event
}

/**
 * Sort events by period and time, then reindex
 */
export function sortAndReindexEvents(events: Event[]): Event[] {
  const sorted = [...events].sort((a, b) => {
    if (a.period !== b.period) return a.period - b.period
    return a.start_time.localeCompare(b.start_time)
  })
  
  sorted.forEach((e, i) => {
    e.idx = i
  })
  
  return sorted
}
