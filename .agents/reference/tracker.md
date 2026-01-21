# Tracker Rules

**Tracker-specific patterns and rules**

Last Updated: 2026-01-15

---

## Tracker Architecture

### Current State
- **HTML/JavaScript** - Prototype tracker
- **Location:** `ui/tracker/`

### Future State
- **Rust/Next.js** - Production tracker
- **Conversion:** Document all logic before conversion

---

## Tracker Patterns

### Event Tracking

**Event Types:**
- Goal
- Shot
- Pass
- Faceoff
- Penalty
- Shift

**Event Structure:**
```javascript
{
  event_type: 'Goal',
  event_detail: 'Goal_Scored',
  event_player_1: 'player_id',
  event_player_2: 'assist_player_id',
  period: 1,
  time: '10:30',
  x: 0.5,
  y: 0.3
}
```

### State Management

**Current (HTML/JS):**
- Local state in JavaScript
- Export to JSON

**Future (Rust/Next.js):**
- State management library
- Real-time sync with backend

---

## Goal Counting Logic

### Goal Event Pattern

**ALWAYS use:**
```javascript
if (event_type === 'Goal' && event_detail === 'Goal_Scored') {
  // Count as goal
}
```

**NEVER count:**
- `event_type === 'Shot'` with `event_detail === 'Goal'`
- Any other combination

---

## Export Patterns

### Current Export Format

**JSON Structure:**
```json
{
  "game_id": "game_123",
  "events": [...],
  "shifts": [...],
  "metadata": {...}
}
```

**Maintain compatibility** during conversion.

---

## Keyboard Shortcuts

### Current Shortcuts

- Document all keyboard shortcuts
- Maintain in Rust/Next.js version
- Provide user documentation

---

## Related Rules

- `core.md` - Core rules (goal counting)
- `data.md` - Data validation rules
- `dashboard.md` - UI patterns (for Next.js conversion)

---

*Last Updated: 2026-01-15*
