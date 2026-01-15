'use client'

import * as Tabs from '@radix-ui/react-tabs'
import { OverviewTab } from './player-tabs/overview-tab'
import { SeasonTab } from './player-tabs/season-tab'
import { CareerTab } from './player-tabs/career-tab'

interface PlayerProfileTabsProps {
  playerId: string
  seasonId: string
  gameType: string
  gameLog: any[]
  allRecentGames?: any[]
  playerStats: any
  career: any
  defaultTab?: string
  advancedStatsContent: React.ReactNode
  playerShots?: any[]
  opponentTeamsMap?: Map<string, any>
  playerTeamInfo?: any
  playerPosition?: string
  hasPlayedGoalie?: boolean
  hasPlayedSkater?: boolean
  goalieStats?: any
  isBoth?: boolean
  seasonStatsForCareer?: any[]
  goalieSeasonStatsForCareer?: any[]
  regularSeasonStats?: any[]
  playoffSeasonStats?: any[]
}

export function PlayerProfileTabs({
  playerId,
  seasonId,
  gameType,
  gameLog,
  allRecentGames = [],
  playerStats,
  career,
  defaultTab = 'overview',
  advancedStatsContent,
  playerShots = [],
  opponentTeamsMap,
  playerTeamInfo,
  playerPosition,
  hasPlayedGoalie = false,
  hasPlayedSkater = true,
  goalieStats,
  isBoth = false,
  seasonStatsForCareer = [],
  goalieSeasonStatsForCareer = [],
  regularSeasonStats = [],
  playoffSeasonStats = []
}: PlayerProfileTabsProps) {
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
      </Tabs.List>

      <Tabs.Content value="overview" className="space-y-6">
        <OverviewTab 
          playerId={playerId}
          playerStats={playerStats}
          gameLog={gameLog}
          allRecentGames={allRecentGames}
          playerShots={playerShots}
          opponentTeamsMap={opponentTeamsMap}
          playerTeamInfo={playerTeamInfo}
        />
      </Tabs.Content>

      <Tabs.Content value="season" className="space-y-6">
        <SeasonTab 
          playerStats={playerStats}
          gameLog={gameLog}
          seasonId={seasonId}
          hasPlayedGoalie={hasPlayedGoalie}
          hasPlayedSkater={hasPlayedSkater}
          isBoth={isBoth}
          goalieStats={goalieStats}
        />
      </Tabs.Content>

      <Tabs.Content value="career" className="space-y-6">
        <CareerTab 
          playerId={playerId}
          career={career}
          playerPosition={playerPosition}
          hasPlayedGoalie={hasPlayedGoalie}
          hasPlayedSkater={hasPlayedSkater}
          isBoth={isBoth}
          seasonStatsForCareer={seasonStatsForCareer}
          goalieSeasonStatsForCareer={goalieSeasonStatsForCareer}
          regularSeasonStats={regularSeasonStats}
          playoffSeasonStats={playoffSeasonStats}
        />
      </Tabs.Content>

      <Tabs.Content value="advanced" className="space-y-6">
        {advancedStatsContent}
      </Tabs.Content>
    </Tabs.Root>
  )
}
