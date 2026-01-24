'use client'

import Link from 'next/link'
import { Star } from 'lucide-react'
import { cn } from '@/lib/utils'
import { PlayerPhoto } from '@/components/players/player-photo'
import { TeamLogo } from '@/components/teams/team-logo'

interface StarPlayer {
  player_id: string
  player_name: string
  player_image?: string | null
  team_name?: string
  team_id?: string
  team_logo?: string | null
  team_cd?: string
  primary_color?: string
  goals: number
  assists: number
  points: number
  position?: string
  // For goalies
  saves?: number
  save_pct?: number
  goals_against?: number
}

interface ThreeStarsProps {
  stars: [StarPlayer, StarPlayer, StarPlayer] | StarPlayer[]
  className?: string
}

export function ThreeStars({ stars, className }: ThreeStarsProps) {
  if (!stars || stars.length < 3) {
    return null
  }

  const [firstStar, secondStar, thirdStar] = stars

  return (
    <div className={cn('bg-card rounded-xl border border-border overflow-hidden', className)}>
      <div className="px-4 py-2 border-b border-border bg-gradient-to-r from-yellow-500/10 via-transparent to-yellow-500/10">
        <div className="flex items-center gap-2">
          <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
          <h2 className="font-display text-sm font-semibold uppercase tracking-wider">Three Stars</h2>
        </div>
      </div>

      <div className="divide-y divide-border">
        <StarRow player={firstStar} rank={1} />
        <StarRow player={secondStar} rank={2} />
        <StarRow player={thirdStar} rank={3} />
      </div>
    </div>
  )
}

interface StarRowProps {
  player: StarPlayer
  rank: 1 | 2 | 3
}

function StarRow({ player, rank }: StarRowProps) {
  const starColors = {
    1: 'text-yellow-500',
    2: 'text-gray-400',
    3: 'text-amber-700'
  }

  const isGoalie = player.position?.toUpperCase() === 'G' ||
                   player.position?.toUpperCase() === 'GOALIE' ||
                   player.saves !== undefined

  return (
    <div className="px-4 py-2.5 flex items-center gap-3 hover:bg-muted/30 transition-colors">
      {/* Rank stars */}
      <div className="flex items-center gap-0.5 w-12 flex-shrink-0">
        {Array.from({ length: rank }).map((_, i) => (
          <Star
            key={i}
            className={cn('w-3.5 h-3.5 fill-current', starColors[rank])}
          />
        ))}
      </div>

      {/* Player photo */}
      <Link
        href={`/norad/player/${player.player_id}`}
        className="flex-shrink-0 hover:opacity-80 transition-opacity"
      >
        <PlayerPhoto
          src={player.player_image || null}
          name={player.player_name}
          primaryColor={player.primary_color}
          size="sm"
        />
      </Link>

      {/* Player name & team */}
      <div className="flex-1 min-w-0">
        <Link
          href={`/norad/player/${player.player_id}`}
          className="font-display text-sm font-semibold text-foreground hover:text-primary transition-colors block truncate"
        >
          {player.player_name}
        </Link>
        {player.team_name && (
          <div className="flex items-center gap-1.5">
            {player.team_logo && (
              <TeamLogo
                src={player.team_logo}
                name={player.team_name}
                abbrev={player.team_cd}
                primaryColor={player.primary_color}
                size="xs"
              />
            )}
            <span className="text-xs text-muted-foreground truncate">{player.team_name}</span>
          </div>
        )}
      </div>

      {/* Stats */}
      <div className="flex-shrink-0 text-right">
        {isGoalie ? (
          <div>
            <div className="font-mono text-sm font-bold text-foreground">
              {player.saves ?? 0} SV
            </div>
            <div className="text-xs font-mono text-muted-foreground">
              {player.save_pct !== undefined
                ? `${(player.save_pct * 100).toFixed(1)}%`
                : `${player.goals_against ?? 0} GA`
              }
            </div>
          </div>
        ) : (
          <div>
            <div className="font-mono text-sm font-bold text-foreground">
              {player.goals}G {player.assists}A
            </div>
            <div className="text-xs font-mono text-muted-foreground">
              {player.points} pts
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
