'use client'

import { useMemo } from 'react'
import { cn } from '@/lib/utils'

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
}

interface ShotHeatmapProps {
  shots: Shot[]
  width?: number
  height?: number
  showGoals?: boolean
  showXG?: boolean
}

// Rink dimensions (normalized to 0-1, then scaled)
const RINK_WIDTH = 200
const RINK_HEIGHT = 85
const NET_WIDTH = 6
const NET_HEIGHT = 4
const NET_Y = RINK_HEIGHT - 2 // Position of net at bottom

export function ShotHeatmap({ 
  shots, 
  width = 400, 
  height = 170,
  showGoals = true,
  showXG = false
}: ShotHeatmapProps) {
  const processedShots = useMemo(() => {
    return shots
      .map(shot => {
        // Handle both coordinate formats
        const x = shot.x_coord ?? shot.shot_x ?? null
        const y = shot.y_coord ?? shot.shot_y ?? null
        
        if (x === null || y === null) return null
        
        // Normalize coordinates (assuming they're in 0-1 range or need conversion)
        // If coordinates are already in rink space, use them directly
        const normalizedX = typeof x === 'number' ? x : parseFloat(String(x)) || 0
        const normalizedY = typeof y === 'number' ? y : parseFloat(String(y)) || 0
        
        // Convert to pixel coordinates
        const pixelX = normalizedX * width
        const pixelY = normalizedY * height
        
        return {
          x: pixelX,
          y: pixelY,
          isGoal: shot.is_goal || shot.shot_result === 'Goal',
          xg: shot.xg ? (typeof shot.xg === 'number' ? shot.xg : parseFloat(String(shot.xg))) : 0,
          dangerZone: shot.danger_zone || shot.danger_level || 'medium'
        }
      })
      .filter((shot): shot is NonNullable<typeof shot> => shot !== null)
  }, [shots, width, height])

  const goals = processedShots.filter(s => s.isGoal)
  const shotsOnGoal = processedShots.filter(s => !s.isGoal)
  const totalXG = processedShots.reduce((sum, s) => sum + s.xg, 0)

  if (processedShots.length === 0) {
    return (
      <div className="bg-muted/30 rounded-lg p-8 text-center">
        <p className="text-sm text-muted-foreground">No shot data available</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Stats Summary */}
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center gap-4">
          <div>
            <span className="text-muted-foreground">Total Shots: </span>
            <span className="font-semibold">{processedShots.length}</span>
          </div>
          {showGoals && (
            <div>
              <span className="text-muted-foreground">Goals: </span>
              <span className="font-semibold text-goal">{goals.length}</span>
            </div>
          )}
          {showXG && (
            <div>
              <span className="text-muted-foreground">xG: </span>
              <span className="font-semibold">{totalXG.toFixed(2)}</span>
            </div>
          )}
        </div>
      </div>

      {/* Heatmap Canvas */}
      <div className="relative bg-muted/20 rounded-lg overflow-hidden" style={{ width, height }}>
        {/* Rink Background */}
        <svg width={width} height={height} className="absolute inset-0">
          {/* Rink outline */}
          <rect
            x="0"
            y="0"
            width={width}
            height={height}
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            className="text-border opacity-30"
          />
          
          {/* Center line */}
          <line
            x1={width / 2}
            y1={0}
            x2={width / 2}
            y2={height}
            stroke="currentColor"
            strokeWidth="1"
            className="text-border opacity-20"
          />
          
          {/* Net */}
          <rect
            x={(width - NET_WIDTH) / 2}
            y={height - NET_Y}
            width={NET_WIDTH}
            height={NET_HEIGHT}
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            className="text-goal"
          />
        </svg>

        {/* Shot markers */}
        {processedShots.map((shot, idx) => {
          const size = shot.isGoal ? 8 : 4
          const opacity = shot.isGoal ? 1 : 0.6
          const color = shot.isGoal 
            ? 'rgb(239, 68, 68)' // red for goals
            : shot.xg > 0.3
            ? 'rgb(251, 191, 36)' // yellow for high xG
            : 'rgb(59, 130, 246)' // blue for regular shots

          return (
            <div
              key={idx}
              className="absolute rounded-full border-2 border-white"
              style={{
                left: `${shot.x - size / 2}px`,
                top: `${shot.y - size / 2}px`,
                width: `${size}px`,
                height: `${size}px`,
                backgroundColor: color,
                opacity,
                transform: 'translate(-50%, -50%)'
              }}
              title={`${shot.isGoal ? 'Goal' : 'Shot'} - xG: ${shot.xg.toFixed(2)}`}
            />
          )
        })}
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 text-xs text-muted-foreground">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-goal border border-white" />
          <span>Goal</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-yellow-500 border border-white opacity-60" />
          <span>High xG (&gt;0.3)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-blue-500 border border-white opacity-60" />
          <span>Shot</span>
        </div>
      </div>
    </div>
  )
}
