'use client'

import { useState, useMemo } from 'react'
import Link from 'next/link'
import { cn } from '@/lib/utils'
import { ExportButton } from '@/components/export/ExportButton'
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react'
import { PlayerPhoto } from '@/components/players/player-photo'

interface Player {
  player_id?: string
  player_name: string
  team_name?: string
  points_rank: number
  games_played: number
  goals: number
  assists: number
  points: number
  points_per_game?: number
  pim: number
  current_skill_rating?: number
  jersey_number?: number
  player_primary_position?: string
}

interface PlayersTableWithExportProps {
  players: Player[]
}

type SortField = 'rank' | 'player' | 'team' | 'gp' | 'goals' | 'assists' | 'points' | 'pointsPerGame' | 'pim' | 'rating' | 'jersey'
type SortDirection = 'asc' | 'desc'

export function PlayersTableWithExport({ players }: PlayersTableWithExportProps) {
  const [sortField, setSortField] = useState<SortField>('rank')
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc')

  const sortedPlayers = useMemo(() => {
    const sorted = [...players]

    sorted.sort((a, b) => {
      let aValue: any
      let bValue: any

      switch (sortField) {
        case 'rank':
          aValue = a.points_rank
          bValue = b.points_rank
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
        case 'pim':
          aValue = a.pim
          bValue = b.pim
          break
        case 'rating':
          aValue = a.current_skill_rating || 0
          bValue = b.current_skill_rating || 0
          break
        case 'jersey':
          aValue = a.jersey_number || 999
          bValue = b.jersey_number || 999
          break
        default:
          aValue = a.points_rank
          bValue = b.points_rank
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

  // Prepare data for export
  const exportData = sortedPlayers.map(p => ({
    Rank: p.points_rank,
    Player: p.player_name,
    Team: p.team_name || '',
    GP: p.games_played,
    G: p.goals,
    A: p.assists,
    P: p.points,
    'P/G': p.points_per_game?.toFixed(2) || '',
    PIM: p.pim,
  }))

  return (
    <div className="bg-card rounded-xl border border-border overflow-hidden">
      <div className="px-4 py-3 bg-accent border-b border-border flex items-center justify-between">
        <h2 className="font-display text-sm font-semibold uppercase tracking-wider">
          Player Rankings
        </h2>
        <ExportButton data={exportData} filename="players" />
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-accent border-b-2 border-border">
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider w-16 cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('rank')}
              >
                <div className="flex items-center justify-center gap-1">
                  Rank
                  <SortIcon field="rank" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-left font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('player')}
              >
                <div className="flex items-center gap-1">
                  Player
                  <SortIcon field="player" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-left font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('team')}
              >
                <div className="flex items-center gap-1">
                  Team
                  <SortIcon field="team" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('gp')}
              >
                <div className="flex items-center justify-center gap-1">
                  GP
                  <SortIcon field="gp" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-goal uppercase tracking-wider cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('goals')}
              >
                <div className="flex items-center justify-center gap-1">
                  G
                  <SortIcon field="goals" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-assist uppercase tracking-wider cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('assists')}
              >
                <div className="flex items-center justify-center gap-1">
                  A
                  <SortIcon field="assists" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-primary uppercase tracking-wider cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('points')}
              >
                <div className="flex items-center justify-center gap-1">
                  P
                  <SortIcon field="points" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('pointsPerGame')}
              >
                <div className="flex items-center justify-center gap-1">
                  P/G
                  <SortIcon field="pointsPerGame" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase tracking-wider cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('pim')}
              >
                <div className="flex items-center justify-center gap-1">
                  PIM
                  <SortIcon field="pim" />
                </div>
              </th>
            </tr>
          </thead>
          <tbody>
            {sortedPlayers.map((player) => {
              const isTop3 = player.points_rank <= 3
              
              return (
                <tr
                  key={player.player_id || player.player_name}
                  className={cn(
                    'border-b border-border transition-colors hover:bg-muted/50',
                    player.points_rank % 2 === 0 && 'bg-accent/30'
                  )}
                >
                  <td className="px-4 py-3 text-center">
                    <span className={cn(
                      'font-display font-bold',
                      isTop3 ? 'text-lg text-assist' : 'text-muted-foreground'
                    )}>
                      {player.points_rank}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {player.player_id ? (
                      <Link
                        href={`/norad/players/${player.player_id}`}
                        className="font-display text-sm text-foreground hover:text-primary transition-colors"
                      >
                        {player.player_name}
                      </Link>
                    ) : (
                      <span className="font-display text-sm text-foreground">
                        {player.player_name}
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-sm text-muted-foreground">
                    {player.team_name ? (
                      <Link href={`/norad/team/${player.team_name.replace(/\s+/g, '_')}`} className="hover:text-foreground transition-colors">
                        {player.team_name}
                      </Link>
                    ) : (
                      <span>{player.team_name || '-'}</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-center font-mono text-sm text-muted-foreground">
                    {player.games_played}
                  </td>
                  <td className="px-4 py-3 text-center font-mono text-sm text-goal font-semibold">
                    {player.goals}
                  </td>
                  <td className="px-4 py-3 text-center font-mono text-sm text-assist">
                    {player.assists}
                  </td>
                  <td className="px-4 py-3 text-center font-mono text-xl font-bold text-primary">
                    {player.points}
                  </td>
                  <td className="px-4 py-3 text-center font-mono text-sm text-muted-foreground">
                    {player.points_per_game?.toFixed(2) ?? '-'}
                  </td>
                  <td className="px-4 py-3 text-center font-mono text-sm text-muted-foreground">
                    {player.pim}
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
