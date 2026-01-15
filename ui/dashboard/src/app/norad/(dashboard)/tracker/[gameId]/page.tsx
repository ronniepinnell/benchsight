/**
 * BenchSight Game Tracker - Game-specific tracker page
 * 
 * Main tracker interface for a specific game
 */

'use client'

import { useEffect } from 'react'
import { TrackerLayout } from '@/components/tracker/TrackerLayout'
import { TrackerHeader } from '@/components/tracker/TrackerHeader'
import { TrackerPanel } from '@/components/tracker/TrackerPanel'
import { Rink } from '@/components/tracker/Rink'
import { EventForm } from '@/components/tracker/EventForm'
import { EventList } from '@/components/tracker/EventList'
import { ShiftPanel } from '@/components/tracker/ShiftPanel'
import { useKeyboardShortcuts } from '@/lib/tracker/hooks/useKeyboardShortcuts'
import { useAutoSave } from '@/lib/tracker/hooks/useAutoSave'
import { useLoadGame } from '@/lib/tracker/hooks/useLoadGame'
import { useTrackerStore } from '@/lib/tracker/state'

interface TrackerGamePageProps {
  params: {
    gameId: string
  }
}

export default function TrackerGamePage({ params }: TrackerGamePageProps) {
  const gameId = parseInt(params.gameId)
  const { setGame, gameId: currentGameId } = useTrackerStore()

  // Enable keyboard shortcuts
  useKeyboardShortcuts()

  // Enable auto-save
  useAutoSave(gameId)

  // Load game data and roster from Supabase
  const { isLoading } = useLoadGame(gameId)

  useEffect(() => {
    if (gameId && gameId !== currentGameId) {
      // Game will be loaded by useLoadGame hook
      // Just ensure state is initialized
    }
  }, [gameId, currentGameId])

  return (
    <TrackerLayout header={<TrackerHeader />}>
      <div className="flex h-full">
        {/* Left Panel: Shifts */}
        <TrackerPanel title="Shifts & Lineups" className="w-72">
          <ShiftPanel />
        </TrackerPanel>

        {/* Center: Rink & Events */}
        <div className="flex-1 flex flex-col bg-background">
          {/* Rink */}
          <div className="flex-1 min-h-0 p-4">
            <Rink />
          </div>
          
          {/* Event List */}
          <div className="h-64 border-t bg-card">
            <EventList />
          </div>
        </div>

        {/* Right Panel: Event Form */}
        <TrackerPanel title="Event Entry" className="w-80">
          <EventForm />
        </TrackerPanel>
      </div>
    </TrackerLayout>
  )
}
