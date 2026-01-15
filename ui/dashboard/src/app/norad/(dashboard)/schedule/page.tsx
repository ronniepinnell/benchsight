// src/app/(dashboard)/schedule/page.tsx
import Link from 'next/link'
import { getUpcomingSchedule, getRecentGames } from '@/lib/supabase/queries/games'
import { getTeamById } from '@/lib/supabase/queries/teams'
import { createClient } from '@/lib/supabase/server'
import { Calendar, Clock, ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'
import { TeamLogo } from '@/components/teams/team-logo'
import { MatchupPredictor } from '@/components/games/matchup-predictor'

export const revalidate = 300

export const metadata = {
  title: 'Schedule | BenchSight',
  description: 'NORAD Hockey League game schedule',
}

export default async function SchedulePage() {
  const supabase = await createClient()
  
  const [upcoming, recent] = await Promise.all([
    getUpcomingSchedule(10),
    getRecentGames(10)
  ])
  
  // Get unique team IDs for logos
  const allTeamIds = [...new Set([
    ...upcoming.flatMap(g => [
      g.home_team_id ? String(g.home_team_id) : null,
      g.away_team_id ? String(g.away_team_id) : null
    ]),
    ...recent.flatMap(g => [
      g.home_team_id ? String(g.home_team_id) : null,
      g.away_team_id ? String(g.away_team_id) : null
    ])
  ].filter(Boolean))]
  
  const teams = await Promise.all(
    allTeamIds.map(id => getTeamById(id).catch(() => null))
  )
  const teamsMap = new Map(
    teams.filter(Boolean).map(t => [String(t!.team_id), t!])
  )
  
  // Get team stats for matchup predictions
  const teamStatsPromises = allTeamIds.map(async (teamId) => {
    const team = teamsMap.get(teamId)
    if (!team) return null
    
    // Get season stats
    const { data: seasonStats, error: seasonStatsError } = await supabase
      .from('fact_team_season_stats_basic')
      .select('wins, losses, ties, goals_for, goals_against, games_played')
      .eq('team_id', teamId)
      .order('season', { ascending: false })
      .limit(1)
      .maybeSingle()
    
    // Get advanced stats
    const { data: advancedStats, error: advancedStatsError } = await supabase
      .from('fact_team_game_stats')
      .select('corsi_for, corsi_against, fenwick_for, fenwick_against')
      .eq('team_id', teamId)
      .limit(20)
    
    // Calculate aggregates
    const advStats = advancedStats || []
    const totals = advStats.reduce((acc, stat) => ({
      cf: (acc.cf || 0) + (Number(stat.corsi_for ?? stat.cf ?? 0) || 0),
      ca: (acc.ca || 0) + (Number(stat.corsi_against ?? stat.ca ?? 0) || 0),
      ff: (acc.ff || 0) + (Number(stat.fenwick_for ?? stat.ff ?? 0) || 0),
      fa: (acc.fa || 0) + (Number(stat.fenwick_against ?? stat.fa ?? 0) || 0),
      games: acc.games + 1,
    }), { cf: 0, ca: 0, ff: 0, fa: 0, games: 0 })
    
    const cfPct = totals.cf + totals.ca > 0 ? (totals.cf / (totals.cf + totals.ca)) * 100 : null
    const ffPct = totals.ff + totals.fa > 0 ? (totals.ff / (totals.ff + totals.fa)) * 100 : null
    
    const stats = seasonStats
    const wins = stats?.wins || 0
    const losses = stats?.losses || 0
    const ties = stats?.ties || 0
    const gamesPlayed = stats?.games_played || (wins + losses + ties)
    const points = wins * 2 + ties
    const winPct = gamesPlayed > 0 ? (points / (gamesPlayed * 2)) * 100 : null
    
    return {
      team_id: teamId,
      team_name: team.team_name,
      team_logo: team.team_logo,
      team_cd: team.team_cd,
      primary_color: team.primary_color,
      team_color1: team.team_color1,
      team_color2: team.team_color2,
      winPct: winPct || undefined,
      goalsFor: stats?.goals_for || undefined,
      goalsAgainst: stats?.goals_against || undefined,
      cfPct: cfPct || undefined,
      ffPct: ffPct || undefined,
    }
  })
  
  const teamStatsList = await Promise.all(teamStatsPromises)
  const teamStatsMap = new Map(
    teamStatsList.filter(Boolean).map(t => [t!.team_id, t!])
  )
  
  // Get head-to-head history for upcoming games
  const h2hPromises = upcoming.map(async (game) => {
    if (!game.home_team_id || !game.away_team_id) return { gameId: game.game_id, h2h: null }
    
    const { data: h2hGames, error: h2hError } = await supabase
      .from('dim_schedule')
      .select('home_team_id, away_team_id, home_total_goals, away_total_goals')
      .or(`and(home_team_id.eq.${game.home_team_id},away_team_id.eq.${game.away_team_id}),and(home_team_id.eq.${game.away_team_id},away_team_id.eq.${game.home_team_id})`)
      .not('home_total_goals', 'is', null)
      .limit(20)
    
    if (!h2hGames || h2hGames.length === 0) {
      return { gameId: game.game_id, h2h: null }
    }
    
    const h2h = h2hGames.reduce((acc, g) => {
      const isHome = String(g.home_team_id) === String(game.home_team_id)
      const homeGoals = Number(g.home_total_goals || 0)
      const awayGoals = Number(g.away_total_goals || 0)
      
      if (isHome) {
        if (homeGoals > awayGoals) acc.homeWins++
        else if (awayGoals > homeGoals) acc.awayWins++
        else acc.ties++
      } else {
        if (awayGoals > homeGoals) acc.homeWins++
        else if (homeGoals > awayGoals) acc.awayWins++
        else acc.ties++
      }
      
      acc.totalHomeGoals += homeGoals
      acc.totalAwayGoals += awayGoals
      acc.totalGames++
      
      return acc
    }, { homeWins: 0, awayWins: 0, ties: 0, totalHomeGoals: 0, totalAwayGoals: 0, totalGames: 0 })
    
    return {
      gameId: game.game_id,
      h2h: h2h.totalGames > 0 ? {
        homeWins: h2h.homeWins,
        awayWins: h2h.awayWins,
        ties: h2h.ties,
        totalGames: h2h.totalGames,
        avgHomeGoals: h2h.totalGames > 0 ? h2h.totalHomeGoals / h2h.totalGames : 0,
        avgAwayGoals: h2h.totalGames > 0 ? h2h.totalAwayGoals / h2h.totalGames : 0,
      } : null
    }
  })
  
  const h2hResults = await Promise.all(h2hPromises)
  const h2hMap = new Map(h2hResults.map(r => [r.gameId, r.h2h]))
  
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="font-display text-2xl font-bold tracking-wider uppercase flex items-center gap-3">
          <span className="w-1 h-6 bg-primary rounded" />
          Schedule
        </h1>
        <p className="text-sm text-muted-foreground mt-2 ml-4">
          Upcoming games and recent results
        </p>
      </div>
      
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Upcoming Games */}
        <div className="space-y-6">
          <div className="bg-card rounded-xl border border-border overflow-hidden">
            <div className="px-4 py-3 bg-accent border-b border-border">
              <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                <Clock className="w-4 h-4 text-primary" />
                Upcoming Games
              </h2>
            </div>
            <div className="divide-y divide-border">
              {upcoming.length > 0 ? (
                upcoming.map((game) => {
                  const gameDate = new Date(game.date).toLocaleDateString('en-US', {
                    weekday: 'short',
                    month: 'short',
                    day: 'numeric',
                  })
                  const gameTime = game.time ?? 'TBD'
                  
                  const homeTeamStats = game.home_team_id ? teamStatsMap.get(String(game.home_team_id)) : null
                  const awayTeamStats = game.away_team_id ? teamStatsMap.get(String(game.away_team_id)) : null
                  const h2h = h2hMap.get(game.game_id) || null
                  
                  return (
                    <div key={game.game_id} className="p-4 hover:bg-muted/50 transition-colors space-y-3">
                      <div className="flex items-center gap-2 mb-2">
                        <Calendar className="w-4 h-4 text-muted-foreground" />
                        <span className="text-xs font-mono text-muted-foreground uppercase">
                          {gameDate} • {gameTime}
                        </span>
                      </div>
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
                          <div>
                            <Link 
                              href={`/norad/team/${game.away_team_name?.replace(/\s+/g, '_') || '#'}`}
                              className="font-display text-sm text-foreground hover:text-primary transition-colors"
                            >
                              {game.away_team_name}
                            </Link>
                            <div className="font-display text-sm text-muted-foreground">
                              @{' '}
                              <Link 
                                href={`/norad/team/${game.home_team_name?.replace(/\s+/g, '_') || '#'}`}
                                className="hover:text-foreground transition-colors"
                              >
                                {game.home_team_name}
                              </Link>
                            </div>
                          </div>
                        </div>
                        <span className="text-xs font-mono text-primary uppercase bg-primary/10 px-2 py-1 rounded">
                          Upcoming
                        </span>
                      </div>
                      
                      {/* Matchup Predictor for this game */}
                      {homeTeamStats && awayTeamStats && (
                        <div className="pt-3 border-t border-border">
                          <MatchupPredictor
                            homeTeam={homeTeamStats}
                            awayTeam={awayTeamStats}
                            h2hHistory={h2h || undefined}
                            isHomeGame={true}
                          />
                        </div>
                      )}
                    </div>
                  )
                })
              ) : (
                <div className="p-8 text-center text-muted-foreground">
                  No upcoming games scheduled.
                </div>
              )}
            </div>
          </div>
        </div>
        
        {/* Recent Results */}
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Calendar className="w-4 h-4 text-save" />
              Recent Results
            </h2>
          </div>
          {recent.length > 0 ? (
            <div className="divide-y divide-border">
              {recent.map((game) => {
              const homeWon = game.home_total_goals > game.away_total_goals
              const awayWon = game.away_total_goals > game.home_total_goals
              const gameDate = new Date(game.date).toLocaleDateString('en-US', {
                weekday: 'short',
                month: 'short',
                day: 'numeric',
              })
              
              return (
                <Link
                  key={game.game_id}
                  href={`/norad/games/${game.game_id}`}
                  className="block p-4 hover:bg-muted/50 transition-colors group"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <Calendar className="w-4 h-4 text-muted-foreground" />
                    <span className="text-xs font-mono text-muted-foreground uppercase">
                      {gameDate}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex-1 space-y-1">
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
                            href={`/team/${game.away_team_name?.replace(/\s+/g, '_') || '#'}`}
                            className={cn(
                              'font-display text-sm hover:text-primary transition-colors',
                              awayWon ? 'text-foreground font-semibold' : 'text-muted-foreground'
                            )}
                          >
                            {game.away_team_name}
                          </Link>
                        </div>
                        <span className={cn(
                          'font-mono font-bold',
                          awayWon ? 'text-save' : 'text-muted-foreground'
                        )}>
                          {game.away_total_goals}
                        </span>
                      </div>
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
                              href={`/team/${game.home_team_name?.replace(/\s+/g, '_') || '#'}`}
                              className="hover:text-foreground transition-colors"
                            >
                              {game.home_team_name}
                            </Link>
                          </span>
                        </div>
                        <span className={cn(
                          'font-mono font-bold',
                          homeWon ? 'text-save' : 'text-muted-foreground'
                        )}>
                          {game.home_total_goals}
                        </span>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-muted-foreground ml-4 group-hover:text-primary transition-colors" />
                  </div>
                </Link>
              )
              })}
            </div>
          ) : (
            <div className="p-8 text-center">
              <p className="text-muted-foreground text-sm">No recent games found.</p>
            </div>
          )}
          {recent.length > 0 && (
            <div className="px-4 py-3 bg-accent/50 border-t border-border">
              <Link 
                href="/norad/games" 
                className="text-xs font-mono text-primary hover:underline"
              >
                View all games →
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
