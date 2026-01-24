'use client'

import { Video } from 'lucide-react'
import { cn } from '@/lib/utils'
import { extractYouTubeVideoId, formatYouTubeEmbedUrl } from '@/lib/utils/video'

interface GameVideoEmbedProps {
  videoUrl: string | null
  startTime?: number | null
  className?: string
}

export function GameVideoEmbed({
  videoUrl,
  startTime,
  className
}: GameVideoEmbedProps) {
  if (!videoUrl) {
    return null
  }

  const videoId = extractYouTubeVideoId(videoUrl)
  if (!videoId) {
    return null
  }

  const embedUrl = formatYouTubeEmbedUrl(videoId, startTime)
  if (!embedUrl) {
    return null
  }

  return (
    <div className={cn('bg-card rounded-xl border border-border overflow-hidden', className)}>
      <div className="px-4 py-2 border-b border-border bg-gradient-to-r from-primary/10 via-transparent to-primary/10">
        <div className="flex items-center gap-2">
          <Video className="w-4 h-4 text-primary" />
          <h2 className="font-display text-sm font-semibold uppercase tracking-wider">Game Video</h2>
        </div>
      </div>

      <div className="aspect-video w-full">
        <iframe
          src={embedUrl}
          title="Game Video"
          className="w-full h-full"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        />
      </div>
    </div>
  )
}
