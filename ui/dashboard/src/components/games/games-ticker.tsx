// src/components/games/games-ticker.tsx
'use client'

import { useRef, useCallback, useEffect, useState } from 'react'
import Link from 'next/link'
import { ChevronLeft, ChevronRight, Play } from 'lucide-react'
import { cn } from '@/lib/utils'
import { TeamLogo } from '@/components/teams/team-logo'

interface TickerGame {
  game_id: string
  date: string
  home_team_id: string
  away_team_id: string
  home_team_name?: string
  away_team_name?: string
  home_total_goals?: number
  away_total_goals?: number
  game_time?: string
}

interface Team {
  team_id: string
  team_name: string
  team_cd: string
  team_logo?: string
  team_color1?: string
  team_color2?: string
}

interface GamesTickerProps {
  gamesByDate: Map<string, TickerGame[]>
  sortedDates: string[]
  today: string
  teamsMap: Map<string, Team>
  teamsByName: Map<string, Team>
  gamesWithVideos: Set<string>
}

function formatGameTime(gameTime: string | null | undefined): string {
  if (!gameTime) return 'TBD'
  const [hours, minutes] = gameTime.split(':')
  const h = parseInt(hours, 10)
  const h12 = h % 12 || 12
  return `${h12}:${minutes}`
}

export function GamesTicker({
  gamesByDate,
  sortedDates,
  today,
  teamsMap,
  teamsByName,
  gamesWithVideos
}: GamesTickerProps) {
  const scrollRef = useRef<HTMLDivElement>(null)
  const todayRef = useRef<HTMLDivElement>(null)
  const [mounted, setMounted] = useState(false)

  // Center on today/most recent games on mount
  useEffect(() => {
    setMounted(true)
    const timer = setTimeout(() => {
      if (todayRef.current && scrollRef.current) {
        const container = scrollRef.current
        const todayEl = todayRef.current
        const containerWidth = container.clientWidth
        const todayOffset = todayEl.offsetLeft
        const todayWidth = todayEl.clientWidth
        // Center the today element
        container.scrollLeft = todayOffset - (containerWidth / 2) + (todayWidth / 2)
      }
    }, 100)
    return () => clearTimeout(timer)
  }, [])

  const handleScrollLeft = useCallback(() => {
    scrollRef.current?.scrollBy({ left: -300, behavior: 'smooth' })
  }, [])

  const handleScrollRight = useCallback(() => {
    scrollRef.current?.scrollBy({ left: 300, behavior: 'smooth' })
  }, [])

  return (
    <div className="bg-card border-b border-border relative">
      {/* Left scroll button */}
      <button
        type="button"
        onClick={handleScrollLeft}
        className="absolute left-0 top-0 bottom-0 z-20 w-8 bg-card hover:bg-muted flex items-center justify-center border-r border-border cursor-pointer"
        aria-label="Scroll left"
      >
        <ChevronLeft className="w-5 h-5 pointer-events-none" />
      </button>

      {/* Right scroll button */}
      <button
        type="button"
        onClick={handleScrollRight}
        className="absolute right-0 top-0 bottom-0 z-20 w-8 bg-card hover:bg-muted flex items-center justify-center border-l border-border cursor-pointer"
        aria-label="Scroll right"
      >
        <ChevronRight className="w-5 h-5 pointer-events-none" />
      </button>

      {/* Scrollable area */}
      <div
        ref={scrollRef}
        className="flex items-stretch overflow-x-auto scrollbar-hide ml-8 mr-8"
        style={{ scrollBehavior: 'auto' }}
      >
        {sortedDates.map(date => {
          const games = gamesByDate.get(date) || []
          const isToday = date === today
          const isFuture = date > today
          // Find the most recent past date or today
          const isMostRecentPast = !isFuture && sortedDates.filter(d => d <= today).slice(-1)[0] === date
          const dateLabel = isToday ? 'Today' : new Date(date).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })

          return (
            <div
              key={date}
              ref={isToday || isMostRecentPast ? todayRef : undefined}
              className="flex items-stretch border-r border-border shrink-0"
            >
              <div className={cn(
                'px-2 py-1 flex items-center text-[9px] font-mono uppercase border-r border-border min-w-[50px]',
                isToday ? 'bg-primary/20 text-primary font-bold' : isFuture ? 'bg-muted/30 text-primary' : 'text-muted-foreground'
              )}>
                {dateLabel}
              </div>
              {games.map((game) => {
                const homeTeam = teamsMap.get(String(game.home_team_id)) || teamsByName.get(game.home_team_name || '')
                const awayTeam = teamsMap.get(String(game.away_team_id)) || teamsByName.get(game.away_team_name || '')
                const homeGoals = game.home_total_goals ?? 0
                const awayGoals = game.away_total_goals ?? 0
                const homeWon = homeGoals > awayGoals
                const awayWon = awayGoals > homeGoals
                const isFutureGame = date > today
                const hasVideo = gamesWithVideos.has(String(game.game_id))

                return (
                  <Link
                    key={game.game_id || `${date}-${game.home_team_id}`}
                    href={isFutureGame ? '/norad/schedule' : `/norad/games/${game.game_id}`}
                    className={cn(
                      'flex flex-col px-2 py-1.5 hover:bg-muted/50 transition-colors min-w-[110px]',
                      isFutureGame && 'bg-muted/10'
                    )}
                  >
                    <div className="flex items-center justify-between gap-1">
                      <div className="flex items-center gap-1">
                        {awayTeam && <TeamLogo src={awayTeam.team_logo || null} name="" abbrev={awayTeam.team_cd} primaryColor={awayTeam.team_color1} secondaryColor={awayTeam.team_color2} size="xs" />}
                        <span className={cn('text-[10px] font-mono', awayWon && !isFutureGame && 'font-bold')}>{awayTeam?.team_cd}</span>
                      </div>
                      {!isFutureGame && <span className={cn('font-mono text-xs', awayWon ? 'font-bold' : 'text-muted-foreground')}>{awayGoals}</span>}
                    </div>
                    <div className="flex items-center justify-between gap-1 mt-0.5">
                      <div className="flex items-center gap-1">
                        {homeTeam && <TeamLogo src={homeTeam.team_logo || null} name="" abbrev={homeTeam.team_cd} primaryColor={homeTeam.team_color1} secondaryColor={homeTeam.team_color2} size="xs" />}
                        <span className={cn('text-[10px] font-mono', homeWon && !isFutureGame && 'font-bold')}>{homeTeam?.team_cd}</span>
                      </div>
                      {!isFutureGame ? (
                        <span className={cn('font-mono text-xs', homeWon ? 'font-bold' : 'text-muted-foreground')}>{homeGoals}</span>
                      ) : (
                        <span className="text-[8px] text-muted-foreground">{formatGameTime(game.game_time)}</span>
                      )}
                    </div>
                    <div className="flex items-center justify-center gap-1 text-[8px] font-mono mt-0.5">
                      {isFutureGame ? (
                        <span className="text-primary">Upcoming</span>
                      ) : (
                        <>
                          <span className="text-muted-foreground">Final</span>
                          {hasVideo && <Play className="w-2.5 h-2.5 text-red-500 fill-current" />}
                        </>
                      )}
                    </div>
                  </Link>
                )
              })}
            </div>
          )
        })}
      </div>
    </div>
  )
}
