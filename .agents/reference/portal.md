# Portal Rules

**Portal-specific patterns and rules**

Last Updated: 2026-01-15

---

## Portal Architecture

### Current State
- **HTML/JavaScript** - Prototype portal
- **Location:** `ui/portal/`

### Future State
- **Next.js** - Production portal
- **Integration:** Connect to API

---

## Portal Patterns

### ETL Management UI

**Features:**
- ETL execution control
- Status monitoring
- Table management
- Data verification

### Admin Interface

**Components:**
- ETL runner
- Status dashboard
- Table browser
- Settings panel

---

## API Integration

### ETL Control

```typescript
// Trigger ETL
const response = await fetch('/api/etl/run', {
  method: 'POST',
  body: JSON.stringify({
    games: selectedGames,
    wipe: wipeFlag
  })
})

// Check status
const status = await fetch(`/api/etl/status/${jobId}`)
```

---

## Related Rules

- `core.md` - Core rules
- `api.md` - API integration patterns
- `dashboard.md` - Next.js patterns

---

*Last Updated: 2026-01-15*
