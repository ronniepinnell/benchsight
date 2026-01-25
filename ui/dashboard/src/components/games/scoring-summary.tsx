'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Target, ChevronDown, Play } from 'lucide-react'
import { cn } from '@/lib/utils'
import { TeamLogo } from '@/components/teams/team-logo'
import { PlayerPhoto } from '@/components/players/player-photo'
import { MiniShotRink } from '@/components/games/mini-shot-rink'

interface GoalAssist {
  player_id: string
  player_name: string
  assist_type: 'primary' | 'secondary'
  playerLink?: string | null
}

interface ProcessedGoal {
  id: string
  period: number
  timeStr: string
  scorerName: string | null
  scorerId: string | null
  scorerImage: string | null
  scorerLink: string | null
  scoringTeam: {
    team_name: string
    team_logo: string | null
    team_cd?: string
    primary_color?: string
    team_color1?: string
    team_color2?: string
  } | null
  assists: GoalAssist[]
  runningScore: { home: number; away: number }
  videoLink: string | null
  // Expanded details
  strength?: string | null
  shotX?: number | null
  shotY?: number | null
  isRush?: boolean
  isRebound?: boolean
  goalieName?: string | null
}

interface ScoringSummaryProps {
  goals: ProcessedGoal[]
  homeTeamName: string
  awayTeamName: string
  hasVideo: boolean
  gameId: number
}

export function ScoringSummary({
  goals,
  homeTeamName,
  awayTeamName,
  hasVideo,
  gameId
}: ScoringSummaryProps) {
  const [expandedGoalId, setExpandedGoalId] = useState<string | null>(null)

  if (goals.length === 0) return null

  // Group goals by period
  const goalsByPeriod = new Map<number, ProcessedGoal[]>()
  goals.forEach((goal) => {
    if (!goalsByPeriod.has(goal.period)) {
      goalsByPeriod.set(goal.period, [])
    }
    goalsByPeriod.get(goal.period)!.push(goal)
  })

  const periods = Array.from(goalsByPeriod.keys()).sort((a, b) => a - b)

  return (
    <div className="bg-card rounded-xl border border-border overflow-hidden">
      <div className="px-4 py-3 bg-accent border-b border-border">
        <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
          <Target className="w-4 h-4 text-goal" />
          Scoring Summary ({goals.length})
        </h2>
      </div>
      <div className="divide-y divide-border">
        {periods.map((period) => {
          const periodGoals = goalsByPeriod.get(period)!
          const periodLabel = period > 3 ? `OT${period - 3}` : `Period ${period}`

          return (
            <div key={period}>
              {/* Period Header */}
              <div className="px-4 py-2 bg-muted/50 border-b border-border">
                <h3 className="font-display text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  {periodLabel} ({periodGoals.length} {periodGoals.length === 1 ? 'Goal' : 'Goals'})
                </h3>
              </div>
              {/* Goals in this period */}
              {periodGoals.map((goal) => {
                const isExpanded = expandedGoalId === goal.id
                const scoreStr = `${goal.runningScore.away}-${goal.runningScore.home}`

                return (
                  <div key={goal.id}>
                    {/* Goal Row - Clickable to expand */}
                    <button
                      onClick={() => setExpandedGoalId(isExpanded ? null : goal.id)}
                      className={cn(
                        'w-full p-4 flex items-center gap-3 hover:bg-muted/30 transition-colors text-left',
                        isExpanded && 'bg-muted/20'
                      )}
                    >
                      {/* Time */}
                      <div className="w-14 text-center flex-shrink-0">
                        <div className="font-mono text-sm font-semibold text-foreground">{goal.timeStr}</div>
                      </div>

                      {/* Team Logo */}
                      {goal.scoringTeam && (
                        <TeamLogo
                          src={goal.scoringTeam.team_logo}
                          name={goal.scoringTeam.team_name}
                          abbrev={goal.scoringTeam.team_cd}
                          primaryColor={goal.scoringTeam.primary_color || goal.scoringTeam.team_color1}
                          secondaryColor={goal.scoringTeam.team_color2}
                          size="sm"
                        />
                      )}

                      {/* Player Photo */}
                      <PlayerPhoto
                        src={goal.scorerImage}
                        name={goal.scorerName || 'Unknown'}
                        primaryColor={goal.scoringTeam?.primary_color || goal.scoringTeam?.team_color1}
                        size="sm"
                      />

                      {/* Player Info */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="inline-flex items-center px-1.5 py-0.5 rounded bg-green-500/20 text-green-600 dark:text-green-400 text-xs font-bold uppercase tracking-wide">
                            Goal
                          </span>
                          <span className="font-display text-sm font-semibold text-foreground truncate">
                            {goal.scorerName || 'Unknown Scorer'}
                          </span>
                        </div>
                        {/* Compact assists display */}
                        <div className="text-xs text-muted-foreground mt-0.5 truncate">
                          {goal.assists.length > 0 ? (
                            <>Assisted by: {goal.assists.map(a => a.player_name).join(', ')}</>
                          ) : (
                            <span className="italic">Unassisted</span>
                          )}
                        </div>
                      </div>

                      {/* Running Score */}
                      <div className="font-mono text-lg font-bold text-foreground tabular-nums flex-shrink-0">
                        {scoreStr}
                      </div>

                      {/* Expand Icon */}
                      <ChevronDown className={cn(
                        'w-5 h-5 text-muted-foreground transition-transform flex-shrink-0',
                        isExpanded && 'rotate-180'
                      )} />
                    </button>

                    {/* Expanded Details Panel */}
                    {isExpanded && (
                      <div className="bg-muted/10 border-t border-border/50 p-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {/* Left: Shot Location */}
                          <div className="space-y-2">
                            <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                              <Target className="w-3 h-3" />
                              Shot Location
                            </div>
                            <MiniShotRink
                              shotX={goal.shotX ?? null}
                              shotY={goal.shotY ?? null}
                              isGoal={true}
                            />
                          </div>

                          {/* Right: Goal Details */}
                          <div className="space-y-3">
                            {/* Scorer with link */}
                            <div>
                              <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">Scorer</div>
                              {goal.scorerLink ? (
                                <Link
                                  href={goal.scorerLink}
                                  className="font-display text-sm font-semibold text-foreground hover:text-primary transition-colors"
                                >
                                  {goal.scorerName}
                                </Link>
                              ) : (
                                <span className="font-display text-sm font-semibold text-foreground">
                                  {goal.scorerName || 'Unknown'}
                                </span>
                              )}
                            </div>

                            {/* Assists with links */}
                            <div>
                              <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">Assists</div>
                              {goal.assists.length > 0 ? (
                                <div className="space-y-1">
                                  {goal.assists.map((assist, idx) => (
                                    <div key={idx} className="text-sm">
                                      {assist.playerLink ? (
                                        <Link
                                          href={assist.playerLink}
                                          className="text-foreground hover:text-primary transition-colors"
                                        >
                                          {assist.player_name}
                                        </Link>
                                      ) : (
                                        <span className="text-foreground">{assist.player_name}</span>
                                      )}
                                      <span className="text-xs text-muted-foreground ml-1">
                                        ({assist.assist_type})
                                      </span>
                                    </div>
                                  ))}
                                </div>
                              ) : (
                                <span className="text-sm text-muted-foreground italic">Unassisted</span>
                              )}
                            </div>

                            {/* Goalie */}
                            {goal.goalieName && (
                              <div>
                                <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">Goalie</div>
                                <span className="text-sm text-foreground">{goal.goalieName}</span>
                              </div>
                            )}

                            {/* Tags */}
                            <div className="flex flex-wrap gap-1.5">
                              {goal.strength && goal.strength !== 'Even' && goal.strength !== 'EV' && (
                                <span className={cn(
                                  'px-2 py-0.5 rounded text-xs font-medium',
                                  goal.strength === 'PP' ? 'bg-yellow-500/20 text-yellow-600 dark:text-yellow-400' :
                                  goal.strength === 'SH' ? 'bg-red-500/20 text-red-600 dark:text-red-400' :
                                  'bg-muted text-muted-foreground'
                                )}>
                                  {goal.strength}
                                </span>
                              )}
                              {goal.isRush && (
                                <span className="px-2 py-0.5 rounded bg-purple-500/20 text-purple-600 dark:text-purple-400 text-xs font-medium">
                                  Rush
                                </span>
                              )}
                              {goal.isRebound && (
                                <span className="px-2 py-0.5 rounded bg-orange-500/20 text-orange-600 dark:text-orange-400 text-xs font-medium">
                                  Rebound
                                </span>
                              )}
                            </div>

                            {/* Video Link */}
                            {goal.videoLink && hasVideo && (
                              <div className="pt-2">
                                <a
                                  href={goal.videoLink}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="inline-flex items-center gap-2 px-3 py-1.5 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors text-sm"
                                >
                                  <Play className="w-4 h-4" />
                                  Watch Goal
                                </a>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          )
        })}
      </div>
    </div>
  )
}
