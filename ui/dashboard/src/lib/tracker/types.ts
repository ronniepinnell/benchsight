/**
 * BenchSight Game Tracker - TypeScript Types
 * 
 * Extracted from tracker_index_v23.5.html for Next.js rebuild
 */

// ============================================================
// EVENT TYPES
// ============================================================

export type EventType = 
  | 'Faceoff'
  | 'Shot'
  | 'Pass'
  | 'Goal'
  | 'Turnover'
  | 'Zone_Entry_Exit'
  | 'Penalty'
  | 'Stoppage'
  | 'Possession'
  | 'Save'
  | 'Rebound'
  | 'DeadIce'
  | 'Play'
  | 'Intermission'
  | 'Clockstop'
  | 'Timeout'

export type Zone = 'o' | 'n' | 'd' // Offensive, Neutral, Defensive
export type Team = 'home' | 'away'
export type Period = 1 | 2 | 3 | 4 // 4 = OT
export type PeriodString = '1' | '2' | '3' | 'OT'

// ============================================================
// PLAYER
// ============================================================

export interface Player {
  num: string
  name: string
  team: Team
  role?: PlayerRole
  position?: PlayerPosition
  xy?: XYCoordinate[]
}

export type PlayerRole = 
  | 'event_team_player_1'  // E1 - Primary player
  | 'event_team_player_2'  // E2 - Secondary
  | 'event_team_player_3'  // E3 - Third
  | 'opponent_player_1'    // O1 - Primary opponent
  | 'opponent_player_2'    // O2 - Secondary opponent
  | 'opponent_player_3'    // O3 - Third opponent

export type PlayerPosition = 'F' | 'D' | 'G' // Forward, Defense, Goalie

// ============================================================
// COORDINATES
// ============================================================

export interface XYCoordinate {
  x: number
  y: number
}

// ============================================================
// EVENT
// ============================================================

export interface Event {
  // Identity
  idx?: number // Event index (for ordering)
  eventId?: string // Unique event ID (e.g., 'EV1896901058')
  
  // Time
  period: Period
  start_time: string // Format: "MM:SS" (e.g., "12:30")
  end_time?: string // Format: "MM:SS"
  
  // Event details
  type: EventType
  detail1?: string // Primary detail (e.g., 'Shot_OnNetSaved')
  detail2?: string // Secondary detail (e.g., 'Shot-Wrist')
  
  // Context
  team: Team
  zone?: Zone
  success?: boolean // Success indicator
  strength?: string // Game strength (e.g., '5v5', '5v4')
  
  // Players
  players: Player[]
  
  // Coordinates
  puckXY?: XYCoordinate[] // Puck trajectory points
  netXY?: XYCoordinate // Net target (for shots)
  
  // Metadata
  isHighlight?: boolean
  videoUrl?: string // v23.7: Individual YouTube link for this highlight
  linkedEventIdx?: number // Linked event index (for sequences like Shot->Save)
  assistToGoalIdx?: number // v23.8: Assist to goal index (for Pass->Goal assists, separate from linked events)
  notes?: string
  
  // Video sync
  videoTime?: number // Video timestamp (seconds)
}

// ============================================================
// SHIFT
// ============================================================

export interface Shift {
  // Identity
  idx?: number // Shift index
  shiftId?: string // Unique shift ID
  
  // Time
  period: Period
  start_time: string // Format: "MM:SS"
  end_time: string // Format: "MM:SS"
  start_type?: string // How shift started (e.g., 'OnTheFly')
  stop_type?: string // How shift ended (e.g., 'OnTheFly')
  
  // Context
  strength?: string // Game strength (e.g., '5v5')
  stoppageTime?: number // Stoppage time in seconds
  
  // Players on ice
  home: Lineup
  away: Lineup
  
  // Metadata
  videoTime?: number // Video timestamp (seconds)
}

export interface Lineup {
  F1: Player | null // Forward 1
  F2: Player | null // Forward 2
  F3: Player | null // Forward 3
  D1: Player | null // Defense 1
  D2: Player | null // Defense 2
  G: Player | null  // Goalie
  X: Player | null  // Extra
}

// ============================================================
// GAME STATE
// ============================================================

export interface GameState {
  // Game info
  gameId: number | null
  homeTeam: string
  awayTeam: string
  homeColor: string
  awayColor: string
  homeLogo?: string | null
  awayLogo?: string | null
  
  // Period
  period: Period
  periodLengths: PeriodLengths
  periodLength: number // Legacy - use getPeriodLength() instead
  homeAttacksRightP1: boolean // Which end home attacks in P1
  
  // Clock
  clock: string // Format: "MM:SS"
  score: {
    home: number
    away: number
  }
  
  // Rosters
  rosters: {
    home: Player[]
    away: Player[]
  }
  
  // Slots (current lineups)
  slots: {
    home: Lineup
    away: Lineup
  }
  
  // Data
  events: Event[]
  shifts: Shift[]
  evtIdx: number // Next event index
  shiftIdx: number // Next shift index
  
  // Current editing
  curr: {
    type: EventType | null
    players: Player[]
    puckXY: XYCoordinate[]
    netXY: XYCoordinate | null
  }
  selectedPlayer: Player | null
  editingEvtIdx: number | null
  editingShiftIdx: number | null
  
  // XY mode
  xyMode: 'puck' | 'player'
  xySlot: number
  
  // Video
  videoPlayer: VideoPlayerState
  
  // Sync
  lastSave: Date | null
  connected: boolean
}

export interface PeriodLengths {
  1: number
  2: number
  3: number
  OT: number
}

// ============================================================
// VIDEO
// ============================================================

export interface VideoPlayerState {
  sources: VideoSource[]
  currentSourceIdx: number
  isPlaying: boolean
  currentTime: number // Current video time (seconds)
  speed: number // Playback speed (0.25, 0.5, 1, 1.5, 2)
  autoSync: boolean // Auto-populate times from video
  ytPlayer?: any // YouTube IFrame API player instance
  gameMarkers: GameMarkers
}

export interface VideoSource {
  id: string
  name: string
  type: 'youtube' | 'file'
  url: string
  hotkey?: string
}

export interface GameMarkers {
  P1Start: number | null // Video timestamp (seconds)
  P1End: number | null
  P2Start: number | null
  P2End: number | null
  P3Start: number | null
  P3End: number | null
  OTStart: number | null
  OTEnd: number | null
  stoppages: Stoppage[]
}

export interface Stoppage {
  startTime: number // Video timestamp (seconds)
  endTime: number
  type: string
  note?: string
}

export interface VideoTiming {
  videoStartOffset: number // Seconds to skip at video start
  intermission1: number // Seconds after P1 (default 900 = 15 min)
  intermission2: number // Seconds after P2
  intermission3: number // Seconds after P3 if OT
  timeouts: Timeout[]
  youtubeUrl?: string
}

export interface Timeout {
  period: Period
  gameTime: string // Format: "MM:SS"
  duration: number // Duration in seconds
}

// ============================================================
// REFERENCE DATA
// ============================================================

export interface PlayDetail {
  id: string
  name: string
  category: string
}

export interface EventDetail {
  id: string
  name: string
  eventType: EventType
}

export interface EventTypeRef {
  id: string
  code: string
  name: string
  category: string
}

export interface PlayerRoleRef {
  id: string
  name: string
  abbreviation: string
}

// ============================================================
// EXPORT
// ============================================================

export interface ExportEvent {
  // Core fields matching ETL format
  game_id: number
  event_id: string
  period: number
  start_time: string
  end_time?: string
  event_type: string
  event_detail_1?: string
  event_detail_2?: string
  team: string
  zone?: string
  success?: boolean
  strength?: string
  
  // Players (event_team_player_1, event_team_player_2, etc.)
  [key: string]: any // Allow additional fields
}

export interface ExportShift {
  // Core fields matching ETL format
  game_id: number
  shift_id: string
  period: number
  start_time: string
  end_time: string
  start_type?: string
  stop_type?: string
  strength?: string
  
  // Players (home_forward_1, away_forward_1, etc.)
  [key: string]: any // Allow additional fields
}

// ============================================================
// UTILITIES
// ============================================================

export interface TrackerSettings {
  supabaseUrl?: string
  supabaseKey?: string
  autoSaveInterval?: number // seconds
  periodLengths?: PeriodLengths
}
