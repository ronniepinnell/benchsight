// src/app/(dashboard)/leaders/page.tsx
import Link from 'next/link'
import { createClient } from '@/lib/supabase/server'
import { getCurrentSeason, getAllSeasons } from '@/lib/supabase/queries/league'
import { getPlayers } from '@/lib/supabase/queries/players'
import { getTeams } from '@/lib/supabase/queries/teams'
import { Award, Trophy, Target, TrendingUp } from 'lucide-react'
import { SortableLeadersTable } from '@/components/leaders/sortable-leaders-table'
import { SortableGoaliesTable } from '@/components/leaders/sortable-goalies-table'
import { SeasonFilter } from '@/components/leaders/season-filter'
import { PlayerPhoto } from '@/components/players/player-photo'
import { TeamLogo } from '@/components/teams/team-logo'
import { cn } from '@/lib/utils'

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
  const [pointsLeaders, goalieWins, goalieGAA, players, teams] = await Promise.all([
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
    getTeams(),
  ])

  const pointsData = pointsLeaders.data || []
  const goaliesWinsData = goalieWins.data || []
  const goaliesGAAData = goalieGAA.data || []
  const playersList = players || []
  const playersMap = new Map(playersList.map(p => [String(p.player_id), p]))
  const teamsMap = new Map(teams.map(t => [String(t.team_id), t]))

  // Get top 3 for featured cards
  const top3Skaters = pointsData.slice(0, 3)
  const top3Goalies = goaliesWinsData.slice(0, 3)

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

      {/* Top 3 Featured Cards */}
      {activeTab === 'skaters' && top3Skaters.length > 0 && (
        <div className="grid md:grid-cols-3 gap-4">
          {top3Skaters.map((player, index) => {
            const playerData = playersMap.get(String(player.player_id))
            const teamData = teamsMap.get(String(player.team_id))
            const medals = ['text-yellow-500', 'text-gray-400', 'text-amber-600']
            const bgColors = ['bg-yellow-500/10 border-yellow-500/30', 'bg-gray-400/10 border-gray-400/30', 'bg-amber-600/10 border-amber-600/30']

            return (
              <Link
                key={player.player_id}
                href={`/norad/players/${player.player_id}`}
                className={cn(
                  'bg-card rounded-xl border-2 p-4 hover:shadow-lg transition-all group',
                  bgColors[index]
                )}
              >
                <div className="flex items-center gap-3 mb-3">
                  <div className={cn('font-display text-3xl font-bold', medals[index])}>
                    #{index + 1}
                  </div>
                  <Trophy className={cn('w-6 h-6', medals[index])} />
                </div>

                <div className="flex items-center gap-4 mb-4">
                  <PlayerPhoto
                    src={playerData?.player_image || null}
                    name={player.player_name || ''}
                    size="lg"
                  />
                  <div className="flex-1">
                    <div className="font-display text-lg font-bold group-hover:text-primary transition-colors">
                      {player.player_full_name || player.player_name}
                    </div>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      {teamData && (
                        <TeamLogo
                          src={teamData.team_logo || null}
                          name={player.team_name || ''}
                          abbrev={teamData.team_cd}
                          primaryColor={teamData.primary_color || teamData.team_color1}
                          secondaryColor={teamData.team_color2}
                          size="xs"
                        />
                      )}
                      <span>{player.team_name}</span>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-4 gap-2 text-center">
                  <div>
                    <div className="font-mono text-xs text-muted-foreground uppercase">GP</div>
                    <div className="font-mono text-lg">{player.games_played}</div>
                  </div>
                  <div>
                    <div className="font-mono text-xs text-goal uppercase">G</div>
                    <div className="font-mono text-lg text-goal font-bold">{player.goals}</div>
                  </div>
                  <div>
                    <div className="font-mono text-xs text-assist uppercase">A</div>
                    <div className="font-mono text-lg text-assist">{player.assists}</div>
                  </div>
                  <div>
                    <div className="font-mono text-xs text-primary uppercase">PTS</div>
                    <div className="font-mono text-xl text-primary font-bold">{player.points}</div>
                  </div>
                </div>
              </Link>
            )
          })}
        </div>
      )}

      {activeTab === 'goalies' && top3Goalies.length > 0 && (
        <div className="grid md:grid-cols-3 gap-4">
          {top3Goalies.map((goalie, index) => {
            const playerData = playersMap.get(String(goalie.player_id))
            const teamData = teamsMap.get(String(goalie.team_id))
            const medals = ['text-yellow-500', 'text-gray-400', 'text-amber-600']
            const bgColors = ['bg-yellow-500/10 border-yellow-500/30', 'bg-gray-400/10 border-gray-400/30', 'bg-amber-600/10 border-amber-600/30']
            const gaaData = goaliesGAAData.find(g => String(g.player_id) === String(goalie.player_id))

            return (
              <Link
                key={goalie.player_id}
                href={`/norad/goalies/${goalie.player_id}`}
                className={cn(
                  'bg-card rounded-xl border-2 p-4 hover:shadow-lg transition-all group',
                  bgColors[index]
                )}
              >
                <div className="flex items-center gap-3 mb-3">
                  <div className={cn('font-display text-3xl font-bold', medals[index])}>
                    #{index + 1}
                  </div>
                  <Trophy className={cn('w-6 h-6', medals[index])} />
                </div>

                <div className="flex items-center gap-4 mb-4">
                  <PlayerPhoto
                    src={playerData?.player_image || null}
                    name={goalie.player_name || ''}
                    size="lg"
                  />
                  <div className="flex-1">
                    <div className="font-display text-lg font-bold group-hover:text-primary transition-colors">
                      {goalie.player_full_name || goalie.player_name}
                    </div>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      {teamData && (
                        <TeamLogo
                          src={teamData.team_logo || null}
                          name={goalie.team_name || ''}
                          abbrev={teamData.team_cd}
                          primaryColor={teamData.primary_color || teamData.team_color1}
                          secondaryColor={teamData.team_color2}
                          size="xs"
                        />
                      )}
                      <span>{goalie.team_name}</span>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-2 text-center">
                  <div>
                    <div className="font-mono text-xs text-muted-foreground uppercase">GP</div>
                    <div className="font-mono text-lg">{goalie.games_played}</div>
                  </div>
                  <div>
                    <div className="font-mono text-xs text-save uppercase">Wins</div>
                    <div className="font-mono text-xl text-save font-bold">{goalie.wins}</div>
                  </div>
                  <div>
                    <div className="font-mono text-xs text-primary uppercase">GAA</div>
                    <div className="font-mono text-lg text-primary">{gaaData?.gaa?.toFixed(2) || '-'}</div>
                  </div>
                </div>
              </Link>
            )
          })}
        </div>
      )}

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
