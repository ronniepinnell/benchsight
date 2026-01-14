'use client'

import { useState } from 'react'
import { ChevronDown, ChevronUp, HelpCircle } from 'lucide-react'
import { cn } from '@/lib/utils'
import { getStatDefinition } from '@/lib/stats/definitions'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import { PercentileBadge } from '@/components/stats/percentile-badge'

interface StatCardProps {
  title: string
  icon: React.ReactNode
  children: React.ReactNode
  defaultExpanded?: boolean
  className?: string
}

export function StatCard({ 
  title, 
  icon, 
  children, 
  defaultExpanded = false,
  className 
}: StatCardProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded)

  return (
    <div className={cn('bg-card rounded-lg border border-border overflow-hidden', className)}>
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-muted/50 transition-colors"
      >
        <div className="flex items-center gap-2">
          {icon}
          <h3 className="font-display text-sm font-semibold text-foreground uppercase tracking-wider">
            {title}
          </h3>
        </div>
        {isExpanded ? (
          <ChevronUp className="w-4 h-4 text-muted-foreground" />
        ) : (
          <ChevronDown className="w-4 h-4 text-muted-foreground" />
        )}
      </button>
      {isExpanded && (
        <div className="px-4 pb-4 border-t border-border pt-3">
          {children}
        </div>
      )}
    </div>
  )
}

interface StatRowProps {
  label: string
  value: string | number
  highlight?: boolean
  color?: 'goal' | 'assist' | 'save' | 'primary' | 'muted'
  description?: string
  onClick?: () => void
  expandable?: boolean
  expandedContent?: React.ReactNode
  percentiles?: {
    overall?: number | null
    byRating?: number | null
    byPosition?: number | null
    byPositionRating?: number | null
  }
}

export function StatRow({ 
  label, 
  value, 
  highlight = false, 
  color,
  description,
  onClick,
  expandable = false,
  expandedContent,
  percentiles
}: StatRowProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const colorClasses = {
    goal: 'text-goal',
    assist: 'text-assist',
    save: 'text-save',
    primary: 'text-primary',
    muted: 'text-muted-foreground',
  }

  // Format value - show "-" for zero or missing values
  const formatValue = (val: string | number): string => {
    if (val === null || val === undefined || val === '') return '-'
    const num = typeof val === 'string' ? parseFloat(val) : val
    if (isNaN(num)) {
      // If it's already a formatted string (like "1.23%"), return it
      if (typeof val === 'string' && val.includes('%')) return val
      return '-'
    }
    // For zero values, show "-" unless it's a percentage
    if (num === 0 && !label.includes('%')) return '-'
    return String(val)
  }

  const displayValue = formatValue(value)

  // Get stat definition for tooltip - try multiple label variations
  const cleanLabel = label.replace(/\s*\(.*?\)\s*/g, '').trim()
  const statDef = getStatDefinition(cleanLabel) || getStatDefinition(label)
  const tooltipContent = statDef ? (
    <div className="space-y-2 max-w-sm">
      <div>
        <div className="font-semibold text-sm mb-1">{statDef.name}</div>
        <div className="text-xs text-muted-foreground leading-relaxed">{statDef.description}</div>
      </div>
      <div className="border-t border-border pt-2">
        <div className="text-xs font-semibold text-foreground mb-1">Formula:</div>
        <div className="text-xs text-muted-foreground font-mono bg-muted/30 p-2 rounded">{statDef.formula}</div>
      </div>
      {statDef.calculation && (
        <div className="border-t border-border pt-2">
          <div className="text-xs font-semibold text-foreground mb-1">Calculation Steps:</div>
          <div className="text-xs text-muted-foreground whitespace-pre-line leading-relaxed bg-muted/20 p-2 rounded">{statDef.calculation}</div>
        </div>
      )}
      {statDef.examples && (
        <div className="border-t border-border pt-2">
          <div className="text-xs font-semibold text-foreground mb-1">Example:</div>
          <div className="text-xs text-muted-foreground leading-relaxed italic">{statDef.examples}</div>
        </div>
      )}
      {statDef.benchmarks && (
        <div className="border-t border-border pt-2">
          <div className="text-xs font-semibold text-foreground mb-1">Performance Benchmarks:</div>
          <div className="text-xs text-muted-foreground leading-relaxed">{statDef.benchmarks}</div>
        </div>
      )}
      {statDef.interpretation && (
        <div className="border-t border-border pt-2">
          <div className="text-xs font-semibold text-foreground mb-1">How to Interpret:</div>
          <div className="text-xs text-muted-foreground leading-relaxed">{statDef.interpretation}</div>
        </div>
      )}
      {statDef.similarStats && statDef.similarStats.length > 0 && (
        <div className="border-t border-border pt-2">
          <div className="text-xs font-semibold text-foreground mb-1">Related Stats:</div>
          <div className="text-xs text-muted-foreground">{statDef.similarStats.join(', ')}</div>
        </div>
      )}
      <div className="border-t border-border pt-2">
        <div className="text-xs text-muted-foreground leading-relaxed">{statDef.context}</div>
      </div>
    </div>
  ) : description ? (
    <div className="text-sm max-w-xs">{description}</div>
  ) : null

  const handleClick = () => {
    if (expandable || onClick) {
      setIsExpanded(!isExpanded)
      onClick?.()
    }
  }

  return (
    <div>
      <div 
        className={cn(
          "flex justify-between items-center py-1.5 group",
          (expandable || onClick) && "cursor-pointer hover:bg-muted/30 rounded px-1 -mx-1 transition-colors"
        )}
        onClick={handleClick}
      >
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <span className="text-xs text-muted-foreground">{label}</span>
          {tooltipContent && (
            <TooltipProvider>
              <Tooltip content={tooltipContent} side="right">
                <HelpCircle className="w-3 h-3 text-muted-foreground hover:text-foreground transition-colors cursor-help flex-shrink-0" />
              </Tooltip>
            </TooltipProvider>
          )}
          {percentiles && (percentiles.overall !== null || percentiles.byPosition !== null || percentiles.byRating !== null || percentiles.byPositionRating !== null) && (
            <PercentileBadge
              overall={percentiles.overall}
              byRating={percentiles.byRating}
              byPosition={percentiles.byPosition}
              byPositionRating={percentiles.byPositionRating}
              size="sm"
            />
          )}
          {(expandable || onClick) && (
            <ChevronDown className={cn(
              "w-3 h-3 text-muted-foreground transition-transform flex-shrink-0 ml-auto",
              isExpanded && "transform rotate-180"
            )} />
          )}
        </div>
        <span className={cn(
          'font-mono text-sm flex-shrink-0 ml-2',
          highlight && 'font-semibold',
          color && colorClasses[color],
          displayValue === '-' && 'text-muted-foreground'
        )}>
          {displayValue}
        </span>
      </div>
      {isExpanded && expandedContent && (
        <div className="pl-4 pb-2 border-l-2 border-border ml-2">
          {expandedContent}
        </div>
      )}
    </div>
  )
}
