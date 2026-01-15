// src/components/teams/team-lines-tab.tsx
import Link from 'next/link'
import { createClient } from '@/lib/supabase/server'
import { Users, TrendingUp, Target, Activity } from 'lucide-react'
import { cn } from '@/lib/utils'
import { PlayerPhoto } from '@/components/players/player-photo'

interface TeamLinesTabProps {
  teamId: string
  teamName: string
  seasonId: string
  playersMap: Map<string, any>
  team: any
}

export async function TeamLinesTab({ teamId, teamName, seasonId, playersMap, team }: TeamLinesTabProps) {
  const supabase = await createClient()
  
  // Get line combinations for this team
  // fact_line_combos has home_team_id and away_team_id, and venue ('home' or 'away')
  // First get games for this team in this season
  const { data: scheduleGames } = await supabase
    .from('dim_schedule')
    .select('game_id, home_team_id, away_team_id')
    .eq('season_id', seasonId)
    .or(`home_team_id.eq.${teamId},away_team_id.eq.${teamId}`)
  
  const gameIds = (scheduleGames || []).map(g => g.game_id).filter(Boolean)
  
  if (gameIds.length === 0) {
    return (
      <div className="space-y-6">
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Users className="w-4 h-4" />
              Line Combinations - {teamName}
            </h2>
          </div>
          <div className="p-6">
            <div className="text-center py-8 text-muted-foreground">
              No games found for {teamName} in this season.
            </div>
          </div>
        </div>
      </div>
    )
  }
  
  const { data: lineCombos } = await supabase
    .from('fact_line_combos')
    .select('*')
    .in('game_id', gameIds)
    .eq('combo_type', 'forward')
    .limit(500)
  
  // Create a map of game_id -> team venue for filtering
  const gameVenueMap = new Map<number, 'home' | 'away'>()
  scheduleGames?.forEach((game: any) => {
    if (game.home_team_id === teamId) {
      gameVenueMap.set(game.game_id, 'home')
    } else if (game.away_team_id === teamId) {
      gameVenueMap.set(game.game_id, 'away')
    }
  })
  
  // Filter to only this team's lines (by venue)
  const teamLines = (lineCombos || []).filter((combo: any) => {
    const gameId = combo.game_id
    const expectedVenue = gameVenueMap.get(gameId)
    return expectedVenue && combo.venue === expectedVenue
  })
  
  // Aggregate by forward combo
  const linePerformance = new Map<string, any>()
  
  for (const combo of teamLines) {
    const forwardCombo = combo.forward_combo || ''
    if (!forwardCombo) continue
    
    if (!linePerformance.has(forwardCombo)) {
      linePerformance.set(forwardCombo, {
        forwardCombo,
        games: 0,
        toi: 0,
        goalsFor: 0,
        goalsAgainst: 0,
        cf: 0,
        ca: 0,
      })
    }
    
    const line = linePerformance.get(forwardCombo)!
    line.games += 1
    line.toi += Number(combo.toi_together || 0)
    line.goalsFor += Number(combo.goals_for || 0)
    line.goalsAgainst += Number(combo.goals_against || 0)
    line.cf += Number(combo.corsi_for || 0)
    line.ca += Number(combo.corsi_against || 0)
  }
  
  // Convert to array and calculate rates
  const lineStats = Array.from(linePerformance.values())
    .filter(line => line.games > 0 && line.toi > 0)
    .map(line => {
      const cfPct = (line.cf + line.ca) > 0 ? (line.cf / (line.cf + line.ca)) * 100 : 50
      const gfPct = (line.goalsFor + line.goalsAgainst) > 0 ? (line.goalsFor / (line.goalsFor + line.goalsAgainst)) * 100 : 50
      const toiMinutes = line.toi / 60
      
      // Parse forward combo (comma-separated player IDs)
      const playerIds = line.forwardCombo.split(',').filter(Boolean)
      
      return {
        ...line,
        playerIds,
        cfPct,
        gfPct,
        toiMinutes,
        goalsForPer60: toiMinutes > 0 ? (line.goalsFor / toiMinutes) * 60 : 0,
        goalsAgainstPer60: toiMinutes > 0 ? (line.goalsAgainst / toiMinutes) * 60 : 0,
        goalDiff: line.goalsFor - line.goalsAgainst,
      }
    })
    .sort((a, b) => b.toiMinutes - a.toiMinutes)
  
  // Get player names
  const allPlayerIds = new Set<string>()
  lineStats.forEach(line => {
    line.playerIds.forEach((id: string) => allPlayerIds.add(id))
  })
  
  const { data: playersData } = await supabase
    .from('dim_player')
    .select('player_id, player_name, player_full_name')
    .in('player_id', Array.from(allPlayerIds))
  
  const playersNameMap = new Map(
    (playersData || []).map(p => [String(p.player_id), p])
  )
  
  // Add player names to lines
  const linesWithNames = lineStats.map(line => {
    const playerNames = line.playerIds
      .map((id: string) => {
        const player = playersNameMap.get(id) || playersMap.get(id)
        return player?.player_name || player?.player_full_name || 'Unknown'
      })
      .filter(Boolean)
    
    return {
      ...line,
      lineName: playerNames.join(' - '),
    }
  })
  
  return (
    <div className="space-y-6">
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="px-4 py-3 bg-accent border-b border-border">
          <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
            <Users className="w-4 h-4" />
            Line Combinations - {teamName}
          </h2>
        </div>
        <div className="p-6">
          <p className="text-sm text-muted-foreground mb-6">
            Forward line combinations for {teamName}. See <Link href="/norad/analytics/lines" className="text-primary hover:underline">Line Combinations Analysis</Link> for league-wide data.
          </p>
          
          {linesWithNames.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border bg-accent/50">
                    <th className="px-3 py-2 text-left font-display text-xs text-muted-foreground">Line</th>
                    <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">GP</th>
                    <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">TOI</th>
                    <th className="px-2 py-2 text-center font-display text-xs text-save">GF</th>
                    <th className="px-2 py-2 text-center font-display text-xs text-goal">GA</th>
                    <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">CF%</th>
                    <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">GF%</th>
                  </tr>
                </thead>
                <tbody>
                  {linesWithNames.map((line, index) => (
                    <tr key={index} className="border-b border-border/50 hover:bg-muted/30">
                      <td className="px-3 py-3">
                        <div className="flex items-center gap-2">
                          {line.playerIds.slice(0, 3).map((playerId: string) => {
                            const player = playersNameMap.get(playerId) || playersMap.get(playerId)
                            return (
                              <Link
                                key={playerId}
                                href={`/norad/players/${playerId}`}
                                className="flex items-center gap-1 text-foreground hover:text-primary transition-colors"
                              >
                                <PlayerPhoto
                                  src={player?.player_image || null}
                                  name={player?.player_name || ''}
                                  size="xs"
                                />
                                <span className="text-xs font-semibold">
                                  {player?.player_name || player?.player_full_name || 'Unknown'}
                                </span>
                              </Link>
                            )
                          })}
                        </div>
                      </td>
                      <td className="px-2 py-3 text-center font-mono">{line.games}</td>
                      <td className="px-2 py-3 text-center font-mono">{Math.round(line.toiMinutes)}</td>
                      <td className="px-2 py-3 text-center font-mono text-save">{line.goalsFor}</td>
                      <td className="px-2 py-3 text-center font-mono text-goal">{line.goalsAgainst}</td>
                      <td className={cn(
                        "px-2 py-3 text-center font-mono font-semibold",
                        line.cfPct >= 50 ? "text-save" : "text-goal"
                      )}>
                        {line.cfPct.toFixed(1)}%
                      </td>
                      <td className={cn(
                        "px-2 py-3 text-center font-mono",
                        line.gfPct >= 50 ? "text-save" : "text-goal"
                      )}>
                        {line.gfPct.toFixed(1)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              No line combination data available for {teamName} in this season.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
