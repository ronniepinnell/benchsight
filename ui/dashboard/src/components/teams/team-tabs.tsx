'use client'

import Link from 'next/link'
import { usePathname, useSearchParams } from 'next/navigation'
import { Users, BarChart3, Activity, Target } from 'lucide-react'
import { cn } from '@/lib/utils'

interface TeamTabsProps {
  teamName: string
  currentTab?: string
}

const tabs = [
  { id: 'overview', label: 'Overview', icon: Activity },
  { id: 'roster', label: 'Roster', icon: Users },
  { id: 'lines', label: 'Lines', icon: Users },
  { id: 'analytics', label: 'Analytics', icon: BarChart3 },
  { id: 'matchups', label: 'Matchups', icon: Target },
]

export function TeamTabs({ teamName, currentTab = 'overview' }: TeamTabsProps) {
  const pathname = usePathname()
  const searchParams = useSearchParams()
  
  const buildHref = (tabId: string) => {
    const params = new URLSearchParams(searchParams.toString())
    params.set('tab', tabId)
    return `${pathname}?${params.toString()}`
  }

  return (
    <div className="flex gap-2 border-b border-border pb-2 overflow-x-auto">
      {tabs.map((tab) => {
        const Icon = tab.icon
        const isActive = currentTab === tab.id
        return (
          <Link
            key={tab.id}
            href={buildHref(tab.id)}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-t-lg transition-all whitespace-nowrap',
              isActive
                ? 'bg-card border border-b-0 border-border -mb-[1px] text-foreground font-semibold'
                : 'hover:bg-muted/50 text-muted-foreground'
            )}
          >
            <Icon className="w-4 h-4" />
            <span className="font-display text-sm">{tab.label}</span>
          </Link>
        )
      })}
    </div>
  )
}
