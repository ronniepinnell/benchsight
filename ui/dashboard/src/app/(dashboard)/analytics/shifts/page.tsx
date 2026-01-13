// src/app/(dashboard)/analytics/shifts/page.tsx
import Link from 'next/link'
import { ArrowLeft, Timer } from 'lucide-react'

export const metadata = {
  title: 'Shift Viewer | BenchSight Analytics',
  description: 'View and analyze player shifts',
}

export default function ShiftViewerPage() {
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
            <Timer className="w-5 h-5" />
            Shift Viewer
          </h1>
        </div>
        <div className="p-6">
          <p className="text-muted-foreground text-center">
            Shift analysis feature coming soon. This will allow you to view and analyze player shifts in detail.
          </p>
        </div>
      </div>
    </div>
  )
}
