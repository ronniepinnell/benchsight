# Tracker XY Positioning System

**Rink coordinate system and XY positioning logic**

Last Updated: 2026-01-21
Version: 2.00

---

## Overview

The tracker uses a coordinate system to track puck and player positions on the rink. This document details the XY positioning system, coordinate conversion, and zone determination.

**Coordinate System:** Canvas-based (pixels)  
**Rink Dimensions:** Standard NHL rink (200ft x 85ft)  
**Zone System:** 3 zones (Offensive, Neutral, Defensive)

---

## Coordinate System

### Rink Dimensions

```
Standard NHL Rink:
- Length: 200 feet (60.96 meters)
- Width: 85 feet (25.91 meters)
- Neutral zone: 50 feet (15.24 meters)
- End zones: 75 feet each (22.86 meters)
```

### Canvas Coordinate System

```
Canvas coordinates (pixels):
- Origin (0, 0): Top-left corner
- X-axis: Left to right (0 to canvas.width)
- Y-axis: Top to bottom (0 to canvas.height)
- Center: (canvas.width / 2, canvas.height / 2)
```

### Rink Coordinate System

```
Rink coordinates (feet):
- Origin (0, 0): Center ice
- X-axis: Left to right (-100 to +100 feet)
- Y-axis: Top to bottom (-42.5 to +42.5 feet)
- Center: (0, 0)
```

---

## Coordinate Conversion

### Canvas to Rink Coordinates

```typescript
function convertCanvasToRink(
  canvasX: number,
  canvasY: number,
  canvasWidth: number,
  canvasHeight: number
): { x: number, y: number } {
  // Convert to rink coordinates
  const rinkX = (canvasX / canvasWidth) * 200 - 100  // -100 to +100
  const rinkY = (canvasY / canvasHeight) * 85 - 42.5  // -42.5 to +42.5
  
  return { x: rinkX, y: rinkY }
}
```

### Rink to Canvas Coordinates

```typescript
function convertRinkToCanvas(
  rinkX: number,
  rinkY: number,
  canvasWidth: number,
  canvasHeight: number
): { x: number, y: number } {
  // Convert to canvas coordinates
  const canvasX = ((rinkX + 100) / 200) * canvasWidth
  const canvasY = ((rinkY + 42.5) / 85) * canvasHeight
  
  return { x: canvasX, y: canvasY }
}
```

---

## Period Direction Handling

### Home Attacks Right in Period 1

```typescript
function adjustXYForPeriod(
  x: number,
  y: number,
  period: number,
  homeAttacksRightP1: boolean
): { x: number, y: number } {
  // In even periods, flip X coordinate
  if (period % 2 === 0) {
    x = -x  // Flip horizontally
  }
  
  // If home attacks left in P1, flip all periods
  if (!homeAttacksRightP1) {
    x = -x
  }
  
  return { x, y }
}
```

### Zone Determination

```typescript
function getZoneFromXY(
  x: number,
  y: number,
  period: number,
  team: 'home' | 'away',
  homeAttacksRightP1: boolean
): 'Offensive' | 'Neutral' | 'Defensive' {
  // Adjust for period direction
  const adjusted = adjustXYForPeriod(x, y, period, homeAttacksRightP1)
  
  // Determine zone based on X coordinate
  // Neutral zone: -25 to +25 feet
  // Offensive zone: +25 to +100 feet (for team attacking right)
  // Defensive zone: -100 to -25 feet (for team attacking left)
  
  if (adjusted.x > 25) {
    return team === 'home' ? 'Offensive' : 'Defensive'
  } else if (adjusted.x < -25) {
    return team === 'home' ? 'Defensive' : 'Offensive'
  } else {
    return 'Neutral'
  }
}
```

---

## XY Position Setting

### Setting Puck XY

```typescript
function setPuckXY(x: number, y: number) {
  // Convert canvas coordinates to rink coordinates
  const rinkCoords = convertCanvasToRink(x, y, canvasWidth, canvasHeight)
  
  // Adjust for period
  const adjusted = adjustXYForPeriod(
    rinkCoords.x,
    rinkCoords.y,
    S.period,
    S.homeAttacksRightP1
  )
  
  // Set in current event
  S.curr.puckXY = [adjusted.x, adjusted.y]
  
  // Determine zone
  const zone = getZoneFromXY(
    adjusted.x,
    adjusted.y,
    S.period,
    S.evtTeam,
    S.homeAttacksRightP1
  )
  
  // Update UI
  updateRinkDisplay()
  updateZoneDisplay(zone)
}
```

### Setting Player XY

```typescript
function setPlayerXY(
  playerId: string,
  slot: string,
  x: number,
  y: number
) {
  // Convert canvas coordinates
  const rinkCoords = convertCanvasToRink(x, y, canvasWidth, canvasHeight)
  
  // Adjust for period
  const adjusted = adjustXYForPeriod(
    rinkCoords.x,
    rinkCoords.y,
    S.period,
    S.homeAttacksRightP1
  )
  
  // Set in slot
  const team = S.slots.home[slot] ? 'home' : 'away'
  if (S.slots[team][slot]) {
    S.slots[team][slot].xy = [adjusted.x, adjusted.y]
  }
  
  // Update UI
  updateRinkDisplay()
}
```

---

## Rink Drawing

### Draw Rink Canvas

```typescript
function drawRink(canvas: HTMLCanvasElement) {
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  // Clear canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  
  // Draw rink outline
  drawRinkOutline(ctx, canvas.width, canvas.height)
  
  // Draw center line
  drawCenterLine(ctx, canvas.width, canvas.height)
  
  // Draw blue lines
  drawBlueLines(ctx, canvas.width, canvas.height)
  
  // Draw faceoff circles
  drawFaceoffCircles(ctx, canvas.width, canvas.height)
  
  // Draw goal creases
  drawGoalCreases(ctx, canvas.width, canvas.height)
  
  // Draw zones
  drawZones(ctx, canvas.width, canvas.height)
}
```

### Draw Events on Rink

```typescript
function drawEventsOnRink(canvas: HTMLCanvasElement, events: Event[]) {
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  events.forEach(event => {
    if (event.puckXY) {
      // Convert rink coordinates to canvas
      const canvasCoords = convertRinkToCanvas(
        event.puckXY[0],
        event.puckXY[1],
        canvas.width,
        canvas.height
      )
      
      // Draw event marker
      drawEventMarker(ctx, canvasCoords.x, canvasCoords.y, event.event_type)
    }
  })
}
```

---

## XY Validation

### Validate XY Position

```typescript
function validateXYPosition(x: number, y: number): boolean {
  // Check if within rink bounds
  // Rink: -100 to +100 feet (X), -42.5 to +42.5 feet (Y)
  if (x < -100 || x > 100) return false
  if (y < -42.5 || y > 42.5) return false
  
  return true
}
```

### Snap to Zone

```typescript
function snapXYToZone(
  x: number,
  y: number,
  zone: 'Offensive' | 'Neutral' | 'Defensive'
): { x: number, y: number } {
  // Snap X coordinate to zone center
  switch (zone) {
    case 'Offensive':
      x = 62.5  // Center of offensive zone
      break
    case 'Neutral':
      x = 0  // Center ice
      break
    case 'Defensive':
      x = -62.5  // Center of defensive zone
      break
  }
  
  return { x, y }
}
```

---

## XY History

### Track XY History

```typescript
function addXYToHistory(x: number, y: number) {
  S.xyHistory.push({
    x,
    y,
    timestamp: Date.now(),
    period: S.period,
    team: S.evtTeam
  })
  
  // Keep only last 100 positions
  if (S.xyHistory.length > 100) {
    S.xyHistory.shift()
  }
}
```

### Undo XY

```typescript
function undoXY() {
  if (S.xyHistory.length > 0) {
    const last = S.xyHistory.pop()
    if (last) {
      S.curr.puckXY = [last.x, last.y]
      updateRinkDisplay()
    }
  }
}
```

---

## Related Documentation

- [TRACKER_COMPLETE_LOGIC.md](TRACKER_COMPLETE_LOGIC.md) - Function reference
- [TRACKER_STATE_MANAGEMENT.md](TRACKER_STATE_MANAGEMENT.md) - State management
- [TRACKER_EVENT_FLOW.md](TRACKER_EVENT_FLOW.md) - Event workflow
- [TRACKER_VIDEO_INTEGRATION.md](TRACKER_VIDEO_INTEGRATION.md) - Video integration

---

*Last Updated: 2026-01-15*
