'use client'

import { useState, useMemo } from 'react'
import Link from 'next/link'
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react'
import { cn } from '@/lib/utils'
import { TeamLogo } from '@/components/teams/team-logo'

type SortField = 'team' | 'gp' | 'rating' | 'goals' | 'assists' | 'points' | 'pim' | 'goalsPerGame' | 'assistsPerGame' | 'pointsPerGame'
type SortDirection = 'asc' | 'desc'

interface PriorTeam {
  team_id: string
  team_name: string
  games: number
  goals: number
  assists: number
  points: number
  pim: number
  avg_rating?: number | null
  team_info?: any
}

interface SortablePriorTeamsTableProps {
  teams: PriorTeam[]
  seasonId: string
  seasonAvgRating?: number | null
}

export function SortablePriorTeamsTable({ teams, seasonId, seasonAvgRating }: SortablePriorTeamsTableProps) {
  const [sortField, setSortField] = useState<SortField>('points')
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc')

  const sortedTeams = useMemo(() => {
    const sorted = [...teams]

    sorted.sort((a, b) => {
      let aValue: any
      let bValue: any

      switch (sortField) {
        case 'team':
          aValue = (a.team_info?.team_name || a.team_name || '').toLowerCase()
          bValue = (b.team_info?.team_name || b.team_name || '').toLowerCase()
          break
        case 'gp':
          aValue = a.games
          bValue = b.games
          break
        case 'rating':
          aValue = a.avg_rating ?? 0
          bValue = b.avg_rating ?? 0
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
        case 'pim':
          aValue = a.pim
          bValue = b.pim
          break
        case 'goalsPerGame':
          aValue = a.games > 0 ? (a.goals / a.games) : 0
          bValue = b.games > 0 ? (b.goals / b.games) : 0
          break
        case 'assistsPerGame':
          aValue = a.games > 0 ? (a.assists / a.games) : 0
          bValue = b.games > 0 ? (b.assists / b.games) : 0
          break
        case 'pointsPerGame':
          aValue = a.games > 0 ? (a.points / a.games) : 0
          bValue = b.games > 0 ? (b.points / b.games) : 0
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
  }, [teams, sortField, sortDirection])

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
              onClick={() => handleSort('team')}
            >
              <div className="flex items-center gap-1">
                Team
                <SortIcon field="team" />
              </div>
            </th>
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
            <th 
              className="px-2 py-2 text-center font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
              onClick={() => handleSort('pim')}
            >
              <div className="flex items-center justify-center gap-1">
                PIM
                <SortIcon field="pim" />
              </div>
            </th>
            <th 
              className="px-2 py-2 text-center font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
              onClick={() => handleSort('goalsPerGame')}
            >
              <div className="flex items-center justify-center gap-1">
                G/G
                <SortIcon field="goalsPerGame" />
              </div>
            </th>
            <th 
              className="px-2 py-2 text-center font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
              onClick={() => handleSort('assistsPerGame')}
            >
              <div className="flex items-center justify-center gap-1">
                A/G
                <SortIcon field="assistsPerGame" />
              </div>
            </th>
            <th 
              className="px-2 py-2 text-center font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
              onClick={() => handleSort('pointsPerGame')}
            >
              <div className="flex items-center justify-center gap-1">
                P/G
                <SortIcon field="pointsPerGame" />
              </div>
            </th>
          </tr>
        </thead>
        <tbody>
          {sortedTeams.map((team) => {
            const teamInfo = team.team_info
            const goalsPerGame = team.games > 0 ? (team.goals / team.games) : 0
            const assistsPerGame = team.games > 0 ? (team.assists / team.games) : 0
            const pointsPerGame = team.games > 0 ? (team.points / team.games) : 0
            
            return (
              <tr key={`${seasonId}-${team.team_id}`} className="border-b border-border hover:bg-muted/50">
                <td className="px-3 py-2">
                  <Link
                    href={`/norad/team/${(teamInfo?.team_name || team.team_name || '').replace(/\s+/g, '_')}`}
                    className="flex items-center gap-2 text-foreground hover:text-primary transition-colors"
                  >
                    {teamInfo && (
                      <TeamLogo
                        src={teamInfo.team_logo || null}
                        name={teamInfo.team_name || team.team_name}
                        abbrev={teamInfo.team_cd}
                        primaryColor={teamInfo.primary_color || teamInfo.team_color1}
                        secondaryColor={teamInfo.team_color2}
                        size="xs"
                      />
                    )}
                    <span className="font-display text-sm font-semibold">
                      {teamInfo?.team_name || team.team_name}
                    </span>
                  </Link>
                </td>
                <td className="px-2 py-2 text-center font-mono text-muted-foreground">{team.games}</td>
                <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                  {team.avg_rating != null ? Math.round(Number(team.avg_rating)) : '-'}
                </td>
                <td className="px-2 py-2 text-center font-mono text-goal font-semibold">{team.goals}</td>
                <td className="px-2 py-2 text-center font-mono text-assist">{team.assists}</td>
                <td className="px-2 py-2 text-center font-mono text-primary font-semibold">{team.points}</td>
                <td className="px-2 py-2 text-center font-mono text-muted-foreground">{team.pim}</td>
                <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                  {goalsPerGame.toFixed(2)}
                </td>
                <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                  {assistsPerGame.toFixed(2)}
                </td>
                <td className="px-2 py-2 text-center font-mono text-xs text-muted-foreground">
                  {pointsPerGame.toFixed(2)}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
