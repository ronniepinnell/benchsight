'use client'

import { useState } from 'react'
import { BarChart3, TrendingUp, Target, Zap, Shield, Activity } from 'lucide-react'
import { cn } from '@/lib/utils'
import Link from 'next/link'

interface AdvancedStatsSectionProps {
  teamId: string
  teamName: string
  seasonId?: string
  gameType?: string
}

const statCategories = [
  { id: 'possession', label: 'Possession', icon: Activity },
  { id: 'special', label: 'Special Teams', icon: Zap },
  { id: 'zone', label: 'Zone Play', icon: Target },
  { id: 'physical', label: 'Physical', icon: Shield },
  { id: 'shooting', label: 'Shooting', icon: BarChart3 },
  { id: 'war', label: 'WAR/GAR', icon: TrendingUp },
]

export function AdvancedStatsSection({ 
  teamId, 
  teamName, 
  seasonId, 
  gameType = 'All' 
}: AdvancedStatsSectionProps) {
  const [activeCategory, setActiveCategory] = useState('possession')
  
  return (
    <div className="bg-card rounded-xl border border-border overflow-hidden">
      <div className="px-4 py-3 bg-accent border-b border-border">
        <h2 className="font-display text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
          <BarChart3 className="w-4 h-4" />
          Advanced Statistics
        </h2>
      </div>
      
      {/* Category Tabs */}
      <div className="flex gap-2 border-b border-border px-4 pt-3 pb-2 overflow-x-auto">
        {statCategories.map((category) => {
          const Icon = category.icon
          const isActive = activeCategory === category.id
          return (
            <button
              key={category.id}
              onClick={() => setActiveCategory(category.id)}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-t-lg transition-all whitespace-nowrap',
                isActive
                  ? 'bg-card border border-b-0 border-border -mb-[1px] text-foreground font-semibold'
                  : 'hover:bg-muted/50 text-muted-foreground'
              )}
            >
              <Icon className="w-4 h-4" />
              <span className="font-display text-sm">{category.label}</span>
            </button>
          )
        })}
      </div>
      
      {/* Stats Content - Will be populated by server component */}
      <div className="p-6">
        <p className="text-sm text-muted-foreground">
          Loading advanced statistics...
        </p>
      </div>
    </div>
  )
}
