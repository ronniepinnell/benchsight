import { createClient } from '@/lib/supabase/server'
import { GamesTicker } from './games-ticker'

function groupGamesByDate(games: any[]) {
  const grouped = new Map<string, any[]>()
  games.forEach(game => {
    const date = game.date ? new Date(game.date).toISOString().split('T')[0] : 'unknown'
    if (!grouped.has(date)) grouped.set(date, [])
    grouped.get(date)!.push(game)
  })
  return grouped
}

export async function GamesTickerWrapper() {
  const supabase = await createClient()
  const today = new Date().toISOString().split('T')[0]

  // Fetch recent and upcoming games
  const [recentResult, upcomingResult, teamsResult, videosResult] = await Promise.all([
    supabase
      .from('dim_schedule')
      .select('game_id, date, game_time, home_team_id, away_team_id, home_team_name, away_team_name, home_total_goals, away_total_goals')
      .eq('schedule_type', 'Past')
      .order('date', { ascending: false })
      .limit(20),
    supabase
      .from('dim_schedule')
      .select('game_id, date, game_time, home_team_id, away_team_id, home_team_name, away_team_name')
      .eq('schedule_type', 'Upcoming')
      .order('date', { ascending: true })
      .limit(15),
    supabase
      .from('dim_team')
      .select('team_id, team_name, team_cd, team_logo, team_color1, team_color2'),
    supabase
      .from('fact_video')
      .select('game_id')
  ])

  const recentGames = recentResult.data || []
  const upcomingGames = upcomingResult.data || []
  const teams = teamsResult.data || []
  const videos = videosResult.data || []

  // Create maps
  const teamsMap = new Map(teams.map(t => [String(t.team_id), t]))
  const teamsByName = new Map(teams.map(t => [t.team_name, t]))
  const gamesWithVideos = new Set(videos.map(v => String(v.game_id)))

  // Combine games for ticker
  const pastForTicker = recentGames.slice(0, 15).reverse()
  const upcomingForTicker = upcomingGames.slice(0, 10)
  const allGamesForTicker = [...pastForTicker, ...upcomingForTicker]
  const gamesByDate = groupGamesByDate(allGamesForTicker)
  const sortedDates = Array.from(gamesByDate.keys()).sort((a, b) => new Date(a).getTime() - new Date(b).getTime())

  // Convert to serializable format
  const teamsMapObj = Object.fromEntries(teamsMap)
  const teamsByNameObj = Object.fromEntries(teamsByName)
  const gamesWithVideosArr = Array.from(gamesWithVideos)
  const gamesByDateArr = Array.from(gamesByDate.entries())

  return (
    <GamesTicker
      gamesByDate={new Map(gamesByDateArr)}
      sortedDates={sortedDates}
      today={today}
      teamsMap={new Map(Object.entries(teamsMapObj))}
      teamsByName={new Map(Object.entries(teamsByNameObj))}
      gamesWithVideos={new Set(gamesWithVideosArr)}
    />
  )
}
