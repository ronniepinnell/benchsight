'use client'

import { cn } from '@/lib/utils'

interface NetFrontSVGProps {
  shotX: number | null   // net_x: 0-72 (inches, left to right facing goalie)
  shotY: number | null   // net_y: 0-48 (inches, bottom to top)
  isGoal: boolean
  className?: string
}

/**
 * Front-facing hockey net visualization.
 * Shows where a shot/goal hit the net from the shooter's perspective.
 *
 * Hockey net dimensions: 72 inches wide (6 feet) x 48 inches tall (4 feet)
 * Coordinate system from tracker: x 0-72, y 0-48
 */

// SVG dimensions
const SVG_WIDTH = 180
const SVG_HEIGHT = 130

// Net area within SVG (with padding for posts/labels)
const NET_LEFT = 20
const NET_TOP = 15
const NET_WIDTH = 140
const NET_HEIGHT = 95

// Real net dimensions in inches
const NET_INCHES_W = 72
const NET_INCHES_H = 48

export function NetFrontSVG({
  shotX,
  shotY,
  isGoal,
  className
}: NetFrontSVGProps) {
  const hasLocation = shotX !== null && shotY !== null &&
    !isNaN(shotX) && !isNaN(shotY)

  // Map net coordinates (inches) to SVG pixels
  // x: 0 (left) to 72 (right) → NET_LEFT to NET_LEFT + NET_WIDTH
  // y: 0 (bottom/ice) to 48 (top/crossbar) → NET_TOP + NET_HEIGHT (bottom) to NET_TOP (top)
  // Clamp to valid range to handle any data quality issues
  const clamp = (val: number, min: number, max: number) => Math.max(min, Math.min(max, val))
  const mapX = (x: number) => NET_LEFT + (clamp(x, 0, NET_INCHES_W) / NET_INCHES_W) * NET_WIDTH
  const mapY = (y: number) => NET_TOP + NET_HEIGHT - (clamp(y, 0, NET_INCHES_H) / NET_INCHES_H) * NET_HEIGHT

  const dotX = hasLocation ? mapX(shotX) : 0
  const dotY = hasLocation ? mapY(shotY) : 0

  // Net zone lines (thirds)
  const thirdW = NET_WIDTH / 3
  const thirdH = NET_HEIGHT / 2

  // Post dimensions
  const postWidth = 3

  return (
    <div className={cn('relative', className)}>
      <svg
        width={SVG_WIDTH}
        height={SVG_HEIGHT}
        viewBox={`0 0 ${SVG_WIDTH} ${SVG_HEIGHT}`}
        className="bg-slate-900/60 rounded-lg"
      >
        {/* Ice surface at bottom */}
        <rect
          x={0}
          y={NET_TOP + NET_HEIGHT}
          width={SVG_WIDTH}
          height={SVG_HEIGHT - NET_TOP - NET_HEIGHT}
          fill="rgba(226, 232, 240, 0.08)"
        />

        {/* Net mesh background */}
        <rect
          x={NET_LEFT}
          y={NET_TOP}
          width={NET_WIDTH}
          height={NET_HEIGHT}
          fill="rgba(148, 163, 184, 0.08)"
          rx={2}
        />

        {/* Net mesh grid lines - vertical */}
        {Array.from({ length: 9 }, (_, i) => {
          const x = NET_LEFT + ((i + 1) / 10) * NET_WIDTH
          return (
            <line
              key={`v${i}`}
              x1={x} y1={NET_TOP}
              x2={x} y2={NET_TOP + NET_HEIGHT}
              stroke="rgba(148, 163, 184, 0.15)"
              strokeWidth={0.5}
            />
          )
        })}

        {/* Net mesh grid lines - horizontal */}
        {Array.from({ length: 6 }, (_, i) => {
          const y = NET_TOP + ((i + 1) / 7) * NET_HEIGHT
          return (
            <line
              key={`h${i}`}
              x1={NET_LEFT} y1={y}
              x2={NET_LEFT + NET_WIDTH} y2={y}
              stroke="rgba(148, 163, 184, 0.15)"
              strokeWidth={0.5}
            />
          )
        })}

        {/* Zone divider lines (dotted) - vertical thirds */}
        <line
          x1={NET_LEFT + thirdW} y1={NET_TOP}
          x2={NET_LEFT + thirdW} y2={NET_TOP + NET_HEIGHT}
          stroke="rgba(148, 163, 184, 0.25)"
          strokeWidth={0.75}
          strokeDasharray="3,3"
        />
        <line
          x1={NET_LEFT + thirdW * 2} y1={NET_TOP}
          x2={NET_LEFT + thirdW * 2} y2={NET_TOP + NET_HEIGHT}
          stroke="rgba(148, 163, 184, 0.25)"
          strokeWidth={0.75}
          strokeDasharray="3,3"
        />

        {/* Zone divider line - horizontal half */}
        <line
          x1={NET_LEFT} y1={NET_TOP + thirdH}
          x2={NET_LEFT + NET_WIDTH} y2={NET_TOP + thirdH}
          stroke="rgba(148, 163, 184, 0.25)"
          strokeWidth={0.75}
          strokeDasharray="3,3"
        />

        {/* Crossbar (top) */}
        <rect
          x={NET_LEFT - postWidth / 2}
          y={NET_TOP - postWidth / 2}
          width={NET_WIDTH + postWidth}
          height={postWidth}
          fill={isGoal ? '#dc2626' : '#94a3b8'}
          rx={1}
        />

        {/* Left post */}
        <rect
          x={NET_LEFT - postWidth / 2}
          y={NET_TOP - postWidth / 2}
          width={postWidth}
          height={NET_HEIGHT + postWidth}
          fill={isGoal ? '#dc2626' : '#94a3b8'}
          rx={1}
        />

        {/* Right post */}
        <rect
          x={NET_LEFT + NET_WIDTH - postWidth / 2}
          y={NET_TOP - postWidth / 2}
          width={postWidth}
          height={NET_HEIGHT + postWidth}
          fill={isGoal ? '#dc2626' : '#94a3b8'}
          rx={1}
        />

        {/* Zone labels */}
        <text x={NET_LEFT + thirdW / 2} y={NET_TOP + thirdH / 2} textAnchor="middle" dominantBaseline="middle" className="fill-slate-600 text-[7px] font-mono uppercase">
          Glove
        </text>
        <text x={NET_LEFT + thirdW / 2} y={NET_TOP + thirdH / 2 + 9} textAnchor="middle" dominantBaseline="middle" className="fill-slate-600 text-[7px] font-mono uppercase">
          High
        </text>
        <text x={NET_LEFT + thirdW * 2.5} y={NET_TOP + thirdH / 2} textAnchor="middle" dominantBaseline="middle" className="fill-slate-600 text-[7px] font-mono uppercase">
          Blocker
        </text>
        <text x={NET_LEFT + thirdW * 2.5} y={NET_TOP + thirdH / 2 + 9} textAnchor="middle" dominantBaseline="middle" className="fill-slate-600 text-[7px] font-mono uppercase">
          High
        </text>
        <text x={NET_LEFT + thirdW / 2} y={NET_TOP + thirdH * 1.5} textAnchor="middle" dominantBaseline="middle" className="fill-slate-600 text-[7px] font-mono uppercase">
          Glove
        </text>
        <text x={NET_LEFT + thirdW / 2} y={NET_TOP + thirdH * 1.5 + 9} textAnchor="middle" dominantBaseline="middle" className="fill-slate-600 text-[7px] font-mono uppercase">
          Low
        </text>
        <text x={NET_LEFT + thirdW * 2.5} y={NET_TOP + thirdH * 1.5} textAnchor="middle" dominantBaseline="middle" className="fill-slate-600 text-[7px] font-mono uppercase">
          Blocker
        </text>
        <text x={NET_LEFT + thirdW * 2.5} y={NET_TOP + thirdH * 1.5 + 9} textAnchor="middle" dominantBaseline="middle" className="fill-slate-600 text-[7px] font-mono uppercase">
          Low
        </text>
        <text x={NET_LEFT + NET_WIDTH / 2} y={NET_TOP + NET_HEIGHT - 8} textAnchor="middle" dominantBaseline="middle" className="fill-slate-600 text-[7px] font-mono uppercase">
          Five Hole
        </text>

        {/* Shot location marker */}
        {hasLocation && (
          <g>
            {/* Glow */}
            <circle
              cx={dotX}
              cy={dotY}
              r={14}
              fill={isGoal ? 'rgba(34, 197, 94, 0.25)' : 'rgba(59, 130, 246, 0.25)'}
            />
            {/* Dot */}
            <circle
              cx={dotX}
              cy={dotY}
              r={8}
              fill={isGoal ? 'rgb(34, 197, 94)' : 'rgb(59, 130, 246)'}
              stroke="white"
              strokeWidth={2}
            />
            {/* Inner dot for goals */}
            {isGoal && (
              <circle
                cx={dotX}
                cy={dotY}
                r={3}
                fill="white"
              />
            )}
          </g>
        )}

        {/* No location label */}
        {!hasLocation && (
          <text
            x={SVG_WIDTH / 2}
            y={NET_TOP + NET_HEIGHT / 2}
            textAnchor="middle"
            className="fill-slate-500 text-xs"
          >
            No net location data
          </text>
        )}

        {/* Title label */}
        <text
          x={SVG_WIDTH / 2}
          y={SVG_HEIGHT - 4}
          textAnchor="middle"
          className="fill-slate-500 text-[8px] font-mono uppercase tracking-wider"
        >
          Net Front View
        </text>
      </svg>
    </div>
  )
}
