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
  
  const baseUrl = `https://www.youtube.com/embed/${id}`
  
  if (startTimeSeconds !== null && startTimeSeconds !== undefined && startTimeSeconds > 0) {
    return `${baseUrl}?start=${Math.floor(startTimeSeconds)}`
  }
  
  return baseUrl
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
