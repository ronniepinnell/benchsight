// src/app/(dashboard)/team/[teamName]/page.tsx
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getTeamByName, getTeamById, getStandings } from '@/lib/supabase/queries/teams'
import { getRecentGames } from '@/lib/supabase/queries/games'
import { getPlayers } from '@/lib/supabase/queries/players'
import { createClient } from '@/lib/supabase/server'
import { ArrowLeft, Users, Trophy, Calendar, TrendingUp, Target } from 'lucide-react'
import { cn } from '@/lib/utils'
import { TeamLogo } from '@/components/teams/team-logo'
import { PlayerPhoto } from '@/components/players/player-photo'
import { SeasonSelector } from '@/components/teams/season-selector'

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
          giveaways: (acc.giveaways || 0) + (stat.giveaways || 0),
          takeaways: (acc.takeaways || 0) + (stat.takeaways || 0),
          games: acc.games + 1,
        }), { hits: 0, blocks: 0, giveaways: 0, takeaways: 0, games: 0 })
        return {
          ...totals,
          toDiff: totals.takeaways - totals.giveaways,
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
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Possession Stats */}
          {possessionStats && (
            <div className="space-y-3">
              <h3 className="font-display text-sm font-semibold text-foreground uppercase tracking-wider border-b border-border pb-2">
                Possession
              </h3>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">CF%</span>
                  <span className="font-mono font-semibold text-foreground">{possessionStats.cfPct.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">FF%</span>
                  <span className="font-mono font-semibold text-foreground">{possessionStats.ffPct.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Corsi For</span>
                  <span className="font-mono text-foreground">{possessionStats.cf}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Corsi Against</span>
                  <span className="font-mono text-foreground">{possessionStats.ca}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">xG</span>
                  <span className="font-mono text-foreground">{possessionStats.xg.toFixed(2)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Goals - xG</span>
                  <span className={cn(
                    'font-mono font-semibold',
                    possessionStats.xgDiff > 0 ? 'text-save' : 'text-goal'
                  )}>
                    {possessionStats.xgDiff > 0 ? '+' : ''}{possessionStats.xgDiff.toFixed(2)}
                  </span>
                </div>
              </div>
            </div>
          )}
          
          {/* Special Teams */}
          {specialTeamsStats && (
            <div className="space-y-3">
              <h3 className="font-display text-sm font-semibold text-foreground uppercase tracking-wider border-b border-border pb-2">
                Special Teams
              </h3>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">PP%</span>
                  <span className="font-mono font-semibold text-primary">{specialTeamsStats.ppPct.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">PP Goals</span>
                  <span className="font-mono text-foreground">{specialTeamsStats.ppGoals}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">PP Opportunities</span>
                  <span className="font-mono text-foreground">{specialTeamsStats.ppOpps}</span>
                </div>
                <div className="flex justify-between items-center border-t border-border pt-2 mt-2">
                  <span className="text-xs text-muted-foreground">PK%</span>
                  <span className="font-mono font-semibold text-save">{specialTeamsStats.pkPct.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">PK Goals Against</span>
                  <span className="font-mono text-goal">{specialTeamsStats.pkGoalsAgainst}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">PK Opportunities</span>
                  <span className="font-mono text-foreground">{specialTeamsStats.pkOpps}</span>
                </div>
              </div>
            </div>
          )}
          
          {/* Zone Play */}
          {zoneStats && (
            <div className="space-y-3">
              <h3 className="font-display text-sm font-semibold text-foreground uppercase tracking-wider border-b border-border pb-2">
                Zone Play
              </h3>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Zone Entry %</span>
                  <span className="font-mono font-semibold text-foreground">{zoneStats.zePct.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Zone Entries</span>
                  <span className="font-mono text-foreground">{zoneStats.ze}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Successful Entries</span>
                  <span className="font-mono text-save">{zoneStats.zeSuccess}</span>
                </div>
                <div className="flex justify-between items-center border-t border-border pt-2 mt-2">
                  <span className="text-xs text-muted-foreground">Zone Exit %</span>
                  <span className="font-mono font-semibold text-foreground">{zoneStats.zxPct.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Zone Exits</span>
                  <span className="font-mono text-foreground">{zoneStats.zx}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Successful Exits</span>
                  <span className="font-mono text-save">{zoneStats.zxSuccess}</span>
                </div>
              </div>
            </div>
          )}
          
          {/* WAR/GAR */}
          {warStats && (
            <div className="space-y-3">
              <h3 className="font-display text-sm font-semibold text-foreground uppercase tracking-wider border-b border-border pb-2">
                WAR/GAR
              </h3>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Total WAR</span>
                  <span className="font-mono font-semibold text-primary">{warStats.totalWAR}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Total GAR</span>
                  <span className="font-mono text-foreground">{warStats.totalGAR}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Avg Game Score</span>
                  <span className="font-mono text-foreground">{warStats.avgGameScore}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Avg Rating</span>
                  <span className="font-mono text-foreground">{warStats.avgRating}</span>
                </div>
              </div>
            </div>
          )}
          
          {/* Physical */}
          {physicalStats && (
            <div className="space-y-3">
              <h3 className="font-display text-sm font-semibold text-foreground uppercase tracking-wider border-b border-border pb-2">
                Physical
              </h3>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Hits</span>
                  <span className="font-mono font-semibold text-foreground">{physicalStats.hits}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Hits/Game</span>
                  <span className="font-mono text-foreground">{physicalStats.hitsPerGame}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Blocks</span>
                  <span className="font-mono font-semibold text-save">{physicalStats.blocks}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Blocks/Game</span>
                  <span className="font-mono text-foreground">{physicalStats.blocksPerGame}</span>
                </div>
                <div className="flex justify-between items-center border-t border-border pt-2 mt-2">
                  <span className="text-xs text-muted-foreground">Takeaways</span>
                  <span className="font-mono text-save">{physicalStats.takeaways}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Giveaways</span>
                  <span className="font-mono text-goal">{physicalStats.giveaways}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">TO Differential</span>
                  <span className={cn(
                    'font-mono font-semibold',
                    physicalStats.toDiff > 0 ? 'text-save' : physicalStats.toDiff < 0 ? 'text-goal' : 'text-muted-foreground'
                  )}>
                    {physicalStats.toDiff > 0 ? '+' : ''}{physicalStats.toDiff}
                  </span>
                </div>
              </div>
            </div>
          )}
          
          {/* Shooting */}
          {shootingStats && (
            <div className="space-y-3">
              <h3 className="font-display text-sm font-semibold text-foreground uppercase tracking-wider border-b border-border pb-2">
                Shooting
              </h3>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Shooting %</span>
                  <span className="font-mono font-semibold text-primary">{shootingStats.shootingPct}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Shot Accuracy</span>
                  <span className="font-mono text-foreground">{shootingStats.shotAccuracy}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Total Shots</span>
                  <span className="font-mono text-foreground">{shootingStats.shots}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Shots on Goal</span>
                  <span className="font-mono text-foreground">{shootingStats.sog}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Shots/Game</span>
                  <span className="font-mono text-foreground">{shootingStats.shotsPerGame}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">SOG/Game</span>
                  <span className="font-mono text-foreground">{shootingStats.sogPerGame}</span>
                </div>
              </div>
            </div>
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
  searchParams: Promise<{ season?: string; gameType?: string }>
}) {
  const { teamName } = await params
  const { season: selectedSeason, gameType: selectedGameType } = await searchParams
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
    : []
  
  // Get current season (latest)
  const currentSeason = seasons[0]?.season_id || ''
  const seasonId = selectedSeason || currentSeason
  const gameType = selectedGameType || 'All' // 'All', 'Regular', 'Playoffs'
  
  // Get team standing - fetch historical if season selected
  let teamStanding = standings.find(s => s.team_id === team.team_id)
  
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
  }
  
  // Get team's recent completed games directly from dim_schedule
  const { data: teamGamesData } = await supabase
    .from('dim_schedule')
    .select('*')
    .or(`home_team_name.eq.${team.team_name},away_team_name.eq.${team.team_name},home_team_id.eq.${team.team_id},away_team_id.eq.${team.team_id}`)
    .not('home_total_goals', 'is', null) // Only completed games
    .order('date', { ascending: false })
    .limit(10)
  
  const teamGames = (teamGamesData || []).filter((g: any) => g.home_total_goals !== null && g.away_total_goals !== null)
  
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
  
  // Get upcoming games from noradhockey.com API
  let upcomingGames: any[] = []
  try {
    // Construct API URL - use environment variable or default to localhost for dev
    const baseUrl = process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'
    const apiUrl = `${baseUrl}/api/norad/schedule?team=${encodeURIComponent(team.team_name)}&teamId=${encodeURIComponent(team.team_id)}`
    
    const noradResponse = await fetch(apiUrl, { 
      next: { revalidate: 300 }, // Cache for 5 minutes
      headers: {
        'Content-Type': 'application/json',
      }
    })
    
    if (noradResponse.ok) {
      const noradData = await noradResponse.json()
      upcomingGames = noradData.games || []
    } else {
      const errorData = await noradResponse.json().catch(() => ({}))
      console.warn('NORAD API returned error:', noradResponse.status, errorData.error || noradResponse.statusText)
    }
  } catch (error) {
    console.error('Error fetching from NORAD API:', error)
    // Will fall through to database fallback
  }
  
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
  
  // Fetch roster - use historical stats if season is selected, otherwise current
  let roster: any[] = []
  let goalies: any[] = []
  
  if (seasonId && seasonId !== currentSeason) {
    // Historical season - fetch from fact_player_season_stats_basic
    const { data: historicalRoster } = await supabase
      .from('fact_player_season_stats_basic')
      .select('*')
      .eq('team_id', team.team_id)
      .eq('season_id', seasonId)
      .eq('game_type', gameType === 'All' ? 'All' : gameType)
      .order('points', { ascending: false })
    
    // Deduplicate roster by player_id (keep highest points)
    const rosterMap = new Map<string, any>()
    ;(historicalRoster || []).forEach((player: any) => {
      const playerId = String(player.player_id)
      const existing = rosterMap.get(playerId)
      if (!existing || (player.points || 0) > (existing.points || 0)) {
        rosterMap.set(playerId, player)
      }
    })
    roster = Array.from(rosterMap.values()).sort((a, b) => (b.points || 0) - (a.points || 0))
    
    // Historical goalies
    const { data: historicalGoalies } = await supabase
      .from('fact_goalie_season_stats_basic')
      .select('*')
      .eq('team_id', team.team_id)
      .eq('season_id', seasonId)
      .eq('game_type', gameType === 'All' ? 'All' : gameType)
      .order('gaa', { ascending: true })
    
    // Deduplicate goalies by player_id (keep best GAA)
    const goaliesMap = new Map<string, any>()
    ;(historicalGoalies || []).forEach((goalie: any) => {
      const playerId = String(goalie.player_id)
      const existing = goaliesMap.get(playerId)
      if (!existing || (goalie.gaa || 999) < (existing.gaa || 999)) {
        goaliesMap.set(playerId, goalie)
      }
    })
    goalies = Array.from(goaliesMap.values()).sort((a, b) => (a.gaa || 999) - (b.gaa || 999))
  } else {
    // Current season - use views
    const { data: currentRoster } = await supabase
      .from('v_rankings_players_current')
      .select('*')
      .eq('team_name', team.team_name)
      .order('points', { ascending: false })
    
    // Deduplicate roster by player_id (keep highest points)
    const rosterMap = new Map<string, any>()
    ;(currentRoster || []).forEach((player: any) => {
      const playerId = String(player.player_id)
      const existing = rosterMap.get(playerId)
      if (!existing || (player.points || 0) > (existing.points || 0)) {
        rosterMap.set(playerId, player)
      }
    })
    roster = Array.from(rosterMap.values()).sort((a, b) => (b.points || 0) - (a.points || 0))
    
    const { data: currentGoalies } = await supabase
      .from('v_leaderboard_goalie_gaa')
      .select('*')
      .or(`team_id.eq.${team.team_id},team_name.eq.${team.team_name}`)
      .order('gaa', { ascending: true })
    
    // Deduplicate goalies by player_id (keep best GAA)
    const goaliesMap = new Map<string, any>()
    ;(currentGoalies || []).forEach((goalie: any) => {
      const playerId = String(goalie.player_id)
      const existing = goaliesMap.get(playerId)
      if (!existing || (goalie.gaa || 999) < (existing.gaa || 999)) {
        goaliesMap.set(playerId, goalie)
      }
    })
    goalies = Array.from(goaliesMap.values()).sort((a, b) => (a.gaa || 999) - (b.gaa || 999))
  }
  
  // Create players map for photos - ensure we have player_image
  const playersMap = new Map(players.map(p => [String(p.player_id), p]))
  
  // Fetch player images for roster players that might be missing from playersMap
  const rosterPlayerIds = (roster || []).map(p => String(p.player_id)).filter(id => !playersMap.has(id))
  if (rosterPlayerIds.length > 0) {
    const { data: missingPlayers } = await supabase
      .from('dim_player')
      .select('player_id, player_image, player_full_name')
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
      .select('player_id, player_image, player_full_name')
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
        href="/teams" 
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Teams
      </Link>
      
      {/* Team Header */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div 
          className="h-3"
          style={{ backgroundColor: team.primary_color || team.team_color1 || '#3b82f6' }}
        />
        <div className="p-6">
          <div className="flex items-center gap-6">
            <TeamLogo
              src={team.team_logo || null}
              name={team.team_name || ''}
              abbrev={team.team_cd}
              primaryColor={team.primary_color || team.team_color1}
              secondaryColor={team.team_color2}
              size="xl"
            />
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="font-display text-3xl font-bold tracking-wider text-foreground">
                    {team.team_name}
                  </h1>
                  {teamStanding && (
                    <div className="flex items-center gap-4 mt-2">
                      <div className="flex items-center gap-2">
                        <Trophy className="w-4 h-4 text-assist" />
                        <span className="text-sm text-muted-foreground">
                          #{teamStanding.standing} in standings
                        </span>
                      </div>
                      <span className="text-sm font-mono text-muted-foreground">
                        {teamStanding.games_played} GP
                      </span>
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
      
      {/* Game Type Tabs */}
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
          if (tab.id !== 'All') {
            params.set('gameType', tab.id)
          }
          const href = params.toString() ? `?${params.toString()}` : ''
          
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
              <span className="font-display text-sm">
                {tab.label}
              </span>
            </Link>
          )
        })}
      </div>
      
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
      
      {/* Advanced Stats Section */}
      <TeamAdvancedStatsSection 
        teamId={team.team_id}
        teamName={team.team_name}
        seasonId={seasonId}
        gameType={gameType}
      />
      
      {/* Content Grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Roster */}
        <div className="lg:col-span-2 bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Users className="w-4 h-4" />
              Roster ({roster?.length ?? 0} skaters)
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-accent/50">
                  <th className="px-3 py-2 text-left font-display text-xs text-muted-foreground">Player</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">GP</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-goal">G</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-assist">A</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-primary">P</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">P/G</th>
                </tr>
              </thead>
              <tbody>
                {roster?.slice(0, 15).map((player) => {
                  const playerInfo = playersMap.get(String(player.player_id))
                  return (
                    <tr key={player.player_id} className="border-b border-border hover:bg-muted/50">
                      <td className="px-3 py-2">
                        <Link 
                          href={`/players/${player.player_id}`}
                          className="flex items-center gap-2 text-foreground hover:text-primary transition-colors"
                        >
                          <PlayerPhoto
                            src={playerInfo?.player_image || null}
                            name={player.player_name || ''}
                            primaryColor={team.primary_color || team.team_color1}
                            size="sm"
                          />
                          <span>{player.player_name}</span>
                        </Link>
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-muted-foreground">{player.games_played}</td>
                      <td className="px-2 py-2 text-center font-mono text-goal font-semibold">{player.goals}</td>
                      <td className="px-2 py-2 text-center font-mono text-assist">{player.assists}</td>
                      <td className="px-2 py-2 text-center font-mono text-primary font-semibold">{player.points}</td>
                      <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                        {player.points_per_game?.toFixed(2) ?? '-'}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
        
        {/* Sidebar */}
        <div className="space-y-6">
          {/* Goalies */}
          {goalies && goalies.length > 0 && (
            <div className="bg-card rounded-xl border border-border overflow-hidden">
              <div className="px-4 py-3 bg-accent border-b border-border">
                <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                  <Target className="w-4 h-4 text-save" />
                  Goaltending
                </h2>
              </div>
              <div className="divide-y divide-border">
                {goalies.map((goalie) => {
                  const goalieInfo = playersMap.get(String(goalie.player_id))
                  return (
                    <Link
                      key={goalie.player_id}
                      href={`/players/${goalie.player_id}`}
                      className="flex items-center gap-3 p-3 hover:bg-muted/50 transition-colors"
                    >
                      <PlayerPhoto
                        src={goalieInfo?.player_image || null}
                        name={goalie.player_name || ''}
                        primaryColor={team.primary_color || team.team_color1}
                        size="sm"
                      />
                      <div className="flex-1">
                        <div className="font-display text-sm font-semibold text-foreground">
                          {goalie.player_name}
                        </div>
                        <div className="flex items-center gap-4 mt-1 text-xs font-mono">
                          <span className="text-muted-foreground">{goalie.games_played} GP</span>
                          <span className="text-primary">{goalie.gaa?.toFixed(2)} GAA</span>
                          <span className="text-save">{goalie.save_pct ? (goalie.save_pct * 100).toFixed(1) : '-'}%</span>
                        </div>
                      </div>
                    </Link>
                  )
                })}
              </div>
            </div>
          )}
          
          {/* Recent Games - Always show */}
          <div className="bg-card rounded-xl border border-border overflow-hidden">
            <div className="px-4 py-3 bg-accent border-b border-border">
              <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                Recent Games
              </h2>
            </div>
            <div className="divide-y divide-border">
              {teamGames && teamGames.length > 0 ? teamGames.slice(0, 5).map((game: any) => {
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
                const won = teamGoals > oppGoals
                const gameDate = new Date((game as any).date).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                })
                
                // Get opponent team info for logo
                const opponentTeam = opponentId ? opponentTeamsMap.get(opponentId) : null
                
                return (
                  <Link
                    key={game.game_id}
                    href={`/games/${game.game_id}`}
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
                            {gameDate} • {isHome ? 'vs' : '@'}
                          </div>
                          <div className="font-display text-sm text-foreground">
                            {opponentName}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={cn(
                          'font-mono text-lg font-bold',
                          won ? 'text-save' : 'text-goal'
                        )}>
                          {teamGoals}-{oppGoals}
                        </div>
                        <div className={cn(
                          'text-xs font-mono uppercase',
                          won ? 'text-save' : 'text-goal'
                        )}>
                          {won ? 'W' : teamGoals === oppGoals ? 'T' : 'L'}
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
                            <div className="font-display text-sm text-foreground">
                              {opponentName}
                            </div>
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
    </div>
  )
}
