/**
 * Tracker Game Selection Page
 * 
 * Allows users to select a game to track or create a new tracking session
 */

'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import { Button } from '@/components/ui/button'
import { toast } from '@/lib/tracker/utils/toast'
import Link from 'next/link'

interface Game {
  game_id: string
  home_team: string
  away_team: string
  game_date?: string
  home_score?: number
  away_score?: number
}

export default function TrackerPage() {
  const router = useRouter()
  const [games, setGames] = useState<Game[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    loadRecentGames()
  }, [])

  const loadRecentGames = async () => {
    try {
      const supabase = createClient()
      
      // Try to load from stage_dim_schedule
      const { data: scheduleGames, error: scheduleError } = await supabase
        .from('stage_dim_schedule')
        .select('game_id, home_team, away_team, game_date')
        .order('game_date', { ascending: false })
        .limit(50)

      if (scheduleGames && !scheduleError) {
        setGames(scheduleGames.map(g => ({
          game_id: String(g.game_id),
          home_team: g.home_team || 'Home',
          away_team: g.away_team || 'Away',
          game_date: g.game_date
        })))
      } else {
        // Fallback: try fact_game_status
        const { data: statusGames, error: statusError } = await supabase
          .from('fact_game_status')
          .select('game_id, home_team, away_team, game_date')
          .order('game_date', { ascending: false })
          .limit(50)

        if (statusGames && !statusError) {
          setGames(statusGames.map(g => ({
            game_id: String(g.game_id),
            home_team: g.home_team || 'Home',
            away_team: g.away_team || 'Away',
            game_date: g.game_date
          })))
        }
      }
    } catch (error: any) {
      console.error('Error loading games:', error)
      toast('Error loading games', 'error')
    } finally {
      setIsLoading(false)
    }
  }

  const handleGameSelect = (gameId: string) => {
    router.push(`/tracker/${gameId}`)
  }

  const handleNewGame = () => {
    const gameId = prompt('Enter game ID for new tracking session:')
    if (gameId) {
      router.push(`/tracker/${gameId}`)
    }
  }

  const filteredGames = games.filter(game => {
    if (!searchQuery) return true
    const query = searchQuery.toLowerCase()
    return (
      game.home_team.toLowerCase().includes(query) ||
      game.away_team.toLowerCase().includes(query) ||
      game.game_id.includes(query)
    )
  })

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold">Game Tracker</h1>
          <p className="text-muted-foreground mt-2">
            Select a game to track events, shifts, and statistics
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <Button onClick={handleNewGame}>
            + New Tracking Session
          </Button>
          <Button onClick={loadRecentGames} variant="outline">
            🔄 Refresh
          </Button>
          <Button 
            onClick={() => router.push('/tracker/videos')} 
            variant="outline"
          >
            🎥 Manage Videos
          </Button>
        </div>

        {/* Search */}
        <div>
          <input
            type="text"
            placeholder="Search games by team or game ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-2 border border-border rounded-lg bg-input"
          />
        </div>

        {/* Games List */}
        {isLoading ? (
          <div className="text-center py-12 text-muted-foreground">
            Loading games...
          </div>
        ) : filteredGames.length === 0 ? (
          <div className="text-center py-12 text-muted-foreground">
            {searchQuery ? 'No games found matching your search' : 'No games found'}
          </div>
        ) : (
          <div className="space-y-2">
            {filteredGames.map((game) => (
              <button
                key={game.game_id}
                onClick={() => handleGameSelect(game.game_id)}
                className="w-full p-4 border border-border rounded-lg hover:bg-muted transition-colors text-left"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-semibold">
                      {game.home_team} vs {game.away_team}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      Game ID: {game.game_id}
                      {game.game_date && ` • ${new Date(game.game_date).toLocaleDateString()}`}
                    </div>
                  </div>
                  <div className="text-muted-foreground">
                    →
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}

        {/* Info */}
        <div className="border rounded-lg p-4 bg-muted/50">
          <p className="text-sm text-muted-foreground">
            <strong>Note:</strong> The tracker is being rebuilt in Next.js. 
            You can still use the original tracker at <code className="text-xs bg-background px-1 py-0.5 rounded">ui/tracker/tracker_index_v23.5.html</code>
          </p>
        </div>
      </div>
    </div>
  )
}
