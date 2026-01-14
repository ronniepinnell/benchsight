/**
 * Auto-Save Hook
 * 
 * Auto-save tracker state to localStorage
 */

import { useEffect, useRef } from 'react'
import { useTrackerStore } from '../state'

const STORAGE_KEY_PREFIX = 'benchsight_tracker_'
const AUTO_SAVE_INTERVAL = 30000 // 30 seconds

export function useAutoSave(gameId: number | null) {
  const store = useTrackerStore.getState()
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const lastSaveRef = useRef<Date | null>(null)

  useEffect(() => {
    if (!gameId) {
      // Clear interval if no game
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
      return
    }

    // Auto-save function
    const save = () => {
      const state = useTrackerStore.getState()
      const data = {
        gameId: state.gameId,
        period: state.period,
        clock: state.clock,
        score: state.score,
        events: state.events,
        shifts: state.shifts,
        slots: state.slots,
        evtIdx: state.evtIdx,
        shiftIdx: state.shiftIdx,
        periodLengths: state.periodLengths,
        homeAttacksRightP1: state.homeAttacksRightP1,
        lastSave: new Date().toISOString()
      }

      const key = `${STORAGE_KEY_PREFIX}${gameId}`
      try {
        localStorage.setItem(key, JSON.stringify(data))
        lastSaveRef.current = new Date()
        useTrackerStore.setState({ lastSave: lastSaveRef.current })
      } catch (err) {
        console.error('Auto-save error:', err)
      }
    }

    // Load from storage on mount
    const load = () => {
      const key = `${STORAGE_KEY_PREFIX}${gameId}`
      const stored = localStorage.getItem(key)
      
      if (stored) {
        try {
          const data = JSON.parse(stored)
          
          // Restore state (be careful not to overwrite everything)
          const updates: any = {}
          if (data.events) updates.events = data.events
          if (data.shifts) updates.shifts = data.shifts
          if (data.slots) updates.slots = data.slots
          if (data.evtIdx !== undefined) updates.evtIdx = data.evtIdx
          if (data.shiftIdx !== undefined) updates.shiftIdx = data.shiftIdx
          if (data.period !== undefined) updates.period = data.period
          if (data.clock) updates.clock = data.clock
          if (data.score) updates.score = data.score
          if (data.periodLengths) updates.periodLengths = data.periodLengths
          if (data.homeAttacksRightP1 !== undefined) updates.homeAttacksRightP1 = data.homeAttacksRightP1
          
          if (data.lastSave) {
            lastSaveRef.current = new Date(data.lastSave)
            updates.lastSave = lastSaveRef.current
          }
          
          if (Object.keys(updates).length > 0) {
            useTrackerStore.setState(updates)
          }
        } catch (err) {
          console.error('Error loading saved state:', err)
        }
      }
    }

    // Load on mount
    load()

    // Set up auto-save interval
    intervalRef.current = setInterval(save, AUTO_SAVE_INTERVAL)

    // Save on unmount
    return () => {
      save()
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [gameId])
}
