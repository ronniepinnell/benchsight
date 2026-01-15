// src/components/teams/team-analytics-tab.tsx
import { createClient } from '@/lib/supabase/server'
import { BarChart3, Target, TrendingUp } from 'lucide-react'
import { cn } from '@/lib/utils'
import { TeamAdvancedStatsSection } from './advanced-stats-section'

interface TeamAnalyticsTabProps {
  teamId: string
  teamName: string
  seasonId: string
  gameType: string
}

export async function TeamAnalyticsTab({ teamId, teamName, seasonId, gameType }: TeamAnalyticsTabProps) {
  const supabase = await createClient()
  
  // Get zone time data
  // fact_team_zone_time has: offensive_zone_events, neutral_zone_events, defensive_zone_events
  // fact_team_zone_time does NOT have team_id - need to filter by game_id -> dim_schedule -> venue
  const { data: scheduleGames } = await supabase
    .from('dim_schedule')
    .select('game_id, home_team_id, away_team_id')
    .eq('season_id', seasonId)
    .or(`home_team_id.eq.${teamId},away_team_id.eq.${teamId}`)
  
  const gameIds = (scheduleGames || []).map(g => g.game_id).filter(Boolean)
  
  // Create map of game_id -> team venue
  const gameVenueMap = new Map<number, 'home' | 'away'>()
  scheduleGames?.forEach((game: any) => {
    if (game.home_team_id === teamId) {
      gameVenueMap.set(game.game_id, 'home')
    } else if (game.away_team_id === teamId) {
      gameVenueMap.set(game.game_id, 'away')
    }
  })
  
  const { data: zoneTimeData } = gameIds.length > 0 ? await supabase
    .from('fact_team_zone_time')
    .select('*')
    .in('game_id', gameIds)
    .limit(500)
  : { data: [] }
  
  // Filter to this team's zone time (by venue matching)
  const teamZoneTime = (zoneTimeData || []).filter((zt: any) => {
    const gameId = zt.game_id
    const expectedVenue = gameVenueMap.get(gameId)
    return expectedVenue && zt.venue === expectedVenue
  })
  
  // Get WOWY data - fact_wowy has player_1_id, player_2_id, home_team_id, away_team_id
  // Filter by team via home_team_id or away_team_id
  const { data: wowyData } = gameIds.length > 0 ? await supabase
    .from('fact_wowy')
    .select('*')
    .in('game_id', gameIds)
    .or(`home_team_id.eq.${teamId},away_team_id.eq.${teamId}`)
    .limit(500)
  : { data: [] }
  
  // Aggregate zone time - use events as proxy for time
  const zoneTimeTotals = (teamZoneTime || []).reduce((acc, zt) => ({
    offensive: acc.offensive + (Number(zt.offensive_zone_events || 0)),
    neutral: acc.neutral + (Number(zt.neutral_zone_events || 0)),
    defensive: acc.defensive + (Number(zt.defensive_zone_events || 0)),
  }), { offensive: 0, neutral: 0, defensive: 0 })
  
  const totalZoneTime = zoneTimeTotals.offensive + zoneTimeTotals.neutral + zoneTimeTotals.defensive
  const offensivePct = totalZoneTime > 0 ? (zoneTimeTotals.offensive / totalZoneTime) * 100 : 0
  const defensivePct = totalZoneTime > 0 ? (zoneTimeTotals.defensive / totalZoneTime) * 100 : 0
  
  return (
    <div className="space-y-6">
      <TeamAdvancedStatsSection 
        teamId={teamId}
        teamName={teamName}
        seasonId={seasonId}
        gameType={gameType}
      />
      
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="px-4 py-3 bg-accent border-b border-border">
          <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
            <Target className="w-4 h-4" />
            Zone Time Analysis
          </h2>
        </div>
        <div className="p-6">
          {totalZoneTime > 0 ? (
            <div className="space-y-4">
              <div className="grid md:grid-cols-3 gap-4">
                <div className="bg-muted/30 rounded-lg p-4 text-center">
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Offensive Zone</div>
                  <div className="font-mono text-2xl font-bold text-save">
                    {offensivePct.toFixed(1)}%
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {zoneTimeTotals.offensive} events
                  </div>
                </div>
                <div className="bg-muted/30 rounded-lg p-4 text-center">
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Neutral Zone</div>
                  <div className="font-mono text-2xl font-bold text-muted-foreground">
                    {totalZoneTime > 0 ? ((zoneTimeTotals.neutral / totalZoneTime) * 100).toFixed(1) : '0.0'}%
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {zoneTimeTotals.neutral} events
                  </div>
                </div>
                <div className="bg-muted/30 rounded-lg p-4 text-center">
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Defensive Zone</div>
                  <div className="font-mono text-2xl font-bold text-goal">
                    {defensivePct.toFixed(1)}%
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {zoneTimeTotals.defensive} events
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground text-center py-8">
              No zone time data available for {teamName} in this season.
            </p>
          )}
        </div>
      </div>
      
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="px-4 py-3 bg-accent border-b border-border">
          <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
            <TrendingUp className="w-4 h-4" />
            WOWY Analysis
          </h2>
        </div>
        <div className="p-6">
          {wowyData && wowyData.length > 0 ? (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground mb-4">
                WOWY (With Or Without You) analysis shows how players perform together vs. apart.
                {wowyData.length} player combinations tracked.
              </p>
              
              {/* WOWY Table */}
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border bg-accent/50">
                      <th className="px-3 py-2 text-left font-display text-xs text-muted-foreground">Player 1</th>
                      <th className="px-3 py-2 text-left font-display text-xs text-muted-foreground">Player 2</th>
                      <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">TOI Together</th>
                      <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">CF% Together</th>
                      <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">CF% Apart</th>
                      <th className="px-2 py-2 text-center font-display text-xs text-muted-foreground">Delta</th>
                    </tr>
                  </thead>
                  <tbody>
                    {wowyData.slice(0, 20).map((wowy: any, index: number) => (
                      <tr key={index} className="border-b border-border/50 hover:bg-muted/30">
                        <td className="px-3 py-2">{wowy.player_1_name || wowy.player_1_id || '-'}</td>
                        <td className="px-3 py-2">{wowy.player_2_name || wowy.player_2_id || '-'}</td>
                        <td className="px-2 py-2 text-center font-mono">
                          {wowy.toi_together ? Math.round(wowy.toi_together / 60) : '-'} min
                        </td>
                        <td className="px-2 py-2 text-center font-mono">
                          {wowy.cf_pct_together ? wowy.cf_pct_together.toFixed(1) + '%' : '-'}
                        </td>
                        <td className="px-2 py-2 text-center font-mono">
                          {wowy.cf_pct_apart ? wowy.cf_pct_apart.toFixed(1) + '%' : '-'}
                        </td>
                        <td className={cn(
                          "px-2 py-2 text-center font-mono font-semibold",
                          wowy.cf_pct_delta > 0 ? "text-save" : wowy.cf_pct_delta < 0 ? "text-goal" : ""
                        )}>
                          {wowy.cf_pct_delta ? (wowy.cf_pct_delta > 0 ? '+' : '') + wowy.cf_pct_delta.toFixed(1) + '%' : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground text-center py-8">
              No WOWY data available for {teamName} in this season.
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
