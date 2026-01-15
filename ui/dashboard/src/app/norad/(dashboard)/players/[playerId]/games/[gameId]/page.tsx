// @ts-nocheck
// src/app/(dashboard)/players/[playerId]/games/[gameId]/page.tsx
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getPlayerById } from '@/lib/supabase/queries/players'
import { getGameFromSchedule, getGameRoster } from '@/lib/supabase/queries/games'
import { getTeamById } from '@/lib/supabase/queries/teams'
import { createClient } from '@/lib/supabase/server'
import { ArrowLeft, Target, TrendingUp, Activity, BarChart3, Zap, Clock, Users, Play, List } from 'lucide-react'
import { cn } from '@/lib/utils'
import { PlayerPhoto } from '@/components/players/player-photo'
import { TeamLogo } from '@/components/teams/team-logo'
import { StatCard } from '@/components/players/stat-card'
import { PlayByPlayTimeline } from '@/components/games/PlayByPlayTimeline'
import { EnhancedShotMap } from '@/components/charts/enhanced-shot-map'

export const revalidate = 300

export async function generateMetadata({ params }: { params: Promise<{ playerId: string; gameId: string }> }) {
  const { playerId, gameId } = await params
  return {
    title: `Game ${gameId} Stats | Player ${playerId} | BenchSight`,
    description: `Advanced game statistics for player ${playerId} in game ${gameId}`,
  }
}

export default async function PlayerGameStatsPage({ 
  params 
}: { 
  params: Promise<{ playerId: string; gameId: string }> 
}) {
  const { playerId, gameId } = await params
  const gameIdNum = parseInt(gameId)
  
  if (isNaN(gameIdNum)) {
    notFound()
  }
  
  const supabase = await createClient()
  
  // Fetch data in parallel
  const [player, game, gameStatsResult, gameStatusResult, playerEventsResult, playerShotsResult, shiftsResult] = await Promise.all([
    getPlayerById(playerId).catch(() => null),
    getGameFromSchedule(gameIdNum).catch(() => null),
    supabase
      .from('fact_player_game_stats')
      .select('*')
      .eq('player_id', playerId)
      .eq('game_id', gameIdNum)
      .maybeSingle(),
    supabase
      .from('fact_game_status')
      .select('tracking_status')
      .eq('game_id', gameIdNum)
      .maybeSingle(),
    // Get all events involving this player - we'll filter after fetching
    supabase
      .from('fact_events')
      .select('*')
      .eq('game_id', gameIdNum)
      .order('event_id', { ascending: true }),
    // Get shots by this player
    supabase
      .from('fact_shot_xy')
      .select('*')
      .eq('game_id', gameIdNum)
      .eq('player_id', playerId),
    // Get shifts for this player
    supabase
      .from('fact_shifts')
      .select('*')
      .eq('game_id', gameIdNum)
      .eq('player_id', playerId)
      .order('shift_start_total_seconds', { ascending: true })
  ])
  
  if (!player || !game) {
    notFound()
  }
  
  const gameStats = gameStatsResult.error ? null : gameStatsResult.data
  const hasTracking = gameStatusResult.data?.tracking_status === 'Complete' || gameStatusResult.data?.tracking_status === 'Partial'
  
  // Get player events (filter to only events where this player is involved)
  const allEvents = playerEventsResult.error ? [] : (playerEventsResult.data || [])
  const playerName = player.player_name || player.player_full_name || ''
  const playerEvents = allEvents.filter((event: any) => {
    // Check if player is in event_player_ids
    if (event.event_player_ids) {
      const playerIds = event.event_player_ids.split(',').map((id: string) => id.trim())
      if (playerIds.includes(playerId)) return true
    }
    // Check if player is in opp_player_ids
    if (event.opp_player_ids) {
      const oppIds = event.opp_player_ids.split(',').map((id: string) => id.trim())
      if (oppIds.includes(playerId)) return true
    }
    // Check player_name field
    if (event.player_name === playerName) return true
    // Check event_player_1 and event_player_2
    if (event.event_player_1 === playerName) return true
    if (event.event_player_2 === playerName) return true
    return false
  })
  
  // Get player shots
  const playerShots = playerShotsResult.error ? [] : (playerShotsResult.data || [])
  
  // Get player shifts
  const playerShifts = shiftsResult.error ? [] : (shiftsResult.data || [])
  
  // Get team info
  const teamId = gameStats?.team_id || String(game.home_team_id || game.away_team_id || '')
  const opponentId = gameStats?.team_id === String(game.home_team_id) 
    ? String(game.away_team_id || '') 
    : String(game.home_team_id || '')
  
  const [team, opponent] = await Promise.all([
    teamId ? getTeamById(teamId).catch(() => null) : Promise.resolve(null),
    opponentId ? getTeamById(opponentId).catch(() => null) : Promise.resolve(null)
  ])
  
  // Get all players for the timeline
  let allPlayersData: any[] = []
  try {
    const { data, error } = await supabase
      .from('dim_player')
      .select('*')
    if (!error && data) {
      allPlayersData = data
    }
  } catch (error) {
    console.error('Error fetching players:', error)
  }
  
  const playersMap = new Map(
    (allPlayersData || []).map((p: any) => [String(p.player_id), p])
  )
  
  // Determine which team is home/away for timeline
  const homeTeamId = String(game.home_team_id || '')
  const awayTeamId = String(game.away_team_id || '')
  
  const homeTeamForTimeline = String(team?.team_id || '') === homeTeamId ? team : 
                              (homeTeamId ? await getTeamById(homeTeamId).catch(() => null) : null)
  const awayTeamForTimeline = String(team?.team_id || '') === awayTeamId ? team : 
                              (awayTeamId ? await getTeamById(awayTeamId).catch(() => null) : null)
  
  // Get micro stats if available
  let microStats = null
  if (hasTracking) {
    try {
      const { data, error } = await supabase
        .from('fact_player_micro_stats')
        .select('*')
        .eq('player_id', playerId)
        .eq('game_id', gameIdNum)
      
      if (!error && data && data.length > 0) {
        microStats = data.reduce((acc: any, stat: any) => {
          acc[stat.micro_stat] = stat.count
          return acc
        }, {})
      }
    } catch (error) {
      console.error('Error fetching micro stats:', error)
    }
  }
  
  const formatTime = (seconds: number | null | undefined) => {
    if (!seconds) return '-'
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }
  
  const formatDecimal = (val: number | null | undefined, decimals: number = 1) => {
    if (val === null || val === undefined) return '-'
    return Number(val).toFixed(decimals)
  }
  
  const formatPercent = (val: number | null | undefined) => {
    if (val === null || val === undefined) return '-'
    return Number(val).toFixed(1) + '%'
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link 
            href={`/norad/games/${gameId}`}
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="font-display text-2xl font-bold tracking-wider uppercase flex items-center gap-3">
              <span className="w-1 h-6 bg-shot rounded" />
              {player.player_name || player.player_full_name || 'Player'} - Game {gameId}
            </h1>
            <p className="text-sm text-muted-foreground mt-2 ml-4">
              Advanced game statistics and microstats
            </p>
          </div>
        </div>
        <Link 
          href={`/players/${playerId}`}
          className="text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          View Player Profile →
        </Link>
      </div>
      
      {/* Game Context */}
      <div className="bg-card rounded-xl border border-border p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            {team && (
              <TeamLogo
                src={team.team_logo || null}
                name={team.team_name || ''}
                abbrev={team.team_cd}
                primaryColor={team.primary_color || team.team_color1}
                secondaryColor={team.team_color2}
                size="md"
              />
            )}
            <div>
              <div className="font-display text-lg font-semibold">
                {team?.team_name || 'Team'} vs {opponent?.team_name || 'Opponent'}
              </div>
              <div className="text-sm text-muted-foreground">
                {game.date ? new Date(game.date).toLocaleDateString('en-US', { 
                  weekday: 'long', 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                }) : 'Date TBD'}
                {hasTracking && (
                  <span className="ml-2 px-2 py-1 bg-primary/10 text-primary rounded text-xs font-mono">
                    Tracked Game
                  </span>
                )}
              </div>
            </div>
          </div>
          {gameStats && (
            <div className="text-right">
              <div className="text-3xl font-mono font-bold text-primary">
                {gameStats.goals || 0}G {gameStats.assists || 0}A {gameStats.points || 0}P
              </div>
              <div className="text-sm text-muted-foreground mt-1">
                {formatTime(gameStats.toi_seconds)}
              </div>
            </div>
          )}
        </div>
      </div>
      
      {!gameStats && (
        <div className="bg-card rounded-xl border border-border p-8 text-center">
          <p className="text-muted-foreground">
            No game statistics available for this player in this game.
          </p>
        </div>
      )}
      
      {gameStats && (
        <>
          {/* Core Stats */}
          <div className="grid md:grid-cols-4 gap-4">
            <StatCard label="Goals" value={gameStats.goals || 0} className="text-goal" />
            <StatCard label="Assists" value={gameStats.assists || 0} className="text-assist" />
            <StatCard label="Points" value={gameStats.points || 0} className="text-primary" />
            <StatCard label="+/-" value={gameStats.plus_minus || 0} />
            <StatCard label="Shots" value={gameStats.shots || gameStats.shots_on_goal || 0} />
            <StatCard label="TOI" value={formatTime(gameStats.toi_seconds)} />
            <StatCard label="Shifts" value={gameStats.shifts || 0} />
            <StatCard label="Avg Shift" value={gameStats.avg_shift_length ? formatDecimal(gameStats.avg_shift_length, 1) + 's' : '-'} />
          </div>
          
          {/* Possession Stats */}
          {hasTracking && (
            <div className="bg-card rounded-xl border border-border overflow-hidden">
              <div className="px-4 py-3 bg-accent border-b border-border">
                <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                  <BarChart3 className="w-4 h-4" />
                  Possession Metrics
                </h2>
              </div>
              <div className="p-6">
                <div className="grid md:grid-cols-4 gap-4">
                  <StatCard label="Corsi For" value={gameStats.cf || 0} />
                  <StatCard label="Corsi Against" value={gameStats.ca || 0} />
                  <StatCard label="CF%" value={formatPercent(gameStats.cf_pct)} className="text-primary" />
                  <StatCard label="Fenwick For" value={gameStats.ff || 0} />
                  <StatCard label="Fenwick Against" value={gameStats.fa || 0} />
                  <StatCard label="FF%" value={formatPercent(gameStats.ff_pct)} className="text-primary" />
                  <StatCard label="xG For" value={formatDecimal(gameStats.xg_for)} />
                  <StatCard label="xG Against" value={formatDecimal(gameStats.xga)} />
                </div>
              </div>
            </div>
          )}
          
          {/* Zone Stats */}
          {hasTracking && (
            <div className="bg-card rounded-xl border border-border overflow-hidden">
              <div className="px-4 py-3 bg-accent border-b border-border">
                <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                  <Target className="w-4 h-4" />
                  Zone Transitions
                </h2>
              </div>
              <div className="p-6">
                <div className="grid md:grid-cols-4 gap-4">
                  <StatCard label="Zone Entries" value={gameStats.zone_entries || 0} />
                  <StatCard label="Controlled Entries" value={gameStats.zone_entries_successful || gameStats.zone_entry_controlled || 0} />
                  <StatCard label="Entry Success %" value={formatPercent(
                    (gameStats.zone_entries_successful || gameStats.zone_entry_controlled || 0) / 
                    ((gameStats.zone_entries || 0) || 1) * 100
                  )} />
                  <StatCard label="Zone Exits" value={gameStats.zone_exits || 0} />
                  <StatCard label="Controlled Exits" value={gameStats.zone_exits_successful || gameStats.zone_exit_controlled || 0} />
                  <StatCard label="Exit Success %" value={formatPercent(
                    (gameStats.zone_exits_successful || gameStats.zone_exit_controlled || 0) / 
                    ((gameStats.zone_exits || 0) || 1) * 100
                  )} />
                </div>
              </div>
            </div>
          )}
          
          {/* Passing Stats */}
          {hasTracking && (
            <div className="bg-card rounded-xl border border-border overflow-hidden">
              <div className="px-4 py-3 bg-accent border-b border-border">
                <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                  <Users className="w-4 h-4" />
                  Passing
                </h2>
              </div>
              <div className="p-6">
                <div className="grid md:grid-cols-4 gap-4">
                  <StatCard label="Pass Attempts" value={gameStats.pass_attempts || gameStats.pass_att || 0} />
                  <StatCard label="Pass Completed" value={gameStats.pass_completed || gameStats.pass_comp || 0} />
                  <StatCard label="Pass %" value={formatPercent(gameStats.pass_pct)} className="text-primary" />
                  <StatCard label="Giveaways" value={gameStats.giveaways || gameStats.give || 0} />
                  <StatCard label="Takeaways" value={gameStats.takeaways || gameStats.take || 0} />
                </div>
              </div>
            </div>
          )}
          
          {/* Micro Stats */}
          {hasTracking && microStats && (
            <div className="bg-card rounded-xl border border-border overflow-hidden">
              <div className="px-4 py-3 bg-accent border-b border-border">
                <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                  <Zap className="w-4 h-4" />
                  Micro Statistics
                </h2>
              </div>
              <div className="p-6">
                <div className="grid md:grid-cols-4 gap-4">
                  {microStats.dekes && <StatCard label="Dekes" value={microStats.dekes} />}
                  {microStats.drives_total && <StatCard label="Drives" value={microStats.drives_total} />}
                  {microStats.forechecks && <StatCard label="Forechecks" value={microStats.forechecks} />}
                  {microStats.backchecks && <StatCard label="Backchecks" value={microStats.backchecks} />}
                  {microStats.puck_battles_total && <StatCard label="Puck Battles" value={microStats.puck_battles_total} />}
                  {microStats.screens && <StatCard label="Screens" value={microStats.screens} />}
                  {microStats.crash_net && <StatCard label="Crash Net" value={microStats.crash_net} />}
                  {microStats.cycles && <StatCard label="Cycles" value={microStats.cycles} />}
                  {microStats.give_and_go && <StatCard label="Give & Go" value={microStats.give_and_go} />}
                  {microStats.loose_puck_wins && <StatCard label="Loose Puck Wins" value={microStats.loose_puck_wins} />}
                </div>
              </div>
            </div>
          )}
          
          {/* Physical Stats */}
          {hasTracking && (
            <div className="bg-card rounded-xl border border-border overflow-hidden">
              <div className="px-4 py-3 bg-accent border-b border-border">
                <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                  <Activity className="w-4 h-4" />
                  Physical Play
                </h2>
              </div>
              <div className="p-6">
                <div className="grid md:grid-cols-4 gap-4">
                  <StatCard label="Hits" value={gameStats.hits || 0} />
                  <StatCard label="Hits Taken" value={gameStats.hits_taken || 0} />
                  <StatCard label="Blocks" value={gameStats.blocks || 0} />
                  <StatCard label="Faceoffs Won" value={gameStats.fo_wins || 0} />
                  <StatCard label="Faceoffs Lost" value={gameStats.fo_losses || 0} />
                  <StatCard label="FO%" value={formatPercent(gameStats.fo_pct)} />
                </div>
              </div>
            </div>
          )}
          
          {/* Player Events Timeline */}
          {playerEvents.length > 0 && (
            <div className="bg-card rounded-xl border border-border overflow-hidden">
              <div className="px-4 py-3 bg-accent border-b border-border">
                <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                  <Play className="w-4 h-4" />
                  Player Events
                </h2>
              </div>
              <div className="p-6">
                <PlayByPlayTimeline
                  events={playerEvents}
                  homeTeam={homeTeamForTimeline?.team_name || game.home_team_name || 'Home'}
                  awayTeam={awayTeamForTimeline?.team_name || game.away_team_name || 'Away'}
                  homeTeamId={homeTeamId}
                  awayTeamId={awayTeamId}
                  playersMap={playersMap}
                  homeTeamData={homeTeamForTimeline ? {
                    team_name: homeTeamForTimeline.team_name || game.home_team_name || 'Home',
                    team_logo: homeTeamForTimeline.team_logo,
                    team_cd: homeTeamForTimeline.team_cd,
                    primary_color: homeTeamForTimeline.primary_color || homeTeamForTimeline.team_color1,
                    team_color1: homeTeamForTimeline.team_color1
                  } : undefined}
                  awayTeamData={awayTeamForTimeline ? {
                    team_name: awayTeamForTimeline.team_name || game.away_team_name || 'Away',
                    team_logo: awayTeamForTimeline.team_logo,
                    team_cd: awayTeamForTimeline.team_cd,
                    primary_color: awayTeamForTimeline.primary_color || awayTeamForTimeline.team_color1,
                    team_color1: awayTeamForTimeline.team_color1
                  } : undefined}
                />
              </div>
            </div>
          )}
          
          {/* Shot Map */}
          {playerShots.length > 0 && (
            <div className="bg-card rounded-xl border border-border overflow-hidden">
              <div className="px-4 py-3 bg-accent border-b border-border">
                <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                  <Target className="w-4 h-4" />
                  Shot Map
                </h2>
              </div>
              <div className="p-6">
                <EnhancedShotMap
                  shots={playerShots}
                />
              </div>
            </div>
          )}
          
          {/* Shifts */}
          {playerShifts.length > 0 && (
            <div className="bg-card rounded-xl border border-border overflow-hidden">
              <div className="px-4 py-3 bg-accent border-b border-border">
                <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                  <List className="w-4 h-4" />
                  Shifts ({playerShifts.length})
                </h2>
              </div>
              <div className="p-6">
                <div className="space-y-2">
                  {playerShifts.map((shift: any, idx: number) => {
                    const shiftStart = shift.shift_start_total_seconds || shift.shift_start_seconds || 0
                    const shiftEnd = shift.shift_end_total_seconds || shift.shift_end_seconds || 0
                    const duration = shiftEnd - shiftStart
                    const period = shift.period || 1
                    const periodLabel = period > 3 ? `OT${period - 3}` : `P${period}`
                    
                    // Calculate time within period
                    const periodStart = (period - 1) * 1200 // Approximate
                    const startTimeInPeriod = shiftStart - periodStart
                    const endTimeInPeriod = shiftEnd - periodStart
                    const startMin = Math.floor(startTimeInPeriod / 60)
                    const startSec = Math.floor(startTimeInPeriod % 60)
                    const endMin = Math.floor(endTimeInPeriod / 60)
                    const endSec = Math.floor(endTimeInPeriod % 60)
                    
                    return (
                      <div key={shift.shift_id || idx} className="flex items-center gap-4 p-3 bg-muted/30 rounded-lg border border-border">
                        <div className="w-16 text-xs font-mono text-muted-foreground text-center">
                          {periodLabel}
                        </div>
                        <div className="w-32 text-xs font-mono text-foreground">
                          {startMin}:{String(startSec).padStart(2, '0')} - {endMin}:{String(endSec).padStart(2, '0')}
                        </div>
                        <div className="flex-1 text-xs text-muted-foreground">
                          {formatTime(duration)} duration
                          {shift.strength && (
                            <span className="ml-2 px-2 py-0.5 bg-background rounded text-[10px]">
                              {shift.strength}
                            </span>
                          )}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}