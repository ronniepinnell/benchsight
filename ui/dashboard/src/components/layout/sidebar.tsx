// src/components/layout/sidebar.tsx
'use client'

import Link from 'next/link'
import Image from 'next/image'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import {
  BarChart3,
  Trophy,
  Users,
  User,
  Calendar,
  Gamepad2,
  Target,
  Timer,
  TrendingUp,
  ChevronLeft,
  Award,
  TestTube,
  Database,
} from 'lucide-react'
import { useState } from 'react'

interface NavItem {
  name: string
  href: string
  icon: React.ReactNode
}

interface NavSection {
  name: string
  icon: string
  items: NavItem[]
}

const navigation: NavSection[] = [
  {
    name: 'Games',
    icon: '🏒',
    items: [
      { name: 'Recent Games', href: '/norad/games', icon: <Gamepad2 className="w-4 h-4" /> },
      { name: 'Shot Maps', href: '/norad/games/shots', icon: <Target className="w-4 h-4" /> },
    ],
  },
  {
    name: 'League',
    icon: '🏆',
    items: [
      { name: 'Standings', href: '/norad/standings', icon: <BarChart3 className="w-4 h-4" /> },
      { name: 'Leaders', href: '/norad/leaders', icon: <Trophy className="w-4 h-4" /> },
      { name: 'Goalies', href: '/norad/goalies', icon: <Award className="w-4 h-4" /> },
      { name: 'Schedule', href: '/norad/schedule', icon: <Calendar className="w-4 h-4" /> },
    ],
  },
  {
    name: 'Teams',
    icon: '👥',
    items: [
      { name: 'All Teams', href: '/norad/teams', icon: <Users className="w-4 h-4" /> },
    ],
  },
  {
    name: 'Players',
    icon: '🧑‍🤝‍🧑',
    items: [
      { name: 'Search Players', href: '/norad/players', icon: <User className="w-4 h-4" /> },
      { name: 'Compare', href: '/norad/players/compare', icon: <TrendingUp className="w-4 h-4" /> },
    ],
  },
  {
    name: 'Analytics',
    icon: '🔬',
    items: [
      { name: 'League Overview', href: '/norad/analytics/overview', icon: <BarChart3 className="w-4 h-4" /> },
      { name: 'League Statistics', href: '/norad/analytics/statistics', icon: <TrendingUp className="w-4 h-4" /> },
      { name: 'Team Comparison', href: '/norad/analytics/teams', icon: <Users className="w-4 h-4" /> },
      { name: 'Shift Viewer', href: '/norad/analytics/shifts', icon: <Timer className="w-4 h-4" /> },
      { name: 'Trends', href: '/norad/analytics/trends', icon: <TrendingUp className="w-4 h-4" /> },
    ],
  },
  {
    name: 'Tools',
    icon: '🛠️',
    items: [
      { name: 'Game Tracker', href: '/norad/tracker', icon: <Timer className="w-4 h-4" /> },
      { name: 'Admin Portal', href: '/norad/admin', icon: <Database className="w-4 h-4" /> },
    ],
  },
  {
    name: 'Prototypes',
    icon: '🧪',
    items: [
      { name: 'Example', href: '/norad/prototypes/example', icon: <TestTube className="w-4 h-4" /> },
      { name: 'Test Connection', href: '/norad/prototypes/test-connection', icon: <Database className="w-4 h-4" /> },
      { name: 'Design System', href: '/norad/prototypes/design-system', icon: <Target className="w-4 h-4" /> },
    ],
  },
]

export function Sidebar() {
  const pathname = usePathname()
  const [collapsed, setCollapsed] = useState(false)

  return (
    <aside
      className={cn(
        'fixed top-0 left-0 h-screen bg-card border-r border-border flex flex-col transition-all duration-200 z-50',
        collapsed ? 'w-16' : 'w-60'
      )}
    >
      {/* Logo */}
      <div className={cn(
        'border-b border-border flex items-center gap-3',
        collapsed ? 'p-3 justify-center' : 'p-4'
      )}>
        <Image
          src="https://www.noradhockey.com/wp-content/uploads/2022/05/New-NORAD-Logo-White.png"
          alt="NORAD"
          width={28}
          height={28}
          unoptimized
        />
        {!collapsed && (
          <span className="font-display font-bold tracking-wider text-sm">
            BENCHSIGHT
          </span>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-2">
        {navigation.map((section) => (
          <div key={section.name} className="mb-2">
            {!collapsed && (
              <div className="flex items-center gap-2 px-3 py-2 text-[10px] font-mono text-muted-foreground tracking-wider uppercase">
                <span>{section.icon}</span>
                <span>{section.name}</span>
              </div>
            )}
            
            {section.items.map((item) => {
              const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
              
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    'flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors mb-0.5',
                    collapsed && 'justify-center',
                    isActive
                      ? 'bg-muted text-foreground border border-border'
                      : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                  )}
                  title={collapsed ? item.name : undefined}
                >
                  {item.icon}
                  {!collapsed && <span>{item.name}</span>}
                </Link>
              )
            })}
          </div>
        ))}
      </nav>

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="p-3 border-t border-border text-muted-foreground hover:text-foreground transition-colors flex items-center justify-center gap-2 text-xs font-mono"
      >
        <ChevronLeft className={cn(
          'w-4 h-4 transition-transform',
          collapsed && 'rotate-180'
        )} />
        {!collapsed && <span>Collapse</span>}
      </button>
    </aside>
  )
}
