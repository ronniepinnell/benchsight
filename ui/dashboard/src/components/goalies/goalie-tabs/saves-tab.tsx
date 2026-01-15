// src/components/goalies/goalie-tabs/saves-tab.tsx
import Link from 'next/link'
import { createClient } from '@/lib/supabase/server'
import { Target } from 'lucide-react'

interface SavesTabProps {
  goalieId: string
}

export async function SavesTab({ goalieId }: SavesTabProps) {
  const supabase = await createClient()
  
  // Get saves data - try fact_saves first, fallback to fact_goalie_game_stats
  let savesData: any[] = []
  let saveTypeCounts = new Map<string, number>()
  
  // Try fact_saves table - fact_saves doesn't have goalie_id, need to filter by event_type='Save' and player_id
  // Or use fact_events filtered by Save events
  const { data: saveEvents } = await supabase
    .from('fact_events')
    .select('*')
    .eq('event_type', 'Save')
    .order('game_id', { ascending: false })
    .limit(500)
  
  // Also try fact_saves if it exists
  const { data: factSavesData, error: savesError } = await supabase
    .from('fact_saves')
    .select('*')
    .order('game_id', { ascending: false })
    .limit(500)
    .catch(() => ({ data: null, error: null }))
  
  // Get goalie's game stats for save breakdown
  const { data: goalieGameStats } = await supabase
    .from('fact_goalie_game_stats')
    .select('game_id, saves, shots_against, hd_saves, hd_shots_against, saves_butterfly, saves_pad, saves_glove, saves_blocker, saves_chest, saves_stick, saves_scramble, date')
    .eq('player_id', goalieId)
    .order('game_id', { ascending: false })
    .limit(50)
  
  if (goalieGameStats && goalieGameStats.length > 0) {
    // Create detailed save breakdown from game stats
    savesData = goalieGameStats.map((stat: any) => ({
      game_id: stat.game_id,
      date: stat.date,
      saves: stat.saves,
      shots_against: stat.shots_against,
      hd_saves: stat.hd_saves,
      hd_shots_against: stat.hd_shots_against,
      save_types: {
        butterfly: stat.saves_butterfly || 0,
        pad: stat.saves_pad || 0,
        glove: stat.saves_glove || 0,
        blocker: stat.saves_blocker || 0,
        chest: stat.saves_chest || 0,
        stick: stat.saves_stick || 0,
        scramble: stat.saves_scramble || 0,
      }
    }))
    
    // Aggregate save types
    goalieGameStats.forEach((stat: any) => {
      if (stat.saves_butterfly) saveTypeCounts.set('Butterfly', (saveTypeCounts.get('Butterfly') || 0) + (stat.saves_butterfly || 0))
      if (stat.saves_pad) saveTypeCounts.set('Pad', (saveTypeCounts.get('Pad') || 0) + (stat.saves_pad || 0))
      if (stat.saves_glove) saveTypeCounts.set('Glove', (saveTypeCounts.get('Glove') || 0) + (stat.saves_glove || 0))
      if (stat.saves_blocker) saveTypeCounts.set('Blocker', (saveTypeCounts.get('Blocker') || 0) + (stat.saves_blocker || 0))
      if (stat.saves_chest) saveTypeCounts.set('Chest', (saveTypeCounts.get('Chest') || 0) + (stat.saves_chest || 0))
      if (stat.saves_stick) saveTypeCounts.set('Stick', (saveTypeCounts.get('Stick') || 0) + (stat.saves_stick || 0))
      if (stat.saves_scramble) saveTypeCounts.set('Scramble', (saveTypeCounts.get('Scramble') || 0) + (stat.saves_scramble || 0))
    })
  } else {
    // Fallback: Get save data from fact_goalie_game_stats
    const { data: goalieGameStats } = await supabase
      .from('fact_goalie_game_stats')
      .select('game_id, saves, shots_against, hd_saves, hd_shots_against, date')
      .eq('player_id', goalieId)
      .order('game_id', { ascending: false })
      .limit(50)
    
    if (goalieGameStats && goalieGameStats.length > 0) {
      // Create summary from game stats
      savesData = goalieGameStats.map((stat: any) => ({
        game_id: stat.game_id,
        save_type: 'All Saves',
        save_location: 'Various',
        danger_level: 'Mixed',
        date: stat.date,
        saves: stat.saves,
        shots_against: stat.shots_against,
        hd_saves: stat.hd_saves,
        hd_shots_against: stat.hd_shots_against,
      }))
      
      // Aggregate by game
      saveTypeCounts.set('All Saves', savesData.reduce((sum, s) => sum + (s.saves || 0), 0))
      saveTypeCounts.set('HD Saves', savesData.reduce((sum, s) => sum + (s.hd_saves || 0), 0))
    }
  }
  
  if (!savesData || savesData.length === 0) {
    return (
      <div className="bg-card rounded-xl border border-border p-8 text-center">
        <p className="text-muted-foreground">No save data available for this goalie.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="px-4 py-3 bg-accent border-b border-border">
          <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
            <Target className="w-4 h-4" />
            Save-by-Save Breakdown
          </h2>
        </div>
        <div className="p-6">
          <p className="text-sm text-muted-foreground mb-4">
            {savesData.length} saves tracked
          </p>
          
          {/* Save Type Distribution */}
          <div className="mb-6">
            <h3 className="font-display text-sm font-semibold mb-3">Save Type Distribution</h3>
            <div className="grid md:grid-cols-4 gap-4">
              {Array.from(saveTypeCounts.entries()).map(([type, count]) => (
                <div key={type} className="bg-muted/30 rounded-lg p-4 text-center">
                  <div className="text-xs font-mono text-muted-foreground uppercase mb-1">{type}</div>
                  <div className="font-mono text-2xl font-bold text-foreground">{count}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Saves Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-2 font-mono text-xs text-muted-foreground uppercase">Game</th>
                  <th className="text-left py-2 font-mono text-xs text-muted-foreground uppercase">Date</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">Saves</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">Shots</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">SV%</th>
                  <th className="text-right py-2 font-mono text-xs text-muted-foreground uppercase">HD Saves</th>
                  <th className="text-left py-2 font-mono text-xs text-muted-foreground uppercase">Save Types</th>
                </tr>
              </thead>
              <tbody>
                {savesData.slice(0, 50).map((save: any, index: number) => {
                  const savePct = save.shots_against > 0 
                    ? ((save.saves || 0) / save.shots_against * 100).toFixed(1) 
                    : '-'
                  const hdSavePct = save.hd_shots_against > 0
                    ? ((save.hd_saves || 0) / save.hd_shots_against * 100).toFixed(1)
                    : '-'
                  
                  const saveTypes = save.save_types || {}
                  const typeBreakdown = Object.entries(saveTypes)
                    .filter(([_, count]: [string, any]) => count > 0)
                    .map(([type, count]: [string, any]) => `${type}: ${count}`)
                    .join(', ') || 'Various'
                  
                  return (
                    <tr key={index} className="border-b border-border/50 hover:bg-muted/30">
                      <td className="py-2">
                        <Link 
                          href={`/norad/games/${save.game_id}`}
                          className="text-foreground hover:text-primary transition-colors"
                        >
                          {save.game_id || '-'}
                        </Link>
                      </td>
                      <td className="py-2 text-muted-foreground">
                        {save.date ? new Date(save.date).toLocaleDateString() : '-'}
                      </td>
                      <td className="text-right py-2 font-mono">{save.saves || 0}</td>
                      <td className="text-right py-2 font-mono">{save.shots_against || 0}</td>
                      <td className="text-right py-2 font-mono">{savePct}%</td>
                      <td className="text-right py-2 font-mono">
                        {save.hd_saves || 0} / {save.hd_shots_against || 0} ({hdSavePct}%)
                      </td>
                      <td className="py-2 text-xs text-muted-foreground">{typeBreakdown}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
