'use client'

/**
 * Edit Shift Modal Component
 * 
 * Modal for editing existing shifts
 */

import { useState, useEffect } from 'react'
import { useTrackerStore } from '@/lib/tracker/state'
import { SHIFT_START_TYPES, SHIFT_STOP_TYPES } from '@/lib/tracker/constants'
import { Button } from '@/components/ui/button'
import { PlayerRoster } from './PlayerRoster'
import { PlayerSlot } from './ShiftPanel'
import { toast } from '@/lib/tracker/utils/toast'
import type { Shift, Player } from '@/lib/tracker/types'

interface EditShiftModalProps {
  isOpen: boolean
  onClose: () => void
}

export function EditShiftModal({ isOpen, onClose }: EditShiftModalProps) {
  const {
    shifts,
    editingShiftIdx,
    updateShift,
    deleteShift,
    slots
  } = useTrackerStore()

  const shift = editingShiftIdx !== null ? shifts.find(s => s.idx === editingShiftIdx) : null

  const [period, setPeriod] = useState(1)
  const [startTime, setStartTime] = useState('')
  const [endTime, setEndTime] = useState('')
  const [startType, setStartType] = useState('OnTheFly')
  const [stopType, setStopType] = useState('OnTheFly')
  const [strength, setStrength] = useState('5v5')
  const [shiftSlots, setShiftSlots] = useState<{ home: typeof slots.home; away: typeof slots.away }>({
    home: { F1: null, F2: null, F3: null, D1: null, D2: null, G: null, X: null },
    away: { F1: null, F2: null, F3: null, D1: null, D2: null, G: null, X: null }
  })
  const [selectingSlot, setSelectingSlot] = useState<{ team: 'home' | 'away'; position: keyof typeof slots.home } | null>(null)

  // Load shift data when modal opens
  useEffect(() => {
    if (shift && isOpen) {
      setPeriod(shift.period)
      setStartTime(shift.start_time || '')
      setEndTime(shift.end_time || '')
      setStartType(shift.start_type || 'OnTheFly')
      setStopType(shift.stop_type || 'OnTheFly')
      setStrength(shift.strength || '5v5')
      
      // Load shift lineup
      if (shift.home) {
        setShiftSlots(prev => ({ ...prev, home: shift.home || prev.home }))
      }
      if (shift.away) {
        setShiftSlots(prev => ({ ...prev, away: shift.away || prev.away }))
      }
    }
  }, [shift, isOpen])

  const handleSave = () => {
    if (!shift || editingShiftIdx === null) return

    updateShift(editingShiftIdx, {
      period,
      start_time: startTime,
      end_time: endTime,
      start_type: startType,
      stop_type: stopType,
      strength,
      home: shiftSlots.home,
      away: shiftSlots.away
    })

    toast('Shift updated', 'success')
    onClose()
  }

  const handleDelete = () => {
    if (!shift || editingShiftIdx === null) return
    if (!confirm(`Delete shift #${editingShiftIdx + 1}?`)) return

    deleteShift(editingShiftIdx)
    toast('Shift deleted', 'success')
    onClose()
  }

  const handlePlayerClick = (team: 'home' | 'away', position: keyof typeof slots.home, player: Player | null) => {
    if (player) {
      // Remove player from slot
      setShiftSlots(prev => ({
        ...prev,
        [team]: {
          ...prev[team],
          [position]: null
        }
      }))
      toast(`Removed #${player.num} from ${position}`, 'info')
    } else {
      // Set as selecting slot
      setSelectingSlot({ team, position })
    }
  }

  const handleRosterPlayerClick = (player: Player) => {
    if (!selectingSlot) return

    setShiftSlots(prev => ({
      ...prev,
      [selectingSlot.team]: {
        ...prev[selectingSlot.team],
        [selectingSlot.position]: player
      }
    }))
    setSelectingSlot(null)
    toast(`Added #${player.num} to ${selectingSlot.position}`, 'success')
  }

  if (!isOpen || !shift) return null

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50" onClick={onClose}>
      <div
        className="bg-card border border-border rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold">Edit Shift #{editingShiftIdx !== null ? editingShiftIdx + 1 : ''}</h2>
          <button
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground"
          >
            ×
          </button>
        </div>

        <div className="space-y-4">
          {/* Period & Times */}
          <div className="grid grid-cols-4 gap-2">
            <div>
              <label className="text-xs text-muted-foreground block mb-1">Period</label>
              <select
                value={period}
                onChange={(e) => setPeriod(parseInt(e.target.value))}
                className="w-full px-2 py-1 text-sm bg-input border border-border rounded"
              >
                {[1, 2, 3, 4].map(p => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs text-muted-foreground block mb-1">Start Time</label>
              <input
                type="text"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                className="w-full px-2 py-1 text-sm bg-input border border-border rounded"
                placeholder="MM:SS"
              />
            </div>
            <div>
              <label className="text-xs text-muted-foreground block mb-1">End Time</label>
              <input
                type="text"
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
                className="w-full px-2 py-1 text-sm bg-input border border-border rounded"
                placeholder="MM:SS"
              />
            </div>
            <div>
              <label className="text-xs text-muted-foreground block mb-1">Strength</label>
              <input
                type="text"
                value={strength}
                onChange={(e) => setStrength(e.target.value)}
                className="w-full px-2 py-1 text-sm bg-input border border-border rounded"
                placeholder="5v5"
              />
            </div>
          </div>

          {/* Start/Stop Types */}
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-xs text-muted-foreground block mb-1">Start Type</label>
              <select
                value={startType}
                onChange={(e) => setStartType(e.target.value)}
                className="w-full px-2 py-1 text-sm bg-input border border-border rounded"
              >
                {SHIFT_START_TYPES.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs text-muted-foreground block mb-1">Stop Type</label>
              <select
                value={stopType}
                onChange={(e) => setStopType(e.target.value)}
                className="w-full px-2 py-1 text-sm bg-input border border-border rounded"
              >
                {SHIFT_STOP_TYPES.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Lineups */}
          <div className="grid grid-cols-2 gap-4 border-t pt-4">
            {/* Home Team */}
            <div className="space-y-2">
              <div className="text-xs font-semibold text-blue-500 uppercase">Home</div>
              
              <div className="space-y-1">
                {/* Forwards */}
                <div className="grid grid-cols-3 gap-1">
                  {['F1', 'F2', 'F3'].map((pos) => (
                    <PlayerSlot
                      key={pos}
                      position={pos}
                      player={shiftSlots.home[pos as keyof typeof shiftSlots.home]}
                      team="home"
                      onClick={() => handlePlayerClick('home', pos as any, shiftSlots.home[pos as keyof typeof shiftSlots.home])}
                    />
                  ))}
                </div>

                {/* Defense */}
                <div className="grid grid-cols-2 gap-1">
                  {['D1', 'D2'].map((pos) => (
                    <PlayerSlot
                      key={pos}
                      position={pos}
                      player={shiftSlots.home[pos as keyof typeof shiftSlots.home]}
                      team="home"
                      onClick={() => handlePlayerClick('home', pos as any, shiftSlots.home[pos as keyof typeof shiftSlots.home])}
                    />
                  ))}
                </div>

                {/* Goalie & Extra */}
                <div className="grid grid-cols-2 gap-1">
                  {['G', 'X'].map((pos) => (
                    <PlayerSlot
                      key={pos}
                      position={pos}
                      player={shiftSlots.home[pos as keyof typeof shiftSlots.home]}
                      team="home"
                      onClick={() => handlePlayerClick('home', pos as any, shiftSlots.home[pos as keyof typeof shiftSlots.home])}
                    />
                  ))}
                </div>
              </div>
            </div>

            {/* Away Team */}
            <div className="space-y-2">
              <div className="text-xs font-semibold text-red-500 uppercase">Away</div>
              
              <div className="space-y-1">
                {/* Forwards */}
                <div className="grid grid-cols-3 gap-1">
                  {['F1', 'F2', 'F3'].map((pos) => (
                    <PlayerSlot
                      key={pos}
                      position={pos}
                      player={shiftSlots.away[pos as keyof typeof shiftSlots.away]}
                      team="away"
                      onClick={() => handlePlayerClick('away', pos as any, shiftSlots.away[pos as keyof typeof shiftSlots.away])}
                    />
                  ))}
                </div>

                {/* Defense */}
                <div className="grid grid-cols-2 gap-1">
                  {['D1', 'D2'].map((pos) => (
                    <PlayerSlot
                      key={pos}
                      position={pos}
                      player={shiftSlots.away[pos as keyof typeof shiftSlots.away]}
                      team="away"
                      onClick={() => handlePlayerClick('away', pos as any, shiftSlots.away[pos as keyof typeof shiftSlots.away])}
                    />
                  ))}
                </div>

                {/* Goalie & Extra */}
                <div className="grid grid-cols-2 gap-1">
                  {['G', 'X'].map((pos) => (
                    <PlayerSlot
                      key={pos}
                      position={pos}
                      player={shiftSlots.away[pos as keyof typeof shiftSlots.away]}
                      team="away"
                      onClick={() => handlePlayerClick('away', pos as any, shiftSlots.away[pos as keyof typeof shiftSlots.away])}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Player Selection (when clicking empty slot) */}
          {selectingSlot && (
            <div className="space-y-2 border-t pt-4 bg-muted/50 p-4 rounded">
              <div className="text-xs font-semibold uppercase">
                Select Player for {selectingSlot.team} {selectingSlot.position}
              </div>
              <div className="max-h-48 overflow-y-auto">
                <PlayerRoster 
                  team={selectingSlot.team} 
                  onPlayerSelect={handleRosterPlayerClick}
                />
              </div>
              <Button
                onClick={() => setSelectingSlot(null)}
                variant="outline"
                size="sm"
                className="w-full"
              >
                Cancel
              </Button>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex gap-2 mt-6">
          <Button
            onClick={handleSave}
            className="flex-1"
            size="lg"
          >
            Save Changes
          </Button>
          <Button
            onClick={handleDelete}
            variant="destructive"
            size="lg"
          >
            Delete
          </Button>
          <Button
            onClick={onClose}
            variant="outline"
            size="lg"
          >
            Cancel
          </Button>
        </div>
      </div>
    </div>
  )
}
