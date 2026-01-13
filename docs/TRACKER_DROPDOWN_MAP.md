# Tracker Dropdown → Supabase Dim Table Mapping

## UI Element to Dim Table Map

| Circle | UI Element | Field Name | Supabase Table | Column Used | Status |
|--------|------------|------------|----------------|-------------|--------|
| 🔘 Gray | Event Type Buttons | `event_type` | `dim_event_type` | `event_type_code` | ✅ Fixed in v22.1 |
| 🔵 Blue | DETAIL 1 | `event_detail` | `dim_event_detail` | `event_detail_name` | ✅ Working |
| 🟣 Pink | DETAIL 2 | `event_detail_2` | `dim_event_detail_2` | `event_detail_2_name` | ✅ Working |
| 🟢 Green | PLAY DETAIL 1 | `play_detail` | `dim_play_detail` | `play_detail_name` | ✅ Working |
| 🔴 Red | PLAY DETAIL 2 | `play_detail_2` | `dim_play_detail_2` | `play_detail_2_name` | ✅ Working |

---

## Current Code Locations (index.html)

### Event Types (Gray) - NEEDS FIX
**Line 1663** - Currently hardcoded:
```javascript
eventTypes: ['Faceoff','Shot','Pass','Goal','Turnover','Zone_Entry_Exit','Penalty','Stoppage','Possession','Save','Rebound','DeadIce','Play','Intermission','Clockstop','Timeout'],
```

Should load from `dim_event_type` like the others.

### Event Detail 1 (Blue) - ✅ Working
**Line 1845**:
```javascript
const { data: ed1, error: e2a } = await S.sb.from('dim_event_detail')
  .select('event_detail_id,event_detail_name,event_type')
```

### Event Detail 2 (Pink) - ✅ Working
**Line 1860**:
```javascript
const { data: ed2, error: e2b } = await S.sb.from('dim_event_detail_2')
  .select('event_detail_2_id,event_detail_2_name,event_detail_2_code')
```

### Play Detail 1 (Green) - ✅ Working
**Line 1817**:
```javascript
const { data: pd1, error: e1 } = await S.sb.from('dim_play_detail')
  .select('play_detail_id,play_detail_name,play_category')
```

### Play Detail 2 (Red) - ✅ Working
**Line 1831**:
```javascript
const { data: pd2, error: e2 } = await S.sb.from('dim_play_detail_2')
  .select('play_detail_2_id,play_detail_2_name,play_category')
```

---

## Import Value Mapping Popup (Line 8026-8030)

The fuzzy matching popup correctly maps to all 5 dim tables:

```javascript
const tables = [
  { name: 'dim_event_type', field: 'event_type', col: 'event_type_code' },
  { name: 'dim_event_detail', field: 'event_detail', col: 'event_detail_code' },
  { name: 'dim_event_detail_2', field: 'event_detail_2', col: 'event_detail_2_code' },
  { name: 'dim_play_detail', field: 'play_detail', col: 'play_detail_code' },
  { name: 'dim_play_detail_2', field: 'play_detail_2', col: 'play_detail_2_code' }
];
```

---

## Supabase Table Structure

### dim_event_type (23 rows)
```
event_type_id | event_type_code | event_type_name
ET01          | Faceoff         | Faceoff
ET02          | Shot            | Shot
...
```

### dim_event_detail (49 rows)
```
event_detail_id | event_detail_code    | event_detail_name    | event_type
ED001           | Shot_OnNetSaved      | Shot On Net (Saved)  | Shot
ED002           | Shot_Goal            | Shot Goal            | Shot
...
```

### dim_event_detail_2 (176 rows)
```
event_detail_2_id | event_detail_2_code | event_detail_2_name
ED2001            | Shot-Wrist          | Wrist Shot
ED2002            | Shot-Slap           | Slap Shot
...
```

### dim_play_detail (111 rows)
```
play_detail_id | play_detail_code                    | play_detail_name
PD001          | OffensivePlay_Shot-WristShot        | Offensive Play - Wrist Shot
PD002          | DefensivePlay_Block-StickBlock      | Defensive Play - Stick Block
...
```

### dim_play_detail_2 (111 rows)
```
play_detail_2_id | play_detail_2_code | play_detail_2_name
PD2001           | Cycle              | Cycle Play
PD2002           | Rush               | Rush Play
...
```

---

## Recommended Fix for Event Types

To make Event Types load from Supabase like the others:

1. Add loading code after line 1870:
```javascript
// Load dim_event_type for event type buttons
const { data: et, error: etErr } = await S.sb.from('dim_event_type')
  .select('event_type_id,event_type_code,event_type_name')
  .order('display_order,event_type_name');

if (!etErr && et) {
  S.eventTypes = et.map(e => ({
    id: e.event_type_id,
    code: e.event_type_code,
    name: e.event_type_name
  }));
  console.log('Loaded', S.eventTypes.length, 'event types');
}
```

2. Update button generation to use dynamic list

3. Add "Show More" toggle for less common event types
