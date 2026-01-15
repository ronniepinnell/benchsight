'use client'

import * as Tabs from '@radix-ui/react-tabs'
import { OverviewTab } from './goalie-tabs/overview-tab'
import { SeasonTab } from './goalie-tabs/season-tab'
import { CareerTab } from './goalie-tabs/career-tab'
import { AdvancedTab } from './goalie-tabs/advanced-tab'
import dynamic from 'next/dynamic'

// Dynamically import SavesTab to handle async server component
// Disable SSR to avoid client/server boundary issues during build
const SavesTabWrapper = dynamic(
  () => import('./goalie-tabs/saves-tab-wrapper').then(mod => ({ default: mod.SavesTabWrapper })),
  { 
    ssr: false,
    loading: () => <div className="bg-card rounded-xl border border-border p-8 text-center"><p className="text-muted-foreground">Loading saves data...</p></div>
  }
)

interface GoalieProfileTabsProps {
  goalieId: string
  seasonId: string
  gameLog: any[]
  currentStats: any
  career: any
  gameStats: any[]
  trendData: any[]
  advancedStats: any
  defaultTab?: string
}

export function GoalieProfileTabs({
  goalieId,
  seasonId,
  gameLog,
  currentStats,
  career,
  gameStats,
  trendData,
  advancedStats,
  defaultTab = 'overview',
}: GoalieProfileTabsProps) {
  return (
    <Tabs.Root defaultValue={defaultTab} className="space-y-4">
      <Tabs.List className="flex gap-2 border-b border-border">
        <Tabs.Trigger
          value="overview"
          className="px-4 py-2 text-sm font-display border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:text-primary text-muted-foreground data-[state=active]:text-foreground transition-colors"
        >
          Overview
        </Tabs.Trigger>
        <Tabs.Trigger
          value="season"
          className="px-4 py-2 text-sm font-display border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:text-primary text-muted-foreground data-[state=active]:text-foreground transition-colors"
        >
          Season
        </Tabs.Trigger>
        <Tabs.Trigger
          value="career"
          className="px-4 py-2 text-sm font-display border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:text-primary text-muted-foreground data-[state=active]:text-foreground transition-colors"
        >
          Career
        </Tabs.Trigger>
        <Tabs.Trigger
          value="advanced"
          className="px-4 py-2 text-sm font-display border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:text-primary text-muted-foreground data-[state=active]:text-foreground transition-colors"
        >
          Advanced
        </Tabs.Trigger>
        <Tabs.Trigger
          value="saves"
          className="px-4 py-2 text-sm font-display border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:text-primary text-muted-foreground data-[state=active]:text-foreground transition-colors"
        >
          Saves
        </Tabs.Trigger>
      </Tabs.List>

      <Tabs.Content value="overview" className="space-y-6">
        <OverviewTab
          goalieId={goalieId}
          gameLog={gameLog}
          currentStats={currentStats}
          trendData={trendData}
        />
      </Tabs.Content>

      <Tabs.Content value="season" className="space-y-6">
        <SeasonTab
          goalieId={goalieId}
          seasonId={seasonId}
          gameLog={gameLog}
          gameStats={gameStats}
        />
      </Tabs.Content>

      <Tabs.Content value="career" className="space-y-6">
        <CareerTab
          career={career}
          gameLog={gameLog}
        />
      </Tabs.Content>

      <Tabs.Content value="advanced" className="space-y-6">
        <AdvancedTab
          advancedStats={advancedStats}
          gameStats={gameStats}
        />
      </Tabs.Content>

      <Tabs.Content value="saves" className="space-y-6">
        <SavesTabWrapper goalieId={goalieId} />
      </Tabs.Content>
    </Tabs.Root>
  )
}
