---
name: tracker-dev
description: Work on the game tracking application for recording hockey events and shifts. Use when developing tracker features or debugging tracking functionality.
allowed-tools: Bash, Read, Write, Edit
---

# Tracker Development

The tracker is a comprehensive game tracking application for recording hockey events, shifts, and statistics.

## Current Status

- Version: 27.0
- Status: 100% functional (current version)
- Future: Rust backend + Next.js frontend conversion planned

## Start Tracker

```bash
# Serve tracker locally
cd ui/tracker && python -m http.server 8081
```

Tracker runs at: http://localhost:8081

## Architecture

**Current:** Vanilla HTML5 + JavaScript (35K+ lines, 722 functions)

**Module Structure:**
```
html/modules/
├── core/      # Core event/shift tracking
├── data/      # Data management and export
├── events/    # Event handling system
├── shifts/    # Shift tracking logic
├── stats/     # Statistics calculation
├── storage/   # Local storage persistence
├── ui/        # User interface components
├── utils/     # Utility functions
├── video/     # Video playback integration
└── xy/        # XY position tracking
```

## Event Types (15+)

- Shot, Goal, Save
- Pass, Reception
- Faceoff (win/loss)
- Zone Entry, Zone Exit
- Turnover, Takeaway
- Hit, Block
- Penalty
- Icing, Offside
- Stoppage

## Key Features

1. **Event Tracking**
   - 15+ event types with details
   - XY positioning on rink
   - Player attribution
   - Micro-stats (play_detail1, play_detail2)

2. **Shift Tracking**
   - Player entry/exit times
   - On-ice player management
   - Time on ice calculations

3. **Video Integration**
   - HTML5, YouTube support
   - Event-video synchronization
   - Timeline navigation

4. **Data Export**
   - Excel format
   - Local storage backup
   - Supabase sync (optional)

## Critical Data Rules

1. **Event Players**
   - event_player_1: Primary actor
   - event_player_2: Secondary actor (assists, etc.)
   - opp_player_1-3: Opposing players

2. **Linked Events**
   - linked_event_key connects related events
   - Micro-stats count ONCE per linked chain

3. **Faceoffs**
   - event_player_1 = winner
   - opp_player_1 = loser

## Development Focus

For conversion to Rust/Next.js:
1. Preserve all 722 functions
2. Maintain event type compatibility
3. Keep Excel export format
4. Ensure video sync works
5. Support offline mode
