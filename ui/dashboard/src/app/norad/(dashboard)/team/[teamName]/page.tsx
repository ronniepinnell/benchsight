// src/app/(dashboard)/team/[teamName]/page.tsx
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getTeamByName, getTeamById, getStandings } from '@/lib/supabase/queries/teams'
import { getRecentGames } from '@/lib/supabase/queries/games'
import { getPlayers } from '@/lib/supabase/queries/players'
import { createClient } from '@/lib/supabase/server'
import { ArrowLeft, Users, Trophy, Calendar, TrendingUp, Target, Activity, BarChart3, Award } from 'lucide-react'
import { cn } from '@/lib/utils'
import { TeamLogo } from '@/components/teams/team-logo'
import { PlayerPhoto } from '@/components/players/player-photo'
import { SeasonSelector } from '@/components/teams/season-selector'
import { StatCard, StatRow } from '@/components/players/stat-card'
import { TeamLinesTab } from '@/components/teams/team-lines-tab'
import { TeamAnalyticsTab } from '@/components/teams/team-analytics-tab'
import { TeamMatchupsTab } from '@/components/teams/team-matchups-tab'
import { SortableRosterTable } from '@/components/teams/sortable-roster-table'
import { SortableGoalieRosterTable } from '@/components/teams/sortable-goalie-roster-table'

// Team Advanced Stats Section Component
async function TeamAdvancedStatsSection({ 
  teamId, 
  teamName, 
  seasonId, 
  gameType 
}: { 
  teamId: string
  teamName: string
  seasonId: string
  gameType: string
}) {
  const supabase = await createClient()
  
  // Fetch all advanced stats in parallel
  const [
    possessionStats,
    specialTeamsStats,
    zoneStats,
    warStats,
    physicalStats,
    shootingStats
  ] = await Promise.all([
    // Possession stats
    supabase
      .from('fact_team_game_stats')
      .select('corsi_for, corsi_against, fenwick_for, fenwick_against, xg_for, goals')
      .eq('team_id', teamId)
      .eq('season_id', seasonId)
      .eq('game_type', gameType === 'All' ? 'All' : gameType)
      .then(({ data }) => {
        if (!data || data.length === 0) return null
        const totals = data.reduce((acc, stat) => ({
          cf: (acc.cf || 0) + (stat.corsi_for || 0),
          ca: (acc.ca || 0) + (stat.corsi_against || 0),
          ff: (acc.ff || 0) + (stat.fenwick_for || 0),
          fa: (acc.fa || 0) + (stat.fenwick_against || 0),
          xg: (acc.xg || 0) + (stat.xg_for || 0),
          goals: (acc.goals || 0) + (stat.goals || 0),
        }), { cf: 0, ca: 0, ff: 0, fa: 0, xg: 0, goals: 0 })
        const cfPct = totals.cf + totals.ca > 0 ? (totals.cf / (totals.cf + totals.ca)) * 100 : 0
        const ffPct = totals.ff + totals.fa > 0 ? (totals.ff / (totals.ff + totals.fa)) * 100 : 0
        return { ...totals, cfPct, ffPct, xgDiff: totals.goals - totals.xg }
      }),
    
    // Special teams
    supabase
      .from('dim_schedule')
      .select('home_team_id, away_team_id, home_pp_goals, away_pp_goals, home_pp_opportunities, away_pp_opportunities, home_pk_goals_against, away_pk_goals_against, home_pk_opportunities, away_pk_opportunities')
      .or(`home_team_id.eq.${teamId},away_team_id.eq.${teamId}`)
      .eq('season_id', seasonId)
      .then(({ data }) => {
        if (!data || data.length === 0) return null
        const totals = data.reduce((acc, game) => {
          const isHome = game.home_team_id === teamId
          return {
            ppGoals: acc.ppGoals + (isHome ? (game.home_pp_goals || 0) : (game.away_pp_goals || 0)),
            ppOpps: acc.ppOpps + (isHome ? (game.home_pp_opportunities || 0) : (game.away_pp_opportunities || 0)),
            pkGoalsAgainst: acc.pkGoalsAgainst + (isHome ? (game.home_pk_goals_against || 0) : (game.away_pk_goals_against || 0)),
            pkOpps: acc.pkOpps + (isHome ? (game.home_pk_opportunities || 0) : (game.away_pk_opportunities || 0)),
          }
        }, { ppGoals: 0, ppOpps: 0, pkGoalsAgainst: 0, pkOpps: 0 })
        const ppPct = totals.ppOpps > 0 ? (totals.ppGoals / totals.ppOpps) * 100 : 0
        const pkPct = totals.pkOpps > 0 ? ((totals.pkOpps - totals.pkGoalsAgainst) / totals.pkOpps) * 100 : 0
        return { ...totals, ppPct, pkPct }
      }),
    
    // Zone stats
    supabase
      .from('fact_player_game_stats')
      .select('zone_entries, zone_entries_successful, zone_exits, zone_exits_successful')
      .eq('team_id', teamId)
      .eq('season_id', seasonId)
      .eq('game_type', gameType === 'All' ? 'All' : gameType)
      .then(({ data }) => {
        if (!data || data.length === 0) return null
        const totals = data.reduce((acc, stat) => ({
          ze: (acc.ze || 0) + (stat.zone_entries || 0),
          zeSuccess: (acc.zeSuccess || 0) + (stat.zone_entries_successful || 0),
          zx: (acc.zx || 0) + (stat.zone_exits || 0),
          zxSuccess: (acc.zxSuccess || 0) + (stat.zone_exits_successful || 0),
        }), { ze: 0, zeSuccess: 0, zx: 0, zxSuccess: 0 })
        const zePct = totals.ze > 0 ? (totals.zeSuccess / totals.ze) * 100 : 0
        const zxPct = totals.zx > 0 ? (totals.zxSuccess / totals.zx) * 100 : 0
        return { ...totals, zePct, zxPct }
      }),
    
    // WAR/GAR
    supabase
      .from('fact_team_game_stats')
      .select('gar_total, war, avg_game_score, avg_adjusted_rating')
      .eq('team_id', teamId)
      .eq('season_id', seasonId)
      .eq('game_type', gameType === 'All' ? 'All' : gameType)
      .then(({ data }) => {
        if (!data || data.length === 0) return null
        const totals = data.reduce((acc, stat) => ({
          gar: (acc.gar || 0) + (stat.gar_total || 0),
          war: (acc.war || 0) + (stat.war || 0),
          gameScore: (acc.gameScore || 0) + (stat.avg_game_score || 0),
          rating: (acc.rating || 0) + (stat.avg_adjusted_rating || 0),
          games: acc.games + 1,
        }), { gar: 0, war: 0, gameScore: 0, rating: 0, games: 0 })
        return {
          totalGAR: totals.gar.toFixed(1),
          totalWAR: totals.war.toFixed(1),
          avgGameScore: totals.games > 0 ? (totals.gameScore / totals.games).toFixed(2) : '0.00',
          avgRating: totals.games > 0 ? (totals.rating / totals.games).toFixed(1) : '0.0',
        }
      }),
    
    // Physical stats
    supabase
      .from('fact_team_game_stats')
      .select('hits, blocks, giveaways, takeaways')
      .eq('team_id', teamId)
      .eq('season_id', seasonId)
      .eq('game_type', gameType === 'All' ? 'All' : gameType)
      .then(({ data }) => {
        if (!data || data.length === 0) return null
        const totals = data.reduce((acc, stat) => ({
          hits: (acc.hits || 0) + (stat.hits || 0),
          blocks: (acc.blocks || 0) + (stat.blocks || 0),
          badGiveaways: (acc.badGiveaways || 0) + (Number(stat.bad_giveaways ?? stat.bad_give ?? 0) || 0),
          takeaways: (acc.takeaways || 0) + (stat.takeaways || 0),
          games: acc.games + 1,
        }), { hits: 0, blocks: 0, badGiveaways: 0, takeaways: 0, games: 0 })
        return {
          ...totals,
          toDiff: totals.takeaways - totals.badGiveaways,
          giveaways: totals.badGiveaways, // For display
          hitsPerGame: totals.games > 0 ? (totals.hits / totals.games).toFixed(1) : '0.0',
          blocksPerGame: totals.games > 0 ? (totals.blocks / totals.games).toFixed(1) : '0.0',
        }
      }),
    
    // Shooting stats
    supabase
      .from('fact_team_game_stats')
      .select('shots, sog, goals')
      .eq('team_id', teamId)
      .eq('season_id', seasonId)
      .eq('game_type', gameType === 'All' ? 'All' : gameType)
      .then(({ data }) => {
        if (!data || data.length === 0) return null
        const totals = data.reduce((acc, stat) => ({
          shots: (acc.shots || 0) + (stat.shots || 0),
          sog: (acc.sog || 0) + (stat.sog || 0),
          goals: (acc.goals || 0) + (stat.goals || 0),
          games: acc.games + 1,
        }), { shots: 0, sog: 0, goals: 0, games: 0 })
        const shootingPct = totals.sog > 0 ? (totals.goals / totals.sog) * 100 : 0
        const shotAccuracy = totals.shots > 0 ? (totals.sog / totals.shots) * 100 : 0
        return {
          ...totals,
          shootingPct: shootingPct.toFixed(1),
          shotAccuracy: shotAccuracy.toFixed(1),
          shotsPerGame: totals.games > 0 ? (totals.shots / totals.games).toFixed(1) : '0.0',
          sogPerGame: totals.games > 0 ? (totals.sog / totals.games).toFixed(1) : '0.0',
        }
      }),
  ])
  
  // Only show section if we have at least one category of stats
  // Always show the section header, even if some stats are missing
  const hasAnyStats = possessionStats || specialTeamsStats || zoneStats || warStats || physicalStats || shootingStats
  
  if (!hasAnyStats) {
    return (
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="px-4 py-3 bg-accent border-b border-border">
          <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
            <TrendingUp className="w-4 h-4" />
            Advanced Statistics
          </h2>
        </div>
        <div className="p-6">
          <p className="text-sm text-muted-foreground text-center">
            Advanced statistics will appear here once game data is available.
          </p>
        </div>
      </div>
    )
  }
  
  return (
    <div className="bg-card rounded-xl border border-border overflow-hidden">
      <div className="px-4 py-3 bg-accent border-b border-border">
        <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
          <TrendingUp className="w-4 h-4" />
          Advanced Statistics
        </h2>
      </div>
      <div className="p-6">
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Possession Stats */}
          {possessionStats && (
            <StatCard 
              title="Possession" 
              icon={<Activity className="w-4 h-4" />}
              defaultExpanded={true}
            >
              <div className="space-y-1">
                <StatRow 
                  label="CF%" 
                  value={`${possessionStats.cfPct.toFixed(1)}%`}
                  highlight
                  color="primary"
                  description="Corsi For Percentage - Shot attempts for vs against"
                />
                <StatRow 
                  label="FF%" 
                  value={`${possessionStats.ffPct.toFixed(1)}%`}
                  highlight
                  color="primary"
                  description="Fenwick For Percentage - Unblocked shot attempts for vs against"
                />
                <div className="border-t border-border pt-2 mt-2">
                  <StatRow 
                    label="Corsi For" 
                    value={possessionStats.cf}
                    description="Total shot attempts (shots + blocks + misses) for"
                  />
                  <StatRow 
                    label="Corsi Against" 
                    value={possessionStats.ca}
                    description="Total shot attempts against"
                  />
                </div>
                <div className="border-t border-border pt-2 mt-2">
                  <StatRow 
                    label="Fenwick For" 
                    value={possessionStats.ff}
                    description="Unblocked shot attempts for"
                  />
                  <StatRow 
                    label="Fenwick Against" 
                    value={possessionStats.fa}
                    description="Unblocked shot attempts against"
                  />
                </div>
                <div className="border-t border-border pt-2 mt-2">
                  <StatRow 
                    label="Expected Goals" 
                    value={possessionStats.xg.toFixed(2)}
                    description="Expected goals based on shot quality and location"
                  />
                  <StatRow 
                    label="Goals - xG" 
                    value={`${possessionStats.xgDiff > 0 ? '+' : ''}${possessionStats.xgDiff.toFixed(2)}`}
                    highlight
                    color={possessionStats.xgDiff > 0 ? 'save' : 'goal'}
                    description="Difference between actual goals and expected goals"
                  />
                </div>
              </div>
            </StatCard>
          )}
          
          {/* Special Teams */}
          {specialTeamsStats && (
            <StatCard 
              title="Special Teams" 
              icon={<Zap className="w-4 h-4" />}
              defaultExpanded={true}
            >
              <div className="space-y-1">
                <StatRow 
                  label="PP%" 
                  value={`${specialTeamsStats.ppPct.toFixed(1)}%`}
                  highlight
                  color="primary"
                  description="Power play percentage - Goals scored on power play"
                />
                <StatRow 
                  label="PP Goals" 
                  value={specialTeamsStats.ppGoals}
                  color="goal"
                  description="Goals scored on power play"
                />
                <StatRow 
                  label="PP Opportunities" 
                  value={specialTeamsStats.ppOpps}
                  description="Power play opportunities"
                />
                <div className="border-t border-border pt-2 mt-2">
                  <StatRow 
                    label="PK%" 
                    value={`${specialTeamsStats.pkPct.toFixed(1)}%`}
                    highlight
                    color="save"
                    description="Penalty kill percentage - Success rate on penalty kill"
                  />
                  <StatRow 
                    label="PK Goals Against" 
                    value={specialTeamsStats.pkGoalsAgainst}
                    color="goal"
                    description="Goals allowed while shorthanded"
                  />
                  <StatRow 
                    label="PK Opportunities" 
                    value={specialTeamsStats.pkOpps}
                    description="Penalty kill opportunities"
                  />
                </div>
              </div>
            </StatCard>
          )}
          
          {/* Zone Play */}
          {zoneStats && (
            <StatCard 
              title="Zone Play" 
              icon={<Zap className="w-4 h-4" />}
              defaultExpanded={true}
            >
              <div className="space-y-1">
                <StatRow 
                  label="Zone Entry %" 
                  value={`${zoneStats.zePct.toFixed(1)}%`}
                  highlight
                  color="primary"
                  description="Percentage of successful zone entries"
                />
                <StatRow 
                  label="Zone Entries" 
                  value={zoneStats.ze}
                  description="Total zone entry attempts"
                />
                <StatRow 
                  label="Successful Entries" 
                  value={zoneStats.zeSuccess}
                  color="save"
                  description="Zone entries that resulted in possession"
                />
                <div className="border-t border-border pt-2 mt-2">
                  <StatRow 
                    label="Zone Exit %" 
                    value={`${zoneStats.zxPct.toFixed(1)}%`}
                    highlight
                    color="primary"
                    description="Percentage of successful zone exits"
                  />
                  <StatRow 
                    label="Zone Exits" 
                    value={zoneStats.zx}
                    description="Total zone exit attempts"
                  />
                  <StatRow 
                    label="Successful Exits" 
                    value={zoneStats.zxSuccess}
                    color="save"
                    description="Zone exits that maintained possession"
                  />
                </div>
              </div>
            </StatCard>
          )}
          
          {/* WAR/GAR */}
          {warStats && (
            <StatCard 
              title="WAR/GAR" 
              icon={<TrendingUp className="w-4 h-4" />}
              defaultExpanded={true}
            >
              <div className="space-y-1">
                <StatRow 
                  label="Total WAR" 
                  value={warStats.totalWAR}
                  highlight
                  color="primary"
                  description="Wins Above Replacement - Total value added in wins"
                />
                <StatRow 
                  label="Total GAR" 
                  value={warStats.totalGAR}
                  highlight
                  color="primary"
                  description="Goals Above Replacement - Total value added in goals"
                />
                <div className="border-t border-border pt-2 mt-2">
                  <StatRow 
                    label="Avg Game Score" 
                    value={warStats.avgGameScore}
                    description="Average game score across all games"
                  />
                  <StatRow 
                    label="Avg Rating" 
                    value={warStats.avgRating}
                    description="Average player rating per game"
                  />
                </div>
              </div>
            </StatCard>
          )}
          
          {/* Physical */}
          {physicalStats && (
            <StatCard 
              title="Physical" 
              icon={<Shield className="w-4 h-4" />}
              defaultExpanded={true}
            >
              <div className="space-y-1">
                <StatRow 
                  label="Hits" 
                  value={physicalStats.hits}
                  highlight
                  description="Total hits delivered"
                />
                <StatRow 
                  label="Hits/Game" 
                  value={physicalStats.hitsPerGame}
                  description="Average hits per game"
                />
                <StatRow 
                  label="Blocks" 
                  value={physicalStats.blocks}
                  highlight
                  color="save"
                  description="Total shots blocked"
                />
                <StatRow 
                  label="Blocks/Game" 
                  value={physicalStats.blocksPerGame}
                  description="Average blocks per game"
                />
                <div className="border-t border-border pt-2 mt-2">
                  <StatRow 
                    label="Takeaways" 
                    value={physicalStats.takeaways}
                    color="save"
                    description="Puck takeaways"
                  />
                  <StatRow 
                    label="Bad Giveaways" 
                    value={physicalStats.giveaways}
                    color="goal"
                    description="Bad puck giveaways (turnovers)"
                  />
                  <StatRow 
                    label="TO Differential" 
                    value={`${physicalStats.toDiff > 0 ? '+' : ''}${physicalStats.toDiff}`}
                    highlight
                    color={physicalStats.toDiff > 0 ? 'save' : physicalStats.toDiff < 0 ? 'goal' : 'muted'}
                    description="Takeaway minus bad giveaway differential"
                  />
                </div>
              </div>
            </StatCard>
          )}
          
          {/* Shooting */}
          {shootingStats && (
            <StatCard 
              title="Shooting" 
              icon={<BarChart3 className="w-4 h-4" />}
              defaultExpanded={true}
            >
              <div className="space-y-1">
                <StatRow 
                  label="Shooting %" 
                  value={`${shootingStats.shootingPct}%`}
                  highlight
                  color="primary"
                  description="Goals per shot on goal"
                />
                <StatRow 
                  label="Shot Accuracy" 
                  value={`${shootingStats.shotAccuracy}%`}
                  description="Shots on goal per total shot attempts"
                />
                <div className="border-t border-border pt-2 mt-2">
                  <StatRow 
                    label="Total Shots" 
                    value={shootingStats.shots}
                    description="Total shot attempts"
                  />
                  <StatRow 
                    label="Shots on Goal" 
                    value={shootingStats.sog}
                    description="Shots that reached the net"
                  />
                </div>
                <div className="border-t border-border pt-2 mt-2">
                  <StatRow 
                    label="Shots/Game" 
                    value={shootingStats.shotsPerGame}
                    description="Average shot attempts per game"
                  />
                  <StatRow 
                    label="SOG/Game" 
                    value={shootingStats.sogPerGame}
                    description="Average shots on goal per game"
                  />
                </div>
              </div>
            </StatCard>
          )}
        </div>
      </div>
    </div>
  )
}

export const revalidate = 300

export async function generateMetadata({ params }: { params: Promise<{ teamName: string }> }) {
  const { teamName } = await params
  // Convert underscores back to spaces for lookup
  const decodedName = teamName.replace(/_/g, ' ')
  const team = await getTeamByName(decodedName)
    
  return {
    title: team ? `${team.team_name} | BenchSight` : 'Team | BenchSight',
    description: team ? `${team.team_name} team profile and statistics` : 'Team profile',
  }
}

export default async function TeamDetailPage({ 
  params,
  searchParams
}: { 
  params: Promise<{ teamName: string }>
  searchParams: Promise<{ season?: string; gameType?: string; tab?: string }>
}) {
  const { teamName } = await params
  const { season: selectedSeason, gameType: selectedGameType, tab: selectedTab } = await searchParams
  const activeTab = selectedTab || 'overview'
  // Convert underscores back to spaces for lookup
  const decodedName = teamName.replace(/_/g, ' ')
  
  if (!decodedName) {
    notFound()
  }
  
  const supabase = await createClient()
  
  // Fetch team data first
  const [team, standings, players] = await Promise.all([
    getTeamByName(decodedName),
    getStandings(),
    getPlayers()
  ])
  
  if (!team) {
    notFound()
  }
  
  // Get available seasons for this team
  const { data: seasonsData } = await supabase
    .from('fact_team_season_stats_basic')
    .select('season_id, season')
    .eq('team_id', team.team_id)
    .order('season', { ascending: false })
  
  const seasons = seasonsData 
    ? [...new Map(seasonsData.map(s => [s.season_id, s])).values()]
        .filter(s => {
          const seasonStr = String(s.season || '')
          return !seasonStr.toLowerCase().includes('summer')
        })
    : []
  
  // Get current season (latest)
  const currentSeason = seasons[0]?.season_id || ''
  const seasonId = selectedSeason || currentSeason
  const gameType = selectedGameType || 'All' // 'All', 'Regular', 'Playoffs'
  
  // Get the season string to check if advanced analytics are available
  const selectedSeasonData = seasons.find(s => s.season_id === seasonId)
  const seasonString = selectedSeasonData?.season || ''
  const hasAdvancedAnalytics = seasonString >= '20252026'
  
  // Get team standing - fetch historical if season selected
  let teamStanding = standings.find(s => s.team_id === team.team_id)
  
  // Get regular season finish position and champion/runner-up status
  let regularSeasonFinish: number | null = null
  let isChampion = false
  let isRunnerUp = false
  
  if (seasonId && seasonId !== currentSeason) {
    // Fetch historical standings for selected season
    const { data: historicalStanding } = await supabase
      .from('fact_team_season_stats_basic')
      .select('*')
      .eq('team_id', team.team_id)
      .eq('season_id', seasonId)
      .eq('game_type', gameType === 'All' ? 'All' : gameType)
      .single()
    
    if (historicalStanding) {
      const points = historicalStanding.points || (historicalStanding.wins * 2 + (historicalStanding.ties || 0))
      const gamesPlayed = historicalStanding.games_played || 0
      const winPct = gamesPlayed > 0 ? (points / (gamesPlayed * 2)) * 100 : 0
      
      teamStanding = {
        ...historicalStanding,
        standing: 0, // Will need to calculate from all teams
        win_percentage: winPct,
      } as any
    }
    
    // Get regular season finish position
    const { data: regularSeasonStandings } = await supabase
      .from('fact_team_season_stats_basic')
      .select('team_id, points, wins, goal_diff')
      .eq('season_id', seasonId)
      .eq('game_type', 'Regular')
      .order('points', { ascending: false })
      .order('wins', { ascending: false })
      .order('goal_diff', { ascending: false })
    
    if (regularSeasonStandings) {
      const teamIndex = regularSeasonStandings.findIndex(s => String(s.team_id) === String(team.team_id))
      if (teamIndex !== -1) {
        regularSeasonFinish = teamIndex + 1
      }
    }
    
    // Check if team won/lost the last game in the season (champion/runner-up)
    const { data: lastGame } = await supabase
      .from('dim_schedule')
      .select('*')
      .eq('season_id', seasonId)
      .not('home_total_goals', 'is', null)
      .not('away_total_goals', 'is', null)
      .order('date', { ascending: false })
      .order('game_id', { ascending: false })
      .limit(1)
      .single()
    
    if (lastGame) {
      const homeGoals = Number(lastGame.home_total_goals) || 0
      const awayGoals = Number(lastGame.away_total_goals) || 0
      const homeTeamId = String(lastGame.home_team_id || '')
      const awayTeamId = String(lastGame.away_team_id || '')
      const teamId = String(team.team_id)
      
      if (homeGoals > awayGoals) {
        // Home team won
        if (homeTeamId === teamId) {
          isChampion = true
        } else if (awayTeamId === teamId) {
          isRunnerUp = true
        }
      } else if (awayGoals > homeGoals) {
        // Away team won
        if (awayTeamId === teamId) {
          isChampion = true
        } else if (homeTeamId === teamId) {
          isRunnerUp = true
        }
      }
    }
  }
  
  // Get team's recent completed games directly from dim_schedule
  let teamGamesQuery = supabase
    .from('dim_schedule')
    .select('*')
    .or(`home_team_name.eq.${team.team_name},away_team_name.eq.${team.team_name},home_team_id.eq.${team.team_id},away_team_id.eq.${team.team_id}`)
    .not('home_total_goals', 'is', null) // Only completed games
  
  // Filter by season if specified and not empty
  if (seasonId && seasonId.trim() !== '') {
    teamGamesQuery = teamGamesQuery.eq('season_id', seasonId)
  }
  
  const { data: teamGamesData, error: teamGamesError } = await teamGamesQuery
    .order('date', { ascending: false })
    .limit(20) // Get more games to show
  
  if (teamGamesError) {
    console.error('Error fetching team games:', teamGamesError)
  }
  
  const teamGames = (teamGamesData || []).filter((g: any) => g.home_total_goals !== null && g.away_total_goals !== null)
  
  // Get championship game IDs for each season to identify championship games
  // Get all seasons that have games in teamGames
  const seasonsInGames = [...new Set(teamGames.map((g: any) => g.season_id).filter(Boolean))]
  const championshipGameIds = new Set<number>()
  
  // Fetch last game for each season in parallel
  if (seasonsInGames.length > 0) {
    const lastGamesPromises = seasonsInGames.map(seasonId => 
      supabase
        .from('dim_schedule')
        .select('game_id')
        .eq('season_id', seasonId)
        .not('home_total_goals', 'is', null)
        .not('away_total_goals', 'is', null)
        .order('date', { ascending: false })
        .order('game_id', { ascending: false })
        .limit(1)
        .maybeSingle()
    )
    
    const lastGamesResults = await Promise.all(lastGamesPromises)
    lastGamesResults.forEach(result => {
      if (result.data?.game_id) {
        championshipGameIds.add(Number(result.data.game_id))
      }
    })
  }
  
  // Get opponent team info for recent games
  const opponentIds = [...new Set(teamGames.map((g: any) => {
    const homeId = String(g.home_team_id || '')
    const awayId = String(g.away_team_id || '')
    const homeName = g.home_team_name || ''
    const awayName = g.away_team_name || ''
    const isHome = homeId === team.team_id || homeName === team.team_name
    return isHome ? (g.away_team_id || null) : (g.home_team_id || null)
  }))].filter((id): id is string => Boolean(id))
  const opponentTeams = await Promise.all(
    opponentIds.map(id => getTeamById(String(id)))
  )
  const opponentTeamsMap = new Map(
    opponentTeams.filter(Boolean).map(t => [String(t!.team_id), t!])
  )
  
  // Get upcoming games from database directly (skip NORAD API to prevent blocking)
  // The NORAD API was causing slow page loads, so we'll use database only
  let upcomingGames: any[] = []
  
  // Fallback to database if NORAD API fails or returns no games
  if (upcomingGames.length === 0) {
    const today = new Date().toISOString().split('T')[0]
    const { data: upcomingGamesData } = await supabase
      .from('dim_schedule')
      .select('*')
      .or(`home_team_name.eq.${team.team_name},away_team_name.eq.${team.team_name},home_team_id.eq.${team.team_id},away_team_id.eq.${team.team_id}`)
      .gte('date', today)
      .order('date', { ascending: true })
      .limit(20)
    
    // Filter to only games that haven't been played (no scores)
    upcomingGames = (upcomingGamesData || []).filter((g: any) => 
      g.home_total_goals === null || g.away_total_goals === null || 
      g.home_total_goals === undefined || g.away_total_goals === undefined
    ).slice(0, 10)
  }
  
  // Also get opponent teams for upcoming games
  const upcomingOpponentIds = [...new Set((upcomingGames || []).map((g: any) => {
    const homeName = g.home_team_name || g.home_team || ''
    const awayName = g.away_team_name || g.away_team || ''
    const homeId = g.home_team_id || ''
    const awayId = g.away_team_id || ''
    const isHome = homeName === team.team_name || homeId === team.team_id
    return isHome ? awayId : homeId
  }))].filter((id): id is string => Boolean(id))
  const upcomingOpponentTeams = await Promise.all(
    upcomingOpponentIds.map(id => getTeamById(String(id)))
  )
  upcomingOpponentTeams.forEach(t => {
    if (t) opponentTeamsMap.set(String(t.team_id), t)
  })
  
  // Get current season to determine roster logic
  const { getCurrentSeason } = await import('@/lib/supabase/queries/league')
  const currentSeasonId = await getCurrentSeason()
  const isCurrentSeason = !seasonId || seasonId === currentSeason
  
  // Fetch roster - use historical stats if season is selected, otherwise current
  let roster: any[] = []
  let rosterGoalies: any[] = []
  let subSkaters: any[] = []
  let subGoalies: any[] = []
  
  // Get all players who played for this team from fact_gameroster
  let gameRosterQuery = supabase
    .from('fact_gameroster')
    .select('player_id, team_id, game_id, player_position, player_full_name, goals, assist, points, season_id')
    .or(`team_id.eq.${team.team_id},team_name.eq.${team.team_name}`)
  
  // If current season, filter by season_id
  if (isCurrentSeason && currentSeasonId) {
    gameRosterQuery = gameRosterQuery.eq('season_id', currentSeasonId)
  } else if (seasonId) {
    gameRosterQuery = gameRosterQuery.eq('season_id', seasonId)
  }
  
  const { data: allGameRoster } = await gameRosterQuery
  
  // Get game IDs for filtering advanced stats
  const { data: scheduleForRoster } = seasonId 
    ? await supabase
        .from('dim_schedule')
        .select('game_id')
        .eq('season_id', seasonId)
    : { data: null }
  
  const gameIdsForRoster = scheduleForRoster?.map(g => g.game_id) || []
  
  if (allGameRoster && allGameRoster.length > 0) {
    // Count games per player and aggregate stats
    const playerGameCounts = new Map<string, number>()
    const playerStats = new Map<string, { goals: number; assists: number; points: number; position?: string }>()
    // Track all positions each player has played in games for this team
    const playerPositionsPlayed = new Map<string, Set<string>>()
    
    allGameRoster.forEach(gr => {
      const pid = String(gr.player_id)
      playerGameCounts.set(pid, (playerGameCounts.get(pid) || 0) + 1)
      
      const existing = playerStats.get(pid) || { goals: 0, assists: 0, points: 0 }
      playerStats.set(pid, {
        goals: existing.goals + (Number(gr.goals) || 0),
        assists: existing.assists + (Number(gr.assist) || 0),
        points: existing.points + (Number(gr.points) || (Number(gr.goals) || 0) + (Number(gr.assist) || 0)),
        position: gr.player_position || existing.position,
      })
      
      // Track all positions played in games
      if (gr.player_position) {
        const posSet = playerPositionsPlayed.get(pid) || new Set<string>()
        posSet.add(String(gr.player_position).toLowerCase())
        playerPositionsPlayed.set(pid, posSet)
      }
    })
    
    const allPlayerIds = Array.from(playerGameCounts.keys())
    
    if (allPlayerIds.length > 0) {
      // Get player details
      const { data: allPlayers } = await supabase
        .from('dim_player')
        .select('*')
        .in('player_id', allPlayerIds)
      
      const playersMapForRoster = new Map((allPlayers || []).map(p => [String(p.player_id), p]))
      
      // Separate into goalies and skaters based on positions actually played in games
      const goalieIds: string[] = []
      const skaterIds: string[] = []
      
      allPlayerIds.forEach(pid => {
        const player = playersMapForRoster.get(pid)
        const positionsPlayed = playerPositionsPlayed.get(pid) || new Set<string>()
        const primaryPosition = (player?.player_primary_position || '').toLowerCase()
        
        // Check if player has played as goalie in any game for this team
        const hasPlayedGoalie = Array.from(positionsPlayed).some(pos => 
          pos.includes('goalie') || pos === 'g' || pos.includes('goaltender')
        ) || primaryPosition.includes('goalie')
        
        // Check if player has played as skater in any game for this team
        const hasPlayedSkater = Array.from(positionsPlayed).some(pos => 
          !pos.includes('goalie') && pos !== 'g' && !pos.includes('goaltender') && pos !== ''
        ) || (!primaryPosition.includes('goalie') && primaryPosition !== '')
        
        // If they've played as goalie, add to goalie list
        if (hasPlayedGoalie) {
          goalieIds.push(pid)
        }
        
        // If they've played as skater, add to skater list
        if (hasPlayedSkater) {
          skaterIds.push(pid)
        }
        
        // If no positions found in games and no primary position, default based on primary position
        if (positionsPlayed.size === 0 && primaryPosition) {
          if (primaryPosition.includes('goalie')) {
            goalieIds.push(pid)
          } else {
            skaterIds.push(pid)
          }
        }
      })
      
      if (isCurrentSeason && currentSeasonId) {
        // CURRENT SEASON: Main roster from dim_player.current_team
        const { data: mainRosterPlayers } = await supabase
          .from('dim_player')
          .select('*')
          .eq('player_norad_current_team_id', team.team_id)
          .not('player_norad_current_team_id', 'is', null)
        
        const mainRosterPlayerIds = new Set((mainRosterPlayers || []).map(p => String(p.player_id)))
        
        // Separate main roster skaters and goalies
        const mainRosterSkaterIds = skaterIds.filter(id => mainRosterPlayerIds.has(id))
        const mainRosterGoalieIds = goalieIds.filter(id => mainRosterPlayerIds.has(id))
        
        // Get stats for main roster players
        if (mainRosterSkaterIds.length > 0) {
          const { data: rosterStats } = await supabase
            .from('v_rankings_players_current')
            .select('*')
            .in('player_id', mainRosterSkaterIds)
            .or(`team_id.eq.${team.team_id},team_name.eq.${team.team_name}`)
          
          const statsMap = new Map((rosterStats || []).map(s => [String(s.player_id), s]))
          roster = mainRosterSkaterIds.map(pid => {
            const player = playersMapForRoster.get(pid)
            const stats = statsMap.get(pid) || playerStats.get(pid)
            const games = playerGameCounts.get(pid) || 0
            return {
              ...player,
              ...stats,
              player_id: pid,
              player_name: player?.player_name || player?.player_full_name || '',
              games_played: stats?.games_played ?? games,
              goals: stats?.goals ?? (playerStats.get(pid)?.goals || 0),
              assists: stats?.assists ?? (playerStats.get(pid)?.assists || 0),
              points: stats?.points ?? (playerStats.get(pid)?.points || 0),
              points_per_game: stats?.points_per_game ?? (games > 0 ? ((playerStats.get(pid)?.points || 0) / games) : 0),
              jersey_number: player?.jersey_number,
              current_skill_rating: player?.current_skill_rating,
              player_primary_position: player?.player_primary_position,
            }
          }).filter(p => p.player_id).sort((a, b) => (b.points ?? 0) - (a.points ?? 0))
        }
        
        // Get main roster goalies
        if (mainRosterGoalieIds.length > 0) {
          // Try v_leaderboard_goalie_gaa first (requires 5+ games)
          const { data: goalieStats } = await supabase
            .from('v_leaderboard_goalie_gaa')
            .select('*')
            .in('player_id', mainRosterGoalieIds)
            .eq('team_name', team.team_name)
          
          // Also try fact_goalie_season_stats_basic for goalies with <5 games
          const { data: goalieStatsBasic } = await supabase
            .from('fact_goalie_season_stats_basic')
            .select('player_id, games_played, gaa, goals_against, wins, losses, ties, shutouts, win_pct')
            .in('player_id', mainRosterGoalieIds)
            .eq('team_id', team.team_id)
            .eq('game_type', 'All')
            .eq('season_id', currentSeasonId || '')
          
          // Fetch saves and shots_against from goalie game stats
          const { data: goalieGameStats } = await supabase
            .from('fact_goalie_game_stats')
            .select('player_id, saves, shots_against, save_pct')
            .in('player_id', mainRosterGoalieIds)
          
          // Get schedule to match by season
          if (goalieGameStats && goalieGameStats.length > 0) {
            const goalieGameIds = goalieGameStats.map(g => g.game_id).filter(Boolean)
            const { data: goalieSchedule } = await supabase
              .from('dim_schedule')
              .select('game_id, season_id')
              .in('game_id', goalieGameIds)
              .eq('season_id', currentSeasonId || '')
            
            const scheduleMap = new Map((goalieSchedule || []).map(s => [s.game_id, s.season_id]))
            
            // Aggregate saves and shots_against by player
            const savesByPlayer = new Map<string, { saves: number; shots_against: number }>()
            goalieGameStats.forEach(stat => {
              const seasonId = stat.game_id ? scheduleMap.get(stat.game_id) : null
              if (seasonId === currentSeasonId) {
                const pid = String(stat.player_id)
                const existing = savesByPlayer.get(pid) || { saves: 0, shots_against: 0 }
                savesByPlayer.set(pid, {
                  saves: existing.saves + (Number(stat.saves) || 0),
                  shots_against: existing.shots_against + (Number(stat.shots_against) || 0),
                })
              }
            })
            
            // Merge saves data into basic stats
            ;(goalieStatsBasic || []).forEach(s => {
              const savesData = savesByPlayer.get(String(s.player_id))
              if (savesData) {
                s.saves = savesData.saves
                s.shots_against = savesData.shots_against
                s.save_pct = savesData.shots_against > 0
                  ? (savesData.saves / savesData.shots_against)
                  : null
              }
            })
          }
          
          const statsMap = new Map((goalieStats || []).map(s => [String(s.player_id), s]))
          // Add basic stats for goalies not in the GAA leaderboard
          ;(goalieStatsBasic || []).forEach(s => {
            if (!statsMap.has(String(s.player_id))) {
              statsMap.set(String(s.player_id), s)
            }
          })
          
          rosterGoalies = mainRosterGoalieIds.map(pid => {
            const player = playersMapForRoster.get(pid)
            const stats = statsMap.get(pid)
            const games = playerGameCounts.get(pid) || 0
            // Calculate GAA if not in stats but we have goals_against
            let gaa = stats?.gaa ?? null
            if (gaa == null && stats?.goals_against != null && games > 0) {
              gaa = stats.goals_against / games // GAA = goals against per game
            }
            return {
              ...player,
              ...stats,
              player_id: pid,
              player_name: player?.player_name || player?.player_full_name || '',
              games_played: stats?.games_played ?? games,
              gaa: gaa,
              save_pct: stats?.save_pct ?? null,
              jersey_number: player?.jersey_number,
              current_skill_rating: player?.current_skill_rating,
            }
          }).filter(p => p.player_id).sort((a, b) => (a.gaa ?? 999) - (b.gaa ?? 999))
        }
        
        // SUBS: Players who played games but aren't on main roster (1+ games)
        const subSkaterIds = skaterIds.filter(id => !mainRosterPlayerIds.has(id))
        const subGoalieIds = goalieIds.filter(id => !mainRosterPlayerIds.has(id))
        
        if (subGoalieIds.length > 0) {
          // Calculate GAA from game scores for this specific team
          // Get games where these goalies played for this team
          const { data: goalieGames } = await supabase
            .from('fact_gameroster')
            .select('player_id, game_id, team_id, team_venue')
            .in('player_id', subGoalieIds)
            .or(`team_id.eq.${team.team_id},team_name.eq.${team.team_name}`)
            .eq('season_id', currentSeasonId || '')
          
          if (goalieGames && goalieGames.length > 0) {
            // Get unique game IDs
            const uniqueGameIds = [...new Set(goalieGames.map(g => g.game_id).filter(id => id != null))]
            
            // Get game scores from schedule
            const { data: gameScores } = await supabase
              .from('dim_schedule')
              .select('game_id, home_team_id, away_team_id, home_total_goals, away_total_goals, official_home_goals, official_away_goals')
              .in('game_id', uniqueGameIds)
            
            const scoresMap = new Map((gameScores || []).map(g => [g.game_id, g]))
            
            // Aggregate goals_against per goalie for this team
            const goalieTeamStats = new Map<string, { goals_against: number; games: number }>()
            
            goalieGames.forEach(rosterEntry => {
              const pid = String(rosterEntry.player_id)
              const gameId = rosterEntry.game_id
              const gameScore = scoresMap.get(gameId)
              
              if (!gameScore) return
              
              // Determine if goalie's team was home or away
              const isHome = String(gameScore.home_team_id) === String(team.team_id) ||
                           String(rosterEntry.team_venue) === 'home'
              
              // Get goals against (opponent's goals)
              const goalsAgainst = isHome 
                ? (gameScore.official_away_goals ?? gameScore.away_total_goals ?? 0)
                : (gameScore.official_home_goals ?? gameScore.home_total_goals ?? 0)
              
              const existing = goalieTeamStats.get(pid) || { goals_against: 0, games: 0 }
              goalieTeamStats.set(pid, {
                goals_against: existing.goals_against + Number(goalsAgainst),
                games: existing.games + 1
              })
            })
            
            subGoalies = subGoalieIds.map(pid => {
              const player = playersMapForRoster.get(pid)
              const teamStats = goalieTeamStats.get(pid)
              const games = teamStats?.games || playerGameCounts.get(pid) || 0
              const goalsAgainst = teamStats?.goals_against || 0
              
              // Calculate GAA for this specific team
              let gaa: number | null = null
              if (games > 0) {
                gaa = goalsAgainst / games
              }
              
              return {
                ...player,
                player_id: pid,
                player_name: player?.player_name || player?.player_full_name || '',
                games_played: games,
                gaa: gaa,
                goals_against: goalsAgainst,
                save_pct: null,
                saves: null,
                shots_against: null,
                wins: null,
                losses: null,
                ties: null,
                shutouts: null,
                jersey_number: player?.jersey_number,
                current_skill_rating: player?.current_skill_rating,
              }
            }).filter(p => p.player_id).sort((a, b) => (a.gaa ?? 999) - (b.gaa ?? 999))
          } else {
            // Fallback if no games found
            subGoalies = subGoalieIds.map(pid => {
              const player = playersMapForRoster.get(pid)
              const games = playerGameCounts.get(pid) || 0
              return {
                ...player,
                player_id: pid,
                player_name: player?.player_name || player?.player_full_name || '',
                games_played: games,
                gaa: null,
                save_pct: null,
              }
            }).filter(p => p.player_id)
          }
        }
        
        if (subSkaterIds.length > 0) {
          const { data: subStats } = await supabase
            .from('v_rankings_players_current')
            .select('*')
            .in('player_id', subSkaterIds)
            .or(`team_id.eq.${team.team_id},team_name.eq.${team.team_name}`)
          
          const statsMap = new Map((subStats || []).map(s => [String(s.player_id), s]))
          subSkaters = subSkaterIds.map(pid => {
            const player = playersMapForRoster.get(pid)
            const stats = statsMap.get(pid) || playerStats.get(pid)
            const games = playerGameCounts.get(pid) || 0
            return {
              ...player,
              ...stats,
              player_id: pid,
              player_name: player?.player_name || player?.player_full_name || '',
              games_played: games,
              goals: stats?.goals ?? (playerStats.get(pid)?.goals || 0),
              assists: stats?.assists ?? (playerStats.get(pid)?.assists || 0),
              points: stats?.points ?? (playerStats.get(pid)?.points || 0),
              points_per_game: games > 0 ? ((playerStats.get(pid)?.points || 0) / games) : 0,
              jersey_number: player?.jersey_number,
              current_skill_rating: player?.current_skill_rating,
              player_primary_position: player?.player_primary_position,
            }
          }).filter(p => p.player_id).sort((a, b) => (b.points ?? 0) - (a.points ?? 0))
        }
        
        if (subGoalieIds.length > 0) {
          // Calculate GAA from game scores for this specific team
          // Get games where these goalies played for this team
          const { data: goalieGames } = await supabase
            .from('fact_gameroster')
            .select('player_id, game_id, team_id, team_venue')
            .in('player_id', subGoalieIds)
            .or(`team_id.eq.${team.team_id},team_name.eq.${team.team_name}`)
            .eq('season_id', seasonId)
          
          if (goalieGames && goalieGames.length > 0) {
            // Get unique game IDs
            const uniqueGameIds = [...new Set(goalieGames.map(g => g.game_id).filter(id => id != null))]
            
            // Get game scores from schedule
            const { data: gameScores } = await supabase
              .from('dim_schedule')
              .select('game_id, home_team_id, away_team_id, home_total_goals, away_total_goals, official_home_goals, official_away_goals')
              .in('game_id', uniqueGameIds)
            
            const scoresMap = new Map((gameScores || []).map(g => [g.game_id, g]))
            
            // Aggregate goals_against per goalie for this team
            const goalieTeamStats = new Map<string, { goals_against: number; games: number }>()
            
            goalieGames.forEach(rosterEntry => {
              const pid = String(rosterEntry.player_id)
              const gameId = rosterEntry.game_id
              const gameScore = scoresMap.get(gameId)
              
              if (!gameScore) return
              
              // Determine if goalie's team was home or away
              const isHome = String(gameScore.home_team_id) === String(team.team_id) ||
                           String(rosterEntry.team_venue) === 'home'
              
              // Get goals against (opponent's goals)
              const goalsAgainst = isHome 
                ? (gameScore.official_away_goals ?? gameScore.away_total_goals ?? 0)
                : (gameScore.official_home_goals ?? gameScore.home_total_goals ?? 0)
              
              const existing = goalieTeamStats.get(pid) || { goals_against: 0, games: 0 }
              goalieTeamStats.set(pid, {
                goals_against: existing.goals_against + Number(goalsAgainst),
                games: existing.games + 1
              })
            })
            
            subGoalies = subGoalieIds.map(pid => {
              const player = playersMapForRoster.get(pid)
              const teamStats = goalieTeamStats.get(pid)
              const games = teamStats?.games || playerGameCounts.get(pid) || 0
              const goalsAgainst = teamStats?.goals_against || 0
              
              // Calculate GAA for this specific team
              let gaa: number | null = null
              if (games > 0) {
                gaa = goalsAgainst / games
              }
              
              return {
                ...player,
                player_id: pid,
                player_name: player?.player_name || player?.player_full_name || '',
                games_played: games,
                gaa: gaa,
                goals_against: goalsAgainst,
                save_pct: null,
                saves: null,
                shots_against: null,
                wins: null,
                losses: null,
                ties: null,
                shutouts: null,
                jersey_number: player?.jersey_number,
                current_skill_rating: player?.current_skill_rating,
              }
            }).filter(p => p.player_id).sort((a, b) => (a.gaa ?? 999) - (b.gaa ?? 999))
          } else {
            // Fallback if no games found
            subGoalies = subGoalieIds.map(pid => {
              const player = playersMapForRoster.get(pid)
              const games = playerGameCounts.get(pid) || 0
              return {
                ...player,
                player_id: pid,
                player_name: player?.player_name || player?.player_full_name || '',
                games_played: games,
                gaa: null,
                save_pct: null,
              }
            }).filter(p => p.player_id)
          }
        }
      } else if (seasonId && seasonId !== currentSeason) {
        // PRIOR SEASONS: Separate main roster (5+ games) and subs (<5 games)
        const mainRosterSkaterIds: string[] = []
        const mainRosterGoalieIds: string[] = []
        const subSkaterIds: string[] = []
        const subGoalieIds: string[] = []
        
        playerGameCounts.forEach((games, playerId) => {
          const isGoalie = goalieIds.includes(playerId)
          if (games >= 5) {
            if (isGoalie) {
              mainRosterGoalieIds.push(playerId)
            } else {
              mainRosterSkaterIds.push(playerId)
            }
          } else {
            if (isGoalie) {
              subGoalieIds.push(playerId)
            } else {
              subSkaterIds.push(playerId)
            }
          }
        })
        
        // Fetch main roster skaters - use season stats for prior seasons
        if (mainRosterSkaterIds.length > 0) {
          const { data: seasonStats } = await supabase
            .from('fact_player_season_stats_basic')
            .select('player_id, games_played, goals, assists, points, pim')
            .in('player_id', mainRosterSkaterIds)
            .eq('team_id', team.team_id)
            .eq('season_id', seasonId)
            .eq('game_type', 'All')
          
          const statsMap = new Map((seasonStats || []).map(s => [String(s.player_id), s]))
          
          roster = mainRosterSkaterIds.map(pid => {
            const player = playersMapForRoster.get(pid)
            const stats = statsMap.get(pid) || playerStats.get(pid) || { goals: 0, assists: 0, points: 0, games_played: 0 }
            const games = stats.games_played || playerGameCounts.get(pid) || 0
            return {
              ...player,
              ...stats,
              player_id: pid,
              player_name: player?.player_name || player?.player_full_name || '',
              games_played: games,
              goals: stats.goals || 0,
              assists: stats.assists || 0,
              points: stats.points || 0,
              points_per_game: games > 0 ? ((stats.points || 0) / games) : 0,
              jersey_number: player?.jersey_number,
              current_skill_rating: player?.current_skill_rating,
              player_primary_position: player?.player_primary_position,
            }
          }).filter(p => p.player_id).sort((a, b) => (b.points ?? 0) - (a.points ?? 0))
        }
        
        // Fetch main roster goalies
        if (mainRosterGoalieIds.length > 0) {
          // Try v_leaderboard_goalie_gaa first (requires 5+ games)
          const { data: goalieStats } = await supabase
            .from('v_leaderboard_goalie_gaa')
            .select('*')
            .in('player_id', mainRosterGoalieIds)
            .eq('team_name', team.team_name)
            .eq('season_id', seasonId)
          
          // Also try fact_goalie_season_stats_basic for goalies with <5 games
          const { data: goalieStatsBasic } = await supabase
            .from('fact_goalie_season_stats_basic')
            .select('player_id, games_played, gaa, goals_against, wins, losses, ties, shutouts, win_pct')
            .in('player_id', mainRosterGoalieIds)
            .eq('team_id', team.team_id)
            .eq('game_type', 'All')
            .eq('season_id', seasonId)
          
          // Fetch saves and shots_against from goalie game stats
          const { data: goalieGameStats } = await supabase
            .from('fact_goalie_game_stats')
            .select('player_id, game_id, saves, shots_against, save_pct')
            .in('player_id', mainRosterGoalieIds)
          
          // Get schedule to match by season
          if (goalieGameStats && goalieGameStats.length > 0) {
            const goalieGameIds = goalieGameStats.map(g => g.game_id).filter(Boolean)
            const { data: goalieSchedule } = await supabase
              .from('dim_schedule')
              .select('game_id, season_id')
              .in('game_id', goalieGameIds)
              .eq('season_id', seasonId)
            
            const scheduleMap = new Map((goalieSchedule || []).map(s => [s.game_id, s.season_id]))
            
            // Aggregate saves and shots_against by player
            const savesByPlayer = new Map<string, { saves: number; shots_against: number }>()
            goalieGameStats.forEach(stat => {
              const seasonIdMatch = stat.game_id ? scheduleMap.get(stat.game_id) : null
              if (seasonIdMatch === seasonId) {
                const pid = String(stat.player_id)
                const existing = savesByPlayer.get(pid) || { saves: 0, shots_against: 0 }
                savesByPlayer.set(pid, {
                  saves: existing.saves + (Number(stat.saves) || 0),
                  shots_against: existing.shots_against + (Number(stat.shots_against) || 0),
                })
              }
            })
            
            // Merge saves data into basic stats
            ;(goalieStatsBasic || []).forEach(s => {
              const savesData = savesByPlayer.get(String(s.player_id))
              if (savesData) {
                s.saves = savesData.saves
                s.shots_against = savesData.shots_against
                s.save_pct = savesData.shots_against > 0
                  ? (savesData.saves / savesData.shots_against)
                  : null
              }
            })
          }
          
          const statsMap = new Map((goalieStats || []).map(s => [String(s.player_id), s]))
          // Add basic stats for goalies not in the GAA leaderboard
          ;(goalieStatsBasic || []).forEach(s => {
            if (!statsMap.has(String(s.player_id))) {
              statsMap.set(String(s.player_id), s)
            }
          })
          
          rosterGoalies = mainRosterGoalieIds.map(pid => {
            const player = playersMapForRoster.get(pid)
            const stats = statsMap.get(pid)
            const games = playerGameCounts.get(pid) || 0
            // Calculate GAA if not in stats but we have goals_against
            let gaa = stats?.gaa ?? null
            if (gaa == null && stats?.goals_against != null && games > 0) {
              gaa = stats.goals_against / games // GAA = goals against per game
            }
            return {
              ...player,
              ...stats,
              player_id: pid,
              player_name: player?.player_name || player?.player_full_name || '',
              games_played: stats?.games_played ?? games,
              gaa: gaa,
              save_pct: stats?.save_pct ?? null,
              saves: stats?.saves ?? null,
              shots_against: stats?.shots_against ?? null,
              wins: stats?.wins ?? null,
              losses: stats?.losses ?? null,
              ties: stats?.ties ?? null,
              shutouts: stats?.shutouts ?? null,
              goals_against: stats?.goals_against ?? null,
              jersey_number: player?.jersey_number,
              current_skill_rating: player?.current_skill_rating,
            }
          }).filter(p => p.player_id).sort((a, b) => (a.gaa ?? 999) - (b.gaa ?? 999))
        }
        
        // Fetch sub skaters - use season stats for prior seasons
        if (subSkaterIds.length > 0) {
          const { data: seasonStats } = await supabase
            .from('fact_player_season_stats_basic')
            .select('player_id, games_played, goals, assists, points, pim')
            .in('player_id', subSkaterIds)
            .eq('team_id', team.team_id)
            .eq('season_id', seasonId)
            .eq('game_type', 'All')
          
          const statsMap = new Map((seasonStats || []).map(s => [String(s.player_id), s]))
          
          subSkaters = subSkaterIds.map(pid => {
            const player = playersMapForRoster.get(pid)
            const stats = statsMap.get(pid) || playerStats.get(pid) || { goals: 0, assists: 0, points: 0, games_played: 0 }
            const games = stats.games_played || playerGameCounts.get(pid) || 0
            return {
              ...player,
              ...stats,
              player_id: pid,
              player_name: player?.player_name || player?.player_full_name || '',
              games_played: games,
              goals: stats.goals || 0,
              assists: stats.assists || 0,
              points: stats.points || 0,
              points_per_game: games > 0 ? ((stats.points || 0) / games) : 0,
              jersey_number: player?.jersey_number,
              current_skill_rating: player?.current_skill_rating,
              player_primary_position: player?.player_primary_position,
            }
          }).filter(p => p.player_id).sort((a, b) => (b.points ?? 0) - (a.points ?? 0))
        }
        
        // Fetch sub goalies
        if (subGoalieIds.length > 0) {
          // Calculate GAA from game scores for this specific team
          // Get games where these goalies played for this team
          const { data: goalieGames } = await supabase
            .from('fact_gameroster')
            .select('player_id, game_id, team_id, team_venue')
            .in('player_id', subGoalieIds)
            .or(`team_id.eq.${team.team_id},team_name.eq.${team.team_name}`)
            .eq('season_id', seasonId)
          
          if (goalieGames && goalieGames.length > 0) {
            // Get unique game IDs
            const uniqueGameIds = [...new Set(goalieGames.map(g => g.game_id).filter(id => id != null))]
            
            // Get game scores from schedule
            const { data: gameScores } = await supabase
              .from('dim_schedule')
              .select('game_id, home_team_id, away_team_id, home_total_goals, away_total_goals, official_home_goals, official_away_goals')
              .in('game_id', uniqueGameIds)
            
            const scoresMap = new Map((gameScores || []).map(g => [g.game_id, g]))
            
            // Aggregate goals_against per goalie for this team
            const goalieTeamStats = new Map<string, { goals_against: number; games: number }>()
            
            goalieGames.forEach(rosterEntry => {
              const pid = String(rosterEntry.player_id)
              const gameId = rosterEntry.game_id
              const gameScore = scoresMap.get(gameId)
              
              if (!gameScore) return
              
              // Determine if goalie's team was home or away
              const isHome = String(gameScore.home_team_id) === String(team.team_id) ||
                           String(rosterEntry.team_venue) === 'home'
              
              // Get goals against (opponent's goals)
              const goalsAgainst = isHome 
                ? (gameScore.official_away_goals ?? gameScore.away_total_goals ?? 0)
                : (gameScore.official_home_goals ?? gameScore.home_total_goals ?? 0)
              
              const existing = goalieTeamStats.get(pid) || { goals_against: 0, games: 0 }
              goalieTeamStats.set(pid, {
                goals_against: existing.goals_against + Number(goalsAgainst),
                games: existing.games + 1
              })
            })
            
            subGoalies = subGoalieIds.map(pid => {
              const player = playersMapForRoster.get(pid)
              const teamStats = goalieTeamStats.get(pid)
              const games = teamStats?.games || playerGameCounts.get(pid) || 0
              const goalsAgainst = teamStats?.goals_against || 0
              
              // Calculate GAA for this specific team
              let gaa: number | null = null
              if (games > 0) {
                gaa = goalsAgainst / games
              }
              
              return {
                ...player,
                player_id: pid,
                player_name: player?.player_name || player?.player_full_name || '',
                games_played: games,
                gaa: gaa,
                goals_against: goalsAgainst,
                save_pct: null,
                saves: null,
                shots_against: null,
                wins: null,
                losses: null,
                ties: null,
                shutouts: null,
                jersey_number: player?.jersey_number,
                current_skill_rating: player?.current_skill_rating,
              }
            }).filter(p => p.player_id).sort((a, b) => (a.gaa ?? 999) - (b.gaa ?? 999))
          } else {
            // Fallback if no games found
            subGoalies = subGoalieIds.map(pid => {
              const player = playersMapForRoster.get(pid)
              const games = playerGameCounts.get(pid) || 0
              return {
                ...player,
                player_id: pid,
                player_name: player?.player_name || player?.player_full_name || '',
                games_played: games,
                gaa: null,
                save_pct: null,
              }
            }).filter(p => p.player_id)
          }
        }
      }
    }
  }
  
  // Set goalies for backward compatibility with display sections
  const goalies = rosterGoalies
  
  // Create players map for photos - ensure we have player_image
  const playersMap = new Map(players.map(p => [String(p.player_id), p]))
  
  // Fetch player images for roster players that might be missing from playersMap
  const rosterPlayerIds = (roster || []).map(p => String(p.player_id)).filter(id => !playersMap.has(id))
  if (rosterPlayerIds.length > 0) {
    const { data: missingPlayers } = await supabase
      .from('dim_player')
      .select('player_id, player_image, player_full_name, jersey_number, current_skill_rating')
      .in('player_id', rosterPlayerIds)
    
    if (missingPlayers) {
      missingPlayers.forEach(p => {
        playersMap.set(String(p.player_id), {
          ...p,
          player_image: p.player_image || null
        } as any)
      })
    }
  }
  
  // Same for goalies
  const goaliePlayerIds = (goalies || []).map(g => String(g.player_id)).filter(id => !playersMap.has(id))
  if (goaliePlayerIds.length > 0) {
    const { data: missingGoalies } = await supabase
      .from('dim_player')
      .select('player_id, player_image, player_full_name, jersey_number, current_skill_rating')
      .in('player_id', goaliePlayerIds)
    
    if (missingGoalies) {
      missingGoalies.forEach(p => {
        playersMap.set(String(p.player_id), {
          ...p,
          player_image: p.player_image || null
        } as any)
      })
    }
  }
  
  // Fetch images for sub skaters
  const subSkaterPlayerIds = (subSkaters || []).map(p => String(p.player_id)).filter(id => !playersMap.has(id))
  if (subSkaterPlayerIds.length > 0) {
    const { data: missingSubSkaters } = await supabase
      .from('dim_player')
      .select('player_id, player_image, player_full_name, jersey_number, current_skill_rating')
      .in('player_id', subSkaterPlayerIds)
    
    if (missingSubSkaters) {
      missingSubSkaters.forEach(p => {
        playersMap.set(String(p.player_id), {
          ...p,
          player_image: p.player_image || null
        } as any)
      })
    }
  }
  
  // Fetch images for sub goalies
  const subGoaliePlayerIds = (subGoalies || []).map(g => String(g.player_id)).filter(id => !playersMap.has(id))
  if (subGoaliePlayerIds.length > 0) {
    const { data: missingSubGoalies } = await supabase
      .from('dim_player')
      .select('player_id, player_image, player_full_name, jersey_number, current_skill_rating')
      .in('player_id', subGoaliePlayerIds)
    
    if (missingSubGoalies) {
      missingSubGoalies.forEach(p => {
        playersMap.set(String(p.player_id), {
          ...p,
          player_image: p.player_image || null
        } as any)
      })
    }
  }
  
  // Calculate stats from teamStanding (which may be historical)
  const wins = teamStanding?.wins ?? 0
  const losses = teamStanding?.losses ?? 0
  const ties = teamStanding?.ties ?? 0
  const goalsFor = teamStanding?.goals_for ?? 0
  const goalsAgainst = teamStanding?.goals_against ?? 0
  const differential = goalsFor - goalsAgainst
  const points = teamStanding?.points ?? (wins * 2 + ties)
  const gamesPlayed = teamStanding?.games_played ?? 0
  // Win percentage = points / (games_played * 2) * 100
  const winPct = gamesPlayed > 0 ? (points / (gamesPlayed * 2)) * 100 : 0
  
  return (
    <div className="space-y-6">
      {/* Back Link */}
      <Link 
        href="/norad/teams" 
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Teams
      </Link>
      
      {/* Team Header */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div 
          className="h-4"
          style={{ backgroundColor: team.primary_color || team.team_color1 || '#3b82f6' }}
        />
        <div className="p-6">
          <div className="flex items-start gap-6">
            <TeamLogo
              src={team.team_logo || null}
              name={team.team_name || ''}
              abbrev={team.team_cd}
              primaryColor={team.primary_color || team.team_color1}
              secondaryColor={team.team_color2}
              size="2xl"
            />
            <div className="flex-1">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h1 className="font-display text-4xl font-bold tracking-wider text-foreground mb-3">
                    {team.team_name}
                  </h1>
                  
                  {/* Record and Standings - Prominent Display */}
                  {teamStanding && (
                    <div className="space-y-3">
                      <div className="flex items-center gap-6 flex-wrap">
                        <div>
                          <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Record</div>
                          <div className="font-display text-3xl font-bold text-foreground">
                            {wins}-{losses}-{ties}
                          </div>
                        </div>
                        <div>
                          <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Win %</div>
                          <div className="font-mono text-2xl font-bold text-primary">
                            {winPct.toFixed(1)}%
                          </div>
                        </div>
                        <div>
                          <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Points</div>
                          <div className="font-mono text-2xl font-bold text-primary">
                            {points}
                          </div>
                        </div>
                        <div>
                          <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Standing</div>
                          <div className="font-mono text-2xl font-bold text-foreground">
                            #{teamStanding.standing || regularSeasonFinish || '-'}
                          </div>
                        </div>
                        <div>
                          <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Games Played</div>
                          <div className="font-mono text-xl font-semibold text-foreground">
                            {teamStanding.games_played || 0}
                          </div>
                        </div>
                      </div>
                      
                      {/* Champion/Runner-up badges */}
                      <div className="flex items-center gap-3 flex-wrap">
                        {isChampion && (
                          <div className="flex items-center gap-2 px-4 py-2 bg-assist/20 border-2 border-assist rounded-lg">
                            <Trophy className="w-5 h-5 text-assist" />
                            <span className="text-sm font-bold text-assist uppercase tracking-wider">
                              Champion
                            </span>
                          </div>
                        )}
                        {isRunnerUp && (
                          <div className="flex items-center gap-2 px-4 py-2 bg-muted border-2 border-border rounded-lg">
                            <Trophy className="w-5 h-5 text-muted-foreground" />
                            <span className="text-sm font-bold text-muted-foreground uppercase tracking-wider">
                              Runner Up
                            </span>
                          </div>
                        )}
                        {regularSeasonFinish && !isChampion && (
                          <div className="flex items-center gap-2 px-3 py-1 bg-accent border border-border rounded">
                            <Trophy className="w-4 h-4 text-assist" />
                            <span className="text-xs text-muted-foreground">
                              #{regularSeasonFinish} Regular Season Finish
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
                {seasons.length > 1 && (
                  <SeasonSelector 
                    seasons={seasons.map(s => ({ season_id: s.season_id, season: s.season }))}
                    currentSeason={seasonId}
                  />
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Main Content Tabs */}
      <div className="flex gap-2 border-b border-border pb-2">
        {[
          { id: 'overview', label: 'Overview', icon: Activity },
          { id: 'roster', label: 'Roster', icon: Users },
          { id: 'lines', label: 'Lines', icon: Users },
          { id: 'analytics', label: 'Analytics', icon: BarChart3 },
          { id: 'matchups', label: 'Matchups', icon: Target },
        ].map((tab) => {
          const Icon = tab.icon
          const isActive = activeTab === tab.id
          const params = new URLSearchParams()
          if (seasonId && seasonId !== currentSeason) {
            params.set('season', seasonId)
          }
          if (gameType !== 'All') {
            params.set('gameType', gameType)
          }
          params.set('tab', tab.id)
          const href = `?${params.toString()}`
          
          return (
            <Link
              key={tab.id}
              href={href}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-t-lg transition-all',
                isActive
                  ? 'bg-card border border-b-0 border-border -mb-[1px] text-foreground font-semibold'
                  : 'hover:bg-muted/50 text-muted-foreground'
              )}
            >
              <Icon className="w-4 h-4" />
              <span className="font-display text-sm">
                {tab.label}
              </span>
            </Link>
          )
        })}
      </div>
      
      {/* Game Type Filter (shown on Overview tab) */}
      {activeTab === 'overview' && (
        <div className="flex gap-2 border-b border-border pb-2">
          {[
            { id: 'All', label: 'All Games' },
            { id: 'Regular', label: 'Regular Season' },
            { id: 'Playoffs', label: 'Playoffs' },
          ].map((tab) => {
            const isActive = gameType === tab.id
            const params = new URLSearchParams()
            if (seasonId && seasonId !== currentSeason) {
              params.set('season', seasonId)
            }
            if (activeTab !== 'overview') {
              params.set('tab', activeTab)
            }
            if (tab.id !== 'All') {
              params.set('gameType', tab.id)
            }
            const href = params.toString() ? `?${params.toString()}` : ''
            
            return (
              <Link
                key={tab.id}
                href={href}
                className={cn(
                  'flex items-center gap-2 px-4 py-2 rounded-t-lg transition-all text-sm',
                  isActive
                    ? 'bg-muted border border-border text-foreground font-semibold'
                    : 'hover:bg-muted/50 text-muted-foreground'
                )}
              >
                <span className="font-display text-xs">
                  {tab.label}
                </span>
              </Link>
            )
          })}
        </div>
      )}
      
      {/* Tab Content */}
      {activeTab === 'overview' && (
        <>
      {/* Stats Overview */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-card rounded-lg p-4 border border-border text-center">
          <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Record</div>
          <div className="font-display text-2xl font-bold text-foreground">
            {wins}-{losses}-{ties}
          </div>
        </div>
        <div className="bg-card rounded-lg p-4 border border-border text-center">
          <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Win %</div>
          <div className="font-mono text-2xl font-bold text-primary">
            {winPct.toFixed(1)}%
          </div>
        </div>
        <div className="bg-card rounded-lg p-4 border border-border text-center">
          <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Goals For</div>
          <div className="font-mono text-2xl font-bold text-save">{goalsFor}</div>
        </div>
        <div className="bg-card rounded-lg p-4 border border-border text-center">
          <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Goals Against</div>
          <div className="font-mono text-2xl font-bold text-goal">{goalsAgainst}</div>
        </div>
        <div className="bg-card rounded-lg p-4 border border-border text-center">
          <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Differential</div>
          <div className={cn(
            'font-mono text-2xl font-bold',
            differential > 0 && 'text-save',
            differential < 0 && 'text-goal',
            differential === 0 && 'text-muted-foreground'
          )}>
            {differential > 0 ? '+' : ''}{differential}
          </div>
        </div>
      </div>
      
      {/* Advanced Stats Section - Only show for 20252026 and later */}
      {hasAdvancedAnalytics && (
        <TeamAdvancedStatsSection 
          teamId={team.team_id}
          teamName={team.team_name}
          seasonId={seasonId}
          gameType={gameType}
        />
      )}
      
      {/* Content Grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Roster */}
        <div className="lg:col-span-2 space-y-4">
          {/* Main Roster Goalies */}
          {rosterGoalies && rosterGoalies.length > 0 && (
            <div className="bg-card rounded-xl border border-border overflow-hidden">
              <div className="px-4 py-3 bg-accent border-b border-border">
                <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                  <Target className="w-4 h-4 text-save" />
                  {isCurrentSeason ? 'Goaltending' : 'Main Goalies (5+ games)'} ({rosterGoalies.length})
                </h2>
              </div>
              <SortableGoalieRosterTable
                goalies={rosterGoalies}
                playersMap={playersMap}
                teamColor={team.primary_color || team.team_color1}
              />
            </div>
          )}
          
          {/* Main Roster Skaters */}
          <div className="bg-card rounded-xl border border-border overflow-hidden">
            <div className="px-4 py-3 bg-accent border-b border-border">
              <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                <Users className="w-4 h-4" />
                {isCurrentSeason ? 'Roster' : 'Main Roster (5+ games)'} ({roster?.length ?? 0} skaters)
              </h2>
            </div>
            <SortableRosterTable
              players={roster?.slice(0, 15) || []}
              playersMap={playersMap}
              teamColor={team.primary_color || team.team_color1}
              hasAdvancedAnalytics={hasAdvancedAnalytics}
            />
          </div>
          
          {/* Sub Goalies Section */}
          {subGoalies && subGoalies.length > 0 && (
            <div className="bg-card rounded-xl border border-border overflow-hidden">
              <div className="px-4 py-3 bg-accent border-b border-border">
                <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                  <Target className="w-4 h-4 text-muted-foreground" />
                  {isCurrentSeason ? 'Sub Goalies' : 'Sub Goalies (<5 games)'} ({subGoalies.length})
                </h2>
              </div>
              <SortableGoalieRosterTable
                goalies={subGoalies}
                playersMap={playersMap}
                teamColor={team.primary_color || team.team_color1}
              />
            </div>
          )}
        
          {/* Sub Skaters Section */}
          {subSkaters && subSkaters.length > 0 && (
            <div className="bg-card rounded-xl border border-border overflow-hidden">
              <div className="px-4 py-3 bg-accent border-b border-border">
                <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                  <Users className="w-4 h-4 text-muted-foreground" />
                  {isCurrentSeason ? 'Sub Skaters' : 'Sub Skaters (<5 games)'} ({subSkaters.length})
                </h2>
              </div>
              <SortableRosterTable
                players={subSkaters}
                playersMap={playersMap}
                teamColor={team.primary_color || team.team_color1}
                hasAdvancedAnalytics={hasAdvancedAnalytics}
              />
            </div>
          )}
        </div>
        
        {/* Sidebar */}
        <div className="space-y-6">
          
          {/* Recent Games - Always show */}
          <div className="bg-card rounded-xl border border-border overflow-hidden">
            <div className="px-4 py-3 bg-accent border-b border-border flex items-center justify-between">
              <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                Recent Games
              </h2>
              {teamGames && teamGames.length > 5 && (
                <Link
                  href={`/norad/games?team=${team.team_id}${seasonId ? `&season=${seasonId}` : ''}`}
                  className="text-xs font-mono text-primary hover:underline"
                >
                  View All →
                </Link>
              )}
            </div>
            <div className="divide-y divide-border">
              {teamGames && teamGames.length > 0 ? teamGames.slice(0, 10).map((game: any) => {
                if (!game.game_id) return null

                const homeId = String((game as any).home_team_id || '')
                const awayId = String((game as any).away_team_id || '')
                const homeName = (game as any).home_team_name || ''
                const awayName = (game as any).away_team_name || ''
                const isHome = homeId === team.team_id || homeName === team.team_name
                const teamGoals = isHome ? (game as any).home_total_goals : (game as any).away_total_goals
                const oppGoals = isHome ? (game as any).away_total_goals : (game as any).home_total_goals
                const opponentId = isHome ? awayId : homeId
                const opponentName = isHome ? awayName : homeName
                const opponentTeam = opponentId ? opponentTeamsMap.get(opponentId) : null
                const won = teamGoals > oppGoals
                const tied = teamGoals === oppGoals
                const gameDate = new Date((game as any).date).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                })
                const gameType = (game as any).game_type || 'Regular'
                const isChampionship = championshipGameIds.has(Number(game.game_id))
                const gameTypeLabel = isChampionship ? 'Championship' : gameType
                
                return (
                  <Link
                    key={game.game_id}
                    href={`/norad/games/${game.game_id}`}
                    className="block p-4 hover:bg-muted/50 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3 flex-1">
                        {opponentTeam && (
                          <TeamLogo
                            src={opponentTeam.team_logo || null}
                            name={opponentTeam.team_name || opponentName || ''}
                            abbrev={opponentTeam.team_cd}
                            primaryColor={opponentTeam.primary_color || opponentTeam.team_color1}
                            secondaryColor={opponentTeam.team_color2}
                            size="sm"
                          />
                        )}
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-mono text-muted-foreground">{gameDate}</span>
                            <span className="text-xs text-muted-foreground">•</span>
                            <span className="text-xs font-mono text-muted-foreground">{isHome ? 'vs' : '@'}</span>
                            <span className="font-display text-sm font-semibold text-foreground">
                              {opponentName}
                            </span>
                            {isChampionship && (
                              <Trophy className="w-3.5 h-3.5 text-yellow-500 fill-yellow-500" title="Championship Game" />
                            )}
                            <span className={cn(
                              'text-xs font-mono uppercase px-1.5 py-0.5 rounded',
                              isChampionship 
                                ? 'bg-yellow-500/20 text-yellow-600 font-semibold'
                                : gameType === 'Playoffs'
                                ? 'bg-primary/20 text-primary'
                                : 'bg-muted text-muted-foreground'
                            )}>
                              {gameTypeLabel}
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="text-right flex items-center gap-3">
                        <div className={cn(
                          'font-mono text-xl font-bold',
                          won ? 'text-save' : tied ? 'text-muted-foreground' : 'text-goal'
                        )}>
                          {teamGoals}-{oppGoals}
                        </div>
                        <div className={cn(
                          'text-xs font-mono uppercase font-bold px-2 py-1 rounded',
                          won ? 'bg-save/20 text-save' : tied ? 'bg-muted text-muted-foreground' : 'bg-goal/20 text-goal'
                        )}>
                          {won ? 'W' : tied ? 'T' : 'L'}
                        </div>
                      </div>
                    </div>
                  </Link>
                )
              }) : (
                <div className="p-3 text-sm text-muted-foreground text-center">
                  No recent games found
                </div>
              )}
            </div>
            {teamGames && teamGames.length > 0 && (
              <div className="px-4 py-3 bg-accent/50 border-t border-border">
                <Link 
                  href={`/norad/games?team=${team.team_id}${seasonId ? `&season=${seasonId}` : ''}`}
                  className="text-xs font-mono text-primary hover:underline"
                >
                  View all games →
                </Link>
              </div>
            )}
          </div>
          
          {/* Upcoming Games - Always show */}
          <div className="bg-card rounded-xl border border-border overflow-hidden">
            <div className="px-4 py-3 bg-accent border-b border-border">
              <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                <Calendar className="w-4 h-4 text-primary" />
                Upcoming Schedule
              </h2>
            </div>
            <div className="divide-y divide-border">
              {upcomingGames && upcomingGames.length > 0 ? upcomingGames.slice(0, 5).map((game: any) => {
                  // Handle both NORAD API format and database format
                  const homeName = game.home_team_name || game.home_team || ''
                  const awayName = game.away_team_name || game.away_team || ''
                  const homeId = game.home_team_id || ''
                  const awayId = game.away_team_id || ''
                  
                  if (!homeName && !awayName && !game.game_id) return null
                  
                  const isHome = homeName === team.team_name || homeId === team.team_id
                  const opponentName = isHome ? awayName : homeName
                  const opponentId = isHome ? awayId : homeId
                  
                  const gameDate = (game.date || game.game_date)
                    ? new Date(game.date || game.game_date).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                      })
                    : 'TBD'
                  const gameTime = (game.time || game.game_time || 'TBD').toString()
                  
                  // Get opponent team info for logo
                  const opponentTeam = opponentId ? opponentTeamsMap.get(String(opponentId)) : null
                  
                  return (
                    <div
                      key={game.game_id}
                      className="block p-3 hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          {opponentTeam && (
                            <TeamLogo
                              src={opponentTeam.team_logo || null}
                              name={opponentTeam.team_name || opponentName || ''}
                              abbrev={opponentTeam.team_cd}
                              primaryColor={opponentTeam.primary_color || opponentTeam.team_color1}
                              secondaryColor={opponentTeam.team_color2}
                              size="xs"
                            />
                          )}
                          <div>
                            <div className="text-xs font-mono text-muted-foreground">
                              {gameDate} • {gameTime} • {isHome ? 'vs' : '@'}
                            </div>
                            <Link 
                              href={opponentTeam ? `/team/${(opponentTeam.team_name || opponentName).replace(/\s+/g, '_')}` : '#'}
                              className="font-display text-sm text-foreground hover:text-primary transition-colors"
                            >
                              {opponentName}
                            </Link>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-xs font-mono text-muted-foreground">
                            {game.venue || 'TBD'}
                          </div>
                        </div>
                      </div>
                    </div>
                  )
                }) : (
                  <div className="p-3 text-sm text-muted-foreground text-center">
                    No upcoming games scheduled
                  </div>
                )}
              </div>
            </div>
        </div>
      </div>
      </>
      )}
      
      {activeTab === 'roster' && (
        <div className="space-y-4">
          {/* Main Roster Goalies */}
          {rosterGoalies && rosterGoalies.length > 0 && (
            <div className="bg-card rounded-xl border border-border overflow-hidden">
              <div className="px-4 py-3 bg-accent border-b border-border">
                <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                  <Target className="w-4 h-4 text-save" />
                  {isCurrentSeason ? 'Goaltending' : 'Main Goalies (5+ games)'} ({rosterGoalies.length})
                </h2>
              </div>
              <SortableGoalieRosterTable
                goalies={rosterGoalies}
                playersMap={playersMap}
                teamColor={team.primary_color || team.team_color1}
              />
            </div>
          )}
          
          {/* Main Roster Skaters */}
          <div className="bg-card rounded-xl border border-border overflow-hidden">
            <div className="px-4 py-3 bg-accent border-b border-border">
              <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                <Users className="w-4 h-4" />
                {isCurrentSeason ? 'Full Roster' : 'Main Roster (5+ games)'} ({roster?.length ?? 0} skaters)
              </h2>
            </div>
            <SortableRosterTable
              players={roster || []}
              playersMap={playersMap}
              teamColor={team.primary_color || team.team_color1}
              hasAdvancedAnalytics={hasAdvancedAnalytics}
            />
          </div>
        
          {/* Sub Goalies Section */}
          {subGoalies && subGoalies.length > 0 && (
            <div className="bg-card rounded-xl border border-border overflow-hidden">
              <div className="px-4 py-3 bg-accent border-b border-border">
                <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                  <Target className="w-4 h-4 text-muted-foreground" />
                  {isCurrentSeason ? 'Sub Goalies' : 'Sub Goalies (<5 games)'} ({subGoalies.length})
                </h2>
              </div>
              <SortableGoalieRosterTable
                goalies={subGoalies}
                playersMap={playersMap}
                teamColor={team.primary_color || team.team_color1}
              />
            </div>
          )}
        
          {/* Sub Skaters Section */}
          {subSkaters && subSkaters.length > 0 && (
            <div className="bg-card rounded-xl border border-border overflow-hidden">
              <div className="px-4 py-3 bg-accent border-b border-border">
                <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                  <Users className="w-4 h-4" />
                  {isCurrentSeason ? 'Sub Skaters' : 'Sub Skaters (<5 games)'} ({subSkaters.length})
                </h2>
              </div>
              <SortableRosterTable
                players={subSkaters}
                playersMap={playersMap}
                teamColor={team.primary_color || team.team_color1}
                hasAdvancedAnalytics={hasAdvancedAnalytics}
              />
            </div>
          )}
        </div>
      )}
      
      {activeTab === 'lines' && (
        <TeamLinesTab 
          teamId={team.team_id}
          teamName={team.team_name}
          seasonId={seasonId}
          playersMap={playersMap}
          team={team}
        />
      )}
      
      {activeTab === 'analytics' && (
        <TeamAnalyticsTab 
          teamId={team.team_id}
          teamName={team.team_name}
          seasonId={seasonId}
          gameType={gameType}
        />
      )}
      
      {activeTab === 'matchups' && (
        <TeamMatchupsTab 
          teamId={team.team_id}
          teamName={team.team_name}
          seasonId={seasonId}
        />
      )}
    </div>
  )
}
