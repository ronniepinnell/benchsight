/**
 * Hook to load game data and roster from Supabase
 */

import { useEffect, useState } from 'react'
import { useTrackerStore } from '../state'
import { loadGameRoster, loadGameData, loadTrackingData } from '../supabase'
import { loadEventsFromSupabase, loadShiftsFromSupabase } from '../sync'
import { toast } from '../utils/toast'
import { processAllGoalsForAssists } from '../utils/assists'

export function useLoadGame(gameId: string | number | null) {
  const { setGame, setRosters } = useTrackerStore()
  const [isLoading, setIsLoading] = useState(false)
  const [isLoaded, setIsLoaded] = useState(false)

  useEffect(() => {
    if (!gameId) return

    const gameIdStr = String(gameId)
    
    // Reset loaded state when gameId changes
    setIsLoaded(false)

    const loadData = async () => {
      setIsLoading(true)

      try {
        // Load game metadata
        const gameData = await loadGameData(gameIdStr)
        if (gameData) {
          setGame(
            parseInt(gameIdStr),
            gameData.homeTeam,
            gameData.awayTeam
          )

          // Set scores if available
          if (gameData.homeScore !== undefined || gameData.awayScore !== undefined) {
            useTrackerStore.setState({
              score: {
                home: gameData.homeScore || 0,
                away: gameData.awayScore || 0
              }
            })
          }

          toast(`Loaded game: ${gameData.homeTeam} vs ${gameData.awayTeam}`, 'success')
        } else {
          toast(`Game ${gameIdStr} not found`, 'error')
        }

        // Load roster
        const rosters = await loadGameRoster(gameIdStr)
        if (rosters.home.length > 0 || rosters.away.length > 0) {
          setRosters(rosters.home, rosters.away)
          toast(`Loaded ${rosters.home.length + rosters.away.length} players`, 'success')
        } else {
          toast('No roster found - you can manually add players', 'warning')
        }

        // Load tracking data from Supabase
        const cloudEvents = await loadEventsFromSupabase(gameIdStr)
        const cloudShifts = await loadShiftsFromSupabase(gameIdStr)
        
        if (cloudEvents.length > 0 || cloudShifts.length > 0) {
          // Load from cloud if available, otherwise try localStorage
          const state = useTrackerStore.getState()
          
          if (cloudEvents.length > 0) {
            // v23.8: Process all goals to detect and link assists after loading
            // Note: processAllGoalsForAssists modifies events in-place
            const autoLinked = processAllGoalsForAssists(cloudEvents, true)
            
            useTrackerStore.setState({ events: cloudEvents })
            toast(`Loaded ${cloudEvents.length} events from cloud`, 'success')
            
            if (autoLinked > 0) {
              toast(`Auto-linked ${autoLinked} assist(s) for goals`, 'success')
            }
          }
          
          if (cloudShifts.length > 0) {
            useTrackerStore.setState({ shifts: cloudShifts })
            toast(`Loaded ${cloudShifts.length} shifts from cloud`, 'success')
          }
        } else {
          // Fallback: try loading from localStorage
          const saved = localStorage.getItem(`bs_tracker_${gameIdStr}`)
          if (saved) {
            try {
              const gameState = JSON.parse(saved)
              if (gameState.events?.length > 0 || gameState.shifts?.length > 0) {
                const loadedEvents = gameState.events || []
                
                // v23.8: Process all goals to detect and link assists after loading
                // Note: processAllGoalsForAssists modifies events in-place
                const autoLinked = processAllGoalsForAssists(loadedEvents, true)
                
                useTrackerStore.setState({
                  events: loadedEvents,
                  shifts: gameState.shifts || []
                })
                toast('Loaded from local storage', 'info')
                
                if (autoLinked > 0) {
                  toast(`Auto-linked ${autoLinked} assist(s) for goals`, 'success')
                }
              }
            } catch (error) {
              console.error('Error loading from localStorage:', error)
            }
          }
        }

        setIsLoaded(true)
      } catch (error: any) {
        console.error('Error loading game:', error)
        toast(`Error loading game: ${error.message}`, 'error')
      } finally {
        setIsLoading(false)
      }
    }

    loadData()
  }, [gameId, isLoaded, setGame, setRosters])

  return { isLoading, isLoaded }
}
