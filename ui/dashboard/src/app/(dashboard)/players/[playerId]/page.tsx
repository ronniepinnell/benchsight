// src/app/(dashboard)/players/[playerId]/page.tsx
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getPlayerById, getPlayerCareerSummary, getPlayerGameLog } from '@/lib/supabase/queries/players'
import { getTeamById } from '@/lib/supabase/queries/teams'
import { createClient } from '@/lib/supabase/server'
import { ArrowLeft, Target, Sparkles, TrendingUp, Calendar, Activity, Zap, Shield, BarChart3 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { PlayerPhoto } from '@/components/players/player-photo'
import { TeamLogo } from '@/components/teams/team-logo'
import { SeasonSelector } from '@/components/teams/season-selector'

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
  gameType 
}: { 
  playerId: string
  seasonId: string
  gameType: string
}) {
  const supabase = await createClient()
  
  // First, get all schedule data for filtering
  const { data: allScheduleData } = await supabase
    .from('dim_schedule')
    .select('game_id, season_id, game_type')
  
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
    const { data: directStats } = await supabase
      .from('fact_player_game_stats')
      .select('game_id, season_id')
      .eq('player_id', playerId)
      .limit(1)
    
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
    per60Stats
  ] = await Promise.all([
    // Possession stats - try both column name formats
    (gameIds.length > 0
      ? supabase.from('fact_player_game_stats').select('cf, ca, ff, fa, xg, g, corsi_for, corsi_against, fenwick_for, fenwick_against, xg_for, goals, game_id, season_id').eq('player_id', playerId).in('game_id', gameIds)
      : supabase.from('fact_player_game_stats').select('cf, ca, ff, fa, xg, g, corsi_for, corsi_against, fenwick_for, fenwick_against, xg_for, goals, game_id, season_id').eq('player_id', playerId)
    )
      .then(({ data, error }) => {
        if (error) {
          console.error('Error fetching possession stats:', error)
          return null
        }
        if (!data || data.length === 0) return null
        
        // Filter by season_id if it exists in the data, and by game_id if we have filtered gameIds
        let filteredData = data
        if (gameIds.length > 0) {
          filteredData = data.filter(stat => gameIds.includes(stat.game_id))
        }
        if (filteredData.length === 0) return null
        
        const totals = filteredData.reduce((acc, stat) => {
          // Handle both column name formats
          const cf = stat.corsi_for || stat.cf || 0
          const ca = stat.corsi_against || stat.ca || 0
          const ff = stat.fenwick_for || stat.ff || 0
          const fa = stat.fenwick_against || stat.fa || 0
          const xg = stat.xg_for || stat.xg || 0
          const goals = stat.goals || stat.g || 0
          return {
            cf: (acc.cf || 0) + (parseFloat(String(cf)) || 0),
            ca: (acc.ca || 0) + (parseFloat(String(ca)) || 0),
            ff: (acc.ff || 0) + (parseFloat(String(ff)) || 0),
            fa: (acc.fa || 0) + (parseFloat(String(fa)) || 0),
            xg: (acc.xg || 0) + (parseFloat(String(xg)) || 0),
            goals: (acc.goals || 0) + (parseFloat(String(goals)) || 0),
          }
        }, { cf: 0, ca: 0, ff: 0, fa: 0, xg: 0, goals: 0 })
        const cfPct = totals.cf + totals.ca > 0 ? (totals.cf / (totals.cf + totals.ca)) * 100 : 0
        const ffPct = totals.ff + totals.fa > 0 ? (totals.ff / (totals.ff + totals.fa)) * 100 : 0
        return { ...totals, cfPct, ffPct, xgDiff: totals.goals - totals.xg }
      }),
    
    // Zone stats
    (gameIds.length > 0
      ? supabase.from('fact_player_game_stats').select('zone_entry, zone_entry_controlled, zone_exit, zone_exit_controlled, zone_entries, zone_entries_successful, zone_exits, zone_exits_successful, game_id').eq('player_id', playerId).in('game_id', gameIds)
      : supabase.from('fact_player_game_stats').select('zone_entry, zone_entry_controlled, zone_exit, zone_exit_controlled, zone_entries, zone_entries_successful, zone_exits, zone_exits_successful, game_id').eq('player_id', playerId)
    )
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
          const ze = stat.zone_entries || stat.zone_entry || 0
          const zeSuccess = stat.zone_entries_successful || stat.zone_entry_controlled || 0
          const zx = stat.zone_exits || stat.zone_exit || 0
          const zxSuccess = stat.zone_exits_successful || stat.zone_exit_controlled || 0
          return {
            ze: (acc.ze || 0) + (parseFloat(String(ze)) || 0),
            zeSuccess: (acc.zeSuccess || 0) + (parseFloat(String(zeSuccess)) || 0),
            zx: (acc.zx || 0) + (parseFloat(String(zx)) || 0),
            zxSuccess: (acc.zxSuccess || 0) + (parseFloat(String(zxSuccess)) || 0),
          }
        }, { ze: 0, zeSuccess: 0, zx: 0, zxSuccess: 0 })
        const zePct = totals.ze > 0 ? (totals.zeSuccess / totals.ze) * 100 : 0
        const zxPct = totals.zx > 0 ? (totals.zxSuccess / totals.zx) * 100 : 0
        return { ...totals, zePct, zxPct }
      }),
    
    // WAR/GAR
    (gameIds.length > 0
      ? supabase.from('fact_player_game_stats').select('gar, war, game_score, player_rating, game_id').eq('player_id', playerId).in('game_id', gameIds)
      : supabase.from('fact_player_game_stats').select('gar, war, game_score, player_rating, game_id').eq('player_id', playerId)
    )
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
          gar: (acc.gar || 0) + (parseFloat(String(stat.gar)) || 0),
          war: (acc.war || 0) + (parseFloat(String(stat.war)) || 0),
          gameScore: (acc.gameScore || 0) + (parseFloat(String(stat.game_score)) || 0),
          rating: (acc.rating || 0) + (parseFloat(String(stat.player_rating)) || 0),
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
    (gameIds.length > 0
      ? supabase.from('fact_player_game_stats').select('hit, blk, give, take, hits, blocks, giveaways, takeaways, game_id').eq('player_id', playerId).in('game_id', gameIds)
      : supabase.from('fact_player_game_stats').select('hit, blk, give, take, hits, blocks, giveaways, takeaways, game_id').eq('player_id', playerId)
    )
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
          const hits = stat.hits || stat.hit || 0
          const blocks = stat.blocks || stat.blk || 0
          const giveaways = stat.giveaways || stat.give || 0
          const takeaways = stat.takeaways || stat.take || 0
          return {
            hits: (acc.hits || 0) + (parseFloat(String(hits)) || 0),
            blocks: (acc.blocks || 0) + (parseFloat(String(blocks)) || 0),
            giveaways: (acc.giveaways || 0) + (parseFloat(String(giveaways)) || 0),
            takeaways: (acc.takeaways || 0) + (parseFloat(String(takeaways)) || 0),
            games: acc.games + 1,
          }
        }, { hits: 0, blocks: 0, giveaways: 0, takeaways: 0, games: 0 })
        return {
          ...totals,
          toDiff: totals.takeaways - totals.giveaways,
          hitsPerGame: totals.games > 0 ? (totals.hits / totals.games).toFixed(1) : '0.0',
          blocksPerGame: totals.games > 0 ? (totals.blocks / totals.games).toFixed(1) : '0.0',
        }
      }),
    
    // Shooting stats
    (gameIds.length > 0
      ? supabase.from('fact_player_game_stats').select('sog, sh_pct, g, shots, shooting_pct, goals, game_id').eq('player_id', playerId).in('game_id', gameIds)
      : supabase.from('fact_player_game_stats').select('sog, sh_pct, g, shots, shooting_pct, goals, game_id').eq('player_id', playerId)
    )
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
          // Handle both column name formats
          const shots = stat.shots || 0
          const sog = stat.sog || 0
          const goals = stat.goals || stat.g || 0
          return {
            shots: (acc.shots || 0) + (parseFloat(String(shots)) || 0),
            sog: (acc.sog || 0) + (parseFloat(String(sog)) || 0),
            goals: (acc.goals || 0) + (parseFloat(String(goals)) || 0),
            games: acc.games + 1,
          }
        }, { shots: 0, sog: 0, goals: 0, games: 0 })
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
    
    // Per-60 rates
    (gameIds.length > 0
      ? supabase.from('fact_player_game_stats').select('g_60, sog_60, pts_60, toi_seconds, goals_per_60, assists_per_60, points_per_60, game_id').eq('player_id', playerId).in('game_id', gameIds)
      : supabase.from('fact_player_game_stats').select('g_60, sog_60, pts_60, toi_seconds, goals_per_60, assists_per_60, points_per_60, game_id').eq('player_id', playerId)
    )
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
          const g60 = stat.goals_per_60 || stat.g_60 || 0
          const p60 = stat.points_per_60 || stat.pts_60 || 0
          const toi = stat.toi_seconds || 0
          return {
            g60: (acc.g60 || 0) + (parseFloat(String(g60)) || 0),
            p60: (acc.p60 || 0) + (parseFloat(String(p60)) || 0),
            toi: (acc.toi || 0) + (parseFloat(String(toi)) || 0),
            games: acc.games + 1,
          }
        }, { g60: 0, p60: 0, toi: 0, games: 0 })
        // Calculate assists/60 from points/60 - goals/60
        const a60 = totals.p60 - totals.g60
        return {
          goalsPer60: totals.games > 0 ? (totals.g60 / totals.games).toFixed(2) : '0.00',
          assistsPer60: totals.games > 0 ? (a60 / totals.games).toFixed(2) : '0.00',
          pointsPer60: totals.games > 0 ? (totals.p60 / totals.games).toFixed(2) : '0.00',
          avgTOI: totals.games > 0 ? (totals.toi / totals.games / 60).toFixed(1) : '0.0',
        }
      }),
  ])
  
  const hasAnyStats = possessionStats || zoneStats || warStats || physicalStats || shootingStats || per60Stats
  
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
              <h3 className="font-display text-sm font-semibold text-foreground uppercase tracking-wider border-b border-border pb-2 flex items-center gap-2">
                <Activity className="w-4 h-4" />
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
          
          {/* Zone Play */}
          {zoneStats && (
            <div className="space-y-3">
              <h3 className="font-display text-sm font-semibold text-foreground uppercase tracking-wider border-b border-border pb-2 flex items-center gap-2">
                <Zap className="w-4 h-4" />
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
              <h3 className="font-display text-sm font-semibold text-foreground uppercase tracking-wider border-b border-border pb-2 flex items-center gap-2">
                <TrendingUp className="w-4 h-4" />
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
              <h3 className="font-display text-sm font-semibold text-foreground uppercase tracking-wider border-b border-border pb-2 flex items-center gap-2">
                <Shield className="w-4 h-4" />
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
              <h3 className="font-display text-sm font-semibold text-foreground uppercase tracking-wider border-b border-border pb-2 flex items-center gap-2">
                <BarChart3 className="w-4 h-4" />
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
          
          {/* Per-60 Rates */}
          {per60Stats && (
            <div className="space-y-3">
              <h3 className="font-display text-sm font-semibold text-foreground uppercase tracking-wider border-b border-border pb-2 flex items-center gap-2">
                <Target className="w-4 h-4" />
                Per 60 Rates
              </h3>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Goals/60</span>
                  <span className="font-mono font-semibold text-goal">{per60Stats.goalsPer60}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Assists/60</span>
                  <span className="font-mono font-semibold text-assist">{per60Stats.assistsPer60}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Points/60</span>
                  <span className="font-mono font-semibold text-primary">{per60Stats.pointsPer60}</span>
                </div>
                <div className="flex justify-between items-center border-t border-border pt-2 mt-2">
                  <span className="text-xs text-muted-foreground">Avg TOI</span>
                  <span className="font-mono text-foreground">{per60Stats.avgTOI} min</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default async function PlayerDetailPage({ 
  params,
  searchParams
}: { 
  params: Promise<{ playerId: string }>
  searchParams: Promise<{ season?: string; gameType?: string }>
}) {
  const { playerId } = await params
  const { season: selectedSeason, gameType: selectedGameType } = await searchParams
  
  if (!playerId) {
    notFound()
  }
  
  const supabase = await createClient()
  
  const [player, career] = await Promise.all([
    getPlayerById(playerId),
    getPlayerCareerSummary(playerId).catch(() => null)
  ])
  
  if (!player) {
    notFound()
  }
  
  // Get available seasons for this player
  const { data: seasonsData } = await supabase
    .from('fact_player_season_stats_basic')
    .select('season_id, season')
    .eq('player_id', playerId)
    .order('season', { ascending: false })
  
  const seasons = seasonsData 
    ? [...new Map(seasonsData.map(s => [s.season_id, s])).values()]
    : []
  
  // Get current season (latest)
  const currentSeason = seasons[0]?.season_id || ''
  const seasonId = selectedSeason || currentSeason
  const gameType = selectedGameType || 'All' // 'All', 'Regular', 'Playoffs'
  
  // Get game IDs from schedule first (needed for filtering)
  const { data: scheduleForGames } = await supabase
    .from('dim_schedule')
    .select('game_id, season_id, game_type, date')
    .eq('season_id', seasonId)
  
  // Filter by game_type if not 'All'
  const filteredSchedule = gameType === 'All' 
    ? scheduleForGames 
    : scheduleForGames?.filter(s => s.game_type === gameType) || []
  
  const gameIdsForLog = filteredSchedule?.map(g => g.game_id) || []
  
  // Get player stats for selected season/game type
  let playerStats: any = null
  
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
  
  // Get game log for selected season/game type
  let gameLog: any[] = []
  if (gameIdsForLog.length > 0) {
    const { data: gameLogData, error: gameLogError } = await supabase
      .from('fact_player_game_stats')
      .select('*')
      .eq('player_id', playerId)
      .in('game_id', gameIdsForLog)
      .order('game_id', { ascending: false })
      .limit(20)
    
    if (gameLogError) {
      console.error('Error fetching game log:', gameLogError)
    }
    
    // Merge with schedule data to get dates
    gameLog = (gameLogData || []).map(game => {
      const scheduleInfo = filteredSchedule?.find(s => s.game_id === game.game_id)
      return {
        ...game,
        date: scheduleInfo?.date || game.date,
      }
    }).sort((a, b) => {
      const dateA = a.date ? new Date(a.date).getTime() : 0
      const dateB = b.date ? new Date(b.date).getTime() : 0
      return dateB - dateA
    })
  } else {
    // Fallback: try to get any game stats for this player (no season/game type filter)
    const { data: gameLogData, error: gameLogError } = await supabase
      .from('fact_player_game_stats')
      .select('*')
      .eq('player_id', playerId)
      .order('game_id', { ascending: false })
      .limit(20)
    
    if (gameLogError) {
      console.error('Error fetching game log (fallback):', gameLogError)
    }
    
    gameLog = gameLogData || []
  }
  
  // Get current team info (use player_norad_current_team_id if available, otherwise team_id)
  const currentTeamId = player.player_norad_current_team_id || player.team_id || playerStats?.team_id
  const teamInfo = currentTeamId ? await getTeamById(String(currentTeamId)).catch(() => null) : null
  
  return (
    <div className="space-y-6">
      {/* Back Link */}
      <Link 
        href="/players" 
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Players
      </Link>
      
      {/* Player Header */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="bg-gradient-to-r from-primary/10 via-transparent to-primary/10 p-6">
          <div className="flex items-start gap-6">
            {/* Player Photo */}
            <PlayerPhoto
              src={player.player_image || null}
              name={player.player_full_name || player.player_name || ''}
              primaryColor={teamInfo?.primary_color || teamInfo?.team_color1}
              size="xl"
            />
            
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="font-display text-3xl font-bold text-foreground">
                    {player.player_full_name || player.player_name}
                  </h1>
                  <div className="flex items-center gap-4 mt-3">
                    {player.jersey_number && (
                      <span className="text-sm font-mono text-muted-foreground">
                        #{player.jersey_number}
                      </span>
                    )}
                    {teamInfo && (
                      <Link 
                        href={teamInfo ? `/team/${(teamInfo.team_name || '').replace(/\s+/g, '_')}` : '#'}
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
      
      {/* Season Stats */}
      {playerStats && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="bg-card rounded-lg p-4 border border-border text-center">
            <div className="text-xs font-mono text-muted-foreground uppercase mb-1">GP</div>
            <div className="font-mono text-2xl font-bold text-foreground">{playerStats.games_played || 0}</div>
          </div>
          <div className="bg-card rounded-lg p-4 border border-border text-center">
            <div className="flex items-center justify-center gap-1 mb-1">
              <Target className="w-3 h-3 text-goal" />
              <span className="text-xs font-mono text-goal uppercase">Goals</span>
            </div>
            <div className="font-mono text-2xl font-bold text-goal">{playerStats.goals || 0}</div>
          </div>
          <div className="bg-card rounded-lg p-4 border border-border text-center">
            <div className="flex items-center justify-center gap-1 mb-1">
              <Sparkles className="w-3 h-3 text-assist" />
              <span className="text-xs font-mono text-assist uppercase">Assists</span>
            </div>
            <div className="font-mono text-2xl font-bold text-assist">{playerStats.assists || 0}</div>
          </div>
          <div className="bg-card rounded-lg p-4 border border-border text-center">
            <div className="flex items-center justify-center gap-1 mb-1">
              <TrendingUp className="w-3 h-3 text-primary" />
              <span className="text-xs font-mono text-primary uppercase">Points</span>
            </div>
            <div className="font-mono text-2xl font-bold text-primary">{playerStats.points || 0}</div>
          </div>
          <div className="bg-card rounded-lg p-4 border border-border text-center">
            <div className="text-xs font-mono text-muted-foreground uppercase mb-1">P/G</div>
            <div className="font-mono text-2xl font-bold text-foreground">
              {playerStats.points_per_game?.toFixed(2) ?? (playerStats.games_played > 0 ? ((playerStats.points || 0) / playerStats.games_played).toFixed(2) : '-')}
            </div>
          </div>
        </div>
      )}
      
      {/* Advanced Stats Section */}
      {seasonId && (
        <PlayerAdvancedStatsSection 
          playerId={playerId}
          seasonId={seasonId}
          gameType={gameType}
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
                  {playerStats.shooting_pct ? (playerStats.shooting_pct * 100).toFixed(1) + '%' : '-'}
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
          
          {/* Discipline */}
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
        </div>
      )}
      
      {/* Game Log */}
      {gameLog.length > 0 && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border flex items-center justify-between">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              Game Log
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-accent/50">
                  <th className="px-4 py-2 text-left font-display text-xs text-muted-foreground">Date</th>
                  <th className="px-4 py-2 text-left font-display text-xs text-muted-foreground">Opponent</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-goal">G</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-assist">A</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-primary">P</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-shot">S</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">+/-</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">TOI</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">CF%</th>
                </tr>
              </thead>
              <tbody>
                {gameLog.filter(game => game && game.game_id).map((game: any) => {
                  const gameDate = game.date ? new Date(game.date).toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric',
                  }) : '-'
                  
                  const toiMinutes = game.toi_seconds ? Math.floor(game.toi_seconds / 60) : 0
                  const toiSeconds = game.toi_seconds ? game.toi_seconds % 60 : 0
                  const toiDisplay = toiMinutes > 0 ? `${toiMinutes}:${toiSeconds.toString().padStart(2, '0')}` : '-'
                  
                  return (
                    <tr key={game.player_game_key || `game-${game.game_id}`} className="border-b border-border hover:bg-muted/50">
                      <td className="px-4 py-2 font-mono text-xs text-muted-foreground">
                        {game.game_id ? (
                          <Link href={`/games/${game.game_id}`} className="hover:text-primary">
                            {gameDate}
                          </Link>
                        ) : (
                          <span>{gameDate}</span>
                        )}
                      </td>
                      <td className="px-4 py-2 text-foreground">
                        {game.opponent_team_name ?? game.team_name ?? '-'}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-goal font-semibold">
                        {game.goals || 0}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-assist">
                        {game.assists || 0}
                      </td>
                      <td className="px-2 py-2 text-center font-mono font-bold text-primary">
                        {game.points || 0}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-shot">
                        {game.shots || game.sog || 0}
                      </td>
                      <td className={cn(
                        'px-2 py-2 text-center font-mono',
                        (game.plus_minus_total ?? game.plus_minus ?? 0) > 0 && 'text-save',
                        (game.plus_minus_total ?? game.plus_minus ?? 0) < 0 && 'text-goal'
                      )}>
                        {(game.plus_minus_total ?? game.plus_minus ?? 0) > 0 ? '+' : ''}{(game.plus_minus_total ?? game.plus_minus ?? 0)}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                        {toiDisplay}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                        {game.cf_pct ? game.cf_pct.toFixed(1) + '%' : '-'}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
      
      {/* Actions */}
      <div className="flex gap-4">
        <Link
          href={`/players/compare?p1=${playerId}`}
          className="bg-card border border-border rounded-lg px-4 py-2 text-sm font-display hover:border-primary/50 transition-colors"
        >
          Compare with another player →
        </Link>
      </div>
    </div>
  )
}
