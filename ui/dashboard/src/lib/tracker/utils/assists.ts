/**
 * Auto-Assist Detection and Linking
 * 
 * Detects Pass events that should be linked to Goal events as assists
 * v23.8: Auto-detects assists when logging goals or loading games
 */

import type { Event } from '../types'
import { sortAndReindexEvents } from '../events'

/**
 * Parse time string (MM:SS) to seconds
 */
function parseTime(timeStr: string): number {
  if (!timeStr) return 0
  const [min, sec] = timeStr.split(':').map(Number)
  return (min || 0) * 60 + (sec || 0)
}

/**
 * Check if a player has an assist marker in play_detail1 or play_detail2
 */
function hasAssistMarker(player: any): boolean {
  const pd1 = (player.playD1 || '').toLowerCase()
  const pd2 = (player.playD2 || '').toLowerCase()
  return pd1.includes('assist') || pd2.includes('assist')
}

/**
 * Auto-detect and link assists for a single goal event
 * 
 * @param goalEvent - The goal event to process
 * @param allEvents - All events in the game (will be searched for recent passes)
 * @param silent - If true, don't show prompts (for batch processing)
 * @returns Result object with autoLinked count and passes needing manual review
 */
export function detectAndLinkAssists(
  goalEvent: Event,
  allEvents: Event[],
  silent: boolean = false
): { autoLinked: number; passesNeedingReview: Event[] } {
  if (!goalEvent || goalEvent.type !== 'Goal') {
    return { autoLinked: 0, passesNeedingReview: [] }
  }

  const goalTime = parseTime(goalEvent.start_time)
  const goalPeriod = goalEvent.period
  const goalTeam = goalEvent.team
  const goalIdx = goalEvent.idx ?? 0

  // Find recent Pass events (within 10 seconds before goal, same period, same team)
  const recentPasses = allEvents
    .filter(e => {
      if (e.type !== 'Pass') return false
      if (e.period !== goalPeriod) return false
      if (e.team !== goalTeam) return false
      if ((e.idx ?? 0) >= goalIdx) return false // Must be before goal

      const passTime = parseTime(e.start_time)
      const timeDiff = goalTime - passTime
      return timeDiff >= 0 && timeDiff <= 10 // Within 10 seconds
    })
    .sort((a, b) => parseTime(b.start_time) - parseTime(a.start_time)) // Most recent first

  if (recentPasses.length === 0) {
    return { autoLinked: 0, passesNeedingReview: [] }
  }

  // Separate passes that already have assist markers vs those that don't
  const passesWithAssist: Event[] = []
  const passesWithoutAssist: Event[] = []

  recentPasses.forEach(pass => {
    const hasAssist = pass.players?.some(p => hasAssistMarker(p))
    if (hasAssist) {
      passesWithAssist.push(pass)
    } else {
      passesWithoutAssist.push(pass)
    }
  })

  // Auto-link passes that already have assist markers
  // v23.8: Use assistToGoalIdx instead of linkedEventIdx for assists
  let autoLinked = 0
  if (passesWithAssist.length > 0) {
    passesWithAssist.forEach(pass => {
      // Find the pass in allEvents array and update it
      const passIdx = allEvents.findIndex(e => e === pass)
      if (passIdx >= 0) {
        const passEvent = allEvents[passIdx]
        if (passEvent.assistToGoalIdx === null || passEvent.assistToGoalIdx === undefined) {
          passEvent.assistToGoalIdx = goalIdx
          autoLinked++
        }
      }
    })
  }

  return {
    autoLinked,
    passesNeedingReview: silent ? [] : passesWithoutAssist
  }
}

/**
 * Process all goals to detect and link assists
 * Called after loading games from Supabase, Excel, or localStorage
 * 
 * @param events - All events in the game
 * @param silent - If true, don't show prompts (for batch processing)
 * @returns Total number of assists auto-linked
 */
export function processAllGoalsForAssists(
  events: Event[],
  silent: boolean = true
): number {
  if (!events || events.length === 0) return 0

  // Sort events first to ensure proper ordering
  const sortedEvents = sortAndReindexEvents([...events])
  
  const goals = sortedEvents.filter(e => e.type === 'Goal')
  if (goals.length === 0) return 0

  let totalAutoLinked = 0
  const passesNeedingReview: Array<{ goal: Event; passes: Event[] }> = []

  goals.forEach(goal => {
    const result = detectAndLinkAssists(goal, sortedEvents, silent)
    totalAutoLinked += result.autoLinked
    if (result.passesNeedingReview.length > 0) {
      passesNeedingReview.push({
        goal,
        passes: result.passesNeedingReview
      })
    }
  })

  // Return passes needing review for UI to show modal
  if (!silent && passesNeedingReview.length > 0) {
    // Store in a way that UI can access (could use a callback or event)
    // For now, we'll return the count and let the UI handle it
    return totalAutoLinked
  }

  return totalAutoLinked
}
