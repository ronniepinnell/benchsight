// lib/utils/game-data.ts
// Extracted data processing logic for game detail page

import type { DimPlayer, DimTeam, FactPlayerGameStats } from '@/types/database'

// ============================================================================
// Types
// ============================================================================

export interface TeamAggregates {
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

export interface ProcessedRoster {
  homeRoster: Record<string, any>[]
  awayRoster: Record<string, any>[]
  homeForwards: Record<string, any>[]
  homeDefense: Record<string, any>[]
  homeGoalies: Record<string, any>[]
  awayForwards: Record<string, any>[]
  awayDefense: Record<string, any>[]
  awayGoalies: Record<string, any>[]
  homePlayers: Record<string, any>[]
  awayPlayers: Record<string, any>[]
}

export interface TopPerformer {
  player_id: string
  player_name: string
  goals: number
  assists: number
  points: number
}

export interface ThreeStar {
  player_id: string
  player_name: string
  player_image: string | null
  team_name: string | undefined
  team_id: string
  team_logo: string | null
  team_cd: string | undefined
  primary_color: string | undefined
  goals: number
  assists: number
  points: number
  position: string | undefined
}

export interface AssistInfo {
  player_id: string
  player_name: string
  assist_type: 'primary' | 'secondary'
}

export interface GameEvent {
  event_id?: string
  period?: number
  time_start_total_seconds?: number
  time_seconds?: number
  time_remaining?: string
  period_time?: string
  event_start_min?: number
  event_start_sec?: number
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
  running_video_time?: number
}

// ============================================================================
// Calculation Helpers
// ============================================================================

/**
 * Calculate team aggregates from player stats list
 */
export function calculateTeamAggregates(
  playerStatsList: (FactPlayerGameStats | Record<string, any>)[]
): TeamAggregates {
  return playerStatsList.reduce<TeamAggregates>(
    (acc, stat) => {
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
        badGiveaways:
          (acc.badGiveaways || 0) +
          (Number(stat.bad_giveaways ?? statAny.bad_give ?? 0) || 0),
        toi: (acc.toi || 0) + (Number(stat.toi_seconds ?? 0) || 0),
      }
    },
    {
      cf: 0,
      ca: 0,
      ff: 0,
      fa: 0,
      goals: 0,
      assists: 0,
      points: 0,
      shots: 0,
      hits: 0,
      blocks: 0,
      takeaways: 0,
      badGiveaways: 0,
      toi: 0,
    }
  )
}

/**
 * Calculate percentage (for CF%, FF%, etc.)
 */
export function calculatePercentage(forValue: number, againstValue: number): number {
  const total = forValue + againstValue
  return total > 0 ? (forValue / total) * 100 : 0
}

// ============================================================================
// Player Maps
// ============================================================================

/**
 * Build player lookup maps from players data
 */
export function buildPlayerMaps(playersData: DimPlayer[]): {
  playersMap: Map<string, DimPlayer>
  playerNameToIdMap: Map<string, string>
} {
  // Create players map for photos (optimized - single pass)
  const playersMap = new Map<string, DimPlayer>(
    playersData.map((p) => [String(p.player_id), p])
  )

  // Create name-to-ID map for goal scorers (multiple name variations)
  const playerNameToIdMap = new Map<string, string>()
  playersData.forEach((p: DimPlayer) => {
    if (p.player_name) {
      const nameLower = p.player_name.toLowerCase().trim()
      playerNameToIdMap.set(nameLower, String(p.player_id))
      // Also add "Last, First" format if it's "First Last"
      const parts = p.player_name.trim().split(/\s+/)
      if (parts.length === 2) {
        playerNameToIdMap.set(
          `${parts[1]}, ${parts[0]}`.toLowerCase(),
          String(p.player_id)
        )
      }
    }
    if (p.player_full_name) {
      const fullNameLower = p.player_full_name.toLowerCase().trim()
      playerNameToIdMap.set(fullNameLower, String(p.player_id))
      // Also add "Last, First" format if it's "First Last"
      const parts = p.player_full_name.trim().split(/\s+/)
      if (parts.length === 2) {
        playerNameToIdMap.set(
          `${parts[1]}, ${parts[0]}`.toLowerCase(),
          String(p.player_id)
        )
      }
    }
  })

  return { playersMap, playerNameToIdMap }
}

// ============================================================================
// Roster Processing
// ============================================================================

/**
 * Process roster data into home/away teams with position splits
 */
export function processRoster(
  rosterData: Record<string, any>[],
  game: { home_team_id?: string | number; away_team_id?: string | number; home_team_name?: string; away_team_name?: string },
  playersMap: Map<string, DimPlayer>
): ProcessedRoster {
  const homeRoster: Record<string, any>[] = []
  const awayRoster: Record<string, any>[] = []

  const homeTeamId = String(game.home_team_id || '').trim()
  const awayTeamId = String(game.away_team_id || '').trim()
  const homeTeamName = String(game.home_team_name || '').trim()
  const awayTeamName = String(game.away_team_name || '').trim()

  rosterData.forEach((r: Record<string, any>) => {
    const teamVenue = String(r.team_venue || '').trim()
    const teamName = String(r.team_name || '').trim()
    const rosterTeamId = String(r.team_id || '').trim()

    // Match by team_id first (most reliable), then team_venue, then team_name
    const isHome =
      rosterTeamId === homeTeamId ||
      teamVenue === 'Home' ||
      teamName === homeTeamName ||
      (teamVenue === '' && teamName === '' && rosterTeamId === homeTeamId)

    const isAway =
      rosterTeamId === awayTeamId ||
      teamVenue === 'Away' ||
      teamName === awayTeamName ||
      (teamVenue === '' && teamName === '' && rosterTeamId === awayTeamId)

    if (isHome) {
      homeRoster.push(r)
    } else if (isAway) {
      awayRoster.push(r)
    } else if (process.env.NODE_ENV === 'development') {
      console.warn('Unmatched roster entry:', {
        team_venue: teamVenue,
        team_name: teamName,
        team_id: rosterTeamId,
        home_team_id: homeTeamId,
        away_team_id: awayTeamId,
        player_name: r.player_name || r.player_full_name,
      })
    }
  })

  // Helper to check if position is defense
  const isDefensePosition = (pos: string): boolean => {
    const p = pos.toUpperCase()
    return p === 'D' || p === 'LD' || p === 'RD' || p === 'DEF' || p === 'DEFENSE'
  }

  // Helper to check if position is goalie
  const isGoaliePosition = (pos: string): boolean => {
    const p = pos.toUpperCase()
    return p === 'G' || p.includes('GOALIE')
  }

  // Separate players and goalies, then separate forwards and defense
  const homeForwards: Record<string, any>[] = []
  const homeDefense: Record<string, any>[] = []
  const homeGoalies: Record<string, any>[] = []
  const awayForwards: Record<string, any>[] = []
  const awayDefense: Record<string, any>[] = []
  const awayGoalies: Record<string, any>[] = []

  const categorizePlayer = (
    r: Record<string, any>,
    forwards: Record<string, any>[],
    defense: Record<string, any>[],
    goalies: Record<string, any>[]
  ) => {
    const gamePos = String(r.player_position || '').trim()
    const playerId = String(r.player_id || '')
    const playerInfo = playersMap.get(playerId)
    const primaryPos = String(playerInfo?.player_primary_position || '').trim()

    // Check if goalie
    if (isGoaliePosition(gamePos) || isGoaliePosition(primaryPos) || r.goals_against) {
      goalies.push(r)
    } else if (isDefensePosition(gamePos) || isDefensePosition(primaryPos)) {
      defense.push(r)
    } else {
      forwards.push(r)
    }
  }

  homeRoster.forEach((r) => categorizePlayer(r, homeForwards, homeDefense, homeGoalies))
  awayRoster.forEach((r) => categorizePlayer(r, awayForwards, awayDefense, awayGoalies))

  return {
    homeRoster,
    awayRoster,
    homeForwards,
    homeDefense,
    homeGoalies,
    awayForwards,
    awayDefense,
    awayGoalies,
    homePlayers: [...homeForwards, ...homeDefense],
    awayPlayers: [...awayForwards, ...awayDefense],
  }
}

/**
 * Pad arrays to equal length for aligned table display
 */
export function padArray<T>(arr: T[], targetLength: number): (T | null)[] {
  const padded: (T | null)[] = [...arr]
  while (padded.length < targetLength) {
    padded.push(null)
  }
  return padded
}

// ============================================================================
// Stats Processing
// ============================================================================

/**
 * Filter player stats by team
 */
export function filterStatsByTeam(
  allPlayerStats: Record<string, any>[],
  teamId: string | number | undefined,
  teamName: string | undefined,
  venue: 'Home' | 'Away'
): Record<string, any>[] {
  const teamIdStr = teamId ? String(teamId) : ''
  const teamNameStr = teamName || ''

  return allPlayerStats.filter((stat: any) => {
    const statTeamId = String(stat.team_id || '')
    const statTeamName = stat.team_name || ''

    return (
      statTeamId === teamIdStr ||
      statTeamName === teamNameStr ||
      (stat.team_venue === venue && statTeamName)
    )
  })
}

/**
 * Get top performers by points
 */
export function getTopPerformers(
  playerStatsList: Record<string, any>[],
  limit: number = 5
): TopPerformer[] {
  return playerStatsList
    .map((stat: any) => ({
      player_id: String(stat.player_id),
      player_name: stat.player_name || stat.player_full_name || '',
      goals: Number(stat.goals ?? stat.g ?? 0),
      assists: Number(stat.assists ?? stat.a ?? 0),
      points: Number(
        stat.points ??
          stat.pts ??
          Number(stat.goals ?? stat.g ?? 0) + Number(stat.assists ?? stat.a ?? 0)
      ),
    }))
    .sort((a, b) => b.points - a.points || b.goals - a.goals)
    .slice(0, limit)
}

/**
 * Calculate three stars of the game
 */
export function calculateThreeStars(
  homePlayerStatsList: Record<string, any>[],
  awayPlayerStatsList: Record<string, any>[],
  game: { home_team_name?: string; away_team_name?: string },
  homeTeamId: string | number | undefined,
  awayTeamId: string | number | undefined,
  homeTeam: DimTeam | null,
  awayTeam: DimTeam | null,
  playerImageMap: Map<string, string | null>
): ThreeStar[] {
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
      points: Number(
        stat.points ??
          stat.pts ??
          Number(stat.goals ?? stat.g ?? 0) + Number(stat.assists ?? stat.a ?? 0)
      ),
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
      points: Number(
        stat.points ??
          stat.pts ??
          Number(stat.goals ?? stat.g ?? 0) + Number(stat.assists ?? stat.a ?? 0)
      ),
      position: stat.position || stat.player_position,
    })),
  ]
    .sort((a, b) => b.points - a.points || b.goals - a.goals)
    .slice(0, 3)

  return allPlayerPerformers
}

/**
 * Create player stats map for quick lookup
 */
export function createPlayerStatsMap(
  statsList: (FactPlayerGameStats | Record<string, any>)[]
): Map<string, FactPlayerGameStats | Record<string, any>> {
  return new Map(statsList.map((s) => [String(s.player_id), s]))
}

// ============================================================================
// Assist Processing
// ============================================================================

/**
 * Process assist events and map them to goals
 */
export function processAssists(
  goalsData: GameEvent[],
  allAssistEvents: GameEvent[]
): Map<string, AssistInfo[]> {
  const assistEventsMap = new Map<string, AssistInfo[]>()

  if (goalsData.length === 0 || allAssistEvents.length === 0) {
    return assistEventsMap
  }

  // Filter to events with assist indicators
  const assistCandidates = allAssistEvents.filter((e: GameEvent) => {
    const pd1 = (e.play_detail1 || '').toLowerCase()
    const pd2 = (e.play_detail_2 || '').toLowerCase()
    return (
      pd1.includes('assistprimary') ||
      pd1.includes('assistsecondary') ||
      pd2.includes('assistprimary') ||
      pd2.includes('assistsecondary')
    )
  })

  // Group assists by goal event
  goalsData.forEach((goal: GameEvent, goalIndex: number) => {
    const assists: AssistInfo[] = []

    assistCandidates.forEach((assistEvent: GameEvent) => {
      // Check if this assist event is in the same sequence/play as the goal
      const sameSequence =
        goal.sequence_key && assistEvent.sequence_key === goal.sequence_key
      const samePlay = goal.play_key && assistEvent.play_key === goal.play_key
      const linkedToGoal =
        goal.linked_event_key &&
        assistEvent.linked_event_key === goal.linked_event_key
      // Also check if assist happens within 10 seconds before goal
      const timeDiff =
        goal.time_start_total_seconds && assistEvent.time_start_total_seconds
          ? goal.time_start_total_seconds - assistEvent.time_start_total_seconds
          : null
      const timeRelated = timeDiff !== null && timeDiff > 0 && timeDiff <= 10

      if (sameSequence || samePlay || linkedToGoal || timeRelated) {
        const playDetail1 = (assistEvent.play_detail1 || '').toLowerCase()
        const playDetail2 = (assistEvent.play_detail_2 || '').toLowerCase()

        if (
          playDetail1.includes('assistprimary') ||
          playDetail2.includes('assistprimary')
        ) {
          const playerIds = (assistEvent.event_player_ids || '')
            .split(',')
            .map((id: string) => id.trim())
            .filter(Boolean)
          if (playerIds.length > 0) {
            assists.push({
              player_id: playerIds[0],
              player_name: assistEvent.player_name || '',
              assist_type: 'primary',
            })
          }
        } else if (
          playDetail1.includes('assistsecondary') ||
          playDetail2.includes('assistsecondary')
        ) {
          const playerIds = (assistEvent.event_player_ids || '')
            .split(',')
            .map((id: string) => id.trim())
            .filter(Boolean)
          if (playerIds.length > 0) {
            assists.push({
              player_id: playerIds[0],
              player_name: assistEvent.player_name || '',
              assist_type: 'secondary',
            })
          }
        }
      }
    })

    // Remove duplicates by player_id
    const uniqueAssists = assists.filter(
      (assist, idx, self) =>
        idx === self.findIndex((a) => a.player_id === assist.player_id)
    )

    if (uniqueAssists.length > 0) {
      assistEventsMap.set(
        goal.event_id || String(goal.time_start_total_seconds || goalIndex),
        uniqueAssists
      )
    }
  })

  return assistEventsMap
}

// ============================================================================
// Highlight Processing
// ============================================================================

export interface EnhancedHighlight extends GameEvent {
  period_time: string
  event_time: string
}

/**
 * Enhance highlights with period/time info
 */
export function enhanceHighlights(highlightsRaw: GameEvent[]): EnhancedHighlight[] {
  return highlightsRaw.map((event: GameEvent) => {
    const period = event.period || 1
    const timeSeconds = event.time_start_total_seconds || event.time_seconds || 0
    const periodTime = event.time_remaining || event.period_time
    const minutes = Math.floor(timeSeconds / 60) % 20
    const seconds = timeSeconds % 60
    const timeStr = periodTime || `${minutes}:${seconds.toString().padStart(2, '0')}`

    return {
      ...event,
      period_time: timeStr,
      event_time: `${periodTime || timeStr} (P${period})`,
    }
  })
}
