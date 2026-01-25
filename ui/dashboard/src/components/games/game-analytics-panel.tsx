'use client'

import { BarChart3, Target, TrendingUp, Shield } from 'lucide-react'
import { cn } from '@/lib/utils'

interface TeamStats {
  team_name: string
  shots?: number
  goals?: number
  corsi_for?: number
  corsi_against?: number
  fenwick_for?: number
  fenwick_against?: number
  xg_for?: number
  xg_against?: number
  high_danger_chances?: number
  scoring_chances?: number
  saves?: number
  save_percentage?: number
}

interface GameAnalyticsPanelProps {
  homeStats?: TeamStats | null
  awayStats?: TeamStats | null
  homeTeamName?: string
  awayTeamName?: string
  homeColor?: string
  awayColor?: string
  className?: string
}

export function GameAnalyticsPanel({
  homeStats,
  awayStats,
  homeTeamName = 'Home',
  awayTeamName = 'Away',
  homeColor = '#3b82f6', // blue-500 fallback
  awayColor = '#ef4444', // red-500 fallback
  className
}: GameAnalyticsPanelProps) {
  // Calculate derived stats
  const homeCorsiFor = homeStats?.corsi_for || 0
  const homeCorsiAgainst = homeStats?.corsi_against || 0
  const awayCorsiFor = awayStats?.corsi_for || 0
  const awayCorsiAgainst = awayStats?.corsi_against || 0

  const homeCorsiFPercent = homeCorsiFor + homeCorsiAgainst > 0
    ? ((homeCorsiFor / (homeCorsiFor + homeCorsiAgainst)) * 100).toFixed(1)
    : '--'
  const awayCorsiFPercent = awayCorsiFor + awayCorsiAgainst > 0
    ? ((awayCorsiFor / (awayCorsiFor + awayCorsiAgainst)) * 100).toFixed(1)
    : '--'

  const homeXG = homeStats?.xg_for || 0
  const awayXG = awayStats?.xg_for || 0

  const stats = [
    {
      label: 'Shots',
      home: homeStats?.shots || 0,
      away: awayStats?.shots || 0,
      icon: Target,
    },
    {
      label: 'Goals',
      home: homeStats?.goals || 0,
      away: awayStats?.goals || 0,
      icon: Target,
      highlight: true,
    },
    {
      label: 'Expected Goals (xG)',
      home: homeXG.toFixed(2),
      away: awayXG.toFixed(2),
      icon: TrendingUp,
    },
    {
      label: 'Corsi For %',
      home: homeCorsiFPercent,
      away: awayCorsiFPercent,
      icon: BarChart3,
      suffix: '%',
    },
    {
      label: 'High Danger Chances',
      home: homeStats?.high_danger_chances || 0,
      away: awayStats?.high_danger_chances || 0,
      icon: Target,
    },
    {
      label: 'Scoring Chances',
      home: homeStats?.scoring_chances || 0,
      away: awayStats?.scoring_chances || 0,
      icon: Target,
    },
    {
      label: 'Save %',
      home: homeStats?.save_percentage ? (homeStats.save_percentage * 100).toFixed(1) : '--',
      away: awayStats?.save_percentage ? (awayStats.save_percentage * 100).toFixed(1) : '--',
      icon: Shield,
      suffix: '%',
    },
  ]

  return (
    <div className={cn('bg-card rounded-xl border border-border overflow-hidden', className)}>
      <div className="px-4 py-3 bg-accent border-b border-border">
        <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
          <BarChart3 className="w-4 h-4" />
          Game Analytics Summary
        </h2>
      </div>

      <div className="p-4">
        {/* Team Headers */}
        <div className="grid grid-cols-3 gap-4 mb-4 text-center">
          <div className="font-display font-semibold text-sm">
            {awayTeamName}
          </div>
          <div className="font-display font-semibold text-xs text-muted-foreground uppercase">
            Stat
          </div>
          <div className="font-display font-semibold text-sm">
            {homeTeamName}
          </div>
        </div>

        {/* Stats Rows */}
        <div className="space-y-2">
          {stats.map((stat, idx) => {
            const homeVal = typeof stat.home === 'number' ? stat.home : parseFloat(stat.home as string) || 0
            const awayVal = typeof stat.away === 'number' ? stat.away : parseFloat(stat.away as string) || 0
            const total = homeVal + awayVal
            const homeWidth = total > 0 ? (homeVal / total) * 100 : 50
            const awayWidth = total > 0 ? (awayVal / total) * 100 : 50

            return (
              <div key={idx} className="space-y-1">
                <div className="grid grid-cols-3 gap-4 text-center items-center">
                  <div className={cn(
                    'text-lg font-bold tabular-nums',
                    stat.highlight && awayVal > homeVal && 'text-goal'
                  )}>
                    {stat.away}{stat.suffix || ''}
                  </div>
                  <div className="text-xs text-muted-foreground flex items-center justify-center gap-1">
                    <stat.icon className="w-3 h-3" />
                    {stat.label}
                  </div>
                  <div className={cn(
                    'text-lg font-bold tabular-nums',
                    stat.highlight && homeVal > awayVal && 'text-goal'
                  )}>
                    {stat.home}{stat.suffix || ''}
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="flex h-2 rounded-full overflow-hidden bg-muted">
                  <div
                    className="transition-all"
                    style={{ width: `${awayWidth}%`, backgroundColor: awayColor }}
                  />
                  <div
                    className="transition-all"
                    style={{ width: `${homeWidth}%`, backgroundColor: homeColor }}
                  />
                </div>
              </div>
            )
          })}
        </div>

        {/* Legend */}
        <div className="flex justify-center gap-6 mt-6 text-xs text-muted-foreground">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded" style={{ backgroundColor: awayColor }} />
            <span>{awayTeamName}</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded" style={{ backgroundColor: homeColor }} />
            <span>{homeTeamName}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
