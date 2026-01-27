'use client'

import { useState } from 'react'
import { Play, X } from 'lucide-react'

interface GoalVideoPlayerProps {
  embedUrl: string
  title?: string
}

export function GoalVideoPlayer({ embedUrl, title = 'Goal Replay' }: GoalVideoPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false)

  return (
    <div className="mt-3 pt-3 border-t border-border/30">
      {isPlaying ? (
        <>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              <Play className="w-3 h-3" />
              Goal Replay
            </div>
            <button
              onClick={() => setIsPlaying(false)}
              className="flex items-center gap-1 px-2 py-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
            >
              <X className="w-3 h-3" />
              Close
            </button>
          </div>
          <div className="relative w-full aspect-video max-w-lg rounded-lg overflow-hidden bg-black">
            <iframe
              src={embedUrl}
              className="absolute inset-0 w-full h-full"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              title={title}
            />
          </div>
        </>
      ) : (
        <button
          onClick={() => setIsPlaying(true)}
          className="inline-flex items-center gap-2 px-3 py-1.5 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors text-sm"
        >
          <Play className="w-4 h-4" />
          Watch Goal
        </button>
      )}
    </div>
  )
}
