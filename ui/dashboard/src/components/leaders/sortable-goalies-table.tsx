// src/components/leaders/sortable-goalies-table.tsx
'use client'

import { useState, useMemo } from 'react'
import Link from 'next/link'
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react'
import { cn } from '@/lib/utils'
import { PlayerPhoto } from '@/components/players/player-photo'
import type { VLeaderboardGoalieWins } from '@/types/database'

type SortField = 'rank' | 'player' | 'team' | 'gp' | 'wins' | 'losses' | 'gaa' | 'savePct'
type SortDirection = 'asc' | 'desc'

interface SortableGoaliesTableProps {
  goalies: VLeaderboardGoalieWins[]
  playersMap?: Map<string, any>
  isCurrentSeason?: boolean
}

export function SortableGoaliesTable({ goalies, playersMap, isCurrentSeason = false }: SortableGoaliesTableProps) {
  const [sortField, setSortField] = useState<SortField>('rank')
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc')

  const sortedGoalies = useMemo(() => {
    const sorted = [...goalies].map((goalie) => {
      const gaa = (goalie as any).gaa
      const shotsAgainst = (goalie as any).shots_against || goalie.shots_against
      const goalsAgainst = goalie.goals_against || 0
      const savePct = (goalie as any).save_pct || (shotsAgainst && shotsAgainst > 0
        ? ((shotsAgainst - goalsAgainst) / shotsAgainst * 100)
        : 0)
      
      // Calculate GAA if not provided: (goals_against / games_played) * 60 minutes
      const calculatedGAA = gaa || (goalie.games_played > 0 && goalsAgainst > 0 
        ? (goalsAgainst / goalie.games_played) * 60 
        : 0)
      
      // For current season: use current team from dim_players
      // For past seasons: use team_name from leaderboard (the team they played for that season)
      let displayTeam = goalie.team_name // Default to leaderboard team_name
      
      if (isCurrentSeason) {
        // Use current team from dim_players for current season
        const playerData = playersMap?.get(String(goalie.player_id))
        displayTeam = playerData?.player_norad_current_team || playerData?.team_name || goalie.team_name
      }
      
      return {
        ...goalie,
        rank: goalie.wins_rank || 0,
        gaa: calculatedGAA,
        savePct,
        displayTeam, // Team to display (current team for current season, season team for past seasons)
      }
    })

    sorted.sort((a, b) => {
      let aValue: any
      let bValue: any

      switch (sortField) {
        case 'rank':
          aValue = a.rank
          bValue = b.rank
          break
        case 'player':
          aValue = a.player_name?.toLowerCase() || ''
          bValue = b.player_name?.toLowerCase() || ''
          break
        case 'team':
          // Use displayTeam which is already set correctly based on current vs past season
          aValue = (a.displayTeam || '').toLowerCase()
          bValue = (b.displayTeam || '').toLowerCase()
          break
        case 'gp':
          aValue = a.games_played || 0
          bValue = b.games_played || 0
          break
        case 'wins':
          aValue = a.wins || 0
          bValue = b.wins || 0
          break
        case 'losses':
          aValue = a.losses || 0
          bValue = b.losses || 0
          break
        case 'gaa':
          // For GAA, lower is better, so reverse the sort
          aValue = (a as any).gaa || 999
          bValue = (b as any).gaa || 999
          break
        case 'savePct':
          aValue = a.savePct
          bValue = b.savePct
          break
        default:
          return 0
      }

      if (typeof aValue === 'string') {
        return sortDirection === 'asc' 
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue)
      }

      // For GAA, reverse the sort direction since lower is better
      if (sortField === 'gaa') {
        return sortDirection === 'asc' ? bValue - aValue : aValue - bValue
      }

      return sortDirection === 'asc' ? aValue - bValue : bValue - aValue
    })

    return sorted
  }, [goalies, sortField, sortDirection, isCurrentSeason, playersMap])

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('asc')
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
    <div className="bg-card rounded-xl border border-border overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-accent border-b-2 border-border">
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider w-16 cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('rank')}
              >
                <div className="flex items-center justify-center">
                  Rank
                  <SortIcon field="rank" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-left font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('player')}
              >
                <div className="flex items-center">
                  Player
                  <SortIcon field="player" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-left font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('team')}
              >
                <div className="flex items-center">
                  Team
                  <SortIcon field="team" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('gp')}
              >
                <div className="flex items-center justify-center">
                  GP
                  <SortIcon field="gp" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-save uppercase tracking-wider cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('wins')}
              >
                <div className="flex items-center justify-center">
                  W
                  <SortIcon field="wins" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-goal uppercase tracking-wider cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('losses')}
              >
                <div className="flex items-center justify-center">
                  L
                  <SortIcon field="losses" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-primary uppercase tracking-wider cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('gaa')}
              >
                <div className="flex items-center justify-center">
                  GAA
                  <SortIcon field="gaa" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-assist uppercase tracking-wider cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('savePct')}
              >
                <div className="flex items-center justify-center">
                  SV%
                  <SortIcon field="savePct" />
                </div>
              </th>
            </tr>
          </thead>
          <tbody>
            {sortedGoalies.map((goalie) => {
              const isTop3 = goalie.rank <= 3

              return (
                <tr
                  key={goalie.player_id}
                  className={cn(
                    'border-b border-border transition-colors hover:bg-muted/50',
                    goalie.rank % 2 === 0 && 'bg-accent/30'
                  )}
                >
                  <td className="px-4 py-3 text-center">
                    <span className={cn(
                      'font-display font-bold',
                      isTop3 ? 'text-lg text-assist' : 'text-muted-foreground'
                    )}>
                      {goalie.rank}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {goalie.player_id ? (
                      <Link
                        href={`/players/${goalie.player_id}`}
                        className="flex items-center gap-2 hover:text-primary transition-colors"
                      >
                        <PlayerPhoto
                          src={playersMap?.get(String(goalie.player_id))?.player_image || null}
                          name={goalie.player_name || ''}
                          size="sm"
                        />
                        <span className="font-display text-sm text-foreground">
                          {goalie.player_name}
                        </span>
                      </Link>
                    ) : (
                      <div className="flex items-center gap-2">
                        <PlayerPhoto
                          src={playersMap?.get(String(goalie.player_id))?.player_image || null}
                          name={goalie.player_name || ''}
                          size="sm"
                        />
                        <span className="font-display text-sm text-foreground">
                          {goalie.player_name}
                        </span>
                      </div>
                    )}
                  </td>
                  <td className="px-4 py-3 text-sm text-muted-foreground">
                    {goalie.displayTeam ? (
                      <Link 
                        href={`/team/${goalie.displayTeam.replace(/\s+/g, '_')}`}
                        className="hover:text-foreground transition-colors"
                      >
                        {goalie.displayTeam}
                      </Link>
                    ) : (
                      <span>-</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-center font-mono text-sm text-muted-foreground">
                    {goalie.games_played}
                  </td>
                  <td className="px-4 py-3 text-center font-mono text-sm font-semibold text-save">
                    {goalie.wins}
                  </td>
                  <td className="px-4 py-3 text-center font-mono text-sm text-goal">
                    {goalie.losses}
                  </td>
                  <td className="px-4 py-3 text-center font-mono text-sm text-primary font-semibold">
                    {(goalie as any).gaa ? (goalie as any).gaa.toFixed(2) : '-'}
                  </td>
                  <td className="px-4 py-3 text-center font-mono text-sm text-assist">
                    {goalie.savePct > 0 ? goalie.savePct.toFixed(1) + '%' : '-'}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
