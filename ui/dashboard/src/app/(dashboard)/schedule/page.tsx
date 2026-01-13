// src/app/(dashboard)/schedule/page.tsx
import Link from 'next/link'
import { getUpcomingSchedule, getRecentGames } from '@/lib/supabase/queries/games'
import { Calendar, Clock, ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'

export const revalidate = 300

export const metadata = {
  title: 'Schedule | BenchSight',
  description: 'NORAD Hockey League game schedule',
}

export default async function SchedulePage() {
  const [upcoming, recent] = await Promise.all([
    getUpcomingSchedule(10),
    getRecentGames(10)
  ])
  
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="font-display text-2xl font-bold tracking-wider uppercase flex items-center gap-3">
          <span className="w-1 h-6 bg-primary rounded" />
          Schedule
        </h1>
        <p className="text-sm text-muted-foreground mt-2 ml-4">
          Upcoming games and recent results
        </p>
      </div>
      
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Upcoming Games */}
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Clock className="w-4 h-4 text-primary" />
              Upcoming Games
            </h2>
          </div>
          <div className="divide-y divide-border">
            {upcoming.length > 0 ? (
              upcoming.map((game) => {
                const gameDate = new Date(game.date).toLocaleDateString('en-US', {
                  weekday: 'short',
                  month: 'short',
                  day: 'numeric',
                })
                const gameTime = game.time ?? 'TBD'
                
                return (
                  <div key={game.game_id} className="p-4 hover:bg-muted/50 transition-colors">
                    <div className="flex items-center gap-2 mb-2">
                      <Calendar className="w-4 h-4 text-muted-foreground" />
                      <span className="text-xs font-mono text-muted-foreground uppercase">
                        {gameDate} • {gameTime}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-display text-sm text-foreground">
                          {game.away_team_name}
                        </div>
                        <div className="font-display text-sm text-muted-foreground">
                          @ {game.home_team_name}
                        </div>
                      </div>
                      <span className="text-xs font-mono text-primary uppercase bg-primary/10 px-2 py-1 rounded">
                        Upcoming
                      </span>
                    </div>
                  </div>
                )
              })
            ) : (
              <div className="p-8 text-center text-muted-foreground">
                No upcoming games scheduled.
              </div>
            )}
          </div>
        </div>
        
        {/* Recent Results */}
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Calendar className="w-4 h-4 text-save" />
              Recent Results
            </h2>
          </div>
          <div className="divide-y divide-border">
            {recent.map((game) => {
              const homeWon = game.home_total_goals > game.away_total_goals
              const awayWon = game.away_total_goals > game.home_total_goals
              const gameDate = new Date(game.date).toLocaleDateString('en-US', {
                weekday: 'short',
                month: 'short',
                day: 'numeric',
              })
              
              return (
                <Link
                  key={game.game_id}
                  href={`/games/${game.game_id}`}
                  className="block p-4 hover:bg-muted/50 transition-colors group"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <Calendar className="w-4 h-4 text-muted-foreground" />
                    <span className="text-xs font-mono text-muted-foreground uppercase">
                      {gameDate}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center justify-between">
                        <span className={cn(
                          'font-display text-sm',
                          awayWon ? 'text-foreground font-semibold' : 'text-muted-foreground'
                        )}>
                          {game.away_team_name}
                        </span>
                        <span className={cn(
                          'font-mono font-bold',
                          awayWon ? 'text-save' : 'text-muted-foreground'
                        )}>
                          {game.away_total_goals}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className={cn(
                          'font-display text-sm',
                          homeWon ? 'text-foreground font-semibold' : 'text-muted-foreground'
                        )}>
                          @ {game.home_team_name}
                        </span>
                        <span className={cn(
                          'font-mono font-bold',
                          homeWon ? 'text-save' : 'text-muted-foreground'
                        )}>
                          {game.home_total_goals}
                        </span>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-muted-foreground ml-4 group-hover:text-primary transition-colors" />
                  </div>
                </Link>
              )
            })}
          </div>
          <div className="px-4 py-3 bg-accent/50 border-t border-border">
            <Link 
              href="/games" 
              className="text-xs font-mono text-primary hover:underline"
            >
              View all games →
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
