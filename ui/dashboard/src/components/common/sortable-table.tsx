'use client'

import { useState, useMemo, ReactNode } from 'react'
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react'
import { cn } from '@/lib/utils'

export type SortDirection = 'asc' | 'desc'

export interface SortableColumn<T = any> {
  key: string
  label: string
  sortFn?: (a: T, b: T) => number
  className?: string
  headerClassName?: string
  render?: (value: any, row: T) => ReactNode
}

interface SortableTableProps<T = any> {
  data: T[]
  columns: SortableColumn<T>[]
  defaultSortKey?: string
  defaultSortDirection?: SortDirection
  rowKey?: (row: T, index: number) => string | number
  className?: string
  theadClassName?: string
  tbodyClassName?: string
  rowClassName?: (row: T, index: number) => string
}

export function SortableTable<T = any>({
  data,
  columns,
  defaultSortKey,
  defaultSortDirection = 'asc',
  rowKey,
  className,
  theadClassName,
  tbodyClassName,
  rowClassName,
}: SortableTableProps<T>) {
  const [sortKey, setSortKey] = useState<string>(defaultSortKey || columns[0]?.key || '')
  const [sortDirection, setSortDirection] = useState<SortDirection>(defaultSortDirection)

  const sortedData = useMemo(() => {
    if (!sortKey) return data
    
    const column = columns.find(col => col.key === sortKey)
    if (!column) return data

    const sorted = [...data]
    
    sorted.sort((a, b) => {
      if (column.sortFn) {
        return column.sortFn(a, b)
      }
      
      // Default sorting
      const aValue = (a as any)[sortKey]
      const bValue = (b as any)[sortKey]
      
      if (aValue === null || aValue === undefined) return 1
      if (bValue === null || bValue === undefined) return -1
      
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortDirection === 'asc'
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue)
      }
      
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortDirection === 'asc' ? aValue - bValue : bValue - aValue
      }
      
      // Fallback to string comparison
      const aStr = String(aValue).toLowerCase()
      const bStr = String(bValue).toLowerCase()
      return sortDirection === 'asc'
        ? aStr.localeCompare(bStr)
        : bStr.localeCompare(aStr)
    })
    
    return sorted
  }, [data, sortKey, sortDirection, columns])

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortKey(key)
      setSortDirection('asc')
    }
  }

  const SortIcon = ({ field }: { field: string }) => {
    if (sortKey !== field) {
      return <ArrowUpDown className="w-3 h-3 ml-1 opacity-50" />
    }
    return sortDirection === 'asc' 
      ? <ArrowUp className="w-3 h-3 ml-1" />
      : <ArrowDown className="w-3 h-3 ml-1" />
  }

  return (
    <div className={cn("overflow-x-auto", className)}>
      <table className="w-full text-sm">
        <thead className={theadClassName}>
          <tr className="border-b border-border bg-accent/50">
            {columns.map((column) => (
              <th
                key={column.key}
                onClick={() => handleSort(column.key)}
                className={cn(
                  "px-3 py-2 font-display text-xs text-muted-foreground cursor-pointer hover:bg-muted/50 transition-colors",
                  column.headerClassName
                )}
              >
                <div className="flex items-center gap-1">
                  {column.label}
                  <SortIcon field={column.key} />
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className={tbodyClassName}>
          {sortedData.map((row, index) => (
            <tr
              key={rowKey ? rowKey(row, index) : index}
              className={cn(
                "border-b border-border hover:bg-muted/50",
                rowClassName ? rowClassName(row, index) : ''
              )}
            >
              {columns.map((column) => {
                const value = (row as any)[column.key]
                return (
                  <td
                    key={column.key}
                    className={cn("px-3 py-2", column.className)}
                  >
                    {column.render ? column.render(value, row) : value}
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
