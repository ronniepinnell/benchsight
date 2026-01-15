// src/app/(dashboard)/goalies/page.tsx
import Link from 'next/link'
import { getGoalieGAALeaders, getGoalieWinsLeaders } from '@/lib/supabase/queries/goalies'
import { getCurrentSeason, getAllSeasons } from '@/lib/supabase/queries/league'
import { createClient } from '@/lib/supabase/server'
import { Shield, Trophy, Target } from 'lucide-react'
import { cn } from '@/lib/utils'
import { ExportButton } from '@/components/export/ExportButton'
import { SeasonFilter } from '@/components/leaders/season-filter'

export const revalidate = 300

export const metadata = {
  title: 'Goalies | BenchSight',
  description: 'NORAD Hockey League goaltending leaders',
}

export default async function GoaliesPage({
  searchParams,
}: {
  searchParams: Promise<{ tab?: string; season?: string }>
}) {
  const params = await searchParams
  const activeTab = params.tab || 'gaa'
  const selectedSeason = params.season || null
  
  const supabase = await createClient()
  const currentSeason = await getCurrentSeason()
  const allSeasons = await getAllSeasons()
  const seasonId = selectedSeason || currentSeason || allSeasons[0] || null
  
  // Fetch goalie leaders with season filter
  const [gaaLeadersResult, winsLeadersResult, savePctResult] = await Promise.all([
    seasonId
      ? supabase
          .from('v_leaderboard_goalie_gaa')
          .select('*')
          .eq('season_id', seasonId)
          .order('season_rank', { ascending: true })
          .limit(15)
      : supabase
          .from('v_leaderboard_goalie_gaa')
          .select('*')
          .order('season_rank', { ascending: true })
          .limit(15),
    seasonId
      ? supabase
          .from('v_leaderboard_goalie_wins')
          .select('*')
          .eq('season_id', seasonId)
          .order('season_rank', { ascending: true })
          .limit(15)
      : supabase
          .from('v_leaderboard_goalie_wins')
          .select('*')
          .order('season_rank', { ascending: true })
          .limit(15),
    seasonId
      ? supabase
          .from('v_rankings_goalies_current')
          .select('*')
          .eq('season_id', seasonId)
          .order('save_pct', { ascending: false })
          .limit(15)
      : supabase
          .from('v_rankings_goalies_current')
          .select('*')
          .order('save_pct', { ascending: false })
          .limit(15),
  ])
  
  const gaaLeaders = gaaLeadersResult.data || []
  const winsLeaders = winsLeadersResult.data || []
  const savePctLeaders = savePctResult.data || []

  const tabs = [
    { id: 'gaa', label: 'GAA', icon: Shield, color: 'text-save' },
    { id: 'wins', label: 'Wins', icon: Trophy, color: 'text-assist' },
    { id: 'savepct', label: 'Save %', icon: Target, color: 'text-primary' },
    { id: 'all', label: 'All Stats', icon: Target, color: 'text-primary' },
  ]

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="font-display text-2xl font-bold tracking-wider uppercase flex items-center gap-3">
          <span className="w-1 h-6 bg-save rounded" />
          Goaltending Leaders
        </h1>
        <p className="text-sm text-muted-foreground mt-2 ml-4">
          Top goaltenders by season
        </p>
      </div>

      {/* Season Filter */}
      <SeasonFilter 
        seasons={allSeasons} 
        currentSeason={currentSeason} 
        selectedSeason={seasonId} 
      />

      {/* Tabs */}
      <div className="flex gap-2 border-b border-border pb-2">
        {tabs.map((tab) => {
          const Icon = tab.icon
          const isActive = activeTab === tab.id
          return (
            <Link
              key={tab.id}
              href={`/norad/goalies?tab=${tab.id}${seasonId && seasonId !== currentSeason ? `&season=${seasonId}` : ''}`}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-t-lg transition-all',
                isActive
                  ? 'bg-card border border-b-0 border-border -mb-[1px]'
                  : 'hover:bg-muted/50'
              )}
            >
              <Icon className={cn('w-4 h-4', isActive ? tab.color : 'text-muted-foreground')} />
              <span className={cn(
                'font-display text-sm',
                isActive ? 'text-foreground font-semibold' : 'text-muted-foreground'
              )}>
                {tab.label}
              </span>
            </Link>
          )
        })}
      </div>

      {/* Content based on tab */}
      {activeTab === 'gaa' && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border flex items-center justify-between">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Shield className="w-4 h-4 text-save" />
              Goals Against Average Leaders
            </h2>
            <ExportButton 
              data={gaaLeaders.map(g => ({
                Rank: g.season_rank || 0,
                Goalie: g.player_name,
                Team: g.team_name,
                GP: g.games_played,
                GAA: g.gaa?.toFixed(2) || '',
                'SV%': g.save_pct ? (g.save_pct * 100).toFixed(1) + '%' : '',
                Saves: g.saves,
              }))}
              filename="goalie_gaa_leaders"
            />
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border bg-accent/50">
                  <th className="px-4 py-3 text-center font-display text-xs text-muted-foreground w-16">Rank</th>
                  <th className="px-4 py-3 text-left font-display text-xs text-muted-foreground">Goalie</th>
                  <th className="px-4 py-3 text-left font-display text-xs text-muted-foreground">Team</th>
                  <th className="px-4 py-3 text-center font-display text-xs text-muted-foreground">GP</th>
                  <th className="px-4 py-3 text-center font-display text-xs text-save">GAA</th>
                  <th className="px-4 py-3 text-center font-display text-xs text-muted-foreground">SV%</th>
                  <th className="px-4 py-3 text-center font-display text-xs text-muted-foreground">Saves</th>
                </tr>
              </thead>
              <tbody>
                {gaaLeaders.map((goalie, index) => {
                  const rank = index + 1
                  const isTop3 = rank <= 3
                  return (
                    <tr key={goalie.player_id} className={cn(
                      'border-b border-border hover:bg-muted/50',
                      rank % 2 === 0 && 'bg-accent/30'
                    )}>
                      <td className="px-4 py-3 text-center">
                        <span className={cn(
                          'font-display font-bold',
                          isTop3 ? 'text-lg text-save' : 'text-muted-foreground'
                        )}>
                          {rank}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <Link href={`/norad/goalies/${goalie.player_id}`} className="font-display text-sm hover:text-primary">
                          {goalie.player_name}
                        </Link>
                      </td>
                      <td className="px-4 py-3 text-sm text-muted-foreground">{goalie.team_name}</td>
                      <td className="px-4 py-3 text-center font-mono text-sm text-muted-foreground">{goalie.games_played}</td>
                      <td className="px-4 py-3 text-center font-mono text-xl font-bold text-save">
                        {goalie.gaa?.toFixed(2) ?? '-'}
                      </td>
                      <td className="px-4 py-3 text-center font-mono text-sm">
                        {goalie.save_pct ? (goalie.save_pct * 100).toFixed(1) + '%' : '-'}
                      </td>
                      <td className="px-4 py-3 text-center font-mono text-sm text-muted-foreground">{goalie.saves}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'wins' && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border flex items-center justify-between">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Trophy className="w-4 h-4 text-assist" />
              Wins Leaders
            </h2>
            <ExportButton 
              data={winsLeaders.map(g => ({
                Rank: g.season_rank || 0,
                Goalie: g.player_name,
                Team: g.team_name,
                GP: g.games_played,
                W: g.wins,
                L: g.losses,
                'Win %': g.games_played > 0 ? ((g.wins / g.games_played) * 100).toFixed(1) + '%' : '',
              }))}
              filename="goalie_wins_leaders"
            />
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border bg-accent/50">
                  <th className="px-4 py-3 text-center font-display text-xs text-muted-foreground w-16">Rank</th>
                  <th className="px-4 py-3 text-left font-display text-xs text-muted-foreground">Goalie</th>
                  <th className="px-4 py-3 text-left font-display text-xs text-muted-foreground">Team</th>
                  <th className="px-4 py-3 text-center font-display text-xs text-muted-foreground">GP</th>
                  <th className="px-4 py-3 text-center font-display text-xs text-assist">W</th>
                  <th className="px-4 py-3 text-center font-display text-xs text-goal">L</th>
                  <th className="px-4 py-3 text-center font-display text-xs text-muted-foreground">WIN%</th>
                </tr>
              </thead>
              <tbody>
                {winsLeaders.map((goalie, index) => {
                  const rank = index + 1
                  const isTop3 = rank <= 3
                  const gp = goalie.games_played || 1
                  const wins = goalie.wins || 0
                  const winPct = ((wins / gp) * 100).toFixed(1)
                  return (
                    <tr key={goalie.player_id} className={cn(
                      'border-b border-border hover:bg-muted/50',
                      rank % 2 === 0 && 'bg-accent/30'
                    )}>
                      <td className="px-4 py-3 text-center">
                        <span className={cn(
                          'font-display font-bold',
                          isTop3 ? 'text-lg text-assist' : 'text-muted-foreground'
                        )}>
                          {rank}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <Link href={`/norad/goalies/${goalie.player_id}`} className="font-display text-sm hover:text-primary">
                          {goalie.player_name}
                        </Link>
                      </td>
                      <td className="px-4 py-3 text-sm text-muted-foreground">{goalie.team_name}</td>
                      <td className="px-4 py-3 text-center font-mono text-sm text-muted-foreground">{goalie.games_played}</td>
                      <td className="px-4 py-3 text-center font-mono text-xl font-bold text-assist">{goalie.wins}</td>
                      <td className="px-4 py-3 text-center font-mono text-sm text-goal">{goalie.losses}</td>
                      <td className="px-4 py-3 text-center font-mono text-sm">{winPct}%</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'savepct' && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border flex items-center justify-between">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Target className="w-4 h-4 text-primary" />
              Save Percentage Leaders
            </h2>
            <ExportButton 
              data={savePctLeaders.map((g: any) => ({
                Rank: savePctLeaders.indexOf(g) + 1,
                Goalie: g.player_name,
                Team: g.team_name,
                GP: g.games_played,
                'SV%': g.save_pct ? (g.save_pct * 100).toFixed(1) + '%' : '',
                GAA: g.gaa?.toFixed(2) || '',
                Saves: g.saves,
              }))}
              filename="goalie_save_pct_leaders"
            />
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border bg-accent/50">
                  <th className="px-4 py-3 text-center font-display text-xs text-muted-foreground w-16">Rank</th>
                  <th className="px-4 py-3 text-left font-display text-xs text-muted-foreground">Goalie</th>
                  <th className="px-4 py-3 text-left font-display text-xs text-muted-foreground">Team</th>
                  <th className="px-4 py-3 text-center font-display text-xs text-muted-foreground">GP</th>
                  <th className="px-4 py-3 text-center font-display text-xs text-primary">SV%</th>
                  <th className="px-4 py-3 text-center font-display text-xs text-save">GAA</th>
                  <th className="px-4 py-3 text-center font-display text-xs text-muted-foreground">Saves</th>
                </tr>
              </thead>
              <tbody>
                {savePctLeaders.map((goalie: any, index: number) => {
                  const rank = index + 1
                  const isTop3 = rank <= 3
                  return (
                    <tr key={goalie.player_id} className={cn(
                      'border-b border-border hover:bg-muted/50',
                      rank % 2 === 0 && 'bg-accent/30'
                    )}>
                      <td className="px-4 py-3 text-center">
                        <span className={cn(
                          'font-display font-bold',
                          isTop3 ? 'text-lg text-primary' : 'text-muted-foreground'
                        )}>
                          {rank}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <Link href={`/norad/goalies/${goalie.player_id}`} className="font-display text-sm hover:text-primary">
                          {goalie.player_name}
                        </Link>
                      </td>
                      <td className="px-4 py-3 text-sm text-muted-foreground">{goalie.team_name}</td>
                      <td className="px-4 py-3 text-center font-mono text-sm text-muted-foreground">{goalie.games_played}</td>
                      <td className="px-4 py-3 text-center font-mono text-xl font-bold text-primary">
                        {goalie.save_pct ? (goalie.save_pct * 100).toFixed(1) + '%' : '-'}
                      </td>
                      <td className="px-4 py-3 text-center font-mono text-sm text-save">
                        {goalie.gaa?.toFixed(2) ?? '-'}
                      </td>
                      <td className="px-4 py-3 text-center font-mono text-sm text-muted-foreground">{goalie.saves}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'all' && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Target className="w-4 h-4 text-primary" />
              Complete Goalie Statistics
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-accent/50">
                  <th className="px-3 py-3 text-left font-display text-xs text-muted-foreground">Goalie</th>
                  <th className="px-3 py-3 text-left font-display text-xs text-muted-foreground">Team</th>
                  <th className="px-2 py-3 text-center font-display text-xs text-muted-foreground">GP</th>
                  <th className="px-2 py-3 text-center font-display text-xs text-assist">W</th>
                  <th className="px-2 py-3 text-center font-display text-xs text-goal">L</th>
                  <th className="px-2 py-3 text-center font-display text-xs text-save">GAA</th>
                  <th className="px-2 py-3 text-center font-display text-xs text-primary">SV%</th>
                  <th className="px-2 py-3 text-center font-display text-xs text-muted-foreground">SA</th>
                  <th className="px-2 py-3 text-center font-display text-xs text-muted-foreground">SV</th>
                  <th className="px-2 py-3 text-center font-display text-xs text-muted-foreground">GA</th>
                </tr>
              </thead>
              <tbody>
                {gaaLeaders.map((goalie, index) => {
                  const winsData = winsLeaders.find(g => g.player_id === goalie.player_id)
                  return (
                    <tr key={goalie.player_id} className={cn(
                      'border-b border-border hover:bg-muted/50',
                      index % 2 === 0 && 'bg-accent/30'
                    )}>
                      <td className="px-3 py-3">
                        <Link href={`/norad/goalies/${goalie.player_id}`} className="font-display hover:text-primary">
                          {goalie.player_name}
                        </Link>
                      </td>
                      <td className="px-3 py-3 text-muted-foreground">{goalie.team_name}</td>
                      <td className="px-2 py-3 text-center font-mono text-muted-foreground">{goalie.games_played}</td>
                      <td className="px-2 py-3 text-center font-mono font-semibold text-assist">{winsData?.wins ?? '-'}</td>
                      <td className="px-2 py-3 text-center font-mono text-goal">{winsData?.losses ?? '-'}</td>
                      <td className="px-2 py-3 text-center font-mono font-semibold text-save">{goalie.gaa?.toFixed(2) ?? '-'}</td>
                      <td className="px-2 py-3 text-center font-mono font-semibold text-primary">
                        {goalie.save_pct ? (goalie.save_pct * 100).toFixed(1) + '%' : '-'}
                      </td>
                      <td className="px-2 py-3 text-center font-mono text-muted-foreground">{goalie.shots_against}</td>
                      <td className="px-2 py-3 text-center font-mono text-muted-foreground">{goalie.saves}</td>
                      <td className="px-2 py-3 text-center font-mono text-muted-foreground">{goalie.goals_against}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
