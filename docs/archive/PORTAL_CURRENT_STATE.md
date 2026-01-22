# Admin Portal Current State

**Assessment of current admin portal implementation**

Last Updated: 2026-01-21
Version: 2.00

---

## Overview

The admin portal is currently a UI mockup with no backend functionality. This document details what exists and what's missing.

**Location:** `ui/portal/index.html`  
**Status:** UI mockup only (10% complete)  
**Backend:** None (no API integration)

---

## Current Implementation

### What Exists

#### UI Components

**Design:**
- ✅ Modern dark theme UI
- ✅ Cyberpunk aesthetic
- ✅ Responsive layout
- ✅ Navigation sidebar
- ✅ Main content area

**Pages/Sections:**
- ✅ ETL Control interface (UI only)
- ✅ Game Management interface (UI only)
- ✅ Data Browser interface (UI only)
- ✅ Settings interface (UI only)

**UI Elements:**
- ✅ Buttons and controls
- ✅ Forms and inputs
- ✅ Tables and lists
- ✅ Modals and dialogs

#### JavaScript

**Current Functions:**
- Basic UI interactions (show/hide, toggle)
- Form handling (placeholder)
- Button click handlers (placeholder)
- No actual API calls
- No data fetching
- No state management

---

## What's Missing

### Backend Integration

**Critical Missing Features:**
- ❌ **NO API Integration** - All buttons are placeholders
- ❌ **NO Data Fetching** - No connection to Supabase or API
- ❌ **NO ETL Triggering** - Cannot actually trigger ETL
- ❌ **NO Game Management** - Cannot create/edit/delete games
- ❌ **NO Data Display** - Cannot view actual data

### Authentication

**Missing:**
- ❌ **NO Authentication** - No login system
- ❌ **NO User Management** - No user roles
- ❌ **NO Protected Routes** - No access control

### Functionality

**Missing Features:**
- ❌ ETL job triggering
- ❌ ETL status monitoring
- ❌ Upload to Supabase
- ❌ Game creation/editing
- ❌ Data browsing
- ❌ Settings persistence

---

## Current Code Structure

### HTML Structure

```html
<!DOCTYPE html>
<html>
<head>
  <!-- Styles -->
</head>
<body>
  <div class="portal-container">
    <nav class="sidebar">
      <!-- Navigation -->
    </nav>
    <main class="content">
      <!-- ETL Control Section -->
      <section id="etl-control">
        <button onclick="triggerETL()">Run ETL</button>
        <!-- Placeholder - no actual function -->
      </section>
      
      <!-- Game Management Section -->
      <section id="game-management">
        <!-- UI only -->
      </section>
      
      <!-- Data Browser Section -->
      <section id="data-browser">
        <!-- UI only -->
      </section>
    </main>
  </div>
</body>
</html>
```

### JavaScript Functions (Placeholders)

```javascript
function triggerETL() {
  // Placeholder - does nothing
  alert('ETL trigger clicked (not implemented)')
}

function uploadToSupabase() {
  // Placeholder - does nothing
  alert('Upload clicked (not implemented)')
}

function createGame() {
  // Placeholder - does nothing
  alert('Create game clicked (not implemented)')
}
```

---

## Integration Requirements

### API Integration Needed

**ETL Endpoints:**
- `POST /api/etl/trigger` - Trigger ETL
- `GET /api/etl/status/{job_id}` - Get ETL status
- `GET /api/etl/history` - Get ETL history

**Upload Endpoints:**
- `POST /api/upload/to-supabase` - Upload tables
- `GET /api/upload/status/{job_id}` - Get upload status

**Staging Endpoints:**
- `POST /api/staging/blb-tables/upload` - Upload BLB data
- `POST /api/staging/tracking/upload` - Upload tracking data

### Supabase Integration Needed

**Direct Queries:**
- Game list from `dim_schedule`
- Player list from `dim_player`
- Team list from `dim_team`
- Table metadata

---

## Development Plan

### Phase 1: API Integration (Priority: HIGH)

**Tasks:**
1. Replace placeholder functions with real API calls
2. Implement ETL trigger functionality
3. Implement status polling
4. Implement upload functionality

**Example Implementation:**
```javascript
async function triggerETL() {
  try {
    const response = await fetch('http://localhost:8000/api/etl/trigger', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        mode: 'full',
        options: {
          wipe: false,
          upload_to_supabase: true
        }
      })
    })
    
    const job = await response.json()
    startPollingJobStatus(job.job_id)
  } catch (error) {
    showError('Failed to trigger ETL: ' + error.message)
  }
}
```

### Phase 2: Data Display (Priority: MEDIUM)

**Tasks:**
1. Connect to Supabase
2. Display game list
3. Display table list
4. Display data browser

### Phase 3: Game Management (Priority: MEDIUM)

**Tasks:**
1. Create game functionality
2. Edit game functionality
3. Delete game functionality
4. Game status display

### Phase 4: Authentication (Priority: LOW)

**Tasks:**
1. Add login page
2. Add authentication check
3. Add user management
4. Add role-based access

---

## Current File Structure

```
ui/portal/
├── index.html          # Main portal page (UI mockup)
├── styles.css          # Styles (if separate)
└── script.js           # JavaScript (if separate)
```

**Note:** Currently, everything is in `index.html` (single file).

---

## Next Steps

### Immediate (Week 1)

1. **Connect to API:**
   - Replace placeholder functions
   - Implement API calls
   - Add error handling

2. **ETL Control:**
   - Implement ETL trigger
   - Add status polling
   - Add progress display

3. **Basic Data Display:**
   - Connect to Supabase
   - Display game list
   - Display table list

### Short-term (Weeks 2-4)

4. **Game Management:**
   - Create/edit/delete games
   - Game status tracking

5. **Upload Functionality:**
   - Upload to Supabase
   - Upload status monitoring

6. **Data Browser:**
   - Browse tables
   - View table data
   - Export data

---

## Related Documentation

- [PORTAL_DEVELOPMENT_PLAN.md](PORTAL_DEVELOPMENT_PLAN.md) - Development roadmap
- [PORTAL_API_REQUIREMENTS.md](PORTAL_API_REQUIREMENTS.md) - API requirements

---

*Last Updated: 2026-01-15*
