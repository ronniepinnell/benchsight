// @ts-nocheck
// src/app/norad/(dashboard)/games/[gameId]/page.tsx
import Link from 'next/link'
import { notFound } from 'next/navigation'
import {
  getGameFromSchedule,
  getGameRoster,
  getGameGoals,
  getGameGoalieStats,
  getGameShots,
  getGameVideos,
  getGameHighlights,
  getPriorGames,
  getGamePlayerStats,
  getTeamGameStats,
  getGameAssistEvents,
  getPlayerImages,
  checkIsChampionshipGame,
  getGameAllEvents,
  getGameShifts,
  getGameHighlightEvents,
  getGamePlayerShiftCounts,
} from '@/lib/supabase/queries/games'
import { getGameTrackingStatus } from '@/lib/supabase/queries/game-tracking'
import { createClient } from '@/lib/supabase/server'
import { getTeamById } from '@/lib/supabase/queries/teams'
import { getPlayers } from '@/lib/supabase/queries/players'
import { ArrowLeft, Target, User, TrendingUp, Activity, BarChart3, Shield, Zap, ExternalLink, Trophy, ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils'
import {
  calculateTeamAggregates,
  calculatePercentage,
  buildPlayerMaps,
  processRoster,
  padArray,
  filterStatsByTeam,
  getTopPerformers,
  calculateThreeStars,
  createPlayerStatsMap,
  processAssists,
  enhanceHighlights,
  type GameEvent,
  type EnhancedHighlight,
} from '@/lib/utils/game-data'
import { TeamLogo } from '@/components/teams/team-logo'
import { PlayerPhoto } from '@/components/players/player-photo'
import { ShotHeatmap } from '@/components/charts/shot-heatmap'
import { EnhancedShotMap } from '@/components/charts/enhanced-shot-map'
import { StatCard, StatRow } from '@/components/players/stat-card'
import { GameHighlights } from '@/components/games/game-highlights'
import { GameSummary } from '@/components/games/game-summary'
import { PlayByPlayTimeline } from '@/components/games/PlayByPlayTimeline'
import { ShiftChart } from '@/components/games/shift-chart'
import { ShiftsTimeline } from '@/components/games/shifts-timeline'
import { GameAnalyticsPanel } from '@/components/games/game-analytics-panel'
import { SortableGoaliesTable } from '@/components/games/sortable-goalies-table'
import { ThreeStars } from '@/components/games/three-stars'
import { GameDetailTabs } from '@/components/games/game-detail-tabs'
import { GameMediaSection } from '@/components/games/game-media-section'
import { CompactTeamStats } from '@/components/games/compact-team-stats'
import { MiniShotRink } from '@/components/games/mini-shot-rink'
import type { FactPlayerGameStats, FactGoalieGameStats, DimTeam, DimPlayer } from '@/types/database'

export const revalidate = 300

export async function generateMetadata({ params }: { params: Promise<{ gameId: string }> }) {
  const { gameId } = await params
  const gameIdNum = parseInt(gameId)
  
  // Try to get game data for better metadata
  let gameTitle = `Game ${gameId}`
  let gameDescription = `Box score and stats for game ${gameId}`
  
  if (!isNaN(gameIdNum)) {
    try {
      const game = await getGameFromSchedule(gameIdNum)
      if (game) {
        const homeTeam = game.home_team_name || 'Home'
        const awayTeam = game.away_team_name || 'Away'
        const homeScore = game.home_total_goals ?? 0
        const awayScore = game.away_total_goals ?? 0
        const gameDate = game.date ? new Date(game.date).toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
          year: 'numeric'
        }) : ''
        
        gameTitle = `${awayTeam} @ ${homeTeam}${gameDate ? ` - ${gameDate}` : ''} | BenchSight`
        gameDescription = `${awayTeam} ${awayScore} - ${homeScore} ${homeTeam}. Box score, player stats, and game highlights.`
      }
    } catch (error) {
      // Fall back to default metadata if game fetch fails
      console.error('Error fetching game for metadata:', error)
    }
  }
  
  return {
    title: gameTitle,
    description: gameDescription,
  }
}

export default async function GameDetailPage({ 
  params 
}: { 
  params: Promise<{ gameId: string }> 
}) {
  const { gameId } = await params
  const gameIdNum = parseInt(gameId)
  
  if (isNaN(gameIdNum)) {
    notFound()
  }

  const supabase = await createClient()

  // Get game from dim_schedule
  const game = await getGameFromSchedule(gameIdNum)
  if (!game) {
    notFound()
  }

  // Fetch all data in parallel with improved error handling
  const [
    roster, goals, players, goalieStats, shots,
    highlightEventsResult, allEventsResult, shiftsResult, priorGamesResult,
    gameVideosResult, gameHighlightsResult, playerShiftCountsResult
  ] = await Promise.allSettled([
    getGameRoster(gameIdNum),
    getGameGoals(gameIdNum),
    getPlayers(),
    getGameGoalieStats(gameIdNum),
    getGameShots(gameIdNum),
    getGameHighlightEvents(gameIdNum),
    getGameAllEvents(gameIdNum),
    getGameShifts(gameIdNum),
    getPriorGames(gameIdNum, game.season_id, game.home_team_id, game.away_team_id, game),
    getGameVideos(gameIdNum),
    getGameHighlights(gameIdNum),
    getGamePlayerShiftCounts(gameIdNum)
  ])

  // Extract results with error handling
  const rosterData = roster.status === 'fulfilled' ? roster.value : []
  const goalsData = goals.status === 'fulfilled' ? goals.value : []
  const playersData = players.status === 'fulfilled' ? players.value : []
  const priorGamesData = priorGamesResult.status === 'fulfilled' ? priorGamesResult.value : { homeGames: [], awayGames: [], headToHeadGames: [] }
  const goalieStatsData = goalieStats.status === 'fulfilled' ? goalieStats.value : []
  const shotsData = shots.status === 'fulfilled' ? shots.value : []
  const highlightEventsData = highlightEventsResult.status === 'fulfilled' ? highlightEventsResult.value : []
  const allEvents = allEventsResult.status === 'fulfilled' ? allEventsResult.value : []
  const shiftsData = shiftsResult.status === 'fulfilled' ? shiftsResult.value : []
  const gameVideos = gameVideosResult.status === 'fulfilled' ? gameVideosResult.value : []
  const gameHighlights = gameHighlightsResult.status === 'fulfilled' ? gameHighlightsResult.value : []
  const playerShiftCounts = playerShiftCountsResult.status === 'fulfilled' ? playerShiftCountsResult.value : new Map<string, number>()

  // Log any rejected promises for debugging (development only)
  if (process.env.NODE_ENV === 'development') {
    const results = [roster, goals, players, goalieStats, shots, highlightEventsResult, allEventsResult, shiftsResult, priorGamesResult, gameVideosResult, gameHighlightsResult]
    const rejected = results.filter((p) => p.status === 'rejected')
    if (rejected.length > 0) {
      console.warn(`Some data failed to load for game ${gameIdNum}`)
    }
    if (rosterData.length === 0) {
      console.warn(`No roster data found for game ${gameIdNum}`)
    }
  }

  // Enhance highlight events with period/time info
  const highlightsRaw = highlightEventsData.filter((e: GameEvent) =>
    e.is_goal || e.is_highlight || e.is_save || e.event_type === 'Goal'
  )
  const highlights = enhanceHighlights(highlightsRaw)

  // Get tracking status
  const gameTrackingStatus = await getGameTrackingStatus(gameIdNum).catch(() => null)
  const hasVideo = gameTrackingStatus?.hasVideo || false
  const hasTracking = gameTrackingStatus?.status !== 'none' && gameTrackingStatus !== null
  const hasEvents = gameTrackingStatus?.hasEvents || false
  const hasShifts = gameTrackingStatus?.hasShifts || false
  const hasXY = gameTrackingStatus?.hasXY || false
  const hasTrackedEvents = allEvents.length > 0

  // Get team info for logos
  const homeTeamId = game.home_team_id
  const awayTeamId = game.away_team_id
  const [homeTeamResult, awayTeamResult] = await Promise.allSettled([
    homeTeamId ? getTeamById(String(homeTeamId)) : Promise.resolve(null),
    awayTeamId ? getTeamById(String(awayTeamId)) : Promise.resolve(null)
  ])
  const homeTeam: DimTeam | null = homeTeamResult.status === 'fulfilled' ? homeTeamResult.value : null
  const awayTeam: DimTeam | null = awayTeamResult.status === 'fulfilled' ? awayTeamResult.value : null

  // Build player lookup maps
  const { playersMap, playerNameToIdMap } = buildPlayerMaps(playersData)

  // Create jersey number to player name map from roster (for shifts)
  const jerseyToPlayerMap = new Map<string, { player_name: string; team_id: string }>()
  rosterData.forEach((r: any) => {
    const jerseyNum = r.player_game_number
    if (jerseyNum !== null && jerseyNum !== undefined) {
      jerseyToPlayerMap.set(String(Math.floor(Number(jerseyNum))), {
        player_name: r.player_full_name || r.player_name || `#${jerseyNum}`,
        team_id: String(r.team_id || '')
      })
    }
  })

  // Also create event_id -> player_id map from event_player_ids for goals
  const goalEventPlayerIdsMap = new Map<string, string>()
  goalsData.forEach((goal) => {
    if (goal.event_id && goal.event_player_ids) {
      // event_player_ids is comma-separated, first one is the scorer (event_player_1)
      const playerIds = goal.event_player_ids.split(',').map(id => id.trim()).filter(Boolean)
      if (playerIds.length > 0) {
        goalEventPlayerIdsMap.set(goal.event_id, playerIds[0])
      }
    }
  })
  
  // Fetch assist events for goals (events with play_detail1='AssistPrimary' or 'AssistSecondary' in same sequence/play)
  const assistEventsMap = new Map<string, Array<{ player_id: string; player_name: string; assist_type: 'primary' | 'secondary' }>>()
  
  // Get all events for this game that might be assists (filter in JS to avoid complex Supabase query)
  let allAssistEvents: GameEvent[] = []
  if (hasVideo && goalsData.length > 0) {
    try {
      const { data: allAssistEventsData, error: allAssistEventsError } = await supabase
        .from('fact_events')
        .select('event_id, sequence_key, play_key, player_name, event_player_ids, play_detail1, play_detail_2, linked_event_key, time_start_total_seconds')
        .eq('game_id', gameIdNum)
      
      allAssistEvents = allAssistEventsError ? [] : (allAssistEventsData || [])
    } catch (error) {
      console.error('Error fetching assist events:', error)
      allAssistEvents = []
    }
  }
  
  if (hasVideo && goalsData.length > 0 && allAssistEvents.length > 0) {
    // Filter to events with assist indicators
    const assistCandidates = allAssistEvents.filter((e: GameEvent) => {
      const pd1 = (e.play_detail1 || '').toLowerCase()
      const pd2 = (e.play_detail_2 || '').toLowerCase()
      return pd1.includes('assistprimary') || pd1.includes('assistsecondary') || 
             pd2.includes('assistprimary') || pd2.includes('assistsecondary')
    })
    
    // Group assists by goal event (same sequence/play or linked)
    goalsData.forEach((goal: GameEvent, goalIndex: number) => {
      const assists: Array<{ player_id: string; player_name: string; assist_type: 'primary' | 'secondary' }> = []
      
      assistCandidates.forEach((assistEvent: GameEvent) => {
        // Check if this assist event is in the same sequence/play as the goal, or happens just before the goal
        const sameSequence = goal.sequence_key && assistEvent.sequence_key === goal.sequence_key
        const samePlay = goal.play_key && assistEvent.play_key === goal.play_key
        const linkedToGoal = goal.linked_event_key && assistEvent.linked_event_key === goal.linked_event_key
        // Also check if assist happens within 10 seconds before goal (likely related)
        const timeDiff = goal.time_start_total_seconds && assistEvent.time_start_total_seconds
          ? goal.time_start_total_seconds - assistEvent.time_start_total_seconds
          : null
        const timeRelated = timeDiff !== null && timeDiff > 0 && timeDiff <= 10
        
        if (sameSequence || samePlay || linkedToGoal || timeRelated) {
          const playDetail1 = (assistEvent.play_detail1 || '').toLowerCase()
          const playDetail2 = (assistEvent.play_detail_2 || '').toLowerCase()
          
          if (playDetail1.includes('assistprimary') || playDetail2.includes('assistprimary')) {
            // Get player ID from event_player_ids (first one is event_player_1)
            const playerIds = (assistEvent.event_player_ids || '').split(',').map((id: string) => id.trim()).filter(Boolean)
            if (playerIds.length > 0) {
              assists.push({
                player_id: playerIds[0],
                player_name: assistEvent.player_name || '',
                assist_type: 'primary'
              })
            }
          } else if (playDetail1.includes('assistsecondary') || playDetail2.includes('assistsecondary')) {
            const playerIds = (assistEvent.event_player_ids || '').split(',').map((id: string) => id.trim()).filter(Boolean)
            if (playerIds.length > 0) {
              assists.push({
                player_id: playerIds[0],
                player_name: assistEvent.player_name || '',
                assist_type: 'secondary'
              })
            }
          }
        }
      })
      
      // Remove duplicates by player_id
      const uniqueAssists = assists.filter((assist, idx, self) => 
        idx === self.findIndex(a => a.player_id === assist.player_id)
      )
      
      if (uniqueAssists.length > 0) {
        assistEventsMap.set(goal.event_id || String(goal.time_start_total_seconds || goalIndex), uniqueAssists)
      }
    })
  }
  
  // Separate roster into home/away, players/goalies (optimized - single pass)
  const homeRoster: Array<Record<string, any>> = []
  const awayRoster: Array<Record<string, any>> = []
  
  rosterData.forEach((r: Record<string, any>) => {
    const teamVenue = String(r.team_venue || '').trim()
    const teamName = String(r.team_name || '').trim()
    const rosterTeamId = String(r.team_id || '').trim()
    const homeTeamName = String(game.home_team_name || '').trim()
    const awayTeamName = String(game.away_team_name || '').trim()
    const homeTeamId = String(game.home_team_id || '').trim()
    const awayTeamId = String(game.away_team_id || '').trim()
    
    // Match by team_id first (most reliable), then team_venue, then team_name
    const isHome = rosterTeamId === homeTeamId || 
                   teamVenue === 'Home' || 
                   teamName === homeTeamName ||
                   (teamVenue === '' && teamName === '' && rosterTeamId === homeTeamId)
    
    const isAway = rosterTeamId === awayTeamId || 
                   teamVenue === 'Away' || 
                   teamName === awayTeamName ||
                   (teamVenue === '' && teamName === '' && rosterTeamId === awayTeamId)
    
    if (isHome) {
      homeRoster.push(r)
    } else if (isAway) {
      awayRoster.push(r)
    } else if (process.env.NODE_ENV === 'development') {
      // Debug: Log unmatched roster entries (only in development)
      console.warn('Unmatched roster entry:', { 
        team_venue: teamVenue, 
        team_name: teamName, 
        team_id: rosterTeamId,
        home_team_id: homeTeamId,
        away_team_id: awayTeamId,
        player_name: r.player_name || r.player_full_name 
      })
    }
  })
  
  // Separate players and goalies, then separate forwards and defense
  // Performance: Single pass per roster
  const homeForwards: Array<Record<string, any>> = []
  const homeDefense: Array<Record<string, any>> = []
  const homeGoalies: Array<Record<string, any>> = []
  const awayForwards: Array<Record<string, any>> = []
  const awayDefense: Array<Record<string, any>> = []
  const awayGoalies: Array<Record<string, any>> = []
  
  homeRoster.forEach((r: Record<string, any>) => {
    // Use player_position from fact_gameroster first, then fallback to player_primary_position from dim_player
    const gamePos = String(r.player_position || '').trim().toUpperCase()
    const playerId = String(r.player_id || '')
    const playerInfo = playersMap.get(playerId)
    const primaryPos = String(playerInfo?.player_primary_position || '').trim().toUpperCase()
    
    // Check if goalie
    if (gamePos === 'G' || gamePos.includes('GOALIE') || primaryPos.includes('GOALIE') || r.goals_against) {
      homeGoalies.push(r)
    } else {
      // Check if defense - use both game position and primary position
      const isDefense = gamePos === 'D' || 
                       gamePos === 'LD' || 
                       gamePos === 'RD' || 
                       gamePos === 'DEF' ||
                       gamePos === 'DEFENSE' ||
                       primaryPos === 'D' ||
                       primaryPos === 'LD' ||
                       primaryPos === 'RD' ||
                       primaryPos === 'DEF' ||
                       primaryPos === 'DEFENSE'
      
      if (isDefense) {
        homeDefense.push(r)
      } else {
        // Everything else is a forward
        homeForwards.push(r)
      }
    }
  })
  
  awayRoster.forEach((r: Record<string, any>) => {
    // Use player_position from fact_gameroster first, then fallback to player_primary_position from dim_player
    const gamePos = String(r.player_position || '').trim().toUpperCase()
    const playerId = String(r.player_id || '')
    const playerInfo = playersMap.get(playerId)
    const primaryPos = String(playerInfo?.player_primary_position || '').trim().toUpperCase()
    
    // Check if goalie
    if (gamePos === 'G' || gamePos.includes('GOALIE') || primaryPos.includes('GOALIE') || r.goals_against) {
      awayGoalies.push(r)
    } else {
      // Check if defense - use both game position and primary position
      const isDefense = gamePos === 'D' || 
                       gamePos === 'LD' || 
                       gamePos === 'RD' || 
                       gamePos === 'DEF' ||
                       gamePos === 'DEFENSE' ||
                       primaryPos === 'D' ||
                       primaryPos === 'LD' ||
                       primaryPos === 'RD' ||
                       primaryPos === 'DEF' ||
                       primaryPos === 'DEFENSE'
      
      if (isDefense) {
        awayDefense.push(r)
      } else {
        // Everything else is a forward
        awayForwards.push(r)
      }
    }
  })
  
  // For backwards compatibility, also create combined arrays
  const homePlayers = [...homeForwards, ...homeDefense]
  const awayPlayers = [...awayForwards, ...awayDefense]
  
  // Calculate max players per position group to align totals rows
  // Totals should appear at row 6 for both teams (so pad to at least 5 players)
  const maxForwards = Math.max(homeForwards.length, awayForwards.length, 5) // At least 5 so totals at row 6
  const maxDefense = Math.max(homeDefense.length, awayDefense.length, 5) // At least 5 so totals at row 6
  
  // Pad shorter lists with empty rows so totals align
  const padArray = <T,>(arr: T[], targetLength: number): (T | null)[] => {
    const padded = [...arr]
    while (padded.length < targetLength) {
      padded.push(null as T)
    }
    return padded
  }
  
  const paddedAwayForwards = padArray(awayForwards, maxForwards)
  const paddedHomeForwards = padArray(homeForwards, maxForwards)
  const paddedAwayDefense = padArray(awayDefense, maxDefense)
  const paddedHomeDefense = padArray(homeDefense, maxDefense)
  
  // Get advanced stats for players from fact_player_game_stats
  // Query all players for this game, then filter by team (safer than .in() with empty arrays)
  const { data: allPlayerStatsData, error: allPlayerStatsError } = await supabase
    .from('fact_player_game_stats')
    .select('*')
    .eq('game_id', gameIdNum)
    
  const allPlayerStats = allPlayerStatsError ? [] : (allPlayerStatsData || [])

  // Fetch player images from dim_player for all players in this game
  const playerIds = [...new Set(allPlayerStats.map((s: any) => s.player_id).filter(Boolean))]
  let playerImageMap = new Map<string, string | null>()

  if (playerIds.length > 0) {
    const { data: playerImages } = await supabase
      .from('dim_player')
      .select('player_id, player_image')
      .in('player_id', playerIds)

    if (playerImages) {
      playerImages.forEach((p: any) => {
        playerImageMap.set(String(p.player_id), p.player_image || null)
      })
    }
  }

  // Filter by team (by team_id or team_name for compatibility)
  const homePlayerStatsList = allPlayerStats.filter((stat: any) => {
    const statTeamId = String(stat.team_id || '')
    const statTeamName = stat.team_name || ''
    const homeTeamIdStr = homeTeamId ? String(homeTeamId) : ''
    const homeTeamName = game.home_team_name || ''
    
    return statTeamId === homeTeamIdStr || 
           statTeamName === homeTeamName ||
           (stat.team_venue === 'Home' && statTeamName)
  })
  
  const awayPlayerStatsList = allPlayerStats.filter((stat: any) => {
    const statTeamId = String(stat.team_id || '')
    const statTeamName = stat.team_name || ''
    const awayTeamIdStr = awayTeamId ? String(awayTeamId) : ''
    const awayTeamName = game.away_team_name || ''
    
    return statTeamId === awayTeamIdStr || 
           statTeamName === awayTeamName ||
           (stat.team_venue === 'Away' && statTeamName)
  })
  
  // Get top performers for each team (by points)
  const homeTopPerformers = homePlayerStatsList
    .map((stat: any) => ({
      player_id: String(stat.player_id),
      player_name: stat.player_name || stat.player_full_name || '',
      goals: Number(stat.goals ?? stat.g ?? 0),
      assists: Number(stat.assists ?? stat.a ?? 0),
      points: Number(stat.points ?? stat.pts ?? (Number(stat.goals ?? stat.g ?? 0) + Number(stat.assists ?? stat.a ?? 0))),
    }))
    .sort((a, b) => b.points - a.points || b.goals - a.goals)
    .slice(0, 5)
  
  const awayTopPerformers = awayPlayerStatsList
    .map((stat: any) => ({
      player_id: String(stat.player_id),
      player_name: stat.player_name || stat.player_full_name || '',
      goals: Number(stat.goals ?? stat.g ?? 0),
      assists: Number(stat.assists ?? stat.a ?? 0),
      points: Number(stat.points ?? stat.pts ?? (Number(stat.goals ?? stat.g ?? 0) + Number(stat.assists ?? stat.a ?? 0))),
    }))
    .sort((a, b) => b.points - a.points || b.goals - a.goals)
    .slice(0, 5)

  // Calculate Three Stars - combine all players and get top 3 by points/impact
  const allPlayerPerformers = [
    ...homePlayerStatsList.map((stat: any) => ({
      player_id: String(stat.player_id),
      player_name: stat.player_name || stat.player_full_name || '',
      player_image: playerImageMap.get(String(stat.player_id)) || null,
      team_name: game.home_team_name,
      team_id: String(homeTeamId),
      team_logo: homeTeam?.team_logo || null,
      team_cd: homeTeam?.team_cd,
      primary_color: homeTeam?.primary_color || homeTeam?.team_color1,
      goals: Number(stat.goals ?? stat.g ?? 0),
      assists: Number(stat.assists ?? stat.a ?? 0),
      points: Number(stat.points ?? stat.pts ?? (Number(stat.goals ?? stat.g ?? 0) + Number(stat.assists ?? stat.a ?? 0))),
      position: stat.position || stat.player_position,
    })),
    ...awayPlayerStatsList.map((stat: any) => ({
      player_id: String(stat.player_id),
      player_name: stat.player_name || stat.player_full_name || '',
      player_image: playerImageMap.get(String(stat.player_id)) || null,
      team_name: game.away_team_name,
      team_id: String(awayTeamId),
      team_logo: awayTeam?.team_logo || null,
      team_cd: awayTeam?.team_cd,
      primary_color: awayTeam?.primary_color || awayTeam?.team_color1,
      goals: Number(stat.goals ?? stat.g ?? 0),
      assists: Number(stat.assists ?? stat.a ?? 0),
      points: Number(stat.points ?? stat.pts ?? (Number(stat.goals ?? stat.g ?? 0) + Number(stat.assists ?? stat.a ?? 0))),
      position: stat.position || stat.player_position,
    })),
  ]
    .sort((a, b) => b.points - a.points || b.goals - a.goals)
    .slice(0, 3)

  // Get team game stats for additional details
  const { data: teamGameStatsData, error: teamGameStatsError } = await supabase
    .from('fact_team_game_stats')
    .select('*')
    .eq('game_id', gameIdNum)
    
  const teamGameStats = teamGameStatsError ? [] : (teamGameStatsData || [])
  
  const homeTeamGameStats = (teamGameStats || []).find((t: any) => 
    String(t.team_id) === String(homeTeamId) || t.team_name === game.home_team_name
  )
  const awayTeamGameStats = (teamGameStats || []).find((t: any) => 
    String(t.team_id) === String(awayTeamId) || t.team_name === game.away_team_name
  )
  
  // Get special teams stats from schedule
  const homePPGoals = Number(game.home_pp_goals ?? 0)
  const homePPOpps = Number(game.home_pp_opportunities ?? 0)
  const awayPPGoals = Number(game.away_pp_goals ?? 0)
  const awayPPOpps = Number(game.away_pp_opportunities ?? 0)
  
  // Calculate team aggregates using helper function
  const homeTeamAggs = calculateTeamAggregates(homePlayerStatsList);
  const awayTeamAggs = calculateTeamAggregates(awayPlayerStatsList);
  
  // Calculate percentages using helper function
  const homeCFPct = calculatePercentage(homeTeamAggs.cf, homeTeamAggs.ca);
  const homeFFPct = calculatePercentage(homeTeamAggs.ff, homeTeamAggs.fa);
  const awayCFPct = calculatePercentage(awayTeamAggs.cf, awayTeamAggs.ca);
  const awayFFPct = calculatePercentage(awayTeamAggs.ff, awayTeamAggs.fa);
  
  const homeGoals = game.home_total_goals ?? 0;
  const awayGoals = game.away_total_goals ?? 0;
  
  // Shift counts per player are fetched from fact_shift_players via getGamePlayerShiftCounts
  // The playerShiftCounts Map is already extracted from the Promise.allSettled results

  // Create maps of player_id to advanced stats (with shift counts merged in)
  const createPlayerStatsMap = (statsList: (FactPlayerGameStats | Record<string, any>)[]) =>
    new Map<string, FactPlayerGameStats | Record<string, any>>(
      statsList.map((s) => {
        const playerId = String(s.player_id)
        const shiftCount = playerShiftCounts.get(playerId) ?? s.shifts ?? null
        return [playerId, { ...s, shifts: shiftCount }]
      })
    );

  const homePlayerStatsMap = createPlayerStatsMap(homePlayerStatsList);
  const awayPlayerStatsMap = createPlayerStatsMap(awayPlayerStatsList);

  // Helper function to check if a player has game stats available (more reliable than just hasVideo)
  const hasPlayerGameStats = (playerId: string | null | undefined): boolean => {
    if (!playerId) return false
    const playerIdStr = String(playerId)
    return homePlayerStatsMap.has(playerIdStr) || awayPlayerStatsMap.has(playerIdStr)
  }

  // Helper function to get player link - links to game stats if available, otherwise player profile
  const getPlayerGameLink = (playerId: string | null | undefined): string | null => {
    if (!playerId) return null
    const playerIdStr = String(playerId)
    // Check if player has game stats OR if game is tracked
    if (hasPlayerGameStats(playerIdStr) || hasTracking) {
      return `/norad/players/${playerIdStr}/games/${gameIdNum}`
    }
    return `/norad/players/${playerIdStr}`
  }
  
  // Check if this is a championship game (last game of the season, but not current season)
  let isChampionshipGame = false
  if (game.season_id) {
    // Get current season to exclude it (championship hasn't been determined yet)
    const { data: currentSeasonData } = await supabase
      .from('v_standings_current')
      .select('season_id')
      .limit(1)
      .maybeSingle()
    
    const currentSeason = currentSeasonData?.season_id || null
    
    // Only check for championship if this is NOT the current season
    if (currentSeason && game.season_id !== currentSeason) {
      const { data: lastGame } = await supabase
        .from('dim_schedule')
        .select('game_id')
        .eq('season_id', game.season_id)
        .not('home_total_goals', 'is', null)
        .not('away_total_goals', 'is', null)
        .order('date', { ascending: false })
        .order('game_id', { ascending: false })
        .limit(1)
        .maybeSingle()
      
      if (lastGame?.game_id === gameIdNum) {
        isChampionshipGame = true
      }
    }
  }
  
  const gameType = game.game_type || 'Regular'
  const isPlayoff = gameType === 'Playoffs' || gameType === 'playoffs' || gameType === 'Playoff'
  
  return (
    <div className="space-y-6">
      {/* Back Link and NORAD Link */}
      <div className="flex items-center justify-between">
        <Link 
          href="/norad/games" 
          className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Games
        </Link>
        {(game as any).game_url && (
          <a
            href={(game as any).game_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-primary transition-colors"
            title="View on NORAD Hockey"
          >
            <ExternalLink className="w-4 h-4" />
            <span>View on NORAD</span>
          </a>
        )}
      </div>
      
      {/* Scoreboard - ESPN-Style Centered Layout */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="bg-gradient-to-r from-primary/10 via-transparent to-primary/10 p-6">
          {/* Game Status Badge */}
          <div className="flex items-center justify-center gap-3 mb-4">
            {(() => {
              // Determine if game went to OT from dim_schedule data
              const gameAny = game as any
              const homeOTGoals = Number(gameAny.home_team_periodOT_goals) || 0
              const awayOTGoals = Number(gameAny.away_team_periodOT_goals) || 0
              const hasOT = homeOTGoals > 0 || awayOTGoals > 0
              const statusText = hasOT ? 'FINAL/OT' : 'FINAL'

              return (
                <span className="px-3 py-1 bg-muted text-foreground font-mono text-xs font-bold uppercase tracking-wider rounded">
                  {statusText}
                </span>
              )
            })()}
            {isPlayoff && (
              <span className="px-3 py-1 bg-primary/20 text-primary font-mono text-xs font-bold uppercase tracking-wider rounded">
                Playoffs
              </span>
            )}
          </div>

          {/* Championship Banner */}
          {isChampionshipGame && (
            <div className="flex items-center justify-center gap-2 mb-4">
              <Trophy className="w-5 h-5 text-yellow-500 fill-yellow-500" />
              <span className="font-display text-lg font-bold text-yellow-500 uppercase tracking-wider">
                Championship Game
              </span>
              <Trophy className="w-5 h-5 text-yellow-500 fill-yellow-500" />
            </div>
          )}

          {/* Centered Score Display */}
          <div className="flex items-center justify-center gap-4 md:gap-8">
            {/* Away Team */}
            <div className="flex items-center gap-3 md:gap-4">
              {awayTeam && (
                <Link
                  href={`/norad/team/${(awayTeam.team_name || game.away_team_name || '').replace(/\s+/g, '_')}`}
                  className="hover:opacity-80 transition-opacity"
                >
                  <TeamLogo
                    src={awayTeam.team_logo || null}
                    name={awayTeam.team_name || game.away_team_name || ''}
                    abbrev={awayTeam.team_cd}
                    primaryColor={awayTeam.primary_color || awayTeam.team_color1}
                    secondaryColor={awayTeam.team_color2}
                    size="xl"
                  />
                </Link>
              )}
              <div className="text-right">
                {awayTeam?.team_name || game.away_team_name ? (
                  <Link
                    href={`/norad/team/${(awayTeam?.team_name || game.away_team_name || '').replace(/\s+/g, '_')}`}
                    className="font-display text-lg md:text-xl font-bold text-foreground hover:text-primary transition-colors block"
                  >
                    {game.away_team_name || 'Away'}
                  </Link>
                ) : (
                  <div className="font-display text-lg md:text-xl font-bold text-foreground">
                    {game.away_team_name || 'Away'}
                  </div>
                )}
                <div className="text-xs text-muted-foreground font-mono">AWAY</div>
              </div>
            </div>

            {/* Score */}
            <div className="flex items-center gap-3 md:gap-6">
              <div className={cn(
                'font-mono text-5xl md:text-6xl font-bold tabular-nums',
                awayGoals > homeGoals ? 'text-foreground' : 'text-muted-foreground'
              )}>
                {awayGoals}
              </div>
              <div className="text-2xl md:text-3xl text-muted-foreground font-mono">-</div>
              <div className={cn(
                'font-mono text-5xl md:text-6xl font-bold tabular-nums',
                homeGoals > awayGoals ? 'text-foreground' : 'text-muted-foreground'
              )}>
                {homeGoals}
              </div>
            </div>

            {/* Home Team */}
            <div className="flex items-center gap-3 md:gap-4">
              <div className="text-left">
                {homeTeam?.team_name || game.home_team_name ? (
                  <Link
                    href={`/norad/team/${(homeTeam?.team_name || game.home_team_name || '').replace(/\s+/g, '_')}`}
                    className="font-display text-lg md:text-xl font-bold text-foreground hover:text-primary transition-colors block"
                  >
                    {game.home_team_name || 'Home'}
                  </Link>
                ) : (
                  <div className="font-display text-lg md:text-xl font-bold text-foreground">
                    {game.home_team_name || 'Home'}
                  </div>
                )}
                <div className="text-xs text-muted-foreground font-mono">HOME</div>
              </div>
              {homeTeam && (
                <Link
                  href={`/norad/team/${(homeTeam.team_name || game.home_team_name || '').replace(/\s+/g, '_')}`}
                  className="hover:opacity-80 transition-opacity"
                >
                  <TeamLogo
                    src={homeTeam.team_logo || null}
                    name={homeTeam.team_name || game.home_team_name || ''}
                    abbrev={homeTeam.team_cd}
                    primaryColor={homeTeam.primary_color || homeTeam.team_color1}
                    secondaryColor={homeTeam.team_color2}
                    size="xl"
                  />
                </Link>
              )}
            </div>
          </div>

          {/* Date */}
          <div className="text-center mt-4">
            <div className="text-sm font-mono text-muted-foreground">
              {game.date ? new Date(game.date).toLocaleDateString('en-US', {
                weekday: 'long',
                month: 'long',
                day: 'numeric',
                year: 'numeric'
              }) : ''}
            </div>
          </div>
        </div>
        
        {/* Compact Period Score Table - Using dim_schedule data */}
        {(() => {
          // Get period goals directly from dim_schedule (source of truth)
          const gameAny = game as any
          const homeP1 = Number(gameAny.home_team_period1_goals) || 0
          const awayP1 = Number(gameAny.away_team_period1_goals) || 0
          const homeP2 = Number(gameAny.home_team_period2_goals) || 0
          const awayP2 = Number(gameAny.away_team_period2_goals) || 0
          const homeP3 = Number(gameAny.home_team_period3_goals) || 0
          const awayP3 = Number(gameAny.away_team_period3_goals) || 0
          const homeOT = Number(gameAny.home_team_periodOT_goals) || 0
          const awayOT = Number(gameAny.away_team_periodOT_goals) || 0

          // Build OT periods array if there were OT goals
          const otPeriods: Array<{ period: number; home: number; away: number }> = []
          if (homeOT > 0 || awayOT > 0) {
            otPeriods.push({ period: 4, home: homeOT, away: awayOT })
          }

          // Don't show if no period data at all
          const hasAnyPeriodData = homeP1 > 0 || awayP1 > 0 || homeP2 > 0 || awayP2 > 0 || homeP3 > 0 || awayP3 > 0 || otPeriods.length > 0
          if (!hasAnyPeriodData) {
            return null
          }

          return (
            <div className="px-4 py-3 bg-accent/50 border-t border-border">
              <table className="w-full max-w-md mx-auto text-sm">
                <thead>
                  <tr className="text-muted-foreground font-mono text-xs">
                    <th className="text-left py-1 w-24"></th>
                    <th className="text-center py-1 w-10">1</th>
                    <th className="text-center py-1 w-10">2</th>
                    <th className="text-center py-1 w-10">3</th>
                    {otPeriods.map((ot, idx) => (
                      <th key={`ot-header-${ot.period}`} className="text-center py-1 w-10">OT{idx + 1}</th>
                    ))}
                    <th className="text-center py-1 w-10 font-semibold text-foreground">T</th>
                  </tr>
                </thead>
                <tbody className="font-mono">
                  {/* Away Team Row */}
                  <tr>
                    <td className="py-1.5">
                      <div className="flex items-center gap-2">
                        {awayTeam && (
                          <TeamLogo
                            src={awayTeam.team_logo || null}
                            name={awayTeam.team_name || ''}
                            abbrev={awayTeam.team_cd}
                            primaryColor={awayTeam.primary_color || awayTeam.team_color1}
                            size="xs"
                          />
                        )}
                        <span className="text-xs text-muted-foreground">{awayTeam?.team_cd || game.away_team_name?.substring(0, 3).toUpperCase() || 'AWY'}</span>
                      </div>
                    </td>
                    <td className="text-center py-1.5">{awayP1}</td>
                    <td className="text-center py-1.5">{awayP2}</td>
                    <td className="text-center py-1.5">{awayP3}</td>
                    {otPeriods.map(ot => (
                      <td key={`away-ot-${ot.period}`} className="text-center py-1.5">{ot.away}</td>
                    ))}
                    <td className={cn(
                      'text-center py-1.5 font-bold',
                      awayGoals > homeGoals ? 'text-foreground' : 'text-muted-foreground'
                    )}>{awayGoals}</td>
                  </tr>
                  {/* Home Team Row */}
                  <tr>
                    <td className="py-1.5">
                      <div className="flex items-center gap-2">
                        {homeTeam && (
                          <TeamLogo
                            src={homeTeam.team_logo || null}
                            name={homeTeam.team_name || ''}
                            abbrev={homeTeam.team_cd}
                            primaryColor={homeTeam.primary_color || homeTeam.team_color1}
                            size="xs"
                          />
                        )}
                        <span className="text-xs text-muted-foreground">{homeTeam?.team_cd || game.home_team_name?.substring(0, 3).toUpperCase() || 'HOM'}</span>
                      </div>
                    </td>
                    <td className="text-center py-1.5">{homeP1}</td>
                    <td className="text-center py-1.5">{homeP2}</td>
                    <td className="text-center py-1.5">{homeP3}</td>
                    {otPeriods.map(ot => (
                      <td key={`home-ot-${ot.period}`} className="text-center py-1.5">{ot.home}</td>
                    ))}
                    <td className={cn(
                      'text-center py-1.5 font-bold',
                      homeGoals > awayGoals ? 'text-foreground' : 'text-muted-foreground'
                    )}>{homeGoals}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          )
        })()}
      </div>

      {/* Media Section: Video, Highlights, Three Stars, Team Stats */}
      <GameMediaSection
        videos={gameVideos}
        highlights={gameHighlights}
        stars={allPlayerPerformers.slice(0, 3)}
        gameId={gameIdNum}
        homeTeam={game.home_team_name || 'Home'}
        awayTeam={game.away_team_name || 'Away'}
        homeColor={homeTeam?.primary_color || homeTeam?.team_color1 || '#1e40af'}
        awayColor={awayTeam?.primary_color || awayTeam?.team_color1 || '#dc2626'}
        teamStatsContent={
          (homeTeamGameStats || awayTeamGameStats || homePPOpps > 0 || awayPPOpps > 0) ? (
            <CompactTeamStats
              awayTeamAbbrev={awayTeam?.team_cd || game.away_team_name?.substring(0, 3).toUpperCase() || 'AWY'}
              homeTeamAbbrev={homeTeam?.team_cd || game.home_team_name?.substring(0, 3).toUpperCase() || 'HOM'}
              stats={[
                // Avg Rating - calculated from roster players
                ...(() => {
                  const allAwaySkaters = [...awayForwards, ...awayDefense]
                  const allHomeSkaters = [...homeForwards, ...homeDefense]
                  const awayWithRatings = allAwaySkaters.filter(p => {
                    const playerInfo = playersMap.get(String(p.player_id))
                    const rating = playerInfo?.current_skill_rating
                    return rating != null && rating !== '' && Number(rating) > 0
                  })
                  const homeWithRatings = allHomeSkaters.filter(p => {
                    const playerInfo = playersMap.get(String(p.player_id))
                    const rating = playerInfo?.current_skill_rating
                    return rating != null && rating !== '' && Number(rating) > 0
                  })
                  const awayAvgRating = awayWithRatings.length > 0
                    ? awayWithRatings.reduce((sum, p) => {
                        const playerInfo = playersMap.get(String(p.player_id))
                        return sum + Number(playerInfo?.current_skill_rating || 0)
                      }, 0) / awayWithRatings.length
                    : null
                  const homeAvgRating = homeWithRatings.length > 0
                    ? homeWithRatings.reduce((sum, p) => {
                        const playerInfo = playersMap.get(String(p.player_id))
                        return sum + Number(playerInfo?.current_skill_rating || 0)
                      }, 0) / homeWithRatings.length
                    : null

                  if (awayAvgRating !== null || homeAvgRating !== null) {
                    return [{
                      label: 'Avg Rating',
                      away: awayAvgRating !== null ? awayAvgRating.toFixed(1) : '-',
                      home: homeAvgRating !== null ? homeAvgRating.toFixed(1) : '-',
                      awayWins: (awayAvgRating || 0) > (homeAvgRating || 0),
                      homeWins: (homeAvgRating || 0) > (awayAvgRating || 0),
                    }]
                  }
                  return []
                })(),
                // Shot Attempts (total)
                ...(homeTeamGameStats?.shots || awayTeamGameStats?.shots || homeTeamAggs.shots > 0 || awayTeamAggs.shots > 0 ? [{
                  label: 'Shot Attempts',
                  away: awayTeamGameStats?.shots ?? awayTeamAggs.shots ?? 0,
                  home: homeTeamGameStats?.shots ?? homeTeamAggs.shots ?? 0,
                  awayWins: (awayTeamGameStats?.shots ?? awayTeamAggs.shots ?? 0) > (homeTeamGameStats?.shots ?? homeTeamAggs.shots ?? 0),
                  homeWins: (homeTeamGameStats?.shots ?? homeTeamAggs.shots ?? 0) > (awayTeamGameStats?.shots ?? awayTeamAggs.shots ?? 0),
                }] : []),
                // SOG (shots on goal)
                ...(homeTeamGameStats?.sog || awayTeamGameStats?.sog ? [{
                  label: 'SOG',
                  away: awayTeamGameStats?.sog ?? 0,
                  home: homeTeamGameStats?.sog ?? 0,
                  awayWins: (awayTeamGameStats?.sog ?? 0) > (homeTeamGameStats?.sog ?? 0),
                  homeWins: (homeTeamGameStats?.sog ?? 0) > (awayTeamGameStats?.sog ?? 0),
                }] : []),
                // Shooting %
                ...(homeTeamGameStats?.shooting_pct || awayTeamGameStats?.shooting_pct ? [{
                  label: 'SH%',
                  away: awayTeamGameStats?.shooting_pct ? `${Number(awayTeamGameStats.shooting_pct).toFixed(1)}%` : '-',
                  home: homeTeamGameStats?.shooting_pct ? `${Number(homeTeamGameStats.shooting_pct).toFixed(1)}%` : '-',
                  awayWins: Number(awayTeamGameStats?.shooting_pct || 0) > Number(homeTeamGameStats?.shooting_pct || 0),
                  homeWins: Number(homeTeamGameStats?.shooting_pct || 0) > Number(awayTeamGameStats?.shooting_pct || 0),
                }] : []),
                // xG (expected goals)
                ...(homeTeamGameStats?.xg_for || awayTeamGameStats?.xg_for ? [{
                  label: 'xG',
                  away: awayTeamGameStats?.xg_for ? Number(awayTeamGameStats.xg_for).toFixed(2) : '-',
                  home: homeTeamGameStats?.xg_for ? Number(homeTeamGameStats.xg_for).toFixed(2) : '-',
                  awayWins: Number(awayTeamGameStats?.xg_for || 0) > Number(homeTeamGameStats?.xg_for || 0),
                  homeWins: Number(homeTeamGameStats?.xg_for || 0) > Number(awayTeamGameStats?.xg_for || 0),
                }] : []),
                // FO% (faceoff percentage) - placeholder, needs ETL aggregation
                // TODO: Aggregate from fact_player_game_stats fo_wins/fo_losses
                // Power Play
                ...(homePPOpps > 0 || awayPPOpps > 0 ? [{
                  label: 'PP',
                  away: `${awayPPGoals || 0}/${awayPPOpps || 0}`,
                  home: `${homePPGoals || 0}/${homePPOpps || 0}`,
                }] : []),
                // PIM (penalty minutes) - placeholder, needs ETL aggregation
                // TODO: Aggregate from fact_penalties
                // Hits
                ...(homeTeamGameStats?.hits || awayTeamGameStats?.hits || homeTeamAggs.hits > 0 || awayTeamAggs.hits > 0 ? [{
                  label: 'Hits',
                  away: awayTeamGameStats?.hits ?? homeTeamAggs.hits ?? 0,
                  home: homeTeamGameStats?.hits ?? homeTeamAggs.hits ?? 0,
                  awayWins: (awayTeamGameStats?.hits ?? awayTeamAggs.hits ?? 0) > (homeTeamGameStats?.hits ?? homeTeamAggs.hits ?? 0),
                  homeWins: (homeTeamGameStats?.hits ?? homeTeamAggs.hits ?? 0) > (awayTeamGameStats?.hits ?? awayTeamAggs.hits ?? 0),
                }] : []),
                // Corsi For %
                ...(hasTracking && (homeTeamGameStats?.cf_pct || awayTeamGameStats?.cf_pct || homeCFPct > 0 || awayCFPct > 0) ? [{
                  label: 'CF%',
                  away: `${awayTeamGameStats?.cf_pct ? Number(awayTeamGameStats.cf_pct).toFixed(0) : awayCFPct.toFixed(0)}%`,
                  home: `${homeTeamGameStats?.cf_pct ? Number(homeTeamGameStats.cf_pct).toFixed(0) : homeCFPct.toFixed(0)}%`,
                  awayWins: (Number(awayTeamGameStats?.cf_pct) || awayCFPct) > (Number(homeTeamGameStats?.cf_pct) || homeCFPct),
                  homeWins: (Number(homeTeamGameStats?.cf_pct) || homeCFPct) > (Number(awayTeamGameStats?.cf_pct) || awayCFPct),
                }] : []),
                // Fenwick For %
                ...(hasTracking && (homeTeamGameStats?.ff_pct || awayTeamGameStats?.ff_pct || homeFFPct > 0 || awayFFPct > 0) ? [{
                  label: 'FF%',
                  away: `${awayTeamGameStats?.ff_pct ? Number(awayTeamGameStats.ff_pct).toFixed(0) : awayFFPct.toFixed(0)}%`,
                  home: `${homeTeamGameStats?.ff_pct ? Number(homeTeamGameStats.ff_pct).toFixed(0) : homeFFPct.toFixed(0)}%`,
                  awayWins: (Number(awayTeamGameStats?.ff_pct) || awayFFPct) > (Number(homeTeamGameStats?.ff_pct) || homeFFPct),
                  homeWins: (Number(homeTeamGameStats?.ff_pct) || homeFFPct) > (Number(awayTeamGameStats?.ff_pct) || awayFFPct),
                }] : []),
                // Takeaways
                ...(homeTeamGameStats?.takeaways || awayTeamGameStats?.takeaways || homeTeamAggs.takeaways > 0 || awayTeamAggs.takeaways > 0 ? [{
                  label: 'Takeaways',
                  away: awayTeamGameStats?.takeaways ?? awayTeamAggs.takeaways ?? 0,
                  home: homeTeamGameStats?.takeaways ?? homeTeamAggs.takeaways ?? 0,
                  awayWins: (awayTeamGameStats?.takeaways ?? awayTeamAggs.takeaways ?? 0) > (homeTeamGameStats?.takeaways ?? homeTeamAggs.takeaways ?? 0),
                  homeWins: (homeTeamGameStats?.takeaways ?? homeTeamAggs.takeaways ?? 0) > (awayTeamGameStats?.takeaways ?? awayTeamAggs.takeaways ?? 0),
                }] : []),
                // Giveaways
                ...(homeTeamGameStats?.giveaways || awayTeamGameStats?.giveaways || homeTeamAggs.badGiveaways > 0 || awayTeamAggs.badGiveaways > 0 ? [{
                  label: 'Giveaways',
                  away: awayTeamGameStats?.giveaways ?? awayTeamAggs.badGiveaways ?? 0,
                  home: homeTeamGameStats?.giveaways ?? homeTeamAggs.badGiveaways ?? 0,
                  awayWins: (awayTeamGameStats?.giveaways ?? awayTeamAggs.badGiveaways ?? 0) < (homeTeamGameStats?.giveaways ?? homeTeamAggs.badGiveaways ?? 0),
                  homeWins: (homeTeamGameStats?.giveaways ?? homeTeamAggs.badGiveaways ?? 0) < (awayTeamGameStats?.giveaways ?? awayTeamAggs.badGiveaways ?? 0),
                }] : []),
                // Forechecks
                ...(homeTeamGameStats?.forechecks || awayTeamGameStats?.forechecks ? [{
                  label: 'Forechecks',
                  away: awayTeamGameStats?.forechecks ?? 0,
                  home: homeTeamGameStats?.forechecks ?? 0,
                  awayWins: (awayTeamGameStats?.forechecks ?? 0) > (homeTeamGameStats?.forechecks ?? 0),
                  homeWins: (homeTeamGameStats?.forechecks ?? 0) > (awayTeamGameStats?.forechecks ?? 0),
                }] : []),
              ]}
              viewAllLink={`/norad/games/${gameIdNum}/analysis`}
            />
          ) : undefined
        }
      />

      {/* Scoring Summary - Grouped by Period */}
      {(() => {
        // Use allEvents filtered for ACTUAL goals per CLAUDE.md rules:
        // Goals are ONLY counted when event_type='Goal' AND event_detail='Goal_Scored'
        const allGoalsFromEvents = allEvents.filter((event: any) =>
          event.event_type === 'Goal' && event.event_detail === 'Goal_Scored'
        )

        // Combine with goalsData to ensure we don't miss any goals
        const allGoals = [...goalsData]
        allGoalsFromEvents.forEach((event: any) => {
          // Only add if not already in goalsData (by event_id)
          if (event.event_id && !allGoals.find(g => g.event_id === event.event_id)) {
            allGoals.push(event)
          }
        })

        if (allGoals.length === 0) return null
        
        // Helper function to get period (used throughout)
        const getPeriod = (goal: GameEvent): number => {
          if (typeof goal.period === 'number') return goal.period
          if (typeof goal.period === 'string') {
            const parsed = parseInt(goal.period, 10)
            return isNaN(parsed) ? 1 : parsed
          }
          return 1
        }
        
        // First, sort all goals chronologically to calculate running score
        // time_start_total_seconds is elapsed time from game start, so ASCENDING = first goal first
        const allGoalsSorted = [...allGoals].sort((a: GameEvent, b: GameEvent) => {
          const periodA = getPeriod(a)
          const periodB = getPeriod(b)
          if (periodA !== periodB) {
            return periodA - periodB
          }
          // Within same period, sort by elapsed time ASCENDING (lower time = earlier in period)
          const timeA = a.time_start_total_seconds ?? a.time_seconds ?? 0
          const timeB = b.time_start_total_seconds ?? b.time_seconds ?? 0
          return timeA - timeB
        })
        
        // Calculate running score for each goal
        let homeScore = 0
        let awayScore = 0
        const goalScores = new Map<string, { home: number; away: number }>()
        
        allGoalsSorted.forEach((goal: GameEvent) => {
          // Determine scoring team - check multiple fields (same logic as display)
          const teamId = goal.team_id || (goal as any).event_team_id || null
          const scoringTeamId = teamId ? String(teamId) : null
          
          // Try to match by team ID first
          let isHomeGoal = false
          let isAwayGoal = false
          
          if (scoringTeamId) {
            if (scoringTeamId === String(homeTeamId)) {
              isHomeGoal = true
            } else if (scoringTeamId === String(awayTeamId)) {
              isAwayGoal = true
            }
          }
          
          // Fallback: try to match by team name if ID matching failed
          if (!isHomeGoal && !isAwayGoal) {
            const teamName = (goal as any).player_team || (goal as any).event_team || (goal as any).home_team || (goal as any).away_team || null
            if (teamName) {
              if (teamName === game.home_team_name || teamName === homeTeam?.team_name) {
                isHomeGoal = true
              } else if (teamName === game.away_team_name || teamName === awayTeam?.team_name) {
                isAwayGoal = true
              }
            }
          }
          
          // Final fallback: use team_venue field
          if (!isHomeGoal && !isAwayGoal && (goal as any).team_venue) {
            if ((goal as any).team_venue === 'Home' || (goal as any).team_venue === 'home') {
              isHomeGoal = true
            } else if ((goal as any).team_venue === 'Away' || (goal as any).team_venue === 'away') {
              isAwayGoal = true
            }
          }
          
          // Update scores
          if (isHomeGoal) {
            homeScore++
          } else if (isAwayGoal) {
            awayScore++
          }
          
          // Use event_id as primary key, fallback to a consistent constructed key
          const goalKey = goal.event_id || `${getPeriod(goal)}-${goal.time_start_total_seconds ?? goal.time_seconds ?? 0}-${scoringTeamId || 'unknown'}`
          goalScores.set(goalKey, { home: homeScore, away: awayScore })
        })
        
        // Group goals by period
        const goalsByPeriod = new Map<number, GameEvent[]>()
        allGoals.forEach((goal: GameEvent) => {
          const period = getPeriod(goal)
          if (!goalsByPeriod.has(period)) {
            goalsByPeriod.set(period, [])
          }
          goalsByPeriod.get(period)!.push(goal)
        })
        
        // Sort periods
        const periods = Array.from(goalsByPeriod.keys()).sort((a, b) => a - b)
        
        return (
          <div className="bg-card rounded-xl border border-border overflow-hidden">
            <div className="px-4 py-3 bg-accent border-b border-border">
              <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                <Target className="w-4 h-4 text-goal" />
                Scoring Summary ({allGoals.length})
              </h2>
            </div>
            <div className="divide-y divide-border">
              {periods.map((period) => {
                const periodGoals = goalsByPeriod.get(period)!
                  // Sort goals within period by elapsed time ASCENDING (lower time = earlier goal)
                  .sort((a: GameEvent, b: GameEvent) => {
                    const timeA = a.time_start_total_seconds ?? a.time_seconds ?? 0
                    const timeB = b.time_start_total_seconds ?? b.time_seconds ?? 0
                    return timeA - timeB
                  })
                
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
                    {periodGoals.map((goal: GameEvent, index: number) => {
                      // Use event_start_min/sec (countdown time) if available
                      // Otherwise fall back to calculating from total seconds
                      let minutes: number
                      let seconds: number

                      if (goal.event_start_min !== undefined && goal.event_start_sec !== undefined) {
                        // Use countdown time directly from data
                        minutes = goal.event_start_min
                        seconds = goal.event_start_sec
                      } else {
                        // Calculate countdown from elapsed time (20:00 - elapsed)
                        const timeSeconds = goal.time_start_total_seconds ?? goal.time_seconds ?? 0
                        const periodSecondsElapsed = timeSeconds % 1200 // 20 minutes = 1200 seconds
                        const periodSecondsRemaining = 1200 - periodSecondsElapsed
                        minutes = Math.floor(periodSecondsRemaining / 60)
                        seconds = Math.floor(periodSecondsRemaining % 60)
                      }
                      const timeStr = `${minutes}:${seconds.toString().padStart(2, '0')}`
                      
                      // Determine which team scored - check multiple fields
                      const teamId = goal.team_id || (goal as any).event_team_id || null
                      const scoringTeamId = teamId ? String(teamId) : null
                      
                      // Try to match by team ID first
                      let scoringTeam: DimTeam | null = null
                      if (scoringTeamId) {
                        if (scoringTeamId === String(homeTeamId)) {
                          scoringTeam = homeTeam
                        } else if (scoringTeamId === String(awayTeamId)) {
                          scoringTeam = awayTeam
                        }
                      }
                      
                      // Fallback: try to match by team name if ID matching failed
                      if (!scoringTeam) {
                        const teamName = (goal as any).player_team || (goal as any).event_team || (goal as any).home_team || (goal as any).away_team || null
                        if (teamName) {
                          if (teamName === game.home_team_name || teamName === homeTeam?.team_name) {
                            scoringTeam = homeTeam
                          } else if (teamName === game.away_team_name || teamName === awayTeam?.team_name) {
                            scoringTeam = awayTeam
                          }
                        }
                      }
                      
                      // Final fallback: use team_venue field
                      if (!scoringTeam && (goal as any).team_venue) {
                        if ((goal as any).team_venue === 'Home' || (goal as any).team_venue === 'home') {
                          scoringTeam = homeTeam
                        } else if ((goal as any).team_venue === 'Away' || (goal as any).team_venue === 'away') {
                          scoringTeam = awayTeam
                        }
                      }
                      
                      // Get video link for this goal
                      const goalVideoTime = goal.running_video_time || goal.time_start_total_seconds
                      const goalVideoUrl = goal.video_url || game.video_url_1 || game.video_url_2
                      const videoStartOffset = game.video_start_offset || 0
                      const videoLink = goalVideoUrl && goalVideoTime 
                        ? `${goalVideoUrl}#t=${Math.max(0, (goalVideoTime || 0) - videoStartOffset)}`
                        : null
                      
                      // Get scorer info
                      let scorerName: string | null = null
                      let scorerId: string | null = null
                      
                      // First, try to get player ID from event_player_ids
                      if (goal.event_id && goalEventPlayerIdsMap.has(goal.event_id)) {
                        scorerId = goalEventPlayerIdsMap.get(goal.event_id)!
                        const scorerPlayer = playersMap.get(scorerId)
                        scorerName = scorerPlayer?.player_name || scorerPlayer?.player_full_name || null
                      }
                      
                      // If no ID found, try player_name field
                      if (!scorerName && goal.player_name) {
                        scorerName = goal.player_name
                        scorerId = playerNameToIdMap.get(goal.player_name.toLowerCase().trim()) || null
                      }
                      
                      // Fallback to event_player_1
                      if (!scorerName && goal.event_player_1) {
                        scorerName = goal.event_player_1
                        scorerId = playerNameToIdMap.get(goal.event_player_1.toLowerCase().trim()) || null
                      }
                      
                      // Get player image
                      const scorerPlayer = scorerId ? playersMap.get(scorerId) : null
                      const scorerImage = scorerPlayer?.player_image || null
                      
                      // Get running score for this goal - use same key format as when storing
                      const goalKey = goal.event_id || `${getPeriod(goal)}-${goal.time_start_total_seconds ?? goal.time_seconds ?? 0}-${scoringTeamId || 'unknown'}`
                      const runningScore = goalScores.get(goalKey) || { home: 0, away: 0 }
                      
                      // Determine score format: away - home (standard hockey format)
                      const scoreStr = `${runningScore.away}-${runningScore.home}`
                      
                      // Get goal details for expanded view
                      const shotX = (goal as any).puck_x_start ?? null
                      const shotY = (goal as any).puck_y_start ?? null
                      const strength = (goal as any).strength ?? null
                      const isRush = (goal as any).is_rush === 1
                      const isRebound = (goal as any).is_rebound === 1
                      const goalieName = (goal as any).goalie_name ?? null

                      return (
                        <details key={`${period}-${index}`} className="group">
                          <summary className="p-4 flex items-center gap-3 hover:bg-muted/30 transition-colors cursor-pointer list-none">
                            {/* Time */}
                            <div className="w-14 text-center flex-shrink-0">
                              <div className="font-mono text-sm font-semibold text-foreground">{timeStr}</div>
                            </div>

                            {/* Team Logo */}
                            {scoringTeam && (
                              <TeamLogo
                                src={scoringTeam.team_logo || null}
                                name={scoringTeam.team_name || ''}
                                abbrev={scoringTeam.team_cd}
                                primaryColor={scoringTeam.primary_color || scoringTeam.team_color1}
                                secondaryColor={scoringTeam.team_color2}
                                size="sm"
                              />
                            )}

                            {/* Player Photo - Always show with fallback */}
                            <PlayerPhoto
                              src={scorerImage}
                              name={scorerName || 'Unknown'}
                              primaryColor={scoringTeam?.primary_color || scoringTeam?.team_color1}
                              size="sm"
                            />

                            {/* Player Info */}
                            <div className="flex-1 min-w-0">
                              {/* Goal Label + Scorer Name */}
                              <div className="flex items-center gap-2">
                                <span className="inline-flex items-center px-1.5 py-0.5 rounded bg-green-500/20 text-green-600 dark:text-green-400 text-xs font-bold uppercase tracking-wide">
                                  Goal
                                </span>
                                <span className="font-display text-sm font-semibold text-foreground truncate">
                                  {scorerName || 'Unknown Scorer'}
                                </span>
                              </div>
                              {/* Compact assists display */}
                              {(() => {
                                const goalKey = goal.event_id || String(goal.time_start_total_seconds || index)
                                const assists = assistEventsMap.get(goalKey) ||
                                              (goal.event_id ? assistEventsMap.get(goal.event_id) : null) ||
                                              (goal.time_start_total_seconds ? assistEventsMap.get(String(goal.time_start_total_seconds)) : null)

                                if (assists && assists.length > 0) {
                                  return (
                                    <div className="text-xs text-muted-foreground mt-0.5 truncate">
                                      Assisted by: {assists.map(a => {
                                        const assistPlayer = playersMap.get(a.player_id)
                                        return assistPlayer?.player_name || assistPlayer?.player_full_name || a.player_name || 'Unknown'
                                      }).join(', ')}
                                    </div>
                                  )
                                }
                                if (goal.event_player_2) {
                                  return (
                                    <div className="text-xs text-muted-foreground mt-0.5 truncate">
                                      Assisted by: {goal.event_player_2}
                                    </div>
                                  )
                                }
                                return (
                                  <div className="text-xs text-muted-foreground mt-0.5 italic">
                                    Unassisted
                                  </div>
                                )
                              })()}
                            </div>

                            {/* Running Score */}
                            <div className="font-mono text-lg font-bold text-foreground tabular-nums flex-shrink-0">
                              {scoreStr}
                            </div>

                            {/* Expand Icon */}
                            <ChevronDown className="w-5 h-5 text-muted-foreground transition-transform group-open:rotate-180 flex-shrink-0" />
                          </summary>

                          {/* Expanded Details Panel */}
                          <div className="bg-muted/10 border-t border-border/50 p-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              {/* Left: Shot Location */}
                              <div className="space-y-2">
                                <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                                  <Target className="w-3 h-3" />
                                  Shot Location
                                </div>
                                <MiniShotRink
                                  shotX={shotX}
                                  shotY={shotY}
                                  isGoal={true}
                                />
                              </div>

                              {/* Right: Goal Details */}
                              <div className="space-y-3">
                                {/* Scorer with link */}
                                <div>
                                  <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">Scorer</div>
                                  {getPlayerGameLink(scorerId) ? (
                                    <Link
                                      href={getPlayerGameLink(scorerId)!}
                                      className="font-display text-sm font-semibold text-foreground hover:text-primary transition-colors"
                                    >
                                      {scorerName}
                                    </Link>
                                  ) : (
                                    <span className="font-display text-sm font-semibold text-foreground">
                                      {scorerName || 'Unknown'}
                                    </span>
                                  )}
                                </div>

                                {/* Assists with links */}
                                <div>
                                  <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">Assists</div>
                                  {(() => {
                                    const goalKey = goal.event_id || String(goal.time_start_total_seconds || index)
                                    const assists = assistEventsMap.get(goalKey) ||
                                                  (goal.event_id ? assistEventsMap.get(goal.event_id) : null) ||
                                                  (goal.time_start_total_seconds ? assistEventsMap.get(String(goal.time_start_total_seconds)) : null)

                                    if (assists && assists.length > 0) {
                                      const sortedAssists = [...assists].sort((a, b) => {
                                        if (a.assist_type === 'primary' && b.assist_type === 'secondary') return -1
                                        if (a.assist_type === 'secondary' && b.assist_type === 'primary') return 1
                                        return 0
                                      })
                                      return (
                                        <div className="space-y-1">
                                          {sortedAssists.map((assist, idx) => {
                                            const assistPlayer = playersMap.get(assist.player_id)
                                            const assistName = assistPlayer?.player_name || assistPlayer?.player_full_name || assist.player_name || 'Unknown'
                                            const assistLink = getPlayerGameLink(assist.player_id)
                                            return (
                                              <div key={idx} className="text-sm">
                                                {assistLink ? (
                                                  <Link href={assistLink} className="text-foreground hover:text-primary transition-colors">
                                                    {assistName}
                                                  </Link>
                                                ) : (
                                                  <span className="text-foreground">{assistName}</span>
                                                )}
                                                <span className="text-xs text-muted-foreground ml-1">({assist.assist_type})</span>
                                              </div>
                                            )
                                          })}
                                        </div>
                                      )
                                    }
                                    if (goal.event_player_2) {
                                      const assistId = playerNameToIdMap.get(goal.event_player_2.toLowerCase().trim()) || null
                                      const assistLink = getPlayerGameLink(assistId)
                                      return assistLink ? (
                                        <Link href={assistLink} className="text-sm text-foreground hover:text-primary transition-colors">
                                          {goal.event_player_2}
                                        </Link>
                                      ) : (
                                        <span className="text-sm text-foreground">{goal.event_player_2}</span>
                                      )
                                    }
                                    return <span className="text-sm text-muted-foreground italic">Unassisted</span>
                                  })()}
                                </div>

                                {/* Goalie */}
                                {goalieName && (
                                  <div>
                                    <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">Goalie</div>
                                    <span className="text-sm text-foreground">{goalieName}</span>
                                  </div>
                                )}

                                {/* Tags */}
                                <div className="flex flex-wrap gap-1.5">
                                  {strength && strength !== 'Even' && strength !== 'EV' && (
                                    <span className={cn(
                                      'px-2 py-0.5 rounded text-xs font-medium',
                                      strength === 'PP' ? 'bg-yellow-500/20 text-yellow-600 dark:text-yellow-400' :
                                      strength === 'SH' ? 'bg-red-500/20 text-red-600 dark:text-red-400' :
                                      'bg-muted text-muted-foreground'
                                    )}>
                                      {strength}
                                    </span>
                                  )}
                                  {isRush && (
                                    <span className="px-2 py-0.5 rounded bg-purple-500/20 text-purple-600 dark:text-purple-400 text-xs font-medium">
                                      Rush
                                    </span>
                                  )}
                                  {isRebound && (
                                    <span className="px-2 py-0.5 rounded bg-orange-500/20 text-orange-600 dark:text-orange-400 text-xs font-medium">
                                      Rebound
                                    </span>
                                  )}
                                </div>

                                {/* Video Link */}
                                {videoLink && hasVideo && (
                                  <div className="pt-2">
                                    <a
                                      href={videoLink}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="inline-flex items-center gap-2 px-3 py-1.5 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors text-sm"
                                    >
                                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                                        <path d="M8 5v14l11-7z"/>
                                      </svg>
                                      Watch Goal
                                    </a>
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        </details>
                      )
                    })}
                  </div>
                )
              })}
            </div>
          </div>
        )
      })()}

      {/* Head-to-Head Games This Season - Ticker Style */}
      {priorGamesData.headToHeadGames && priorGamesData.headToHeadGames.length > 0 && (() => {
        const allH2HGames = priorGamesData.headToHeadGames.sort((a: any, b: any) => {
          const dateA = a.date ? new Date(a.date).getTime() : 0
          const dateB = b.date ? new Date(b.date).getTime() : 0
          return dateA - dateB
        })

        return (
          <div className="bg-card rounded-xl border border-border overflow-hidden">
            <div className="px-4 py-3 bg-accent border-b border-border">
              <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                <Activity className="w-4 h-4" />
                Season Series ({allH2HGames.length})
              </h2>
            </div>
            <div className="p-3">
              <div className="flex items-stretch gap-2 overflow-x-auto pb-1 scrollbar-hide">
                {allH2HGames.map((h2hGame: any) => {
                  const hGoals = h2hGame.home_total_goals ?? null
                  const aGoals = h2hGame.away_total_goals ?? null
                  const hasScore = hGoals !== null && aGoals !== null
                  const homeWon = hasScore && hGoals > aGoals
                  const awayWon = hasScore && aGoals > hGoals
                  const isCurrentGame = h2hGame.game_id === gameIdNum
                  const isFutureGame = !hasScore
                  const isPlayoff = h2hGame.game_type === 'Playoffs' || h2hGame.game_type === 'playoffs' || h2hGame.game_type === 'Playoff'

                  // Determine which team data to use based on H2H game
                  const h2hHomeIsHome = String(h2hGame.home_team_id) === String(homeTeam?.team_id)
                  const displayHomeTeam = h2hHomeIsHome ? homeTeam : awayTeam
                  const displayAwayTeam = h2hHomeIsHome ? awayTeam : homeTeam

                  const gameDate = h2hGame.date ? new Date(h2hGame.date).toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric'
                  }) : ''

                  return (
                    <Link
                      key={h2hGame.game_id}
                      href={isCurrentGame ? '#' : `/norad/games/${h2hGame.game_id}`}
                      className={cn(
                        'flex flex-col px-3 py-2 rounded-lg border transition-all min-w-[100px] shrink-0',
                        isCurrentGame
                          ? 'bg-primary/15 border-primary ring-1 ring-primary/50'
                          : 'border-border hover:border-primary/50 hover:bg-muted/30',
                        isFutureGame && !isCurrentGame && 'opacity-60'
                      )}
                    >
                      {/* Date */}
                      <div className="text-[9px] font-mono text-muted-foreground text-center mb-1.5">
                        {gameDate}
                        {isPlayoff && <span className="ml-1 text-primary">P</span>}
                      </div>

                      {/* Away Team Row */}
                      <div className="flex items-center justify-between gap-1.5">
                        <div className="flex items-center gap-1">
                          <TeamLogo
                            src={displayAwayTeam?.team_logo || null}
                            name=""
                            abbrev={displayAwayTeam?.team_cd || ''}
                            primaryColor={displayAwayTeam?.primary_color || displayAwayTeam?.team_color1}
                            secondaryColor={displayAwayTeam?.team_color2}
                            size="xs"
                          />
                          <span className={cn(
                            'text-[10px] font-mono',
                            awayWon && 'font-bold'
                          )}>
                            {displayAwayTeam?.team_cd || 'AWY'}
                          </span>
                        </div>
                        {hasScore && (
                          <span className={cn(
                            'font-mono text-xs',
                            awayWon ? 'font-bold' : 'text-muted-foreground'
                          )}>
                            {aGoals}
                          </span>
                        )}
                      </div>

                      {/* Home Team Row */}
                      <div className="flex items-center justify-between gap-1.5 mt-0.5">
                        <div className="flex items-center gap-1">
                          <TeamLogo
                            src={displayHomeTeam?.team_logo || null}
                            name=""
                            abbrev={displayHomeTeam?.team_cd || ''}
                            primaryColor={displayHomeTeam?.primary_color || displayHomeTeam?.team_color1}
                            secondaryColor={displayHomeTeam?.team_color2}
                            size="xs"
                          />
                          <span className={cn(
                            'text-[10px] font-mono',
                            homeWon && 'font-bold'
                          )}>
                            {displayHomeTeam?.team_cd || 'HME'}
                          </span>
                        </div>
                        {hasScore ? (
                          <span className={cn(
                            'font-mono text-xs',
                            homeWon ? 'font-bold' : 'text-muted-foreground'
                          )}>
                            {hGoals}
                          </span>
                        ) : (
                          <span className="text-[8px] text-muted-foreground">TBD</span>
                        )}
                      </div>

                      {/* Status */}
                      <div className="text-[8px] font-mono text-center mt-1">
                        {isCurrentGame ? (
                          <span className="text-primary font-semibold">This Game</span>
                        ) : isFutureGame ? (
                          <span className="text-muted-foreground">Upcoming</span>
                        ) : (
                          <span className="text-muted-foreground">Final</span>
                        )}
                      </div>
                    </Link>
                  )
                })}
              </div>
            </div>
          </div>
        )
      })()}
      
      {/* Box Score Tables - Separated by Forwards/Defense */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Away Team - Forwards */}
        {(awayForwards.length > 0 || awayPlayers.length > 0) && (
          <div className="bg-card rounded-xl border border-border overflow-hidden">
            <div className="px-4 py-3 bg-accent border-b border-border">
              <div className="flex items-center gap-2">
                {awayTeam && (
                  <Link 
                    href={`/norad/team/${(awayTeam.team_name || game.away_team_name || '').replace(/\s+/g, '_')}`}
                    className="hover:opacity-80 transition-opacity"
                  >
                    <TeamLogo
                      src={awayTeam.team_logo || null}
                      name={awayTeam.team_name || ''}
                      abbrev={awayTeam.team_cd}
                      primaryColor={awayTeam.primary_color || awayTeam.team_color1}
                      secondaryColor={awayTeam.team_color2}
                      size="sm"
                    />
                  </Link>
                )}
                {awayTeam?.team_name || game.away_team_name ? (
                  <Link 
                    href={`/norad/team/${(awayTeam?.team_name || game.away_team_name || '').replace(/\s+/g, '_')}`}
                    className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2 hover:text-primary transition-colors"
                  >
                    <User className="w-4 h-4" />
                    {awayTeam?.team_name || game.away_team_name || 'Away'} Forwards
                  </Link>
                ) : (
                  <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                    <User className="w-4 h-4" />
                    {awayTeam?.team_name || game.away_team_name || 'Away'} Forwards
                  </h2>
                )}
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border bg-accent/50">
                    <th className="px-3 py-2 text-left font-display text-xs text-muted-foreground">Player</th>
                    <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">#</th>
                    <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">Rating</th>
                    <th className="px-2 py-2 text-center font-display text-xs text-goal">G</th>
                    <th className="px-2 py-2 text-center font-display text-xs text-assist">A</th>
                    <th className="px-2 py-2 text-center font-display text-xs text-primary">P</th>
                    {hasTracking && (
                      <>
                        <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">S</th>
                        <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">+/-</th>
                      </>
                    )}
                    <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">PIM</th>
                    {hasTracking && (
                      <>
                        {hasShifts && (
                          <>
                            <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">TOI</th>
                            <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">Shifts</th>
                          </>
                        )}
                        <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">CF%</th>
                        {hasEvents && (
                          <>
                            <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">P</th>
                            <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">GvA</th>
                            <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">TkA</th>
                          </>
                        )}
                      </>
                    )}
                  </tr>
                </thead>
                <tbody>
                  {(awayForwards.length > 0 ? paddedAwayForwards : awayPlayers).map((player: any, index: number) => {
                    // Skip rendering empty padding rows
                    if (player === null) {
                      return (
                        <tr key={`away-forward-pad-${index}`} className="border-b border-border">
                          <td colSpan={hasTracking ? (hasShifts ? (hasEvents ? 15 : 12) : 10) : 6} className="px-2 py-2"></td>
                        </tr>
                      )
                    }
                    const playerInfo = playersMap.get(String(player.player_id))
                    const advStats = awayPlayerStatsMap.get(String(player.player_id))
                    const goals = Number(player.goals ?? 0)
                    const assists = Number(player.assist ?? 0)
                    const points = goals + assists
                    
                    const playerLink = getPlayerGameLink(player.player_id) || `/norad/players/${player.player_id}`
                    
                    return (
                      <tr key={player.player_game_id || player.player_id} className="border-b border-border hover:bg-muted/50">
                        <td className="px-3 py-2">
                          <Link 
                            href={playerLink} 
                            className="flex items-center gap-2 text-foreground hover:text-primary transition-colors"
                          >
                            <PlayerPhoto
                              src={playerInfo?.player_image || null}
                              name={player.player_full_name || player.player_name || ''}
                              primaryColor={awayTeam?.primary_color || awayTeam?.team_color1}
                              size="sm"
                            />
                            <div className="flex items-center gap-1.5">
                              <span>{player.player_full_name || player.player_name}</span>
                              {(() => {
                                const subValue = player.sub ?? player.is_sub
                                const isSub = subValue === true || subValue === 1 || 
                                             String(subValue).toLowerCase() === 'true' || 
                                             String(subValue) === '1' ||
                                             String(subValue).toLowerCase() === 'yes'
                                return isSub ? (
                                  <span className="text-xs font-mono bg-muted px-1.5 py-0.5 rounded uppercase text-muted-foreground">
                                    SUB
                                  </span>
                                ) : null
                              })()}
                            </div>
                          </Link>
                        </td>
                        <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                          {player.player_game_number ?? playerInfo?.jersey_number ?? '-'}
                        </td>
                        <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                          {playerInfo?.current_skill_rating ? Math.round(Number(playerInfo.current_skill_rating)) : '-'}
                        </td>
                        <td className="px-2 py-2 text-center font-mono text-goal">{goals}</td>
                        <td className="px-2 py-2 text-center font-mono text-assist">{assists}</td>
                        <td className="px-2 py-2 text-center font-mono font-semibold">{points}</td>
                        {hasTracking && (
                          <>
                            <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                              {advStats?.shots ?? advStats?.sog ?? (advStats ? '-' : null)}
                            </td>
                            <td className={cn(
                              'px-2 py-2 text-center font-mono',
                              (advStats?.plus_minus_total ?? advStats?.plus_minus ?? 0) > 0 && 'text-save',
                              (advStats?.plus_minus_total ?? advStats?.plus_minus ?? 0) < 0 && 'text-goal'
                            )}>
                              {(advStats?.plus_minus_total ?? advStats?.plus_minus ?? 0) > 0 ? '+' : ''}
                              {(advStats?.plus_minus_total ?? advStats?.plus_minus ?? 0) || 0}
                            </td>
                          </>
                        )}
                        <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                          {player.pim ?? player.pim_total ?? 0}
                        </td>
                        {hasTracking && (
                          <>
                            {hasShifts && (
                              <>
                                <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                                  {advStats?.toi_seconds 
                                    ? (() => {
                                        const mins = Math.floor((advStats.toi_seconds || 0) / 60)
                                        const secs = (advStats.toi_seconds || 0) % 60
                                        return `${mins}:${secs.toString().padStart(2, '0')}`
                                      })()
                                    : '-'}
                                </td>
                                <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                                  {advStats?.shifts ?? '-'}
                                </td>
                              </>
                            )}
                            <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                              {advStats?.cf_pct 
                                ? (typeof advStats.cf_pct === 'number' 
                                    ? Number(advStats.cf_pct).toFixed(1) + '%' 
                                    : String(advStats.cf_pct))
                                : '-'}
                            </td>
                            {hasEvents && (
                              <>
                                <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                                  {advStats?.pass_attempts ?? advStats?.pass_att ?? advStats?.pass_completed ?? advStats?.pass_comp ?? '-'}
                                </td>
                                <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                                  {advStats?.giveaways ?? advStats?.give ?? '-'}
                                </td>
                                <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                                  {advStats?.takeaways ?? advStats?.take ?? '-'}
                                </td>
                              </>
                            )}
                          </>
                        )}
                      </tr>
                    )
                  })}
                  {awayPlayers.length === 0 && (
                    <tr>
                      <td colSpan={hasTracking ? (hasShifts ? (hasEvents ? 15 : 12) : 10) : 6} className="px-3 py-4 text-center text-sm text-muted-foreground">
                        No roster data available
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
        
        {/* Home Team - Forwards */}
        {(homeForwards.length > 0 || homePlayers.length > 0) && (
          <div className="bg-card rounded-xl border border-border overflow-hidden">
            <div className="px-4 py-3 bg-accent border-b border-border">
              <div className="flex items-center gap-2">
                {homeTeam && (
                  <Link 
                    href={`/norad/team/${(homeTeam.team_name || game.home_team_name || '').replace(/\s+/g, '_')}`}
                    className="hover:opacity-80 transition-opacity"
                  >
                    <TeamLogo
                      src={homeTeam.team_logo || null}
                      name={homeTeam.team_name || ''}
                      abbrev={homeTeam.team_cd}
                      primaryColor={homeTeam.primary_color || homeTeam.team_color1}
                      secondaryColor={homeTeam.team_color2}
                      size="sm"
                    />
                  </Link>
                )}
                {homeTeam?.team_name || game.home_team_name ? (
                  <Link 
                    href={`/norad/team/${(homeTeam?.team_name || game.home_team_name || '').replace(/\s+/g, '_')}`}
                    className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2 hover:text-primary transition-colors"
                  >
                    <User className="w-4 h-4" />
                    {homeTeam?.team_name || game.home_team_name || 'Home'} {homeForwards.length > 0 ? 'Forwards' : 'Skaters'}
                  </Link>
                ) : (
                  <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                    <User className="w-4 h-4" />
                    {homeTeam?.team_name || game.home_team_name || 'Home'} {homeForwards.length > 0 ? 'Forwards' : 'Skaters'}
                  </h2>
                )}
              </div>
            </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-accent/50">
                  <th className="px-3 py-2 text-left font-display text-xs text-muted-foreground">Player</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">#</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">Rating</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-goal">G</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-assist">A</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-primary">P</th>
                  {hasTracking && (
                    <>
                      <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">S</th>
                      <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">+/-</th>
                    </>
                  )}
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">PIM</th>
                  {hasTracking && (
                    <>
                      {hasShifts && (
                        <>
                          <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">TOI</th>
                          <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">Shifts</th>
                        </>
                      )}
                      <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">CF%</th>
                      {hasEvents && (
                        <>
                          <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">P</th>
                          <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">GvA</th>
                          <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">TkA</th>
                        </>
                      )}
                    </>
                  )}
                </tr>
              </thead>
              <tbody>
                {(homeForwards.length > 0 ? paddedHomeForwards : homePlayers).map((player: any, index: number) => {
                  // Skip rendering empty padding rows
                  if (player === null) {
                    return (
                      <tr key={`home-forward-pad-${index}`} className="border-b border-border">
                        <td colSpan={hasTracking ? (hasShifts ? (hasEvents ? 15 : 12) : 10) : 6} className="px-2 py-2"></td>
                      </tr>
                    )
                  }
                  const playerInfo = playersMap.get(String(player.player_id))
                  const advStats = homePlayerStatsMap.get(String(player.player_id))
                  const goals = Number(player.goals ?? 0)
                  const assists = Number(player.assist ?? 0)
                  const points = goals + assists
                  
                  const playerLink = getPlayerGameLink(player.player_id) || `/norad/players/${player.player_id}`
                  
                  return (
                    <tr key={player.player_game_id || player.player_id} className="border-b border-border hover:bg-muted/50">
                      <td className="px-3 py-2">
                        <Link 
                          href={playerLink} 
                          className="flex items-center gap-2 text-foreground hover:text-primary transition-colors"
                        >
                          <PlayerPhoto
                            src={playerInfo?.player_image || null}
                            name={player.player_full_name || player.player_name || ''}
                            primaryColor={homeTeam?.primary_color || homeTeam?.team_color1}
                            size="sm"
                          />
                          <div className="flex items-center gap-1.5">
                            <span>{player.player_full_name || player.player_name}</span>
                            {(() => {
                              const subValue = player.sub ?? player.is_sub
                              const isSub = subValue === true || subValue === 1 || 
                                           String(subValue).toLowerCase() === 'true' || 
                                           String(subValue) === '1' ||
                                           String(subValue).toLowerCase() === 'yes'
                              return isSub ? (
                                <span className="text-xs font-mono bg-muted px-1.5 py-0.5 rounded uppercase text-muted-foreground">
                                  SUB
                                </span>
                              ) : null
                            })()}
                          </div>
                        </Link>
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                        {player.player_game_number ?? playerInfo?.jersey_number ?? '-'}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                        {playerInfo?.current_skill_rating ? Math.round(Number(playerInfo.current_skill_rating)) : '-'}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-goal">{goals}</td>
                      <td className="px-2 py-2 text-center font-mono text-assist">{assists}</td>
                      <td className="px-2 py-2 text-center font-mono font-semibold">{points}</td>
                      {hasTracking && (
                        <>
                          <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                            {advStats?.shots ?? advStats?.sog ?? (advStats ? '-' : null)}
                          </td>
                          <td className={cn(
                            'px-2 py-2 text-center font-mono',
                            (advStats?.plus_minus_total ?? advStats?.plus_minus ?? 0) > 0 && 'text-save',
                            (advStats?.plus_minus_total ?? advStats?.plus_minus ?? 0) < 0 && 'text-goal'
                          )}>
                            {(advStats?.plus_minus_total ?? advStats?.plus_minus ?? 0) > 0 ? '+' : ''}
                            {(advStats?.plus_minus_total ?? advStats?.plus_minus ?? 0) || 0}
                          </td>
                        </>
                      )}
                      <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                        {player.pim ?? player.pim_total ?? 0}
                      </td>
                      {hasTracking && (
                        <>
                          {hasShifts && (
                            <>
                              <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                                {advStats?.toi_seconds 
                                  ? (() => {
                                      const mins = Math.floor((advStats.toi_seconds || 0) / 60)
                                      const secs = (advStats.toi_seconds || 0) % 60
                                      return `${mins}:${secs.toString().padStart(2, '0')}`
                                    })()
                                  : '-'}
                              </td>
                              <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                                {advStats?.shifts ?? '-'}
                              </td>
                            </>
                          )}
                          <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                            {advStats?.cf_pct 
                              ? (typeof advStats.cf_pct === 'number' 
                                  ? Number(advStats.cf_pct).toFixed(1) + '%' 
                                  : String(advStats.cf_pct))
                              : '-'}
                          </td>
                          {hasEvents && (
                            <>
                              <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                                {advStats?.pass_attempts ?? advStats?.pass_att ?? advStats?.pass_completed ?? advStats?.pass_comp ?? '-'}
                              </td>
                              <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                                {advStats?.giveaways ?? advStats?.give ?? '-'}
                              </td>
                              <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                                {advStats?.takeaways ?? advStats?.take ?? '-'}
                              </td>
                            </>
                          )}
                        </>
                      )}
                    </tr>
                  )
                  })}
                {homePlayers.length === 0 && (
                  <tr>
                    <td colSpan={hasTracking ? (hasShifts ? (hasEvents ? 15 : 12) : 10) : 6} className="px-3 py-4 text-center text-sm text-muted-foreground">
                      No roster data available
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
        )}
        
        {/* Away Team - Defense */}
        {awayDefense.length > 0 && (
          <div className="bg-card rounded-xl border border-border overflow-hidden">
            <div className="px-4 py-3 bg-accent border-b border-border">
              <div className="flex items-center gap-2">
                {awayTeam && (
                  <Link 
                    href={`/norad/team/${(awayTeam.team_name || game.away_team_name || '').replace(/\s+/g, '_')}`}
                    className="hover:opacity-80 transition-opacity"
                  >
                    <TeamLogo
                      src={awayTeam.team_logo || null}
                      name={awayTeam.team_name || ''}
                      abbrev={awayTeam.team_cd}
                      primaryColor={awayTeam.primary_color || awayTeam.team_color1}
                      secondaryColor={awayTeam.team_color2}
                      size="sm"
                    />
                  </Link>
                )}
                {awayTeam?.team_name || game.away_team_name ? (
                  <Link 
                    href={`/norad/team/${(awayTeam?.team_name || game.away_team_name || '').replace(/\s+/g, '_')}`}
                    className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2 hover:text-primary transition-colors"
                  >
                    <User className="w-4 h-4" />
                    {awayTeam?.team_name || game.away_team_name || 'Away'} Defense
                  </Link>
                ) : (
                  <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                    <User className="w-4 h-4" />
                    {awayTeam?.team_name || game.away_team_name || 'Away'} Defense
                  </h2>
                )}
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border bg-accent/50">
                    <th className="px-3 py-2 text-left font-display text-xs text-muted-foreground">Player</th>
                    <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">#</th>
                    <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">Rating</th>
                    <th className="px-2 py-2 text-center font-display text-xs text-goal">G</th>
                    <th className="px-2 py-2 text-center font-display text-xs text-assist">A</th>
                    <th className="px-2 py-2 text-center font-display text-xs text-primary">P</th>
                    {hasTracking && (
                      <>
                        <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">S</th>
                        <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">+/-</th>
                      </>
                    )}
                    <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">PIM</th>
                    {hasTracking && (
                      <>
                        {hasShifts && (
                          <>
                            <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">TOI</th>
                            <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">Shifts</th>
                          </>
                        )}
                        <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">CF%</th>
                        {hasEvents && (
                          <>
                            <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">P</th>
                            <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">GvA</th>
                            <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">TkA</th>
                          </>
                        )}
                      </>
                    )}
                  </tr>
                </thead>
                <tbody>
                  {paddedAwayDefense.map((player: any, index: number) => {
                    // Skip rendering empty padding rows
                    if (player === null) {
                      return (
                        <tr key={`away-defense-pad-${index}`} className="border-b border-border">
                          <td colSpan={hasTracking ? (hasShifts ? (hasEvents ? 15 : 12) : 10) : 6} className="px-2 py-2"></td>
                        </tr>
                      )
                    }
                    const playerInfo = playersMap.get(String(player.player_id))
                    const advStats = awayPlayerStatsMap.get(String(player.player_id))
                  const goals = Number(player.goals ?? 0)
                  const assists = Number(player.assist ?? 0)
                  const points = goals + assists
                  
                  const playerLink = getPlayerGameLink(player.player_id) || `/norad/players/${player.player_id}`
                  
                  return (
                    <tr key={player.player_game_id || player.player_id} className="border-b border-border hover:bg-muted/50">
                      <td className="px-3 py-2">
                        <Link 
                          href={playerLink} 
                          className="flex items-center gap-2 text-foreground hover:text-primary transition-colors"
                        >
                          <PlayerPhoto
                            src={playerInfo?.player_image || null}
                            name={player.player_full_name || player.player_name || ''}
                            primaryColor={awayTeam?.primary_color || awayTeam?.team_color1}
                            size="sm"
                          />
                          <div className="flex items-center gap-1.5">
                            <span>{player.player_full_name || player.player_name}</span>
                            {(() => {
                              const subValue = player.sub ?? player.is_sub
                              const isSub = subValue === true || subValue === 1 ||
                                           String(subValue).toLowerCase() === 'true' ||
                                           String(subValue) === '1' ||
                                           String(subValue).toLowerCase() === 'yes'
                              return isSub ? (
                                <span className="text-xs font-mono bg-muted px-1.5 py-0.5 rounded uppercase text-muted-foreground">
                                  SUB
                                </span>
                              ) : null
                            })()}
                          </div>
                        </Link>
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                        {player.player_game_number ?? playerInfo?.jersey_number ?? '-'}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                        {playerInfo?.current_skill_rating ? Math.round(Number(playerInfo.current_skill_rating)) : '-'}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-goal">{goals}</td>
                      <td className="px-2 py-2 text-center font-mono text-assist">{assists}</td>
                      <td className="px-2 py-2 text-center font-mono font-semibold">{points}</td>
                      {hasTracking && (
                        <>
                          <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                            {advStats?.shots ?? advStats?.sog ?? (advStats ? '-' : null)}
                          </td>
                          <td className={cn(
                            'px-2 py-2 text-center font-mono',
                            (advStats?.plus_minus_total ?? advStats?.plus_minus ?? 0) > 0 && 'text-save',
                            (advStats?.plus_minus_total ?? advStats?.plus_minus ?? 0) < 0 && 'text-goal'
                          )}>
                            {(advStats?.plus_minus_total ?? advStats?.plus_minus ?? 0) > 0 ? '+' : ''}
                            {(advStats?.plus_minus_total ?? advStats?.plus_minus ?? 0) || 0}
                          </td>
                        </>
                      )}
                      <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                        {player.pim ?? player.pim_total ?? 0}
                      </td>
                      {hasTracking && (
                        <>
                          {hasShifts && (
                            <>
                              <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                                {advStats?.toi_seconds 
                                  ? (() => {
                                      const mins = Math.floor((advStats.toi_seconds || 0) / 60)
                                      const secs = (advStats.toi_seconds || 0) % 60
                                      return `${mins}:${secs.toString().padStart(2, '0')}`
                                    })()
                                  : '-'}
                              </td>
                              <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                                {advStats?.shifts ?? '-'}
                              </td>
                            </>
                          )}
                          <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                            {advStats?.cf_pct 
                              ? (typeof advStats.cf_pct === 'number' 
                                  ? Number(advStats.cf_pct).toFixed(1) + '%' 
                                  : String(advStats.cf_pct))
                              : '-'}
                          </td>
                          {hasEvents && (
                            <>
                              <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                                {advStats?.pass_attempts ?? advStats?.pass_att ?? advStats?.pass_completed ?? advStats?.pass_comp ?? '-'}
                              </td>
                              <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                                {advStats?.giveaways ?? advStats?.give ?? '-'}
                              </td>
                              <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                                {advStats?.takeaways ?? advStats?.take ?? '-'}
                              </td>
                            </>
                          )}
                        </>
                      )}
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
        )}
        
        {/* Home Team - Defense */}
        {homeDefense.length > 0 && (
          <div className="bg-card rounded-xl border border-border overflow-hidden">
            <div className="px-4 py-3 bg-accent border-b border-border">
              <div className="flex items-center gap-2">
                {homeTeam && (
                  <Link 
                    href={`/norad/team/${(homeTeam.team_name || game.home_team_name || '').replace(/\s+/g, '_')}`}
                    className="hover:opacity-80 transition-opacity"
                  >
                    <TeamLogo
                      src={homeTeam.team_logo || null}
                      name={homeTeam.team_name || ''}
                      abbrev={homeTeam.team_cd}
                      primaryColor={homeTeam.primary_color || homeTeam.team_color1}
                      secondaryColor={homeTeam.team_color2}
                      size="sm"
                    />
                  </Link>
                )}
                {homeTeam?.team_name || game.home_team_name ? (
                  <Link 
                    href={`/norad/team/${(homeTeam?.team_name || game.home_team_name || '').replace(/\s+/g, '_')}`}
                    className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2 hover:text-primary transition-colors"
                  >
                    <User className="w-4 h-4" />
                    {homeTeam?.team_name || game.home_team_name || 'Home'} Defense
                  </Link>
                ) : (
                  <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                    <User className="w-4 h-4" />
                    {homeTeam?.team_name || game.home_team_name || 'Home'} Defense
                  </h2>
                )}
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border bg-accent/50">
                    <th className="px-3 py-2 text-left font-display text-xs text-muted-foreground">Player</th>
                    <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">#</th>
                    <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">Rating</th>
                    <th className="px-2 py-2 text-center font-display text-xs text-goal">G</th>
                    <th className="px-2 py-2 text-center font-display text-xs text-assist">A</th>
                    <th className="px-2 py-2 text-center font-display text-xs text-primary">P</th>
                    {hasTracking && (
                      <>
                        <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">S</th>
                        <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">+/-</th>
                      </>
                    )}
                    <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">PIM</th>
                    {hasTracking && (
                      <>
                        {hasShifts && (
                          <>
                            <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">TOI</th>
                            <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">Shifts</th>
                          </>
                        )}
                        <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">CF%</th>
                        {hasEvents && (
                          <>
                            <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">P</th>
                            <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">GvA</th>
                            <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">TkA</th>
                          </>
                        )}
                      </>
                    )}
                  </tr>
                </thead>
                <tbody>
                  {paddedHomeDefense.map((player: any, index: number) => {
                    // Skip rendering empty padding rows
                    if (player === null) {
                      return (
                        <tr key={`home-defense-pad-${index}`} className="border-b border-border">
                          <td colSpan={hasTracking ? (hasShifts ? (hasEvents ? 15 : 12) : 10) : 6} className="px-2 py-2"></td>
                        </tr>
                      )
                    }
                    const playerInfo = playersMap.get(String(player.player_id))
                    const advStats = homePlayerStatsMap.get(String(player.player_id))
                    const goals = Number(player.goals ?? 0)
                    const assists = Number(player.assist ?? 0)
                    const points = goals + assists
                    
                    const playerLink = getPlayerGameLink(player.player_id) || `/norad/players/${player.player_id}`
                    
                    return (
                      <tr key={player.player_game_id || player.player_id} className="border-b border-border hover:bg-muted/50">
                        <td className="px-3 py-2">
                          <Link 
                            href={playerLink} 
                            className="flex items-center gap-2 text-foreground hover:text-primary transition-colors"
                          >
                            <PlayerPhoto
                              src={playerInfo?.player_image || null}
                              name={player.player_full_name || player.player_name || ''}
                              primaryColor={homeTeam?.primary_color || homeTeam?.team_color1}
                              size="sm"
                            />
                            <div className="flex items-center gap-1.5">
                              <span>{player.player_full_name || player.player_name}</span>
                              {(() => {
                                const subValue = player.sub ?? player.is_sub
                                const isSub = subValue === true || subValue === 1 || 
                                             String(subValue).toLowerCase() === 'true' || 
                                             String(subValue) === '1' ||
                                             String(subValue).toLowerCase() === 'yes'
                                return isSub ? (
                                  <span className="text-xs font-mono bg-muted px-1.5 py-0.5 rounded uppercase text-muted-foreground">
                                    SUB
                                  </span>
                                ) : null
                              })()}
                            </div>
                          </Link>
                        </td>
                        <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                          {player.player_game_number ?? playerInfo?.jersey_number ?? '-'}
                        </td>
                        <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                          {playerInfo?.current_skill_rating ? Math.round(Number(playerInfo.current_skill_rating)) : '-'}
                        </td>
                        <td className="px-2 py-2 text-center font-mono text-goal">{goals}</td>
                        <td className="px-2 py-2 text-center font-mono text-assist">{assists}</td>
                        <td className="px-2 py-2 text-center font-mono font-semibold">{points}</td>
                        {hasTracking && (
                          <>
                            <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                              {advStats?.shots ?? advStats?.sog ?? (advStats ? '-' : null)}
                            </td>
                            <td className={cn(
                              'px-2 py-2 text-center font-mono',
                              (advStats?.plus_minus_total ?? advStats?.plus_minus ?? 0) > 0 && 'text-save',
                              (advStats?.plus_minus_total ?? advStats?.plus_minus ?? 0) < 0 && 'text-goal'
                            )}>
                              {(advStats?.plus_minus_total ?? advStats?.plus_minus ?? 0) > 0 ? '+' : ''}
                              {(advStats?.plus_minus_total ?? advStats?.plus_minus ?? 0) || 0}
                            </td>
                          </>
                        )}
                        <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                          {player.pim ?? player.pim_total ?? 0}
                        </td>
                        {hasTracking && (
                          <>
                            {hasShifts && (
                              <>
                                <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                                  {advStats?.toi_seconds 
                                    ? (() => {
                                        const mins = Math.floor((advStats.toi_seconds || 0) / 60)
                                        const secs = (advStats.toi_seconds || 0) % 60
                                        return `${mins}:${secs.toString().padStart(2, '0')}`
                                      })()
                                    : '-'}
                                </td>
                                <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                                  {advStats?.shifts ?? '-'}
                                </td>
                              </>
                            )}
                            <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                              {advStats?.cf_pct 
                                ? (typeof advStats.cf_pct === 'number' 
                                    ? Number(advStats.cf_pct).toFixed(1) + '%' 
                                    : String(advStats.cf_pct))
                                : '-'}
                            </td>
                            {hasEvents && (
                              <>
                                <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                                  {advStats?.pass_attempts ?? advStats?.pass_att ?? advStats?.pass_completed ?? advStats?.pass_comp ?? '-'}
                                </td>
                                <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                                  {advStats?.giveaways ?? advStats?.give ?? '-'}
                                </td>
                                <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                                  {advStats?.takeaways ?? advStats?.take ?? '-'}
                                </td>
                              </>
                            )}
                          </>
                        )}
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Goalies - Separated Section */}
      {(homeGoalies.length > 0 || awayGoalies.length > 0 || goalieStatsData.length > 0) && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Target className="w-4 h-4 text-save" />
              Goaltending
            </h2>
          </div>
          {(() => {
            // Deduplicate goalies - combine roster goalies and goalieStats, removing duplicates by player_id
            const goalieMap = new Map<string, any>()
            
            // Add roster goalies first
            const allRosterGoalies = awayGoalies.concat(homeGoalies);
            allRosterGoalies.forEach((goalie: any) => {
              const playerId = String(goalie.player_id || '')
              if (playerId && !goalieMap.has(playerId)) {
                goalieMap.set(playerId, goalie)
              }
            })
            
            // Add goalieStats, preferring stats data if duplicate
            goalieStatsData.forEach((goalie: FactGoalieGameStats | Record<string, any>) => {
              const playerId = String(goalie.player_id || '')
              if (playerId) {
                goalieMap.set(playerId, goalie) // This will overwrite roster entry if exists
              }
            })
            
            // Prepare goalies data for sortable table
            const goaliesForTable = Array.from(goalieMap.values()).map((goalie: any) => {
              const goalieTeamId = String(goalie.team_id || '')
              const goalieTeam = goalieTeamId === String(homeTeamId) ? homeTeam : 
                                 goalieTeamId === String(awayTeamId) ? awayTeam : null
              
              const saves = Number(goalie.saves ?? goalie.sv ?? 0)
              const goalsAgainst = Number(goalie.goals_against ?? goalie.ga ?? 0)
              const shotsAgainst = Number(goalie.shots_against ?? goalie.sa ?? saves + goalsAgainst)
              const savePct = shotsAgainst > 0 ? (saves / shotsAgainst) : 0
              const toiMinutes = goalie.toi_seconds ? Number(goalie.toi_seconds) / 60 : 60 // Default to 60 if unknown
              const gaa = toiMinutes > 0 ? (goalsAgainst / toiMinutes) * 60 : 0
              
              return {
                player_id: String(goalie.player_id),
                player_name: goalie.player_name || goalie.player_full_name || '',
                player_full_name: goalie.player_full_name || goalie.player_name || '',
                team_id: goalieTeamId,
                team_name: goalieTeam?.team_name || goalie.team_name || '',
                saves: saves || undefined,
                shots: shotsAgainst || undefined,
                save_pct: savePct > 0 ? savePct : undefined,
                goals_against: goalsAgainst,
                gaa: gaa > 0 ? gaa : undefined,
              }
            })
            
            // Create teams map for the component
            const teamsMapForGoalies = new Map<string, any>()
            if (homeTeam) teamsMapForGoalies.set(String(homeTeamId), homeTeam)
            if (awayTeam) teamsMapForGoalies.set(String(awayTeamId), awayTeam)
            
            return (
              <SortableGoaliesTable
                goalies={goaliesForTable}
                playersMap={playersMap}
                teamsMap={teamsMapForGoalies}
                hasTracking={hasTracking}
              />
            )
          })()}
        </div>
      )}
      
      {/* Advanced Analytics Tabs - Only show when we have tracked data */}
      {(hasEvents || hasShifts || hasXY) && (
        <GameDetailTabs
          hasPlayByPlay={hasEvents}
          hasShots={hasXY && shotsData && shotsData.length > 0}
          hasShifts={hasShifts && shiftsData && shiftsData.length > 0}
          playByPlayContent={
            hasEvents && (
              <PlayByPlayTimeline
                events={allEvents}
                homeTeam={homeTeam?.team_name || game.home_team_name || 'Home'}
                awayTeam={awayTeam?.team_name || game.away_team_name || 'Away'}
                homeTeamId={String(homeTeamId || '')}
                awayTeamId={String(awayTeamId || '')}
                playersMap={playersMap}
                homeTeamData={homeTeam ? {
                  team_name: homeTeam.team_name || game.home_team_name || 'Home',
                  team_logo: homeTeam.team_logo,
                  team_cd: homeTeam.team_cd,
                  primary_color: homeTeam.primary_color || homeTeam.team_color1,
                  team_color1: homeTeam.team_color1
                } : undefined}
                awayTeamData={awayTeam ? {
                  team_name: awayTeam.team_name || game.away_team_name || 'Away',
                  team_logo: awayTeam.team_logo,
                  team_cd: awayTeam.team_cd,
                  primary_color: awayTeam.primary_color || awayTeam.team_color1,
                  team_color1: awayTeam.team_color1
                } : undefined}
                videoUrl={gameVideos.length > 0 ? gameVideos[0].video_url : null}
                videoStartOffset={gameVideos.length > 0 ? (gameVideos[0].period_1_start || 0) : 0}
                videos={gameVideos}
                shifts={shiftsData}
                jerseyToPlayerMap={jerseyToPlayerMap}
              />
            )
          }
          shiftsContent={
            hasShifts && shiftsData && shiftsData.length > 0 && (
              <ShiftsTimeline
                shifts={shiftsData}
                homeTeam={homeTeam?.team_name || game.home_team_name || 'Home'}
                awayTeam={awayTeam?.team_name || game.away_team_name || 'Away'}
                homeTeamId={String(homeTeamId || '')}
                awayTeamId={String(awayTeamId || '')}
                homeColor={homeTeam?.primary_color || homeTeam?.team_color1 || '#3b82f6'}
                awayColor={awayTeam?.primary_color || awayTeam?.team_color1 || '#ef4444'}
                jerseyToPlayerMap={jerseyToPlayerMap}
                videos={gameVideos}
                events={allEvents?.map(e => ({
                  event_id: e.event_id,
                  event_type: e.event_type,
                  event_detail: e.event_detail,
                  player_team: e.player_team,
                  shift_id: (e as any).shift_id || (e as any).shift_index,
                  running_video_time: e.running_video_time
                })) || []}
              />
            )
          }
          shotsContent={
            hasXY && shotsData && shotsData.length > 0 && (
              <EnhancedShotMap
                shots={shotsData.map(shot => ({
                  x_coord: shot.x_coord ?? shot.shot_x,
                  y_coord: shot.y_coord ?? shot.shot_y,
                  shot_x: shot.shot_x ?? shot.x_coord,
                  shot_y: shot.shot_y ?? shot.y_coord,
                  is_goal: shot.is_goal,
                  shot_result: shot.shot_result,
                  xg: shot.xg ?? shot.shot_xg,
                  danger_zone: shot.danger_zone,
                  danger_level: shot.danger_level,
                  period: shot.period,
                  strength: shot.strength,
                  player_id: shot.player_id,
                  player_name: shot.player_name,
                  event_type: shot.event_type,
                }))}
                width={600}
                height={300}
                showFilters={true}
                title="Shot Map"
              />
            )
          }
          hasAnalytics={!!(homeTeamGameStats || awayTeamGameStats)}
          analyticsContent={
            (homeTeamGameStats || awayTeamGameStats) && (
              <GameAnalyticsPanel
                homeStats={homeTeamGameStats ? {
                  team_name: homeTeam?.team_name || game.home_team_name || 'Home',
                  shots: homeTeamGameStats.shots,
                  goals: homeTeamGameStats.goals,
                  corsi_for: homeTeamGameStats.cf || homeTeamGameStats.corsi_for,
                  corsi_against: homeTeamGameStats.ca || homeTeamGameStats.corsi_against,
                  fenwick_for: homeTeamGameStats.ff || homeTeamGameStats.fenwick_for,
                  fenwick_against: homeTeamGameStats.fa || homeTeamGameStats.fenwick_against,
                  xg_for: homeTeamGameStats.xg_for || homeTeamGameStats.xgf,
                  xg_against: homeTeamGameStats.xg_against || homeTeamGameStats.xga,
                  high_danger_chances: homeTeamGameStats.high_danger_chances || homeTeamGameStats.hd_chances,
                  scoring_chances: homeTeamGameStats.scoring_chances || homeTeamGameStats.sc,
                  save_percentage: homeTeamGameStats.save_pct || homeTeamGameStats.sv_pct,
                } : null}
                awayStats={awayTeamGameStats ? {
                  team_name: awayTeam?.team_name || game.away_team_name || 'Away',
                  shots: awayTeamGameStats.shots,
                  goals: awayTeamGameStats.goals,
                  corsi_for: awayTeamGameStats.cf || awayTeamGameStats.corsi_for,
                  corsi_against: awayTeamGameStats.ca || awayTeamGameStats.corsi_against,
                  fenwick_for: awayTeamGameStats.ff || awayTeamGameStats.fenwick_for,
                  fenwick_against: awayTeamGameStats.fa || awayTeamGameStats.fenwick_against,
                  xg_for: awayTeamGameStats.xg_for || awayTeamGameStats.xgf,
                  xg_against: awayTeamGameStats.xg_against || awayTeamGameStats.xga,
                  high_danger_chances: awayTeamGameStats.high_danger_chances || awayTeamGameStats.hd_chances,
                  scoring_chances: awayTeamGameStats.scoring_chances || awayTeamGameStats.sc,
                  save_percentage: awayTeamGameStats.save_pct || awayTeamGameStats.sv_pct,
                } : null}
                homeTeamName={homeTeam?.team_name || game.home_team_name || 'Home'}
                awayTeamName={awayTeam?.team_name || game.away_team_name || 'Away'}
                homeColor={homeTeam?.primary_color || homeTeam?.team_color1 || '#3b82f6'}
                awayColor={awayTeam?.primary_color || awayTeam?.team_color1 || '#ef4444'}
              />
            )
          }
        />
      )}

      {/* Prior Games - Season Results (As of Game Date) */}
      {(priorGamesData.homeGames.length > 0 || priorGamesData.awayGames.length > 0) && (
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Away Team Prior Games (Left side to match scoreboard) */}
          {priorGamesData.awayGames.length > 0 && (
            <div className="bg-card rounded-xl border border-border overflow-hidden">
              <div className="px-4 py-3 bg-accent border-b border-border">
                <div className="flex items-center gap-2">
                  {awayTeam && (
                    <Link
                      href={`/norad/team/${(awayTeam.team_name || game.away_team_name || '').replace(/\s+/g, '_')}`}
                      className="hover:opacity-80 transition-opacity"
                    >
                      <TeamLogo
                        src={awayTeam.team_logo || null}
                        name={awayTeam.team_name || ''}
                        abbrev={awayTeam.team_cd}
                        primaryColor={awayTeam.primary_color || awayTeam.team_color1}
                        secondaryColor={awayTeam.team_color2}
                        size="sm"
                      />
                    </Link>
                  )}
                  <h2 className="font-display text-sm font-semibold uppercase tracking-wider">
                    {awayTeam?.team_name || game.away_team_name || 'Away'} Prior Games
                  </h2>
                </div>
              </div>
              <div className="divide-y divide-border">
                {priorGamesData.awayGames.map((priorGame: any) => {
                  const isHome = String(priorGame.home_team_id) === String(game.away_team_id)
                  const teamGoals = isHome ? (priorGame.home_total_goals ?? 0) : (priorGame.away_total_goals ?? 0)
                  const oppGoals = isHome ? (priorGame.away_total_goals ?? 0) : (priorGame.home_total_goals ?? 0)
                  const opponent = isHome ? priorGame.away_team_name : priorGame.home_team_name
                  const result = teamGoals > oppGoals ? 'W' : teamGoals < oppGoals ? 'L' : 'T'
                  const resultColor = result === 'W' ? 'text-save' : result === 'L' ? 'text-goal' : 'text-muted-foreground'

                  return (
                    <Link
                      key={priorGame.game_id}
                      href={`/norad/games/${priorGame.game_id}`}
                      className="flex items-center justify-between p-3 hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex items-center gap-3 flex-1">
                        <span className={`font-mono font-bold text-sm ${resultColor}`}>{result}</span>
                        <div className="flex-1">
                          <div className="text-sm font-medium">
                            vs {opponent}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {priorGame.date ? new Date(priorGame.date).toLocaleDateString('en-US', {
                              month: 'short',
                              day: 'numeric',
                              year: 'numeric'
                            }) : ''}
                          </div>
                        </div>
                      </div>
                      <div className="font-mono text-sm font-semibold">
                        <span className={isHome ? 'text-primary' : 'text-muted-foreground'}>
                          {teamGoals}
                        </span>
                        <span className="text-muted-foreground mx-1">-</span>
                        <span className={!isHome ? 'text-primary' : 'text-muted-foreground'}>
                          {oppGoals}
                        </span>
                      </div>
                    </Link>
                  )
                })}
              </div>
            </div>
          )}

          {/* Home Team Prior Games (Right side to match scoreboard) */}
          {priorGamesData.homeGames.length > 0 && (
            <div className="bg-card rounded-xl border border-border overflow-hidden">
              <div className="px-4 py-3 bg-accent border-b border-border">
                <div className="flex items-center gap-2">
                  {homeTeam && (
                    <Link
                      href={`/norad/team/${(homeTeam.team_name || game.home_team_name || '').replace(/\s+/g, '_')}`}
                      className="hover:opacity-80 transition-opacity"
                    >
                      <TeamLogo
                        src={homeTeam.team_logo || null}
                        name={homeTeam.team_name || ''}
                        abbrev={homeTeam.team_cd}
                        primaryColor={homeTeam.primary_color || homeTeam.team_color1}
                        secondaryColor={homeTeam.team_color2}
                        size="sm"
                      />
                    </Link>
                  )}
                  <h2 className="font-display text-sm font-semibold uppercase tracking-wider">
                    {homeTeam?.team_name || game.home_team_name || 'Home'} Prior Games
                  </h2>
                </div>
              </div>
              <div className="divide-y divide-border">
                {priorGamesData.homeGames.map((priorGame: any) => {
                  const isHome = String(priorGame.home_team_id) === String(game.home_team_id)
                  const teamGoals = isHome ? (priorGame.home_total_goals ?? 0) : (priorGame.away_total_goals ?? 0)
                  const oppGoals = isHome ? (priorGame.away_total_goals ?? 0) : (priorGame.home_total_goals ?? 0)
                  const opponent = isHome ? priorGame.away_team_name : priorGame.home_team_name
                  const result = teamGoals > oppGoals ? 'W' : teamGoals < oppGoals ? 'L' : 'T'
                  const resultColor = result === 'W' ? 'text-save' : result === 'L' ? 'text-goal' : 'text-muted-foreground'

                  return (
                    <Link
                      key={priorGame.game_id}
                      href={`/norad/games/${priorGame.game_id}`}
                      className="flex items-center justify-between p-3 hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex items-center gap-3 flex-1">
                        <span className={`font-mono font-bold text-sm ${resultColor}`}>{result}</span>
                        <div className="flex-1">
                          <div className="text-sm font-medium">
                            vs {opponent}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {priorGame.date ? new Date(priorGame.date).toLocaleDateString('en-US', {
                              month: 'short',
                              day: 'numeric',
                              year: 'numeric'
                            }) : ''}
                          </div>
                        </div>
                      </div>
                      <div className="font-mono text-sm font-semibold">
                        <span className={isHome ? 'text-primary' : 'text-muted-foreground'}>
                          {teamGoals}
                        </span>
                        <span className="text-muted-foreground mx-1">-</span>
                        <span className={!isHome ? 'text-primary' : 'text-muted-foreground'}>
                          {oppGoals}
                        </span>
                      </div>
                    </Link>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tracking Status - Compact Footer (Very Bottom) */}
      {gameTrackingStatus && (
        <details className="group">
          <summary className="cursor-pointer list-none bg-muted/30 rounded-lg px-4 py-2 flex items-center justify-between hover:bg-muted/50 transition-colors">
            <div className="flex items-center gap-3">
              <span className="text-xs font-mono text-muted-foreground uppercase">Tracking:</span>
              <span className={cn(
                'px-2 py-0.5 rounded text-xs font-mono font-medium',
                gameTrackingStatus.status === 'full' && 'bg-save/20 text-save',
                gameTrackingStatus.status === 'partial' && 'bg-assist/20 text-assist',
                gameTrackingStatus.status === 'non-full' && 'bg-primary/20 text-primary',
                gameTrackingStatus.status === 'none' && 'bg-muted text-muted-foreground'
              )}>
                {gameTrackingStatus.status === 'full' && 'Full'}
                {gameTrackingStatus.status === 'partial' && 'Partial'}
                {gameTrackingStatus.status === 'non-full' && 'Non-Full'}
                {gameTrackingStatus.status === 'none' && 'None'}
              </span>
              <span className="text-xs font-mono text-muted-foreground hidden md:inline">
                {[
                  gameTrackingStatus.hasEvents && `${gameTrackingStatus.eventCount} events`,
                  gameTrackingStatus.hasShifts && `${gameTrackingStatus.shiftCount} shifts`,
                  gameTrackingStatus.hasXY && `${gameTrackingStatus.xyCount} XY`,
                  gameTrackingStatus.hasVideo && 'Video'
                ].filter(Boolean).join(' | ')}
              </span>
            </div>
            <span className="text-xs text-muted-foreground group-open:rotate-180 transition-transform">
              &#9660;
            </span>
          </summary>
          <div className="mt-2 p-4 bg-muted/20 rounded-lg">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Events</div>
                <div className={cn(
                  'font-mono font-semibold',
                  gameTrackingStatus.hasEvents ? 'text-foreground' : 'text-muted-foreground'
                )}>
                  {gameTrackingStatus.hasEvents ? gameTrackingStatus.eventCount.toLocaleString() : 'None'}
                </div>
              </div>
              <div>
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Shifts</div>
                <div className={cn(
                  'font-mono font-semibold',
                  gameTrackingStatus.hasShifts ? 'text-foreground' : 'text-muted-foreground'
                )}>
                  {gameTrackingStatus.hasShifts ? gameTrackingStatus.shiftCount.toLocaleString() : 'None'}
                </div>
              </div>
              <div>
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">XY Data</div>
                <div className={cn(
                  'font-mono font-semibold',
                  gameTrackingStatus.hasXY ? 'text-foreground' : 'text-muted-foreground'
                )}>
                  {gameTrackingStatus.hasXY ? gameTrackingStatus.xyCount.toLocaleString() : 'None'}
                </div>
              </div>
              <div>
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Video</div>
                <div className={cn(
                  'font-mono font-semibold',
                  gameTrackingStatus.hasVideo ? 'text-foreground' : 'text-muted-foreground'
                )}>
                  {gameTrackingStatus.hasVideo ? 'Available' : 'None'}
                </div>
              </div>
            </div>
            {gameTrackingStatus.missing.length > 0 && (
              <div className="mt-3 pt-3 border-t border-border/50">
                <div className="text-xs font-mono text-muted-foreground">
                  Missing: {gameTrackingStatus.missing.join(', ')}
                </div>
              </div>
            )}
          </div>
        </details>
      )}
    </div>
  )
}
