// src/lib/utils/index.ts
import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Merge Tailwind classes with clsx
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Format time in MM:SS
 */
export function formatGameTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

/**
 * Format time remaining in period (countdown)
 */
export function formatTimeRemaining(seconds: number, periodLength: number = 900): string {
  const remaining = periodLength - (seconds % periodLength)
  return formatGameTime(remaining)
}

/**
 * Format date for display
 */
export function formatDate(date: string | Date, style: 'short' | 'long' = 'short'): string {
  const d = typeof date === 'string' ? new Date(date) : date
  
  if (style === 'short') {
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }
  
  return d.toLocaleDateString('en-US', { 
    weekday: 'short',
    month: 'short', 
    day: 'numeric',
    year: 'numeric'
  })
}

/**
 * Format number with +/- sign for differential
 */
export function formatDiff(num: number): string {
  if (num > 0) return `+${num}`
  return num.toString()
}

/**
 * Calculate points per game
 */
export function calculatePPG(points: number, games: number): string {
  if (games === 0) return '0.00'
  return (points / games).toFixed(2)
}

/**
 * Calculate goals against average
 */
export function calculateGAA(goalsAgainst: number, games: number): string {
  if (games === 0) return '0.00'
  return (goalsAgainst / games).toFixed(2)
}

/**
 * Calculate save percentage
 */
export function calculateSavePct(saves: number, shotsAgainst: number): string {
  if (shotsAgainst === 0) return '.000'
  return (saves / shotsAgainst).toFixed(3).replace('0.', '.')
}

/**
 * Format record as W-L-T
 */
export function formatRecord(wins: number, losses: number, ties: number): string {
  return `${wins}-${losses}-${ties}`
}

/**
 * Get position display name
 */
export function getPositionName(pos: string | null): string {
  const positions: Record<string, string> = {
    'F': 'Forward',
    'D': 'Defense',
    'G': 'Goalie',
    'C': 'Center',
    'LW': 'Left Wing',
    'RW': 'Right Wing',
  }
  return positions[pos ?? ''] ?? pos ?? 'Unknown'
}

/**
 * Get skill level display
 */
export function getSkillDisplay(level: number | null): string {
  if (level === null) return 'N/A'
  return `Skill ${level}`
}

/**
 * Generate gradient CSS from team colors
 */
export function teamGradient(primary: string | null, secondary: string | null): string {
  const p = primary ?? '#1e40af'
  const s = secondary ?? '#3b82f6'
  return `linear-gradient(135deg, ${p} 0%, ${s} 100%)`
}

/**
 * Truncate text with ellipsis
 */
export function truncate(text: string, length: number): string {
  if (text.length <= length) return text
  return text.slice(0, length) + '...'
}

/**
 * Get initials from name
 */
export function getInitials(name: string): string {
  return name
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

/**
 * Format season value (number or string) to "xxxx-xxxx" format
 * Handles both numeric (20242025) and string formats (N20242025F, 20242025)
 */
export function formatSeason(season: string | number | null | undefined): string {
  if (!season) return ''
  
  if (typeof season === 'number') {
    const year = Math.floor(season / 10000)
    const nextYear = season % 10000
    return `${year}-${nextYear}`
  }
  
  const seasonStr = String(season)
  // Try to match patterns like "20242025" or "N20242025F"
  const match = seasonStr.match(/(\d{4})(\d{4})/)
  if (match) {
    const [, startYear, endYear] = match
    return `${startYear}-${endYear}`
  }
  
  return seasonStr
}
