// src/app/(dashboard)/analytics/micro-stats/page.tsx
import Link from 'next/link'
import { createClient } from '@/lib/supabase/server'
import { ArrowLeft, Zap, Target, Activity, TrendingUp, BarChart3 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { PlayerPhoto } from '@/components/players/player-photo'
import { TeamLogo } from '@/components/teams/team-logo'

export const revalidate = 300

export const metadata = {
  title: 'Micro Stats Explorer | BenchSight Analytics',
  description: 'Explore detailed micro statistics for players',
}

// Common micro stats categories
const MICRO_STAT_CATEGORIES = {
  'Offensive Skills': [
    'dekes', 'drives_total', 'drives_middle', 'drives_wide', 'drives_corner',
    'cutbacks', 'delays', 'crash_net', 'screens', 'give_and_go', 'second_touch', 'cycles'
  ],
  'Defensive Skills': [
    'poke_checks', 'stick_checks', 'zone_ent_denials', 'backchecks', 'forechecks', 'breakouts'
  ],
  'Puck Battles': [
    'puck_battles_total', 'loose_puck_wins', 'puck_recoveries', 'board_battles_won'
  ],
  'Passing': [
    'passes_stretch', 'passes_rim', 'passes_bank', 'passes_cross_ice', 'passes_breakout',
    'passes_royal_road', 'passes_slot', 'passes_behind_net'
  ],
  'Shooting': [
    'shots_one_timer', 'shots_snap', 'shots_wrist', 'shots_slap', 'shots_tip', 'shots_deflection'
  ],
  'Zone Play': [
    'dump_ins', 'micro_off_zone', 'micro_def_zone', 'micro_neutral_zone'
  ]
}

export default async function MicroStatsExplorerPage() {
  const supabase = await createClient()
  
  // Get micro stats aggregated by player
  // Note: fact_player_micro_stats might be structured differently, so we'll query fact_player_game_stats
  // which should have micro stats as columns
  const { data: playerStats } = await supabase
    .from('fact_player_game_stats')
    .select(`
      player_id,
      player_name,
      game_id,
      dekes,
      drives_total,
      drives_middle,
      drives_wide,
      drives_corner,
      cutbacks,
      delays,
      crash_net,
      screens,
      give_and_go,
      second_touch,
      cycles,
      poke_checks,
      stick_checks,
      zone_ent_denials,
      backchecks,
      forechecks,
      breakouts,
      dump_ins,
      loose_puck_wins,
      puck_recoveries,
      puck_battles_total,
      plays_successful,
      plays_unsuccessful,
      play_success_rate
    `)
    .not('dekes', 'is', null)
    .limit(1000)
  
  // Aggregate micro stats by player
  const playerMicroStats = new Map<string, any>()
  
  if (playerStats) {
    for (const stat of playerStats) {
      const playerId = String(stat.player_id)
      if (!playerMicroStats.has(playerId)) {
        playerMicroStats.set(playerId, {
          player_id: playerId,
          player_name: stat.player_name,
          games: 0,
          dekes: 0,
          drives_total: 0,
          drives_middle: 0,
          drives_wide: 0,
          drives_corner: 0,
          cutbacks: 0,
          delays: 0,
          crash_net: 0,
          screens: 0,
          give_and_go: 0,
          second_touch: 0,
          cycles: 0,
          poke_checks: 0,
          stick_checks: 0,
          zone_ent_denials: 0,
          backchecks: 0,
          forechecks: 0,
          breakouts: 0,
          dump_ins: 0,
          loose_puck_wins: 0,
          puck_recoveries: 0,
          puck_battles_total: 0,
          plays_successful: 0,
          plays_unsuccessful: 0,
        })
      }
      
      const player = playerMicroStats.get(playerId)!
      player.games += 1
      player.dekes += Number(stat.dekes || 0)
      player.drives_total += Number(stat.drives_total || 0)
      player.drives_middle += Number(stat.drives_middle || 0)
      player.drives_wide += Number(stat.drives_wide || 0)
      player.drives_corner += Number(stat.drives_corner || 0)
      player.cutbacks += Number(stat.cutbacks || 0)
      player.delays += Number(stat.delays || 0)
      player.crash_net += Number(stat.crash_net || 0)
      player.screens += Number(stat.screens || 0)
      player.give_and_go += Number(stat.give_and_go || 0)
      player.second_touch += Number(stat.second_touch || 0)
      player.cycles += Number(stat.cycles || 0)
      player.poke_checks += Number(stat.poke_checks || 0)
      player.stick_checks += Number(stat.stick_checks || 0)
      player.zone_ent_denials += Number(stat.zone_ent_denials || 0)
      player.backchecks += Number(stat.backchecks || 0)
      player.forechecks += Number(stat.forechecks || 0)
      player.breakouts += Number(stat.breakouts || 0)
      player.dump_ins += Number(stat.dump_ins || 0)
      player.loose_puck_wins += Number(stat.loose_puck_wins || 0)
      player.puck_recoveries += Number(stat.puck_recoveries || 0)
      player.puck_battles_total += Number(stat.puck_battles_total || 0)
      player.plays_successful += Number(stat.plays_successful || 0)
      player.plays_unsuccessful += Number(stat.plays_unsuccessful || 0)
    }
  }
  
  // Convert to array and calculate per-game rates
  const aggregatedStats = Array.from(playerMicroStats.values()).map(player => ({
    ...player,
    dekesPerGame: player.games > 0 ? (player.dekes / player.games) : 0,
    drivesPerGame: player.games > 0 ? (player.drives_total / player.games) : 0,
    puckBattlesPerGame: player.games > 0 ? (player.puck_battles_total / player.games) : 0,
    forechecksPerGame: player.games > 0 ? (player.forechecks / player.games) : 0,
    backchecksPerGame: player.games > 0 ? (player.backchecks / player.games) : 0,
    playSuccessRate: (player.plays_successful + player.plays_unsuccessful) > 0
      ? (player.plays_successful / (player.plays_successful + player.plays_unsuccessful)) * 100
      : 0
  }))
  
  // Get players for photos
  const playerIds = aggregatedStats.map(p => p.player_id)
  const { data: playersData } = await supabase
    .from('dim_player')
    .select('player_id, player_name, player_full_name, player_image, team_id')
    .in('player_id', playerIds)
  
  const playersMap = new Map(
    (playersData || []).map(p => [String(p.player_id), p])
  )
  
  // Get teams for logos
  const teamIds = [...new Set((playersData || []).map(p => p.team_id).filter(Boolean))]
  const { data: teamsData } = await supabase
    .from('dim_team')
    .select('team_id, team_name, team_logo, team_cd, primary_color, team_color1')
    .in('team_id', teamIds)
  
  const teamsMap = new Map(
    (teamsData || []).map(t => [String(t.team_id), t])
  )
  
  // Add player and team data
  const statsWithPlayers = aggregatedStats.map(stat => {
    const player = playersMap.get(stat.player_id)
    const team = player ? teamsMap.get(String(player.team_id)) : null
    return { ...stat, player, team }
  })
  
  // Top performers by category
  const topDekes = [...statsWithPlayers].sort((a, b) => b.dekesPerGame - a.dekesPerGame).slice(0, 10)
  const topDrives = [...statsWithPlayers].sort((a, b) => b.drivesPerGame - a.drivesPerGame).slice(0, 10)
  const topPuckBattles = [...statsWithPlayers].sort((a, b) => b.puckBattlesPerGame - a.puckBattlesPerGame).slice(0, 10)
  const topForechecks = [...statsWithPlayers].sort((a, b) => b.forechecksPerGame - a.forechecksPerGame).slice(0, 10)
  
  return (
    <div className="space-y-6">
      {/* Back Link */}
      <Link 
        href="/norad/analytics/overview" 
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Analytics
      </Link>
      
      {/* Header */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="px-4 py-3 bg-accent border-b border-border">
          <h1 className="font-display text-lg font-semibold uppercase tracking-wider flex items-center gap-2">
            <Zap className="w-5 h-5" />
            Micro Stats Explorer
          </h1>
        </div>
        <div className="p-6">
          <p className="text-sm text-muted-foreground mb-6">
            Micro statistics track detailed player actions and skills that don't show up in traditional box scores. 
            These metrics provide insight into a player's style of play and effectiveness.
          </p>
          
          {/* Summary Stats */}
          <div className="grid md:grid-cols-4 gap-4 mb-6">
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Players Tracked</div>
              <div className="font-mono text-2xl font-bold text-foreground">
                {statsWithPlayers.length}
              </div>
            </div>
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Total Dekes</div>
              <div className="font-mono text-2xl font-bold text-primary">
                {statsWithPlayers.reduce((sum, p) => sum + p.dekes, 0)}
              </div>
            </div>
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Total Drives</div>
              <div className="font-mono text-2xl font-bold text-assist">
                {statsWithPlayers.reduce((sum, p) => sum + p.drives_total, 0)}
              </div>
            </div>
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Puck Battles</div>
              <div className="font-mono text-2xl font-bold text-goal">
                {statsWithPlayers.reduce((sum, p) => sum + p.puck_battles_total, 0)}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Top Performers Grid */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Top Dekes */}
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Target className="w-4 h-4" />
              Top Dekes Per Game
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {topDekes.map((player, index) => (
                <Link
                  key={player.player_id}
                  href={`/players/${player.player_id}`}
                  className="flex items-center justify-between p-3 bg-muted/30 rounded-lg hover:bg-muted/50 transition-colors group"
                >
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-xs text-muted-foreground w-6">#{index + 1}</span>
                    {player.player && (
                      <PlayerPhoto
                        src={player.player.player_image || null}
                        name={player.player.player_name || ''}
                        size="xs"
                      />
                    )}
                    <div>
                      <div className="font-semibold text-foreground group-hover:text-primary transition-colors">
                        {player.player_name || player.player?.player_full_name || 'Unknown'}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {player.games} GP, {player.dekes} total
                      </div>
                    </div>
                  </div>
                  <div className="font-mono font-bold text-lg text-primary">
                    {player.dekesPerGame.toFixed(2)}
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
        
        {/* Top Drives */}
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Activity className="w-4 h-4" />
              Top Drives Per Game
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {topDrives.map((player, index) => (
                <Link
                  key={player.player_id}
                  href={`/players/${player.player_id}`}
                  className="flex items-center justify-between p-3 bg-muted/30 rounded-lg hover:bg-muted/50 transition-colors group"
                >
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-xs text-muted-foreground w-6">#{index + 1}</span>
                    {player.player && (
                      <PlayerPhoto
                        src={player.player.player_image || null}
                        name={player.player.player_name || ''}
                        size="xs"
                      />
                    )}
                    <div>
                      <div className="font-semibold text-foreground group-hover:text-primary transition-colors">
                        {player.player_name || player.player?.player_full_name || 'Unknown'}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {player.games} GP, {player.drives_total} total
                      </div>
                    </div>
                  </div>
                  <div className="font-mono font-bold text-lg text-primary">
                    {player.drivesPerGame.toFixed(2)}
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
        
        {/* Top Puck Battles */}
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Zap className="w-4 h-4" />
              Top Puck Battles Per Game
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {topPuckBattles.map((player, index) => (
                <Link
                  key={player.player_id}
                  href={`/players/${player.player_id}`}
                  className="flex items-center justify-between p-3 bg-muted/30 rounded-lg hover:bg-muted/50 transition-colors group"
                >
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-xs text-muted-foreground w-6">#{index + 1}</span>
                    {player.player && (
                      <PlayerPhoto
                        src={player.player.player_image || null}
                        name={player.player.player_name || ''}
                        size="xs"
                      />
                    )}
                    <div>
                      <div className="font-semibold text-foreground group-hover:text-primary transition-colors">
                        {player.player_name || player.player?.player_full_name || 'Unknown'}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {player.games} GP, {player.puck_battles_total} total
                      </div>
                    </div>
                  </div>
                  <div className="font-mono font-bold text-lg text-primary">
                    {player.puckBattlesPerGame.toFixed(2)}
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
        
        {/* Top Forechecks */}
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Top Forechecks Per Game
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {topForechecks.map((player, index) => (
                <Link
                  key={player.player_id}
                  href={`/players/${player.player_id}`}
                  className="flex items-center justify-between p-3 bg-muted/30 rounded-lg hover:bg-muted/50 transition-colors group"
                >
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-xs text-muted-foreground w-6">#{index + 1}</span>
                    {player.player && (
                      <PlayerPhoto
                        src={player.player.player_image || null}
                        name={player.player.player_name || ''}
                        size="xs"
                      />
                    )}
                    <div>
                      <div className="font-semibold text-foreground group-hover:text-primary transition-colors">
                        {player.player_name || player.player?.player_full_name || 'Unknown'}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {player.games} GP, {player.forechecks} total
                      </div>
                    </div>
                  </div>
                  <div className="font-mono font-bold text-lg text-primary">
                    {player.forechecksPerGame.toFixed(2)}
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>
      
      {/* Comprehensive Micro Stats Table */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="px-4 py-3 bg-accent border-b border-border">
          <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
            <BarChart3 className="w-4 h-4" />
            Comprehensive Micro Stats
          </h2>
        </div>
        <div className="p-6">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-2 font-mono text-xs text-muted-foreground uppercase">Player</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">GP</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">Dekes</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">Drives</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">Puck Battles</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">Forechecks</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">Backchecks</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">Loose Puck Wins</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">Success Rate</th>
                </tr>
              </thead>
              <tbody>
                {statsWithPlayers.slice(0, 50).map((stat) => (
                  <tr key={stat.player_id} className="border-b border-border/50 hover:bg-muted/30">
                    <td className="py-3">
                      <Link 
                        href={`/players/${stat.player_id}`}
                        className="flex items-center gap-2 text-foreground hover:text-primary transition-colors"
                      >
                        {stat.player && (
                          <PlayerPhoto
                            src={stat.player.player_image || null}
                            name={stat.player.player_name || ''}
                            size="xs"
                          />
                        )}
                        <span className="font-semibold">
                          {stat.player_name || stat.player?.player_full_name || 'Unknown'}
                        </span>
                        {stat.team && (
                          <TeamLogo
                            src={stat.team.team_logo || null}
                            name={stat.team.team_name || ''}
                            abbrev={stat.team.team_cd}
                            size="xs"
                            showGradient={false}
                          />
                        )}
                      </Link>
                    </td>
                    <td className="text-right py-3 font-mono">{stat.games}</td>
                    <td className="text-right py-3 font-mono">{stat.dekes}</td>
                    <td className="text-right py-3 font-mono">{stat.drives_total}</td>
                    <td className="text-right py-3 font-mono">{stat.puck_battles_total}</td>
                    <td className="text-right py-3 font-mono">{stat.forechecks}</td>
                    <td className="text-right py-3 font-mono">{stat.backchecks}</td>
                    <td className="text-right py-3 font-mono">{stat.loose_puck_wins}</td>
                    <td className="text-right py-3 font-mono">
                      {stat.playSuccessRate > 0 ? stat.playSuccessRate.toFixed(1) : '-'}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
