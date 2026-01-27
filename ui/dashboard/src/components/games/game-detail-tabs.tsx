'use client'

import * as React from 'react'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Activity, Target, Clock, ListOrdered, BarChart3 } from 'lucide-react'
import { cn } from '@/lib/utils'

interface GameDetailTabsProps {
  scoringContent?: React.ReactNode
  playByPlayContent?: React.ReactNode
  shotsContent?: React.ReactNode
  shiftsContent?: React.ReactNode
  analyticsContent?: React.ReactNode
  hasScoring?: boolean
  hasPlayByPlay: boolean
  hasShots: boolean
  hasShifts: boolean
  hasAnalytics?: boolean
  className?: string
}

export function GameDetailTabs({
  scoringContent,
  playByPlayContent,
  shotsContent,
  shiftsContent,
  analyticsContent,
  hasScoring = false,
  hasPlayByPlay,
  hasShots,
  hasShifts,
  hasAnalytics = false,
  className
}: GameDetailTabsProps) {
  // Determine default tab - prioritize play-by-play
  const defaultTab = hasPlayByPlay ? 'playbyplay' : hasShifts ? 'shifts' : hasShots ? 'shots' : hasAnalytics ? 'analytics' : 'scoring'

  // Count available tabs for responsive layout
  const tabCount = (hasScoring ? 1 : 0) + (hasPlayByPlay ? 1 : 0) + (hasShots ? 1 : 0) + (hasShifts ? 1 : 0) + (hasAnalytics ? 1 : 0)

  return (
    <Tabs defaultValue={defaultTab} className={cn('w-full', className)}>
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="border-b border-border bg-muted/30 px-4 py-3">
          <TabsList className={cn(
            'grid w-full max-w-2xl',
            tabCount === 1 && 'grid-cols-1',
            tabCount === 2 && 'grid-cols-2',
            tabCount === 3 && 'grid-cols-3',
            tabCount === 4 && 'grid-cols-4',
            tabCount === 5 && 'grid-cols-5'
          )}>
            {hasScoring && (
              <TabsTrigger value="scoring" icon={<ListOrdered className="w-4 h-4" />}>
                Scoring
              </TabsTrigger>
            )}

            {hasPlayByPlay && (
              <TabsTrigger value="playbyplay" icon={<Activity className="w-4 h-4" />}>
                Play-by-Play
              </TabsTrigger>
            )}

            {hasShots && (
              <TabsTrigger value="shots" icon={<Target className="w-4 h-4" />}>
                Shots
              </TabsTrigger>
            )}

            {hasShifts && (
              <TabsTrigger value="shifts" icon={<Clock className="w-4 h-4" />}>
                Shifts
              </TabsTrigger>
            )}

            {hasAnalytics && (
              <TabsTrigger value="analytics" icon={<BarChart3 className="w-4 h-4" />}>
                Analytics
              </TabsTrigger>
            )}
          </TabsList>
        </div>

        {hasScoring && (
          <TabsContent value="scoring" className="mt-0 p-0">
            {scoringContent}
          </TabsContent>
        )}

        {hasPlayByPlay && (
          <TabsContent value="playbyplay" className="mt-0 p-4">
            {playByPlayContent}
          </TabsContent>
        )}

        {hasShots && (
          <TabsContent value="shots" className="mt-0 p-4">
            {shotsContent}
          </TabsContent>
        )}

        {hasShifts && (
          <TabsContent value="shifts" className="mt-0 p-4">
            {shiftsContent}
          </TabsContent>
        )}

        {hasAnalytics && (
          <TabsContent value="analytics" className="mt-0 p-4">
            {analyticsContent}
          </TabsContent>
        )}
      </div>
    </Tabs>
  )
}
