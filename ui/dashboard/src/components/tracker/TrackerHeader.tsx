'use client'

/**
 * Tracker Header Component
 * 
 * Header bar with game info, clock, score, period selector
 */

import { useState } from 'react'
import { useTrackerStore } from '@/lib/tracker/state'
import { exportToExcel } from '@/lib/tracker/export'
import { saveGameStateToSupabase } from '@/lib/tracker/sync'
import { Button } from '@/components/ui/button'
import { toast } from '@/lib/tracker/utils/toast'
import { Period } from '@/lib/tracker/types'

export function TrackerHeader() {
  const {
    gameId,
    homeTeam,
    awayTeam,
    period,
    clock,
    score,
    events,
    shifts,
    periodLengths,
    homeAttacksRightP1,
    setPeriod
  } = useTrackerStore()
  
  const [isSyncing, setIsSyncing] = useState(false)

  const handleExport = async () => {
    if (!gameId) {
      toast('No game loaded', 'error')
      return
    }
    
    try {
      await exportToExcel(
        String(gameId),
        homeTeam,
        awayTeam,
        events,
        shifts,
        periodLengths,
        homeAttacksRightP1
      )
      toast('Export successful', 'success')
    } catch (error: any) {
      toast(error.message || 'Export failed', 'error')
    }
  }

  const handleSync = async () => {
    if (!gameId) {
      toast('No game loaded', 'error')
      return
    }

    setIsSyncing(true)
    try {
      const gameState = useTrackerStore.getState()
      const result = await saveGameStateToSupabase(gameState)
      
      if (result.success) {
        toast(result.message, 'success')
      } else {
        toast(result.message, 'error')
      }
    } catch (error: any) {
      toast(`Sync failed: ${error.message}`, 'error')
    } finally {
      setIsSyncing(false)
    }
  }

  if (!gameId) {
    return (
      <div className="px-4 py-2 border-b">
        <p className="text-sm text-muted-foreground">No game loaded</p>
      </div>
    )
  }

  return (
    <div className="px-4 py-2 flex items-center gap-4">
      {/* Game info */}
      <div className="flex items-center gap-2">
        <span className="text-sm font-semibold">{homeTeam}</span>
        <span className="text-sm text-muted-foreground">vs</span>
        <span className="text-sm font-semibold">{awayTeam}</span>
      </div>

      {/* Period selector */}
      <div className="flex gap-1">
        {[1, 2, 3, 4].map((p) => (
          <Button
            key={p}
            variant={period === p ? 'default' : 'outline'}
            size="sm"
            onClick={() => setPeriod(p as Period)}
            className="h-7 px-2 text-xs"
          >
            {p === 4 ? 'OT' : `P${p}`}
          </Button>
        ))}
      </div>

      {/* Clock */}
      <div className="ml-auto flex items-center gap-4">
        <div className="text-lg font-mono font-bold">{clock}</div>
        
        {/* Score */}
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-blue-500">{score.home}</span>
          <span className="text-sm text-muted-foreground">-</span>
          <span className="text-sm font-semibold text-red-500">{score.away}</span>
        </div>
        
        {/* Sync Button */}
        <Button
          onClick={handleSync}
          variant="outline"
          size="sm"
          className="h-7 px-3 text-xs"
          disabled={isSyncing}
        >
          {isSyncing ? '⏳ Syncing...' : '☁️ Sync'}
        </Button>
        
        {/* Export Button */}
        <Button
          onClick={handleExport}
          variant="outline"
          size="sm"
          className="h-7 px-3 text-xs"
        >
          📥 Export
        </Button>
      </div>
    </div>
  )
}
