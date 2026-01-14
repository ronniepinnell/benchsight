'use client'

/**
 * Shift Panel Component
 * 
 * Panel for managing shifts and lineups
 */

import { useState } from 'react'
import { useTrackerStore } from '@/lib/tracker/state'
import { PlayerRoster } from './PlayerRoster'
import { EditShiftModal } from './EditShiftModal'
import { createShift } from '@/lib/tracker/shifts'
import { deriveStrength } from '@/lib/tracker/utils/strength'
import { SHIFT_START_TYPES, SHIFT_STOP_TYPES, SHIFT_TYPES } from '@/lib/tracker/constants'
import { toast } from '@/lib/tracker/utils/toast'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import type { Player } from '@/lib/tracker/types'

const SimpleInput = ({ value, onChange, ...props }: any) => (
  <input
    className="w-full px-2 py-1 text-xs bg-input border border-border rounded"
    value={value || ''}
    onChange={(e) => onChange(e.target.value)}
    {...props}
  />
)

const SimpleSelect = ({ value, onChange, children, ...props }: any) => (
  <select
    className="w-full px-2 py-1 text-xs bg-input border border-border rounded"
    value={value || ''}
    onChange={(e) => onChange(e.target.value)}
    {...props}
  >
    {children}
  </select>
)

export function ShiftPanel() {
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)
  
  const {
    period,
    clock,
    slots,
    rosters,
    shifts,
    addShift,
    setSlot,
    clearSlot
  } = useTrackerStore()

  const [startTime, setStartTime] = useState(clock)
  const [endTime, setEndTime] = useState('')
  const [startType, setStartType] = useState('OnTheFly')
  const [stopType, setStopType] = useState('OnTheFly')

  const handleLogShift = () => {
    if (!startTime) {
      toast('Enter start time', 'error')
      return
    }

    const shift = createShift({
      period,
      startTime,
      endTime: endTime || clock,
      startType,
      stopType,
      home: slots.home,
      away: slots.away,
      events: [] // TODO: Pass events for stoppage calculation
    })

    addShift(shift)
    setStartTime(endTime || clock)
    setEndTime('')
    
    const stoppageTime = shift.stoppageTime || 0
    toast(`Shift #${shift.idx ? shift.idx + 1 : ''} logged (${stoppageTime}s stoppage)`, 'success')
  }

  const currentStrength = deriveStrength(slots.home, slots.away)

  const [selectingSlot, setSelectingSlot] = useState<{ team: 'home' | 'away'; position: keyof typeof slots.home } | null>(null)

  const handlePlayerClick = (team: 'home' | 'away', position: keyof typeof slots.home, player: Player | null) => {
    if (player) {
      // Remove player from slot
      clearSlot(team, position)
      toast(`Removed #${player.num} from ${position}`, 'info')
    } else {
      // Set as selecting slot - will show roster below
      setSelectingSlot({ team, position })
    }
  }

  const handleRosterPlayerClick = (player: Player) => {
    if (!selectingSlot) return

    setSlot(selectingSlot.team, selectingSlot.position, player)
    setSelectingSlot(null)
    toast(`Added #${player.num} to ${selectingSlot.position}`, 'success')
  }

  return (
    <div className="space-y-4 p-2">
      {/* Current Strength */}
      <div className="p-2 bg-muted rounded text-center">
        <div className="text-xs text-muted-foreground mb-1">Strength</div>
        <div className="text-lg font-bold text-accent">{currentStrength}</div>
      </div>

      {/* Home Team Slots */}
      <div className="space-y-2">
        <div className="text-xs font-semibold text-blue-500 uppercase">Home</div>
        
        <div className="space-y-1">
          {/* Forwards */}
          <div className="grid grid-cols-3 gap-1">
            {['F1', 'F2', 'F3'].map((pos) => (
              <PlayerSlot
                key={pos}
                position={pos}
                player={slots.home[pos as keyof typeof slots.home]}
                team="home"
                onClick={() => handlePlayerClick('home', pos as any, slots.home[pos as keyof typeof slots.home])}
              />
            ))}
          </div>

          {/* Defense */}
          <div className="grid grid-cols-2 gap-1">
            {['D1', 'D2'].map((pos) => (
              <PlayerSlot
                key={pos}
                position={pos}
                player={slots.home[pos as keyof typeof slots.home]}
                team="home"
                onClick={() => handlePlayerClick('home', pos as any, slots.home[pos as keyof typeof slots.home])}
              />
            ))}
          </div>

          {/* Goalie & Extra */}
          <div className="grid grid-cols-2 gap-1">
            {['G', 'X'].map((pos) => (
              <PlayerSlot
                key={pos}
                position={pos}
                player={slots.home[pos as keyof typeof slots.home]}
                team="home"
                onClick={() => handlePlayerClick('home', pos as any, slots.home[pos as keyof typeof slots.home])}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Away Team Slots */}
      <div className="space-y-2">
        <div className="text-xs font-semibold text-red-500 uppercase">Away</div>
        
        <div className="space-y-1">
          {/* Forwards */}
          <div className="grid grid-cols-3 gap-1">
            {['F1', 'F2', 'F3'].map((pos) => (
              <PlayerSlot
                key={pos}
                position={pos}
                player={slots.away[pos as keyof typeof slots.away]}
                team="away"
                onClick={() => handlePlayerClick('away', pos as any, slots.away[pos as keyof typeof slots.away])}
              />
            ))}
          </div>

          {/* Defense */}
          <div className="grid grid-cols-2 gap-1">
            {['D1', 'D2'].map((pos) => (
              <PlayerSlot
                key={pos}
                position={pos}
                player={slots.away[pos as keyof typeof slots.away]}
                team="away"
                onClick={() => handlePlayerClick('away', pos as any, slots.away[pos as keyof typeof slots.away])}
              />
            ))}
          </div>

          {/* Goalie & Extra */}
          <div className="grid grid-cols-2 gap-1">
            {['G', 'X'].map((pos) => (
              <PlayerSlot
                key={pos}
                position={pos}
                player={slots.away[pos as keyof typeof slots.away]}
                team="away"
                onClick={() => handlePlayerClick('away', pos as any, slots.away[pos as keyof typeof slots.away])}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Shift Times */}
      <div className="space-y-2 border-t pt-2">
        <div className="text-xs font-semibold uppercase">Shift Times</div>
        
        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="text-xs text-muted-foreground block mb-1">Start</label>
            <SimpleInput
              type="text"
              value={startTime}
              onChange={setStartTime}
              placeholder="MM:SS"
            />
          </div>
          <div>
            <label className="text-xs text-muted-foreground block mb-1">End</label>
            <SimpleInput
              type="text"
              value={endTime}
              onChange={setEndTime}
              placeholder="MM:SS"
            />
          </div>
        </div>

        <div>
          <label className="text-xs text-muted-foreground block mb-1">Start Type</label>
          <SimpleSelect value={startType} onChange={setStartType}>
            {SHIFT_START_TYPES.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </SimpleSelect>
        </div>

        <div>
          <label className="text-xs text-muted-foreground block mb-1">Stop Type</label>
          <SimpleSelect value={stopType} onChange={setStopType}>
            {SHIFT_STOP_TYPES.filter(Boolean).map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </SimpleSelect>
        </div>

        <Button
          onClick={handleLogShift}
          className="w-full"
          size="sm"
        >
          Log Shift
        </Button>
      </div>

      {/* Player Selection (when clicking empty slot) */}
      {selectingSlot && (
        <div className="space-y-2 border-t pt-2 bg-muted/50 p-2 rounded">
          <div className="text-xs font-semibold uppercase">
            Select Player for {selectingSlot.team} {selectingSlot.position}
          </div>
          <div className="max-h-32 overflow-y-auto">
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

      {/* Shift Log */}
      <div className="space-y-1 border-t pt-2">
        <div className="text-xs font-semibold uppercase">Recent Shifts</div>
        <div className="space-y-1 max-h-48 overflow-y-auto">
          {shifts.slice(-10).reverse().map((shift, i) => (
            <div
              key={shift.idx ?? i}
              className="text-xs p-2 bg-muted/50 rounded cursor-pointer hover:bg-muted"
              onClick={() => {
                if (shift.idx !== undefined) {
                  setEditingShift(shift.idx)
                  setIsEditModalOpen(true)
                }
              }}
            >
              <div className="font-mono">
                P{shift.period} {shift.start_time} - {shift.end_time}
              </div>
              <div className="text-muted-foreground text-[10px]">
                {shift.strength || '5v5'}
              </div>
            </div>
          ))}
          {shifts.length === 0 && (
            <div className="text-xs text-muted-foreground text-center py-4">
              No shifts logged
            </div>
          )}
        </div>
      </div>

      {/* Edit Modal */}
      <EditShiftModal
        isOpen={isEditModalOpen}
        onClose={() => {
          setIsEditModalOpen(false)
          setEditingShift(null)
        }}
      />
    </div>
  )
}

export interface PlayerSlotProps {
  position: string
  player: Player | null
  team: 'home' | 'away'
  onClick: () => void
}

export function PlayerSlot({ position, player, team, onClick }: PlayerSlotProps) {
  const filled = !!player
  const teamColor = team === 'home' ? 'border-blue-500' : 'border-red-500'
  const fillColor = team === 'home' ? 'bg-blue-500/10' : 'bg-red-500/10'

  return (
    <button
      onClick={onClick}
      className={cn(
        'min-h-[32px] p-1 rounded border-2 text-xs font-semibold transition-colors flex flex-col items-center justify-center',
        filled ? `${teamColor} ${fillColor}` : 'border-border bg-input hover:bg-muted',
        !filled && 'text-muted-foreground'
      )}
    >
      {player ? (
        <>
          <span className="font-bold">#{player.num}</span>
          {player.name && (
            <span className="text-[10px] text-muted-foreground truncate w-full">
              {player.name}
            </span>
          )}
        </>
      ) : (
        <span>{position}</span>
      )}
    </button>
  )
}
