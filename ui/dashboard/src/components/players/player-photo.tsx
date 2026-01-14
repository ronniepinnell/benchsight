// src/components/players/player-photo.tsx
'use client'

import { useState, useEffect } from 'react'
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

// Validate if a URL is valid and not empty
function isValidImageUrl(url: string | null | undefined): boolean {
  if (!url || typeof url !== 'string' || url.trim() === '') {
    return false
  }
  
  const trimmedUrl = url.trim().toLowerCase()
  
  // Filter out placeholder text
  const placeholderTexts = [
    'image coming soon',
    'coming soon',
    'placeholder',
    'no image',
    'image not available',
    'tbd',
    'n/a',
    'na'
  ]
  
  if (placeholderTexts.some(text => trimmedUrl.includes(text))) {
    return false
  }
  
  // Check if it's a valid URL format
  try {
    const urlObj = new URL(url)
    return urlObj.protocol === 'http:' || urlObj.protocol === 'https:'
  } catch {
    // If URL parsing fails, check if it starts with http/https
    return url.startsWith('http://') || url.startsWith('https://')
  }
}

export function PlayerPhoto({
  src,
  name,
  primaryColor,
  size = 'md',
  className,
}: PlayerPhotoProps) {
  const [imageError, setImageError] = useState(false)
  const [currentSrc, setCurrentSrc] = useState<string | null>(null)
  
  const borderColor = primaryColor ?? '#1e3a5f'
  
  // Reset error state when src changes
  useEffect(() => {
    setImageError(false)
    // Handle empty strings, null, undefined, or invalid URLs
    if (!src || (typeof src === 'string' && src.trim() === '')) {
      setCurrentSrc(null)
      return
    }
    const validSrc = isValidImageUrl(src) ? src : null
    setCurrentSrc(validSrc)
  }, [src])
  
  // Determine what to display
  const displaySrc = imageError ? placeholderUrl : currentSrc
  const showImage = displaySrc && !imageError
  
  const handleImageError = () => {
    if (currentSrc && currentSrc !== placeholderUrl) {
      // Try placeholder if original fails
      setCurrentSrc(placeholderUrl)
      setImageError(false) // Reset to try placeholder
    } else {
      // Both original and placeholder failed, show initials
      setImageError(true)
      setCurrentSrc(null)
    }
  }
  
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
      {showImage ? (
        <Image
          src={displaySrc}
          alt={name}
          width={imageSizes[size]}
          height={imageSizes[size]}
          className="object-cover w-full h-full"
          unoptimized
          onError={handleImageError}
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
