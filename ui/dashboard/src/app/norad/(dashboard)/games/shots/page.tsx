// src/app/norad/(dashboard)/games/shots/page.tsx
import Link from 'next/link'
import { createClient } from '@/lib/supabase/server'
import { getCurrentSeason, getAllSeasons } from '@/lib/supabase/queries/league'
import { getTeamById } from '@/lib/supabase/queries/teams'
import { Target, Calendar, ExternalLink } from 'lucide-react'
import { cn } from '@/lib/utils'
import { TeamLogo } from '@/components/teams/team-logo'
import { SeasonFilter } from '@/components/leaders/season-filter'

export const revalidate = 300

export const metadata = {
  title: 'Shot Maps | BenchSight',
  description: 'NORAD Hockey League game shot maps',
}

export default async function GamesShotsPage({
  searchParams,
}: {
  searchParams: Promise<{ season?: string; game?: string }>
}) {
  const params = await searchParams
  const seasonId = params.season || null
  const gameId = params.game || null

  const supabase = await createClient()
  const currentSeason = await getCurrentSeason()
  const allSeasons = await getAllSeasons()
  const selectedSeason = seasonId || currentSeason

  // Get games with shot data
  let gamesQuery = supabase
    .from('dim_schedule')
    .select('game_id, date, home_team_name, away_team_name, home_team_id, away_team_id, home_total_goals, away_total_goals, official_home_goals, official_away_goals, season_id, game_type')
    .not('home_total_goals', 'is', null)
    .not('away_total_goals', 'is', null)

  if (selectedSeason) {
    gamesQuery = gamesQuery.eq('season_id', selectedSeason)
  }

  // Get games that have shot data
  const { data: gamesData } = await gamesQuery
    .order('date', { ascending: false })
    .limit(100)

  // Check which games have shot data
  const gameIds = (gamesData || []).map(g => g.game_id).filter((id): id is number => id !== null && id !== undefined)
  
  let gamesWithShots: any[] = []
  if (gameIds.length > 0) {
    const { data: shotsData } = await supabase
      .from('fact_shot_xy')
      .select('game_id')
      .in('game_id', gameIds)
    
    const gamesWithShotData = new Set((shotsData || []).map(s => s.game_id))
    gamesWithShots = (gamesData || []).filter(g => gamesWithShotData.has(g.game_id))
  }

  // Get unique team IDs for logos
  const teamIds = Array.from(
    new Set(
      gamesWithShots
        .flatMap(g => [
          g.home_team_id ? String(g.home_team_id) : null,
          g.away_team_id ? String(g.away_team_id) : null,
        ])
        .filter(Boolean)
    )
  )

  const teamData = await Promise.all(
    teamIds.map(id => (id ? getTeamById(id).catch(() => null) : Promise.resolve(null)))
  )
  const teamsMap = new Map(
    teamData.filter(Boolean).map(t => [String(t!.team_id), t!])
  )

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="font-display text-2xl font-bold tracking-wider uppercase flex items-center gap-3">
          <span className="w-1 h-6 bg-goal rounded" />
          Shot Maps
        </h1>
        <p className="text-sm text-muted-foreground mt-2 ml-4">
          Browse shot maps for games with tracking data
        </p>
      </div>

      {/* Season Filter */}
      <SeasonFilter 
        seasons={allSeasons} 
        currentSeason={currentSeason} 
        selectedSeason={selectedSeason} 
      />

      {/* Games List */}
      <div className="space-y-3">
        {gamesWithShots.length > 0 ? (
          gamesWithShots.map((game) => {
            if (!game.game_id) return null
            
            const homeGoals = game.official_home_goals ?? game.home_total_goals ?? 0
            const awayGoals = game.official_away_goals ?? game.away_total_goals ?? 0
            const homeWon = homeGoals > awayGoals
            const awayWon = awayGoals > homeGoals
            const gameDate = game.date ? new Date(game.date).toLocaleDateString('en-US', {
              weekday: 'short',
              month: 'short',
              day: 'numeric',
            }) : 'Unknown Date'
            
            const homeTeam = game.home_team_id ? teamsMap.get(String(game.home_team_id)) : null
            const awayTeam = game.away_team_id ? teamsMap.get(String(game.away_team_id)) : null

            return (
              <Link
                key={game.game_id}
                href={`/norad/games/${game.game_id}`}
                className="block bg-card rounded-lg border border-border hover:border-primary/50 transition-all hover:shadow-lg group"
              >
                <div className="p-4">
                  {/* Date */}
                  <div className="flex items-center gap-2 mb-3">
                    <Calendar className="w-4 h-4 text-muted-foreground" />
                    <span className="text-xs font-mono text-muted-foreground uppercase">
                      {gameDate}
                    </span>
                    {game.game_type && game.game_type !== 'Regular' && (
                      <span className={cn(
                        'text-xs font-mono uppercase px-1.5 py-0.5 rounded',
                        game.game_type === 'Playoffs'
                          ? 'bg-primary/20 text-primary'
                          : 'bg-muted text-muted-foreground'
                      )}>
                        {game.game_type}
                      </span>
                    )}
                  </div>
                  
                  {/* Matchup */}
                  <div className="flex items-center justify-between">
                    <div className="flex-1 space-y-2">
                      {/* Away Team */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          {awayTeam && (
                            <TeamLogo
                              src={awayTeam.team_logo || null}
                              name={awayTeam.team_name || game.away_team_name || ''}
                              abbrev={awayTeam.team_cd}
                              primaryColor={awayTeam.primary_color || awayTeam.team_color1}
                              secondaryColor={awayTeam.team_color2}
                              size="xs"
                            />
                          )}
                          <span className={cn(
                            'font-display text-sm',
                            awayWon ? 'text-foreground font-semibold' : 'text-muted-foreground'
                          )}>
                            {game.away_team_name ?? 'Away Team'}
                          </span>
                        </div>
                        <span className={cn(
                          'font-mono text-xl font-bold',
                          awayWon ? 'text-save' : 'text-muted-foreground'
                        )}>
                          {awayGoals}
                        </span>
                      </div>
                      
                      {/* Home Team */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          {homeTeam && (
                            <TeamLogo
                              src={homeTeam.team_logo || null}
                              name={homeTeam.team_name || game.home_team_name || ''}
                              abbrev={homeTeam.team_cd}
                              primaryColor={homeTeam.primary_color || homeTeam.team_color1}
                              secondaryColor={homeTeam.team_color2}
                              size="xs"
                            />
                          )}
                          <span className={cn(
                            'font-display text-sm',
                            homeWon ? 'text-foreground font-semibold' : 'text-muted-foreground'
                          )}>
                            @ {game.home_team_name ?? 'Home Team'}
                          </span>
                        </div>
                        <span className={cn(
                          'font-mono text-xl font-bold',
                          homeWon ? 'text-save' : 'text-muted-foreground'
                        )}>
                          {homeGoals}
                        </span>
                      </div>
                    </div>
                    
                    {/* Arrow & Shot Map Indicator */}
                    <div className="flex items-center gap-3 ml-4">
                      <div className="flex items-center gap-1 text-xs text-muted-foreground">
                        <Target className="w-4 h-4" />
                        <span className="font-mono">Shot Map</span>
                      </div>
                      <ExternalLink className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" />
                    </div>
                  </div>
                </div>
              </Link>
            )
          })
        ) : (
          <div className="bg-card rounded-lg border border-border p-8 text-center">
            <Target className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">
              {selectedSeason
                ? 'No games with shot data found for this season.'
                : 'No games with shot data found.'}
            </p>
            <p className="text-sm text-muted-foreground mt-2">
              Shot maps are only available for games with full tracking data.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
