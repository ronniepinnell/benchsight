'use client'

import { Download } from 'lucide-react'
import { downloadCSV } from '@/lib/export/csv'
import { cn } from '@/lib/utils'

interface ExportButtonProps {
  data: any[]
  filename: string
  className?: string
  disabled?: boolean
}

export function ExportButton({ data, filename, className, disabled }: ExportButtonProps) {
  const handleExport = () => {
    if (!data || data.length === 0) {
      alert('No data to export')
      return
    }
    downloadCSV(data, filename)
  }

  return (
    <button
      onClick={handleExport}
      disabled={disabled || !data || data.length === 0}
      className={cn(
        'inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium rounded-lg',
        'bg-muted hover:bg-muted/80 text-foreground',
        'border border-border hover:border-primary/50',
        'transition-colors',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        className
      )}
      title="Export to CSV"
    >
      <Download className="w-4 h-4" />
      Export CSV
    </button>
  )
}
