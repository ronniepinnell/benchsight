# Admin Portal Development Plan

**Roadmap to full portal functionality**

Last Updated: 2026-01-15  
Version: 1.0

---

## Overview

This document outlines the development plan to transform the admin portal from a UI mockup into a fully functional admin interface.

**Current State:** UI mockup only (10% complete)  
**Target State:** Fully functional admin portal (100% complete)  
**Timeline:** 4-6 weeks

---

## Development Phases

### Phase 1: API Integration (Week 1-2)

**Goal:** Connect portal to API and enable core functionality

#### Week 1: ETL Integration

**Tasks:**
1. **Replace Placeholder Functions**
   - Replace `triggerETL()` with real API call
   - Replace `uploadToSupabase()` with real API call
   - Add error handling

2. **Implement ETL Trigger**
   ```javascript
   async function triggerETL(mode, options) {
     const response = await fetch('/api/etl/trigger', {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify({ mode, options })
     })
     const job = await response.json()
     return job
   }
   ```

3. **Implement Status Polling**
   ```javascript
   async function pollETLStatus(jobId) {
     const response = await fetch(`/api/etl/status/${jobId}`)
     const job = await response.json()
     updateETLStatus(job)
     if (job.status === 'running') {
       setTimeout(() => pollETLStatus(jobId), 1000)
     }
   }
   ```

4. **Add Progress Display**
   - Progress bar
   - Current step display
   - Error messages

**Deliverables:**
- ✅ ETL trigger working
- ✅ Status polling working
- ✅ Progress display functional

#### Week 2: Upload Integration

**Tasks:**
1. **Implement Upload Trigger**
   - Connect to `/api/upload/to-supabase`
   - Support all upload modes
   - Add progress tracking

2. **Implement Schema Generation**
   - Connect to `/api/upload/generate-schema`
   - Display schema file location
   - Add download link

3. **Add Upload Status**
   - Poll upload status
   - Display upload progress
   - Show completion status

**Deliverables:**
- ✅ Upload functionality working
- ✅ Schema generation working
- ✅ Upload status display

---

### Phase 2: Data Display (Week 3)

**Goal:** Display actual data from Supabase

#### Tasks

1. **Connect to Supabase**
   - Initialize Supabase client
   - Add authentication (if needed)
   - Test connection

2. **Game List Display**
   - Fetch games from `dim_schedule`
   - Display in table
   - Add filters (season, date, etc.)

3. **Table List Display**
   - List all ETL tables
   - Show table metadata (row count, columns)
   - Add table details view

4. **Data Browser**
   - Browse table data
   - Add pagination
   - Add search/filter

**Deliverables:**
- ✅ Game list functional
- ✅ Table list functional
- ✅ Data browser functional

---

### Phase 3: Game Management (Week 4)

**Goal:** Enable game creation and management

#### Tasks

1. **Create Game**
   - Form for new game
   - Validation
   - Save to Supabase

2. **Edit Game**
   - Load game data
   - Edit form
   - Update in Supabase

3. **Delete Game**
   - Confirmation dialog
   - Delete from Supabase
   - Update display

4. **Game Status**
   - Track game status (scheduled, in-progress, completed)
   - Display tracking status
   - Show ETL status

**Deliverables:**
- ✅ Create game working
- ✅ Edit game working
- ✅ Delete game working
- ✅ Game status tracking

---

### Phase 4: Enhanced Features (Week 5-6)

**Goal:** Add advanced features and polish

#### Tasks

1. **Staging Data Upload**
   - BLB table upload
   - Tracking data upload
   - Data validation

2. **Settings Management**
   - Save settings to localStorage/Supabase
   - User preferences
   - API configuration

3. **Notifications**
   - Toast notifications
   - Success/error messages
   - Job completion alerts

4. **UI Polish**
   - Loading states
   - Error states
   - Empty states
   - Responsive design

**Deliverables:**
- ✅ Staging upload working
- ✅ Settings functional
- ✅ Notifications working
- ✅ UI polished

---

## Technical Implementation

### Technology Stack

**Frontend:**
- HTML/CSS/JavaScript (current)
- OR: Convert to React/Next.js (future)

**API Integration:**
- Fetch API for HTTP requests
- WebSocket for real-time updates (future)

**State Management:**
- Local state (JavaScript variables)
- OR: React Context/Zustand (if converted to React)

### API Client

```javascript
class APIClient {
  constructor(baseURL) {
    this.baseURL = baseURL || 'http://localhost:8000'
  }
  
  async triggerETL(mode, options) {
    const response = await fetch(`${this.baseURL}/api/etl/trigger`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode, options })
    })
    return response.json()
  }
  
  async getETLStatus(jobId) {
    const response = await fetch(`${this.baseURL}/api/etl/status/${jobId}`)
    return response.json()
  }
  
  // ... other methods
}

const api = new APIClient()
```

### State Management

```javascript
const portalState = {
  etlJobs: [],
  currentJob: null,
  games: [],
  tables: [],
  settings: {}
}

function updateState(updates) {
  Object.assign(portalState, updates)
  updateUI()
}
```

---

## Feature Checklist

### ETL Control

- [ ] Trigger ETL (full mode)
- [ ] Trigger ETL (single game mode)
- [ ] Trigger ETL (incremental mode)
- [ ] View ETL status
- [ ] View ETL history
- [ ] Cancel ETL job
- [ ] View ETL progress
- [ ] View ETL errors

### Upload Control

- [ ] Upload all tables
- [ ] Upload dimension tables
- [ ] Upload fact tables
- [ ] Upload specific tables
- [ ] View upload status
- [ ] Generate schema
- [ ] Download schema

### Game Management

- [ ] List games
- [ ] Create game
- [ ] Edit game
- [ ] Delete game
- [ ] View game details
- [ ] Filter games
- [ ] Search games

### Data Browser

- [ ] List tables
- [ ] View table data
- [ ] Filter table data
- [ ] Search table data
- [ ] Export table data
- [ ] View table schema

### Staging

- [ ] Upload BLB tables
- [ ] Update BLB tables
- [ ] Upload tracking data
- [ ] View staging data
- [ ] Clear staging tables

### Settings

- [ ] API URL configuration
- [ ] Supabase configuration
- [ ] User preferences
- [ ] Save settings
- [ ] Load settings

---

## Success Criteria

### Phase 1 Complete

- ✅ Can trigger ETL from portal
- ✅ Can see ETL status in real-time
- ✅ Can upload to Supabase
- ✅ Can see upload progress

### Phase 2 Complete

- ✅ Can view game list
- ✅ Can view table list
- ✅ Can browse table data

### Phase 3 Complete

- ✅ Can create games
- ✅ Can edit games
- ✅ Can delete games

### Phase 4 Complete

- ✅ All features functional
- ✅ UI polished
- ✅ Error handling complete
- ✅ Ready for production

---

## Related Documentation

- [PORTAL_CURRENT_STATE.md](PORTAL_CURRENT_STATE.md) - Current state assessment
- [PORTAL_API_REQUIREMENTS.md](PORTAL_API_REQUIREMENTS.md) - API requirements
- [API_REFERENCE.md](API_REFERENCE.md) - API endpoint reference

---

*Last Updated: 2026-01-15*
