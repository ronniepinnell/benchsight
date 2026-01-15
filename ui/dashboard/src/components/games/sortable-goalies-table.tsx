'use client'

import { useState, useMemo } from 'react'
import Link from 'next/link'
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react'
import { cn } from '@/lib/utils'
import { PlayerPhoto } from '@/components/players/player-photo'
import { TeamLogo } from '@/components/teams/team-logo'

type SortField = 'goalie' | 'team' | 'saves' | 'shots' | 'savePct' | 'ga' | 'gaa'
type SortDirection = 'asc' | 'desc'

interface GoalieRow {
  player_id: string
  player_name?: string
  player_full_name?: string
  team_id?: string
  team_name?: string
  saves?: number
  shots?: number
  save_pct?: number
  goals_against?: number
  gaa?: number
  [key: string]: any
}

interface SortableGoaliesTableProps {
  goalies: GoalieRow[]
  playersMap: Map<string, any>
  teamsMap: Map<string, any>
  hasTracking: boolean
}

export function SortableGoaliesTable({
  goalies,
  playersMap,
  teamsMap,
  hasTracking,
}: SortableGoaliesTableProps) {
  const [sortField, setSortField] = useState<SortField>('gaa')
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc')

  const sortedGoalies = useMemo(() => {
    const sorted = [...goalies]

    sorted.sort((a, b) => {
      let aValue: any
      let bValue: any

      switch (sortField) {
        case 'goalie':
          aValue = (a.player_full_name || a.player_name || '').toLowerCase()
          bValue = (b.player_full_name || b.player_name || '').toLowerCase()
          break
        case 'team':
          aValue = (a.team_name || '').toLowerCase()
          bValue = (b.team_name || '').toLowerCase()
          break
        case 'saves':
          aValue = Number(a.saves ?? 0)
          bValue = Number(b.saves ?? 0)
          break
        case 'shots':
          aValue = Number(a.shots ?? 0)
          bValue = Number(b.shots ?? 0)
          break
        case 'savePct':
          aValue = typeof a.save_pct === 'number' ? a.save_pct : parseFloat(String(a.save_pct || 0))
          bValue = typeof b.save_pct === 'number' ? b.save_pct : parseFloat(String(b.save_pct || 0))
          break
        case 'ga':
          aValue = Number(a.goals_against ?? 0)
          bValue = Number(b.goals_against ?? 0)
          break
        case 'gaa':
          aValue = typeof a.gaa === 'number' ? a.gaa : parseFloat(String(a.gaa || 999))
          bValue = typeof b.gaa === 'number' ? b.gaa : parseFloat(String(b.gaa || 999))
          break
        default:
          aValue = typeof a.gaa === 'number' ? a.gaa : parseFloat(String(a.gaa || 999))
          bValue = typeof b.gaa === 'number' ? b.gaa : parseFloat(String(b.gaa || 999))
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
      setSortDirection(field === 'gaa' || field === 'ga' ? 'asc' : 'desc')
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
              onClick={() => handleSort('goalie')}
            >
              <div className="flex items-center gap-1">
                Goalie
                <SortIcon field="goalie" />
              </div>
            </th>
            <th 
              className="px-3 py-2 text-left font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
              onClick={() => handleSort('team')}
            >
              <div className="flex items-center gap-1">
                Team
                <SortIcon field="team" />
              </div>
            </th>
            {hasTracking && (
              <>
                <th 
                  className="px-2 py-2 text-center font-display text-xs text-save cursor-pointer hover:bg-muted/50 transition-colors"
                  onClick={() => handleSort('saves')}
                >
                  <div className="flex items-center justify-center gap-1">
                    Saves
                    <SortIcon field="saves" />
                  </div>
                </th>
                <th 
                  className="px-2 py-2 text-center font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
                  onClick={() => handleSort('shots')}
                >
                  <div className="flex items-center justify-center gap-1">
                    Shots
                    <SortIcon field="shots" />
                  </div>
                </th>
                <th 
                  className="px-2 py-2 text-center font-display text-xs text-primary cursor-pointer hover:bg-muted/50 transition-colors"
                  onClick={() => handleSort('savePct')}
                >
                  <div className="flex items-center justify-center gap-1">
                    SV%
                    <SortIcon field="savePct" />
                  </div>
                </th>
              </>
            )}
            <th 
              className="px-2 py-2 text-center font-display text-xs text-goal cursor-pointer hover:bg-muted/50 transition-colors"
              onClick={() => handleSort('ga')}
            >
              <div className="flex items-center justify-center gap-1">
                GA
                <SortIcon field="ga" />
              </div>
            </th>
            {hasTracking && (
              <th 
                className="px-2 py-2 text-center font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('gaa')}
              >
                <div className="flex items-center justify-center gap-1">
                  GAA
                  <SortIcon field="gaa" />
                </div>
              </th>
            )}
          </tr>
        </thead>
        <tbody>
          {sortedGoalies.map((goalie) => {
            const goalieInfo = playersMap.get(String(goalie.player_id))
            const goalieTeamId = String(goalie.team_id || '')
            const goalieTeam = teamsMap.get(goalieTeamId)
            
            return (
              <tr key={goalie.player_id} className="border-b border-border hover:bg-muted/50">
                <td className="px-3 py-2">
                  <Link
                    href={`/norad/players/${goalie.player_id}`}
                    className="flex items-center gap-2 text-foreground hover:text-primary transition-colors"
                  >
                    <PlayerPhoto
                      src={goalieInfo?.player_image || null}
                      name={goalie.player_full_name || goalie.player_name || ''}
                      primaryColor={goalieTeam?.primary_color || goalieTeam?.team_color1}
                      size="sm"
                    />
                    <span>{goalie.player_full_name || goalie.player_name}</span>
                  </Link>
                </td>
                <td className="px-3 py-2">
                  {goalieTeam ? (
                    <Link
                      href={`/norad/team/${(goalieTeam.team_name || '').replace(/\s+/g, '_')}`}
                      className="flex items-center gap-2 text-foreground hover:text-primary transition-colors"
                    >
                      <TeamLogo
                        src={goalieTeam.team_logo || null}
                        name={goalieTeam.team_name || ''}
                        abbrev={goalieTeam.team_cd}
                        primaryColor={goalieTeam.primary_color || goalieTeam.team_color1}
                        secondaryColor={goalieTeam.team_color2}
                        size="xs"
                      />
                      <span className="text-sm">{goalieTeam.team_name || goalie.team_name}</span>
                    </Link>
                  ) : (
                    <span className="text-sm text-muted-foreground">{goalie.team_name || '-'}</span>
                  )}
                </td>
                {hasTracking && (
                  <>
                    <td className="px-2 py-2 text-center font-mono text-save font-semibold">
                      {goalie.saves ?? '-'}
                    </td>
                    <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                      {goalie.shots ?? '-'}
                    </td>
                    <td className="px-2 py-2 text-center font-mono text-primary font-semibold">
                      {goalie.save_pct 
                        ? (typeof goalie.save_pct === 'number' 
                            ? (goalie.save_pct * 100).toFixed(1) + '%'
                            : String(goalie.save_pct))
                        : '-'}
                    </td>
                  </>
                )}
                <td className="px-2 py-2 text-center font-mono text-goal font-semibold">
                  {goalie.goals_against ?? 0}
                </td>
                {hasTracking && (
                  <td className="px-2 py-2 text-center font-mono text-muted-foreground">
                    {goalie.gaa != null && !isNaN(Number(goalie.gaa))
                      ? Number(goalie.gaa).toFixed(2)
                      : '-'}
                  </td>
                )}
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
