'use client'

import { cn } from '@/lib/utils'

export interface PlayerMarker {
  x: number  // Center-relative: -100 to 100 (0 = center ice)
  y: number  // Center-relative: -42.5 to 42.5 (0 = center)
  name?: string
  number?: string | number
  team: 'home' | 'away'
  isSelected?: boolean
  playerId?: string
  seq?: number  // point_number for ordering multi-point paths
  role?: string  // player_role from fact_player_xy_long (e.g., event_player_1, opp_player_2)
}

export interface PuckPosition {
  x: number
  y: number
  seq?: number
}

interface IceRinkSVGProps {
  players?: PlayerMarker[]
  puckPath?: PuckPosition[]
  showPuck?: boolean
  homeColor?: string
  awayColor?: string
  className?: string
  showZoneLabels?: boolean
  flipZones?: boolean
  onRinkClick?: (x: number, y: number) => void
  homeTeamName?: string
  awayTeamName?: string
  focusedPlayerId?: string | null
  onPlayerClick?: (playerId: string) => void
}

/**
 * Convert data coordinates to SVG coordinates
 * Data uses center-relative: x from -100 to 100, y from -42.5 to 42.5 (standard)
 * But some data may use y from -100 to 100 (scaled)
 * SVG viewBox is 0 0 200 85
 */
const toSvg = (x: number, y: number): { x: number; y: number } => {
  // Clamp x to valid range
  const clampedX = Math.max(-100, Math.min(100, x))

  // Check if Y appears to be in -100 to 100 range (scaled) vs -42.5 to 42.5 (standard)
  // If y is outside -50 to 50, assume it's in the scaled range
  let normalizedY = y
  if (Math.abs(y) > 50) {
    // Scale from -100/100 to -42.5/42.5
    normalizedY = (y / 100) * 42.5
  }
  const clampedY = Math.max(-42.5, Math.min(42.5, normalizedY))

  return {
    x: clampedX + 100,  // 0-200
    y: clampedY + 42.5  // 0-85
  }
}

export function IceRinkSVG({
  players = [],
  puckPath = [],
  showPuck = true,
  homeColor = '#3b82f6',  // Blue
  awayColor = '#ef4444',   // Red
  className,
  showZoneLabels = true,
  flipZones = false,
  onRinkClick,
  homeTeamName = 'Home',
  awayTeamName = 'Away',
  focusedPlayerId = null,
  onPlayerClick
}: IceRinkSVGProps) {

  const handleClick = (e: React.MouseEvent<SVGSVGElement>) => {
    if (!onRinkClick) return

    const svg = e.currentTarget
    const rect = svg.getBoundingClientRect()
    const scaleX = 200 / rect.width
    const scaleY = 85 / rect.height

    const svgX = (e.clientX - rect.left) * scaleX
    const svgY = (e.clientY - rect.top) * scaleY

    // Convert to center-relative
    const relX = svgX - 100
    const relY = svgY - 42.5

    onRinkClick(relX, relY)
  }

  return (
    <svg
      viewBox="0 0 200 85"
      className={cn('w-full h-auto', className)}
      onClick={handleClick}
    >
      <defs>
        {/* Ice gradient */}
        <linearGradient id="iceGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#f0f9ff" />
          <stop offset="50%" stopColor="#e0f2fe" />
          <stop offset="100%" stopColor="#f0f9ff" />
        </linearGradient>

        {/* Ice texture pattern */}
        <pattern id="iceTexture" patternUnits="userSpaceOnUse" width="10" height="10">
          <circle cx="5" cy="5" r="0.3" fill="#bae6fd" opacity="0.3" />
        </pattern>

        {/* Goal crease gradient */}
        <linearGradient id="creaseGrad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#60a5fa" stopOpacity="0.3" />
          <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.2" />
        </linearGradient>

        {/* Net mesh pattern (unused - nets now use direct lines for reliability) */}
      </defs>

      {/* Ice surface with rounded corners */}
      <rect x="0" y="0" width="200" height="85" rx="14" ry="14" fill="url(#iceGrad)" />
      <rect x="0" y="0" width="200" height="85" rx="14" ry="14" fill="url(#iceTexture)" />

      {/* Board outline */}
      <rect x="0" y="0" width="200" height="85" rx="14" ry="14" fill="none" stroke="#94a3b8" strokeWidth="1" />

      {/* Blue lines */}
      <line x1="74" y1="0" x2="74" y2="85" stroke="#2563eb" strokeWidth="2" />
      <line x1="126" y1="0" x2="126" y2="85" stroke="#2563eb" strokeWidth="2" />

      {/* Red center line (dashed) */}
      <line x1="100" y1="0" x2="100" y2="85" stroke="#dc2626" strokeWidth="2" strokeDasharray="4,2" />

      {/* Goal lines - extend to boards (accounting for corner radius) */}
      <line x1="11" y1="5" x2="11" y2="80" stroke="#dc2626" strokeWidth="1" />
      <line x1="189" y1="5" x2="189" y2="80" stroke="#dc2626" strokeWidth="1" />

      {/* Center ice circle */}
      <circle cx="100" cy="42.5" r="15" fill="none" stroke="#2563eb" strokeWidth="1" />
      <circle cx="100" cy="42.5" r="1" fill="#2563eb" />

      {/* Faceoff circles - Defensive zone (left) */}
      <circle cx="31" cy="22" r="15" fill="none" stroke="#dc2626" strokeWidth="0.5" />
      <circle cx="31" cy="22" r="1" fill="#dc2626" />
      <circle cx="31" cy="63" r="15" fill="none" stroke="#dc2626" strokeWidth="0.5" />
      <circle cx="31" cy="63" r="1" fill="#dc2626" />

      {/* Faceoff circles - Offensive zone (right) */}
      <circle cx="169" cy="22" r="15" fill="none" stroke="#dc2626" strokeWidth="0.5" />
      <circle cx="169" cy="22" r="1" fill="#dc2626" />
      <circle cx="169" cy="63" r="15" fill="none" stroke="#dc2626" strokeWidth="0.5" />
      <circle cx="169" cy="63" r="1" fill="#dc2626" />

      {/* Neutral zone faceoff dots */}
      <circle cx="80" cy="22" r="1" fill="#dc2626" />
      <circle cx="80" cy="63" r="1" fill="#dc2626" />
      <circle cx="120" cy="22" r="1" fill="#dc2626" />
      <circle cx="120" cy="63" r="1" fill="#dc2626" />

      {/* Goal creases - proper semicircle shape in front of goal line */}
      {/* NHL crease: 6 feet radius semicircle extending from goal posts, in front of goal line */}
      {/* Left goal crease (curved toward center ice at x=17) */}
      <path
        d="M11 38.5 L17 38.5 A4 4 0 0 1 17 46.5 L11 46.5 Z"
        fill="url(#creaseGrad)"
        stroke="#60a5fa"
        strokeWidth="0.5"
      />
      {/* Right goal crease (curved toward center ice at x=183) */}
      <path
        d="M189 38.5 L183 38.5 A4 4 0 0 0 183 46.5 L189 46.5 Z"
        fill="url(#creaseGrad)"
        stroke="#60a5fa"
        strokeWidth="0.5"
      />

      {/* Goal nets - behind the goal line */}
      {/* Left goal net (x=3 to x=11, centered at y=42.5) */}
      <rect x="3" y="37.5" width="8" height="10" fill="#94a3b8" stroke="#0f172a" strokeWidth="1.5" rx="1" />
      <line x1="5" y1="37.5" x2="5" y2="47.5" stroke="#64748b" strokeWidth="0.5" />
      <line x1="7" y1="37.5" x2="7" y2="47.5" stroke="#64748b" strokeWidth="0.5" />
      <line x1="9" y1="37.5" x2="9" y2="47.5" stroke="#64748b" strokeWidth="0.5" />
      <line x1="3" y1="40" x2="11" y2="40" stroke="#64748b" strokeWidth="0.5" />
      <line x1="3" y1="42.5" x2="11" y2="42.5" stroke="#64748b" strokeWidth="0.5" />
      <line x1="3" y1="45" x2="11" y2="45" stroke="#64748b" strokeWidth="0.5" />
      <line x1="11" y1="37.5" x2="11" y2="47.5" stroke="#dc2626" strokeWidth="2.5" />

      {/* Right goal net (x=189 to x=197, centered at y=42.5) */}
      <rect x="189" y="37.5" width="8" height="10" fill="#94a3b8" stroke="#0f172a" strokeWidth="1.5" rx="1" />
      <line x1="191" y1="37.5" x2="191" y2="47.5" stroke="#64748b" strokeWidth="0.5" />
      <line x1="193" y1="37.5" x2="193" y2="47.5" stroke="#64748b" strokeWidth="0.5" />
      <line x1="195" y1="37.5" x2="195" y2="47.5" stroke="#64748b" strokeWidth="0.5" />
      <line x1="189" y1="40" x2="197" y2="40" stroke="#64748b" strokeWidth="0.5" />
      <line x1="189" y1="42.5" x2="197" y2="42.5" stroke="#64748b" strokeWidth="0.5" />
      <line x1="189" y1="45" x2="197" y2="45" stroke="#64748b" strokeWidth="0.5" />
      <line x1="189" y1="37.5" x2="189" y2="47.5" stroke="#dc2626" strokeWidth="2.5" />

      {/* Trapezoid areas */}
      <polygon points="11,28 0,20 0,65 11,57" fill="#94a3b8" opacity="0.1" />
      <polygon points="189,28 200,20 200,65 189,57" fill="#94a3b8" opacity="0.1" />

      {/* Zone labels */}
      {showZoneLabels && (
        <g className="text-[3.5px]" fill="#64748b">
          <text x="37" y="82" textAnchor="middle">{flipZones ? `${homeTeamName} OFF` : `${awayTeamName} OFF`}</text>
          <text x="100" y="82" textAnchor="middle">NEUTRAL</text>
          <text x="163" y="82" textAnchor="middle">{flipZones ? `${awayTeamName} OFF` : `${homeTeamName} OFF`}</text>
        </g>
      )}

      {/* Puck path */}
      {showPuck && puckPath.length > 0 && (
        <g>
          {/* Path lines - dotted black lines */}
          {puckPath.length > 1 && puckPath.map((point, i) => {
            if (i === 0) return null
            const prev = puckPath[i - 1]
            // Only draw line if consecutive sequence numbers
            if (point.seq !== undefined && prev.seq !== undefined && point.seq !== prev.seq + 1) {
              return null
            }
            const p1 = toSvg(prev.x, prev.y)
            const p2 = toSvg(point.x, point.y)
            return (
              <line
                key={`puck-line-${i}`}
                x1={p1.x}
                y1={p1.y}
                x2={p2.x}
                y2={p2.y}
                stroke="#333"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeDasharray="3,2"
              />
            )
          })}

          {/* Puck markers - black puck */}
          {puckPath.map((point, i) => {
            const pos = toSvg(point.x, point.y)
            const isLast = i === puckPath.length - 1
            return (
              <g key={`puck-${i}`}>
                {/* Glow effect for visibility */}
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r={isLast ? 5 : 3}
                  fill="rgba(0, 0, 0, 0.2)"
                />
                {/* Puck */}
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r={isLast ? 3 : 2}
                  fill="#1a1a1a"
                  stroke="#fff"
                  strokeWidth={isLast ? 1 : 0.5}
                />
              </g>
            )
          })}
        </g>
      )}

      {/* Player movement lines (team-colored, grouped by playerId) */}
      {(() => {
        // Group players by playerId to draw connecting lines
        const grouped = new Map<string, PlayerMarker[]>()
        players.forEach(p => {
          if (!p.playerId) return
          const existing = grouped.get(p.playerId)
          if (existing) existing.push(p)
          else grouped.set(p.playerId, [p])
        })

        return Array.from(grouped.entries()).map(([pid, points]) => {
          if (points.length < 2) return null
          const sorted = [...points].sort((a, b) => (a.seq ?? 0) - (b.seq ?? 0))
          const color = sorted[0].team === 'home' ? homeColor : awayColor
          const isFocused = !focusedPlayerId || pid === focusedPlayerId

          return sorted.map((point, i) => {
            if (i === 0) return null
            const prev = sorted[i - 1]
            const p1 = toSvg(prev.x, prev.y)
            const p2 = toSvg(point.x, point.y)
            return (
              <line
                key={`trail-${pid}-${i}`}
                x1={p1.x} y1={p1.y}
                x2={p2.x} y2={p2.y}
                stroke={color}
                strokeWidth="1"
                strokeLinecap="round"
                strokeDasharray="2,1.5"
                opacity={isFocused ? 0.6 : 0.1}
              />
            )
          })
        })
      })()}

      {/* Player markers */}
      {players.map((player, i) => {
        const pos = toSvg(player.x, player.y)
        const color = player.team === 'home' ? homeColor : awayColor
        const hasNumber = player.number !== undefined && player.number !== null && player.number !== ''
        const isFirstPoint = !player.seq || player.seq === 1
        const isFocused = !focusedPlayerId || player.playerId === focusedPlayerId
        const markerOpacity = isFocused ? 1 : 0.2
        const clickable = onPlayerClick && player.playerId

        // Trail dots (non-first points): render as small circles, no jersey number
        if (!isFirstPoint) {
          return (
            <g key={`player-${i}`} opacity={markerOpacity}>
              <circle
                cx={pos.x}
                cy={pos.y}
                r={2}
                fill={color}
                stroke="#000"
                strokeWidth="0.3"
                opacity={0.7}
              />
            </g>
          )
        }

        // First point: full circle with jersey number
        const radius = hasNumber ? (player.isSelected ? 5 : 4) : (player.isSelected ? 4 : 3)

        return (
          <g
            key={`player-${i}`}
            opacity={markerOpacity}
            style={clickable ? { cursor: 'pointer' } : undefined}
            onClick={clickable ? (e) => { e.stopPropagation(); onPlayerClick!(player.playerId!) } : undefined}
          >
            {/* Glow ring for selected player (event_player_1) */}
            {player.isSelected && (
              <circle
                cx={pos.x}
                cy={pos.y}
                r={radius + 2}
                fill="none"
                stroke="#fbbf24"
                strokeWidth="1.5"
                opacity="0.7"
              />
            )}

            {/* Focus ring when this player is the focused one */}
            {focusedPlayerId && player.playerId === focusedPlayerId && (
              <circle
                cx={pos.x}
                cy={pos.y}
                r={radius + 2}
                fill="none"
                stroke="#fff"
                strokeWidth="1.5"
                opacity="0.9"
              />
            )}

            {/* Player circle */}
            <circle
              cx={pos.x}
              cy={pos.y}
              r={radius}
              fill={color}
              stroke={player.isSelected ? '#fff' : '#000'}
              strokeWidth={player.isSelected ? 1.5 : 0.5}
            />

            {/* Jersey number inside circle */}
            {hasNumber ? (
              <text
                x={pos.x}
                y={pos.y}
                textAnchor="middle"
                dominantBaseline="central"
                fill="#fff"
                stroke="#000"
                strokeWidth="0.3"
                paintOrder="stroke"
                className="text-[3px]"
                style={{ fontWeight: 700 }}
              >
                {player.number}
              </text>
            ) : (
              /* Fallback: player name initial below circle */
              player.name && (
                <text
                  x={pos.x}
                  y={pos.y + radius + 3}
                  textAnchor="middle"
                  className="text-[2.5px]"
                  fill="#1e293b"
                >
                  {player.name.split(' ').pop()?.charAt(0)}
                </text>
              )
            )}
          </g>
        )
      })}
    </svg>
  )
}
