'use client'

import Link from 'next/link'
import { Calendar, Clock, Target, TrendingUp, Users, Zap, Shield, BarChart3, Play, Award } from 'lucide-react'
import { cn } from '@/lib/utils'
import { TeamLogo } from '@/components/teams/team-logo'
import { PlayerPhoto } from '@/components/players/player-photo'

interface GameSummaryProps {
  game: {
    game_id: number
    date?: string
    home_team_name?: string
    away_team_name?: string
    home_team_id?: string
    away_team_id?: string
    home_total_goals?: number
    away_total_goals?: number
    official_home_goals?: number
    official_away_goals?: number
    season?: string
    venue?: string
  }
  homeTeam?: {
    team_id?: string
    team_name?: string
    team_logo?: string
    team_cd?: string
    primary_color?: string
    team_color1?: string
    team_color2?: string
  }
  awayTeam?: {
    team_id?: string
    team_name?: string
    team_logo?: string
    team_cd?: string
    primary_color?: string
    team_color1?: string
    team_color2?: string
  }
  topPerformers?: {
    home: Array<{ player_id: string, player_name: string, goals: number, assists: number, points: number }>
    away: Array<{ player_id: string, player_name: string, goals: number, assists: number, points: number }>
  }
  gameStats?: {
    home: {
      shots?: number
      sog?: number
      hits?: number
      blocks?: number
      giveaways?: number
      takeaways?: number
      pim?: number
      pp_goals?: number
      pp_opportunities?: number
    }
    away: {
      shots?: number
      sog?: number
      hits?: number
      blocks?: number
      giveaways?: number
      takeaways?: number
      pim?: number
      pp_goals?: number
      pp_opportunities?: number
    }
  }
}

export function GameSummary({
  game,
  homeTeam,
  awayTeam,
  topPerformers,
  gameStats
}: GameSummaryProps) {
  const homeGoals = game.official_home_goals ?? game.home_total_goals ?? 0
  const awayGoals = game.official_away_goals ?? game.away_total_goals ?? 0
  const homeWon = homeGoals > awayGoals
  const awayWon = awayGoals > homeGoals
  const isOT = (homeGoals !== awayGoals) && Math.abs(homeGoals - awayGoals) === 1
  
  const gameDate = game.date ? new Date(game.date).toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric'
  }) : 'Date TBD'
  
  const totalGoals = homeGoals + awayGoals
  const goalDiff = Math.abs(homeGoals - awayGoals)
  
  // Calculate PP%
  const homePP = gameStats?.home.pp_opportunities && gameStats.home.pp_opportunities > 0
    ? ((gameStats.home.pp_goals || 0) / gameStats.home.pp_opportunities * 100).toFixed(0)
    : null
  const awayPP = gameStats?.away.pp_opportunities && gameStats.away.pp_opportunities > 0
    ? ((gameStats.away.pp_goals || 0) / gameStats.away.pp_opportunities * 100).toFixed(0)
    : null
  
  return (
    <div className="bg-card rounded-xl border border-border overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary/10 via-transparent to-primary/10 px-6 py-4 border-b border-border">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 text-muted-foreground" />
            <span className="text-xs font-mono text-muted-foreground uppercase">{gameDate}</span>
          </div>
          {game.venue && (
            <span className="text-xs text-muted-foreground">{game.venue}</span>
          )}
        </div>
        
        {/* Score Box */}
        <div className="flex items-center justify-between py-4">
          {/* Away Team */}
          <div className="flex items-center gap-3 flex-1">
            {awayTeam && (
              <TeamLogo
                src={awayTeam.team_logo || null}
                name={awayTeam.team_name || game.away_team_name || ''}
                abbrev={awayTeam.team_cd}
                primaryColor={awayTeam.primary_color || awayTeam.team_color1}
                secondaryColor={awayTeam.team_color2}
                size="md"
              />
            )}
            <div className="flex-1">
              <Link
                href={awayTeam ? `/team/${(awayTeam.team_name || game.away_team_name || '').replace(/\s+/g, '_')}` : '#'}
                className={cn(
                  'font-display text-lg font-bold hover:text-primary transition-colors block',
                  awayWon ? 'text-save' : 'text-foreground'
                )}
              >
                {awayTeam?.team_name || game.away_team_name || 'Away Team'}
              </Link>
            </div>
            <div className={cn(
              'font-mono text-3xl font-bold',
              awayWon ? 'text-save' : 'text-muted-foreground'
            )}>
              {awayGoals}
            </div>
          </div>
          
          {/* VS Separator */}
          <div className="px-4">
            <span className="text-muted-foreground font-display">@</span>
          </div>
          
          {/* Home Team */}
          <div className="flex items-center gap-3 flex-1 justify-end">
            <div className={cn(
              'font-mono text-3xl font-bold',
              homeWon ? 'text-save' : 'text-muted-foreground'
            )}>
              {homeGoals}
            </div>
            <div className="flex-1 text-right">
              <Link
                href={homeTeam ? `/team/${(homeTeam.team_name || game.home_team_name || '').replace(/\s+/g, '_')}` : '#'}
                className={cn(
                  'font-display text-lg font-bold hover:text-primary transition-colors block',
                  homeWon ? 'text-save' : 'text-foreground'
                )}
              >
                {homeTeam?.team_name || game.home_team_name || 'Home Team'}
              </Link>
            </div>
            {homeTeam && (
              <TeamLogo
                src={homeTeam.team_logo || null}
                name={homeTeam.team_name || game.home_team_name || ''}
                abbrev={homeTeam.team_cd}
                primaryColor={homeTeam.primary_color || homeTeam.team_color1}
                secondaryColor={homeTeam.team_color2}
                size="md"
              />
            )}
          </div>
        </div>
        
        {/* Game Result Summary */}
        <div className="flex items-center gap-4 text-xs text-muted-foreground mt-2">
          <span className={cn(
            'font-semibold uppercase',
            homeWon ? 'text-save' : awayWon ? 'text-save' : 'text-muted-foreground'
          )}>
            {homeWon ? `${homeTeam?.team_name || game.home_team_name} Wins` : 
             awayWon ? `${awayTeam?.team_name || game.away_team_name} Wins` : 
             'Tie'}
          </span>
          {goalDiff > 0 && (
            <span>• {goalDiff} goal{goalDiff > 1 ? 's' : ''} difference</span>
          )}
          {isOT && (
            <span className="text-primary">• Overtime</span>
          )}
          {totalGoals >= 10 && (
            <span className="text-goal">• High Scoring Game</span>
          )}
        </div>
      </div>
      
      {/* Detailed Stats */}
      <div className="p-6 space-y-6">
        {/* Team Stats Comparison */}
        {gameStats && (
          <div className="grid md:grid-cols-2 gap-6">
            {/* Home Team Stats */}
            <div className="space-y-3">
              <h3 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                {homeTeam && (
                  <TeamLogo
                    src={homeTeam.team_logo || null}
                    name={homeTeam.team_name || ''}
                    abbrev={homeTeam.team_cd}
                    primaryColor={homeTeam.primary_color || homeTeam.team_color1}
                    secondaryColor={homeTeam.team_color2}
                    size="xs"
                  />
                )}
                {homeTeam?.team_name || game.home_team_name} Stats
              </h3>
              <div className="grid grid-cols-3 gap-3">
                {gameStats.home.shots !== undefined && (
                  <div className="bg-muted/30 rounded p-2 text-center">
                    <div className="text-[10px] font-mono text-muted-foreground uppercase">Shots</div>
                    <div className="font-mono text-lg font-bold text-foreground">{gameStats.home.shots}</div>
                  </div>
                )}
                {gameStats.home.sog !== undefined && (
                  <div className="bg-muted/30 rounded p-2 text-center">
                    <div className="text-[10px] font-mono text-muted-foreground uppercase">SOG</div>
                    <div className={cn(
                      "font-mono text-lg font-bold",
                      gameStats.away?.sog !== undefined && gameStats.home.sog > gameStats.away.sog ? 'text-save' : 'text-primary'
                    )}>
                      {gameStats.home.sog}
                    </div>
                  </div>
                )}
                {gameStats.home.hits !== undefined && (
                  <div className="bg-muted/30 rounded p-2 text-center">
                    <div className="text-[10px] font-mono text-muted-foreground uppercase">Hits</div>
                    <div className={cn(
                      "font-mono text-lg font-bold",
                      gameStats.away?.hits !== undefined && gameStats.home.hits > gameStats.away.hits ? 'text-save' : 'text-foreground'
                    )}>
                      {gameStats.home.hits}
                    </div>
                  </div>
                )}
                {gameStats.home.blocks !== undefined && (
                  <div className="bg-muted/30 rounded p-2 text-center">
                    <div className="text-[10px] font-mono text-muted-foreground uppercase">Blocks</div>
                    <div className={cn(
                      "font-mono text-lg font-bold",
                      gameStats.away?.blocks !== undefined && gameStats.home.blocks > gameStats.away.blocks ? 'text-save' : 'text-save'
                    )}>
                      {gameStats.home.blocks}
                    </div>
                  </div>
                )}
                {gameStats.home.takeaways !== undefined && (
                  <div className="bg-muted/30 rounded p-2 text-center">
                    <div className="text-[10px] font-mono text-muted-foreground uppercase">Takeaways</div>
                    <div className={cn(
                      "font-mono text-sm font-bold",
                      gameStats.away?.takeaways !== undefined && gameStats.home.takeaways > gameStats.away.takeaways ? 'text-save' : 'text-foreground'
                    )}>
                      {gameStats.home.takeaways}
                    </div>
                  </div>
                )}
                {gameStats.home.giveaways !== undefined && (
                  <div className="bg-muted/30 rounded p-2 text-center">
                    <div className="text-[10px] font-mono text-muted-foreground uppercase">Giveaways</div>
                    <div className={cn(
                      "font-mono text-sm font-bold",
                      gameStats.away?.giveaways !== undefined && gameStats.home.giveaways < gameStats.away.giveaways ? 'text-save' : 'text-goal'
                    )}>
                      {gameStats.home.giveaways}
                    </div>
                  </div>
                )}
                {gameStats.home.pim !== undefined && (
                  <div className="bg-muted/30 rounded p-2 text-center">
                    <div className="text-[10px] font-mono text-muted-foreground uppercase">PIM</div>
                    <div className="font-mono text-sm font-bold text-goal">{gameStats.home.pim}</div>
                  </div>
                )}
                {gameStats.home.pp_opportunities !== undefined && gameStats.home.pp_opportunities > 0 && (
                  <div className="bg-muted/30 rounded p-2 text-center col-span-3">
                    <div className="text-[10px] font-mono text-muted-foreground uppercase">Power Play</div>
                    <div className={cn(
                      "font-mono text-sm font-bold",
                      awayPP !== null && homePP && awayPP && Number(homePP) > Number(awayPP) ? 'text-save' : 'text-primary'
                    )}>
                      {gameStats.home.pp_goals || 0}/{gameStats.home.pp_opportunities} ({homePP}%)
                    </div>
                  </div>
                )}
              </div>
            </div>
            
            {/* Away Team Stats */}
            <div className="space-y-3">
              <h3 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                {awayTeam && (
                  <TeamLogo
                    src={awayTeam.team_logo || null}
                    name={awayTeam.team_name || ''}
                    abbrev={awayTeam.team_cd}
                    primaryColor={awayTeam.primary_color || awayTeam.team_color1}
                    secondaryColor={awayTeam.team_color2}
                    size="xs"
                  />
                )}
                {awayTeam?.team_name || game.away_team_name} Stats
              </h3>
              <div className="grid grid-cols-3 gap-3">
                {gameStats.away.shots !== undefined && (
                  <div className="bg-muted/30 rounded p-2 text-center">
                    <div className="text-[10px] font-mono text-muted-foreground uppercase">Shots</div>
                    <div className="font-mono text-lg font-bold text-foreground">{gameStats.away.shots}</div>
                  </div>
                )}
                {gameStats.away.sog !== undefined && (
                  <div className="bg-muted/30 rounded p-2 text-center">
                    <div className="text-[10px] font-mono text-muted-foreground uppercase">SOG</div>
                    <div className={cn(
                      "font-mono text-lg font-bold",
                      gameStats.home?.sog !== undefined && gameStats.away.sog > gameStats.home.sog ? 'text-save' : 'text-primary'
                    )}>
                      {gameStats.away.sog}
                    </div>
                  </div>
                )}
                {gameStats.away.hits !== undefined && (
                  <div className="bg-muted/30 rounded p-2 text-center">
                    <div className="text-[10px] font-mono text-muted-foreground uppercase">Hits</div>
                    <div className={cn(
                      "font-mono text-lg font-bold",
                      gameStats.home?.hits !== undefined && gameStats.away.hits > gameStats.home.hits ? 'text-save' : 'text-foreground'
                    )}>
                      {gameStats.away.hits}
                    </div>
                  </div>
                )}
                {gameStats.away.blocks !== undefined && (
                  <div className="bg-muted/30 rounded p-2 text-center">
                    <div className="text-[10px] font-mono text-muted-foreground uppercase">Blocks</div>
                    <div className={cn(
                      "font-mono text-lg font-bold",
                      gameStats.home?.blocks !== undefined && gameStats.away.blocks > gameStats.home.blocks ? 'text-save' : 'text-save'
                    )}>
                      {gameStats.away.blocks}
                    </div>
                  </div>
                )}
                {gameStats.away.takeaways !== undefined && (
                  <div className="bg-muted/30 rounded p-2 text-center">
                    <div className="text-[10px] font-mono text-muted-foreground uppercase">Takeaways</div>
                    <div className={cn(
                      "font-mono text-sm font-bold",
                      gameStats.home?.takeaways !== undefined && gameStats.away.takeaways > gameStats.home.takeaways ? 'text-save' : 'text-foreground'
                    )}>
                      {gameStats.away.takeaways}
                    </div>
                  </div>
                )}
                {gameStats.away.giveaways !== undefined && (
                  <div className="bg-muted/30 rounded p-2 text-center">
                    <div className="text-[10px] font-mono text-muted-foreground uppercase">Giveaways</div>
                    <div className={cn(
                      "font-mono text-sm font-bold",
                      gameStats.home?.giveaways !== undefined && gameStats.away.giveaways < gameStats.home.giveaways ? 'text-save' : 'text-goal'
                    )}>
                      {gameStats.away.giveaways}
                    </div>
                  </div>
                )}
                {gameStats.away.pim !== undefined && (
                  <div className="bg-muted/30 rounded p-2 text-center">
                    <div className="text-[10px] font-mono text-muted-foreground uppercase">PIM</div>
                    <div className="font-mono text-sm font-bold text-goal">{gameStats.away.pim}</div>
                  </div>
                )}
                {gameStats.away.pp_opportunities !== undefined && gameStats.away.pp_opportunities > 0 && (
                  <div className="bg-muted/30 rounded p-2 text-center col-span-3">
                    <div className="text-[10px] font-mono text-muted-foreground uppercase">Power Play</div>
                    <div className={cn(
                      "font-mono text-sm font-bold",
                      homePP !== null && awayPP && homePP && Number(awayPP) > Number(homePP) ? 'text-save' : 'text-primary'
                    )}>
                      {gameStats.away.pp_goals || 0}/{gameStats.away.pp_opportunities} ({awayPP}%)
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
        
        {/* Game Highlights Summary */}
        <div className="border-t border-border pt-4">
          <div className="flex items-center justify-between flex-wrap gap-4 text-xs">
            {totalGoals > 0 && (
              <div className="flex items-center gap-2">
                <Target className="w-4 h-4 text-goal" />
                <span className="text-muted-foreground">Total Goals:</span>
                <span className="font-mono font-bold text-goal">{totalGoals}</span>
              </div>
            )}
            {goalDiff > 0 && (
              <div className="flex items-center gap-2">
                <TrendingUp className={cn("w-4 h-4", homeWon ? 'text-save' : 'text-save')} />
                <span className="text-muted-foreground">Margin:</span>
                <span className="font-mono font-bold">{goalDiff} goal{goalDiff > 1 ? 's' : ''}</span>
              </div>
            )}
            {gameStats?.home.shots && gameStats?.away.shots && (
              <div className="flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-primary" />
                <span className="text-muted-foreground">Total Shots:</span>
                <span className="font-mono font-bold">{(gameStats.home.shots || 0) + (gameStats.away.shots || 0)}</span>
              </div>
            )}
            {isOT && (
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-primary" />
                <span className="font-semibold text-primary uppercase">Overtime</span>
              </div>
            )}
          </div>
        </div>
        
        {/* Top Performers */}
        {topPerformers && (topPerformers.home.length > 0 || topPerformers.away.length > 0) && (
          <div className="space-y-4 border-t border-border pt-4">
            <h3 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Award className="w-4 h-4 text-primary" />
              Top Performers
            </h3>
            <div className="grid md:grid-cols-2 gap-4">
              {/* Home Top Performers */}
              {topPerformers.home.length > 0 && (
                <div>
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-2 flex items-center gap-2">
                    {homeTeam && (
                      <TeamLogo
                        src={homeTeam.team_logo || null}
                        name={homeTeam.team_name || ''}
                        abbrev={homeTeam.team_cd}
                        primaryColor={homeTeam.primary_color || homeTeam.team_color1}
                        secondaryColor={homeTeam.team_color2}
                        size="xs"
                      />
                    )}
                    {homeTeam?.team_name || game.home_team_name}
                  </div>
                  <div className="space-y-2">
                    {topPerformers.home.slice(0, 5).map((player, idx) => (
                      <Link
                        key={player.player_id}
                        href={`/players/${player.player_id}`}
                        className="flex items-center gap-3 p-2 bg-muted/20 rounded hover:bg-muted/40 transition-colors group"
                      >
                        <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/10 text-[10px] font-mono font-bold text-primary">
                          {idx + 1}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-medium text-foreground group-hover:text-primary transition-colors truncate">
                            {player.player_name}
                          </div>
                        </div>
                        <div className="flex items-center gap-2 text-xs font-mono flex-shrink-0">
                          {player.goals > 0 && (
                            <span className="text-goal font-semibold">{player.goals}G</span>
                          )}
                          {player.assists > 0 && (
                            <span className="text-assist">{player.assists}A</span>
                          )}
                          <span className="text-primary font-bold">{player.points}P</span>
                        </div>
                      </Link>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Away Top Performers */}
              {topPerformers.away.length > 0 && (
                <div>
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-2 flex items-center gap-2">
                    {awayTeam && (
                      <TeamLogo
                        src={awayTeam.team_logo || null}
                        name={awayTeam.team_name || ''}
                        abbrev={awayTeam.team_cd}
                        primaryColor={awayTeam.primary_color || awayTeam.team_color1}
                        secondaryColor={awayTeam.team_color2}
                        size="xs"
                      />
                    )}
                    {awayTeam?.team_name || game.away_team_name}
                  </div>
                  <div className="space-y-2">
                    {topPerformers.away.slice(0, 5).map((player, idx) => (
                      <Link
                        key={player.player_id}
                        href={`/players/${player.player_id}`}
                        className="flex items-center gap-3 p-2 bg-muted/20 rounded hover:bg-muted/40 transition-colors group"
                      >
                        <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/10 text-[10px] font-mono font-bold text-primary">
                          {idx + 1}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-medium text-foreground group-hover:text-primary transition-colors truncate">
                            {player.player_name}
                          </div>
                        </div>
                        <div className="flex items-center gap-2 text-xs font-mono flex-shrink-0">
                          {player.goals > 0 && (
                            <span className="text-goal font-semibold">{player.goals}G</span>
                          )}
                          {player.assists > 0 && (
                            <span className="text-assist">{player.assists}A</span>
                          )}
                          <span className="text-primary font-bold">{player.points}P</span>
                        </div>
                      </Link>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
