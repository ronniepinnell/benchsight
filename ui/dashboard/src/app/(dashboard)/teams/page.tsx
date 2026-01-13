// src/app/(dashboard)/teams/page.tsx
import Link from 'next/link'
import { getStandings } from '@/lib/supabase/queries/teams'
import { getTeamById } from '@/lib/supabase/queries/teams'
import { getCurrentSeason } from '@/lib/supabase/queries/league'
import { Users, Trophy, Target, Shield } from 'lucide-react'
import { cn } from '@/lib/utils'
import { TeamLogo } from '@/components/teams/team-logo'

export const revalidate = 300

export const metadata = {
  title: 'Teams | BenchSight',
  description: 'NORAD Hockey League teams - current season',
}

export default async function TeamsPage() {
  const [standings, currentSeason] = await Promise.all([
    getStandings(),
    getCurrentSeason()
  ])
  
  // Only show teams from current standings (current season)
  // Fetch team details for each team in standings
  const teamsWithStats = await Promise.all(
    standings.map(async (standing) => {
      const team = await getTeamById(standing.team_id)
      return {
        ...team,
        ...standing,
        standing: standing.standing
      }
    })
  )
  
  // Filter out any null teams and sort by standing
  const validTeams = teamsWithStats
    .filter((t): t is NonNullable<typeof t> => t !== null && t.team_id !== undefined)
    .sort((a, b) => a.standing - b.standing)
  
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="font-display text-2xl font-bold tracking-wider uppercase flex items-center gap-3">
          <span className="w-1 h-6 bg-primary rounded" />
          Teams
        </h1>
        <p className="text-sm text-muted-foreground mt-2 ml-4">
          NORAD Hockey League team profiles and statistics
        </p>
      </div>
      
      {/* Teams Grid */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {validTeams.map((team) => {
          const wins = team.wins ?? 0
          const losses = team.losses ?? 0
          const ties = team.ties ?? 0
          const goalsFor = team.goals_for ?? 0
          const goalsAgainst = team.goals_against ?? 0
          const differential = goalsFor - goalsAgainst
          
          return (
            <Link
              key={team.team_id}
              href={`/team/${(team.team_name || '').replace(/\s+/g, '_')}`}
              className="bg-card rounded-xl border border-border hover:border-primary/50 transition-all hover:shadow-lg group overflow-hidden"
            >
              {/* Team Header with Color Bar */}
              <div 
                className="h-2"
                style={{ backgroundColor: team.primary_color || team.team_color1 || '#3b82f6' }}
              />
              
              <div className="p-4">
                {/* Team Name */}
                <div className="flex items-center gap-3 mb-4">
                  <TeamLogo
                    src={team.team_logo || null}
                    name={team.team_name || ''}
                    abbrev={team.team_cd}
                    primaryColor={team.primary_color || team.team_color1}
                    secondaryColor={team.team_color2}
                    size="lg"
                  />
                  <div className="flex-1">
                    <div className="font-display text-lg font-semibold text-foreground group-hover:text-primary transition-colors">
                      {team.team_name}
                    </div>
                    {team.standing && (
                      <div className="flex items-center gap-2 mt-1">
                        <Trophy className="w-3 h-3 text-assist" />
                        <span className="text-xs font-mono text-muted-foreground">
                          #{team.standing} in standings
                        </span>
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Stats Grid */}
                <div className="grid grid-cols-2 gap-3 mb-4">
                  <div className="text-center p-2 bg-accent/30 rounded">
                    <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Record</div>
                    <div className="font-display font-semibold text-foreground">
                      {wins}-{losses}-{ties}
                    </div>
                    {team.games_played && (
                      <div className="text-xs font-mono text-muted-foreground mt-1">
                        {team.games_played} GP
                      </div>
                    )}
                  </div>
                  <div className="text-center p-2 bg-accent/30 rounded">
                    <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Win %</div>
                    <div className="font-mono font-semibold text-primary">
                      {team.games_played > 0 ? ((team.points || (wins * 2 + ties)) / (team.games_played * 2) * 100).toFixed(1) : '0.0'}%
                    </div>
                  </div>
                </div>
                
                {/* Goals Stats */}
                <div className="grid grid-cols-3 gap-2 mb-4">
                  <div className="text-center">
                    <div className="text-xs font-mono text-muted-foreground uppercase">GF</div>
                    <div className="font-mono font-semibold text-save">
                      {goalsFor}
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-xs font-mono text-muted-foreground uppercase">GA</div>
                    <div className="font-mono font-semibold text-goal">
                      {goalsAgainst}
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-xs font-mono text-muted-foreground uppercase">Diff</div>
                    <span className={cn(
                      'font-mono font-bold',
                      differential > 0 && 'text-save',
                      differential < 0 && 'text-goal',
                      differential === 0 && 'text-muted-foreground'
                    )}>
                      {differential > 0 ? '+' : ''}{differential}
                    </span>
                  </div>
                </div>
                
                {/* Points */}
                {team.points !== undefined && (
                  <div className="flex items-center justify-between pt-3 border-t border-border">
                    <span className="text-xs font-mono text-muted-foreground">Points</span>
                    <span className="font-mono font-bold text-lg text-primary">
                      {team.points}
                    </span>
                  </div>
                )}
              </div>
            </Link>
          )
        })}
      </div>
      
      {validTeams.length === 0 && (
        <div className="bg-card rounded-lg border border-border p-8 text-center">
          <p className="text-muted-foreground">No teams found for current season.</p>
        </div>
      )}
    </div>
  )
}
