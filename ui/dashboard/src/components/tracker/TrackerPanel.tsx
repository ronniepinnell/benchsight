'use client'

/**
 * Tracker Panel Component
 * 
 * Side panel component for tracker (left/right panels)
 */

import { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface TrackerPanelProps {
  title: string
  children: ReactNode
  className?: string
}

export function TrackerPanel({ title, children, className }: TrackerPanelProps) {
  return (
    <div className={cn('flex flex-col border-r bg-card', className)}>
      {/* Panel header */}
      <div className="px-3 py-2 border-b bg-muted/50">
        <h3 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          {title}
        </h3>
      </div>
      
      {/* Panel body */}
      <div className="flex-1 overflow-y-auto p-2">
        {children}
      </div>
    </div>
  )
}
