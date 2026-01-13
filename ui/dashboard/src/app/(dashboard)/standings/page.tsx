// src/app/(dashboard)/standings/page.tsx
import { createClient } from '@/lib/supabase/server'
import { getStandings, getTeams } from '@/lib/supabase/queries/teams'
import { getLeagueSummary, getCurrentSeason } from '@/lib/supabase/queries/league'
import { Trophy, Target, Users, Calendar } from 'lucide-react'
import { SortableStandingsTable } from '@/components/teams/sortable-standings-table'

export const revalidate = 300

export const metadata = {
  title: 'Standings | BenchSight',
  description: 'NORAD Hockey League standings',
}

export default async function StandingsPage() {
  const supabase = await createClient()
  const currentSeason = await getCurrentSeason()
  
  const [standings, leagueSummary, teams, scheduleGamesResult] = await Promise.all([
    getStandings(),
    getLeagueSummary(),
    getTeams(),
    // Get all games from dim_schedule for current season with team IDs for proper matching
    currentSeason
      ? supabase.from('dim_schedule').select('*').eq('season_id', currentSeason).not('home_total_goals', 'is', null).not('away_total_goals', 'is', null).order('date', { ascending: false })
      : supabase.from('dim_schedule').select('*').not('home_total_goals', 'is', null).not('away_total_goals', 'is', null).order('date', { ascending: false }).limit(1000)
  ])

  // Create team lookup maps - by ID and by name (for fallback)
  const teamsMap = new Map(teams.map(t => [String(t.team_id), t]))
  const teamsByNameMap = new Map(teams.map(t => [t.team_name, t]))
  const allGames = scheduleGamesResult.data || []
  
  // Log for debugging (remove in production)
  if (scheduleGamesResult.error) {
    console.error('Error fetching games:', scheduleGamesResult.error)
  }

  // Group games by team_id AND team_name for maximum compatibility
  const gamesByTeamId = new Map<string, any[]>()
  const gamesByTeamName = new Map<string, any[]>()
  
  allGames.forEach(game => {
    const homeTeamId = String(game.home_team_id || '')
    const awayTeamId = String(game.away_team_id || '')
    const homeTeamName = game.home_team_name || ''
    const awayTeamName = game.away_team_name || ''
    
    // Group by team_id
    if (homeTeamId && homeTeamId !== '') {
      if (!gamesByTeamId.has(homeTeamId)) {
        gamesByTeamId.set(homeTeamId, [])
      }
      gamesByTeamId.get(homeTeamId)!.push({ 
        ...game, 
        isHome: true,
        home_total_goals: Number(game.home_total_goals) || 0,
        away_total_goals: Number(game.away_total_goals) || 0
      })
    }
    if (awayTeamId && awayTeamId !== '') {
      if (!gamesByTeamId.has(awayTeamId)) {
        gamesByTeamId.set(awayTeamId, [])
      }
      gamesByTeamId.get(awayTeamId)!.push({ 
        ...game, 
        isHome: false,
        home_total_goals: Number(game.home_total_goals) || 0,
        away_total_goals: Number(game.away_total_goals) || 0
      })
    }
    
    // Also group by team_name as fallback
    if (homeTeamName) {
      if (!gamesByTeamName.has(homeTeamName)) {
        gamesByTeamName.set(homeTeamName, [])
      }
      gamesByTeamName.get(homeTeamName)!.push({ 
        ...game, 
        isHome: true,
        home_total_goals: Number(game.home_total_goals) || 0,
        away_total_goals: Number(game.away_total_goals) || 0
      })
    }
    if (awayTeamName) {
      if (!gamesByTeamName.has(awayTeamName)) {
        gamesByTeamName.set(awayTeamName, [])
      }
      gamesByTeamName.get(awayTeamName)!.push({ 
        ...game, 
        isHome: false,
        home_total_goals: Number(game.home_total_goals) || 0,
        away_total_goals: Number(game.away_total_goals) || 0
      })
    }
  })

  // Calculate streak and last 10 for each team
  const standingsWithStats = standings.map((team) => {
    const teamInfo = teamsMap.get(String(team.team_id))
    
    // Try to get games by team_id first, then fallback to team_name
    let teamGames = gamesByTeamId.get(String(team.team_id)) || []
    if (teamGames.length === 0) {
      // Fallback to team_name matching
      teamGames = gamesByTeamName.get(team.team_name) || []
    }
    
    // Filter to games with valid scores and get last 10 (most recent first)
    teamGames = teamGames
      .filter(g => {
        const homeGoals = Number(g.home_total_goals)
        const awayGoals = Number(g.away_total_goals)
        return !isNaN(homeGoals) && !isNaN(awayGoals) && homeGoals !== null && awayGoals !== null && homeGoals >= 0 && awayGoals >= 0
      })
      .sort((a, b) => {
        // Sort by date descending (most recent first)
        const dateA = new Date(a.date || a.game_date || 0).getTime()
        const dateB = new Date(b.date || b.game_date || 0).getTime()
        return dateB - dateA
      })
      .slice(0, 10)
    
    // Calculate last 10 record (W-L-T)
    const last10Wins = teamGames.filter(g => {
      const homeGoals = Number(g.home_total_goals) || 0
      const awayGoals = Number(g.away_total_goals) || 0
      if (g.isHome) {
        return homeGoals > awayGoals
      } else {
        return awayGoals > homeGoals
      }
    }).length
    const last10Losses = teamGames.filter(g => {
      const homeGoals = Number(g.home_total_goals) || 0
      const awayGoals = Number(g.away_total_goals) || 0
      if (g.isHome) {
        return homeGoals < awayGoals
      } else {
        return awayGoals < homeGoals
      }
    }).length
    const last10Ties = teamGames.filter(g => {
      const homeGoals = Number(g.home_total_goals) || 0
      const awayGoals = Number(g.away_total_goals) || 0
      return homeGoals === awayGoals
    }).length
    const last10 = teamGames.length > 0 ? `${last10Wins}-${last10Losses}-${last10Ties}` : '-'

    // Calculate streak (including ties)
    let streak = '-'
    if (teamGames.length > 0) {
      let streakCount = 0
      let streakType: 'W' | 'L' | 'T' | null = null
      
      for (const game of teamGames) {
        const homeGoals = Number(game.home_total_goals) || 0
        const awayGoals = Number(game.away_total_goals) || 0
        const isWin = game.isHome ? homeGoals > awayGoals : awayGoals > homeGoals
        const isTie = homeGoals === awayGoals
        
        let currentType: 'W' | 'L' | 'T'
        if (isTie) {
          currentType = 'T'
        } else {
          currentType = isWin ? 'W' : 'L'
        }
        
        if (streakType === null) {
          streakType = currentType
          streakCount = 1
        } else if (streakType === currentType) {
          streakCount++
        } else {
          break
        }
      }
      
      if (streakCount > 0 && streakType) {
        streak = `${streakType}${streakCount}`
      }
    }

    return {
      ...team,
      teamInfo,
      last_10: last10,
      streak,
    }
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold tracking-wider uppercase flex items-center gap-3">
          <span className="w-1 h-6 bg-primary rounded" />
          League Standings
        </h1>
        <p className="text-sm text-muted-foreground mt-2 ml-4">Current season team rankings</p>
      </div>

      {leagueSummary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-card rounded-lg p-4 border border-border">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="w-4 h-4 text-primary" />
              <span className="text-xs font-mono text-muted-foreground uppercase">Games</span>
            </div>
            <div className="font-mono text-2xl font-bold text-foreground">{leagueSummary.total_games}</div>
          </div>
          <div className="bg-card rounded-lg p-4 border border-border">
            <div className="flex items-center gap-2 mb-2">
              <Target className="w-4 h-4 text-goal" />
              <span className="text-xs font-mono text-muted-foreground uppercase">Goals</span>
            </div>
            <div className="font-mono text-2xl font-bold text-goal">{leagueSummary.total_goals}</div>
          </div>
          <div className="bg-card rounded-lg p-4 border border-border">
            <div className="flex items-center gap-2 mb-2">
              <Trophy className="w-4 h-4 text-assist" />
              <span className="text-xs font-mono text-muted-foreground uppercase">Teams</span>
            </div>
            <div className="font-mono text-2xl font-bold text-foreground">{leagueSummary.total_teams}</div>
          </div>
          <div className="bg-card rounded-lg p-4 border border-border">
            <div className="flex items-center gap-2 mb-2">
              <Users className="w-4 h-4 text-shot" />
              <span className="text-xs font-mono text-muted-foreground uppercase">Players</span>
            </div>
            <div className="font-mono text-2xl font-bold text-foreground">{leagueSummary.total_players}</div>
          </div>
        </div>
      )}

      <SortableStandingsTable standings={standingsWithStats} />
    </div>
  )
}
