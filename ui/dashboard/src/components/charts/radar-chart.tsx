'use client'

import { ResponsiveContainer, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Legend } from 'recharts'

interface RadarChartData {
  category: string
  value: number
  max?: number
}

interface StatRadarChartProps {
  data: RadarChartData[]
  height?: number
  colors?: string[]
  maxValue?: number
}

export function StatRadarChart({ 
  data, 
  height = 400,
  colors = ['hsl(var(--primary))', 'hsl(var(--assist))'],
  maxValue
}: StatRadarChartProps) {
  // Calculate max value if not provided
  const calculatedMax = maxValue || Math.max(...data.map(d => d.value || d.max || 0)) * 1.2

  // Normalize data
  const normalizedData = data.map(d => ({
    category: d.category,
    value: d.value || 0,
    max: calculatedMax
  }))

  if (normalizedData.length === 0) {
    return (
      <div className="bg-muted/30 rounded-lg p-8 text-center" style={{ height }}>
        <p className="text-sm text-muted-foreground">No data available</p>
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <RadarChart data={normalizedData} margin={{ top: 20, right: 30, bottom: 20, left: 20 }}>
        <PolarGrid stroke="hsl(var(--border))" opacity={0.3} />
        <PolarAngleAxis 
          dataKey="category" 
          tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 11 }}
        />
        <PolarRadiusAxis 
          angle={90} 
          domain={[0, calculatedMax]}
          tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 10 }}
        />
        <Radar
          name="Stats"
          dataKey="value"
          stroke={colors[0]}
          fill={colors[0]}
          fillOpacity={0.6}
          strokeWidth={2}
        />
        <Legend />
      </RadarChart>
    </ResponsiveContainer>
  )
}

// Multi-player comparison radar chart
interface MultiPlayerRadarChartProps {
  data: Array<{
    player: string
    stats: RadarChartData[]
  }>
  height?: number
  colors?: string[]
}

export function MultiPlayerRadarChart({ 
  data, 
  height = 400,
  colors = ['hsl(var(--primary))', 'hsl(var(--assist))', 'hsl(var(--goal))', 'hsl(var(--save))']
}: MultiPlayerRadarChartProps) {
  if (data.length === 0) {
    return (
      <div className="bg-muted/30 rounded-lg p-8 text-center" style={{ height }}>
        <p className="text-sm text-muted-foreground">No data available</p>
      </div>
    )
  }

  // Get all categories from first player (assuming all have same categories)
  const categories = data[0]?.stats.map(s => s.category) || []
  
  // Calculate max value across all players
  const maxValue = Math.max(
    ...data.flatMap(d => d.stats.map(s => s.value || 0))
  ) * 1.2

  // Transform data for radar chart
  const chartData = categories.map(category => {
    const entry: any = { category }
    data.forEach((playerData, idx) => {
      const stat = playerData.stats.find(s => s.category === category)
      entry[`player_${idx}`] = stat?.value || 0
    })
    return entry
  })

  return (
    <ResponsiveContainer width="100%" height={height}>
      <RadarChart data={chartData} margin={{ top: 20, right: 30, bottom: 20, left: 20 }}>
        <PolarGrid stroke="hsl(var(--border))" opacity={0.3} />
        <PolarAngleAxis 
          dataKey="category" 
          tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 11 }}
        />
        <PolarRadiusAxis 
          angle={90} 
          domain={[0, maxValue]}
          tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 10 }}
        />
        {data.map((playerData, idx) => (
          <Radar
            key={playerData.player}
            name={playerData.player}
            dataKey={`player_${idx}`}
            stroke={colors[idx % colors.length]}
            fill={colors[idx % colors.length]}
            fillOpacity={0.3}
            strokeWidth={2}
          />
        ))}
        <Legend />
      </RadarChart>
    </ResponsiveContainer>
  )
}
