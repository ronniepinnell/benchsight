/**
 * Keyboard Shortcuts Hook
 * 
 * Handle keyboard shortcuts for tracker
 * Extracted from tracker_index_v23.5.html setupKeys()
 */

import { useEffect, useCallback } from 'react'
import { useTrackerStore } from '../state'
import { EVENT_HOTKEYS, EVENT_TYPES } from '../constants'
import { toast } from '../utils/toast'
import type { EventType } from '../types'

export function useKeyboardShortcuts() {
  const {
    curr,
    setCurrentType,
    setCurrentTeam,
    setXYMode,
    clearCurrent,
    xyMode,
    evtTeam,
    addEvent
  } = useTrackerStore()

  // Note: We'll need access to logEvent function - for now, just set types
  // Full logging will be handled by EventForm component

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if typing in input/textarea/select
      const target = e.target as HTMLElement
      if (
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.tagName === 'SELECT' ||
        target.isContentEditable
      ) {
        return
      }

      const key = e.key.toUpperCase()

      // Event type shortcuts (F, S, P, G, etc.)
      const eventType = Object.entries(EVENT_HOTKEYS).find(
        ([_, hotkey]) => hotkey.toUpperCase() === key
      )?.[0] as EventType | undefined

      if (eventType && EVENT_TYPES.includes(eventType)) {
        e.preventDefault()
        setCurrentType(eventType)
        return
      }

      // Team toggle
      if (key === 'H' && !e.ctrlKey && !e.altKey) {
        e.preventDefault()
        setCurrentTeam('home')
        toast('Home team selected', 'info')
        return
      }
      
      if (key === 'A' && !e.ctrlKey && !e.altKey) {
        e.preventDefault()
        setCurrentTeam('away')
        toast('Away team selected', 'info')
        return
      }

      // XY mode toggle (Tab)
      if (e.key === 'Tab') {
        e.preventDefault()
        const newMode = xyMode === 'puck' ? 'player' : 'puck'
        setXYMode(newMode)
        toast(newMode === 'puck' ? '🏒 Puck XY mode' : '👤 Player XY mode', 'info')
        return
      }

      // XY mode toggle (backtick)
      if (e.key === '`') {
        e.preventDefault()
        setXYMode('puck')
        toast('🏒 Puck XY mode', 'info')
        return
      }

      // Clear event (Escape)
      if (e.key === 'Escape') {
        e.preventDefault()
        clearCurrent()
        return
      }

      // Number keys 1-6 for player slots (when in player mode)
      if (xyMode === 'player' && e.key >= '1' && e.key <= '6') {
        e.preventDefault()
        // TODO: Set current player slot
        // This would need to be implemented with player selection
        return
      }
    }

    window.addEventListener('keydown', handleKeyDown)

    return () => {
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [curr.type, xyMode, evtTeam, setCurrentType, setCurrentTeam, setXYMode, clearCurrent])
}
