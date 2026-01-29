'use client'

import { useState, useMemo, useEffect } from 'react'
import { cn } from '@/lib/utils'
import {
  Clock,
  Filter,
  ChevronDown,
  ChevronUp,
  Users,
  Play,
  Video,
  Check,
  X
} from 'lucide-react'
import { extractYouTubeVideoId, formatYouTubeHighlightUrl } from '@/lib/utils/video'

// Format text: remove underscores, add spaces to CamelCase
function formatDisplayText(text: string | null | undefined): string {
  if (!text) return ''
  return text
    .replace(/_/g, ' ')
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .replace(/([A-Z]+)([A-Z][a-z])/g, '$1 $2')
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
          {groups && groups.length > 0 ? (
            groups.map(group => (
              <div key={group.label}>
                <div className="px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-muted-foreground bg-muted/50 sticky top-0">
                  {group.label}
                </div>
                {group.options.map(renderOption)}
              </div>
            ))
          ) : (
            options.map(renderOption)
          )}

          {options.length === 0 && (!groups || groups.length === 0) && (
            <div className="px-3 py-2 text-xs text-muted-foreground">No options</div>
          )}
        </div>
      )}
    </div>
  )
}

// Team shift data structure from fact_shifts
interface TeamShift {
  shift_id?: string
  shift_key?: string
  game_id?: number
  shift_index?: number
  period?: number
  shift_start_type?: string
  shift_stop_type?: string
  shift_start_min?: number
  shift_start_sec?: number
  shift_end_min?: number
  shift_end_sec?: number
  shift_start_total_seconds?: number
  shift_end_total_seconds?: number
  shift_duration?: number
  // Home team players
  home_team?: string
  home_team_id?: string
  home_forward_1?: number | string
  home_forward_2?: number | string
  home_forward_3?: number | string
  home_defense_1?: number | string
  home_defense_2?: number | string
  home_xtra?: number | string
  home_goalie?: number | string
  home_team_strength?: number
  // Away team players
  away_team?: string
  away_team_id?: string
  away_forward_1?: number | string
  away_forward_2?: number | string
  away_forward_3?: number | string
  away_defense_1?: number | string
  away_defense_2?: number | string
  away_xtra?: number | string
  away_goalie?: number | string
  away_team_strength?: number
  // Situation
  situation?: string
  strength?: string
  running_video_time?: number
  // Stats
  cf?: number
  ca?: number
  sf?: number
  sa?: number
  // Zone info
  start_zone?: string
  end_zone?: string
  start_zone_id?: string
  end_zone_id?: string
}

interface GameVideo {
  video_key: string
  video_type: string
  video_url: string
}

interface ShiftEvent {
  event_id: string
  event_type?: string
  event_detail?: string
  event_detail_2?: string
  event_player_1?: string
  player_team?: string
  shift_id?: number
  running_video_time?: number
}

interface ShiftsTimelineProps {
  shifts: TeamShift[]
  homeTeam?: string
  awayTeam?: string
  homeTeamId?: string
  awayTeamId?: string
  homeColor?: string
  awayColor?: string
  jerseyToPlayerMap?: Map<string, { player_name: string; team_id: string }>
  videos?: GameVideo[]
  events?: ShiftEvent[]
  onEventClick?: (eventId: string) => void
}

// Highlight timing
const HIGHLIGHT_PRE_OFFSET = 5
const HIGHLIGHT_POST_OFFSET = 15

export function ShiftsTimeline({
  shifts,
  homeTeam = 'Home',
  awayTeam = 'Away',
  homeTeamId,
  awayTeamId,
  homeColor = '#3b82f6',
  awayColor = '#ef4444',
  jerseyToPlayerMap = new Map(),
  videos = [],
  events = [],
  onEventClick,
}: ShiftsTimelineProps) {
  const [expandedPeriods, setExpandedPeriods] = useState<Set<number>>(new Set([1]))
  const [selectedShift, setSelectedShift] = useState<string | null>(null)
  const [playingShift, setPlayingShift] = useState<string | null>(null)
  const [playingEventId, setPlayingEventId] = useState<string | null>(null)
  const [eventVideoTime, setEventVideoTime] = useState<number | null>(null)
  const [selectedVideoIndex, setSelectedVideoIndex] = useState(0)

  // Multi-select Filters
  const [selectedPeriods, setSelectedPeriods] = useState<number[]>([])
  const [selectedPlayers, setSelectedPlayers] = useState<string[]>([])
  const [selectedStrengths, setSelectedStrengths] = useState<string[]>([])
  const [selectedStartTypes, setSelectedStartTypes] = useState<string[]>([])
  const [selectedEndTypes, setSelectedEndTypes] = useState<string[]>([])
  const [showFilterDropdown, setShowFilterDropdown] = useState<string | null>(null)

  // Close filter dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = () => setShowFilterDropdown(null)
    if (showFilterDropdown) {
      document.addEventListener('click', handleClickOutside)
      return () => document.removeEventListener('click', handleClickOutside)
    }
  }, [showFilterDropdown])

  // Get current video
  const currentVideo = videos && videos.length > 0 ? videos[selectedVideoIndex] : null

  // Debug: Log video availability
  if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
    const shiftsWithVideoTime = shifts.filter(s => s.running_video_time !== undefined && s.running_video_time !== null).length
    console.log('[ShiftsTimeline] Videos:', videos?.length || 0, 'Current video:', currentVideo?.video_url, 'Shifts with video time:', shiftsWithVideoTime, '/', shifts.length)
  }

  // Get player name from jersey number
  const getPlayerName = (jerseyNum: number | string | null | undefined): string => {
    if (!jerseyNum || jerseyNum === 0 || jerseyNum === '0') return ''
    const jersey = String(Math.floor(Number(jerseyNum)))
    const player = jerseyToPlayerMap.get(jersey)
    return player?.player_name || `#${jersey}`
  }

  // Get jersey number display
  const getJerseyDisplay = (jerseyNum: number | string | null | undefined): string => {
    if (!jerseyNum || jerseyNum === 0 || jerseyNum === '0') return ''
    return `#${Math.floor(Number(jerseyNum))}`
  }

  // Get all player IDs from a shift for a team
  const getTeamPlayerIds = (shift: TeamShift, team: 'home' | 'away'): (number | string)[] => {
    const players: (number | string)[] = []
    if (team === 'home') {
      if (shift.home_forward_1) players.push(shift.home_forward_1)
      if (shift.home_forward_2) players.push(shift.home_forward_2)
      if (shift.home_forward_3) players.push(shift.home_forward_3)
      if (shift.home_defense_1) players.push(shift.home_defense_1)
      if (shift.home_defense_2) players.push(shift.home_defense_2)
      if (shift.home_xtra) players.push(shift.home_xtra)
    } else {
      if (shift.away_forward_1) players.push(shift.away_forward_1)
      if (shift.away_forward_2) players.push(shift.away_forward_2)
      if (shift.away_forward_3) players.push(shift.away_forward_3)
      if (shift.away_defense_1) players.push(shift.away_defense_1)
      if (shift.away_defense_2) players.push(shift.away_defense_2)
      if (shift.away_xtra) players.push(shift.away_xtra)
    }
    return players.filter(p => p && p !== 0 && p !== '0')
  }

  // Available periods
  const availablePeriods = useMemo(() => {
    const periods = new Set<number>()
    shifts.forEach(shift => {
      if (shift.period && shift.period > 0) periods.add(shift.period)
    })
    return Array.from(periods).sort((a, b) => a - b)
  }, [shifts])

  // Available players (all players across all shifts) with team info
  const availablePlayers = useMemo(() => {
    const playerNames = new Set<string>()
    shifts.forEach(shift => {
      const homePlayerIds = getTeamPlayerIds(shift, 'home')
      const awayPlayerIds = getTeamPlayerIds(shift, 'away')

      homePlayerIds.forEach(id => {
        const name = getPlayerName(id)
        if (name && !name.startsWith('#')) playerNames.add(name)
      })
      awayPlayerIds.forEach(id => {
        const name = getPlayerName(id)
        if (name && !name.startsWith('#')) playerNames.add(name)
      })
    })
    return Array.from(playerNames).sort()
  }, [shifts, jerseyToPlayerMap])

  // Build name → jersey number map from jerseyToPlayerMap
  const nameToJerseyMap = useMemo(() => {
    const map = new Map<string, string>()
    jerseyToPlayerMap.forEach((info, jersey) => {
      if (info.player_name) map.set(info.player_name, jersey)
    })
    return map
  }, [jerseyToPlayerMap])

  // Build name → team_id map from jerseyToPlayerMap
  const nameToTeamMap = useMemo(() => {
    const map = new Map<string, string>()
    jerseyToPlayerMap.forEach((info) => {
      if (info.player_name && info.team_id) map.set(info.player_name, info.team_id)
    })
    return map
  }, [jerseyToPlayerMap])

  // Format player name with jersey number
  const formatPlayerOption = (name: string) => {
    const jersey = nameToJerseyMap.get(name)
    return jersey ? `#${jersey} ${name}` : name
  }

  // Group available players by team (away first, then home - standard hockey display)
  const playerGroups = useMemo((): OptionGroup[] => {
    const awayPlayers: string[] = []
    const homePlayers: string[] = []
    const otherPlayers: string[] = []

    availablePlayers.forEach(name => {
      const teamId = nameToTeamMap.get(name)
      if (teamId === awayTeamId) {
        awayPlayers.push(name)
      } else if (teamId === homeTeamId) {
        homePlayers.push(name)
      } else {
        otherPlayers.push(name)
      }
    })

    const groups: OptionGroup[] = []
    if (awayPlayers.length > 0) groups.push({ label: awayTeam, options: awayPlayers })
    if (homePlayers.length > 0) groups.push({ label: homeTeam, options: homePlayers })
    if (otherPlayers.length > 0) groups.push({ label: 'Other', options: otherPlayers })
    return groups
  }, [availablePlayers, nameToTeamMap, homeTeamId, awayTeamId, homeTeam, awayTeam])

  // Available strengths
  const availableStrengths = useMemo(() => {
    const strengths = new Set<string>()
    shifts.forEach(shift => {
      if (shift.strength) strengths.add(shift.strength)
      if (shift.situation) strengths.add(shift.situation)
    })
    return Array.from(strengths).sort()
  }, [shifts])

  // Available start types
  const availableStartTypes = useMemo(() => {
    const types = new Set<string>()
    shifts.forEach(shift => {
      if (shift.shift_start_type) types.add(shift.shift_start_type)
    })
    return Array.from(types).sort()
  }, [shifts])

  // Available end types
  const availableEndTypes = useMemo(() => {
    const types = new Set<string>()
    shifts.forEach(shift => {
      if (shift.shift_stop_type) types.add(shift.shift_stop_type)
    })
    return Array.from(types).sort()
  }, [shifts])

  // Check if a player in the list is in a shift
  const playerInShiftMulti = (shift: TeamShift, playerNames: string[]): boolean => {
    if (playerNames.length === 0) return true
    const homePlayerIds = getTeamPlayerIds(shift, 'home')
    const awayPlayerIds = getTeamPlayerIds(shift, 'away')
    const allPlayerIds = [...homePlayerIds, ...awayPlayerIds]

    return allPlayerIds.some(id => {
      const name = getPlayerName(id)
      return playerNames.includes(name)
    })
  }

  // Filter and group shifts by period
  const shiftsByPeriod = useMemo(() => {
    let filtered = shifts

    // Apply period filter (multi-select)
    if (selectedPeriods.length > 0) {
      filtered = filtered.filter(s => s.period && selectedPeriods.includes(s.period))
    }

    // Apply player filter (multi-select)
    if (selectedPlayers.length > 0) {
      filtered = filtered.filter(s => playerInShiftMulti(s, selectedPlayers))
    }

    // Apply strength filter (multi-select)
    if (selectedStrengths.length > 0) {
      filtered = filtered.filter(s =>
        (s.strength && selectedStrengths.includes(s.strength)) ||
        (s.situation && selectedStrengths.includes(s.situation))
      )
    }

    // Apply start type filter (multi-select)
    if (selectedStartTypes.length > 0) {
      filtered = filtered.filter(s => s.shift_start_type && selectedStartTypes.includes(s.shift_start_type))
    }

    // Apply end type filter (multi-select)
    if (selectedEndTypes.length > 0) {
      filtered = filtered.filter(s => s.shift_stop_type && selectedEndTypes.includes(s.shift_stop_type))
    }

    // Sort by period ascending, then by start time descending (hockey countdown: 20:00, 19:00, etc.)
    // shift_start_total_seconds is remaining time in seconds, so higher = earlier in period
    const sorted = [...filtered].sort((a, b) => {
      const periodA = a.period || 1
      const periodB = b.period || 1
      if (periodA !== periodB) return periodA - periodB
      // Sort descending by remaining time (higher time first = hockey order)
      const timeA = a.shift_start_total_seconds || 0
      const timeB = b.shift_start_total_seconds || 0
      return timeB - timeA
    })

    // Group by period
    const grouped = new Map<number, TeamShift[]>()
    sorted.forEach(shift => {
      const period = shift.period || 1
      if (!grouped.has(period)) {
        grouped.set(period, [])
      }
      grouped.get(period)!.push(shift)
    })

    return grouped
  }, [shifts, selectedPeriods, selectedPlayers, selectedStrengths, selectedStartTypes, selectedEndTypes])

  // Format time from shift data
  const formatTime = (shift: TeamShift, type: 'start' | 'end'): string => {
    if (type === 'start') {
      if (typeof shift.shift_start_min === 'number' && typeof shift.shift_start_sec === 'number') {
        return `${Math.floor(shift.shift_start_min)}:${String(Math.floor(shift.shift_start_sec)).padStart(2, '0')}`
      }
    } else {
      if (typeof shift.shift_end_min === 'number' && typeof shift.shift_end_sec === 'number') {
        return `${Math.floor(shift.shift_end_min)}:${String(Math.floor(shift.shift_end_sec)).padStart(2, '0')}`
      }
    }
    return '--:--'
  }

  // Format duration
  const formatDuration = (shift: TeamShift): string => {
    let duration = shift.shift_duration || 0
    if (!duration && shift.shift_start_total_seconds !== undefined && shift.shift_end_total_seconds !== undefined) {
      duration = shift.shift_end_total_seconds - shift.shift_start_total_seconds
    }
    if (duration <= 0) return '0:00'
    const min = Math.floor(Math.abs(duration) / 60)
    const sec = Math.floor(Math.abs(duration) % 60)
    return `${min}:${String(sec).padStart(2, '0')}`
  }

  // Get strength display
  const getStrengthDisplay = (shift: TeamShift): string => {
    const homeStrength = shift.home_team_strength || 5
    const awayStrength = shift.away_team_strength || 5
    return `${homeStrength}v${awayStrength}`
  }

  // Get events for a specific shift
  const getShiftEvents = (shift: TeamShift): ShiftEvent[] => {
    if (!events || events.length === 0) return []
    const shiftId = shift.shift_id || shift.shift_index
    if (!shiftId) return []
    return events.filter(e => e.shift_id === shiftId)
  }

  // Get team color for an event
  const getEventTeamColor = (event: ShiftEvent): string => {
    if (event.player_team === homeTeam) return homeColor
    if (event.player_team === awayTeam) return awayColor
    return '#64748b' // muted fallback
  }

  // Format zone with team name context
  const formatZoneWithTeam = (zone: string | undefined): string => {
    if (!zone) return ''
    const zoneLower = zone.toLowerCase()

    // Check if it already contains a team name or is descriptive
    if (zoneLower.includes('offensive') || zoneLower.includes('off') || zoneLower.includes('ozone')) {
      return `${homeTeam} Offensive Zone`
    }
    if (zoneLower.includes('defensive') || zoneLower.includes('def') || zoneLower.includes('dzone')) {
      return `${homeTeam} Defensive Zone`
    }
    if (zoneLower.includes('neutral') || zoneLower.includes('nzone')) {
      return 'Neutral Zone'
    }

    // If zone has a team indicator in the data, use it
    return formatDisplayText(zone)
  }

  // Check if video available
  const hasVideo = (shift: TeamShift): boolean => {
    return currentVideo !== null && shift.running_video_time !== undefined && shift.running_video_time !== null
  }

  // Get embedded video URL for shift (no end time - let video play past shift)
  const getEmbedVideoUrl = (shift: TeamShift): string | null => {
    if (!currentVideo) return null
    if (shift.running_video_time === undefined || shift.running_video_time === null) return null
    const videoId = extractYouTubeVideoId(currentVideo.video_url)
    if (!videoId) return null
    const startTime = Math.max(0, shift.running_video_time - HIGHLIGHT_PRE_OFFSET)
    // No end time - video plays continuously from start point
    return formatYouTubeHighlightUrl(videoId, startTime, 0, true)
  }

  // Get embedded video URL for event (no end time - let video play past event)
  const getEventEmbedVideoUrl = (event: ShiftEvent): string | null => {
    if (!currentVideo) return null
    if (event.running_video_time === undefined || event.running_video_time === null) return null
    const videoId = extractYouTubeVideoId(currentVideo.video_url)
    if (!videoId) return null
    const startTime = Math.max(0, event.running_video_time - HIGHLIGHT_PRE_OFFSET)
    // No end time - video plays continuously from start point
    return formatYouTubeHighlightUrl(videoId, startTime, 0, true)
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

  const periods = Array.from(shiftsByPeriod.keys()).sort((a, b) => a - b)

  if (shifts.length === 0) {
    return (
      <div className="text-center py-8">
        <Clock className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
        <p className="text-muted-foreground">No shift data available for this game</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex items-center gap-2 flex-wrap">
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

        {/* Player Filter */}
        {availablePlayers.length > 0 && (
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
        )}

        {/* Strength Filter */}
        {availableStrengths.length > 0 && (
          <MultiSelectDropdown
            label="Situation"
            options={availableStrengths}
            selected={selectedStrengths}
            onChange={setSelectedStrengths}
            isOpen={showFilterDropdown === 'strength'}
            onToggle={() => setShowFilterDropdown(showFilterDropdown === 'strength' ? null : 'strength')}
            formatOption={formatDisplayText}
          />
        )}

        {/* Start Type Filter */}
        {availableStartTypes.length > 0 && (
          <MultiSelectDropdown
            label="Start Type"
            options={availableStartTypes}
            selected={selectedStartTypes}
            onChange={setSelectedStartTypes}
            isOpen={showFilterDropdown === 'startType'}
            onToggle={() => setShowFilterDropdown(showFilterDropdown === 'startType' ? null : 'startType')}
            formatOption={formatDisplayText}
          />
        )}

        {/* End Type Filter */}
        {availableEndTypes.length > 0 && (
          <MultiSelectDropdown
            label="End Type"
            options={availableEndTypes}
            selected={selectedEndTypes}
            onChange={setSelectedEndTypes}
            isOpen={showFilterDropdown === 'endType'}
            onToggle={() => setShowFilterDropdown(showFilterDropdown === 'endType' ? null : 'endType')}
            formatOption={formatDisplayText}
          />
        )}

        <span className="text-xs text-muted-foreground ml-auto flex items-center gap-2">
          {Array.from(shiftsByPeriod.values()).reduce((acc, s) => acc + s.length, 0)} shifts
          {videos && videos.length > 0 && (
            <span className="flex items-center gap-1 text-green-600 dark:text-green-400">
              <Video className="w-3 h-3" />
              {videos.length} video{videos.length > 1 ? 's' : ''}
            </span>
          )}
        </span>
      </div>

      {/* Timeline */}
      <div className="space-y-3 max-h-[600px] overflow-y-auto">
        {periods.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            No shifts match the selected filters
          </div>
        ) : (
          periods.map((period) => {
            const periodShifts = shiftsByPeriod.get(period) || []
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
                      ({periodShifts.length} shifts)
                    </span>
                  </div>
                </button>

                {/* Period Shifts */}
                {isExpanded && (
                  <div className="divide-y divide-border">
                    {periodShifts.map((shift, idx) => {
                      const shiftKey = shift.shift_key || shift.shift_id || `${period}-${idx}`
                      const isSelected = selectedShift === shiftKey
                      const isPlaying = playingShift === shiftKey
                      const embedUrl = isPlaying ? getEmbedVideoUrl(shift) : null

                      // Get player names for display
                      const homePlayerIds = getTeamPlayerIds(shift, 'home')
                      const awayPlayerIds = getTeamPlayerIds(shift, 'away')

                      return (
                        <div
                          key={shiftKey}
                          onClick={() => setSelectedShift(isSelected ? null : shiftKey)}
                          className={cn(
                            'px-4 py-3 transition-colors cursor-pointer hover:bg-muted/30',
                            isSelected && 'bg-muted/20'
                          )}
                        >
                          {/* Main Row */}
                          <div className="flex items-center gap-2 flex-wrap">
                            {/* Time Range */}
                            <div className="flex-shrink-0 w-16 text-xs font-mono">
                              <div className="text-foreground font-semibold">{formatTime(shift, 'start')}</div>
                              <div className="text-muted-foreground text-[10px]">→ {formatTime(shift, 'end')}</div>
                            </div>

                            {/* Duration */}
                            <div className="flex-shrink-0 w-10 text-xs font-mono text-muted-foreground">
                              {formatDuration(shift)}
                            </div>

                            {/* Strength Badge */}
                            <div className={cn(
                              'flex-shrink-0 px-1.5 py-0.5 rounded text-[10px] font-medium',
                              shift.situation === 'PP' || shift.strength === 'PP'
                                ? 'bg-yellow-500/20 text-yellow-600 dark:text-yellow-400'
                                : shift.situation === 'PK' || shift.strength === 'PK'
                                ? 'bg-red-500/20 text-red-600 dark:text-red-400'
                                : 'bg-muted text-muted-foreground'
                            )}>
                              {getStrengthDisplay(shift)}
                            </div>

                            {/* Shift Start Type → End Type */}
                            <div className="flex-1 min-w-0 text-xs text-foreground">
                              {formatDisplayText(shift.shift_start_type) || 'On The Fly'} → {shift.shift_stop_type && shift.shift_stop_type !== '-' ? formatDisplayText(shift.shift_stop_type) : 'On The Fly'}
                            </div>

                            {/* Watch Button */}
                            {hasVideo(shift) && (
                              <button
                                type="button"
                                onClick={(e) => {
                                  e.stopPropagation()
                                  setSelectedShift(shiftKey)
                                  setPlayingShift(isPlaying ? null : shiftKey)
                                }}
                                className="flex-shrink-0 p-1.5 rounded-full bg-primary/10 hover:bg-primary/20 text-primary transition-colors"
                                title="Watch shift"
                              >
                                <Play className="w-3 h-3" />
                              </button>
                            )}

                            {/* Expand Icon */}
                            <ChevronDown className={cn(
                              'w-4 h-4 text-muted-foreground transition-transform flex-shrink-0',
                              isSelected && 'rotate-180'
                            )} />
                          </div>

                          {/* Expanded Details */}
                          {isSelected && (
                            <div className="mt-3 pt-3 border-t border-border/50">
                              {/* Video Player */}
                              {isPlaying && embedUrl && (
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
                                      key={`shift-video-${shiftKey}-${selectedVideoIndex}`}
                                      src={embedUrl}
                                      title="Shift Video"
                                      className="w-full h-full"
                                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                      allowFullScreen
                                    />
                                  </div>
                                  <button
                                    type="button"
                                    onClick={(e) => {
                                      e.stopPropagation()
                                      setPlayingShift(null)
                                    }}
                                    className="mt-2 text-xs text-muted-foreground hover:text-foreground"
                                  >
                                    Close Video
                                  </button>
                                </div>
                              )}

                              {/* On-Ice Players */}
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {/* Home Team */}
                                <div className="space-y-2">
                                  <div className="flex items-center gap-2">
                                    <div className="w-3 h-3 rounded" style={{ backgroundColor: homeColor }} />
                                    <span className="text-xs font-semibold">{homeTeam}</span>
                                    <span className="text-xs text-muted-foreground">({shift.home_team_strength || 5} skaters)</span>
                                  </div>
                                  <div className="flex flex-wrap gap-1">
                                    {homePlayerIds.map((playerId, pIdx) => {
                                      const name = getPlayerName(playerId)
                                      const isFiltered = selectedPlayers.length > 0 && selectedPlayers.includes(name)
                                      return (
                                        <span
                                          key={pIdx}
                                          className={cn(
                                            'px-2 py-0.5 rounded text-xs',
                                            isFiltered
                                              ? 'bg-primary/20 text-primary font-medium'
                                              : 'bg-muted text-foreground'
                                          )}
                                        >
                                          {name}
                                        </span>
                                      )
                                    })}
                                    {shift.home_goalie && (
                                      <span className="px-2 py-0.5 rounded text-xs bg-blue-500/20 text-blue-600 dark:text-blue-400">
                                        G: {getPlayerName(shift.home_goalie)}
                                      </span>
                                    )}
                                  </div>
                                </div>

                                {/* Away Team */}
                                <div className="space-y-2">
                                  <div className="flex items-center gap-2">
                                    <div className="w-3 h-3 rounded" style={{ backgroundColor: awayColor }} />
                                    <span className="text-xs font-semibold">{awayTeam}</span>
                                    <span className="text-xs text-muted-foreground">({shift.away_team_strength || 5} skaters)</span>
                                  </div>
                                  <div className="flex flex-wrap gap-1">
                                    {awayPlayerIds.map((playerId, pIdx) => {
                                      const name = getPlayerName(playerId)
                                      const isFiltered = selectedPlayers.length > 0 && selectedPlayers.includes(name)
                                      return (
                                        <span
                                          key={pIdx}
                                          className={cn(
                                            'px-2 py-0.5 rounded text-xs',
                                            isFiltered
                                              ? 'bg-primary/20 text-primary font-medium'
                                              : 'bg-muted text-foreground'
                                          )}
                                        >
                                          {name}
                                        </span>
                                      )
                                    })}
                                    {shift.away_goalie && (
                                      <span className="px-2 py-0.5 rounded text-xs bg-red-500/20 text-red-600 dark:text-red-400">
                                        G: {getPlayerName(shift.away_goalie)}
                                      </span>
                                    )}
                                  </div>
                                </div>
                              </div>

                              {/* Zone Information */}
                              {(shift.start_zone || shift.end_zone) && (
                                <div className="mt-3 pt-3 border-t border-border/30 text-xs space-y-1">
                                  {shift.start_zone && (
                                    <div><strong>Start Zone:</strong> {formatZoneWithTeam(shift.start_zone)}</div>
                                  )}
                                  {shift.end_zone && (
                                    <div><strong>End Zone:</strong> {formatZoneWithTeam(shift.end_zone)}</div>
                                  )}
                                </div>
                              )}

                              {/* Events Chain */}
                              {(() => {
                                const shiftEvents = getShiftEvents(shift)
                                return shiftEvents.length > 0 ? (
                                  <div className="mt-3 pt-3 border-t border-border/30 text-xs">
                                    <div className="font-semibold mb-2">Events ({shiftEvents.length}):</div>
                                    <div className="flex flex-wrap items-center gap-1">
                                      {shiftEvents.map((event, idx) => (
                                        <span key={event.event_id} className="flex items-center">
                                          <button
                                            type="button"
                                            onClick={(e) => {
                                              e.stopPropagation()
                                              // If event has video time, play it
                                              if (currentVideo && event.running_video_time !== undefined && event.running_video_time !== null) {
                                                setPlayingEventId(event.event_id)
                                                setEventVideoTime(event.running_video_time)
                                                setPlayingShift(null) // Stop shift video if playing
                                              }
                                              onEventClick?.(event.event_id)
                                            }}
                                            className={cn(
                                              'px-1.5 py-0.5 rounded text-[10px] font-medium hover:opacity-80 transition-opacity',
                                              event.running_video_time !== undefined && event.running_video_time !== null && currentVideo && 'cursor-pointer'
                                            )}
                                            style={{
                                              backgroundColor: `${getEventTeamColor(event)}20`,
                                              color: getEventTeamColor(event)
                                            }}
                                            title={[
                                              event.event_player_1,
                                              formatDisplayText(event.event_detail),
                                              formatDisplayText(event.event_detail_2),
                                              event.running_video_time !== undefined ? '(click to watch)' : ''
                                            ].filter(Boolean).join(' - ')}
                                          >
                                            {event.event_player_1 ? `${event.event_player_1}: ` : ''}
                                            {formatDisplayText(event.event_detail || event.event_type)}
                                            {event.running_video_time !== undefined && currentVideo && (
                                              <Play className="w-2 h-2 inline ml-0.5" />
                                            )}
                                          </button>
                                          {idx < shiftEvents.length - 1 && (
                                            <span className="mx-0.5 text-muted-foreground">→</span>
                                          )}
                                        </span>
                                      ))}
                                    </div>

                                    {/* Event Video Player */}
                                    {playingEventId && eventVideoTime !== null && (() => {
                                      const playingEvent = shiftEvents.find(e => e.event_id === playingEventId)
                                      if (!playingEvent || !currentVideo) return null
                                      const embedUrl = getEventEmbedVideoUrl(playingEvent)
                                      if (!embedUrl) return null
                                      return (
                                        <div className="mt-3">
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
                                                    'px-2 py-1 text-[10px] font-medium rounded transition-colors',
                                                    vidIdx === selectedVideoIndex
                                                      ? 'bg-primary text-primary-foreground'
                                                      : 'bg-muted hover:bg-muted/80 text-muted-foreground'
                                                  )}
                                                >
                                                  {video.video_type.replace('_', ' ')}
                                                </button>
                                              ))}
                                            </div>
                                          )}
                                          <div className="aspect-video w-full rounded-lg overflow-hidden">
                                            <iframe
                                              key={`event-video-${playingEventId}-${selectedVideoIndex}`}
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
                                              setPlayingEventId(null)
                                              setEventVideoTime(null)
                                            }}
                                            className="mt-2 text-[10px] text-muted-foreground hover:text-foreground"
                                          >
                                            Close Video
                                          </button>
                                        </div>
                                      )
                                    })()}
                                  </div>
                                ) : null
                              })()}

                              {/* Shift Stats - by team */}
                              {(shift.cf !== undefined || shift.sf !== undefined) && (
                                <div className="mt-3 pt-3 border-t border-border/30 grid grid-cols-2 gap-4 text-xs">
                                  {/* Home team stats */}
                                  <div className="space-y-1">
                                    <div className="flex items-center gap-1 font-semibold">
                                      <div className="w-2 h-2 rounded-full" style={{ backgroundColor: homeColor }} />
                                      {homeTeam}
                                    </div>
                                    <div className="grid grid-cols-2 gap-2">
                                      {shift.sf !== undefined && (
                                        <div>
                                          <div className="text-muted-foreground">Shots</div>
                                          <div className="font-semibold">{shift.sf}</div>
                                        </div>
                                      )}
                                      {shift.cf !== undefined && (
                                        <div>
                                          <div className="text-muted-foreground">Corsi</div>
                                          <div className="font-semibold">{shift.cf}</div>
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                  {/* Away team stats */}
                                  <div className="space-y-1">
                                    <div className="flex items-center gap-1 font-semibold">
                                      <div className="w-2 h-2 rounded-full" style={{ backgroundColor: awayColor }} />
                                      {awayTeam}
                                    </div>
                                    <div className="grid grid-cols-2 gap-2">
                                      {shift.sa !== undefined && (
                                        <div>
                                          <div className="text-muted-foreground">Shots</div>
                                          <div className="font-semibold">{shift.sa}</div>
                                        </div>
                                      )}
                                      {shift.ca !== undefined && (
                                        <div>
                                          <div className="text-muted-foreground">Corsi</div>
                                          <div className="font-semibold">{shift.ca}</div>
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                </div>
                              )}

                              {/* Watch Button (if not already playing) */}
                              {hasVideo(shift) && !isPlaying && (
                                <div className="mt-3 pt-3 border-t border-border/30">
                                  <button
                                    type="button"
                                    onClick={(e) => {
                                      e.stopPropagation()
                                      setPlayingShift(shiftKey)
                                    }}
                                    className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-primary text-primary-foreground rounded-lg text-xs font-medium hover:bg-primary/90 transition-colors"
                                  >
                                    <Play className="w-3.5 h-3.5" />
                                    Watch Shift
                                  </button>
                                </div>
                              )}
                            </div>
                          )}
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
