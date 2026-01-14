/**
 * Video Management Page
 * 
 * Dedicated page for storing YouTube video links and details for games
 */

'use client'

'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import { Button } from '@/components/ui/button'
import { toast } from '@/lib/tracker/utils/toast'
import { exportToExcel } from '@/lib/tracker/export'
import type { Event, Shift } from '@/lib/tracker/types'

interface VideoLink {
  id?: string
  game_id: string
  video_url: string
  video_type: 'youtube' | 'local' | 'other'
  video_id?: string // YouTube video ID
  title?: string
  description?: string
  start_time?: string // Video start time (for trimming)
  end_time?: string // Video end time (for trimming)
  period?: number // Which period this video covers
  notes?: string
  created_at?: string
  updated_at?: string
}

interface GameVideoData {
  game_id: string
  home_team: string
  away_team: string
  game_date?: string
  videos: VideoLink[]
  events?: Event[]
  shifts?: Shift[]
}

export default function TrackerVideosPage() {
  const router = useRouter()
  const [games, setGames] = useState<GameVideoData[]>([])
  const [selectedGame, setSelectedGame] = useState<GameVideoData | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  // Video form state
  const [videoUrl, setVideoUrl] = useState('')
  const [videoType, setVideoType] = useState<'youtube' | 'local' | 'other'>('youtube')
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [startTime, setStartTime] = useState('')
  const [endTime, setEndTime] = useState('')
  const [period, setPeriod] = useState<number | ''>('')
  const [notes, setNotes] = useState('')

  useEffect(() => {
    loadGames()
  }, [])

  const loadGames = async () => {
    setIsLoading(true)
    try {
      const supabase = createClient()
      
      // Load games from schedule
      const { data: scheduleGames } = await supabase
        .from('stage_dim_schedule')
        .select('game_id, home_team, away_team, game_date')
        .order('game_date', { ascending: false })
        .limit(100)

      if (scheduleGames) {
        // Load videos for each game
        const gamesWithVideos = await Promise.all(
          scheduleGames.map(async (game) => {
            const { data: videos } = await supabase
              .from('tracker_videos')
              .select('*')
              .eq('game_id', game.game_id)
              .order('created_at', { ascending: false })

            return {
              game_id: String(game.game_id),
              home_team: game.home_team || 'Home',
              away_team: game.away_team || 'Away',
              game_date: game.game_date,
              videos: (videos || []) as VideoLink[]
            }
          })
        )

        setGames(gamesWithVideos)
      }
    } catch (error: any) {
      console.error('Error loading games:', error)
      toast('Error loading games', 'error')
    } finally {
      setIsLoading(false)
    }
  }

  const extractYouTubeId = (url: string): string | null => {
    const patterns = [
      /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/,
      /youtube\.com\/watch\?.*v=([^&\n?#]+)/
    ]
    
    for (const pattern of patterns) {
      const match = url.match(pattern)
      if (match) return match[1]
    }
    return null
  }

  const handleAddVideo = async () => {
    if (!selectedGame || !videoUrl) {
      toast('Select a game and enter video URL', 'error')
      return
    }

    try {
      const supabase = createClient()
      
      const videoData: VideoLink = {
        game_id: selectedGame.game_id,
        video_url: videoUrl,
        video_type: videoType,
        video_id: videoType === 'youtube' ? extractYouTubeId(videoUrl) : undefined,
        title: title || undefined,
        description: description || undefined,
        start_time: startTime || undefined,
        end_time: endTime || undefined,
        period: period ? Number(period) : undefined,
        notes: notes || undefined
      }

      const { error } = await supabase
        .from('tracker_videos')
        .insert([videoData])

      if (error) throw error

      toast('Video added successfully', 'success')
      
      // Reset form
      setVideoUrl('')
      setTitle('')
      setDescription('')
      setStartTime('')
      setEndTime('')
      setPeriod('')
      setNotes('')
      
      // Reload games
      loadGames()
    } catch (error: any) {
      console.error('Error adding video:', error)
      toast(`Error: ${error.message}`, 'error')
    }
  }

  const handleDeleteVideo = async (videoId: string) => {
    if (!confirm('Delete this video link?')) return

    try {
      const supabase = createClient()
      const { error } = await supabase
        .from('tracker_videos')
        .delete()
        .eq('id', videoId)

      if (error) throw error

      toast('Video deleted', 'success')
      loadGames()
    } catch (error: any) {
      toast(`Error: ${error.message}`, 'error')
    }
  }

  const handleExport = async (game: GameVideoData) => {
    try {
      // Load events and shifts for this game
      const supabase = createClient()
      
      const { data: eventsData } = await supabase
        .from('stage_events_tracking')
        .select('*')
        .eq('game_id', game.game_id)

      const { data: shiftsData } = await supabase
        .from('stage_shifts_tracking')
        .select('*')
        .eq('game_id', game.game_id)

      // Transform to Event/Shift format (simplified)
      const events: Event[] = (eventsData || []).map((e: any, idx: number) => ({
        idx,
        period: e.period || 1,
        type: e.type as any,
        team: e.team as 'home' | 'away',
        start_time: e.start_time || '',
        end_time: e.end_time,
        zone: e.zone,
        success: e.success,
        strength: e.strength || '5v5',
        detail1: e.detail1,
        detail2: e.detail2,
        isHighlight: e.is_highlight || false,
        players: e.players ? JSON.parse(e.players) : [],
        puckXY: e.puck_xy ? JSON.parse(e.puck_xy) : [],
        netXY: e.net_xy ? JSON.parse(e.net_xy) : undefined
      }))

      const shifts: Shift[] = (shiftsData || []).map((s: any, idx: number) => ({
        idx,
        period: s.period || 1,
        start_time: s.start_time || '',
        end_time: s.end_time,
        start_type: s.start_type,
        stop_type: s.stop_type,
        strength: s.strength || '5v5',
        home: s.home_lineup ? JSON.parse(s.home_lineup) : undefined,
        away: s.away_lineup ? JSON.parse(s.away_lineup) : undefined
      }))

      // Export with video information
      await exportToExcel(
        game.game_id,
        game.home_team,
        game.away_team,
        events,
        shifts,
        { 1: 18, 2: 18, 3: 18, OT: 5 },
        true,
        game.videos
      )

      // Also create a video export file
      const videoExport = {
        game_id: game.game_id,
        home_team: game.home_team,
        away_team: game.away_team,
        game_date: game.game_date,
        videos: game.videos,
        export_date: new Date().toISOString()
      }

      // Download video data as JSON
      const blob = new Blob([JSON.stringify(videoExport, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${game.game_id}_videos_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`
      a.click()
      URL.revokeObjectURL(url)

      toast('Exported tracking data and video links', 'success')
    } catch (error: any) {
      toast(`Export error: ${error.message}`, 'error')
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
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Video Management</h1>
            <p className="text-muted-foreground mt-2">
              Store YouTube video links and details for games, then export
            </p>
          </div>
          <Button onClick={() => router.push('/tracker')} variant="outline">
            ← Back to Tracker
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

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Games List */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Games</h2>
            
            {isLoading ? (
              <div className="text-center py-12 text-muted-foreground">
                Loading games...
              </div>
            ) : filteredGames.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">
                No games found
              </div>
            ) : (
              <div className="space-y-2 max-h-[600px] overflow-y-auto">
                {filteredGames.map((game) => (
                  <div
                    key={game.game_id}
                    className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                      selectedGame?.game_id === game.game_id
                        ? 'border-primary bg-primary/5'
                        : 'border-border hover:bg-muted'
                    }`}
                    onClick={() => setSelectedGame(game)}
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
                        <div className="text-xs text-muted-foreground mt-1">
                          {game.videos.length} video{game.videos.length !== 1 ? 's' : ''}
                        </div>
                      </div>
                      <Button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleExport(game)
                        }}
                        size="sm"
                        variant="outline"
                      >
                        Export
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Video Management */}
          <div className="space-y-4">
            {selectedGame ? (
              <>
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold">
                    Videos for {selectedGame.home_team} vs {selectedGame.away_team}
                  </h2>
                  <Button onClick={() => setSelectedGame(null)} variant="ghost" size="sm">
                    Clear
                  </Button>
                </div>

                {/* Add Video Form */}
                <div className="border rounded-lg p-4 space-y-3 bg-card">
                  <h3 className="font-semibold text-sm">Add Video</h3>
                  
                  <div>
                    <label className="text-xs text-muted-foreground block mb-1">Video URL</label>
                    <input
                      type="text"
                      value={videoUrl}
                      onChange={(e) => setVideoUrl(e.target.value)}
                      placeholder="https://youtube.com/watch?v=..."
                      className="w-full px-3 py-2 text-sm bg-input border border-border rounded"
                    />
                  </div>

                  <div>
                    <label className="text-xs text-muted-foreground block mb-1">Video Type</label>
                    <select
                      value={videoType}
                      onChange={(e) => setVideoType(e.target.value as any)}
                      className="w-full px-3 py-2 text-sm bg-input border border-border rounded"
                    >
                      <option value="youtube">YouTube</option>
                      <option value="local">Local File</option>
                      <option value="other">Other</option>
                    </select>
                  </div>

                  <div>
                    <label className="text-xs text-muted-foreground block mb-1">Title (optional)</label>
                    <input
                      type="text"
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                      placeholder="e.g., Period 1 Highlights"
                      className="w-full px-3 py-2 text-sm bg-input border border-border rounded"
                    />
                  </div>

                  <div>
                    <label className="text-xs text-muted-foreground block mb-1">Description (optional)</label>
                    <textarea
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      placeholder="Video description or notes"
                      rows={2}
                      className="w-full px-3 py-2 text-sm bg-input border border-border rounded"
                    />
                  </div>

                  <div className="grid grid-cols-3 gap-2">
                    <div>
                      <label className="text-xs text-muted-foreground block mb-1">Period</label>
                      <select
                        value={period}
                        onChange={(e) => setPeriod(e.target.value ? Number(e.target.value) : '')}
                        className="w-full px-2 py-2 text-sm bg-input border border-border rounded"
                      >
                        <option value="">All</option>
                        <option value="1">Period 1</option>
                        <option value="2">Period 2</option>
                        <option value="3">Period 3</option>
                        <option value="4">OT</option>
                      </select>
                    </div>
                    <div>
                      <label className="text-xs text-muted-foreground block mb-1">Start Time</label>
                      <input
                        type="text"
                        value={startTime}
                        onChange={(e) => setStartTime(e.target.value)}
                        placeholder="00:00"
                        className="w-full px-2 py-2 text-sm bg-input border border-border rounded"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-muted-foreground block mb-1">End Time</label>
                      <input
                        type="text"
                        value={endTime}
                        onChange={(e) => setEndTime(e.target.value)}
                        placeholder="20:00"
                        className="w-full px-2 py-2 text-sm bg-input border border-border rounded"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="text-xs text-muted-foreground block mb-1">Notes (optional)</label>
                    <textarea
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      placeholder="Additional notes about this video"
                      rows={2}
                      className="w-full px-3 py-2 text-sm bg-input border border-border rounded"
                    />
                  </div>

                  <Button onClick={handleAddVideo} className="w-full">
                    Add Video
                  </Button>
                </div>

                {/* Videos List */}
                <div className="space-y-2">
                  <h3 className="font-semibold text-sm">Videos ({selectedGame.videos.length})</h3>
                  
                  {selectedGame.videos.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground text-sm">
                      No videos added yet
                    </div>
                  ) : (
                    <div className="space-y-2 max-h-[400px] overflow-y-auto">
                      {selectedGame.videos.map((video) => (
                        <div
                          key={video.id}
                          className="border rounded-lg p-3 bg-card"
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              {video.video_type === 'youtube' && video.video_id ? (
                                <a
                                  href={video.video_url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-blue-500 hover:underline text-sm font-medium"
                                >
                                  {video.title || `YouTube Video (${video.video_id})`}
                                </a>
                              ) : (
                                <div className="text-sm font-medium">
                                  {video.title || video.video_url}
                                </div>
                              )}
                              
                              <div className="text-xs text-muted-foreground mt-1">
                                {video.period && `Period ${video.period} • `}
                                {video.start_time && video.end_time
                                  ? `${video.start_time} - ${video.end_time}`
                                  : video.start_time || 'Full video'}
                              </div>
                              
                              {video.description && (
                                <div className="text-xs text-muted-foreground mt-1">
                                  {video.description}
                                </div>
                              )}
                              
                              {video.notes && (
                                <div className="text-xs text-muted-foreground mt-1 italic">
                                  {video.notes}
                                </div>
                              )}
                            </div>
                            
                            <Button
                              onClick={() => video.id && handleDeleteVideo(video.id)}
                              variant="ghost"
                              size="sm"
                              className="text-red-500 hover:text-red-700"
                            >
                              Delete
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div className="text-center py-12 text-muted-foreground">
                Select a game to manage videos
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
