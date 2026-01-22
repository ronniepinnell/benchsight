# Tracker Video Integration

**Video player integration and synchronization logic**

Last Updated: 2026-01-21
Version: 2.00

---

## Overview

The tracker integrates with video players (HTML5 video and YouTube) to synchronize game events with video playback. This document details the video integration logic.

**Video Sources:** HTML5 video, YouTube  
**Sync Mode:** Auto-sync and manual sync  
**Timing:** Handles intermissions, timeouts, period boundaries

---

## Video Player State

### State Structure

```typescript
interface VideoPlayerState {
  sources: VideoSource[]
  currentSourceIdx: number
  isPlaying: boolean
  currentTime: number
  speed: number
  autoSync: boolean
  ytPlayer: YT.Player | null
  gameMarkers: GameMarkers
}

interface VideoSource {
  type: 'html5' | 'youtube'
  url: string
  startTime?: number
  endTime?: number
}

interface GameMarkers {
  P1Start: number | null
  P1End: number | null
  P2Start: number | null
  P2End: number | null
  P3Start: number | null
  P3End: number | null
  OTStart: number | null
  OTEnd: number | null
  stoppages: Stoppage[]
}

interface VideoTiming {
  videoStartOffset: number
  intermission1: number  // 15 min = 900 seconds
  intermission2: number   // 15 min = 900 seconds
  intermission3: number   // 5 min = 300 seconds
  timeouts: Timeout[]
  youtubeUrl: string
}
```

---

## Video Loading

### HTML5 Video

```typescript
function loadVideo(url: string) {
  const video = document.getElementById('video-player') as HTMLVideoElement
  video.src = url
  video.load()
  
  S.videoPlayer.sources = [{
    type: 'html5',
    url: url
  }]
  S.videoPlayer.currentSourceIdx = 0
}
```

### YouTube Video

```typescript
function loadYouTubeVideo(videoId: string) {
  S.videoTiming.youtubeUrl = `https://www.youtube.com/watch?v=${videoId}`
  
  if (!S.videoPlayer.ytPlayer) {
    initializeYouTubePlayer(videoId)
  } else {
    S.videoPlayer.ytPlayer.loadVideoById(videoId)
  }
}

function initializeYouTubePlayer(videoId: string) {
  S.videoPlayer.ytPlayer = new YT.Player('youtube-player', {
    videoId: videoId,
    events: {
      onStateChange: handleYouTubeStateChange,
      onReady: handleYouTubeReady
    }
  })
}
```

---

## Video Synchronization

### Game Time to Video Time

```typescript
function calculateVideoTime(
  period: number,
  gameTime: string,
  videoStartOffset: number,
  intermissions: VideoTiming
): number {
  // Parse game time (MM:SS format)
  const [minutes, seconds] = gameTime.split(':').map(Number)
  const gameSeconds = minutes * 60 + seconds
  
  // Calculate period start time in video
  let videoTime = videoStartOffset
  
  // Add intermissions for previous periods
  if (period > 1) {
    videoTime += intermissions.intermission1  // After P1
  }
  if (period > 2) {
    videoTime += intermissions.intermission2  // After P2
  }
  if (period > 3) {
    videoTime += intermissions.intermission3  // After P3
  }
  
  // Add period time
  const periodStart = (period - 1) * periodLength
  videoTime += periodStart + gameSeconds
  
  return videoTime
}
```

### Video Time to Game Time

```typescript
function calculateGameTime(
  videoTime: number,
  videoStartOffset: number,
  intermissions: VideoTiming
): { period: number, time: string } {
  let remaining = videoTime - videoStartOffset
  
  // Determine period
  let period = 1
  const periodLength = 18 * 60  // 18 minutes in seconds
  
  if (remaining > periodLength) {
    remaining -= periodLength
    remaining -= intermissions.intermission1
    period = 2
  }
  if (remaining > periodLength) {
    remaining -= periodLength
    remaining -= intermissions.intermission2
    period = 3
  }
  if (remaining > periodLength) {
    remaining -= periodLength
    remaining -= intermissions.intermission3
    period = 4  // OT
  }
  
  // Calculate time
  const minutes = Math.floor(remaining / 60)
  const seconds = Math.floor(remaining % 60)
  const time = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  
  return { period, time }
}
```

---

## Auto-Sync

### Sync Video to Event

```typescript
function syncVideoToEvent(event: Event) {
  if (!S.videoPlayer.autoSync) return
  
  const videoTime = calculateVideoTime(
    event.period,
    event.time,
    S.videoTiming.videoStartOffset,
    S.videoTiming
  )
  
  if (S.videoPlayer.ytPlayer) {
    S.videoPlayer.ytPlayer.seekTo(videoTime, true)
  } else {
    const video = document.getElementById('video-player') as HTMLVideoElement
    video.currentTime = videoTime
  }
}
```

### Sync Event to Video

```typescript
function syncEventToVideo() {
  let videoTime: number
  
  if (S.videoPlayer.ytPlayer) {
    videoTime = S.videoPlayer.ytPlayer.getCurrentTime()
  } else {
    const video = document.getElementById('video-player') as HTMLVideoElement
    videoTime = video.currentTime
  }
  
  const { period, time } = calculateGameTime(
    videoTime,
    S.videoTiming.videoStartOffset,
    S.videoTiming
  )
  
  // Update current event time
  if (S.curr) {
    S.curr.period = period
    S.curr.time = time
  }
  
  updateTimeDisplay()
}
```

---

## Period Markers

### Setting Period Markers

```typescript
function setPeriodMarker(period: number, type: 'start' | 'end') {
  let videoTime: number
  
  if (S.videoPlayer.ytPlayer) {
    videoTime = S.videoPlayer.ytPlayer.getCurrentTime()
  } else {
    const video = document.getElementById('video-player') as HTMLVideoElement
    videoTime = video.currentTime
  }
  
  const markerKey = `P${period}${type === 'start' ? 'Start' : 'End'}`
  S.videoPlayer.gameMarkers[markerKey] = videoTime
  
  saveState()
}
```

### Using Period Markers

```typescript
function jumpToPeriod(period: number) {
  const marker = S.videoPlayer.gameMarkers[`P${period}Start`]
  if (marker !== null) {
    if (S.videoPlayer.ytPlayer) {
      S.videoPlayer.ytPlayer.seekTo(marker, true)
    } else {
      const video = document.getElementById('video-player') as HTMLVideoElement
      video.currentTime = marker
    }
  }
}
```

---

## Video Controls

### Playback Controls

```typescript
function playVideo() {
  if (S.videoPlayer.ytPlayer) {
    S.videoPlayer.ytPlayer.playVideo()
  } else {
    const video = document.getElementById('video-player') as HTMLVideoElement
    video.play()
  }
  S.videoPlayer.isPlaying = true
}

function pauseVideo() {
  if (S.videoPlayer.ytPlayer) {
    S.videoPlayer.ytPlayer.pauseVideo()
  } else {
    const video = document.getElementById('video-player') as HTMLVideoElement
    video.pause()
  }
  S.videoPlayer.isPlaying = false
}

function setVideoSpeed(speed: number) {
  S.videoPlayer.speed = speed
  if (S.videoPlayer.ytPlayer) {
    S.videoPlayer.ytPlayer.setPlaybackRate(speed)
  } else {
    const video = document.getElementById('video-player') as HTMLVideoElement
    video.playbackRate = speed
  }
}
```

---

## Related Documentation

- [TRACKER_COMPLETE_LOGIC.md](TRACKER_COMPLETE_LOGIC.md) - Function reference
- [TRACKER_STATE_MANAGEMENT.md](TRACKER_STATE_MANAGEMENT.md) - State management
- [TRACKER_EVENT_FLOW.md](TRACKER_EVENT_FLOW.md) - Event workflow
- [TRACKER_XY_POSITIONING.md](TRACKER_XY_POSITIONING.md) - XY positioning

---

*Last Updated: 2026-01-15*
