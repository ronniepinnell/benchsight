// src/app/(dashboard)/games/[gameId]/page.tsx
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getGameFromSchedule, getGameRoster, getGameGoals, getGameGoalieStats, getGameShots } from '@/lib/supabase/queries/games'
import { createClient } from '@/lib/supabase/server'
import { getTeamById } from '@/lib/supabase/queries/teams'
import { getPlayers } from '@/lib/supabase/queries/players'
import { ArrowLeft, Target, User, TrendingUp, Activity, BarChart3, Shield, Zap } from 'lucide-react'
import { cn } from '@/lib/utils'
import { TeamLogo } from '@/components/teams/team-logo'
import { PlayerPhoto } from '@/components/players/player-photo'
import { ShotHeatmap } from '@/components/charts/shot-heatmap'
import { StatCard, StatRow } from '@/components/players/stat-card'
import { GameHighlights } from '@/components/games/game-highlights'
import { GameSummary } from '@/components/games/game-summary'
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
  const [roster, goals, players, goalieStats, shots, gameEventsResult, gameStatusResult] = await Promise.allSettled([
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
    supabase
      .from('fact_game_status')
      .select('*')
      .eq('game_id', gameIdNum)
      .maybeSingle()
  ])
  
  // Extract results with error handling
  const rosterData = roster.status === 'fulfilled' ? roster.value : []
  const goalsData = goals.status === 'fulfilled' ? goals.value : []
  const playersData = players.status === 'fulfilled' ? players.value : []
  const goalieStatsData = goalieStats.status === 'fulfilled' ? goalieStats.value : []
  const shotsData = shots.status === 'fulfilled' ? shots.value : []
  
  // Handle game events result
  const gameEvents = gameEventsResult.status === 'fulfilled' && !gameEventsResult.value.error
    ? gameEventsResult.value
    : { data: [] }
  
  // Handle game status result
  let gameStatus: { data: any; error?: any } | null = null
  if (gameStatusResult.status === 'fulfilled') {
    const result = gameStatusResult.value
    if (result.error && result.error.code !== 'PGRST116') {
      // PGRST116 is "not found" which is OK, log other errors
      console.error(`Error fetching game status for game ${gameIdNum}:`, result.error)
    } else if (!result.error) {
      gameStatus = result
    }
  } else {
    console.error('Error fetching game status:', gameStatusResult.reason)
  }
  
  // Log any rejected promises for debugging
  const rejected = [roster, goals, players, goalieStats, shots, gameEventsResult, gameStatusResult]
    .filter((p) => p.status === 'rejected')
  if (rejected.length > 0) {
    console.warn(`Some data failed to load for game ${gameIdNum}:`, rejected.map((r) => 
      r.status === 'rejected' ? r.reason : null
    ))
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
  
  // Get tracking status from fact_game_status
  const trackingStatus = gameStatus?.data as { tracking_status?: string; tracking_pct?: number; events_row_count?: number; goal_events?: number } | null
  const hasVideo = trackingStatus?.tracking_status === 'Complete' || trackingStatus?.tracking_status === 'Partial'
  
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
  goalsData.forEach((goal: GameEvent) => {
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
    if (r.team_venue === 'Home' || r.team_name === game.home_team_name) {
      homeRoster.push(r)
    } else if (r.team_venue === 'Away' || r.team_name === game.away_team_name) {
      awayRoster.push(r)
    }
  })
  
  // Separate players and goalies (goalies have position 'G' or goals_against > 0)
  // Performance: Single pass per roster
  const homePlayers: Array<Record<string, any>> = []
  const homeGoalies: Array<Record<string, any>> = []
  const awayPlayers: Array<Record<string, any>> = []
  const awayGoalies: Array<Record<string, any>> = []
  
  homeRoster.forEach((r: Record<string, any>) => {
    const pos = (r.player_position || '').toUpperCase()
    if (pos === 'G' || r.goals_against) {
      homeGoalies.push(r)
    } else {
      homePlayers.push(r)
    }
  })
  
  awayRoster.forEach((r: Record<string, any>) => {
    const pos = (r.player_position || '').toUpperCase()
    if (pos === 'G' || r.goals_against) {
      awayGoalies.push(r)
    } else {
      awayPlayers.push(r)
    }
  })
  
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
  
  return (
    <div className="space-y-6">
      {/* Back Link */}
      <Link 
        href="/games" 
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Games
      </Link>
      
      {/* Scoreboard */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="bg-gradient-to-r from-primary/10 via-transparent to-primary/10 p-6">
          <div className="flex items-center justify-between">
            {/* Away Team */}
            <div className="flex-1 text-center">
              <div className="flex items-center justify-center gap-3 mb-2">
                {awayTeam && (
                  <TeamLogo
                    src={awayTeam.team_logo || null}
                    name={awayTeam.team_name || game.away_team_name || ''}
                    abbrev={awayTeam.team_cd}
                    primaryColor={awayTeam.primary_color || awayTeam.team_color1}
                    secondaryColor={awayTeam.team_color2}
                    size="lg"
                  />
                )}
                <div>
                  <div className="font-display text-lg font-semibold text-foreground">
                    {game.away_team_name || 'Away'}
                  </div>
                </div>
              </div>
              <div className={cn(
                'font-mono text-4xl font-bold',
                awayGoals > homeGoals ? 'text-save' : 'text-muted-foreground'
              )}>
                {awayGoals}
              </div>
            </div>
            
            {/* VS */}
            <div className="px-6">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">VS</div>
              <div className="text-xs font-mono text-muted-foreground">
                {game.date ? new Date(game.date).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric'
                }) : ''}
              </div>
            </div>
            
            {/* Home Team */}
            <div className="flex-1 text-center">
              <div className="flex items-center justify-center gap-3 mb-2">
                {homeTeam && (
                  <TeamLogo
                    src={homeTeam.team_logo || null}
                    name={homeTeam.team_name || game.home_team_name || ''}
                    abbrev={homeTeam.team_cd}
                    primaryColor={homeTeam.primary_color || homeTeam.team_color1}
                    secondaryColor={homeTeam.team_color2}
                    size="lg"
                  />
                )}
                <div>
                  <div className="font-display text-lg font-semibold text-foreground">
                    {game.home_team_name || 'Home'}
                  </div>
                </div>
              </div>
              <div className={cn(
                'font-mono text-4xl font-bold',
                homeGoals > awayGoals ? 'text-save' : 'text-muted-foreground'
              )}>
                {homeGoals}
              </div>
            </div>
          </div>
        </div>
        
        <div className="px-6 py-3 bg-accent/50 border-t border-border text-center">
          <div className="text-xs font-mono text-muted-foreground uppercase mb-1">
            {game.date ? new Date(game.date).toLocaleDateString('en-US', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric'
            }) : 'Game Date'}
          </div>
          <span className="text-xs font-mono text-muted-foreground uppercase">Final</span>
        </div>
      </div>
      
      {/* Team Advanced Stats Summary */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Home Team Aggregates */}
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <div className="flex items-center gap-2">
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
              <h2 className="font-display text-sm font-semibold uppercase tracking-wider">
                {homeTeam?.team_name || game.home_team_name || 'Home'} Team Stats
              </h2>
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
                <TeamLogo
                  src={awayTeam.team_logo || null}
                  name={awayTeam.team_name || ''}
                  abbrev={awayTeam.team_cd}
                  primaryColor={awayTeam.primary_color || awayTeam.team_color1}
                  secondaryColor={awayTeam.team_color2}
                  size="sm"
                />
              )}
              <h2 className="font-display text-sm font-semibold uppercase tracking-wider">
                {awayTeam?.team_name || game.away_team_name || 'Away'} Team Stats
              </h2>
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
      
      {/* Scoring Summary */}
      {goalsData.length > 0 && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Target className="w-4 h-4 text-goal" />
              Scoring Summary
            </h2>
          </div>
          <div className="divide-y divide-border">
            {goalsData.map((goal: GameEvent, index: number) => {
              const period = goal.period
              const minutes = Math.floor((goal.time_seconds ?? 0) / 60)
              const seconds = (goal.time_seconds ?? 0) % 60
              const timeStr = `${minutes}:${seconds.toString().padStart(2, '0')}`
              
              // Determine which team scored
              const scoringTeamId = String(goal.team_id)
              const scoringTeam = scoringTeamId === String(homeTeamId) ? homeTeam : 
                                 scoringTeamId === String(awayTeamId) ? awayTeam : null
              
              // Get video link for this goal
              const goalVideoTime = goal.running_video_time || goal.time_start_total_seconds
              const goalVideoUrl = goal.video_url || game.video_url_1 || game.video_url_2
              const videoStartOffset = game.video_start_offset || 0
              const videoLink = goalVideoUrl && goalVideoTime 
                ? `${goalVideoUrl}#t=${Math.max(0, (goalVideoTime || 0) - videoStartOffset)}`
                : null
              
              return (
                <div key={index} className="p-4 flex items-center gap-4">
                  <div className="w-16 text-center">
                    <span className="text-xs font-mono text-muted-foreground uppercase">P{period}</span>
                    <div className="font-mono text-sm text-foreground">{timeStr}</div>
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
                  {scoringTeam && (
                    <TeamLogo
                      src={scoringTeam.team_logo || null}
                      name={scoringTeam.team_name || ''}
                      abbrev={scoringTeam.team_cd}
                      primaryColor={scoringTeam.primary_color || scoringTeam.team_color1}
                      secondaryColor={scoringTeam.team_color2}
                      size="xs"
                    />
                  )}
                  <div className="flex-1">
                    {(() => {
                      // Try multiple sources for scorer name/ID
                      // Priority: event_player_ids (player ID) > player_name > event_player_1
                      let scorerName: string | null = null
                      let scorerId: string | null = null
                      
                      // First, try to get player ID from event_player_ids
                      if (goal.event_id && goalEventPlayerIdsMap.has(goal.event_id)) {
                        scorerId = goalEventPlayerIdsMap.get(goal.event_id)!
                        const scorerPlayer = playersMap.get(scorerId)
                        scorerName = scorerPlayer?.player_name || scorerPlayer?.player_full_name || null
                      }
                      
                      // If no ID found, try player_name field (should be scorer for goal events)
                      if (!scorerName && goal.player_name) {
                        scorerName = goal.player_name
                        scorerId = playerNameToIdMap.get(goal.player_name.toLowerCase().trim()) || null
                      }
                      
                      // Fallback to event_player_1
                      if (!scorerName && goal.event_player_1) {
                        scorerName = goal.event_player_1
                        scorerId = playerNameToIdMap.get(goal.event_player_1.toLowerCase().trim()) || null
                      }
                      
                      if (scorerName) {
                        const scorerLink = hasVideo && scorerId
                          ? `/players/${scorerId}/games/${gameIdNum}`
                          : scorerId ? `/players/${scorerId}` : null
                        
                        return scorerLink ? (
                          <Link 
                            href={scorerLink}
                            className="font-display text-sm font-semibold text-foreground hover:text-primary transition-colors"
                          >
                            {scorerName}
                          </Link>
                        ) : (
                          <div className="font-display text-sm font-semibold text-foreground">
                            {scorerName}
                          </div>
                        )
                      }
                      
                      // If we have a player ID but no name, try to get name from playersMap
                      if (scorerId && playersMap.has(scorerId)) {
                        const scorerPlayer = playersMap.get(scorerId)!
                        scorerName = scorerPlayer.player_name || scorerPlayer.player_full_name || 'Unknown Player'
                        const scorerLink = hasVideo
                          ? `/players/${scorerId}/games/${gameIdNum}`
                          : `/players/${scorerId}`
                        return (
                          <Link 
                            href={scorerLink}
                            className="font-display text-sm font-semibold text-foreground hover:text-primary transition-colors"
                          >
                            {scorerName}
                          </Link>
                        )
                      }
                      
                      return (
                        <div className="font-display text-sm font-semibold text-muted-foreground">
                          Unknown Scorer
                        </div>
                      )
                    })()}
                    {(() => {
                      // Get assists from assistEventsMap (if available) or fallback to event_player_2
                      // Try multiple keys to find assists
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
                          <div className="text-xs text-muted-foreground space-y-1">
                            {sortedAssists.map((assist, idx) => {
                              const assistPlayer = playersMap.get(assist.player_id)
                              const assistName = assistPlayer?.player_name || assistPlayer?.player_full_name || assist.player_name || 'Unknown'
                              const assistId = assist.player_id
                              
                              return (
                                <div key={idx}>
                                  {assist.assist_type === 'primary' ? 'A1' : 'A2'}:{' '}
                                  {assistId ? (
                                    <Link 
                                      href={hasVideo 
                                        ? `/players/${assistId}/games/${gameIdNum}`
                                        : `/players/${assistId}`}
                                      className="hover:text-foreground transition-colors"
                                    >
                                      {assistName}
                                    </Link>
                                  ) : (
                                    <span>{assistName}</span>
                                  )}
                                </div>
                              )
                            })}
                          </div>
                        )
                      }
                      
                      // Fallback to event_player_2 if no assist events found
                      if (goal.event_player_2) {
                        const assistId = playerNameToIdMap.get(goal.event_player_2.toLowerCase().trim()) || null
                        return (
                          <div className="text-xs text-muted-foreground">
                            Assist:{' '}
                            {assistId ? (
                              <Link 
                                href={hasVideo 
                                  ? `/players/${assistId}/games/${gameIdNum}`
                                  : `/players/${assistId}`}
                                className="hover:text-foreground transition-colors"
                              >
                                {goal.event_player_2}
                              </Link>
                            ) : (
                              <span>{goal.event_player_2}</span>
                            )}
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
        </div>
      )}
      
      {/* Box Score Tables - Players and Goalies Separated */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Away Team Players */}
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <div className="flex items-center gap-2">
              {awayTeam && (
                <TeamLogo
                  src={awayTeam.team_logo || null}
                  name={awayTeam.team_name || ''}
                  abbrev={awayTeam.team_cd}
                  primaryColor={awayTeam.primary_color || awayTeam.team_color1}
                  secondaryColor={awayTeam.team_color2}
                  size="xs"
                />
              )}
              <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                <User className="w-4 h-4" />
                {awayTeam?.team_name || game.away_team_name || 'Away'} Skaters
              </h2>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-accent/50">
                  <th className="px-3 py-2 text-left font-display text-xs text-muted-foreground">Player</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-goal">G</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-assist">A</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-primary">P</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">S</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">+/-</th>
                  {hasVideo && (
                    <>
                      <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">TOI</th>
                      <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">Shifts</th>
                    </>
                  )}
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">CF%</th>
                  {hasVideo && (
                    <>
                      <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">P</th>
                      <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">GvA</th>
                      <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">TkA</th>
                    </>
                  )}
                </tr>
              </thead>
              <tbody>
                {awayPlayers.slice(0, 20).map((player: any) => {
                  const playerInfo = playersMap.get(String(player.player_id))
                  const advStats = awayPlayerStatsMap.get(String(player.player_id))
                  const goals = Number(player.goals ?? 0)
                  const assists = Number(player.assist ?? 0)
                  const points = goals + assists
                  
                  const playerLink = hasVideo 
                    ? `/players/${player.player_id}/games/${gameIdNum}`
                    : `/players/${player.player_id}`
                  
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
                          <span>{player.player_full_name || player.player_name}</span>
                        </Link>
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-goal">{goals}</td>
                      <td className="px-2 py-2 text-center font-mono text-assist">{assists}</td>
                      <td className="px-2 py-2 text-center font-mono font-semibold">{points}</td>
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
                      {hasVideo && (
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
                      {hasVideo && (
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
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
        
        {/* Home Team Players */}
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <div className="flex items-center gap-2">
              {homeTeam && (
                <TeamLogo
                  src={homeTeam.team_logo || null}
                  name={homeTeam.team_name || ''}
                  abbrev={homeTeam.team_cd}
                  primaryColor={homeTeam.primary_color || homeTeam.team_color1}
                  secondaryColor={homeTeam.team_color2}
                  size="xs"
                />
              )}
              <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                <User className="w-4 h-4" />
                {homeTeam?.team_name || game.home_team_name || 'Home'} Skaters
              </h2>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-accent/50">
                  <th className="px-3 py-2 text-left font-display text-xs text-muted-foreground">Player</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-goal">G</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-assist">A</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-primary">P</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">S</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">+/-</th>
                  {hasVideo && (
                    <>
                      <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">TOI</th>
                      <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">Shifts</th>
                    </>
                  )}
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">CF%</th>
                  {hasVideo && (
                    <>
                      <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">P</th>
                      <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">GvA</th>
                      <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">TkA</th>
                    </>
                  )}
                </tr>
              </thead>
              <tbody>
                {homePlayers.slice(0, 20).map((player: any) => {
                  const playerInfo = playersMap.get(String(player.player_id))
                  const advStats = homePlayerStatsMap.get(String(player.player_id))
                  const goals = Number(player.goals ?? 0)
                  const assists = Number(player.assist ?? 0)
                  const points = goals + assists
                  
                  const playerLink = hasVideo 
                    ? `/players/${player.player_id}/games/${gameIdNum}`
                    : `/players/${player.player_id}`
                  
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
                          <span>{player.player_full_name || player.player_name}</span>
                        </Link>
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-goal">{goals}</td>
                      <td className="px-2 py-2 text-center font-mono text-assist">{assists}</td>
                      <td className="px-2 py-2 text-center font-mono font-semibold">{points}</td>
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
                      {hasVideo && (
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
                      {hasVideo && (
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
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
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
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-accent/50">
                  <th className="px-3 py-2 text-left font-display text-xs text-muted-foreground">Goalie</th>
                  <th className="px-3 py-2 text-left font-display text-xs text-muted-foreground">Team</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-save">Saves</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-goal">GA</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">Shots</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-primary">SV%</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">GAA</th>
                </tr>
              </thead>
              <tbody>
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
                  
                  return Array.from(goalieMap.values())
                })().map((goalie: any) => {
                  const goalieInfo = playersMap.get(String(goalie.player_id))
                  const goalieTeamId = String(goalie.team_id || '')
                  const goalieTeam = goalieTeamId === String(homeTeamId) ? homeTeam : 
                                     goalieTeamId === String(awayTeamId) ? awayTeam : null
                  
                  const saves = Number(goalie.saves ?? goalie.sv ?? 0)
                  const goalsAgainst = Number(goalie.goals_against ?? goalie.ga ?? 0)
                  const shotsAgainst = Number(goalie.shots_against ?? goalie.sa ?? saves + goalsAgainst)
                  const savePct = shotsAgainst > 0 ? (saves / shotsAgainst) * 100 : 0
                  const toiMinutes = goalie.toi_seconds ? Number(goalie.toi_seconds) / 60 : 60 // Default to 60 if unknown
                  const gaa = toiMinutes > 0 ? (goalsAgainst / toiMinutes) * 60 : 0
                  
                  return (
                    <tr key={goalie.goalie_game_key || goalie.player_game_id || goalie.player_id} className="border-b border-border hover:bg-muted/50">
                      <td className="px-3 py-2">
                        <Link 
                          href={hasVideo 
                            ? `/players/${goalie.player_id}/games/${gameIdNum}`
                            : `/players/${goalie.player_id}`} 
                          className="flex items-center gap-2 text-foreground hover:text-primary transition-colors"
                        >
                          <PlayerPhoto
                            src={goalieInfo?.player_image || null}
                            name={goalie.player_name || goalie.player_full_name || ''}
                            primaryColor={goalieTeam?.primary_color || goalieTeam?.team_color1}
                            size="sm"
                          />
                          <span>{goalie.player_name || goalie.player_full_name}</span>
                        </Link>
                      </td>
                      <td className="px-3 py-2">
                        {goalieTeam && (
                          <Link 
                            href={`/team/${(goalieTeam.team_name || '').replace(/\s+/g, '_')}`}
                            className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
                          >
                            <TeamLogo
                              src={goalieTeam.team_logo || null}
                              name={goalieTeam.team_name || ''}
                              abbrev={goalieTeam.team_cd}
                              primaryColor={goalieTeam.primary_color || goalieTeam.team_color1}
                              secondaryColor={goalieTeam.team_color2}
                              size="xs"
                            />
                            <span>{goalie.team_name || goalieTeam.team_name}</span>
                          </Link>
                        )}
                        {!goalieTeam && <span className="text-muted-foreground">{goalie.team_name}</span>}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-save font-semibold">{saves}</td>
                      <td className="px-2 py-2 text-center font-mono text-goal">{goalsAgainst}</td>
                      <td className="px-2 py-2 text-center font-mono text-muted-foreground">{shotsAgainst}</td>
                      <td className="px-2 py-2 text-center font-mono text-primary font-semibold">
                        {savePct > 0 ? savePct.toFixed(1) + '%' : '-'}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                        {gaa > 0 ? gaa.toFixed(2) : '-'}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
      
      {/* Tracking Status */}
      {(trackingStatus || gameStatusResult.error) && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Activity className="w-4 h-4" />
              Game Tracking Status
            </h2>
          </div>
          <div className="p-6">
            {gameStatusResult.error ? (
              <div className="text-sm text-muted-foreground">
                <p className="font-mono text-xs text-destructive mb-2">Error loading tracking status:</p>
                <p className="text-xs font-mono bg-muted p-2 rounded">{String(gameStatusResult.error.message || gameStatusResult.error)}</p>
              </div>
            ) : trackingStatus ? (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Status</div>
                  <div className={cn(
                    'font-mono text-sm font-semibold',
                    trackingStatus.tracking_status === 'Complete' && 'text-save',
                    trackingStatus.tracking_status === 'Partial' && 'text-primary',
                    (!trackingStatus.tracking_status || trackingStatus.tracking_status === 'Not Tracked') && 'text-muted-foreground'
                  )}>
                    {trackingStatus.tracking_status || 'Not Tracked'}
                  </div>
                </div>
              {trackingStatus.tracking_pct && (
                <div>
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Tracked</div>
                  <div className="font-mono text-sm font-semibold text-primary">
                    {trackingStatus.tracking_pct}%
                  </div>
                </div>
              )}
              {trackingStatus.events_row_count && (
                <div>
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Events</div>
                  <div className="font-mono text-sm font-semibold text-foreground">
                    {trackingStatus.events_row_count}
                  </div>
                </div>
              )}
                {trackingStatus.goal_events && (
                  <div>
                    <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Goals</div>
                    <div className="font-mono text-sm font-semibold text-goal">
                      {trackingStatus.goal_events}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-sm text-muted-foreground">
                No tracking status available for this game.
              </div>
            )}
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
      
      {/* Shot Heatmap */}
      {shots && shots.length > 0 && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              Shot Chart
            </h2>
          </div>
          <div className="p-6">
            <ShotHeatmap shots={shotsData} showGoals={true} showXG={true} />
          </div>
        </div>
      )}
    </div>
  )
}
