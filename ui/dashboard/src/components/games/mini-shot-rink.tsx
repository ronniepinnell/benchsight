'use client'

import { cn } from '@/lib/utils'

interface MiniShotRinkProps {
  shotX: number | null  // X coordinate in feet (-100 to +100, from center ice)
  shotY: number | null  // Y coordinate in feet (-42.5 to +42.5, rink width)
  isGoal: boolean
  className?: string
}

/**
 * Real hockey rink dimensions:
 * - Full rink: 200 feet long x 85 feet wide
 * - Center ice to goal line: ~89 feet
 * - Coordinates in data: X from -100 to +100 (length), Y from -42.5 to +42.5 (width)
 *
 * We show a half-rink view (offensive zone) looking down at the net
 */

// SVG dimensions for the mini rink display
const SVG_WIDTH = 200
const SVG_HEIGHT = 140

// Rink coordinate bounds (feet)
const RINK_X_MAX = 100   // Behind the net (center ice is 0)
const RINK_Y_MIN = -42.5 // Left boards
const RINK_Y_MAX = 42.5  // Right boards

// Goal line position from center ice (feet)
const GOAL_LINE_X = 89

export function MiniShotRink({
  shotX,
  shotY,
  isGoal,
  className
}: MiniShotRinkProps) {
  // Convert rink coordinates (feet) to SVG pixels
  // X in data: distance from center ice (negative = one end, positive = other end)
  // Y in data: width position (negative = left, positive = right looking down rink)

  const hasShotLocation = shotX !== null && shotY !== null &&
    !isNaN(shotX) && !isNaN(shotY)

  // Normalize X to always show attacking the same net (use absolute value)
  const absX = hasShotLocation ? Math.abs(shotX) : 0

  // Map rink feet to SVG pixels
  // X: 0 (center ice / top of view) to 100 (behind net / bottom of view)
  // Y: -42.5 (left) to +42.5 (right)
  const mapX = (x: number) => (x / RINK_X_MAX) * SVG_HEIGHT
  const mapY = (y: number) => ((y - RINK_Y_MIN) / (RINK_Y_MAX - RINK_Y_MIN)) * SVG_WIDTH

  // Shot position in SVG coordinates
  const shotPixelX = hasShotLocation ? mapY(shotY) : 0  // Y becomes horizontal
  const shotPixelY = hasShotLocation ? mapX(absX) : 0   // X becomes vertical (depth)

  // Key rink positions in SVG
  const goalLineY = mapX(GOAL_LINE_X)  // ~89 feet from center
  const blueLineY = mapX(25)           // Blue line ~25 feet from center
  const centerX = SVG_WIDTH / 2

  // Net dimensions and position (at goal line)
  const netWidth = 24
  const netHeight = 8
  const netX = (SVG_WIDTH - netWidth) / 2
  const netY = goalLineY

  // Crease semicircle (6 foot radius from center of goal)
  const creaseRadius = (6 / RINK_X_MAX) * SVG_HEIGHT

  // Faceoff circles (offensive zone dots at ~20 feet from goal line, 22 feet from center)
  const faceoffY = mapX(GOAL_LINE_X - 20)
  const faceoffLeftX = mapY(-22)
  const faceoffRightX = mapY(22)
  const faceoffDotRadius = 4

  return (
    <div className={cn('relative', className)}>
      <svg
        width={SVG_WIDTH}
        height={SVG_HEIGHT}
        viewBox={`0 0 ${SVG_WIDTH} ${SVG_HEIGHT}`}
        className="bg-slate-900/60 rounded-lg"
      >
        {/* Ice surface */}
        <rect
          x={4}
          y={4}
          width={SVG_WIDTH - 8}
          height={SVG_HEIGHT - 8}
          rx={16}
          fill="rgba(226, 232, 240, 0.05)"
          stroke="currentColor"
          strokeWidth={2}
          className="text-slate-600"
        />

        {/* Blue line */}
        <line
          x1={8}
          y1={blueLineY}
          x2={SVG_WIDTH - 8}
          y2={blueLineY}
          stroke="currentColor"
          strokeWidth={3}
          className="text-blue-500/60"
        />

        {/* Goal line */}
        <line
          x1={8}
          y1={goalLineY}
          x2={SVG_WIDTH - 8}
          y2={goalLineY}
          stroke="currentColor"
          strokeWidth={2}
          className="text-red-500/50"
        />

        {/* Center line marker (partial, at top) */}
        <line
          x1={centerX}
          y1={4}
          x2={centerX}
          y2={20}
          stroke="currentColor"
          strokeWidth={2}
          className="text-red-500/40"
        />

        {/* Crease (goalie area - semicircle in front of net) */}
        <path
          d={`M ${netX - 4} ${netY}
              A ${creaseRadius} ${creaseRadius} 0 0 1 ${netX + netWidth + 4} ${netY}`}
          fill="rgba(59, 130, 246, 0.15)"
          stroke="currentColor"
          strokeWidth={1.5}
          className="text-blue-400/60"
        />

        {/* Faceoff circles (just the dots) */}
        <circle
          cx={faceoffLeftX}
          cy={faceoffY}
          r={faceoffDotRadius}
          fill="currentColor"
          className="text-red-500/70"
        />
        <circle
          cx={faceoffRightX}
          cy={faceoffY}
          r={faceoffDotRadius}
          fill="currentColor"
          className="text-red-500/70"
        />

        {/* Net frame */}
        <rect
          x={netX}
          y={netY}
          width={netWidth}
          height={netHeight}
          fill="rgba(0, 0, 0, 0.3)"
          stroke="currentColor"
          strokeWidth={2}
          className={isGoal ? 'text-green-500' : 'text-slate-400'}
        />

        {/* Net crossbar (front edge) */}
        <line
          x1={netX}
          y1={netY}
          x2={netX + netWidth}
          y2={netY}
          stroke="currentColor"
          strokeWidth={3}
          className={isGoal ? 'text-green-400' : 'text-slate-400'}
        />

        {/* Shot location marker */}
        {hasShotLocation && (
          <g>
            {/* Shot trail to net center (for goals) */}
            {isGoal && (
              <line
                x1={shotPixelX}
                y1={shotPixelY}
                x2={centerX}
                y2={netY}
                stroke="currentColor"
                strokeWidth={1.5}
                strokeDasharray="4,4"
                className="text-green-500/60"
              />
            )}

            {/* Shot location glow */}
            <circle
              cx={shotPixelX}
              cy={shotPixelY}
              r={12}
              fill={isGoal ? 'rgba(34, 197, 94, 0.2)' : 'rgba(59, 130, 246, 0.2)'}
            />

            {/* Shot marker */}
            <circle
              cx={shotPixelX}
              cy={shotPixelY}
              r={7}
              fill={isGoal ? 'rgb(34, 197, 94)' : 'rgb(59, 130, 246)'}
              stroke="white"
              strokeWidth={2}
            />

            {/* Inner dot for goals */}
            {isGoal && (
              <circle
                cx={shotPixelX}
                cy={shotPixelY}
                r={2.5}
                fill="white"
              />
            )}

            {/* Distance label */}
            <text
              x={shotPixelX}
              y={shotPixelY - 14}
              textAnchor="middle"
              className="fill-slate-400 text-[10px] font-mono"
            >
              {Math.round(GOAL_LINE_X - absX)}ft
            </text>
          </g>
        )}

        {/* No location label */}
        {!hasShotLocation && (
          <text
            x={SVG_WIDTH / 2}
            y={SVG_HEIGHT / 2}
            textAnchor="middle"
            className="fill-slate-500 text-xs"
          >
            No location data
          </text>
        )}

        {/* Zone labels */}
        <text
          x={SVG_WIDTH / 2}
          y={blueLineY - 6}
          textAnchor="middle"
          className="fill-slate-500 text-[9px] font-medium uppercase tracking-wider"
        >
          Offensive Zone
        </text>
      </svg>
    </div>
  )
}
