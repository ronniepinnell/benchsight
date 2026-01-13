// src/components/prototypes/prototype-template.tsx
// Template component for quick prototyping

import { createClient } from '@/lib/supabase/server'
import { cn } from '@/lib/utils'

interface PrototypeTemplateProps {
  title: string
  description?: string
  children?: React.ReactNode
}

/**
 * Template component for prototyping new dashboard pages
 * 
 * Usage:
 * ```tsx
 * export default async function MyPrototype() {
 *   const supabase = await createClient()
 *   const { data } = await supabase.from('v_standings_current').select('*')
 *   
 *   return (
 *     <PrototypeTemplate title="My Prototype" description="Testing new visualization">
 *       {/* Your content *\/}
 *     </PrototypeTemplate>
 *   )
 * }
 * ```
 */
export function PrototypeTemplate({ 
  title, 
  description, 
  children 
}: PrototypeTemplateProps) {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="font-display text-2xl font-bold tracking-wider uppercase flex items-center gap-3">
          <span className="w-1 h-6 bg-primary rounded" />
          {title}
        </h1>
        {description && (
          <p className="text-sm text-muted-foreground mt-2 ml-4">{description}</p>
        )}
      </div>

      {/* Content */}
      {children}
    </div>
  )
}

/**
 * Stat card component for displaying metrics
 */
export function StatCard({ 
  label, 
  value, 
  icon: Icon, 
  color = 'text-primary' 
}: { 
  label: string
  value: string | number
  icon?: React.ComponentType<{ className?: string }>
  color?: string
}) {
  return (
    <div className="bg-card rounded-lg p-4 border border-border">
      {Icon && (
        <div className="flex items-center gap-2 mb-2">
          <Icon className={cn('w-4 h-4', color)} />
          <span className="text-xs font-mono text-muted-foreground uppercase">{label}</span>
        </div>
      )}
      {!Icon && (
        <div className="text-xs font-mono text-muted-foreground uppercase mb-2">{label}</div>
      )}
      <div className="font-mono text-2xl font-bold text-foreground">{value}</div>
    </div>
  )
}

/**
 * Simple table component for prototyping
 */
export function PrototypeTable<T extends Record<string, any>>({
  data,
  columns,
}: {
  data: T[]
  columns: Array<{
    key: keyof T
    label: string
    render?: (value: any, row: T) => React.ReactNode
  }>
}) {
  return (
    <div className="bg-card rounded-xl border border-border overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-accent border-b-2 border-border">
              {columns.map((col) => (
                <th
                  key={String(col.key)}
                  className="px-4 py-3 text-left font-display text-xs font-semibold text-muted-foreground uppercase"
                >
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr
                key={idx}
                className={cn(
                  'border-b border-border transition-colors hover:bg-muted/50',
                  idx % 2 === 0 && 'bg-accent/30'
                )}
              >
                {columns.map((col) => (
                  <td key={String(col.key)} className="px-4 py-3 text-sm">
                    {col.render ? col.render(row[col.key], row) : String(row[col.key] ?? '')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
