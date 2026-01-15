// src/app/(dashboard)/analytics/lines/page.tsx
import Link from 'next/link'
import { createClient } from '@/lib/supabase/server'
import { ArrowLeft, Users, TrendingUp, BarChart3, Activity, Target } from 'lucide-react'
import { cn } from '@/lib/utils'
import { PlayerPhoto } from '@/components/players/player-photo'
import { TeamLogo } from '@/components/teams/team-logo'
import { ExportButton } from '@/components/export/ExportButton'

export const revalidate = 300

export const metadata = {
  title: 'Line Combinations Analysis | BenchSight Analytics',
  description: 'Line combination performance, WOWY analysis, and optimal line suggestions',
}

export default async function LineCombinationsPage() {
  const supabase = await createClient()
  
  // Get line combination data
  const { data: lineCombos } = await supabase
    .from('fact_line_combos')
    .select('*')
    .limit(500)
  
  // Aggregate line combos by team and line
  const linePerformance = new Map<string, any>()
  
  if (lineCombos) {
    for (const combo of lineCombos) {
      // fact_line_combos uses forward_combo (comma-separated string), not forward_1, forward_2, forward_3
      const forwardCombo = combo.forward_combo || ''
      if (!forwardCombo) continue
      
      // Use forward_combo as the key
      const lineKey = `${combo.home_team_id || combo.away_team_id || 'unknown'}_${forwardCombo}`
      
      if (!linePerformance.has(lineKey)) {
        linePerformance.set(lineKey, {
          teamId: combo.home_team_id || combo.away_team_id,
          forwardCombo: forwardCombo,
          games: 0,
          toi: 0,
          goalsFor: 0,
          goalsAgainst: 0,
          cf: 0,
          ca: 0,
        })
      }
      
      const line = linePerformance.get(lineKey)!
      line.games += 1
      line.toi += Number(combo.toi_together || 0)
      line.goalsFor += Number(combo.goals_for || 0)
      line.goalsAgainst += Number(combo.goals_against || 0)
      line.cf += Number(combo.corsi_for || 0)
      line.ca += Number(combo.corsi_against || 0)
    }
  }
  
  // Get WOWY data for display
  const { data: wowyData } = await supabase
    .from('fact_wowy')
    .select('*')
    .limit(100)
  
  // Convert to array and calculate rates
  const lineStats = Array.from(linePerformance.values())
    .filter(line => line.games > 0 && line.toi > 0)
    .map(line => {
      const cfPct = (line.cf + line.ca) > 0 ? (line.cf / (line.cf + line.ca)) * 100 : 50
      const gfPct = (line.goalsFor + line.goalsAgainst) > 0 ? (line.goalsFor / (line.goalsFor + line.goalsAgainst)) * 100 : 50
      const toiMinutes = line.toi / 60
      
      return {
        ...line,
        cfPct,
        gfPct,
        toiMinutes,
        goalsForPer60: toiMinutes > 0 ? (line.goalsFor / toiMinutes) * 60 : 0,
        goalsAgainstPer60: toiMinutes > 0 ? (line.goalsAgainst / toiMinutes) * 60 : 0,
        goalDiff: line.goalsFor - line.goalsAgainst,
      }
    })
    .sort((a, b) => b.toiMinutes - a.toiMinutes)
  
  // Get players for names - parse forward_combo
  const allPlayerIds = new Set<string>()
  lineStats.forEach(line => {
    const playerIds = (line.forwardCombo || '').split(',').filter(Boolean)
    playerIds.forEach(id => allPlayerIds.add(id.trim()))
  })
  
  const { data: playersData } = await supabase
    .from('dim_player')
    .select('player_id, player_name, player_full_name, player_image')
    .in('player_id', Array.from(allPlayerIds))
  
  const playersMap = new Map(
    (playersData || []).map(p => [String(p.player_id), p])
  )
  
  // Get teams for logos
  const teamIds = [...new Set(lineStats.map(l => l.teamId).filter(Boolean))]
  const { data: teamsData } = await supabase
    .from('dim_team')
    .select('team_id, team_name, team_logo, team_cd, primary_color, team_color1')
    .in('team_id', teamIds)
  
  const teamsMap = new Map(
    (teamsData || []).map(t => [String(t.team_id), t])
  )
  
  // Add player and team names - parse forward_combo
  const linesWithNames = lineStats.map(line => {
    const team = teamsMap.get(String(line.teamId))
    const playerIds = (line.forwardCombo || '').split(',').filter(Boolean).map(id => id.trim())
    const playerNames = playerIds
      .map(id => {
        const player = playersMap.get(id)
        return player?.player_name || player?.player_full_name || 'Unknown'
      })
      .filter(Boolean)
    
    return {
      ...line,
      team,
      playerIds: playerIds,
      playerNames: playerNames,
      lineName: playerNames.join(' - ') || 'Unknown Line',
    }
  })
  
  // Top performing lines
  const topCFPct = [...linesWithNames]
    .filter(l => l.games >= 3)
    .sort((a, b) => b.cfPct - a.cfPct)
    .slice(0, 10)
  
  const topGFPct = [...linesWithNames]
    .filter(l => l.games >= 3)
    .sort((a, b) => b.gfPct - a.gfPct)
    .slice(0, 10)
  
  const topTOI = [...linesWithNames]
    .sort((a, b) => b.toiMinutes - a.toiMinutes)
    .slice(0, 10)
  
  return (
    <div className="space-y-6">
      {/* Back Link */}
      <Link 
        href="/norad/analytics/overview" 
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Analytics
      </Link>
      
      {/* Header */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="px-4 py-3 bg-accent border-b border-border">
          <h1 className="font-display text-lg font-semibold uppercase tracking-wider flex items-center gap-2">
            <Users className="w-5 h-5" />
            Line Combinations Analysis
          </h1>
        </div>
        <div className="p-6">
          <p className="text-sm text-muted-foreground mb-6">
            Analyze line combination performance, chemistry, and effectiveness. WOWY (With Or Without You) 
            analysis shows how players perform together vs. apart.
          </p>
          
          {/* Summary Stats */}
          <div className="grid md:grid-cols-4 gap-4 mb-6">
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Total Lines</div>
              <div className="font-mono text-2xl font-bold text-foreground">
                {linesWithNames.length}
              </div>
            </div>
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Total TOI</div>
              <div className="font-mono text-2xl font-bold text-primary">
                {Math.round(linesWithNames.reduce((sum, l) => sum + l.toiMinutes, 0))} min
              </div>
            </div>
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Avg CF%</div>
              <div className="font-mono text-2xl font-bold text-assist">
                {linesWithNames.length > 0 
                  ? (linesWithNames.reduce((sum, l) => sum + l.cfPct, 0) / linesWithNames.length).toFixed(1)
                  : '0.0'}%
              </div>
            </div>
            <div className="bg-muted/30 rounded-lg p-4 text-center">
              <div className="text-xs font-mono text-muted-foreground uppercase mb-1">Total Goals</div>
              <div className="font-mono text-2xl font-bold text-goal">
                {linesWithNames.reduce((sum, l) => sum + l.goalsFor, 0)}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Top Performing Lines */}
      <div className="grid md:grid-cols-3 gap-6">
        {/* Top CF% */}
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Top CF% (Min 3 GP)
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {topCFPct.map((line, index) => (
                <div
                  key={index}
                  className="p-3 bg-muted/30 rounded-lg"
                >
                  <div className="flex items-center justify-between mb-2">
                    {line.team && (
                      <TeamLogo
                        src={line.team.team_logo || null}
                        name={line.team.team_name || ''}
                        abbrev={line.team.team_cd}
                        size="xs"
                        showGradient={false}
                      />
                    )}
                    <span className="font-mono text-xs text-muted-foreground">#{index + 1}</span>
                  </div>
                  <div className="text-sm font-semibold mb-1">{line.lineName}</div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-muted-foreground">{line.games} GP</span>
                    <span className="font-mono font-bold text-save">{line.cfPct.toFixed(1)}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
        
        {/* Top GF% */}
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Target className="w-4 h-4" />
              Top GF% (Min 3 GP)
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {topGFPct.map((line, index) => (
                <div
                  key={index}
                  className="p-3 bg-muted/30 rounded-lg"
                >
                  <div className="flex items-center justify-between mb-2">
                    {line.team && (
                      <TeamLogo
                        src={line.team.team_logo || null}
                        name={line.team.team_name || ''}
                        abbrev={line.team.team_cd}
                        size="xs"
                        showGradient={false}
                      />
                    )}
                    <span className="font-mono text-xs text-muted-foreground">#{index + 1}</span>
                  </div>
                  <div className="text-sm font-semibold mb-1">{line.lineName}</div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-muted-foreground">{line.games} GP</span>
                    <span className="font-mono font-bold text-save">{line.gfPct.toFixed(1)}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
        
        {/* Top TOI */}
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Activity className="w-4 h-4" />
              Most Used Lines
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {topTOI.map((line, index) => (
                <div
                  key={index}
                  className="p-3 bg-muted/30 rounded-lg"
                >
                  <div className="flex items-center justify-between mb-2">
                    {line.team && (
                      <TeamLogo
                        src={line.team.team_logo || null}
                        name={line.team.team_name || ''}
                        abbrev={line.team.team_cd}
                        size="xs"
                        showGradient={false}
                      />
                    )}
                    <span className="font-mono text-xs text-muted-foreground">#{index + 1}</span>
                  </div>
                  <div className="text-sm font-semibold mb-1">{line.lineName}</div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-muted-foreground">{line.games} GP</span>
                    <span className="font-mono font-bold text-primary">{Math.round(line.toiMinutes)} min</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
      
      {/* Comprehensive Line Stats Table */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="px-4 py-3 bg-accent border-b border-border flex items-center justify-between">
          <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
            <BarChart3 className="w-4 h-4" />
            Comprehensive Line Statistics
          </h2>
          <ExportButton 
            data={linesWithNames
              .filter(l => l.games >= 3)
              .map(l => ({
                Line: l.lineName,
                Team: l.team?.team_name || 'Unknown',
                GP: l.games,
                TOI: Math.round(l.toiMinutes),
                GF: l.goalsFor,
                GA: l.goalsAgainst,
                'CF%': l.cfPct.toFixed(1) + '%',
                'GF%': l.gfPct.toFixed(1) + '%',
              }))}
            filename="line_combinations"
          />
        </div>
        <div className="p-6">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-2 font-mono text-xs text-muted-foreground uppercase">Line</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">GP</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">TOI</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">GF</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">GA</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">CF%</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">GF%</th>
                </tr>
              </thead>
              <tbody>
                {linesWithNames
                  .filter(l => l.games >= 3)
                  .sort((a, b) => b.cfPct - a.cfPct)
                  .slice(0, 50)
                  .map((line, index) => (
                  <tr key={index} className="border-b border-border/50 hover:bg-muted/30">
                    <td className="py-3">
                      <div className="flex items-center gap-2">
                        {line.team && (
                          <TeamLogo
                            src={line.team.team_logo || null}
                            name={line.team.team_name || ''}
                            abbrev={line.team.team_cd}
                            size="xs"
                            showGradient={false}
                          />
                        )}
                        <div>
                          <div className="font-semibold text-foreground">
                            {line.lineName}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {line.team?.team_name || 'Unknown'}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="text-right py-3 font-mono">{line.games}</td>
                    <td className="text-right py-3 font-mono">{Math.round(line.toiMinutes)}</td>
                    <td className="text-right py-3 font-mono text-save">{line.goalsFor}</td>
                    <td className="text-right py-3 font-mono text-goal">{line.goalsAgainst}</td>
                    <td className={cn(
                      "text-right py-3 font-mono font-semibold",
                      line.cfPct >= 50 ? "text-save" : "text-goal"
                    )}>
                      {line.cfPct.toFixed(1)}%
                    </td>
                    <td className={cn(
                      "text-right py-3 font-mono",
                      line.gfPct >= 50 ? "text-save" : "text-goal"
                    )}>
                      {line.gfPct.toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      
      {/* WOWY Analysis Section */}
      {wowyData && wowyData.length > 0 && (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <div className="px-4 py-3 bg-accent border-b border-border">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
              <Users className="w-4 h-4" />
              WOWY Analysis (With Or Without You)
            </h2>
          </div>
          <div className="p-6">
            <p className="text-sm text-muted-foreground mb-4">
              {wowyData.length} player combinations tracked. WOWY shows how players perform together vs. apart.
            </p>
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
                  {wowyData.slice(0, 30).map((wowy: any, index: number) => (
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
        </div>
      )}
    </div>
  )
}
