// src/app/(dashboard)/analytics/faceoffs/page.tsx
import Link from 'next/link'
import { createClient } from '@/lib/supabase/server'
import { ArrowLeft, Target, TrendingUp, BarChart3, Activity, Users } from 'lucide-react'
import { cn } from '@/lib/utils'
import { PlayerPhoto } from '@/components/players/player-photo'
import { TeamLogo } from '@/components/teams/team-logo'
import { ExportButton } from '@/components/export/ExportButton'

export const revalidate = 300

export const metadata = {
  title: 'Faceoff Analysis | BenchSight Analytics',
  description: 'Faceoff leaders, win percentages, and zone analysis',
}

export default async function FaceoffAnalysisPage() {
  const supabase = await createClient()
  
  // Get faceoff stats from player game stats
  const { data: playerStats } = await supabase
    .from('fact_player_game_stats')
    .select(`
      player_id,
      player_name,
      game_id,
      fo_wins,
      fo_losses,
      fo_total,
      fo_pct
    `)
    .not('fo_total', 'is', null)
    .gt('fo_total', 0)
    .limit(1000)
  
  // Aggregate faceoff stats by player
  const playerFaceoffStats = new Map<string, any>()
  
  if (playerStats) {
    for (const stat of playerStats) {
      const playerId = String(stat.player_id)
      if (!playerFaceoffStats.has(playerId)) {
        playerFaceoffStats.set(playerId, {
          player_id: playerId,
          player_name: stat.player_name,
          games: 0,
          foWins: 0,
          foLosses: 0,
          foTotal: 0,
        })
      }
      
      const player = playerFaceoffStats.get(playerId)!
      player.games += 1
      player.foWins += Number(stat.fo_wins || 0)
      player.foLosses += Number(stat.fo_losses || 0)
      player.foTotal += Number(stat.fo_total || 0)
    }
  }
  
  // Convert to array and calculate rates
  const aggregatedStats = Array.from(playerFaceoffStats.values()).map(player => {
    const foPct = player.foTotal > 0 ? (player.foWins / player.foTotal) * 100 : 0
    return {
      ...player,
      foPct,
      foWinsPerGame: player.games > 0 ? (player.foWins / player.games) : 0,
      foTotalPerGame: player.games > 0 ? (player.foTotal / player.games) : 0,
    }
  })
  
  // Get players for photos
  const playerIds = aggregatedStats.map(p => p.player_id)
  const { data: playersData } = await supabase
    .from('dim_player')
    .select('player_id, player_name, player_full_name, player_image, team_id, player_primary_position')
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
  
  // Top performers
  const topFaceoffWinPct = [...statsWithPlayers]
    .filter(p => p.foTotal >= 20)
    .sort((a, b) => b.foPct - a.foPct)
    .slice(0, 10)
  
  const topFaceoffWins = [...statsWithPlayers]
    .sort((a, b) => b.foWins - a.foWins)
    .slice(0, 10)
  
  const topFaceoffVolume = [...statsWithPlayers]
    .sort((a, b) => b.foTotal - a.foTotal)
    .slice(0, 10)
  
  // Calculate summary stats
  const totalFaceoffs = statsWithPlayers.reduce((sum, p) => sum + p.foTotal, 0)
  const totalWins = statsWithPlayers.reduce((sum, p) => sum + p.foWins, 0)
  const avgWinPct = totalFaceoffs > 0 ? (totalWins / totalFaceoffs) * 100 : 0
  
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
            <Target className="w-5 h-5" />
            Faceoff Analysis
          </h1>
        </div>
        <div className="p-6">
          <p className="text-sm text-muted-foreground mb-6">
            Faceoffs are critical possession battles. Winning faceoffs, especially in key zones, 
            can significantly impact game outcomes.
          </p>
          
          {/* Summary Stats */}
          <div className="grid md:grid-cols-4 gap-4 mb-6">
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Total Faceoffs</div>
              <div className="font-mono text-2xl font-bold text-foreground">
                {totalFaceoffs}
              </div>
            </div>
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Total Wins</div>
              <div className="font-mono text-2xl font-bold text-save">
                {totalWins}
              </div>
            </div>
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Avg Win %</div>
              <div className="font-mono text-2xl font-bold text-primary">
                {avgWinPct.toFixed(1)}%
              </div>
            </div>
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Players Tracked</div>
              <div className="font-mono text-2xl font-bold text-assist">
                {statsWithPlayers.length}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Top Performers Grid */}
      <div className="grid md:grid-cols-3 gap-6">
        {/* Top Faceoff Win % */}
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Top Win % (Min 20 FO)
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {topFaceoffWinPct.map((player, index) => (
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
                        {player.foWins}/{player.foTotal}
                      </div>
                    </div>
                  </div>
                  <div className="font-mono font-bold text-lg text-save">
                    {player.foPct.toFixed(1)}%
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
        
        {/* Top Faceoff Wins */}
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Activity className="w-4 h-4" />
              Top Faceoff Wins
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {topFaceoffWins.map((player, index) => (
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
                        {player.foPct.toFixed(1)}% win rate
                      </div>
                    </div>
                  </div>
                  <div className="font-mono font-bold text-lg text-primary">
                    {player.foWins}
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
        
        {/* Top Faceoff Volume */}
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Users className="w-4 h-4" />
              Top Faceoff Volume
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {topFaceoffVolume.map((player, index) => (
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
                        {player.foPct.toFixed(1)}% win rate
                      </div>
                    </div>
                  </div>
                  <div className="font-mono font-bold text-lg text-primary">
                    {player.foTotal}
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>
      
      {/* Comprehensive Faceoff Stats Table */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="px-4 py-3 bg-accent border-b border-border flex items-center justify-between">
          <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
            <BarChart3 className="w-4 h-4" />
            Comprehensive Faceoff Statistics
          </h2>
          <ExportButton 
            data={statsWithPlayers
              .filter(p => p.foTotal > 0)
              .map(f => ({
                Player: f.playerName,
                Team: f.teamName,
                GP: f.games,
                Wins: f.totalWins,
                Losses: f.totalLosses,
                Total: f.foTotal,
                'Win %': f.winPct.toFixed(1) + '%',
                'Avg/G': f.avgPerGame.toFixed(1),
              }))}
            filename="faceoff_stats"
          />
        </div>
        <div className="p-6">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-2 font-mono text-xs text-muted-foreground uppercase">Player</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">GP</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">Total</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">Wins</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">Losses</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">Win %</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">FO/Game</th>
                </tr>
              </thead>
              <tbody>
                {statsWithPlayers
                  .filter(p => p.foTotal > 0)
                  .sort((a, b) => b.foTotal - a.foTotal)
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
                    <td className="text-right py-3 font-mono font-semibold text-primary">{stat.foTotal}</td>
                    <td className="text-right py-3 font-mono text-save">{stat.foWins}</td>
                    <td className="text-right py-3 font-mono text-goal">{stat.foLosses}</td>
                    <td className={cn(
                      "text-right py-3 font-mono font-semibold",
                      stat.foPct >= 50 ? "text-save" : "text-goal"
                    )}>
                      {stat.foPct.toFixed(1)}%
                    </td>
                    <td className="text-right py-3 font-mono">{stat.foTotalPerGame.toFixed(1)}</td>
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
