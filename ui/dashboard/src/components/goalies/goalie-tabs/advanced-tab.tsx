// src/components/goalies/goalie-tabs/advanced-tab.tsx
import { BarChart3 } from 'lucide-react'
import { StatCard } from '@/components/players/stat-card'

interface AdvancedTabProps {
  advancedStats: any
  gameStats: any[]
}

export function AdvancedTab({ advancedStats }: AdvancedTabProps) {
  const formatDecimal = (val: number | null | undefined, decimals: number = 2) => {
    if (val === null || val === undefined) return '-'
    return Number(val).toFixed(decimals)
  }

  const formatPercent = (val: number | null | undefined) => {
    if (val === null || val === undefined) return '-'
    return Number(val).toFixed(1) + '%'
  }

  const hdSavePct = advancedStats.hdShotsAgainst > 0
    ? (advancedStats.hdSaves / advancedStats.hdShotsAgainst) * 100
    : 0
  const qualityStartRate = advancedStats.games > 0
    ? (advancedStats.qualityStarts / advancedStats.games) * 100
    : 0

  return (
    <div className="space-y-6">
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="px-4 py-3 bg-accent border-b border-border">
          <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
            <BarChart3 className="w-4 h-4" />
            Advanced Statistics
          </h2>
        </div>
        <div className="p-6">
          <div className="grid md:grid-cols-4 gap-4">
            <StatCard 
              label="GSAx" 
              value={formatDecimal(advancedStats.totalGSAx)}
              className={advancedStats.totalGSAx > 0 ? "text-save" : "text-goal"}
            />
            <StatCard 
              label="WAR" 
              value={formatDecimal(advancedStats.totalWAR)}
              className={advancedStats.totalWAR > 0 ? "text-save" : "text-goal"}
            />
            <StatCard 
              label="GAR" 
              value={formatDecimal(advancedStats.totalGAR)}
              className={advancedStats.totalGAR > 0 ? "text-save" : "text-goal"}
            />
            <StatCard 
              label="HD Save %" 
              value={formatPercent(hdSavePct)}
            />
            <StatCard 
              label="Quality Starts" 
              value={advancedStats.qualityStarts}
            />
            <StatCard 
              label="QS Rate" 
              value={formatPercent(qualityStartRate)}
            />
            <StatCard 
              label="Total Saves" 
              value={advancedStats.totalSaves}
            />
            <StatCard 
              label="Shots Against" 
              value={advancedStats.totalShotsAgainst}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
