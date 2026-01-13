// src/components/players/player-photo.tsx
'use client'

import Image from 'next/image'
import { cn, getInitials } from '@/lib/utils'

interface PlayerPhotoProps {
  src: string | null
  name: string
  primaryColor?: string | null
  size?: 'sm' | 'md' | 'lg' | 'xl'
  className?: string
}

const sizeClasses = {
  sm: 'w-8 h-8',
  md: 'w-10 h-10',
  lg: 'w-16 h-16',
  xl: 'w-32 h-32',
}

const imageSizes = {
  sm: 32,
  md: 40,
  lg: 64,
  xl: 128,
}

const placeholderUrl = 'https://www.noradhockey.com/wp-content/uploads/2022/08/Place-Holder.jpg'

export function PlayerPhoto({
  src,
  name,
  primaryColor,
  size = 'md',
  className,
}: PlayerPhotoProps) {
  const borderColor = primaryColor ?? '#1e3a5f'
  
  return (
    <div
      className={cn(
        'rounded-full overflow-hidden shrink-0',
        sizeClasses[size],
        className
      )}
      style={{
        border: `3px solid ${borderColor}`,
      }}
    >
      {src ? (
        <Image
          src={src}
          alt={name}
          width={imageSizes[size]}
          height={imageSizes[size]}
          className="object-cover w-full h-full"
          unoptimized
          onError={(e) => {
            // Fallback to placeholder on error
            (e.target as HTMLImageElement).src = placeholderUrl
          }}
        />
      ) : (
        <div className="w-full h-full bg-muted flex items-center justify-center">
          <span className="font-display font-bold text-muted-foreground text-xs">
            {getInitials(name)}
          </span>
        </div>
      )}
    </div>
  )
}
