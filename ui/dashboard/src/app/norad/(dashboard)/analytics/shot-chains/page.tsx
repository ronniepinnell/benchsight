// src/app/(dashboard)/analytics/shot-chains/page.tsx
import Link from 'next/link'
import { createClient } from '@/lib/supabase/server'
import { ArrowLeft, Target, TrendingUp, BarChart3, Zap } from 'lucide-react'
import { cn } from '@/lib/utils'
import { PlayerPhoto } from '@/components/players/player-photo'
import { TeamLogo } from '@/components/teams/team-logo'

export const revalidate = 300

export const metadata = {
  title: 'Shot Chains Analysis | BenchSight Analytics',
  description: 'Shot sequence visualization and chain analysis',
}

export default async function ShotChainsPage() {
  const supabase = await createClient()
  
  // Get shot chain data from events
  // Shot chains are sequences of events leading to shots
  // Get all events (not just shots) to build chains
  const { data: allEvents } = await supabase
    .from('fact_events')
    .select('*')
    .order('game_id', { ascending: false })
    .order('time_start_total_seconds', { ascending: true })
    .limit(5000)
  
  // Get shots specifically
  const { data: shotEvents } = await supabase
    .from('fact_events')
    .select('*')
    .in('event_type', ['Shot', 'Goal'])
    .order('game_id', { ascending: false })
    .order('time_start_total_seconds', { ascending: true })
    .limit(1000)
  
  // Group shots by game
  const shotsByGame = new Map<number, any[]>()
  if (shotEvents) {
    for (const event of shotEvents) {
      const gameId = event.game_id
      if (!gameId) continue
      if (!shotsByGame.has(gameId)) {
        shotsByGame.set(gameId, [])
      }
      shotsByGame.get(gameId)!.push(event)
    }
  }
  
  // Build shot chains - trace back from shots using linked_event_key or sequence
  const shotChains: Array<{
    gameId: number
    shotEvent: any
    chainLength: number
    eventsBeforeShot: any[]
  }> = []
  
  if (allEvents && shotEvents) {
    // Create event map by event_key for quick lookup
    const eventMap = new Map<string, any>()
    allEvents.forEach(e => {
      if (e.event_key) {
        eventMap.set(String(e.event_key), e)
      }
    })
    
    // For each shot, try to build chain
    shotEvents.forEach(shot => {
      const chain: any[] = [shot]
      let currentEvent = shot
      let chainLength = 1
      const maxChainLength = 10 // Prevent infinite loops
      
      // Trace back using linked_event_key or sequence_index
      while (chainLength < maxChainLength) {
        const linkedKey = currentEvent.linked_event_key
        const sequenceIndex = currentEvent.sequence_index
        const playIndex = currentEvent.play_index
        
        let prevEvent: any = null
        
        // Try linked_event_key first
        if (linkedKey && eventMap.has(String(linkedKey))) {
          prevEvent = eventMap.get(String(linkedKey))
        }
        // Try sequence_index - 1
        else if (sequenceIndex && shot.game_id) {
          const prevSeqIndex = sequenceIndex - 1
          prevEvent = allEvents.find(e => 
            e.game_id === shot.game_id && 
            e.sequence_index === prevSeqIndex
          )
        }
        // Try play_index - 1
        else if (playIndex && shot.game_id) {
          const prevPlayIndex = playIndex - 1
          prevEvent = allEvents.find(e => 
            e.game_id === shot.game_id && 
            e.play_index === prevPlayIndex
          )
        }
        
        if (!prevEvent || prevEvent.event_type === 'Shot' || prevEvent.event_type === 'Goal') {
          break // Stop if we hit another shot or can't find previous event
        }
        
        chain.unshift(prevEvent) // Add to beginning of chain
        currentEvent = prevEvent
        chainLength++
      }
      
      shotChains.push({
        gameId: shot.game_id,
        shotEvent: shot,
        chainLength: chain.length,
        eventsBeforeShot: chain.slice(0, -1), // All events except the shot itself
      })
    })
  }
  
  // Analyze shot patterns
  const shotPatterns = {
    totalShots: shotEvents?.length || 0,
    totalGoals: shotEvents?.filter(e => e.is_goal || e.event_type === 'Goal').length || 0,
    avgShotsPerGame: shotsByGame.size > 0 ? (shotEvents?.length || 0) / shotsByGame.size : 0,
    totalChains: shotChains.length,
    avgChainLength: shotChains.length > 0 
      ? shotChains.reduce((sum, chain) => sum + chain.chainLength, 0) / shotChains.length 
      : 0,
  }
  
  // Analyze chain patterns
  const chainEventTypes = new Map<string, number>()
  shotChains.forEach(chain => {
    chain.eventsBeforeShot.forEach(event => {
      const eventType = event.event_type || 'Unknown'
      chainEventTypes.set(eventType, (chainEventTypes.get(eventType) || 0) + 1)
    })
  })
  
  return (
    <div className="space-y-6">
      {/* Back Link */}
      <Link 
        href="/norad/analytics/overview" 
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Analytics
      </Link>
      
      {/* Header */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="px-4 py-3 bg-accent border-b border-border">
          <h1 className="font-display text-lg font-semibold uppercase tracking-wider flex items-center gap-2">
            <Target className="w-5 h-5" />
            Shot Chains Analysis
          </h1>
        </div>
        <div className="p-6">
          <p className="text-sm text-muted-foreground mb-6">
            Analyze shot sequences and patterns. Shot chains show the sequence of events leading to shots and goals.
          </p>
          
          {/* Summary Stats */}
          <div className="grid md:grid-cols-4 gap-4 mb-6">
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Total Shots</div>
              <div className="font-mono text-2xl font-bold text-foreground">
                {shotPatterns.totalShots}
              </div>
            </div>
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Total Goals</div>
              <div className="font-mono text-2xl font-bold text-goal">
                {shotPatterns.totalGoals}
              </div>
            </div>
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Avg Shots/Game</div>
              <div className="font-mono text-2xl font-bold text-primary">
                {shotPatterns.avgShotsPerGame.toFixed(1)}
              </div>
            </div>
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Games Analyzed</div>
              <div className="font-mono text-2xl font-bold text-assist">
                {shotsByGame.size}
              </div>
            </div>
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Total Chains</div>
              <div className="font-mono text-2xl font-bold text-primary">
                {shotPatterns.totalChains}
              </div>
            </div>
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Avg Chain Length</div>
              <div className="font-mono text-2xl font-bold text-assist">
                {shotPatterns.avgChainLength.toFixed(1)}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Chain Event Types */}
      {chainEventTypes.size > 0 && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              Events Leading to Shots
            </h2>
          </div>
          <div className="p-6">
            <div className="grid md:grid-cols-4 gap-4 mb-6">
              {Array.from(chainEventTypes.entries())
                .sort((a, b) => b[1] - a[1])
                .slice(0, 8)
                .map(([eventType, count]) => (
                  <div key={eventType} className="bg-muted/30 rounded-lg p-4 text-center">
                    <div className="text-xs font-mono text-muted-foreground uppercase mb-1">{eventType}</div>
                    <div className="font-mono text-2xl font-bold text-foreground">{count}</div>
                  </div>
                ))}
            </div>
          </div>
        </div>
      )}
      
      {/* Sample Shot Chains */}
      {shotChains.length > 0 && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Zap className="w-4 h-4" />
              Sample Shot Chains
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {shotChains
                .filter(chain => chain.chainLength > 1)
                .slice(0, 10)
                .map((chain, index) => (
                  <div key={index} className="bg-muted/30 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs font-mono text-muted-foreground">
                        Game {chain.gameId} • Chain Length: {chain.chainLength}
                      </span>
                      {chain.shotEvent.is_goal && (
                        <span className="text-xs font-semibold text-goal">GOAL</span>
                      )}
                    </div>
                    <div className="flex items-center gap-2 flex-wrap">
                      {chain.eventsBeforeShot.map((event, idx) => (
                        <span key={idx} className="text-xs bg-card px-2 py-1 rounded">
                          {event.event_type || 'Event'}
                        </span>
                      ))}
                      <span className="text-xs bg-goal/20 text-goal px-2 py-1 rounded font-semibold">
                        {chain.shotEvent.is_goal ? 'GOAL' : 'SHOT'}
                      </span>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
