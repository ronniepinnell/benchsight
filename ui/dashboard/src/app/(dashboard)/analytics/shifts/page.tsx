// src/app/(dashboard)/analytics/shifts/page.tsx
import Link from 'next/link'
import { createClient } from '@/lib/supabase/server'
import { ArrowLeft, Timer, TrendingUp, Clock, Activity } from 'lucide-react'
import { cn } from '@/lib/utils'

export const revalidate = 300

export const metadata = {
  title: 'Shift Viewer | BenchSight Analytics',
  description: 'View and analyze player shifts',
}

export default async function ShiftViewerPage() {
  const supabase = await createClient()
  
  // Get recent games with shift data
  const { data: recentGames } = await supabase
    .from('dim_schedule')
    .select('game_id, date, home_team_name, away_team_name, home_total_goals, away_total_goals')
    .not('home_total_goals', 'is', null)
    .order('date', { ascending: false })
    .limit(10)
    .catch(() => ({ data: [] }))
  
  // Get shift data if available
  const { data: shiftData } = await supabase
    .from('fact_shifts')
    .select('*')
    .limit(100)
    .catch(() => ({ data: [] }))
  
  return (
    <div className="space-y-6">
      {/* Back Link */}
      <Link 
        href="/analytics/overview" 
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Analytics
      </Link>
      
      {/* Header */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="px-4 py-3 bg-accent border-b border-border">
          <h1 className="font-display text-lg font-semibold uppercase tracking-wider flex items-center gap-2">
            <Timer className="w-5 h-5" />
            Shift Analysis
          </h1>
        </div>
        <div className="p-6">
          {shiftData && shiftData.length > 0 ? (
            <div className="space-y-4">
              <div className="grid md:grid-cols-3 gap-4">
                <div className="bg-muted/30 rounded-lg p-4 text-center">
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Total Shifts</div>
                  <div className="font-mono text-2xl font-bold text-foreground">{shiftData.length}</div>
                </div>
                <div className="bg-muted/30 rounded-lg p-4 text-center">
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Games Tracked</div>
                  <div className="font-mono text-2xl font-bold text-primary">
                    {new Set(shiftData.map((s: any) => s.game_id)).size}
                  </div>
                </div>
                <div className="bg-muted/30 rounded-lg p-4 text-center">
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Players</div>
                  <div className="font-mono text-2xl font-bold text-assist">
                    {new Set(shiftData.map((s: any) => s.player_id)).size}
                  </div>
                </div>
              </div>
              
              <div className="bg-muted/20 rounded-lg p-6 text-center">
                <Activity className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">
                  Detailed shift analysis and visualization features are in development.
                  This will include shift length analysis, line combinations, and shift-by-shift performance metrics.
                </p>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <Timer className="w-16 h-16 text-muted-foreground mx-auto mb-4 opacity-50" />
              <p className="text-muted-foreground mb-2">
                Shift data is being collected and will be available soon.
              </p>
              <p className="text-sm text-muted-foreground">
                This feature will allow you to analyze player shifts, line combinations, and shift-by-shift performance.
              </p>
            </div>
          )}
        </div>
      </div>
      
      {/* Recent Games with Shifts */}
      {recentGames && recentGames.length > 0 && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Clock className="w-4 h-4" />
              Recent Games
            </h2>
          </div>
          <div className="divide-y divide-border">
            {recentGames.map((game: any) => (
              <Link
                key={game.game_id}
                href={`/games/${game.game_id}`}
                className="block p-4 hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-xs font-mono text-muted-foreground mb-1">
                      {game.date ? new Date(game.date).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric'
                      }) : 'Unknown Date'}
                    </div>
                    <div className="font-display text-sm text-foreground">
                      {game.away_team_name} @ {game.home_team_name}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-mono text-lg font-bold">
                      {game.away_total_goals ?? 0} - {game.home_total_goals ?? 0}
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
