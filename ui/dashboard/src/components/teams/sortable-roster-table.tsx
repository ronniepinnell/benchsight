'use client'

import { useState, useMemo } from 'react'
import Link from 'next/link'
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react'
import { cn } from '@/lib/utils'
import { PlayerPhoto } from '@/components/players/player-photo'

type SortField = 'player' | 'gp' | 'goals' | 'assists' | 'points' | 'pointsPerGame' | 'plusMinus' | 'cfPct' | 'toiPerGame' | 'pim'
type SortDirection = 'asc' | 'desc'

interface RosterPlayer {
  player_id: string
  player_name: string
  games_played: number
  goals: number
  assists: number
  points: number
  points_per_game?: number
  plus_minus?: number
  cf_pct?: number
  toi_per_game?: number
  pim?: number
  pim_total?: number
  jersey_number?: number | string
  current_skill_rating?: number | string
  player_primary_position?: string
}

interface SortableRosterTableProps {
  players: RosterPlayer[]
  playersMap: Map<string, any>
  teamColor?: string
  hasAdvancedAnalytics: boolean
  title?: string
}

export function SortableRosterTable({ 
  players, 
  playersMap, 
  teamColor,
  hasAdvancedAnalytics,
  title 
}: SortableRosterTableProps) {
  const [sortField, setSortField] = useState<SortField>('points')
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc')

  // Separate players into forwards and defense
  // Use player_primary_position from dim_player (NOT position from fact_gameroster)
  const { forwards, defense } = useMemo(() => {
    const fwds: RosterPlayer[] = []
    const defs: RosterPlayer[] = []
    
    players.forEach(player => {
      // ONLY use player_primary_position from dim_player - this is the source of truth
      const pos = String(player.player_primary_position || '').trim()
      const posUpper = pos.toUpperCase()
      
      // Skip goalies - they're shown separately
      if (posUpper.includes('GOALIE') || posUpper === 'G' || posUpper.includes('GOALTENDER')) {
        return
      }
      
      // Defense positions: "Defense", "D", "LD", "RD", "DEF"
      // Must be exact match or very specific to avoid false positives
      const isDefense = posUpper === 'DEFENSE' || 
                       posUpper === 'D' || 
                       posUpper === 'LD' || 
                       posUpper === 'RD' || 
                       posUpper === 'DEF'
      
      if (isDefense) {
        defs.push(player)
      } else if (pos && pos !== '') {
        // Only add to forwards if we have a position and it's not defense/goalie
        fwds.push(player)
      }
      // If no position at all, don't add to either list
    })
    
    return { forwards: fwds, defense: defs }
  }, [players])

  const sortedPlayers = useMemo(() => {
    const sorted = [...players]

    sorted.sort((a, b) => {
      let aValue: any
      let bValue: any

      switch (sortField) {
        case 'player':
          aValue = a.player_name?.toLowerCase() || ''
          bValue = b.player_name?.toLowerCase() || ''
          break
        case 'gp':
          aValue = a.games_played
          bValue = b.games_played
          break
        case 'goals':
          aValue = a.goals
          bValue = b.goals
          break
        case 'assists':
          aValue = a.assists
          bValue = b.assists
          break
        case 'points':
          aValue = a.points
          bValue = b.points
          break
        case 'pointsPerGame':
          aValue = a.points_per_game || 0
          bValue = b.points_per_game || 0
          break
        case 'plusMinus':
          aValue = a.plus_minus || 0
          bValue = b.plus_minus || 0
          break
        case 'cfPct':
          aValue = typeof a.cf_pct === 'number' ? a.cf_pct : parseFloat(String(a.cf_pct || 0))
          bValue = typeof b.cf_pct === 'number' ? b.cf_pct : parseFloat(String(b.cf_pct || 0))
          break
        case 'toiPerGame':
          aValue = typeof a.toi_per_game === 'number' ? a.toi_per_game : parseFloat(String(a.toi_per_game || 0))
          bValue = typeof b.toi_per_game === 'number' ? b.toi_per_game : parseFloat(String(b.toi_per_game || 0))
          break
        case 'pim':
          aValue = a.pim ?? a.pim_total ?? 0
          bValue = b.pim ?? b.pim_total ?? 0
          break
        default:
          aValue = a.points
          bValue = b.points
      }

      if (typeof aValue === 'string') {
        return sortDirection === 'asc'
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue)
      }

      return sortDirection === 'asc' ? aValue - bValue : bValue - aValue
    })

    return sorted
  }, [players, sortField, sortDirection])

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

  const renderTable = (playerList: RosterPlayer[], sectionTitle: string) => {
    const sorted = [...playerList]
    sorted.sort((a, b) => {
      let aValue: any
      let bValue: any

      switch (sortField) {
        case 'player':
          aValue = a.player_name?.toLowerCase() || ''
          bValue = b.player_name?.toLowerCase() || ''
          break
        case 'gp':
          aValue = a.games_played
          bValue = b.games_played
          break
        case 'goals':
          aValue = a.goals
          bValue = b.goals
          break
        case 'assists':
          aValue = a.assists
          bValue = b.assists
          break
        case 'points':
          aValue = a.points
          bValue = b.points
          break
        case 'pointsPerGame':
          aValue = a.points_per_game || 0
          bValue = b.points_per_game || 0
          break
        case 'plusMinus':
          aValue = a.plus_minus || 0
          bValue = b.plus_minus || 0
          break
        case 'cfPct':
          aValue = typeof a.cf_pct === 'number' ? a.cf_pct : parseFloat(String(a.cf_pct || 0))
          bValue = typeof b.cf_pct === 'number' ? b.cf_pct : parseFloat(String(b.cf_pct || 0))
          break
        case 'toiPerGame':
          aValue = typeof a.toi_per_game === 'number' ? a.toi_per_game : parseFloat(String(a.toi_per_game || 0))
          bValue = typeof b.toi_per_game === 'number' ? b.toi_per_game : parseFloat(String(b.toi_per_game || 0))
          break
        case 'pim':
          aValue = a.pim ?? a.pim_total ?? 0
          bValue = b.pim ?? b.pim_total ?? 0
          break
        default:
          aValue = a.points
          bValue = b.points
      }

      if (typeof aValue === 'string') {
        return sortDirection === 'asc'
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue)
      }

      return sortDirection === 'asc' ? aValue - bValue : bValue - aValue
    })

    return (
      <div className="overflow-x-auto">
        {sectionTitle && (
          <div className="px-4 py-2 bg-muted/30 border-b border-border">
            <h3 className="font-display text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              {sectionTitle} ({sorted.length})
            </h3>
          </div>
        )}
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
              <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">#</th>
              <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">Rating</th>
            <th 
              className="px-2 py-2 text-center font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
              onClick={() => handleSort('gp')}
            >
              <div className="flex items-center justify-center gap-1">
                GP
                <SortIcon field="gp" />
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
            {hasAdvancedAnalytics && (
              <>
                <th 
                  className="px-2 py-2 text-center font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
                  onClick={() => handleSort('pointsPerGame')}
                >
                  <div className="flex items-center justify-center gap-1">
                    P/G
                    <SortIcon field="pointsPerGame" />
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
                <th 
                  className="px-2 py-2 text-center font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
                  onClick={() => handleSort('cfPct')}
                >
                  <div className="flex items-center justify-center gap-1">
                    CF%
                    <SortIcon field="cfPct" />
                  </div>
                </th>
                <th 
                  className="px-2 py-2 text-center font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
                  onClick={() => handleSort('toiPerGame')}
                >
                  <div className="flex items-center justify-center gap-1">
                    TOI/G
                    <SortIcon field="toiPerGame" />
                  </div>
                </th>
              </>
            )}
            {!hasAdvancedAnalytics && (
              <th 
                className="px-2 py-2 text-center font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('pim')}
              >
                <div className="flex items-center justify-center gap-1">
                  PIM
                  <SortIcon field="pim" />
                </div>
              </th>
            )}
          </tr>
        </thead>
        <tbody>
          {sorted.map((player) => {
            const playerInfo = playersMap.get(String(player.player_id))
            return (
              <tr key={player.player_id} className="border-b border-border hover:bg-muted/50">
                <td className="px-3 py-2">
                  <Link 
                    href={`/norad/players/${player.player_id}`}
                    className="flex items-center gap-2 text-foreground hover:text-primary transition-colors"
                  >
                    <PlayerPhoto
                      src={playerInfo?.player_image || null}
                      name={player.player_name || ''}
                      primaryColor={teamColor}
                      size="sm"
                    />
                    <span>{player.player_name}</span>
                  </Link>
                </td>
                <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                  {player.jersey_number ?? playerInfo?.jersey_number ?? '-'}
                </td>
                <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                  {player.current_skill_rating ?? playerInfo?.current_skill_rating 
                    ? Math.round(Number(player.current_skill_rating ?? playerInfo?.current_skill_rating)) 
                    : '-'}
                </td>
                <td className="px-2 py-2 text-center font-mono text-muted-foreground">{player.games_played}</td>
                <td className="px-2 py-2 text-center font-mono text-goal font-semibold">{player.goals}</td>
                <td className="px-2 py-2 text-center font-mono text-assist">{player.assists}</td>
                <td className="px-2 py-2 text-center font-mono text-primary font-semibold">{player.points}</td>
                {hasAdvancedAnalytics && (
                  <>
                    <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                      {player.points_per_game?.toFixed(2) ?? '-'}
                    </td>
                    <td className={cn(
                      'px-2 py-2 text-center font-mono text-xs',
                      (player.plus_minus ?? 0) > 0 && 'text-save',
                      (player.plus_minus ?? 0) < 0 && 'text-goal'
                    )}>
                      {(player.plus_minus ?? 0) > 0 ? '+' : ''}{player.plus_minus ?? 0}
                    </td>
                    <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                      {player.cf_pct ? (typeof player.cf_pct === 'number' ? player.cf_pct.toFixed(1) : parseFloat(String(player.cf_pct)).toFixed(1)) + '%' : '-'}
                    </td>
                    <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                      {player.toi_per_game ? (typeof player.toi_per_game === 'number' ? player.toi_per_game.toFixed(1) : parseFloat(String(player.toi_per_game)).toFixed(1)) : '-'}
                    </td>
                  </>
                )}
                {!hasAdvancedAnalytics && (
                  <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                    {player.pim ?? player.pim_total ?? 0}
                  </td>
                )}
              </tr>
            )
          })}
          
          {/* Position Totals Row */}
          {sorted.length > 0 && (() => {
            const playersWithRatings = sorted.filter(p => {
              const rating = p.current_skill_rating ?? playersMap.get(String(p.player_id))?.current_skill_rating
              return rating != null && rating !== '' && Number(rating) > 0
            })
            const avgRating = playersWithRatings.length > 0
              ? playersWithRatings.reduce((sum, p) => {
                  const rating = p.current_skill_rating ?? playersMap.get(String(p.player_id))?.current_skill_rating
                  return sum + Number(rating || 0)
                }, 0) / playersWithRatings.length
              : null
            
            const totalGP = sorted.reduce((sum, p) => sum + (Number(p.games_played) || 0), 0)
            const totalGoals = sorted.reduce((sum, p) => sum + (Number(p.goals) || 0), 0)
            const totalAssists = sorted.reduce((sum, p) => sum + (Number(p.assists) || 0), 0)
            const totalPoints = sorted.reduce((sum, p) => sum + (Number(p.points) || 0), 0)
            const totalPlusMinus = sorted.reduce((sum, p) => sum + (Number(p.plus_minus) || 0), 0)
            const totalPIM = sorted.reduce((sum, p) => sum + (Number(p.pim ?? p.pim_total) || 0), 0)
            
            return (
              <tr className="border-t-2 border-border bg-muted/30 font-bold">
                <td className="px-3 py-2 font-display">
                  {sectionTitle} Totals
                </td>
                <td className="px-2 py-2 text-center"></td>
                <td className="px-2 py-2 text-center font-mono text-sm text-muted-foreground">
                  {avgRating != null ? Number(avgRating).toFixed(1) : '-'}
                </td>
                <td className="px-2 py-2 text-center font-mono text-muted-foreground font-semibold">
                  {totalGP}
                </td>
                <td className="px-2 py-2 text-center font-mono text-goal font-semibold">
                  {totalGoals}
                </td>
                <td className="px-2 py-2 text-center font-mono text-assist font-semibold">
                  {totalAssists}
                </td>
                <td className="px-2 py-2 text-center font-mono text-primary font-semibold">
                  {totalPoints}
                </td>
                {hasAdvancedAnalytics && (
                  <>
                    <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                      {totalGP > 0 ? (totalPoints / totalGP).toFixed(2) : '-'}
                    </td>
                    <td className={cn(
                      'px-2 py-2 text-center font-mono text-xs font-semibold',
                      totalPlusMinus > 0 && 'text-save',
                      totalPlusMinus < 0 && 'text-goal'
                    )}>
                      {totalPlusMinus > 0 ? '+' : ''}{totalPlusMinus}
                    </td>
                    <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">-</td>
                    <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">-</td>
                  </>
                )}
                {!hasAdvancedAnalytics && (
                  <td className="px-2 py-2 text-center font-mono text-muted-foreground font-semibold">
                    {totalPIM}
                  </td>
                )}
              </tr>
            )
          })()}
        </tbody>
      </table>
      </div>
    )
  }

  // Calculate overall totals for all skaters
  const allSkaters = [...forwards, ...defense]
  const overallTotals = useMemo(() => {
    if (allSkaters.length === 0) return null
    
    const playersWithRatings = allSkaters.filter(p => {
      const rating = p.current_skill_rating ?? playersMap.get(String(p.player_id))?.current_skill_rating
      return rating != null && rating !== '' && Number(rating) > 0
    })
    const avgRating = playersWithRatings.length > 0
      ? playersWithRatings.reduce((sum, p) => {
          const rating = p.current_skill_rating ?? playersMap.get(String(p.player_id))?.current_skill_rating
          return sum + Number(rating || 0)
        }, 0) / playersWithRatings.length
      : null
    
    return {
      avgRating,
      totalGP: allSkaters.reduce((sum, p) => sum + (Number(p.games_played) || 0), 0),
      totalGoals: allSkaters.reduce((sum, p) => sum + (Number(p.goals) || 0), 0),
      totalAssists: allSkaters.reduce((sum, p) => sum + (Number(p.assists) || 0), 0),
      totalPoints: allSkaters.reduce((sum, p) => sum + (Number(p.points) || 0), 0),
      totalPlusMinus: allSkaters.reduce((sum, p) => sum + (Number(p.plus_minus) || 0), 0),
      totalPIM: allSkaters.reduce((sum, p) => sum + (Number(p.pim ?? p.pim_total) || 0), 0),
    }
  }, [allSkaters, playersMap])

  return (
    <div className="space-y-4">
      {forwards.length > 0 && renderTable(forwards, 'Forwards')}
      {defense.length > 0 && renderTable(defense, 'Defense')}
      
      {/* Overall Team Totals - Separate Section */}
      {overallTotals && (forwards.length > 0 || defense.length > 0) && (
        <div className="mt-4 border-t-2 border-border pt-4">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-accent/50">
                  <th className="px-3 py-2 text-left font-display text-xs text-muted-foreground">Team Totals</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">#</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">Rating</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">GP</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-goal">G</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-assist">A</th>
                  <th className="px-2 py-2 text-center font-display text-xs text-primary">P</th>
                  {hasAdvancedAnalytics && (
                    <>
                      <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">P/G</th>
                      <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">+/-</th>
                      <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">CF%</th>
                      <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">TOI/G</th>
                    </>
                  )}
                  {!hasAdvancedAnalytics && (
                    <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">PIM</th>
                  )}
                </tr>
              </thead>
              <tbody>
                <tr className="border-b-2 border-border bg-muted/30 font-bold">
                  <td className="px-3 py-2 font-display">All Skaters</td>
                  <td className="px-2 py-2 text-center"></td>
                  <td className="px-2 py-2 text-center font-mono text-sm text-muted-foreground">
                    {overallTotals.avgRating != null ? Number(overallTotals.avgRating).toFixed(1) : '-'}
                  </td>
                  <td className="px-2 py-2 text-center font-mono text-muted-foreground font-semibold">
                    {overallTotals.totalGP}
                  </td>
                  <td className="px-2 py-2 text-center font-mono text-goal font-semibold">
                    {overallTotals.totalGoals}
                  </td>
                  <td className="px-2 py-2 text-center font-mono text-assist font-semibold">
                    {overallTotals.totalAssists}
                  </td>
                  <td className="px-2 py-2 text-center font-mono text-primary font-semibold">
                    {overallTotals.totalPoints}
                  </td>
                  {hasAdvancedAnalytics && (
                    <>
                      <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                        {overallTotals.totalGP > 0 ? (overallTotals.totalPoints / overallTotals.totalGP).toFixed(2) : '-'}
                      </td>
                      <td className={cn(
                        'px-2 py-2 text-center font-mono text-xs font-semibold',
                        overallTotals.totalPlusMinus > 0 && 'text-save',
                        overallTotals.totalPlusMinus < 0 && 'text-goal'
                      )}>
                        {overallTotals.totalPlusMinus > 0 ? '+' : ''}{overallTotals.totalPlusMinus}
                      </td>
                      <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">-</td>
                      <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">-</td>
                    </>
                  )}
                  {!hasAdvancedAnalytics && (
                    <td className="px-2 py-2 text-center font-mono text-muted-foreground font-semibold">
                      {overallTotals.totalPIM}
                    </td>
                  )}
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}
      
      {forwards.length === 0 && defense.length === 0 && (
        <div className="text-center text-sm text-muted-foreground py-8">
          No roster data available
        </div>
      )}
    </div>
  )
}
