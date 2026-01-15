'use client'

import { useState, useMemo } from 'react'
import { cn } from '@/lib/utils'
import { 
  Goal, 
  AlertCircle, 
  Clock, 
  Filter,
  ChevronDown,
  ChevronUp,
  Target,
  Shield
} from 'lucide-react'
import type { FactEvents } from '@/types/database'
import { TeamLogo } from '@/components/teams/team-logo'

interface PlayByPlayTimelineProps {
  events: FactEvents[]
  homeTeam: string
  awayTeam: string
  homeTeamId: string
  awayTeamId: string
  playersMap?: Map<string, { player_name?: string; player_full_name?: string }>
  homeTeamData?: { team_name: string; team_logo?: string | null; team_cd?: string; primary_color?: string; team_color1?: string }
  awayTeamData?: { team_name: string; team_logo?: string | null; team_cd?: string; primary_color?: string; team_color1?: string }
}

type EventFilter = 'all' | 'goals' | 'penalties' | 'highlights'

export function PlayByPlayTimeline({ 
  events, 
  homeTeam, 
  awayTeam,
  homeTeamId,
  awayTeamId,
  playersMap = new Map(),
  homeTeamData,
  awayTeamData
}: PlayByPlayTimelineProps) {
  const [filter, setFilter] = useState<EventFilter>('all')
  const [expandedPeriods, setExpandedPeriods] = useState<Set<number>>(new Set([1, 2, 3]))
  const [selectedEvent, setSelectedEvent] = useState<string | null>(null)
  const [showDebug, setShowDebug] = useState(false)
  const [debugEvent, setDebugEvent] = useState<FactEvents | null>(null)
  const [viewMode, setViewMode] = useState<'basic' | 'detailed'>('basic')
  
  // Additional filters
  const [selectedPeriod, setSelectedPeriod] = useState<number | 'all'>('all')
  const [selectedTeam, setSelectedTeam] = useState<string | 'all'>('all')
  const [selectedPlayer, setSelectedPlayer] = useState<string | 'all'>('all')
  
  // Helper function to get period as number
  const getPeriod = (event: FactEvents): number => {
    // Check multiple possible fields for period
    const eventAny = event as any
    const periodValue: number | string | null | undefined = event.period ?? eventAny.period_id ?? eventAny.period_number ?? null
    
    if (periodValue === null || periodValue === undefined) {
      // Fall through to time-based calculation
    } else if (typeof periodValue === 'number') {
      // Handle numeric period (including 0, which might be a valid period in some systems)
      if (periodValue > 0) return periodValue
      // If period is 0 or negative, try to calculate from time
    } else {
      // Handle string period
      const periodStr = String(periodValue)
      // Try to parse string period
      const parsed = parseInt(periodStr, 10)
      if (!isNaN(parsed) && parsed > 0) return parsed
      // Try to extract number from period_id format (e.g., "P3", "Period 3", "3")
      const matchResult = periodStr.match(/(\d+)/)
      if (matchResult && matchResult[1]) {
        const num = parseInt(matchResult[1], 10)
        if (!isNaN(num) && num > 0) return num
      }
    }
    
    // Fallback: Calculate period from time_start_total_seconds
    // Typical period lengths: 18 min = 1080 sec, 20 min = 1200 sec
    const timeSeconds = event.time_start_total_seconds ?? event.time_seconds ?? 0
    if (timeSeconds > 0) {
      // Try 18-minute periods first (1080 seconds) - common for youth hockey
      const period18min = Math.floor(timeSeconds / 1080) + 1
      if (period18min <= 10 && period18min > 0) {
        return period18min
      }
      // Try 20-minute periods (1200 seconds) - standard
      const period20min = Math.floor(timeSeconds / 1200) + 1
      if (period20min <= 10 && period20min > 0) {
        return period20min
      }
    }
    
    // Default to period 1 if we can't determine
    return 1
  }

  // Get unique periods, teams, and players for filter dropdowns
  const availablePeriods = useMemo(() => {
    const periods = new Set<number>()
    const periodCounts = new Map<number, number>()
    
    events.forEach(event => {
      const period = getPeriod(event)
      if (period > 0) {
        periods.add(period)
        periodCounts.set(period, (periodCounts.get(period) || 0) + 1)
      }
    })
    
    // Debug: log period distribution
    if (typeof window !== 'undefined') {
      console.log('PlayByPlayTimeline - Period distribution:', Array.from(periodCounts.entries()).sort((a, b) => a[0] - b[0]))
      console.log('PlayByPlayTimeline - Available periods:', Array.from(periods).sort((a, b) => a - b))
      console.log('PlayByPlayTimeline - Total events:', events.length)
      // Log sample of period 3 events if they exist
      const period3Events = events.filter(e => {
        const p = getPeriod(e)
        return p === 3
      })
      if (period3Events.length > 0) {
        console.log('PlayByPlayTimeline - Period 3 events found:', period3Events.length)
        console.log('PlayByPlayTimeline - Sample period 3 event:', period3Events[0])
      } else {
        console.log('PlayByPlayTimeline - No period 3 events found in data')
        // Log all unique period values from raw data
        const rawPeriods = new Set()
        events.forEach(e => {
          rawPeriods.add(e.period)
          rawPeriods.add((e as any).period_id)
        })
        console.log('PlayByPlayTimeline - Raw period values in data:', Array.from(rawPeriods))
      }
    }
    
    return Array.from(periods).sort((a, b) => a - b)
  }, [events])
  
  const availableTeams = useMemo(() => {
    const teams = new Set<string>()
    events.forEach(event => {
      if (event.player_team) teams.add(event.player_team)
    })
    return Array.from(teams).sort()
  }, [events])
  
  const availablePlayers = useMemo(() => {
    const players = new Set<string>()
    events.forEach(event => {
      if (event.event_player_1) players.add(event.event_player_1)
      if (event.event_player_2) players.add(event.event_player_2)
      if (event.player_name) players.add(event.player_name)
    })
    return Array.from(players).sort()
  }, [events])

  // Create maps for linked events - group events by linked_event_key (primary), then fallback to other keys
  const eventsByLinkedKey = useMemo(() => {
    const map = new Map<string, FactEvents[]>()
    events.forEach(event => {
      // Use linked_event_key first (primary driver), then fallback to event_chain_key, sequence_key, or play_key
      const eventAny = event as any // Type assertion to access fields that might not be in type
      const key = eventAny.linked_event_key || eventAny.event_chain_key || eventAny.sequence_key || eventAny.play_key
      if (key) {
        if (!map.has(key)) {
          map.set(key, [])
        }
        map.get(key)!.push(event)
      }
    })
    // Sort events within each linked group by time (descending - hockey time counts down)
    map.forEach((groupEvents) => {
      groupEvents.sort((a, b) => {
        const timeA = a.time_start_total_seconds || a.time_seconds || 0
        const timeB = b.time_start_total_seconds || b.time_seconds || 0
        return timeB - timeA  // Descending: higher time values first (hockey time counts down)
      })
    })
    return map
  }, [events])

  // Get player name helper
  const getPlayerName = (playerId: string | null | undefined, fallback: string = 'Unknown'): string => {
    if (!playerId) return fallback
    const player = playersMap.get(String(playerId))
    return player?.player_full_name || player?.player_name || fallback
  }

  // Parse comma-separated player IDs and return array of player names
  const getPlayerNamesFromIds = (playerIdsString: string | null | undefined): string[] => {
    if (!playerIdsString) return []
    // Split by comma, trim whitespace, filter out empty strings
    const ids = playerIdsString.split(',').map(id => id.trim()).filter(Boolean)
    return ids.map(id => getPlayerName(id)).filter(name => name !== 'Unknown')
  }

  // Get all event players (from event_player_ids)
  const getEventPlayers = (event: FactEvents): string[] => {
    return getPlayerNamesFromIds(event.event_player_ids)
  }

  // Get all opponent players (from opp_player_ids)
  const getOppPlayers = (event: FactEvents): string[] => {
    return getPlayerNamesFromIds(event.opp_player_ids)
  }

  // Calculate period start times (max time_start_total_seconds per period)
  // This handles variable period start times (e.g., period might start at 17:50 instead of 18:00)
  const periodStartTimes = useMemo(() => {
    const starts = new Map<number, number>()
    events.forEach(event => {
      const period = getPeriod(event)
      const time = event.time_start_total_seconds || event.time_seconds || 0
      const currentMax = starts.get(period) || 0
      if (time > currentMax) {
        starts.set(period, time)
      }
    })
    return starts
  }, [events])

  // Extract event_index from event_id for proper sorting
  // Event ID format: EV{game_id}{event_index:05d} (e.g., EV1896901000 = event_index 1000)
  const getEventIndex = (eventId: string): number => {
    if (!eventId || !eventId.startsWith('EV')) return 999999
    try {
      // Extract last 5 digits as event_index
      const indexStr = eventId.slice(-5)
      return parseInt(indexStr, 10)
    } catch {
      return 999999
    }
  }

  // Group events by period, sorted by period first, then event_index (to maintain chronological order)
  const eventsByPeriod = useMemo(() => {
    // First, sort all events by period, then by event_index (ascending to maintain order)
    const sortedEvents = [...events].sort((a, b) => {
      const periodA = getPeriod(a)
      const periodB = getPeriod(b)
      // Sort by period first
      if (periodA !== periodB) {
        return periodA - periodB
      }
      // If same period, sort by event_index (ascending) to maintain chronological order
      // Then by time DESCENDING (hockey time counts down: 18:00 → 0:00) as secondary sort
      const indexA = getEventIndex(a.event_id)
      const indexB = getEventIndex(b.event_id)
      if (indexA !== indexB) {
        return indexA - indexB  // Ascending: lower event_index first (earlier events)
      }
      // If same event_index, sort by time DESCENDING
      const timeA = a.time_start_total_seconds || a.time_seconds || 0
      const timeB = b.time_start_total_seconds || b.time_seconds || 0
      return timeB - timeA  // Descending: higher time values first (hockey time counts down)
    })
    
    // Then group by period
    const grouped = new Map<number, FactEvents[]>()
    sortedEvents.forEach(event => {
      const period = getPeriod(event)
      if (!grouped.has(period)) {
        grouped.set(period, [])
      }
      grouped.get(period)!.push(event)
    })

    return grouped
  }, [events])

  // Filter events based on selected filters
  const filteredEventsByPeriod = useMemo(() => {
    const filtered = new Map<number, FactEvents[]>()
    
    eventsByPeriod.forEach((periodEvents, period) => {
      let filteredEvents = periodEvents

      // Filter by period
      if (selectedPeriod !== 'all' && period !== selectedPeriod) {
        return // Skip this period
      }

      // Exclude saves
      filteredEvents = filteredEvents.filter(e => {
        const isSave = e.is_save === 1 || 
                      e.event_type?.toLowerCase().includes('save')
        return !isSave
      })

      // Exclude rebounds
      filteredEvents = filteredEvents.filter(e => {
        const isRebound = e.is_rebound === 1 ||
                         e.event_type?.toLowerCase().includes('rebound') ||
                         e.event_detail?.toLowerCase().includes('rebound') ||
                         e.play_detail1?.toLowerCase().includes('rebound') ||
                         (e as any).event_detail_2?.toLowerCase().includes('rebound')
        return !isRebound
      })

      // Exclude "bad" giveaways (misplay, pass intercepted, pass blocked, pass missed)
      filteredEvents = filteredEvents.filter(e => {
        const isGiveaway = e.event_type?.toLowerCase().includes('giveaway') || 
                          e.play_detail1?.toLowerCase().includes('giveaway')
        if (isGiveaway) {
          // Check if it's a "bad" giveaway: misplay, pass intercepted, pass blocked, pass missed
          const eventDetail = e.event_detail?.toLowerCase() || ''
          const eventDetail2 = (e as any).event_detail_2?.toLowerCase() || ''
          const playDetail1 = e.play_detail1?.toLowerCase() || ''
          const playDetail2 = e.play_detail_2?.toLowerCase() || ''
          
          const isBad = eventDetail.includes('misplay') || 
                       eventDetail.includes('pass intercepted') ||
                       eventDetail.includes('pass blocked') ||
                       eventDetail.includes('pass missed') ||
                       eventDetail2.includes('misplay') ||
                       eventDetail2.includes('pass intercepted') ||
                       eventDetail2.includes('pass blocked') ||
                       eventDetail2.includes('pass missed') ||
                       playDetail1.includes('misplay') ||
                       playDetail1.includes('pass intercepted') ||
                       playDetail1.includes('pass blocked') ||
                       playDetail1.includes('pass missed') ||
                       playDetail2.includes('misplay') ||
                       playDetail2.includes('pass intercepted') ||
                       playDetail2.includes('pass blocked') ||
                       playDetail2.includes('pass missed')
          
          // Exclude if it's a bad giveaway
          return !isBad
        }
        return true
      })

      // Basic view: only show important events (game state, faceoffs, shots, goals, penalties, takeaways, giveaways, zone entries/exits)
      if (viewMode === 'basic') {
        filteredEvents = filteredEvents.filter(e => {
          const eventType = e.event_type?.toLowerCase() || ''
          const eventDetail = e.event_detail?.toLowerCase() || ''
          const playDetail = e.play_detail1?.toLowerCase() || ''
          
          // Game state events (always show)
          const isGameState = 
            eventType.includes('game start') || eventType.includes('gamestart') ||
            eventType.includes('intermission') ||
            eventType.includes('period start') || eventType.includes('periodstart') ||
            eventType.includes('period end') || eventType.includes('periodend') ||
            eventType.includes('game end') || eventType.includes('gameend') ||
            eventDetail.includes('game start') || eventDetail.includes('gamestart') ||
            eventDetail.includes('intermission') ||
            eventDetail.includes('period start') || eventDetail.includes('periodstart') ||
            eventDetail.includes('period end') || eventDetail.includes('periodend') ||
            eventDetail.includes('game end') || eventDetail.includes('gameend') ||
            playDetail.includes('game start') || playDetail.includes('gamestart') ||
            playDetail.includes('intermission') ||
            playDetail.includes('period start') || playDetail.includes('periodstart') ||
            playDetail.includes('period end') || playDetail.includes('periodend') ||
            playDetail.includes('game end') || playDetail.includes('gameend')
          
          // Goals
          const isGoal = e.is_goal === 1 || eventType === 'goal'
          
          // Shots
          const isShot = eventType.includes('shot') || playDetail.includes('shot')
          
          // Faceoffs
          const isFaceoff = eventType.includes('faceoff')
          
          // Penalties
          const isPenalty = eventType.includes('penalty') || playDetail.includes('penalty')
          
          // Takeaways
          const isTakeaway = eventType.includes('takeaway') || playDetail.includes('takeaway')
          
          // Giveaways (non-bad ones are already filtered out)
          const isGiveaway = eventType.includes('giveaway') || playDetail.includes('giveaway')
          
          // Zone entries/exits
          const isZone = eventType.includes('zone')
          
          return isGameState || isGoal || isShot || isFaceoff || isPenalty || isTakeaway || isGiveaway || isZone
        })
      }

      // Filter by event type
      if (filter === 'goals') {
        filteredEvents = filteredEvents.filter(e => e.is_goal === 1 || e.event_type === 'Goal')
      } else if (filter === 'penalties') {
        filteredEvents = filteredEvents.filter(e => 
          e.event_type?.toLowerCase().includes('penalty') || 
          e.play_detail1?.toLowerCase().includes('penalty')
        )
      } else if (filter === 'highlights') {
        filteredEvents = filteredEvents.filter(e => 
          e.is_highlight === 1 || 
          e.is_goal === 1
        )
      }

      // Filter by team
      if (selectedTeam !== 'all') {
        filteredEvents = filteredEvents.filter(e => 
          e.player_team === selectedTeam
        )
      }

      // Filter by player
      if (selectedPlayer !== 'all') {
        filteredEvents = filteredEvents.filter(e => 
          e.event_player_1 === selectedPlayer ||
          e.event_player_2 === selectedPlayer ||
          e.player_name === selectedPlayer
        )
      }

      if (filteredEvents.length > 0) {
        filtered.set(period, filteredEvents)
      }
    })

    return filtered
  }, [eventsByPeriod, filter, selectedPeriod, selectedTeam, selectedPlayer, viewMode])

  const formatTime = (event: FactEvents): string => {
    const period = getPeriod(event)
    const periodStartTime = periodStartTimes.get(period) || 0
    
    // Expected period start: 18:00 = 1080 seconds (for 18-minute periods)
    const expectedPeriodStart = 1080
    
    // If we have event_start_min and event_start_sec, use them but adjust if needed
    if (
      typeof event.event_start_min === 'number' && 
      typeof event.event_start_sec === 'number' &&
      !isNaN(event.event_start_min) &&
      !isNaN(event.event_start_sec)
    ) {
      // If the period actually started at 18:00 but database shows lower values,
      // calculate the offset and adjust
      if (periodStartTime > 0 && periodStartTime < expectedPeriodStart) {
        // Offset = difference between expected start (18:00) and actual max time in data
        const offset = expectedPeriodStart - periodStartTime
        // Adjust: add offset to get correct time
        const currentSeconds = event.event_start_min * 60 + event.event_start_sec
        const adjustedSeconds = currentSeconds + offset
        const minutes = Math.floor(adjustedSeconds / 60)
        const secs = adjustedSeconds % 60
        return `${minutes}:${secs.toString().padStart(2, '0')}`
      }
      // If period start is correct (>= 1080), use values directly
      return `${event.event_start_min}:${event.event_start_sec.toString().padStart(2, '0')}`
    }
    
    // FALLBACK: Calculate from time_start_total_seconds
    const timeSeconds = event.time_start_total_seconds ?? event.time_seconds ?? 0
    
    // Adjust if period should start at 18:00 but max time is less
    if (periodStartTime > 0 && periodStartTime < expectedPeriodStart) {
      const offset = expectedPeriodStart - periodStartTime
      const adjustedSeconds = timeSeconds + offset
      const minutes = Math.floor(adjustedSeconds / 60)
      const secs = adjustedSeconds % 60
      return `${minutes}:${secs.toString().padStart(2, '0')}`
    }
    
    // Otherwise use modulo 1200 (for 20-min periods) or direct value
    const periodSeconds = timeSeconds % 1200
    const minutes = Math.floor(periodSeconds / 60)
    const secs = Math.floor(periodSeconds % 60)
    return `${minutes}:${secs.toString().padStart(2, '0')}`
  }

  const formatEndTime = (event: FactEvents): string | null => {
    const period = getPeriod(event)
    const periodStartTime = periodStartTimes.get(period) || 0
    const expectedPeriodStart = 1080
    
    // If we have event_end_min and event_end_sec, use them but adjust if needed
    if (
      typeof event.event_end_min === 'number' && 
      typeof event.event_end_sec === 'number' &&
      !isNaN(event.event_end_min) &&
      !isNaN(event.event_end_sec)
    ) {
      if (periodStartTime > 0 && periodStartTime < expectedPeriodStart) {
        const offset = expectedPeriodStart - periodStartTime
        const currentSeconds = event.event_end_min * 60 + event.event_end_sec
        const adjustedSeconds = currentSeconds + offset
        const minutes = Math.floor(adjustedSeconds / 60)
        const secs = adjustedSeconds % 60
        return `${minutes}:${secs.toString().padStart(2, '0')}`
      }
      return `${event.event_end_min}:${event.event_end_sec.toString().padStart(2, '0')}`
    }
    
    // FALLBACK: Calculate from time_end_total_seconds
    const timeEndSeconds = (event as any).time_end_total_seconds
    if (timeEndSeconds) {
      if (periodStartTime > 0 && periodStartTime < expectedPeriodStart) {
        const offset = expectedPeriodStart - periodStartTime
        const adjustedSeconds = timeEndSeconds + offset
        const minutes = Math.floor(adjustedSeconds / 60)
        const secs = adjustedSeconds % 60
        return `${minutes}:${secs.toString().padStart(2, '0')}`
      }
      const periodSeconds = timeEndSeconds % 1200
      const minutes = Math.floor(periodSeconds / 60)
      const secs = Math.floor(periodSeconds % 60)
      return `${minutes}:${secs.toString().padStart(2, '0')}`
    }
    
    return null
  }

  const getEventIcon = (event: FactEvents) => {
    if (event.is_goal === 1 || event.event_type === 'Goal') {
      return <Goal className="w-4 h-4 text-goal" />
    }
    if (event.is_save === 1 || event.event_type === 'Save') {
      return <Shield className="w-4 h-4 text-primary" />
    }
    if (event.event_type?.toLowerCase().includes('shot')) {
      return <Target className="w-4 h-4 text-muted-foreground" />
    }
    if (event.event_type?.toLowerCase().includes('penalty')) {
      return <AlertCircle className="w-4 h-4 text-destructive" />
    }
    return <Clock className="w-4 h-4 text-muted-foreground" />
  }

  const getEventColor = (event: FactEvents): string => {
    const teamId = event.team_id || event.event_team_id || ''
    const isHome = teamId === homeTeamId || event.team_venue === 'Home'
    
    if (event.is_goal === 1) {
      return 'bg-goal/20 border-goal/50'
    }
    if (event.is_save === 1) {
      return 'bg-primary/20 border-primary/50'
    }
    if (event.event_type?.toLowerCase().includes('penalty')) {
      return 'bg-destructive/20 border-destructive/50'
    }
    return 'bg-accent border-border'
  }

  const getEventDescription = (event: FactEvents, linkedEvents?: FactEvents[]): string => {
    // Check for events that don't need players/teams (deadice, stoppage)
    const eventTypeLower = event.event_type?.toLowerCase() || ''
    const eventDetailLower = event.event_detail?.toLowerCase() || ''
    const playDetailLower = event.play_detail1?.toLowerCase() || ''
    
    const isDeadIceOrStoppage = 
      eventTypeLower.includes('deadice') || 
      eventTypeLower.includes('dead ice') ||
      eventTypeLower.includes('stoppage') ||
      eventDetailLower.includes('deadice') ||
      eventDetailLower.includes('dead ice') ||
      eventDetailLower.includes('stoppage') ||
      playDetailLower.includes('deadice') ||
      playDetailLower.includes('dead ice') ||
      playDetailLower.includes('stoppage')
    
    if (isDeadIceOrStoppage) {
      // Return just the event type/detail without player names
      return event.event_type?.replace(/_/g, ' ') || event.event_detail || event.play_detail1 || 'Stoppage'
    }
    
    // Get players from event_player_ids (primary), fallback to event_player_1, then player_name
    const eventPlayers = getEventPlayers(event)
    const playerName = eventPlayers.length > 0 
      ? eventPlayers[0]  // First player from event_player_ids
      : event.event_player_1 || event.player_name || 'Unknown'
    
    // Get opponent players if available
    const oppPlayers = getOppPlayers(event)
    
    // Handle goals
    if (event.is_goal === 1 || event.event_type === 'Goal') {
      // Get assists from event_player_ids (players after the first one)
      const assists = eventPlayers.length > 1 ? eventPlayers.slice(1) : []
      // Fallback to event_player_2 if event_player_ids not available
      if (assists.length === 0 && event.event_player_2) {
        assists.push(event.event_player_2)
      }
      const assistText = assists.length > 0 
        ? ` (Assist${assists.length > 1 ? 's' : ''}: ${assists.join(', ')})`
        : ''
      return `${playerName} - Goal${assistText}`
    }
    
    // Handle shots with saves
    if (event.event_type?.toLowerCase().includes('shot') || 
        event.play_detail1?.toLowerCase().includes('shot')) {
      // Use opp_player_ids for the goalie who saved it
      const goalieName = oppPlayers.length > 0 
        ? oppPlayers[0]  // First player from opp_player_ids is the goalie
        : null
      
      if (goalieName) {
        return `Shot by ${playerName} saved by ${goalieName}`
      }
      return `Shot by ${playerName}`
    }
    
    // Handle saves (with linked shot)
    if (event.is_save === 1 || event.event_type === 'Save') {
      // Look for linked shot event
      if (linkedEvents) {
        const shotEvent = linkedEvents.find(e => 
          e.event_type?.toLowerCase().includes('shot') || 
          e.play_detail1?.toLowerCase().includes('shot')
        )
        if (shotEvent) {
          const shotEventPlayers = getEventPlayers(shotEvent)
          const shotPlayerName = shotEventPlayers.length > 0
            ? shotEventPlayers[0]
            : shotEvent.event_player_1 || shotEvent.player_name || 'Unknown'
          return `Save by ${playerName} (shot by ${shotPlayerName})`
        }
      }
      return `Save by ${playerName}`
    }
    
    // Handle turnovers (especially intercepted passes)
    if (event.event_type?.toLowerCase().includes('turnover') || 
        event.play_detail1?.toLowerCase().includes('turnover') ||
        event.play_detail1?.toLowerCase().includes('intercept') ||
        event.play_detail_2?.toLowerCase().includes('intercept')) {
      // Use only event_detail_2 for turnover description (not event_type)
      const detail2 = (event as any).event_detail_2 || event.play_detail_2 || ''
      
      if (event.play_detail1?.toLowerCase().includes('intercept') || 
          event.play_detail_2?.toLowerCase().includes('intercept') ||
          event.event_detail?.toLowerCase().includes('intercept')) {
        return detail2 ? `Pass Intercepted - ${detail2} by ${playerName}` : `Pass Intercepted - Turnover by ${playerName}`
      }
      return detail2 ? `${detail2} by ${playerName}` : `Turnover by ${playerName}`
    }
    
    // Handle passes
    if (event.event_type?.toLowerCase().includes('pass')) {
      const isSuccessful = event.event_successful === true || 
                          (event as any).play_detail_successful?.toLowerCase() === 'successful' ||
                          (event as any).play_detail_successful === 's'
      // Show recipient if available (second player in event_player_ids)
      const recipient = eventPlayers.length > 1 ? eventPlayers[1] : null
      const recipientText = recipient ? ` to ${recipient}` : ''
      return `${isSuccessful ? 'Pass' : 'Pass Missed'} by ${playerName}${recipientText}`
    }
    
    // Handle takeaways
    if (event.event_type?.toLowerCase().includes('takeaway') || 
        event.play_detail1?.toLowerCase().includes('takeaway')) {
      return `Takeaway by ${playerName}`
    }
    
    // Handle giveaways
    if (event.event_type?.toLowerCase().includes('giveaway') || 
        event.play_detail1?.toLowerCase().includes('giveaway')) {
      return `Giveaway by ${playerName}`
    }
    
    // Handle penalties
    if (event.event_type?.toLowerCase().includes('penalty')) {
      return `${playerName} - ${event.play_detail1 || event.event_type}`
    }
    
    // Handle faceoffs
    if (event.event_type?.toLowerCase().includes('faceoff')) {
      // Faceoff won by first player from event_player_ids against first player from opp_player_ids
      const opponentName = oppPlayers.length > 0 
        ? oppPlayers[0]  // First player from opp_player_ids
        : 'Unknown'
      return `Faceoff won by ${playerName} against ${opponentName}`
    }
    
    // Handle zone entries/exits
    if (event.event_type?.toLowerCase().includes('zone')) {
      // Use only event_detail_2 for zone entry/exit description (not event_type)
      const detail2 = (event as any).event_detail_2 || event.play_detail_2 || ''
      return detail2 ? `${detail2} - ${playerName}` : `${event.event_type.replace(/_/g, ' ')} - ${playerName}`
    }
    
    // Default description - use event_type and event_detail if available
    if (event.event_type) {
      const detail = event.event_detail && event.event_detail !== event.event_type 
        ? ` (${event.event_detail})` 
        : event.play_detail1 
        ? ` (${event.play_detail1})` 
        : ''
      return `${event.event_type.replace(/_/g, ' ')}${detail}${playerName !== 'Unknown' ? ` - ${playerName}` : ''}`
    }
    
    return event.play_detail1 || event.event_detail || 'Event'
  }

  const togglePeriod = (period: number) => {
    const newExpanded = new Set(expandedPeriods)
    if (newExpanded.has(period)) {
      newExpanded.delete(period)
    } else {
      newExpanded.add(period)
    }
    setExpandedPeriods(newExpanded)
  }

  const periods = Array.from(filteredEventsByPeriod.keys()).sort((a, b) => a - b)

  if (events.length === 0) {
    return (
      <div className="bg-card rounded-xl border border-border p-8 text-center">
        <Clock className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
        <p className="text-muted-foreground">No events available for this game</p>
      </div>
    )
  }

  return (
    <div className="bg-card rounded-xl border border-border overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 bg-accent border-b border-border">
        <div className="flex items-center justify-between">
          <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
            <Clock className="w-4 h-4" />
            Play-by-Play Timeline
          </h2>
          
          {/* Filters and Debug Toggle */}
          <div className="flex items-center gap-2 flex-wrap">
            <button
              onClick={() => setShowDebug(!showDebug)}
              className="text-xs text-muted-foreground hover:text-foreground px-2 py-1 rounded border border-border bg-background"
              title="Toggle debug view"
            >
              {showDebug ? 'Hide' : 'Show'} Debug
            </button>
            <button
              onClick={() => setViewMode(viewMode === 'basic' ? 'detailed' : 'basic')}
              className={cn(
                "text-xs px-2 py-1 rounded border border-border transition-colors",
                viewMode === 'basic' 
                  ? "bg-primary text-primary-foreground border-primary" 
                  : "bg-background text-muted-foreground hover:text-foreground"
              )}
              title="Toggle between basic and detailed view"
            >
              {viewMode === 'basic' ? 'Basic' : 'Detailed'}
            </button>
            <Filter className="w-4 h-4 text-muted-foreground" />
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value as EventFilter)}
              className="bg-background border border-border rounded-md px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="all">All Events</option>
              <option value="goals">Goals</option>
              <option value="penalties">Penalties</option>
              <option value="highlights">Highlights</option>
            </select>
            <select
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(e.target.value === 'all' ? 'all' : Number(e.target.value))}
              className="bg-background border border-border rounded-md px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="all">All Periods</option>
              {availablePeriods.map(period => (
                <option key={period} value={period}>
                  {period > 3 ? `OT${period - 3}` : `Period ${period}`}
                </option>
              ))}
            </select>
            <select
              value={selectedTeam}
              onChange={(e) => setSelectedTeam(e.target.value)}
              className="bg-background border border-border rounded-md px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="all">All Teams</option>
              {availableTeams.map(team => (
                <option key={team} value={team}>{team}</option>
              ))}
            </select>
            <select
              value={selectedPlayer}
              onChange={(e) => setSelectedPlayer(e.target.value)}
              className="bg-background border border-border rounded-md px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary min-w-[120px]"
            >
              <option value="all">All Players</option>
              {availablePlayers.map(player => (
                <option key={player} value={player}>{player}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Debug Panel */}
      {showDebug && (
        <div className="px-6 py-4 bg-muted border-b border-border max-h-96 overflow-y-auto">
          <div className="text-xs font-mono space-y-3">
            {/* Period Start Times Summary */}
            <div>
              <div className="font-semibold mb-2">Period Start Times (Max time_start_total_seconds per period):</div>
              {Array.from(periodStartTimes.entries()).map(([period, maxTime]) => (
                <div key={period}>
                  Period {period}: {maxTime} seconds = {Math.floor(maxTime / 60)}:{String(maxTime % 60).padStart(2, '0')}
                </div>
              ))}
            </div>

            {/* Selected Event Details */}
            {debugEvent && (
              <div className="pt-2 border-t border-border">
                <div className="font-semibold mb-2">Selected Event Data:</div>
                <div><strong>event_id:</strong> {debugEvent.event_id}</div>
                <div><strong>period:</strong> {debugEvent.period}</div>
                <div><strong>event_start_min:</strong> {debugEvent.event_start_min}</div>
                <div><strong>event_start_sec:</strong> {debugEvent.event_start_sec}</div>
                <div><strong>time_start_total_seconds:</strong> {debugEvent.time_start_total_seconds}</div>
                <div><strong>time_seconds:</strong> {debugEvent.time_seconds || 'N/A'}</div>
                <div><strong>periodStartTime (max):</strong> {periodStartTimes.get(getPeriod(debugEvent)) || 'N/A'}</div>
                <div><strong>formatted_time:</strong> {formatTime(debugEvent)}</div>
                <div><strong>event_type:</strong> {debugEvent.event_type}</div>
                <div className="mt-2 pt-2 border-t border-border">
                  <strong>Raw JSON:</strong>
                  <pre className="mt-1 text-[10px] overflow-auto max-h-40 bg-background p-2 rounded">
                    {JSON.stringify(debugEvent, null, 2)}
                  </pre>
                </div>
              </div>
            )}

            {/* First 5 Events Summary */}
            <div className="pt-2 border-t border-border">
              <div className="font-semibold mb-2">First 5 Events (by period):</div>
              <div className="space-y-1 text-[10px]">
                {events.slice(0, 5).map((event, idx) => (
                  <div key={event.event_id || idx} className="flex gap-4">
                    <span>P{getPeriod(event)}</span>
                    <span>min:{event.event_start_min} sec:{event.event_start_sec}</span>
                    <span>total_sec:{event.time_start_total_seconds}</span>
                    <span>→ {formatTime(event)}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Timeline */}
      <div className="p-6 space-y-4 max-h-[600px] overflow-y-auto">
        {periods.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            No events match the selected filter
          </div>
        ) : (
          periods.map((period) => {
            const periodEvents = filteredEventsByPeriod.get(period) || []
            const isExpanded = expandedPeriods.has(period)
            const periodLabel = period > 3 ? `OT${period - 3}` : `Period ${period}`

            return (
              <div key={period} className="border border-border rounded-lg overflow-hidden">
                {/* Period Header */}
                <button
                  onClick={() => togglePeriod(period)}
                  className="w-full px-4 py-3 bg-accent/50 hover:bg-accent transition-colors flex items-center justify-between"
                >
                  <div className="flex items-center gap-3">
                    {isExpanded ? (
                      <ChevronUp className="w-4 h-4 text-muted-foreground" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-muted-foreground" />
                    )}
                    <span className="font-display text-sm font-semibold">{periodLabel}</span>
                    <span className="text-xs text-muted-foreground">
                      ({periodEvents.length} events)
                    </span>
                  </div>
                </button>

                {/* Period Events */}
                {isExpanded && (
                  <div className="divide-y divide-border">
                    {periodEvents.map((event, idx) => {
                      const eventKey = event.event_id || `${period}-${idx}`
                      const isSelected = selectedEvent === eventKey
                      const time = formatTime(event)
                      
                      // Use player_team to determine which team this event belongs to
                      let playerTeamName = event.player_team || ''
                      
                      // For faceoffs, try to get team from first player in event_player_ids if player_team is missing
                      if (!playerTeamName && event.event_type?.toLowerCase().includes('faceoff')) {
                        const eventPlayers = getEventPlayers(event)
                        if (eventPlayers.length > 0) {
                          // Get first player ID and look up their team
                          const playerIds = event.event_player_ids?.split(',').map(id => id.trim()).filter(Boolean) || []
                          if (playerIds.length > 0) {
                            const firstPlayerId = playerIds[0]
                            const firstPlayer = playersMap.get(firstPlayerId)
                            if (firstPlayer && (firstPlayer as any).team_name) {
                              playerTeamName = (firstPlayer as any).team_name
                            }
                          }
                        }
                      }
                      
                      // Match player_team to home or away team
                      const homeTeamName = homeTeamData?.team_name || homeTeam
                      const awayTeamName = awayTeamData?.team_name || awayTeam
                      
                      const isHomeTeam = playerTeamName === homeTeamName || 
                                        playerTeamName === homeTeam ||
                                        event.team_venue === 'Home' ||
                                        (event.team_id || event.event_team_id) === homeTeamId
                      
                      // Get team data for logo - use player_team to match
                      let teamData = null
                      let teamName = playerTeamName || 'Unknown'
                      
                      if (playerTeamName === homeTeamName || playerTeamName === homeTeam) {
                        teamData = homeTeamData
                        teamName = playerTeamName || homeTeamName
                      } else if (playerTeamName === awayTeamName || playerTeamName === awayTeam) {
                        teamData = awayTeamData
                        teamName = playerTeamName || awayTeamName
                      } else if (isHomeTeam) {
                        teamData = homeTeamData
                        teamName = homeTeamName
                      } else {
                        teamData = awayTeamData
                        teamName = awayTeamName
                      }
                      
                      // For faceoffs, ensure we show the team of the winning player
                      if (event.event_type?.toLowerCase().includes('faceoff') && !teamData) {
                        // Try to match by team_id or event_team_id
                        const teamId = event.team_id || (event as any).event_team_id
                        if (teamId) {
                          if (String(teamId) === String(homeTeamId)) {
                            teamData = homeTeamData
                            teamName = homeTeamName
                          } else if (String(teamId) === String(awayTeamId)) {
                            teamData = awayTeamData
                            teamName = awayTeamName
                          }
                        }
                      }
                      
                      // Check if this event type should not show team information
                      const eventTypeLower = event.event_type?.toLowerCase() || ''
                      const eventDetailLower = event.event_detail?.toLowerCase() || ''
                      const playDetailLower = event.play_detail1?.toLowerCase() || ''
                      
                      // Game state events that don't need teams: game start, intermission, period start/end, game end
                      // Faceoffs DO need teams, so they're not included here
                      const isGameStateEvent = 
                        eventTypeLower.includes('game start') ||
                        eventTypeLower.includes('gamestart') ||
                        eventTypeLower.includes('intermission') ||
                        eventTypeLower.includes('period start') ||
                        eventTypeLower.includes('periodstart') ||
                        eventTypeLower.includes('period end') ||
                        eventTypeLower.includes('periodend') ||
                        eventTypeLower.includes('game end') ||
                        eventTypeLower.includes('gameend') ||
                        eventDetailLower.includes('game start') ||
                        eventDetailLower.includes('gamestart') ||
                        eventDetailLower.includes('intermission') ||
                        eventDetailLower.includes('period start') ||
                        eventDetailLower.includes('periodstart') ||
                        eventDetailLower.includes('period end') ||
                        eventDetailLower.includes('periodend') ||
                        eventDetailLower.includes('game end') ||
                        eventDetailLower.includes('gameend') ||
                        playDetailLower.includes('game start') ||
                        playDetailLower.includes('gamestart') ||
                        playDetailLower.includes('intermission') ||
                        playDetailLower.includes('period start') ||
                        playDetailLower.includes('periodstart') ||
                        playDetailLower.includes('period end') ||
                        playDetailLower.includes('periodend') ||
                        playDetailLower.includes('game end') ||
                        playDetailLower.includes('gameend')
                      
                      // Get linked events for this event
                      const eventAny = event as any // Type assertion to access fields that might not be in type
                      // Use linked_event_key first (primary driver), then fallback to other keys
                      const linkedKey = eventAny.linked_event_key || eventAny.event_chain_key || eventAny.sequence_key || eventAny.play_key
                      const linkedEvents = linkedKey ? eventsByLinkedKey.get(linkedKey) : undefined

                      return (
                        <div
                          key={eventKey}
                          onClick={() => {
                            setSelectedEvent(isSelected ? null : eventKey)
                            setDebugEvent(event)
                          }}
                          className={cn(
                            'px-4 py-3 transition-colors cursor-pointer',
                            getEventColor(event),
                            isSelected && 'ring-2 ring-primary'
                          )}
                        >
                          <div className="flex items-start gap-3">
                            {/* Time */}
                            <div className="flex-shrink-0 w-20 text-xs font-mono text-muted-foreground">
                              {(() => {
                                const endTime = formatEndTime(event)
                                return endTime ? (
                                  <div>
                                    <div>{time}</div>
                                    <div className="text-[10px] opacity-70">→ {endTime}</div>
                                  </div>
                                ) : (
                                  <div>{time}</div>
                                )
                              })()}
                            </div>

                            {/* Icon */}
                            <div className="flex-shrink-0 mt-0.5">
                              {getEventIcon(event)}
                            </div>

                            {/* Event Details */}
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-1">
                                {/* Team Logo - only show if not a game state event */}
                                {!isGameStateEvent && teamData && (
                                  <TeamLogo
                                    src={teamData.team_logo || null}
                                    name={teamData.team_name || teamName}
                                    abbrev={teamData.team_cd}
                                    size="sm"
                                    showGradient={false}
                                  />
                                )}
                                {/* Team Name - only show if not a game state event */}
                                {!isGameStateEvent && (
                                  <span 
                                    className="text-xs font-semibold"
                                    style={(teamData as any)?.primary_color || (teamData as any)?.team_color1 ? {
                                      color: (teamData as any).primary_color || (teamData as any).team_color1
                                    } : {
                                      color: 'inherit' // Use default foreground color if no team color
                                    }}
                                  >
                                    {teamName}
                                  </span>
                                )}
                                <span className="text-xs text-foreground">
                                  {getEventDescription(event, linkedEvents)}
                                </span>
                              </div>
                              
                              {/* Additional Details - Expanded View */}
                              {isSelected && (
                                <div className="mt-2 pt-2 border-t border-border/50 text-xs text-muted-foreground space-y-2">
                                  {/* Basic Info */}
                                  <div className="grid grid-cols-2 gap-2">
                                    <div><strong>Event ID:</strong> {event.event_id}</div>
                                    <div><strong>Period:</strong> {getPeriod(event)}</div>
                                    <div><strong>Event Type:</strong> {event.event_type}</div>
                                    <div><strong>Event Type ID:</strong> {event.event_type_id}</div>
                                  </div>

                                  {/* Time Info */}
                                  <div className="pt-2 border-t border-border/30">
                                    <div className="font-semibold mb-1">Time Information:</div>
                                    <div className="grid grid-cols-2 gap-2">
                                      <div>Start: {event.event_start_min}:{String(event.event_start_sec).padStart(2, '0')}</div>
                                      <div>Total Seconds: {event.time_start_total_seconds}</div>
                                      {event.event_end_min !== undefined && (
                                        <div>End: {event.event_end_min}:{String(event.event_end_sec || 0).padStart(2, '0')}</div>
                                      )}
                                      {event.duration && <div>Duration: {event.duration}s</div>}
                                    </div>
                                  </div>

                                  {/* Player Info */}
                                  <div className="pt-2 border-t border-border/30">
                                    <div className="font-semibold mb-1">Player Information:</div>
                                    <div className="space-y-1">
                                      {event.event_player_1 && <div><strong>Player 1:</strong> {event.event_player_1}</div>}
                                      {event.event_player_2 && <div><strong>Player 2:</strong> {event.event_player_2}</div>}
                                      {event.player_name && <div><strong>Player Name:</strong> {event.player_name}</div>}
                                      {event.event_player_ids && (
                                        <div>
                                          <strong>Player IDs:</strong> {event.event_player_ids}
                                          <div className="text-xs mt-1">
                                            Players: {getEventPlayers(event).join(', ') || 'None found'}
                                          </div>
                                        </div>
                                      )}
                                      {event.opp_player_ids && (
                                        <div>
                                          <strong>Opp Player IDs:</strong> {event.opp_player_ids}
                                          <div className="text-xs mt-1">
                                            Opponents: {getOppPlayers(event).join(', ') || 'None found'}
                                          </div>
                                        </div>
                                      )}
                                      {event.player_role && <div><strong>Player Role:</strong> {event.player_role}</div>}
                                      {event.player_team && <div><strong>Player Team:</strong> {event.player_team}</div>}
                                    </div>
                                  </div>

                                  {/* Event Details */}
                                  <div className="pt-2 border-t border-border/30">
                                    <div className="font-semibold mb-1">Event Details:</div>
                                    <div className="space-y-1">
                                      {event.event_detail && <div><strong>Event Detail:</strong> {event.event_detail}</div>}
                                      {event.event_detail_id && <div><strong>Event Detail ID:</strong> {event.event_detail_id}</div>}
                                      {event.play_detail1 && <div><strong>Play Detail 1:</strong> {event.play_detail1}</div>}
                                      {event.play_detail_2 && <div><strong>Play Detail 2:</strong> {event.play_detail_2}</div>}
                                      {event.event_successful !== null && event.event_successful !== undefined && (
                                        <div><strong>Successful:</strong> {event.event_successful ? 'Yes' : 'No'}</div>
                                      )}
                                    </div>
                                  </div>

                                  {/* Context Info */}
                                  <div className="pt-2 border-t border-border/30">
                                    <div className="font-semibold mb-1">Context:</div>
                                    <div className="grid grid-cols-2 gap-2">
                                      {event.event_team_zone && <div><strong>Zone:</strong> {event.event_team_zone}</div>}
                                      {event.team_venue && <div><strong>Team Venue:</strong> {event.team_venue}</div>}
                                      {event.team_id && <div><strong>Team ID:</strong> {event.team_id}</div>}
                                      {event.event_team_id && <div><strong>Event Team ID:</strong> {event.event_team_id}</div>}
                                      {event.strength && <div><strong>Strength:</strong> {event.strength}</div>}
                                      {event.home_team && <div><strong>Home Team:</strong> {event.home_team}</div>}
                                      {event.away_team && <div><strong>Away Team:</strong> {event.away_team}</div>}
                                    </div>
                                  </div>

                                  {/* Flags */}
                                  <div className="pt-2 border-t border-border/30">
                                    <div className="font-semibold mb-1">Flags:</div>
                                    <div className="grid grid-cols-2 gap-2">
                                      {event.is_goal === 1 && <div className="text-goal">✓ Goal</div>}
                                      {event.is_save === 1 && <div className="text-primary">✓ Save</div>}
                                      {event.is_highlight === 1 && <div>✓ Highlight</div>}
                                      {event.is_rebound === 1 && <div>✓ Rebound</div>}
                                      {event.is_rush === 1 && <div>✓ Rush</div>}
                                    </div>
                                  </div>

                                  {/* Linking Info */}
                                  <div className="pt-2 border-t border-border/30">
                                    <div className="font-semibold mb-1">Linking:</div>
                                    <div className="space-y-1">
                                      {eventAny.event_chain_key && <div><strong>Event Chain Key:</strong> {eventAny.event_chain_key}</div>}
                                      {eventAny.linked_event_key && <div><strong>Linked Event Key:</strong> {eventAny.linked_event_key}</div>}
                                      {eventAny.sequence_key && <div><strong>Sequence Key:</strong> {eventAny.sequence_key}</div>}
                                      {eventAny.play_key && <div><strong>Play Key:</strong> {eventAny.play_key}</div>}
                                      {linkedEvents && linkedEvents.length > 1 && (
                                        <div className="mt-2 pt-2 border-t border-border/30">
                                          <div className="font-semibold mb-1">Linked Events ({linkedEvents.length}):</div>
                                          {linkedEvents.filter(e => e.event_id !== event.event_id).map((linkedEvent, i) => (
                                            <div key={i} className="text-xs pl-2 border-l-2 border-border/30">
                                              • {getEventDescription(linkedEvent)}
                                            </div>
                                          ))}
                                        </div>
                                      )}
                                    </div>
                                  </div>

                                  {/* Video Info */}
                                  {(event.running_video_time || event.video_url) && (
                                    <div className="pt-2 border-t border-border/30">
                                      <div className="font-semibold mb-1">Video:</div>
                                      <div className="space-y-1">
                                        {event.running_video_time && <div><strong>Video Time:</strong> {event.running_video_time}s</div>}
                                        {event.video_url && <div><strong>Video URL:</strong> <a href={event.video_url} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">{event.video_url}</a></div>}
                                      </div>
                                    </div>
                                  )}

                                  {/* Raw JSON (Collapsible) */}
                                  <details className="pt-2 border-t border-border/30">
                                    <summary className="font-semibold cursor-pointer hover:text-foreground">Raw JSON Data</summary>
                                    <pre className="mt-2 text-[10px] overflow-auto max-h-60 bg-background p-2 rounded border border-border/30">
                                      {JSON.stringify(event, null, 2)}
                                    </pre>
                                  </details>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
