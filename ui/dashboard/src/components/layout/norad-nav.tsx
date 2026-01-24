'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Trophy, Users, UserCircle, Award, BarChart3, CalendarDays, Activity } from 'lucide-react'
import { cn } from '@/lib/utils'

const navItems = [
  { href: '/norad/standings', label: 'Standings', icon: Trophy },
  { href: '/norad/teams', label: 'Teams', icon: Users },
  { href: '/norad/players', label: 'Players', icon: UserCircle },
  { href: '/norad/leaders', label: 'Leaders', icon: Award },
  { href: '/norad/games', label: 'Games', icon: BarChart3 },
  { href: '/norad/schedule', label: 'Schedule', icon: CalendarDays },
  { href: '/norad/analytics', label: 'Analytics', icon: Activity },
]

export function NoradNav() {
  const pathname = usePathname()

  return (
    <div className="border-b border-border bg-card sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4">
        <nav className="flex items-center justify-center gap-1 py-1.5 overflow-x-auto scrollbar-hide">
          {navItems.map(({ href, label, icon: Icon }) => {
            const isActive = pathname === href || pathname.startsWith(href + '/')
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  'flex items-center gap-1.5 px-3 py-1.5 text-xs font-mono rounded transition-colors whitespace-nowrap',
                  isActive
                    ? 'text-primary bg-primary/10 font-semibold'
                    : 'text-muted-foreground hover:text-primary hover:bg-muted'
                )}
              >
                <Icon className="w-3.5 h-3.5" />
                {label}
              </Link>
            )
          })}
        </nav>
      </div>
    </div>
  )
}
