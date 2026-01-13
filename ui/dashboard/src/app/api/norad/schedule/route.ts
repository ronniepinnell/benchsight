import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

// Fetch upcoming games from noradhockey.com
// This is a server-side API route that scrapes the schedule page

interface NoradGame {
  game_id?: number
  date?: string
  time?: string
  home_team?: string
  away_team?: string
  home_team_id?: string
  away_team_id?: string
  home_score?: number
  away_score?: number
  venue?: string
  game_date?: string
  game_time?: string
}

async function getLeagueIdFromDatabase(): Promise<string | null> {
  try {
    const supabase = await createClient()
    
    // Try to get league_id directly from dim_schedule (if column exists)
    const { data: scheduleData, error: scheduleError } = await supabase
      .from('dim_schedule')
      .select('league_id')
      .not('league_id', 'is', null)
      .limit(1)
      .single()
    
    if (!scheduleError && scheduleData?.league_id) {
      return String(scheduleData.league_id)
    }
    
    // If not in dim_schedule, try joining to dim_season
    const { data: seasonData, error: seasonError } = await supabase
      .from('dim_schedule')
      .select(`
        season_id,
        dim_season!inner(league_id)
      `)
      .not('season_id', 'is', null)
      .limit(1)
      .single()
    
    if (!seasonError && seasonData && typeof seasonData === 'object' && 'dim_season' in seasonData) {
      const season = seasonData.dim_season as any
      if (season?.league_id) {
        return String(season.league_id)
      }
    }
    
    // Alternative: query dim_season directly for current season
    const { data: currentSeason, error: seasonDirectError } = await supabase
      .from('dim_season')
      .select('league_id')
      .not('league_id', 'is', null)
      .order('start_date', { ascending: false })
      .limit(1)
      .single()
    
    if (!seasonDirectError && currentSeason?.league_id) {
      return String(currentSeason.league_id)
    }
    
    return null
  } catch (error) {
    console.error('Error fetching league_id from database:', error)
    return null
  }
}

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const teamName = searchParams.get('team')
    const teamId = searchParams.get('teamId')
    
    // Try to get league_id from multiple sources (priority order)
    let leagueId = searchParams.get('leagueId') // 1. Query parameter (highest priority)
    
    if (!leagueId) {
      leagueId = await getLeagueIdFromDatabase() // 2. Database lookup
    }
    
    if (!leagueId) {
      leagueId = process.env.NEXT_PUBLIC_NORAD_LEAGUE_ID // 3. Environment variable (fallback)
    }
    
    if (!leagueId) {
      return NextResponse.json(
        { 
          error: 'League ID not found. Please ensure dim_schedule or dim_season has league_id populated, or set NEXT_PUBLIC_NORAD_LEAGUE_ID environment variable.',
          hint: 'Upload your schedule data to Supabase with league_id column populated, or pass leagueId as a query parameter.'
        },
        { status: 400 }
      )
    }

    // Build schedule URL - try to get current season schedule
    const scheduleUrl = `https://www.noradhockey.com/schedule/list/league_id/${leagueId}`
    
    // Fetch the schedule page
    const response = await fetch(scheduleUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
      },
      next: { revalidate: 300 } // Cache for 5 minutes
    })

    if (!response.ok) {
      throw new Error(`Failed to fetch schedule: ${response.statusText}`)
    }

    const html = await response.text()
    
    // Parse HTML to extract games
    const games = parseNoradSchedule(html, teamName, teamId)
    
    return NextResponse.json({ games })
  } catch (error: any) {
    console.error('Error fetching NORAD schedule:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to fetch schedule from noradhockey.com', games: [] },
      { status: 500 }
    )
  }
}

function parseNoradSchedule(html: string, filterTeam?: string | null, filterTeamId?: string | null): NoradGame[] {
  const games: NoradGame[] = []
  const today = new Date()
  
  // Try multiple parsing strategies
  
  // Strategy 1: Look for JSON data embedded in script tags
  const scriptMatches = html.match(/<script[^>]*>([\s\S]*?)<\/script>/gi) || []
  for (const script of scriptMatches) {
    // Look for common JSON patterns
    const jsonPatterns = [
      /window\.__INITIAL_STATE__\s*=\s*({.+?});/s,
      /var\s+scheduleData\s*=\s*({.+?});/s,
      /"games":\s*\[(.*?)\]/s,
    ]
    
    for (const pattern of jsonPatterns) {
      const match = script.match(pattern)
      if (match) {
        try {
          const data = JSON.parse(match[1])
          // Try to extract games from various possible structures
          if (Array.isArray(data)) {
            games.push(...data.map(parseGameFromJson))
          } else if (data.games && Array.isArray(data.games)) {
            games.push(...data.games.map(parseGameFromJson))
          } else if (data.schedule && Array.isArray(data.schedule)) {
            games.push(...data.schedule.map(parseGameFromJson))
          }
        } catch (e) {
          // Not valid JSON, continue
        }
      }
    }
  }
  
  // Strategy 2: Parse HTML table structure
  if (games.length === 0) {
    // Look for table rows with game data
    const tableRegex = /<table[^>]*>([\s\S]*?)<\/table>/gi
    const tables = html.match(tableRegex) || []
    
    for (const table of tables) {
      const rowRegex = /<tr[^>]*>([\s\S]*?)<\/tr>/gi
      const rows = table.match(rowRegex) || []
      
      for (const row of rows) {
        const game = parseGameFromRow(row)
        if (game && (game.home_team || game.away_team)) {
          games.push(game)
        }
      }
    }
  }
  
  // Filter games
  let filteredGames = games.filter(game => {
    // Only upcoming games (no scores or future dates)
    if (game.home_score !== undefined || game.away_score !== undefined) {
      return false
    }
    
    // Filter by team if provided
    if (filterTeam) {
      const teamMatch = game.home_team?.toLowerCase().includes(filterTeam.toLowerCase()) ||
                       game.away_team?.toLowerCase().includes(filterTeam.toLowerCase())
      if (!teamMatch) return false
    }
    
    if (filterTeamId) {
      const idMatch = game.home_team_id === filterTeamId || game.away_team_id === filterTeamId
      if (!idMatch) return false
    }
    
    // Filter to future dates only
    if (game.date || game.game_date) {
      const gameDate = new Date(game.date || game.game_date || '')
      if (gameDate < today) {
        return false
      }
    }
    
    return true
  })
  
  // Sort by date
  filteredGames.sort((a, b) => {
    const dateA = new Date(a.date || a.game_date || '9999-12-31').getTime()
    const dateB = new Date(b.date || b.game_date || '9999-12-31').getTime()
    return dateA - dateB
  })
  
  return filteredGames.slice(0, 20) // Limit to 20 games
}

function parseGameFromJson(data: any): NoradGame {
  return {
    game_id: data.game_id || data.id || data.event_id,
    date: data.date || data.game_date || data.scheduled_date,
    time: data.time || data.game_time || data.scheduled_time,
    home_team: data.home_team || data.home_team_name,
    away_team: data.away_team || data.away_team_name,
    home_team_id: data.home_team_id,
    away_team_id: data.away_team_id,
    home_score: data.home_score || data.home_total_goals,
    away_score: data.away_score || data.away_total_goals,
    venue: data.venue || data.location,
    game_date: data.date || data.game_date,
    game_time: data.time || data.game_time,
  }
}

function parseGameFromRow(row: string): NoradGame | null {
  try {
    const game: NoradGame = {}
    
    // Extract game ID from link
    const gameIdMatch = row.match(/\/game\/(\d+)/i) || row.match(/event\/(\d+)/i) || row.match(/game_id["']?\s*[:=]\s*["']?(\d+)/i)
    if (gameIdMatch) {
      game.game_id = parseInt(gameIdMatch[1])
    }
    
    // Extract date (various formats)
    const dateMatch = row.match(/(\d{4}-\d{2}-\d{2})|(\d{1,2}\/\d{1,2}\/\d{4})|(\d{1,2}-\d{1,2}-\d{4})/)
    if (dateMatch) {
      game.date = dateMatch[0]
      game.game_date = dateMatch[0]
    }
    
    // Extract time
    const timeMatch = row.match(/(\d{1,2}:\d{2}\s*(?:AM|PM)?)/i) || row.match(/(\d{1,2}:\d{2})/)
    if (timeMatch) {
      game.time = timeMatch[0].trim()
      game.game_time = timeMatch[0].trim()
    }
    
    // Extract team names - look for links or text
    const teamLinkRegex = /<a[^>]*href="[^"]*team[^"]*"[^>]*>([^<]+)<\/a>/gi
    const teamLinks = row.match(teamLinkRegex) || []
    if (teamLinks.length >= 2) {
      game.away_team = teamLinks[0].replace(/<[^>]+>/g, '').trim()
      game.home_team = teamLinks[1].replace(/<[^>]+>/g, '').trim()
    } else {
      // Try to find team names in table cells
      const cellRegex = /<td[^>]*>([^<]+)<\/td>/g
      const cells = row.match(cellRegex) || []
      if (cells.length >= 2) {
        const cellTexts = cells.map(c => c.replace(/<[^>]+>/g, '').trim()).filter(c => c && !c.match(/^\d+$/) && !c.match(/^\d{1,2}:\d{2}/))
        if (cellTexts.length >= 2) {
          game.away_team = cellTexts[0]
          game.home_team = cellTexts[1]
        }
      }
    }
    
    // Extract scores if available
    const scoreMatch = row.match(/(\d+)\s*[-–]\s*(\d+)/)
    if (scoreMatch) {
      game.away_score = parseInt(scoreMatch[1])
      game.home_score = parseInt(scoreMatch[2])
    }
    
    // Extract venue
    const venueMatch = row.match(/venue["']?\s*[:=]\s*["']?([^"']+)/i) || row.match(/<td[^>]*>([^<]*rink[^<]*)<\/td>/i)
    if (venueMatch) {
      game.venue = venueMatch[1].trim()
    }
    
    return game
  } catch (e) {
    return null
  }
}
