/**
 * Tracker State Management
 * 
 * State structure extracted from tracker_index_v23.5.html
 * Converted to TypeScript with React-friendly state management
 */

import { create } from 'zustand'
import type { 
  GameState, 
  Event, 
  Shift, 
  Player,
  Period,
  PeriodLengths,
  Lineup,
  XYCoordinate,
  EventType
} from './types'

interface TrackerState extends GameState {
  // Actions
  setGame: (gameId: number, homeTeam: string, awayTeam: string) => void
  setRosters: (home: Player[], away: Player[]) => void
  setPeriod: (period: Period) => void
  setClock: (time: string) => void
  updateScore: (home: number, away: number) => void
  
  // Events
  addEvent: (event: Omit<Event, 'idx'>) => Event
  updateEvent: (idx: number, event: Partial<Event>) => void
  deleteEvent: (idx: number) => void
  setEditingEvent: (idx: number | null) => void
  
  // Shifts
  addShift: (shift: Omit<Shift, 'idx'>) => Shift
  updateShift: (idx: number, shift: Partial<Shift>) => void
  deleteShift: (idx: number) => void
  setEditingShift: (idx: number | null) => void
  
  // Current event being built
  evtTeam: 'home' | 'away'
  setCurrentType: (type: EventType | null) => void
  setCurrentTeam: (team: 'home' | 'away') => void
  addCurrentPlayer: (player: Player) => void
  removeCurrentPlayer: (player: Player | string) => void
  setCurrentPuckXY: (xy: XYCoordinate[]) => void
  setCurrentNetXY: (xy: XYCoordinate | null) => void
  setCurrentPlayerXY: (playerNum: string, team: 'home' | 'away', xy: XYCoordinate) => void
  clearCurrent: () => void
  
  // Slots (lineups)
  slots: {
    home: Lineup
    away: Lineup
  }
  setSlot: (team: 'home' | 'away', position: keyof Lineup, player: Player | null) => void
  clearSlot: (team: 'home' | 'away', position: keyof Lineup) => void
  
  // XY mode
  setXYMode: (mode: 'puck' | 'player') => void
  setXYSlot: (slot: number) => void
  
  // Settings
  setPeriodLengths: (lengths: PeriodLengths) => void
  setHomeAttacksRightP1: (value: boolean) => void
}

const defaultPeriodLengths: PeriodLengths = {
  1: 18,
  2: 18,
  3: 18,
  OT: 5
}

const defaultLineup: Lineup = {
  F1: null,
  F2: null,
  F3: null,
  D1: null,
  D2: null,
  G: null,
  X: null
}

const initialState: GameState = {
  gameId: null,
  homeTeam: 'Home',
  awayTeam: 'Away',
  homeColor: '#3b82f6',
  awayColor: '#ef4444',
  homeLogo: null,
  awayLogo: null,
  period: 1,
  periodLengths: defaultPeriodLengths,
  periodLength: 18,
  homeAttacksRightP1: true,
  clock: '18:00',
  score: { home: 0, away: 0 },
  rosters: { home: [], away: [] },
  slots: {
    home: { ...defaultLineup },
    away: { ...defaultLineup }
  },
  events: [],
  shifts: [],
  evtIdx: 0,
  shiftIdx: 0,
  curr: {
    type: null,
    players: [],
    puckXY: [],
    netXY: null
  },
  evtTeam: 'home' as const,
  selectedPlayer: null,
  editingEvtIdx: null,
  editingShiftIdx: null,
  xyMode: 'puck',
  xySlot: 1,
  videoPlayer: {
    sources: [],
    currentSourceIdx: 0,
    isPlaying: false,
    currentTime: 0,
    speed: 1,
    autoSync: true,
    gameMarkers: {
      P1Start: null,
      P1End: null,
      P2Start: null,
      P2End: null,
      P3Start: null,
      P3End: null,
      OTStart: null,
      OTEnd: null,
      stoppages: []
    }
  },
  lastSave: null,
  connected: false
}

export const useTrackerStore = create<TrackerState>((set, get) => ({
  ...initialState,
  
  // Game actions
  setGame: (gameId, homeTeam, awayTeam) => {
    set({ gameId, homeTeam, awayTeam })
  },
  
  setRosters: (home, away) => {
    set({ rosters: { home, away } })
  },
  
  setPeriod: (period) => {
    const { periodLengths } = get()
    const periodLength = periodLengths[period === 4 ? 'OT' : period]
    set({ 
      period, 
      clock: `${periodLength}:00` 
    })
  },
  
  setClock: (clock) => {
    set({ clock })
  },
  
  updateScore: (home, away) => {
    set({ score: { home, away } })
  },
  
  // Event actions
  addEvent: (eventData) => {
    const { evtIdx, events } = get()
    const event: Event = {
      ...eventData,
      idx: evtIdx
    }
    const newEvents = [...events, event].sort((a, b) => {
      // Sort by period, then time
      if (a.period !== b.period) return a.period - b.period
      return a.start_time.localeCompare(b.start_time)
    })
    // Reindex after sort
    newEvents.forEach((e, i) => { e.idx = i })
    set({ 
      events: newEvents, 
      evtIdx: evtIdx + 1,
      lastEndTime: eventData.end_time || eventData.start_time
    })
    return event
  },
  
  updateEvent: (idx, updates) => {
    const { events } = get()
    const newEvents = [...events]
    const eventIdx = newEvents.findIndex(e => e.idx === idx)
    if (eventIdx >= 0) {
      newEvents[eventIdx] = { ...newEvents[eventIdx], ...updates }
      // Re-sort after update
      const sorted = newEvents.sort((a, b) => {
        if (a.period !== b.period) return a.period - b.period
        return a.start_time.localeCompare(b.start_time)
      })
      // Reindex
      sorted.forEach((e, i) => { e.idx = i })
      set({ events: sorted })
    }
  },
  
  deleteEvent: (idx) => {
    const { events } = get()
    const newEvents = events.filter(e => e.idx !== idx)
    // Reindex
    newEvents.forEach((e, i) => { e.idx = i })
    set({ events: newEvents, evtIdx: Math.max(...newEvents.map(e => e.idx || 0), 0) + 1 })
  },
  
  setEditingEvent: (editingEvtIdx) => {
    set({ editingEvtIdx })
  },
  
  // Shift actions
  addShift: (shiftData) => {
    const { shiftIdx, shifts } = get()
    const shift: Shift = {
      ...shiftData,
      idx: shiftIdx
    }
    set({ 
      shifts: [...shifts, shift], 
      shiftIdx: shiftIdx + 1,
      lastEndTime: shiftData.end_time
    })
    return shift
  },
  
  updateShift: (idx, updates) => {
    const { shifts } = get()
    const newShifts = [...shifts]
    const shiftIdx = newShifts.findIndex(s => s.idx === idx)
    if (shiftIdx >= 0) {
      newShifts[shiftIdx] = { ...newShifts[shiftIdx], ...updates }
      set({ shifts: newShifts })
    }
  },
  
  deleteShift: (idx) => {
    const { shifts } = get()
    set({ shifts: shifts.filter(s => s.idx !== idx) })
  },
  
  setEditingShift: (editingShiftIdx) => {
    set({ editingShiftIdx })
  },
  
  // Current event actions
  setCurrentType: (type) => {
    set(state => ({ curr: { ...state.curr, type } }))
  },
  
  setCurrentTeam: (team) => {
    set({ evtTeam: team })
  },
  
  addCurrentPlayer: (player) => {
    set(state => ({
      curr: {
        ...state.curr,
        players: [...state.curr.players, player]
      }
    }))
  },
  
  removeCurrentPlayer: (player) => {
    set(state => {
      const playerNum = typeof player === 'string' ? player : player.num
      const playerTeam = typeof player === 'string' ? undefined : player.team
      
      return {
        curr: {
          ...state.curr,
          players: state.curr.players.filter(p => {
            if (playerTeam) {
              return !(p.num === playerNum && p.team === playerTeam)
            }
            return p.num !== playerNum
          })
        }
      }
    })
  },
  
  setCurrentPuckXY: (puckXY) => {
    set(state => ({ curr: { ...state.curr, puckXY } }))
  },
  
  setCurrentNetXY: (netXY) => {
    set(state => ({ curr: { ...state.curr, netXY } }))
  },
  
  setCurrentPlayerXY: (playerNum: string, team: 'home' | 'away', xy: XYCoordinate) => {
    set(state => {
      const newPlayers = state.curr.players.map(p => {
        if (p.num === playerNum && p.team === team) {
          return {
            ...p,
            xy: [...(p.xy || []), xy]
          }
        }
        return p
      })
      return { curr: { ...state.curr, players: newPlayers } }
    })
  },
  
  clearCurrent: () => {
    set({
      curr: {
        type: null,
        players: [],
        puckXY: [],
        netXY: null
      },
      selectedPlayer: null
    })
  },
  
  // Slot actions
  setSlot: (team, position, player) => {
    set(state => ({
      slots: {
        ...state.slots,
        [team]: {
          ...state.slots[team],
          [position]: player
        }
      }
    }))
  },
  
  clearSlot: (team, position) => {
    set(state => ({
      slots: {
        ...state.slots,
        [team]: {
          ...state.slots[team],
          [position]: null
        }
      }
    }))
  },
  
  // XY mode
  setXYMode: (xyMode) => {
    set({ xyMode })
  },
  
  setXYSlot: (xySlot) => {
    set({ xySlot })
  },
  
  // Settings
  setPeriodLengths: (periodLengths) => {
    set({ 
      periodLengths,
      periodLength: periodLengths[1] // Legacy compatibility
    })
  },
  
  setHomeAttacksRightP1: (homeAttacksRightP1) => {
    set({ homeAttacksRightP1 })
  }
}))
