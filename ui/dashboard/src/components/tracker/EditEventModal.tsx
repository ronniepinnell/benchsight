'use client'

/**
 * Edit Event Modal Component
 * 
 * Modal for editing existing events
 */

import { useState, useEffect } from 'react'
import { useTrackerStore } from '@/lib/tracker/state'
import { EVENT_DETAILS, EVENT_TYPES } from '@/lib/tracker/constants'
import { Button } from '@/components/ui/button'
import { PlayerChip } from './PlayerChip'
import { PlayerSelectDropdown } from './PlayerSelectDropdown'
import { toast } from '@/lib/tracker/utils/toast'
import { cn } from '@/lib/utils'
import { SearchableSelect, SearchableSelectOption } from '@/components/common/searchable-select'
import type { Event, EventType, Zone, Player } from '@/lib/tracker/types'

interface EditEventModalProps {
  isOpen: boolean
  onClose: () => void
}

export function EditEventModal({ isOpen, onClose }: EditEventModalProps) {
  const {
    events,
    editingEvtIdx,
    updateEvent,
    deleteEvent,
    evtTeam,
    setCurrentTeam,
    period,
    homeAttacksRightP1,
    addCurrentPlayer,
    removeCurrentPlayer
  } = useTrackerStore()

  const event = editingEvtIdx !== null ? events.find(e => e.idx === editingEvtIdx) : null

  const [eventType, setEventType] = useState<EventType | ''>('')
  const [team, setTeam] = useState<'home' | 'away'>('home')
  const [startTime, setStartTime] = useState('')
  const [endTime, setEndTime] = useState('')
  const [zone, setZone] = useState<Zone | ''>('')
  const [success, setSuccess] = useState<'s' | 'u' | ''>('')
  const [strength, setStrength] = useState('5v5')
  const [detail1, setDetail1] = useState('')
  const [detail2, setDetail2] = useState('')
  const [isHighlight, setIsHighlight] = useState(false)
  const [videoUrl, setVideoUrl] = useState('')
  const [players, setPlayers] = useState<Player[]>([])

  // Load event data when modal opens
  useEffect(() => {
    if (event && isOpen) {
      setEventType(event.type)
      setTeam(event.team)
      setStartTime(event.start_time)
      setEndTime(event.end_time || '')
      setZone(event.zone || '')
      setSuccess(event.success ? 's' : 'u')
      setStrength(event.strength || '5v5')
      setDetail1(event.detail1 || '')
      setDetail2(event.detail2 || '')
      setIsHighlight(event.isHighlight || false)
      setVideoUrl(event.videoUrl || '')
      setPlayers(event.players || [])
    }
  }, [event, isOpen])

  const detail1Options = eventType ? EVENT_DETAILS[eventType]?.d1 || [] : []

  const getDetail2Options = () => {
    if (!eventType || !detail1) return []
    const details = EVENT_DETAILS[eventType]
    if (!details) return []

    if (detail1.includes('Giveaway') && details.d2_Giveaway) return details.d2_Giveaway
    if (detail1.includes('Takeaway') && details.d2_Takeaway) return details.d2_Takeaway
    if (detail1.includes('Entry') && details.d2_Entry) return details.d2_Entry
    if (detail1.includes('Exit') && details.d2_Exit) return details.d2_Exit
    if (detail1.includes('Offensive') && details.d2_Offensive) return details.d2_Offensive
    if (detail1.includes('Defensive') && details.d2_Defensive) return details.d2_Defensive
    if (detail1.includes('Play') && details.d2_Play) return details.d2_Play

    return details.d2 || []
  }

  const detail2Options = getDetail2Options()

  const handleSave = () => {
    if (!event || editingEvtIdx === null) return

    updateEvent(editingEvtIdx, {
      type: eventType as EventType,
      team,
      start_time: startTime,
      end_time: endTime || undefined,
      zone: zone || undefined,
      success: success === 's' ? true : success === 'u' ? false : undefined,
      strength,
      detail1: detail1 || undefined,
      detail2: detail2 || undefined,
      isHighlight,
      videoUrl: isHighlight ? (videoUrl || undefined) : undefined, // v23.7: Individual highlight video URL
      players
    })

    toast('Event updated', 'success')
    onClose()
  }

  const handleDelete = () => {
    if (!event || editingEvtIdx === null) return
    if (!confirm(`Delete event #${editingEvtIdx + 1}?`)) return

    deleteEvent(editingEvtIdx)
    toast('Event deleted', 'success')
    onClose()
  }

  const handleAddPlayer = (player: Player) => {
    setPlayers([...players, player])
  }

  const handleRemovePlayer = (player: Player) => {
    setPlayers(players.filter(p => !(p.num === player.num && p.team === player.team)))
  }

  if (!isOpen || !event) return null

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50" onClick={onClose}>
      <div
        className="bg-card border border-border rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold">Edit Event #{editingEvtIdx !== null ? editingEvtIdx + 1 : ''}</h2>
          <button
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground"
          >
            ×
          </button>
        </div>

        <div className="space-y-4">
          {/* Event Type */}
          <div>
            <label className="text-xs text-muted-foreground uppercase mb-2 block">Event Type</label>
            <SearchableSelect
              options={[
                { value: '', label: '--', searchText: '' },
                ...EVENT_TYPES.map((type) => ({
                  value: type,
                  label: type,
                  searchText: type,
                })),
              ]}
              value={eventType}
              onChange={(val) => setEventType(val as EventType)}
              placeholder="--"
            />
          </div>

          {/* Team */}
          <div className="flex gap-2">
            <Button
              variant={team === 'home' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setTeam('home')}
              className={cn('flex-1', team === 'home' && 'bg-blue-600 hover:bg-blue-700')}
            >
              Home
            </Button>
            <Button
              variant={team === 'away' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setTeam('away')}
              className={cn('flex-1', team === 'away' && 'bg-red-600 hover:bg-red-700')}
            >
              Away
            </Button>
          </div>

          {/* Time */}
          <div className="grid grid-cols-2 gap-2">
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
          </div>

          {/* Details */}
          {eventType && (
            <>
              {detail1Options.length > 0 && (
                <div>
                  <label className="text-xs text-muted-foreground block mb-1">Detail 1</label>
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
                  <label className="text-xs text-muted-foreground block mb-1">Detail 2</label>
                  <select
                    value={detail2}
                    onChange={(e) => setDetail2(e.target.value)}
                    className="w-full px-2 py-1 text-sm bg-input border border-border rounded"
                  >
                    <option value="">--</option>
                    {detail2Options.map((opt) => (
                      <option key={opt} value={opt}>
                        {opt}
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </>
          )}

          {/* Zone, Success, Strength */}
          <div className="grid grid-cols-3 gap-2">
            <div>
              <label className="text-xs text-muted-foreground block mb-1">Zone</label>
              <SearchableSelect
                options={[
                  { value: '', label: '--', searchText: '' },
                  { value: 'o', label: 'Offensive', searchText: 'offensive' },
                  { value: 'n', label: 'Neutral', searchText: 'neutral' },
                  { value: 'd', label: 'Defensive', searchText: 'defensive' },
                ]}
                value={zone}
                onChange={(val) => setZone(val as Zone)}
                placeholder="--"
              />
            </div>
            <div>
              <label className="text-xs text-muted-foreground block mb-1">Success</label>
              <select
                value={success}
                onChange={(e) => setSuccess(e.target.value as 's' | 'u' | '')}
                className="w-full px-2 py-1 text-sm bg-input border border-border rounded"
              >
                <option value="">--</option>
                <option value="s">Success</option>
                <option value="u">Unsuccess</option>
              </select>
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

          {/* Highlight */}
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="editHighlight"
              checked={isHighlight}
              onChange={(e) => {
                setIsHighlight(e.target.checked)
                if (!e.target.checked) setVideoUrl('')
              }}
            />
            <label htmlFor="editHighlight" className="text-xs">
              ⭐ Highlight
            </label>
          </div>

          {/* Video URL for highlights (v23.7) */}
          {isHighlight && (
            <div className="space-y-1">
              <label htmlFor="editVideoUrl" className="text-xs text-muted-foreground">
                YouTube URL for this highlight:
              </label>
              <input
                type="text"
                id="editVideoUrl"
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
                placeholder="https://youtube.com/watch?v=..."
                className="w-full px-2 py-1 text-xs bg-input border border-border rounded text-foreground"
              />
            </div>
          )}

          {/* Players */}
          <div>
            <label className="text-xs text-muted-foreground uppercase mb-2 block">Players</label>
            <div className="flex flex-wrap gap-1 p-2 bg-muted/50 rounded min-h-[40px] mb-2">
              {players.length === 0 ? (
                <span className="text-xs text-muted-foreground">No players</span>
              ) : (
                players.map((player, i) => (
                  <PlayerChip
                    key={`${player.team}-${player.num}-${i}`}
                    player={player}
                    role={player.role}
                    onRemove={() => handleRemovePlayer(player)}
                  />
                ))
              )}
            </div>
            <div>
              <PlayerSelectDropdown 
                team={team} 
                currentPlayers={players}
                onPlayerSelect={handleAddPlayer}
                evtTeam={team}
              />
            </div>
          </div>
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
