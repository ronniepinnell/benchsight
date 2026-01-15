// src/components/teams/team-matchups-tab.tsx
import Link from 'next/link'
import { createClient } from '@/lib/supabase/server'
import { getTeamById } from '@/lib/supabase/queries/teams'
import { Target, Trophy } from 'lucide-react'
import { cn } from '@/lib/utils'
import { TeamLogo } from './team-logo'

interface TeamMatchupsTabProps {
  teamId: string
  teamName: string
  seasonId: string
}

export async function TeamMatchupsTab({ teamId, teamName, seasonId }: TeamMatchupsTabProps) {
  const supabase = await createClient()
  
  // Get all games for this team in this season
  const { data: games } = await supabase
    .from('dim_schedule')
    .select('*')
    .eq('season_id', seasonId)
    .or(`home_team_id.eq.${teamId},away_team_id.eq.${teamId}`)
    .not('home_total_goals', 'is', null) // Only completed games
    .order('date', { ascending: false })
  
  // Aggregate head-to-head records
  const matchupMap = new Map<string, {
    teamId: string
    teamName: string
    wins: number
    losses: number
    ties: number
    goalsFor: number
    goalsAgainst: number
  }>()
  
  if (games) {
    for (const game of games) {
      const isHome = game.home_team_id === teamId
      const opponentId = isHome ? game.away_team_id : game.home_team_id
      const opponentName = isHome ? game.away_team_name : game.home_team_name
      
      if (!opponentId || !opponentName) continue
      
      const teamGoals = isHome ? (game.home_total_goals || 0) : (game.away_total_goals || 0)
      const oppGoals = isHome ? (game.away_total_goals || 0) : (game.home_total_goals || 0)
      
      if (!matchupMap.has(opponentId)) {
        matchupMap.set(opponentId, {
          teamId: opponentId,
          teamName: opponentName,
          wins: 0,
          losses: 0,
          ties: 0,
          goalsFor: 0,
          goalsAgainst: 0,
        })
      }
      
      const matchup = matchupMap.get(opponentId)!
      matchup.goalsFor += teamGoals
      matchup.goalsAgainst += oppGoals
      
      if (teamGoals > oppGoals) {
        matchup.wins += 1
      } else if (teamGoals < oppGoals) {
        matchup.losses += 1
      } else {
        matchup.ties += 1
      }
    }
  }
  
  // Convert to array and sort by total games
  const matchups = Array.from(matchupMap.values())
    .map(m => ({
      ...m,
      games: m.wins + m.losses + m.ties,
      winPct: (m.wins + m.losses + m.ties) > 0 ? (m.wins / (m.wins + m.losses + m.ties)) * 100 : 0,
      goalDiff: m.goalsFor - m.goalsAgainst,
    }))
    .sort((a, b) => b.games - a.games)
  
  // Get team logos
  const teamIds = matchups.map(m => m.teamId)
  const teams = await Promise.all(
    teamIds.map(id => getTeamById(id).catch(() => null))
  )
  const teamsMap = new Map(
    teams.filter(Boolean).map(t => [String(t!.team_id), t!])
  )
  
  return (
    <div className="bg-card rounded-xl border border-border overflow-hidden">
      <div className="px-4 py-3 bg-accent border-b border-border">
        <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
          <Target className="w-4 h-4" />
          Head-to-Head Matchups - {teamName}
        </h2>
      </div>
      <div className="p-6">
        {matchups.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-accent/50">
                  <th className="px-3 py-2 text-left font-display text-xs text-muted-foreground">Opponent</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">GP</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-save">W</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-goal">L</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">T</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-primary">Win %</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">GF</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">GA</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">Diff</th>
                </tr>
              </thead>
              <tbody>
                {matchups.map((matchup) => {
                  const opponentTeam = teamsMap.get(matchup.teamId)
                  return (
                    <tr key={matchup.teamId} className="border-b border-border/50 hover:bg-muted/30">
                      <td className="px-3 py-3">
                        <Link
                          href={`/norad/team/${(matchup.teamName || '').replace(/\s+/g, '_')}`}
                          className="flex items-center gap-2 text-foreground hover:text-primary transition-colors"
                        >
                          {opponentTeam && (
                            <TeamLogo
                              src={opponentTeam.team_logo || null}
                              name={opponentTeam.team_name || ''}
                              abbrev={opponentTeam.team_cd}
                              size="xs"
                              showGradient={false}
                            />
                          )}
                          <span className="font-semibold">{matchup.teamName}</span>
                        </Link>
                      </td>
                      <td className="px-2 py-3 text-center font-mono">{matchup.games}</td>
                      <td className="px-2 py-3 text-center font-mono text-save font-semibold">{matchup.wins}</td>
                      <td className="px-2 py-3 text-center font-mono text-goal">{matchup.losses}</td>
                      <td className="px-2 py-3 text-center font-mono text-muted-foreground">{matchup.ties}</td>
                      <td className="px-2 py-3 text-center font-mono font-semibold text-primary">
                        {matchup.winPct.toFixed(1)}%
                      </td>
                      <td className="px-2 py-3 text-center font-mono">{matchup.goalsFor}</td>
                      <td className="px-2 py-3 text-center font-mono">{matchup.goalsAgainst}</td>
                      <td className={cn(
                        "px-2 py-3 text-center font-mono font-semibold",
                        matchup.goalDiff > 0 ? "text-save" : matchup.goalDiff < 0 ? "text-goal" : ""
                      )}>
                        {matchup.goalDiff > 0 ? '+' : ''}{matchup.goalDiff}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            No matchup data available for {teamName} in this season.
          </div>
        )}
      </div>
    </div>
  )
}
