// src/app/(dashboard)/teams/compare/page.tsx
import Link from 'next/link'
import { createClient } from '@/lib/supabase/server'
import { getTeamById } from '@/lib/supabase/queries/teams'
import { ArrowLeft, Users, TrendingUp, Target, BarChart3, Trophy } from 'lucide-react'
import { cn } from '@/lib/utils'
import { TeamLogo } from '@/components/teams/team-logo'
import { StatCard } from '@/components/players/stat-card'

export const revalidate = 300

export const metadata = {
  title: 'Compare Teams | BenchSight',
  description: 'Compare team statistics side-by-side',
}

export default async function CompareTeamsPage({
  searchParams,
}: {
  searchParams: Promise<{ t1?: string; t2?: string; t3?: string; t4?: string }>
}) {
  const params = await searchParams
  const teamIds = [params.t1, params.t2, params.t3, params.t4].filter(Boolean) as string[]
  
  if (teamIds.length === 0) {
    return (
      <div className="space-y-6">
        <Link 
          href="/norad/teams"
          className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Teams
        </Link>
        <div className="bg-card rounded-xl border border-border p-8 text-center">
          <h1 className="font-display text-2xl font-bold mb-4">Compare Teams</h1>
          <p className="text-muted-foreground mb-6">
            Select teams to compare by visiting their profile pages
          </p>
          <Link
            href="/norad/teams"
            className="inline-block bg-primary text-primary-foreground px-6 py-3 rounded-lg hover:bg-primary/90 transition-colors"
          >
            Browse Teams
          </Link>
        </div>
      </div>
    )
  }
  
  const supabase = await createClient()
  
  // Fetch all team data
  const teamsData = await Promise.all(
    teamIds.map(async (teamId) => {
      const team = await getTeamById(teamId).catch(() => null)
      
      // Get season stats
      const { data: seasonStats } = await supabase
        .from('fact_team_season_stats_basic')
        .select('*')
        .eq('team_id', teamId)
        .order('season', { ascending: false })
        .limit(1)
        .maybeSingle()
      
      return {
        teamId,
        team,
        seasonStats: seasonStats || null,
      }
    })
  )
  
  // Prepare comparison data
  const comparisonStats = teamsData.map(({ team, seasonStats }) => ({
    name: team?.team_name || 'Unknown',
    teamId: team?.team_id || '',
    logo: team?.team_logo,
    wins: seasonStats?.wins || 0,
    losses: seasonStats?.losses || 0,
    points: seasonStats?.points || 0,
    goalsFor: seasonStats?.goals_for || 0,
    goalsAgainst: seasonStats?.goals_against || 0,
    goalDiff: (seasonStats?.goals_for || 0) - (seasonStats?.goals_against || 0),
    gamesPlayed: seasonStats?.games_played || 0,
    winPct: seasonStats?.games_played > 0 
      ? ((seasonStats?.wins || 0) / seasonStats.games_played) * 100 
      : 0,
  }))
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link 
            href="/norad/teams"
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="font-display text-2xl font-bold tracking-wider uppercase flex items-center gap-3">
              <span className="w-1 h-6 bg-primary rounded" />
              Compare Teams
            </h1>
            <p className="text-sm text-muted-foreground mt-2 ml-4">
              Side-by-side team comparison
            </p>
          </div>
        </div>
      </div>
      
      {/* Team Headers */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
        {comparisonStats.map((team, index) => (
          <Link
            key={index}
            href={`/team/${(team.name || '').replace(/\s+/g, '_')}`}
            className="bg-card rounded-xl border border-border p-6 hover:border-primary/50 transition-colors"
          >
            <div className="flex flex-col items-center text-center">
              <TeamLogo
                src={team.logo || null}
                name={team.name}
                size="lg"
              />
              <div className="mt-4 font-display font-semibold text-foreground">
                {team.name}
              </div>
            </div>
          </Link>
        ))}
      </div>
      
      {/* Comparison Table */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="px-4 py-3 bg-accent border-b border-border">
          <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
            <BarChart3 className="w-4 h-4" />
            Stat Comparison
          </h2>
        </div>
        <div className="p-6">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-2 font-mono text-xs text-muted-foreground uppercase">Stat</th>
                  {comparisonStats.map((_, index) => (
                    <th key={index} className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">
                      Team {index + 1}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-border/50">
                  <td className="py-3 font-semibold">Games Played</td>
                  {comparisonStats.map((team, index) => (
                    <td key={index} className="text-right py-3 font-mono">{team.gamesPlayed}</td>
                  ))}
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 font-semibold">Wins</td>
                  {comparisonStats.map((team, index) => (
                    <td key={index} className="text-right py-3 font-mono text-save">{team.wins}</td>
                  ))}
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 font-semibold">Losses</td>
                  {comparisonStats.map((team, index) => (
                    <td key={index} className="text-right py-3 font-mono text-goal">{team.losses}</td>
                  ))}
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 font-semibold">Points</td>
                  {comparisonStats.map((team, index) => (
                    <td key={index} className="text-right py-3 font-mono font-semibold text-primary">{team.points}</td>
                  ))}
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 font-semibold">Win %</td>
                  {comparisonStats.map((team, index) => (
                    <td key={index} className="text-right py-3 font-mono">{team.winPct.toFixed(1)}%</td>
                  ))}
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 font-semibold">Goals For</td>
                  {comparisonStats.map((team, index) => (
                    <td key={index} className="text-right py-3 font-mono text-goal">{team.goalsFor}</td>
                  ))}
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 font-semibold">Goals Against</td>
                  {comparisonStats.map((team, index) => (
                    <td key={index} className="text-right py-3 font-mono text-goal">{team.goalsAgainst}</td>
                  ))}
                </tr>
                <tr>
                  <td className="py-3 font-semibold">Goal Differential</td>
                  {comparisonStats.map((team, index) => (
                    <td key={index} className={cn(
                      "text-right py-3 font-mono font-semibold",
                      team.goalDiff > 0 ? "text-save" : team.goalDiff < 0 ? "text-goal" : ""
                    )}>
                      {team.goalDiff > 0 ? '+' : ''}{team.goalDiff}
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
