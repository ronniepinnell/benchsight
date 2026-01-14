'use client'

/**
 * Tracker Layout Component
 * 
 * Main layout for the game tracker interface
 */

import { ReactNode } from 'react'

interface TrackerLayoutProps {
  children: ReactNode
  header: ReactNode
}

export function TrackerLayout({ children, header }: TrackerLayoutProps) {
  return (
    <div className="h-screen flex flex-col bg-background text-foreground">
      {/* Header */}
      <header className="border-b bg-card">
        {header}
      </header>
      
      {/* Main content */}
      <main className="flex-1 overflow-hidden">
        {children}
      </main>
    </div>
  )
}
