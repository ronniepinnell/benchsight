// @ts-nocheck
// src/app/(dashboard)/players/[playerId]/page.tsx
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getPlayerById, getPlayerCareerSummary, getPlayerGameLog } from '@/lib/supabase/queries/players'
import { getTeamById } from '@/lib/supabase/queries/teams'
import { createClient } from '@/lib/supabase/server'
import { ArrowLeft, Target, Sparkles, TrendingUp, Calendar, Activity, Zap, Shield, BarChart3, Info, Users, Clock, ExternalLink } from 'lucide-react'
import { cn, formatSeason } from '@/lib/utils'
import { PlayerPhoto } from '@/components/players/player-photo'
import { TeamLogo } from '@/components/teams/team-logo'
import { SeasonSelector } from '@/components/teams/season-selector'
import { StatCard, StatRow } from '@/components/players/stat-card'
import { GameStatDrilldown } from '@/components/stats/game-stat-drilldown'
import { calculatePercentile } from '@/lib/stats/percentiles'
import { GameCard } from '@/components/players/game-card'
import { PlayerProfileTabs } from '@/components/players/player-profile-tabs'
import { EnhancedShotMap } from '@/components/charts/enhanced-shot-map'
import { getPlayerShots } from '@/lib/supabase/queries/games'
import { Breadcrumbs } from '@/components/navigation/breadcrumbs'
import { SortablePriorTeamsTable } from '@/components/players/sortable-prior-teams-table'
import { CollapsibleSection } from '@/components/common/collapsible-section'

export const revalidate = 300

export async function generateMetadata({ params }: { params: Promise<{ playerId: string }> }) {
  const { playerId } = await params
  const player = await getPlayerById(playerId)
  return {
    title: player ? `${player.player_name} | BenchSight` : 'Player | BenchSight',
    description: player ? `Statistics for ${player.player_name}` : 'Player statistics',
  }
}

// Player Advanced Stats Section Component
async function PlayerAdvancedStatsSection({ 
  playerId, 
  seasonId, 
  gameType,
  gameIds = [],
  playerPosition,
  playerRating
}: { 
  playerId: string
  seasonId: string
  gameType: string
  gameIds?: number[]
  playerPosition?: string
  playerRating?: number
}) {
  try {
    const supabase = await createClient()
    
    // First, get all schedule data for filtering
    const { data: allScheduleData, error: scheduleError } = await supabase
      .from('dim_schedule')
      .select('game_id, season_id, game_type')
    
    if (scheduleError) {
      console.error('Error fetching schedule:', scheduleError)
    }
    
    // Filter schedule by season and game type
    const filteredSchedule = allScheduleData?.filter(s => {
      const seasonMatch = s.season_id === seasonId
      const gameTypeMatch = gameType === 'All' || s.game_type === gameType
      return seasonMatch && gameTypeMatch
    }) || []
    
    const gameIds = filteredSchedule.map(g => g.game_id)
    
    // If no games found, try to get any games for this player anyway (fallback)
    if (gameIds.length === 0) {
      // Still try to fetch stats - maybe season_id is in fact_player_game_stats directly
      const { data: directStats, error: directError } = await supabase
        .from('fact_player_game_stats')
        .select('game_id, season_id')
        .eq('player_id', playerId)
        .limit(1)
      
      if (directError) {
        console.error('Error checking for player stats:', directError)
      }
      
      if (!directStats || directStats.length === 0) {
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
                No game data available for this player.
              </p>
            </div>
          </div>
        )
      }
    }
  
  // Fetch all advanced stats in parallel
  // Query all stats for this player, then filter by game_ids if we have them
  const [
    possessionStats,
    zoneStats,
    warStats,
    physicalStats,
    shootingStats,
    per60Stats,
    faceoffStats,
    passingStats,
    situationalStats,
    assistBreakdownStats,
    microStats,
    qocStats
  ] = await Promise.all([
    // Possession stats - query all columns first, then extract what we need
    supabase
      .from('fact_player_game_stats')
      .select('*')
      .eq('player_id', playerId)
      .then(({ data, error }) => {
        if (error) {
          console.error('Error fetching possession stats:', error)
          return null
        }
        if (!data || data.length === 0) {
          return null
        }
        
        // Filter by game_id if we have filtered gameIds
        let filteredData = data
        if (gameIds.length > 0) {
          filteredData = data.filter(stat => gameIds.includes(stat.game_id))
        }
        if (filteredData.length === 0) {
          return null
        }
        
        const totals = filteredData.reduce((acc, stat) => {
          // Handle both column name formats - check what actually exists
          const cf = stat.corsi_for ?? stat.cf ?? 0
          const ca = stat.corsi_against ?? stat.ca ?? 0
          const ff = stat.fenwick_for ?? stat.ff ?? 0
          const fa = stat.fenwick_against ?? stat.fa ?? 0
          const xg = stat.xg_for ?? stat.xg ?? stat.expected_goals ?? 0
          const goals = stat.goals ?? stat.g ?? 0
          const goalsFor = stat.goals_for ?? stat.gf ?? 0
          const goalsAgainst = stat.goals_against ?? stat.ga ?? 0
          const cfPctRel = stat.cf_pct_rel ?? stat.corsi_pct_rel ?? 0
          const ffPctRel = stat.ff_pct_rel ?? stat.fenwick_pct_rel ?? 0
          const plusEv = stat.plus_ev ?? stat.plus_events ?? 0
          const minusEv = stat.minus_ev ?? stat.minus_events ?? 0
          const plusMinusEv = stat.plus_minus_ev ?? stat.plus_minus_even_strength ?? 0
          
          return {
            cf: (acc.cf || 0) + (Number(cf) || 0),
            ca: (acc.ca || 0) + (Number(ca) || 0),
            ff: (acc.ff || 0) + (Number(ff) || 0),
            fa: (acc.fa || 0) + (Number(fa) || 0),
            xg: (acc.xg || 0) + (Number(xg) || 0),
            goals: (acc.goals || 0) + (Number(goals) || 0),
            goalsFor: (acc.goalsFor || 0) + (Number(goalsFor) || 0),
            goalsAgainst: (acc.goalsAgainst || 0) + (Number(goalsAgainst) || 0),
            cfPctRel: (acc.cfPctRel || 0) + (Number(cfPctRel) || 0),
            ffPctRel: (acc.ffPctRel || 0) + (Number(ffPctRel) || 0),
            plusEv: (acc.plusEv || 0) + (Number(plusEv) || 0),
            minusEv: (acc.minusEv || 0) + (Number(minusEv) || 0),
            plusMinusEv: (acc.plusMinusEv || 0) + (Number(plusMinusEv) || 0),
            games: acc.games + 1,
          }
        }, { cf: 0, ca: 0, ff: 0, fa: 0, xg: 0, goals: 0, goalsFor: 0, goalsAgainst: 0, cfPctRel: 0, ffPctRel: 0, plusEv: 0, minusEv: 0, plusMinusEv: 0, games: 0 })
        
        // Only return if we have meaningful data
        if (totals.cf === 0 && totals.ca === 0 && totals.ff === 0 && totals.fa === 0) {
          return null
        }
        const cfPct = totals.cf + totals.ca > 0 ? (totals.cf / (totals.cf + totals.ca)) * 100 : 0
        const ffPct = totals.ff + totals.fa > 0 ? (totals.ff / (totals.ff + totals.fa)) * 100 : 0
        const gfPct = totals.goalsFor + totals.goalsAgainst > 0 ? (totals.goalsFor / (totals.goalsFor + totals.goalsAgainst)) * 100 : 0
        const xgDiff = Number(totals.goals) - Number(totals.xg)
        const avgCfPctRel = totals.games > 0 ? totals.cfPctRel / totals.games : 0
        const avgFfPctRel = totals.games > 0 ? totals.ffPctRel / totals.games : 0
        return { 
          ...totals, 
          cfPct: Number(cfPct), 
          ffPct: Number(ffPct), 
          gfPct: Number(gfPct),
          xgDiff: Number(xgDiff),
          cfPctRel: Number(avgCfPctRel),
          ffPctRel: Number(avgFfPctRel),
        }
      }).catch((error) => {
        console.error('Error in possession stats query:', error)
        return null
      }),
    
    // Zone stats - query all columns
    supabase
      .from('fact_player_game_stats')
      .select('*')
      .eq('player_id', playerId)
      .then(({ data, error }) => {
        if (error) {
          console.error('Error fetching zone stats:', error)
          return null
        }
        if (!data || data.length === 0) return null
        
        let filteredData = data
        if (gameIds.length > 0) {
          filteredData = data.filter(stat => gameIds.includes(stat.game_id))
        }
        if (filteredData.length === 0) return null
        
        const totals = filteredData.reduce((acc, stat) => {
          // Handle both column name formats
          const ze = stat.zone_entries ?? stat.zone_entry ?? 0
          const zeSuccess = stat.zone_entries_successful ?? stat.zone_entry_controlled ?? 0
          const zx = stat.zone_exits ?? stat.zone_exit ?? 0
          const zxSuccess = stat.zone_exits_successful ?? stat.zone_exit_controlled ?? 0
          return {
            ze: (acc.ze || 0) + (Number(ze) || 0),
            zeSuccess: (acc.zeSuccess || 0) + (Number(zeSuccess) || 0),
            zx: (acc.zx || 0) + (Number(zx) || 0),
            zxSuccess: (acc.zxSuccess || 0) + (Number(zxSuccess) || 0),
          }
        }, { ze: 0, zeSuccess: 0, zx: 0, zxSuccess: 0 })
        const zePct = totals.ze > 0 ? (totals.zeSuccess / totals.ze) * 100 : 0
        const zxPct = totals.zx > 0 ? (totals.zxSuccess / totals.zx) * 100 : 0
        
        // Only return if we have meaningful data
        if (totals.ze === 0 && totals.zx === 0) {
          return null
        }
        
        return { ...totals, zePct: Number(zePct), zxPct: Number(zxPct) }
      }).catch((error) => {
        console.error('Error in zone stats query:', error)
        return null
      }),
    
    // WAR/GAR - query all columns
    supabase
      .from('fact_player_game_stats')
      .select('*')
      .eq('player_id', playerId)
      .then(({ data, error }) => {
        if (error) {
          console.error('Error fetching WAR stats:', error)
          return null
        }
        if (!data || data.length === 0) return null
        
        let filteredData = data
        if (gameIds.length > 0) {
          filteredData = data.filter(stat => gameIds.includes(stat.game_id))
        }
        if (filteredData.length === 0) return null
        
        const totals = filteredData.reduce((acc, stat) => ({
          gar: (acc.gar || 0) + (Number(stat.gar) || 0),
          war: (acc.war || 0) + (Number(stat.war) || 0),
          gameScore: (acc.gameScore || 0) + (Number(stat.game_score) || 0),
          rating: (acc.rating || 0) + (Number(stat.player_rating) || 0),
          performanceIndex: (acc.performanceIndex || 0) + (Number(stat.performance_index) || 0),
          adjustedRating: (acc.adjustedRating || 0) + (Number(stat.adjusted_rating) || 0),
          games: acc.games + 1,
        }), { gar: 0, war: 0, gameScore: 0, rating: 0, performanceIndex: 0, adjustedRating: 0, games: 0 })
        // Only return if we have meaningful data
        if (totals.gar === 0 && totals.war === 0 && totals.gameScore === 0 && totals.rating === 0) {
          return null
        }
        
        return {
          totalGAR: Number(totals.gar).toFixed(1),
          totalWAR: Number(totals.war).toFixed(1),
          avgGameScore: totals.games > 0 ? Number(totals.gameScore / totals.games).toFixed(2) : '0.00',
          avgRating: totals.games > 0 ? Number(totals.rating / totals.games).toFixed(1) : '0.0',
          avgPerformanceIndex: totals.games > 0 && totals.performanceIndex !== 0 ? Number(totals.performanceIndex / totals.games).toFixed(2) : null,
          avgAdjustedRating: totals.games > 0 && totals.adjustedRating !== 0 ? Number(totals.adjustedRating / totals.games).toFixed(1) : null,
        }
      }).catch((error) => {
        console.error('Error in WAR stats query:', error)
        return null
      }),
    
    // Physical stats - query all columns
    supabase
      .from('fact_player_game_stats')
      .select('*')
      .eq('player_id', playerId)
      .then(({ data, error }) => {
        if (error) {
          console.error('Error fetching physical stats:', error)
          return null
        }
        if (!data || data.length === 0) return null
        
        let filteredData = data
        if (gameIds.length > 0) {
          filteredData = data.filter(stat => gameIds.includes(stat.game_id))
        }
        if (filteredData.length === 0) return null
        
        const totals = filteredData.reduce((acc, stat) => {
          // Handle both column name formats
          const hits = stat.hits ?? stat.hit ?? 0
          const blocks = stat.blocks ?? stat.blk ?? 0
          const badGiveaways = stat.bad_giveaways ?? stat.bad_give ?? 0
          const takeaways = stat.takeaways ?? stat.take ?? 0
          return {
            hits: (acc.hits || 0) + (Number(hits) || 0),
            blocks: (acc.blocks || 0) + (Number(blocks) || 0),
            badGiveaways: (acc.badGiveaways || 0) + (Number(badGiveaways) || 0),
            takeaways: (acc.takeaways || 0) + (Number(takeaways) || 0),
            games: acc.games + 1,
          }
        }, { hits: 0, blocks: 0, badGiveaways: 0, takeaways: 0, games: 0 })
        // Only return if we have meaningful data
        if (totals.hits === 0 && totals.blocks === 0 && totals.badGiveaways === 0 && totals.takeaways === 0) {
          return null
        }
        
        return {
          ...totals,
          giveaways: totals.badGiveaways, // For display, show bad giveaways
          toDiff: Number(totals.takeaways) - Number(totals.badGiveaways),
          hitsPerGame: totals.games > 0 ? Number(totals.hits / totals.games).toFixed(1) : '0.0',
          blocksPerGame: totals.games > 0 ? Number(totals.blocks / totals.games).toFixed(1) : '0.0',
        }
      }).catch((error) => {
        console.error('Error in physical stats query:', error)
        return null
      }),
    
    // Shooting stats - query all columns
    supabase
      .from('fact_player_game_stats')
      .select('*')
      .eq('player_id', playerId)
      .then(({ data, error }) => {
        if (error) {
          console.error('Error fetching shooting stats:', error)
          return null
        }
        if (!data || data.length === 0) return null
        
        let filteredData = data
        if (gameIds.length > 0) {
          filteredData = data.filter(stat => gameIds.includes(stat.game_id))
        }
        if (filteredData.length === 0) return null
        
        const totals = filteredData.reduce((acc, stat) => {
          // Handle both column name formats - try multiple column name variations
          const shots = stat.shots ?? stat.shot ?? stat.shots_total ?? 0
          const sog = stat.sog ?? stat.shots_on_goal ?? stat.shotsOnGoal ?? stat.shotsOnNet ?? 0
          const goals = stat.goals ?? stat.g ?? 0
          const shotsBlocked = stat.shots_blocked ?? stat.shotsBlocked ?? stat.blocks ?? stat.blocked_shots ?? 0
          const shotsMissed = stat.shots_missed ?? stat.shotsMissed ?? stat.missed_shots ?? stat.missedShots ?? 0
          return {
            shots: (acc.shots || 0) + (Number(shots) || 0),
            sog: (acc.sog || 0) + (Number(sog) || 0),
            goals: (acc.goals || 0) + (Number(goals) || 0),
            shotsBlocked: (acc.shotsBlocked || 0) + (Number(shotsBlocked) || 0),
            shotsMissed: (acc.shotsMissed || 0) + (Number(shotsMissed) || 0),
            games: acc.games + 1,
          }
        }, { shots: 0, sog: 0, goals: 0, shotsBlocked: 0, shotsMissed: 0, games: 0 })
        // Only return if we have meaningful data (allow goals even if shots not tracked)
        if (totals.shots === 0 && totals.sog === 0 && totals.goals === 0 && totals.shotsBlocked === 0 && totals.shotsMissed === 0) {
          return null
        }
        
        const shootingPct = totals.sog > 0 ? (totals.goals / totals.sog) * 100 : 0
        const shotAccuracy = totals.shots > 0 ? (totals.sog / totals.shots) * 100 : 0
        return {
          ...totals,
          shootingPct: Number(shootingPct).toFixed(1),
          shotAccuracy: Number(shotAccuracy).toFixed(1),
          shotsPerGame: totals.games > 0 ? Number(totals.shots / totals.games).toFixed(1) : '0.0',
          sogPerGame: totals.games > 0 ? Number(totals.sog / totals.games).toFixed(1) : '0.0',
          shotsBlockedPerGame: totals.games > 0 ? Number(totals.shotsBlocked / totals.games).toFixed(1) : '0.0',
          shotsMissedPerGame: totals.games > 0 ? Number(totals.shotsMissed / totals.games).toFixed(1) : '0.0',
        }
      }).catch((error) => {
        console.error('Error in shooting stats query:', error)
        return null
      }),
    
    // Per-60 rates - query all columns
    supabase
      .from('fact_player_game_stats')
      .select('*')
      .eq('player_id', playerId)
      .then(({ data, error }) => {
        if (error) {
          console.error('Error fetching per-60 stats:', error)
          return null
        }
        if (!data || data.length === 0) return null
        
        let filteredData = data
        if (gameIds.length > 0) {
          filteredData = data.filter(stat => gameIds.includes(stat.game_id))
        }
        if (filteredData.length === 0) return null
        
        const totals = filteredData.reduce((acc, stat) => {
          // Handle both column name formats
          const g60 = stat.goals_per_60 ?? stat.g_60 ?? 0
          const p60 = stat.points_per_60 ?? stat.pts_60 ?? 0
          const toi = stat.toi_seconds ?? 0
          const shifts = stat.shift_count ?? stat.shifts ?? 0
          const avgShift = stat.avg_shift ?? stat.avg_shift_length ?? 0
          return {
            g60: (acc.g60 || 0) + (Number(g60) || 0),
            p60: (acc.p60 || 0) + (Number(p60) || 0),
            toi: (acc.toi || 0) + (Number(toi) || 0),
            shifts: (acc.shifts || 0) + (Number(shifts) || 0),
            avgShift: (acc.avgShift || 0) + (Number(avgShift) || 0),
            games: acc.games + 1,
          }
        }, { g60: 0, p60: 0, toi: 0, shifts: 0, avgShift: 0, games: 0 })
        // Only return if we have meaningful data (TOI > 0)
        if (totals.toi === 0) {
          return null
        }
        
        // Calculate assists/60 from points/60 - goals/60
        const a60 = totals.p60 - totals.g60
        return {
          goalsPer60: totals.games > 0 ? Number(totals.g60 / totals.games).toFixed(2) : '0.00',
          assistsPer60: totals.games > 0 ? Number(a60 / totals.games).toFixed(2) : '0.00',
          pointsPer60: totals.games > 0 ? Number(totals.p60 / totals.games).toFixed(2) : '0.00',
          avgTOI: totals.games > 0 ? Number(totals.toi / totals.games / 60).toFixed(1) : '0.0',
          totalShifts: totals.shifts,
          avgShiftsPerGame: totals.games > 0 ? Number(totals.shifts / totals.games).toFixed(1) : '0.0',
          avgShiftLength: totals.games > 0 ? Number(totals.avgShift / totals.games).toFixed(2) : '0.00',
        }
      }).catch((error) => {
        console.error('Error in per-60 stats query:', error)
        return null
      }),
    
    // Faceoff stats - query all columns
    supabase
      .from('fact_player_game_stats')
      .select('*')
      .eq('player_id', playerId)
      .then(({ data, error }) => {
        if (error) {
          console.error('Error fetching faceoff stats:', error)
          return null
        }
        if (!data || data.length === 0) return null
        
        let filteredData = data
        if (gameIds.length > 0) {
          filteredData = data.filter(stat => gameIds.includes(stat.game_id))
        }
        if (filteredData.length === 0) return null
        
        const totals = filteredData.reduce((acc, stat) => {
          const foWins = stat.fo_wins ?? stat.fow ?? 0
          const foLosses = stat.fo_losses ?? stat.fol ?? 0
          const foTotal = stat.fo_total ?? (Number(foWins) + Number(foLosses)) ?? 0
          return {
            foWins: (acc.foWins || 0) + (Number(foWins) || 0),
            foLosses: (acc.foLosses || 0) + (Number(foLosses) || 0),
            foTotal: (acc.foTotal || 0) + (Number(foTotal) || 0),
            games: acc.games + 1,
          }
        }, { foWins: 0, foLosses: 0, foTotal: 0, games: 0 })
        
        // Only return if we have meaningful data
        if (totals.foTotal === 0) {
          return null
        }
        
        const foPct = totals.foTotal > 0 ? (totals.foWins / totals.foTotal) * 100 : 0
        return {
          ...totals,
          foPct: Number(foPct).toFixed(1),
          foWinsPerGame: totals.games > 0 ? Number(totals.foWins / totals.games).toFixed(1) : '0.0',
        }
      }).catch((error) => {
        console.error('Error in faceoff stats query:', error)
        return null
      }),
    
    // Passing stats - query all columns
    supabase
      .from('fact_player_game_stats')
      .select('*')
      .eq('player_id', playerId)
      .then(({ data, error }) => {
        if (error) {
          console.error('Error fetching passing stats:', error)
          return null
        }
        if (!data || data.length === 0) return null
        
        let filteredData = data
        if (gameIds.length > 0) {
          filteredData = data.filter(stat => gameIds.includes(stat.game_id))
        }
        if (filteredData.length === 0) return null
        
        const totals = filteredData.reduce((acc, stat) => {
          const passAttempts = stat.pass_attempts ?? stat.pass_att ?? 0
          const passCompleted = stat.pass_completed ?? stat.pass_comp ?? 0
          return {
            passAttempts: (acc.passAttempts || 0) + (Number(passAttempts) || 0),
            passCompleted: (acc.passCompleted || 0) + (Number(passCompleted) || 0),
            games: acc.games + 1,
          }
        }, { passAttempts: 0, passCompleted: 0, games: 0 })
        
        // Only return if we have meaningful data
        if (totals.passAttempts === 0) {
          return null
        }
        
        const passPct = totals.passAttempts > 0 ? (totals.passCompleted / totals.passAttempts) * 100 : 0
        return {
          ...totals,
          passPct: Number(passPct).toFixed(1),
          passAttemptsPerGame: totals.games > 0 ? Number(totals.passAttempts / totals.games).toFixed(1) : '0.0',
          passCompletedPerGame: totals.games > 0 ? Number(totals.passCompleted / totals.games).toFixed(1) : '0.0',
        }
      }).catch((error) => {
        console.error('Error in passing stats query:', error)
        return null
      }),
    
    // Situational stats (5v5, PP, PK) - query all columns
    supabase
      .from('fact_player_game_stats')
      .select('*')
      .eq('player_id', playerId)
      .then(({ data, error }) => {
        if (error) {
          console.error('Error fetching situational stats:', error)
          return null
        }
        if (!data || data.length === 0) return null
        
        let filteredData = data
        if (gameIds.length > 0) {
          filteredData = data.filter(stat => gameIds.includes(stat.game_id))
        }
        if (filteredData.length === 0) return null
        
        const totals = filteredData.reduce((acc, stat) => {
          const toi5v5 = stat.toi_5v5 ?? 0
          const goals5v5 = stat.goals_5v5 ?? 0
          const toiPP = stat.toi_pp ?? 0
          const goalsPP = stat.goals_pp ?? 0
          const toiPK = stat.toi_pk ?? 0
          const goalsPK = stat.goals_pk ?? 0
          return {
            toi5v5: (acc.toi5v5 || 0) + (Number(toi5v5) || 0),
            goals5v5: (acc.goals5v5 || 0) + (Number(goals5v5) || 0),
            toiPP: (acc.toiPP || 0) + (Number(toiPP) || 0),
            goalsPP: (acc.goalsPP || 0) + (Number(goalsPP) || 0),
            toiPK: (acc.toiPK || 0) + (Number(toiPK) || 0),
            goalsPK: (acc.goalsPK || 0) + (Number(goalsPK) || 0),
            games: acc.games + 1,
          }
        }, { toi5v5: 0, goals5v5: 0, toiPP: 0, goalsPP: 0, toiPK: 0, goalsPK: 0, games: 0 })
        
        // Only return if we have meaningful data
        if (totals.toi5v5 === 0 && totals.toiPP === 0 && totals.toiPK === 0) {
          return null
        }
        
        return {
          ...totals,
          toi5v5Minutes: Number(totals.toi5v5 / 60).toFixed(1),
          toiPPMinutes: Number(totals.toiPP / 60).toFixed(1),
          toiPKMinutes: Number(totals.toiPK / 60).toFixed(1),
          goals5v5Per60: totals.toi5v5 > 0 ? Number((totals.goals5v5 / totals.toi5v5) * 3600).toFixed(2) : '0.00',
          goalsPPPer60: totals.toiPP > 0 ? Number((totals.goalsPP / totals.toiPP) * 3600).toFixed(2) : '0.00',
        }
      }).catch((error) => {
        console.error('Error in situational stats query:', error)
        return null
      }),
    
    // Assist breakdown (Primary vs Secondary) - query all columns
    supabase
      .from('fact_player_game_stats')
      .select('*')
      .eq('player_id', playerId)
      .then(({ data, error }) => {
        if (error) {
          console.error('Error fetching assist breakdown stats:', error)
          return null
        }
        if (!data || data.length === 0) return null
        
        let filteredData = data
        if (gameIds.length > 0) {
          filteredData = data.filter(stat => gameIds.includes(stat.game_id))
        }
        if (filteredData.length === 0) return null
        
        const totals = filteredData.reduce((acc, stat) => {
          const primaryAssists = stat.primary_assists ?? stat.primary_assist ?? 0
          const secondaryAssists = stat.secondary_assists ?? stat.secondary_assist ?? 0
          const totalAssists = stat.assists ?? stat.a ?? 0
          return {
            primaryAssists: (acc.primaryAssists || 0) + (Number(primaryAssists) || 0),
            secondaryAssists: (acc.secondaryAssists || 0) + (Number(secondaryAssists) || 0),
            totalAssists: (acc.totalAssists || 0) + (Number(totalAssists) || 0),
            games: acc.games + 1,
          }
        }, { primaryAssists: 0, secondaryAssists: 0, totalAssists: 0, games: 0 })
        
        // Only return if we have meaningful data
        if (totals.totalAssists === 0) {
          return null
        }
        
        const primaryPct = totals.totalAssists > 0 ? (totals.primaryAssists / totals.totalAssists) * 100 : 0
        const secondaryPct = totals.totalAssists > 0 ? (totals.secondaryAssists / totals.totalAssists) * 100 : 0
        return {
          ...totals,
          primaryPct: Number(primaryPct).toFixed(1),
          secondaryPct: Number(secondaryPct).toFixed(1),
          primaryPerGame: totals.games > 0 ? Number(totals.primaryAssists / totals.games).toFixed(2) : '0.00',
          secondaryPerGame: totals.games > 0 ? Number(totals.secondaryAssists / totals.games).toFixed(2) : '0.00',
        }
      }).catch((error) => {
        console.error('Error in assist breakdown stats query:', error)
        return null
      }),
    
    // Micro stats (defensive events, puck battles, etc.) - query all columns
    supabase
      .from('fact_player_game_stats')
      .select('*')
      .eq('player_id', playerId)
      .then(({ data, error }) => {
        if (error) {
          console.error('Error fetching micro stats:', error)
          return null
        }
        if (!data || data.length === 0) return null
        
        let filteredData = data
        if (gameIds.length > 0) {
          filteredData = data.filter(stat => gameIds.includes(stat.game_id))
        }
        if (filteredData.length === 0) return null
        
        const totals = filteredData.reduce((acc, stat) => {
          const primaryDef = stat.primary_def_events ?? stat.primary_def ?? 0
          const supportDef = stat.support_def_events ?? stat.support_def ?? 0
          const defInvolvement = stat.def_involvement ?? 0
          const dekes = stat.dekes ?? 0
          const drivesTotal = stat.drives_total ?? ((stat.drives_middle ?? 0) + (stat.drives_wide ?? 0) + (stat.drives_corner ?? 0))
          const cutbacks = stat.cutbacks ?? 0
          const forechecks = stat.forechecks ?? stat.forecheck ?? 0
          const backchecks = stat.backchecks ?? stat.backcheck ?? 0
          const puckBattles = stat.puck_battles_total ?? stat.puck_battles ?? 0
          const loosePuckWins = stat.loose_puck_wins ?? stat.puck_recoveries ?? 0
          const cycles = stat.cycles ?? 0
          const giveAndGo = stat.give_and_go ?? 0
          const screens = stat.screens ?? 0
          const crashNet = stat.crash_net ?? 0
          
          return {
            primaryDef: (acc.primaryDef || 0) + (Number(primaryDef) || 0),
            supportDef: (acc.supportDef || 0) + (Number(supportDef) || 0),
            defInvolvement: (acc.defInvolvement || 0) + (Number(defInvolvement) || 0),
            dekes: (acc.dekes || 0) + (Number(dekes) || 0),
            drivesTotal: (acc.drivesTotal || 0) + (Number(drivesTotal) || 0),
            cutbacks: (acc.cutbacks || 0) + (Number(cutbacks) || 0),
            forechecks: (acc.forechecks || 0) + (Number(forechecks) || 0),
            backchecks: (acc.backchecks || 0) + (Number(backchecks) || 0),
            puckBattles: (acc.puckBattles || 0) + (Number(puckBattles) || 0),
            loosePuckWins: (acc.loosePuckWins || 0) + (Number(loosePuckWins) || 0),
            cycles: (acc.cycles || 0) + (Number(cycles) || 0),
            giveAndGo: (acc.giveAndGo || 0) + (Number(giveAndGo) || 0),
            screens: (acc.screens || 0) + (Number(screens) || 0),
            crashNet: (acc.crashNet || 0) + (Number(crashNet) || 0),
            games: acc.games + 1,
          }
        }, { 
          primaryDef: 0, supportDef: 0, defInvolvement: 0, dekes: 0, drivesTotal: 0, 
          cutbacks: 0, forechecks: 0, backchecks: 0, puckBattles: 0, loosePuckWins: 0,
          cycles: 0, giveAndGo: 0, screens: 0, crashNet: 0, games: 0
        })
        
        // Only return if we have meaningful data
        if (totals.primaryDef === 0 && totals.supportDef === 0 && totals.dekes === 0 && 
            totals.drivesTotal === 0 && totals.forechecks === 0 && totals.backchecks === 0 &&
            totals.puckBattles === 0) {
          return null
        }
        
        return {
          ...totals,
          primaryDefPerGame: totals.games > 0 ? Number(totals.primaryDef / totals.games).toFixed(1) : '0.0',
          supportDefPerGame: totals.games > 0 ? Number(totals.supportDef / totals.games).toFixed(1) : '0.0',
          dekesPerGame: totals.games > 0 ? Number(totals.dekes / totals.games).toFixed(1) : '0.0',
          drivesPerGame: totals.games > 0 ? Number(totals.drivesTotal / totals.games).toFixed(1) : '0.0',
          forechecksPerGame: totals.games > 0 ? Number(totals.forechecks / totals.games).toFixed(1) : '0.0',
          backchecksPerGame: totals.games > 0 ? Number(totals.backchecks / totals.games).toFixed(1) : '0.0',
          puckBattlesPerGame: totals.games > 0 ? Number(totals.puckBattles / totals.games).toFixed(1) : '0.0',
        }
      }).catch((error) => {
        console.error('Error in micro stats query:', error)
        return null
      }),
    
    // QoC (Quality of Competition) stats
    supabase
      .from('fact_player_qoc_summary')
      .select('*')
      .eq('player_id', playerId)
      .then(({ data, error }) => {
        if (error) {
          console.error('Error fetching QoC stats:', error)
          return null
        }
        if (!data || data.length === 0) return null
        
        let filteredData = data
        if (gameIds.length > 0) {
          filteredData = data.filter(stat => gameIds.includes(stat.game_id))
        }
        if (filteredData.length === 0) return null
        
        const totals = filteredData.reduce((acc, stat) => ({
          avgOppRating: acc.avgOppRating + (Number(stat.avg_opp_rating) || 0),
          avgOwnRating: acc.avgOwnRating + (Number(stat.avg_own_rating) || 0),
          ratingDiff: acc.ratingDiff + (Number(stat.rating_diff) || 0),
          shiftsTracked: acc.shiftsTracked + (Number(stat.shifts_tracked) || 0),
          games: acc.games + 1,
        }), { avgOppRating: 0, avgOwnRating: 0, ratingDiff: 0, shiftsTracked: 0, games: 0 })
        
        return {
          avgOppRating: totals.games > 0 ? Number(totals.avgOppRating / totals.games).toFixed(2) : '0.00',
          avgOwnRating: totals.games > 0 ? Number(totals.avgOwnRating / totals.games).toFixed(2) : '0.00',
          avgRatingDiff: totals.games > 0 ? Number(totals.ratingDiff / totals.games).toFixed(2) : '0.00',
          totalShifts: totals.shiftsTracked,
        }
      }).catch((error) => {
        console.error('Error in QoC stats query:', error)
        return null
      }),
  ])
  
    const hasAnyStats = possessionStats || zoneStats || warStats || physicalStats || shootingStats || per60Stats || faceoffStats || passingStats || situationalStats || assistBreakdownStats || microStats || qocStats
    
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
        <div className="space-y-4">
          {/* Offensive Stats Group */}
          <div className="bg-card rounded-xl border border-border overflow-hidden">
            <div className="px-4 py-3 bg-accent border-b border-border">
              <h3 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                <Target className="w-4 h-4" />
                Offensive Statistics
              </h3>
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
                  value={`${typeof possessionStats.cfPct === 'number' ? possessionStats.cfPct.toFixed(1) : possessionStats.cfPct || '0.0'}%`}
                  highlight
                  color="primary"
                  description="Corsi For Percentage - Shot attempts for vs against"
                  expandable={true}
                  expandedContent={
                    <GameStatDrilldown
                      playerId={playerId}
                      statKey="cf_pct"
                      statLabel="CF%"
                      gameIds={gameIds}
                    />
                  }
                  percentiles={possessionStats.percentiles?.cfPct}
                />
                <StatRow 
                  label="FF%" 
                  value={`${typeof possessionStats.ffPct === 'number' ? possessionStats.ffPct.toFixed(1) : possessionStats.ffPct || '0.0'}%`}
                  highlight
                  color="primary"
                  description="Fenwick For Percentage - Unblocked shot attempts for vs against"
                  expandable={true}
                  expandedContent={
                    <GameStatDrilldown
                      playerId={playerId}
                      statKey="ff_pct"
                      statLabel="FF%"
                      gameIds={gameIds}
                    />
                  }
                  percentiles={possessionStats.percentiles?.ffPct}
                />
                <div className="border-t border-border pt-2 mt-2">
                  <StatRow 
                    label="Corsi For" 
                    value={possessionStats.cf}
                    description="Total shot attempts (shots + blocks + misses) for"
                    expandable={true}
                    expandedContent={
                      <GameStatDrilldown
                        playerId={playerId}
                        statKey="corsi_for"
                        statLabel="CF"
                        gameIds={gameIds}
                      />
                    }
                  />
                  <StatRow 
                    label="Corsi Against" 
                    value={possessionStats.ca}
                    description="Total shot attempts against"
                    expandable={true}
                    expandedContent={
                      <GameStatDrilldown
                        playerId={playerId}
                        statKey="corsi_against"
                        statLabel="CA"
                        gameIds={gameIds}
                      />
                    }
                  />
                </div>
                <div className="border-t border-border pt-2 mt-2">
                  <StatRow 
                    label="Fenwick For" 
                    value={possessionStats.ff}
                    description="Unblocked shot attempts for"
                    expandable={true}
                    expandedContent={
                      <GameStatDrilldown
                        playerId={playerId}
                        statKey="fenwick_for"
                        statLabel="FF"
                        gameIds={gameIds}
                      />
                    }
                  />
                  <StatRow 
                    label="Fenwick Against" 
                    value={possessionStats.fa}
                    description="Unblocked shot attempts against"
                    expandable={true}
                    expandedContent={
                      <GameStatDrilldown
                        playerId={playerId}
                        statKey="fenwick_against"
                        statLabel="FA"
                        gameIds={gameIds}
                      />
                    }
                  />
                </div>
                <div className="border-t border-border pt-2 mt-2">
                  <StatRow 
                    label="Expected Goals" 
                    value={typeof possessionStats.xg === 'number' ? possessionStats.xg.toFixed(2) : possessionStats.xg || '0.00'}
                    description="Expected goals based on shot quality and location"
                    expandable={true}
                    expandedContent={
                      <GameStatDrilldown
                        playerId={playerId}
                        statKey="xg_for"
                        statLabel="xG"
                        gameIds={gameIds}
                      />
                    }
                    percentiles={possessionStats.percentiles?.xg}
                  />
                  <StatRow 
                    label="Goals - xG" 
                    value={`${possessionStats.xgDiff > 0 ? '+' : ''}${typeof possessionStats.xgDiff === 'number' ? possessionStats.xgDiff.toFixed(2) : possessionStats.xgDiff || '0.00'}`}
                    highlight
                    color={possessionStats.xgDiff > 0 ? 'save' : 'goal'}
                    description="Difference between actual goals and expected goals"
                  />
                </div>
                {(possessionStats.cfPctRel !== 0 || possessionStats.ffPctRel !== 0 || possessionStats.gfPct !== 0) && (
                  <div className="border-t border-border pt-2 mt-2">
                    <div className="text-xs font-semibold text-muted-foreground uppercase mb-1">Relative Stats</div>
                    {possessionStats.cfPctRel !== 0 && (
                      <StatRow 
                        label="CF% Rel" 
                        value={`${possessionStats.cfPctRel > 0 ? '+' : ''}${typeof possessionStats.cfPctRel === 'number' ? possessionStats.cfPctRel.toFixed(1) : possessionStats.cfPctRel || '0.0'}%`}
                        highlight
                        color={possessionStats.cfPctRel > 0 ? 'save' : possessionStats.cfPctRel < 0 ? 'goal' : 'muted'}
                        description="Corsi For % relative to team average"
                      />
                    )}
                    {possessionStats.ffPctRel !== 0 && (
                      <StatRow 
                        label="FF% Rel" 
                        value={`${possessionStats.ffPctRel > 0 ? '+' : ''}${typeof possessionStats.ffPctRel === 'number' ? possessionStats.ffPctRel.toFixed(1) : possessionStats.ffPctRel || '0.0'}%`}
                        highlight
                        color={possessionStats.ffPctRel > 0 ? 'save' : possessionStats.ffPctRel < 0 ? 'goal' : 'muted'}
                        description="Fenwick For % relative to team average"
                      />
                    )}
                    {possessionStats.gfPct !== 0 && (
                      <StatRow 
                        label="GF%" 
                        value={`${typeof possessionStats.gfPct === 'number' ? possessionStats.gfPct.toFixed(1) : possessionStats.gfPct || '0.0'}%`}
                        highlight
                        color="primary"
                        description="Goals For % - Goals for vs goals against when on ice"
                      />
                    )}
                  </div>
                )}
                {(possessionStats.plusEv !== 0 || possessionStats.minusEv !== 0 || possessionStats.plusMinusEv !== 0) && (
                  <div className="border-t border-border pt-2 mt-2">
                    <div className="text-xs font-semibold text-muted-foreground uppercase mb-1">Even Strength +/-</div>
                    <StatRow 
                      label="+/- (EV)" 
                      value={`${possessionStats.plusMinusEv > 0 ? '+' : ''}${possessionStats.plusMinusEv || 0}`}
                      highlight
                      color={possessionStats.plusMinusEv > 0 ? 'save' : possessionStats.plusMinusEv < 0 ? 'goal' : 'muted'}
                      description="Plus/minus at even strength only"
                    />
                    <StatRow 
                      label="Plus Events" 
                      value={possessionStats.plusEv || 0}
                      color="save"
                      description="Goals for while on ice at even strength"
                    />
                    <StatRow 
                      label="Minus Events" 
                      value={possessionStats.minusEv || 0}
                      color="goal"
                      description="Goals against while on ice at even strength"
                    />
                  </div>
                )}
              </div>
            </StatCard>
          )}
            </div>
            </div>
          </div>

          {/* Defensive Stats Group */}
          <div className="bg-card rounded-xl border border-border overflow-hidden">
            <div className="px-4 py-3 bg-accent border-b border-border">
              <h3 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                <Shield className="w-4 h-4" />
                Defensive Statistics
              </h3>
            </div>
            <div className="p-6">
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Zone Play */}
              {zoneStats && (
                <StatCard 
                  title="Zone Play" 
                  icon={<Zap className="w-4 h-4" />}
                  defaultExpanded={false}
                >
              <div className="space-y-1">
                <StatRow 
                  label="Zone Entry %" 
                  value={`${typeof zoneStats.zePct === 'number' ? zoneStats.zePct.toFixed(1) : zoneStats.zePct || '0.0'}%`}
                  highlight
                  color="primary"
                  description="Percentage of successful zone entries"
                  expandable={true}
                  expandedContent={
                    <GameStatDrilldown
                      playerId={playerId}
                      statKey="zone_entry_pct"
                      statLabel="Zone Entry %"
                      gameIds={gameIds}
                    />
                  }
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
                    value={`${typeof zoneStats.zxPct === 'number' ? zoneStats.zxPct.toFixed(1) : zoneStats.zxPct || '0.0'}%`}
                    highlight
                    color="primary"
                    description="Percentage of successful zone exits"
                    expandable={true}
                    expandedContent={
                      <GameStatDrilldown
                        playerId={playerId}
                        statKey="zone_exit_pct"
                        statLabel="Zone Exit %"
                        gameIds={gameIds}
                      />
                    }
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
              
              {/* Physical */}
              {physicalStats && (
                <StatCard 
                  title="Physical" 
                  icon={<Shield className="w-4 h-4" />}
                  defaultExpanded={false}
                >
              <div className="space-y-1">
                <StatRow 
                  label="Total WAR" 
                  value={warStats.totalWAR}
                  highlight
                  color="primary"
                  description="Wins Above Replacement - Total value added in wins"
                  expandable={true}
                  expandedContent={
                    <GameStatDrilldown
                      playerId={playerId}
                      statKey="war"
                      statLabel="WAR"
                      gameIds={gameIds}
                    />
                  }
                  percentiles={warStats.percentiles?.war}
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
                  {warStats.avgPerformanceIndex !== null && warStats.avgPerformanceIndex !== undefined && warStats.avgPerformanceIndex !== '0.00' && (
                    <StatRow 
                      label="Performance Index" 
                      value={warStats.avgPerformanceIndex}
                      highlight
                      description="Average performance index - overall impact metric"
                    />
                  )}
                  {warStats.avgAdjustedRating !== null && warStats.avgAdjustedRating !== undefined && warStats.avgAdjustedRating !== '0.0' && (
                    <StatRow 
                      label="Adjusted Rating" 
                      value={warStats.avgAdjustedRating}
                      description="Average adjusted rating accounting for competition"
                    />
                  )}
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
                  expandable={true}
                  expandedContent={
                    <GameStatDrilldown
                      playerId={playerId}
                      statKey="hits"
                      statLabel="Hits"
                      gameIds={gameIds}
                    />
                  }
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
                  expandable={true}
                  expandedContent={
                    <GameStatDrilldown
                      playerId={playerId}
                      statKey="blocks"
                      statLabel="Blocks"
                      gameIds={gameIds}
                    />
                  }
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
                    expandable={true}
                    expandedContent={
                      <GameStatDrilldown
                        playerId={playerId}
                        statKey="takeaways"
                        statLabel="Takeaways"
                        gameIds={gameIds}
                      />
                    }
                  />
                  <StatRow 
                    label="Bad Giveaways" 
                    value={physicalStats.giveaways}
                    color="goal"
                    description="Bad puck giveaways (turnovers)"
                    expandable={true}
                    expandedContent={
                      <GameStatDrilldown
                        playerId={playerId}
                        statKey="bad_giveaways"
                        statLabel="Bad Giveaways"
                        gameIds={gameIds}
                      />
                    }
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
            </div>
            </div>
          </div>

          {/* Special Teams Group */}
          <div className="bg-card rounded-xl border border-border overflow-hidden">
            <div className="px-4 py-3 bg-accent border-b border-border">
              <h3 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                <Users className="w-4 h-4" />
                Special Teams & Faceoffs
              </h3>
            </div>
            <div className="p-6">
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Faceoffs */}
              {faceoffStats && (
                <StatCard 
                  title="Faceoffs" 
                  icon={<Users className="w-4 h-4" />}
                  defaultExpanded={false}
                >
                  <div className="space-y-1">
                    <StatRow 
                      label="Faceoff %" 
                      value={`${faceoffStats.foPct}%`}
                      highlight
                      color="primary"
                      description="Faceoff win percentage"
                      expandable={true}
                      expandedContent={
                        <GameStatDrilldown
                          playerId={playerId}
                          statKey="fo_pct"
                          statLabel="Faceoff %"
                          gameIds={gameIds}
                        />
                      }
                    />
                    <StatRow 
                      label="Faceoff Wins" 
                      value={faceoffStats.foWins}
                      highlight
                      color="save"
                      description="Total faceoffs won"
                    />
                    <StatRow 
                      label="Faceoff Losses" 
                      value={faceoffStats.foLosses}
                      color="goal"
                      description="Total faceoffs lost"
                    />
                    <div className="border-t border-border pt-2 mt-2">
                      <StatRow 
                        label="Total Faceoffs" 
                        value={faceoffStats.foTotal}
                        description="Total faceoffs taken"
                      />
                      <StatRow 
                        label="Wins/Game" 
                        value={faceoffStats.foWinsPerGame}
                        description="Average faceoff wins per game"
                      />
                    </div>
                  </div>
                </StatCard>
              )}
              
              {/* Situational */}
              {situationalStats && (
                <StatCard 
                  title="Situational" 
                  icon={<Clock className="w-4 h-4" />}
                  defaultExpanded={false}
                >
                  <div className="space-y-1">
                    <div className="text-xs font-semibold text-muted-foreground uppercase mb-2">5v5</div>
                    <StatRow 
                      label="TOI (5v5)" 
                      value={`${situationalStats.toi5v5Minutes} min`}
                      description="Total time on ice at 5v5"
                    />
                    <StatRow 
                      label="Goals (5v5)" 
                      value={situationalStats.goals5v5}
                      highlight
                      color="goal"
                      description="Goals scored at 5v5"
                    />
                    <StatRow 
                      label="Goals/60 (5v5)" 
                      value={situationalStats.goals5v5Per60}
                      description="Goals per 60 minutes at 5v5"
                    />
                    <div className="border-t border-border pt-2 mt-2">
                      <div className="text-xs font-semibold text-muted-foreground uppercase mb-2">Power Play</div>
                      <StatRow 
                        label="TOI (PP)" 
                        value={`${situationalStats.toiPPMinutes} min`}
                        description="Total time on ice on power play"
                      />
                      <StatRow 
                        label="Goals (PP)" 
                        value={situationalStats.goalsPP}
                        highlight
                        color="goal"
                        description="Goals scored on power play"
                      />
                      <StatRow 
                        label="Goals/60 (PP)" 
                        value={situationalStats.goalsPPPer60}
                        description="Goals per 60 minutes on power play"
                      />
                    </div>
                    <div className="border-t border-border pt-2 mt-2">
                      <div className="text-xs font-semibold text-muted-foreground uppercase mb-2">Penalty Kill</div>
                      <StatRow 
                        label="TOI (PK)" 
                        value={`${situationalStats.toiPKMinutes} min`}
                        description="Total time on ice on penalty kill"
                      />
                      <StatRow 
                        label="Goals (PK)" 
                        value={situationalStats.goalsPK}
                        highlight
                        color="goal"
                        description="Goals scored while shorthanded"
                      />
                    </div>
                  </div>
                </StatCard>
              )}
            </div>
            </div>
          </div>

          {/* Advanced Metrics Group */}
          <div className="bg-card rounded-xl border border-border overflow-hidden">
            <div className="px-4 py-3 bg-accent border-b border-border">
              <h3 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                <TrendingUp className="w-4 h-4" />
                Advanced Metrics
              </h3>
            </div>
            <div className="p-6">
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* WAR/GAR */}
              {warStats && (
                <StatCard 
                  title="WAR/GAR" 
                  icon={<TrendingUp className="w-4 h-4" />}
                  defaultExpanded={false}
                >
              <div className="space-y-1">
                <StatRow 
                  label="Shooting %" 
                  value={`${shootingStats.shootingPct}%`}
                  highlight
                  color="primary"
                  description="Goals per shot on goal"
                  expandable={true}
                  expandedContent={
                    <GameStatDrilldown
                      playerId={playerId}
                      statKey="shooting_pct"
                      statLabel="Shooting %"
                      gameIds={gameIds}
                    />
                  }
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
                    expandable={true}
                    expandedContent={
                      <GameStatDrilldown
                        playerId={playerId}
                        statKey="shots"
                        statLabel="Shots"
                        gameIds={gameIds}
                      />
                    }
                  />
                  <StatRow 
                    label="Shots on Goal" 
                    value={shootingStats.sog}
                    description="Shots that reached the net"
                    expandable={true}
                    expandedContent={
                      <GameStatDrilldown
                        playerId={playerId}
                        statKey="sog"
                        statLabel="SOG"
                        gameIds={gameIds}
                      />
                    }
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
                {(shootingStats.shotsBlocked > 0 || shootingStats.shotsMissed > 0) && (
                  <div className="border-t border-border pt-2 mt-2">
                    <div className="text-xs font-semibold text-muted-foreground uppercase mb-1">Shot Breakdown</div>
                    {shootingStats.shotsBlocked > 0 && (
                      <StatRow 
                        label="Shots Blocked" 
                        value={shootingStats.shotsBlocked}
                        description="Total shots blocked by opponents"
                      />
                    )}
                    {shootingStats.shotsMissed > 0 && (
                      <StatRow 
                        label="Shots Missed" 
                        value={shootingStats.shotsMissed}
                        description="Total shots that missed the net"
                      />
                    )}
                    {shootingStats.shotsBlockedPerGame && shootingStats.shotsBlockedPerGame !== '0.0' && (
                      <StatRow 
                        label="Blocked/Game" 
                        value={shootingStats.shotsBlockedPerGame}
                        description="Average shots blocked per game"
                      />
                    )}
                    {shootingStats.shotsMissedPerGame && shootingStats.shotsMissedPerGame !== '0.0' && (
                      <StatRow 
                        label="Missed/Game" 
                        value={shootingStats.shotsMissedPerGame}
                        description="Average shots missed per game"
                      />
                    )}
                  </div>
                )}
              </div>
            </StatCard>
              )}
              
              {/* Per-60 Rates */}
              {per60Stats && (
                <StatCard 
                  title="Per 60 Rates" 
                  icon={<Target className="w-4 h-4" />}
                  defaultExpanded={false}
                >
              <div className="space-y-1">
                <StatRow 
                  label="Goals/60" 
                  value={per60Stats.goalsPer60}
                  highlight
                  color="goal"
                  description="Goals per 60 minutes of ice time"
                  expandable={true}
                  expandedContent={
                    <GameStatDrilldown
                      playerId={playerId}
                      statKey="goals_per_60"
                      statLabel="Goals/60"
                      gameIds={gameIds}
                    />
                  }
                />
                <StatRow 
                  label="Assists/60" 
                  value={per60Stats.assistsPer60}
                  highlight
                  color="assist"
                  description="Assists per 60 minutes of ice time"
                  expandable={true}
                  expandedContent={
                    <GameStatDrilldown
                      playerId={playerId}
                      statKey="assists_per_60"
                      statLabel="Assists/60"
                      gameIds={gameIds}
                    />
                  }
                />
                <StatRow 
                  label="Points/60" 
                  value={per60Stats.pointsPer60}
                  highlight
                  color="primary"
                  description="Points per 60 minutes of ice time"
                  expandable={true}
                  expandedContent={
                    <GameStatDrilldown
                      playerId={playerId}
                      statKey="points_per_60"
                      statLabel="Points/60"
                      gameIds={gameIds}
                    />
                  }
                />
                <div className="border-t border-border pt-2 mt-2">
                  <StatRow 
                    label="Avg TOI" 
                    value={`${per60Stats.avgTOI} min`}
                    description="Average time on ice per game"
                  />
                  {per60Stats.totalShifts > 0 && (
                    <>
                      <StatRow 
                        label="Total Shifts" 
                        value={per60Stats.totalShifts}
                        description="Total number of shifts taken"
                      />
                      {per60Stats.avgShiftsPerGame && per60Stats.avgShiftsPerGame !== '0.0' && (
                        <StatRow 
                          label="Shifts/Game" 
                          value={per60Stats.avgShiftsPerGame}
                          description="Average shifts per game"
                        />
                      )}
                      {per60Stats.avgShiftLength && per60Stats.avgShiftLength !== '0.00' && (
                        <StatRow 
                          label="Avg Shift Length" 
                          value={`${per60Stats.avgShiftLength} min`}
                          description="Average length of each shift"
                        />
                      )}
                    </>
                  )}
                </div>
              </div>
            </StatCard>
              )}
              
              {/* Passing */}
              {passingStats && (
                <StatCard 
                  title="Passing" 
                  icon={<Zap className="w-4 h-4" />}
                  defaultExpanded={false}
                >
              <div className="space-y-1">
                <StatRow 
                  label="Pass %" 
                  value={`${passingStats.passPct}%`}
                  highlight
                  color="primary"
                  description="Pass completion percentage"
                  expandable={true}
                  expandedContent={
                    <GameStatDrilldown
                      playerId={playerId}
                      statKey="pass_pct"
                      statLabel="Pass %"
                      gameIds={gameIds}
                    />
                  }
                />
                <StatRow 
                  label="Pass Attempts" 
                  value={passingStats.passAttempts}
                  description="Total pass attempts"
                />
                <StatRow 
                  label="Passes Completed" 
                  value={passingStats.passCompleted}
                  highlight
                  color="save"
                  description="Successful passes"
                />
                <div className="border-t border-border pt-2 mt-2">
                  <StatRow 
                    label="Attempts/Game" 
                    value={passingStats.passAttemptsPerGame}
                    description="Average pass attempts per game"
                  />
                  <StatRow 
                    label="Completed/Game" 
                    value={passingStats.passCompletedPerGame}
                    description="Average completed passes per game"
                  />
                </div>
              </div>
            </StatCard>
              )}
              
              {/* Assist Breakdown */}
              {assistBreakdownStats && (
                <StatCard 
                  title="Assist Breakdown" 
                  icon={<Sparkles className="w-4 h-4" />}
                  defaultExpanded={false}
                >
              <div className="space-y-1">
                <StatRow 
                  label="Primary Assists" 
                  value={assistBreakdownStats.primaryAssists}
                  highlight
                  color="assist"
                  description="First assist on a goal"
                />
                <StatRow 
                  label="Secondary Assists" 
                  value={assistBreakdownStats.secondaryAssists}
                  color="assist"
                  description="Second assist on a goal"
                />
                <div className="border-t border-border pt-2 mt-2">
                  <StatRow 
                    label="Primary %" 
                    value={`${assistBreakdownStats.primaryPct}%`}
                    highlight
                    description="Percentage of assists that are primary"
                  />
                  <StatRow 
                    label="Secondary %" 
                    value={`${assistBreakdownStats.secondaryPct}%`}
                    description="Percentage of assists that are secondary"
                  />
                </div>
                <div className="border-t border-border pt-2 mt-2">
                  <StatRow 
                    label="Primary/Game" 
                    value={assistBreakdownStats.primaryPerGame}
                    description="Average primary assists per game"
                  />
                  <StatRow 
                    label="Secondary/Game" 
                    value={assistBreakdownStats.secondaryPerGame}
                    description="Average secondary assists per game"
                  />
                </div>
              </div>
            </StatCard>
              )}
              
              {/* Micro Stats */}
              {microStats && (
                <StatCard 
                  title="Micro Stats" 
                  icon={<Activity className="w-4 h-4" />}
                  defaultExpanded={false}
                >
              <div className="space-y-1">
                <div className="text-xs font-semibold text-muted-foreground uppercase mb-2">Offensive</div>
                {microStats.dekes > 0 && (
                  <StatRow 
                    label="Dekes" 
                    value={microStats.dekes}
                    description="Total dekes attempted"
                  />
                )}
                {microStats.drivesTotal > 0 && (
                  <StatRow 
                    label="Drives" 
                    value={microStats.drivesTotal}
                    description="Total drives to the net"
                  />
                )}
                {microStats.cutbacks > 0 && (
                  <StatRow 
                    label="Cutbacks" 
                    value={microStats.cutbacks}
                    description="Cutback moves"
                  />
                )}
                {microStats.cycles > 0 && (
                  <StatRow 
                    label="Cycles" 
                    value={microStats.cycles}
                    description="Cycling plays"
                  />
                )}
                {microStats.giveAndGo > 0 && (
                  <StatRow 
                    label="Give & Go" 
                    value={microStats.giveAndGo}
                    description="Give and go plays"
                  />
                )}
                {microStats.screens > 0 && (
                  <StatRow 
                    label="Screens" 
                    value={microStats.screens}
                    description="Screens set"
                  />
                )}
                {microStats.crashNet > 0 && (
                  <StatRow 
                    label="Crash Net" 
                    value={microStats.crashNet}
                    description="Net crashes"
                  />
                )}
                
                {(microStats.forechecks > 0 || microStats.backchecks > 0) && (
                  <div className="border-t border-border pt-2 mt-2">
                    <div className="text-xs font-semibold text-muted-foreground uppercase mb-2">Defensive</div>
                    {microStats.forechecks > 0 && (
                      <StatRow 
                        label="Forechecks" 
                        value={microStats.forechecks}
                        color="save"
                        description="Forechecking plays"
                      />
                    )}
                    {microStats.backchecks > 0 && (
                      <StatRow 
                        label="Backchecks" 
                        value={microStats.backchecks}
                        color="save"
                        description="Backchecking plays"
                      />
                    )}
                    {microStats.primaryDef > 0 && (
                      <StatRow 
                        label="Primary Def Events" 
                        value={microStats.primaryDef}
                        highlight
                        color="save"
                        description="Primary defensive involvement"
                      />
                    )}
                    {microStats.supportDef > 0 && (
                      <StatRow 
                        label="Support Def Events" 
                        value={microStats.supportDef}
                        color="save"
                        description="Support defensive plays"
                      />
                    )}
                    {microStats.defInvolvement > 0 && (
                      <StatRow 
                        label="Def Involvement" 
                        value={microStats.defInvolvement}
                        highlight
                        color="save"
                        description="Total defensive involvement"
                      />
                    )}
                  </div>
                )}
                
                {microStats.puckBattles > 0 && (
                  <div className="border-t border-border pt-2 mt-2">
                    <div className="text-xs font-semibold text-muted-foreground uppercase mb-2">Puck Battles</div>
                    <StatRow 
                      label="Puck Battles" 
                      value={microStats.puckBattles}
                      highlight
                      description="Total puck battles"
                    />
                    {microStats.loosePuckWins > 0 && (
                      <StatRow 
                        label="Loose Puck Wins" 
                        value={microStats.loosePuckWins}
                        color="save"
                        description="Loose puck recoveries"
                      />
                    )}
                  </div>
                )}
              </div>
            </StatCard>
          )}
          
          {/* Situational */}
          {situationalStats && (
            <StatCard 
              title="Situational" 
              icon={<Clock className="w-4 h-4" />}
              defaultExpanded={true}
            >
              <div className="space-y-1">
                <div className="text-xs font-semibold text-muted-foreground uppercase mb-2">5v5</div>
                <StatRow 
                  label="TOI (5v5)" 
                  value={`${situationalStats.toi5v5Minutes} min`}
                  description="Total time on ice at 5v5"
                />
                <StatRow 
                  label="Goals (5v5)" 
                  value={situationalStats.goals5v5}
                  highlight
                  color="goal"
                  description="Goals scored at 5v5"
                />
                <StatRow 
                  label="Goals/60 (5v5)" 
                  value={situationalStats.goals5v5Per60}
                  description="Goals per 60 minutes at 5v5"
                />
                <div className="border-t border-border pt-2 mt-2">
                  <div className="text-xs font-semibold text-muted-foreground uppercase mb-2">Power Play</div>
                  <StatRow 
                    label="TOI (PP)" 
                    value={`${situationalStats.toiPPMinutes} min`}
                    description="Total time on ice on power play"
                  />
                  <StatRow 
                    label="Goals (PP)" 
                    value={situationalStats.goalsPP}
                    highlight
                    color="goal"
                    description="Goals scored on power play"
                  />
                  <StatRow 
                    label="Goals/60 (PP)" 
                    value={situationalStats.goalsPPPer60}
                    description="Goals per 60 minutes on power play"
                  />
                </div>
                <div className="border-t border-border pt-2 mt-2">
                  <div className="text-xs font-semibold text-muted-foreground uppercase mb-2">Penalty Kill</div>
                  <StatRow 
                    label="TOI (PK)" 
                    value={`${situationalStats.toiPKMinutes} min`}
                    description="Total time on ice on penalty kill"
                  />
                  <StatRow 
                    label="Goals (PK)" 
                    value={situationalStats.goalsPK}
                    highlight
                    color="goal"
                    description="Goals scored while shorthanded"
                  />
                </div>
              </div>
            </StatCard>
          )}
          
          {/* Quality of Competition */}
          {qocStats && (
            <StatCard 
              title="Quality of Competition" 
              icon={<TrendingUp className="w-4 h-4" />}
              defaultExpanded={true}
            >
              <div className="space-y-1">
                <StatRow 
                  label="Avg Opponent Rating" 
                  value={qocStats.avgOppRating}
                  description="Average skill rating of opponents faced"
                />
                <StatRow 
                  label="Avg Own Rating" 
                  value={qocStats.avgOwnRating}
                  description="Average player's own rating"
                />
                <StatRow 
                  label="Rating Differential" 
                  value={qocStats.avgRatingDiff}
                  description="Own rating minus opponent rating (positive = easier competition)"
                  color={Number(qocStats.avgRatingDiff) > 0 ? "goal" : "save"}
                />
                <StatRow 
                  label="Total Shifts Tracked" 
                  value={qocStats.totalShifts}
                  description="Number of shifts used for QoC calculation"
                />
              </div>
            </StatCard>
          )}
            </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    )
  } catch (error) {
    console.error('Error in PlayerAdvancedStatsSection:', error)
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
            Error loading advanced statistics. Please try refreshing the page.
          </p>
        </div>
      </div>
    )
  }
}

export default async function PlayerDetailPage({ 
  params,
  searchParams
}: { 
  params: Promise<{ playerId: string }>
  searchParams: Promise<{ season?: string; gameType?: string }>
}) {
  try {
    const { playerId } = await params
    const { season: selectedSeason, gameType: selectedGameType } = await searchParams
    
    if (!playerId) {
      notFound()
    }
    
    const supabase = await createClient()
    
    const [player, career] = await Promise.all([
      getPlayerById(playerId).catch(() => null),
      getPlayerCareerSummary(playerId).catch(() => null)
    ])
    
    if (!player) {
      notFound()
    }
  
  // Get available seasons for this player from fact_gameroster (more comprehensive)
  const { data: rosterSeasons } = await supabase
    .from('fact_gameroster')
    .select('season_id, season')
    .eq('player_id', playerId)
    .not('season_id', 'is', null)
  
  // Also get from fact_player_season_stats_basic as fallback
  const { data: statsSeasons } = await supabase
    .from('fact_player_season_stats_basic')
    .select('season_id, season')
    .eq('player_id', playerId)
  
  // Combine and deduplicate
  const allSeasonsData = [
    ...(rosterSeasons || []),
    ...(statsSeasons || [])
  ]
  
  const seasons = allSeasonsData.length > 0
    ? [...new Map(allSeasonsData.map(s => [s.season_id, s])).values()]
        .filter(s => {
          const seasonStr = String(s.season || '')
          return !seasonStr.toLowerCase().includes('summer')
        })
        .sort((a, b) => {
          // Sort by season (descending - most recent first)
          const seasonA = typeof a.season === 'number' ? a.season : parseInt(String(a.season || '0'))
          const seasonB = typeof b.season === 'number' ? b.season : parseInt(String(b.season || '0'))
          return seasonB - seasonA
        })
    : []
  
  // Get current season (latest)
  const currentSeason = seasons[0]?.season_id || ''
  const seasonId = selectedSeason || currentSeason
  const gameType = selectedGameType || 'All' // 'All', 'Regular', 'Playoffs'
  
  // Get game IDs from schedule first (needed for filtering)
  // Only filter by season_id if we have one
  const scheduleQuery = supabase
    .from('dim_schedule')
    .select('game_id, season_id, game_type, date')
  
  const { data: scheduleForGames } = seasonId 
    ? await scheduleQuery.eq('season_id', seasonId)
    : await scheduleQuery
  
  // Filter by game_type if not 'All'
  const filteredSchedule = gameType === 'All' 
    ? scheduleForGames 
    : scheduleForGames?.filter(s => s.game_type === gameType) || []
  
  const gameIdsForLog = filteredSchedule?.map(g => g.game_id) || []
  
  // Check what positions the player has actually played in games (from fact_gameroster)
  // Do this early so we know what stats to fetch
  const { data: playerPositionsData } = await supabase
    .from('fact_gameroster')
    .select('player_position')
    .eq('player_id', playerId)
    .not('player_position', 'is', null)
  
  // Determine positions played
  const positionsPlayed = new Set<string>()
  if (playerPositionsData) {
    playerPositionsData.forEach(gr => {
      const pos = String(gr.player_position || '').toLowerCase()
      if (pos.includes('goalie') || pos === 'g') {
        positionsPlayed.add('goalie')
      } else if (pos && pos !== 'goalie' && pos !== 'g') {
        positionsPlayed.add('skater')
      }
    })
  }
  
  // Fallback to primary position if no game roster data
  if (positionsPlayed.size === 0 && player.player_primary_position) {
    const primaryPos = player.player_primary_position.toLowerCase()
    if (primaryPos.includes('goalie')) {
      positionsPlayed.add('goalie')
    } else {
      positionsPlayed.add('skater')
    }
  }
  
  const hasPlayedGoalie = positionsPlayed.has('goalie')
  const hasPlayedSkater = positionsPlayed.has('skater')
  const isBoth = hasPlayedGoalie && hasPlayedSkater
  
  // Get player stats for selected season/game type (only if they've played as skater)
  let playerStats: any = null
  
  // Only fetch skater stats if player has played as skater
  if (hasPlayedSkater) {
    // Try fact_player_season_stats_basic first (has season_id and game_type)
    const { data: seasonStats } = await supabase
      .from('fact_player_season_stats_basic')
      .select('*')
      .eq('player_id', playerId)
      .eq('season_id', seasonId)
      .eq('game_type', gameType === 'All' ? 'All' : gameType)
      .maybeSingle()
    
    if (seasonStats) {
      playerStats = seasonStats
    } else if (seasonId === currentSeason) {
      // Fallback to current view if no season stats found
      const { data: currentStats } = await supabase
        .from('v_rankings_players_current')
        .select('*')
        .eq('player_id', playerId)
        .maybeSingle()
      
      if (currentStats) {
        playerStats = currentStats
      }
    }
    
    // If still no stats, try aggregating from game stats
    if (!playerStats && gameIdsForLog.length > 0) {
      const { data: gameStats } = await supabase
        .from('fact_player_game_stats')
        .select('g, a, pts, sog, pim, plus_minus, goals, assists, points, shots, shooting_pct')
        .eq('player_id', playerId)
        .in('game_id', gameIdsForLog)
      
      if (gameStats && gameStats.length > 0) {
        const totals = gameStats.reduce((acc, stat) => ({
          games_played: acc.games_played + 1,
          goals: (acc.goals || 0) + (parseFloat(String(stat.goals || stat.g || 0)) || 0),
          assists: (acc.assists || 0) + (parseFloat(String(stat.assists || stat.a || 0)) || 0),
          points: (acc.points || 0) + (parseFloat(String(stat.points || stat.pts || 0)) || 0),
          shots: (acc.shots || 0) + (parseFloat(String(stat.shots || stat.sog || 0)) || 0),
          pim: (acc.pim || 0) + (parseFloat(String(stat.pim || 0)) || 0),
          plus_minus: (acc.plus_minus || 0) + (parseFloat(String(stat.plus_minus || 0)) || 0),
        }), { games_played: 0, goals: 0, assists: 0, points: 0, shots: 0, pim: 0, plus_minus: 0 })
        
        playerStats = {
          ...totals,
          points_per_game: totals.games_played > 0 ? (totals.points / totals.games_played) : 0,
          shooting_pct: totals.shots > 0 ? (totals.goals / totals.shots) : 0,
        }
      }
    }
  }
  
  // Get ALL recent games (not filtered by season/game type) for recent games section
  // This will show the most recent games regardless of filters
  let allRecentGames: any[] = []
  
  // Fetch all recent games from fact_gameroster (most comprehensive)
  const { data: allRecentRosterData } = await supabase
    .from('fact_gameroster')
    .select('*')
    .eq('player_id', playerId)
    .order('game_id', { ascending: false })
    .limit(100)
  
  if (allRecentRosterData && allRecentRosterData.length > 0) {
    const allRecentGameIds = allRecentRosterData.map(r => r.game_id)
    const { data: allRecentSchedule } = await supabase
      .from('dim_schedule')
      .select('*')
      .in('game_id', allRecentGameIds)
    
    const allRecentScheduleMap = new Map((allRecentSchedule || []).map(s => [s.game_id, s]))
    
    allRecentGames = allRecentRosterData.map(roster => {
      const schedule = allRecentScheduleMap.get(roster.game_id)
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
  }
  
  // Get game log for selected season/game type (for stats/advanced analytics)
  // Priority: fact_player_game_stats > fact_gameroster + dim_schedule
  let gameLog: any[] = []
  
  if (gameIdsForLog.length > 0) {
    // Try advanced stats first
    const { data: gameLogData, error: gameLogError } = await supabase
      .from('fact_player_game_stats')
      .select('*')
      .eq('player_id', playerId)
      .in('game_id', gameIdsForLog)
      .order('game_id', { ascending: false })
      .limit(50)
    
    if (gameLogData && gameLogData.length > 0) {
      // Merge with schedule data to get dates and scores
      gameLog = gameLogData.map(game => {
        const scheduleInfo = filteredSchedule?.find(s => s.game_id === game.game_id)
        return {
          ...game,
          date: scheduleInfo?.date || game.date,
          home_team_name: scheduleInfo?.home_team_name || game.home_team_name,
          away_team_name: scheduleInfo?.away_team_name || game.away_team_name,
          home_total_goals: scheduleInfo?.home_total_goals ?? game.home_total_goals,
          away_total_goals: scheduleInfo?.away_total_goals ?? game.away_total_goals,
        }
      }).sort((a, b) => {
        const dateA = a.date ? new Date(a.date).getTime() : 0
        const dateB = b.date ? new Date(b.date).getTime() : 0
        return dateB - dateA
      })
    } else {
      // Fallback to fact_gameroster + dim_schedule
      const { data: rosterData } = await supabase
        .from('fact_gameroster')
        .select('*')
        .eq('player_id', playerId)
        .in('game_id', gameIdsForLog)
        .order('game_id', { ascending: false })
        .limit(50)
      
      if (rosterData && rosterData.length > 0) {
        const rosterGameIds = rosterData.map(r => r.game_id)
        const { data: scheduleForRoster } = await supabase
          .from('dim_schedule')
          .select('*')
          .in('game_id', rosterGameIds)
        
        const scheduleMap = new Map((scheduleForRoster || []).map(s => [s.game_id, s]))
        
        gameLog = rosterData.map(roster => {
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
            home_team_name: schedule?.home_team_name,
            away_team_name: schedule?.away_team_name,
            home_total_goals: schedule?.home_total_goals ?? null,
            away_total_goals: schedule?.away_total_goals ?? null,
            goals: goals,
            assists: assists,
            points: points,
            shots: null, // Not in gameroster
            sog: null,
            plus_minus: null,
            toi_seconds: null,
            cf_pct: null,
            // Mark as basic stats
            _source: 'gameroster'
          }
        }).sort((a, b) => {
          const dateA = a.date ? new Date(a.date).getTime() : 0
          const dateB = b.date ? new Date(b.date).getTime() : 0
          return dateB - dateA
        })
      }
    }
  } else {
    // Fallback: try to get any game stats for this player (no season/game type filter)
    // Try advanced stats first
    const { data: gameLogData } = await supabase
      .from('fact_player_game_stats')
      .select('*')
      .eq('player_id', playerId)
      .order('game_id', { ascending: false })
      .limit(50)
    
    if (gameLogData && gameLogData.length > 0) {
      // Get schedule data for scores
      const gameIds = gameLogData.map(g => g.game_id)
      const { data: scheduleData } = await supabase
        .from('dim_schedule')
        .select('*')
        .in('game_id', gameIds)
      
      const scheduleMap = new Map((scheduleData || []).map(s => [s.game_id, s]))
      
      gameLog = gameLogData.map(game => {
        const schedule = scheduleMap.get(game.game_id)
        return {
          ...game,
          date: schedule?.date || game.date,
          home_team_name: schedule?.home_team_name || game.home_team_name,
          away_team_name: schedule?.away_team_name || game.away_team_name,
          home_total_goals: schedule?.home_total_goals ?? game.home_total_goals,
          away_total_goals: schedule?.away_total_goals ?? game.away_total_goals,
        }
      }).sort((a, b) => {
        const dateA = a.date ? new Date(a.date).getTime() : 0
        const dateB = b.date ? new Date(b.date).getTime() : 0
        return dateB - dateA
      })
    } else {
      // Fallback to gameroster
      const { data: rosterData } = await supabase
        .from('fact_gameroster')
        .select('*')
        .eq('player_id', playerId)
        .order('game_id', { ascending: false })
        .limit(50)
      
      if (rosterData && rosterData.length > 0) {
        const rosterGameIds = rosterData.map(r => r.game_id)
        const { data: scheduleForRoster } = await supabase
          .from('dim_schedule')
          .select('*')
          .in('game_id', rosterGameIds)
        
        const scheduleMap = new Map((scheduleForRoster || []).map(s => [s.game_id, s]))
        
        gameLog = rosterData.map(roster => {
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
      }
    }
  }
  
  // Get current team info (use player_norad_current_team_id if available, otherwise team_id)
  const currentTeamId = player.player_norad_current_team_id || player.team_id || playerStats?.team_id
  const teamInfo = currentTeamId ? await getTeamById(String(currentTeamId)).catch(() => null) : null
  
  // Get opponent teams for game cards - include both gameLog and allRecentGames
  const allOpponentNames = [
    ...new Set([
      ...gameLog.slice(0, 6).map((g: any) => g.opponent_team_name || g.team_name),
      ...allRecentGames.slice(0, 6).map((g: any) => g.opponent_team_name || g.team_name)
    ].filter(Boolean))
  ]
  const opponentTeams = await Promise.all(
    allOpponentNames.map(name => {
      const teamName = String(name).replace(/\s+/g, ' ')
      return supabase
        .from('dim_team')
        .select('*')
        .eq('team_name', teamName)
        .maybeSingle()
        .then(({ data }) => data)
        .catch(() => null)
    })
  )
  const opponentTeamsMap = new Map(
    opponentTeams.filter(Boolean).map(t => [t!.team_name, t!])
  )
  
  // Also get player's team info for team logos
  const playerTeamName = player.player_norad_current_team || player.team_name
  let playerTeamInfo: any = null
  if (playerTeamName) {
    const { data: playerTeamData } = await supabase
      .from('dim_team')
      .select('*')
      .eq('team_name', playerTeamName)
      .maybeSingle()
    playerTeamInfo = playerTeamData
  }
  
  // Fetch year-by-year stats for career tab (includes team_id and team_name)
  // Fetch All, Regular, and Playoff stats separately
  const [allStatsResult, regularStatsResult, playoffStatsResult] = await Promise.all([
    supabase
      .from('fact_player_season_stats_basic')
      .select('season_id, season, team_id, team_name, games_played, goals, assists, points, pim')
      .eq('player_id', playerId)
      .eq('game_type', 'All')
      .order('season', { ascending: false }),
    supabase
      .from('fact_player_season_stats_basic')
      .select('season_id, season, team_id, team_name, games_played, goals, assists, points, pim')
      .eq('player_id', playerId)
      .eq('game_type', 'Regular')
      .order('season', { ascending: false }),
    supabase
      .from('fact_player_season_stats_basic')
      .select('season_id, season, team_id, team_name, games_played, goals, assists, points, pim')
      .eq('player_id', playerId)
      .eq('game_type', 'Playoffs')
      .order('season', { ascending: false }),
  ])
  
  const seasonStatsForCareer = allStatsResult.data || []
  const regularSeasonStats = regularStatsResult.data || []
  const playoffSeasonStats = playoffStatsResult.data || []
  
  // Fetch average ratings by season from fact_gameroster
  const { data: gameRosterRatings } = await supabase
    .from('fact_gameroster')
    .select('season_id, player_skill_rating')
    .eq('player_id', playerId)
    .not('player_skill_rating', 'is', null)
  
  // Calculate average rating per season
  const ratingsBySeason = new Map<string, { total: number; count: number }>()
  if (gameRosterRatings) {
    gameRosterRatings.forEach(gr => {
      const seasonId = gr.season_id
      const rating = Number(gr.player_skill_rating)
      if (seasonId && !isNaN(rating)) {
        const existing = ratingsBySeason.get(seasonId) || { total: 0, count: 0 }
        ratingsBySeason.set(seasonId, {
          total: existing.total + rating,
          count: existing.count + 1,
        })
      }
    })
  }
  
  const avgRatingsBySeason = new Map<string, number>()
  ratingsBySeason.forEach((value, seasonId) => {
    if (value.count > 0) {
      avgRatingsBySeason.set(seasonId, value.total / value.count)
    }
  })
  
  // Get team details for logos
  let seasonStatsWithTeams: any[] = []
  if (seasonStatsForCareer && seasonStatsForCareer.length > 0) {
    const allTeamIds = [...new Set((seasonStatsForCareer || [])
      .map(s => s.team_id)
      .filter(Boolean))]
    
    const { data: teamsData } = await supabase
      .from('dim_team')
      .select('team_id, team_name, team_logo, team_cd')
      .in('team_id', allTeamIds)
    
    const teamsMap = new Map((teamsData || []).map(t => [String(t.team_id), t]))
    
    // Merge season stats with team details and add ratings
    seasonStatsWithTeams = (seasonStatsForCareer || []).map(stat => {
      const teamDetails = stat.team_id ? teamsMap.get(String(stat.team_id)) : null
      const avgRating = avgRatingsBySeason.get(stat.season_id)
      return {
        ...stat,
        team_name: teamDetails?.team_name || stat.team_name || null,
        team_logo: teamDetails?.team_logo,
        team_cd: teamDetails?.team_cd,
        avg_rating: avgRating || null,
      }
    })
  }
  
  // Fetch goalie stats if player has played as goalie
  let goalieStats: any = null
  let goalieSeasonStatsForCareer: any[] = []
  
  if (hasPlayedGoalie) {
    // Fetch goalie stats for selected season/game type
    const { data: goalieSeasonStats } = await supabase
      .from('fact_goalie_season_stats_basic')
      .select('*')
      .eq('player_id', playerId)
      .eq('season_id', seasonId)
      .eq('game_type', gameType === 'All' ? 'All' : gameType)
      .maybeSingle()
    
    if (goalieSeasonStats) {
      goalieStats = goalieSeasonStats
    }
    
    // Fetch goalie career stats
    const { data: goalieCareerStats } = await supabase
      .from('fact_goalie_season_stats_basic')
      .select('season_id, season, games_played, goals_against, gaa, wins, losses, shutouts, team_id, team_name')
      .eq('player_id', playerId)
      .eq('game_type', 'All')
      .order('season', { ascending: false })
    
    goalieSeasonStatsForCareer = goalieCareerStats || []
    
    // Also fetch goalie game stats to calculate saves and shots_against for save percentage
    if (goalieSeasonStatsForCareer.length > 0) {
      const { data: goalieGameStats } = await supabase
        .from('fact_goalie_game_stats')
        .select('game_id, saves, shots_against, save_pct')
        .eq('player_id', playerId)
      
      // Get schedule to match by season
      if (goalieGameStats && goalieGameStats.length > 0) {
        const goalieGameIds = goalieGameStats.map(g => g.game_id)
        const { data: goalieSchedule } = await supabase
          .from('dim_schedule')
          .select('game_id, season_id')
          .in('game_id', goalieGameIds)
        
        const scheduleMap = new Map((goalieSchedule || []).map(s => [s.game_id, s.season_id]))
        
        // Aggregate saves and shots_against by season
        const savesBySeason = new Map<string, { saves: number; shots_against: number }>()
        goalieGameStats.forEach(stat => {
          const seasonId = scheduleMap.get(stat.game_id)
          if (seasonId) {
            const existing = savesBySeason.get(seasonId) || { saves: 0, shots_against: 0 }
            savesBySeason.set(seasonId, {
              saves: existing.saves + (Number(stat.saves) || 0),
              shots_against: existing.shots_against + (Number(stat.shots_against) || 0),
            })
          }
        })
        
        // Merge saves data into goalie season stats
        goalieSeasonStatsForCareer = goalieSeasonStatsForCareer.map(stat => {
          const savesData = savesBySeason.get(stat.season_id)
          return {
            ...stat,
            saves: savesData?.saves || 0,
            shots_against: savesData?.shots_against || 0,
            save_percent: savesData && savesData.shots_against > 0
              ? (savesData.saves / savesData.shots_against) * 100
              : null,
          }
        })
      }
    }
  }
  
  // Get player shots for shot map
  let playerShots: any[] = []
  try {
    const shotsData = await getPlayerShots(playerId, 100)
    playerShots = shotsData.map(shot => ({
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
    }))
  } catch (error) {
    console.error('Error fetching player shots:', error)
  }
  
  // Get prior teams with full stats (5+ games per team per season)
  let priorTeams: any[] = []
  let careerTotals: any = {
    games_played: 0,
    goals: 0,
    assists: 0,
    points: 0,
    pim: 0,
  }
  
  try {
    // Fetch all game roster data with stats and ratings
    const { data: allGameRoster } = await supabase
      .from('fact_gameroster')
      .select('team_id, team_name, season_id, game_id, goals, assist, points, pim, pim_total, skill_rating')
      .eq('player_id', playerId)
      .not('season_id', 'is', null)
      .not('team_id', 'is', null)
    
    if (allGameRoster && allGameRoster.length > 0) {
      // Aggregate stats per team per season (including ratings)
      const teamSeasonStats = new Map<string, {
        games: number
        goals: number
        assists: number
        points: number
        pim: number
        team_name: string
        ratings: number[] // Array of ratings for averaging
      }>()
      
      allGameRoster.forEach(gr => {
        const key = `${gr.season_id}|${gr.team_id}`
        const existing = teamSeasonStats.get(key) || {
          games: 0,
          goals: 0,
          assists: 0,
          points: 0,
          pim: 0,
          team_name: gr.team_name || '',
          ratings: [],
        }
        
        // Get rating for this game from fact_gameroster
        const gameRating = gr.skill_rating ? Number(gr.skill_rating) : null
        if (gameRating && !isNaN(gameRating) && gameRating > 0) {
          existing.ratings.push(gameRating)
        }
        
        teamSeasonStats.set(key, {
          games: existing.games + 1,
          goals: existing.goals + (Number(gr.goals) || 0),
          assists: existing.assists + (Number(gr.assist) || 0),
          points: existing.points + (Number(gr.points) || (Number(gr.goals) || 0) + (Number(gr.assist) || 0)),
          pim: existing.pim + (Number(gr.pim ?? gr.pim_total) || 0),
          team_name: existing.team_name || gr.team_name || '',
          ratings: existing.ratings,
        })
      })
      
      // Filter to only teams with 5+ games and group by season
      const seasonTeams = new Map<string, Array<{
        team_id: string
        team_name: string
        games: number
        goals: number
        assists: number
        points: number
        pim: number
        avg_rating: number | null
      }>>()
      
      teamSeasonStats.forEach((stats, key) => {
        if (stats.games >= 5) {
          const [seasonId, teamId] = key.split('|')
          
          // Calculate average rating for this team/season
          const avgRating = stats.ratings.length > 0
            ? stats.ratings.reduce((sum, r) => sum + r, 0) / stats.ratings.length
            : null
          
          if (!seasonTeams.has(seasonId)) {
            seasonTeams.set(seasonId, [])
          }
          seasonTeams.get(seasonId)!.push({
            team_id: teamId,
            team_name: stats.team_name,
            games: stats.games,
            goals: stats.goals,
            assists: stats.assists,
            points: stats.points,
            pim: stats.pim,
            avg_rating: avgRating,
          })
          
          // Add to career totals
          careerTotals.games_played += stats.games
          careerTotals.goals += stats.goals
          careerTotals.assists += stats.assists
          careerTotals.points += stats.points
          careerTotals.pim += stats.pim
        }
      })
      
      // Get season info and team details
      const seasonIds = Array.from(seasonTeams.keys())
      const { data: seasonData } = await supabase
        .from('dim_schedule')
        .select('season_id, season')
        .in('season_id', seasonIds)
      
      const seasonMap = new Map((seasonData || []).map(s => [s.season_id, s.season]))
      
      // Get team details
      const allTeamIds = [...new Set(Array.from(seasonTeams.values()).flat().map(t => t.team_id))]
      const { data: teamsData } = await supabase
        .from('dim_team')
        .select('team_id, team_name, team_logo, team_cd, primary_color, team_color1, team_color2')
        .in('team_id', allTeamIds)
      
      const teamsMap = new Map((teamsData || []).map(t => [String(t.team_id), t]))
      
      // Build prior teams list with stats
      priorTeams = Array.from(seasonTeams.entries())
        .map(([seasonId, teams]) => {
          const season = seasonMap.get(seasonId) || seasonId
          const isFreeAgent = teams.length > 1
          
          // Calculate season totals (if multiple teams)
          // For average rating, calculate weighted average by games played
          const seasonTotals = teams.reduce((acc, team) => {
            const totalGames = acc.games + team.games
            const weightedRating = team.avg_rating && team.games > 0
              ? (acc.avg_rating || 0) * (acc.games / totalGames) + team.avg_rating * (team.games / totalGames)
              : acc.avg_rating || team.avg_rating || null
            
            return {
              games: totalGames,
              goals: acc.goals + team.goals,
              assists: acc.assists + team.assists,
              points: acc.points + team.points,
              pim: acc.pim + team.pim,
              avg_rating: weightedRating,
            }
          }, { games: 0, goals: 0, assists: 0, points: 0, pim: 0, avg_rating: null as number | null })
          
          return {
            season_id: seasonId,
            season,
            is_free_agent: isFreeAgent,
            season_totals: seasonTotals,
            teams: teams.map(t => ({
              ...t,
              team_info: teamsMap.get(t.team_id) || null,
            })),
          }
        })
        .sort((a, b) => {
          // Sort by season (descending - most recent first)
          const seasonA = typeof a.season === 'number' ? a.season : parseInt(String(a.season || '0'))
          const seasonB = typeof b.season === 'number' ? b.season : parseInt(String(b.season || '0'))
          return seasonB - seasonA
        })
    }
  } catch (error) {
    console.error('Error fetching prior teams:', error)
  }
  
  return (
    <div className="space-y-6">
      {/* Back Link */}
      <Link 
        href="/norad/players" 
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Players
      </Link>
      
      {/* Player Header */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="bg-gradient-to-r from-primary/10 via-transparent to-primary/10 p-6">
          <div className="flex items-start gap-6">
            {/* Player Photo with Rating and Jersey */}
            <div className="flex flex-col items-center gap-3">
              <PlayerPhoto
                src={player.player_image || null}
                name={player.player_full_name || player.player_name || ''}
                primaryColor={teamInfo?.primary_color || teamInfo?.team_color1}
                size="2xl"
              />
              <div className="flex flex-col items-center gap-1">
                {player.jersey_number && (
                  <span className="text-lg font-mono font-bold text-foreground">
                    #{player.jersey_number}
                  </span>
                )}
                {player.current_skill_rating && (
                  <span className="text-sm font-mono text-primary font-semibold">
                    Rating: {Math.round(Number(player.current_skill_rating))}
                  </span>
                )}
              </div>
            </div>
            
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-3">
                    <h1 className="font-display text-3xl font-bold text-foreground">
                      {player.player_full_name || player.player_name}
                    </h1>
                    {player.player_url && (
                      <a
                        href={player.player_url}
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
                  <div className="flex items-center gap-4 mt-3">
                    {teamInfo && (
                      <Link 
                        href={teamInfo ? `/norad/team/${(teamInfo.team_name || '').replace(/\s+/g, '_')}` : '#'}
                        className="flex items-center gap-2 text-sm text-foreground hover:text-primary transition-colors"
                      >
                        <TeamLogo
                          src={teamInfo.team_logo || null}
                          name={teamInfo.team_name || ''}
                          abbrev={teamInfo.team_cd}
                          primaryColor={teamInfo.primary_color || teamInfo.team_color1}
                          secondaryColor={teamInfo.team_color2}
                          size="sm"
                        />
                        <span>{player.player_norad_current_team || teamInfo.team_name || player.team_name}</span>
                      </Link>
                    )}
                    {player.player_primary_position && (
                      <span className="text-xs font-mono bg-accent px-2 py-1 rounded uppercase">
                        {player.player_primary_position}
                      </span>
                    )}
                  </div>
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
      
      {/* Player Info Section */}
      <CollapsibleSection
        title="Player Info"
        icon={<Info className="w-4 h-4" />}
        defaultExpanded={true}
      >
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Birth Year</div>
              <div className="font-mono text-lg font-semibold text-foreground">
                {player.birth_year ? (
                  <>
                    {player.birth_year}
                    {(() => {
                      const currentYear = new Date().getFullYear()
                      const age = currentYear - Number(player.birth_year)
                      return age > 0 && age < 150 ? ` (Age ${age})` : ''
                    })()}
                  </>
                ) : (
                  'na'
                )}
              </div>
            </div>
              {player.player_gender && (
                <div>
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Gender</div>
                  <div className="font-display text-lg font-semibold text-foreground">
                    {player.player_gender}
                  </div>
                </div>
              )}
              {player.player_primary_position && (
                <div>
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Position</div>
                  <div className="font-display text-lg font-semibold text-foreground">
                    {player.player_primary_position}
                  </div>
                </div>
              )}
              {player.highest_beer_league && (
                <div>
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Highest Beer League</div>
                  <div className="font-display text-lg font-semibold text-foreground">
                    {player.highest_beer_league}
                  </div>
                </div>
              )}
              {player.current_skill_rating && (
                <div>
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Current Rating</div>
                  <div className="font-mono text-lg font-semibold text-primary">
                    {Math.round(Number(player.current_skill_rating))}
                  </div>
                </div>
              )}
              {player.player_rating_ly && (
                <div>
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Last Year's Rating</div>
                  <div className="font-mono text-lg font-semibold text-muted-foreground">
                    {player.player_rating_ly}
                  </div>
                </div>
              )}
              {player.other_url && (
                <div className="md:col-span-2 lg:col-span-3">
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-1">External Link</div>
                  <a
                    href={player.other_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 text-sm text-primary hover:underline"
                  >
                    <ExternalLink className="w-4 h-4" />
                    <span>{player.other_url}</span>
                  </a>
                </div>
              )}
            </div>
          </div>
        </CollapsibleSection>
      
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
      
      {/* Quick Stats (Season Summary) - Moved above Career Stats */}
      {hasPlayedSkater && playerStats && (
        <CollapsibleSection
          title={isBoth ? "Quick Stats - Skater" : "Quick Stats"}
          icon={<TrendingUp className="w-4 h-4" />}
          defaultExpanded={true}
        >
          <div className="p-6">
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-card rounded-lg p-4 border border-border">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Games Played</div>
                <div className="font-mono text-2xl font-bold text-foreground">{playerStats.games_played || 0}</div>
              </div>
              <div className="bg-card rounded-lg p-4 border border-border">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Goals</div>
                <div className="font-mono text-2xl font-bold text-goal">{playerStats.goals || 0}</div>
              </div>
              <div className="bg-card rounded-lg p-4 border border-border">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Assists</div>
                <div className="font-mono text-2xl font-bold text-assist">{playerStats.assists || 0}</div>
              </div>
              <div className="bg-card rounded-lg p-4 border border-border">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Points</div>
                <div className="font-mono text-2xl font-bold text-primary">{playerStats.points || 0}</div>
              </div>
            </div>
          </div>
        </CollapsibleSection>
      )}
      
      {hasPlayedGoalie && goalieStats && (
        <CollapsibleSection
          title={isBoth ? "Quick Stats - Goalie" : "Quick Stats"}
          icon={<Shield className="w-4 h-4" />}
          defaultExpanded={true}
        >
          <div className="p-6">
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-card rounded-lg p-4 border border-border">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Games Played</div>
                <div className="font-mono text-2xl font-bold text-foreground">{goalieStats.games_played || 0}</div>
              </div>
              <div className="bg-card rounded-lg p-4 border border-border">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">GAA</div>
                <div className="font-mono text-2xl font-bold text-primary">
                  {goalieStats.gaa ? Number(goalieStats.gaa).toFixed(2) : '-'}
                </div>
              </div>
              <div className="bg-card rounded-lg p-4 border border-border">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">SV%</div>
                <div className="font-mono text-2xl font-bold text-foreground">
                  {goalieStats.save_percent 
                    ? Number(goalieStats.save_percent).toFixed(1) + '%'
                    : goalieStats.sv_pct
                      ? Number(goalieStats.sv_pct).toFixed(1) + '%'
                      : '-'}
                </div>
              </div>
              <div className="bg-card rounded-lg p-4 border border-border">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Wins</div>
                <div className="font-mono text-2xl font-bold text-foreground">{goalieStats.wins || 0}</div>
              </div>
            </div>
          </div>
        </CollapsibleSection>
      )}
      
      {/* Career Stats Summary - Skater Stats */}
      {hasPlayedSkater && (career || careerTotals.games_played > 0) && (
        <CollapsibleSection
          title={isBoth ? "Career Stats - Skater" : "Career Stats"}
          icon={<TrendingUp className="w-4 h-4" />}
          defaultExpanded={true}
        >
          <div className="p-6">
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div className="bg-card rounded-lg p-4 border border-border text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">GP</div>
                <div className="font-mono text-2xl font-bold text-foreground">
                  {career?.career_games || career?.games_played || careerTotals.games_played || 0}
                </div>
              </div>
              <div className="bg-card rounded-lg p-4 border border-border text-center">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <Target className="w-3 h-3 text-goal" />
                  <span className="text-xs font-mono text-goal uppercase">Goals</span>
                </div>
                <div className="font-mono text-2xl font-bold text-goal">
                  {career?.career_goals || career?.goals || careerTotals.goals || 0}
                </div>
              </div>
              <div className="bg-card rounded-lg p-4 border border-border text-center">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <Sparkles className="w-3 h-3 text-assist" />
                  <span className="text-xs font-mono text-assist uppercase">Assists</span>
                </div>
                <div className="font-mono text-2xl font-bold text-assist">
                  {career?.career_assists || career?.assists || careerTotals.assists || 0}
                </div>
              </div>
              <div className="bg-card rounded-lg p-4 border border-border text-center">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <TrendingUp className="w-3 h-3 text-primary" />
                  <span className="text-xs font-mono text-primary uppercase">Points</span>
                </div>
                <div className="font-mono text-2xl font-bold text-primary">
                  {career?.career_points || career?.points || careerTotals.points || 0}
                </div>
              </div>
              <div className="bg-card rounded-lg p-4 border border-border text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">P/G</div>
                <div className="font-mono text-2xl font-bold text-foreground">
                  {career?.points_per_game 
                    ? (typeof career.points_per_game === 'number' 
                        ? career.points_per_game.toFixed(2) 
                        : career.points_per_game)
                    : (careerTotals.games_played > 0 
                        ? Number((careerTotals.points || 0) / careerTotals.games_played).toFixed(2) 
                        : '0.00')}
                </div>
              </div>
            </div>
          </div>
        </CollapsibleSection>
      )}
      
      {/* Career Stats Summary - Goalie Stats */}
      {hasPlayedGoalie && goalieSeasonStatsForCareer.length > 0 && (() => {
        // Calculate career goalie totals
        const goalieCareerTotals = goalieSeasonStatsForCareer.reduce((acc, stat) => ({
          games_played: acc.games_played + (Number(stat.games_played) || 0),
          goals_against: acc.goals_against + (Number(stat.goals_against) || 0),
          saves: acc.saves + (Number(stat.saves) || 0),
          shots_against: acc.shots_against + (Number(stat.shots_against) || 0),
        }), { games_played: 0, goals_against: 0, saves: 0, shots_against: 0 })
        
        const careerGAA = goalieCareerTotals.games_played > 0 
          ? goalieCareerTotals.goals_against / goalieCareerTotals.games_played 
          : null
        const careerSV = goalieCareerTotals.shots_against > 0
          ? (goalieCareerTotals.saves / goalieCareerTotals.shots_against) * 100
          : null
        
        return (
          <CollapsibleSection
            title={isBoth ? "Career Stats - Goalie" : "Career Stats"}
            icon={<Shield className="w-4 h-4" />}
            defaultExpanded={true}
          >
            <div className="p-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-card rounded-lg p-4 border border-border text-center">
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-1">GP</div>
                  <div className="font-mono text-2xl font-bold text-foreground">
                    {goalieCareerTotals.games_played || 0}
                  </div>
                </div>
                <div className="bg-card rounded-lg p-4 border border-border text-center">
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-1">GAA</div>
                  <div className="font-mono text-2xl font-bold text-foreground">
                    {careerGAA ? careerGAA.toFixed(2) : '-'}
                  </div>
                </div>
                <div className="bg-card rounded-lg p-4 border border-border text-center">
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-1">SV%</div>
                  <div className="font-mono text-2xl font-bold text-foreground">
                    {careerSV ? careerSV.toFixed(1) + '%' : '-'}
                  </div>
                </div>
                <div className="bg-card rounded-lg p-4 border border-border text-center">
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Saves</div>
                  <div className="font-mono text-2xl font-bold text-foreground">
                    {goalieCareerTotals.saves || 0}
                  </div>
                </div>
              </div>
            </div>
          </CollapsibleSection>
        )
      })()}
      
      
      {/* Prior Teams Section */}
      {priorTeams.length > 0 && (
        <CollapsibleSection
          title="Prior Teams"
          icon={<Users className="w-4 h-4" />}
          defaultExpanded={true}
        >
          <div className="p-6">
            <div className="space-y-6">
              {priorTeams.map((seasonData) => (
                <div key={seasonData.season_id} className="border-b border-border last:border-0 pb-6 last:pb-0">
                  {/* Season Header */}
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <span className="font-display text-base font-semibold text-foreground">
                        {formatSeason(seasonData.season || seasonData.season_id)}
                      </span>
                      {seasonData.is_free_agent && (
                        <span className="text-xs font-mono bg-muted px-2 py-1 rounded uppercase text-muted-foreground">
                          Free Agent
                        </span>
                      )}
                    </div>
                  </div>
                  
                  {/* Teams with Stats Table - Sortable */}
                  <SortablePriorTeamsTable
                    teams={seasonData.teams.map(t => ({
                      team_id: t.team_id,
                      team_name: t.team_name,
                      games: t.games,
                      goals: t.goals,
                      assists: t.assists,
                      points: t.points,
                      pim: t.pim,
                      avg_rating: t.avg_rating,
                      team_info: t.team_info ? {
                        team_id: t.team_info.team_id,
                        team_name: t.team_info.team_name,
                        team_logo: t.team_info.team_logo,
                        team_cd: t.team_info.team_cd,
                        primary_color: t.team_info.primary_color,
                        team_color1: t.team_info.team_color1,
                        team_color2: t.team_info.team_color2,
                      } : null,
                    }))}
                    seasonId={seasonData.season_id}
                    seasonAvgRating={seasonData.season_totals?.avg_rating}
                  />
                  
                  {/* Season Totals Row */}
                  {seasonData.teams.length > 1 && (
                    <div className="mt-4 border-t-2 border-border pt-4">
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b border-border bg-accent/50">
                              <th className="px-3 py-2 text-left font-display text-xs text-muted-foreground">Season Total</th>
                              <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">GP</th>
                              <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">Rating</th>
                              <th className="px-2 py-2 text-center font-display text-xs text-goal">G</th>
                              <th className="px-2 py-2 text-center font-display text-xs text-assist">A</th>
                              <th className="px-2 py-2 text-center font-display text-xs text-primary">P</th>
                              <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">PIM</th>
                              <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">G/G</th>
                              <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">A/G</th>
                              <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">P/G</th>
                            </tr>
                          </thead>
                          <tbody>
                            {(() => {
                              const totals = seasonData.season_totals
                              const goalsPerGame = totals.games > 0 ? (totals.goals / totals.games) : 0
                              const assistsPerGame = totals.games > 0 ? (totals.assists / totals.games) : 0
                              const pointsPerGame = totals.games > 0 ? (totals.points / totals.games) : 0
                              
                              return (
                                <tr className="border-b-2 border-border bg-muted/30 font-bold">
                                  <td className="px-3 py-2 font-display">Season Total</td>
                                  <td className="px-2 py-2 text-center font-mono text-muted-foreground font-semibold">
                                    {totals.games}
                                  </td>
                                  <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                                    {totals.avg_rating != null ? Math.round(Number(totals.avg_rating)) : '-'}
                                  </td>
                                  <td className="px-2 py-2 text-center font-mono text-goal font-semibold">
                                    {totals.goals}
                                  </td>
                                  <td className="px-2 py-2 text-center font-mono text-assist font-semibold">
                                    {totals.assists}
                                  </td>
                                  <td className="px-2 py-2 text-center font-mono text-primary font-semibold">
                                    {totals.points}
                                  </td>
                                  <td className="px-2 py-2 text-center font-mono text-muted-foreground font-semibold">
                                    {totals.pim}
                                  </td>
                                  <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                                    {goalsPerGame.toFixed(2)}
                                  </td>
                                  <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                                    {assistsPerGame.toFixed(2)}
                                  </td>
                                  <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                                    {pointsPerGame.toFixed(2)}
                                  </td>
                                </tr>
                              )
                            })()}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                </div>
              ))}
              
              {/* Career Totals */}
              {careerTotals.games_played > 0 && (
                <div className="border-t-2 border-border pt-6 mt-6">
                  <h3 className="font-display text-base font-semibold text-foreground mb-4">Career Totals</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-border bg-accent/50">
                          <th className="px-3 py-2 text-left font-display text-xs text-muted-foreground">GP</th>
                          <th className="px-2 py-2 text-center font-display text-xs text-goal">G</th>
                          <th className="px-2 py-2 text-center font-display text-xs text-assist">A</th>
                          <th className="px-2 py-2 text-center font-display text-xs text-primary">P</th>
                          <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">PIM</th>
                          <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">G/G</th>
                          <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">A/G</th>
                          <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">P/G</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr className="border-b-2 border-border bg-muted/30 font-bold">
                          <td className="px-3 py-2 font-display font-mono text-muted-foreground font-semibold">
                            {careerTotals.games_played}
                          </td>
                          <td className="px-2 py-2 text-center font-mono text-goal font-semibold">
                            {careerTotals.goals}
                          </td>
                          <td className="px-2 py-2 text-center font-mono text-assist font-semibold">
                            {careerTotals.assists}
                          </td>
                          <td className="px-2 py-2 text-center font-mono text-primary font-semibold">
                            {careerTotals.points}
                          </td>
                          <td className="px-2 py-2 text-center font-mono text-muted-foreground font-semibold">
                            {careerTotals.pim}
                          </td>
                          <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                            {careerTotals.games_played > 0 ? (careerTotals.goals / careerTotals.games_played).toFixed(2) : '0.00'}
                          </td>
                          <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                            {careerTotals.games_played > 0 ? (careerTotals.assists / careerTotals.games_played).toFixed(2) : '0.00'}
                          </td>
                          <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                            {careerTotals.games_played > 0 ? (careerTotals.points / careerTotals.games_played).toFixed(2) : '0.00'}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          </div>
        </CollapsibleSection>
      )}
      
      {/* Player Profile Tabs */}
      <PlayerProfileTabs
        playerId={playerId}
        seasonId={seasonId || ''}
        gameType={gameType}
        gameLog={gameLog}
        allRecentGames={allRecentGames}
        playerStats={playerStats}
        career={career}
        playerShots={playerShots}
        opponentTeamsMap={opponentTeamsMap}
        playerTeamInfo={playerTeamInfo}
        playerPosition={hasPlayedGoalie && !hasPlayedSkater ? 'Goalie' : hasPlayedSkater ? player.player_primary_position : undefined}
        hasPlayedGoalie={hasPlayedGoalie}
        hasPlayedSkater={hasPlayedSkater}
        goalieStats={goalieStats}
        isBoth={isBoth}
        seasonStatsForCareer={seasonStatsWithTeams.length > 0 ? seasonStatsWithTeams : (seasonStatsForCareer || [])}
        goalieSeasonStatsForCareer={goalieSeasonStatsForCareer}
        regularSeasonStats={regularSeasonStats}
        playoffSeasonStats={playoffSeasonStats}
        advancedStatsContent={
          <>
            {hasPlayedSkater && (
              <PlayerAdvancedStatsSection 
                playerId={playerId}
                seasonId={seasonId || ''}
                gameType={gameType}
                gameIds={gameIdsForLog}
                playerPosition={player.player_primary_position || playerStats?.position}
                playerRating={playerStats?.skill_rating ? (typeof playerStats.skill_rating === 'number' ? playerStats.skill_rating : parseFloat(String(playerStats.skill_rating))) : undefined}
              />
            )}
            
            {/* Additional Stats */}
            {playerStats && (
              <div className="grid md:grid-cols-2 gap-6">
                {/* Shooting Stats */}
                <div className="bg-card rounded-xl border border-border overflow-hidden">
                  <div className="px-4 py-3 bg-accent border-b border-border">
                    <h2 className="font-display text-sm font-semibold uppercase tracking-wider">
                      Shooting Stats
                    </h2>
                  </div>
                  <div className="p-4 grid grid-cols-3 gap-4">
                    <div className="text-center">
                      <div className="text-xs font-mono text-muted-foreground uppercase">Shots</div>
                      <div className="font-mono text-xl font-bold text-shot">{playerStats.shots || 0}</div>
                    </div>
                    <div className="text-center">
                      <div className="text-xs font-mono text-muted-foreground uppercase">SH%</div>
                      <div className="font-mono text-xl font-bold text-foreground">
                        {playerStats.shooting_pct 
                          ? (typeof playerStats.shooting_pct === 'number' 
                              ? Number(playerStats.shooting_pct * 100).toFixed(1) + '%' 
                              : String(playerStats.shooting_pct))
                          : '-'}
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-xs font-mono text-muted-foreground uppercase">+/-</div>
                      <div className={cn(
                        'font-mono text-xl font-bold',
                        (playerStats.plus_minus ?? 0) > 0 && 'text-save',
                        (playerStats.plus_minus ?? 0) < 0 && 'text-goal'
                      )}>
                        {(playerStats.plus_minus ?? 0) > 0 ? '+' : ''}{playerStats.plus_minus ?? 0}
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Discipline - Add to Special Teams accordion */}
                {(playerStats.pim > 0 || playerStats.minor_penalties > 0 || playerStats.major_penalties > 0) && (
                  <div className="bg-card rounded-xl border border-border overflow-hidden">
                    <div className="px-4 py-3 bg-accent border-b border-border">
                      <h2 className="font-display text-sm font-semibold uppercase tracking-wider">
                        Discipline
                      </h2>
                    </div>
                    <div className="p-4 grid grid-cols-3 gap-4">
                      <div className="text-center">
                        <div className="text-xs font-mono text-muted-foreground uppercase">PIM</div>
                        <div className="font-mono text-xl font-bold text-foreground">{playerStats.pim || 0}</div>
                      </div>
                      <div className="text-center">
                        <div className="text-xs font-mono text-muted-foreground uppercase">Minor</div>
                        <div className="font-mono text-xl font-bold text-foreground">{playerStats.minor_penalties || 0}</div>
                      </div>
                      <div className="text-center">
                        <div className="text-xs font-mono text-muted-foreground uppercase">Major</div>
                        <div className="font-mono text-xl font-bold text-goal">{playerStats.major_penalties || 0}</div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </>
        }
      />
      
      {/* Actions */}
      <div className="flex gap-4">
        <Link
          href={`/players/${playerId}/trends`}
          className="bg-card border border-border rounded-lg px-4 py-2 text-sm font-display hover:border-primary/50 transition-colors flex items-center gap-2"
        >
          <TrendingUp className="w-4 h-4" />
          View Trends
        </Link>
        <Link
          href={`/players/compare?p1=${playerId}`}
          className="bg-card border border-border rounded-lg px-4 py-2 text-sm font-display hover:border-primary/50 transition-colors"
        >
          Compare with another player →
        </Link>
      </div>
    </div>
    )
  } catch (error) {
    console.error('Error in PlayerDetailPage:', error)
    return (
      <div className="space-y-6 p-6">
        <div className="bg-card rounded-xl border border-border p-6">
          <h1 className="font-display text-2xl font-bold text-foreground mb-4">Error Loading Player</h1>
          <p className="text-muted-foreground">
            There was an error loading this player's data. Please try refreshing the page.
          </p>
          <Link 
            href="/norad/players" 
            className="inline-flex items-center gap-2 mt-4 text-sm text-primary hover:underline"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Players
          </Link>
        </div>
      </div>
    )
  }
}
