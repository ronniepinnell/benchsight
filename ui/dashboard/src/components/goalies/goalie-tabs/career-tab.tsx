// src/components/goalies/goalie-tabs/career-tab.tsx
import { Award } from 'lucide-react'
import { StatCard } from '@/components/players/stat-card'

interface CareerTabProps {
  career: any
  gameLog: any[]
}

export function CareerTab({ career }: CareerTabProps) {
  const formatPercent = (val: number | null | undefined) => {
    if (val === null || val === undefined) return '-'
    return Number(val).toFixed(1) + '%'
  }

  const formatDecimal = (val: number | null | undefined, decimals: number = 2) => {
    if (val === null || val === undefined) return '-'
    return Number(val).toFixed(decimals)
  }

  if (!career) {
    return (
      <div className="bg-card rounded-xl border border-border p-8 text-center">
        <p className="text-muted-foreground">No career data available.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="px-4 py-3 bg-accent border-b border-border">
          <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
            <Award className="w-4 h-4" />
            Career Summary
          </h2>
        </div>
        <div className="p-6">
          <div className="grid md:grid-cols-4 gap-4">
            <StatCard label="Total Games" value={career.total_games || 0} />
            <StatCard label="Total Wins" value={career.total_wins || 0} className="text-save" />
            <StatCard label="Total Losses" value={career.total_losses || 0} className="text-goal" />
            <StatCard label="Career Save %" value={career.career_save_pct ? formatPercent(career.career_save_pct * 100) : '-'} />
            <StatCard label="Career GAA" value={career.career_gaa ? formatDecimal(career.career_gaa) : '-'} />
            <StatCard label="Total Shutouts" value={career.total_shutouts || 0} className="text-assist" />
          </div>
        </div>
      </div>
    </div>
  )
}
