// src/app/(dashboard)/analytics/trends/page.tsx
import Link from 'next/link'
import { ArrowLeft, TrendingUp } from 'lucide-react'

export const metadata = {
  title: 'Trends | BenchSight Analytics',
  description: 'View league and player trends over time',
}

export default function TrendsPage() {
  return (
    <div className="space-y-6">
      {/* Back Link */}
      <Link 
        href="/analytics/overview" 
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Analytics
      </Link>
      
      {/* Header */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="px-4 py-3 bg-accent border-b border-border">
          <h1 className="font-display text-lg font-semibold uppercase tracking-wider flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Trends Analysis
          </h1>
        </div>
        <div className="p-6">
          <p className="text-muted-foreground text-center">
            Trends analysis feature coming soon. This will show league and player trends over time.
          </p>
        </div>
      </div>
    </div>
  )
}
