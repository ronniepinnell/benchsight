// src/components/leaders/sortable-leaders-table.tsx
'use client'

import { useState, useMemo } from 'react'
import Link from 'next/link'
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react'
import { cn } from '@/lib/utils'
import { PlayerPhoto } from '@/components/players/player-photo'
import type { VLeaderboardPoints, VLeaderboardGoals, VLeaderboardAssists } from '@/types/database'

type LeaderData = VLeaderboardPoints | VLeaderboardGoals | VLeaderboardAssists

type SortField = 'rank' | 'player' | 'team' | 'gp' | 'goals' | 'assists' | 'points' | 'goalsPerGame' | 'assistsPerGame' | 'pointsPerGame'
type SortDirection = 'asc' | 'desc'

interface SortableLeadersTableProps {
  leaders: LeaderData[]
  playersMap?: Map<string, any>
}

export function SortableLeadersTable({ leaders, playersMap }: SortableLeadersTableProps) {
  const [sortField, setSortField] = useState<SortField>('rank')
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc')

  const sortedLeaders = useMemo(() => {
    const sorted = [...leaders].map((player) => ({
      ...player,
      rank: player.season_rank || 0,
      goalsPerGame: player.games_played > 0 ? player.goals / player.games_played : 0,
      assistsPerGame: player.games_played > 0 ? player.assists / player.games_played : 0,
      pointsPerGame: player.games_played > 0 ? player.points / player.games_played : 0,
    }))

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
          aValue = a.team_name?.toLowerCase() || ''
          bValue = b.team_name?.toLowerCase() || ''
          break
        case 'gp':
          aValue = a.games_played || 0
          bValue = b.games_played || 0
          break
        case 'goals':
          aValue = a.goals || 0
          bValue = b.goals || 0
          break
        case 'assists':
          aValue = a.assists || 0
          bValue = b.assists || 0
          break
        case 'points':
          aValue = a.points || 0
          bValue = b.points || 0
          break
        case 'goalsPerGame':
          aValue = a.goalsPerGame
          bValue = b.goalsPerGame
          break
        case 'assistsPerGame':
          aValue = a.assistsPerGame
          bValue = b.assistsPerGame
          break
        case 'pointsPerGame':
          aValue = a.pointsPerGame
          bValue = b.pointsPerGame
          break
        default:
          return 0
      }

      if (typeof aValue === 'string') {
        return sortDirection === 'asc' 
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue)
      }

      return sortDirection === 'asc' ? aValue - bValue : bValue - aValue
    })

    return sorted
  }, [leaders, sortField, sortDirection])

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
                className="px-4 py-3 text-center font-display text-xs font-semibold text-goal uppercase tracking-wider cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('goals')}
              >
                <div className="flex items-center justify-center">
                  G
                  <SortIcon field="goals" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-assist uppercase tracking-wider cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('assists')}
              >
                <div className="flex items-center justify-center">
                  A
                  <SortIcon field="assists" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-primary uppercase tracking-wider cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('points')}
              >
                <div className="flex items-center justify-center">
                  P
                  <SortIcon field="points" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-goal uppercase tracking-wider cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('goalsPerGame')}
              >
                <div className="flex items-center justify-center">
                  G/GP
                  <SortIcon field="goalsPerGame" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-assist uppercase tracking-wider cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('assistsPerGame')}
              >
                <div className="flex items-center justify-center">
                  A/GP
                  <SortIcon field="assistsPerGame" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-primary uppercase tracking-wider cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('pointsPerGame')}
              >
                <div className="flex items-center justify-center">
                  P/GP
                  <SortIcon field="pointsPerGame" />
                </div>
              </th>
            </tr>
          </thead>
          <tbody>
            {sortedLeaders.map((player) => {
              const isTop3 = player.rank <= 3

              return (
                <tr
                  key={player.player_id}
                  className={cn(
                    'border-b border-border transition-colors hover:bg-muted/50',
                    player.rank % 2 === 0 && 'bg-accent/30'
                  )}
                >
                  <td className="px-4 py-3 text-center">
                    <span className={cn(
                      'font-display font-bold',
                      isTop3 ? 'text-lg text-assist' : 'text-muted-foreground'
                    )}>
                      {player.rank}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <Link
                      href={`/players/${player.player_id}`}
                      className="flex items-center gap-2 hover:text-primary transition-colors"
                    >
                      <PlayerPhoto
                        src={playersMap?.get(String(player.player_id))?.player_image || null}
                        name={player.player_name || ''}
                        size="sm"
                      />
                      <span className="font-display text-sm text-foreground">
                        {player.player_name}
                      </span>
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-sm text-muted-foreground">
                    {player.team_name}
                  </td>
                  <td className="px-4 py-3 text-center font-mono text-sm text-muted-foreground">
                    {player.games_played}
                  </td>
                  <td className="px-4 py-3 text-center font-mono text-sm font-semibold text-goal">
                    {player.goals}
                  </td>
                  <td className="px-4 py-3 text-center font-mono text-sm text-assist">
                    {player.assists}
                  </td>
                  <td className="px-4 py-3 text-center font-mono font-bold text-sm text-primary">
                    {player.points}
                  </td>
                  <td className="px-4 py-3 text-center font-mono text-sm text-goal">
                    {player.goalsPerGame.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 text-center font-mono text-sm text-assist">
                    {player.assistsPerGame.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 text-center font-mono text-sm text-primary font-semibold">
                    {player.pointsPerGame.toFixed(2)}
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
