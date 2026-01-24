/**
 * Video utility functions for YouTube URL handling and video timestamp formatting
 */

/**
 * Extract YouTube video ID from various URL formats
 * Supports:
 * - https://www.youtube.com/watch?v=VIDEO_ID
 * - https://youtu.be/VIDEO_ID
 * - https://www.youtube.com/embed/VIDEO_ID
 * - VIDEO_ID (if already just the ID)
 */
export function extractYouTubeVideoId(url: string | null | undefined): string | null {
  if (!url) return null
  
  // If it's already just an ID (no URLs, no special chars except dashes/underscores)
  if (/^[a-zA-Z0-9_-]{11}$/.test(url.trim())) {
    return url.trim()
  }
  
  // Try to extract from various YouTube URL formats
  const patterns = [
    /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})/,
    /^https?:\/\/(?:www\.)?youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})/,
    /^https?:\/\/youtu\.be\/([a-zA-Z0-9_-]{11})/,
    /^https?:\/\/(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]{11})/,
  ]
  
  for (const pattern of patterns) {
    const match = url.match(pattern)
    if (match && match[1]) {
      return match[1]
    }
  }
  
  return null
}

/**
 * Format YouTube URL with start time
 * @param videoId - YouTube video ID or URL
 * @param startTimeSeconds - Start time in seconds
 * @returns YouTube URL with t parameter
 */
export function formatYouTubeUrlWithTime(
  videoId: string | null | undefined,
  startTimeSeconds: number | null | undefined
): string | null {
  if (!videoId) return null
  
  const id = extractYouTubeVideoId(videoId)
  if (!id) return null
  
  const baseUrl = `https://www.youtube.com/watch?v=${id}`
  
  if (startTimeSeconds !== null && startTimeSeconds !== undefined && startTimeSeconds > 0) {
    return `${baseUrl}&t=${Math.floor(startTimeSeconds)}s`
  }
  
  return baseUrl
}

/**
 * Common YouTube embed parameters to minimize overlays and set quality
 * - rel=0: Don't show related videos from other channels
 * - modestbranding=1: Reduce YouTube branding
 * - iv_load_policy=3: Disable video annotations
 * - fs=1: Allow fullscreen
 * - vq=hd1080: Request 1080p quality (YouTube may override based on connection)
 * - hd=1: Prefer HD playback
 */
const YOUTUBE_EMBED_PARAMS = {
  rel: '0',
  modestbranding: '1',
  iv_load_policy: '3',
  fs: '1',
  vq: 'hd1080',
  hd: '1',
}

/**
 * Create YouTube embed URL with start time
 * @param videoId - YouTube video ID or URL
 * @param startTimeSeconds - Start time in seconds
 * @returns YouTube embed URL
 */
export function formatYouTubeEmbedUrl(
  videoId: string | null | undefined,
  startTimeSeconds: number | null | undefined
): string | null {
  if (!videoId) return null

  const id = extractYouTubeVideoId(videoId)
  if (!id) return null

  const params = new URLSearchParams(YOUTUBE_EMBED_PARAMS)

  if (startTimeSeconds !== null && startTimeSeconds !== undefined && startTimeSeconds > 0) {
    params.set('start', String(Math.floor(startTimeSeconds)))
  }

  return `https://www.youtube.com/embed/${id}?${params.toString()}`
}

/**
 * Create YouTube embed URL with start and end times for highlight clips
 * @param videoId - YouTube video ID or URL
 * @param startTimeSeconds - Start time in seconds
 * @param endTimeSeconds - End time in seconds
 * @param autoplay - Whether to autoplay the video
 * @returns YouTube embed URL with start, end, and autoplay parameters
 */
export function formatYouTubeHighlightUrl(
  videoId: string | null | undefined,
  startTimeSeconds: number,
  endTimeSeconds: number,
  autoplay: boolean = true
): string | null {
  if (!videoId) return null

  const id = extractYouTubeVideoId(videoId)
  if (!id) return null

  const params = new URLSearchParams(YOUTUBE_EMBED_PARAMS)

  if (startTimeSeconds > 0) {
    params.set('start', String(Math.floor(startTimeSeconds)))
  }

  if (endTimeSeconds > startTimeSeconds) {
    params.set('end', String(Math.floor(endTimeSeconds)))
  }

  if (autoplay) {
    params.set('autoplay', '1')
  }

  return `https://www.youtube.com/embed/${id}?${params.toString()}`
}

/**
 * Calculate video timestamp considering offset
 * @param runningVideoTime - Running video time from event/shift
 * @param videoStartOffset - Offset from dim_schedule (seconds to skip at start)
 * @returns Adjusted video timestamp
 */
export function calculateVideoTimestamp(
  runningVideoTime: number | null | undefined,
  videoStartOffset: number | null | undefined = 0
): number {
  const baseTime = runningVideoTime || 0
  const offset = videoStartOffset || 0
  return Math.max(0, baseTime - offset)
}
