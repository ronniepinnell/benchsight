# Comprehensive Enhancement Plan

## Overview
This document outlines the plan for comprehensive enhancements to the BenchSight dashboard, including video highlights, enhanced pages, stat pages, and improved linking.

## 1. Video Highlights System

### Data Sources
- `dim_schedule`: `video_url_1`, `video_url_2`, `video_start_offset`
- `fact_events`: `video_url`, `running_video_time`
- `fact_shifts`: `video_start_time`, `video_end_time`

### Implementation
- Enhance `GameHighlights` component to use YouTube URLs with start times
- Create shift highlights using shift video timestamps
- Add video player component for embedded YouTube playback
- Format YouTube URLs with `?t=` parameter for start times

## 2. Compare Players Page

### Current State
- Basic comparison exists
- Limited stats shown

### Enhancements Needed
- Add comprehensive stats comparison (all advanced stats)
- Add visual comparison (charts, side-by-side)
- Add head-to-head matchup data
- Add season-over-season trends for both players

## 3. Trends Page

### Current State
- Placeholder content only

### Enhancements Needed
- Time-series visualizations
- Player performance trends
- Team statistics evolution
- League-wide metric comparisons
- Interactive charts (line charts, bar charts)

## 4. Shift Viewer Page

### Current State
- Basic placeholder

### Enhancements Needed
- Shift-by-shift visualization
- Line combination analysis
- Shift length analysis
- Video integration for shifts
- Shift quality metrics
- Zone time analysis

## 5. Game Pages (Tracked vs Non-Tracked)

### Tracked Games
- Full advanced stats
- Event-by-event timeline
- Shift data
- Video highlights
- Shot heatmaps
- Zone time analysis
- Line combinations

### Non-Tracked Games
- Basic box score
- Game summary
- Team stats
- Player stats (from fact_gameroster)
- Goals/scoring summary

## 6. Stat Pages (Dedicated Pages)

### Implementation
- Create `/stats/[statKey]` route
- Comprehensive stat details
- League leaders
- Historical context
- Player rankings
- Team rankings
- Trend analysis
- Formula/calculation details

### Stats to Support
- CF%, FF%, xG
- WAR, GAR
- Shooting %
- Goals/60, Assists/60, Points/60
- Faceoff %
- Pass %
- Zone Entry/Exit %
- Hits, Blocks, Takeaways
- All major stats

## 7. Linking Improvements

### Ensure All Clickable Elements Link:
- Player names → `/players/[playerId]`
- Team names → `/team/[teamName]`
- Game IDs/dates → `/games/[gameId]`
- Stat values → `/stats/[statKey]` (when stat pages exist)

## Priority Order

1. **Video Highlights** (High Impact)
2. **Game Pages Enhancement** (High Impact)
3. **Stat Pages** (High Impact, Complex)
4. **Compare/Trends/Shift Viewer** (Medium Impact)
5. **Linking Improvements** (Ongoing)
