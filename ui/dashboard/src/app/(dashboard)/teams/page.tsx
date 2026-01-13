// src/app/(dashboard)/teams/page.tsx
import Link from 'next/link'
import { getTeams, getStandings } from '@/lib/supabase/queries/teams'
import { Users, Trophy, Target, Shield } from 'lucide-react'
import { cn } from '@/lib/utils'

export const revalidate = 300

export const metadata = {
  title: 'Teams | BenchSight',
  description: 'NORAD Hockey League teams',
}

export default async function TeamsPage() {
  const [teams, standings] = await Promise.all([
    getTeams(),
    getStandings()
  ])
  
  // Merge standings data with teams
  const teamsWithStats = teams.map(team => {
    const standing = standings.find(s => s.team_id === team.team_id)
    return { ...team, ...standing }
  })
  
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
        {teamsWithStats.map((team) => {
          const wins = team.wins ?? 0
          const losses = team.losses ?? 0
          const ties = team.ties ?? 0
          const goalsFor = team.goals_for ?? 0
          const goalsAgainst = team.goals_against ?? 0
          const differential = goalsFor - goalsAgainst
          
          return (
            <Link
              key={team.team_id}
              href={`/teams/${team.team_id}`}
              className="bg-card rounded-xl border border-border hover:border-primary/50 transition-all hover:shadow-lg group overflow-hidden"
            >
              {/* Team Header with Color Bar */}
              <div 
                className="h-2"
                style={{ backgroundColor: team.team_color ?? '#3b82f6' }}
              />
              
              <div className="p-4">
                {/* Team Name */}
                <div className="flex items-center gap-3 mb-4">
                  <div 
                    className="w-12 h-12 rounded-lg flex items-center justify-center text-white font-display font-bold text-lg"
                    style={{ backgroundColor: team.team_color ?? '#3b82f6' }}
                  >
                    {team.team_name?.substring(0, 2).toUpperCase() ?? 'TM'}
                  </div>
                  <div>
                    <div className="font-display text-lg font-semibold text-foreground group-hover:text-primary transition-colors">
                      {team.team_name}
                    </div>
                    {team.standing_rank && (
                      <div className="text-xs font-mono text-muted-foreground">
                        #{team.standing_rank} in standings
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Stats Grid */}
                <div className="grid grid-cols-3 gap-3 mb-4">
                  <div className="text-center">
                    <div className="text-xs font-mono text-muted-foreground uppercase">Record</div>
                    <div className="font-display font-semibold text-foreground">
                      {wins}-{losses}-{ties}
                    </div>
                  </div>
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
                </div>
                
                {/* Differential */}
                <div className="flex items-center justify-between pt-3 border-t border-border">
                  <span className="text-xs font-mono text-muted-foreground">Goal Diff</span>
                  <span className={cn(
                    'font-mono font-bold text-lg',
                    differential > 0 && 'text-save',
                    differential < 0 && 'text-goal',
                    differential === 0 && 'text-muted-foreground'
                  )}>
                    {differential > 0 ? '+' : ''}{differential}
                  </span>
                </div>
              </div>
            </Link>
          )
        })}
      </div>
      
      {teams.length === 0 && (
        <div className="bg-card rounded-lg border border-border p-8 text-center">
          <p className="text-muted-foreground">No teams found.</p>
        </div>
      )}
    </div>
  )
}
