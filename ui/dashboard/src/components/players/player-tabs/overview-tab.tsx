import { Calendar, Target, TrendingUp, Sparkles } from 'lucide-react'
import Link from 'next/link'
import { GameCard } from '@/components/players/game-card'
import { TrendLineChart } from '@/components/charts/trend-line-chart'
import { StatRadarChart } from '@/components/charts/radar-chart'
import { EnhancedShotMap } from '@/components/charts/enhanced-shot-map'
import { CollapsibleSection } from '@/components/common/collapsible-section'
import { cn } from '@/lib/utils'

interface OverviewTabProps {
  playerId: string
  playerStats: any
  gameLog: any[]
  allRecentGames?: any[]
  playerShots?: any[]
  opponentTeamsMap?: Map<string, any>
  playerTeamInfo?: any
}

export function OverviewTab({ playerId, playerStats, gameLog, allRecentGames = [], playerShots = [], opponentTeamsMap, playerTeamInfo }: OverviewTabProps) {
  // Prepare trend data for last 10 games
  const recentGames = gameLog.slice(0, 10).reverse()
  const trendData = recentGames.map((game: any, index: number) => ({
    game: `Game ${index + 1}`,
    goals: Number(game.goals || 0),
    assists: Number(game.assists || 0),
    points: Number(game.points || 0),
  }))

  return (
    <div className="space-y-6">
      {/* Performance Trend */}
      {trendData.length > 0 && (
        <CollapsibleSection
          title="Performance Trend (Last 10 Games)"
          icon={<TrendingUp className="w-4 h-4" />}
          defaultExpanded={true}
        >
          <div className="p-6">
            <TrendLineChart
              data={trendData}
              xAxisKey="game"
              dataKeys={[
                { key: 'goals', name: 'Goals', color: 'hsl(var(--goal))' },
                { key: 'assists', name: 'Assists', color: 'hsl(var(--assist))' },
                { key: 'points', name: 'Points', color: 'hsl(var(--primary))' },
              ]}
              height={250}
            />
          </div>
        </CollapsibleSection>
      )}

      {/* Stat Breakdown Radar Chart */}
      {playerStats && (
        <CollapsibleSection
          title="Stat Breakdown"
          icon={<Target className="w-4 h-4" />}
          defaultExpanded={true}
        >
          <div className="p-6">
            <StatRadarChart
              data={[
                { category: 'Goals', value: Number(playerStats.goals || 0) },
                { category: 'Assists', value: Number(playerStats.assists || 0) },
                { category: 'Points', value: Number(playerStats.points || 0) },
                { category: 'Shots', value: Number(playerStats.shots || 0) },
                { category: 'Hits', value: Number(playerStats.hits || 0) },
                { category: 'Blocks', value: Number(playerStats.blocks || 0) },
              ]}
              height={300}
            />
          </div>
        </CollapsibleSection>
      )}

      {/* Shot Map */}
      {playerShots && playerShots.length > 0 && (
        <CollapsibleSection
          title="Shot Map"
          icon={<Target className="w-4 h-4" />}
          defaultExpanded={true}
        >
          <div className="p-6">
            <EnhancedShotMap 
              shots={playerShots}
              width={600}
              height={300}
              showFilters={true}
              title="Shot Map"
            />
          </div>
        </CollapsibleSection>
      )}

      {/* Quick Stats Grid */}
      {playerStats && (
        <CollapsibleSection
          title="Quick Stats"
          icon={<Target className="w-4 h-4" />}
          defaultExpanded={true}
        >
          <div className="p-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-card rounded-lg p-4 border border-border text-center">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <Target className="w-3 h-3 text-goal" />
                  <span className="text-xs font-mono text-goal uppercase">Goals</span>
                </div>
                <div className="font-mono text-2xl font-bold text-goal">{playerStats.goals || 0}</div>
              </div>
              <div className="bg-card rounded-lg p-4 border border-border text-center">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <Sparkles className="w-3 h-3 text-assist" />
                  <span className="text-xs font-mono text-assist uppercase">Assists</span>
                </div>
                <div className="font-mono text-2xl font-bold text-assist">{playerStats.assists || 0}</div>
              </div>
              <div className="bg-card rounded-lg p-4 border border-border text-center">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <TrendingUp className="w-3 h-3 text-primary" />
                  <span className="text-xs font-mono text-primary uppercase">Points</span>
                </div>
                <div className="font-mono text-2xl font-bold text-primary">{playerStats.points || 0}</div>
              </div>
              <div className="bg-card rounded-lg p-4 border border-border text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">P/G</div>
                <div className="font-mono text-2xl font-bold text-foreground">
                  {playerStats.points_per_game 
                    ? (typeof playerStats.points_per_game === 'number' 
                        ? playerStats.points_per_game.toFixed(2) 
                        : playerStats.points_per_game)
                    : (playerStats.games_played > 0 
                        ? Number((playerStats.points || 0) / playerStats.games_played).toFixed(2) 
                        : '-')}
                </div>
              </div>
            </div>
          </div>
        </CollapsibleSection>
      )}

      {/* Recent Games */}
      {(allRecentGames.length > 0 || gameLog.length > 0) && (
        <CollapsibleSection
          title="Recent Games"
          icon={<Calendar className="w-4 h-4" />}
          defaultExpanded={true}
          headerClassName="flex items-center justify-between"
        >
          <div className="p-6">
            <div className="mb-4 flex justify-end">
              <Link
                href={`/norad/players/${playerId}/games`}
                className="text-xs font-display text-primary hover:underline flex items-center gap-1"
              >
                View All Games
                <TrendingUp className="w-3 h-3" />
              </Link>
            </div>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {(allRecentGames.length > 0 ? allRecentGames : gameLog).slice(0, 6).map((game: any, index: number) => {
                // Determine if player's team was home or away
                const isHome = game.team_name && game.opponent_team_name 
                  ? (game.home_team_name === game.team_name || game.away_team_name !== game.team_name)
                  : undefined
                
                // Get opponent team info from map
                const opponentName = game.opponent_team_name || game.team_name || ''
                const opponentTeamInfo = opponentTeamsMap?.get(opponentName)
                
                return (
                  <GameCard
                    key={game.game_id || `game-${index}`}
                    game={game}
                    isHome={isHome}
                    teamInfo={playerTeamInfo}
                    opponentTeamInfo={opponentTeamInfo}
                  />
                )
              })}
            </div>
          </div>
        </CollapsibleSection>
      )}
    </div>
  )
}
