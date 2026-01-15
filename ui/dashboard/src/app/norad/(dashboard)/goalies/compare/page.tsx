// src/app/(dashboard)/goalies/compare/page.tsx
import Link from 'next/link'
import { createClient } from '@/lib/supabase/server'
import { getPlayerById } from '@/lib/supabase/queries/players'
import { getGoalieCurrentStats, getGoalieCareerSummary } from '@/lib/supabase/queries/goalies'
import { getTeamById } from '@/lib/supabase/queries/teams'
import { ArrowLeft, Shield, TrendingUp, Target, BarChart3, Award } from 'lucide-react'
import { cn } from '@/lib/utils'
import { PlayerPhoto } from '@/components/players/player-photo'
import { TeamLogo } from '@/components/teams/team-logo'
import { StatCard } from '@/components/players/stat-card'
import { MultiPlayerRadarChart } from '@/components/charts/radar-chart'

export const revalidate = 300

export const metadata = {
  title: 'Compare Goalies | BenchSight',
  description: 'Compare goalie statistics side-by-side',
}

export default async function CompareGoaliesPage({
  searchParams,
}: {
  searchParams: Promise<{ g1?: string; g2?: string; g3?: string; g4?: string }>
}) {
  const params = await searchParams
  const goalieIds = [params.g1, params.g2, params.g3, params.g4].filter(Boolean) as string[]
  
  if (goalieIds.length === 0) {
    return (
      <div className="space-y-6">
        <Link 
          href="/norad/goalies"
          className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Goalies
        </Link>
        <div className="bg-card rounded-xl border border-border p-8 text-center">
          <h1 className="font-display text-2xl font-bold mb-4">Compare Goalies</h1>
          <p className="text-muted-foreground mb-6">
            Select goalies to compare by visiting their profile pages and clicking "Compare Goalies"
          </p>
          <Link
            href="/norad/goalies"
            className="inline-block bg-primary text-primary-foreground px-6 py-3 rounded-lg hover:bg-primary/90 transition-colors"
          >
            Browse Goalies
          </Link>
        </div>
      </div>
    )
  }
  
  const supabase = await createClient()
  
  // Fetch all goalie data
  const goaliesData = await Promise.all(
    goalieIds.map(async (goalieId) => {
      const [player, currentStats, career] = await Promise.all([
        getPlayerById(goalieId).catch(() => null),
        getGoalieCurrentStats(goalieId).catch(() => null),
        getGoalieCareerSummary(goalieId).catch(() => null),
      ])
      
      const team = player?.team_id ? await getTeamById(player.team_id).catch(() => null) : null
      
      return {
        playerId: goalieId,
        player,
        team,
        currentStats,
        career,
      }
    })
  )
  
  const formatDecimal = (val: number | null | undefined, decimals: number = 2) => {
    if (val === null || val === undefined) return '-'
    return Number(val).toFixed(decimals)
  }
  
  const formatPercent = (val: number | null | undefined) => {
    if (val === null || val === undefined) return '-'
    return Number(val).toFixed(1) + '%'
  }
  
  // Prepare comparison data
  const comparisonStats = goaliesData.map(({ player, currentStats, career, team }) => ({
    name: player?.player_name || player?.player_full_name || 'Unknown',
    team: team?.team_name || 'Unknown',
    teamLogo: team?.team_logo,
    photo: player?.player_image,
    games: currentStats?.games_played || career?.total_games || 0,
    wins: currentStats?.wins || career?.total_wins || 0,
    losses: currentStats?.losses || career?.total_losses || 0,
    savePct: currentStats?.save_pct ? currentStats.save_pct * 100 : (career?.career_save_pct ? career.career_save_pct * 100 : 0),
    gaa: currentStats?.gaa || career?.career_gaa || 0,
    shutouts: currentStats?.shutouts || career?.total_shutouts || 0,
    saves: currentStats?.saves || 0,
    goalsAgainst: currentStats?.goals_against || 0,
    shotsAgainst: currentStats?.shots_against || 0,
  }))
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link 
            href="/norad/goalies"
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="font-display text-2xl font-bold tracking-wider uppercase flex items-center gap-3">
              <span className="w-1 h-6 bg-save rounded" />
              Compare Goalies
            </h1>
            <p className="text-sm text-muted-foreground mt-2 ml-4">
              Side-by-side goalie comparison
            </p>
          </div>
        </div>
      </div>
      
      {/* Goalie Headers */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
        {comparisonStats.map((goalie, index) => (
          <div key={index} className="bg-card rounded-xl border border-border p-4">
            <Link 
              href={`/norad/goalies/${goalieIds[index]}`}
              className="flex flex-col items-center text-center hover:text-primary transition-colors"
            >
              <PlayerPhoto
                src={goalie.photo || null}
                name={goalie.name}
                size="lg"
              />
              <div className="mt-3">
                <div className="font-display font-semibold text-foreground">
                  {goalie.name}
                </div>
                {goalie.teamLogo && (
                  <TeamLogo
                    src={goalie.teamLogo}
                    name={goalie.team}
                    size="xs"
                    showGradient={false}
                  />
                )}
              </div>
            </Link>
          </div>
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
                      Goalie {index + 1}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-border/50">
                  <td className="py-3 font-semibold">Games Played</td>
                  {comparisonStats.map((goalie, index) => (
                    <td key={index} className="text-right py-3 font-mono">{goalie.games}</td>
                  ))}
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 font-semibold">Wins</td>
                  {comparisonStats.map((goalie, index) => (
                    <td key={index} className="text-right py-3 font-mono text-save">{goalie.wins}</td>
                  ))}
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 font-semibold">Losses</td>
                  {comparisonStats.map((goalie, index) => (
                    <td key={index} className="text-right py-3 font-mono text-goal">{goalie.losses}</td>
                  ))}
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 font-semibold">Save %</td>
                  {comparisonStats.map((goalie, index) => (
                    <td key={index} className="text-right py-3 font-mono font-semibold text-primary">
                      {formatPercent(goalie.savePct)}
                    </td>
                  ))}
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 font-semibold">GAA</td>
                  {comparisonStats.map((goalie, index) => (
                    <td key={index} className="text-right py-3 font-mono">{formatDecimal(goalie.gaa)}</td>
                  ))}
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 font-semibold">Shutouts</td>
                  {comparisonStats.map((goalie, index) => (
                    <td key={index} className="text-right py-3 font-mono text-assist">{goalie.shutouts}</td>
                  ))}
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 font-semibold">Total Saves</td>
                  {comparisonStats.map((goalie, index) => (
                    <td key={index} className="text-right py-3 font-mono">{goalie.saves}</td>
                  ))}
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-3 font-semibold">Goals Against</td>
                  {comparisonStats.map((goalie, index) => (
                    <td key={index} className="text-right py-3 font-mono">{goalie.goalsAgainst}</td>
                  ))}
                </tr>
                <tr>
                  <td className="py-3 font-semibold">Shots Against</td>
                  {comparisonStats.map((goalie, index) => (
                    <td key={index} className="text-right py-3 font-mono">{goalie.shotsAgainst}</td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      
      {/* Radar Chart Comparison */}
      {comparisonStats.length >= 2 && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Target className="w-4 h-4" />
              Performance Comparison
            </h2>
          </div>
          <div className="p-6">
            <MultiPlayerRadarChart
              data={comparisonStats.map((goalie) => ({
                player: goalie.name,
                stats: [
                  { category: 'Save %', value: goalie.savePct },
                  { category: 'Win Rate', value: (goalie.wins / Math.max(goalie.games, 1)) * 100 },
                  { category: 'Shutout Rate', value: (goalie.shutouts / Math.max(goalie.games, 1)) * 100 },
                  { category: 'Games', value: Math.min(goalie.games / 20 * 100, 100) },
                ]
              }))}
            />
          </div>
        </div>
      )}
    </div>
  )
}
