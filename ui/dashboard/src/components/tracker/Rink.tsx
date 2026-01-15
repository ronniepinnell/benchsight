'use client'

/**
 * Hockey Rink Component
 * 
 * SVG hockey rink with XY placement functionality
 * Based on tracker_index_v23.5.html
 */

import { useRef, useState, useCallback } from 'react'
import type { XYCoordinate, Period, Team, Zone } from '@/lib/tracker/types'
import { detectFaceoffDot, smartAutoLinkXY, relativeToSvg, svgToRelative } from '@/lib/tracker/utils/xy'
import { getZoneFromClick } from '@/lib/tracker/utils/zone'
import { useTrackerStore } from '@/lib/tracker/state'
import { toast } from '@/lib/tracker/utils/toast'
import { cn } from '@/lib/utils'

interface RinkProps {
  onXYPlace?: (xy: XYCoordinate, zone: Zone) => void
  className?: string
}

export function Rink({ onXYPlace, className }: RinkProps) {
  const svgRef = useRef<SVGSVGElement>(null)
  const [tooltip, setTooltip] = useState<{ x: number; y: number; text: string } | null>(null)
  
  const {
    xyMode,
    period,
    evtTeam,
    homeAttacksRightP1,
    curr,
    setXYMode,
    setCurrentPuckXY,
    setCurrentNetXY,
    setCurrentPlayerXY,
    selectedPlayer
  } = useTrackerStore()

  const handleClick = useCallback((event: React.MouseEvent<SVGSVGElement>) => {
    if (!svgRef.current) return

    const rect = svgRef.current.getBoundingClientRect()
    const svgX = ((event.clientX - rect.left) / rect.width) * 200
    const svgY = ((event.clientY - rect.top) / rect.height) * 85

    // Get zone from click
    const zone = getZoneFromClick(
      svgX,
      period,
      evtTeam as Team,
      homeAttacksRightP1
    )

    // Detect faceoff dot
    const faceoffDot = detectFaceoffDot(svgX, svgY, 5)
    if (faceoffDot && curr.type === 'Faceoff') {
      // Auto-assign E1 and O1 positions for faceoffs
      // Convert SVG coordinates to center-relative for storage
    const relativeXY = svgToRelative(svgX, svgY)
    const xy: XYCoordinate = { x: relativeXY.x, y: relativeXY.y }
      
      // Add to puck XY (faceoff location)
      const newPuckXY = [...(curr.puckXY || []), xy]
      setCurrentPuckXY(newPuckXY)
      
      // Auto-link players if available
      if (curr.players && curr.players.length > 0) {
        smartAutoLinkXY(xy, 1, curr.type, curr.players)
      }
      
      toast('Faceoff dot clicked', 'info')
      onXYPlace?.(xy, zone)
      return
    }

    // Convert SVG coordinates to center-relative for storage
    const relativeXY = svgToRelative(svgX, svgY)
    const xy: XYCoordinate = { x: relativeXY.x, y: relativeXY.y }

    // Place XY based on mode
    if (xyMode === 'puck') {
      const newPuckXY = [...(curr.puckXY || []), xy]
      setCurrentPuckXY(newPuckXY)
      
      // Auto-link XY based on event type
      if (curr.type && curr.players && curr.players.length > 0) {
        const currentSlot = curr.puckXY?.length || 0
        smartAutoLinkXY(xy, currentSlot + 1, curr.type, curr.players)
      }
      
      onXYPlace?.(xy, zone)
    } else {
      // Player mode - add XY to selected player or first player
      if (curr.players && curr.players.length > 0) {
        const targetPlayer = selectedPlayer || curr.players[0]
        if (targetPlayer) {
          setCurrentPlayerXY(targetPlayer.num, targetPlayer.team, xy)
          toast(`Placed XY for #${targetPlayer.num}`, 'info')
        }
      } else {
        toast('Add a player first', 'warning')
      }
      onXYPlace?.(xy, zone)
    }
  }, [xyMode, period, evtTeam, homeAttacksRightP1, curr, selectedPlayer, setCurrentPuckXY, setCurrentPlayerXY, onXYPlace])

  const handleMouseMove = useCallback((event: React.MouseEvent<SVGSVGElement>) => {
    if (!svgRef.current) return

    const rect = svgRef.current.getBoundingClientRect()
    const svgX = ((event.clientX - rect.left) / rect.width) * 200
    const svgY = ((event.clientY - rect.top) / rect.height) * 85

    const zone = getZoneFromClick(
      svgX,
      period,
      evtTeam as Team,
      homeAttacksRightP1
    )

    setTooltip({
      x: event.clientX,
      y: event.clientY,
      text: `X: ${svgX.toFixed(1)}, Y: ${svgY.toFixed(1)}, Zone: ${zone}`
    })
  }, [period, evtTeam, homeAttacksRightP1])

  const handleMouseLeave = useCallback(() => {
    setTooltip(null)
  }, [])

  // Determine zone labels based on period
  const isOddPeriod = period === 1 || period === 3 || period === 4
  const homeOffensiveRight = isOddPeriod ? homeAttacksRightP1 : !homeAttacksRightP1

  return (
    <div className={cn('relative flex items-center justify-center p-2', className)}>
      {/* Mode indicator */}
      <div className={cn(
        'absolute top-2 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full text-xs font-semibold border-2 z-10',
        xyMode === 'puck' 
          ? 'bg-black text-white border-white' 
          : 'bg-accent text-foreground border-accent'
      )}>
        {xyMode === 'puck' ? '🏒 PUCK' : '👤 PLAYER'}
      </div>

      {/* Tooltip */}
      {tooltip && (
        <div
          className="absolute bg-black/90 text-white px-2 py-1 rounded text-xs pointer-events-none z-20"
          style={{
            left: tooltip.x,
            top: tooltip.y - 30,
            transform: 'translateX(-50%)'
          }}
        >
          {tooltip.text}
        </div>
      )}

      {/* Rink SVG */}
      <svg
        ref={svgRef}
        viewBox="0 0 200 85"
        className="max-w-full max-h-full cursor-crosshair"
        onClick={handleClick}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
      >
        <defs>
          <linearGradient id="iceGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#f0f9ff" stopOpacity={1} />
            <stop offset="50%" stopColor="#e0f2fe" stopOpacity={1} />
            <stop offset="100%" stopColor="#f0f9ff" stopOpacity={1} />
          </linearGradient>
          <pattern id="iceTexture" patternUnits="userSpaceOnUse" width="4" height="4">
            <rect width="4" height="4" fill="#e0f2fe" opacity={0.3} />
            <circle cx="1" cy="1" r="0.3" fill="#fff" opacity={0.4} />
          </pattern>
        </defs>

        {/* Ice surface */}
        <rect x="0" y="0" width="200" height="85" fill="url(#iceGrad)" rx="14" ry="14" />
        <rect x="0" y="0" width="200" height="85" fill="url(#iceTexture)" rx="14" ry="14" />
        
        {/* Boards */}
        <rect
          x="0"
          y="0"
          width="200"
          height="85"
          fill="none"
          rx="14"
          ry="14"
          stroke="#1f2937"
          strokeWidth="2"
        />

        {/* Blue lines */}
        <rect x="74" y="0" width="2" height="85" fill="#1e40af" />
        <rect x="124" y="0" width="2" height="85" fill="#1e40af" />

        {/* Red center line (dashed) */}
        <line
          x1="100"
          y1="0"
          x2="100"
          y2="85"
          stroke="#dc2626"
          strokeWidth="1.5"
          strokeDasharray="4,2"
        />

        {/* Goal lines */}
        <line x1="11" y1="0" x2="11" y2="85" stroke="#dc2626" strokeWidth="1" />
        <line x1="189" y1="0" x2="189" y2="85" stroke="#dc2626" strokeWidth="1" />

        {/* Center ice circle */}
        <circle cx="100" cy="42.5" r="15" fill="none" stroke="#1d4ed8" strokeWidth="0.5" />
        <circle cx="100" cy="42.5" r="1" fill="#1d4ed8" />

        {/* Offensive zone faceoff circles (left) */}
        <circle cx="31" cy="22" r="15" fill="none" stroke="#dc2626" strokeWidth="0.4" />
        <circle cx="31" cy="22" r="1" fill="#dc2626" />
        <circle cx="31" cy="63" r="15" fill="none" stroke="#dc2626" strokeWidth="0.4" />
        <circle cx="31" cy="63" r="1" fill="#dc2626" />

        {/* Offensive zone faceoff circles (right) */}
        <circle cx="169" cy="22" r="15" fill="none" stroke="#dc2626" strokeWidth="0.4" />
        <circle cx="169" cy="22" r="1" fill="#dc2626" />
        <circle cx="169" cy="63" r="15" fill="none" stroke="#dc2626" strokeWidth="0.4" />
        <circle cx="169" cy="63" r="1" fill="#dc2626" />

        {/* Neutral zone dots */}
        <circle cx="80" cy="22" r="0.8" fill="#dc2626" />
        <circle cx="80" cy="63" r="0.8" fill="#dc2626" />
        <circle cx="120" cy="22" r="0.8" fill="#dc2626" />
        <circle cx="120" cy="63" r="0.8" fill="#dc2626" />

        {/* Creases */}
        <path
          d="M 11 38.5 L 15 38.5 A 4 4 0 0 1 15 46.5 L 11 46.5"
          fill="rgba(59,130,246,0.15)"
          stroke="#3b82f6"
          strokeWidth="0.4"
        />
        <path
          d="M 189 38.5 L 185 38.5 A 4 4 0 0 0 185 46.5 L 189 46.5"
          fill="rgba(59,130,246,0.15)"
          stroke="#3b82f6"
          strokeWidth="0.4"
        />

        {/* Goals */}
        <rect x="7" y="39" width="4" height="7" fill="#222" stroke="#fff" strokeWidth="0.3" />
        <rect x="189" y="39" width="4" height="7" fill="#222" stroke="#fff" strokeWidth="0.3" />

        {/* High danger zone (slot area) */}
        <path
          d="M 11 30 L 45 30 L 45 55 L 11 55 Z"
          fill="rgba(239,68,68,0.08)"
          stroke="none"
        />
        <path
          d="M 189 30 L 155 30 L 155 55 L 189 55 Z"
          fill="rgba(239,68,68,0.08)"
          stroke="none"
        />

        {/* Zone labels */}
        <text x="43" y="82" fontSize="3" fill="#64748b" textAnchor="middle">
          {homeOffensiveRight ? 'OFF' : 'DEF'}
        </text>
        <text x="100" y="82" fontSize="3" fill="#64748b" textAnchor="middle">
          NEU
        </text>
        <text x="157" y="82" fontSize="3" fill="#64748b" textAnchor="middle">
          {homeOffensiveRight ? 'DEF' : 'OFF'}
        </text>

        {/* Markers for current event */}
        {curr.puckXY?.map((xy, i) => {
          const svgCoords = relativeToSvg(xy)
          return (
            <circle
              key={`puck-${i}`}
              cx={svgCoords.x}
              cy={svgCoords.y}
              r="2"
              fill="#000"
              stroke="#fff"
              strokeWidth="0.5"
            />
          )
        })}

        {/* Player markers */}
        {curr.players?.map((player, i) =>
          player.xy?.map((xy, j) => {
            const svgCoords = relativeToSvg(xy)
            return (
              <circle
                key={`player-${i}-${j}`}
                cx={svgCoords.x}
                cy={svgCoords.y}
                r="2"
                fill={player.team === 'home' ? '#3b82f6' : '#ef4444'}
                stroke="#fff"
                strokeWidth="0.5"
              />
            )
          })
        )}

        {/* Net marker */}
        {curr.netXY && (() => {
          const svgCoords = relativeToSvg(curr.netXY)
          return (
            <rect
              x={svgCoords.x - 2}
              y={svgCoords.y - 3.5}
              width="4"
              height="7"
              fill="#222"
              stroke="#fff"
              strokeWidth="0.3"
            />
          )
        })()}
      </svg>
    </div>
  )
}
