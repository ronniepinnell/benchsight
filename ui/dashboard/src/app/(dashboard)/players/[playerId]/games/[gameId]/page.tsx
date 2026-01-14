// src/app/(dashboard)/players/[playerId]/games/[gameId]/page.tsx
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getPlayerById } from '@/lib/supabase/queries/players'
import { getGameFromSchedule, getGameRoster } from '@/lib/supabase/queries/games'
import { getTeamById } from '@/lib/supabase/queries/teams'
import { createClient } from '@/lib/supabase/server'
import { ArrowLeft, Target, TrendingUp, Activity, BarChart3, Zap, Clock, Users } from 'lucide-react'
import { cn } from '@/lib/utils'
import { PlayerPhoto } from '@/components/players/player-photo'
import { TeamLogo } from '@/components/teams/team-logo'
import { StatCard } from '@/components/players/stat-card'

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
  const [player, game, gameStatsResult, gameStatusResult] = await Promise.all([
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
      .maybeSingle()
  ])
  
  if (!player || !game) {
    notFound()
  }
  
  const gameStats = gameStatsResult.error ? null : gameStatsResult.data
  const hasTracking = gameStatusResult.data?.tracking_status === 'Complete' || gameStatusResult.data?.tracking_status === 'Partial'
  
  // Get team info
  const teamId = gameStats?.team_id || String(game.home_team_id || game.away_team_id || '')
  const opponentId = gameStats?.team_id === String(game.home_team_id) 
    ? String(game.away_team_id || '') 
    : String(game.home_team_id || '')
  
  const [team, opponent] = await Promise.all([
    teamId ? getTeamById(teamId).catch(() => null) : Promise.resolve(null),
    opponentId ? getTeamById(opponentId).catch(() => null) : Promise.resolve(null)
  ])
  
  // Get micro stats if available
  let microStats = null
  if (hasTracking) {
    const { data } = await supabase
      .from('fact_player_micro_stats')
      .select('*')
      .eq('player_id', playerId)
      .eq('game_id', gameIdNum)
      .catch(() => ({ data: null }))
    
    if (data && data.length > 0) {
      microStats = data.reduce((acc: any, stat: any) => {
        acc[stat.micro_stat] = stat.count
        return acc
      }, {})
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
            href={`/games/${gameId}`}
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
        </>
      )}
    </div>
  )
}