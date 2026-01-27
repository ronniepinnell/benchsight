'use client'

import { useState, useMemo, useCallback } from 'react'
import Link from 'next/link'
import { Video, Play, Star, Clock, ChevronDown, Target } from 'lucide-react'
import { cn } from '@/lib/utils'
import { extractYouTubeVideoId, formatYouTubeEmbedUrl, formatYouTubeHighlightUrl } from '@/lib/utils/video'
import { PlayerPhoto } from '@/components/players/player-photo'
import { IceRinkSVG, type PlayerMarker, type PuckPosition } from '@/components/games/ice-rink-svg'
import { HighlightEventContext, type SelectedEvent } from '@/components/games/highlight-event-context'
import type { FactPuckXYLong, FactPlayerXYLong } from '@/types/database'

// Types
interface GameVideo {
  video_key: string
  game_id: number
  video_type: string
  video_description: string | null
  video_url: string
  period_1_start: number | null
  period_2_start: number | null
  period_3_start: number | null
}

interface Highlight {
  event_id: string
  event_type: string
  event_detail: string | null
  period: number
  player_name: string
  player_team: string
  player_id?: string
  player_image?: string | null
  team_logo?: string | null
  primary_color?: string | null
  is_goal: number
  running_video_time: number
  event_start_min?: number | null
  event_start_sec?: number | null
  // Additional event details
  event_team_zone?: string | null
  strength?: string | null
  is_rebound?: number
  is_rush?: number
  play_detail1?: string | null
  play_detail_2?: string | null
  event_player_2?: string | null
  team_venue?: string | null
  // Shot location and goalie info
  puck_x_start?: number | null
  puck_y_start?: number | null
  goalie_player_id?: string | null
  goalie_name?: string | null
  // Future: separate highlight video URL (compilation clips)
  highlight_video_url?: string | null
}

interface StarPlayer {
  player_id: string
  player_name: string
  player_image?: string | null
  team_name?: string
  team_id?: string
  team_logo?: string | null
  team_cd?: string
  primary_color?: string
  goals: number
  assists: number
  points: number
  position?: string
  saves?: number
  save_pct?: number
  goals_against?: number
}

interface GameMediaSectionProps {
  videos: GameVideo[]
  highlights: Highlight[]
  stars: StarPlayer[]
  gameId: number
  homeTeam: string
  awayTeam: string
  homeColor?: string
  awayColor?: string
  homeTeamId?: string
  teamStatsContent?: React.ReactNode
  className?: string
  // XY visualization data
  puckXYData?: FactPuckXYLong[]
  playerXYData?: FactPlayerXYLong[]
  playerIdToJerseyMap?: Record<string, number>
  playerIdToTeamIdMap?: Record<string, string>
}

// Highlight timing - start 10 seconds before, end 15 seconds after the event
const HIGHLIGHT_PRE_OFFSET = 10
const HIGHLIGHT_POST_OFFSET = 15

// Format game time (countdown) to MM:SS
function formatGameTime(minutes: number | null | undefined, seconds: number | null | undefined): string {
  const mins = minutes ?? 0
  const secs = seconds ?? 0
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// Get period label
function getPeriodLabel(period: number): string {
  if (period === 1) return 'P1'
  if (period === 2) return 'P2'
  if (period === 3) return 'P3'
  return `OT${period - 3}`
}

// Parse assists from play_detail columns
function parseAssists(playDetail1: string | null | undefined, playDetail2: string | null | undefined): {
  primaryAssist: string | null
  secondaryAssist: string | null
} {
  let primaryAssist: string | null = null
  let secondaryAssist: string | null = null

  const details = [playDetail1, playDetail2].filter(Boolean)

  for (const detail of details) {
    if (detail?.includes('AssistPrimary')) {
      // Extract player name if embedded, otherwise just mark as present
      primaryAssist = 'Primary'
    }
    if (detail?.includes('AssistSecondary')) {
      secondaryAssist = 'Secondary'
    }
  }

  return { primaryAssist, secondaryAssist }
}

export function GameMediaSection({
  videos,
  highlights,
  stars,
  gameId,
  homeTeam,
  awayTeam,
  homeColor = '#1e40af',
  awayColor = '#dc2626',
  homeTeamId,
  teamStatsContent,
  className,
  puckXYData = [],
  playerXYData = [],
  playerIdToJerseyMap = {},
  playerIdToTeamIdMap = {},
}: GameMediaSectionProps) {
  const [selectedVideoIndex, setSelectedVideoIndex] = useState(0)
  const [videoStartTime, setVideoStartTime] = useState<number | null>(null)
  const [videoEndTime, setVideoEndTime] = useState<number | null>(null)
  const [autoplay, setAutoplay] = useState(false)
  const [showAllHighlights, setShowAllHighlights] = useState(false)
  const [eventTypeFilter, setEventTypeFilter] = useState<string>('all')
  const [expandedHighlight, setExpandedHighlight] = useState<string | null>(null)
  const [playingHighlight, setPlayingHighlight] = useState<string | null>(null)
  const [selectedContextEvent, setSelectedContextEvent] = useState<SelectedEvent | null>(null)
  const [focusedPlayerId, setFocusedPlayerId] = useState<string | null>(null)

  // Index XY data by event_id for fast lookup
  const puckXYByEvent = useMemo(() => {
    const map = new Map<string, FactPuckXYLong[]>()
    for (const row of puckXYData) {
      const existing = map.get(row.event_id)
      if (existing) existing.push(row)
      else map.set(row.event_id, [row])
    }
    return map
  }, [puckXYData])

  const playerXYByEvent = useMemo(() => {
    const map = new Map<string, FactPlayerXYLong[]>()
    for (const row of playerXYData) {
      const existing = map.get(row.event_id)
      if (existing) existing.push(row)
      else map.set(row.event_id, [row])
    }
    return map
  }, [playerXYData])

  // Build visualization for a given event_id
  const buildVisualization = useCallback((eventId: string, highlight: Highlight): {
    players: PlayerMarker[]
    puckPath: PuckPosition[]
  } | null => {
    const puckRows = puckXYByEvent.get(eventId)
    const playerRows = playerXYByEvent.get(eventId)

    // Build puck path
    const puckPath: PuckPosition[] = []
    if (puckRows && puckRows.length > 0) {
      const sorted = [...puckRows].sort((a, b) => a.point_number - b.point_number)
      for (const row of sorted) {
        puckPath.push({ x: row.x, y: row.y, seq: row.point_number })
      }
    } else if (highlight.puck_x_start != null && highlight.puck_y_start != null) {
      puckPath.push({ x: highlight.puck_x_start, y: highlight.puck_y_start })
    }

    // Build player markers
    const players: PlayerMarker[] = []
    if (playerRows && playerRows.length > 0) {
      // Group by player_id, include all points
      const byPlayer = new Map<string, FactPlayerXYLong[]>()
      for (const row of playerRows) {
        const existing = byPlayer.get(row.player_id)
        if (existing) existing.push(row)
        else byPlayer.set(row.player_id, [row])
      }

      for (const [pid, points] of Array.from(byPlayer.entries())) {
        const sorted = [...points].sort((a, b) => a.point_number - b.point_number)
        const first = sorted[0]
        const jerseyNum = playerIdToJerseyMap[pid]
        const teamId = playerIdToTeamIdMap[pid]
        const isHome = teamId ? teamId === homeTeamId : first.is_event_team
        const team: 'home' | 'away' = isHome ? 'home' : 'away'
        const isSelected = first.player_role === 'event_player_1'

        for (const pt of sorted) {
          players.push({
            x: pt.x,
            y: pt.y,
            name: pt.player_name,
            number: jerseyNum !== undefined ? jerseyNum : undefined,
            team,
            isSelected,
            playerId: pid,
            seq: pt.point_number,
            role: first.player_role,
          })
        }
      }
    }

    if (puckPath.length === 0 && players.length === 0) return null
    return { players, puckPath }
  }, [puckXYByEvent, playerXYByEvent, playerIdToJerseyMap, playerIdToTeamIdMap, homeTeamId])

  const hasVideos = videos.length > 0
  const hasHighlights = highlights.length > 0
  const hasStars = stars.length >= 3 && stars[0]?.points > 0

  // Get unique event types for filter (Goals first, then alphabetical)
  const eventTypes = hasHighlights
    ? ['all', ...Array.from(new Set(highlights.map(h => h.is_goal === 1 ? 'Goal' : h.event_type))).sort((a, b) => {
        if (a === 'Goal') return -1
        if (b === 'Goal') return 1
        return a.localeCompare(b)
      })]
    : ['all']

  // If nothing to show, return null
  if (!hasVideos && !hasHighlights && !hasStars) {
    return null
  }

  const selectedVideo = videos[selectedVideoIndex]
  const videoId = selectedVideo ? extractYouTubeVideoId(selectedVideo.video_url) : null

  // Build embed URL - use highlight URL if we have start/end times, otherwise regular embed
  let embedUrl: string | null = null
  if (videoId) {
    if (videoStartTime !== null && videoEndTime !== null) {
      // Highlight mode with start, end, and autoplay
      embedUrl = formatYouTubeHighlightUrl(videoId, videoStartTime, videoEndTime, autoplay)
    } else if (videoStartTime !== null) {
      // Just start time
      embedUrl = formatYouTubeEmbedUrl(videoId, videoStartTime)
      if (autoplay) {
        embedUrl += (embedUrl?.includes('?') ? '&' : '?') + 'autoplay=1'
      }
    } else {
      // No time parameters
      embedUrl = formatYouTubeEmbedUrl(videoId, null)
    }
  }

  // Filter highlights by event type, then sort (goals first, then other highlights)
  const filteredHighlights = eventTypeFilter === 'all'
    ? highlights
    : highlights.filter(h => {
        const eventType = h.is_goal === 1 ? 'Goal' : h.event_type
        return eventType === eventTypeFilter
      })

  const goalHighlights = filteredHighlights.filter(h => h.is_goal === 1)
  const otherHighlights = filteredHighlights.filter(h => h.is_goal !== 1)
  const sortedHighlights = [...goalHighlights, ...otherHighlights]
  const displayHighlights = showAllHighlights ? sortedHighlights : sortedHighlights.slice(0, 5)

  // Star colors for ranking
  const starColors = {
    1: 'text-yellow-500',
    2: 'text-gray-400',
    3: 'text-amber-700'
  }

  return (
    <div className={cn('grid grid-cols-1 lg:grid-cols-3 gap-6', className)}>
      {/* Left Column: Video + Highlights */}
      <div className="lg:col-span-2 space-y-4">
        {/* Video Player */}
        {hasVideos && embedUrl && (
          <div className="bg-card rounded-xl border border-border overflow-hidden">
            <div className="px-4 py-2 border-b border-border bg-gradient-to-r from-primary/10 via-transparent to-primary/10 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Video className="w-4 h-4 text-primary" />
                <h2 className="font-display text-sm font-semibold uppercase tracking-wider">Game Video</h2>
              </div>

              {/* Video Switcher */}
              {videos.length > 1 && (
                <div className="flex gap-1">
                  {videos.map((video, idx) => (
                    <button
                      key={video.video_key}
                      onClick={() => {
                        setSelectedVideoIndex(idx)
                        setVideoStartTime(null)
                        setVideoEndTime(null)
                        setAutoplay(false)
                      }}
                      className={cn(
                        'px-3 py-1 text-xs font-medium rounded-md transition-colors',
                        idx === selectedVideoIndex
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-muted hover:bg-muted/80 text-muted-foreground'
                      )}
                    >
                      {video.video_type.replace('_', ' ')}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <div className="aspect-video w-full">
              <iframe
                key={`${selectedVideo?.video_key}-${videoStartTime}-${videoEndTime}`}
                src={embedUrl}
                title="Game Video"
                className="w-full h-full"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            </div>
          </div>
        )}

        {/* Highlights List */}
        {hasHighlights && hasVideos && (
          <div className="bg-card rounded-xl border border-border overflow-hidden">
            <div className="px-4 py-2 border-b border-border bg-gradient-to-r from-yellow-500/10 via-transparent to-yellow-500/10">
              <div className="flex items-center justify-between gap-2 flex-wrap">
                <div className="flex items-center gap-2">
                  <Play className="w-4 h-4 text-yellow-500" />
                  <h2 className="font-display text-sm font-semibold uppercase tracking-wider">Highlights</h2>
                  <span className="text-xs text-muted-foreground">
                    ({eventTypeFilter === 'all' ? highlights.length : filteredHighlights.length}{eventTypeFilter !== 'all' && ` / ${highlights.length}`})
                  </span>
                </div>

                {/* Event Type Filter */}
                {eventTypes.length > 2 && (
                  <div className="flex gap-1 flex-wrap">
                    {eventTypes.map((type) => (
                      <button
                        key={type}
                        onClick={() => {
                          setEventTypeFilter(type)
                          setShowAllHighlights(false)
                        }}
                        className={cn(
                          'px-2 py-0.5 text-xs font-medium rounded transition-colors',
                          eventTypeFilter === type
                            ? type === 'Goal'
                              ? 'bg-green-500/20 text-green-600 dark:text-green-400'
                              : 'bg-primary text-primary-foreground'
                            : 'bg-muted/50 hover:bg-muted text-muted-foreground'
                        )}
                      >
                        {type === 'all' ? 'All' : type}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className="divide-y divide-border">
              {displayHighlights.map((highlight) => {
                const isExpanded = expandedHighlight === highlight.event_id

                return (
                  <div key={highlight.event_id}>
                    {/* Highlight Row - Click to expand */}
                    <button
                      onClick={() => {
                        if (isExpanded) {
                          // Collapsing - also stop video and clear rink state
                          setExpandedHighlight(null)
                          setPlayingHighlight(null)
                          setSelectedContextEvent(null)
                          setFocusedPlayerId(null)
                        } else {
                          setExpandedHighlight(highlight.event_id)
                          setSelectedContextEvent(null)
                          setFocusedPlayerId(null)
                        }
                      }}
                      className={cn(
                        'w-full px-4 py-3 flex items-center gap-3 hover:bg-muted/50 transition-colors text-left',
                        isExpanded && 'bg-muted/30'
                      )}
                    >
                      {/* Period & Time */}
                      <div className="flex-shrink-0 w-14 text-center">
                        <div className="text-xs font-mono font-semibold text-muted-foreground">{getPeriodLabel(highlight.period)}</div>
                        <div className="text-xs font-mono text-muted-foreground">
                          {formatGameTime(highlight.event_start_min, highlight.event_start_sec)}
                        </div>
                      </div>

                      {/* Player Photo */}
                      <div className="flex-shrink-0">
                        <PlayerPhoto
                          src={highlight.player_image || null}
                          name={highlight.player_name}
                          primaryColor={highlight.primary_color}
                          size="sm"
                        />
                      </div>

                      {/* Event Details */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          {highlight.is_goal === 1 ? (
                            <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-green-500/20 text-green-600 dark:text-green-400 text-xs font-semibold">
                              GOAL
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-600 dark:text-blue-400 text-xs font-medium">
                              {highlight.event_type}
                            </span>
                          )}
                          <span className="text-sm font-medium text-foreground">{highlight.player_name}</span>
                          <span className="text-xs text-muted-foreground">({highlight.player_team})</span>
                        </div>
                      </div>

                      {/* Expand/Collapse Icon */}
                      <div className="flex-shrink-0">
                        <ChevronDown className={cn(
                          'w-5 h-5 text-muted-foreground transition-transform',
                          isExpanded && 'rotate-180'
                        )} />
                      </div>
                    </button>

                    {/* Expanded Details Panel */}
                    {isExpanded && (() => {
                      const isPlaying = playingHighlight === highlight.event_id

                      // Build highlight video URL (only when playing)
                      const highlightVideoUrl = isPlaying
                        ? (highlight.highlight_video_url
                            ? highlight.highlight_video_url
                            : selectedVideo
                              ? formatYouTubeHighlightUrl(
                                  selectedVideo.video_url,
                                  Math.max(0, highlight.running_video_time - HIGHLIGHT_PRE_OFFSET),
                                  highlight.running_video_time + HIGHLIGHT_POST_OFFSET,
                                  true
                                )
                              : null)
                        : null

                      // Parse assists from play_detail columns
                      const assists = parseAssists(highlight.play_detail1, highlight.play_detail_2)
                      const hasAssists = highlight.event_player_2 || assists.primaryAssist || assists.secondaryAssist

                      // Build rink visualization: use context event if selected, otherwise highlight event
                      const vizEventId = selectedContextEvent?.event_id || highlight.event_id
                      const viz = buildVisualization(vizEventId, highlight)

                      return (
                        <div className="bg-muted/20 border-t border-border/50">
                          {/* Video Player (only shown after Watch is clicked) */}
                          {isPlaying && highlightVideoUrl && (
                            <div className="aspect-video w-full">
                              <iframe
                                key={`highlight-${highlight.event_id}`}
                                src={highlightVideoUrl}
                                title={`${highlight.event_type} - ${highlight.player_name}`}
                                className="w-full h-full"
                                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                allowFullScreen
                              />
                            </div>
                          )}

                          {/* Main Content Grid */}
                          <div className="p-4 space-y-4">
                            {/* Top Row: Rink Visualization + Event Details */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              {/* Left: Ice Rink with players + puck */}
                              <div className="space-y-2">
                                <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                                  <Target className="w-3 h-3" />
                                  {selectedContextEvent ? (
                                    <>
                                      Play Location
                                      <span className="text-primary normal-case font-normal">
                                        ({selectedContextEvent.event_type}: {selectedContextEvent.player_name})
                                      </span>
                                    </>
                                  ) : (
                                    'Event Location'
                                  )}
                                </div>
                                {viz ? (
                                  <IceRinkSVG
                                    players={viz.players}
                                    puckPath={viz.puckPath}
                                    showPuck={true}
                                    homeColor={homeColor}
                                    awayColor={awayColor}
                                    homeTeamName={homeTeam}
                                    awayTeamName={awayTeam}
                                    focusedPlayerId={focusedPlayerId}
                                    onPlayerClick={(pid) => setFocusedPlayerId(prev => prev === pid ? null : pid)}
                                  />
                                ) : (
                                  <div className="bg-muted/30 rounded-lg p-4 text-center text-xs text-muted-foreground">
                                    No location data available
                                  </div>
                                )}
                                {/* Legend */}
                                {viz && (
                                  <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
                                    <span className="flex items-center gap-1">
                                      <span className="w-2 h-2 rounded-full inline-block" style={{ backgroundColor: homeColor }} />
                                      {homeTeam}
                                    </span>
                                    <span className="flex items-center gap-1">
                                      <span className="w-2 h-2 rounded-full inline-block" style={{ backgroundColor: awayColor }} />
                                      {awayTeam}
                                    </span>
                                    <span className="flex items-center gap-1">
                                      <span className="w-2 h-2 rounded-full inline-block bg-gray-800" />
                                      Puck
                                    </span>
                                  </div>
                                )}
                              </div>

                              {/* Right: Event Details */}
                              <div className="space-y-3">
                                {/* Player & Team */}
                                <div className="flex items-center gap-2 flex-wrap">
                                  <span className="text-sm font-semibold text-foreground">{highlight.player_name}</span>
                                  <span className="text-sm text-muted-foreground">• {highlight.player_team}</span>
                                  {highlight.team_venue && (
                                    <span className="text-xs px-1.5 py-0.5 rounded bg-muted text-muted-foreground">
                                      {highlight.team_venue}
                                    </span>
                                  )}
                                </div>

                                {/* Goalie */}
                                {highlight.goalie_name && (
                                  <div className="text-xs">
                                    <span className="text-muted-foreground">Goalie: </span>
                                    <span className="font-medium text-foreground">{highlight.goalie_name}</span>
                                  </div>
                                )}

                                {/* Assists */}
                                {hasAssists && (
                                  <div className="text-xs">
                                    <span className="text-muted-foreground">Assists: </span>
                                    <span className="font-medium text-foreground">
                                      {highlight.event_player_2 || 'Unassisted'}
                                    </span>
                                  </div>
                                )}

                                {/* Tags Row */}
                                <div className="flex flex-wrap gap-1.5">
                                  <span className={cn(
                                    'px-2 py-0.5 rounded text-xs font-medium',
                                    highlight.is_goal === 1
                                      ? 'bg-green-500/20 text-green-600 dark:text-green-400'
                                      : 'bg-blue-500/20 text-blue-600 dark:text-blue-400'
                                  )}>
                                    {highlight.event_type}
                                  </span>

                                  {highlight.event_detail && highlight.event_detail !== 'Goal_Scored' && (
                                    <span className="px-2 py-0.5 rounded bg-muted text-muted-foreground text-xs">
                                      {highlight.event_detail.replace(/_/g, ' ')}
                                    </span>
                                  )}

                                  {highlight.strength && highlight.strength !== 'Even' && (
                                    <span className={cn(
                                      'px-2 py-0.5 rounded text-xs font-medium',
                                      highlight.strength === 'PP' ? 'bg-yellow-500/20 text-yellow-600 dark:text-yellow-400' :
                                      highlight.strength === 'SH' ? 'bg-red-500/20 text-red-600 dark:text-red-400' :
                                      'bg-muted text-muted-foreground'
                                    )}>
                                      {highlight.strength}
                                    </span>
                                  )}

                                  {highlight.is_rush === 1 && (
                                    <span className="px-2 py-0.5 rounded bg-purple-500/20 text-purple-600 dark:text-purple-400 text-xs font-medium">
                                      Rush
                                    </span>
                                  )}

                                  {highlight.is_rebound === 1 && (
                                    <span className="px-2 py-0.5 rounded bg-orange-500/20 text-orange-600 dark:text-orange-400 text-xs font-medium">
                                      Rebound
                                    </span>
                                  )}

                                  {highlight.event_team_zone && (
                                    <span className="px-2 py-0.5 rounded bg-muted text-muted-foreground text-xs">
                                      {highlight.event_team_zone} Zone
                                    </span>
                                  )}
                                </div>

                                {/* Period & Time + Watch Button */}
                                <div className="flex items-center justify-between pt-2">
                                  <div className="text-xs text-muted-foreground">
                                    Period {highlight.period} • {formatGameTime(highlight.event_start_min, highlight.event_start_sec)}
                                  </div>

                                  {!isPlaying && selectedVideo && (
                                    <button
                                      onClick={(e) => {
                                        e.stopPropagation()
                                        setPlayingHighlight(highlight.event_id)
                                      }}
                                      className="flex items-center gap-2 px-3 py-1.5 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors text-sm"
                                    >
                                      <Play className="w-4 h-4" />
                                      Watch
                                    </button>
                                  )}
                                </div>
                              </div>
                            </div>

                            {/* Bottom: Play Sequence */}
                            <div className="border-t border-border/50 pt-4">
                              <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                                <Clock className="w-3 h-3" />
                                Play Sequence
                              </div>
                              <HighlightEventContext
                                gameId={gameId}
                                eventId={highlight.event_id}
                                currentEventTeam={highlight.player_team}
                                homeTeam={homeTeam}
                                awayTeam={awayTeam}
                                homeColor={homeColor}
                                awayColor={awayColor}
                                onEventSelect={(event) => setSelectedContextEvent(event)}
                              />
                            </div>
                          </div>
                        </div>
                      )
                    })()}
                  </div>
                )
              })}
            </div>

            {sortedHighlights.length > 5 && (
              <button
                onClick={() => setShowAllHighlights(!showAllHighlights)}
                className="w-full px-4 py-2 text-sm text-primary hover:bg-muted/30 transition-colors flex items-center justify-center gap-1"
              >
                {showAllHighlights ? 'Show Less' : `Show All ${eventTypeFilter !== 'all' ? eventTypeFilter + 's ' : ''}(${sortedHighlights.length})`}
                <ChevronDown className={cn('w-4 h-4 transition-transform', showAllHighlights && 'rotate-180')} />
              </button>
            )}

            {/* No results message when filter has no matches */}
            {sortedHighlights.length === 0 && eventTypeFilter !== 'all' && (
              <div className="px-4 py-6 text-center text-sm text-muted-foreground">
                No {eventTypeFilter} highlights in this game
              </div>
            )}
          </div>
        )}
      </div>

      {/* Right Column: Three Stars + Team Stats */}
      {(hasStars || teamStatsContent) && (
        <div className="lg:col-span-1 flex flex-col gap-4">
          {hasStars && (
          <div className="bg-card rounded-xl border border-border overflow-hidden flex-shrink-0">
            <div className="px-4 py-2 border-b border-border bg-gradient-to-r from-yellow-500/10 via-transparent to-yellow-500/10">
              <div className="flex items-center gap-2">
                <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                <h2 className="font-display text-sm font-semibold uppercase tracking-wider">Three Stars</h2>
              </div>
            </div>

            <div className="divide-y divide-border">
              {stars.slice(0, 3).map((player, idx) => {
                const rank = (idx + 1) as 1 | 2 | 3
                const isGoalie = player.position?.toUpperCase() === 'G' ||
                                 player.position?.toUpperCase() === 'GOALIE' ||
                                 player.saves !== undefined

                return (
                  <div key={player.player_id} className="px-4 py-2.5 flex items-center gap-3 hover:bg-muted/30 transition-colors">
                    {/* Rank stars */}
                    <div className="flex items-center gap-0.5 w-12 flex-shrink-0">
                      {Array.from({ length: rank }).map((_, i) => (
                        <Star
                          key={i}
                          className={cn('w-3.5 h-3.5 fill-current', starColors[rank])}
                        />
                      ))}
                    </div>

                    {/* Player photo */}
                    <Link
                      href={`/norad/player/${player.player_id}`}
                      className="flex-shrink-0 hover:opacity-80 transition-opacity"
                    >
                      <PlayerPhoto
                        src={player.player_image || null}
                        name={player.player_name}
                        primaryColor={player.primary_color}
                        size="sm"
                      />
                    </Link>

                    {/* Player name & team */}
                    <div className="flex-1 min-w-0">
                      <Link
                        href={`/norad/player/${player.player_id}`}
                        className="font-display text-sm font-semibold text-foreground hover:text-primary transition-colors block truncate"
                      >
                        {player.player_name}
                      </Link>
                      {player.team_name && (
                        <span className="text-xs text-muted-foreground truncate">{player.team_name}</span>
                      )}
                    </div>

                    {/* Stats */}
                    <div className="flex-shrink-0 text-right">
                      {isGoalie ? (
                        <div>
                          <div className="font-mono text-sm font-bold text-foreground">
                            {player.saves ?? 0} SV
                          </div>
                          <div className="text-xs font-mono text-muted-foreground">
                            {player.save_pct !== undefined
                              ? `${(player.save_pct * 100).toFixed(1)}%`
                              : `${player.goals_against ?? 0} GA`
                            }
                          </div>
                        </div>
                      ) : (
                        <div>
                          <div className="font-mono text-sm font-bold text-foreground">
                            {player.goals}G {player.assists}A
                          </div>
                          <div className="text-xs font-mono text-muted-foreground">
                            {player.points} pts
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
          )}

          {/* Team Stats Comparison - stretches to fill remaining height */}
          {teamStatsContent && (
            <div className="flex-1 flex flex-col">
              {teamStatsContent}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
