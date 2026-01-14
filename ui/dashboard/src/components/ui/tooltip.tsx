'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'

interface TooltipProps {
  children: React.ReactNode
  content: React.ReactNode
  side?: 'top' | 'bottom' | 'left' | 'right'
}

const TooltipProvider = ({ children }: { children: React.ReactNode }) => {
  return <>{children}</>
}

const Tooltip = ({ children, content, side = 'right' }: TooltipProps) => {
  const [isOpen, setIsOpen] = React.useState(false)
  
  return (
    <div 
      className="relative inline-block"
      onMouseEnter={() => setIsOpen(true)}
      onMouseLeave={() => setIsOpen(false)}
    >
      {children}
      {isOpen && (
        <div
          className={cn(
            'absolute z-50 min-w-[200px] max-w-sm rounded-md border border-border bg-popover p-3 text-sm text-popover-foreground shadow-lg',
            side === 'right' && 'left-full top-0 ml-2',
            side === 'left' && 'right-full top-0 mr-2',
            side === 'top' && 'bottom-full left-0 mb-2',
            side === 'bottom' && 'top-full left-0 mt-2'
          )}
        >
          {content}
        </div>
      )}
    </div>
  )
}

const TooltipTrigger = ({ children, asChild, ...props }: { children: React.ReactNode; asChild?: boolean }) => {
  return <>{children}</>
}

const TooltipContent = ({ children, className, ...props }: { children: React.ReactNode; className?: string }) => {
  return <>{children}</>
}

export { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider }
