'use client'

import { useState, useMemo } from 'react'
import Link from 'next/link'
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react'
import { cn } from '@/lib/utils'
import { TeamLogo } from '@/components/teams/team-logo'

type SortField = 'rank' | 'team' | 'gp' | 'wins' | 'losses' | 'ties' | 'winPct' | 'gfPerGame' | 'gaPerGame' | 'gfGaDiff' | 'gf' | 'ga' | 'gd'
type SortDirection = 'asc' | 'desc'

interface AllTimeStandingsRow {
  team_id: string
  team_name: string
  season: string
  season_id: string
  games_played: number
  wins: number
  losses: number
  ties: number
  win_pct: number
  gf_per_game: number
  ga_per_game: number
  gf_ga_diff: number
  goals_for_abs: number
  goals_against_abs: number
  goal_diff_abs: number
  rank: number
  teamInfo?: any
  team_season_name: string
}

interface AllTimeStandingsTableProps {
  standings: AllTimeStandingsRow[]
}

export function AllTimeStandingsTable({ standings }: AllTimeStandingsTableProps) {
  const [sortField, setSortField] = useState<SortField>('rank')
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc')

  const sortedStandings = useMemo(() => {
    const sorted = [...standings]

    sorted.sort((a, b) => {
      let aValue: any
      let bValue: any

      switch (sortField) {
        case 'rank':
          aValue = a.rank
          bValue = b.rank
          break
        case 'team':
          aValue = a.team_season_name?.toLowerCase() || ''
          bValue = b.team_season_name?.toLowerCase() || ''
          break
        case 'gp':
          aValue = a.games_played
          bValue = b.games_played
          break
        case 'wins':
          aValue = a.wins
          bValue = b.wins
          break
        case 'losses':
          aValue = a.losses
          bValue = b.losses
          break
        case 'ties':
          aValue = a.ties || 0
          bValue = b.ties || 0
          break
        case 'winPct':
          aValue = a.win_pct
          bValue = b.win_pct
          break
        case 'gfPerGame':
          aValue = a.gf_per_game
          bValue = b.gf_per_game
          break
        case 'gaPerGame':
          aValue = a.ga_per_game
          bValue = b.ga_per_game
          break
        case 'gfGaDiff':
          aValue = a.gf_ga_diff
          bValue = b.gf_ga_diff
          break
        case 'gf':
          aValue = a.goals_for_abs
          bValue = b.goals_for_abs
          break
        case 'ga':
          aValue = a.goals_against_abs
          bValue = b.goals_against_abs
          break
        case 'gd':
          aValue = a.goal_diff_abs
          bValue = b.goal_diff_abs
          break
        default:
          aValue = a.rank
          bValue = b.rank
      }

      if (typeof aValue === 'string') {
        return sortDirection === 'asc'
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue)
      }

      return sortDirection === 'asc' ? aValue - bValue : bValue - aValue
    })

    return sorted
  }, [standings, sortField, sortDirection])

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
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border bg-accent/50">
              <th 
                className="px-4 py-3 text-left font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('rank')}
              >
                <div className="flex items-center gap-1">
                  Rank
                  <SortIcon field="rank" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-left font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('team')}
              >
                <div className="flex items-center gap-1">
                  Team Season
                  <SortIcon field="team" />
                </div>
              </th>
              <th 
                className="px-3 py-3 text-center font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('gp')}
              >
                <div className="flex items-center justify-center gap-1">
                  GP
                  <SortIcon field="gp" />
                </div>
              </th>
              <th 
                className="px-3 py-3 text-center font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('wins')}
              >
                <div className="flex items-center justify-center gap-1">
                  W
                  <SortIcon field="wins" />
                </div>
              </th>
              <th 
                className="px-3 py-3 text-center font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('losses')}
              >
                <div className="flex items-center justify-center gap-1">
                  L
                  <SortIcon field="losses" />
                </div>
              </th>
              <th 
                className="px-3 py-3 text-center font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('ties')}
              >
                <div className="flex items-center justify-center gap-1">
                  T
                  <SortIcon field="ties" />
                </div>
              </th>
              <th 
                className="px-3 py-3 text-center font-display text-xs text-primary cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('winPct')}
              >
                <div className="flex items-center justify-center gap-1">
                  Win%
                  <SortIcon field="winPct" />
                </div>
              </th>
              <th 
                className="px-3 py-3 text-center font-display text-xs text-goal cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('gfPerGame')}
              >
                <div className="flex items-center justify-center gap-1">
                  GF/G
                  <SortIcon field="gfPerGame" />
                </div>
              </th>
              <th 
                className="px-3 py-3 text-center font-display text-xs text-goal cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('gaPerGame')}
              >
                <div className="flex items-center justify-center gap-1">
                  GA/G
                  <SortIcon field="gaPerGame" />
                </div>
              </th>
              <th 
                className="px-3 py-3 text-center font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('gfGaDiff')}
              >
                <div className="flex items-center justify-center gap-1">
                  GF/GA Diff
                  <SortIcon field="gfGaDiff" />
                </div>
              </th>
              <th 
                className="px-3 py-3 text-center font-display text-xs text-goal cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('gf')}
              >
                <div className="flex items-center justify-center gap-1">
                  GF
                  <SortIcon field="gf" />
                </div>
              </th>
              <th 
                className="px-3 py-3 text-center font-display text-xs text-goal cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('ga')}
              >
                <div className="flex items-center justify-center gap-1">
                  GA
                  <SortIcon field="ga" />
                </div>
              </th>
              <th 
                className="px-3 py-3 text-center font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('gd')}
              >
                <div className="flex items-center justify-center gap-1">
                  GD
                  <SortIcon field="gd" />
                </div>
              </th>
            </tr>
          </thead>
          <tbody>
            {sortedStandings.map((team) => (
              <tr key={`${team.team_id}_${team.season_id}`} className="border-b border-border hover:bg-muted/50">
                <td className="px-4 py-3 text-center">
                  <span className={cn(
                    'font-display font-bold',
                    team.rank === 1 ? 'text-lg text-assist' : 'text-muted-foreground'
                  )}>
                    {team.rank}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-3">
                    {team.teamInfo && (
                      <TeamLogo
                        src={team.teamInfo.team_logo || null}
                        name={team.team_name || ''}
                        abbrev={team.teamInfo.team_cd}
                        primaryColor={team.teamInfo.primary_color || team.teamInfo.team_color1}
                        secondaryColor={team.teamInfo.team_color2}
                        size="sm"
                      />
                    )}
                    <Link
                      href={`/norad/team/${team.team_name.replace(/\s+/g, '_')}?season=${team.season_id}`}
                      className="font-display text-sm text-foreground hover:text-primary transition-colors"
                    >
                      {team.team_season_name}
                    </Link>
                  </div>
                </td>
                <td className="px-3 py-3 text-center font-mono text-muted-foreground">{team.games_played}</td>
                <td className="px-3 py-3 text-center font-mono text-save">{team.wins}</td>
                <td className="px-3 py-3 text-center font-mono text-goal">{team.losses}</td>
                <td className="px-3 py-3 text-center font-mono text-muted-foreground">{team.ties || 0}</td>
                <td className="px-3 py-3 text-center font-mono text-primary font-semibold">
                  {team.win_pct ? team.win_pct.toFixed(1) : '0.0'}%
                </td>
                <td className="px-3 py-3 text-center font-mono text-goal">
                  {team.gf_per_game.toFixed(2)}
                </td>
                <td className="px-3 py-3 text-center font-mono text-goal">
                  {team.ga_per_game.toFixed(2)}
                </td>
                <td className={cn(
                  'px-3 py-3 text-center font-mono text-xs cursor-pointer hover:bg-muted/50 transition-colors',
                  team.gf_ga_diff > 0 && 'text-save',
                  team.gf_ga_diff < 0 && 'text-goal'
                )}>
                  {team.gf_ga_diff > 0 ? '+' : ''}{team.gf_ga_diff.toFixed(2)}
                </td>
                <td className="px-3 py-3 text-center font-mono text-goal font-semibold">
                  {team.goals_for_abs}
                </td>
                <td className="px-3 py-3 text-center font-mono text-goal">
                  {team.goals_against_abs}
                </td>
                <td className={cn(
                  'px-3 py-3 text-center font-mono text-xs',
                  team.goal_diff_abs > 0 && 'text-save',
                  team.goal_diff_abs < 0 && 'text-goal'
                )}>
                  {team.goal_diff_abs > 0 ? '+' : ''}{team.goal_diff_abs}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
