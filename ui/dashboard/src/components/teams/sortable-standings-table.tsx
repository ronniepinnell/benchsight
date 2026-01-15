// src/components/teams/sortable-standings-table.tsx
'use client'

import { useState, useMemo } from 'react'
import Link from 'next/link'
import { ArrowUpDown, ArrowUp, ArrowDown, Award } from 'lucide-react'
import { cn } from '@/lib/utils'
import { TeamLogo } from '@/components/teams/team-logo'
import type { VStandingsCurrent } from '@/types/database'

type SortField = 'standing' | 'team' | 'gp' | 'wins' | 'losses' | 'ties' | 'points' | 'winPct' | 'gf' | 'ga' | 'gfPerGame' | 'gaPerGame' | 'gfGaDiff' | 'diff' | 'l10' | 'streak'
type SortDirection = 'asc' | 'desc'

interface StandingsRow extends VStandingsCurrent {
  teamInfo?: any
  last_10?: string
  streak?: string
  ties?: number
  isChampion?: boolean
  isRunnerUp?: boolean
}

interface SortableStandingsTableProps {
  standings: StandingsRow[]
  seasonId?: string
}

export function SortableStandingsTable({ standings, seasonId }: SortableStandingsTableProps) {
  const [sortField, setSortField] = useState<SortField>('standing')
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc')

  const sortedStandings = useMemo(() => {
      const sorted = [...standings].map((team) => {
        const ties = (team as any).ties || 0
        const points = team.points || (team.wins * 2 + ties) // Calculate points: W*2 + T
        // Win percentage = points / (games_played * 2) * 100
        const winPct = team.games_played > 0 ? (points / (team.games_played * 2)) * 100 : 0
        const gfPerGame = team.goals_for_per_game || (team.games_played > 0 ? team.goals_for / team.games_played : 0)
        const gaPerGame = team.goals_against_per_game || (team.games_played > 0 ? team.goals_against / team.games_played : 0)
        return {
          ...team,
          winPct,
          gfPerGame,
          gaPerGame,
          gfGaDiff: gfPerGame - gaPerGame,
          ties,
          points,
        }
      })

    sorted.sort((a, b) => {
      let aValue: any
      let bValue: any

      switch (sortField) {
        case 'standing':
          aValue = a.standing
          bValue = b.standing
          break
        case 'team':
          aValue = a.team_name?.toLowerCase() || ''
          bValue = b.team_name?.toLowerCase() || ''
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
          aValue = a.ties
          bValue = b.ties
          break
        case 'points':
          aValue = a.points
          bValue = b.points
          break
        case 'winPct':
          aValue = a.winPct
          bValue = b.winPct
          break
        case 'gf':
          aValue = a.goals_for
          bValue = b.goals_for
          break
        case 'ga':
          aValue = a.goals_against
          bValue = b.goals_against
          break
        case 'gfPerGame':
          aValue = a.gfPerGame
          bValue = b.gfPerGame
          break
        case 'gaPerGame':
          aValue = a.gaPerGame
          bValue = b.gaPerGame
          break
        case 'gfGaDiff':
          aValue = a.gfGaDiff
          bValue = b.gfGaDiff
          break
        case 'diff':
          aValue = a.goal_diff
          bValue = b.goal_diff
          break
        case 'l10':
          // Parse L10 format "W-L-T" and sort by wins first
          const aL10 = a.last_10 || '0-0-0'
          const bL10 = b.last_10 || '0-0-0'
          const [aW, aL, aT] = aL10.split('-').map(Number)
          const [bW, bL, bT] = bL10.split('-').map(Number)
          aValue = aW * 1000 + aT * 100 - aL // Wins weighted highest
          bValue = bW * 1000 + bT * 100 - bL
          break
        case 'streak':
          // Parse streak format "W3", "L2", "T1"
          const aStreak = a.streak || '-'
          const bStreak = b.streak || '-'
          if (aStreak === '-') aValue = -999
          else if (aStreak.startsWith('W')) aValue = 1000 + parseInt(aStreak.slice(1) || '0')
          else if (aStreak.startsWith('L')) aValue = -1000 - parseInt(aStreak.slice(1) || '0')
          else if (aStreak.startsWith('T')) aValue = parseInt(aStreak.slice(1) || '0')
          else aValue = -999
          
          if (bStreak === '-') bValue = -999
          else if (bStreak.startsWith('W')) bValue = 1000 + parseInt(bStreak.slice(1) || '0')
          else if (bStreak.startsWith('L')) bValue = -1000 - parseInt(bStreak.slice(1) || '0')
          else if (bStreak.startsWith('T')) bValue = parseInt(bStreak.slice(1) || '0')
          else bValue = -999
          break
        default:
          aValue = a.standing
          bValue = b.standing
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
        <table className="w-full">
          <thead>
            <tr className="bg-accent border-b-2 border-border">
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase w-16 cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('standing')}
              >
                <div className="flex items-center justify-center gap-1">
                  #
                  <SortIcon field="standing" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-left font-display text-xs font-semibold text-muted-foreground uppercase cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('team')}
              >
                <div className="flex items-center gap-1">
                  Team
                  <SortIcon field="team" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('gp')}
              >
                <div className="flex items-center justify-center gap-1">
                  GP
                  <SortIcon field="gp" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-save uppercase cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('wins')}
              >
                <div className="flex items-center justify-center gap-1">
                  W
                  <SortIcon field="wins" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-goal uppercase cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('losses')}
              >
                <div className="flex items-center justify-center gap-1">
                  L
                  <SortIcon field="losses" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('ties')}
              >
                <div className="flex items-center justify-center gap-1">
                  T
                  <SortIcon field="ties" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-primary uppercase cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('points')}
              >
                <div className="flex items-center justify-center gap-1">
                  PTS
                  <SortIcon field="points" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('winPct')}
              >
                <div className="flex items-center justify-center gap-1">
                  WIN%
                  <SortIcon field="winPct" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('gf')}
              >
                <div className="flex items-center justify-center gap-1">
                  GF
                  <SortIcon field="gf" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('ga')}
              >
                <div className="flex items-center justify-center gap-1">
                  GA
                  <SortIcon field="ga" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('gfPerGame')}
              >
                <div className="flex items-center justify-center gap-1">
                  GF/GP
                  <SortIcon field="gfPerGame" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('gaPerGame')}
              >
                <div className="flex items-center justify-center gap-1">
                  GA/GP
                  <SortIcon field="gaPerGame" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('gfGaDiff')}
              >
                <div className="flex items-center justify-center gap-1">
                  GF/GA Diff
                  <SortIcon field="gfGaDiff" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-primary uppercase cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('diff')}
              >
                <div className="flex items-center justify-center gap-1">
                  DIFF
                  <SortIcon field="diff" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('l10')}
              >
                <div className="flex items-center justify-center gap-1">
                  L10
                  <SortIcon field="l10" />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center font-display text-xs font-semibold text-muted-foreground uppercase cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleSort('streak')}
              >
                <div className="flex items-center justify-center gap-1">
                  STRK
                  <SortIcon field="streak" />
                </div>
              </th>
            </tr>
          </thead>
          <tbody>
            {sortedStandings.map((team) => {
              const winPct = team.winPct.toFixed(1)
              const isPlayoffSpot = team.standing <= 4
              const gfPerGame = team.gfPerGame.toFixed(2)
              const gaPerGame = team.gaPerGame.toFixed(2)
              const gfGaDiff = team.gfGaDiff.toFixed(2)
              
              return (
                <tr key={team.team_id} className={cn(
                  'border-b border-border transition-colors hover:bg-muted/50',
                  team.standing % 2 === 0 && 'bg-accent/30',
                  isPlayoffSpot && 'border-l-2 border-l-save'
                )}>
                  <td className="px-4 py-3 text-center">
                    <span className={cn('font-display font-bold', team.standing === 1 ? 'text-lg text-assist' : 'text-muted-foreground')}>
                      {team.standing}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <TeamLogo
                        src={team.teamInfo?.team_logo || null}
                        name={team.team_name || ''}
                        abbrev={team.teamInfo?.team_cd}
                        primaryColor={team.teamInfo?.primary_color || team.teamInfo?.team_color1}
                        secondaryColor={team.teamInfo?.team_color2}
                        size="sm"
                      />
                      {team.team_name ? (
                        <Link 
                          href={seasonId 
                            ? `/norad/team/${team.team_name.replace(/\s+/g, '_')}?season=${seasonId}`
                            : `/norad/team/${team.team_name.replace(/\s+/g, '_')}`
                          } 
                          className="font-display text-sm text-foreground hover:text-primary transition-colors flex items-center gap-2"
                        >
                          {team.team_name}
                          {team.isChampion && (
                            <Award className="w-4 h-4 text-yellow-500 fill-yellow-500" title="Champion" />
                          )}
                          {team.isRunnerUp && (
                            <Award className="w-4 h-4 text-gray-400 fill-gray-400" title="Runner Up" />
                          )}
                        </Link>
                      ) : (
                        <span className="font-display text-sm text-foreground flex items-center gap-2">
                          {team.team_name || '-'}
                          {team.isChampion && (
                            <Award className="w-4 h-4 text-yellow-500 fill-yellow-500" title="Champion" />
                          )}
                          {team.isRunnerUp && (
                            <Award className="w-4 h-4 text-gray-400 fill-gray-400" title="Runner Up" />
                          )}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-center font-mono text-sm text-muted-foreground">{team.games_played}</td>
                  <td className="px-4 py-3 text-center font-mono text-sm text-save font-semibold">{team.wins}</td>
                  <td className="px-4 py-3 text-center font-mono text-sm text-goal">{team.losses}</td>
                  <td className="px-4 py-3 text-center font-mono text-sm text-muted-foreground">{team.ties}</td>
                  <td className="px-4 py-3 text-center font-mono text-sm text-primary font-bold">{team.points}</td>
                  <td className="px-4 py-3 text-center font-mono text-sm text-foreground">{winPct}%</td>
                  <td className="px-4 py-3 text-center font-mono text-sm text-muted-foreground">{team.goals_for}</td>
                  <td className="px-4 py-3 text-center font-mono text-sm text-muted-foreground">{team.goals_against}</td>
                  <td className="px-4 py-3 text-center font-mono text-sm text-muted-foreground">{gfPerGame}</td>
                  <td className="px-4 py-3 text-center font-mono text-sm text-muted-foreground">{gaPerGame}</td>
                  <td className={cn('px-4 py-3 text-center font-mono text-sm',
                    team.gfGaDiff > 0 ? 'text-save' : team.gfGaDiff < 0 ? 'text-goal' : 'text-muted-foreground'
                  )}>
                    {team.gfGaDiff > 0 ? '+' : ''}{gfGaDiff}
                  </td>
                  <td className={cn('px-4 py-3 text-center font-mono text-sm font-bold',
                    team.goal_diff > 0 ? 'text-save' : team.goal_diff < 0 ? 'text-goal' : 'text-muted-foreground'
                  )}>
                    {team.goal_diff > 0 ? '+' : ''}{team.goal_diff}
                  </td>
                  <td className="px-4 py-3 text-center font-mono text-sm text-muted-foreground">{team.last_10 || '-'}</td>
                  <td className="px-4 py-3 text-center font-mono text-sm">
                    <span className={cn(
                      team.streak?.startsWith('W') && 'text-save',
                      team.streak?.startsWith('L') && 'text-goal',
                      team.streak?.startsWith('T') && 'text-muted-foreground',
                      !team.streak || team.streak === '-' ? 'text-muted-foreground' : ''
                    )}>
                      {team.streak || '-'}
                    </span>
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
