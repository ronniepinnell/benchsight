// src/components/teams/standings-table.tsx
import { TeamLogo } from './team-logo'
import { cn, formatDiff, formatRecord } from '@/lib/utils'
import type { Standing } from '@/lib/supabase/queries/teams'

interface StandingsTableProps {
  standings: Standing[]
}

export function StandingsTable({ standings }: StandingsTableProps) {
  return (
    <div className="bg-card rounded-xl border border-border overflow-hidden shadow-lg">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-accent border-b-2 border-border">
              <th className="px-4 py-3 text-left font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Pos
              </th>
              <th className="px-4 py-3 text-left font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Team
              </th>
              <th className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                GP
              </th>
              <th className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                W
              </th>
              <th className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                L
              </th>
              <th className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                T
              </th>
              <th className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                PTS
              </th>
              <th className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                GF
              </th>
              <th className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                GA
              </th>
              <th className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                DIFF
              </th>
              <th className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                L10
              </th>
              <th className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                STRK
              </th>
            </tr>
          </thead>
          <tbody>
            {standings.map((team, index) => {
              const pos = index + 1
              const isPlayoff = pos <= 4
              const isElimination = pos >= 9
              
              return (
                <tr
                  key={team.team_id}
                  className={cn(
                    'border-b border-border transition-colors hover:bg-muted/50',
                    index % 2 === 0 && 'bg-accent/30'
                  )}
                  style={{
                    borderLeftWidth: '3px',
                    borderLeftColor: team.primary_color ?? '#1e3a5f',
                  }}
                >
                  {/* Position */}
                  <td className="px-4 py-3">
                    <span
                      className={cn(
                        'font-display font-bold text-lg',
                        isPlayoff && 'text-save',
                        isElimination && 'text-goal',
                        !isPlayoff && !isElimination && 'text-primary'
                      )}
                    >
                      {pos}
                    </span>
                  </td>
                  
                  {/* Team */}
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <TeamLogo
                        src={team.team_logo_url}
                        name={team.team_name}
                        abbrev={team.team_abbrev}
                        primaryColor={team.primary_color}
                        secondaryColor={team.secondary_color}
                        size="sm"
                      />
                      <span className="font-display text-sm text-foreground">
                        {team.team_name}
                      </span>
                    </div>
                  </td>
                  
                  {/* GP */}
                  <td className="px-4 py-3 text-center font-mono text-sm text-muted-foreground">
                    {team.games_played}
                  </td>
                  
                  {/* W */}
                  <td className="px-4 py-3 text-center font-mono text-sm text-save">
                    {team.wins}
                  </td>
                  
                  {/* L */}
                  <td className="px-4 py-3 text-center font-mono text-sm text-goal">
                    {team.losses}
                  </td>
                  
                  {/* T */}
                  <td className="px-4 py-3 text-center font-mono text-sm text-muted-foreground">
                    {team.ties}
                  </td>
                  
                  {/* PTS */}
                  <td className="px-4 py-3 text-center font-mono text-sm font-semibold text-foreground">
                    {team.points}
                  </td>
                  
                  {/* GF */}
                  <td className="px-4 py-3 text-center font-mono text-sm text-muted-foreground">
                    {team.goals_for}
                  </td>
                  
                  {/* GA */}
                  <td className="px-4 py-3 text-center font-mono text-sm text-muted-foreground">
                    {team.goals_against}
                  </td>
                  
                  {/* DIFF */}
                  <td className="px-4 py-3 text-center font-mono text-sm">
                    <span
                      className={cn(
                        team.goal_diff > 0 && 'text-save',
                        team.goal_diff < 0 && 'text-goal',
                        team.goal_diff === 0 && 'text-muted-foreground'
                      )}
                    >
                      {formatDiff(team.goal_diff)}
                    </span>
                  </td>
                  
                  {/* L10 */}
                  <td className="px-4 py-3 text-center font-mono text-sm text-muted-foreground">
                    {team.last_10 ?? '-'}
                  </td>
                  
                  {/* Streak */}
                  <td className="px-4 py-3 text-center font-mono text-sm">
                    <span
                      className={cn(
                        team.streak?.startsWith('W') && 'text-save',
                        team.streak?.startsWith('L') && 'text-goal',
                        !team.streak && 'text-muted-foreground'
                      )}
                    >
                      {team.streak ?? '-'}
                    </span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      
      {/* Legend */}
      <div className="flex gap-6 px-4 py-3 bg-accent/50 border-t border-border">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-save/20 border border-save" />
          <span className="text-xs font-mono text-muted-foreground">
            PLAYOFF POSITION (Top 4)
          </span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-goal/20 border border-goal" />
          <span className="text-xs font-mono text-muted-foreground">
            ELIMINATION ZONE (Bottom 2)
          </span>
        </div>
      </div>
    </div>
  )
}
