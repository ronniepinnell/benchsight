// src/app/norad/(dashboard)/players/[playerId]/games/page.tsx
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getPlayerById } from '@/lib/supabase/queries/players'
import { getAllSeasons } from '@/lib/supabase/queries/league'
import { createClient } from '@/lib/supabase/server'
import { ArrowLeft } from 'lucide-react'
import { PlayerPhoto } from '@/components/players/player-photo'
import { GameCard } from '@/components/players/game-card'
import { PlayerGamesFilters } from '@/components/players/player-games-filters'
import { CollapsibleSeasonSection } from '@/components/players/collapsible-season-section'

export const revalidate = 300

export async function generateMetadata({ params }: { params: Promise<{ playerId: string }> }) {
  const { playerId } = await params
  const player = await getPlayerById(playerId)
  return {
    title: player ? `${player.player_name} - All Games | BenchSight` : 'All Games | BenchSight',
    description: player ? `All games played by ${player.player_name}` : 'Player game history',
  }
}

export default async function PlayerAllGamesPage({
  params,
  searchParams,
}: {
  params: Promise<{ playerId: string }>
  searchParams: Promise<{
    season?: string
    opponent?: string
    gameType?: string
    search?: string
  }>
}) {
  try {
    const { playerId } = await params
    const { season, opponent, gameType, search } = await searchParams
    
    if (!playerId) {
      notFound()
    }
    
    const supabase = await createClient()
    const player = await getPlayerById(playerId)
    
    if (!player) {
      notFound()
    }
    
    // Get all seasons
    const allSeasons = await getAllSeasons()
    
    // Fetch ALL games for this player from fact_gameroster
    let allGamesQuery = supabase
      .from('fact_gameroster')
      .select('*')
      .eq('player_id', playerId)
      .order('game_id', { ascending: false })
      .limit(1000) // Large limit to get all games
    
    const { data: allRosterData } = await allGamesQuery
    
    if (!allRosterData || allRosterData.length === 0) {
      return (
        <div className="space-y-6">
          <Link 
            href={`/norad/players/${playerId}`}
            className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Player
          </Link>
          <div className="bg-card rounded-xl border border-border p-8 text-center">
            <p className="text-muted-foreground">No games found for this player.</p>
          </div>
        </div>
      )
    }
    
    // Get schedule data for all games
    const allGameIds = allRosterData.map(r => r.game_id)
    const { data: allScheduleData } = await supabase
      .from('dim_schedule')
      .select('*')
      .in('game_id', allGameIds)
    
    const scheduleMap = new Map((allScheduleData || []).map(s => [s.game_id, s]))
    
    // Build games list with schedule data
    let allGames = allRosterData.map(roster => {
      const schedule = scheduleMap.get(roster.game_id)
      const goals = Number(roster.goals ?? 0)
      const assists = Number(roster.assist ?? 0)
      const points = goals + assists
      
      return {
        game_id: roster.game_id,
        player_id: roster.player_id,
        player_name: roster.player_full_name || roster.player_name,
        team_name: roster.team_name,
        opponent_team_name: roster.opp_team_name,
        date: schedule?.date || roster.date,
        season_id: schedule?.season_id || roster.season_id,
        season: schedule?.season || roster.season,
        game_type: schedule?.game_type || 'Regular',
        home_team_name: schedule?.home_team_name,
        away_team_name: schedule?.away_team_name,
        home_total_goals: schedule?.home_total_goals ?? null,
        away_total_goals: schedule?.away_total_goals ?? null,
        goals: goals,
        assists: assists,
        points: points,
        shots: null,
        sog: null,
        plus_minus: null,
        toi_seconds: null,
        cf_pct: null,
        _source: 'gameroster'
      }
    }).sort((a, b) => {
      const dateA = a.date ? new Date(a.date).getTime() : 0
      const dateB = b.date ? new Date(b.date).getTime() : 0
      return dateB - dateA
    })
    
    // Apply filters
    if (season) {
      allGames = allGames.filter(g => String(g.season_id) === season || String(g.season) === season)
    }
    
    if (opponent) {
      allGames = allGames.filter(g => 
        (g.opponent_team_name || '').toLowerCase().includes(opponent.toLowerCase()) ||
        (g.team_name || '').toLowerCase().includes(opponent.toLowerCase())
      )
    }
    
    if (gameType && gameType !== 'All') {
      allGames = allGames.filter(g => g.game_type === gameType)
    }
    
    if (search) {
      const searchLower = search.toLowerCase()
      allGames = allGames.filter(g => 
        (g.opponent_team_name || '').toLowerCase().includes(searchLower) ||
        (g.team_name || '').toLowerCase().includes(searchLower) ||
        (g.home_team_name || '').toLowerCase().includes(searchLower) ||
        (g.away_team_name || '').toLowerCase().includes(searchLower) ||
        String(g.game_id).includes(search)
      )
    }
    
    // Get unique opponents for filter
    const uniqueOpponents = [...new Set(
      allRosterData
        .map(r => r.opp_team_name)
        .filter(Boolean)
    )].sort()
    
    // Get unique seasons for this player - use Map to ensure uniqueness by season_id
    const seasonsMap = new Map<string, { season_id: string; season: string | number }>()
    allGames.forEach(g => {
      if (g.season_id && !seasonsMap.has(String(g.season_id))) {
        seasonsMap.set(String(g.season_id), {
          season_id: String(g.season_id),
          season: g.season || g.season_id
        })
      }
    })
    const playerSeasons = Array.from(seasonsMap.values()).sort((a, b) => {
      const seasonA = typeof a.season === 'number' ? a.season : parseInt(String(a.season || '0').replace(/\D/g, '')) || 0
      const seasonB = typeof b.season === 'number' ? b.season : parseInt(String(b.season || '0').replace(/\D/g, '')) || 0
      return seasonB - seasonA
    })
    
    // Group games by season
    const gamesBySeason = new Map<string, any[]>()
    allGames.forEach(game => {
      const seasonKey = String(game.season_id || 'unknown')
      if (!gamesBySeason.has(seasonKey)) {
        gamesBySeason.set(seasonKey, [])
      }
      gamesBySeason.get(seasonKey)!.push(game)
    })
    
    // Get opponent teams map for GameCard
    const opponentNames = [...new Set(allGames.map(g => g.opponent_team_name).filter(Boolean))]
    const { data: opponentTeamsData } = await supabase
      .from('dim_team')
      .select('team_id, team_name, team_logo, team_cd, primary_color, team_color1, team_color2')
      .in('team_name', opponentNames)
    
    const opponentTeamsMap = new Map(
      (opponentTeamsData || []).map(t => [t.team_name, t])
    )
    
    return (
      <div className="space-y-6">
        {/* Header */}
        <div>
          <Link 
            href={`/norad/players/${playerId}`}
            className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Player
          </Link>
          
          <div className="flex items-center gap-4">
            <PlayerPhoto
              src={player.player_image || player.player_photo || null}
              name={player.player_name || ''}
              size="xl"
            />
            <div className="flex-1">
              <h1 className="font-display text-2xl font-bold tracking-wider uppercase flex items-center gap-3">
                <span className="w-1 h-6 bg-shot rounded" />
                {player.player_name || player.player_full_name || 'Player'} - All Games
              </h1>
              <p className="text-sm text-muted-foreground mt-2">
                {allGames.length} game{allGames.length !== 1 ? 's' : ''} found
              </p>
            </div>
          </div>
        </div>
        
        {/* Filters */}
        <PlayerGamesFilters
          playerId={playerId}
          season={season}
          opponent={opponent}
          gameType={gameType}
          search={search}
          playerSeasons={playerSeasons}
          uniqueOpponents={uniqueOpponents}
        />
        
        {/* Games by Season */}
        {allGames.length > 0 ? (
          <div className="space-y-4">
            {playerSeasons.map((seasonInfo) => {
              const seasonGames = gamesBySeason.get(String(seasonInfo.season_id)) || []
              if (seasonGames.length === 0) return null
              
              return (
                <CollapsibleSeasonSection
                  key={seasonInfo.season_id}
                  seasonId={seasonInfo.season_id}
                  season={seasonInfo.season}
                  games={seasonGames}
                >
                  <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {seasonGames.map((game: any, index: number) => {
                      const isHome = game.team_name && game.opponent_team_name 
                        ? (game.home_team_name === game.team_name || game.away_team_name !== game.team_name)
                        : undefined
                      
                      const opponentName = game.opponent_team_name || game.team_name || ''
                      const opponentTeamInfo = opponentTeamsMap.get(opponentName)
                      const gameType = game.game_type || 'Regular'
                      const isPlayoff = gameType === 'Playoffs' || gameType === 'playoffs' || gameType === 'Playoff'
                      
                      return (
                        <GameCard
                          key={game.game_id || `game-${index}`}
                          game={game}
                          isHome={isHome}
                          teamInfo={undefined}
                          opponentTeamInfo={opponentTeamInfo}
                        />
                      )
                    })}
                  </div>
                </CollapsibleSeasonSection>
              )
            })}
          </div>
        ) : (
          <div className="bg-card rounded-xl border border-border p-8 text-center">
            <p className="text-muted-foreground">No games found matching your filters.</p>
          </div>
        )}
      </div>
    )
  } catch (error) {
    console.error('Error in PlayerAllGamesPage:', error)
    notFound()
  }
}
