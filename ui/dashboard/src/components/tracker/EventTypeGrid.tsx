'use client'

/**
 * Event Type Grid Component
 * 
 * Grid of event type buttons with keyboard shortcuts
 */

import { useState } from 'react'
import type { EventType } from '@/lib/tracker/types'
import { MAIN_EVENT_TYPES, EVENT_TYPES, EVENT_HOTKEYS, EVENT_TYPE_COLORS } from '@/lib/tracker/constants'
import { useTrackerStore } from '@/lib/tracker/state'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

export function EventTypeGrid() {
  const [showAll, setShowAll] = useState(false)
  const { curr, setCurrentType } = useTrackerStore()

  const mainTypes = MAIN_EVENT_TYPES
  const extraTypes = EVENT_TYPES.filter(t => !mainTypes.includes(t))

  const handleTypeClick = (type: EventType) => {
    setCurrentType(type)
  }

  return (
    <div className="space-y-2">
      {/* Main event types */}
      <div className="grid grid-cols-4 gap-1">
        {mainTypes.map((type) => {
          const hotkey = EVENT_HOTKEYS[type]
          const isActive = curr.type === type
          const color = EVENT_TYPE_COLORS[type]

          return (
            <Button
              key={type}
              variant={isActive ? 'default' : 'outline'}
              size="sm"
              onClick={() => handleTypeClick(type)}
              className={cn(
                'h-auto py-2 px-1 flex flex-col items-center text-xs',
                isActive && 'font-bold'
              )}
              style={
                isActive
                  ? {
                      backgroundColor: color,
                      borderColor: color,
                      color: '#fff'
                    }
                  : {
                      borderColor: color
                    }
              }
            >
              <span>{type.replace('_Entry_Exit', '')}</span>
              {hotkey && (
                <kbd className="text-[10px] px-1 py-0.5 bg-background/50 rounded text-muted-foreground">
                  {hotkey}
                </kbd>
              )}
            </Button>
          )
        })}

        {/* Show more button */}
        {extraTypes.length > 0 && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowAll(!showAll)}
            className="h-auto py-2 px-1 flex flex-col items-center text-xs border-dashed"
          >
            {showAll ? '◀ Less' : 'More ▶'}
          </Button>
        )}
      </div>

      {/* Extra event types */}
      {showAll && extraTypes.length > 0 && (
        <div className="grid grid-cols-4 gap-1 border-t pt-2">
          {extraTypes.map((type) => {
            const hotkey = EVENT_HOTKEYS[type]
            const isActive = curr.type === type
            const color = EVENT_TYPE_COLORS[type]

            return (
              <Button
                key={type}
                variant={isActive ? 'default' : 'outline'}
                size="sm"
                onClick={() => handleTypeClick(type)}
                className={cn(
                  'h-auto py-2 px-1 flex flex-col items-center text-xs',
                  isActive && 'font-bold'
                )}
                style={
                  isActive
                    ? {
                        backgroundColor: color,
                        borderColor: color,
                        color: '#fff'
                      }
                    : {
                        borderColor: color
                      }
                }
              >
                <span>{type}</span>
                {hotkey && (
                  <kbd className="text-[10px] px-1 py-0.5 bg-background/50 rounded text-muted-foreground">
                    {hotkey}
                  </kbd>
                )}
              </Button>
            )
          })}
        </div>
      )}
    </div>
  )
}
