'use client'

import { useState, useEffect } from 'react'
import { createClient } from '@/lib/supabase/client'
import { cn } from '@/lib/utils'
import { Loader2, MapPin } from 'lucide-react'

interface EventContext {
  event_id: string
  event_type: string
  event_detail: string | null
  player_name: string | null
  player_team: string | null
  period: number
  event_start_min: number | null
  event_start_sec: number | null
  running_video_time: number
  puck_x_start: number | null
  puck_y_start: number | null
  is_goal: number
}

export interface SelectedEvent {
  event_id: string
  player_name: string | null
  event_type: string
  puck_x_start: number | null
  puck_y_start: number | null
  is_goal: boolean
}

interface HighlightEventContextProps {
  gameId: number
  eventId: string
  currentEventTeam: string
  homeTeam: string
  awayTeam: string
  homeColor?: string
  awayColor?: string
  onEventSelect?: (event: SelectedEvent | null) => void
  className?: string
}

// Format game time (countdown) to MM:SS
function formatGameTime(minutes: number | null | undefined, seconds: number | null | undefined): string {
  const mins = minutes ?? 0
  const secs = seconds ?? 0
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// Get abbreviated event type
function getEventAbbreviation(eventType: string): string {
  const abbreviations: Record<string, string> = {
    'Shot': 'SHOT',
    'Goal': 'GOAL',
    'Pass': 'PASS',
    'Faceoff': 'F/O',
    'Possession': 'POSS',
    'Turnover': 'T/O',
    'Takeaway': 'TK',
    'Giveaway': 'GV',
    'ZoneEntry': 'ENTRY',
    'ZoneExit': 'EXIT',
    'Penalty': 'PEN',
    'Hit': 'HIT',
    'Block': 'BLK',
    'Save': 'SAVE',
    'Stoppage': 'STOP',
  }
  return abbreviations[eventType] || eventType.slice(0, 4).toUpperCase()
}

export function HighlightEventContext({
  gameId,
  eventId,
  currentEventTeam,
  homeTeam,
  awayTeam,
  homeColor = '#1e40af',
  awayColor = '#dc2626',
  onEventSelect,
  className
}: HighlightEventContextProps) {
  const [events, setEvents] = useState<EventContext[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null)

  useEffect(() => {
    async function fetchEventContext() {
      setLoading(true)
      setError(null)
      setSelectedEventId(null)

      const supabase = createClient()

      // First get the target event to find its running_video_time
      const { data: targetEvent, error: targetError } = await supabase
        .from('fact_events')
        .select('running_video_time, period')
        .eq('event_id', eventId)
        .single()

      if (targetError || !targetEvent) {
        setError('Failed to load event context')
        setLoading(false)
        return
      }

      // Get ALL events in the same period before this one (by running_video_time)
      // Filter to player_role='event_player_1' to get one row per event (avoid duplicates)
      const { data: contextEvents, error: eventsError } = await supabase
        .from('fact_events')
        .select(`
          event_id, event_type, event_detail, player_name, player_team,
          period, event_start_min, event_start_sec, running_video_time,
          puck_x_start, puck_y_start, is_goal
        `)
        .eq('game_id', gameId)
        .eq('player_role', 'event_player_1')
        .eq('period', targetEvent.period)
        .lt('running_video_time', targetEvent.running_video_time)
        .gt('running_video_time', 0)
        .order('running_video_time', { ascending: false })
        .limit(200)

      if (eventsError) {
        setError('Failed to load previous events')
        setLoading(false)
        return
      }

      // Find the last stoppage/faceoff to use as the start of the play sequence
      const allEvents = (contextEvents || []).reverse()
      const lastStoppageIdx = allEvents.findLastIndex(
        (e: EventContext) => e.event_type === 'Faceoff' || e.event_type === 'Stoppage'
      )
      // Show from last faceoff/stoppage onward, or last 30 events if no stoppage found
      const startIdx = lastStoppageIdx >= 0 ? lastStoppageIdx : Math.max(0, allEvents.length - 30)
      setEvents(allEvents.slice(startIdx))
      setLoading(false)
    }

    fetchEventContext()
  }, [gameId, eventId])

  const handleEventClick = (event: EventContext) => {
    const hasLocation = event.puck_x_start !== null && event.puck_y_start !== null

    if (selectedEventId === event.event_id) {
      // Deselect - go back to showing the highlight event
      setSelectedEventId(null)
      onEventSelect?.(null)
    } else if (hasLocation) {
      setSelectedEventId(event.event_id)
      onEventSelect?.({
        event_id: event.event_id,
        player_name: event.player_name,
        event_type: event.event_type,
        puck_x_start: event.puck_x_start,
        puck_y_start: event.puck_y_start,
        is_goal: event.is_goal === 1,
      })
    }
  }

  if (loading) {
    return (
      <div className={cn('flex items-center justify-center py-4', className)}>
        <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />
        <span className="ml-2 text-xs text-muted-foreground">Loading play sequence...</span>
      </div>
    )
  }

  if (error || events.length === 0) {
    return (
      <div className={cn('py-2 text-xs text-muted-foreground text-center', className)}>
        {error || 'No previous events available'}
      </div>
    )
  }

  return (
    <div className={cn('space-y-0.5', className)}>
      {events.map((event) => {
        const isHome = event.player_team === homeTeam
        const isAway = event.player_team === awayTeam
        const teamColor = isHome ? homeColor : isAway ? awayColor : undefined
        const hasLocation = event.puck_x_start !== null && event.puck_y_start !== null
        const isSelected = selectedEventId === event.event_id

        return (
          <button
            key={event.event_id}
            onClick={() => handleEventClick(event)}
            disabled={!hasLocation}
            className={cn(
              'w-full flex items-center gap-2 px-2 py-1 rounded text-xs text-left',
              'transition-colors',
              hasLocation ? 'cursor-pointer hover:bg-muted/40' : 'cursor-default',
              isSelected ? 'bg-primary/20 ring-1 ring-primary/50' : 'bg-muted/20'
            )}
          >
            {/* Time */}
            <span className="w-10 font-mono text-muted-foreground flex-shrink-0">
              {formatGameTime(event.event_start_min, event.event_start_sec)}
            </span>

            {/* Event Type */}
            <span
              className={cn(
                'w-12 font-semibold flex-shrink-0 text-center px-1 py-0.5 rounded',
                event.event_type === 'Goal' && 'bg-green-500/20 text-green-500',
                event.event_type === 'Shot' && 'bg-blue-500/20 text-blue-400',
                event.event_type === 'Turnover' && 'bg-red-500/20 text-red-400',
                !['Goal', 'Shot', 'Turnover'].includes(event.event_type) && 'bg-muted/50 text-muted-foreground'
              )}
            >
              {getEventAbbreviation(event.event_type)}
            </span>

            {/* Player */}
            <span className="flex-1 truncate text-foreground">
              {event.player_name || '-'}
            </span>

            {/* Location indicator */}
            {hasLocation && (
              <MapPin
                className={cn(
                  'w-3 h-3 flex-shrink-0',
                  isSelected ? 'text-primary' : 'text-muted-foreground'
                )}
              />
            )}

            {/* Team indicator */}
            <span
              className="w-2 h-2 rounded-full flex-shrink-0"
              style={{ backgroundColor: teamColor || '#666' }}
              title={event.player_team || 'Unknown'}
            />
          </button>
        )
      })}

      {/* Current event marker */}
      <button
        onClick={() => {
          setSelectedEventId(null)
          onEventSelect?.(null)
        }}
        className={cn(
          'w-full flex items-center gap-2 px-2 py-1 rounded text-xs',
          'transition-colors cursor-pointer',
          !selectedEventId
            ? 'bg-primary/20 ring-1 ring-primary/50'
            : 'bg-primary/10 hover:bg-primary/15'
        )}
      >
        <span className="text-primary font-medium">
          Current Event
        </span>
      </button>
    </div>
  )
}
