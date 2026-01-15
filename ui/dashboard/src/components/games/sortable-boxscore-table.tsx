'use client'

import { useState, useMemo } from 'react'
import Link from 'next/link'
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react'
import { cn } from '@/lib/utils'
import { PlayerPhoto } from '@/components/players/player-photo'

type SortField = 'player' | 'jersey' | 'rating' | 'goals' | 'assists' | 'points' | 'shots' | 'plusMinus' | 'pim' | 'toi' | 'shifts' | 'cfPct' | 'passes' | 'giveaways' | 'takeaways'
type SortDirection = 'asc' | 'desc'

interface BoxscorePlayer {
  player_id: string
  player_game_id?: string
  player_full_name?: string
  player_name?: string
  player_game_number?: number
  jersey_number?: number
  goals?: number
  assist?: number
  points?: number
  pim?: number
  pim_total?: number
  is_sub?: boolean | number | string
  sub?: boolean | number | string
  [key: string]: any // For advanced stats
}

interface SortableBoxscoreTableProps {
  players: BoxscorePlayer[]
  playersMap: Map<string, any>
  advStatsMap?: Map<string, any>
  teamColor?: string
  hasTracking: boolean
  hasShifts: boolean
  hasEvents: boolean
  getPlayerLink: (playerId: string) => string
  showSubBadge?: boolean
}

export function SortableBoxscoreTable({
  players,
  playersMap,
  advStatsMap,
  teamColor,
  hasTracking,
  hasShifts,
  hasEvents,
  getPlayerLink,
  showSubBadge = true,
}: SortableBoxscoreTableProps) {
  const [sortField, setSortField] = useState<SortField>('points')
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc')

  const sortedPlayers = useMemo(() => {
    const sorted = [...players]

    sorted.sort((a, b) => {
      let aValue: any
      let bValue: any

      switch (sortField) {
        case 'player':
          aValue = (a.player_full_name || a.player_name || '').toLowerCase()
          bValue = (b.player_full_name || b.player_name || '').toLowerCase()
          break
        case 'jersey':
          aValue = a.player_game_number ?? a.jersey_number ?? 999
          bValue = b.player_game_number ?? b.jersey_number ?? 999
          break
        case 'rating':
          const aPlayerInfo = playersMap.get(String(a.player_id))
          const bPlayerInfo = playersMap.get(String(b.player_id))
          aValue = aPlayerInfo?.current_skill_rating ? Number(aPlayerInfo.current_skill_rating) : 0
          bValue = bPlayerInfo?.current_skill_rating ? Number(bPlayerInfo.current_skill_rating) : 0
          break
        case 'goals':
          aValue = Number(a.goals ?? 0)
          bValue = Number(b.goals ?? 0)
          break
        case 'assists':
          aValue = Number(a.assist ?? 0)
          bValue = Number(b.assist ?? 0)
          break
        case 'points':
          aValue = Number(a.goals ?? 0) + Number(a.assist ?? 0)
          bValue = Number(b.goals ?? 0) + Number(b.assist ?? 0)
          break
        case 'shots':
          aValue = Number(a.shots ?? a.sog ?? 0)
          bValue = Number(b.shots ?? b.sog ?? 0)
          break
        case 'plusMinus':
          aValue = Number(a.plus_minus_total ?? a.plus_minus ?? 0)
          bValue = Number(b.plus_minus_total ?? b.plus_minus ?? 0)
          break
        case 'pim':
          aValue = Number(a.pim ?? a.pim_total ?? 0)
          bValue = Number(b.pim ?? b.pim_total ?? 0)
          break
        case 'toi':
          aValue = Number(a.toi_seconds ?? 0)
          bValue = Number(b.toi_seconds ?? 0)
          break
        case 'shifts':
          aValue = Number(a.shifts ?? 0)
          bValue = Number(b.shifts ?? 0)
          break
        case 'cfPct':
          aValue = typeof a.cf_pct === 'number' ? a.cf_pct : parseFloat(String(a.cf_pct || 0))
          bValue = typeof b.cf_pct === 'number' ? b.cf_pct : parseFloat(String(b.cf_pct || 0))
          break
        case 'passes':
          aValue = Number(a.pass_attempts ?? a.pass_att ?? a.pass_completed ?? a.pass_comp ?? 0)
          bValue = Number(b.pass_attempts ?? b.pass_att ?? b.pass_completed ?? b.pass_comp ?? 0)
          break
        case 'giveaways':
          aValue = Number(a.giveaways ?? a.give ?? 0)
          bValue = Number(b.giveaways ?? b.give ?? 0)
          break
        case 'takeaways':
          aValue = Number(a.takeaways ?? a.take ?? 0)
          bValue = Number(b.takeaways ?? b.take ?? 0)
          break
        default:
          aValue = Number(a.goals ?? 0) + Number(a.assist ?? 0)
          bValue = Number(b.goals ?? 0) + Number(b.assist ?? 0)
      }

      if (typeof aValue === 'string') {
        return sortDirection === 'asc'
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue)
      }

      return sortDirection === 'asc' ? aValue - bValue : bValue - aValue
    })

    return sorted
  }, [players, sortField, sortDirection, playersMap])

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('desc')
    }
  }

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) {
      return <ArrowUpDown className="w-3 h-3 ml-1 opacity-50" />
    }
    return sortDirection === 'asc' 
      ? <ArrowUp className="w-3 h-3 ml-1" />
      : <ArrowDown className="w-3 h-3 ml-1" />
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border bg-accent/50">
            <th 
              className="px-3 py-2 text-left font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
              onClick={() => handleSort('player')}
            >
              <div className="flex items-center gap-1">
                Player
                <SortIcon field="player" />
              </div>
            </th>
            <th 
              className="px-2 py-2 text-center font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
              onClick={() => handleSort('jersey')}
            >
              <div className="flex items-center justify-center gap-1">
                #
                <SortIcon field="jersey" />
              </div>
            </th>
            <th 
              className="px-2 py-2 text-center font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
              onClick={() => handleSort('rating')}
            >
              <div className="flex items-center justify-center gap-1">
                Rating
                <SortIcon field="rating" />
              </div>
            </th>
            <th 
              className="px-2 py-2 text-center font-display text-xs text-goal cursor-pointer hover:bg-muted/50 transition-colors"
              onClick={() => handleSort('goals')}
            >
              <div className="flex items-center justify-center gap-1">
                G
                <SortIcon field="goals" />
              </div>
            </th>
            <th 
              className="px-2 py-2 text-center font-display text-xs text-assist cursor-pointer hover:bg-muted/50 transition-colors"
              onClick={() => handleSort('assists')}
            >
              <div className="flex items-center justify-center gap-1">
                A
                <SortIcon field="assists" />
              </div>
            </th>
            <th 
              className="px-2 py-2 text-center font-display text-xs text-primary cursor-pointer hover:bg-muted/50 transition-colors"
              onClick={() => handleSort('points')}
            >
              <div className="flex items-center justify-center gap-1">
                P
                <SortIcon field="points" />
              </div>
            </th>
            {hasTracking && (
              <>
                <th 
                  className="px-2 py-2 text-center font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
                  onClick={() => handleSort('shots')}
                >
                  <div className="flex items-center justify-center gap-1">
                    S
                    <SortIcon field="shots" />
                  </div>
                </th>
                <th 
                  className="px-2 py-2 text-center font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
                  onClick={() => handleSort('plusMinus')}
                >
                  <div className="flex items-center justify-center gap-1">
                    +/-
                    <SortIcon field="plusMinus" />
                  </div>
                </th>
              </>
            )}
            <th 
              className="px-2 py-2 text-center font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
              onClick={() => handleSort('pim')}
            >
              <div className="flex items-center justify-center gap-1">
                PIM
                <SortIcon field="pim" />
              </div>
            </th>
            {hasTracking && (
              <>
                {hasShifts && (
                  <>
                    <th 
                      className="px-2 py-2 text-center font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
                      onClick={() => handleSort('toi')}
                    >
                      <div className="flex items-center justify-center gap-1">
                        TOI
                        <SortIcon field="toi" />
                      </div>
                    </th>
                    <th 
                      className="px-2 py-2 text-center font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
                      onClick={() => handleSort('shifts')}
                    >
                      <div className="flex items-center justify-center gap-1">
                        Shifts
                        <SortIcon field="shifts" />
                      </div>
                    </th>
                  </>
                )}
                <th 
                  className="px-2 py-2 text-center font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
                  onClick={() => handleSort('cfPct')}
                >
                  <div className="flex items-center justify-center gap-1">
                    CF%
                    <SortIcon field="cfPct" />
                  </div>
                </th>
                {hasEvents && (
                  <>
                    <th 
                      className="px-2 py-2 text-center font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
                      onClick={() => handleSort('passes')}
                    >
                      <div className="flex items-center justify-center gap-1">
                        P
                        <SortIcon field="passes" />
                      </div>
                    </th>
                    <th 
                      className="px-2 py-2 text-center font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
                      onClick={() => handleSort('giveaways')}
                    >
                      <div className="flex items-center justify-center gap-1">
                        GvA
                        <SortIcon field="giveaways" />
                      </div>
                    </th>
                    <th 
                      className="px-2 py-2 text-center font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
                      onClick={() => handleSort('takeaways')}
                    >
                      <div className="flex items-center justify-center gap-1">
                        TkA
                        <SortIcon field="takeaways" />
                      </div>
                    </th>
                  </>
                )}
              </>
            )}
          </tr>
        </thead>
        <tbody>
          {sortedPlayers.map((player) => {
            const playerInfo = playersMap.get(String(player.player_id))
            const goals = Number(player.goals ?? 0)
            const assists = Number(player.assist ?? 0)
            const points = goals + assists
            const playerLink = getPlayerLink(player.player_id)
            
            const subValue = player.sub ?? player.is_sub
            const isSub = showSubBadge && (subValue === true || subValue === 1 || 
                         String(subValue).toLowerCase() === 'true' || 
                         String(subValue) === '1' ||
                         String(subValue).toLowerCase() === 'yes')
            
            // Get advanced stats if available
            const advStats = advStatsMap?.get(String(player.player_id)) || (player as any).advStats || {}
            
            return (
              <tr key={player.player_game_id || player.player_id} className="border-b border-border hover:bg-muted/50">
                <td className="px-3 py-2">
                  <Link 
                    href={playerLink} 
                    className="flex items-center gap-2 text-foreground hover:text-primary transition-colors"
                  >
                    <PlayerPhoto
                      src={playerInfo?.player_image || null}
                      name={player.player_full_name || player.player_name || ''}
                      primaryColor={teamColor}
                      size="sm"
                    />
                    <div className="flex items-center gap-1.5">
                      <span>{player.player_full_name || player.player_name}</span>
                      {isSub && (
                        <span className="text-xs font-mono bg-muted px-1.5 py-0.5 rounded uppercase text-muted-foreground">
                          SUB
                        </span>
                      )}
                    </div>
                  </Link>
                </td>
                <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                  {player.player_game_number ?? playerInfo?.jersey_number ?? '-'}
                </td>
                <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                  {playerInfo?.current_skill_rating ? Math.round(Number(playerInfo.current_skill_rating)) : '-'}
                </td>
                <td className="px-2 py-2 text-center font-mono text-goal">{goals}</td>
                <td className="px-2 py-2 text-center font-mono text-assist">{assists}</td>
                <td className="px-2 py-2 text-center font-mono font-semibold">{points}</td>
                {hasTracking && (
                  <>
                    <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                      {advStats?.shots ?? advStats?.sog ?? '-'}
                    </td>
                    <td className={cn(
                      'px-2 py-2 text-center font-mono',
                      (advStats?.plus_minus_total ?? advStats?.plus_minus ?? 0) > 0 && 'text-save',
                      (advStats?.plus_minus_total ?? advStats?.plus_minus ?? 0) < 0 && 'text-goal'
                    )}>
                      {(advStats?.plus_minus_total ?? advStats?.plus_minus ?? 0) > 0 ? '+' : ''}
                      {(advStats?.plus_minus_total ?? advStats?.plus_minus ?? 0) || 0}
                    </td>
                  </>
                )}
                <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                  {player.pim ?? player.pim_total ?? 0}
                </td>
                {hasTracking && (
                  <>
                    {hasShifts && (
                      <>
                        <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                          {advStats?.toi_seconds 
                            ? (() => {
                                const mins = Math.floor((advStats.toi_seconds || 0) / 60)
                                const secs = (advStats.toi_seconds || 0) % 60
                                return `${mins}:${secs.toString().padStart(2, '0')}`
                              })()
                            : '-'}
                        </td>
                        <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                          {advStats?.shifts ?? '-'}
                        </td>
                      </>
                    )}
                    <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                      {advStats?.cf_pct 
                        ? (typeof advStats.cf_pct === 'number' 
                            ? Number(advStats.cf_pct).toFixed(1) + '%' 
                            : String(advStats.cf_pct))
                        : '-'}
                    </td>
                    {hasEvents && (
                      <>
                        <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                          {advStats?.pass_attempts ?? advStats?.pass_att ?? advStats?.pass_completed ?? advStats?.pass_comp ?? '-'}
                        </td>
                        <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                          {advStats?.giveaways ?? advStats?.give ?? '-'}
                        </td>
                        <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                          {advStats?.takeaways ?? advStats?.take ?? '-'}
                        </td>
                      </>
                    )}
                  </>
                )}
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
