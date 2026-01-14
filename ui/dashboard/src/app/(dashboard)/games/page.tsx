// src/app/(dashboard)/games/page.tsx
import Link from 'next/link'
import { getGames } from '@/lib/supabase/queries/games'
import { getTeamById, getTeamsBySeason } from '@/lib/supabase/queries/teams'
import { getCurrentSeason, getAllSeasons } from '@/lib/supabase/queries/league'
import { createClient } from '@/lib/supabase/server'
import { Calendar, ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'
import { TeamLogo } from '@/components/teams/team-logo'
import { GamesFilters } from '@/components/games/games-filters'

export const revalidate = 300

export const metadata = {
  title: 'Games | BenchSight',
  description: 'NORAD Hockey League game results and box scores',
}

export default async function GamesPage({
  searchParams,
}: {
  searchParams: Promise<{
    season?: string
    team?: string
    gameType?: string
    search?: string
    offset?: string
  }>
}) {
  const params = await searchParams
  const limit = 20
  const offset = parseInt(params.offset || '0', 10)
  const seasonId = params.season || null
  const teamId = params.team || null
  const gameType = params.gameType || 'All'
  const search = params.search || null

  // Get selected season first to fetch teams for that season
  const currentSeason = await getCurrentSeason()
  const selectedSeason = seasonId || currentSeason
  
  // Fetch teams for the selected season first
  const teams = await getTeamsBySeason(selectedSeason)
  
  // If a team is selected but not in the current season's teams, clear it
  const validTeamIds = teams.map(t => String(t.team_id))
  const finalTeamId = teamId && validTeamIds.includes(teamId) ? teamId : null
  
  // Fetch remaining data in parallel
  const [allSeasons, gamesResult] = await Promise.all([
    getAllSeasons(),
    getGames({
      limit,
      offset,
      seasonId,
      teamId: finalTeamId,
      gameType,
      search,
    }),
  ])

  const { games, hasMore } = gamesResult
  
  // Get unique team IDs for logos
  const teamIds = Array.from(
    new Set(
      games
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
  
  // Build load more URL
  const buildLoadMoreUrl = () => {
    const urlParams = new URLSearchParams()
    if (seasonId) urlParams.set('season', seasonId)
    if (finalTeamId) urlParams.set('team', finalTeamId)
    if (gameType !== 'All') urlParams.set('gameType', gameType)
    if (search) urlParams.set('search', search)
    urlParams.set('offset', String(offset + limit))
    const queryString = urlParams.toString()
    return `/games${queryString ? `?${queryString}` : ''}`
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="font-display text-2xl font-bold tracking-wider uppercase flex items-center gap-3">
          <span className="w-1 h-6 bg-shot rounded" />
          Games
        </h1>
        <p className="text-sm text-muted-foreground mt-2 ml-4">
          Browse and search game results and box scores
        </p>
      </div>

      {/* Filters */}
      <GamesFilters
        seasons={allSeasons}
        currentSeason={currentSeason}
        selectedSeason={selectedSeason}
        teams={teams.map(t => ({ team_id: String(t.team_id), team_name: t.team_name }))}
        selectedTeam={finalTeamId}
        gameType={gameType}
        search={search}
        seasonId={selectedSeason}
      />
      
      {/* Games List */}
      <div className="space-y-3">
        {games.map((game) => {
          if (!game.game_id) return null
          
          // Get scores from multiple sources, prioritizing official scores
          const homeGoals = game.official_home_goals ?? game.home_total_goals ?? 0
          const awayGoals = game.official_away_goals ?? game.away_total_goals ?? 0
          const homeWon = homeGoals > awayGoals
          const awayWon = awayGoals > homeGoals
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
                      <div className="flex items-center gap-2">
                        {game.away_team_id && teamsMap.get(String(game.away_team_id)) && (
                          <TeamLogo
                            src={teamsMap.get(String(game.away_team_id))!.team_logo || null}
                            name={teamsMap.get(String(game.away_team_id))!.team_name || game.away_team_name || ''}
                            abbrev={teamsMap.get(String(game.away_team_id))!.team_cd}
                            primaryColor={teamsMap.get(String(game.away_team_id))!.primary_color || teamsMap.get(String(game.away_team_id))!.team_color1}
                            secondaryColor={teamsMap.get(String(game.away_team_id))!.team_color2}
                            size="xs"
                          />
                        )}
                        <Link 
                          href={`/team/${(game.away_team_name ?? 'Away Team').replace(/\s+/g, '_')}`}
                          className={cn(
                            'font-display text-sm hover:text-primary transition-colors',
                            awayWon ? 'text-foreground font-semibold' : 'text-muted-foreground'
                          )}
                        >
                          {game.away_team_name ?? 'Away Team'}
                        </Link>
                      </div>
                      <span className={cn(
                        'font-mono text-xl font-bold',
                        awayWon ? 'text-save' : 'text-muted-foreground'
                      )}>
                        {game.away_total_goals ?? 0}
                      </span>
                    </div>
                    
                    {/* Home Team */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {game.home_team_id && teamsMap.get(String(game.home_team_id)) && (
                          <TeamLogo
                            src={teamsMap.get(String(game.home_team_id))!.team_logo || null}
                            name={teamsMap.get(String(game.home_team_id))!.team_name || game.home_team_name || ''}
                            abbrev={teamsMap.get(String(game.home_team_id))!.team_cd}
                            primaryColor={teamsMap.get(String(game.home_team_id))!.primary_color || teamsMap.get(String(game.home_team_id))!.team_color1}
                            secondaryColor={teamsMap.get(String(game.home_team_id))!.team_color2}
                            size="xs"
                          />
                        )}
                        <span className={cn(
                          'font-display text-sm',
                          homeWon ? 'text-foreground font-semibold' : 'text-muted-foreground'
                        )}>
                          @{' '}
                          <Link 
                            href={`/team/${(game.home_team_name ?? 'Home Team').replace(/\s+/g, '_')}`}
                            className="hover:text-foreground transition-colors"
                          >
                            {game.home_team_name ?? 'Home Team'}
                          </Link>
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
      
      {/* Load More Button */}
      {hasMore && (
        <div className="flex justify-center pt-4">
          <Link
            href={buildLoadMoreUrl()}
            className="px-6 py-3 bg-primary text-primary-foreground rounded-lg font-mono text-sm hover:bg-primary/90 transition-colors"
          >
            Load More Games
          </Link>
        </div>
      )}

      {/* No Results */}
      {games.length === 0 && (
        <div className="bg-card rounded-lg border border-border p-8 text-center">
          <p className="text-muted-foreground">
            {search || finalTeamId || seasonId || gameType !== 'All'
              ? 'No games found matching your filters.'
              : 'No games found.'}
          </p>
        </div>
      )}
    </div>
  )
}
