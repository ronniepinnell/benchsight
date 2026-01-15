'use client'

import { useState, useMemo } from 'react'
import { Filter, Target } from 'lucide-react'
import { cn } from '@/lib/utils'
import { ShotHeatmap } from './shot-heatmap'
import { SearchableSelect, SearchableSelectOption } from '@/components/common/searchable-select'

interface Shot {
  x_coord?: number
  y_coord?: number
  shot_x?: number
  shot_y?: number
  is_goal?: boolean
  shot_result?: string
  xg?: number
  danger_zone?: string
  danger_level?: string
  period?: number
  strength?: string
  player_id?: string
  player_name?: string
  event_type?: string
}

interface EnhancedShotMapProps {
  shots: Shot[]
  width?: number
  height?: number
  showFilters?: boolean
  title?: string
}

export function EnhancedShotMap({ 
  shots, 
  width = 600, 
  height = 250,
  showFilters = true,
  title = 'Shot Map'
}: EnhancedShotMapProps) {
  const [selectedPeriod, setSelectedPeriod] = useState<number | 'all'>('all')
  const [selectedStrength, setSelectedStrength] = useState<string>('all')
  const [selectedPlayer, setSelectedPlayer] = useState<string>('all')
  const [showGoalsOnly, setShowGoalsOnly] = useState(false)

  // Get unique values for filters
  const periods = useMemo(() => {
    const unique = [...new Set(shots.map(s => s.period).filter(Boolean))]
    return unique.sort((a, b) => (a || 0) - (b || 0))
  }, [shots])

  const strengths = useMemo(() => {
    const unique = [...new Set(shots.map(s => s.strength).filter(Boolean))]
    return unique.sort()
  }, [shots])

  const players = useMemo(() => {
    const unique = [...new Set(shots.map(s => s.player_name).filter(Boolean))]
    return unique.sort()
  }, [shots])

  // Filter shots based on selected filters
  const filteredShots = useMemo(() => {
    return shots.filter(shot => {
      if (selectedPeriod !== 'all' && shot.period !== selectedPeriod) return false
      if (selectedStrength !== 'all' && shot.strength !== selectedStrength) return false
      if (selectedPlayer !== 'all' && shot.player_name !== selectedPlayer) return false
      if (showGoalsOnly && !shot.is_goal && shot.shot_result !== 'Goal') return false
      return true
    })
  }, [shots, selectedPeriod, selectedStrength, selectedPlayer, showGoalsOnly])

  const goals = filteredShots.filter(s => s.is_goal || s.shot_result === 'Goal')
  const totalShots = filteredShots.length
  const totalGoals = goals.length
  const shootingPct = totalShots > 0 ? ((totalGoals / totalShots) * 100).toFixed(1) : '0.0'

  return (
    <div className="bg-card rounded-xl border border-border overflow-hidden">
      <div className="px-4 py-3 bg-accent border-b border-border">
        <div className="flex items-center justify-between">
          <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
            <Target className="w-4 h-4" />
            {title}
          </h2>
          {showFilters && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Filter className="w-3 h-3" />
              <span>{filteredShots.length} shots</span>
              {totalGoals > 0 && (
                <>
                  <span>•</span>
                  <span className="text-goal">{totalGoals} goals ({shootingPct}%)</span>
                </>
              )}
            </div>
          )}
        </div>
      </div>

      {showFilters && (
        <div className="px-4 py-3 border-b border-border bg-muted/20">
          <div className="flex flex-wrap items-center gap-4">
            {/* Period Filter */}
            {periods.length > 0 && (
              <div className="flex items-center gap-2">
                <label className="text-xs font-mono text-muted-foreground uppercase">Period:</label>
                <SearchableSelect
                  options={[
                    { value: 'all', label: 'All', searchText: 'all' },
                    ...periods.map(p => ({
                      value: String(p),
                      label: `P${p}`,
                      searchText: `period ${p}`,
                    })),
                  ]}
                  value={selectedPeriod === 'all' ? 'all' : String(selectedPeriod)}
                  onChange={(val) => setSelectedPeriod(val === 'all' ? 'all' : Number(val))}
                  placeholder="All"
                  className="min-w-[100px]"
                />
              </div>
            )}

            {/* Strength Filter */}
            {strengths.length > 0 && (
              <div className="flex items-center gap-2">
                <label className="text-xs font-mono text-muted-foreground uppercase">Strength:</label>
                <SearchableSelect
                  options={[
                    { value: 'all', label: 'All', searchText: 'all' },
                    ...strengths.map(s => ({
                      value: s,
                      label: s,
                      searchText: s,
                    })),
                  ]}
                  value={selectedStrength}
                  onChange={setSelectedStrength}
                  placeholder="All"
                  className="min-w-[100px]"
                />
              </div>
            )}

            {/* Player Filter */}
            {players.length > 0 && players.length <= 20 && (
              <div className="flex items-center gap-2">
                <label className="text-xs font-mono text-muted-foreground uppercase">Player:</label>
                <SearchableSelect
                  options={[
                    { value: 'all', label: 'All Players', searchText: 'all players' },
                    ...players.map(p => ({
                      value: p,
                      label: p,
                      searchText: p,
                    })),
                  ]}
                  value={selectedPlayer}
                  onChange={setSelectedPlayer}
                  placeholder="All Players"
                  className="min-w-[150px]"
                />
              </div>
            )}

            {/* Goals Only Toggle */}
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="goals-only"
                checked={showGoalsOnly}
                onChange={(e) => setShowGoalsOnly(e.target.checked)}
                className="w-4 h-4 rounded border-border"
              />
              <label htmlFor="goals-only" className="text-xs font-mono text-muted-foreground uppercase cursor-pointer">
                Goals Only
              </label>
            </div>

            {/* Reset Filters */}
            {(selectedPeriod !== 'all' || selectedStrength !== 'all' || selectedPlayer !== 'all' || showGoalsOnly) && (
              <button
                onClick={() => {
                  setSelectedPeriod('all')
                  setSelectedStrength('all')
                  setSelectedPlayer('all')
                  setShowGoalsOnly(false)
                }}
                className="text-xs text-muted-foreground hover:text-foreground transition-colors"
              >
                Reset
              </button>
            )}
          </div>
        </div>
      )}

      <div className="p-6">
        {filteredShots.length > 0 ? (
          <ShotHeatmap
            shots={filteredShots}
            width={width}
            height={height}
            showGoals={true}
            showXG={true}
          />
        ) : (
          <div className="bg-muted/30 rounded-lg p-8 text-center" style={{ width, height }}>
            <p className="text-sm text-muted-foreground">No shots match the selected filters</p>
          </div>
        )}
      </div>
    </div>
  )
}
