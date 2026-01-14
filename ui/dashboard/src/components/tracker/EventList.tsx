'use client'

/**
 * Event List Component
 * 
 * Display list of tracked events with ability to edit/delete
 */

import { useState } from 'react'
import { useTrackerStore } from '@/lib/tracker/state'
import { getZoneLabel } from '@/lib/tracker/utils/zone'
import { EditEventModal } from './EditEventModal'
import { cn } from '@/lib/utils'
import type { Event } from '@/lib/tracker/types'

export function EventList() {
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)
  
  const {
    events,
    period,
    editingEvtIdx,
    setEditingEvent,
    deleteEvent
  } = useTrackerStore()

  // Filter events by current period (can add filter UI later)
  // Sort by time within period
  const filteredEvents = events
    .filter(e => e.period === period)
    .sort((a, b) => {
      // Sort by start_time
      return a.start_time.localeCompare(b.start_time)
    })

  const handleEventClick = (event: Event) => {
    if (event.idx !== undefined) {
      setEditingEvent(event.idx)
      setIsEditModalOpen(true)
    }
  }

  const handleDeleteEvent = (event: Event, e: React.MouseEvent) => {
    e.stopPropagation()
    if (event.idx !== undefined && confirm(`Delete event #${event.idx + 1}?`)) {
      deleteEvent(event.idx)
    }
  }

  if (filteredEvents.length === 0) {
    return (
      <div className="p-4 text-center text-sm text-muted-foreground">
        No events in this period. Log events to see them here.
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="grid grid-cols-[35px_45px_48px_80px_1fr_30px_24px] gap-2 px-3 py-2 bg-muted/50 border-b text-xs text-muted-foreground font-semibold sticky top-0">
        <div>#</div>
        <div>Time</div>
        <div>T</div>
        <div>Type</div>
        <div>Details</div>
        <div>Zone</div>
        <div></div>
      </div>

      {/* Event List */}
      <div className="flex-1 overflow-y-auto">
        {filteredEvents.map((event, index) => {
          const isActive = event.idx === editingEvtIdx
          const zone = event.zone ? getZoneLabel(event.zone) : ''
          const zoneClass = event.zone === 'o' ? 'bg-green-600' : event.zone === 'd' ? 'bg-red-600' : 'bg-yellow-600'

          return (
            <div
              key={event.idx ?? index}
              onClick={() => handleEventClick(event)}
              className={cn(
                'grid grid-cols-[35px_45px_48px_80px_1fr_30px_24px] gap-2 px-3 py-2 border-b text-xs cursor-pointer hover:bg-muted/50 transition-colors group',
                isActive && 'bg-accent/10 border-accent'
              )}
            >
              {/* Index */}
              <div className="font-mono text-accent">
                {(event.idx ?? index) + 1}
              </div>

              {/* Time */}
              <div className="font-mono text-muted-foreground">
                {event.start_time}
              </div>

              {/* Team */}
              <div className={cn(
                'font-bold text-xs',
                event.team === 'home' ? 'text-blue-500' : 'text-red-500'
              )}>
                {event.team === 'home' ? 'H' : 'A'}
              </div>

              {/* Type */}
              <div className="font-semibold truncate">
                {event.type}
              </div>

              {/* Details */}
              <div className="text-muted-foreground truncate">
                {event.detail1 && (
                  <span>{event.detail1}</span>
                )}
                {event.detail2 && (
                  <span className="ml-1">• {event.detail2}</span>
                )}
                {!event.detail1 && !event.detail2 && (
                  <span className="text-muted-foreground/50">—</span>
                )}
                {event.isHighlight && (
                  <span className="ml-1">⭐</span>
                )}
              </div>

              {/* Zone */}
              <div className="flex items-center justify-center">
                {zone && (
                  <span className={cn(
                    'px-1.5 py-0.5 rounded text-[10px] font-bold text-white',
                    zoneClass
                  )}>
                    {zone.substring(0, 1)}
                  </span>
                )}
              </div>

              {/* Delete button */}
              <button
                onClick={(e) => handleDeleteEvent(event, e)}
                className="text-xs text-destructive hover:text-destructive/80 opacity-0 hover:opacity-100 transition-opacity"
                title="Delete event"
              >
                ×
              </button>
            </div>
          )
        })}
      </div>

      {/* Footer with event count */}
      <div className="px-3 py-2 border-t bg-muted/30 text-xs text-muted-foreground sticky bottom-0">
        {filteredEvents.length} event{filteredEvents.length !== 1 ? 's' : ''} in period {period}
        {' • '}
        {events.length} total event{events.length !== 1 ? 's' : ''}
      </div>

      {/* Edit Modal */}
      <EditEventModal
        isOpen={isEditModalOpen}
        onClose={() => {
          setIsEditModalOpen(false)
          setEditingEvent(null)
        }}
      />
    </div>
  )
}
