// src/app/(dashboard)/leaders/page.tsx
import Link from 'next/link'
import { getPointsLeaders, getGoalsLeaders, getAssistsLeaders } from '@/lib/supabase/queries/players'
import { Trophy, Target, Sparkles, TrendingUp } from 'lucide-react'
import { cn } from '@/lib/utils'

export const revalidate = 300

export const metadata = {
  title: 'Leaders | BenchSight',
  description: 'NORAD Hockey League scoring leaders',
}

export default async function LeadersPage({
  searchParams,
}: {
  searchParams: Promise<{ tab?: string }>
}) {
  const params = await searchParams
  const activeTab = params.tab || 'points'
  
  const [pointsLeaders, goalsLeaders, assistsLeaders] = await Promise.all([
    getPointsLeaders(20),
    getGoalsLeaders(20),
    getAssistsLeaders(20)
  ])

  const tabs = [
    { id: 'points', label: 'Points', icon: TrendingUp, color: 'text-primary' },
    { id: 'goals', label: 'Goals', icon: Target, color: 'text-goal' },
    { id: 'assists', label: 'Assists', icon: Sparkles, color: 'text-assist' },
  ]

  const getActiveLeaders = () => {
    switch (activeTab) {
      case 'goals':
        return goalsLeaders
      case 'assists':
        return assistsLeaders
      default:
        return pointsLeaders
    }
  }

  const leaders = getActiveLeaders()

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="font-display text-2xl font-bold tracking-wider uppercase flex items-center gap-3">
          <span className="w-1 h-6 bg-assist rounded" />
          Scoring Leaders
        </h1>
        <p className="text-sm text-muted-foreground mt-2 ml-4">
          Top scorers in the current season
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-border pb-2">
        {tabs.map((tab) => {
          const Icon = tab.icon
          const isActive = activeTab === tab.id
          return (
            <Link
              key={tab.id}
              href={`/leaders?tab=${tab.id}`}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-t-lg transition-all',
                isActive
                  ? 'bg-card border border-b-0 border-border -mb-[1px]'
                  : 'hover:bg-muted/50'
              )}
            >
              <Icon className={cn('w-4 h-4', isActive ? tab.color : 'text-muted-foreground')} />
              <span className={cn(
                'font-display text-sm',
                isActive ? 'text-foreground font-semibold' : 'text-muted-foreground'
              )}>
                {tab.label}
              </span>
            </Link>
          )
        })}
      </div>

      {/* Leaders Table */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-accent border-b-2 border-border">
                <th className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider w-16">
                  Rank
                </th>
                <th className="px-4 py-3 text-left font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Player
                </th>
                <th className="px-4 py-3 text-left font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Team
                </th>
                <th className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  GP
                </th>
                <th className="px-4 py-3 text-center font-display text-xs font-semibold text-goal uppercase tracking-wider">
                  G
                </th>
                <th className="px-4 py-3 text-center font-display text-xs font-semibold text-assist uppercase tracking-wider">
                  A
                </th>
                <th className="px-4 py-3 text-center font-display text-xs font-semibold text-primary uppercase tracking-wider">
                  P
                </th>
                <th className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Per Game
                </th>
              </tr>
            </thead>
            <tbody>
              {leaders.map((player, index) => {
                const rank = index + 1
                const isTop3 = rank <= 3
                const gp = player.games_played || 1
                const mainStat = activeTab === 'goals' 
                  ? player.goals 
                  : activeTab === 'assists' 
                    ? player.assists 
                    : player.points
                const perGame = (mainStat / gp).toFixed(2)

                return (
                  <tr
                    key={player.player_id}
                    className={cn(
                      'border-b border-border transition-colors hover:bg-muted/50',
                      rank % 2 === 0 && 'bg-accent/30'
                    )}
                  >
                    <td className="px-4 py-3 text-center">
                      <span className={cn(
                        'font-display font-bold',
                        isTop3 ? 'text-lg text-assist' : 'text-muted-foreground'
                      )}>
                        {rank}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <Link
                        href={`/players/${player.player_id}`}
                        className="font-display text-sm text-foreground hover:text-primary transition-colors"
                      >
                        {player.player_name}
                      </Link>
                    </td>
                    <td className="px-4 py-3 text-sm text-muted-foreground">
                      {player.team_name}
                    </td>
                    <td className="px-4 py-3 text-center font-mono text-sm text-muted-foreground">
                      {player.games_played}
                    </td>
                    <td className={cn(
                      'px-4 py-3 text-center font-mono text-sm font-semibold',
                      activeTab === 'goals' ? 'text-xl text-goal' : 'text-goal'
                    )}>
                      {player.goals}
                    </td>
                    <td className={cn(
                      'px-4 py-3 text-center font-mono text-sm',
                      activeTab === 'assists' ? 'text-xl font-semibold text-assist' : 'text-assist'
                    )}>
                      {player.assists}
                    </td>
                    <td className={cn(
                      'px-4 py-3 text-center font-mono font-bold',
                      activeTab === 'points' ? 'text-xl text-primary' : 'text-sm text-primary'
                    )}>
                      {player.points}
                    </td>
                    <td className="px-4 py-3 text-center font-mono text-sm text-muted-foreground">
                      {perGame}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
