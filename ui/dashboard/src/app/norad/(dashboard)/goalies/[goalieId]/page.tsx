// src/app/(dashboard)/goalies/[goalieId]/page.tsx
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getPlayerById } from '@/lib/supabase/queries/players'
import { getGoalieCareerSummary, getGoalieGameLog, getGoalieCurrentStats } from '@/lib/supabase/queries/goalies'
import { getTeamById } from '@/lib/supabase/queries/teams'
import { createClient } from '@/lib/supabase/server'
import { ArrowLeft, Shield, TrendingUp, Target, Activity, BarChart3, Clock, Award } from 'lucide-react'
import { cn } from '@/lib/utils'
import { PlayerPhoto } from '@/components/players/player-photo'
import { TeamLogo } from '@/components/teams/team-logo'
import { StatCard, StatRow } from '@/components/players/stat-card'
import { TrendLineChart } from '@/components/charts/trend-line-chart'
import { GoalieProfileTabs } from '@/components/goalies/goalie-profile-tabs'

export const revalidate = 300

export async function generateMetadata({ params }: { params: Promise<{ goalieId: string }> }) {
  const { goalieId } = await params
  const player = await getPlayerById(goalieId).catch(() => null)
  return {
    title: `${player?.player_name || 'Goalie'} | BenchSight`,
    description: `Goalie statistics and performance for ${player?.player_name || 'goalie'}`,
  }
}

export default async function GoalieProfilePage({ 
  params,
  searchParams
}: { 
  params: Promise<{ goalieId: string }>
  searchParams: Promise<{ season?: string }>
}) {
  const { goalieId } = await params
  const { season: selectedSeason } = await searchParams
  const supabase = await createClient()
  
  // Fetch goalie data
  const [player, career, currentStats, gameLog] = await Promise.all([
    getPlayerById(goalieId).catch(() => null),
    getGoalieCareerSummary(goalieId).catch(() => null),
    getGoalieCurrentStats(goalieId).catch(() => null),
    getGoalieGameLog(goalieId, 50).catch(() => [])
  ])
  
  if (!player) {
    notFound()
  }
  
  // Get team info
  const team = player.team_id ? await getTeamById(player.team_id).catch(() => null) : null
  
  // Get season stats
  const { data: seasonStats } = await supabase
    .from('fact_goalie_season_stats_basic')
    .select('*')
    .eq('player_id', goalieId)
    .order('season', { ascending: false })
    .limit(10)
  
  // Get game stats for trends
  const { data: gameStats } = await supabase
    .from('fact_goalie_game_stats')
    .select('*')
    .eq('player_id', goalieId)
    .order('game_id', { ascending: false })
    .limit(50)
  
  // Calculate trends
  const trendData = (gameStats || []).reverse().map((game, index) => ({
    gameNumber: index + 1,
    savePct: game.save_pct ? game.save_pct * 100 : 0,
    gaa: game.gaa || 0,
    saves: game.saves || 0,
    goalsAgainst: game.goals_against || 0,
    shotsAgainst: game.shots_against || 0,
  }))
  
  // Calculate rolling averages
  const calculateRollingAverage = (data: any[], key: string, window: number) => {
    return data.map((_, index) => {
      const start = Math.max(0, index - window + 1)
      const windowData = data.slice(start, index + 1)
      const sum = windowData.reduce((acc, item) => acc + (Number(item[key]) || 0), 0)
      return windowData.length > 0 ? (sum / windowData.length) : 0
    })
  }
  
  const savePct5Game = calculateRollingAverage(trendData, 'savePct', 5)
  const savePct10Game = calculateRollingAverage(trendData, 'savePct', 10)
  const gaa5Game = calculateRollingAverage(trendData, 'gaa', 5)
  const gaa10Game = calculateRollingAverage(trendData, 'gaa', 10)
  
  const trendDataWithRolling = trendData.map((game, index) => ({
    ...game,
    savePct5Game: savePct5Game[index],
    savePct10Game: savePct10Game[index],
    gaa5Game: gaa5Game[index],
    gaa10Game: gaa10Game[index],
  }))
  
  // Aggregate advanced stats
  const advancedStats = (gameStats || []).reduce((acc, game) => {
    acc.games += 1
    acc.totalSaves += Number(game.saves || 0)
    acc.totalGoalsAgainst += Number(game.goals_against || 0)
    acc.totalShotsAgainst += Number(game.shots_against || 0)
    acc.totalGSAx += Number(game.goalie_gsaa || game.goals_saved_above_avg || 0)
    acc.totalWAR += Number(game.goalie_war || 0)
    acc.totalGAR += Number(game.goalie_gar_total || 0)
    acc.hdSaves += Number(game.hd_saves || 0)
    acc.hdShotsAgainst += Number(game.hd_shots_against || 0)
    acc.qualityStarts += Number(game.quality_start || 0)
    return acc
  }, {
    games: 0,
    totalSaves: 0,
    totalGoalsAgainst: 0,
    totalShotsAgainst: 0,
    totalGSAx: 0,
    totalWAR: 0,
    totalGAR: 0,
    hdSaves: 0,
    hdShotsAgainst: 0,
    qualityStarts: 0,
  })
  
  const avgSavePct = advancedStats.totalShotsAgainst > 0
    ? (advancedStats.totalSaves / advancedStats.totalShotsAgainst) * 100
    : 0
  const avgGAA = advancedStats.games > 0
    ? (advancedStats.totalGoalsAgainst / advancedStats.games) * 60 / 20 // Assuming 20 min periods
    : 0
  const formatDecimal = (val: number | null | undefined, decimals: number = 2) => {
    if (val === null || val === undefined) return '-'
    return Number(val).toFixed(decimals)
  }
  
  const formatPercent = (val: number | null | undefined) => {
    if (val === null || val === undefined) return '-'
    return Number(val).toFixed(1) + '%'
  }
  
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
          <div className="flex items-center gap-4">
            <PlayerPhoto
              src={player.player_image || null}
              name={player.player_name || ''}
              size="xl"
            />
            <div>
              <h1 className="font-display text-3xl font-bold text-foreground">
                {player.player_full_name || player.player_name}
              </h1>
              <div className="flex items-center gap-4 mt-3">
                {team && (
                  <Link 
                    href={`/norad/team/${(team.team_name || '').replace(/\s+/g, '_')}`}
                    className="flex items-center gap-2 text-sm text-foreground hover:text-primary transition-colors"
                  >
                    <TeamLogo
                      src={team.team_logo || null}
                      name={team.team_name || ''}
                      abbrev={team.team_cd}
                      primaryColor={team.primary_color || team.team_color1}
                      secondaryColor={team.team_color2}
                      size="sm"
                    />
                    <span>{team.team_name}</span>
                  </Link>
                )}
                <span className="text-xs font-mono bg-accent px-2 py-1 rounded uppercase">
                  Goalie
                </span>
              </div>
            </div>
          </div>
        </div>
        <Link 
          href={`/norad/goalies/compare?g1=${goalieId}`}
          className="text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          Compare Goalies →
        </Link>
      </div>
      
      {/* Goalie Profile Tabs */}
      <GoalieProfileTabs
        goalieId={goalieId}
        seasonId={selectedSeason || ''}
        gameLog={gameLog}
        currentStats={currentStats}
        career={career}
        gameStats={gameStats || []}
        trendData={trendDataWithRolling}
        advancedStats={advancedStats}
      />
    </div>
  )
}
