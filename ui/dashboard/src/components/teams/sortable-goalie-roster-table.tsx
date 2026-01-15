'use client'

import { useState, useMemo } from 'react'
import Link from 'next/link'
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react'
import { cn } from '@/lib/utils'
import { PlayerPhoto } from '@/components/players/player-photo'

type SortField = 'player' | 'gp' | 'gaa' | 'savePct' | 'wins' | 'losses' | 'shutouts'
type SortDirection = 'asc' | 'desc'

interface GoalieRosterPlayer {
  player_id: string
  player_name: string
  games_played: number
  gaa?: number | null
  save_pct?: number | null
  saves?: number | null
  shots_against?: number | null
  goals_against?: number | null
  wins?: number | null
  losses?: number | null
  ties?: number | null
  shutouts?: number | null
  jersey_number?: number | string
  current_skill_rating?: number | string
}

interface SortableGoalieRosterTableProps {
  goalies: GoalieRosterPlayer[]
  playersMap: Map<string, any>
  teamColor?: string
  title?: string
}

export function SortableGoalieRosterTable({ 
  goalies, 
  playersMap, 
  teamColor,
  title 
}: SortableGoalieRosterTableProps) {
  const [sortField, setSortField] = useState<SortField>('gaa')
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc')

  const sortedGoalies = useMemo(() => {
    const sorted = [...goalies]

    sorted.sort((a, b) => {
      let aValue: any
      let bValue: any

      switch (sortField) {
        case 'player':
          aValue = a.player_name?.toLowerCase() || ''
          bValue = b.player_name?.toLowerCase() || ''
          break
        case 'gp':
          aValue = a.games_played || 0
          bValue = b.games_played || 0
          break
        case 'gaa':
          aValue = a.gaa != null ? Number(a.gaa) : 999
          bValue = b.gaa != null ? Number(b.gaa) : 999
          break
        case 'savePct':
          aValue = a.save_pct != null ? Number(a.save_pct) : -1
          bValue = b.save_pct != null ? Number(b.save_pct) : -1
          break
        case 'wins':
          aValue = a.wins || 0
          bValue = b.wins || 0
          break
        case 'losses':
          aValue = a.losses || 0
          bValue = b.losses || 0
          break
        case 'shutouts':
          aValue = a.shutouts || 0
          bValue = b.shutouts || 0
          break
        default:
          aValue = a.gaa != null ? Number(a.gaa) : 999
          bValue = b.gaa != null ? Number(b.gaa) : 999
      }

      if (typeof aValue === 'string') {
        return sortDirection === 'asc'
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue)
      }

      return sortDirection === 'asc' ? aValue - bValue : bValue - aValue
    })

    return sorted
  }, [goalies, sortField, sortDirection])

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection(field === 'gaa' ? 'asc' : 'desc')
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

  if (goalies.length === 0) {
    return null
  }

  // Calculate totals
  const totalGP = goalies.reduce((sum, g) => sum + (Number(g.games_played) || 0), 0)
  const totalWins = goalies.reduce((sum, g) => sum + (Number(g.wins) || 0), 0)
  const totalLosses = goalies.reduce((sum, g) => sum + (Number(g.losses) || 0), 0)
  const totalTies = goalies.reduce((sum, g) => sum + (Number(g.ties) || 0), 0)
  const totalShutouts = goalies.reduce((sum, g) => sum + (Number(g.shutouts) || 0), 0)
  const totalGoalsAgainst = goalies.reduce((sum, g) => sum + (Number(g.goals_against) || 0), 0)
  const totalSaves = goalies.reduce((sum, g) => sum + (Number(g.saves) || 0), 0)
  const totalShotsAgainst = goalies.reduce((sum, g) => sum + (Number(g.shots_against) || 0), 0)
  
  const avgGAA = totalGP > 0 ? totalGoalsAgainst / totalGP : null
  const avgSavePct = totalShotsAgainst > 0 ? (totalSaves / totalShotsAgainst) * 100 : null
  
  const goaliesWithRatings = goalies.filter(g => {
    const rating = g.current_skill_rating ?? playersMap.get(String(g.player_id))?.current_skill_rating
    return rating != null && rating !== '' && Number(rating) > 0
  })
  const avgRating = goaliesWithRatings.length > 0
    ? goaliesWithRatings.reduce((sum, g) => {
        const rating = g.current_skill_rating ?? playersMap.get(String(g.player_id))?.current_skill_rating
        return sum + Number(rating || 0)
      }, 0) / goaliesWithRatings.length
    : null

  return (
    <div className="overflow-x-auto">
      {title && (
        <div className="px-4 py-2 bg-muted/30 border-b border-border">
          <h3 className="font-display text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            {title} ({sortedGoalies.length})
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
              className="px-2 py-2 text-center font-display text-xs text-primary cursor-pointer hover:bg-muted/50 transition-colors"
              onClick={() => handleSort('gaa')}
            >
              <div className="flex items-center justify-center gap-1">
                GAA
                <SortIcon field="gaa" />
              </div>
            </th>
            <th 
              className="px-2 py-2 text-center font-display text-xs text-save cursor-pointer hover:bg-muted/50 transition-colors"
              onClick={() => handleSort('savePct')}
            >
              <div className="flex items-center justify-center gap-1">
                SV%
                <SortIcon field="savePct" />
              </div>
            </th>
            <th 
              className="px-2 py-2 text-center font-display text-xs text-assist cursor-pointer hover:bg-muted/50 transition-colors"
              onClick={() => handleSort('wins')}
            >
              <div className="flex items-center justify-center gap-1">
                W
                <SortIcon field="wins" />
              </div>
            </th>
            <th 
              className="px-2 py-2 text-center font-display text-xs text-goal cursor-pointer hover:bg-muted/50 transition-colors"
              onClick={() => handleSort('losses')}
            >
              <div className="flex items-center justify-center gap-1">
                L
                <SortIcon field="losses" />
              </div>
            </th>
            <th 
              className="px-2 py-2 text-center font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
              onClick={() => handleSort('shutouts')}
            >
              <div className="flex items-center justify-center gap-1">
                SO
                <SortIcon field="shutouts" />
              </div>
            </th>
            <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">Saves</th>
          </tr>
        </thead>
        <tbody>
          {sortedGoalies.map((goalie) => {
            const goalieInfo = playersMap.get(String(goalie.player_id))
            return (
              <tr key={goalie.player_id} className="border-b border-border hover:bg-muted/50">
                <td className="px-3 py-2">
                  <Link 
                    href={`/norad/players/${goalie.player_id}`}
                    className="flex items-center gap-2 text-foreground hover:text-primary transition-colors"
                  >
                    <PlayerPhoto
                      src={goalieInfo?.player_image || null}
                      name={goalie.player_name || ''}
                      primaryColor={teamColor}
                      size="sm"
                    />
                    <span>{goalie.player_name}</span>
                  </Link>
                </td>
                <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                  {goalie.jersey_number ?? goalieInfo?.jersey_number ?? '-'}
                </td>
                <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                  {goalie.current_skill_rating ?? goalieInfo?.current_skill_rating 
                    ? Math.round(Number(goalie.current_skill_rating ?? goalieInfo?.current_skill_rating)) 
                    : '-'}
                </td>
                <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                  {goalie.games_played || 0}
                </td>
                <td className="px-2 py-2 text-center font-mono text-primary font-semibold">
                  {goalie.gaa != null && !isNaN(Number(goalie.gaa)) ? Number(goalie.gaa).toFixed(2) : '-'}
                </td>
                <td className="px-2 py-2 text-center font-mono text-save font-semibold">
                  {goalie.save_pct != null 
                    ? (typeof goalie.save_pct === 'number' 
                        ? (goalie.save_pct * 100).toFixed(1) 
                        : Number(goalie.save_pct).toFixed(1)) + '%'
                    : '-'}
                </td>
                <td className="px-2 py-2 text-center font-mono text-assist font-semibold">
                  {goalie.wins || 0}
                </td>
                <td className="px-2 py-2 text-center font-mono text-goal">
                  {goalie.losses || 0}
                </td>
                <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                  {goalie.shutouts || 0}
                </td>
                <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                  {goalie.saves || 0}
                </td>
              </tr>
            )
          })}
          
          {/* Totals Row */}
          {sortedGoalies.length > 0 && (
            <tr className="border-t-2 border-border bg-muted/30 font-bold">
              <td className="px-3 py-2 font-display">
                {title ? `${title} Totals` : 'Totals'}
              </td>
              <td className="px-2 py-2 text-center"></td>
              <td className="px-2 py-2 text-center font-mono text-sm text-muted-foreground">
                {avgRating != null ? Number(avgRating).toFixed(1) : '-'}
              </td>
              <td className="px-2 py-2 text-center font-mono text-muted-foreground font-semibold">
                {totalGP}
              </td>
              <td className="px-2 py-2 text-center font-mono text-primary font-semibold">
                {avgGAA != null ? avgGAA.toFixed(2) : '-'}
              </td>
              <td className="px-2 py-2 text-center font-mono text-save font-semibold">
                {avgSavePct != null ? avgSavePct.toFixed(1) + '%' : '-'}
              </td>
              <td className="px-2 py-2 text-center font-mono text-assist font-semibold">
                {totalWins}
              </td>
              <td className="px-2 py-2 text-center font-mono text-goal font-semibold">
                {totalLosses}
              </td>
              <td className="px-2 py-2 text-center font-mono text-muted-foreground font-semibold">
                {totalShutouts}
              </td>
              <td className="px-2 py-2 text-center font-mono text-muted-foreground font-semibold">
                {totalSaves}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}
