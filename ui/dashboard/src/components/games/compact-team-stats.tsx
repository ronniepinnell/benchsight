'use client'

import Link from 'next/link'
import { BarChart3, ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'

interface TeamStatRow {
  label: string
  away: string | number
  home: string | number
  awayWins?: boolean
  homeWins?: boolean
}

interface CompactTeamStatsProps {
  awayTeamAbbrev: string
  homeTeamAbbrev: string
  stats: TeamStatRow[]
  viewAllLink?: string
  className?: string
}

export function CompactTeamStats({
  awayTeamAbbrev,
  homeTeamAbbrev,
  stats,
  viewAllLink,
  className
}: CompactTeamStatsProps) {
  if (stats.length === 0) {
    return null
  }

  return (
    <div className={cn('bg-card rounded-xl border border-border overflow-hidden flex flex-col flex-1', className)}>
      <div className="px-4 py-2 border-b border-border bg-accent/50 flex-shrink-0">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-muted-foreground" />
          <h2 className="font-display text-sm font-semibold uppercase tracking-wider">Team Stats</h2>
        </div>
      </div>

      <div className="overflow-x-auto flex-1">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border">
              <th className="px-3 py-1.5 text-left font-display text-xs text-muted-foreground">Stat</th>
              <th className="px-3 py-1.5 text-center font-display text-xs text-foreground w-16">{awayTeamAbbrev}</th>
              <th className="px-3 py-1.5 text-center font-display text-xs text-foreground w-16">{homeTeamAbbrev}</th>
            </tr>
          </thead>
          <tbody>
            {stats.map((stat, idx) => (
              <tr key={stat.label} className={cn(
                'hover:bg-muted/30 transition-colors',
                idx < stats.length - 1 && 'border-b border-border'
              )}>
                <td className="px-3 py-1.5 font-mono text-xs text-muted-foreground">{stat.label}</td>
                <td className={cn(
                  'px-3 py-1.5 text-center font-mono text-sm',
                  stat.awayWins ? 'font-bold text-foreground' : 'text-muted-foreground'
                )}>
                  {stat.away}
                </td>
                <td className={cn(
                  'px-3 py-1.5 text-center font-mono text-sm',
                  stat.homeWins ? 'font-bold text-foreground' : 'text-muted-foreground'
                )}>
                  {stat.home}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {viewAllLink && (
        <Link
          href={viewAllLink}
          className="flex items-center justify-center gap-1 px-4 py-2 text-sm text-primary hover:bg-muted/30 transition-colors border-t border-border"
        >
          View All Stats
          <ChevronRight className="w-4 h-4" />
        </Link>
      )}
    </div>
  )
}
