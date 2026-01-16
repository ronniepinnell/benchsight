// src/components/layout/topbar.tsx
'use client'

import { UserMenu } from '@/components/auth/user-menu'
import { Menu } from 'lucide-react'
import { cn } from '@/lib/utils'

interface TopbarProps {
  onMobileMenuClick?: () => void
}

export function Topbar({ onMobileMenuClick }: TopbarProps) {
  return (
    <header className={cn(
      'fixed top-0 h-14 bg-card border-b border-border flex items-center justify-between z-[46]',
      'left-0 lg:left-60 right-0',
      'px-4 lg:px-6'
    )}>
      {/* Left side - Mobile menu button and Status */}
      <div className="flex items-center gap-3 lg:gap-4">
        {/* Mobile menu button */}
        <button
          onClick={(e) => {
            e.stopPropagation()
            onMobileMenuClick?.()
          }}
          onTouchStart={(e) => {
            // Ensure touch events work properly
            e.stopPropagation()
          }}
          className="lg:hidden p-2 text-muted-foreground hover:text-foreground active:text-foreground active:bg-muted rounded-md transition-colors touch-manipulation min-w-[44px] min-h-[44px] flex items-center justify-center"
          aria-label="Open menu"
          type="button"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2 lg:gap-4 flex-wrap">
          <div className="flex items-center gap-2 px-2 lg:px-3 py-1 lg:py-1.5 bg-save/10 border border-save/50 rounded-md">
            <div className="w-2 h-2 rounded-full bg-save animate-pulse" />
            <span className="text-[10px] font-mono text-save tracking-wider">
              SYSTEM ONLINE
            </span>
          </div>
          
          <span className="text-xs font-mono text-muted-foreground hidden sm:inline">
            2025-26 Season • Week 18
          </span>
        </div>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-2 lg:gap-4">
        <span className="text-xs font-mono text-muted-foreground hidden md:inline">
          NORAD HOCKEY ANALYTICS
        </span>
        <UserMenu />
      </div>
    </header>
  )
}
