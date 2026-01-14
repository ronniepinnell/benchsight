'use client'

import { useEffect, useState } from 'react'
import { StatDrilldown } from './stat-drilldown'
import { Loader2 } from 'lucide-react'

interface GameStatDrilldownProps {
  playerId: string
  statKey: string
  statLabel: string
  gameIds?: number[]
}

export function GameStatDrilldown({
  playerId,
  statKey,
  statLabel,
  gameIds
}: GameStatDrilldownProps) {
  const [games, setGames] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchGameStats() {
      try {
        const response = await fetch(
          `/api/players/${playerId}/game-stats?stat=${encodeURIComponent(statKey)}${gameIds && gameIds.length > 0 ? `&gameIds=${gameIds.join(',')}` : ''}`
        )
        const data = await response.json()
        setGames(data.games || [])
      } catch (error) {
        console.error('Error fetching game stats:', error)
        setGames([])
      } finally {
        setLoading(false)
      }
    }

    fetchGameStats()
  }, [playerId, statKey, gameIds])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-4">
        <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />
      </div>
    )
  }

  // Map stat key to actual column names (comprehensive list with all variations)
  const columnMap: Record<string, string[]> = {
    'CF%': ['cf_pct', 'cf%'],
    'FF%': ['ff_pct', 'ff%'],
    'CF': ['corsi_for', 'cf'],
    'Corsi For': ['corsi_for', 'cf'],
    'CA': ['corsi_against', 'ca'],
    'Corsi Against': ['corsi_against', 'ca'],
    'FF': ['fenwick_for', 'ff'],
    'Fenwick For': ['fenwick_for', 'ff'],
    'FA': ['fenwick_against', 'fa'],
    'Fenwick Against': ['fenwick_against', 'fa'],
    'Goals': ['goals', 'g'],
    'Assists': ['assists', 'a'],
    'Points': ['points', 'pts'],
    'Shooting %': ['shooting_pct', 'sh_pct', 'shot_pct'],
    'Shots': ['shots'],
    'SOG': ['sog', 'shots_on_goal', 'shots on goal'],
    'Shots on Goal': ['sog', 'shots_on_goal'],
    'TOI': ['toi_seconds', 'toi_playing_seconds'],
    '+/-': ['plus_minus', 'plus_minus_total'],
    '+/- (EV)': ['plus_minus_ev'],
    'Hits': ['hits', 'hit'],
    'Blocks': ['blocks', 'blk'],
    'Takeaways': ['takeaways', 'take'],
    'Giveaways': ['giveaways', 'give'],
    'Bad Giveaways': ['bad_giveaways', 'give_bad'],
    'Faceoff %': ['fo_pct'],
    'Pass %': ['pass_pct'],
    'xG': ['xg_for', 'xg'],
    'WAR': ['war'],
    'GAR': ['gar_total', 'gar'],
    'Game Score': ['game_score'],
    'Goals/60': ['goals_per_60', 'g_60'],
    'Assists/60': ['assists_per_60', 'a_60'],
    'Points/60': ['points_per_60', 'pts_60'],
    'Zone Entry %': ['zone_entry_pct'],
    'Zone Exit %': ['zone_exit_pct'],
  }

  // Get possible column names for this stat
  const mappedColumns = columnMap[statLabel] || []
  const normalizedStatKey = statKey.toLowerCase().replace(/\s+/g, '_')
  
  // Try multiple possible column names (order matters - try mapped first, then variations)
  const possibleColumns = [
    ...mappedColumns,
    normalizedStatKey,
    statKey.toLowerCase(),
    statKey.toLowerCase().replace(/[\/\(\)]/g, '_'),
    statKey.toLowerCase().replace(/[\/\(\)%]/g, ''),
    statKey.toLowerCase().replace(/[\/\(\)%]/g, '').replace(/_/g, ''),
  ]

  const gameStats: any[] = games.map(game => {
    let value = null
    
    // Try each possible column name
    for (const col of possibleColumns) {
      if (game[col] !== null && game[col] !== undefined && game[col] !== '') {
        // Handle string numbers
        if (typeof game[col] === 'string') {
          const parsed = parseFloat(game[col])
          if (!isNaN(parsed)) {
            value = parsed
          } else {
            value = game[col]
          }
        } else {
          value = game[col]
        }
        break
      }
    }
    
    // For per-60 stats, calculate if not present
    if (value === null && (statKey.includes('60') || statKey.includes('per_60'))) {
      let baseStat = statKey.replace('_per_60', '').replace('_/60', '').replace('/60', '').replace('_60', '')
      // Try different column name variations for base stat
      const baseValue = game[baseStat] ?? 
                       game[baseStat.toLowerCase()] ?? 
                       game[baseStat.replace(/_/g, '')] ??
                       (baseStat === 'goals' ? (game.g ?? game.g) : null) ??
                       (baseStat === 'assists' ? (game.a ?? game.a) : null) ??
                       (baseStat === 'points' ? (game.pts ?? game.points) : null) ??
                       0
      
      const toiSeconds = game.toi_seconds ?? game.toi_playing_seconds ?? (game.toi_minutes ? game.toi_minutes * 60 : 0)
      const toiMinutes = toiSeconds / 60
      
      if (toiMinutes > 0 && baseValue !== null && baseValue !== undefined) {
        const numBase = typeof baseValue === 'string' ? parseFloat(baseValue) : baseValue
        if (!isNaN(numBase)) {
          value = (numBase / toiMinutes) * 60
        }
      }
    }
    
    // For percentages, calculate if not present
    if (value === null && (statKey.includes('pct') || statKey.includes('%') || statLabel.includes('%'))) {
      if (statKey.includes('fo') || statKey.includes('faceoff') || statLabel.includes('Faceoff')) {
        const foWins = game.fo_wins ?? game.fow ?? game.foWins ?? 0
        const foLosses = game.fo_losses ?? game.fol ?? game.foLosses ?? 0
        const foTotal = game.fo_total ?? game.fo_taken ?? ((typeof foWins === 'number' ? foWins : parseFloat(String(foWins)) || 0) + (typeof foLosses === 'number' ? foLosses : parseFloat(String(foLosses)) || 0))
        const winsNum = typeof foWins === 'string' ? parseFloat(foWins) : foWins
        const totalNum = typeof foTotal === 'string' ? parseFloat(foTotal) : foTotal
        value = totalNum > 0 ? (winsNum / totalNum) * 100 : 0
      } else if (statKey.includes('pass') || statLabel.includes('Pass')) {
        const passComp = game.pass_completed ?? game.pass_comp ?? game.passCompleted ?? 0
        const passAtt = game.pass_attempts ?? game.pass_att ?? game.passAttempts ?? 0
        const compNum = typeof passComp === 'string' ? parseFloat(passComp) : passComp
        const attNum = typeof passAtt === 'string' ? parseFloat(passAtt) : passAtt
        value = attNum > 0 ? (compNum / attNum) * 100 : 0
      } else if (statKey.includes('zone_entry') || statLabel.includes('Zone Entry')) {
        const zeSuccess = game.zone_entries_successful ?? game.zone_entry_controlled ?? game.zoneEntriesSuccessful ?? 0
        const ze = game.zone_entries ?? game.zone_entry ?? game.zoneEntries ?? 0
        const successNum = typeof zeSuccess === 'string' ? parseFloat(zeSuccess) : zeSuccess
        const totalNum = typeof ze === 'string' ? parseFloat(ze) : ze
        value = totalNum > 0 ? (successNum / totalNum) * 100 : 0
      } else if (statKey.includes('zone_exit') || statLabel.includes('Zone Exit')) {
        const zxSuccess = game.zone_exits_successful ?? game.zone_exit_controlled ?? game.zoneExitsSuccessful ?? 0
        const zx = game.zone_exits ?? game.zone_exit ?? game.zoneExits ?? 0
        const successNum = typeof zxSuccess === 'string' ? parseFloat(zxSuccess) : zxSuccess
        const totalNum = typeof zx === 'string' ? parseFloat(zx) : zx
        value = totalNum > 0 ? (successNum / totalNum) * 100 : 0
      } else if (statKey.includes('shooting') || statLabel.includes('Shooting')) {
        const goals = game.goals ?? game.g ?? 0
        const sog = game.sog ?? game.shots_on_goal ?? 0
        const goalsNum = typeof goals === 'string' ? parseFloat(goals) : goals
        const sogNum = typeof sog === 'string' ? parseFloat(sog) : sog
        value = sogNum > 0 ? (goalsNum / sogNum) * 100 : 0
      } else if (statKey.includes('cf_pct') || statLabel.includes('CF%')) {
        const cf = game.corsi_for ?? game.cf ?? 0
        const ca = game.corsi_against ?? game.ca ?? 0
        const cfNum = typeof cf === 'string' ? parseFloat(cf) : cf
        const caNum = typeof ca === 'string' ? parseFloat(ca) : ca
        const total = cfNum + caNum
        value = total > 0 ? (cfNum / total) * 100 : 0
      } else if (statKey.includes('ff_pct') || statLabel.includes('FF%')) {
        const ff = game.fenwick_for ?? game.ff ?? 0
        const fa = game.fenwick_against ?? game.fa ?? 0
        const ffNum = typeof ff === 'string' ? parseFloat(ff) : ff
        const faNum = typeof fa === 'string' ? parseFloat(fa) : fa
        const total = ffNum + faNum
        value = total > 0 ? (ffNum / total) * 100 : 0
      }
    }
    
    // Fallback: try direct statKey match
    if (value === null || value === undefined) {
      value = game[statKey] ?? game[normalizedStatKey] ?? 0
    }
    
    // Ensure value is a number if it should be
    if (value !== null && value !== undefined && value !== '') {
      if (typeof value === 'string') {
        const parsed = parseFloat(value)
        value = isNaN(parsed) ? value : parsed
      }
    } else {
      value = 0
    }
    
    return {
      game_id: game.game_id,
      date: game.date,
      opponent: game.opponent_team_name || game.team_name,
      value: value,
    }
  })

  // Format function based on stat type
  const formatValue = (val: number | string): string => {
    if (val === null || val === undefined) return '-'
    const num = typeof val === 'string' ? parseFloat(val) : val
    if (isNaN(num)) return String(val)
    
    // Percentage stats
    if (statLabel.includes('%') || columnName.includes('_pct') || columnName === 'cf_pct' || columnName === 'ff_pct') {
      return typeof num === 'number' ? num.toFixed(1) + '%' : String(val)
    }
    
    // Time stats
    if (columnName.includes('toi') || columnName.includes('seconds')) {
      const minutes = Math.floor(num / 60)
      const secs = Math.floor(num % 60)
      return `${minutes}:${secs.toString().padStart(2, '0')}`
    }
    
    // Decimal stats
    if (statLabel.includes('xG') || statLabel.includes('WAR') || statLabel.includes('GAR') || statLabel.includes('Game Score')) {
      return num.toFixed(2)
    }
    
    // Integer stats
    return Math.round(num).toString()
  }

  return (
    <StatDrilldown
      statLabel={statLabel}
      games={gameStats}
      formatValue={formatValue}
    />
  )
}
