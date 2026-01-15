'use client'

import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from 'recharts'
import { Clock } from 'lucide-react'

interface Shift {
  shift_key?: string
  shift_id?: string
  player_id?: string
  player_name?: string
  period?: number
  shift_start_total_seconds?: number
  shift_end_total_seconds?: number
  shift_duration?: number
  shift_start_time?: string
  shift_end_time?: string
  game_id?: number
}

interface ShiftChartProps {
  shifts: Shift[]
  playerId?: string
  height?: number
}

export function ShiftChart({ shifts, playerId, height = 400 }: ShiftChartProps) {
  // Filter by player if specified
  const filteredShifts = playerId 
    ? shifts.filter(s => s.player_id && String(s.player_id) === String(playerId))
    : shifts

  if (filteredShifts.length === 0) {
    return (
      <div className="bg-muted/30 rounded-lg p-8 text-center" style={{ height }}>
        <p className="text-sm text-muted-foreground">No shift data available</p>
      </div>
    )
  }

  // Group shifts by period
  const shiftsByPeriod = filteredShifts.reduce((acc, shift) => {
    const period = shift.period || 1
    if (!acc[period]) {
      acc[period] = []
    }
    acc[period].push(shift)
    return acc
  }, {} as Record<number, Shift[]>)

  // Calculate total TOI per period
  const periodData = Object.entries(shiftsByPeriod).map(([period, periodShifts]) => {
    const totalSeconds = periodShifts.reduce((sum, shift) => {
      // Try multiple duration fields
      const duration = shift.shift_duration || 
        (shift.shift_end_total_seconds && shift.shift_start_total_seconds
          ? (shift.shift_end_total_seconds - shift.shift_start_total_seconds)
          : 0)
      return sum + (duration || 0)
    }, 0)
    return {
      period: `P${period}`,
      shifts: periodShifts.length,
      toi: Math.round(totalSeconds / 60), // Convert to minutes
    }
  })

  if (periodData.length === 0) {
    return (
      <div className="bg-muted/30 rounded-lg p-8 text-center" style={{ height }}>
        <p className="text-sm text-muted-foreground">No shift data available</p>
      </div>
    )
  }

  return (
    <div className="bg-card rounded-xl border border-border overflow-hidden">
      <div className="px-4 py-3 bg-accent border-b border-border">
        <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
          <Clock className="w-4 h-4" />
          Shift Chart
        </h2>
      </div>
      <div className="p-6">
        <ResponsiveContainer width="100%" height={height}>
          <BarChart data={periodData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
            <XAxis 
              dataKey="period" 
              tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
            />
            <YAxis 
              tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
              label={{ value: 'Minutes', angle: -90, position: 'insideLeft', fill: 'hsl(var(--muted-foreground))' }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'hsl(var(--card))', 
                border: '1px solid hsl(var(--border))',
                borderRadius: '8px'
              }}
            />
            <Legend />
            <Bar 
              dataKey="toi" 
              name="TOI (min)" 
              fill="hsl(var(--primary))" 
              radius={[4, 4, 0, 0]}
            />
            <Bar 
              dataKey="shifts" 
              name="Shifts" 
              fill="hsl(var(--assist))" 
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
