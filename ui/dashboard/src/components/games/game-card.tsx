'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Calendar, ChevronRight, CheckCircle2, AlertCircle, XCircle, Info, Trophy } from 'lucide-react'
import { cn } from '@/lib/utils'
import { TeamLogo } from '@/components/teams/team-logo'

interface GameCardProps {
  game: any
  teamsMap: Map<string, any>
  trackingStatus?: {
    status: string
    coverage?: string
    missing?: string[]
  } | null
  isChampionship?: boolean
}

export function GameCard({ game, teamsMap, trackingStatus, isChampionship = false }: GameCardProps) {
  const router = useRouter()
  
  if (!game.game_id) return null
  
  // Get scores from multiple sources, prioritizing official scores
  const homeGoals = game.official_home_goals ?? game.home_total_goals ?? 0
  const awayGoals = game.official_away_goals ?? game.away_total_goals ?? 0
  const homeWon = homeGoals > awayGoals
  const awayWon = awayGoals > homeGoals
  const gameDate = game.date ? new Date(game.date).toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  }) : 'Unknown Date'
  
  const handleCardClick = () => {
    router.push(`/norad/games/${game.game_id}`)
  }
  
  return (
    <div
      onClick={handleCardClick}
      className="block bg-card rounded-lg border border-border hover:border-primary/50 transition-all hover:shadow-lg group cursor-pointer"
    >
      <div className="p-3 sm:p-4">
        {/* Date & Game Type */}
        <div className="flex items-center gap-2 mb-3 flex-wrap">
          <Calendar className="w-4 h-4 text-muted-foreground" />
          <span className="text-xs font-mono text-muted-foreground uppercase">
            {gameDate}
          </span>
          {isChampionship && (
            <div className="flex items-center gap-1">
              <Trophy className="w-3 h-3 text-yellow-500 fill-yellow-500" />
              <span className="text-xs font-mono uppercase px-1.5 py-0.5 rounded bg-yellow-500/20 text-yellow-600 font-semibold">
                Championship
              </span>
            </div>
          )}
          {game.game_type && (
            <span className={cn(
              'text-xs font-mono uppercase px-1.5 py-0.5 rounded',
              game.game_type === 'Playoffs' || game.game_type === 'playoffs' || game.game_type === 'Playoff'
                ? 'bg-primary/20 text-primary'
                : 'bg-muted text-muted-foreground'
            )}>
              {game.game_type === 'Playoffs' || game.game_type === 'playoffs' || game.game_type === 'Playoff' 
                ? 'Playoff' 
                : 'Regular'}
            </span>
          )}
        </div>
        
        {/* Matchup */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-0">
          <div className="flex-1 space-y-2 w-full sm:w-auto">
            {/* Away Team */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {game.away_team_id && teamsMap.get(String(game.away_team_id)) && (
                  <TeamLogo
                    src={teamsMap.get(String(game.away_team_id))!.team_logo || null}
                    name={teamsMap.get(String(game.away_team_id))!.team_name || game.away_team_name || ''}
                    abbrev={teamsMap.get(String(game.away_team_id))!.team_cd}
                    primaryColor={teamsMap.get(String(game.away_team_id))!.primary_color || teamsMap.get(String(game.away_team_id))!.team_color1}
                    secondaryColor={teamsMap.get(String(game.away_team_id))!.team_color2}
                    size="xs"
                  />
                )}
                <Link
                  href={`/norad/team/${(game.away_team_name ?? 'Away Team').replace(/\s+/g, '_')}`}
                  onClick={(e) => e.stopPropagation()}
                  className={cn(
                    'font-display text-sm hover:text-primary transition-colors',
                    awayWon ? 'text-foreground font-semibold' : 'text-muted-foreground'
                  )}
                >
                  {game.away_team_name ?? 'Away Team'}
                </Link>
              </div>
              <span className={cn(
                'font-mono text-xl font-bold',
                awayWon ? 'text-save' : 'text-muted-foreground'
              )}>
                {game.away_total_goals ?? 0}
              </span>
            </div>
            
            {/* Home Team */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {game.home_team_id && teamsMap.get(String(game.home_team_id)) && (
                  <TeamLogo
                    src={teamsMap.get(String(game.home_team_id))!.team_logo || null}
                    name={teamsMap.get(String(game.home_team_id))!.team_name || game.home_team_name || ''}
                    abbrev={teamsMap.get(String(game.home_team_id))!.team_cd}
                    primaryColor={teamsMap.get(String(game.home_team_id))!.primary_color || teamsMap.get(String(game.home_team_id))!.team_color1}
                    secondaryColor={teamsMap.get(String(game.home_team_id))!.team_color2}
                    size="xs"
                  />
                )}
                <span className={cn(
                  'font-display text-sm',
                  homeWon ? 'text-foreground font-semibold' : 'text-muted-foreground'
                )}>
                  @{' '}
                  <Link
                    href={`/norad/team/${(game.home_team_name ?? 'Home Team').replace(/\s+/g, '_')}`}
                    onClick={(e) => e.stopPropagation()}
                    className="hover:text-foreground transition-colors"
                  >
                    {game.home_team_name ?? 'Home Team'}
                  </Link>
                </span>
              </div>
              <span className={cn(
                'font-mono text-xl font-bold',
                homeWon ? 'text-save' : 'text-muted-foreground'
              )}>
                {homeGoals}
              </span>
            </div>
          </div>
          
          {/* Arrow */}
          <ChevronRight className="w-5 h-5 text-muted-foreground ml-4 group-hover:text-primary transition-colors" />
        </div>
        
        {/* Tracking Status & Final indicator */}
        <div className="mt-3 pt-3 border-t border-border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-mono text-muted-foreground uppercase">
              Final
            </span>
            <span className="text-xs font-mono text-primary">
              View Box Score →
            </span>
          </div>
          {(() => {
            if (!trackingStatus || trackingStatus.status === 'none') {
              return (
                <div className="flex items-center gap-2 text-xs">
                  <XCircle className="w-3 h-3 text-muted-foreground" />
                  <span className="text-muted-foreground font-mono">No tracking data</span>
                </div>
              )
            }
            
            const statusConfig = {
              full: { icon: CheckCircle2, color: 'text-save', label: 'Full Tracking' },
              partial: { icon: AlertCircle, color: 'text-assist', label: 'Partial Tracking' },
              'non-full': { icon: Info, color: 'text-primary', label: 'Non-Full Game' },
            }
            
            const config = statusConfig[trackingStatus.status as keyof typeof statusConfig] || statusConfig.partial
            const Icon = config.icon
            
            return (
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-xs">
                  <Icon className={cn('w-3 h-3', config.color)} />
                  <span className={cn('font-mono', config.color)}>{config.label}</span>
                </div>
                {trackingStatus.coverage && (
                  <div className="text-xs font-mono text-muted-foreground ml-5">
                    {trackingStatus.coverage}
                  </div>
                )}
                {trackingStatus.missing && trackingStatus.missing.length > 0 && (
                  <div className="text-xs font-mono text-muted-foreground ml-5">
                    Missing: {trackingStatus.missing.join(', ')}
                  </div>
                )}
              </div>
            )
          })()}
        </div>
      </div>
    </div>
  )
}
