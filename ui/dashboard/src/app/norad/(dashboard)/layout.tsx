// src/app/norad/(dashboard)/layout.tsx
import Link from 'next/link'
import Image from 'next/image'
import { Suspense } from 'react'
import { ExternalLink } from 'lucide-react'
import { GamesTickerWrapper } from '@/components/games/games-ticker-wrapper'
import { NoradNav } from '@/components/layout/norad-nav'

export default function NoradDashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-background">
      {/* Top utility bar */}
      <div className="bg-muted/30 border-b border-border">
        <div className="max-w-7xl mx-auto px-4 py-1 flex items-center justify-between">
          <Link href="/norad" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
            <Image
              src="/images/NORAD_logo.png"
              alt="NORAD"
              width={24}
              height={24}
              className="rounded"
              unoptimized
            />
            <span className="text-xs font-mono font-semibold text-foreground">NORAD</span>
          </Link>
          <a
            href="https://www.noradhockey.com"
            target="_blank"
            rel="noopener noreferrer"
            className="text-[10px] font-mono text-muted-foreground hover:text-primary flex items-center gap-1"
          >
            View on NORAD <ExternalLink className="w-2.5 h-2.5" />
          </a>
        </div>
      </div>

      {/* Games Ticker */}
      <Suspense fallback={<div className="h-16 bg-card border-b border-border animate-pulse" />}>
        <GamesTickerWrapper />
      </Suspense>

      {/* Navigation */}
      <NoradNav />

      {/* Main content area */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {children}
      </main>
    </div>
  )
}
