// src/app/(dashboard)/analytics/trends/page.tsx
import Link from 'next/link'
import { createClient } from '@/lib/supabase/server'
import { ArrowLeft, TrendingUp, BarChart3, Activity, Target } from 'lucide-react'
import { cn } from '@/lib/utils'

export const revalidate = 300

export const metadata = {
  title: 'Trends | BenchSight Analytics',
  description: 'View league and player trends over time',
}

export default async function TrendsPage() {
  const supabase = await createClient()
  
  // Get season data for trends
  const { data: seasons, error: seasonsError } = await supabase
    .from('dim_season')
    .select('*')
    .order('season', { ascending: false })
    .limit(5)
  
  // Get team trends
  const { data: teamTrends, error: teamTrendsError } = await supabase
    .from('fact_team_season_stats_basic')
    .select('team_name, season, wins, losses, goals_for, goals_against')
    .order('season', { ascending: false })
    .limit(50)
  
  // Get player trends
  const { data: playerTrends, error: playerTrendsError } = await supabase
    .from('fact_player_season_stats_basic')
    .select('player_name, season, goals, assists, points')
    .order('season', { ascending: false })
    .order('points', { ascending: false })
    .limit(50)
  
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
            <TrendingUp className="w-5 h-5" />
            Trends Analysis
          </h1>
        </div>
        <div className="p-6">
          <div className="space-y-6">
            {/* Overview Stats */}
            <div className="grid md:grid-cols-4 gap-4">
              <div className="bg-muted/30 rounded-lg p-4 text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Seasons</div>
                <div className="font-mono text-2xl font-bold text-foreground">
                  {seasons?.length || 0}
                </div>
              </div>
              <div className="bg-muted/30 rounded-lg p-4 text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Teams Tracked</div>
                <div className="font-mono text-2xl font-bold text-primary">
                  {new Set(teamTrends?.map((t: any) => t.team_name) || []).size}
                </div>
              </div>
              <div className="bg-muted/30 rounded-lg p-4 text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Players Tracked</div>
                <div className="font-mono text-2xl font-bold text-assist">
                  {new Set(playerTrends?.map((p: any) => p.player_name) || []).size}
                </div>
              </div>
              <div className="bg-muted/30 rounded-lg p-4 text-center">
                <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Data Points</div>
                <div className="font-mono text-2xl font-bold text-goal">
                  {(teamTrends?.length || 0) + (playerTrends?.length || 0)}
                </div>
              </div>
            </div>
            
            {/* Feature Info */}
            <div className="bg-muted/20 rounded-lg p-6">
              <div className="flex items-start gap-4">
                <BarChart3 className="w-8 h-8 text-primary flex-shrink-0 mt-1" />
                <div>
                  <h3 className="font-display text-sm font-semibold text-foreground mb-2">
                    Advanced Trend Analysis Coming Soon
                  </h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    This feature will provide comprehensive trend analysis including:
                  </p>
                  <ul className="space-y-2 text-sm text-muted-foreground">
                    <li className="flex items-center gap-2">
                      <Activity className="w-4 h-4 text-primary" />
                      <span>Player performance trends over time</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <Target className="w-4 h-4 text-assist" />
                      <span>Team statistics evolution across seasons</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <TrendingUp className="w-4 h-4 text-goal" />
                      <span>League-wide metric comparisons</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <BarChart3 className="w-4 h-4 text-primary" />
                      <span>Interactive charts and visualizations</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
            
            {/* Sample Data Preview */}
            {seasons && seasons.length > 0 && (
              <div className="bg-muted/10 rounded-lg p-4">
                <h3 className="font-display text-xs font-semibold uppercase text-muted-foreground mb-3">
                  Available Seasons
                </h3>
                <div className="flex flex-wrap gap-2">
                  {seasons.map((season: any) => (
                    <span
                      key={season.season_id}
                      className="text-xs font-mono bg-accent px-2 py-1 rounded uppercase"
                    >
                      {season.season || season.season_id}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
