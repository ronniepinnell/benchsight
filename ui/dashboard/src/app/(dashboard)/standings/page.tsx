// src/app/(dashboard)/standings/page.tsx
import Link from 'next/link'
import { getStandings } from '@/lib/supabase/queries/teams'
import { getLeagueSummary } from '@/lib/supabase/queries/league'
import { Trophy, Target, Users, Calendar } from 'lucide-react'
import { cn } from '@/lib/utils'

export const revalidate = 300

export const metadata = {
  title: 'Standings | BenchSight',
  description: 'NORAD Hockey League standings',
}

export default async function StandingsPage() {
  const [standings, leagueSummary] = await Promise.all([
    getStandings(),
    getLeagueSummary()
  ])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold tracking-wider uppercase flex items-center gap-3">
          <span className="w-1 h-6 bg-primary rounded" />
          League Standings
        </h1>
        <p className="text-sm text-muted-foreground mt-2 ml-4">Current season team rankings</p>
      </div>

      {leagueSummary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-card rounded-lg p-4 border border-border">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="w-4 h-4 text-primary" />
              <span className="text-xs font-mono text-muted-foreground uppercase">Games</span>
            </div>
            <div className="font-mono text-2xl font-bold text-foreground">{leagueSummary.total_games}</div>
          </div>
          <div className="bg-card rounded-lg p-4 border border-border">
            <div className="flex items-center gap-2 mb-2">
              <Target className="w-4 h-4 text-goal" />
              <span className="text-xs font-mono text-muted-foreground uppercase">Goals</span>
            </div>
            <div className="font-mono text-2xl font-bold text-goal">{leagueSummary.total_goals}</div>
          </div>
          <div className="bg-card rounded-lg p-4 border border-border">
            <div className="flex items-center gap-2 mb-2">
              <Trophy className="w-4 h-4 text-assist" />
              <span className="text-xs font-mono text-muted-foreground uppercase">Teams</span>
            </div>
            <div className="font-mono text-2xl font-bold text-foreground">{leagueSummary.total_teams}</div>
          </div>
          <div className="bg-card rounded-lg p-4 border border-border">
            <div className="flex items-center gap-2 mb-2">
              <Users className="w-4 h-4 text-shot" />
              <span className="text-xs font-mono text-muted-foreground uppercase">Players</span>
            </div>
            <div className="font-mono text-2xl font-bold text-foreground">{leagueSummary.total_players}</div>
          </div>
        </div>
      )}

      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-accent border-b-2 border-border">
                <th className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase w-16">#</th>
                <th className="px-4 py-3 text-left font-display text-xs font-semibold text-muted-foreground uppercase">Team</th>
                <th className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase">GP</th>
                <th className="px-4 py-3 text-center font-display text-xs font-semibold text-save uppercase">W</th>
                <th className="px-4 py-3 text-center font-display text-xs font-semibold text-goal uppercase">L</th>
                <th className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase">WIN%</th>
                <th className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase">GF</th>
                <th className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase">GA</th>
                <th className="px-4 py-3 text-center font-display text-xs font-semibold text-primary uppercase">DIFF</th>
              </tr>
            </thead>
            <tbody>
              {standings.map((team) => {
                const winPct = team.games_played > 0 ? ((team.wins / team.games_played) * 100).toFixed(1) : '0.0'
                const isPlayoffSpot = team.standing <= 4
                
                return (
                  <tr key={team.team_id} className={cn(
                    'border-b border-border transition-colors hover:bg-muted/50',
                    team.standing % 2 === 0 && 'bg-accent/30',
                    isPlayoffSpot && 'border-l-2 border-l-save'
                  )}>
                    <td className="px-4 py-3 text-center">
                      <span className={cn('font-display font-bold', team.standing === 1 ? 'text-lg text-assist' : 'text-muted-foreground')}>
                        {team.standing}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <Link href={`/teams/${encodeURIComponent(team.team_name)}`} className="font-display text-sm text-foreground hover:text-primary transition-colors">
                        {team.team_name}
                      </Link>
                    </td>
                    <td className="px-4 py-3 text-center font-mono text-sm text-muted-foreground">{team.games_played}</td>
                    <td className="px-4 py-3 text-center font-mono text-sm text-save font-semibold">{team.wins}</td>
                    <td className="px-4 py-3 text-center font-mono text-sm text-goal">{team.losses}</td>
                    <td className="px-4 py-3 text-center font-mono text-sm text-foreground">{winPct}%</td>
                    <td className="px-4 py-3 text-center font-mono text-sm text-muted-foreground">{team.goals_for}</td>
                    <td className="px-4 py-3 text-center font-mono text-sm text-muted-foreground">{team.goals_against}</td>
                    <td className={cn('px-4 py-3 text-center font-mono text-sm font-bold',
                      team.goal_diff > 0 ? 'text-save' : team.goal_diff < 0 ? 'text-goal' : 'text-muted-foreground'
                    )}>
                      {team.goal_diff > 0 ? '+' : ''}{team.goal_diff}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
