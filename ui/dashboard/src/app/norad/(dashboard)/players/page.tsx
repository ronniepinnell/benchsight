// src/app/(dashboard)/players/page.tsx
import Link from 'next/link'
import { getCurrentRankings, getPlayers } from '@/lib/supabase/queries/players'
import { getTeams } from '@/lib/supabase/queries/teams'
import { getCurrentSeason, getAllSeasons } from '@/lib/supabase/queries/league'
import { createClient } from '@/lib/supabase/server'
import { Search, TrendingUp, Target, Sparkles } from 'lucide-react'
import { cn } from '@/lib/utils'
import { PlayersTableWithExport } from '@/components/players/players-table-export'
import { PlayerSearchFilters } from '@/components/players/player-search-filters'

export const revalidate = 300

export const metadata = {
  title: 'Players | BenchSight',
  description: 'NORAD Hockey League player statistics',
}

export default async function PlayersPage({
  searchParams,
}: {
  searchParams: Promise<{ 
    search?: string
    position?: string
    team?: string
    minGP?: string
    maxGP?: string
    minRating?: string
    maxRating?: string
    playerId?: string
    season?: string
  }>
}) {
  const params = await searchParams
  const supabase = await createClient()
  
  // Get seasons for filter
  const currentSeason = await getCurrentSeason()
  const allSeasonIds = await getAllSeasons()
  
  // Get season data with names
  const { data: seasonData } = await supabase
    .from('v_standings_all_seasons')
    .select('season_id, season')
    .in('season_id', allSeasonIds)
  
  const seasons = seasonData 
    ? [...new Map(seasonData.map(s => [s.season_id, s])).values()]
    : []
  
  const selectedSeason = params.season || currentSeason || null
  
  // Get all players with full details for filtering
  const allPlayersData = await getPlayers()
  const playersMap = new Map(allPlayersData.map(p => [String(p.player_id), p]))
  
  // Get player rankings - use current season view or query by season
  let players
  if (selectedSeason && selectedSeason !== currentSeason) {
    // Query historical season stats
    const { data: seasonStats } = await supabase
      .from('fact_player_season_stats_basic')
      .select('*')
      .eq('season_id', selectedSeason)
      .eq('game_type', 'All')
      .order('points', { ascending: false })
      .limit(500)
    
    // Transform to match VRankingsPlayersCurrent format
    players = (seasonStats || []).map((stat, index) => ({
      player_id: stat.player_id,
      player_name: stat.player_name || '',
      team_id: stat.team_id,
      team_name: stat.team_name || '',
      games_played: stat.games_played || 0,
      goals: stat.goals || 0,
      assists: stat.assists || 0,
      points: stat.points || 0,
      points_per_game: stat.games_played > 0 ? (stat.points || 0) / stat.games_played : 0,
      points_rank: index + 1,
      pim: stat.pim || 0,
      current_skill_rating: null, // Not available in historical stats
      jersey_number: null,
      player_primary_position: null,
    }))
  } else {
    // Use current season rankings
    players = await getCurrentRankings(500) // Get more for filtering
  }
  
  const teams = await getTeams()
  
  // Enhance players with dim_player data
  const playersWithDetails = players.map(p => ({
    ...p,
    ...playersMap.get(String(p.player_id)),
  }))
  
  // Filter out summer teams (Red, Green, Yellow, Blue)
  const summerTeamNames = ['red', 'green', 'yellow', 'blue']
  const filteredBySummer = playersWithDetails.filter(p => {
    const teamName = (p.team_name || '').toLowerCase()
    return !summerTeamNames.some(summerTeam => teamName.includes(summerTeam))
  })
  
  // Filter players based on search params
  let filteredPlayers = filteredBySummer
  
  if (params.search) {
    const searchLower = params.search.toLowerCase()
    filteredPlayers = filteredPlayers.filter(p => 
      p.player_name?.toLowerCase().includes(searchLower) ||
      p.player_full_name?.toLowerCase().includes(searchLower) ||
      p.team_name?.toLowerCase().includes(searchLower) ||
      String(p.player_id).toLowerCase().includes(searchLower)
    )
  }
  
  if (params.position) {
    const posLower = params.position.toLowerCase()
    filteredPlayers = filteredPlayers.filter(p => {
      const primaryPos = (p.player_primary_position || '').toLowerCase()
      return primaryPos.includes(posLower) || primaryPos === posLower
    })
  }
  
  if (params.team) {
    filteredPlayers = filteredPlayers.filter(p => String(p.team_id) === params.team)
  }
  
  if (params.minGP) {
    const minGP = parseInt(params.minGP)
    filteredPlayers = filteredPlayers.filter(p => (p.games_played || 0) >= minGP)
  }
  
  if (params.maxGP) {
    const maxGP = parseInt(params.maxGP)
    filteredPlayers = filteredPlayers.filter(p => (p.games_played || 0) <= maxGP)
  }
  
  if (params.minRating) {
    const minRating = parseFloat(params.minRating)
    filteredPlayers = filteredPlayers.filter(p => {
      const rating = p.current_skill_rating || 0
      return rating >= minRating
    })
  }
  
  if (params.maxRating) {
    const maxRating = parseFloat(params.maxRating)
    filteredPlayers = filteredPlayers.filter(p => {
      const rating = p.current_skill_rating || 0
      return rating <= maxRating
    })
  }
  
  if (params.playerId) {
    filteredPlayers = filteredPlayers.filter(p => 
      String(p.player_id).toLowerCase().includes(params.playerId!.toLowerCase())
    )
  }
  
  // Limit to top 200 for display
  const displayPlayers = filteredPlayers.slice(0, 200)
  
  // Get leaders for quick stats (from filtered or all)
  const pointsLeader = displayPlayers[0] || players[0]
  const goalsLeader = [...displayPlayers].sort((a, b) => b.goals - a.goals)[0] || [...players].sort((a, b) => b.goals - a.goals)[0]
  const assistsLeader = [...displayPlayers].sort((a, b) => b.assists - a.assists)[0] || [...players].sort((a, b) => b.assists - a.assists)[0]
  
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="font-display text-2xl font-bold tracking-wider uppercase flex items-center gap-3">
          <span className="w-1 h-6 bg-primary rounded" />
          Player Rankings
        </h1>
        <p className="text-sm text-muted-foreground mt-2 ml-4">
          {selectedSeason === currentSeason 
            ? 'Current season player statistics and rankings'
            : `Player statistics and rankings for ${seasons.find(s => s.season_id === selectedSeason)?.season || selectedSeason}`
          }
        </p>
      </div>
      
      {/* Search and Filters */}
      <div className="bg-card rounded-xl border border-border p-4">
        <PlayerSearchFilters
          teams={teams.map(t => ({ team_id: String(t.team_id), team_name: t.team_name || '' }))}
          seasons={seasons}
          currentSeason={currentSeason}
          selectedSeason={selectedSeason}
        />
      </div>
      
      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Link 
          href="/norad/leaders?tab=points"
          className="bg-card rounded-lg p-4 border border-border hover:border-primary/50 transition-colors group"
        >
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-4 h-4 text-primary" />
            <span className="text-xs font-mono text-muted-foreground uppercase">Points Leader</span>
          </div>
          {pointsLeader && (
            <>
              <div className="font-display text-lg font-semibold text-foreground group-hover:text-primary transition-colors">
                {pointsLeader.player_name}
              </div>
              <div className="font-mono text-2xl font-bold text-primary">{pointsLeader.points} pts</div>
            </>
          )}
        </Link>
        
        <Link 
          href="/norad/leaders?tab=goals"
          className="bg-card rounded-lg p-4 border border-border hover:border-goal/50 transition-colors group"
        >
          <div className="flex items-center gap-2 mb-2">
            <Target className="w-4 h-4 text-goal" />
            <span className="text-xs font-mono text-muted-foreground uppercase">Goals Leader</span>
          </div>
          {goalsLeader && (
            <>
              <div className="font-display text-lg font-semibold text-foreground group-hover:text-goal transition-colors">
                {goalsLeader.player_name}
              </div>
              <div className="font-mono text-2xl font-bold text-goal">{goalsLeader.goals} G</div>
            </>
          )}
        </Link>
        
        <Link 
          href="/norad/leaders?tab=assists"
          className="bg-card rounded-lg p-4 border border-border hover:border-assist/50 transition-colors group"
        >
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="w-4 h-4 text-assist" />
            <span className="text-xs font-mono text-muted-foreground uppercase">Assists Leader</span>
          </div>
          {assistsLeader && (
            <>
              <div className="font-display text-lg font-semibold text-foreground group-hover:text-assist transition-colors">
                {assistsLeader.player_name}
              </div>
              <div className="font-mono text-2xl font-bold text-assist">{assistsLeader.assists} A</div>
            </>
          )}
        </Link>
        
        <Link 
          href="/norad/players/compare"
          className="bg-card rounded-lg p-4 border border-border hover:border-shot/50 transition-colors flex flex-col justify-center items-center"
        >
          <Search className="w-8 h-8 text-shot mb-2" />
          <span className="font-display text-sm font-semibold text-foreground">Compare Players</span>
          <span className="text-xs text-muted-foreground">Side-by-side stats</span>
        </Link>
      </div>
      
      {/* Players Table */}
      <PlayersTableWithExport players={displayPlayers} />
    </div>
  )
}
