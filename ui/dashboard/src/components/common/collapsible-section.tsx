'use client'

import { useState, ReactNode } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'
import { cn } from '@/lib/utils'

interface CollapsibleSectionProps {
  title: string
  icon?: ReactNode
  children: ReactNode
  defaultExpanded?: boolean
  className?: string
  headerClassName?: string
  showBorder?: boolean
}

export function CollapsibleSection({
  title,
  icon,
  children,
  defaultExpanded = true,
  className,
  headerClassName,
  showBorder = true,
}: CollapsibleSectionProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded)

  return (
    <div className={cn('bg-card rounded-xl border border-border overflow-hidden', className)}>
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className={cn(
          'w-full px-4 py-3 bg-accent border-b border-border hover:bg-accent/80 transition-colors',
          headerClassName || 'flex items-center justify-between'
        )}
      >
        <div className="flex items-center gap-2">
          {icon}
          <h2 className="font-display text-sm font-semibold uppercase tracking-wider">
            {title}
          </h2>
        </div>
        {isExpanded ? (
          <ChevronUp className="w-4 h-4 text-muted-foreground" />
        ) : (
          <ChevronDown className="w-4 h-4 text-muted-foreground" />
        )}
      </button>
      {isExpanded && (
        <div className={cn(showBorder && 'border-t border-border')}>
          {children}
        </div>
      )}
    </div>
  )
}
