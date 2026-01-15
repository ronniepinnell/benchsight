// src/app/(dashboard)/leaders/page.tsx
import Link from 'next/link'
import { createClient } from '@/lib/supabase/server'
import { getCurrentSeason, getAllSeasons } from '@/lib/supabase/queries/league'
import { getPlayers } from '@/lib/supabase/queries/players'
import { Award } from 'lucide-react'
import { SortableLeadersTable } from '@/components/leaders/sortable-leaders-table'
import { SortableGoaliesTable } from '@/components/leaders/sortable-goalies-table'
import { SeasonFilter } from '@/components/leaders/season-filter'

export const revalidate = 300

export const metadata = {
  title: 'Leaders | BenchSight',
  description: 'NORAD Hockey League scoring leaders',
}

export default async function LeadersPage({
  searchParams,
}: {
  searchParams: Promise<{ tab?: string; season?: string }>
}) {
  const params = await searchParams
  const activeTab = params.tab || 'skaters'
  const selectedSeason = params.season || null
  
  const supabase = await createClient()
  const currentSeason = await getCurrentSeason()
  const allSeasons = await getAllSeasons()
  const seasonId = selectedSeason || currentSeason || allSeasons[0] || null
  
  // Fetch all leaderboard data with season filter and player data for photos
  const [pointsLeaders, goalieWins, goalieGAA, players] = await Promise.all([
    seasonId
      ? supabase.from('v_leaderboard_points').select('*').eq('season_id', seasonId).order('season_rank', { ascending: true }).limit(100)
      : supabase.from('v_leaderboard_points').select('*').order('season_rank', { ascending: true }).limit(100),
    seasonId
      ? supabase.from('v_leaderboard_goalie_wins').select('*').eq('season_id', seasonId).order('wins', { ascending: false }).limit(100)
      : supabase.from('v_leaderboard_goalie_wins').select('*').order('wins', { ascending: false }).limit(100),
    seasonId
      ? supabase.from('v_leaderboard_goalie_gaa').select('*').eq('season_id', seasonId).order('gaa', { ascending: true }).limit(100)
      : supabase.from('v_leaderboard_goalie_gaa').select('*').order('gaa', { ascending: true }).limit(100),
    getPlayers(),
  ])

  const pointsData = pointsLeaders.data || []
  const goaliesWinsData = goalieWins.data || []
  const goaliesGAAData = goalieGAA.data || []
  const playersList = players || []
  const playersMap = new Map(playersList.map(p => [String(p.player_id), p]))

  // Merge goalie wins and GAA data
  const gaaMap = new Map(goaliesGAAData.map(g => [String(g.player_id), g]))
  const goaliesData = goaliesWinsData.map(goalie => ({
    ...goalie,
    gaa: (goalie as any).gaa || gaaMap.get(String(goalie.player_id))?.gaa,
    save_pct: gaaMap.get(String(goalie.player_id))?.save_pct,
    shots_against: gaaMap.get(String(goalie.player_id))?.shots_against,
  }))

  const tabs = [
    { id: 'skaters', label: 'Skaters' },
    { id: 'goalies', label: 'Goalies' },
  ]

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="font-display text-2xl font-bold tracking-wider uppercase flex items-center gap-3">
          <span className="w-1 h-6 bg-assist rounded" />
          League Leaders
        </h1>
        <p className="text-sm text-muted-foreground mt-2 ml-4">
          Top performers by season - sort by any column
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
          const isActive = activeTab === tab.id
          return (
            <Link
              key={tab.id}
              href={`/norad/leaders?tab=${tab.id}${seasonId && seasonId !== currentSeason ? `&season=${seasonId}` : ''}`}
              className={`flex items-center gap-2 px-4 py-2 rounded-t-lg transition-all ${
                isActive
                  ? 'bg-card border border-b-0 border-border -mb-[1px] text-foreground font-semibold'
                  : 'hover:bg-muted/50 text-muted-foreground'
              }`}
            >
              <span className="font-display text-sm">
                {tab.label}
              </span>
            </Link>
          )
        })}
      </div>

      {/* Leaders Table */}
      {activeTab === 'goalies' ? (
        <SortableGoaliesTable 
          goalies={goaliesData} 
          playersMap={playersMap}
          isCurrentSeason={seasonId === currentSeason}
        />
      ) : (
        <SortableLeadersTable 
          leaders={pointsData} 
          playersMap={playersMap}
          isCurrentSeason={seasonId === currentSeason}
        />
      )}
    </div>
  )
}
