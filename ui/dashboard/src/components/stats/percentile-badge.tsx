'use client'

import { TrendingUp, Users, Target, Award } from 'lucide-react'
import { cn } from '@/lib/utils'

interface PercentileBadgeProps {
  overall?: number | null
  byRating?: number | null
  byPosition?: number | null
  byPositionRating?: number | null
  showLabel?: boolean
  size?: 'sm' | 'md'
}

export function PercentileBadge({
  overall,
  byRating,
  byPosition,
  byPositionRating,
  showLabel = false,
  size = 'sm'
}: PercentileBadgeProps) {
  const getPercentileColor = (pct: number | null | undefined) => {
    if (pct === null || pct === undefined) return 'text-muted-foreground'
    if (pct >= 90) return 'text-save font-semibold'
    if (pct >= 75) return 'text-primary'
    if (pct >= 50) return 'text-foreground'
    if (pct >= 25) return 'text-muted-foreground'
    return 'text-muted-foreground/70'
  }

  const getPercentileBg = (pct: number | null | undefined) => {
    if (pct === null || pct === undefined) return 'bg-muted/20'
    if (pct >= 90) return 'bg-save/10'
    if (pct >= 75) return 'bg-primary/10'
    if (pct >= 50) return 'bg-muted/20'
    return 'bg-muted/10'
  }

  const sizeClasses = size === 'sm' ? 'text-[10px] px-1.5 py-0.5' : 'text-xs px-2 py-1'

  return (
    <div className="flex items-center gap-1 flex-wrap">
      {overall !== null && overall !== undefined && (
        <div className={cn(
          'inline-flex items-center gap-1 rounded font-mono',
          sizeClasses,
          getPercentileBg(overall),
          getPercentileColor(overall)
        )} title={`${overall.toFixed(1)}th percentile overall`}>
          <TrendingUp className="w-3 h-3" />
          {showLabel ? 'Overall' : ''}
          <span>{overall.toFixed(0)}</span>
        </div>
      )}
      {byPosition !== null && byPosition !== undefined && (
        <div className={cn(
          'inline-flex items-center gap-1 rounded font-mono',
          sizeClasses,
          getPercentileBg(byPosition),
          getPercentileColor(byPosition)
        )} title={`${byPosition.toFixed(1)}th percentile for position`}>
          <Users className="w-3 h-3" />
          {showLabel ? 'Pos' : ''}
          <span>{byPosition.toFixed(0)}</span>
        </div>
      )}
      {byRating !== null && byRating !== undefined && (
        <div className={cn(
          'inline-flex items-center gap-1 rounded font-mono',
          sizeClasses,
          getPercentileBg(byRating),
          getPercentileColor(byRating)
        )} title={`${byRating.toFixed(1)}th percentile for rating`}>
          <Target className="w-3 h-3" />
          {showLabel ? 'Rating' : ''}
          <span>{byRating.toFixed(0)}</span>
        </div>
      )}
      {byPositionRating !== null && byPositionRating !== undefined && (
        <div className={cn(
          'inline-flex items-center gap-1 rounded font-mono',
          sizeClasses,
          getPercentileBg(byPositionRating),
          getPercentileColor(byPositionRating)
        )} title={`${byPositionRating.toFixed(1)}th percentile for position/rating`}>
          <Award className="w-3 h-3" />
          {showLabel ? 'Pos/Rtg' : ''}
          <span>{byPositionRating.toFixed(0)}</span>
        </div>
      )}
    </div>
  )
}
