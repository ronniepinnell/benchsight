// src/app/(dashboard)/games/page.tsx
import Link from 'next/link'
import { getRecentGames } from '@/lib/supabase/queries/games'
import { Calendar, ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'

export const revalidate = 300

export const metadata = {
  title: 'Recent Games | BenchSight',
  description: 'NORAD Hockey League recent game results',
}

export default async function GamesPage() {
  const games = await getRecentGames(20)
  
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="font-display text-2xl font-bold tracking-wider uppercase flex items-center gap-3">
          <span className="w-1 h-6 bg-shot rounded" />
          Recent Games
        </h1>
        <p className="text-sm text-muted-foreground mt-2 ml-4">
          Latest game results and box scores
        </p>
      </div>
      
      {/* Games List */}
      <div className="space-y-3">
        {games.map((game) => {
          if (!game.game_id) return null
          
          const homeWon = (game.home_total_goals ?? 0) > (game.away_total_goals ?? 0)
          const awayWon = (game.away_total_goals ?? 0) > (game.home_total_goals ?? 0)
          const gameDate = game.date ? new Date(game.date).toLocaleDateString('en-US', {
            weekday: 'short',
            month: 'short',
            day: 'numeric',
          }) : 'Unknown Date'
          
          return (
            <Link
              key={game.game_id}
              href={`/games/${game.game_id}`}
              className="block bg-card rounded-lg border border-border hover:border-primary/50 transition-all hover:shadow-lg group"
            >
              <div className="p-4">
                {/* Date */}
                <div className="flex items-center gap-2 mb-3">
                  <Calendar className="w-4 h-4 text-muted-foreground" />
                  <span className="text-xs font-mono text-muted-foreground uppercase">
                    {gameDate}
                  </span>
                </div>
                
                {/* Matchup */}
                <div className="flex items-center justify-between">
                  <div className="flex-1 space-y-2">
                    {/* Away Team */}
                    <div className="flex items-center justify-between">
                      <span className={cn(
                        'font-display text-sm',
                        awayWon ? 'text-foreground font-semibold' : 'text-muted-foreground'
                      )}>
                        {game.away_team_name ?? 'Away Team'}
                      </span>
                      <span className={cn(
                        'font-mono text-xl font-bold',
                        awayWon ? 'text-save' : 'text-muted-foreground'
                      )}>
                        {game.away_total_goals ?? 0}
                      </span>
                    </div>
                    
                    {/* Home Team */}
                    <div className="flex items-center justify-between">
                      <span className={cn(
                        'font-display text-sm',
                        homeWon ? 'text-foreground font-semibold' : 'text-muted-foreground'
                      )}>
                        @ {game.home_team_name ?? 'Home Team'}
                      </span>
                      <span className={cn(
                        'font-mono text-xl font-bold',
                        homeWon ? 'text-save' : 'text-muted-foreground'
                      )}>
                        {game.home_total_goals ?? 0}
                      </span>
                    </div>
                  </div>
                  
                  {/* Arrow */}
                  <ChevronRight className="w-5 h-5 text-muted-foreground ml-4 group-hover:text-primary transition-colors" />
                </div>
                
                {/* Final indicator */}
                <div className="mt-3 pt-3 border-t border-border flex items-center justify-between">
                  <span className="text-xs font-mono text-muted-foreground uppercase">
                    Final
                  </span>
                  <span className="text-xs font-mono text-primary">
                    View Box Score →
                  </span>
                </div>
              </div>
            </Link>
          )
        })}
      </div>
      
      {games.length === 0 && (
        <div className="bg-card rounded-lg border border-border p-8 text-center">
          <p className="text-muted-foreground">No recent games found.</p>
        </div>
      )}
    </div>
  )
}
