'use client'

/**
 * Event Form Component
 * 
 * Form for entering event details
 */

import { useState, useEffect, useCallback } from 'react'
import { useTrackerStore } from '@/lib/tracker/state'
import { createEvent } from '@/lib/tracker/events'
import { EventTypeGrid } from './EventTypeGrid'
import { Button } from '@/components/ui/button'
// Input/Select components defined inline below
import { SearchableSelect, SearchableSelectOption } from '@/components/common/searchable-select'
import { EVENT_DETAILS } from '@/lib/tracker/constants'
// Zone label utility available but not used in this component
import { cn } from '@/lib/utils'
import { toast } from '@/lib/tracker/utils/toast'
import { PlayerSelectDropdown } from './PlayerSelectDropdown'
import { PlayerChip } from './PlayerChip'
import type { EventType, Zone, Team, Player } from '@/lib/tracker/types'

// Simple Input/Select components (create if needed)
const SimpleInput = ({ value, onChange, ...props }: any) => (
  <input
    className="w-full px-2 py-1 text-sm bg-input border border-border rounded"
    value={value || ''}
    onChange={(e) => onChange(e.target.value)}
    {...props}
  />
)

// SimpleSelect replaced with SearchableSelect - see usage below

export function EventForm() {
  const {
    curr,
    evtTeam,
    period,
    clock,
    slots,
    homeAttacksRightP1,
    homeTeam,
    awayTeam,
    setCurrentType,
    setCurrentTeam,
    addEvent,
    clearCurrent,
    setXYMode,
    removeCurrentPlayer,
    addCurrentPlayer
  } = useTrackerStore()
  const [startTime, setStartTime] = useState(clock)
  const [endTime, setEndTime] = useState('')
  const [zone, setZone] = useState<Zone | ''>('')
  const [success, setSuccess] = useState<'s' | 'u' | ''>('')
  const [strength, setStrength] = useState('5v5')
  const [detail1, setDetail1] = useState('')
  const [detail2, setDetail2] = useState('')
  const [isHighlight, setIsHighlight] = useState(false)
  const [videoUrl, setVideoUrl] = useState('')
  
  // Reset detail2 when detail1 changes
  useEffect(() => {
    if (detail1) {
      // Detail2 options may change based on detail1
      // Reset detail2 if it's no longer valid
      const newOptions = getDetail2Options()
      if (detail2 && !newOptions.includes(detail2)) {
        setDetail2('')
      }
    } else {
      setDetail2('')
    }
  }, [detail1, curr.type])

  // Update start time when clock changes
  useEffect(() => {
    setStartTime(clock)
  }, [clock])

  // Get available detail1 options for current type
  const detail1Options = curr.type ? EVENT_DETAILS[curr.type]?.d1 || [] : []

  // Get available detail2 options
  const getDetail2Options = useCallback(() => {
    if (!curr.type || !detail1) return []
    const details = EVENT_DETAILS[curr.type]
    if (!details) return []

    // Check for conditional d2 arrays
    if (detail1.includes('Giveaway') && details.d2_Giveaway) {
      return details.d2_Giveaway
    }
    if (detail1.includes('Takeaway') && details.d2_Takeaway) {
      return details.d2_Takeaway
    }
    if (detail1.includes('Entry') && details.d2_Entry) {
      return details.d2_Entry
    }
    if (detail1.includes('Exit') && details.d2_Exit) {
      return details.d2_Exit
    }
    if (detail1.includes('Offensive') && details.d2_Offensive) {
      return details.d2_Offensive
    }
    if (detail1.includes('Defensive') && details.d2_Defensive) {
      return details.d2_Defensive
    }
    if (detail1.includes('Play') && details.d2_Play) {
      return details.d2_Play
    }

    return details.d2 || []
  }, [curr.type, detail1])

  const detail2Options = getDetail2Options()

  const handleLogEvent = () => {
    if (!curr.type) {
      toast('Select an event type first', 'error')
      return
    }

    const newEvent = createEvent({
      type: curr.type,
      period,
      team: evtTeam,
      startTime: startTime || clock,
      endTime: endTime || startTime || clock,
      detail1,
      detail2,
      zone: zone || undefined,
      success: success || undefined,
      strength,
      players: curr.players || [],
      puckXY: curr.puckXY || [],
      netXY: curr.netXY || undefined,
      isHighlight,
      videoUrl: isHighlight && videoUrl ? videoUrl : undefined, // v23.7: Individual highlight video URL
      homeAttacksRightP1
    })

    addEvent(newEvent)
    clearCurrent()
    setStartTime(endTime || startTime || clock)
    setEndTime('')
    setDetail1('')
    setDetail2('')
    setZone('')
    setSuccess('')
    setIsHighlight(false)
    setVideoUrl('')
    
    const highlightIcon = newEvent.isHighlight ? ' ⭐' : ''
    toast(`Event #${newEvent.idx ? newEvent.idx + 1 : ''}: ${newEvent.type}${highlightIcon}`, 'success')
  }

  return (
    <div className="space-y-4 p-4">
      {/* Event Type Grid */}
      <div>
        <label className="text-xs text-muted-foreground uppercase mb-2 block">
          Event Type
        </label>
        <EventTypeGrid />
      </div>

      {/* Team Toggle */}
      <div className="flex gap-2">
        <Button
          variant={evtTeam === 'home' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setCurrentTeam('home')}
          className={cn(
            'flex-1',
            evtTeam === 'home' && 'bg-blue-600 hover:bg-blue-700'
          )}
        >
          {homeTeam}
        </Button>
        <Button
          variant={evtTeam === 'away' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setCurrentTeam('away')}
          className={cn(
            'flex-1',
            evtTeam === 'away' && 'bg-red-600 hover:bg-red-700'
          )}
        >
          {awayTeam}
        </Button>
      </div>

      {/* Time Inputs */}
      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className="text-xs text-muted-foreground block mb-1">
            Start Time
          </label>
          <SimpleInput
            type="text"
            value={startTime}
            onChange={setStartTime}
            placeholder="MM:SS"
          />
        </div>
        <div>
          <label className="text-xs text-muted-foreground block mb-1">
            End Time
          </label>
          <SimpleInput
            type="text"
            value={endTime}
            onChange={setEndTime}
            placeholder="MM:SS"
          />
        </div>
      </div>

      {/* Details */}
      {curr.type && (
        <>
          {detail1Options.length > 0 && (
            <div>
              <label className="text-xs text-muted-foreground block mb-1">
                Detail 1
              </label>
              <SearchableSelect
                options={[
                  { value: '', label: '--', searchText: '' },
                  ...detail1Options.map((opt) => ({
                    value: opt,
                    label: opt,
                    searchText: opt,
                  })),
                ]}
                value={detail1}
                onChange={setDetail1}
                placeholder="--"
              />
            </div>
          )}

          {detail2Options.length > 0 && (
            <div>
              <label className="text-xs text-muted-foreground block mb-1">
                Detail 2
              </label>
              <SearchableSelect
                options={[
                  { value: '', label: '--', searchText: '' },
                  ...detail2Options.map((opt) => ({
                    value: opt,
                    label: opt,
                    searchText: opt,
                  })),
                ]}
                value={detail2}
                onChange={setDetail2}
                placeholder="--"
              />
            </div>
          )}
        </>
      )}

      {/* Zone, Success, Strength */}
      <div className="grid grid-cols-3 gap-2">
        <div>
          <label className="text-xs text-muted-foreground block mb-1">Zone</label>
          <SimpleSelect value={zone} onChange={setZone}>
            <option value="">--</option>
            <option value="o">Offensive</option>
            <option value="n">Neutral</option>
            <option value="d">Defensive</option>
          </SimpleSelect>
        </div>
        <div>
          <label className="text-xs text-muted-foreground block mb-1">Success</label>
          <SearchableSelect
            options={[
              { value: '', label: '--', searchText: '' },
              { value: 's', label: 'Success', searchText: 'success' },
              { value: 'u', label: 'Unsuccess', searchText: 'unsuccess' },
            ]}
            value={success}
            onChange={setSuccess}
            placeholder="--"
          />
        </div>
        <div>
          <label className="text-xs text-muted-foreground block mb-1">Strength</label>
          <SimpleInput
            type="text"
            value={strength}
            onChange={setStrength}
            placeholder="5v5"
          />
        </div>
      </div>

      {/* Highlight */}
      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="highlight"
          checked={isHighlight}
          onChange={(e) => {
            setIsHighlight(e.target.checked)
            if (!e.target.checked) setVideoUrl('')
          }}
        />
        <label htmlFor="highlight" className="text-xs">
          ⭐ Highlight
        </label>
      </div>

      {/* Video URL for highlights (v23.7) */}
      {isHighlight && (
        <div className="space-y-1">
          <label htmlFor="videoUrl" className="text-xs text-muted-foreground">
            YouTube URL for this highlight:
          </label>
          <input
            type="text"
            id="videoUrl"
            value={videoUrl}
            onChange={(e) => setVideoUrl(e.target.value)}
            placeholder="https://youtube.com/watch?v=..."
            className="w-full px-2 py-1 text-xs bg-input border border-border rounded text-foreground"
          />
        </div>
      )}

      {/* Current Players */}
      {curr.players && curr.players.length > 0 && (
        <div className="space-y-2">
          <label className="text-xs text-muted-foreground uppercase mb-2 block">
            Event Players
          </label>
          <div className="flex flex-wrap gap-1 p-2 bg-muted/50 rounded min-h-[40px]">
            {curr.players.map((player, i) => (
              <PlayerChip
                key={`${player.team}-${player.num}-${i}`}
                player={player}
                role={player.role}
                onRemove={() => removeCurrentPlayer(player)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Player Selection Dropdown */}
      <div className="space-y-2">
        <label className="text-xs text-muted-foreground uppercase mb-2 block">
          Add Player ({evtTeam === 'home' ? homeTeam : awayTeam})
        </label>
        <PlayerSelectDropdown team={evtTeam} />
      </div>

      {/* XY Mode Toggle */}
      <div className="flex gap-2">
        <Button
          variant={curr.xyMode === 'puck' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setXYMode('puck')}
          className="flex-1"
        >
          🏒 Puck
        </Button>
        <Button
          variant={curr.xyMode === 'player' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setXYMode('player')}
          className="flex-1"
        >
          👤 Player
        </Button>
      </div>

      {/* Log Event Button */}
      <Button
        onClick={handleLogEvent}
        disabled={!curr.type}
        className="w-full"
        size="lg"
      >
        Log Event
      </Button>
    </div>
  )
}
