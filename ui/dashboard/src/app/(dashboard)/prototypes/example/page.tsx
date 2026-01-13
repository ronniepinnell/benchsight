// src/app/(dashboard)/prototypes/example/page.tsx
// Example prototype page - use this as a template!

import { PrototypeTemplate, StatCard, PrototypeTable } from '@/components/prototypes/prototype-template'
import { createClient } from '@/lib/supabase/server'
import { BarChart3, Target, Trophy, Users } from 'lucide-react'
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'

export const revalidate = 300

export const metadata = {
  title: 'Example Prototype | BenchSight',
  description: 'Example dashboard prototype',
}

export default async function ExamplePrototypePage() {
  const supabase = await createClient()
  
  // Example: Fetch standings data
  const { data: standings } = await supabase
    .from('v_standings_current')
    .select('*')
    .order('standing', { ascending: true })
    .limit(10)

  // Example: Calculate some stats
  const totalTeams = standings?.length || 0
  const totalWins = standings?.reduce((sum, team) => sum + (team.wins || 0), 0) || 0
  const avgWinPct = standings?.length 
    ? standings.reduce((sum, team) => {
        const gp = team.games_played || 1
        return sum + ((team.wins || 0) / gp) * 100
      }, 0) / standings.length 
    : 0

  // Prepare chart data
  const chartData = standings?.map(team => ({
    name: team.team_name?.substring(0, 10) || 'Team',
    wins: team.wins || 0,
    losses: team.losses || 0,
  })) || []

  return (
    <PrototypeTemplate 
      title="Example Prototype" 
      description="This is an example prototype showing common patterns"
    >
      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard 
          label="Teams" 
          value={totalTeams} 
          icon={Users}
          color="text-primary"
        />
        <StatCard 
          label="Total Wins" 
          value={totalWins} 
          icon={Trophy}
          color="text-assist"
        />
        <StatCard 
          label="Avg Win %" 
          value={`${avgWinPct.toFixed(1)}%`} 
          icon={BarChart3}
          color="text-goal"
        />
        <StatCard 
          label="Example" 
          value="42" 
          icon={Target}
          color="text-save"
        />
      </div>

      {/* Chart Example */}
      <div className="bg-card rounded-xl border border-border p-6">
        <h2 className="font-display text-lg font-semibold mb-4">Wins vs Losses</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="wins" fill="hsl(var(--save))" name="Wins" />
            <Bar dataKey="losses" fill="hsl(var(--goal))" name="Losses" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Table Example */}
      {standings && standings.length > 0 && (
        <PrototypeTable
          data={standings}
          columns={[
            { key: 'standing', label: 'Rank' },
            { key: 'team_name', label: 'Team' },
            { 
              key: 'wins', 
              label: 'Wins',
              render: (value) => <span className="font-mono font-semibold text-save">{value}</span>
            },
            { 
              key: 'losses', 
              label: 'Losses',
              render: (value) => <span className="font-mono text-goal">{value}</span>
            },
            { 
              key: 'goal_diff', 
              label: 'Goal Diff',
              render: (value) => (
                <span className={`font-mono ${value > 0 ? 'text-save' : value < 0 ? 'text-goal' : ''}`}>
                  {value > 0 ? '+' : ''}{value}
                </span>
              )
            },
          ]}
        />
      )}

      {/* Code Example */}
      <div className="bg-card rounded-xl border border-border p-6">
        <h2 className="font-display text-lg font-semibold mb-4">How to Use This Template</h2>
        <div className="space-y-2 text-sm text-muted-foreground">
          <p>1. Copy this file to create a new prototype</p>
          <p>2. Modify the data fetching queries</p>
          <p>3. Customize the visualizations</p>
          <p>4. Add to sidebar navigation</p>
        </div>
      </div>
    </PrototypeTemplate>
  )
}
