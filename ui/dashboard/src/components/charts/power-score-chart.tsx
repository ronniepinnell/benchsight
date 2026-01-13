'use client'

import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'

interface PowerScoreChartProps {
  data: Array<{
    name: string
    powerScore: number
  }>
}

export function PowerScoreChart({ data }: PowerScoreChartProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} margin={{ top: 5, right: 5, left: 5, bottom: 60 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
        <XAxis 
          dataKey="name" 
          angle={-45} 
          textAnchor="end" 
          height={80}
          tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 11 }}
        />
        <YAxis 
          tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 11 }}
        />
        <Tooltip 
          contentStyle={{
            backgroundColor: 'hsl(var(--card))',
            border: '1px solid hsl(var(--border))',
            borderRadius: '0.5rem',
            color: 'hsl(var(--foreground))',
          }}
        />
        <Bar dataKey="powerScore" fill="hsl(var(--assist))" name="Power Score" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
