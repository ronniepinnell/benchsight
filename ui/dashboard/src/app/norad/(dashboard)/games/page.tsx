// src/app/(dashboard)/games/page.tsx
import Link from 'next/link'
import { getGames } from '@/lib/supabase/queries/games'
import { getTeamById, getTeamsBySeason } from '@/lib/supabase/queries/teams'
import { getCurrentSeason, getAllSeasons } from '@/lib/supabase/queries/league'
import { getGamesTrackingStatus } from '@/lib/supabase/queries/game-tracking'
import { createClient } from '@/lib/supabase/server'
import { GamesFilters } from '@/components/games/games-filters'
import { GameCard } from '@/components/games/game-card'

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
    tracking?: string
  }>
}) {
  const params = await searchParams
  const limit = 20
  const offset = parseInt(params.offset || '0', 10)
  const seasonId = params.season || null
  const teamId = params.team || null
  const gameType = params.gameType || 'All'
  const search = params.search || null
  const trackingFilter = params.tracking || null

  // Get selected season first to fetch teams for that season
  const currentSeason = await getCurrentSeason()
  const selectedSeason = seasonId || currentSeason
  
  // Fetch teams for the selected season first
  const teams = await getTeamsBySeason(selectedSeason)
  
  // If a team is selected but not in the current season's teams, clear it
  const validTeamIds = teams.map(t => String(t.team_id))
  const finalTeamId = teamId && validTeamIds.includes(teamId) ? teamId : null
  
  // When filtering by tracking status, fetch more games to ensure we have enough after filtering
  const fetchLimit = trackingFilter ? 500 : limit
  const fetchOffset = trackingFilter ? 0 : offset
  
  // Fetch remaining data in parallel
  const [allSeasons, gamesResult] = await Promise.all([
    getAllSeasons(),
    getGames({
      limit: fetchLimit,
      offset: fetchOffset,
      seasonId,
      teamId: finalTeamId,
      gameType,
      search,
    }),
  ])

  let { games, hasMore } = gamesResult
  
  // Get tracking status for all games
  const gameIds = games.map(g => g.game_id).filter((id): id is number => id !== null && id !== undefined)
  const trackingStatusMap = gameIds.length > 0 ? await getGamesTrackingStatus(gameIds) : new Map()
  
  // Determine championship games (last game of each season, excluding current season)
  const supabase = await createClient()
  const championshipGameIds = new Set<number>()
  if (gameIds.length > 0) {
    // Get unique seasons from games
    const seasonsInGames = [...new Set(games.map(g => g.season_id).filter(Boolean))]
    
    // Get current season to exclude it
    const currentSeason = await getCurrentSeason()
    
    for (const seasonId of seasonsInGames) {
      // Skip current season
      if (currentSeason && seasonId === currentSeason) continue
      
      // Get last game of this season
      const { data: lastGame } = await supabase
        .from('dim_schedule')
        .select('game_id')
        .eq('season_id', seasonId)
        .not('home_total_goals', 'is', null)
        .not('away_total_goals', 'is', null)
        .order('date', { ascending: false })
        .order('game_id', { ascending: false })
        .limit(1)
        .maybeSingle()
      
      if (lastGame?.game_id) {
        championshipGameIds.add(Number(lastGame.game_id))
      }
    }
  }
  
  // Filter games by tracking status
  if (trackingFilter) {
    games = games.filter(game => {
      const status = trackingStatusMap.get(game.game_id)
      if (!status) {
        return trackingFilter === 'non-tracked'
      }
      
      switch (trackingFilter) {
        case 'tracked':
          return status.status !== 'none'
        case 'non-tracked':
          return status.status === 'none'
        case 'full':
          return status.status === 'full'
        case 'partial':
          return status.status === 'partial'
        case 'non-full':
          return status.status === 'non-full'
        default:
          return true
      }
    })
    
    // After filtering, apply pagination
    const totalFiltered = games.length
    const paginatedGames = games.slice(offset, offset + limit)
    games = paginatedGames
    hasMore = (offset + limit) < totalFiltered
  }
  
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
    if (trackingFilter) urlParams.set('tracking', trackingFilter)
    urlParams.set('offset', String(offset + limit))
    const queryString = urlParams.toString()
    return `/norad/games${queryString ? `?${queryString}` : ''}`
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
        trackingFilter={trackingFilter}
      />
      
      {/* Games List */}
      <div className="space-y-3">
        {games.map((game) => (
          <GameCard
            key={game.game_id}
            game={game}
            teamsMap={teamsMap}
            trackingStatus={trackingStatusMap.get(game.game_id) || null}
            isChampionship={championshipGameIds.has(game.game_id)}
          />
        ))}
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
