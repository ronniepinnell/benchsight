// src/app/(dashboard)/analytics/zone/page.tsx
import Link from 'next/link'
import { createClient } from '@/lib/supabase/server'
import { ArrowLeft, Target, TrendingUp, BarChart3, Activity, MapPin } from 'lucide-react'
import { cn } from '@/lib/utils'
import { PlayerPhoto } from '@/components/players/player-photo'
import { TeamLogo } from '@/components/teams/team-logo'

export const revalidate = 300

export const metadata = {
  title: 'Zone Analytics | BenchSight Analytics',
  description: 'Zone entry and exit analysis, success rates, and zone time',
}

export default async function ZoneAnalyticsPage() {
  const supabase = await createClient()
  
  // Get zone entry summaries
  const { data: zoneEntries } = await supabase
    .from('fact_zone_entry_summary')
    .select('*')
    .limit(500)
  
  // Get zone exit summaries
  const { data: zoneExits } = await supabase
    .from('fact_zone_exit_summary')
    .select('*')
    .limit(500)
  
  // Aggregate zone entries by player
  const playerZoneEntries = new Map<string, any>()
  
  if (zoneEntries) {
    for (const entry of zoneEntries) {
      const playerId = String(entry.player_id)
      if (!playerZoneEntries.has(playerId)) {
        playerZoneEntries.set(playerId, {
          player_id: playerId,
          games: 0,
          totalEntries: 0,
          controlledEntries: 0,
          dumpEntries: 0,
          failedEntries: 0,
        })
      }
      
      const player = playerZoneEntries.get(playerId)!
      player.games += 1
      player.totalEntries += Number(entry.total_entries || 0)
      player.controlledEntries += Number(entry.controlled_entries || 0)
      player.dumpEntries += Number(entry.dump_entries || 0)
      player.failedEntries += Number(entry.failed_entries || 0)
    }
  }
  
  // Aggregate zone exits by player
  const playerZoneExits = new Map<string, any>()
  
  if (zoneExits) {
    for (const exit of zoneExits) {
      const playerId = String(exit.player_id)
      if (!playerZoneExits.has(playerId)) {
        playerZoneExits.set(playerId, {
          player_id: playerId,
          games: 0,
          totalExits: 0,
          controlledExits: 0,
          clearExits: 0,
          failedExits: 0,
        })
      }
      
      const player = playerZoneExits.get(playerId)!
      player.games += 1
      player.totalExits += Number(exit.total_exits || 0)
      player.controlledExits += Number(exit.controlled_exits || 0)
      player.clearExits += Number(exit.clear_exits || 0)
      player.failedExits += Number(exit.failed_exits || 0)
    }
  }
  
  // Combine entry and exit data
  const allPlayerIds = new Set([
    ...Array.from(playerZoneEntries.keys()),
    ...Array.from(playerZoneExits.keys())
  ])
  
  const zoneStats = Array.from(allPlayerIds).map(playerId => {
    const entries = playerZoneEntries.get(playerId) || {
      games: 0,
      totalEntries: 0,
      controlledEntries: 0,
      dumpEntries: 0,
      failedEntries: 0,
    }
    const exits = playerZoneExits.get(playerId) || {
      games: 0,
      totalExits: 0,
      controlledExits: 0,
      clearExits: 0,
      failedExits: 0,
    }
    
    const totalGames = Math.max(entries.games, exits.games)
    const entrySuccessRate = entries.totalEntries > 0
      ? ((entries.controlledEntries + entries.dumpEntries) / entries.totalEntries) * 100
      : 0
    const exitSuccessRate = exits.totalExits > 0
      ? ((exits.controlledExits + exits.clearExits) / exits.totalExits) * 100
      : 0
    const controlledEntryRate = entries.totalEntries > 0
      ? (entries.controlledEntries / entries.totalEntries) * 100
      : 0
    const controlledExitRate = exits.totalExits > 0
      ? (exits.controlledExits / exits.totalExits) * 100
      : 0
    
    return {
      player_id: playerId,
      games: totalGames,
      totalEntries: entries.totalEntries,
      controlledEntries: entries.controlledEntries,
      dumpEntries: entries.dumpEntries,
      failedEntries: entries.failedEntries,
      entrySuccessRate,
      controlledEntryRate,
      totalExits: exits.totalExits,
      controlledExits: exits.controlledExits,
      clearExits: exits.clearExits,
      failedExits: exits.failedExits,
      exitSuccessRate,
      controlledExitRate,
      entriesPerGame: totalGames > 0 ? (entries.totalEntries / totalGames) : 0,
      exitsPerGame: totalGames > 0 ? (exits.totalExits / totalGames) : 0,
    }
  })
  
  // Get players for photos
  const playerIds = zoneStats.map(s => s.player_id)
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
  const statsWithPlayers = zoneStats.map(stat => {
    const player = playersMap.get(stat.player_id)
    const team = player ? teamsMap.get(String(player.team_id)) : null
    return { ...stat, player, team, playerName: player?.player_name || player?.player_full_name || 'Unknown' }
  })
  
  // Top performers
  const topEntryLeaders = [...statsWithPlayers]
    .filter(p => p.totalEntries > 0)
    .sort((a, b) => b.entriesPerGame - a.entriesPerGame)
    .slice(0, 10)
  
  const topControlledEntryRate = [...statsWithPlayers]
    .filter(p => p.totalEntries >= 10)
    .sort((a, b) => b.controlledEntryRate - a.controlledEntryRate)
    .slice(0, 10)
  
  const topExitLeaders = [...statsWithPlayers]
    .filter(p => p.totalExits > 0)
    .sort((a, b) => b.exitsPerGame - a.exitsPerGame)
    .slice(0, 10)
  
  const topControlledExitRate = [...statsWithPlayers]
    .filter(p => p.totalExits >= 10)
    .sort((a, b) => b.controlledExitRate - a.controlledExitRate)
    .slice(0, 10)
  
  // Calculate summary stats
  const totalEntries = statsWithPlayers.reduce((sum, p) => sum + p.totalEntries, 0)
  const totalControlledEntries = statsWithPlayers.reduce((sum, p) => sum + p.controlledEntries, 0)
  const totalExits = statsWithPlayers.reduce((sum, p) => sum + p.totalExits, 0)
  const totalControlledExits = statsWithPlayers.reduce((sum, p) => sum + p.controlledExits, 0)
  const avgEntrySuccessRate = statsWithPlayers.length > 0
    ? statsWithPlayers.reduce((sum, p) => sum + p.entrySuccessRate, 0) / statsWithPlayers.length
    : 0
  const avgExitSuccessRate = statsWithPlayers.length > 0
    ? statsWithPlayers.reduce((sum, p) => sum + p.exitSuccessRate, 0) / statsWithPlayers.length
    : 0
  
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
            <MapPin className="w-5 h-5" />
            Zone Analytics
          </h1>
        </div>
        <div className="p-6">
          <p className="text-sm text-muted-foreground mb-6">
            Zone entries and exits are critical transition moments in hockey. Controlled entries/exits maintain possession 
            and create better scoring opportunities, while dump-ins and clears are safer but less effective.
          </p>
          
          {/* Summary Stats */}
          <div className="grid md:grid-cols-4 gap-4 mb-6">
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Total Entries</div>
              <div className="font-mono text-2xl font-bold text-foreground">
                {totalEntries}
              </div>
              <div className="text-xs text-muted-foreground mt-1">
                {totalControlledEntries} controlled
              </div>
            </div>
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Total Exits</div>
              <div className="font-mono text-2xl font-bold text-primary">
                {totalExits}
              </div>
              <div className="text-xs text-muted-foreground mt-1">
                {totalControlledExits} controlled
              </div>
            </div>
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Avg Entry Success</div>
              <div className="font-mono text-2xl font-bold text-assist">
                {avgEntrySuccessRate.toFixed(1)}%
              </div>
            </div>
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Avg Exit Success</div>
              <div className="font-mono text-2xl font-bold text-goal">
                {avgExitSuccessRate.toFixed(1)}%
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Zone Entry Leaders */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Target className="w-4 h-4" />
              Top Zone Entry Leaders (Per Game)
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {topEntryLeaders.map((player, index) => (
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
                        {player.playerName}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {player.totalEntries} total, {player.controlledEntries} controlled
                      </div>
                    </div>
                  </div>
                  <div className="font-mono font-bold text-lg text-primary">
                    {player.entriesPerGame.toFixed(2)}
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
        
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Top Controlled Entry Rate (Min 10 Entries)
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {topControlledEntryRate.map((player, index) => (
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
                        {player.playerName}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {player.controlledEntries}/{player.totalEntries} controlled
                      </div>
                    </div>
                  </div>
                  <div className="font-mono font-bold text-lg text-save">
                    {player.controlledEntryRate.toFixed(1)}%
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>
      
      {/* Zone Exit Leaders */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Activity className="w-4 h-4" />
              Top Zone Exit Leaders (Per Game)
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {topExitLeaders.map((player, index) => (
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
                        {player.playerName}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {player.totalExits} total, {player.controlledExits} controlled
                      </div>
                    </div>
                  </div>
                  <div className="font-mono font-bold text-lg text-primary">
                    {player.exitsPerGame.toFixed(2)}
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
        
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              Top Controlled Exit Rate (Min 10 Exits)
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {topControlledExitRate.map((player, index) => (
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
                        {player.playerName}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {player.controlledExits}/{player.totalExits} controlled
                      </div>
                    </div>
                  </div>
                  <div className="font-mono font-bold text-lg text-save">
                    {player.controlledExitRate.toFixed(1)}%
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>
      
      {/* Comprehensive Zone Stats Table */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="px-4 py-3 bg-accent border-b border-border">
          <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
            <BarChart3 className="w-4 h-4" />
            Comprehensive Zone Stats
          </h2>
        </div>
        <div className="p-6">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-2 font-mono text-xs text-muted-foreground uppercase">Player</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">GP</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">Entries</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">Controlled</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">Entry %</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">Exits</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">Controlled</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">Exit %</th>
                </tr>
              </thead>
              <tbody>
                {statsWithPlayers
                  .filter(p => p.totalEntries > 0 || p.totalExits > 0)
                  .sort((a, b) => (b.totalEntries + b.totalExits) - (a.totalEntries + a.totalExits))
                  .slice(0, 50)
                  .map((stat) => (
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
                          {stat.playerName}
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
                    <td className="text-right py-3 font-mono">{stat.totalEntries}</td>
                    <td className="text-right py-3 font-mono text-primary">{stat.controlledEntries}</td>
                    <td className="text-right py-3 font-mono">
                      {stat.controlledEntryRate > 0 ? stat.controlledEntryRate.toFixed(1) : '-'}%
                    </td>
                    <td className="text-right py-3 font-mono">{stat.totalExits}</td>
                    <td className="text-right py-3 font-mono text-primary">{stat.controlledExits}</td>
                    <td className="text-right py-3 font-mono">
                      {stat.controlledExitRate > 0 ? stat.controlledExitRate.toFixed(1) : '-'}%
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
