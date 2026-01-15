// @ts-nocheck
// src/app/norad/(dashboard)/games/[gameId]/page.tsx
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getGameFromSchedule, getGameRoster, getGameGoals, getGameGoalieStats, getGameShots } from '@/lib/supabase/queries/games'
import { getGameTrackingStatus } from '@/lib/supabase/queries/game-tracking'
import { createClient } from '@/lib/supabase/server'
import { getTeamById } from '@/lib/supabase/queries/teams'
import { getPlayers } from '@/lib/supabase/queries/players'
import { ArrowLeft, Target, User, TrendingUp, Activity, BarChart3, Shield, Zap, ExternalLink, Trophy } from 'lucide-react'
import { cn } from '@/lib/utils'
import { TeamLogo } from '@/components/teams/team-logo'
import { PlayerPhoto } from '@/components/players/player-photo'
import { ShotHeatmap } from '@/components/charts/shot-heatmap'
import { EnhancedShotMap } from '@/components/charts/enhanced-shot-map'
import { StatCard, StatRow } from '@/components/players/stat-card'
import { GameHighlights } from '@/components/games/game-highlights'
import { GameSummary } from '@/components/games/game-summary'
import { PlayByPlayTimeline } from '@/components/games/PlayByPlayTimeline'
import { ShiftChart } from '@/components/games/shift-chart'
import { SortableGoaliesTable } from '@/components/games/sortable-goalies-table'
import type { FactPlayerGameStats, FactGoalieGameStats, DimTeam, DimPlayer } from '@/types/database'

export const revalidate = 300

// Type definitions for internal use
interface TeamAggregates {
  cf: number
  ca: number
  ff: number
  fa: number
  goals: number
  assists: number
  points: number
  shots: number
  hits: number
  blocks: number
  takeaways: number
  badGiveaways: number
  toi: number
}

interface GameEvent {
  event_id?: string
  period?: number
  time_start_total_seconds?: number
  time_seconds?: number
  time_remaining?: string
  period_time?: string
  is_goal?: boolean
  is_highlight?: boolean
  is_save?: boolean
  event_type?: string
  player_name?: string
  event_player_ids?: string
  event_player_1?: string
  event_player_2?: string
  sequence_key?: string
  play_key?: string
  linked_event_key?: string
  play_detail1?: string
  play_detail_2?: string
  team_id?: string
  event_time?: string
}

interface EnhancedHighlight extends GameEvent {
  period_time: string
  event_time: string
}

// Helper function to calculate team aggregates from player stats
function calculateTeamAggregates(playerStatsList: (FactPlayerGameStats | Record<string, any>)[]): TeamAggregates {
  return playerStatsList.reduce<TeamAggregates>((acc, stat) => {
    // Type assertion to access properties that may not be in FactPlayerGameStats
    const statAny = stat as Record<string, any>
    return {
      cf: (acc.cf || 0) + (Number(stat.corsi_for ?? statAny.cf ?? 0) || 0),
      ca: (acc.ca || 0) + (Number(stat.corsi_against ?? statAny.ca ?? 0) || 0),
      ff: (acc.ff || 0) + (Number(stat.fenwick_for ?? statAny.ff ?? 0) || 0),
      fa: (acc.fa || 0) + (Number(stat.fenwick_against ?? statAny.fa ?? 0) || 0),
      goals: (acc.goals || 0) + (Number(stat.goals ?? 0) || 0),
      assists: (acc.assists || 0) + (Number(stat.assists ?? 0) || 0),
      points: (acc.points || 0) + (Number(stat.points ?? 0) || 0),
      shots: (acc.shots || 0) + (Number(stat.shots ?? 0) || 0),
      hits: (acc.hits || 0) + (Number(stat.hits ?? 0) || 0),
      blocks: (acc.blocks || 0) + (Number(stat.blocks ?? 0) || 0),
      takeaways: (acc.takeaways || 0) + (Number(stat.takeaways ?? 0) || 0),
      badGiveaways: (acc.badGiveaways || 0) + (Number(stat.bad_giveaways ?? statAny.bad_give ?? 0) || 0),
      toi: (acc.toi || 0) + (Number(stat.toi_seconds ?? 0) || 0),
    };
  }, { cf: 0, ca: 0, ff: 0, fa: 0, goals: 0, assists: 0, points: 0, shots: 0, hits: 0, blocks: 0, takeaways: 0, badGiveaways: 0, toi: 0 });
}

// Helper function to calculate percentage
function calculatePercentage(forValue: number, againstValue: number): number {
  const total = forValue + againstValue;
  return total > 0 ? (forValue / total) * 100 : 0;
}

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
  const [roster, goals, players, goalieStats, shots, gameEventsResult, allEventsResult, shiftsResult, priorGamesResult] = await Promise.allSettled([
    getGameRoster(gameIdNum),
    getGameGoals(gameIdNum),
    getPlayers(),
    getGameGoalieStats(gameIdNum),
    getGameShots(gameIdNum),
    supabase
      .from('fact_events')
      .select('*')
      .eq('game_id', gameIdNum)
      .or('is_goal.eq.true,is_highlight.eq.true,is_save.eq.true')
      .order('time_start_total_seconds', { ascending: true })
      .limit(50),
    // Fetch all events for play-by-play timeline
    // Order by event_id to ensure we get events in sequential order (EV1896901000, EV1896901001, etc.)
    supabase
      .from('fact_events')
      .select('*')
      .eq('game_id', gameIdNum)
      .order('event_id', { ascending: true }),
    // Fetch shifts for shift chart
    supabase
      .from('fact_shifts')
      .select('*')
      .eq('game_id', gameIdNum)
      .order('shift_start_total_seconds', { ascending: true }),
    // Fetch prior games for both teams in the same season
    (async () => {
      if (!game.season_id) return { homeGames: [], awayGames: [], headToHeadGames: [] }
      
      // Get prior games for home team
      const { data: homeTeamGames } = await supabase
        .from('dim_schedule')
        .select('game_id, date, home_team_name, away_team_name, home_total_goals, away_total_goals, official_home_goals, official_away_goals, home_team_id, away_team_id')
        .eq('season_id', game.season_id)
        .or(`home_team_id.eq.${game.home_team_id},away_team_id.eq.${game.home_team_id}`)
        .neq('game_id', gameIdNum)
        .not('home_total_goals', 'is', null)
        .not('away_total_goals', 'is', null)
        .order('date', { ascending: false })
        .limit(10)
      
      // Get prior games for away team
      const { data: awayTeamGames } = await supabase
        .from('dim_schedule')
        .select('game_id, date, home_team_name, away_team_name, home_total_goals, away_total_goals, official_home_goals, official_away_goals, home_team_id, away_team_id')
        .eq('season_id', game.season_id)
        .or(`home_team_id.eq.${game.away_team_id},away_team_id.eq.${game.away_team_id}`)
        .neq('game_id', gameIdNum)
        .not('home_total_goals', 'is', null)
        .not('away_total_goals', 'is', null)
        .order('date', { ascending: false })
        .limit(10)
      
      // Get head-to-head games between these two teams in the same season
      // Fetch all games in the season, then filter in JavaScript for better reliability
      const { data: allSeasonGames } = await supabase
        .from('dim_schedule')
        .select('game_id, date, home_team_name, away_team_name, home_total_goals, away_total_goals, official_home_goals, official_away_goals, home_team_id, away_team_id, game_type')
        .eq('season_id', game.season_id)
        .order('date', { ascending: true })
        .order('game_id', { ascending: true })
      
      // Normalize team identifiers for matching
      const homeTeamIds = new Set<string>()
      const awayTeamIds = new Set<string>()
      const homeTeamNames = new Set<string>()
      const awayTeamNames = new Set<string>()
      
      // Add all possible identifiers for home team (normalized)
      if (game.home_team_id) {
        homeTeamIds.add(String(game.home_team_id).trim())
        homeTeamIds.add(String(game.home_team_id).trim().toLowerCase())
      }
      if (game.home_team_name) {
        const normalized = String(game.home_team_name).trim()
        homeTeamNames.add(normalized)
        homeTeamNames.add(normalized.toLowerCase())
      }
      
      // Add all possible identifiers for away team (normalized)
      if (game.away_team_id) {
        awayTeamIds.add(String(game.away_team_id).trim())
        awayTeamIds.add(String(game.away_team_id).trim().toLowerCase())
      }
      if (game.away_team_name) {
        const normalized = String(game.away_team_name).trim()
        awayTeamNames.add(normalized)
        awayTeamNames.add(normalized.toLowerCase())
      }
      
      // Filter games to find head-to-head matchups
      // A game is a head-to-head if:
      // 1. Home team matches one of our teams AND away team matches the other, OR
      // 2. Away team matches one of our teams AND home team matches the other
      const headToHeadGames = (allSeasonGames || [])
        .filter((g: any) => {
          // Always include the current game
          if (Number(g.game_id) === gameIdNum) return true
          
          const gHomeId = g.home_team_id ? String(g.home_team_id).trim() : null
          const gAwayId = g.away_team_id ? String(g.away_team_id).trim() : null
          const gHomeName = g.home_team_name ? String(g.home_team_name).trim() : null
          const gAwayName = g.away_team_name ? String(g.away_team_name).trim() : null
          
          // Check if this game involves both teams
          // Try matching by ID first (case-insensitive), then fallback to name (case-insensitive)
          const homeMatchesHome = (gHomeId && (homeTeamIds.has(gHomeId) || homeTeamIds.has(gHomeId.toLowerCase()))) || 
                                  (gHomeName && (homeTeamNames.has(gHomeName) || homeTeamNames.has(gHomeName.toLowerCase())))
          const homeMatchesAway = (gHomeId && (awayTeamIds.has(gHomeId) || awayTeamIds.has(gHomeId.toLowerCase()))) || 
                                  (gHomeName && (awayTeamNames.has(gHomeName) || awayTeamNames.has(gHomeName.toLowerCase())))
          const awayMatchesHome = (gAwayId && (homeTeamIds.has(gAwayId) || homeTeamIds.has(gAwayId.toLowerCase()))) || 
                                  (gAwayName && (homeTeamNames.has(gAwayName) || homeTeamNames.has(gAwayName.toLowerCase())))
          const awayMatchesAway = (gAwayId && (awayTeamIds.has(gAwayId) || awayTeamIds.has(gAwayId.toLowerCase()))) || 
                                  (gAwayName && (awayTeamNames.has(gAwayName) || awayTeamNames.has(gAwayName.toLowerCase())))
          
          // Match if: (home=our home AND away=our away) OR (home=our away AND away=our home)
          return (homeMatchesHome && awayMatchesAway) || (homeMatchesAway && awayMatchesHome)
        })
        .map((g: any) => ({
          game_id: Number(g.game_id),
          date: g.date,
          home_team_name: g.home_team_name,
          away_team_name: g.away_team_name,
          home_total_goals: g.home_total_goals,
          away_total_goals: g.away_total_goals,
          official_home_goals: g.official_home_goals,
          official_away_goals: g.official_away_goals,
          home_team_id: g.home_team_id,
          away_team_id: g.away_team_id,
          game_type: g.game_type || 'Regular',
        }))
        .sort((a, b) => {
          const dateA = a.date ? new Date(a.date).getTime() : 0
          const dateB = b.date ? new Date(b.date).getTime() : 0
          if (dateA === dateB) {
            return (a.game_id || 0) - (b.game_id || 0)
          }
          return dateA - dateB
        })
      
      // Always include current game if it's not already in the list
      const hasCurrentGame = headToHeadGames.some(g => g.game_id === gameIdNum)
      if (!hasCurrentGame) {
        headToHeadGames.push({
          game_id: gameIdNum,
          date: game.date,
          home_team_name: game.home_team_name,
          away_team_name: game.away_team_name,
          home_total_goals: game.home_total_goals,
          away_total_goals: game.away_total_goals,
          official_home_goals: game.official_home_goals,
          official_away_goals: game.official_away_goals,
          home_team_id: game.home_team_id,
          away_team_id: game.away_team_id,
          game_type: game.game_type || 'Regular',
        })
        // Re-sort after adding current game
        headToHeadGames.sort((a, b) => {
          const dateA = a.date ? new Date(a.date).getTime() : 0
          const dateB = b.date ? new Date(b.date).getTime() : 0
          if (dateA === dateB) {
            return (a.game_id || 0) - (b.game_id || 0)
          }
          return dateA - dateB
        })
      }
      
      // Ensure we always have at least the current game
      const finalHeadToHeadGames = headToHeadGames.length > 0 
        ? headToHeadGames 
        : [{
            game_id: gameIdNum,
            date: game.date,
            home_team_name: game.home_team_name,
            away_team_name: game.away_team_name,
            home_total_goals: game.home_total_goals,
            away_total_goals: game.away_total_goals,
            official_home_goals: game.official_home_goals,
            official_away_goals: game.official_away_goals,
            home_team_id: game.home_team_id,
            away_team_id: game.away_team_id,
            game_type: game.game_type || 'Regular',
          }]
      
      return { 
        homeGames: homeTeamGames || [], 
        awayGames: awayTeamGames || [],
        headToHeadGames: finalHeadToHeadGames
      }
    })()
  ])
  
  // Extract results with error handling
  const rosterData = roster.status === 'fulfilled' ? roster.value : []
  const goalsData = goals.status === 'fulfilled' ? goals.value : []
  const playersData = players.status === 'fulfilled' ? players.value : []
  const priorGamesData = priorGamesResult.status === 'fulfilled' ? priorGamesResult.value : { homeGames: [], awayGames: [], headToHeadGames: [] }
  const goalieStatsData = goalieStats.status === 'fulfilled' ? goalieStats.value : []
  const shotsData = shots.status === 'fulfilled' ? shots.value : []
  
  // Handle game events result (highlights only)
  const gameEvents = gameEventsResult.status === 'fulfilled' && !gameEventsResult.value.error
    ? gameEventsResult.value
    : { data: [] }
  
  // Handle all events result (for play-by-play timeline)
  const allEvents = allEventsResult.status === 'fulfilled' && !allEventsResult.value.error
    ? allEventsResult.value.data || []
    : []
  
  // Handle shifts result
  const shiftsData = shiftsResult.status === 'fulfilled' && !shiftsResult.value.error
    ? shiftsResult.value.data || []
    : []
  
  // Log any rejected promises for debugging
  const rejected = [roster, goals, players, goalieStats, shots, gameEventsResult, allEventsResult, shiftsResult, priorGamesResult]
    .filter((p) => p.status === 'rejected')
  if (rejected.length > 0) {
    const errorDetails = rejected.map((r) => {
      if (r.status === 'rejected') {
        return r.reason?.message || r.reason || 'Unknown error'
      }
      return null
    }).filter(Boolean)
    console.warn(`Some data failed to load for game ${gameIdNum}:`, errorDetails)
  }
  
  // Debug: Log roster data (only in development)
  if (process.env.NODE_ENV === 'development') {
    if (roster.status === 'fulfilled') {
      if (rosterData.length === 0) {
        console.warn(`No roster data found for game ${gameIdNum}`)
      }
    } else if (roster.status === 'rejected') {
      console.error(`Game ${gameIdNum} roster fetch failed:`, roster.reason)
    }
  }
  
  // Get highlights (goals, saves, and other highlight events)
  // Merge with schedule for date/time formatting
  const highlightsRaw = (gameEvents?.data || []).filter((e: GameEvent) => 
    e.is_goal || e.is_highlight || e.is_save || e.event_type === 'Goal'
  )
  
  // Enhance highlights with period/time info
  const highlights: EnhancedHighlight[] = highlightsRaw.map((event: GameEvent) => {
    const period = event.period || 1
    const timeSeconds = event.time_start_total_seconds || event.time_seconds || 0
    const periodTime = event.time_remaining || event.period_time
    const minutes = Math.floor(timeSeconds / 60) % 20 // Period minutes
    const seconds = timeSeconds % 60
    const timeStr = periodTime || `${minutes}:${seconds.toString().padStart(2, '0')}`
    
    return {
      ...event,
      period_time: timeStr,
      event_time: `${periodTime || timeStr} (P${period})`,
    }
  })
  
  // Get tracking status using the new comprehensive function
  const gameTrackingStatus = await getGameTrackingStatus(gameIdNum).catch(() => null)
  const hasVideo = gameTrackingStatus?.hasVideo || false
  const hasTracking = gameTrackingStatus?.status !== 'none' && gameTrackingStatus !== null
  const hasEvents = gameTrackingStatus?.hasEvents || false
  const hasShifts = gameTrackingStatus?.hasShifts || false
  const hasXY = gameTrackingStatus?.hasXY || false
  
  // For play-by-play: if we have events, we have tracked data (regardless of fact_game_status)
  const hasTrackedEvents = allEvents.length > 0
  
  // Get team info for logos with error handling
  const homeTeamId = game.home_team_id
  const awayTeamId = game.away_team_id
  const [homeTeamResult, awayTeamResult] = await Promise.allSettled([
    homeTeamId ? getTeamById(String(homeTeamId)) : Promise.resolve(null),
    awayTeamId ? getTeamById(String(awayTeamId)) : Promise.resolve(null)
  ])
  
  const homeTeam: DimTeam | null = homeTeamResult.status === 'fulfilled' ? homeTeamResult.value : null
  const awayTeam: DimTeam | null = awayTeamResult.status === 'fulfilled' ? awayTeamResult.value : null
  
  // Create players map for photos (optimized - single pass)
  const playersMap = new Map<string, DimPlayer>(
    playersData.map((p) => [String(p.player_id), p])
  )
  
  // Create name-to-ID map for goal scorers (multiple name variations)
  // Performance: Single pass through players array
  const playerNameToIdMap = new Map<string, string>()
  playersData.forEach((p: DimPlayer) => {
    if (p.player_name) {
      const nameLower = p.player_name.toLowerCase().trim()
      playerNameToIdMap.set(nameLower, String(p.player_id))
      // Also add "Last, First" format if it's "First Last"
      const parts = p.player_name.trim().split(/\s+/)
      if (parts.length === 2) {
        playerNameToIdMap.set(`${parts[1]}, ${parts[0]}`.toLowerCase(), String(p.player_id))
      }
    }
    if (p.player_full_name) {
      const fullNameLower = p.player_full_name.toLowerCase().trim()
      playerNameToIdMap.set(fullNameLower, String(p.player_id))
      // Also add "Last, First" format if it's "First Last"
      const parts = p.player_full_name.trim().split(/\s+/)
      if (parts.length === 2) {
        playerNameToIdMap.set(`${parts[1]}, ${parts[0]}`.toLowerCase(), String(p.player_id))
      }
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
  
  // Create maps of player_id to advanced stats
  const createPlayerStatsMap = (statsList: (FactPlayerGameStats | Record<string, any>)[]) => 
    new Map<string, FactPlayerGameStats | Record<string, any>>(
      statsList.map((s) => [String(s.player_id), s])
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
      
      {/* Scoreboard - Enhanced Header */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="bg-gradient-to-r from-primary/10 via-transparent to-primary/10 p-8">
          <div className="flex items-center justify-between">
            {/* Away Team */}
            <div className="flex-1 text-center">
              <div className="flex items-center justify-center gap-4 mb-3">
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
                <div>
                  {awayTeam?.team_name || game.away_team_name ? (
                    <Link 
                      href={`/norad/team/${(awayTeam?.team_name || game.away_team_name || '').replace(/\s+/g, '_')}`}
                      className="font-display text-xl font-bold text-foreground hover:text-primary transition-colors"
                    >
                      {game.away_team_name || 'Away'}
                    </Link>
                  ) : (
                    <div className="font-display text-xl font-bold text-foreground">
                      {game.away_team_name || 'Away'}
                    </div>
                  )}
                </div>
              </div>
              <div className={cn(
                'font-mono text-6xl font-bold',
                awayGoals > homeGoals ? 'text-save' : 'text-muted-foreground'
              )}>
                {awayGoals}
              </div>
            </div>
            
            {/* VS / Date */}
            <div className="px-8 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-2">Final</div>
              <div className="text-sm font-mono text-muted-foreground mb-1">
                {game.date ? new Date(game.date).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric'
                }) : ''}
              </div>
              {game.date && (
                <div className="text-xs font-mono text-muted-foreground">
                  {new Date(game.date).toLocaleDateString('en-US', {
                    weekday: 'long'
                  })}
                </div>
              )}
            </div>
            
            {/* Home Team */}
            <div className="flex-1 text-center">
              <div className="flex items-center justify-center gap-4 mb-3">
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
                <div>
                  {homeTeam?.team_name || game.home_team_name ? (
                    <Link 
                      href={`/norad/team/${(homeTeam?.team_name || game.home_team_name || '').replace(/\s+/g, '_')}`}
                      className="font-display text-xl font-bold text-foreground hover:text-primary transition-colors"
                    >
                      {game.home_team_name || 'Home'}
                    </Link>
                  ) : (
                    <div className="font-display text-xl font-bold text-foreground">
                      {game.home_team_name || 'Home'}
                    </div>
                  )}
                </div>
              </div>
              <div className={cn(
                'font-mono text-6xl font-bold',
                homeGoals > awayGoals ? 'text-save' : 'text-muted-foreground'
              )}>
                {homeGoals}
              </div>
            </div>
          </div>
          
          {/* Championship Banner & Game Type */}
          {(isChampionshipGame || isPlayoff) && (
            <div className="mt-4 pt-4 border-t border-border/50">
              {isChampionshipGame && (
                <div className="flex items-center justify-center gap-2 mb-2">
                  <Trophy className="w-5 h-5 text-yellow-500 fill-yellow-500" />
                  <span className="font-display text-lg font-bold text-yellow-500 uppercase tracking-wider">
                    Championship Game
                  </span>
                  <Trophy className="w-5 h-5 text-yellow-500 fill-yellow-500" />
                </div>
              )}
              <div className="flex items-center justify-center">
                <span className={cn(
                  'text-sm font-mono uppercase px-3 py-1 rounded font-semibold',
                  isPlayoff
                    ? 'bg-primary/20 text-primary'
                    : 'bg-muted text-muted-foreground'
                )}>
                  {isPlayoff ? 'Playoffs' : 'Regular Season'}
                </span>
              </div>
            </div>
          )}
        </div>
        
        <div className="px-6 py-4 bg-accent/50 border-t border-border">
          {/* Period-by-Period Score Breakdown - Show for all games */}
          {(() => {
            // Calculate period scores from goal events (more accurate) - supports multiple OT periods
            const calculatePeriodScores = () => {
              const periodScores: Record<number, { home: number; away: number }> = {}
              
              // Get all goal events
              const goalEvents = allEvents.filter((event: any) => {
                return event.is_goal === true || 
                       (event.event_type === 'Goal' && event.event_detail === 'Goal_Scored')
              })
              
              goalEvents.forEach((event: any) => {
                const period = event.period ? Number(event.period) : 1
                const teamId = event.team_id || event.event_team_id
                
                if (teamId && period >= 1) {
                  // Initialize period if not exists
                  if (!periodScores[period]) {
                    periodScores[period] = { home: 0, away: 0 }
                  }
                  
                  const isHome = String(teamId) === String(homeTeamId)
                  const isAway = String(teamId) === String(awayTeamId)
                  
                  if (isHome) {
                    periodScores[period].home++
                  } else if (isAway) {
                    periodScores[period].away++
                  }
                }
              })
              
              return periodScores
            }
            
            const periodScores = calculatePeriodScores()
            
            // Check if we have event data (more accurate than game table fields)
            const hasEventData = allEvents.length > 0 && allEvents.some((e: any) => 
              (e.is_goal === true || e.event_type === 'Goal') && e.period
            )
            
            // Fallback to game data if no events available
            const gameAny = game as any
            const homeP1 = hasEventData 
              ? (periodScores[1]?.home ?? null)
              : (gameAny.home_team_period1_goals ?? gameAny.home_p1_goals ?? null)
            const awayP1 = hasEventData 
              ? (periodScores[1]?.away ?? null)
              : (gameAny.away_team_period1_goals ?? gameAny.away_p1_goals ?? null)
            const homeP2 = hasEventData 
              ? (periodScores[2]?.home ?? null)
              : (gameAny.home_team_period2_goals ?? gameAny.home_p2_goals ?? null)
            const awayP2 = hasEventData 
              ? (periodScores[2]?.away ?? null)
              : (gameAny.away_team_period2_goals ?? gameAny.away_p2_goals ?? null)
            const homeP3 = hasEventData 
              ? (periodScores[3]?.home ?? null)
              : (gameAny.home_team_period3_goals ?? gameAny.home_p3_goals ?? null)
            const awayP3 = hasEventData 
              ? (periodScores[3]?.away ?? null)
              : (gameAny.away_team_period3_goals ?? gameAny.away_p3_goals ?? null)
            
            // Get all OT periods (period 4+)
            const otPeriods: Array<{ period: number; home: number | null; away: number | null }> = []
            if (hasEventData) {
              // Get all periods > 3 from events
              const otPeriodNumbers = Object.keys(periodScores)
                .map(Number)
                .filter(p => p > 3)
                .sort((a, b) => a - b)
              
              otPeriodNumbers.forEach(periodNum => {
                otPeriods.push({
                  period: periodNum,
                  home: periodScores[periodNum]?.home ?? null,
                  away: periodScores[periodNum]?.away ?? null
                })
              })
            }
            
            // If no OT periods found in events (or no event data), check fallback fields
            // Try multiple field name variations (case variations)
            if (otPeriods.length === 0) {
              // Try all possible field name variations
              const homeOTTotal = gameAny.home_team_periodOT_goals ?? 
                                 gameAny.home_team_periodot_goals ?? 
                                 gameAny.home_ot_goals ??
                                 null
              const awayOTTotal = gameAny.away_team_periodOT_goals ?? 
                                gameAny.away_team_periodot_goals ?? 
                                gameAny.away_ot_goals ??
                                null
              
              // Also check if game went to OT by comparing regulation goals to total goals
              const homeRegulation = (homeP1 ?? 0) + (homeP2 ?? 0) + (homeP3 ?? 0)
              const awayRegulation = (awayP1 ?? 0) + (awayP2 ?? 0) + (awayP3 ?? 0)
              const homeTotal = Number(gameAny.home_total_goals) ?? 0
              const awayTotal = Number(gameAny.away_total_goals) ?? 0
              const homeOTCalculated = homeTotal > homeRegulation ? homeTotal - homeRegulation : null
              const awayOTCalculated = awayTotal > awayRegulation ? awayTotal - awayRegulation : null
              
              // Use explicit OT goals if available, otherwise calculate from totals
              const finalHomeOT = homeOTTotal !== null && homeOTTotal !== undefined 
                ? Number(homeOTTotal) 
                : (homeOTCalculated !== null && homeOTCalculated > 0 ? homeOTCalculated : null)
              const finalAwayOT = awayOTTotal !== null && awayOTTotal !== undefined 
                ? Number(awayOTTotal) 
                : (awayOTCalculated !== null && awayOTCalculated > 0 ? awayOTCalculated : null)
              
              if (finalHomeOT !== null || finalAwayOT !== null) {
                // For now, show total OT goals in a single OT period
                // In the future, if we have per-OT-period data, we can split it
                otPeriods.push({
                  period: 4,
                  home: finalHomeOT,
                  away: finalAwayOT
                })
              }
            }
            
            // Calculate running scores
            const runningHomeP1 = homeP1 ?? 0
            const runningAwayP1 = awayP1 ?? 0
            const runningHomeP2 = (homeP1 ?? 0) + (homeP2 ?? 0)
            const runningAwayP2 = (awayP1 ?? 0) + (awayP2 ?? 0)
            const runningHomeP3 = (homeP1 ?? 0) + (homeP2 ?? 0) + (homeP3 ?? 0)
            const runningAwayP3 = (awayP1 ?? 0) + (awayP2 ?? 0) + (awayP3 ?? 0)
            
            // Calculate running scores for each OT period
            const otRunningScores = otPeriods.map((ot, idx) => {
              const prevOTTotal = idx === 0 
                ? runningHomeP3 
                : otPeriods.slice(0, idx).reduce((sum, p) => sum + (p.home ?? 0), runningHomeP3)
              const prevAwayOTTotal = idx === 0 
                ? runningAwayP3 
                : otPeriods.slice(0, idx).reduce((sum, p) => sum + (p.away ?? 0), runningAwayP3)
              return {
                home: prevOTTotal + (ot.home ?? 0),
                away: prevAwayOTTotal + (ot.away ?? 0)
              }
            })
            
            // Only show if we have at least one period of data
            if (homeP1 === null && awayP1 === null && homeP2 === null && awayP2 === null && homeP3 === null && awayP3 === null && otPeriods.length === 0) {
              return null
            }
            
            const totalPeriods = 3 + otPeriods.length
            
            return (
              <div 
                className="grid gap-3 mt-3 pt-3 border-t border-border/50"
                style={{ gridTemplateColumns: `repeat(${Math.min(totalPeriods, 6)}, minmax(0, 1fr))` }}
              >
                <div className="text-center">
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-2">P1</div>
                  {awayP1 !== null && homeP1 !== null ? (
                    <div className="flex items-center justify-center gap-2">
                      {awayTeam && (
                        <TeamLogo
                          src={awayTeam.team_logo || null}
                          name={awayTeam.team_name || ''}
                          abbrev={awayTeam.team_cd}
                          primaryColor={awayTeam.primary_color || awayTeam.team_color1}
                          secondaryColor={awayTeam.team_color2}
                          size="sm"
                        />
                      )}
                      <span className="text-sm font-mono font-semibold">{awayP1}</span>
                      <span className="text-xs text-muted-foreground">-</span>
                      <span className="text-sm font-mono font-semibold">{homeP1}</span>
                      {homeTeam && (
                        <TeamLogo
                          src={homeTeam.team_logo || null}
                          name={homeTeam.team_name || ''}
                          abbrev={homeTeam.team_cd}
                          primaryColor={homeTeam.primary_color || homeTeam.team_color1}
                          secondaryColor={homeTeam.team_color2}
                          size="sm"
                        />
                      )}
                    </div>
                  ) : (
                    <div className="text-xs font-mono text-muted-foreground">-</div>
                  )}
                  {/* Running Score */}
                  {(awayP1 !== null || homeP1 !== null) && (
                    <div className="text-xs font-mono text-muted-foreground mt-2 pt-2 border-t border-border/30">
                      {runningAwayP1} - {runningHomeP1}
                    </div>
                  )}
                </div>
                <div className="text-center">
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-2">P2</div>
                  {awayP2 !== null && homeP2 !== null ? (
                    <div className="flex items-center justify-center gap-2">
                      {awayTeam && (
                        <TeamLogo
                          src={awayTeam.team_logo || null}
                          name={awayTeam.team_name || ''}
                          abbrev={awayTeam.team_cd}
                          primaryColor={awayTeam.primary_color || awayTeam.team_color1}
                          secondaryColor={awayTeam.team_color2}
                          size="sm"
                        />
                      )}
                      <span className="text-sm font-mono font-semibold">{awayP2}</span>
                      <span className="text-xs text-muted-foreground">-</span>
                      <span className="text-sm font-mono font-semibold">{homeP2}</span>
                      {homeTeam && (
                        <TeamLogo
                          src={homeTeam.team_logo || null}
                          name={homeTeam.team_name || ''}
                          abbrev={homeTeam.team_cd}
                          primaryColor={homeTeam.primary_color || homeTeam.team_color1}
                          secondaryColor={homeTeam.team_color2}
                          size="sm"
                        />
                      )}
                    </div>
                  ) : (
                    <div className="text-xs font-mono text-muted-foreground">-</div>
                  )}
                  {/* Running Score */}
                  {(awayP2 !== null || homeP2 !== null) && (
                    <div className="text-xs font-mono text-muted-foreground mt-2 pt-2 border-t border-border/30">
                      {runningAwayP2} - {runningHomeP2}
                    </div>
                  )}
                </div>
                <div className="text-center">
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-2">P3</div>
                  {awayP3 !== null && homeP3 !== null ? (
                    <div className="flex items-center justify-center gap-2">
                      {awayTeam && (
                        <TeamLogo
                          src={awayTeam.team_logo || null}
                          name={awayTeam.team_name || ''}
                          abbrev={awayTeam.team_cd}
                          primaryColor={awayTeam.primary_color || awayTeam.team_color1}
                          secondaryColor={awayTeam.team_color2}
                          size="sm"
                        />
                      )}
                      <span className="text-sm font-mono font-semibold">{awayP3}</span>
                      <span className="text-xs text-muted-foreground">-</span>
                      <span className="text-sm font-mono font-semibold">{homeP3}</span>
                      {homeTeam && (
                        <TeamLogo
                          src={homeTeam.team_logo || null}
                          name={homeTeam.team_name || ''}
                          abbrev={homeTeam.team_cd}
                          primaryColor={homeTeam.primary_color || homeTeam.team_color1}
                          secondaryColor={homeTeam.team_color2}
                          size="sm"
                        />
                      )}
                    </div>
                  ) : (
                    <div className="text-xs font-mono text-muted-foreground">-</div>
                  )}
                  {/* Running Score */}
                  {(awayP3 !== null || homeP3 !== null) && (
                    <div className="text-xs font-mono text-muted-foreground mt-2 pt-2 border-t border-border/30">
                      {runningAwayP3} - {runningHomeP3}
                    </div>
                  )}
                </div>
                {/* OT Periods - Dynamic */}
                {otPeriods.map((ot, idx) => {
                  const otNumber = idx + 1
                  const runningHome = otRunningScores[idx]?.home ?? 0
                  const runningAway = otRunningScores[idx]?.away ?? 0
                  
                  return (
                    <div key={`ot-${ot.period}`} className="text-center">
                      <div className="text-xs font-mono text-muted-foreground uppercase mb-2">
                        OT{otNumber}
                      </div>
                      {ot.away !== null && ot.home !== null ? (
                        <div className="flex items-center justify-center gap-2">
                          {awayTeam && (
                            <TeamLogo
                              src={awayTeam.team_logo || null}
                              name={awayTeam.team_name || ''}
                              abbrev={awayTeam.team_cd}
                              primaryColor={awayTeam.primary_color || awayTeam.team_color1}
                              secondaryColor={awayTeam.team_color2}
                              size="sm"
                            />
                          )}
                          <span className="text-sm font-mono font-semibold">{ot.away}</span>
                          <span className="text-xs text-muted-foreground">-</span>
                          <span className="text-sm font-mono font-semibold">{ot.home}</span>
                          {homeTeam && (
                            <TeamLogo
                              src={homeTeam.team_logo || null}
                              name={homeTeam.team_name || ''}
                              abbrev={homeTeam.team_cd}
                              primaryColor={homeTeam.primary_color || homeTeam.team_color1}
                              secondaryColor={homeTeam.team_color2}
                              size="sm"
                            />
                          )}
                        </div>
                      ) : (
                        <div className="text-xs font-mono text-muted-foreground">-</div>
                      )}
                      {/* Running Score */}
                      {(ot.away !== null || ot.home !== null) && (
                        <div className="text-xs font-mono text-muted-foreground mt-2 pt-2 border-t border-border/30">
                          {runningAway} - {runningHome}
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            )
          })()}
        </div>
      </div>
      
      {/* Team Stats Comparison - Show for all games */}
      {(homeTeamGameStats || awayTeamGameStats || homePPOpps > 0 || awayPPOpps > 0) && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              Team Stats Comparison
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-accent/50">
                  <th className="px-4 py-2 text-left font-display text-xs text-muted-foreground">Stat</th>
                  <th className="px-4 py-2 text-center font-display text-xs text-foreground">
                    {awayTeam?.team_cd || game.away_team_name || 'Away'}
                  </th>
                  <th className="px-4 py-2 text-center font-display text-xs text-foreground">
                    {homeTeam?.team_cd || game.home_team_name || 'Home'}
                  </th>
                </tr>
              </thead>
              <tbody>
                {/* Shots */}
                {(homeTeamGameStats?.shots_for || awayTeamGameStats?.shots_for || homeTeamAggs.shots > 0 || awayTeamAggs.shots > 0) && (
                  <tr className="border-b border-border hover:bg-muted/50 transition-colors">
                    <td className="px-4 py-2 font-mono text-xs text-muted-foreground">Shots</td>
                    <td className="px-4 py-2 text-center font-mono font-semibold">
                      {awayTeamGameStats?.shots_for ?? awayTeamAggs.shots ?? 0}
                    </td>
                    <td className="px-4 py-2 text-center font-mono font-semibold">
                      {homeTeamGameStats?.shots_for ?? homeTeamAggs.shots ?? 0}
                    </td>
                  </tr>
                )}
                
                {/* Shots on Goal */}
                {(homeTeamGameStats?.shots_on_goal_for || awayTeamGameStats?.shots_on_goal_for) && (
                  <tr className="border-b border-border hover:bg-muted/50 transition-colors">
                    <td className="px-4 py-2 font-mono text-xs text-muted-foreground">Shots on Goal</td>
                    <td className="px-4 py-2 text-center font-mono font-semibold">
                      {awayTeamGameStats?.shots_on_goal_for ?? 0}
                    </td>
                    <td className="px-4 py-2 text-center font-mono font-semibold">
                      {homeTeamGameStats?.shots_on_goal_for ?? 0}
                    </td>
                  </tr>
                )}
                
                {/* Faceoffs */}
                {(homeTeamGameStats?.fo_taken || awayTeamGameStats?.fo_taken) && (
                  <tr className="border-b border-border hover:bg-muted/50 transition-colors">
                    <td className="px-4 py-2 font-mono text-xs text-muted-foreground">Faceoffs Won</td>
                    <td className="px-4 py-2 text-center font-mono font-semibold">
                      {awayTeamGameStats?.fo_wins ?? 0} / {awayTeamGameStats?.fo_taken ?? 0}
                      {awayTeamGameStats?.fo_pct && (
                        <span className="text-xs text-muted-foreground ml-1">
                          ({Number(awayTeamGameStats.fo_pct).toFixed(1)}%)
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-2 text-center font-mono font-semibold">
                      {homeTeamGameStats?.fo_wins ?? 0} / {homeTeamGameStats?.fo_taken ?? 0}
                      {homeTeamGameStats?.fo_pct && (
                        <span className="text-xs text-muted-foreground ml-1">
                          ({Number(homeTeamGameStats.fo_pct).toFixed(1)}%)
                        </span>
                      )}
                    </td>
                  </tr>
                )}
                
                {/* Power Play */}
                {(homePPOpps > 0 || awayPPOpps > 0 || homeTeamGameStats?.pp_opportunities || awayTeamGameStats?.pp_opportunities) && (
                  <tr className="border-b border-border hover:bg-muted/50 transition-colors">
                    <td className="px-4 py-2 font-mono text-xs text-muted-foreground">Power Play</td>
                    <td className="px-4 py-2 text-center font-mono font-semibold">
                      {awayPPGoals || awayTeamGameStats?.pp_goals || 0} / {awayPPOpps || awayTeamGameStats?.pp_opportunities || 0}
                      {awayPPOpps > 0 && (
                        <span className="text-xs text-muted-foreground ml-1">
                          ({((awayPPGoals || awayTeamGameStats?.pp_goals || 0) / awayPPOpps * 100).toFixed(1)}%)
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-2 text-center font-mono font-semibold">
                      {homePPGoals || homeTeamGameStats?.pp_goals || 0} / {homePPOpps || homeTeamGameStats?.pp_opportunities || 0}
                      {homePPOpps > 0 && (
                        <span className="text-xs text-muted-foreground ml-1">
                          ({((homePPGoals || homeTeamGameStats?.pp_goals || 0) / homePPOpps * 100).toFixed(1)}%)
                        </span>
                      )}
                    </td>
                  </tr>
                )}
                
                {/* Penalty Kill */}
                {(homeTeamGameStats?.pk_opportunities || awayTeamGameStats?.pk_opportunities) && (
                  <tr className="border-b border-border hover:bg-muted/50 transition-colors">
                    <td className="px-4 py-2 font-mono text-xs text-muted-foreground">Penalty Kill</td>
                    <td className="px-4 py-2 text-center font-mono font-semibold">
                      {awayTeamGameStats?.pk_opportunities ? (awayTeamGameStats.pk_opportunities - (awayTeamGameStats.pk_goals_against || 0)) : 0} / {awayTeamGameStats?.pk_opportunities || 0}
                      {awayTeamGameStats?.pk_pct && (
                        <span className="text-xs text-muted-foreground ml-1">
                          ({Number(awayTeamGameStats.pk_pct).toFixed(1)}%)
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-2 text-center font-mono font-semibold">
                      {homeTeamGameStats?.pk_opportunities ? (homeTeamGameStats.pk_opportunities - (homeTeamGameStats.pk_goals_against || 0)) : 0} / {homeTeamGameStats?.pk_opportunities || 0}
                      {homeTeamGameStats?.pk_pct && (
                        <span className="text-xs text-muted-foreground ml-1">
                          ({Number(homeTeamGameStats.pk_pct).toFixed(1)}%)
                        </span>
                      )}
                    </td>
                  </tr>
                )}
                
                {/* Hits */}
                {(homeTeamGameStats?.hits || awayTeamGameStats?.hits || homeTeamAggs.hits > 0 || awayTeamAggs.hits > 0) && (
                  <tr className="border-b border-border hover:bg-muted/50 transition-colors">
                    <td className="px-4 py-2 font-mono text-xs text-muted-foreground">Hits</td>
                    <td className="px-4 py-2 text-center font-mono font-semibold">
                      {awayTeamGameStats?.hits ?? awayTeamAggs.hits ?? 0}
                    </td>
                    <td className="px-4 py-2 text-center font-mono font-semibold">
                      {homeTeamGameStats?.hits ?? homeTeamAggs.hits ?? 0}
                    </td>
                  </tr>
                )}
                
                {/* Blocks */}
                {(homeTeamGameStats?.blocks || awayTeamGameStats?.blocks || homeTeamAggs.blocks > 0 || awayTeamAggs.blocks > 0) && (
                  <tr className="border-b border-border hover:bg-muted/50 transition-colors">
                    <td className="px-4 py-2 font-mono text-xs text-muted-foreground">Blocks</td>
                    <td className="px-4 py-2 text-center font-mono font-semibold">
                      {awayTeamGameStats?.blocks ?? awayTeamAggs.blocks ?? 0}
                    </td>
                    <td className="px-4 py-2 text-center font-mono font-semibold">
                      {homeTeamGameStats?.blocks ?? homeTeamAggs.blocks ?? 0}
                    </td>
                  </tr>
                )}
                
                {/* PIM */}
                {(homeTeamGameStats?.pim || awayTeamGameStats?.pim) && (
                  <tr className="border-b border-border hover:bg-muted/50 transition-colors">
                    <td className="px-4 py-2 font-mono text-xs text-muted-foreground">Penalty Minutes</td>
                    <td className="px-4 py-2 text-center font-mono font-semibold">
                      {awayTeamGameStats?.pim ?? 0}
                    </td>
                    <td className="px-4 py-2 text-center font-mono font-semibold">
                      {homeTeamGameStats?.pim ?? 0}
                    </td>
                  </tr>
                )}
                
                {/* Corsi/Fenwick (if available) */}
                {hasTracking && (homeTeamGameStats?.cf_pct || awayTeamGameStats?.cf_pct) && (
                  <>
                    <tr className="border-b border-border hover:bg-muted/50 transition-colors">
                      <td className="px-4 py-2 font-mono text-xs text-muted-foreground">CF%</td>
                      <td className="px-4 py-2 text-center font-mono font-semibold">
                        {awayTeamGameStats?.cf_pct ? Number(awayTeamGameStats.cf_pct).toFixed(1) : awayCFPct.toFixed(1)}%
                      </td>
                      <td className="px-4 py-2 text-center font-mono font-semibold">
                        {homeTeamGameStats?.cf_pct ? Number(homeTeamGameStats.cf_pct).toFixed(1) : homeCFPct.toFixed(1)}%
                      </td>
                    </tr>
                    <tr className="border-b border-border hover:bg-muted/50 transition-colors">
                      <td className="px-4 py-2 font-mono text-xs text-muted-foreground">FF%</td>
                      <td className="px-4 py-2 text-center font-mono font-semibold">
                        {awayTeamGameStats?.ff_pct ? Number(awayTeamGameStats.ff_pct).toFixed(1) : awayFFPct.toFixed(1)}%
                      </td>
                      <td className="px-4 py-2 text-center font-mono font-semibold">
                        {homeTeamGameStats?.ff_pct ? Number(homeTeamGameStats.ff_pct).toFixed(1) : homeFFPct.toFixed(1)}%
                      </td>
                    </tr>
                  </>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
      
      {/* Team Advanced Stats Summary - Only show if we have tracking data */}
      {hasTracking && (
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Home Team Aggregates */}
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
                  className="font-display text-sm font-semibold uppercase tracking-wider hover:text-primary transition-colors"
                >
                  {homeTeam?.team_name || game.home_team_name || 'Home'} Team Stats
                </Link>
              ) : (
                <h2 className="font-display text-sm font-semibold uppercase tracking-wider">
                  {homeTeam?.team_name || game.home_team_name || 'Home'} Team Stats
                </h2>
              )}
            </div>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">CF%</div>
                <div className="font-mono text-xl font-semibold text-primary">{homeCFPct.toFixed(1)}%</div>
              </div>
              <div className="text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">FF%</div>
                <div className="font-mono text-xl font-semibold text-primary">{homeFFPct.toFixed(1)}%</div>
              </div>
              <div className="text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Shots</div>
                <div className="font-mono text-xl font-semibold">{homeTeamAggs.shots}</div>
              </div>
              <div className="text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Hits</div>
                <div className="font-mono text-xl font-semibold">{homeTeamAggs.hits}</div>
              </div>
              <div className="text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Blocks</div>
                <div className="font-mono text-xl font-semibold text-save">{homeTeamAggs.blocks}</div>
              </div>
              <div className="text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">TO Diff</div>
                <div className={cn(
                  'font-mono text-xl font-semibold',
                  (homeTeamAggs.takeaways - homeTeamAggs.badGiveaways) > 0 ? 'text-save' : 'text-goal'
                )}>
                  {(homeTeamAggs.takeaways - homeTeamAggs.badGiveaways) > 0 ? '+' : ''}
                  {homeTeamAggs.takeaways - homeTeamAggs.badGiveaways}
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Away Team Aggregates */}
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
                  className="font-display text-sm font-semibold uppercase tracking-wider hover:text-primary transition-colors"
                >
                  {awayTeam?.team_name || game.away_team_name || 'Away'} Team Stats
                </Link>
              ) : (
                <h2 className="font-display text-sm font-semibold uppercase tracking-wider">
                  {awayTeam?.team_name || game.away_team_name || 'Away'} Team Stats
                </h2>
              )}
            </div>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">CF%</div>
                <div className="font-mono text-xl font-semibold text-primary">{awayCFPct.toFixed(1)}%</div>
              </div>
              <div className="text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">FF%</div>
                <div className="font-mono text-xl font-semibold text-primary">{awayFFPct.toFixed(1)}%</div>
              </div>
              <div className="text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Shots</div>
                <div className="font-mono text-xl font-semibold">{awayTeamAggs.shots}</div>
              </div>
              <div className="text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Hits</div>
                <div className="font-mono text-xl font-semibold">{awayTeamAggs.hits}</div>
              </div>
              <div className="text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Blocks</div>
                <div className="font-mono text-xl font-semibold text-save">{awayTeamAggs.blocks}</div>
              </div>
              <div className="text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">TO Diff</div>
                <div className={cn(
                  'font-mono text-xl font-semibold',
                  (awayTeamAggs.takeaways - awayTeamAggs.badGiveaways) > 0 ? 'text-save' : 'text-goal'
                )}>
                  {(awayTeamAggs.takeaways - awayTeamAggs.badGiveaways) > 0 ? '+' : ''}
                  {awayTeamAggs.takeaways - awayTeamAggs.badGiveaways}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      )}
      
      {/* Scoring Summary - Grouped by Period */}
      {(() => {
        // Use allEvents filtered for goals instead of goalsData to ensure we get all periods
        // Filter allEvents for goals (event_type='Goal' or is_goal=true)
        const allGoalsFromEvents = allEvents.filter((event: any) => 
          event.event_type === 'Goal' || event.is_goal === true
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
        const allGoalsSorted = [...allGoals].sort((a: GameEvent, b: GameEvent) => {
          const periodA = getPeriod(a)
          const periodB = getPeriod(b)
          if (periodA !== periodB) {
            return periodA - periodB
          }
          // Within same period, sort by time DESCENDING (hockey time counts down)
          const timeA = a.time_start_total_seconds ?? a.time_seconds ?? 0
          const timeB = b.time_start_total_seconds ?? b.time_seconds ?? 0
          return timeB - timeA
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
                Scoring Summary
              </h2>
            </div>
            <div className="divide-y divide-border">
              {periods.map((period) => {
                const periodGoals = goalsByPeriod.get(period)!
                  // Sort goals within period by time DESCENDING (hockey time counts down)
                  .sort((a: GameEvent, b: GameEvent) => {
                    const timeA = a.time_start_total_seconds ?? a.time_seconds ?? 0
                    const timeB = b.time_start_total_seconds ?? b.time_seconds ?? 0
                    return timeB - timeA
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
                      // Use time_start_total_seconds if available, otherwise time_seconds
                      const timeSeconds = goal.time_start_total_seconds ?? goal.time_seconds ?? 0
                      // Calculate period time (time within the period)
                      const periodSeconds = timeSeconds % 1200 // 20 minutes = 1200 seconds per period
                      const minutes = Math.floor(periodSeconds / 60)
                      const seconds = Math.floor(periodSeconds % 60)
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
                      
                      return (
                        <div key={`${period}-${index}`} className="p-4 flex items-center gap-4">
                          <div className="w-20 text-center flex-shrink-0">
                            <div className="font-mono text-base font-semibold text-foreground">{timeStr}</div>
                            {videoLink && hasVideo && (
                              <a
                                href={videoLink}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs text-primary hover:underline mt-1 block"
                                title="Watch goal video"
                              >
                                ▶ Video
                              </a>
                            )}
                          </div>
                          
                          {/* Team Logo */}
                          {scoringTeam && (
                            <TeamLogo
                              src={scoringTeam.team_logo || null}
                              name={scoringTeam.team_name || ''}
                              abbrev={scoringTeam.team_cd}
                              primaryColor={scoringTeam.primary_color || scoringTeam.team_color1}
                              secondaryColor={scoringTeam.team_color2}
                              size="md"
                            />
                          )}
                          
                          {/* Running Score */}
                          <div className="flex items-center gap-2 min-w-[60px]">
                            <div className="font-mono text-lg font-bold text-foreground">
                              {scoreStr}
                            </div>
                          </div>
                          
                          {/* Player Photo */}
                          {scorerImage && (
                            <PlayerPhoto
                              src={scorerImage}
                              name={scorerName || ''}
                              size="sm"
                            />
                          )}
                          
                          <div className="flex-1">
                            {scorerName ? (
                              getPlayerGameLink(scorerId) ? (
                                <Link
                                  href={getPlayerGameLink(scorerId)!}
                                  className="font-display text-sm font-semibold text-foreground hover:text-primary transition-colors"
                                >
                                  {scorerName}
                                </Link>
                              ) : (
                                <div className="font-display text-sm font-semibold text-foreground">
                                  {scorerName}
                                </div>
                              )
                            ) : scorerId && playersMap.has(scorerId) ? (
                              (() => {
                                const player = playersMap.get(scorerId)!
                                const name = player.player_name || player.player_full_name || 'Unknown Player'
                                return getPlayerGameLink(scorerId) ? (
                                  <Link
                                    href={getPlayerGameLink(scorerId)!}
                                    className="font-display text-sm font-semibold text-foreground hover:text-primary transition-colors"
                                  >
                                    {name}
                                  </Link>
                                ) : (
                                  <div className="font-display text-sm font-semibold text-foreground">
                                    {name}
                                  </div>
                                )
                              })()
                            ) : (
                              <div className="font-display text-sm font-semibold text-muted-foreground">
                                Unknown Scorer
                              </div>
                            )}
                            {/* Assists */}
                            {(() => {
                              // Get assists from assistEventsMap (if available) or fallback to event_player_2
                              const goalKey = goal.event_id || String(goal.time_start_total_seconds || index)
                              const assists = assistEventsMap.get(goalKey) || 
                                            (goal.event_id ? assistEventsMap.get(goal.event_id) : null) ||
                                            (goal.time_start_total_seconds ? assistEventsMap.get(String(goal.time_start_total_seconds)) : null)
                              
                              if (assists && assists.length > 0) {
                                // Sort: primary first, then secondary
                                const sortedAssists = assists.sort((a, b) => {
                                  if (a.assist_type === 'primary' && b.assist_type === 'secondary') return -1
                                  if (a.assist_type === 'secondary' && b.assist_type === 'primary') return 1
                                  return 0
                                })
                                
                                return (
                                  <div className="text-xs text-muted-foreground space-y-1 mt-1">
                                    {sortedAssists.map((assist, idx) => {
                                      const assistPlayer = playersMap.get(assist.player_id)
                                      const assistName = assistPlayer?.player_name || assistPlayer?.player_full_name || assist.player_name || 'Unknown'
                                      const assistId = assist.player_id
                                      const assistImage = assistPlayer?.player_image || null
                                      const assistLink = getPlayerGameLink(assistId)
                                      
                                      return (
                                        <div key={idx} className="flex items-center gap-2">
                                          {assistImage && (
                                            <PlayerPhoto
                                              src={assistImage}
                                              name={assistName}
                                              size="xs"
                                            />
                                          )}
                                          <span>
                                            {assist.assist_type === 'primary' ? 'A1' : 'A2'}:{' '}
                                            {assistLink ? (
                                              <Link
                                                href={assistLink}
                                                className="hover:text-foreground transition-colors"
                                              >
                                                {assistName}
                                              </Link>
                                            ) : (
                                              <span>{assistName}</span>
                                            )}
                                          </span>
                                        </div>
                                      )
                                    })}
                                  </div>
                                )
                              }
                              
                              // Fallback to event_player_2 if no assist events found
                              if (goal.event_player_2) {
                                const assistId = playerNameToIdMap.get(goal.event_player_2.toLowerCase().trim()) || null
                                const assistPlayer = assistId ? playersMap.get(assistId) : null
                                const assistImage = assistPlayer?.player_image || null
                                const assistLink = getPlayerGameLink(assistId)
                                
                                return (
                                  <div className="text-xs text-muted-foreground mt-1 flex items-center gap-2">
                                    {assistImage && (
                                      <PlayerPhoto
                                        src={assistImage}
                                        name={goal.event_player_2}
                                        size="xs"
                                      />
                                    )}
                                    <span>
                                      Assist:{' '}
                                      {assistLink ? (
                                        <Link
                                          href={assistLink}
                                          className="hover:text-foreground transition-colors"
                                        >
                                          {goal.event_player_2}
                                        </Link>
                                      ) : (
                                        <span>{goal.event_player_2}</span>
                                      )}
                                    </span>
                                  </div>
                                )
                              }
                              
                              return null
                            })()}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                )
              })}
            </div>
          </div>
        )
      })()}
      
      {/* Head-to-Head Games This Season */}
      {priorGamesData.headToHeadGames && priorGamesData.headToHeadGames.length > 0 && (() => {
        const regularSeasonGames = priorGamesData.headToHeadGames.filter((g: any) => 
          !g.game_type || g.game_type === 'Regular' || g.game_type === 'regular'
        )
        const playoffGames = priorGamesData.headToHeadGames.filter((g: any) => 
          g.game_type === 'Playoffs' || g.game_type === 'playoffs' || g.game_type === 'Playoff'
        )
        
        return (
          <div className="bg-card rounded-xl border border-border overflow-hidden">
            <div className="px-4 py-3 bg-accent border-b border-border">
              <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                <Activity className="w-4 h-4" />
                Head-to-Head This Season
              </h2>
            </div>
            <div className="p-6 space-y-6">
              {/* Regular Season Games */}
              {regularSeasonGames.length > 0 && (
                <div>
                  <h3 className="font-display text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">
                    Regular Season ({regularSeasonGames.length})
                  </h3>
                  <div className="space-y-2">
                    {regularSeasonGames.map((h2hGame: any) => {
                      const homeGoals = h2hGame.official_home_goals ?? h2hGame.home_total_goals ?? null
                      const awayGoals = h2hGame.official_away_goals ?? h2hGame.away_total_goals ?? null
                      const hasScore = homeGoals !== null && awayGoals !== null
                      const gameDate = h2hGame.date ? new Date(h2hGame.date).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric'
                      }) : ''
                      const isCurrentGame = h2hGame.game_id === gameIdNum
                      const isFutureGame = !hasScore
                      
                      return (
                        <Link
                          key={h2hGame.game_id}
                          href={`/norad/games/${h2hGame.game_id}`}
                          className={cn(
                            'block p-3 rounded-lg border border-border hover:border-primary/50 transition-all',
                            isCurrentGame && 'bg-primary/10 border-primary',
                            isFutureGame && 'opacity-75'
                          )}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                <span className="text-xs font-mono text-muted-foreground">{gameDate}</span>
                                {isFutureGame && (
                                  <span className="text-xs font-mono uppercase px-1.5 py-0.5 rounded bg-muted text-muted-foreground">
                                    Scheduled
                                  </span>
                                )}
                              </div>
                              <div className="flex items-center gap-2">
                                <span className={cn(
                                  'font-display text-sm',
                                  hasScore && awayGoals! > homeGoals! ? 'font-semibold text-foreground' : 'text-muted-foreground'
                                )}>
                                  {h2hGame.away_team_name || 'Away'}
                                </span>
                                {hasScore ? (
                                  <>
                                    <span className="font-mono text-sm font-bold text-foreground">
                                      {awayGoals}
                                    </span>
                                    <span className="text-muted-foreground">-</span>
                                    <span className="font-mono text-sm font-bold text-foreground">
                                      {homeGoals}
                                    </span>
                                  </>
                                ) : (
                                  <span className="text-xs font-mono text-muted-foreground">vs</span>
                                )}
                                <span className={cn(
                                  'font-display text-sm',
                                  hasScore && homeGoals! > awayGoals! ? 'font-semibold text-foreground' : 'text-muted-foreground'
                                )}>
                                  {h2hGame.home_team_name || 'Home'}
                                </span>
                                {isCurrentGame && (
                                  <span className="text-xs font-mono bg-primary text-primary-foreground px-2 py-0.5 rounded">
                                    Current Game
                                  </span>
                                )}
                              </div>
                            </div>
                            <ExternalLink className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                          </div>
                        </Link>
                      )
                    })}
                  </div>
                </div>
              )}
              
              {/* Playoff Games */}
              {playoffGames.length > 0 && (
                <div>
                  <h3 className="font-display text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">
                    Playoffs ({playoffGames.length})
                  </h3>
                  <div className="space-y-2">
                    {playoffGames.map((h2hGame: any) => {
                      const homeGoals = h2hGame.official_home_goals ?? h2hGame.home_total_goals ?? null
                      const awayGoals = h2hGame.official_away_goals ?? h2hGame.away_total_goals ?? null
                      const hasScore = homeGoals !== null && awayGoals !== null
                      const gameDate = h2hGame.date ? new Date(h2hGame.date).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric'
                      }) : ''
                      const isCurrentGame = h2hGame.game_id === gameIdNum
                      const isFutureGame = !hasScore
                      
                      return (
                        <Link
                          key={h2hGame.game_id}
                          href={`/norad/games/${h2hGame.game_id}`}
                          className={cn(
                            'block p-3 rounded-lg border border-border hover:border-primary/50 transition-all',
                            isCurrentGame && 'bg-primary/10 border-primary',
                            isFutureGame && 'opacity-75'
                          )}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                <span className="text-xs font-mono text-muted-foreground">{gameDate}</span>
                                <span className="text-xs font-mono uppercase px-1.5 py-0.5 rounded bg-primary/20 text-primary">
                                  Playoff
                                </span>
                                {isFutureGame && (
                                  <span className="text-xs font-mono uppercase px-1.5 py-0.5 rounded bg-muted text-muted-foreground">
                                    Scheduled
                                  </span>
                                )}
                              </div>
                              <div className="flex items-center gap-2">
                                <span className={cn(
                                  'font-display text-sm',
                                  hasScore && awayGoals! > homeGoals! ? 'font-semibold text-foreground' : 'text-muted-foreground'
                                )}>
                                  {h2hGame.away_team_name || 'Away'}
                                </span>
                                {hasScore ? (
                                  <>
                                    <span className="font-mono text-sm font-bold text-foreground">
                                      {awayGoals}
                                    </span>
                                    <span className="text-muted-foreground">-</span>
                                    <span className="font-mono text-sm font-bold text-foreground">
                                      {homeGoals}
                                    </span>
                                  </>
                                ) : (
                                  <span className="text-xs font-mono text-muted-foreground">vs</span>
                                )}
                                <span className={cn(
                                  'font-display text-sm',
                                  hasScore && homeGoals! > awayGoals! ? 'font-semibold text-foreground' : 'text-muted-foreground'
                                )}>
                                  {h2hGame.home_team_name || 'Home'}
                                </span>
                                {isCurrentGame && (
                                  <span className="text-xs font-mono bg-primary text-primary-foreground px-2 py-0.5 rounded">
                                    Current Game
                                  </span>
                                )}
                              </div>
                            </div>
                            <ExternalLink className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                          </div>
                        </Link>
                      )
                    })}
                  </div>
                </div>
              )}
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
      
      {/* Team Totals - Separate Section with Aligned Rows */}
      {((awayForwards.length > 0 || awayDefense.length > 0) || (homeForwards.length > 0 || homeDefense.length > 0)) && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              Team Totals
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-accent/50">
                  <th className="px-3 py-2 text-left font-display text-xs text-muted-foreground">Team</th>
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
                {/* Away Team Totals */}
                {(awayForwards.length > 0 || awayDefense.length > 0) && (() => {
                  const allAwaySkaters = [...awayForwards, ...awayDefense]
                  const playersWithRatings = allAwaySkaters.filter(p => {
                    const playerInfo = playersMap.get(String(p.player_id))
                    const rating = playerInfo?.current_skill_rating
                    return rating != null && rating !== '' && Number(rating) > 0
                  })
                  const avgRating = playersWithRatings.length > 0
                    ? playersWithRatings.reduce((sum, p) => {
                        const playerInfo = playersMap.get(String(p.player_id))
                        return sum + Number(playerInfo?.current_skill_rating || 0)
                      }, 0) / playersWithRatings.length
                    : null

                  return (
                    <tr className="border-b-2 border-border bg-muted/30 font-bold">
                      <td className="px-3 py-2 font-display">
                        {awayTeam?.team_name || game.away_team_name || 'Away'}
                      </td>
                      <td className="px-2 py-2 text-center"></td>
                      <td className="px-2 py-2 text-center font-mono text-sm">
                        {avgRating != null ? Number(avgRating).toFixed(1) : '-'}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-goal font-semibold">
                        {allAwaySkaters.reduce((sum, p) => sum + Number(p.goals ?? 0), 0)}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-assist font-semibold">
                        {allAwaySkaters.reduce((sum, p) => sum + Number(p.assist ?? 0), 0)}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-primary font-semibold">
                        {allAwaySkaters.reduce((sum, p) => sum + Number(p.goals ?? 0) + Number(p.assist ?? 0), 0)}
                      </td>
                      {hasTracking && (
                        <>
                          <td className="px-2 py-2 text-center font-mono text-muted-foreground font-semibold">
                            {allAwaySkaters.reduce((sum, p) => {
                              const advStats = awayPlayerStatsMap.get(String(p.player_id))
                              return sum + (Number(advStats?.shots ?? advStats?.sog ?? 0) || 0)
                            }, 0)}
                          </td>
                          <td className="px-2 py-2 text-center font-mono text-muted-foreground font-semibold">
                            {allAwaySkaters.reduce((sum, p) => {
                              const advStats = awayPlayerStatsMap.get(String(p.player_id))
                              return sum + (Number(advStats?.plus_minus_total ?? advStats?.plus_minus ?? 0) || 0)
                            }, 0)}
                          </td>
                        </>
                      )}
                      <td className="px-2 py-2 text-center font-mono text-muted-foreground font-semibold">
                        {allAwaySkaters.reduce((sum, p) => sum + Number(p.pim ?? p.pim_total ?? 0), 0)}
                      </td>
                      {hasTracking && (
                        <>
                          {hasShifts && (
                            <>
                              <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">-</td>
                              <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">-</td>
                            </>
                          )}
                          <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">-</td>
                          {hasEvents && (
                            <>
                              <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">-</td>
                              <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">-</td>
                              <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">-</td>
                            </>
                          )}
                        </>
                      )}
                    </tr>
                  )
                })()}
                
                {/* Home Team Totals */}
                {(homeForwards.length > 0 || homeDefense.length > 0) && (() => {
                  const allHomeSkaters = [...homeForwards, ...homeDefense]
                  const playersWithRatings = allHomeSkaters.filter(p => {
                    const playerInfo = playersMap.get(String(p.player_id))
                    const rating = playerInfo?.current_skill_rating
                    return rating != null && rating !== '' && Number(rating) > 0
                  })
                  const avgRating = playersWithRatings.length > 0
                    ? playersWithRatings.reduce((sum, p) => {
                        const playerInfo = playersMap.get(String(p.player_id))
                        return sum + Number(playerInfo?.current_skill_rating || 0)
                      }, 0) / playersWithRatings.length
                    : null

                  return (
                    <tr className="border-b-2 border-border bg-muted/30 font-bold">
                      <td className="px-3 py-2 font-display">
                        {homeTeam?.team_name || game.home_team_name || 'Home'}
                      </td>
                      <td className="px-2 py-2 text-center"></td>
                      <td className="px-2 py-2 text-center font-mono text-sm">
                        {avgRating != null ? Number(avgRating).toFixed(1) : '-'}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-goal font-semibold">
                        {allHomeSkaters.reduce((sum, p) => sum + Number(p.goals ?? 0), 0)}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-assist font-semibold">
                        {allHomeSkaters.reduce((sum, p) => sum + Number(p.assist ?? 0), 0)}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-primary font-semibold">
                        {allHomeSkaters.reduce((sum, p) => sum + Number(p.goals ?? 0) + Number(p.assist ?? 0), 0)}
                      </td>
                      {hasTracking && (
                        <>
                          <td className="px-2 py-2 text-center font-mono text-muted-foreground font-semibold">
                            {allHomeSkaters.reduce((sum, p) => {
                              const advStats = homePlayerStatsMap.get(String(p.player_id))
                              return sum + (Number(advStats?.shots ?? advStats?.sog ?? 0) || 0)
                            }, 0)}
                          </td>
                          <td className="px-2 py-2 text-center font-mono text-muted-foreground font-semibold">
                            {allHomeSkaters.reduce((sum, p) => {
                              const advStats = homePlayerStatsMap.get(String(p.player_id))
                              return sum + (Number(advStats?.plus_minus_total ?? advStats?.plus_minus ?? 0) || 0)
                            }, 0)}
                          </td>
                        </>
                      )}
                      <td className="px-2 py-2 text-center font-mono text-muted-foreground font-semibold">
                        {allHomeSkaters.reduce((sum, p) => sum + Number(p.pim ?? p.pim_total ?? 0), 0)}
                      </td>
                      {hasTracking && (
                        <>
                          {hasShifts && (
                            <>
                              <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">-</td>
                              <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">-</td>
                            </>
                          )}
                          <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">-</td>
                          {hasEvents && (
                            <>
                              <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">-</td>
                              <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">-</td>
                              <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">-</td>
                            </>
                          )}
                        </>
                      )}
                    </tr>
                  )
                })()}
              </tbody>
            </table>
          </div>
        </div>
      )}
      
      {/* Prior Games - Season Results */}
      {(priorGamesData.homeGames.length > 0 || priorGamesData.awayGames.length > 0) && (
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Home Team Prior Games */}
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
                  const teamGoals = isHome ? (priorGame.official_home_goals ?? priorGame.home_total_goals ?? 0) : (priorGame.official_away_goals ?? priorGame.away_total_goals ?? 0)
                  const oppGoals = isHome ? (priorGame.official_away_goals ?? priorGame.away_total_goals ?? 0) : (priorGame.official_home_goals ?? priorGame.home_total_goals ?? 0)
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
          
          {/* Away Team Prior Games */}
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
                  const teamGoals = isHome ? (priorGame.official_home_goals ?? priorGame.home_total_goals ?? 0) : (priorGame.official_away_goals ?? priorGame.away_total_goals ?? 0)
                  const oppGoals = isHome ? (priorGame.official_away_goals ?? priorGame.away_total_goals ?? 0) : (priorGame.official_home_goals ?? priorGame.home_total_goals ?? 0)
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
      
      {/* Tracking Status */}
      {gameTrackingStatus && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Activity className="w-4 h-4" />
              Game Tracking Status
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {/* Status Badge */}
              <div className="flex items-center gap-3">
                <div className={cn(
                  'px-3 py-1.5 rounded-lg font-mono text-sm font-semibold',
                  gameTrackingStatus.status === 'full' && 'bg-save/20 text-save',
                  gameTrackingStatus.status === 'partial' && 'bg-assist/20 text-assist',
                  gameTrackingStatus.status === 'non-full' && 'bg-primary/20 text-primary',
                  gameTrackingStatus.status === 'none' && 'bg-muted text-muted-foreground'
                )}>
                  {gameTrackingStatus.status === 'full' && 'Full Tracking'}
                  {gameTrackingStatus.status === 'partial' && 'Partial Tracking'}
                  {gameTrackingStatus.status === 'non-full' && 'Non-Full Game'}
                  {gameTrackingStatus.status === 'none' && 'No Tracking'}
                </div>
                {gameTrackingStatus.coverage && (
                  <div className="text-xs font-mono text-muted-foreground">
                    {gameTrackingStatus.coverage}
                  </div>
                )}
              </div>
              
              {/* Components Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Events</div>
                  <div className={cn(
                    'font-mono text-sm font-semibold',
                    gameTrackingStatus.hasEvents ? 'text-foreground' : 'text-muted-foreground'
                  )}>
                    {gameTrackingStatus.hasEvents ? gameTrackingStatus.eventCount.toLocaleString() : 'None'}
                  </div>
                </div>
                <div>
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Shifts</div>
                  <div className={cn(
                    'font-mono text-sm font-semibold',
                    gameTrackingStatus.hasShifts ? 'text-foreground' : 'text-muted-foreground'
                  )}>
                    {gameTrackingStatus.hasShifts ? gameTrackingStatus.shiftCount.toLocaleString() : 'None'}
                  </div>
                </div>
                <div>
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-1">XY Data</div>
                  <div className={cn(
                    'font-mono text-sm font-semibold',
                    gameTrackingStatus.hasXY ? 'text-foreground' : 'text-muted-foreground'
                  )}>
                    {gameTrackingStatus.hasXY ? gameTrackingStatus.xyCount.toLocaleString() : 'None'}
                  </div>
                </div>
                <div>
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Video</div>
                  <div className={cn(
                    'font-mono text-sm font-semibold',
                    gameTrackingStatus.hasVideo ? 'text-foreground' : 'text-muted-foreground'
                  )}>
                    {gameTrackingStatus.hasVideo ? 'Available' : 'None'}
                  </div>
                </div>
              </div>
              
              {/* Missing Components */}
              {gameTrackingStatus.missing.length > 0 && (
                <div className="pt-2 border-t border-border">
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Missing Components</div>
                  <div className="text-sm text-muted-foreground">
                    {gameTrackingStatus.missing.join(', ')}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      
      {/* Game Highlights */}
      {highlights && highlights.length > 0 && (
        <GameHighlights
          highlights={highlights}
          homeTeam={homeTeam || undefined}
          awayTeam={awayTeam || undefined}
          gameId={gameIdNum}
          gameVideoUrl={game.video_url_1 || game.video_url_2 || null}
          gameVideoStartOffset={game.video_start_offset || 0}
        />
      )}

      {/* Play-by-Play Timeline - Only show if we have events */}
      {hasEvents && (
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
        />
      )}

      {/* Shift Chart - Only show if we have shifts */}
      {hasShifts && shiftsData && shiftsData.length > 0 && (
        <ShiftChart shifts={shiftsData} />
      )}

      {/* Enhanced Shot Map - Only show if we have XY data */}
      {hasXY && shots && shots.length > 0 && (
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
      )}
    </div>
  )
}
