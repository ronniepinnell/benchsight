'use client'

import Link from 'next/link'
import { Calendar, Target, TrendingUp, ArrowRight } from 'lucide-react'
import { cn } from '@/lib/utils'
import { TeamLogo } from '@/components/teams/team-logo'

interface GameCardProps {
  game: {
    game_id: number
    date?: string
    home_team_name?: string
    away_team_name?: string
    home_total_goals?: number
    away_total_goals?: number
    opponent_team_name?: string
    team_name?: string
    goals?: number
    assists?: number
    points?: number
    shots?: number
    sog?: number
    plus_minus?: number
    plus_minus_total?: number
    toi_seconds?: number
    cf_pct?: number
    player_rating?: number
    game_score?: number
    game_type?: string
  }
  isHome?: boolean
  teamInfo?: {
    team_id?: string
    team_name?: string
    team_logo?: string
    team_cd?: string
    primary_color?: string
    team_color1?: string
    team_color2?: string
  }
  opponentTeamInfo?: {
    team_id?: string
    team_name?: string
    team_logo?: string
    team_cd?: string
    primary_color?: string
    team_color1?: string
    team_color2?: string
  }
}

export function GameCard({ game, isHome, teamInfo, opponentTeamInfo }: GameCardProps) {
  if (!game.game_id) return null

  const gameDate = game.date ? new Date(game.date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  }) : 'Unknown Date'

  const opponentName = game.opponent_team_name || (isHome ? game.away_team_name : game.home_team_name) || 'Opponent'
  const teamGoals = isHome ? (game.home_total_goals ?? 0) : (game.away_total_goals ?? 0)
  const oppGoals = isHome ? (game.away_total_goals ?? 0) : (game.home_total_goals ?? 0)
  const won = teamGoals > oppGoals
  const tied = teamGoals === oppGoals

  const toiMinutes = game.toi_seconds ? Math.floor(game.toi_seconds / 60) : 0
  const toiSeconds = game.toi_seconds ? game.toi_seconds % 60 : 0
  const toiDisplay = toiMinutes > 0 ? `${toiMinutes}:${toiSeconds.toString().padStart(2, '0')}` : '-'

  return (
    <Link
      href={`/norad/games/${game.game_id}`}
      className="block bg-card rounded-lg border border-border hover:border-primary/50 transition-all hover:shadow-lg group"
    >
      <div className="p-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 text-muted-foreground" />
            <span className="text-xs font-mono text-muted-foreground uppercase">
              {gameDate}
            </span>
            {game.game_type && (game.game_type === 'Playoffs' || game.game_type === 'playoffs' || game.game_type === 'Playoff') && (
              <span className="text-xs font-mono uppercase px-1.5 py-0.5 rounded bg-primary/20 text-primary">
                Playoff
              </span>
            )}
          </div>
          <ArrowRight className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors" />
        </div>

        {/* Opponent */}
        <div className="flex items-center gap-3 mb-4">
          {opponentTeamInfo && (
            <TeamLogo
              src={opponentTeamInfo.team_logo || null}
              name={opponentTeamInfo.team_name || opponentName}
              abbrev={opponentTeamInfo.team_cd}
              primaryColor={opponentTeamInfo.primary_color || opponentTeamInfo.team_color1}
              secondaryColor={opponentTeamInfo.team_color2}
              size="sm"
            />
          )}
          <div className="flex-1">
            <div className="text-xs font-mono text-muted-foreground mb-1">
              {isHome ? 'vs' : '@'} {opponentName}
            </div>
            <div className={cn(
              'font-mono text-lg font-bold',
              won ? 'text-save' : tied ? 'text-muted-foreground' : 'text-goal'
            )}>
              {teamGoals}-{oppGoals}
            </div>
          </div>
        </div>

        {/* Player Stats */}
        <div className="grid grid-cols-4 gap-2 pt-3 border-t border-border">
          <div className="text-center">
            <div className="text-xs font-mono text-muted-foreground uppercase mb-1">G</div>
            <div className="font-mono font-semibold text-goal">{game.goals || 0}</div>
          </div>
          <div className="text-center">
            <div className="text-xs font-mono text-muted-foreground uppercase mb-1">A</div>
            <div className="font-mono font-semibold text-assist">{game.assists || 0}</div>
          </div>
          <div className="text-center">
            <div className="text-xs font-mono text-muted-foreground uppercase mb-1">P</div>
            <div className="font-mono font-bold text-primary">{game.points || 0}</div>
          </div>
          <div className="text-center">
            <div className="text-xs font-mono text-muted-foreground uppercase mb-1">+/-</div>
            <div className={cn(
              'font-mono font-semibold',
              (game.plus_minus_total ?? game.plus_minus ?? 0) > 0 && 'text-save',
              (game.plus_minus_total ?? game.plus_minus ?? 0) < 0 && 'text-goal'
            )}>
              {(game.plus_minus_total ?? game.plus_minus ?? 0) > 0 ? '+' : ''}{(game.plus_minus_total ?? game.plus_minus ?? 0)}
            </div>
          </div>
        </div>

        {/* Advanced Stats Row */}
        {(game.shots || game.toi_seconds || game.cf_pct !== undefined) && (
          <div className="grid grid-cols-3 gap-2 pt-2 mt-2 border-t border-border">
            {game.shots !== undefined && (
              <div className="text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">S</div>
                <div className="font-mono text-sm text-shot">{game.shots || 0}</div>
              </div>
            )}
            {game.toi_seconds && (
              <div className="text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">TOI</div>
                <div className="font-mono text-sm text-muted-foreground">{toiDisplay}</div>
              </div>
            )}
            {game.cf_pct !== undefined && (
              <div className="text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">CF%</div>
                <div className="font-mono text-sm text-muted-foreground">
                  {typeof game.cf_pct === 'number' ? game.cf_pct.toFixed(1) + '%' : '-'}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Rating/Game Score */}
        {(game.player_rating || game.game_score) && (
          <div className="flex items-center justify-center gap-4 pt-2 mt-2 border-t border-border">
            {game.player_rating && (
              <div className="flex items-center gap-1">
                <TrendingUp className="w-3 h-3 text-primary" />
                <span className="text-xs font-mono text-muted-foreground">Rating:</span>
                <span className="text-xs font-mono font-semibold text-primary">
                  {typeof game.player_rating === 'number' ? game.player_rating.toFixed(1) : game.player_rating}
                </span>
              </div>
            )}
            {game.game_score && (
              <div className="flex items-center gap-1">
                <Target className="w-3 h-3 text-assist" />
                <span className="text-xs font-mono text-muted-foreground">Score:</span>
                <span className="text-xs font-mono font-semibold text-assist">
                  {typeof game.game_score === 'number' ? game.game_score.toFixed(1) : game.game_score}
                </span>
              </div>
            )}
          </div>
        )}
      </div>
    </Link>
  )
}
