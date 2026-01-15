// src/app/(dashboard)/teams/free-agents/page.tsx
import Link from 'next/link'
import { getPlayers } from '@/lib/supabase/queries/players'
import { createClient } from '@/lib/supabase/server'
import { ArrowLeft, Users } from 'lucide-react'
import { PlayerPhoto } from '@/components/players/player-photo'

export const revalidate = 300

export async function generateMetadata() {
  return {
    title: 'Free Agents | BenchSight',
    description: 'Players not currently assigned to a team',
  }
}

export default async function FreeAgentsPage() {
  const supabase = await createClient()
  
  // Get all players
  const players = await getPlayers()
  
  // Filter to free agents (current_team = 'free agent' or no current team)
  const freeAgents = players.filter(p => {
    const currentTeam = String(p.player_norad_current_team || '').trim()
    const currentTeamId = String(p.player_norad_current_team_id || '').trim()
    
    // Check if current team name is 'free agent' (case-insensitive)
    const isFreeAgent = currentTeam.toLowerCase() === 'free agent' || 
                        currentTeam.toLowerCase().includes('free agent')
    
    // Also include players with no current team ID or empty/null values
    const hasNoTeam = !currentTeamId || 
                      currentTeamId === '' || 
                      currentTeamId === 'null' ||
                      currentTeamId.toLowerCase() === 'null'
    
    return isFreeAgent || hasNoTeam
  })
  
  // Get stats for free agents from current season
  const playerIds = freeAgents.map(p => String(p.player_id)).filter(Boolean)
  let freeAgentStats: any[] = []
  
  if (playerIds.length > 0) {
    try {
      const { data: stats, error } = await supabase
        .from('v_rankings_players_current')
        .select('*')
        .in('player_id', playerIds)
      
      if (error) {
        console.error('Error fetching free agent stats:', error)
      }
      
      freeAgentStats = stats || []
    } catch (error) {
      console.error('Error fetching free agent stats:', error)
      freeAgentStats = []
    }
  }
  
  // Create stats map
  const statsMap = new Map(freeAgentStats.map(s => [String(s.player_id), s]))
  
  // Merge player info with stats and sort by points
  const freeAgentsWithStats = freeAgents.map(player => {
    const stats = statsMap.get(String(player.player_id))
    return {
      ...player,
      ...stats,
      player_name: player.player_name || player.player_full_name || 'Unknown Player',
      games_played: stats?.games_played ?? 0,
      goals: stats?.goals ?? 0,
      assists: stats?.assists ?? 0,
      points: stats?.points ?? 0,
      points_per_game: stats?.points_per_game ?? (stats?.games_played > 0 ? (stats?.points ?? 0) / stats.games_played : 0),
    }
  }).sort((a, b) => (b.points ?? 0) - (a.points ?? 0))
  
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
      
      {/* Header */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="p-6">
          <div className="flex items-center gap-6">
            <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center">
              <Users className="w-8 h-8 text-muted-foreground" />
            </div>
            <div>
              <h1 className="font-display text-3xl font-bold tracking-wider text-foreground">
                Free Agents
              </h1>
              <p className="text-sm text-muted-foreground mt-1">
                Players not currently assigned to a team
              </p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Roster */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="px-4 py-3 bg-accent border-b border-border">
          <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
            <Users className="w-4 h-4" />
            Free Agents ({freeAgentsWithStats.length} players)
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-accent/50">
                <th className="px-3 py-2 text-left font-display text-xs text-muted-foreground">Player</th>
                <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">Position</th>
                <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">GP</th>
                <th className="px-2 py-2 text-center font-display text-xs text-goal">G</th>
                <th className="px-2 py-2 text-center font-display text-xs text-assist">A</th>
                <th className="px-2 py-2 text-center font-display text-xs text-primary">P</th>
                <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">P/G</th>
              </tr>
            </thead>
            <tbody>
              {freeAgentsWithStats.length > 0 ? (
                freeAgentsWithStats.map((player) => {
                  return (
                    <tr key={player.player_id} className="border-b border-border hover:bg-muted/50">
                      <td className="px-3 py-2">
                        <Link 
                          href={`/norad/players/${player.player_id}`}
                          className="flex items-center gap-2 text-foreground hover:text-primary transition-colors"
                        >
                          <PlayerPhoto
                            src={player.player_image || null}
                            name={player.player_name || ''}
                            size="sm"
                          />
                          <span>{player.player_name}</span>
                        </Link>
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                        {player.player_primary_position || player.position || '-'}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-muted-foreground">{player.games_played ?? 0}</td>
                      <td className="px-2 py-2 text-center font-mono text-goal font-semibold">{player.goals ?? 0}</td>
                      <td className="px-2 py-2 text-center font-mono text-assist">{player.assists ?? 0}</td>
                      <td className="px-2 py-2 text-center font-mono text-primary font-semibold">{player.points ?? 0}</td>
                      <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                        {player.points_per_game ? player.points_per_game.toFixed(2) : '-'}
                      </td>
                    </tr>
                  )
                })
              ) : (
                <tr>
                  <td colSpan={7} className="px-3 py-4 text-center text-sm text-muted-foreground">
                    No free agents found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
