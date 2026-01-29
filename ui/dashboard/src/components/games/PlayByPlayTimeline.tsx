'use client'

import { useState, useMemo, useEffect, useRef, useCallback } from 'react'
import { cn } from '@/lib/utils'
import {
  Goal,
  AlertCircle,
  Clock,
  Filter,
  ChevronDown,
  ChevronUp,
  Target,
  Shield,
  Play,
  Link2,
  Video,
  Check,
  X
} from 'lucide-react'
import { extractYouTubeVideoId, formatYouTubeHighlightUrl } from '@/lib/utils/video'
import type { FactEvents, FactPuckXYLong, FactPlayerXYLong } from '@/types/database'
import { TeamLogo } from '@/components/teams/team-logo'
import { IceRinkSVG } from '@/components/games/ice-rink-svg'
import type { PlayerMarker, PuckPosition } from '@/components/games/ice-rink-svg'
import { NetFrontSVG } from '@/components/games/net-front-svg'

// Format text: remove underscores, add spaces to CamelCase, capitalize
function formatDisplayText(text: string | null | undefined): string {
  if (!text) return ''
  return text
    .replace(/_/g, ' ')  // Replace underscores with spaces
    .replace(/([a-z])([A-Z])/g, '$1 $2')  // Add space before capitals in CamelCase
    .replace(/([A-Z]+)([A-Z][a-z])/g, '$1 $2')  // Handle consecutive capitals
    .trim()
}

// Multi-select dropdown component
interface OptionGroup {
  label: string
  options: string[]
}

interface MultiSelectDropdownProps {
  label: string
  options: string[]
  selected: string[]
  onChange: (selected: string[]) => void
  isOpen: boolean
  onToggle: () => void
  formatOption?: (option: string) => string
  groups?: OptionGroup[]
}

function MultiSelectDropdown({
  label,
  options,
  selected,
  onChange,
  isOpen,
  onToggle,
  formatOption = (o) => o,
  groups
}: MultiSelectDropdownProps) {
  const toggleOption = (option: string) => {
    if (selected.includes(option)) {
      onChange(selected.filter(s => s !== option))
    } else {
      onChange([...selected, option])
    }
  }

  const clearAll = () => onChange([])

  const renderOption = (option: string) => (
    <button
      key={option}
      type="button"
      onClick={(e) => {
        e.stopPropagation()
        toggleOption(option)
      }}
      className={cn(
        "w-full px-3 py-1.5 text-xs text-left hover:bg-accent flex items-center gap-2",
        selected.includes(option) && "bg-primary/5"
      )}
    >
      <span className={cn(
        "w-4 h-4 border rounded flex items-center justify-center flex-shrink-0",
        selected.includes(option) ? "bg-primary border-primary" : "border-border"
      )}>
        {selected.includes(option) && <Check className="w-3 h-3 text-primary-foreground" />}
      </span>
      <span className="truncate">{formatOption(option)}</span>
    </button>
  )

  return (
    <div className="relative">
      <button
        type="button"
        onClick={onToggle}
        className={cn(
          "flex items-center gap-1 px-2 py-1.5 text-xs rounded-md border transition-colors min-w-[100px]",
          selected.length > 0
            ? "bg-primary/10 border-primary text-primary"
            : "bg-background border-border text-muted-foreground hover:text-foreground"
        )}
      >
        <span className="truncate max-w-[80px]">
          {selected.length === 0 ? label : `${label} (${selected.length})`}
        </span>
        <ChevronDown className="w-3 h-3 flex-shrink-0" />
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-1 z-50 bg-background border border-border rounded-md shadow-lg min-w-[200px] max-h-[300px] overflow-y-auto">
          {/* Clear all button */}
          {selected.length > 0 && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation()
                clearAll()
              }}
              className="w-full px-3 py-1.5 text-xs text-left text-destructive hover:bg-destructive/10 border-b border-border flex items-center gap-1"
            >
              <X className="w-3 h-3" />
              Clear all
            </button>
          )}

          {/* Grouped options */}
          {groups ? (
            groups.map(group => (
              <div key={group.label}>
                <div className="px-3 py-1 text-[10px] font-semibold text-muted-foreground uppercase tracking-wider bg-muted/30 border-b border-border sticky top-0">
                  {group.label}
                </div>
                {group.options.map(renderOption)}
              </div>
            ))
          ) : (
            options.map(renderOption)
          )}

          {!groups && options.length === 0 && (
            <div className="px-3 py-2 text-xs text-muted-foreground">No options</div>
          )}
        </div>
      )}
    </div>
  )
}

interface GameVideo {
  video_key: string
  video_type: string
  video_url: string
}

interface ShiftData {
  shift_id?: number
  shift_index?: number
  home_forward_1?: number | string
  home_forward_2?: number | string
  home_forward_3?: number | string
  home_defense_1?: number | string
  home_defense_2?: number | string
  home_xtra?: number | string
  home_goalie?: number | string
  away_forward_1?: number | string
  away_forward_2?: number | string
  away_forward_3?: number | string
  away_defense_1?: number | string
  away_defense_2?: number | string
  away_xtra?: number | string
  away_goalie?: number | string
}

interface RosterPlayer {
  name: string
  gameNumber: number | null
  teamId: string
  isGoalie: boolean
}

interface PlayByPlayTimelineProps {
  events: FactEvents[]
  homeTeam: string
  awayTeam: string
  homeTeamId: string
  awayTeamId: string
  playersMap?: Map<string, { player_name?: string; player_full_name?: string }>
  homeTeamData?: { team_name: string; team_logo?: string | null; team_cd?: string; primary_color?: string; team_color1?: string }
  awayTeamData?: { team_name: string; team_logo?: string | null; team_cd?: string; primary_color?: string; team_color1?: string }
  videoUrl?: string | null
  videoStartOffset?: number
  videos?: GameVideo[]
  shifts?: ShiftData[]
  jerseyToPlayerMap?: Map<string, { player_name: string; team_id: string }>
  puckXYData?: FactPuckXYLong[]
  playerXYData?: FactPlayerXYLong[]
  playerIdToJerseyMap?: Record<string, number>
  playerIdToTeamIdMap?: Record<string, string>
  rosterPlayers?: RosterPlayer[]
  eventPlayerRoles?: Array<{ event_id: string; player_id: string; player_role: string }>
}

// Highlight timing offsets
const HIGHLIGHT_PRE_OFFSET = 5
const HIGHLIGHT_POST_OFFSET = 15

export function PlayByPlayTimeline({
  events,
  homeTeam,
  awayTeam,
  homeTeamId,
  awayTeamId,
  playersMap = new Map(),
  homeTeamData,
  awayTeamData,
  videoUrl,
  videoStartOffset = 0,
  videos = [],
  shifts = [],
  jerseyToPlayerMap = new Map(),
  puckXYData = [],
  playerXYData = [],
  playerIdToJerseyMap = {},
  playerIdToTeamIdMap = {},
  rosterPlayers = [],
  eventPlayerRoles = []
}: PlayByPlayTimelineProps) {
  const [expandedPeriods, setExpandedPeriods] = useState<Set<number>>(new Set([1, 2, 3]))
  const [selectedEvent, setSelectedEvent] = useState<string | null>(null)
  const [showDebug, setShowDebug] = useState(false)
  const [debugEvent, setDebugEvent] = useState<FactEvents | null>(null)
  const [viewMode, setViewMode] = useState<'basic' | 'detailed'>('basic')
  const [highlightedEvent, setHighlightedEvent] = useState<string | null>(null)
  const [playingEvent, setPlayingEvent] = useState<string | null>(null)
  const [selectedVideoIndex, setSelectedVideoIndex] = useState(0)
  const [focusedPlayerId, setFocusedPlayerId] = useState<string | null>(null)
  const [roleFilter, setRoleFilter] = useState<string | null>(null) // null = all, 'event_primary', 'opp_primary', 'event_support', 'opp_support'

  // Get current video
  const currentVideo = videos.length > 0 ? videos[selectedVideoIndex] : videoUrl ? {
    video_key: 'main',
    video_type: 'Main',
    video_url: videoUrl,
  } : null

  // Get embedded video URL with timestamp
  const getEmbedVideoUrl = (event: FactEvents): string | null => {
    if (!currentVideo) return null
    if (event.running_video_time === undefined || event.running_video_time === null) return null
    const videoId = extractYouTubeVideoId(currentVideo.video_url)
    if (!videoId) return null
    const startTime = Math.max(0, event.running_video_time - HIGHLIGHT_PRE_OFFSET)
    const endTime = event.running_video_time + HIGHLIGHT_POST_OFFSET
    return formatYouTubeHighlightUrl(videoId, startTime, endTime, true)
  }

  // Check if video available for event
  const hasVideo = (event: FactEvents): boolean => {
    return currentVideo !== null && event.running_video_time !== undefined && event.running_video_time !== null
  }

  // Get player name from jersey number
  const getPlayerNameFromJersey = (jerseyNum: number | string | null | undefined): string => {
    if (!jerseyNum || jerseyNum === 0 || jerseyNum === '0') return ''
    const jersey = String(Math.floor(Number(jerseyNum)))
    const player = jerseyToPlayerMap.get(jersey)
    return player?.player_name || `#${jersey}`
  }

  // Build reverse map: player name -> player IDs (for filtering by all event/opp players)
  const nameToIdsMap = useMemo(() => {
    const map = new Map<string, Set<string>>()
    playersMap.forEach((info, playerId) => {
      const names = [info.player_name, info.player_full_name].filter(Boolean) as string[]
      names.forEach(name => {
        let ids = map.get(name)
        if (!ids) {
          ids = new Set<string>()
          map.set(name, ids)
        }
        ids.add(playerId)
      })
    })
    return map
  }, [playersMap])

  // Check if any player from selectedNames appears in an event's event_player_ids or opp_player_ids
  const eventInvolvesAnyPlayer = useCallback((event: FactEvents, selectedNames: string[]): boolean => {
    // Quick check on direct name fields first
    if (event.event_player_1 && selectedNames.includes(event.event_player_1)) return true
    if (event.event_player_2 && selectedNames.includes(event.event_player_2)) return true
    if (event.player_name && selectedNames.includes(event.player_name)) return true

    // Build set of all selected player IDs
    const selectedIds = new Set<string>()
    selectedNames.forEach(name => {
      const ids = nameToIdsMap.get(name)
      if (ids) ids.forEach(id => selectedIds.add(id))
    })
    if (selectedIds.size === 0) return false

    // Check event_player_ids (comma-separated)
    if (event.event_player_ids) {
      const eventIds = event.event_player_ids.split(',').map(id => id.trim())
      if (eventIds.some(id => selectedIds.has(id))) return true
    }

    // Check opp_player_ids (comma-separated)
    if (event.opp_player_ids) {
      const oppIds = event.opp_player_ids.split(',').map(id => id.trim())
      if (oppIds.some(id => selectedIds.has(id))) return true
    }

    return false
  }, [nameToIdsMap])

  // Index puck XY data by event_id
  const puckXYByEvent = useMemo(() => {
    const map = new Map<string, FactPuckXYLong[]>()
    for (const row of puckXYData) {
      const existing = map.get(row.event_id)
      if (existing) {
        existing.push(row)
      } else {
        map.set(row.event_id, [row])
      }
    }
    return map
  }, [puckXYData])

  // Index player XY data by event_id
  const playerXYByEvent = useMemo(() => {
    const map = new Map<string, FactPlayerXYLong[]>()
    for (const row of playerXYData) {
      const existing = map.get(row.event_id)
      if (existing) {
        existing.push(row)
      } else {
        map.set(row.event_id, [row])
      }
    }
    return map
  }, [playerXYData])

  // Index event player roles by event_id -> Set of player_roles present in that event
  // Also build event_id -> Map<player_id, player_role> for player-specific role filtering
  const eventRolesMap = useMemo(() => {
    const rolesMap = new Map<string, Set<string>>()
    const playerRolesMap = new Map<string, Map<string, string>>()
    for (const row of eventPlayerRoles) {
      if (!row.event_id || !row.player_role) continue
      // Set of roles present in event
      let roles = rolesMap.get(row.event_id)
      if (!roles) {
        roles = new Set()
        rolesMap.set(row.event_id, roles)
      }
      roles.add(row.player_role)
      // Player -> role mapping
      if (row.player_id) {
        let playerMap = playerRolesMap.get(row.event_id)
        if (!playerMap) {
          playerMap = new Map()
          playerRolesMap.set(row.event_id, playerMap)
        }
        playerMap.set(row.player_id, row.player_role)
      }
    }
    return { rolesMap, playerRolesMap }
  }, [eventPlayerRoles])

  // Index play_detail1/play_detail_2 per player_name per event_id from allEvents
  const eventPlayerDetailsMap = useMemo(() => {
    const map = new Map<string, Map<string, { play_detail1: string | null; play_detail_2: string | null; player_role: string }>>()
    for (const e of events) {
      if (!e.event_id || !e.player_name) continue
      let eventMap = map.get(e.event_id)
      if (!eventMap) {
        eventMap = new Map()
        map.set(e.event_id, eventMap)
      }
      // Use player_name as key (unique within an event's roles)
      if (!eventMap.has(e.player_name)) {
        eventMap.set(e.player_name, {
          play_detail1: e.play_detail1 || null,
          play_detail_2: (e as any).play_detail_2 || null,
          player_role: e.player_role || ''
        })
      }
    }
    return map
  }, [events])

  // Build IceRinkSVG visualization data for an event
  const buildEventVisualization = useCallback((event: FactEvents): {
    players: PlayerMarker[]
    puckPath: PuckPosition[]
  } | null => {
    const puckRows = puckXYByEvent.get(event.event_id)
    const playerRows = playerXYByEvent.get(event.event_id)

    // If no XY long data at all, return null (caller handles fallback)
    if (!puckRows && !playerRows) return null

    // Build puck path from long data, sorted by point_number
    const puckPath: PuckPosition[] = (puckRows || [])
      .sort((a, b) => a.point_number - b.point_number)
      .map(r => ({ x: r.x, y: r.y, seq: r.point_number }))

    // Build player markers - ALL points per player (for movement paths)
    const players: PlayerMarker[] = []
    // Track which player_role maps to which player_id (for isSelected)
    const roleToId = new Map<string, string>()

    const allPoints = (playerRows || [])
      .sort((a, b) => a.player_role.localeCompare(b.player_role) || a.point_number - b.point_number)

    for (const row of allPoints) {
      roleToId.set(row.player_role, row.player_id)

      // Determine home/away
      let team: 'home' | 'away' = 'away'
      const playerTeamId = playerIdToTeamIdMap[row.player_id]
      if (playerTeamId) {
        team = String(playerTeamId) === String(homeTeamId) ? 'home' : 'away'
      } else {
        const eventTeamVenue = (event as any).team_venue
        if (row.is_event_team) {
          team = eventTeamVenue === 'Home' ? 'home' : 'away'
        } else {
          team = eventTeamVenue === 'Home' ? 'away' : 'home'
        }
      }

      const jerseyNum = playerIdToJerseyMap[row.player_id]
      const isSelected = row.player_role === 'event_player_1'

      players.push({
        x: row.x,
        y: row.y,
        name: row.player_name,
        number: jerseyNum !== undefined ? jerseyNum : undefined,
        team,
        isSelected,
        playerId: row.player_id,
        seq: row.point_number,
        role: row.player_role
      })
    }

    return { players, puckPath }
  }, [puckXYByEvent, playerXYByEvent, homeTeamId, playerIdToJerseyMap, playerIdToTeamIdMap])

  // Get players on ice for an event based on shift_id
  const getPlayersOnIce = (event: FactEvents): { home: string[], away: string[] } | null => {
    const shiftId = (event as any).shift_id || (event as any).shift_index
    if (!shiftId || shifts.length === 0) return null

    const shift = shifts.find(s => s.shift_id === shiftId || s.shift_index === shiftId)
    if (!shift) return null

    const homePlayerJerseys: (number | string)[] = []
    const awayPlayerJerseys: (number | string)[] = []

    // Collect home players
    if (shift.home_forward_1) homePlayerJerseys.push(shift.home_forward_1)
    if (shift.home_forward_2) homePlayerJerseys.push(shift.home_forward_2)
    if (shift.home_forward_3) homePlayerJerseys.push(shift.home_forward_3)
    if (shift.home_defense_1) homePlayerJerseys.push(shift.home_defense_1)
    if (shift.home_defense_2) homePlayerJerseys.push(shift.home_defense_2)
    if (shift.home_xtra) homePlayerJerseys.push(shift.home_xtra)

    // Collect away players
    if (shift.away_forward_1) awayPlayerJerseys.push(shift.away_forward_1)
    if (shift.away_forward_2) awayPlayerJerseys.push(shift.away_forward_2)
    if (shift.away_forward_3) awayPlayerJerseys.push(shift.away_forward_3)
    if (shift.away_defense_1) awayPlayerJerseys.push(shift.away_defense_1)
    if (shift.away_defense_2) awayPlayerJerseys.push(shift.away_defense_2)
    if (shift.away_xtra) awayPlayerJerseys.push(shift.away_xtra)

    return {
      home: homePlayerJerseys.map(j => getPlayerNameFromJersey(j)).filter(Boolean),
      away: awayPlayerJerseys.map(j => getPlayerNameFromJersey(j)).filter(Boolean)
    }
  }

  // Refs for scrolling to events
  const eventRefs = useRef<Map<string, HTMLDivElement>>(new Map())

  // Scroll to an event by ID
  const scrollToEvent = useCallback((eventId: string) => {
    const element = eventRefs.current.get(eventId)
    if (element) {
      // Find the event's period and expand it if needed
      const event = events.find(e => e.event_id === eventId)
      if (event) {
        const period = getPeriod(event)
        if (!expandedPeriods.has(period)) {
          const newExpanded = new Set(expandedPeriods)
          newExpanded.add(period)
          setExpandedPeriods(newExpanded)
        }
      }

      // Scroll to the element with some offset
      setTimeout(() => {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' })
        // Highlight the event temporarily
        setHighlightedEvent(eventId)
        setSelectedEvent(eventId)
        setTimeout(() => setHighlightedEvent(null), 2000)
      }, 100)
    }
  }, [events, expandedPeriods])

  // Multi-select Filters (using arrays)
  const [selectedPeriods, setSelectedPeriods] = useState<number[]>([])
  const [selectedTeams, setSelectedTeams] = useState<string[]>([])
  const [selectedPlayers, setSelectedPlayers] = useState<string[]>([])
  const [selectedPlayersOnIce, setSelectedPlayersOnIce] = useState<string[]>([])
  const [selectedEventTypes, setSelectedEventTypes] = useState<string[]>([])
  const [selectedEventDetails, setSelectedEventDetails] = useState<string[]>([])
  const [selectedEventDetails2, setSelectedEventDetails2] = useState<string[]>([])
  const [showFilterDropdown, setShowFilterDropdown] = useState<string | null>(null)
  
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

  // Base filter function - excludes saves, rebounds, bad giveaways
  const getBaseFilteredEvents = useMemo(() => {
    let filtered = events

    // Exclude saves
    filtered = filtered.filter(e => {
      const isSave = e.is_save === 1 ||
                    e.event_type?.toLowerCase().includes('save')
      return !isSave
    })

    // Exclude rebounds
    filtered = filtered.filter(e => {
      const isRebound = e.is_rebound === 1 ||
                       e.event_type?.toLowerCase().includes('rebound') ||
                       e.event_detail?.toLowerCase().includes('rebound') ||
                       e.play_detail1?.toLowerCase().includes('rebound') ||
                       e.event_detail_2?.toLowerCase().includes('rebound')
      return !isRebound
    })

    // Exclude "bad" giveaways
    filtered = filtered.filter(e => {
      const isGiveaway = e.event_type?.toLowerCase().includes('giveaway') ||
                        e.play_detail1?.toLowerCase().includes('giveaway')
      if (isGiveaway) {
        const eventDetail = e.event_detail?.toLowerCase() || ''
        const eventDetail2 = e.event_detail_2?.toLowerCase() || ''
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

        return !isBad
      }
      return true
    })

    return filtered
  }, [events])

  // Get unique event types for filtering (based on base filtered events with other filters applied)
  const availableEventTypes = useMemo(() => {
    let filtered = getBaseFilteredEvents

    // Apply team filter
    if (selectedTeams.length > 0) {
      filtered = filtered.filter(e => e.player_team && selectedTeams.includes(e.player_team))
    }

    // Apply player filter (checks all event_player and opp_player fields)
    if (selectedPlayers.length > 0) {
      filtered = filtered.filter(e => eventInvolvesAnyPlayer(e, selectedPlayers))
    }

    const types = new Set<string>()
    filtered.forEach(event => {
      if (event.event_type) types.add(event.event_type)
    })
    return Array.from(types).sort()
  }, [getBaseFilteredEvents, selectedTeams, selectedPlayers, eventInvolvesAnyPlayer])

  // Get unique event details for filtering (cascading with event type)
  const availableEventDetails = useMemo(() => {
    let filtered = getBaseFilteredEvents

    // Apply event type filter
    if (selectedEventTypes.length > 0) {
      filtered = filtered.filter(e => e.event_type && selectedEventTypes.includes(e.event_type))
    }

    // Apply team filter
    if (selectedTeams.length > 0) {
      filtered = filtered.filter(e => e.player_team && selectedTeams.includes(e.player_team))
    }

    // Apply player filter (checks all event_player and opp_player fields)
    if (selectedPlayers.length > 0) {
      filtered = filtered.filter(e => eventInvolvesAnyPlayer(e, selectedPlayers))
    }

    const details = new Set<string>()
    filtered.forEach(event => {
      if (event.event_detail) details.add(event.event_detail)
    })
    return Array.from(details).sort()
  }, [getBaseFilteredEvents, selectedEventTypes, selectedTeams, selectedPlayers, eventInvolvesAnyPlayer])

  // Get unique event detail 2 / play_detail_2 for filtering (cascading with event type and detail)
  const availableEventDetails2 = useMemo(() => {
    let filtered = getBaseFilteredEvents

    // Apply event type filter
    if (selectedEventTypes.length > 0) {
      filtered = filtered.filter(e => e.event_type && selectedEventTypes.includes(e.event_type))
    }

    // Apply event detail filter
    if (selectedEventDetails.length > 0) {
      filtered = filtered.filter(e => e.event_detail && selectedEventDetails.includes(e.event_detail))
    }

    // Apply team filter
    if (selectedTeams.length > 0) {
      filtered = filtered.filter(e => e.player_team && selectedTeams.includes(e.player_team))
    }

    // Apply player filter (checks all event_player and opp_player fields)
    if (selectedPlayers.length > 0) {
      filtered = filtered.filter(e => eventInvolvesAnyPlayer(e, selectedPlayers))
    }

    const details = new Set<string>()
    filtered.forEach(event => {
      if (event.play_detail_2) details.add(event.play_detail_2)
      if (event.event_detail_2) details.add(event.event_detail_2)
    })
    return Array.from(details).sort()
  }, [getBaseFilteredEvents, selectedEventTypes, selectedEventDetails, selectedTeams, selectedPlayers, eventInvolvesAnyPlayer])

  // Get unique teams for filtering (cascading with event type and detail)
  const availableTeams = useMemo(() => {
    let filtered = getBaseFilteredEvents

    // Apply event type filter
    if (selectedEventTypes.length > 0) {
      filtered = filtered.filter(e => e.event_type && selectedEventTypes.includes(e.event_type))
    }

    // Apply event detail filter
    if (selectedEventDetails.length > 0) {
      filtered = filtered.filter(e => e.event_detail && selectedEventDetails.includes(e.event_detail))
    }

    const teams = new Set<string>()
    filtered.forEach(event => {
      if (event.player_team) teams.add(event.player_team)
    })
    return Array.from(teams).sort()
  }, [getBaseFilteredEvents, selectedEventTypes, selectedEventDetails])

  // Build roster lookup maps: player name -> game number, player name -> teamId
  const rosterGameNumberMap = useMemo(() => {
    const map = new Map<string, number>()
    rosterPlayers.forEach(rp => {
      if (rp.gameNumber !== null) map.set(rp.name, rp.gameNumber)
    })
    return map
  }, [rosterPlayers])

  const rosterTeamMap = useMemo(() => {
    const map = new Map<string, string>()
    rosterPlayers.forEach(rp => {
      map.set(rp.name, rp.teamId)
    })
    return map
  }, [rosterPlayers])

  // Format player name with game number: "#17 John Smith"
  const formatPlayerOption = useCallback((name: string) => {
    const num = rosterGameNumberMap.get(name)
    return num !== undefined ? `#${num} ${name}` : name
  }, [rosterGameNumberMap])

  // Get unique players for filtering (cascading with event type, detail, and team)
  // Includes goalies from roster data
  const availablePlayers = useMemo(() => {
    let filtered = getBaseFilteredEvents

    // Apply event type filter
    if (selectedEventTypes.length > 0) {
      filtered = filtered.filter(e => e.event_type && selectedEventTypes.includes(e.event_type))
    }

    // Apply event detail filter
    if (selectedEventDetails.length > 0) {
      filtered = filtered.filter(e => e.event_detail && selectedEventDetails.includes(e.event_detail))
    }

    // Apply team filter
    if (selectedTeams.length > 0) {
      filtered = filtered.filter(e => e.player_team && selectedTeams.includes(e.player_team))
    }

    const players = new Set<string>()
    filtered.forEach(event => {
      if (event.event_player_1) players.add(event.event_player_1)
      if (event.event_player_2) players.add(event.event_player_2)
      if (event.player_name) players.add(event.player_name)
    })

    // Add goalies from roster (they don't appear as event_player_1/2 typically)
    rosterPlayers.forEach(rp => {
      if (rp.isGoalie) {
        // If team filter is active, only include goalies from selected teams
        if (selectedTeams.length > 0) {
          const rosterTeamName = rp.teamId === homeTeamId ? homeTeam : rp.teamId === awayTeamId ? awayTeam : ''
          if (rosterTeamName && selectedTeams.includes(rosterTeamName)) {
            players.add(rp.name)
          }
        } else {
          players.add(rp.name)
        }
      }
    })

    return Array.from(players).sort()
  }, [getBaseFilteredEvents, selectedEventTypes, selectedEventDetails, selectedTeams, rosterPlayers, homeTeamId, awayTeamId, homeTeam, awayTeam])

  // Build grouped player options for the Player filter (grouped by team)
  const playerGroups = useMemo((): OptionGroup[] => {
    const homeLabel = homeTeamData?.team_cd || homeTeam
    const awayLabel = awayTeamData?.team_cd || awayTeam
    const homePlayers: string[] = []
    const awayPlayers: string[] = []
    const otherPlayers: string[] = []

    availablePlayers.forEach(name => {
      const teamId = rosterTeamMap.get(name)
      if (teamId === homeTeamId) {
        homePlayers.push(name)
      } else if (teamId === awayTeamId) {
        awayPlayers.push(name)
      } else {
        otherPlayers.push(name)
      }
    })

    const groups: OptionGroup[] = []
    if (awayPlayers.length > 0) groups.push({ label: awayLabel, options: awayPlayers })
    if (homePlayers.length > 0) groups.push({ label: homeLabel, options: homePlayers })
    if (otherPlayers.length > 0) groups.push({ label: 'Other', options: otherPlayers })
    return groups
  }, [availablePlayers, rosterTeamMap, homeTeamId, awayTeamId, homeTeam, awayTeam, homeTeamData, awayTeamData])

  // Get all unique players who were on ice during any shift (for "Players On Ice" filter)
  // Includes goalies from shifts
  const availablePlayersOnIce = useMemo(() => {
    const players = new Set<string>()
    shifts.forEach(shift => {
      const jerseys = [
        shift.home_forward_1, shift.home_forward_2, shift.home_forward_3,
        shift.home_defense_1, shift.home_defense_2, shift.home_xtra,
        shift.home_goalie,
        shift.away_forward_1, shift.away_forward_2, shift.away_forward_3,
        shift.away_defense_1, shift.away_defense_2, shift.away_xtra,
        shift.away_goalie
      ]
      jerseys.forEach(jersey => {
        if (jersey && jersey !== 0 && jersey !== '0') {
          const name = getPlayerNameFromJersey(jersey)
          if (name && !name.startsWith('#')) {
            players.add(name)
          }
        }
      })
    })
    return Array.from(players).sort()
  }, [shifts, jerseyToPlayerMap])

  // Reset child filters when parent filter changes make current selection invalid
  useEffect(() => {
    if (selectedEventTypes.length > 0) {
      const validTypes = selectedEventTypes.filter(t => availableEventTypes.includes(t))
      if (validTypes.length !== selectedEventTypes.length) {
        setSelectedEventTypes(validTypes)
      }
    }
  }, [availableEventTypes, selectedEventTypes])

  useEffect(() => {
    if (selectedEventDetails.length > 0) {
      const validDetails = selectedEventDetails.filter(d => availableEventDetails.includes(d))
      if (validDetails.length !== selectedEventDetails.length) {
        setSelectedEventDetails(validDetails)
      }
    }
  }, [availableEventDetails, selectedEventDetails])

  useEffect(() => {
    if (selectedEventDetails2.length > 0) {
      const validDetails = selectedEventDetails2.filter(d => availableEventDetails2.includes(d))
      if (validDetails.length !== selectedEventDetails2.length) {
        setSelectedEventDetails2(validDetails)
      }
    }
  }, [availableEventDetails2, selectedEventDetails2])

  useEffect(() => {
    if (selectedTeams.length > 0) {
      const validTeams = selectedTeams.filter(t => availableTeams.includes(t))
      if (validTeams.length !== selectedTeams.length) {
        setSelectedTeams(validTeams)
      }
    }
  }, [availableTeams, selectedTeams])

  useEffect(() => {
    if (selectedPlayers.length > 0) {
      const validPlayers = selectedPlayers.filter(p => availablePlayers.includes(p))
      if (validPlayers.length !== selectedPlayers.length) {
        setSelectedPlayers(validPlayers)
      }
    }
  }, [availablePlayers, selectedPlayers])

  // Close filter dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = () => setShowFilterDropdown(null)
    if (showFilterDropdown) {
      document.addEventListener('click', handleClickOutside)
      return () => document.removeEventListener('click', handleClickOutside)
    }
  }, [showFilterDropdown])

  // Helper to check if any player in the shift is selected in playersOnIce filter
  const shiftHasSelectedPlayer = (shiftId: number | undefined): boolean => {
    if (selectedPlayersOnIce.length === 0 || !shiftId) return true
    const shift = shifts.find(s => s.shift_id === shiftId || s.shift_index === shiftId)
    if (!shift) return true

    const jerseys = [
      shift.home_forward_1, shift.home_forward_2, shift.home_forward_3,
      shift.home_defense_1, shift.home_defense_2, shift.home_xtra,
      shift.away_forward_1, shift.away_forward_2, shift.away_forward_3,
      shift.away_defense_1, shift.away_defense_2, shift.away_xtra
    ]

    return jerseys.some(jersey => {
      if (!jersey || jersey === 0 || jersey === '0') return false
      const name = getPlayerNameFromJersey(jersey)
      return name && selectedPlayersOnIce.includes(name)
    })
  }

  // Create maps for linked events - group events by linked_event_key (primary), then fallback to other keys
  const eventsByLinkedKey = useMemo(() => {
    const map = new Map<string, FactEvents[]>()
    events.forEach(event => {
      // Use linked_event_key first (primary driver), then fallback to sequence_key or play_key
      const eventAny = event as any // Type assertion to access fields that might not be in type
      const key = eventAny.linked_event_key || eventAny.sequence_key || eventAny.play_key
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

      // Filter by period (multi-select)
      if (selectedPeriods.length > 0 && !selectedPeriods.includes(period)) {
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
                         e.event_detail_2?.toLowerCase().includes('rebound')
        return !isRebound
      })

      // Exclude "bad" giveaways (misplay, pass intercepted, pass blocked, pass missed)
      filteredEvents = filteredEvents.filter(e => {
        const isGiveaway = e.event_type?.toLowerCase().includes('giveaway') || 
                          e.play_detail1?.toLowerCase().includes('giveaway')
        if (isGiveaway) {
          // Check if it's a "bad" giveaway: misplay, pass intercepted, pass blocked, pass missed
          const eventDetail = e.event_detail?.toLowerCase() || ''
          const eventDetail2 = e.event_detail_2?.toLowerCase() || ''
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

      // Filter by event type (multi-select)
      if (selectedEventTypes.length > 0) {
        filteredEvents = filteredEvents.filter(e => e.event_type && selectedEventTypes.includes(e.event_type))
      }

      // Filter by event detail (multi-select)
      if (selectedEventDetails.length > 0) {
        filteredEvents = filteredEvents.filter(e => e.event_detail && selectedEventDetails.includes(e.event_detail))
      }

      // Filter by event detail 2 / play_detail_2 (multi-select)
      if (selectedEventDetails2.length > 0) {
        filteredEvents = filteredEvents.filter(e => {
          return (e.play_detail_2 && selectedEventDetails2.includes(e.play_detail_2)) ||
                 (e.event_detail_2 && selectedEventDetails2.includes(e.event_detail_2))
        })
      }

      // Filter by team (multi-select)
      if (selectedTeams.length > 0) {
        filteredEvents = filteredEvents.filter(e => e.player_team && selectedTeams.includes(e.player_team))
      }

      // Filter by player (multi-select - checks all event_player and opp_player fields)
      if (selectedPlayers.length > 0) {
        filteredEvents = filteredEvents.filter(e => eventInvolvesAnyPlayer(e, selectedPlayers))
      }

      // Filter by players on ice (multi-select) - filter by shift
      if (selectedPlayersOnIce.length > 0) {
        filteredEvents = filteredEvents.filter(e => {
          const shiftId = (e as any).shift_id || (e as any).shift_index
          return shiftHasSelectedPlayer(shiftId)
        })
      }

      // Filter by role using fact_event_players data (proper player_role values)
      // Works with or without player selection (#182)
      if (roleFilter) {
        const { rolesMap, playerRolesMap } = eventRolesMap
        const matchRole = (role: string): boolean => {
          if (roleFilter === 'event_primary') return role === 'event_player_1'
          if (roleFilter === 'event_support') return role.startsWith('event_player_') && role !== 'event_player_1'
          if (roleFilter === 'opp_primary') return role === 'opp_player_1'
          if (roleFilter === 'opp_support') return role.startsWith('opp_player_') && role !== 'opp_player_1'
          return true
        }
        filteredEvents = filteredEvents.filter(e => {
          if (!e.event_id) return false
          if (selectedPlayers.length > 0) {
            // Player selected: show events where THAT player has the matching role
            const playerMap = playerRolesMap.get(e.event_id)
            if (!playerMap) return false
            return selectedPlayers.some(pid => {
              const role = playerMap.get(pid)
              return role ? matchRole(role) : false
            })
          } else {
            // No player selected: show events where ANY player has the matching role
            const roles = rolesMap.get(e.event_id)
            if (!roles) return false
            return Array.from(roles).some(matchRole)
          }
        })
      }

      if (filteredEvents.length > 0) {
        filtered.set(period, filteredEvents)
      }
    })

    return filtered
  }, [eventsByPeriod, selectedPeriods, selectedTeams, selectedPlayers, selectedPlayersOnIce, selectedEventTypes, selectedEventDetails, selectedEventDetails2, viewMode, shiftHasSelectedPlayer, eventInvolvesAnyPlayer, roleFilter, eventRolesMap])

  // Max period length in minutes (for detecting cumulative vs per-period times)
  const periodLengthMinutes = useMemo(() => {
    // Use P1's max event_start_min as the reference period length
    const p1Events = events.filter(e => getPeriod(e) === 1)
    let maxMin = 0
    p1Events.forEach(e => {
      if (typeof e.event_start_min === 'number' && !isNaN(e.event_start_min) && e.event_start_min <= 25) {
        maxMin = Math.max(maxMin, e.event_start_min)
      }
    })
    return maxMin > 0 ? maxMin : 18 // Default to 18 if no P1 data
  }, [events])

  const formatTime = (event: FactEvents): string => {
    const period = getPeriod(event)

    // Use event_start_min and event_start_sec directly - they are the period clock
    if (
      typeof event.event_start_min === 'number' &&
      typeof event.event_start_sec === 'number' &&
      !isNaN(event.event_start_min) &&
      !isNaN(event.event_start_sec)
    ) {
      let minutes = event.event_start_min
      const secs = event.event_start_sec

      // If minutes > period length * 1.3, it's likely cumulative (total game time)
      // Convert to per-period time by subtracting prior periods
      if (minutes > periodLengthMinutes * 1.3 && period > 1) {
        minutes = minutes - (period - 1) * periodLengthMinutes
      }

      // Clamp to reasonable range
      if (minutes < 0) minutes = 0

      return `${Math.floor(minutes)}:${Math.floor(secs).toString().padStart(2, '0')}`
    }

    // FALLBACK: Calculate from time_start_total_seconds
    const timeSeconds = event.time_start_total_seconds ?? event.time_seconds ?? 0

    // time_start_total_seconds could be countdown (high→low) or elapsed (low→high)
    // Use periodLengthMinutes to determine the period clock
    const periodLengthSec = periodLengthMinutes * 60
    if (periodLengthSec > 0 && timeSeconds >= 0 && timeSeconds <= periodLengthSec) {
      // Elapsed time → convert to countdown: periodLength - elapsed
      const countdown = periodLengthSec - timeSeconds
      const minutes = Math.floor(countdown / 60)
      const secs = Math.floor(countdown % 60)
      return `${minutes}:${secs.toString().padStart(2, '0')}`
    }

    // Last resort: direct display
    const minutes = Math.floor(Math.abs(timeSeconds) / 60)
    const secs = Math.floor(Math.abs(timeSeconds) % 60)
    return `${minutes}:${secs.toString().padStart(2, '0')}`
  }

  const formatEndTime = (event: FactEvents): string | null => {
    const period = getPeriod(event)

    // Use event_end_min and event_end_sec directly
    if (
      typeof event.event_end_min === 'number' &&
      typeof event.event_end_sec === 'number' &&
      !isNaN(event.event_end_min) &&
      !isNaN(event.event_end_sec)
    ) {
      let minutes = event.event_end_min
      const secs = event.event_end_sec

      // If cumulative, adjust to per-period
      if (minutes > periodLengthMinutes * 1.3 && period > 1) {
        minutes = minutes - (period - 1) * periodLengthMinutes
      }
      if (minutes < 0) minutes = 0

      return `${Math.floor(minutes)}:${Math.floor(secs).toString().padStart(2, '0')}`
    }

    // FALLBACK: Calculate from time_end_total_seconds
    const timeEndSeconds = (event as any).time_end_total_seconds
    if (timeEndSeconds != null && timeEndSeconds !== 0) {
      const periodLengthSec = periodLengthMinutes * 60
      if (periodLengthSec > 0 && timeEndSeconds >= 0 && timeEndSeconds <= periodLengthSec) {
        const countdown = periodLengthSec - timeEndSeconds
        const minutes = Math.floor(countdown / 60)
        const secs = Math.floor(countdown % 60)
        return `${minutes}:${secs.toString().padStart(2, '0')}`
      }
      const minutes = Math.floor(Math.abs(timeEndSeconds) / 60)
      const secs = Math.floor(Math.abs(timeEndSeconds) % 60)
      return `${minutes}:${secs.toString().padStart(2, '0')}`
    }

    return null
  }

  // Generate video URL with timestamp for an event
  const getVideoUrlWithTimestamp = (event: FactEvents): string | null => {
    if (!videoUrl || !event.running_video_time) return null

    // Calculate adjusted time: running_video_time - video_start_offset
    const adjustedTime = Math.max(0, event.running_video_time - videoStartOffset)
    const seconds = Math.floor(adjustedTime)

    // Handle YouTube URLs - add &t= parameter
    if (videoUrl.includes('youtube.com') || videoUrl.includes('youtu.be')) {
      const separator = videoUrl.includes('?') ? '&' : '?'
      return `${videoUrl}${separator}t=${seconds}`
    }

    // For other video URLs, just append timestamp as query param
    const separator = videoUrl.includes('?') ? '&' : '?'
    return `${videoUrl}${separator}t=${seconds}`
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
      return formatDisplayText(event.event_type) || formatDisplayText(event.event_detail) || formatDisplayText(event.play_detail1) || 'Stoppage'
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
    
    // Handle shots - show shot type from event_detail (e.g., Shot_OnNet, Shot_Missed, Shot_Blocked)
    if (event.event_type?.toLowerCase() === 'shot' ||
        event.event_type?.toLowerCase().includes('shot')) {
      const eventDetail = event.event_detail || ''

      // Parse the shot type from event_detail
      let shotOutcome = ''
      if (eventDetail.toLowerCase().includes('goal') || eventDetail.toLowerCase().includes('scored')) {
        shotOutcome = 'Goal'
      } else if (eventDetail.toLowerCase().includes('saved') || eventDetail.toLowerCase().includes('onnet')) {
        shotOutcome = 'Saved'
      } else if (eventDetail.toLowerCase().includes('blocked')) {
        shotOutcome = 'Blocked'
      } else if (eventDetail.toLowerCase().includes('missed') || eventDetail.toLowerCase().includes('post')) {
        shotOutcome = 'Missed'
      }

      // Get goalie name for saves
      const goalieName = oppPlayers.length > 0 ? oppPlayers[0] : null

      if (shotOutcome === 'Saved' && goalieName) {
        return `Shot by ${playerName} - Saved by ${goalieName}`
      } else if (shotOutcome === 'Blocked') {
        const blockerName = oppPlayers.length > 0 ? oppPlayers[0] : null
        return blockerName
          ? `Shot by ${playerName} - Blocked by ${blockerName}`
          : `Shot by ${playerName} - Blocked`
      } else if (shotOutcome === 'Missed') {
        return `Shot by ${playerName} - Missed`
      } else if (shotOutcome) {
        return `Shot by ${playerName} - ${shotOutcome}`
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
    
    // Handle turnovers - distinguish between giveaways and takeaways using event_detail
    if (event.event_type?.toLowerCase() === 'turnover' ||
        event.event_type?.toLowerCase().includes('turnover')) {
      const eventDetail = event.event_detail?.toLowerCase() || ''

      if (eventDetail.includes('takeaway')) {
        // Takeaway - good play by the player
        const fromPlayer = oppPlayers.length > 0 ? oppPlayers[0] : null
        return fromPlayer
          ? `Takeaway by ${playerName} from ${fromPlayer}`
          : `Takeaway by ${playerName}`
      } else if (eventDetail.includes('giveaway')) {
        // Giveaway - player lost the puck
        const toPlayer = oppPlayers.length > 0 ? oppPlayers[0] : null
        return toPlayer
          ? `Giveaway by ${playerName} to ${toPlayer}`
          : `Giveaway by ${playerName}`
      } else if (eventDetail.includes('intercept')) {
        const interceptor = oppPlayers.length > 0 ? oppPlayers[0] : null
        return interceptor
          ? `Pass Intercepted - ${interceptor} stole from ${playerName}`
          : `Pass Intercepted by opponent from ${playerName}`
      }

      // Generic turnover
      return `Turnover by ${playerName}`
    }

    // Handle standalone takeaways
    if (event.event_type?.toLowerCase().includes('takeaway') ||
        event.play_detail1?.toLowerCase().includes('takeaway')) {
      const fromPlayer = oppPlayers.length > 0 ? oppPlayers[0] : null
      return fromPlayer
        ? `Takeaway by ${playerName} from ${fromPlayer}`
        : `Takeaway by ${playerName}`
    }

    // Handle standalone giveaways
    if (event.event_type?.toLowerCase().includes('giveaway') ||
        event.play_detail1?.toLowerCase().includes('giveaway')) {
      const toPlayer = oppPlayers.length > 0 ? oppPlayers[0] : null
      return toPlayer
        ? `Giveaway by ${playerName} to ${toPlayer}`
        : `Giveaway by ${playerName}`
    }
    
    // Handle passes - show pass outcome from event_detail (e.g., Pass_Completed, Pass_Missed)
    if (event.event_type?.toLowerCase() === 'pass' ||
        event.event_type?.toLowerCase().includes('pass')) {
      const eventDetail = event.event_detail?.toLowerCase() || ''

      // Determine pass outcome from event_detail
      const isCompleted = eventDetail.includes('completed') || eventDetail.includes('success')
      const isIntercepted = eventDetail.includes('intercepted')
      const isBlocked = eventDetail.includes('blocked')
      const isMissed = eventDetail.includes('missed')

      // Get recipient from second player in event_player_ids
      const recipient = eventPlayers.length > 1 ? eventPlayers[1] : null
      const recipientText = recipient ? ` to ${recipient}` : ''

      if (isIntercepted) {
        const interceptor = oppPlayers.length > 0 ? oppPlayers[0] : null
        return interceptor
          ? `Pass by ${playerName} - Intercepted by ${interceptor}`
          : `Pass by ${playerName} - Intercepted`
      } else if (isBlocked) {
        return `Pass by ${playerName} - Blocked`
      } else if (isMissed) {
        return `Pass by ${playerName}${recipientText} - Missed`
      } else if (isCompleted) {
        return `Pass by ${playerName}${recipientText}`
      }

      // Fallback to event_successful field
      const isSuccessful = event.event_successful === true
      return `${isSuccessful ? 'Pass' : 'Pass'} by ${playerName}${recipientText}`
    }
    
    // Handle penalties
    if (event.event_type?.toLowerCase().includes('penalty')) {
      return `${playerName} - ${event.play_detail1 || event.event_type}`
    }
    
    // Handle faceoffs
    // Per CLAUDE.md: event_player_1 (player_role) is faceoff winner, opp_player_1 is faceoff loser
    // IMPORTANT: For faceoffs with multiple event_player_ids, the winner is in event.player_name field
    // event_player_ids may contain the winner + teammate who received the puck
    if (event.event_type?.toLowerCase().includes('faceoff')) {
      // Use player_name as primary source for faceoff winner (it's always the winner)
      const winnerName = event.player_name || playerName
      const loserName = oppPlayers.length > 0 ? oppPlayers[0] : null

      if (loserName) {
        return `Faceoff won by ${winnerName} against ${loserName}`
      }
      return `Faceoff won by ${winnerName}`
    }
    
    // Handle zone entries/exits
    if (event.event_type?.toLowerCase().includes('zone')) {
      // Use only event_detail_2 for zone entry/exit description (not event_type)
      const detail2 = event.event_detail_2 || event.play_detail_2 || ''
      return detail2 ? `${formatDisplayText(detail2)} - ${playerName}` : `${formatDisplayText(event.event_type)} - ${playerName}`
    }

    // Default description - use event_type and event_detail if available
    if (event.event_type) {
      const detail = event.event_detail && event.event_detail !== event.event_type
        ? ` (${formatDisplayText(event.event_detail)})`
        : event.play_detail1
        ? ` (${formatDisplayText(event.play_detail1)})`
        : ''
      return `${formatDisplayText(event.event_type)}${detail}${playerName !== 'Unknown' ? ` - ${playerName}` : ''}`
    }

    return formatDisplayText(event.play_detail1) || formatDisplayText(event.event_detail) || 'Event'
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
              type="button"
              onClick={() => setShowDebug(!showDebug)}
              className="text-xs text-muted-foreground hover:text-foreground px-2 py-1 rounded border border-border bg-background"
              title="Toggle debug view"
            >
              {showDebug ? 'Hide' : 'Show'} Debug
            </button>
            <button
              type="button"
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
            {/* Period Filter */}
            <MultiSelectDropdown
              label="Period"
              options={availablePeriods.map(String)}
              selected={selectedPeriods.map(String)}
              onChange={(vals) => setSelectedPeriods(vals.map(Number))}
              isOpen={showFilterDropdown === 'period'}
              onToggle={() => setShowFilterDropdown(showFilterDropdown === 'period' ? null : 'period')}
              formatOption={(p) => Number(p) > 3 ? `OT${Number(p) - 3}` : `Period ${p}`}
            />
            {/* Event Type Filter */}
            <MultiSelectDropdown
              label="Event Type"
              options={availableEventTypes}
              selected={selectedEventTypes}
              onChange={setSelectedEventTypes}
              isOpen={showFilterDropdown === 'eventType'}
              onToggle={() => setShowFilterDropdown(showFilterDropdown === 'eventType' ? null : 'eventType')}
              formatOption={formatDisplayText}
            />
            {/* Event Detail Filter */}
            <MultiSelectDropdown
              label="Detail"
              options={availableEventDetails}
              selected={selectedEventDetails}
              onChange={setSelectedEventDetails}
              isOpen={showFilterDropdown === 'eventDetail'}
              onToggle={() => setShowFilterDropdown(showFilterDropdown === 'eventDetail' ? null : 'eventDetail')}
              formatOption={formatDisplayText}
            />
            {/* Event Detail 2 Filter */}
            {availableEventDetails2.length > 0 && (
              <MultiSelectDropdown
                label="Detail 2"
                options={availableEventDetails2}
                selected={selectedEventDetails2}
                onChange={setSelectedEventDetails2}
                isOpen={showFilterDropdown === 'eventDetail2'}
                onToggle={() => setShowFilterDropdown(showFilterDropdown === 'eventDetail2' ? null : 'eventDetail2')}
                formatOption={formatDisplayText}
              />
            )}
            {/* Team Filter */}
            <MultiSelectDropdown
              label="Team"
              options={availableTeams}
              selected={selectedTeams}
              onChange={setSelectedTeams}
              isOpen={showFilterDropdown === 'team'}
              onToggle={() => setShowFilterDropdown(showFilterDropdown === 'team' ? null : 'team')}
            />
            {/* Player Filter (grouped by team, with game numbers) */}
            <MultiSelectDropdown
              label="Player"
              options={availablePlayers}
              selected={selectedPlayers}
              onChange={setSelectedPlayers}
              isOpen={showFilterDropdown === 'player'}
              onToggle={() => setShowFilterDropdown(showFilterDropdown === 'player' ? null : 'player')}
              formatOption={formatPlayerOption}
              groups={playerGroups.length > 0 ? playerGroups : undefined}
            />
            {/* Players On Ice Filter */}
            {availablePlayersOnIce.length > 0 && (
              <MultiSelectDropdown
                label="On Ice"
                options={availablePlayersOnIce}
                selected={selectedPlayersOnIce}
                onChange={setSelectedPlayersOnIce}
                isOpen={showFilterDropdown === 'playersOnIce'}
                onToggle={() => setShowFilterDropdown(showFilterDropdown === 'playersOnIce' ? null : 'playersOnIce')}
                formatOption={formatPlayerOption}
              />
            )}
            {/* Role Filter (filters event list + XY rink visualization) */}
            {(
              <div className="flex items-center gap-0.5 border border-border rounded-md overflow-hidden">
                {[
                  { key: null as string | null, label: 'All' },
                  { key: 'event_primary', label: 'Primary' },
                  { key: 'event_support', label: 'Support' },
                  { key: 'opp_primary', label: 'Opp 1' },
                  { key: 'opp_support', label: 'Opp Sup' },
                ].map(({ key, label }) => (
                  <button
                    key={label}
                    type="button"
                    onClick={() => { setRoleFilter(key); setFocusedPlayerId(null) }}
                    className={cn(
                      'px-2 py-1 text-[10px] transition-colors',
                      roleFilter === key
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-background text-muted-foreground hover:text-foreground hover:bg-muted/50'
                    )}
                  >
                    {label}
                  </button>
                ))}
              </div>
            )}
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
      <div className="p-2 sm:p-4 md:p-6 space-y-4 max-h-[600px] overflow-y-auto">
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
                  type="button"
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
                      const linkedKey = eventAny.linked_event_key || eventAny.sequence_key || eventAny.play_key
                      const linkedEvents = linkedKey ? eventsByLinkedKey.get(linkedKey) : undefined

                      return (
                        <div
                          key={eventKey}
                          ref={(el) => {
                            if (el) eventRefs.current.set(eventKey, el)
                          }}
                          onClick={() => {
                            setSelectedEvent(isSelected ? null : eventKey)
                            setDebugEvent(event)
                            if (isSelected) { setFocusedPlayerId(null); setRoleFilter(null) }
                          }}
                          className={cn(
                            'px-2 sm:px-4 py-2 sm:py-3 transition-colors cursor-pointer',
                            getEventColor(event),
                            isSelected && 'ring-2 ring-primary',
                            highlightedEvent === eventKey && 'ring-2 ring-yellow-400 bg-yellow-50 dark:bg-yellow-900/20 animate-pulse'
                          )}
                        >
                          <div className="flex items-start gap-1.5 sm:gap-3">
                            {/* Time */}
                            <div className="flex-shrink-0 w-12 sm:w-20 text-[10px] sm:text-xs font-mono text-muted-foreground">
                              {(() => {
                                const endTime = formatEndTime(event)
                                return endTime ? (
                                  <div>
                                    <div>{time}</div>
                                    <div className="text-[9px] sm:text-[10px] opacity-70">→ {endTime}</div>
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
                              <div className="flex items-center gap-1 sm:gap-2 mb-1 flex-wrap">
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
                                {/* Team Name - hide on mobile, show on sm+ */}
                                {!isGameStateEvent && (
                                  <span
                                    className="hidden sm:inline text-xs font-semibold"
                                    style={(teamData as any)?.primary_color || (teamData as any)?.team_color1 ? {
                                      color: (teamData as any).primary_color || (teamData as any).team_color1
                                    } : {
                                      color: 'inherit'
                                    }}
                                  >
                                    {teamName}
                                  </span>
                                )}
                                <span className="text-[11px] sm:text-xs text-foreground">
                                  {getEventDescription(event, linkedEvents)}
                                </span>
                                {/* Watch Button */}
                                {hasVideo(event) && (
                                  <button
                                    type="button"
                                    onClick={(e) => {
                                      e.stopPropagation()
                                      setSelectedEvent(eventKey)
                                      setPlayingEvent(playingEvent === eventKey ? null : eventKey)
                                    }}
                                    className="ml-auto flex-shrink-0 p-1 sm:p-1.5 rounded-full bg-primary/10 hover:bg-primary/20 text-primary transition-colors"
                                    title="Watch video at this event"
                                  >
                                    <Play className="w-3 h-3" />
                                  </button>
                                )}
                              </div>
                              
                              {/* Additional Details - Expanded View */}
                              {isSelected && (
                                <div className="mt-2 pt-2 border-t border-border/50 text-xs text-muted-foreground space-y-2">
                                  {/* Embedded Video Player */}
                                  {playingEvent === eventKey && (() => {
                                    const embedUrl = getEmbedVideoUrl(event)
                                    return embedUrl ? (
                                      <div className="mb-4">
                                        {/* Camera Switcher */}
                                        {videos.length > 1 && (
                                          <div className="flex gap-1 mb-2">
                                            {videos.map((video, vidIdx) => (
                                              <button
                                                key={video.video_key}
                                                type="button"
                                                onClick={(e) => {
                                                  e.stopPropagation()
                                                  setSelectedVideoIndex(vidIdx)
                                                }}
                                                className={cn(
                                                  'px-3 py-1 text-xs font-medium rounded-md transition-colors',
                                                  vidIdx === selectedVideoIndex
                                                    ? 'bg-primary text-primary-foreground'
                                                    : 'bg-muted hover:bg-muted/80 text-muted-foreground'
                                                )}
                                              >
                                                <Video className="w-3 h-3 inline mr-1" />
                                                {video.video_type.replace('_', ' ')}
                                              </button>
                                            ))}
                                          </div>
                                        )}
                                        <div className="aspect-video w-full rounded-lg overflow-hidden">
                                          <iframe
                                            key={`event-video-${eventKey}-${selectedVideoIndex}`}
                                            src={embedUrl}
                                            title="Event Video"
                                            className="w-full h-full"
                                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                            allowFullScreen
                                          />
                                        </div>
                                        <button
                                          type="button"
                                          onClick={(e) => {
                                            e.stopPropagation()
                                            setPlayingEvent(null)
                                          }}
                                          className="mt-2 text-xs text-muted-foreground hover:text-foreground"
                                        >
                                          Close Video
                                        </button>
                                      </div>
                                    ) : null
                                  })()}

                                  {/* Players (clickable to highlight on rink) */}
                                  {(() => {
                                    const epIds = event.event_player_ids?.split(',').map(id => id.trim()).filter(Boolean) || []
                                    const opIds = event.opp_player_ids?.split(',').map(id => id.trim()).filter(Boolean) || []
                                    const epNames = getEventPlayers(event)
                                    const opNames = getOppPlayers(event)

                                    const renderClickableName = (name: string, playerId: string | undefined, idx: number) => {
                                      const isFocused = playerId && focusedPlayerId === playerId
                                      return (
                                        <button
                                          key={idx}
                                          type="button"
                                          onClick={(e) => {
                                            e.stopPropagation()
                                            if (playerId) {
                                              setFocusedPlayerId(prev => prev === playerId ? null : playerId)
                                            }
                                          }}
                                          className={cn(
                                            "inline text-xs hover:underline transition-colors",
                                            isFocused ? "text-primary font-semibold" : "text-foreground"
                                          )}
                                        >
                                          {name}
                                        </button>
                                      )
                                    }

                                    return (
                                      <div className="grid grid-cols-2 gap-2">
                                        {epNames.length > 0 && (
                                          <div className="text-xs">
                                            <strong>Players: </strong>
                                            {epNames.map((name, idx) => (
                                              <span key={idx}>
                                                {idx > 0 && ', '}
                                                {renderClickableName(name, epIds[idx], idx)}
                                              </span>
                                            ))}
                                          </div>
                                        )}
                                        {opNames.length > 0 && (
                                          <div className="text-xs">
                                            <strong>Opponents: </strong>
                                            {opNames.map((name, idx) => (
                                              <span key={idx}>
                                                {idx > 0 && ', '}
                                                {renderClickableName(name, opIds[idx], idx)}
                                              </span>
                                            ))}
                                          </div>
                                        )}
                                      </div>
                                    )
                                  })()}

                                  {/* Play details for focused player */}
                                  {focusedPlayerId && (() => {
                                    const detailsMap = eventPlayerDetailsMap.get(event.event_id)
                                    if (!detailsMap) return null
                                    // Find the player name for this player_id
                                    const epIds = event.event_player_ids?.split(',').map(id => id.trim()).filter(Boolean) || []
                                    const opIds = event.opp_player_ids?.split(',').map(id => id.trim()).filter(Boolean) || []
                                    const epNames = getEventPlayers(event)
                                    const opNames = getOppPlayers(event)

                                    let focusedName: string | null = null
                                    const epIdx = epIds.indexOf(focusedPlayerId)
                                    const opIdx = opIds.indexOf(focusedPlayerId)
                                    if (epIdx >= 0 && epNames[epIdx]) focusedName = epNames[epIdx]
                                    else if (opIdx >= 0 && opNames[opIdx]) focusedName = opNames[opIdx]

                                    if (!focusedName) return null
                                    const details = detailsMap.get(focusedName)
                                    if (!details) return null
                                    if (!details.play_detail1 && !details.play_detail_2) return null

                                    return (
                                      <div className="px-2 py-1.5 rounded bg-primary/5 border border-primary/20 text-xs">
                                        <div className="font-semibold text-primary mb-0.5">{focusedName} — Details</div>
                                        {details.player_role && (
                                          <div className="text-muted-foreground">Role: {formatDisplayText(details.player_role)}</div>
                                        )}
                                        {details.play_detail1 && (
                                          <div>Detail 1: {formatDisplayText(details.play_detail1)}</div>
                                        )}
                                        {details.play_detail_2 && (
                                          <div>Detail 2: {formatDisplayText(details.play_detail_2)}</div>
                                        )}
                                      </div>
                                    )
                                  })()}

                                  {/* Event Details */}
                                  <div className="grid grid-cols-2 gap-2">
                                    <div><strong>Type:</strong> {formatDisplayText(event.event_type)}</div>
                                    {event.event_detail && <div><strong>Detail:</strong> {formatDisplayText(event.event_detail)}</div>}
                                    {event.event_detail_2 && <div><strong>Detail 2:</strong> {formatDisplayText(event.event_detail_2)}</div>}
                                    {event.play_detail1 && <div><strong>Play Detail:</strong> {formatDisplayText(event.play_detail1)}</div>}
                                    {event.play_detail_2 && <div><strong>Play Detail 2:</strong> {formatDisplayText(event.play_detail_2)}</div>}
                                  </div>

                                  {/* Context */}
                                  <div className="grid grid-cols-2 gap-2">
                                    {event.event_team_zone && <div><strong>Zone:</strong> {formatDisplayText(event.event_team_zone)}</div>}
                                    {event.strength && <div><strong>Strength:</strong> {formatDisplayText(event.strength)}</div>}
                                    {event.duration && event.duration > 0 && <div><strong>Duration:</strong> {event.duration}s</div>}
                                    {event.event_successful !== null && event.event_successful !== undefined && (
                                      <div><strong>Successful:</strong> {event.event_successful ? 'Yes' : 'No'}</div>
                                    )}
                                  </div>

                                  {/* Players On Ice */}
                                  {(() => {
                                    const playersOnIce = getPlayersOnIce(event)
                                    if (!playersOnIce) return null
                                    return (
                                      <div className="pt-2 border-t border-border/30">
                                        <div className="font-semibold mb-1">Players On Ice:</div>
                                        <div className="grid grid-cols-2 gap-2">
                                          <div>
                                            <div className="flex items-center gap-1 mb-1">
                                              <div className="w-2 h-2 rounded-full" style={{ backgroundColor: homeTeamData?.primary_color || homeTeamData?.team_color1 || '#3b82f6' }} />
                                              <span className="text-[10px] font-medium">{homeTeam}</span>
                                            </div>
                                            <div className="text-[10px] text-muted-foreground">
                                              {playersOnIce.home.join(', ') || 'N/A'}
                                            </div>
                                          </div>
                                          <div>
                                            <div className="flex items-center gap-1 mb-1">
                                              <div className="w-2 h-2 rounded-full" style={{ backgroundColor: awayTeamData?.primary_color || awayTeamData?.team_color1 || '#ef4444' }} />
                                              <span className="text-[10px] font-medium">{awayTeam}</span>
                                            </div>
                                            <div className="text-[10px] text-muted-foreground">
                                              {playersOnIce.away.join(', ') || 'N/A'}
                                            </div>
                                          </div>
                                        </div>
                                      </div>
                                    )
                                  })()}

                                  {/* Flags */}
                                  {(event.is_goal === 1 || event.is_save === 1 || event.is_highlight === 1 || event.is_rebound === 1 || event.is_rush === 1) && (
                                    <div className="flex flex-wrap gap-1.5">
                                      {event.is_goal === 1 && <span className="px-2 py-0.5 rounded bg-green-500/20 text-green-600 dark:text-green-400 text-xs">Goal</span>}
                                      {event.is_save === 1 && <span className="px-2 py-0.5 rounded bg-blue-500/20 text-blue-600 dark:text-blue-400 text-xs">Save</span>}
                                      {event.is_highlight === 1 && <span className="px-2 py-0.5 rounded bg-yellow-500/20 text-yellow-600 dark:text-yellow-400 text-xs">Highlight</span>}
                                      {event.is_rebound === 1 && <span className="px-2 py-0.5 rounded bg-orange-500/20 text-orange-600 dark:text-orange-400 text-xs">Rebound</span>}
                                      {event.is_rush === 1 && <span className="px-2 py-0.5 rounded bg-purple-500/20 text-purple-600 dark:text-purple-400 text-xs">Rush</span>}
                                    </div>
                                  )}

                                  {/* Ice Rink Visualization - XY long data or fallback to puck_x/y_start */}
                                  {(() => {
                                    const viz = buildEventVisualization(event)
                                    const homeColor = homeTeamData?.primary_color || homeTeamData?.team_color1 || '#3b82f6'
                                    const awayColor = awayTeamData?.primary_color || awayTeamData?.team_color1 || '#ef4444'

                                    if (viz) {
                                      // Full visualization with players + puck path from XY long tables
                                      if (viz.players.length === 0 && viz.puckPath.length === 0) return null

                                      // Apply role filter to players
                                      const filteredPlayers = roleFilter ? viz.players.filter(p => {
                                        if (!p.role) return true // keep players without role data
                                        if (roleFilter === 'event_primary') return p.role === 'event_player_1'
                                        if (roleFilter === 'opp_primary') return p.role === 'opp_player_1'
                                        if (roleFilter === 'event_support') return p.role.startsWith('event_player_') && p.role !== 'event_player_1'
                                        if (roleFilter === 'opp_support') return p.role.startsWith('opp_player_') && p.role !== 'opp_player_1'
                                        return true
                                      }) : viz.players

                                      return (
                                        <div className="pt-2 border-t border-border/30">
                                          <div className="font-semibold text-xs mb-1">Ice Positions:</div>
                                          <div className="w-full max-w-sm mx-auto">
                                            <IceRinkSVG
                                              players={filteredPlayers}
                                              puckPath={viz.puckPath}
                                              showPuck={true}
                                              showZoneLabels={true}
                                              homeColor={homeColor}
                                              awayColor={awayColor}
                                              homeTeamName={homeTeam}
                                              awayTeamName={awayTeam}
                                              className="border border-border rounded-lg"
                                              focusedPlayerId={focusedPlayerId}
                                              onPlayerClick={(pid) => setFocusedPlayerId(prev => prev === pid ? null : pid)}
                                            />
                                          </div>
                                          {/* Legend */}
                                          <div className="flex items-center justify-center gap-3 mt-1">
                                            <div className="flex items-center gap-1">
                                              <div className="w-2 h-2 rounded-full" style={{ backgroundColor: homeColor }} />
                                              <span className="text-[10px] text-muted-foreground">{homeTeam}</span>
                                            </div>
                                            <div className="flex items-center gap-1">
                                              <div className="w-2 h-2 rounded-full" style={{ backgroundColor: awayColor }} />
                                              <span className="text-[10px] text-muted-foreground">{awayTeam}</span>
                                            </div>
                                            <div className="flex items-center gap-1">
                                              <div className="w-2 h-2 rounded-full bg-gray-900" />
                                              <span className="text-[10px] text-muted-foreground">Puck</span>
                                            </div>
                                          </div>
                                        </div>
                                      )
                                    }

                                    // Fallback: single puck dot from puck_x_start / puck_y_start
                                    const puckX = event.puck_x_start
                                    const puckY = event.puck_y_start
                                    if (puckX === null || puckX === undefined || puckY === null || puckY === undefined) return null
                                    return (
                                      <div className="pt-2 border-t border-border/30">
                                        <div className="font-semibold mb-1 text-xs">Puck Location:</div>
                                        <div className="w-full max-w-sm mx-auto">
                                          <IceRinkSVG
                                            puckPath={[{
                                              x: puckX,
                                              y: puckY,
                                              seq: 1
                                            }]}
                                            showPuck={true}
                                            showZoneLabels={true}
                                            homeColor={homeColor}
                                            awayColor={awayColor}
                                            className="border border-border rounded-lg"
                                          />
                                        </div>
                                        <div className="text-[10px] text-muted-foreground text-center mt-1">
                                          Position: ({Number(puckX).toFixed(1)}, {Number(puckY).toFixed(1)})
                                        </div>
                                      </div>
                                    )
                                  })()}

                                  {/* Net Front View (if net_x/net_y data exists) */}
                                  {event.net_x != null && event.net_y != null && (
                                    <div className="pt-2 border-t border-border/30">
                                      <div className="font-semibold mb-1 text-xs">Net Placement:</div>
                                      <div className="w-full max-w-[180px] mx-auto">
                                        <NetFrontSVG
                                          shotX={event.net_x}
                                          shotY={event.net_y}
                                          isGoal={event.is_goal === 1}
                                        />
                                      </div>
                                    </div>
                                  )}

                                  {/* Video Time / Watch Button */}
                                  {hasVideo(event) && playingEvent !== eventKey && (
                                    <div className="pt-2 border-t border-border/30 flex items-center gap-2">
                                      {event.running_video_time && event.running_video_time > 0 && (
                                        <span><strong>Video Time:</strong> {Math.floor(event.running_video_time / 60)}:{String(Math.floor(event.running_video_time % 60)).padStart(2, '0')}</span>
                                      )}
                                      <button
                                        type="button"
                                        onClick={(e) => {
                                          e.stopPropagation()
                                          setPlayingEvent(eventKey)
                                        }}
                                        className="inline-flex items-center gap-1 px-2 py-1 bg-primary text-primary-foreground rounded text-xs hover:bg-primary/90 transition-colors"
                                      >
                                        <Play className="w-3 h-3" />
                                        Watch
                                      </button>
                                    </div>
                                  )}
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
