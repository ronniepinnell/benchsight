// src/app/norad/page.tsx
import Link from 'next/link'
import Image from 'next/image'
import { createClient } from '@/lib/supabase/server'
import { getCurrentSeason } from '@/lib/supabase/queries/league'
import { getStandings, getTeams } from '@/lib/supabase/queries/teams'
import { getPlayers } from '@/lib/supabase/queries/players'
import {
  Trophy, ChevronRight, Award, Calendar, Video,
  Flame, Snowflake, TrendingUp, TrendingDown, Play, ExternalLink,
  Users, UserCircle, BarChart3, CalendarDays,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { TeamLogo } from '@/components/teams/team-logo'
import { PlayerPhoto } from '@/components/players/player-photo'
import { GamesTicker } from '@/components/games/games-ticker'

export const revalidate = 300

export const metadata = {
  title: 'NORAD Hockey League | BenchSight',
  description: 'NORAD Hockey League analytics - standings, stats, and game results',
}

function formatGameTime(gameTime: string | null): string {
  if (!gameTime) return 'TBD'
  const [hours, minutes] = gameTime.split(':')
  const h = parseInt(hours, 10)
  const h12 = h % 12 || 12
  return `${h12}:${minutes}`
}

// Parse time string to minutes for sorting
function parseTimeToMinutes(timeStr: string | null): number {
  if (!timeStr) return 9999
  const [hours, minutes] = timeStr.split(':').map(Number)
  return hours * 60 + (minutes || 0)
}

function groupGamesByDate(games: any[]) {
  const grouped = new Map<string, any[]>()
  games.forEach(game => {
    const date = game.date ? new Date(game.date).toISOString().split('T')[0] : 'unknown'
    if (!grouped.has(date)) grouped.set(date, [])
    grouped.get(date)!.push(game)
  })
  return grouped
}

function calculateTeamForm(teamName: string, recentGames: any[]) {
  const teamGames = recentGames
    .filter(g => g.home_team_name === teamName || g.away_team_name === teamName)
    .sort((a, b) => new Date(b.date || 0).getTime() - new Date(a.date || 0).getTime())
    .slice(0, 10)

  let l10Wins = 0, l10Losses = 0, l10OT = 0
  let currentStreak = 0
  let streakType: 'W' | 'L' | null = null
  let streakBroken = false

  teamGames.forEach((game, idx) => {
    const isHome = game.home_team_name === teamName
    const teamGoals = isHome ? (game.home_total_goals ?? 0) : (game.away_total_goals ?? 0)
    const oppGoals = isHome ? (game.away_total_goals ?? 0) : (game.home_total_goals ?? 0)
    const won = teamGoals > oppGoals
    const lost = teamGoals < oppGoals

    if (won) l10Wins++
    else if (lost) l10Losses++
    else l10OT++

    if (!streakBroken) {
      if (idx === 0) {
        streakType = won ? 'W' : (lost ? 'L' : null)
        currentStreak = 1
      } else if (streakType === 'W' && won) {
        currentStreak++
      } else if (streakType === 'L' && lost) {
        currentStreak++
      } else {
        streakBroken = true
      }
    }
  })

  return {
    l10: `${l10Wins}-${l10Losses}-${l10OT}`,
    streak: streakType ? `${streakType}${currentStreak}` : '-',
    isHot: streakType === 'W' && currentStreak >= 3,
    isCold: streakType === 'L' && currentStreak >= 3,
  }
}

function calculateStandingsAsOfDate(games: any[], asOfDate: string, teamNames: string[]) {
  const teamStats = new Map<string, { wins: number; losses: number; otl: number; pts: number }>()
  teamNames.forEach(name => teamStats.set(name, { wins: 0, losses: 0, otl: 0, pts: 0 }))

  games.forEach(game => {
    const gameDate = game.date ? game.date.split(' ')[0].split('T')[0] : null
    if (!gameDate || gameDate > asOfDate) return
    const homeGoals = game.home_total_goals ?? 0
    const awayGoals = game.away_total_goals ?? 0
    if (homeGoals + awayGoals === 0) return

    const homeTeam = game.home_team_name
    const awayTeam = game.away_team_name
    if (!homeTeam || !awayTeam) return

    const homeStats = teamStats.get(homeTeam)
    const awayStats = teamStats.get(awayTeam)
    if (!homeStats || !awayStats) return

    if (homeGoals > awayGoals) {
      homeStats.wins++; homeStats.pts += 2; awayStats.losses++
    } else if (awayGoals > homeGoals) {
      awayStats.wins++; awayStats.pts += 2; homeStats.losses++
    } else {
      homeStats.otl++; homeStats.pts += 1; awayStats.otl++; awayStats.pts += 1
    }
  })

  const rankings = Array.from(teamStats.entries())
    .sort((a, b) => b[1].pts - a[1].pts)
    .map((entry, idx) => ({ teamName: entry[0], rank: idx + 1, ...entry[1] }))

  return new Map(rankings.map(r => [r.teamName, r.rank]))
}

export default async function NoradLandingPage() {
  const supabase = await createClient()
  const currentSeason = await getCurrentSeason()
  const now = new Date()
  const today = `${now.getUTCFullYear()}-${String(now.getUTCMonth() + 1).padStart(2, '0')}-${String(now.getUTCDate()).padStart(2, '0')}`
  const weekAgo = new Date(now)
  weekAgo.setDate(weekAgo.getDate() - 7)
  const weekAgoStr = `${weekAgo.getUTCFullYear()}-${String(weekAgo.getUTCMonth() + 1).padStart(2, '0')}-${String(weekAgo.getUTCDate()).padStart(2, '0')}`

  const [standings, teams, players, pointsLeaders, goalieLeaders, scheduleData, videosResult, noradBrandingResult] = await Promise.all([
    getStandings(),
    getTeams(),
    getPlayers(),
    currentSeason
      ? supabase.from('v_leaderboard_points').select('*').eq('season_id', currentSeason).order('season_rank', { ascending: true }).limit(5)
      : supabase.from('v_leaderboard_points').select('*').order('season_rank', { ascending: true }).limit(5),
    currentSeason
      ? supabase.from('v_leaderboard_goalie_gaa').select('*').eq('season_id', currentSeason).order('gaa', { ascending: true }).limit(3)
      : supabase.from('v_leaderboard_goalie_gaa').select('*').order('gaa', { ascending: true }).limit(3),
    currentSeason
      ? supabase.from('dim_schedule').select('*').eq('season_id', currentSeason).order('date', { ascending: false })
      : supabase.from('dim_schedule').select('*').order('date', { ascending: false }).limit(100),
    supabase.from('fact_video').select('*').order('game_id', { ascending: false }),
    supabase.from('dim_team').select('*').eq('team_name', 'NORAD').single(),
  ])

  const noradBranding = noradBrandingResult.data || null
  const leagueLogo = noradBranding?.team_logo || 'https://www.noradhockey.com/wp-content/uploads/2022/05/New-NORAD-Logo-White.png'
  const leaguePrimaryColor = noradBranding?.team_color1 || '#1e40af'

  const teamsMap = new Map(teams.map(t => [String(t.team_id), t]))
  const teamsByName = new Map(teams.map(t => [t.team_name, t]))
  const playersMap = new Map(players.map(p => [String(p.player_id), p]))
  const teamNames = teams.map(t => t.team_name)

  const videosData = videosResult.data || []
  const videosByGame = new Map<string, any[]>()
  videosData.forEach(v => {
    const gid = String(v.game_id)
    if (!videosByGame.has(gid)) videosByGame.set(gid, [])
    videosByGame.get(gid)!.push(v)
  })
  const gamesWithVideos = new Set(videosData.map(v => String(v.game_id)))

  const allScheduleGames = scheduleData.data || []
  const parseGameDate = (dateStr: string | null) => dateStr ? dateStr.split(' ')[0].split('T')[0] : null

  const recentGames = allScheduleGames.filter(g => {
    const gameDate = parseGameDate(g.date)
    const hasScore = (g.home_total_goals ?? 0) + (g.away_total_goals ?? 0) > 0
    return gameDate && gameDate < today && hasScore
  }).sort((a, b) => new Date(b.date || 0).getTime() - new Date(a.date || 0).getTime())

  // Upcoming sorted by date (soonest first), then by time
  const upcomingGames = allScheduleGames.filter(g => {
    const gameDate = parseGameDate(g.date)
    const hasNoScore = (g.home_total_goals ?? 0) + (g.away_total_goals ?? 0) === 0
    return gameDate && gameDate >= today && hasNoScore
  }).sort((a, b) => {
    const dateA = new Date(a.date || 0).getTime()
    const dateB = new Date(b.date || 0).getTime()
    if (dateA !== dateB) return dateA - dateB
    return parseTimeToMinutes(a.game_time) - parseTimeToMinutes(b.game_time)
  })

  const playedGames = allScheduleGames.filter(g => (g.home_total_goals ?? 0) + (g.away_total_goals ?? 0) > 0)
    .sort((a, b) => new Date(b.date || 0).getTime() - new Date(a.date || 0).getTime())

  const currentRankings = calculateStandingsAsOfDate(allScheduleGames, today, teamNames)
  const weekAgoRankings = calculateStandingsAsOfDate(allScheduleGames, weekAgoStr, teamNames)

  const pastForTicker = recentGames.slice(0, 15).reverse()
  const upcomingForTicker = upcomingGames.slice(0, 10)
  const allGamesForTicker = [...pastForTicker, ...upcomingForTicker]
  const gamesByDate = groupGamesByDate(allGamesForTicker)
  const sortedDates = Array.from(gamesByDate.keys()).sort((a, b) => new Date(a).getTime() - new Date(b).getTime())

  // Calculate accurate standings from played games only
  const teamStatsCalc = new Map<string, { gp: number; wins: number; losses: number; ties: number; pts: number; gf: number; ga: number }>()
  teamNames.forEach(name => teamStatsCalc.set(name, { gp: 0, wins: 0, losses: 0, ties: 0, pts: 0, gf: 0, ga: 0 }))

  playedGames.forEach(game => {
    const homeGoals = game.home_total_goals ?? 0
    const awayGoals = game.away_total_goals ?? 0
    const homeTeamName = game.home_team_name
    const awayTeamName = game.away_team_name
    if (!homeTeamName || !awayTeamName) return

    const homeStats = teamStatsCalc.get(homeTeamName)
    const awayStats = teamStatsCalc.get(awayTeamName)
    if (!homeStats || !awayStats) return

    // Increment GP and goals
    homeStats.gp++; homeStats.gf += homeGoals; homeStats.ga += awayGoals
    awayStats.gp++; awayStats.gf += awayGoals; awayStats.ga += homeGoals

    // Determine winner and assign points
    if (homeGoals > awayGoals) {
      homeStats.wins++; homeStats.pts += 2
      awayStats.losses++
    } else if (awayGoals > homeGoals) {
      awayStats.wins++; awayStats.pts += 2
      homeStats.losses++
    } else {
      homeStats.ties++; homeStats.pts += 1
      awayStats.ties++; awayStats.pts += 1
    }
  })

  // Sort by points descending
  const sortedTeams = Array.from(teamStatsCalc.entries())
    .filter(([_, stats]) => stats.gp > 0)
    .sort((a, b) => b[1].pts - a[1].pts)

  const powerRankings = sortedTeams.slice(0, 10).map(([teamName, stats], index) => {
    const teamData = teamsByName.get(teamName)
    const teamInfo = teamData ? teamsMap.get(String(teamData.team_id)) : undefined
    const form = calculateTeamForm(teamName, playedGames)
    const maxPts = stats.gp * 2
    const ptsPct = maxPts > 0 ? (stats.pts / maxPts * 100).toFixed(0) : '0'
    const currentRank = currentRankings.get(teamName) || (index + 1)
    const previousRank = weekAgoRankings.get(teamName) || currentRank
    const trendValue = previousRank - currentRank
    const gfg = stats.gp > 0 ? stats.gf / stats.gp : 0
    const gag = stats.gp > 0 ? stats.ga / stats.gp : 0
    const diff = stats.gf - stats.ga

    return {
      team_id: teamData?.team_id || '',
      team_name: teamName,
      teamInfo,
      powerRank: index + 1,
      gp: stats.gp,
      wins: stats.wins,
      losses: stats.losses,
      otl: stats.ties,
      pts: stats.pts,
      ptsPct,
      trend: trendValue,
      gf: stats.gf,
      ga: stats.ga,
      diff,
      gfg,
      gag,
      ...form
    }
  })

  const leadersData = pointsLeaders.data || []
  const goaliesData = goalieLeaders.data || []
  const gamesWithVideoData = playedGames.filter(g => gamesWithVideos.has(String(g.game_id)))

  const teamsMapObj = Object.fromEntries(teamsMap)
  const teamsByNameObj = Object.fromEntries(teamsByName)
  const gamesWithVideosArr = Array.from(gamesWithVideos)
  const gamesByDateArr = Array.from(gamesByDate.entries())

  return (
    <div className="min-h-screen bg-background">
      {/* Top Bar - View on NORAD link */}
      <div className="bg-muted/30 border-b border-border">
        <div className="max-w-7xl mx-auto px-4 py-1 flex justify-end">
          <a
            href="https://www.noradhockey.com"
            target="_blank"
            rel="noopener noreferrer"
            className="text-[10px] font-mono text-muted-foreground hover:text-primary flex items-center gap-1"
          >
            View on NORAD <ExternalLink className="w-2.5 h-2.5" />
          </a>
        </div>
      </div>

      {/* Games Ticker */}
      <GamesTicker
        gamesByDate={new Map(gamesByDateArr)}
        sortedDates={sortedDates}
        today={today}
        teamsMap={new Map(Object.entries(teamsMapObj))}
        teamsByName={new Map(Object.entries(teamsByNameObj))}
        gamesWithVideos={new Set(gamesWithVideosArr)}
      />

      {/* Hero Section - Centered logo */}
      <div className="border-b border-border" style={{ background: `linear-gradient(to bottom, ${leaguePrimaryColor}15 0%, transparent 100%)` }}>
        <div className="max-w-7xl mx-auto px-4 py-4 text-center">
          <Image src={leagueLogo} alt="NORAD Hockey League" width={80} height={80} className="mx-auto mb-2" unoptimized />
          <h1 className="font-display text-xl sm:text-2xl font-bold tracking-wider uppercase">NORAD Hockey League</h1>
        </div>
      </div>

      {/* Navigation Links */}
      <div className="border-b border-border bg-card">
        <div className="max-w-7xl mx-auto px-4">
          <nav className="flex items-center justify-center gap-1 py-1.5 overflow-x-auto">
            <Link href="/norad/standings" className="flex items-center gap-1 px-3 py-1 text-[10px] font-mono text-muted-foreground hover:text-primary hover:bg-muted rounded transition-colors">
              <Trophy className="w-3 h-3" /> Standings
            </Link>
            <Link href="/norad/teams" className="flex items-center gap-1 px-3 py-1 text-[10px] font-mono text-muted-foreground hover:text-primary hover:bg-muted rounded transition-colors">
              <Users className="w-3 h-3" /> Teams
            </Link>
            <Link href="/norad/players" className="flex items-center gap-1 px-3 py-1 text-[10px] font-mono text-muted-foreground hover:text-primary hover:bg-muted rounded transition-colors">
              <UserCircle className="w-3 h-3" /> Players
            </Link>
            <Link href="/norad/leaders" className="flex items-center gap-1 px-3 py-1 text-[10px] font-mono text-muted-foreground hover:text-primary hover:bg-muted rounded transition-colors">
              <Award className="w-3 h-3" /> Leaders
            </Link>
            <Link href="/norad/games" className="flex items-center gap-1 px-3 py-1 text-[10px] font-mono text-muted-foreground hover:text-primary hover:bg-muted rounded transition-colors">
              <BarChart3 className="w-3 h-3" /> Games
            </Link>
            <Link href="/norad/schedule" className="flex items-center gap-1 px-3 py-1 text-[10px] font-mono text-muted-foreground hover:text-primary hover:bg-muted rounded transition-colors">
              <CalendarDays className="w-3 h-3" /> Schedule
            </Link>
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-3">
        <div className="grid lg:grid-cols-12 gap-3">
          {/* Left Column - Power Rankings + Games */}
          <div className="lg:col-span-7 space-y-3">
            {/* Power Rankings */}
            <div className="bg-card rounded-lg border border-border overflow-hidden">
              <div className="px-3 py-1.5 bg-accent border-b border-border flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Trophy className="w-4 h-4 text-yellow-500" />
                  <h2 className="font-display font-semibold uppercase tracking-wider text-xs">Power Rankings</h2>
                </div>
                <Link href="/norad/standings" className="text-[10px] font-mono text-primary hover:underline flex items-center gap-1">Standings <ChevronRight className="w-3 h-3" /></Link>
              </div>
              <div className="text-[9px] overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="bg-muted/30 font-mono text-muted-foreground uppercase border-b border-border">
                      <th className="px-1 py-1 text-center w-8">#</th>
                      <th className="px-1 py-1 text-left">Team</th>
                      <th className="px-1 py-1 text-center">GP</th>
                      <th className="px-1 py-1 text-center">W-L-T</th>
                      <th className="px-1 py-1 text-center">Pts</th>
                      <th className="px-1 py-1 text-center hidden sm:table-cell">Pts%</th>
                      <th className="px-1 py-1 text-center">GF</th>
                      <th className="px-1 py-1 text-center">GA</th>
                      <th className="px-1 py-1 text-center">Diff</th>
                      <th className="px-1 py-1 text-center hidden sm:table-cell">GF/G</th>
                      <th className="px-1 py-1 text-center hidden sm:table-cell">GA/G</th>
                      <th className="px-1 py-1 text-center hidden md:table-cell">L10</th>
                      <th className="px-1 py-1 text-center hidden md:table-cell">Strk</th>
                    </tr>
                  </thead>
                  <tbody>
                    {powerRankings.map((team) => {
                      return (
                        <tr key={team.team_id} className="hover:bg-muted/50 transition-colors border-b border-border/50 last:border-0" style={{ borderLeft: `3px solid ${team.teamInfo?.team_color1 || '#666'}` }}>
                          <td className="px-1 py-1 text-center">
                            <div className="flex items-center justify-center gap-0.5 font-mono">
                              <span className="font-bold text-muted-foreground">{team.powerRank}</span>
                              {team.trend !== 0 && (
                                <span className={cn('text-[8px] flex items-center', team.trend > 0 ? 'text-green-500' : 'text-red-500')}>
                                  {team.trend > 0 ? <TrendingUp className="w-2.5 h-2.5" /> : <TrendingDown className="w-2.5 h-2.5" />}
                                  {Math.abs(team.trend)}
                                </span>
                              )}
                            </div>
                          </td>
                          <td className="px-1 py-1">
                            <Link href={`/norad/teams/${team.team_id}`} className="flex items-center gap-1 min-w-0">
                              {team.teamInfo && <TeamLogo src={team.teamInfo.team_logo || null} name={team.team_name} abbrev={team.teamInfo.team_cd} primaryColor={team.teamInfo.team_color1} secondaryColor={team.teamInfo.team_color2} size="xs" />}
                              <span className="font-display truncate">{team.team_name}</span>
                              {team.isHot && <Flame className="w-3 h-3 text-orange-500 shrink-0" />}
                              {team.isCold && <Snowflake className="w-3 h-3 text-blue-400 shrink-0" />}
                            </Link>
                          </td>
                          <td className="px-1 py-1 text-center font-mono text-muted-foreground">{team.gp}</td>
                          <td className="px-1 py-1 text-center font-mono">{team.wins}-{team.losses}-{team.otl}</td>
                          <td className="px-1 py-1 text-center font-mono font-bold text-primary">{team.pts}</td>
                          <td className="px-1 py-1 text-center font-mono hidden sm:table-cell">.{team.ptsPct}</td>
                          <td className="px-1 py-1 text-center font-mono text-goal">{team.gf}</td>
                          <td className="px-1 py-1 text-center font-mono text-red-400">{team.ga}</td>
                          <td className="px-1 py-1 text-center font-mono">
                            <span className={cn(team.diff > 0 ? 'text-green-500' : team.diff < 0 ? 'text-red-500' : 'text-muted-foreground')}>
                              {team.diff > 0 ? '+' : ''}{team.diff}
                            </span>
                          </td>
                          <td className="px-1 py-1 text-center font-mono text-muted-foreground hidden sm:table-cell">{team.gfg.toFixed(1)}</td>
                          <td className="px-1 py-1 text-center font-mono text-muted-foreground hidden sm:table-cell">{team.gag.toFixed(1)}</td>
                          <td className="px-1 py-1 text-center font-mono text-muted-foreground hidden md:table-cell">{team.l10}</td>
                          <td className="px-1 py-1 text-center font-mono hidden md:table-cell">
                            <span className={cn(team.streak.startsWith('W') ? 'text-green-500' : team.streak.startsWith('L') ? 'text-red-500' : 'text-muted-foreground')}>{team.streak}</span>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Recent & Upcoming Games - Same layout */}
            <div className="grid grid-cols-2 gap-3">
              {/* Recent Games */}
              <div className="bg-card rounded-lg border border-border overflow-hidden">
                <div className="px-2 py-1 bg-accent border-b border-border flex items-center justify-between">
                  <div className="flex items-center gap-1"><Calendar className="w-3 h-3 text-muted-foreground" /><h2 className="font-display font-semibold uppercase tracking-wider text-[10px]">Recent</h2></div>
                  <Link href="/norad/games" className="text-[8px] font-mono text-primary hover:underline">All</Link>
                </div>
                <div className="divide-y divide-border">
                  {recentGames.slice(0, 5).map((game, idx) => {
                    const homeTeam = teamsMap.get(String(game.home_team_id))
                    const awayTeam = teamsMap.get(String(game.away_team_id))
                    const homeGoals = game.home_total_goals ?? 0
                    const awayGoals = game.away_total_goals ?? 0
                    const homeWon = homeGoals > awayGoals
                    const dateStr = game.date ? new Date(game.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : ''
                    return (
                      <Link key={idx} href={`/norad/games/${game.game_id}`} className="block px-1.5 py-1.5 hover:bg-muted/50 h-[44px]">
                        <div className="flex items-center justify-between text-[8px] font-mono">
                          <span className="text-muted-foreground">{dateStr}</span>
                          <span className="text-muted-foreground">{formatGameTime(game.game_time)}</span>
                        </div>
                        <div className="flex items-center justify-between text-[9px] mt-0.5">
                          <div className="flex items-center gap-1">
                            {awayTeam && <TeamLogo src={awayTeam.team_logo || null} name="" abbrev={awayTeam.team_cd} primaryColor={awayTeam.team_color1} secondaryColor={awayTeam.team_color2} size="xs" />}
                            <span className={cn(!homeWon && 'font-bold')}>{awayTeam?.team_cd}</span>
                          </div>
                          <div className="flex items-center gap-1 text-center">
                            <span className={cn('font-mono', !homeWon ? 'font-bold' : 'text-muted-foreground')}>{awayGoals}</span>
                            <span className="text-muted-foreground text-[8px]">@</span>
                            <span className={cn('font-mono', homeWon ? 'font-bold' : 'text-muted-foreground')}>{homeGoals}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <span className={cn(homeWon && 'font-bold')}>{homeTeam?.team_cd}</span>
                            {homeTeam && <TeamLogo src={homeTeam.team_logo || null} name="" abbrev={homeTeam.team_cd} primaryColor={homeTeam.team_color1} secondaryColor={homeTeam.team_color2} size="xs" />}
                          </div>
                        </div>
                      </Link>
                    )
                  })}
                  {recentGames.length === 0 && <div className="p-2 text-center text-muted-foreground text-[9px]">No recent games</div>}
                </div>
              </div>

              {/* Upcoming Games */}
              <div className="bg-card rounded-lg border border-border overflow-hidden">
                <div className="px-2 py-1 bg-accent border-b border-border flex items-center justify-between">
                  <div className="flex items-center gap-1"><Calendar className="w-3 h-3 text-primary" /><h2 className="font-display font-semibold uppercase tracking-wider text-[10px]">Upcoming</h2></div>
                  <Link href="/norad/schedule" className="text-[8px] font-mono text-primary hover:underline">Sched</Link>
                </div>
                <div className="divide-y divide-border">
                  {upcomingGames.slice(0, 5).map((game, idx) => {
                    const homeTeam = teamsMap.get(String(game.home_team_id))
                    const awayTeam = teamsMap.get(String(game.away_team_id))
                    const dateStr = game.date ? new Date(game.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : ''
                    return (
                      <div key={idx} className="px-1.5 py-1.5 h-[44px]">
                        <div className="flex items-center justify-between text-[8px] font-mono">
                          <span className="text-primary">{dateStr}</span>
                          <span className="text-muted-foreground">{formatGameTime(game.game_time)}</span>
                        </div>
                        <div className="flex items-center justify-between text-[9px] mt-0.5">
                          <div className="flex items-center gap-1">
                            {awayTeam && <TeamLogo src={awayTeam.team_logo || null} name="" abbrev={awayTeam.team_cd} primaryColor={awayTeam.team_color1} secondaryColor={awayTeam.team_color2} size="xs" />}
                            <span>{awayTeam?.team_cd}</span>
                          </div>
                          <span className="text-muted-foreground text-[8px]">@</span>
                          <div className="flex items-center gap-1">
                            <span>{homeTeam?.team_cd}</span>
                            {homeTeam && <TeamLogo src={homeTeam.team_logo || null} name="" abbrev={homeTeam.team_cd} primaryColor={homeTeam.team_color1} secondaryColor={homeTeam.team_color2} size="xs" />}
                          </div>
                        </div>
                      </div>
                    )
                  })}
                  {upcomingGames.length === 0 && <div className="p-2 text-center text-muted-foreground text-[9px] h-[44px]">No upcoming games</div>}
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Leaders + Watch Games */}
          <div className="lg:col-span-5 flex flex-col gap-3">
            {/* Scoring Leaders */}
            <div className="bg-card rounded-lg border border-border overflow-hidden">
              <div className="px-3 py-1.5 bg-accent border-b border-border flex items-center justify-between">
                <div className="flex items-center gap-2"><Award className="w-4 h-4 text-assist" /><h2 className="font-display font-semibold uppercase tracking-wider text-xs">Scoring Leaders</h2></div>
                <Link href="/norad/leaders" className="text-[10px] font-mono text-primary hover:underline flex items-center gap-1">All <ChevronRight className="w-3 h-3" /></Link>
              </div>
              <div className="divide-y divide-border">
                {leadersData.map((player, index) => {
                  const playerTeam = teamsMap.get(String(player.team_id))
                  const playerData = playersMap.get(String(player.player_id))
                  const teamColor1 = playerTeam?.team_color1 || '#1e3a5f'
                  const teamColor2 = playerTeam?.team_color2 || teamColor1
                  const playerName = player.player_full_name || playerData?.player_full_name || playerData?.player_name || 'Unknown'

                  return (
                    <Link key={player.player_id} href={`/norad/players/${player.player_id}`}
                      className="flex items-center gap-2 px-2 py-1.5 hover:bg-muted/50 transition-colors"
                      style={{ borderLeft: `3px solid ${teamColor1}` }}>
                      <span className={cn('font-mono w-4 text-center text-[10px]', index === 0 ? 'text-yellow-500 font-bold' : 'text-muted-foreground')}>{index + 1}</span>
                      <PlayerPhoto src={playerData?.player_image || null} name={playerName} primaryColor={teamColor1} size="sm" />
                      <div className="flex-1 min-w-0">
                        <div className="font-display text-xs truncate">{playerName}</div>
                        <div className="flex items-center gap-1 text-[8px] text-muted-foreground">
                          {playerTeam && <TeamLogo src={playerTeam.team_logo || null} name="" abbrev={playerTeam.team_cd} primaryColor={teamColor1} secondaryColor={teamColor2} size="xs" />}
                          <span>{playerTeam?.team_name || player.team_name}</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-mono text-sm font-bold text-primary">{player.points}</div>
                        <div className="font-mono text-[8px] text-muted-foreground"><span className="text-goal">{player.goals}G</span> <span className="text-assist">{player.assists}A</span></div>
                      </div>
                    </Link>
                  )
                })}
              </div>
            </div>

            {/* Goalie Leaders */}
            <div className="bg-card rounded-lg border border-border overflow-hidden">
              <div className="px-3 py-1.5 bg-accent border-b border-border flex items-center justify-between">
                <div className="flex items-center gap-2"><Award className="w-4 h-4 text-save" /><h2 className="font-display font-semibold uppercase tracking-wider text-xs">Goalie Leaders</h2></div>
                <Link href="/norad/leaders?tab=goalies" className="text-[10px] font-mono text-primary hover:underline flex items-center gap-1">All <ChevronRight className="w-3 h-3" /></Link>
              </div>
              <div className="divide-y divide-border">
                {goaliesData.map((goalie, index) => {
                  const goalieTeam = teamsMap.get(String(goalie.team_id))
                  const goalieData = playersMap.get(String(goalie.player_id))
                  const teamColor1 = goalieTeam?.team_color1 || '#1e3a5f'
                  const teamColor2 = goalieTeam?.team_color2 || teamColor1
                  const goalieName = goalie.player_full_name || goalie.player_name || goalieData?.player_full_name || 'Unknown'

                  return (
                    <Link key={goalie.player_id} href={`/norad/goalies/${goalie.player_id}`}
                      className="flex items-center gap-2 px-2 py-1.5 hover:bg-muted/50 transition-colors"
                      style={{ borderLeft: `3px solid ${teamColor1}` }}>
                      <span className={cn('font-mono w-4 text-center text-[10px]', index === 0 ? 'text-yellow-500 font-bold' : 'text-muted-foreground')}>{index + 1}</span>
                      <PlayerPhoto src={goalieData?.player_image || null} name={goalieName} primaryColor={teamColor1} size="sm" />
                      <div className="flex-1 min-w-0">
                        <div className="font-display text-xs truncate">{goalieName}</div>
                        <div className="flex items-center gap-1 text-[8px] text-muted-foreground">
                          {goalieTeam && <TeamLogo src={goalieTeam.team_logo || null} name="" abbrev={goalieTeam.team_cd} primaryColor={teamColor1} secondaryColor={teamColor2} size="xs" />}
                          <span>{goalieTeam?.team_name || goalie.team_name}</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-mono text-sm font-bold text-save">{goalie.gaa?.toFixed(2)}</div>
                        <div className="font-mono text-[8px] text-muted-foreground">{goalie.wins}W • {goalie.games_played}GP</div>
                      </div>
                    </Link>
                  )
                })}
                {goaliesData.length === 0 && <div className="p-2 text-center text-muted-foreground text-xs">No goalie data</div>}
              </div>
            </div>

            {/* Watch Games */}
            <div className="bg-card rounded-lg border border-border overflow-hidden">
              <div className="px-3 py-1.5 bg-accent border-b border-border flex items-center justify-between">
                <div className="flex items-center gap-2"><Video className="w-4 h-4 text-red-500" /><h2 className="font-display font-semibold uppercase tracking-wider text-xs">Watch Games</h2></div>
                <Link href="/norad/games" className="text-[10px] font-mono text-primary hover:underline flex items-center gap-1">All <ChevronRight className="w-3 h-3" /></Link>
              </div>
              {gamesWithVideoData.length > 0 ? (
                <div className="divide-y divide-border overflow-y-auto max-h-[200px]">
                  {gamesWithVideoData.slice(0, 6).map((game) => {
                    const homeTeam = teamsMap.get(String(game.home_team_id))
                    const awayTeam = teamsMap.get(String(game.away_team_id))
                    const homeGoals = game.home_total_goals ?? 0
                    const awayGoals = game.away_total_goals ?? 0
                    const homeWon = homeGoals > awayGoals
                    const winnerColor = homeWon ? (homeTeam?.team_color1 || '#666') : (awayTeam?.team_color1 || '#666')
                    const gameVideos = videosByGame.get(String(game.game_id)) || []
                    const dateStr = game.date ? new Date(game.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : ''

                    return (
                      <Link key={game.game_id} href={`/norad/games/${game.game_id}`}
                        className="flex items-center gap-2 px-2 py-1 hover:bg-muted/50 transition-colors"
                        style={{ borderLeft: `3px solid ${winnerColor}` }}>
                        <Play className="w-3 h-3 text-red-500 fill-current shrink-0" />
                        <div className="flex items-center gap-2 flex-1 min-w-0 text-[10px]">
                          <div className="flex items-center gap-1">
                            {awayTeam && <TeamLogo src={awayTeam.team_logo || null} name="" abbrev={awayTeam.team_cd} primaryColor={awayTeam.team_color1} secondaryColor={awayTeam.team_color2} size="xs" />}
                            <span className={cn(!homeWon && 'font-semibold')}>{awayTeam?.team_cd}</span>
                            <span className={cn('font-mono', !homeWon ? 'font-bold' : 'text-muted-foreground')}>{awayGoals}</span>
                          </div>
                          <span className="text-muted-foreground">@</span>
                          <div className="flex items-center gap-1">
                            <span className={cn('font-mono', homeWon ? 'font-bold' : 'text-muted-foreground')}>{homeGoals}</span>
                            <span className={cn(homeWon && 'font-semibold')}>{homeTeam?.team_cd}</span>
                            {homeTeam && <TeamLogo src={homeTeam.team_logo || null} name="" abbrev={homeTeam.team_cd} primaryColor={homeTeam.team_color1} secondaryColor={homeTeam.team_color2} size="xs" />}
                          </div>
                        </div>
                        <div className="flex items-center gap-1 shrink-0">
                          {gameVideos.slice(0, 2).map((v) => (
                            <span key={v.video_key} className="text-[7px] px-1 py-0.5 bg-red-500/20 text-red-400 rounded font-mono">
                              {v.video_type === 'Full_Ice' ? 'Full' : v.video_type === 'Broadcast' ? 'TV' : 'Vid'}
                            </span>
                          ))}
                        </div>
                        <span className="text-[8px] font-mono text-muted-foreground shrink-0">{dateStr}</span>
                      </Link>
                    )
                  })}
                </div>
              ) : (
                <div className="p-3 text-center text-muted-foreground text-xs">No videos available</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
