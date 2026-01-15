'use client'

import Link from 'next/link'
import { Target, Play, Clock, Zap, Video, ExternalLink } from 'lucide-react'
import { cn } from '@/lib/utils'
import { TeamLogo } from '@/components/teams/team-logo'
import { formatYouTubeUrlWithTime, calculateVideoTimestamp } from '@/lib/utils/video'

interface HighlightEvent {
  event_id?: string
  game_id: number
  period: number
  time_seconds?: number
  event_type: string
  event_detail: string
  event_player_1?: string
  event_player_2?: string
  team_id?: string
  team_name?: string
  is_goal?: boolean
  is_highlight?: boolean
  is_save?: boolean
  video_url?: string
  running_video_time?: number
  video_timestamp?: number
  event_time?: string
  period_time?: string
}

interface GameHighlightsProps {
  highlights: HighlightEvent[]
  homeTeam?: {
    team_id?: string
    team_name?: string
    team_logo?: string
    team_cd?: string
    primary_color?: string
    team_color1?: string
    team_color2?: string
  }
  awayTeam?: {
    team_id?: string
    team_name?: string
    team_logo?: string
    team_cd?: string
    primary_color?: string
    team_color1?: string
    team_color2?: string
  }
  gameId: number
  gameVideoUrl?: string | null
  gameVideoStartOffset?: number | null
}

interface GameHighlightsProps {
  highlights: HighlightEvent[]
  homeTeam?: {
    team_id?: string
    team_name?: string
    team_logo?: string
    team_cd?: string
    primary_color?: string
    team_color1?: string
    team_color2?: string
  }
  awayTeam?: {
    team_id?: string
    team_name?: string
    team_logo?: string
    team_cd?: string
    primary_color?: string
    team_color1?: string
    team_color2?: string
  }
  gameId: number
}

export function GameHighlights({ 
  highlights, 
  homeTeam, 
  awayTeam,
  gameId,
  gameVideoUrl,
  gameVideoStartOffset = 0
}: GameHighlightsProps) {
  if (!highlights || highlights.length === 0) {
    return (
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="px-4 py-3 bg-accent border-b border-border">
          <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
            <Play className="w-4 h-4 text-primary" />
            Game Highlights
          </h2>
        </div>
        <div className="p-6 text-center">
          <p className="text-sm text-muted-foreground">
            No highlight data available for this game.
          </p>
        </div>
      </div>
    )
  }
  
  const formatTime = (seconds?: number, periodTime?: string) => {
    if (periodTime) return periodTime
    if (!seconds) return '-'
    const minutes = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${minutes}:${secs.toString().padStart(2, '0')}`
  }
  
  const getEventIcon = (event: HighlightEvent) => {
    if (event.is_goal) return <Target className="w-4 h-4 text-goal" />
    if (event.is_save) return <Zap className="w-4 h-4 text-save" />
    return <Play className="w-4 h-4 text-primary" />
  }
  
  const getEventLabel = (event: HighlightEvent) => {
    if (event.is_goal) return 'Goal'
    if (event.is_save) return 'Save'
    if (event.event_type === 'Shot') return 'Shot'
    if (event.event_type === 'Hit') return 'Hit'
    return event.event_type || 'Event'
  }
  
  const getTeamForEvent = (event: HighlightEvent) => {
    if (!event.team_id) return null
    const teamId = String(event.team_id)
    if (homeTeam && String(homeTeam.team_id) === teamId) return homeTeam
    if (awayTeam && String(awayTeam.team_id) === teamId) return awayTeam
    return null
  }
  
  // Get video URL for an event (prioritize event-specific URL, fallback to game URL)
  const getVideoUrlForEvent = (event: HighlightEvent): string | null => {
    const videoUrl = event.video_url || gameVideoUrl
    if (!videoUrl) return null
    
    // Use running_video_time from event, or video_timestamp, or calculate from time_seconds
    const runningVideoTime = event.running_video_time ?? event.video_timestamp ?? (event.time_seconds ? event.time_seconds : null)
    
    if (runningVideoTime !== null && runningVideoTime !== undefined) {
      // Adjust for video start offset
      const adjustedTime = calculateVideoTimestamp(runningVideoTime, gameVideoStartOffset)
      return formatYouTubeUrlWithTime(videoUrl, adjustedTime)
    }
    
    // If no time info, just return the base URL
    return formatYouTubeUrlWithTime(videoUrl, null)
  }
  
  return (
    <div className="bg-card rounded-xl border border-border overflow-hidden">
      <div className="px-4 py-3 bg-accent border-b border-border">
        <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
          <Play className="w-4 h-4 text-primary" />
          Game Highlights ({highlights.length})
        </h2>
      </div>
      <div className="divide-y divide-border max-h-[600px] overflow-y-auto">
        {highlights.map((event, index) => {
          const eventTeam = getTeamForEvent(event)
          const timeStr = formatTime(event.time_seconds, event.period_time || event.event_time)
          
          return (
            <div 
              key={event.event_id || `highlight-${index}`} 
              className="p-4 hover:bg-muted/50 transition-colors"
            >
              <div className="flex items-start gap-4">
                {/* Time & Period */}
                <div className="w-20 flex-shrink-0 text-center">
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-1">
                    P{event.period}
                  </div>
                  <div className="flex items-center justify-center gap-1">
                    <Clock className="w-3 h-3 text-muted-foreground" />
                    <span className="font-mono text-sm text-foreground">{timeStr}</span>
                  </div>
                </div>
                
                {/* Team Logo */}
                {eventTeam && (
                  <TeamLogo
                    src={eventTeam.team_logo || null}
                    name={eventTeam.team_name || ''}
                    abbrev={eventTeam.team_cd}
                    primaryColor={eventTeam.primary_color || eventTeam.team_color1}
                    secondaryColor={eventTeam.team_color2}
                    size="sm"
                  />
                )}
                
                {/* Event Details */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    {getEventIcon(event)}
                    <span className={cn(
                      'text-sm font-semibold',
                      event.is_goal && 'text-goal',
                      event.is_save && 'text-save',
                      !event.is_goal && !event.is_save && 'text-foreground'
                    )}>
                      {getEventLabel(event)}
                    </span>
                  </div>
                  
                  {event.event_player_1 && (
                    <div className="text-sm text-foreground">
                      {event.event_player_1}
                      {event.event_player_2 && (
                        <span className="text-muted-foreground">
                          {' '}(Assist: {event.event_player_2})
                        </span>
                      )}
                    </div>
                  )}
                  
                  {event.event_detail && event.event_detail !== event.event_type && (
                    <div className="text-xs text-muted-foreground mt-1">
                      {event.event_detail}
                    </div>
                  )}
                </div>
                
                {/* Video Link (if available) */}
                {(() => {
                  const videoUrl = getVideoUrlForEvent(event)
                  if (!videoUrl) return null
                  
                  return (
                    <Link
                      href={videoUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-shrink-0 text-primary hover:text-foreground transition-colors flex items-center gap-1.5 px-2 py-1 rounded hover:bg-primary/10"
                      title="Watch highlight on YouTube"
                    >
                      <Video className="w-4 h-4" />
                      <span className="text-xs font-medium">Watch</span>
                      <ExternalLink className="w-3 h-3 opacity-70" />
                    </Link>
                  )
                })()}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
