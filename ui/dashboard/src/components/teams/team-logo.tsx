// src/components/teams/team-logo.tsx
'use client'

import { cn, teamGradient, getInitials } from '@/lib/utils'

interface TeamLogoProps {
  src: string | null
  name: string
  abbrev?: string
  primaryColor?: string | null
  secondaryColor?: string | null
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  className?: string
  showGradient?: boolean
}

const sizeClasses = {
  xs: 'w-5 h-5',
  sm: 'w-8 h-8',
  md: 'w-10 h-10',
  lg: 'w-16 h-16',
  xl: 'w-24 h-24',
}

const imageSizes = {
  xs: 16,
  sm: 24,
  md: 32,
  lg: 56,
  xl: 88,
}

export function TeamLogo({
  src,
  name,
  abbrev,
  primaryColor,
  secondaryColor,
  size = 'md',
  className,
  showGradient = true,
}: TeamLogoProps) {
  const gradient = teamGradient(primaryColor, secondaryColor)
  
  return (
    <div
      className={cn(
        'rounded-lg flex items-center justify-center p-[2px] shrink-0 overflow-hidden',
        sizeClasses[size],
        className
      )}
      style={{
        background: showGradient ? gradient : 'transparent',
      }}
      suppressHydrationWarning
    >
      {src ? (
        <img
          src={src}
          alt={name}
          width={imageSizes[size]}
          height={imageSizes[size]}
          className="object-contain w-full h-full block"
          loading="lazy"
          decoding="async"
          suppressHydrationWarning
        />
      ) : (
        <span 
          className={cn(
            'font-display font-bold text-white',
            size === 'xs' && 'text-[8px]',
            size === 'sm' && 'text-xs',
            size === 'md' && 'text-sm',
            size === 'lg' && 'text-lg',
            size === 'xl' && 'text-2xl',
          )}
        >
          {abbrev ?? getInitials(name)}
        </span>
      )}
    </div>
  )
}
